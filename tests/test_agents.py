"""dio who --agents (FINISH.md step 8b): the `claude agents --json --all` fallback. Each config
dir's listing, with CLAUDE_CONFIG_DIR removed for the default ~/.claude and set to the dir
otherwise, once per config dir with its first root's label, and still for a dir whose sessions
directory is missing; the rows it adds for live sessions that no sessions file or roster entry
covers, and none for those they cover; the stopped row with no pid key, passed over; output not
in the format, a top-level value that is not an array among it, a non-zero exit, a signal, the
timeout and a command that cannot be started, each one row for its dir; an interrupt while dio
waits, which kills the listing's process group with SIGKILL and then reaps the child; --address
never reaching a listed row; and no process at all without --agents.

The listing comes from a fake claude, a /bin/sh script the test writes into its temporary tree,
which records each run's pid, its arguments, its stdin, and CLAUDE_CONFIG_DIR alone, by name:
whether it is set, and its value. It prints the fixture its config dir holds. The fixtures are
built from the shapes in DX-18's record (meta/research/done/dx18-probe-2026-10-22/: 8a's
interactive rows and its stopped background row) and from r1b:272 (a running background row,
documented, not measured), never from a real listing. Every run that could start a process names
the fake with --agents-command or has PATH hold only the fake's directory, so no test reaches a
real claude. No test runs strace, and none sleeps: the timeout is main's agents_timeout, 0.2 s
in its test, and only the fake waits. The interrupt is a real SIGINT to the test's own process,
in which dio runs: the fake sends it to its parent when the test, inside dio's call that waits
on the listing, has read the fake's `ready` line and sent it SIGUSR1.

Run from the repository root, with TMPDIR set to a scratch directory (tests/README.md):

    TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -v
"""

import contextlib
import inspect
import io
import json
import os
import select
import shlex
import signal
import subprocess
import time
import unittest
from unittest import mock

import fixtures
from fixtures import TORN, Clock, World, proc_start

dio = fixtures.load_dio()
LABEL = '  fallback: claude agents'
STARTED_AT = 1792112724000  # a listing's startedAt is milliseconds since the epoch, as at 8a
# The fake claude. @DEFAULT@ is the test's ~/.claude and @LOG@ its record, both shell-quoted.
FAKE = r'''#!/bin/sh
# A fake claude for tests/test_agents.py, which writes it into its temporary tree. Each run
# appends one line to the log: its pid, its arguments, its stdin (/dev/null or other), and
# CLAUDE_CONFIG_DIR alone, by name: set and its value, or unset and -. It then acts for the config
# dir that variable names, else the test's ~/.claude. If agents.hang is there, it starts a child
# that waits, records that child's pid, and waits itself, so only dio's timeout ends it. If
# agents.interrupt is there, it sets SIGUSR1 to send SIGINT to its parent, dio's process, starts
# and records such a child, prints `ready` and waits, so only dio's kill ends it. It writes
# agents.err to its stderr and agents.json to its stdout, ends by SIGTERM if agents.signal is
# there, and exits with the number in agents.exit, else 0.
if [ -n "${CLAUDE_CONFIG_DIR+x}" ]; then
    config=$CLAUDE_CONFIG_DIR state=set value=$CLAUDE_CONFIG_DIR
else
    config=@DEFAULT@ state=unset value=-
fi
if [ /proc/$$/fd/0 -ef /dev/null ]; then stdin=/dev/null; else stdin=other; fi
printf '%s\t%s\t%s\t%s\t%s\n' "$$" "$*" "$stdin" "$state" "$value" >> @LOG@
if [ -e "$config/agents.hang" ]; then
    /bin/sleep 300 &
    printf '%s\n' "$!" > "$config/agents.child"
    wait
fi
if [ -e "$config/agents.interrupt" ]; then
    trap 'kill -INT $PPID' USR1
    /bin/sleep 300 &
    printf '%s\n' "$!" > "$config/agents.child"
    printf 'ready\n'
    wait
    wait
fi
if [ -e "$config/agents.err" ]; then /bin/cat "$config/agents.err" >&2; fi
if [ -e "$config/agents.json" ]; then /bin/cat "$config/agents.json"; fi
if [ -e "$config/agents.signal" ]; then kill -TERM $$; fi
if [ -e "$config/agents.exit" ]; then exit "$(/bin/cat "$config/agents.exit")"; fi
exit 0
'''


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


def session_id(number):
    """A made-up sessionId, shaped like the fixtures' (fixtures.World.record)."""
    return '00000000-0000-4000-8000-%012d' % number


def interactive(pid, name, status='idle', **extra):
    """A live interactive row with the keys 8a's listing gave every such row: cwd, kind, name,
    pid, sessionId, startedAt and status (DX-18's record)."""
    row = {'cwd': '/', 'kind': 'interactive', 'name': name, 'pid': pid, 'sessionId': session_id(pid),
           'startedAt': STARTED_AT, 'status': status}
    row.update(extra)
    return row


