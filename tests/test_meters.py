"""dio meters (FINISH.md step 7): the usage, model_limits, context and credits lines, their
states and the parse, the join of a context file to its session's name by id, the order of the
lines, the exits, the defaults under HOME, and, under strace, no .key path opened and no write.

Every fixture is built in the test's temporary tree from FINISH.md's shapes and the Team status
line writer's (the jq programs that write the usage and context files), never copied from a real
file, and every flag points into that tree. In-process runs take the injected clock
(fixtures.Clock); the built dio runs on the real clock, against files written from it. No test
sleeps. MetersStraceTests is the one test here that runs strace.

Run from the repository root, with TMPDIR set to a scratch directory (tests/README.md):

    TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -v
"""

import contextlib
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import time
import unittest
from unittest import mock

import fixtures
from fixtures import CANARY, DIO, REPOSITORY, SECOND_CANARY, Clock, World

dio = fixtures.load_dio()
FINISH = os.path.join(REPOSITORY, 'meta', 'roadmap', '0.0', 'FINISH.md')
DAY = 86400
HEADER = '| started | ended | job | model | turns | cost | status | rc |'
SEPARATOR = '|---|---|---|---|---|---|---|---|'
# model_limits in file order, which is not sorted order: the line keeps the file's.
MODEL_LIMITS = '{"sonnet": {"used_percentage": 3, "resets_at": 1792130400}, "fable": [12.5, null]}'
FIELDS = {'usage': 8, 'model_limits': 3, 'context': 7, 'credits': 5}
CALL = re.compile(r'^(?:[0-9]+ +)?([a-z0-9_]+)\(')
WRITE_CALLS = ('creat', 'rename', 'renameat', 'renameat2', 'link', 'linkat', 'symlink', 'symlinkat',
               'unlink', 'unlinkat', 'mkdir', 'mkdirat', 'rmdir', 'mknod', 'mknodat', 'truncate',
               'chmod', 'fchmodat', 'chown', 'lchown', 'fchownat', 'utime', 'utimes', 'utimensat',
               'futimesat', 'setxattr', 'lsetxattr', 'removexattr', 'lremovexattr')


def setUpModule():
    fixtures.require_tmpdir()


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def utc(seconds):
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(seconds))


def window(used, resets_at):
    return {'used_percentage': used, 'resets_at': resets_at}


def team_usage(written_at, five, seven, **extra):
    """A usage file as the Team writer's jq makes it: written_at, written_at_iso, written_by,
    account, and rate_limits holding five_hour and seven_day, each null or a window."""
    record = {'written_at': written_at, 'written_at_iso': utc(written_at), 'written_by': 'probe-t_3',
              'account': 'team', 'rate_limits': {'five_hour': five, 'seven_day': seven}}
    record.update(extra)
    return record


def max_usage(written_at, five, seven):
    """The Max writer's: the same, with the model_limits the Team writer leaves out."""
    text = json.dumps(dict(team_usage(written_at, five, seven), account='max'))
    return (text[:-1] + ', "model_limits": ' + MODEL_LIMITS + '}').encode()


def context_record(session_id, written_at, used=17, name='probe-t_3', **extra):
    """A context file as the Team writer's jq makes it, <session_id>.json."""
    record = {'written_at': written_at, 'written_at_iso': utc(written_at), 'session_id': session_id,
              'session_name': name, 'cwd': '/', 'model': 'claude-opus-5-5',
              'context_window': {'total_input_tokens': 1000, 'context_window_size': 200000,
                                 'used_percentage': used,
                                 'remaining_percentage': 100 - used if type(used) in (int, float) else None},
              'rate_limits': {'five_hour': None, 'seven_day': None}}
    record.update(extra)
    return record


def row(job, cost='0.12'):
    return ('| 2026-10-21T13:00:00Z | 2026-10-21T13:05:00Z | %s | claude-sonnet-5-5 | 3 | %s | ok | 0 |'
            % (job, cost))


def records(out, kind=None):
    rows = [line.split('\t') for line in out.splitlines()]
    return [r for r in rows if kind is None or r[0] == kind]


