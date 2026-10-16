"""dio who and dio register (MIN.md step 1): every rule, each output form, the ambiguity
exit, the grace with an injected clock, and role resolution against a test role file.

Run from the repository root, with TMPDIR set to a scratch directory (tests/README.md):

    TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -v
"""

import contextlib
import io
import json
import os
import shutil
import stat
import subprocess
import unittest
from datetime import datetime, timedelta
from unittest import mock

import fixtures
from fixtures import (CANARY, DIO, JUNK, REPOSITORY, SECOND_CANARY, TORN, TORN_BYTES, VERSION,
                      Clock, World, proc_start)

dio = fixtures.load_dio()


def setUpModule():
    fixtures.require_tmpdir()


def table(output):
    """{(account, pid): {column: cell}} from a dio who table, cut at the header's offsets."""
    lines = output.splitlines()
    starts = [lines[0].index(name) for name in dio.HEADER]
    bounds = list(zip(starts, starts[1:] + [None]))
    rows = {}
    for line in lines[1:]:
        cells = {name: line[a:b].strip() for name, (a, b) in zip(dio.HEADER, bounds)}
        rows[(cells['ACCOUNT'], cells['PID'])] = cells
    return rows


class Base(unittest.TestCase):
    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)
        home = mock.patch.dict(os.environ, {'HOME': self.world.home})
        home.start()
        self.addCleanup(home.stop)
        self.clock = Clock()

    def main(self, *args, environ=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                status = dio.main(list(args), now=self.clock, environ=environ or {})
            except SystemExit as e:
                status = e.code
        return status, out.getvalue(), err.getvalue()

    def who(self, *extra):
        """dio who over the world; `extra` comes last, so a repeated flag in it wins."""
        return self.main('who', *(self.world.who_flags() + list(extra)))

    def state(self, pid, account='team', *extra):
        status, out, err = self.who(*extra)
        self.assertEqual(status, 0, err)
        return table(out)[(account, str(pid))]['STATE']

    def grace_entry(self, pid, config_dir=None):
        config_dir = config_dir or os.path.dirname(self.world.team_root)
        name = dio.GraceCache.entry_name(config_dir, pid)
        with open(os.path.join(self.world.state, 'cache', name), encoding='utf-8') as f:
            return json.load(f)

    def recording_open(self):
        """Patch os.open for one call of dio; returns the list it records (path, flags, dir_fd) into."""
        calls, real_open = [], os.open

        def record(path, flags, mode=0o777, *, dir_fd=None):
            calls.append((path, flags, dir_fd))
            return real_open(path, flags, mode, dir_fd=dir_fd)
        patcher = mock.patch.object(dio.os, 'open', record)
        patcher.start()
        self.addCleanup(patcher.stop)
        return calls, patcher


class ReaderTests(Base):
    def setUp(self):
        super().setUp()
        self.world.standard()

    def test_only_names_matching_digits_dot_json_become_rows(self):
        status, out, err = self.who()
        self.assertEqual(status, 0, err)
        w, rows = self.world, table(out)
        self.assertEqual({pid for account, pid in rows if account == 'team'},
                         {'123', TORN, str(w.dead), str(w.reused), str(w.busy), str(w.idle)})
        self.assertEqual({pid for account, pid in rows if account == 'max'}, {str(w.max_live)})

    def test_entries_that_do_not_match_are_never_opened_or_logged(self):
        calls, patcher = self.recording_open()
        status, out, err = self.who()
        patcher.stop()
        opened = {os.path.basename(path) for path, _, _ in calls}
        for name in JUNK + ('123.key', SECOND_CANARY):
            self.assertNotIn(name, opened)
            self.assertNotIn(name, out + err)

    def test_no_path_dio_opens_names_a_key_file(self):
        calls, patcher = self.recording_open()
        self.who()
        patcher.stop()
        self.assertIn('%d.json' % self.world.busy, [path for path, _, _ in calls])
        self.assertEqual([path for path, _, _ in calls if '.key' in path], [])

    def test_entries_that_do_not_match_are_named_by_no_system_call_that_takes_a_path(self):
        # Never opened, stat'ed or named at all: strace's %file class traces every system call
        # that takes a path, the stat family (newfstatat, statx and the rest) included.
        self.assertIsNotNone(shutil.which('strace'), 'strace is required')
        trace = os.path.join(self.world.base, 'file.trace')
        result = subprocess.run(['strace', '-f', '-e', 'trace=%file', '-o', trace, DIO, 'who']
                                + self.world.who_flags(), env=self.world.env(),
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(trace, encoding='utf-8', errors='replace') as f:
            lines = f.read().splitlines()

        def naming(name):
            return [line for line in lines if '"%s"' % name in line or '/%s"' % name in line]
        # The trace is not blind: it holds a matching name's open and its socket's stat.
        self.assertTrue(naming('%d.json' % self.world.busy))
        self.assertTrue([line for line in naming('%d.sock' % self.world.busy) if 'stat' in line])
        for name in JUNK + ('123.key', SECOND_CANARY):
            self.assertEqual(naming(name), [], name)

    def test_matches_are_opened_with_o_nofollow_relative_to_the_listed_directory(self):
        calls, patcher = self.recording_open()
        self.who()
        patcher.stop()
        matches = [(flags, dir_fd) for path, flags, dir_fd in calls if path.endswith('.json')
                   and not path.startswith('grace-') and not path.startswith('.tmp-')]
        self.assertGreaterEqual(len(matches), 7)
        for flags, dir_fd in matches:
            self.assertTrue(flags & os.O_NOFOLLOW and flags & os.O_NONBLOCK)
            self.assertIsNotNone(dir_fd)

    def test_symlink_named_123_json_is_refused_and_its_target_never_read(self):
        calls, patcher = self.recording_open()
        status, out, err = self.who()
        patcher.stop()
        self.assertEqual(table(out)[('team', '123')]['STATE'], 'unknown (refused: symlink)')
        flags = [f for path, f, _ in calls if path == '123.json']
        self.assertEqual(len(flags), 1)
        self.assertTrue(flags[0] & os.O_NOFOLLOW)
        self.assertNotIn(CANARY.decode().strip(), out + err)

    def test_fifo_named_like_a_sessions_file_is_refused_without_blocking(self):
        os.mkfifo(os.path.join(self.world.team_root, '999.json'))
        result = self.world.run('who', *self.world.who_flags(), timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(table(result.stdout)[('team', '999')]['STATE'],
                         'unknown (refused: not a regular file)')

    def test_directory_named_like_a_sessions_file_is_refused(self):
        os.mkdir(os.path.join(self.world.team_root, '998.json'))
        self.assertEqual(self.state(998), 'unknown (refused: not a regular file)')

    def test_socket_file_named_like_a_sessions_file_is_refused(self):
        self.world.listen('997.json', self.world.team_root)
        self.assertEqual(self.state(997), 'unknown (refused: not a regular file)')

    @unittest.skipIf(os.geteuid() == 0, 'root can read a mode-000 file')
    def test_unreadable_sessions_file_reads_unreadable(self):
        path = self.world.session(self.world.team_root, self.world.record(
            self.world.live_process(), 'probe-t_8'))
        os.chmod(path, 0)
        self.assertEqual(self.state(os.path.basename(path)[:-5]), 'unknown (unreadable: EACCES)')

    def test_a_missing_sessions_directory_is_reported_and_the_other_still_read(self):
        status, out, err = self.main('who', '--sessions-root', 'max=' + self.world.max_root,
                                     '--sessions-root', 'team=' + self.world.team_root + '-absent',
                                     '--state-root', self.world.state)
        self.assertEqual(status, 0)
        self.assertIn('cannot read the team sessions directory', err)
        self.assertEqual(table(out)[('max', str(self.world.max_live))]['STATE'], 'live')


class ParseTests(Base):
    def setUp(self):
        super().setUp()
        self.world.standard()

    def test_half_written_json_reads_as_a_sessions_format_mismatch(self):
        self.assertEqual(self.state(TORN), 'unknown (sessions format: %s)' % VERSION)

    def test_a_mismatch_with_no_version_anywhere_reads_version_unknown(self):
        root = self.world.make('cfg-other', 'sessions')
        self.world.write(root, TORN + '.json', TORN_BYTES)
        status, out, err = self.main('who', '--sessions-root', 'other=' + root,
                                     '--state-root', self.world.state)
        self.assertEqual(table(out)[('other', TORN)]['STATE'],
                         'unknown (sessions format: version unknown)')

    def test_a_mismatched_file_shows_its_own_version_when_readable(self):
        pid = self.world.live_process()
        record = self.world.record(pid, 'probe-t_8', version='9.9.9')
        record['procStart'] = int(record['procStart'])
        self.world.session(self.world.team_root, record)
        self.assertEqual(self.state(pid), 'unknown (sessions format: 9.9.9)')

    def test_every_listed_field_is_checked_strictly(self):
        pid = self.world.live_process()
        good = self.world.record(pid, 'probe-t_8')
        root = self.world.make('cfg-strict', 'sessions')

        def without(key):
            record = dict(good)
            del record[key]
            return record
        cases = {
            'pid missing': without('pid'),
            'pid a string': dict(good, pid=str(pid)),
            'pid a boolean': dict(good, pid=True),
            'pid not the number in the file name': dict(good, pid=pid + 1),
            'procStart missing': without('procStart'),
            'procStart a number': dict(good, procStart=int(good['procStart'])),
            'procStart not digits': dict(good, procStart='12a'),
            'messagingSocketPath missing': without('messagingSocketPath'),
            'messagingSocketPath relative': dict(good, messagingSocketPath='socks/1.sock'),
            'messagingSocketPath with a newline': dict(good, messagingSocketPath='/x\n.sock'),
            'sessionId a number': dict(good, sessionId=5),
            'cwd null': dict(good, cwd=None),
            'name a number': dict(good, name=7),
            'name with an escape character': dict(good, name='probe\x1b[2J'),
            'status not one of the four': dict(good, status='parked'),
            'status a list': dict(good, status=['idle']),
            'startedAt a string': dict(good, startedAt='2026-10-15'),
            'updatedAt negative': dict(good, updatedAt=-1),
            'version a number': dict(good, version=2),
            'a JSON list': [good],
            'duplicate keys': ('{"pid": %d, "pid": %d, "procStart": "%s", "messagingSocketPath": "%s"}'
                               % (pid, pid, good['procStart'], good['messagingSocketPath'])).encode(),
            'NaN': json.dumps(good)[:-1].encode() + b', "updatedAt2": NaN}',
            'not UTF-8': json.dumps(dict(good, name='x')).encode().replace(b'"x"', b'"\xff"'),
            'trailing data': json.dumps(good).encode() + b'}',
            'larger than 64 KiB': json.dumps(dict(good, cwd='/' + 'x' * 70000)).encode(),
        }
        self.world.write(root, '%d.json' % pid, good)
        status, out, err = self.main('who', '--sessions-root', 'team=' + root, '--state-root', self.world.state)
        self.assertEqual(table(out)[('team', str(pid))]['STATE'], 'live')
        for case, content in cases.items():
            with self.subTest(case=case):
                self.world.write(root, '%d.json' % pid, content)
                status, out, err = self.main('who', '--sessions-root', 'team=' + root,
                                             '--state-root', self.world.state)
                self.assertTrue(table(out)[('team', str(pid))]['STATE'].startswith(
                    'unknown (sessions format: '), case)

    def test_a_name_with_leading_zeros_is_a_mismatch(self):
        pid = self.world.live_process()
        self.world.write(self.world.team_root, '0%d.json' % pid, self.world.record(pid, 'probe-t_8'))
        self.assertTrue(self.state('0%d' % pid).startswith('unknown (sessions format: '))

    def test_keys_the_plan_does_not_list_are_ignored(self):
        pid = self.world.live_process()
        self.world.session(self.world.team_root, self.world.record(
            pid, 'probe-t_8', peerFeatures=['x'], pidDomain='d', entrypoint='cli', nameSince=1,
            statusUpdatedAt=2, somethingNew={'nested': [1, 2]}))
        self.assertEqual(self.state(pid), 'live')

    def test_a_null_or_absent_name_is_accepted(self):
        null_pid, absent_pid = self.world.live_process(), self.world.live_process()
        self.world.session(self.world.team_root, self.world.record(null_pid, None))
        record = self.world.record(absent_pid, 'x')
        del record['name']
        self.world.session(self.world.team_root, record)
        status, out, err = self.who()
        rows = table(out)
        for pid in (null_pid, absent_pid):
            self.assertEqual(rows[('team', str(pid))]['NAME'], '-')
            self.assertEqual(rows[('team', str(pid))]['STATE'], 'live')


class ProcessCheckTests(Base):
    def setUp(self):
        super().setUp()
        self.world.standard()

    def test_a_live_process_with_status_busy_reads_live(self):
        self.assertEqual(self.state(self.world.busy), 'live')

    def test_a_live_process_with_status_idle_reads_live_idle(self):
        self.assertEqual(self.state(self.world.idle), 'live-idle')

    def test_status_shell_waiting_or_absent_reads_live(self):
        pids = {}
        for status in ('shell', 'waiting', None):
            pid = self.world.live_process()
            record = self.world.record(pid, 'probe-t_%d' % (20 + len(pids)), status=status or 'busy')
            if status is None:
                del record['status']
            self.world.session(self.world.team_root, record)
            pids[status] = pid
        status, out, err = self.who()
        for pid in pids.values():
            self.assertEqual(table(out)[('team', str(pid))]['STATE'], 'live')

    def test_a_reused_pid_with_a_different_procstart_fails_the_check(self):
        self.assertEqual(self.state(self.world.reused), dio.CHECKING)
        self.assertEqual(self.grace_entry(self.world.reused)['failedCheck'], 'start time differs')

    def test_a_dead_pid_fails_the_check(self):
        self.assertEqual(self.state(self.world.dead), dio.CHECKING)
        self.assertEqual(self.grace_entry(self.world.dead)['failedCheck'], 'no process')

    def test_a_missing_socket_file_fails_the_check(self):
        pid = self.world.live_process()
        self.world.session(self.world.team_root, self.world.record(
            pid, 'probe-t_8', sock=os.path.join(self.world.socks, 'absent.sock')))
        self.assertEqual(self.state(pid), dio.CHECKING)
        self.assertEqual(self.grace_entry(pid)['failedCheck'], 'no socket file')

    def test_a_socket_path_that_is_not_a_socket_fails_the_check(self):
        pid = self.world.live_process()
        plain = self.world.write(self.world.socks, 'plain.sock', b'')
        self.world.session(self.world.team_root, self.world.record(pid, 'probe-t_8', sock=plain))
        self.assertEqual(self.state(pid), dio.CHECKING)
        self.assertEqual(self.grace_entry(pid)['failedCheck'], 'not a socket')

    def test_a_live_session_under_a_path_longer_than_108_bytes_reads_live(self):
        deep = self.world.make('d' * 120)
        root = self.world.make('d' * 120, 'sessions')
        pid = self.world.live_process()
        sock = self.world.listen('%d.sock' % pid, deep)
        self.assertGreater(len(sock.encode()), 108)
        self.world.session(root, self.world.record(pid, 'probe-t_8', sock=sock))
        flags = ['--sessions-root', 'team=' + root, '--state-root', self.world.state,
                 '--roles', self.world.roles]
        result = self.world.run('who', *flags)
        self.assertEqual(result.returncode, 0, result.stderr)
        row = table(result.stdout)[('team', str(pid))]
        self.assertEqual((row['SOCKET'], row['STATE']), (sock, 'live'))
        result = self.world.run('who', '--address', 'probe-t_8', *flags)
        self.assertEqual((result.returncode, result.stdout), (0, sock + '\n'))

    @unittest.skipIf(os.geteuid() == 0, 'root can search a mode-000 directory')
    def test_a_socket_dio_cannot_examine_reads_no_process_check_and_starts_no_grace(self):
        locked = self.world.make('locked')
        pid = self.world.live_process()
        self.world.session(self.world.team_root, self.world.record(
            pid, 'probe-t_8', sock=os.path.join(locked, '%d.sock' % pid)))
        os.chmod(locked, 0)  # the pid and start time pass; the socket's stat gets EACCES
        self.addCleanup(os.chmod, locked, 0o700)
        self.assertEqual(self.state(pid), 'unknown (no process check: EACCES)')
        self.assertNotIn(dio.GraceCache.entry_name(os.path.dirname(self.world.team_root), pid),
                         self.world.cache_files())

    def test_the_account_is_the_directory_read(self):
        status, out, err = self.main('who', '--sessions-root', 'team=' + self.world.max_root,
                                     '--sessions-root', 'max=' + self.world.team_root,
                                     '--state-root', self.world.state)
        rows = table(out)
        self.assertEqual(rows[('team', str(self.world.max_live))]['NAME'], 'probe-m_1')
        self.assertEqual(rows[('max', str(self.world.busy))]['NAME'], 'probe-t_3')

    def test_the_start_time_is_field_22_of_proc_stat(self):
        self.assertEqual(dio.proc_start_of(os.getpid()), proc_start(os.getpid()))
        self.assertEqual(dio.proc_start_of(self.world.busy), proc_start(self.world.busy))
        self.assertIsNone(dio.proc_start_of(self.world.dead))


class GraceTests(Base):
    def dead_world(self, name='probe-t_2'):
        dead = self.world.dead_pid()
        self.world.session(self.world.team_root, self.world.record(
            dead, name, start='100', sock=os.path.join(self.world.socks, 'gone.sock')))
        return dead

    def test_a_failed_check_reads_checking_until_60_seconds_then_gone(self):
        dead = self.dead_world()  # the texts are M6's, so they are written out, not dio.CHECKING
        self.assertEqual(self.state(dead), 'unknown (checking)')
        self.clock.advance(59.999999)
        self.assertEqual(self.state(dead), 'unknown (checking)')
        self.clock.advance(0.000001)
        self.assertEqual(self.state(dead), 'gone')

    def test_the_built_dio_prints_m6s_texts_unknown_checking_then_gone(self):
        # M6 reads these two texts off a terminal, so they are pinned as the built dio prints
        # them on the real clock. Before the second run, the entry's times move back 61 s.
        dead = self.dead_world()
        flags = ['--sessions-root', 'team=' + self.world.team_root, '--state-root', self.world.state]
        result = self.world.run('who', *flags)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(table(result.stdout)[('team', str(dead))]['STATE'], 'unknown (checking)')
        path = os.path.join(self.world.state, 'cache',
                            dio.GraceCache.entry_name(os.path.dirname(self.world.team_root), dead))
        with open(path, encoding='utf-8') as f:
            entry = json.load(f)
        for key in ('firstFailedAt', 'goneAt'):
            moment = datetime.strptime(entry[key], '%Y-%m-%dT%H:%M:%S.%fZ') - timedelta(seconds=61)
            entry[key] = moment.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(entry, f)
        result = self.world.run('who', *flags)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(table(result.stdout)[('team', str(dead))]['STATE'], 'gone')

    def test_the_entry_holds_absolute_utc_times_with_the_grace_beside_them(self):
        dead = self.dead_world()
        self.state(dead)
        entry = self.grace_entry(dead)
        self.assertEqual(entry, {
            'configDir': os.path.dirname(self.world.team_root), 'pid': dead, 'procStart': '100',
            'failedCheck': 'no process', 'firstFailedAt': '2026-10-16T01:00:00.000000Z',
            'graceSeconds': 60, 'goneAt': '2026-10-16T01:01:00.000000Z'})
        name = dio.GraceCache.entry_name(os.path.dirname(self.world.team_root), dead)
        self.assertEqual(stat.S_IMODE(os.stat(os.path.join(self.world.state, 'cache', name)).st_mode)
                         & 0o077, 0)

    def test_entries_are_keyed_by_config_dir_and_pid(self):
        dead = self.dead_world()
        self.world.session(self.world.max_root, self.world.record(
            dead, 'probe-m_2', start='100', sock=os.path.join(self.world.socks, 'gone.sock')))
        self.who()
        names = [n for n in self.world.cache_files() if n.startswith('grace-')]
        self.assertEqual(len(names), 2)
        for root in (self.world.team_root, self.world.max_root):
            config_dir = os.path.dirname(root)
            self.assertIn(dio.GraceCache.entry_name(config_dir, dead), names)
            self.assertEqual(self.grace_entry(dead, config_dir)['configDir'], config_dir)

    def test_a_passing_check_removes_the_entry(self):
        pid = self.world.live_process()
        self.world.session(self.world.team_root, self.world.record(
            pid, 'probe-t_8', sock=self.world.socket_of(pid)))
        self.assertEqual(self.state(pid), dio.CHECKING)
        self.assertEqual(len(self.world.cache_files()), 1)
        self.world.listen('%d.sock' % pid)
        self.assertEqual(self.state(pid), 'live')
        self.assertEqual(self.world.cache_files(), [])

    def test_an_entry_for_an_earlier_process_with_the_same_pid_restarts_the_grace(self):
        dead = self.dead_world()
        self.state(dead)
        self.clock.advance(120)
        self.world.session(self.world.team_root, self.world.record(
            dead, 'probe-t_2', start='200', sock=os.path.join(self.world.socks, 'gone.sock')))
        self.assertEqual(self.state(dead), dio.CHECKING)
        entry = self.grace_entry(dead)
        self.assertEqual((entry['procStart'], entry['firstFailedAt']), ('200', '2026-10-16T01:02:00.000000Z'))

    def test_the_first_writers_time_stands_when_two_runs_race(self):
        dead = self.dead_world()
        self.state(dead)
        self.clock.advance(70)
        real_load, loads = dio.GraceCache._load, []

        def load_blind_once(cache, name):
            loads.append(name)  # the first load misses the entry another run has just written
            return (False, None) if len(loads) == 1 else real_load(cache, name)
        with mock.patch.object(dio.GraceCache, '_load', load_blind_once):
            self.assertEqual(self.state(dead), dio.GONE)
        self.assertEqual(len(loads), 2)
        self.assertEqual(self.grace_entry(dead)['firstFailedAt'], '2026-10-16T01:00:00.000000Z')
        self.assertFalse([n for n in self.world.cache_files() if n.startswith('.tmp-')])

    def test_entries_for_pids_without_a_file_or_roster_entry_are_pruned(self):
        dead = self.dead_world()
        self.state(dead)
        cache = os.path.join(self.world.state, 'cache')
        orphan = dio.GraceCache.entry_name(os.path.dirname(self.world.team_root), 31337)
        elsewhere = dio.GraceCache.entry_name('/nowhere/cfg', 31337)
        for name in (orphan, elsewhere):
            with open(os.path.join(cache, name), 'w') as f:
                f.write('{}')
        self.who()
        files = self.world.cache_files()
        self.assertNotIn(orphan, files)
        self.assertIn(elsewhere, files)
        self.assertIn(dio.GraceCache.entry_name(os.path.dirname(self.world.team_root), dead), files)

    def test_without_a_writable_cache_a_failed_check_stays_checking(self):
        dead = self.dead_world()
        args = ['who', '--sessions-root', 'team=' + self.world.team_root,
                '--state-root', os.path.join(self.world.base, 'absent')]
        status, out, err = self.main(*args)
        self.assertIn('the grace cache cannot be written', err)
        self.clock.advance(600)
        status, out, err = self.main(*args)
        self.assertEqual(table(out)[('team', str(dead))]['STATE'], dio.CHECKING)

    def test_a_symlinked_cache_directory_is_never_written_through(self):
        dead = self.dead_world()
        elsewhere = self.world.make('elsewhere')
        os.symlink(elsewhere, os.path.join(self.world.state, 'cache'))
        status, out, err = self.who()
        self.assertIn('the grace cache cannot be written', err)
        self.assertEqual(table(out)[('team', str(dead))]['STATE'], dio.CHECKING)
        self.assertEqual(os.listdir(elsewhere), [])


class OutputTests(Base):
    def setUp(self):
        super().setUp()
        self.world.standard()

    def resolve(self, *args):
        return self.who('--address', *args)

    def test_who_prints_the_columns_for_both_accounts(self):
        status, out, err = self.who()
        self.assertEqual(out.splitlines()[0].split(), list(dio.HEADER))
        rows = table(out)
        self.assertEqual({account for account, _ in rows}, {'max', 'team'})
        busy = rows[('team', str(self.world.busy))]
        self.assertEqual((busy['NAME'], busy['VERSION'], busy['SOCKET']),
                         ('probe-t_3', VERSION, self.world.socket_of(self.world.busy)))
        self.assertRegex(busy['STARTED'], r'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$')
        self.assertEqual(rows[('team', '123')]['SOCKET'], '-')

    def test_prefix_lists_live_matches_only_sorted_by_the_trailing_number(self):
        for name in ('probe-t_10', 'probe-t_9'):
            pid = self.world.live_process()
            self.world.session(self.world.team_root, self.world.record(pid, name))
        status, out, err = self.who('--prefix', 'probe-t')
        self.assertEqual(status, 0, err)
        names = [line.split()[1] for line in out.splitlines()[1:]]
        self.assertEqual(names, ['probe-t_3', 'probe-t_4', 'probe-t_9', 'probe-t_10'])

    def test_prefix_matches_every_name_that_starts_with_it(self):
        status, out, err = self.who('--prefix', 'probe')
        names = [line.split()[1] for line in out.splitlines()[1:]]
        self.assertEqual(names, ['probe-m_1', 'probe-t_3', 'probe-t_4'])

    def test_prefix_with_no_live_match_exits_1(self):
        status, out, err = self.who('--prefix', 'nobody')
        self.assertEqual((status, out), (1, ''))
        self.assertIn('no live session', err)

    def test_address_of_a_role_prints_its_holders_socket(self):
        self.assertEqual(self.resolve('team-seat'), (0, self.world.socket_of(self.world.busy) + '\n', ''))

    def test_address_of_an_exact_live_name_prints_its_socket(self):
        self.assertEqual(self.resolve('probe-t_4'), (0, self.world.socket_of(self.world.idle) + '\n', ''))

    def test_address_of_a_bare_prefix_with_one_live_match_prints_it(self):
        self.assertEqual(self.resolve('probe-m'), (0, self.world.socket_of(self.world.max_live) + '\n', ''))

    def test_address_of_a_bare_prefix_with_several_live_is_ambiguous_and_exits_1(self):
        status, out, err = self.resolve('probe-t')
        self.assertEqual(status, 1)
        self.assertEqual(out.splitlines(), [
            '%s  probe-t_3  team' % self.world.socket_of(self.world.busy),
            '%s  probe-t_4  team' % self.world.socket_of(self.world.idle),
            'ambiguous: 2 live'])

    def test_address_highest_picks_the_highest_trailing_number(self):
        status, out, err = self.resolve('probe-t', '--highest')
        self.assertEqual((status, out), (0, self.world.socket_of(self.world.idle) + '\n'))
        self.assertIn('--highest chose probe-t_4 of 2 live', err)

    def test_address_of_a_role_with_no_live_holder_exits_1(self):
        status, out, err = self.resolve('ghost')
        self.assertEqual((status, out), (1, ''))
        self.assertIn('ghost = nobody_9: no live holder', err)

    def test_address_of_a_role_with_two_holders_resolves_the_one_live(self):
        self.assertEqual(self.resolve('poster')[:2], (0, self.world.socket_of(self.world.max_live) + '\n'))

    def test_address_tries_a_role_before_an_exact_name_equal_to_it(self):
        pid = self.world.live_process()  # a live session named team-seat, the role's own name
        self.world.session(self.world.team_root, self.world.record(pid, 'team-seat'))
        self.assertEqual(self.resolve('team-seat'), (0, self.world.socket_of(self.world.busy) + '\n', ''))

    def test_address_tries_an_exact_name_before_a_bare_prefix(self):
        pid = self.world.live_process()  # live as probe-t, beside the live probe-t_3 and probe-t_4
        self.world.session(self.world.team_root, self.world.record(pid, 'probe-t'))
        self.assertEqual(self.resolve('probe-t'), (0, self.world.socket_of(pid) + '\n', ''))

    def test_an_exact_name_live_twice_is_ambiguous_even_with_highest(self):
        pid = self.world.live_process()  # a second live probe-t_4, on the other account
        self.world.session(self.world.max_root, self.world.record(pid, 'probe-t_4'))
        for extra in ((), ('--highest',)):
            status, out, err = self.resolve('probe-t_4', *extra)
            self.assertEqual(status, 1, extra)
            self.assertEqual(out.splitlines(), [
                '%s  probe-t_4  max' % self.world.socket_of(pid),
                '%s  probe-t_4  team' % self.world.socket_of(self.world.idle),
                'ambiguous: 2 live'], extra)

    def test_a_role_with_several_live_holders_is_ambiguous_even_with_highest(self):
        with open(self.world.roles, 'w') as f:
            f.write('```\npair = probe-t_3, probe-t_4\n```\n')
        status, out, err = self.resolve('pair', '--highest')
        self.assertEqual(status, 1)
        self.assertEqual(out.splitlines()[-1], 'ambiguous: 2 live')

    def test_lines_outside_the_fenced_block_are_not_roles(self):
        for outside in ('outside', 'after'):
            status, out, err = self.resolve(outside)
            self.assertEqual((status, out), (1, ''))
            self.assertIn('no live session for %s' % outside, err)

    def test_a_session_that_is_not_live_does_not_resolve(self):
        for name in ('probe-t_2', 'probe-t_1'):  # dead, and a reused pid
            self.assertEqual(self.resolve(name)[:2], (1, ''))

    def test_a_bare_prefix_never_reaches_a_longer_name(self):
        pid = self.world.live_process()
        self.world.session(self.world.team_root, self.world.record(pid, 'probe-t_10'))
        self.assertEqual(self.resolve('probe-t_1')[:2], (1, ''))

    def test_a_malformed_role_file_exits_2(self):
        with open(self.world.roles, 'w') as f:
            f.write('```\nteam-seat probe-t_3\n```\n')
        status, out, err = self.resolve('team-seat')
        self.assertEqual((status, out), (2, ''))
        self.assertIn('not a role line', err)

    def test_a_missing_role_file_still_resolves_names(self):
        status, out, err = self.resolve('probe-t_4', '--roles', self.world.roles + '-absent')
        self.assertEqual((status, out), (0, self.world.socket_of(self.world.idle) + '\n'))
        self.assertIn('no role file', err)

    def test_highest_without_address_is_a_usage_error(self):
        status, out, err = self.who('--highest')
        self.assertEqual(status, 2)
        self.assertIn('--highest needs --address', err)


class RegisterTests(Base):
    def setUp(self):
        super().setUp()
        self.pid = self.world.live_process()
        self.sock = self.world.listen('%d.sock' % self.pid)
        self.config_dir = os.path.dirname(self.world.team_root)

    def environ(self, **changes):
        environ = {'CLAUDE_CODE_MESSAGING_SOCKET': self.sock, 'CLAUDE_CONFIG_DIR': self.config_dir}
        environ.update(changes)
        return {k: v for k, v in environ.items() if v is not None}

    def register(self, name, *args, **changes):
        return self.main('register', name, '--state-root', self.world.state, *args,
                         environ=self.environ(**changes))

    def roster(self):
        roster = os.path.join(self.world.state, 'roster')
        names = sorted(os.listdir(roster)) if os.path.isdir(roster) else []
        entries = []
        for name in names:
            with open(os.path.join(roster, name), encoding='utf-8') as f:
                entries.append((name, json.load(f)))
        return entries

    def test_register_writes_name_socket_pid_and_start_time_into_the_roster(self):
        status, out, err = self.register('probe-t_5')
        self.assertEqual(status, 0, err)
        [(name, entry)] = self.roster()
        self.assertEqual(name, '%s-%d.json' % (dio.config_key(self.config_dir), self.pid))
        self.assertEqual(entry, {'configDir': self.config_dir, 'messagingSocketPath': self.sock,
                                 'name': 'probe-t_5', 'pid': self.pid,
                                 'procStart': proc_start(self.pid),
                                 'registeredAt': '2026-10-16T01:00:00.000000Z'})
        path = os.path.join(self.world.state, 'roster', name)
        self.assertEqual(stat.S_IMODE(os.stat(path).st_mode) & 0o077, 0)

    def test_register_output_is_labelled_as_the_fallback(self):
        status, out, err = self.register('probe-t_5')
        self.assertEqual(out, 'registered probe-t_5  pid %d  %s  fallback: register\n' % (self.pid, self.sock))

    def test_register_refuses_without_the_socket_variable(self):
        status, out, err = self.register('probe-t_5', CLAUDE_CODE_MESSAGING_SOCKET=None)
        self.assertEqual(status, 1)
        self.assertIn('CLAUDE_CODE_MESSAGING_SOCKET is not set', err)
        self.assertEqual(self.roster(), [])

    def test_register_takes_the_pid_from_the_socket_name_or_from_pid(self):
        other = self.world.listen('seat.sock')
        status, out, err = self.register('probe-t_5', CLAUDE_CODE_MESSAGING_SOCKET=other)
        self.assertEqual(status, 1)
        self.assertIn('pass --pid', err)
        status, out, err = self.register('probe-t_5', '--pid', str(self.pid), CLAUDE_CODE_MESSAGING_SOCKET=other)
        self.assertEqual(status, 0, err)
        self.assertEqual(self.roster()[0][1]['pid'], self.pid)

    def test_register_refuses_a_pid_with_no_process(self):
        dead = self.world.dead_pid()
        status, out, err = self.register('probe-t_5', '--pid', str(dead))
        self.assertEqual(status, 1)
        self.assertIn('no process %d' % dead, err)

    def test_register_refuses_a_socket_path_that_is_not_a_socket(self):
        plain = self.world.write(self.world.socks, 'plain-%d.sock' % self.pid, b'')
        status, out, err = self.register('probe-t_5', '--pid', str(self.pid),
                                         CLAUDE_CODE_MESSAGING_SOCKET=plain)
        self.assertEqual(status, 1)
        self.assertIn('no socket at', err)

    def test_the_zone_directories_dio_makes_have_mode_0700(self):
        umask = os.umask(0)  # so each mode is exactly the one dio asks mkdir for
        try:
            self.main('who', '--sessions-root', 'team=' + self.world.team_root,
                      '--state-root', self.world.state)
            status, out, err = self.register('probe-t_5')
        finally:
            os.umask(umask)
        self.assertEqual(status, 0, err)
        for leaf in ('cache', 'roster'):
            mode = os.lstat(os.path.join(self.world.state, leaf)).st_mode
            self.assertTrue(stat.S_ISDIR(mode), leaf)
            self.assertEqual(stat.S_IMODE(mode), 0o700, leaf)

    def test_register_refuses_a_name_with_control_characters(self):
        self.assertEqual(self.register('probe\nt_5')[0], 2)

    def test_register_keys_the_entry_by_the_config_dir(self):
        self.register('probe-t_5', CLAUDE_CONFIG_DIR=None)
        self.assertEqual(self.roster()[0][1]['configDir'], os.path.join(self.world.home, '.claude'))
        other = os.path.join(self.world.base, 'cfg-other')
        self.register('probe-t_5', '--config-dir', other)
        self.assertEqual(sorted(e['configDir'] for _, e in self.roster()),
                         sorted([os.path.join(self.world.home, '.claude'), other]))

    def test_a_new_registration_from_the_same_session_replaces_the_old(self):
        self.register('probe-t_5')
        self.register('probe-t_6')
        self.assertEqual([e['name'] for _, e in self.roster()], ['probe-t_6'])

    def test_who_shows_a_roster_only_seat_labelled_fallback_register(self):
        self.register('probe-t_5')
        status, out, err = self.who()
        row = table(out)[('team', str(self.pid))]
        self.assertEqual((row['NAME'], row['STATE']), ('probe-t_5', 'live  fallback: register'))

    def test_address_and_prefix_resolve_a_roster_only_seat_with_its_label(self):
        self.register('probe-t_5')
        self.assertEqual(self.who('--address', 'probe-t_5')[:2], (0, self.sock + '  fallback: register\n'))
        status, out, err = self.who('--prefix', 'probe-t')
        self.assertTrue(out.splitlines()[1].endswith('live  fallback: register'))

    def test_a_roster_entry_is_hidden_when_its_sessions_file_parses(self):
        self.register('probe-t_5')
        self.world.session(self.world.team_root, self.world.record(self.pid, 'probe-t_5', sock=self.sock))
        status, out, err = self.who()
        self.assertNotIn('fallback: register', out)
        self.assertEqual(table(out)[('team', str(self.pid))]['STATE'], 'live')

    def test_a_roster_entry_is_shown_when_its_sessions_file_is_a_mismatch(self):
        self.register('probe-t_5')
        self.world.write(self.world.team_root, '%d.json' % self.pid, b'{"pid": ')
        status, out, err = self.who()
        lines = [line for line in out.splitlines() if ' %d ' % self.pid in line]
        self.assertEqual(len(lines), 2)
        self.assertTrue(any(line.endswith('live  fallback: register') for line in lines))
        self.assertTrue(any('unknown (sessions format: ' in line for line in lines))

    def test_a_roster_entry_for_a_dead_process_goes_through_the_grace(self):
        self.register('probe-t_5')
        self.world.children[0].stdin.close()
        self.world.children[0].wait()
        self.assertEqual(table(self.who()[1])[('team', str(self.pid))]['STATE'],
                         'unknown (checking)  fallback: register')
        self.clock.advance(60)
        self.assertEqual(table(self.who()[1])[('team', str(self.pid))]['STATE'],
                         'gone  fallback: register')

    def test_a_roster_entry_not_in_the_format_is_ignored_with_a_warning(self):
        self.register('probe-t_5')
        [(name, entry)] = self.roster()
        with open(os.path.join(self.world.state, 'roster', name), 'w') as f:
            json.dump(dict(entry, extra=1), f)
        status, out, err = self.who()
        self.assertIn("ignored roster entry %s: not in dio register's format" % name, err)
        self.assertNotIn('fallback: register', out)


LONG_N = 'probe-t_' + '7' * 5000  # int() refuses more than 4300 digits by default
HUGE = int('9' * 400)  # too large for a float: math.isfinite raises OverflowError


class CraftedNumberTests(Base):
    """A number in a crafted file that int() or a float cannot hold gives a row or a warning,
    never a traceback, in dio who and under --prefix and --address. Each case runs the
    built src/dio, so the exit status is the process's own."""

    def setUp(self):
        super().setUp()
        self.world.standard()

    def run_who(self, *args):
        result = self.world.run('who', *args, *self.world.who_flags())
        self.assertNotIn('Traceback', result.stderr)
        return result

    def names(self, output):
        return [line.split()[1] for line in output.splitlines()[1:]]

    def register(self, name, pid):
        sock = self.world.listen('%d.sock' % pid)
        result = self.world.run('register', name, '--state-root', self.world.state,
                                CLAUDE_CODE_MESSAGING_SOCKET=sock,
                                CLAUDE_CONFIG_DIR=os.path.dirname(self.world.team_root))
        self.assertEqual(result.returncode, 0, result.stderr)
        return sock

    def test_a_400_digit_integer_startedat_or_updatedat_reads_as_a_sessions_format_mismatch(self):
        for field in ('startedAt', 'updatedAt'):
            with self.subTest(field=field):
                pid = self.world.live_process()
                path = self.world.session(self.world.team_root,
                                          self.world.record(pid, 'probe-t_8', **{field: HUGE}))
                result = self.run_who()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(table(result.stdout)[('team', str(pid))]['STATE'],
                                 'unknown (sessions format: %s)' % VERSION)
                result = self.run_who('--prefix', 'probe-t')
                self.assertEqual((result.returncode, self.names(result.stdout)),
                                 (0, ['probe-t_3', 'probe-t_4']))
                result = self.run_who('--address', 'probe-t_8')
                self.assertEqual((result.returncode, result.stdout), (1, ''))
                self.assertIn('no live session for probe-t_8', result.stderr)
                os.unlink(path)

    def test_a_400_digit_integer_in_a_roster_entry_leaves_it_out_with_the_warning(self):
        pid = self.world.live_process()
        self.register('probe-t_5', pid)
        name = '%s-%d.json' % (dio.config_key(os.path.dirname(self.world.team_root)), pid)
        path = os.path.join(self.world.state, 'roster', name)
        with open(path, encoding='utf-8') as f:
            entry = json.load(f)
        for case, crafted in (('as its pid', dict(entry, pid=HUGE)),
                              ('as an added startedAt', dict(entry, startedAt=HUGE))):
            with self.subTest(case=case):
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(crafted, f)
                result = self.run_who()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn(('team', str(pid)), table(result.stdout))
                self.assertIn("ignored roster entry %s: not in dio register's format" % name,
                              result.stderr)
                result = self.run_who('--prefix', 'probe-t')
                self.assertEqual((result.returncode, self.names(result.stdout)),
                                 (0, ['probe-t_3', 'probe-t_4']))
                result = self.run_who('--address', 'probe-t_5')
                self.assertEqual((result.returncode, result.stdout), (1, ''))

    def test_a_name_ending_in_a_5000_digit_n_gives_its_row_from_a_sessions_file(self):
        pid = self.world.live_process()
        self.world.session(self.world.team_root, self.world.record(pid, LONG_N))
        sock = self.world.socket_of(pid)
        result = self.run_who()
        self.assertEqual(result.returncode, 0, result.stderr)
        row = table(result.stdout)[('team', str(pid))]
        self.assertEqual((row['NAME'], row['SOCKET'], row['STATE']), (LONG_N, sock, 'live'))
        result = self.run_who('--prefix', 'probe-t')
        self.assertEqual((result.returncode, self.names(result.stdout)),
                         (0, ['probe-t_3', 'probe-t_4', LONG_N]))
        result = self.run_who('--address', LONG_N)
        self.assertEqual((result.returncode, result.stdout), (0, sock + '\n'))
        result = self.run_who('--address', 'probe-t')
        self.assertEqual((result.returncode, result.stdout.splitlines()[-1]), (1, 'ambiguous: 3 live'))
        result = self.run_who('--address', 'probe-t', '--highest')
        self.assertEqual((result.returncode, result.stdout), (0, sock + '\n'))

    def test_a_name_ending_in_a_5000_digit_n_gives_its_fallback_row_from_a_roster_entry(self):
        pid = self.world.live_process()
        sock = self.register(LONG_N, pid)
        result = self.run_who()
        self.assertEqual(result.returncode, 0, result.stderr)
        row = table(result.stdout)[('team', str(pid))]
        self.assertEqual((row['NAME'], row['SOCKET'], row['STATE']),
                         (LONG_N, sock, 'live  fallback: register'))
        result = self.run_who('--prefix', 'probe-t')
        self.assertEqual((result.returncode, self.names(result.stdout)),
                         (0, ['probe-t_3', 'probe-t_4', LONG_N]))
        self.assertTrue(result.stdout.splitlines()[-1].endswith('live  fallback: register'))
        result = self.run_who('--address', LONG_N)
        self.assertEqual((result.returncode, result.stdout), (0, sock + '  fallback: register\n'))
        result = self.run_who('--address', 'probe-t')
        self.assertEqual((result.returncode, result.stdout.splitlines()[-1]), (1, 'ambiguous: 3 live'))
        result = self.run_who('--address', 'probe-t', '--highest')
        self.assertEqual((result.returncode, result.stdout), (0, sock + '  fallback: register\n'))


class DefaultsTests(Base):
    def test_the_defaults_are_the_plans_paths(self):
        home = self.world.home
        self.assertEqual(dio.default_sessions_roots(), [
            ('max', os.path.join(home, '.claude', 'sessions')),
            ('team', os.path.join(home, '.claude-team', 'sessions'))])
        self.assertEqual(dio.default_state_root(), os.path.join(home, '.local', 'share', 'diogenes'))
        self.assertEqual(dio.default_role_file(),
                         os.path.join(os.path.realpath(REPOSITORY), 'meta', 'ROLES.md'))

    def test_who_and_register_without_flags_use_the_defaults_under_home(self):
        home = self.world.home
        sessions = os.path.join(home, '.claude-team', 'sessions')
        zone = os.path.join(home, '.local', 'share', 'diogenes')
        os.makedirs(sessions)
        os.makedirs(zone)
        pid = self.world.live_process()
        self.world.session(sessions, self.world.record(pid, 'probe-t_7'))
        result = self.world.run('who')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('cannot read the max sessions directory', result.stderr)
        self.assertEqual(table(result.stdout)[('team', str(pid))]['STATE'], 'live')
        result = self.world.run('register', 'probe-t_7',
                                CLAUDE_CODE_MESSAGING_SOCKET=self.world.socket_of(pid),
                                CLAUDE_CONFIG_DIR=os.path.join(home, '.claude-team'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(os.listdir(os.path.join(zone, 'roster')),
                         ['%s-%d.json' % (dio.config_key(os.path.join(home, '.claude-team')), pid)])
        result = self.world.run('who', '--address', 'team-seat')
        self.assertEqual(result.returncode, 1)
        self.assertIn('team-seat = ', result.stderr)  # read from this repository's meta/ROLES.md
        self.assertIn('no live holder', result.stderr)


class EntryPointTests(Base):
    def test_dio_runs_through_its_shebang_in_isolated_mode(self):
        self.world.standard()
        plant = self.world.make('plant')
        marker = os.path.join(self.world.base, 'planted-module-ran')
        with open(os.path.join(plant, 'json.py'), 'w') as f:
            f.write('open(%r, "w").close()\nraise SystemExit(9)\n' % marker)
        result = self.world.run('who', *self.world.who_flags(), PYTHONPATH=plant)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(os.path.exists(marker))

    def test_no_bytecode_is_written_under_src(self):
        self.world.standard()
        self.world.run('who', *self.world.who_flags())
        self.assertFalse(os.path.exists(os.path.join(REPOSITORY, 'src', '__pycache__')))


class StaticTests(unittest.TestCase):
    def test_the_source_never_names_a_key_file(self):
        with open(DIO, 'rb') as f:
            self.assertNotIn(b'.key', f.read())

    def test_no_file_in_src_or_tests_holds_a_team_path(self):
        team_path = ('/home/' + 'randy/Team').encode()
        for top in ('src', 'tests'):
            for dirpath, dirnames, filenames in os.walk(os.path.join(REPOSITORY, top)):
                for name in filenames:
                    with open(os.path.join(dirpath, name), 'rb') as f:
                        self.assertNotIn(team_path, f.read(), os.path.join(dirpath, name))


if __name__ == '__main__':
    unittest.main()