def stopped_background(name='probe-bg_1'):
    """The stopped background row with 8a's keys: cwd, id, kind, name, sessionId, startedAt and
    state, and no pid or status key at all (FINISH.md, "Step 8a's merge"). The id is made up: the
    record gives its key, not its form."""
    return {'cwd': '/', 'id': 'bg-0001', 'kind': 'background', 'name': name,
            'sessionId': '00000000-0000-4000-9000-000000000001', 'startedAt': STARTED_AT,
            'state': 'stopped'}


def running_background(pid, name, status='busy'):
    """A running background row as r1b:272 documents it, documented, not measured: the stopped
    row's keys with state `working`, and a pid and a status."""
    return dict(stopped_background(name), id='bg-%d' % pid, sessionId=session_id(pid),
                state='working', pid=pid, status=status)


class AgentsBase(unittest.TestCase):
    """The standard world, a fake claude, and an empty listing in both config dirs."""

    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)
        home = mock.patch.dict(os.environ, {'HOME': self.world.home})
        home.start()
        self.addCleanup(home.stop)
        self.clock = Clock()
        self.world.standard()
        self.max_dir = os.path.dirname(self.world.max_root)
        self.team_dir = os.path.dirname(self.world.team_root)
        self.default = os.path.join(self.world.home, '.claude')  # what dio takes for ~/.claude
        self.bin = self.world.make('bin')
        self.fake = os.path.join(self.bin, 'claude')
        self.log = os.path.join(self.world.base, 'agents.log')
        with open(self.fake, 'w', encoding='utf-8') as f:
            f.write(FAKE.replace('@DEFAULT@', shlex.quote(self.default))
                    .replace('@LOG@', shlex.quote(self.log)))
        os.chmod(self.fake, 0o755)
        # main's environment for the in-process runs: PATH holds only the fake's directory.
        self.environ = {'HOME': self.world.home, 'PATH': self.bin}
        for config_dir in (self.max_dir, self.team_dir):
            self.list_in(config_dir, [])

    # -- building

    def list_in(self, config_dir, listing=None, status=None, err=None, hang=False, killed=False,
                interrupt=False):
        """What the fake does for `config_dir`: print `listing` (rows as JSON, or bytes as they
        are), write `err` to its stderr, exit with `status`, end by SIGTERM, wait until killed,
        or, with `interrupt`, print `ready`, send dio SIGINT on SIGUSR1, and wait until killed."""
        os.makedirs(config_dir, exist_ok=True)
        if listing is not None:
            data = listing if isinstance(listing, bytes) else json.dumps(listing).encode()
            self.world.write(config_dir, 'agents.json', data)
        if status is not None:
            self.world.write(config_dir, 'agents.exit', b'%d\n' % status)
        if err is not None:
            self.world.write(config_dir, 'agents.err', err)
        for name, wanted in (('agents.hang', hang), ('agents.signal', killed),
                             ('agents.interrupt', interrupt)):
            if wanted:
                self.world.write(config_dir, name, b'')

    # -- running

    def main(self, *args, environ=None, timeout=None):
        out, err = io.StringIO(), io.StringIO()
        extra = {} if timeout is None else {'agents_timeout': timeout}
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                status = dio.main(list(args), now=self.clock,
                                  environ=self.environ if environ is None else environ, **extra)
            except SystemExit as e:
                status = e.code
        return status, out.getvalue(), err.getvalue()

    def who(self, *extra):
        """dio who over the world, without --agents; `extra` comes last."""
        return self.main('who', *(self.world.who_flags() + list(extra)))

    def agents(self, *extra, timeout=None):
        """dio who --agents over the world, the fake named by --agents-command; `extra` comes last."""
        return self.main('who', '--agents', '--agents-command', self.fake,
                         *(self.world.who_flags() + list(extra)), timeout=timeout)

    def runs(self):
        """The fake's record: per run, (pid, arguments, stdin, set or unset, CLAUDE_CONFIG_DIR or -)."""
        if not os.path.exists(self.log):
            return []
        with open(self.log, encoding='utf-8') as f:
            return [tuple(line.rstrip('\n').split('\t', 4)) for line in f]

    def lines_for(self, out, pid):
        return [line for line in out.splitlines()[1:] if line.split()[2] == str(pid)]