class MetersBase(unittest.TestCase):
    """Both usage files fresh on the injected clock, both context roots empty, both ledgers a
    header alone, and the standard world's sessions roots, each behind its flag."""

    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)
        patcher = mock.patch.dict(os.environ, {'HOME': self.world.home})
        patcher.start()
        self.addCleanup(patcher.stop)
        self.clock = Clock()
        self.now = int(self.clock().timestamp())
        self.usage = {account: os.path.join(self.world.make('usage-' + account), 'usage-latest.json')
                      for account in ('max', 'team')}
        self.context = {account: self.world.make('context-' + account) for account in ('max', 'team')}
        self.ledger = {source: os.path.join(self.world.make('ledger-' + source), 'LEDGER.md')
                       for source in ('management', 'libs')}
        self.put('max', max_usage(self.now - 35, window(42, self.now + 7200),
                                  window(33.5, self.now + 4 * DAY)))
        self.put('team', team_usage(self.now - 20, window(12, self.now + 3600),
                                    window(30, self.now + 6 * DAY)))
        for source in self.ledger:
            self.ledger_text(source, [HEADER, SEPARATOR])

    # -- building

    def put(self, account, content):
        path = self.usage[account]
        return self.world.write(os.path.dirname(path), os.path.basename(path), content)

    def put_context(self, account, name, content):
        return self.world.write(self.context[account], name, content)

    def ledger_text(self, source, lines, ending='\n'):
        data = ending.join(lines) + ending if lines else ''
        with open(self.ledger[source], 'wb') as f:
            f.write(data.encode('utf-8', 'surrogateescape'))

    # -- running

    def flags(self, contexts=('max', 'team'), ledgers=('management', 'libs')):
        flags = ['--max-usage', self.usage['max'], '--team-usage', self.usage['team']]
        for account in contexts:
            flags += ['--context-root', '%s=%s' % (account, self.context[account])]
        for source in ledgers:
            flags += ['--ledger', '%s=%s' % (source, self.ledger[source])]
        return flags + ['--sessions-root', 'max=' + self.world.max_root,
                        '--sessions-root', 'team=' + self.world.team_root]

    def meters(self, *args):
        """dio meters in-process on the injected clock, with `args` in place of self.flags()."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                status = dio.main(['meters'] + (list(args) or self.flags()), now=self.clock)
            except SystemExit as e:
                status = e.code
        return status, out.getvalue(), err.getvalue()

    def line(self, kind, label, *args):
        status, out, err = self.meters(*args)
        found = [r for r in records(out, kind) if r[1] == label]
        self.assertEqual(len(found), 1, out + err)
        return found[0]

    def recording_open(self):
        """Patch os.open for one call of dio; returns (calls, patcher), each call (path, flags,
        the directory its dir_fd names, or None)."""
        calls, real_open = [], os.open

        def record(path, flags, mode=0o777, *, dir_fd=None):
            where = None if dir_fd is None else os.readlink('/proc/self/fd/%d' % dir_fd)
            calls.append((path, flags, where))
            return real_open(path, flags, mode, dir_fd=dir_fd)
        patcher = mock.patch.object(dio.os, 'open', record)
        patcher.start()
        self.addCleanup(patcher.stop)
        return calls, patcher


class UsageTests(MetersBase):
    def test_a_fresh_file_reads_measured_with_its_age_its_figures_and_its_resets_in_utc(self):
        status, out, err = self.meters()
        self.assertEqual((status, err), (0, ''))
        self.assertEqual(records(out, 'usage'), [
            ['usage', 'max', 'measured', '35', '42', '2026-10-16T03:00:00Z', '33.5',
             '2026-10-20T01:00:00Z'],
            ['usage', 'team', 'measured', '20', '12', '2026-10-16T02:00:00Z', '30',
             '2026-10-22T01:00:00Z']])

    def test_measured_to_600_seconds_and_past_it_stale_in_whole_minutes_rounded_down(self):
        for age, state in ((0, 'measured'), (600, 'measured'), (601, 'stale (10 min)'),
                           (659, 'stale (10 min)'), (660, 'stale (11 min)'), (720, 'stale (12 min)'),
                           (779, 'stale (12 min)'), (780, 'stale (13 min)'),
                           (7 * DAY, 'stale (10080 min)')):
            with self.subTest(age=age):
                self.put('team', team_usage(self.now - age, None, None))
                status, out, err = self.meters()
                self.assertEqual(records(out, 'usage')[1][2:4], [state, str(age)])
                self.assertEqual(status, 0 if state == 'measured' else 1)

    def test_a_written_at_later_than_the_clock_reads_measured_with_its_negative_age(self):
        # Decision 29: "measured while the age is at most 600" holds for a negative age.
        self.put('team', team_usage(self.now + 90, None, None))
        self.assertEqual(self.line('usage', 'team')[2:4], ['measured', '-90'])

    def test_m5s_aging_line_makes_both_copies_read_stale_12_min(self):
        # FINISH.md's M5 aging line, run as it is printed on a Max-shaped and a Team-shaped copy,
        # then the built dio within the minute, on the real clock.
        text = read(FINISH)
        body = re.search(r'^```sh\n(.*?)^```$', text[text.index("**M5's aging line**"):],
                         re.M | re.S).group(1)
        self.assertEqual(body.count('\n'), 1)
        now = int(time.time())
        self.put('max', max_usage(now - 30, window(42, now + 7200), window(33, now + DAY)))
        self.put('team', team_usage(now - 30, window(12, now + 3600), None))
        for account in ('max', 'team'):
            argv = shlex.split(body)
            self.assertEqual(argv[-1], '<copy>')
            result = subprocess.run(argv[:-1] + [self.usage[account]], env=self.world.env(),
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual((result.returncode, result.stderr), (0, ''))
        result = self.world.run('meters', *self.flags())
        self.assertEqual(result.returncode, 1, result.stderr)
        usage = records(result.stdout, 'usage')
        self.assertEqual([line[2] for line in usage], ['stale (12 min)', 'stale (12 min)'])
        self.assertTrue(all(720 <= int(line[3]) < 780 for line in usage), usage)
        self.assertEqual(len(records(result.stdout, 'model_limits')), 1)

    def test_an_absent_file_or_directory_reads_unknown_absent_with_dash_figures(self):
        os.unlink(self.usage['max'])
        self.assertEqual(self.line('usage', 'max'), ['usage', 'max', 'unknown (absent)'] + ['-'] * 5)
        shutil.rmtree(os.path.dirname(self.usage['team']))
        status, out, err = self.meters()
        self.assertEqual(status, 1)
        self.assertEqual(records(out, 'usage')[1], ['usage', 'team', 'unknown (absent)'] + ['-'] * 5)

    def test_a_symlink_is_refused_and_its_target_never_read(self):
        target = self.world.write(self.world.base, 'target.json',
                                  team_usage(self.now, None, None, written_by='TARGET-MARKER'))
        os.unlink(self.usage['team'])
        os.symlink(target, self.usage['team'])
        calls, patcher = self.recording_open()
        status, out, err = self.meters()
        patcher.stop()
        self.assertEqual(status, 1)
        self.assertEqual(records(out, 'usage')[1], ['usage', 'team', 'unknown (refused: symlink)']
                         + ['-'] * 5)
        opened = [(path, flags) for path, flags, _ in calls if path == 'usage-latest.json']
        self.assertEqual(len(opened), 2)  # each account's file, relative to its directory
        self.assertTrue(all(flags & os.O_NOFOLLOW for _, flags in opened))
        self.assertEqual([path for path, _, _ in calls if 'target' in path], [])
        self.assertNotIn('TARGET-MARKER', out + err)

    def test_a_fifo_is_refused_without_blocking(self):
        os.unlink(self.usage['team'])
        os.mkfifo(self.usage['team'])
        result = self.world.run('meters', *self.flags(), timeout=60)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(records(result.stdout, 'usage')[1],
                         ['usage', 'team', 'unknown (refused: not a regular file)'] + ['-'] * 5)

    def test_a_path_that_names_a_directory_is_refused_as_not_a_regular_file(self):
        directory = os.path.dirname(self.usage['team'])
        for path in (directory, directory + '/'):
            with self.subTest(path=path):
                flags = self.flags()
                flags[flags.index('--team-usage') + 1] = path
                self.assertEqual(self.line('usage', 'team', *flags)[2],
                                 'unknown (refused: not a regular file)')

    def test_a_file_over_64_kib_reads_usage_format_and_one_of_64_kib_reads(self):
        record = team_usage(self.now - 20, None, None, pad='')
        size = len(json.dumps(record).encode())
        for pad, state in ((65536 - size, 'measured'), (65537 - size, 'unknown (usage format)')):
            with self.subTest(bytes=size + pad):
                self.put('team', dict(record, pad='x' * pad))
                self.assertEqual(os.path.getsize(self.usage['team']), size + pad)
                self.assertEqual(self.line('usage', 'team')[2], state)

    def test_a_duplicate_key_reads_usage_format(self):
        good = json.dumps(team_usage(self.now - 20, None, None))
        self.put('team', ('{"written_at": %d, ' % self.now + good[1:]).encode())
        self.assertEqual(self.line('usage', 'team'), ['usage', 'team', 'unknown (usage format)']
                         + ['-'] * 5)

    def test_nan_or_infinity_anywhere_reads_usage_format(self):
        good = json.dumps(team_usage(self.now - 20, None, None))
        for constant in ('NaN', 'Infinity', '-Infinity'):
            with self.subTest(constant=constant):
                self.put('team', (good[:-1] + ', "extra": %s}' % constant).encode())
                self.assertEqual(self.line('usage', 'team')[2], 'unknown (usage format)')

    def test_a_written_at_that_is_not_an_integer_time_reads_usage_format(self):
        good = team_usage(self.now - 20, None, None)
        for case, value in (('a float', self.now - 20.5), ('a whole float', float(self.now - 20)),
                            ('a string', str(self.now - 20)), ('a boolean', True), ('null', None),
                            ('a 400-digit integer', int('9' * 400)),
                            ('past the year 9999', 253402300800)):
            with self.subTest(case=case):
                self.put('team', dict(good, written_at=value))
                self.assertEqual(self.line('usage', 'team')[2], 'unknown (usage format)')
        record = dict(good)
        del record['written_at']
        self.put('team', record)
        self.assertEqual(self.line('usage', 'team')[2], 'unknown (usage format)')

    def test_every_other_departure_from_the_usage_format_reads_usage_format(self):
        good = team_usage(self.now - 20, window(12, self.now + 3600), window(30, self.now + DAY))
        text = json.dumps(good)

        def limits(**windows):
            return dict(good, rate_limits=dict(good['rate_limits'], **windows))

        def without(key):
            record = dict(good['rate_limits'])
            del record[key]
            return dict(good, rate_limits=record)
        cases = {
            'a JSON list': [good],
            'rate_limits absent': {k: v for k, v in good.items() if k != 'rate_limits'},
            'rate_limits null': dict(good, rate_limits=None),
            'rate_limits a list': dict(good, rate_limits=[]),
            'five_hour absent': without('five_hour'),
            'seven_day absent': without('seven_day'),
            'a window a list': limits(five_hour=[12, self.now]),
            'a window empty': limits(five_hour={}),
            'used_percentage a string': limits(five_hour=window('12', self.now)),
            'used_percentage negative': limits(five_hour=window(-1, self.now)),
            'used_percentage a boolean': limits(five_hour=window(True, self.now)),
            'used_percentage null': limits(five_hour=window(None, self.now)),
            'used_percentage past a float': text.replace('"used_percentage": 12', '"used_percentage": 1e400').encode(),
            'resets_at a float': limits(seven_day=window(30, self.now + 0.5)),
            'resets_at a string': limits(seven_day=window(30, str(self.now))),
            'resets_at absent': limits(seven_day={'used_percentage': 30}),
            'resets_at past the year 9999': limits(seven_day=window(30, 253402300800)),
            'not UTF-8': text.replace('probe-t_3', 'probe\xff').encode('latin-1'),
            'trailing data': text.encode() + b'}',
            'empty': b'',
        }
        for case, content in cases.items():
            with self.subTest(case=case):
                self.put('team', content)
                self.assertEqual(self.line('usage', 'team'),
                                 ['usage', 'team', 'unknown (usage format)'] + ['-'] * 5)

    def test_a_null_window_prints_dash_for_its_figure_and_its_reset(self):
        self.put('team', team_usage(self.now - 20, None, window(30, self.now + DAY)))
        self.assertEqual(self.line('usage', 'team'), ['usage', 'team', 'measured', '20', '-', '-', '30',
                                                      '2026-10-17T01:00:00Z'])
        self.put('team', team_usage(self.now - 20, None, None))
        status, out, err = self.meters()
        self.assertEqual(status, 0)
        self.assertEqual(records(out, 'usage')[1], ['usage', 'team', 'measured', '20', '-', '-', '-', '-'])

    def test_keys_the_format_does_not_name_are_ignored(self):
        self.put('team', team_usage(self.now - 20, dict(window(12, self.now), extra=[1]), None,
                                    rate_limits_note='x', nested={'a': {'b': None}}))
        self.assertEqual(self.line('usage', 'team')[2], 'measured')

    @unittest.skipIf(os.geteuid() == 0, 'root can read a mode-000 file')
    def test_an_unreadable_file_reads_unreadable_with_its_errno(self):
        os.chmod(self.usage['team'], 0)
        self.assertEqual(self.line('usage', 'team'), ['usage', 'team', 'unknown (unreadable: EACCES)']
                         + ['-'] * 5)


class ExitTests(MetersBase):
    def test_exit_0_when_both_usage_lines_read_measured_and_1_when_either_does_not(self):
        self.assertEqual(self.meters()[0], 0)
        for case, account, content in (
                ('max stale', 'max', max_usage(self.now - 601, None, None)),
                ('team stale', 'team', team_usage(self.now - 601, None, None)),
                ('team in another format', 'team', b'{}')):
            with self.subTest(case=case):
                saved = read(self.usage[account])
                self.put(account, content)
                self.assertEqual(self.meters()[0], 1)
                self.put(account, saved.encode())
        os.unlink(self.usage['max'])
        os.unlink(self.usage['team'])
        self.assertEqual(self.meters()[0], 1)

    def test_no_other_line_changes_the_exit(self):
        self.put_context('team', 'bad-1.json', b'not json')
        self.put_context('max', 'old-1.json', context_record('old-1', self.now - 7 * DAY))
        self.ledger_text('management', ['| another | header |'])
        os.unlink(self.ledger['libs'])
        status, out, err = self.meters()
        self.assertEqual(status, 0)
        self.assertEqual([r[-1] for r in records(out, 'context')],
                         ['stale (10080 min)', 'unknown (context format)'])
        self.assertEqual([r[3] for r in records(out, 'credits')],
                         ['unknown (ledger format)', 'unknown (absent)'])

    def test_a_usage_error_exits_2_with_no_traceback(self):
        for args in (['--bogus'], ['--context-root', 'nolabel'], ['--context-root', '=/x'],
                     ['--ledger', 'libs='], ['--sessions-root', 'with space=/x'], ['--max-usage'],
                     ['extra']):
            with self.subTest(args=args):
                result = self.world.run('meters', *args)
                self.assertEqual((result.returncode, result.stdout), (2, ''))
                self.assertIn('usage: dio', result.stderr)
                self.assertNotIn('Traceback', result.stderr)


class ModelLimitsTests(MetersBase):
    def test_a_max_shaped_file_gives_one_compact_line_in_file_order(self):
        status, out, err = self.meters()
        self.assertEqual(records(out, 'model_limits'), [
            ['model_limits', 'max',
             '{"sonnet":{"used_percentage":3,"resets_at":1792130400},"fable":[12.5,null]}']])

    def test_a_team_shaped_file_gives_none(self):
        status, out, err = self.meters()
        self.assertEqual([r[1] for r in records(out, 'model_limits')], ['max'])
        self.assertNotIn('model_limits', read(self.usage['team']))

    def test_a_stale_file_still_gives_it_and_a_file_not_in_the_usage_format_gives_none(self):
        self.put('max', max_usage(self.now - 3600, None, None))
        self.assertEqual(self.line('usage', 'max')[2], 'stale (60 min)')
        self.assertEqual(len(records(self.meters()[1], 'model_limits')), 1)
        self.put('max', max_usage(self.now - 3600, None, None).replace(
            b'"written_at": %d' % (self.now - 3600), b'"written_at": 1.5'))
        self.assertEqual(self.line('usage', 'max')[2], 'unknown (usage format)')
        self.assertEqual(records(self.meters()[1], 'model_limits'), [])

    def test_a_value_json_cannot_hold_prints_dash(self):
        # Decision 31: 1e400 parses as an infinity, which JSON cannot hold.
        self.put('max', max_usage(self.now - 35, None, None).replace(b'12.5', b'1e400'))
        self.assertEqual(self.line('model_limits', 'max'), ['model_limits', 'max', '-'])
        self.assertEqual(self.line('usage', 'max')[2], 'measured')

    def test_the_json_takes_decision_20s_escapes_and_stays_on_one_line(self):
        self.put('max', max_usage(self.now - 35, None, None).replace(
            b'"fable"', '"a\\tb c\\\\"'.encode()))
        status, out, err = self.meters()
        self.assertEqual(records(out, 'model_limits')[0][2],
                         '{"sonnet":{"used_percentage":3,"resets_at":1792130400},'
                         '"a\\\\tb\\u2028c\\\\\\\\":[12.5,null]}')
        self.assertEqual(len(out.splitlines()), len(out.split('\n')) - 1)


class ContextTests(MetersBase):
    def setUp(self):
        super().setUp()
        self.world.standard()

    def sid(self, pid):
        """The sessionId the fixtures give a sessions file."""
        return '00000000-0000-4000-8000-%012d' % pid

    def context_line(self, account, session_id, *args):
        found = [r for r in records(self.meters(*args)[1], 'context') if r[1:3] == [account, session_id]]
        self.assertEqual(len(found), 1)
        return found[0]

    def test_parse_session_also_returns_the_session_id(self):
        record = self.world.record(self.world.busy, 'probe-t_3', sock=self.world.socket_of(self.world.busy))
        parsed = dio.parse_session(json.dumps(record).encode(), str(self.world.busy))
        self.assertEqual(parsed['sessionId'], self.sid(self.world.busy))
        del record['sessionId']
        self.assertIsNone(dio.parse_session(json.dumps(record).encode(), str(self.world.busy))['sessionId'])

    def test_the_name_is_the_parsed_sessions_files_whose_session_id_is_the_files_id(self):
        w = self.world
        for account, pid, name in (('team', w.busy, 'probe-t_3'), ('team', w.dead, 'probe-t_2'),
                                   ('max', w.max_live, 'probe-m_1')):
            self.put_context(account, self.sid(pid) + '.json',
                             context_record(self.sid(pid), self.now - 5, name='from-statusline'))
        status, out, err = self.meters()
        self.assertEqual((status, err), (0, ''))
        self.assertEqual(records(out, 'context'), [
            ['context', 'max', self.sid(w.max_live), 'probe-m_1', '17', '5', 'measured']] + sorted([
                ['context', 'team', self.sid(w.busy), 'probe-t_3', '17', '5', 'measured'],
                ['context', 'team', self.sid(w.dead), 'probe-t_2', '17', '5', 'measured']]))

    def test_a_file_no_parsed_sessions_file_matches_prints_its_own_session_name_as_statusline(self):
        self.put_context('team', 'ended-1.json', context_record('ended-1', self.now - 3 * DAY,
                                                                name='Ailp-team_14'))
        self.assertEqual(self.context_line('team', 'ended-1'),
                         ['context', 'team', 'ended-1', 'statusline:Ailp-team_14', '17', str(3 * DAY),
                          'stale (4320 min)'])

    def test_with_no_match_and_no_session_name_the_name_is_dash(self):
        record = context_record('anon-1', self.now - 5)
        for case, content in (('null', dict(record, session_name=None)),
                              ('empty', dict(record, session_name='')),
                              ('absent', {k: v for k, v in record.items() if k != 'session_name'})):
            with self.subTest(case=case):
                self.put_context('team', 'anon-1.json', content)
                self.assertEqual(self.context_line('team', 'anon-1')[3], '-')

    def test_a_matching_sessions_file_with_a_null_name_prints_dash_not_the_statusline_name(self):
        pid = self.world.live_process()
        self.world.session(self.world.team_root, self.world.record(pid, None))
        self.put_context('team', self.sid(pid) + '.json', context_record(self.sid(pid), self.now))
        self.assertEqual(self.context_line('team', self.sid(pid))[3], '-')

    def test_a_sessions_file_that_does_not_parse_names_nothing(self):
        pid = self.world.live_process()
        record = self.world.record(pid, 'probe-t_8')
        record['procStart'] = int(record['procStart'])  # a mismatch for dio who's parse
        self.world.session(self.world.team_root, record)
        self.put_context('team', self.sid(pid) + '.json', context_record(self.sid(pid), self.now,
                                                                         name='probe-t_8'))
        self.assertEqual(self.context_line('team', self.sid(pid))[3], 'statusline:probe-t_8')

    def test_when_two_parsed_sessions_files_carry_the_id_the_highest_pid_names_it(self):
        # Decision 26.
        low, high = sorted((self.world.live_process(), self.world.live_process()))
        shared = 'shared-session-1'
        old = self.world.record(low, 'old_1', sessionId=shared)
        new = self.world.record(high, 'new_2', sessionId=shared)
        self.put_context('team', shared + '.json', context_record(shared, self.now))
        for first_root, second_root in ((self.world.max_root, self.world.team_root),
                                        (self.world.team_root, self.world.max_root)):
            with self.subTest(highest_in=second_root):
                for root in (self.world.max_root, self.world.team_root):
                    for pid in (low, high):
                        path = os.path.join(root, '%d.json' % pid)
                        if os.path.exists(path):
                            os.unlink(path)
                self.world.session(first_root, old)
                self.world.session(second_root, new)
                self.assertEqual(self.context_line('team', shared)[3], 'new_2')

    def test_a_null_or_absent_used_percentage_prints_dash(self):
        record = context_record('ctx-1', self.now - 5)
        for case, content in (('null', context_record('ctx-1', self.now - 5, used=None)),
                              ('absent', dict(record, context_window={'total_input_tokens': 1})),
                              ('context_window null', dict(record, context_window=None)),
                              ('context_window absent',
                               {k: v for k, v in record.items() if k != 'context_window'})):
            with self.subTest(case=case):
                self.put_context('team', 'ctx-1.json', content)
                self.assertEqual(self.context_line('team', 'ctx-1')[4:], ['-', '5', 'measured'])

    def test_the_figure_prints_as_the_file_gives_it(self):
        for used, shown in ((17, '17'), (17.25, '17.25'), (0, '0'), (99.0, '99.0')):
            with self.subTest(used=used):
                self.put_context('team', 'ctx-1.json', context_record('ctx-1', self.now, used=used))
                self.assertEqual(self.context_line('team', 'ctx-1')[4], shown)

    def test_the_age_and_state_are_as_for_a_usage_file(self):
        for age, state in ((0, 'measured'), (600, 'measured'), (601, 'stale (10 min)'),
                           (7 * DAY, 'stale (10080 min)')):
            with self.subTest(age=age):
                self.put_context('team', 'ctx-1.json', context_record('ctx-1', self.now - age))
                self.assertEqual(self.context_line('team', 'ctx-1')[5:], [str(age), state])

    def test_only_names_like_the_writers_are_read_and_the_rest_never_opened_or_logged(self):
        skipped = ('.ctx.AbC123', '.ctx.json', 'a.b.json', 'abc.json.tmp', 'ABC.JSON', 'a b.json',
                   'caf\xe9.json', '.json', 'x.json~', 'notes.txt', 'ctx-canary.key')
        for name in skipped:
            self.put_context('team', name, context_record('x', self.now))
        self.put_context('team', 'good-1.json', context_record('good-1', self.now))
        calls, patcher = self.recording_open()
        status, out, err = self.meters()
        patcher.stop()
        self.assertEqual([r[2] for r in records(out, 'context')], ['good-1'])
        opened = {os.path.basename(path) for path, _, _ in calls}
        self.assertIn('good-1.json', opened)
        for name in skipped:
            self.assertNotIn(name, opened)
            self.assertNotIn(name, out + err)

    def test_bad_json_and_every_other_departure_read_context_format(self):
        good = context_record('ctx-1', self.now - 5, name='probe-x_1')
        text = json.dumps(good)
        cases = {
            'not JSON': b'not json', 'half written': text[:40].encode(), 'a JSON list': [good],
            'duplicate key': ('{"written_at": %d, ' % self.now + text[1:]).encode(),
            'NaN': (text[:-1] + ', "x": NaN}').encode(),
            'written_at absent': {k: v for k, v in good.items() if k != 'written_at'},
            'written_at a float': dict(good, written_at=self.now + 0.5),
            'written_at a string': dict(good, written_at=str(self.now)),
            'session_id absent': {k: v for k, v in good.items() if k != 'session_id'},
            'session_id another id': dict(good, session_id='ctx-2'),
            'session_id a number': dict(good, session_id=1),
            'context_window a list': dict(good, context_window=[17]),
            'context_window a number': dict(good, context_window=17),
            'used_percentage a string': context_record('ctx-1', self.now, used='17'),
            'used_percentage negative': context_record('ctx-1', self.now, used=-1),
            'used_percentage a boolean': context_record('ctx-1', self.now, used=True),
            'session_name a number': dict(good, session_name=7),
            'over 64 KiB': dict(good, cwd='/' + 'x' * 70000),
            'not UTF-8': text.replace('probe-x_1', 'probe\xff').encode('latin-1'),
        }
        for case, content in cases.items():
            with self.subTest(case=case):
                self.put_context('team', 'ctx-1.json', content)
                self.assertEqual(self.context_line('team', 'ctx-1'),
                                 ['context', 'team', 'ctx-1', '-', '-', '-', 'unknown (context format)'])

    def test_a_symlink_a_fifo_or_a_directory_named_like_a_context_file_is_refused(self):
        target = self.world.write(self.world.base, 'ctx-target.json', CANARY)
        os.symlink(target, os.path.join(self.context['team'], 'lnk-1.json'))
        os.mkfifo(os.path.join(self.context['team'], 'fifo-1.json'))
        os.mkdir(os.path.join(self.context['team'], 'dir-1.json'))
        result = self.world.run('meters', *self.flags(), timeout=60)
        self.assertEqual(result.returncode, 1, result.stderr)  # the injected clock is not the real one
        self.assertEqual(records(result.stdout, 'context'), [
            ['context', 'team', 'dir-1', '-', '-', '-', 'unknown (refused: not a regular file)'],
            ['context', 'team', 'fifo-1', '-', '-', '-', 'unknown (refused: not a regular file)'],
            ['context', 'team', 'lnk-1', '-', '-', '-', 'unknown (refused: symlink)']])
        self.assertNotIn(CANARY.decode().strip(), result.stdout + result.stderr)

    def test_the_join_holds_for_a_context_file_that_reads_unknown(self):
        sid = self.sid(self.world.busy)
        os.symlink(self.world.write(self.world.base, 't.json', b'{}'),
                   os.path.join(self.context['team'], sid + '.json'))
        self.assertEqual(self.context_line('team', sid),
                         ['context', 'team', sid, 'probe-t_3', '-', '-', 'unknown (refused: symlink)'])

    def test_lines_go_by_account_in_the_order_given_then_by_session_id(self):
        for account, ids in (('max', ('b-2', 'a-1')), ('team', ('a-0', 'Z-9'))):
            for session_id in ids:
                self.put_context(account, session_id + '.json', context_record(session_id, self.now))
        status, out, err = self.meters()
        self.assertEqual([r[1:3] for r in records(out, 'context')],
                         [['max', 'a-1'], ['max', 'b-2'], ['team', 'Z-9'], ['team', 'a-0']])
        status, out, err = self.meters(*self.flags(contexts=('team', 'max')))
        self.assertEqual([r[1:3] for r in records(out, 'context')],
                         [['team', 'Z-9'], ['team', 'a-0'], ['max', 'a-1'], ['max', 'b-2']])
        flags = self.flags(contexts=()) + ['--context-root', 'one=' + self.context['team'],
                                           '--context-root', 'one=' + self.context['max']]
        status, out, err = self.meters(*flags)
        self.assertEqual([r[2] for r in records(out, 'context')], ['Z-9', 'a-0', 'a-1', 'b-2'])

    def test_lines_go_by_session_id_where_the_file_names_sort_another_way(self):
        # Decision 24, D7v's finding 1: `-` and `_` sort either side of the `.` before `json`, so
        # the files' names sort a-1, a, a_1, b while their ids sort a, a-1, a_1, b.
        ids = ('a', 'a-1', 'a_1', 'b')
        self.assertEqual(sorted(i + '.json' for i in ids), ['a-1.json', 'a.json', 'a_1.json', 'b.json'])
        for session_id in reversed(ids):
            self.put_context('team', session_id + '.json', context_record(session_id, self.now))
        status, out, err = self.meters()
        self.assertEqual([r[2] for r in records(out, 'context')], list(ids))

    def test_two_context_directories_under_one_label_merge_into_one_run_by_session_id(self):
        # Decision 24, D7v's finding 1: each directory's ids sort between the other's, so the
        # run is not the first directory's lines followed by the second's.
        for account, ids in (('max', ('b-1', 'd-1')), ('team', ('a-1', 'c-1'))):
            for session_id in ids:
                self.put_context(account, session_id + '.json', context_record(session_id, self.now))
        flags = self.flags(contexts=()) + ['--context-root', 'one=' + self.context['max'],
                                           '--context-root', 'one=' + self.context['team']]
        status, out, err = self.meters(*flags)
        self.assertEqual([r[1:3] for r in records(out, 'context')],
                         [['one', 'a-1'], ['one', 'b-1'], ['one', 'c-1'], ['one', 'd-1']])

    def test_a_context_root_that_cannot_be_read_gives_one_unknown_line(self):
        not_a_directory = self.world.write(self.world.base, 'plain', b'')
        flags = self.flags(contexts=()) + ['--context-root', 'max=' + self.context['max'] + '-absent',
                                           '--context-root', 'team=' + not_a_directory]
        status, out, err = self.meters(*flags)
        self.assertEqual(status, 0)
        self.assertEqual(records(out, 'context'), [
            ['context', 'max', '-', '-', '-', '-', 'unknown (absent)'],
            ['context', 'team', '-', '-', '-', '-', 'unknown (unreadable: ENOTDIR)']])

    def test_a_sessions_root_that_cannot_be_read_is_warned_and_the_lines_still_print(self):
        self.put_context('team', 'ctx-1.json', context_record('ctx-1', self.now, name='n_1'))
        flags = self.flags()
        flags[flags.index('team=' + self.world.team_root)] = 'team=' + self.world.team_root + '-absent'
        status, out, err = self.meters(*flags)
        self.assertEqual(status, 0)
        self.assertIn('dio: cannot read the team sessions directory', err)
        self.assertEqual(self.context_line('team', 'ctx-1', *flags)[3], 'statusline:n_1')

    def test_a_context_file_removed_between_the_listing_and_its_read_is_skipped(self):
        for session_id in ('gone-1', 'kept-1'):
            self.put_context('team', session_id + '.json', context_record(session_id, self.now))
        real_read = dio.read_regular

        def removed_first(name, dir_fd, limit=dio.RECORD_LIMIT):
            if name == 'gone-1.json':
                os.unlink(name, dir_fd=dir_fd)
            return real_read(name, dir_fd, limit)
        with mock.patch.object(dio, 'read_regular', removed_first):
            status, out, err = self.meters()
        self.assertEqual([r[2] for r in records(out, 'context')], ['kept-1'])


class CreditsTests(MetersBase):
    def test_each_row_prints_as_it_is_with_its_pool_team_org_for_a_team_job(self):
        rows = [row('pool-test-team-2026-10-21 (team)'), row('dio-r1-nightly'), row('x(team)'),
                row('(team) first'), row('padded (team)   '), row('team')]
        self.ledger_text('management', [HEADER, SEPARATOR] + rows)
        status, out, err = self.meters()
        self.assertEqual(records(out, 'credits'), [
            ['credits', 'management', pool, 'uncorrected', text] for pool, text in zip(
                ['team-org', 'individual-org', 'individual-org', 'individual-org', 'team-org',
                 'individual-org'], rows)])

    def test_every_row_prints_in_file_order_and_lines_that_are_not_rows_are_skipped(self):
        rows = [row('job-%02d' % n) for n in range(30)]
        self.ledger_text('management', [HEADER, SEPARATOR] + rows[:10] + ['', 'A note.', ' ' + rows[0]]
                         + rows[10:])
        status, out, err = self.meters()
        self.assertEqual([r[4] for r in records(out, 'credits')], rows)

    def test_both_ledgers_print_in_the_order_given_each_labelled_by_its_source(self):
        self.ledger_text('management', [HEADER, SEPARATOR, row('m-1 (team)')])
        self.ledger_text('libs', [HEADER, SEPARATOR, row('l-1'), row('l-2')])
        status, out, err = self.meters()
        self.assertEqual([r[1:3] for r in records(out, 'credits')],
                         [['management', 'team-org'], ['libs', 'individual-org'], ['libs', 'individual-org']])
        status, out, err = self.meters(*self.flags(ledgers=('libs', 'management')))
        self.assertEqual([r[1] for r in records(out, 'credits')], ['libs', 'libs', 'management'])

    def test_a_tab_a_backslash_a_control_or_a_byte_not_utf8_in_a_row_takes_decision_20s_escapes(self):
        lines = [row('a\tb'), row('c\\d'), row('e\x1bf'), row('g h'), row('i\udcffj')]
        self.ledger_text('management', [HEADER, SEPARATOR] + lines, ending='\r\n')
        status, out, err = self.meters()
        self.assertEqual(len(out.splitlines()), len(out.split('\n')) - 1)
        shown = [r[4] for r in records(out, 'credits')]
        for text, escaped in zip(shown, ('a\\x09b', 'c\\\\d', 'e\\x1bf', 'g\\u2028h', 'i\\xffj')):
            self.assertIn(' %s ' % escaped, text)
            self.assertTrue(text.endswith('| 0 |\\x0d'), text)

    def test_another_header_or_no_separator_gives_one_ledger_format_line(self):
        for case, lines, shown in (
                ('another header', ['| started | ended | job | model | turns | cost | status |',
                                    SEPARATOR, row('j')],
                 '| started | ended | job | model | turns | cost | status |'),
                ('the header renamed', [HEADER.replace('cost', 'price'), SEPARATOR, row('j')],
                 HEADER.replace('cost', 'price')),
                ('no header', [SEPARATOR, row('j')], SEPARATOR),
                ('a row where the separator goes', [HEADER, row('j')], row('j')),
                ('a separator of 7 cells', [HEADER, '|---|---|---|---|---|---|---|', row('j')],
                 '|---|---|---|---|---|---|---|'),
                ('the header alone', [HEADER], '-'),
                ('empty', [], '-')):
            with self.subTest(case=case):
                self.ledger_text('management', lines)
                status, out, err = self.meters()
                self.assertEqual([r for r in records(out, 'credits') if r[1] == 'management'],
                                 [['credits', 'management', '-', 'unknown (ledger format)', shown]])

    def test_a_separator_with_alignment_colons_and_cell_spacing_is_a_separator(self):
        self.ledger_text('management', ['|  started|ended | job | model | turns | cost | status | rc',
                                        '| :--- | ---: | :-: | - | --- | --- | --- | --- |', row('j')])
        self.assertEqual(self.line('credits', 'management')[2:4], ['individual-org', 'uncorrected'])

    def test_a_cell_loses_any_whitespace_around_it_tabs_and_no_break_spaces_included(self):
        # Decision 33, as D7v's finding 3 has it worded: what str.strip() removes, not spaces alone.
        header = HEADER.replace(' started ', '\tstarted\t').replace(' rc ', ' rc ')
        separator = SEPARATOR.replace('|---|', '|\t--- |', 1)
        self.ledger_text('management', [header, separator, row('tabbed (team)\t'), row('nbsp (team)')])
        status, out, err = self.meters()
        self.assertEqual([r[2:4] for r in records(out, 'credits') if r[1] == 'management'],
                         [['team-org', 'uncorrected'], ['individual-org', 'uncorrected']])

    def test_a_row_of_7_or_9_cells_gives_a_ledger_format_line_and_the_other_rows_still_print(self):
        seven = '| a | b | c | d | e | f | g |'
        nine = row('j') + ' extra |'
        self.ledger_text('management', [HEADER, SEPARATOR, row('one'), seven, nine, row('two')])
        status, out, err = self.meters()
        self.assertEqual([r for r in records(out, 'credits') if r[1] == 'management'], [
            ['credits', 'management', 'individual-org', 'uncorrected', row('one')],
            ['credits', 'management', '-', 'unknown (ledger format)', seven],
            ['credits', 'management', '-', 'unknown (ledger format)', nine],
            ['credits', 'management', 'individual-org', 'uncorrected', row('two')]])

    def test_no_ledger_reads_unknown_absent_and_a_link_or_directory_is_refused(self):
        os.unlink(self.ledger['libs'])
        self.assertEqual(self.line('credits', 'libs'), ['credits', 'libs', '-', 'unknown (absent)', '-'])
        os.symlink(self.ledger['management'], self.ledger['libs'])
        self.assertEqual(self.line('credits', 'libs')[3], 'unknown (refused: symlink)')
        os.unlink(self.ledger['libs'])
        os.mkdir(self.ledger['libs'])
        self.assertEqual(self.line('credits', 'libs')[3], 'unknown (refused: not a regular file)')

    def test_a_ledger_over_1_mib_reads_ledger_format_and_one_of_1_mib_reads(self):
        base = HEADER + '\n' + SEPARATOR + '\n' + row('j') + '\n'
        mib = 1024 * 1024  # FINISH.md's 1 MiB, written out so the test does not follow the code
        for size, shown in ((mib, ['individual-org', 'uncorrected']),
                            (mib + 1, ['-', 'unknown (ledger format)'])):
            with self.subTest(size=size):
                with open(self.ledger['management'], 'w', encoding='utf-8') as f:
                    f.write(base + 'x' * (size - len(base) - 1) + '\n')
                self.assertEqual(os.path.getsize(self.ledger['management']), size)
                self.assertEqual(self.line('credits', 'management')[2:4], shown)


class OutputTests(MetersBase):
    def test_the_lines_come_by_kind_usage_model_limits_context_credits_each_on_one_line(self):
        self.put_context('max', 'm-1.json', context_record('m-1', self.now))
        self.put_context('team', 't-1.json', context_record('t-1', self.now))
        self.ledger_text('libs', [HEADER, SEPARATOR, row('l-1')])
        status, out, err = self.meters()
        self.assertEqual((status, err), (0, ''))
        self.assertTrue(out.endswith('\n'))
        lines = records(out)
        self.assertEqual([r[0] for r in lines], ['usage', 'usage', 'model_limits', 'context', 'context',
                                                 'credits'])
        self.assertEqual([r[1] for r in lines], ['max', 'team', 'max', 'max', 'team', 'libs'])
        for line in lines:
            self.assertEqual(len(line), FIELDS[line[0]], line)

    def test_a_name_from_either_file_takes_decision_20s_escapes(self):
        self.world.standard()
        pid = self.world.live_process()
        self.world.session(self.world.team_root, self.world.record(
            pid, 'probe x\\y', sessionId='joined-1'))
        self.put_context('team', 'joined-1.json', context_record('joined-1', self.now))
        self.put_context('team', 'own-1.json', context_record('own-1', self.now, name='a\nb\tc'))
        status, out, err = self.meters()
        self.assertEqual(len(out.splitlines()), len(out.split('\n')) - 1)
        self.assertEqual([r[2:4] for r in records(out, 'context')],
                         [['joined-1', 'probe\\u2028x\\\\y'], ['own-1', 'statusline:a\\x0ab\\x09c']])

    def test_the_help_names_every_flag_and_its_default_under_home(self):
        result = self.world.run('meters', '--help', COLUMNS='1000')  # argparse wraps at hyphens
        self.assertEqual(result.returncode, 0, result.stderr)
        text = ' '.join(result.stdout.split())
        for words in ('--max-usage PATH', '~/.claude/usage-latest.json', '--team-usage PATH',
                      '~/Team/CONFIG/usage-latest.json', '--context-root LABEL=PATH',
                      'max=~/.claude/context', 'team=~/Team/CONFIG/context', '--ledger LABEL=PATH',
                      'management=~/Workspace/MANAGEMENT/credits/LEDGER.md',
                      'libs=~/Workspace/REPOS/nitpick-libs/.internal/credits/LEDGER.md',
                      '--sessions-root LABEL=PATH', 'max=~/.claude/sessions',
                      'team=~/.claude-team/sessions'):
            with self.subTest(words=words):
                self.assertIn(words, text)


class NoFlagTests(MetersBase):
    def test_the_defaults_are_finish_md_s_paths_all_under_home(self):
        home = self.world.home
        self.assertEqual(dio.default_usage_files(), [
            ('max', os.path.join(home, '.claude', 'usage-latest.json')),
            ('team', os.path.join(home, 'Team', 'CONFIG', 'usage-latest.json'))])
        self.assertEqual(dio.default_context_roots(), [
            ('max', os.path.join(home, '.claude', 'context')),
            ('team', os.path.join(home, 'Team', 'CONFIG', 'context'))])
        self.assertEqual(dio.default_ledgers(), [
            ('management', os.path.join(home, 'Workspace', 'MANAGEMENT', 'credits', 'LEDGER.md')),
            ('libs', os.path.join(home, 'Workspace', 'REPOS', 'nitpick-libs', '.internal', 'credits',
                                  'LEDGER.md'))])

    def test_with_no_flag_every_path_dio_meters_opens_is_under_home(self):
        home = os.path.realpath(self.world.home)
        self.place_defaults(self.now)
        calls, patcher = self.recording_open()
        status, out, err = self.meters_without_flags()
        patcher.stop()
        self.assertEqual((status, err), (0, ''))
        resolved = {os.path.realpath(os.path.join(where, path) if where else path)
                    for path, _, where in calls}
        defaults = ([path for _, path in dio.default_usage_files() + dio.default_ledgers()]
                    + [root for _, root in dio.default_context_roots() + dio.default_sessions_roots()])
        self.assertLessEqual({os.path.realpath(path) for path in defaults}, resolved)  # not blind
        for path in resolved:
            self.assertTrue(path.startswith(home + os.sep), path)

    def test_the_built_dio_with_no_flag_reads_the_files_at_their_defaults_under_home(self):
        self.place_defaults(int(time.time()))
        result = self.world.run('meters')
        self.assertEqual((result.returncode, result.stderr), (0, ''))
        lines = records(result.stdout)
        self.assertEqual([r[:2] for r in lines], [
            ['usage', 'max'], ['usage', 'team'], ['model_limits', 'max'], ['context', 'max'],
            ['context', 'team'], ['credits', 'management'], ['credits', 'libs']])
        self.assertEqual([r[2] for r in lines[:2]], ['measured', 'measured'])
        self.assertEqual([r[2:4] for r in lines[3:5]], [['m-1', 'statusline:probe-t_3'],
                                                        ['t-1', 'probe-t_9']])
        self.assertEqual([r[2] for r in lines[5:]], ['team-org', 'individual-org'])

    def place_defaults(self, now):
        """A usage file, a context file and a ledger at each default under HOME, and a sessions
        file under the Team default that names the Team context file's session."""
        home = self.world.home
        paths = dict(dio.default_usage_files())
        for account, content in (('max', max_usage(now - 35, window(42, now + 7200), None)),
                                 ('team', team_usage(now - 20, None, window(30, now + DAY)))):
            os.makedirs(os.path.dirname(paths[account]), exist_ok=True)
            self.world.write(os.path.dirname(paths[account]), 'usage-latest.json', content)
        for (account, root), session_id in zip(dio.default_context_roots(), ('m-1', 't-1')):
            os.makedirs(root)
            self.world.write(root, session_id + '.json', context_record(session_id, now - 5))
        for (source, path), job in zip(dio.default_ledgers(), ('m (team)', 'l')):
            os.makedirs(os.path.dirname(path))
            with open(path, 'w', encoding='utf-8') as f:
                f.write('\n'.join([HEADER, SEPARATOR, row(job)]) + '\n')
        for config in ('.claude', '.claude-team'):
            os.makedirs(os.path.join(home, config, 'sessions'))
        pid = self.world.live_process()
        self.world.session(os.path.join(home, '.claude-team', 'sessions'),
                           self.world.record(pid, 'probe-t_9', sessionId='t-1'))

    def meters_without_flags(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = dio.main(['meters'], now=self.clock)
        return status, out.getvalue(), err.getvalue()


class MetersStraceTests(MetersBase):
    def test_under_strace_the_standard_world_opens_no_key_path_and_writes_nothing(self):
        # FINISH.md step 7: the standard world under strace -f -e trace=%file, with no .key path
        # opened, nothing opened for writing, and no rename, link, unlink or directory made.
        self.assertIsNotNone(shutil.which('strace'), 'strace is required')
        w = self.world.standard()
        now = int(time.time())
        self.put('max', max_usage(now - 35, window(42, now + 7200), None))
        self.put('team', team_usage(now - 20, None, window(30, now + DAY)))
        sid = '00000000-0000-4000-8000-%012d' % w.busy
        self.put_context('team', sid + '.json', context_record(sid, now - 5))
        skipped = ('.ctx.AbC123', 'notes.txt', 'ctx-canary.key')
        for name in skipped:
            self.put_context('team', name, CANARY)
        self.ledger_text('management', [HEADER, SEPARATOR, row('m-1 (team)')])
        trace = os.path.join(w.base, 'meters.trace')
        result = subprocess.run(['strace', '-f', '-e', 'trace=%file', '-o', trace, DIO, 'meters']
                                + self.flags(), env=w.env(), capture_output=True, text=True,
                                timeout=120)
        self.assertEqual((result.returncode, result.stderr), (0, ''))
        self.assertEqual(records(result.stdout, 'context')[0][3], 'probe-t_3')
        with open(trace, encoding='utf-8', errors='replace') as f:
            lines = [line for line in f.read().splitlines() if CALL.match(line)]

        def naming(name):
            return [line for line in lines if '"%s"' % name in line or '/%s"' % name in line]
        # The trace is not blind: it holds the opens of each kind of file dio meters reads.
        for name in ('usage-latest.json', sid + '.json', 'LEDGER.md', '%d.json' % w.busy, '123.json'):
            self.assertTrue([line for line in naming(name) if CALL.match(line).group(1) == 'openat'],
                            name)
        self.assertEqual([line for line in lines if '.key' in line], [])
        for name in ('123.key', SECOND_CANARY) + skipped:
            self.assertEqual(naming(name), [], name)
        writes = [line for line in lines if re.search(r'O_WRONLY|O_RDWR|O_CREAT|O_TRUNC', line)
                  or CALL.match(line).group(1) in WRITE_CALLS]
        self.assertEqual(writes, [])
        self.assertNotIn(CANARY.decode().strip(), result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