class RowTests(AgentsBase):
    def test_sessions_their_sessions_files_cover_add_no_row_so_the_output_is_dio_whos(self):
        # As at 8a (T9): every listed live session has its sessions file, so --agents adds no row.
        w = self.world
        self.list_in(self.team_dir, [interactive(w.busy, 'probe-t_3', 'busy'),
                                     interactive(w.idle, 'probe-t_4', 'idle'), stopped_background()])
        self.list_in(self.max_dir, [interactive(w.max_live, 'probe-m_1', 'busy')])
        plain = self.who()
        self.assertEqual(self.runs(), [])
        self.assertEqual(plain[0], 0)
        self.assertEqual(self.agents(), plain)
        self.assertEqual(len(self.runs()), 2)

    def test_a_live_session_no_sessions_file_covers_is_a_row_labelled_fallback_claude_agents(self):
        pid = self.world.live_process()
        self.list_in(self.team_dir, [interactive(self.world.busy, 'probe-t_3', 'busy'),
                                     interactive(pid, 'probe-t_5', 'idle')])
        status, out, err = self.agents()
        self.assertEqual((status, err), (0, ''))
        self.assertEqual(table(out)[('team', str(pid))], {
            'ACCOUNT': 'team', 'NAME': 'probe-t_5', 'PID': str(pid),
            'STARTED': dio.started_text(proc_start(pid), dio.boot_clock()), 'VERSION': '-',
            'SOCKET': '-', 'STATE': 'live-idle' + LABEL})
        self.assertEqual([line for line in out.splitlines() if line.endswith(LABEL)],
                         self.lines_for(out, pid))

    def test_busy_and_waiting_read_live_and_idle_reads_live_idle(self):
        pids = {status: self.world.live_process() for status in ('busy', 'waiting', 'idle')}
        self.list_in(self.team_dir, [interactive(pid, 'probe-t_%d' % (5 + n), status)
                                     for n, (status, pid) in enumerate(pids.items())])
        rows = table(self.agents()[1])
        self.assertEqual({status: rows[('team', str(pid))]['STATE'] for status, pid in pids.items()},
                         {'busy': 'live' + LABEL, 'waiting': 'live' + LABEL, 'idle': 'live-idle' + LABEL})

    def test_an_interactive_row_and_a_running_background_row_each_give_a_row(self):
        # Each kind: 8a's interactive shape, and r1b:272's running background row, state working
        # with a pid and a status, documented, not measured.
        shell, worker = self.world.live_process(), self.world.live_process()
        self.list_in(self.team_dir, [interactive(shell, 'probe-t_5', 'busy'),
                                     running_background(worker, 'probe-bg_2', 'idle')])
        rows = table(self.agents()[1])
        self.assertEqual((rows[('team', str(shell))]['NAME'], rows[('team', str(shell))]['STATE']),
                         ('probe-t_5', 'live' + LABEL))
        self.assertEqual((rows[('team', str(worker))]['NAME'], rows[('team', str(worker))]['STATE']),
                         ('probe-bg_2', 'live-idle' + LABEL))

    def test_the_stopped_background_row_with_no_pid_key_is_passed_over(self):
        # FINISH.md, "Step 8a's merge": 8a's stopped row has neither key; it is not live, and it
        # never makes the dir `unknown (agents format)`.
        row = stopped_background()
        self.assertEqual(('pid' in row, 'status' in row), (False, False))
        self.list_in(self.team_dir, [row, interactive(self.world.idle, 'probe-t_4', 'idle')])
        status, out, err = self.agents()
        self.assertEqual((status, err), (0, ''))
        self.assertNotIn('claude agents', out)
        self.assertEqual(out, self.who()[1])

    def test_a_listed_pid_with_no_process_reads_gone_at_once_with_no_grace_entry(self):
        dead = self.world.dead_pid()
        self.list_in(self.team_dir, [interactive(dead, 'probe-t_5', 'busy')])
        row = table(self.agents()[1])[('team', str(dead))]
        self.assertEqual((row['STARTED'], row['STATE']), ('-', 'gone' + LABEL))
        self.assertNotIn(dio.GraceCache.entry_name(self.team_dir, dead), self.world.cache_files())

    def test_a_proc_that_cannot_be_examined_reads_no_process_check(self):
        pid = self.world.live_process()
        self.list_in(self.team_dir, [interactive(pid, 'probe-t_5', 'busy')])
        real = dio.proc_start_of

        def refused(number):
            if number == pid:
                raise PermissionError(13, 'Permission denied')
            return real(number)
        with mock.patch.object(dio, 'proc_start_of', refused):
            row = table(self.agents()[1])[('team', str(pid))]
        self.assertEqual(row['STATE'], 'unknown (no process check: EACCES)' + LABEL)

    def test_a_roster_entry_covers_a_listed_session(self):
        pid = self.world.live_process()
        sock = self.world.listen('%d.sock' % pid)
        status, out, err = self.main('register', 'probe-t_5', '--state-root', self.world.state,
                                     environ={'CLAUDE_CODE_MESSAGING_SOCKET': sock,
                                              'CLAUDE_CONFIG_DIR': self.team_dir})
        self.assertEqual(status, 0, err)
        self.list_in(self.team_dir, [interactive(pid, 'probe-t_5', 'busy')])
        status, out, err = self.agents()
        self.assertEqual(len(self.lines_for(out, pid)), 1)
        self.assertEqual(table(out)[('team', str(pid))]['STATE'], 'live  fallback: register')

    def test_a_sessions_file_that_does_not_parse_covers_nothing(self):
        pid = self.world.live_process()
        self.world.write(self.world.team_root, '%d.json' % pid, b'{"pid": ')
        self.list_in(self.team_dir, [interactive(pid, 'probe-t_5', 'busy')])
        lines = self.lines_for(self.agents()[1], pid)
        self.assertEqual(len(lines), 2)
        self.assertTrue(any('unknown (sessions format: ' in line for line in lines))
        self.assertTrue(any(line.endswith('live' + LABEL) for line in lines))

    def test_cover_goes_by_config_dir_and_pid(self):
        # The max session, listed under the team config dir: its max sessions file does not cover
        # it there.
        live = self.world.max_live
        self.list_in(self.team_dir, [interactive(live, 'probe-m_1', 'busy')])
        rows = table(self.agents()[1])
        self.assertEqual(rows[('max', str(live))]['STATE'], 'live')
        self.assertEqual(rows[('team', str(live))]['STATE'], 'live' + LABEL)

    def test_the_name_is_the_listings_and_a_null_or_empty_name_prints_dash(self):
        null, empty = self.world.live_process(), self.world.live_process()
        self.list_in(self.team_dir, [interactive(null, None), interactive(empty, '')])
        rows = table(self.agents()[1])
        for pid in (null, empty):
            self.assertEqual((rows[('team', str(pid))]['NAME'], rows[('team', str(pid))]['STATE']),
                             ('-', 'live-idle' + LABEL))

    def test_the_start_is_the_process_start_proc_stat_gives_not_the_listings_started_at(self):
        pid = self.world.live_process()
        self.list_in(self.team_dir, [interactive(pid, 'probe-t_5', startedAt=0)])
        started = table(self.agents()[1])[('team', str(pid))]['STARTED']
        self.assertEqual(started, dio.started_text(proc_start(pid), dio.boot_clock()))
        self.assertNotEqual(started, '1970-01-01T00:00:00Z')

    def test_keys_the_format_does_not_name_are_ignored(self):
        pid = self.world.live_process()
        self.list_in(self.team_dir, [interactive(pid, 'probe-t_5', 'busy', state='working',
                                                 somethingNew={'nested': [1, 2]}, peerProtocol=1)])
        self.assertEqual(table(self.agents()[1])[('team', str(pid))]['STATE'], 'live' + LABEL)

    def test_listed_rows_sort_among_the_others_by_account_then_trailing_number(self):
        w = self.world
        early, late = w.live_process(), w.live_process()
        self.list_in(self.team_dir, [interactive(late, 'probe-t_35', 'busy'),
                                     interactive(early, 'probe-t_0', 'busy')])
        self.list_in(self.max_dir, status=3)
        status, out, err = self.agents()
        self.assertEqual([tuple(line.split()[0:3:2]) for line in out.splitlines()[1:]], [
            ('max', '-'), ('max', str(w.max_live)),
            ('team', '123'), ('team', TORN), ('team', str(early)), ('team', str(w.reused)),
            ('team', str(w.dead)), ('team', str(w.busy)), ('team', str(w.idle)), ('team', str(late))])

    def test_address_never_resolves_to_a_listed_row(self):
        # Its socket is `-`: as an exact name, a role's holder or a bare prefix's highest, and
        # beside a sessions row of the same name, which resolves alone.
        w = self.world
        listed = {name: w.live_process() for name in ('probe-t_5', 'nobody_9', 'probe-t_99', 'probe-t_4')}
        self.list_in(self.team_dir, [interactive(pid, name, 'busy') for name, pid in listed.items()])
        out = self.agents()[1]
        for pid in listed.values():
            self.assertEqual(table(out)[('team', str(pid))]['STATE'], 'live' + LABEL)
        status, out, err = self.agents('--address', 'probe-t_5')
        self.assertEqual((status, out), (1, ''))
        self.assertIn('no live session for probe-t_5', err)
        status, out, err = self.agents('--address', 'ghost')
        self.assertEqual((status, out), (1, ''))
        self.assertIn('ghost = nobody_9: no live holder', err)
        status, out, err = self.agents('--address', 'probe-t', '--highest')
        self.assertEqual((status, out), (0, w.socket_of(w.idle) + '\n'))
        self.assertIn('--highest chose probe-t_4 of 2 live', err)
        self.assertEqual(self.agents('--address', 'probe-t_4'), (0, w.socket_of(w.idle) + '\n', ''))

    def test_prefix_lists_a_listed_row_with_its_label(self):
        pid = self.world.live_process()
        self.list_in(self.team_dir, [interactive(pid, 'probe-t_5', 'idle')])
        status, out, err = self.agents('--prefix', 'probe-t')
        self.assertEqual(status, 0, err)
        self.assertEqual([line.split()[1] for line in out.splitlines()[1:]],
                         ['probe-t_3', 'probe-t_4', 'probe-t_5'])
        self.assertTrue(out.splitlines()[-1].endswith('live-idle' + LABEL))


class ConfigDirTests(AgentsBase):
    def test_the_default_max_config_dir_lists_with_claude_config_dir_removed(self):
        # T2: ~/.claude, the default max root's config dir, by abspath, so a trailing slash on
        # the root names it too; removed even where dio's own environment sets the variable.
        root = os.path.join(self.default, 'sessions')
        os.makedirs(root)
        environ = dict(self.environ, CLAUDE_CONFIG_DIR=self.team_dir)
        for given in (root, root + '/'):
            status, out, err = self.main('who', '--agents', '--agents-command', self.fake,
                                         '--sessions-root', 'max=' + given,
                                         '--state-root', self.world.state, environ=environ)
            self.assertEqual((status, err), (0, ''))
        self.assertEqual([run[2:] for run in self.runs()], [('/dev/null', 'unset', '-')] * 2)

    def test_any_other_config_dir_lists_with_claude_config_dir_set_to_it_whatever_its_label(self):
        # T2: by the dir, not the label: a root labelled max away from ~/.claude is set too.
        self.agents()
        status, out, err = self.main('who', '--agents', '--agents-command', self.fake,
                                     '--sessions-root', 'max=' + self.world.team_root,
                                     '--sessions-root', 'team=' + self.world.max_root,
                                     '--state-root', self.world.state)
        self.assertEqual((status, err), (0, ''))
        self.assertEqual([run[3:] for run in self.runs()], [
            ('set', self.max_dir), ('set', self.team_dir), ('set', self.team_dir), ('set', self.max_dir)])

    def test_one_listing_per_config_dir_in_the_roots_order_as_agents_json_all_on_dev_null(self):
        status, out, err = self.agents()
        self.assertEqual([run[1:] for run in self.runs()], [
            ('agents --json --all', '/dev/null', 'set', self.max_dir),
            ('agents --json --all', '/dev/null', 'set', self.team_dir)])
        status, out, err = self.main('who', '--agents', '--agents-command', self.fake,
                                     '--sessions-root', 'team=' + self.world.team_root,
                                     '--sessions-root', 'again=' + self.world.team_root + '/',
                                     '--state-root', self.world.state)
        self.assertEqual([run[4] for run in self.runs()[2:]], [self.team_dir])

    def test_two_roots_under_one_config_dir_list_it_once_with_the_first_roots_label(self):
        # Decision 41 (D8bv's finding 4): two sessions directories under one config dir, in
        # both orders of their labels, so the label is the first root's, not the last one's
        # and not the one that sorts first.
        pid = self.world.live_process()
        self.list_in(self.team_dir, [interactive(pid, 'probe-t_5', 'busy')])
        second = self.world.make('cfg-team', 'sessions-b')
        for first, then in (('one', 'two'), ('two', 'one')):
            with self.subTest(first=first):
                before = len(self.runs())
                status, out, err = self.main('who', '--agents', '--agents-command', self.fake,
                                             '--sessions-root', first + '=' + self.world.team_root,
                                             '--sessions-root', then + '=' + second,
                                             '--state-root', self.world.state)
                self.assertEqual((status, err), (0, ''))
                self.assertEqual([run[3:] for run in self.runs()[before:]], [('set', self.team_dir)])
                rows = table(out)
                self.assertEqual(rows[(first, str(pid))]['STATE'], 'live' + LABEL)
                self.assertNotIn((then, str(pid)), rows)

    def test_a_config_dir_whose_sessions_directory_is_missing_is_still_listed(self):
        # Decision 41 (D8bv's finding 4): the listing is the fallback for a config dir whose
        # sessions directory cannot be read, so a missing one is listed after its warning.
        config_dir = os.path.join(self.world.base, 'cfg-new')
        pid = self.world.live_process()
        self.list_in(config_dir, [interactive(pid, 'probe-n_1', 'idle')])
        root = os.path.join(config_dir, 'sessions')
        status, out, err = self.main('who', '--agents', '--agents-command', self.fake,
                                     '--sessions-root', 'max=' + self.world.max_root,
                                     '--sessions-root', 'new=' + root,
                                     '--state-root', self.world.state)
        self.assertEqual(status, 0)
        self.assertEqual(err, 'dio: cannot read the new sessions directory %s: '
                              'No such file or directory\n' % root)
        self.assertFalse(os.path.exists(root))
        self.assertEqual([run[3:] for run in self.runs()], [('set', self.max_dir), ('set', config_dir)])
        self.assertEqual(table(out)[('new', str(pid))]['STATE'], 'live-idle' + LABEL)

    def test_the_child_gets_mains_environ_with_only_claude_config_dir_changed(self):
        # T3, read from dio's own call, since the fake records CLAUDE_CONFIG_DIR alone. With no
        # --agents-command the command is claude, found on the PATH of main's environ: the fake.
        root = os.path.join(self.default, 'sessions')
        os.makedirs(root)
        self.list_in(self.default, [])
        environ = {'HOME': self.world.home, 'PATH': self.bin, 'DIO_TEST_KEPT': 'kept',
                   'CLAUDE_CONFIG_DIR': '/elsewhere'}
        calls, real = [], subprocess.Popen

        def recording(*args, **kwargs):
            calls.append((args, kwargs))
            return real(*args, **kwargs)
        with mock.patch.object(dio.subprocess, 'Popen', recording):
            status, out, err = self.main('who', '--agents', '--sessions-root', 'max=' + root,
                                         '--sessions-root', 'team=' + self.world.team_root,
                                         '--state-root', self.world.state, environ=environ)
        self.assertEqual((status, err), (0, ''))
        self.assertEqual([args for args, _ in calls], [(['claude', 'agents', '--json', '--all'],)] * 2)
        self.assertEqual(calls[0][1]['env'],
                         {key: value for key, value in environ.items() if key != 'CLAUDE_CONFIG_DIR'})
        self.assertEqual(calls[1][1]['env'], dict(environ, CLAUDE_CONFIG_DIR=self.team_dir))
        for _, kwargs in calls:
            self.assertEqual((kwargs['stdin'], kwargs['stdout'], kwargs['stderr']),
                             (subprocess.DEVNULL, subprocess.PIPE, subprocess.PIPE))
        self.assertEqual(environ['CLAUDE_CONFIG_DIR'], '/elsewhere')  # main's own is untouched
        self.assertEqual([run[3:] for run in self.runs()], [('unset', '-'), ('set', self.team_dir)])


class FormatTests(AgentsBase):
    def test_output_not_in_the_format_gives_the_dir_one_unknown_agents_format_row(self):
        pid = self.world.live_process()
        good = interactive(pid, 'probe-t_5', 'busy')

        def without(key):
            return {k: v for k, v in good.items() if k != key}
        text = json.dumps([good])
        cases = {
            'not JSON': b'not json', 'empty': b'', 'half written': text[:40].encode(),
            'a JSON object holding the rows': {'rows': [good]}, 'a JSON object holding a row': {'r': good},
            'a bare row, not in an array': good, 'a row that is a string': ['probe-t_5'],
            'a row that is null': [None],
            'pid a string': [dict(good, pid=str(pid))], 'pid a float': [dict(good, pid=float(pid))],
            'pid a boolean': [dict(good, pid=True)], 'pid null': [dict(good, pid=None)],
            'pid 0': [dict(good, pid=0)], 'pid negative': [dict(good, pid=-pid)],
            'pid of 11 digits': [dict(good, pid=12345678901)],
            'kind absent': [without('kind')], 'kind null': [dict(good, kind=None)],
            'kind a number': [dict(good, kind=1)],
            'status absent': [without('status')], 'status null': [dict(good, status=None)],
            'status shell, which a sessions file may hold': [dict(good, status='shell')],
            'status a list': [dict(good, status=['idle'])],
            'name absent': [without('name')], 'name a number': [dict(good, name=7)],
            'name with an escape character': [dict(good, name='probe\x1b[2J')],
            'duplicate keys': ('[{"pid": %d, ' % pid + text[2:]).encode(),
            'NaN': (text[:-2] + ', "x": NaN}]').encode(),
            'not UTF-8': json.dumps([dict(good, name='x')]).encode().replace(b'"x"', b'"\xff"'),
            'a good row and a bad one': [good, dict(good, pid=str(pid))],
        }
        for case, content in cases.items():
            with self.subTest(case=case):
                self.list_in(self.team_dir, content)
                status, out, err = self.agents()
                self.assertEqual((status, err), (0, ''))
                rows = table(out)
                self.assertEqual(rows[('team', '-')], {
                    'ACCOUNT': 'team', 'NAME': '-', 'PID': '-', 'STARTED': '-', 'VERSION': '-',
                    'SOCKET': '-', 'STATE': 'unknown (agents format)' + LABEL})
                self.assertEqual(len([line for line in out.splitlines() if line.endswith(LABEL)]), 1)
                self.assertEqual(rows[('team', str(self.world.busy))]['STATE'], 'live')

    def test_null_a_number_true_or_an_object_at_the_top_level_gives_one_agents_format_row(self):
        # parse_listing's top-level check (D8bv's finding 1). Without it, null, a number, true
        # and false would raise TypeError, a traceback, and {} would read as an empty listing.
        cases = {'null': b'null', 'a number': b'5', 'true': b'true', 'false': b'false',
                 'an empty object': b'{}', 'a string': b'"probe-t_5"'}
        for case, content in cases.items():
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    dio.parse_listing(content)
                self.list_in(self.team_dir, content)
                status, out, err = self.agents()
                self.assertEqual((status, err), (0, ''))
                self.assertEqual(table(out)[('team', '-')]['STATE'], 'unknown (agents format)' + LABEL)
                self.assertEqual(len([line for line in out.splitlines() if line.endswith(LABEL)]), 1)

    def test_rows_with_no_pid_key_are_passed_over_whatever_else_they_hold(self):
        no_pid = {k: v for k, v in running_background(1, 'probe-bg_3').items() if k != 'pid'}
        self.list_in(self.team_dir, [{}, {'kind': 7}, {'status': 'shell'}, {'name': 7, 'state': 'stopped'},
                                     stopped_background(), no_pid])
        status, out, err = self.agents()
        self.assertEqual((status, err), (0, ''))
        self.assertNotIn('claude agents', out)

    def test_an_empty_array_adds_no_row(self):
        status, out, err = self.agents()
        self.assertEqual((status, out, err), self.who())
        self.assertEqual(len(self.runs()), 2)


class FailureTests(AgentsBase):
    def test_a_non_zero_exit_gives_the_dir_one_unknown_row_whatever_it_printed(self):
        listed, other = self.world.live_process(), self.world.live_process()
        self.list_in(self.team_dir, [interactive(listed, 'probe-t_5', 'busy')], status=3)
        self.list_in(self.max_dir, [interactive(other, 'probe-m_2', 'busy')])
        status, out, err = self.agents()
        self.assertEqual((status, err), (0, ''))
        rows = table(out)
        self.assertEqual(rows[('team', '-')]['STATE'], 'unknown (agents exit 3)' + LABEL)
        self.assertNotIn(('team', str(listed)), rows)
        self.assertEqual(rows[('max', str(other))]['STATE'], 'live' + LABEL)  # the other dir's listing

    def test_a_listing_ended_by_a_signal_gives_the_dir_one_unknown_row(self):
        self.list_in(self.team_dir, killed=True)
        status, out, err = self.agents()
        self.assertEqual((status, err), (0, ''))
        self.assertEqual(table(out)[('team', '-')]['STATE'], 'unknown (agents signal SIGTERM)' + LABEL)

    def test_past_the_timeout_dio_kills_the_child_with_its_process_group_and_waits_for_it(self):
        # T4: main's agents_timeout, 0.2 s here, so no test waits 10 s; only the fake waits. The
        # fake records its pid, and its own child's, which shares its process group.
        self.list_in(self.team_dir, hang=True)
        started = time.monotonic()
        status, out, err = self.agents(timeout=0.2)
        elapsed = time.monotonic() - started
        self.assertEqual((status, err), (0, ''))
        self.assertEqual(table(out)[('team', '-')]['STATE'], 'unknown (agents timeout)' + LABEL)
        self.assertGreaterEqual(elapsed, 0.2)
        self.assertLess(elapsed, 5)
        [fake] = [int(run[0]) for run in self.runs() if run[4] == self.team_dir]
        with open(os.path.join(self.team_dir, 'agents.child'), encoding='utf-8') as f:
            grandchild = int(f.read())
        self.assertFalse(os.path.exists('/proc/%d' % fake))  # killed, and reaped by dio's wait
        self.assertTrue(self.ends(grandchild))  # killed with the group

    def ends(self, pid):
        """Whether `pid` has ended or ends within 5 s. A pidfd turns readable when its process
        ends, so this waits on that event and never sleeps; a process that does not end is
        killed through the same pidfd, so a failure leaves nothing running."""
        try:
            fd = os.pidfd_open(pid)
        except ProcessLookupError:
            return True  # ended, and reaped already
        try:
            if select.select([fd], [], [], 5)[0]:
                return True
            signal.pidfd_send_signal(fd, signal.SIGKILL)
            return False
        finally:
            os.close(fd)

    def kill_at_cleanup(self, pid):
        """Hold a pidfd on `pid` and send SIGKILL through it when the test ends, so a test that
        fails leaves nothing running, and a pid used again meanwhile is never signalled."""
        fd = os.pidfd_open(pid)

        def end():
            try:
                signal.pidfd_send_signal(fd, signal.SIGKILL)
            except ProcessLookupError:
                pass
            finally:
                os.close(fd)
        self.addCleanup(end)

    def test_an_interrupt_while_dio_waits_kills_the_group_with_sigkill_then_waits_for_the_child(self):
        # Decision 37's interrupt path (D8bv's finding 2). A real SIGINT reaches dio's process,
        # the test's own, while dio waits on the listing: once the fake has printed `ready`, the
        # test sends it SIGUSR1 from inside dio's call to communicate, and the fake sends SIGINT
        # to its parent. dio must send SIGKILL, not SIGTERM, to the fake's process group, then
        # wait for the fake, so it is reaped before the interrupt ends dio. The calls are
        # recorded in order, since the `with` block's own short wait could reap the fake too.
        self.list_in(self.max_dir, interrupt=True)
        previous = signal.signal(signal.SIGINT, signal.default_int_handler)
        self.addCleanup(signal.signal, signal.SIGINT, previous)
        children, grandchildren, calls = [], [], []
        real_communicate, real_wait, real_killpg = (subprocess.Popen.communicate,
                                                    subprocess.Popen.wait, os.killpg)

        def communicate(child, *args, **kwargs):
            children.append(child)
            self.addCleanup(child.wait)
            self.kill_at_cleanup(child.pid)
            self.assertEqual(child.stdout.readline(), b'ready\n')
            with open(os.path.join(self.max_dir, 'agents.child'), encoding='utf-8') as f:
                grandchildren.append(int(f.read()))
            self.kill_at_cleanup(grandchildren[0])
            os.kill(child.pid, signal.SIGUSR1)
            return real_communicate(child, *args, **kwargs)

        def wait(child, *args, **kwargs):
            calls.append(('wait', child.pid))
            return real_wait(child, *args, **kwargs)

        def killpg(group, number):
            calls.append(('killpg', group, number))
            return real_killpg(group, number)
        with mock.patch.object(dio.subprocess.Popen, 'communicate', communicate), \
                mock.patch.object(dio.subprocess.Popen, 'wait', wait), \
                mock.patch.object(dio.os, 'killpg', killpg):
            with self.assertRaises(KeyboardInterrupt):
                self.agents(timeout=5)  # a SIGINT that never came would end at 5 s, and fail
        [child], [grandchild] = children, grandchildren
        self.assertEqual(calls, [('killpg', child.pid, signal.SIGKILL), ('wait', child.pid)])
        self.assertEqual(child.returncode, -signal.SIGKILL)
        self.assertFalse(os.path.exists('/proc/%d' % child.pid))  # reaped before dio returned
        self.assertTrue(self.ends(grandchild))  # killed with the group
        self.assertEqual([run[4] for run in self.runs()], [self.max_dir])  # the team dir never ran

    def test_a_command_that_cannot_be_started_gives_each_dir_one_row_and_no_traceback(self):
        plain = self.world.write(self.world.base, 'not-executable', b'#!/bin/sh\nexit 0\n')
        for case, command, reason in (('missing', os.path.join(self.world.base, 'absent'), 'ENOENT'),
                                      ('not executable', plain, 'EACCES'),
                                      ('a directory', self.bin, 'EACCES')):
            with self.subTest(case=case):
                result = self.world.run('who', '--agents', '--agents-command', command,
                                        *self.world.who_flags(), PATH=self.bin)
                self.assertEqual((result.returncode, result.stderr), (0, ''))
                rows = table(result.stdout)
                for account in ('max', 'team'):
                    self.assertEqual(rows[(account, '-')]['STATE'],
                                     'unknown (agents cannot start: %s)%s' % (reason, LABEL))
        self.assertEqual(self.runs(), [])

    def test_an_empty_agents_command_is_not_claude_and_cannot_start(self):
        # PATH holds the fake, named claude: an empty command must not fall back to it.
        status, out, err = self.main('who', '--agents', '--agents-command', '', *self.world.who_flags())
        self.assertEqual((status, err), (0, ''))
        rows = table(out)
        for account in ('max', 'team'):
            self.assertTrue(rows[(account, '-')]['STATE'].startswith('unknown (agents cannot start: '))
        self.assertEqual(self.runs(), [])

    def test_the_listings_stderr_is_read_and_never_shown(self):
        # Through the built dio, whose stderr is its own process's.
        self.list_in(self.team_dir, err=b'NOISE from the listing\n')
        result = self.world.run('who', '--agents', '--agents-command', self.fake,
                                *self.world.who_flags(), PATH=self.bin)
        self.assertEqual((result.returncode, result.stderr), (0, ''))
        self.assertNotIn('NOISE', result.stdout)
        self.assertEqual(len(self.runs()), 2)


class FlagTests(AgentsBase):
    def test_agents_command_without_agents_is_a_usage_error_and_starts_no_process(self):
        status, out, err = self.who('--agents-command', self.fake)
        self.assertEqual((status, out), (2, ''))
        self.assertIn('--agents-command needs --agents', err)
        result = self.world.run('who', '--agents-command', self.fake, *self.world.who_flags(),
                                PATH=self.bin)
        self.assertEqual((result.returncode, result.stdout), (2, ''))
        self.assertIn('--agents-command needs --agents', result.stderr)
        self.assertNotIn('Traceback', result.stderr)
        self.assertEqual(self.runs(), [])

    def test_without_agents_dio_who_starts_no_process(self):
        # T6: in-process with Popen made to fail, and through the built dio with the fake, named
        # claude, alone on PATH; as a table, under --prefix and under --address.
        def refuse(*args, **kwargs):
            raise AssertionError('dio who started a process without --agents')
        forms = ((), ('--prefix', 'probe-t'), ('--address', 'probe-t_3'),
                 ('--address', 'probe-t', '--highest'))
        with mock.patch.object(dio.subprocess, 'Popen', refuse):
            for form in forms:
                with self.subTest(form=form):
                    self.assertIn(self.who(*form)[0], (0, 1))
        for form in forms:
            with self.subTest(form=form, built=True):
                result = self.world.run('who', *self.world.who_flags(), *form, PATH=self.bin)
                self.assertIn(result.returncode, (0, 1))
                self.assertNotIn('Traceback', result.stderr)
        self.assertEqual(self.runs(), [])

    def test_the_timeout_is_mains_agents_timeout_10_seconds_by_default_with_no_flag(self):
        self.assertEqual(inspect.signature(dio.main).parameters['agents_timeout'].default, 10)
        timeouts, real = [], subprocess.Popen.communicate

        def recording(child, *args, **kwargs):
            timeouts.append(kwargs.get('timeout'))
            return real(child, *args, **kwargs)
        with mock.patch.object(dio.subprocess.Popen, 'communicate', recording):
            self.agents()
            self.agents(timeout=0.5)
        self.assertEqual(timeouts, [10, 10, 0.5, 0.5])
        self.assertNotIn('timeout', self.world.run('who', '--help').stdout)  # no flag sets it

    def test_the_usage_text_names_the_two_flags(self):
        result = self.world.run('who', '--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('[--agents] [--agents-command PATH]', ' '.join(result.stdout.split()))


if __name__ == '__main__':
    unittest.main()
