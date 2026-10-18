"""dio watch (MIN.md step 3): the start and the names present at it, the time comparison and
its margin, what wakes the watch and what never does, the cap and REARM, the refusals, the
one-line output, and the re-arm gap that the seat's rule covers.

The clock and the sleep are injected (fixtures.WatchClock), and dio's own sleep is patched to
fail, so no test sleeps. The built dio runs only where it exits at once: its refusals and its
help. The strace case runs dio watch in a child process whose injected sleep runs a second,
untraced process that drops the files.

Run from the repository root, with TMPDIR set to a scratch directory (tests/README.md):

    TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -v
"""

import contextlib
import io
import os
import re
import shutil
import stat
import subprocess
import sys
import unittest
from unittest import mock

import fixtures
from fixtures import CANARY, REPOSITORY, WatchClock, World

dio = fixtures.load_dio()
SECOND = 10 ** 9
UNTESTED = "the time past 10 minutes is untested until the gate's 2-hour leg"


def setUpModule():
    fixtures.require_tmpdir()


def never_sleep(seconds):
    raise AssertionError('a test reached the real sleep (%r s)' % seconds)


class WatchBase(unittest.TestCase):
    """An inbox in the temporary tree, holding files present at the start (PRESENT: each
    name's mtime in seconds from the start), and dio watch run in-process on the injected clock."""

    PRESENT = {'old.md': -3600, 'now.md': 0, 'future.md': 3600}

    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)
        for patcher in (mock.patch.dict(os.environ, {'HOME': self.world.home}),
                        mock.patch.object(dio.SystemClock, 'sleep', staticmethod(never_sleep))):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.clock = WatchClock()
        self.start = self.clock.real_ns()
        self.inbox = self.world.make('inbox')
        for name, offset in self.PRESENT.items():
            self.drop(name, self.start + offset * SECOND)

    def path(self, name):
        return os.path.join(self.inbox, name)

    def drop(self, name, mtime_ns=None):
        """A regular file in the inbox, its mtime set to `mtime_ns` (default: the clock's now)."""
        path = self.path(name)
        with open(path, 'wb') as f:
            f.write(b'a message\n')
        mtime = self.clock.real_ns() if mtime_ns is None else mtime_ns
        os.utime(path, ns=(mtime, mtime))
        return path

    def watch(self, *flags, directory=None):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                status = dio.main(['watch', directory or self.inbox] + list(flags), clock=self.clock)
            except SystemExit as e:
                status = e.code
        return status, out.getvalue(), err.getvalue()

    def wake(self, name):
        return 0, 'WAKE %s\n' % self.path(name), ''

    def rearm(self):
        return 1, 'REARM %s\n' % self.inbox, ''


class WakeTests(WatchBase):
    def test_a_new_regular_file_ends_the_watch_with_wake_and_its_path_exit_0(self):
        self.clock.at(1, lambda: self.drop('2026-10-16T0700-diogenes_0-hello.md'))
        self.assertEqual(self.watch(), self.wake('2026-10-16T0700-diogenes_0-hello.md'))
        self.assertEqual(self.clock.sleeps, [60.0])

    def test_a_relative_directory_is_printed_as_an_absolute_path(self):
        previous = os.getcwd()
        os.chdir(self.world.base)
        self.addCleanup(os.chdir, previous)
        self.clock.at(1, lambda: self.drop('new.md'))
        self.assertEqual(self.watch(directory='inbox'),
                         (0, 'WAKE %s\n' % os.path.join(os.getcwd(), 'inbox', 'new.md'), ''))

    def test_files_present_at_the_start_never_wake_it_whatever_their_mtime(self):
        # M4: "pre-existing files never trigger". Their mtimes are an hour before the start, at
        # it, and an hour after it; during the watch two are touched and one is replaced.
        def change():
            now = self.clock.real_ns()
            os.utime(self.path('now.md'), ns=(now, now))
            os.utime(self.path('future.md'), ns=(now + 10 * SECOND, now + 10 * SECOND))
            os.unlink(self.path('old.md'))
            self.drop('old.md')
        self.clock.at(1, change)
        self.assertEqual(self.watch('--max', '300'), self.rearm())

    def test_a_new_file_stamped_a_millisecond_before_the_start_wakes_it(self):
        # The kernel stamps mtimes from a clock that trails the one the start is read from, so
        # a file made just after the start can carry an mtime before it. This case stamps it 1 ms
        # before; the runs on record reach 1.849 ms (src/README.md).
        self.clock.at(1, lambda: self.drop('new.md', self.start - 10 ** 6))
        self.assertEqual(self.watch(), self.wake('new.md'))

    def test_the_start_lists_the_directory_before_it_reads_the_clock(self):
        # Decision 15's order (D4v's finding 1). The clock's one reading drops a file, so the file
        # lands between the listing and the reading: it is new, its mtime is the start, and the
        # poll that comes at once reports it. A watch that read the clock first would have listed
        # the file as present at the start, and would never report it.
        readings = []

        def reading_drops_a_file():
            readings.append(self.clock.real)
            self.drop('between.md', self.clock.real)
            return self.clock.real
        self.clock.real_ns = reading_drops_a_file
        self.assertEqual(self.watch('--max', '300'), self.wake('between.md'))
        self.assertEqual((readings, self.clock.sleeps), ([self.start], []))

    def test_the_margin_is_2_seconds_and_a_new_file_stamped_earlier_never_wakes_it(self):
        self.assertEqual(dio.MTIME_MARGIN_NS, 2 * SECOND)
        self.clock.at(1, lambda: self.drop('edge.md', self.start - 2 * SECOND))
        self.clock.at(2, lambda: self.drop('inside.md', self.start - 2 * SECOND + 1))
        self.assertEqual(self.watch(), self.wake('inside.md'))
        self.assertEqual(self.clock.sleeps, [60.0, 60.0])  # edge.md was there a poll earlier

    def test_a_new_name_with_an_old_mtime_wakes_it_only_once_its_mtime_is_new(self):
        # A file moved in keeps its own mtime: an hour before the start, it does not count
        # until it is touched.
        self.clock.at(1, lambda: self.drop('moved.md', self.start - 3600 * SECOND))
        self.clock.at(3, lambda: os.utime(self.path('moved.md'), ns=(self.clock.real_ns(),) * 2))
        self.assertEqual(self.watch(), self.wake('moved.md'))
        self.assertEqual(self.clock.sleeps, [60.0] * 3)

    def test_only_a_regular_file_wakes_it(self):
        canary = self.world.write(self.world.base, 'canary.md', CANARY)

        def others():  # each newer than the start, none a regular file
            os.symlink(canary, self.path('link.md'))
            os.mkdir(self.path('sub.md'))
            os.mkfifo(self.path('fifo.md'))
            self.world.listen('sock.md', self.inbox)
        self.clock.at(1, others)
        self.clock.at(3, lambda: self.drop('regular.md'))
        self.assertEqual(self.watch(), self.wake('regular.md'))
        self.assertEqual(self.clock.sleeps, [60.0] * 3)

    def test_the_first_of_several_new_files_is_the_earliest_mtime_then_the_first_name(self):
        def several():
            now = self.clock.real_ns()
            self.drop('b.md', now - 5 * SECOND)
            self.drop('c.md', now - 30 * SECOND)
            self.drop('a.md', now - 5 * SECOND)
        self.clock.at(1, several)
        self.assertEqual(self.watch(), self.wake('c.md'))
        self.clock.at(2, lambda: [self.drop(name, self.clock.real_ns()) for name in ('e.md', 'd.md')])
        self.assertEqual(self.watch(), self.wake('d.md'))

    def test_a_file_that_lands_in_the_last_interval_still_wakes_it(self):
        self.clock.at(2, lambda: self.drop('late.md'))
        self.assertEqual(self.watch('--every', '60', '--max', '120'), self.wake('late.md'))
        self.assertEqual(self.clock.sleeps, [60.0, 60.0])

    def test_a_new_name_removed_between_the_listing_and_its_stat_is_skipped(self):
        real_stat = os.stat

        def stat_after_removal(path, *, dir_fd=None, follow_symlinks=True):
            if path == 'ghost.md':
                raise FileNotFoundError(2, 'No such file or directory')
            return real_stat(path, dir_fd=dir_fd, follow_symlinks=follow_symlinks)
        self.clock.at(1, lambda: (self.drop('ghost.md'), self.drop('real.md', self.clock.real_ns() + 1)))
        with mock.patch.object(dio.os, 'stat', stat_after_removal):
            self.assertEqual(self.watch(), self.wake('real.md'))


class CapTests(WatchBase):
    def test_the_cap_ends_the_watch_with_rearm_and_its_directory_exit_1(self):
        self.assertEqual(self.watch('--max', '300'), self.rearm())
        self.assertEqual(self.clock.sleeps, [60.0] * 5)

    def test_the_defaults_poll_every_60_seconds_and_cap_at_3000(self):
        self.assertEqual((dio.WATCH_EVERY, dio.WATCH_CAP), (60, 3000))
        self.assertEqual(self.watch(), self.rearm())
        self.assertEqual(self.clock.sleeps, [60.0] * 50)

    def test_the_last_sleep_is_cut_to_the_cap(self):
        self.assertEqual(self.watch('--every', '70', '--max', '100'), self.rearm())
        self.assertEqual(self.clock.sleeps, [70.0, 30.0])

    def test_every_longer_than_max_sleeps_once_to_the_cap(self):
        self.assertEqual(self.watch('--every', '600', '--max', '100'), self.rearm())
        self.assertEqual(self.clock.sleeps, [100.0])

    def test_the_largest_values_one_day_are_accepted(self):
        self.assertEqual(self.watch('--every', '86400', '--max', '86400'), self.rearm())
        self.assertEqual(self.clock.sleeps, [86400.0])

    def test_the_cap_is_timed_on_the_monotonic_clock_so_a_real_clock_step_moves_it_not(self):
        for jump in (-3600, 3600):
            with self.subTest(jump=jump):
                self.clock = WatchClock()
                self.clock.at(1, lambda: setattr(self.clock, 'real', self.clock.real + jump * SECOND))
                self.assertEqual(self.watch('--max', '300'), self.rearm())
                self.assertEqual(self.clock.sleeps, [60.0] * 5)


class RefusalTests(WatchBase):
    def refused(self, directory, message):
        self.assertEqual(self.watch(directory=directory), (2, '', 'dio watch: %s\n' % message))
        self.assertEqual(self.clock.sleeps, [])

    def test_a_missing_directory_is_refused_with_exit_2(self):
        missing = os.path.join(self.world.base, 'absent')
        self.refused(missing, 'no such directory: ' + missing)

    def test_a_regular_file_a_fifo_or_a_socket_is_refused_as_not_a_directory_with_exit_2(self):
        fifo = os.path.join(self.world.base, 'fifo')
        os.mkfifo(fifo)  # never opened, so the refusal cannot block on it
        for path in (self.path('old.md'), fifo, self.world.listen('sock', self.world.base)):
            with self.subTest(path=path):
                self.refused(path, 'not a directory: ' + path)

    def test_a_symlink_is_refused_even_to_a_directory_with_exit_2(self):
        link = os.path.join(self.world.base, 'inbox-link')
        os.symlink(self.inbox, link)
        self.refused(link, 'a symlink, not a directory: ' + link)

    @unittest.skipIf(os.geteuid() == 0, 'root can read a mode-000 directory')
    def test_a_directory_it_cannot_read_is_refused_with_exit_2(self):
        os.chmod(self.inbox, 0)
        self.addCleanup(os.chmod, self.inbox, 0o700)
        self.refused(self.inbox, 'cannot read %s: Permission denied' % self.inbox)

    def test_bad_flags_are_usage_errors_with_exit_2(self):
        seconds = 'expected whole seconds from 1 to 86400'
        cases = {'--every 0': ['--every', '0'], '--every -1': ['--every', '-1'],
                 '--every 1.5': ['--every', '1.5'], '--every abc': ['--every', 'abc'],
                 '--every 86401': ['--every', '86401'], '--every in Arabic-Indic digits':
                 ['--every', '\u0666\u0660'], '--max 0': ['--max', '0'],
                 '--max 86401': ['--max', '86401'], '--max empty': ['--max', '']}
        for case, flags in cases.items():
            with self.subTest(case=case):
                status, out, err = self.watch(*flags)
                self.assertEqual((status, out), (2, ''))
                self.assertIn(seconds, err)
        for case, argv in {'no DIR': ['watch'], 'an unknown flag': ['watch', self.inbox, '--since', '5'],
                           'two DIRs': ['watch', self.inbox, self.inbox]}.items():
            with self.subTest(case=case):
                err = io.StringIO()
                with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as raised:
                    dio.main(argv, clock=self.clock)
                self.assertEqual(raised.exception.code, 2)
                self.assertIn('usage: dio', err.getvalue())
        self.assertEqual(self.clock.sleeps, [])

    def test_the_built_dio_refuses_at_once_with_exit_2_and_no_traceback(self):
        missing = os.path.join(self.world.base, 'absent')
        for args, message in ((['watch', missing], 'no such directory: ' + missing),
                              (['watch', self.path('old.md')], 'not a directory: ' + self.path('old.md'))):
            with self.subTest(args=args):
                result = self.world.run(*args)
                self.assertEqual((result.returncode, result.stdout, result.stderr),
                                 (2, '', 'dio watch: %s\n' % message))
        result = self.world.run('watch', self.inbox, '--max', '0')
        self.assertEqual((result.returncode, result.stdout), (2, ''))
        self.assertNotIn('Traceback', result.stderr)


class DuringTests(WatchBase):
    def test_the_directory_removed_during_the_watch_ends_it_with_exit_2(self):
        self.clock.at(1, lambda: shutil.rmtree(self.inbox))
        self.assertEqual(self.watch(), (2, '', 'dio watch: during the watch, no such directory: %s\n'
                                        % self.inbox))

    def test_the_directory_replaced_during_the_watch_ends_it_with_exit_2(self):
        def replace():
            os.rename(self.inbox, self.inbox + '-before')
            os.mkdir(self.inbox)
            self.drop('new.md')  # a new file in the new directory does not count either
        self.clock.at(1, replace)
        self.assertEqual(self.watch(), (2, '', 'dio watch: during the watch, %s is another directory '
                                        'now\n' % self.inbox))

    @unittest.skipIf(os.geteuid() == 0, 'root can read a mode-000 directory')
    def test_the_directory_made_unreadable_during_the_watch_ends_it_with_exit_2(self):
        self.addCleanup(os.chmod, self.inbox, 0o700)
        self.clock.at(1, lambda: os.chmod(self.inbox, 0))
        self.assertEqual(self.watch(), (2, '', 'dio watch: during the watch, cannot read %s: '
                                        'Permission denied\n' % self.inbox))


class OneLineTests(WatchBase):
    def test_a_name_with_a_newline_is_printed_on_one_line_with_an_escape(self):
        self.clock.at(1, lambda: self.drop('a\nWAKE b.md'))
        status, out, err = self.watch()
        self.assertEqual((status, out, err), (0, 'WAKE %s/a\\x0aWAKE b.md\n' % self.inbox, ''))
        self.assertEqual(out.count('\n'), 1)

    def test_a_byte_that_is_not_utf_8_a_backslash_a_line_separator_and_a_c1_control_are_escaped(self):
        def drop_bytes():  # x, the byte ff, a backslash, y, U+2028, z, U+0085
            path = os.path.join(os.fsencode(self.inbox), b'x\xff\\y\xe2\x80\xa8z\xc2\x85.md')
            with open(path, 'wb') as f:
                f.write(b'a message\n')
            os.utime(path, ns=(self.clock.real_ns(),) * 2)
        self.clock.at(1, drop_bytes)
        self.assertEqual(self.watch(), (0, 'WAKE %s/x\\xff\\\\y\\u2028z\\x85.md\n' % self.inbox, ''))

    def test_an_ordinary_path_prints_unchanged(self):
        for text in ('/srv/inbox/2026-10-16T0700-diogenes_0-hello.md', '/x/caf\u00e9 \u4e2d.md'):
            self.assertEqual(dio.printable(text), text)


class NeverOpenedTests(WatchBase):
    def test_new_names_are_stated_relative_without_following_and_nothing_but_the_directory_is_opened(self):
        canary = self.world.write(self.world.base, 'canary.md', CANARY)
        opens, stats, real_open, real_stat = [], [], os.open, os.stat

        def record_open(path, flags, mode=0o777, *, dir_fd=None):
            opens.append((path, flags, dir_fd))
            return real_open(path, flags, mode, dir_fd=dir_fd)

        def record_stat(path, *, dir_fd=None, follow_symlinks=True):
            stats.append((path, dir_fd, follow_symlinks))
            return real_stat(path, dir_fd=dir_fd, follow_symlinks=follow_symlinks)

        def others():
            os.symlink(canary, self.path('link.md'))
            os.mkdir(self.path('sub.md'))
            os.mkfifo(self.path('fifo.md'))
            self.world.listen('sock.md', self.inbox)
        self.clock.at(1, others)
        self.clock.at(2, lambda: self.drop('regular.md'))
        with mock.patch.object(dio.os, 'open', record_open), mock.patch.object(dio.os, 'stat', record_stat):
            status, out, err = self.watch()
        self.assertEqual((status, out, err), self.wake('regular.md'))
        self.assertEqual({path for path, _, _ in opens}, {self.inbox})
        for path, flags, dir_fd in opens:
            self.assertTrue(flags & os.O_DIRECTORY and flags & os.O_NOFOLLOW)
            self.assertIsNone(dir_fd)
        # The names present at the start are never stat'ed; each new one is, each poll, relative
        # to the directory. (Building the parser, argparse's gettext stats its own .mo paths.)
        relative = [(path, follow_symlinks) for path, dir_fd, follow_symlinks in stats
                    if dir_fd is not None]
        self.assertEqual({path for path, _ in relative},
                         {'link.md', 'sub.md', 'fifo.md', 'sock.md', 'regular.md'})
        self.assertEqual([follow for _, follow in relative if follow], [])
        self.assertEqual([path for path, dir_fd, _ in stats
                          if dir_fd is None and path.startswith(self.inbox)], [])
        self.assertNotIn(CANARY.decode().strip(), out + err)

    def test_a_dangling_symlink_present_at_the_start_or_new_never_wakes_it_and_is_never_opened(self):
        # D4v's finding 8. One dangling symlink is in the inbox at the start, with its own mtime
        # an hour after the start; a new one lands at the first sleep, with its own mtime newer
        # than the start. Neither wakes the watch, and the regular file two sleeps later does.
        # Nothing is opened but the directory, nothing is read through a link, the link present
        # at the start is never stat'ed, and the new one is stat'ed relative to the directory
        # without following it. Neither target exists, and neither is ever named.
        old_target = os.path.join(self.world.base, 'absent-old.md')
        new_target = os.path.join(self.world.base, 'absent-new.md')
        os.symlink(old_target, self.path('dangling-old.md'))
        later = self.start + 3600 * SECOND
        os.utime(self.path('dangling-old.md'), ns=(later, later), follow_symlinks=False)
        opens, stats, reads, real_open, real_stat = [], [], [], os.open, os.stat
        real_lstat, real_readlink, real_builtin_open = os.lstat, os.readlink, open

        def record_open(path, flags, mode=0o777, *, dir_fd=None):
            opens.append((path, flags, dir_fd))
            return real_open(path, flags, mode, dir_fd=dir_fd)

        def record_stat(path, *, dir_fd=None, follow_symlinks=True):
            stats.append((path, dir_fd, follow_symlinks))
            return real_stat(path, dir_fd=dir_fd, follow_symlinks=follow_symlinks)

        def record_lstat(path, *, dir_fd=None):
            stats.append((path, dir_fd, False))
            return real_lstat(path, dir_fd=dir_fd)

        def record_readlink(path, *, dir_fd=None):
            reads.append(('readlink', path))
            return real_readlink(path, dir_fd=dir_fd)

        def record_builtin_open(file, *args, **kwargs):
            reads.append(('open', file))
            return real_builtin_open(file, *args, **kwargs)

        def dangle():
            os.symlink(new_target, self.path('dangling-new.md'))
            now = self.clock.real_ns()
            os.utime(self.path('dangling-new.md'), ns=(now, now), follow_symlinks=False)
        self.clock.at(1, dangle)
        self.clock.at(3, lambda: self.drop('regular.md'))
        with mock.patch.object(dio.os, 'open', record_open), \
                mock.patch.object(dio.os, 'stat', record_stat), \
                mock.patch.object(dio.os, 'lstat', record_lstat), \
                mock.patch.object(dio.os, 'readlink', record_readlink), \
                mock.patch('builtins.open', record_builtin_open):
            status, out, err = self.watch()
        self.assertEqual((status, out, err), self.wake('regular.md'))
        self.assertEqual(self.clock.sleeps, [60.0] * 3)  # the polls after sleeps 1 and 2 saw the link
        self.assertEqual({path for path, _, _ in opens}, {self.inbox})
        for path, flags, dir_fd in opens:
            self.assertTrue(flags & os.O_DIRECTORY and flags & os.O_NOFOLLOW)
        # (The test's own drop of regular.md goes through the patched open too, so only the
        # links' and their targets' names are looked for.)
        self.assertEqual([entry for entry in reads
                          if 'dangling' in str(entry[1]) or 'absent-' in str(entry[1])], [])
        relative = [(path, follow) for path, dir_fd, follow in stats if dir_fd is not None]
        self.assertEqual({path for path, _ in relative}, {'dangling-new.md', 'regular.md'})
        self.assertEqual([path for path, follow in relative if follow], [])
        named = [path for path, _, _ in stats + [(p, None, None) for p, _, _ in opens]]
        for absent in ('dangling-old.md', old_target, new_target):
            self.assertEqual([path for path in named if path.endswith(os.path.basename(absent))], [])


# dio watch in a child process: its sleep runs DROPPER in a second process, which strace does
# not trace (no -f), so the trace holds dio's own system calls and not the dropper's.
HELPER = r'''
import subprocess, sys, time
sys.path.insert(0, sys.argv[1])
import fixtures
dio = fixtures.load_dio()
directory, dropper, canary = sys.argv[2], sys.argv[3], sys.argv[4]


class Clock:
    """The real clock for the start, so the dropped files' own mtimes count; a monotonic clock
    that moves only in sleep(), which runs the untraced dropper instead of sleeping."""
    monotonic = 0

    def real_ns(self):
        return time.time_ns()

    def monotonic_ns(self):
        return self.monotonic

    def sleep(self, seconds):
        self.monotonic += round(seconds * 10 ** 9)
        subprocess.run([sys.executable, '-I', '-B', '-c', dropper, directory, canary], check=True)


sys.exit(dio.main(['watch', directory, '--every', '60', '--max', '120'], clock=Clock()))
'''
DROPPER = r'''
import os, socket, sys
directory, canary = sys.argv[1], sys.argv[2]
if not os.path.lexists(os.path.join(directory, 'w-fifo')):  # the first sleep: no regular file
    os.mkfifo(os.path.join(directory, 'w-fifo'))
    os.symlink(canary, os.path.join(directory, 'w-link.md'))
    os.symlink(os.path.join(directory, 'w-missing'), os.path.join(directory, 'w-dangling.md'))
    os.mkdir(os.path.join(directory, 'w-sub'))
    os.chdir(directory)
    socket.socket(socket.AF_UNIX).bind('w-sock')
else:  # the second sleep: the regular file
    with open(os.path.join(directory, 'w-regular.md'), 'wb') as f:
        f.write(b'a message\n')
'''
CALL = re.compile(r'^(?:[0-9]+ +)?([a-z0-9_]+)\(')


class StraceTests(WatchBase):
    def test_under_strace_it_opens_only_the_directory_writes_nothing_and_stats_new_names_unfollowed(self):
        self.assertIsNotNone(shutil.which('strace'), 'strace is required')
        canary = self.world.write(self.world.base, 'w-canary.md', CANARY)
        os.symlink(self.path('w-absent'), self.path('w-dangling-old.md'))  # present, dangling
        trace = os.path.join(self.world.base, 'watch.trace')
        command = ['strace', '-e', 'trace=%file', '-o', trace, sys.executable, '-I', '-B', '-c', HELPER,
                   os.path.dirname(os.path.abspath(fixtures.__file__)), self.inbox, DROPPER, canary]
        result = subprocess.run(command, env=self.world.env(), capture_output=True, text=True, timeout=120)
        self.assertEqual((result.returncode, result.stdout),
                         (0, 'WAKE %s\n' % self.path('w-regular.md')), result.stderr)
        with open(trace, encoding='utf-8', errors='replace') as f:
            lines = [line for line in f.read().splitlines()
                     if CALL.match(line) and CALL.match(line).group(1) != 'execve']

        def calls(name):
            return [line for line in lines if '"%s"' % name in line or '/%s"' % name in line]
        directory = calls(os.path.basename(self.inbox))
        self.assertTrue(directory)  # the trace is not blind: it holds the directory's opens
        for line in directory:
            self.assertIn(CALL.match(line).group(1), ('open', 'openat'), line)
            self.assertIn('O_DIRECTORY', line)
            self.assertIn('O_NOFOLLOW', line)
        writes = [line for line in lines if re.search(r'O_WRONLY|O_RDWR|O_CREAT', line)
                  or CALL.match(line).group(1) in ('unlink', 'unlinkat', 'rename', 'renameat',
                                                   'renameat2', 'mkdir', 'mkdirat', 'link', 'linkat')]
        self.assertEqual(writes, [])
        for name in list(self.PRESENT) + ['w-dangling-old.md', 'w-absent', 'w-missing']:
            self.assertEqual(calls(name), [], name)  # present at the start, or a link's target
        for name in ('w-fifo', 'w-link.md', 'w-dangling.md', 'w-sub', 'w-sock', 'w-regular.md'):
            named = calls(name)
            self.assertTrue(named, name)
            for line in named:
                self.assertIn(CALL.match(line).group(1), ('newfstatat', 'fstatat64', 'statx'), line)
                self.assertIn('AT_SYMLINK_NOFOLLOW', line)
        self.assertEqual(calls(os.path.basename(canary)), [])
        self.assertNotIn(CANARY.decode().strip(), result.stdout + result.stderr)


class GapTests(WatchBase):
    """The re-arm gap (src/README.md). A file that lands between one watch's exit and the next
    watch's start, or within one poll of another, is present at the next start, so no later
    watch reports it. The seat's rule reads it: read the clock before arming each watch, and
    after every exit re-arm first, then read every regular file whose mtime is later than the
    previous reading less the margin."""

    PRESENT = {'old.md': -3600}

    def seats_rule(self, reading):
        """The names the seat's rule reads, given the reading taken before the last watch."""
        names = []
        for name in sorted(os.listdir(self.inbox)):
            st = os.lstat(self.path(name))
            if stat.S_ISREG(st.st_mode) and st.st_mtime_ns > reading - dio.MTIME_MARGIN_NS:
                names.append(name)
        return names

    def test_a_file_dropped_in_the_re_arm_gap_wakes_no_later_watch_and_the_seats_rule_reads_it(self):
        first_reading = self.clock.real_ns()  # the seat reads the clock, then arms
        self.clock.at(1, lambda: self.drop('first.md'))
        self.assertEqual(self.watch(), self.wake('first.md'))
        self.clock.advance(5)  # the seat's turn: the gap
        self.drop('gap.md')  # lands after the first watch's exit
        self.clock.advance(5)
        second_reading = self.clock.real_ns()  # the seat reads the clock, then re-arms
        self.drop('window.md', second_reading + 1000)  # after that reading, before the new listing
        self.assertEqual(self.watch('--max', '300'), self.rearm())  # neither wakes it
        self.assertEqual(self.seats_rule(first_reading), ['first.md', 'gap.md', 'window.md'])
        self.assertEqual(self.seats_rule(second_reading), ['window.md'])

    def test_a_second_file_within_one_poll_of_the_first_wakes_no_later_watch_and_the_rule_reads_it(self):
        reading = self.clock.real_ns()
        self.clock.at(1, lambda: (self.drop('one.md', self.clock.real_ns() - 20 * SECOND),
                                  self.drop('two.md', self.clock.real_ns() - 10 * SECOND)))
        self.assertEqual(self.watch(), self.wake('one.md'))
        self.clock.advance(5)
        self.assertEqual(self.watch('--max', '300'), self.rearm())
        self.assertEqual(self.seats_rule(reading), ['one.md', 'two.md'])

    def test_a_step_back_of_the_real_clock_hides_a_later_file_from_the_watch_and_the_seats_rule(self):
        # D4v's finding 6 (src/README.md, "A step back of the real clock"). An hour into the
        # past at the first sleep: the file that lands then carries an mtime before the start
        # less 2 s, so the watch ends at its cap, and the seat's rule, whose reading was taken
        # before the step, misses it too. After a step back of only 2 s, a minute into the
        # watch, a file that lands then still wakes it, and the rule reads it.
        reading = self.clock.real_ns()  # the seat reads the clock, then arms

        def step_back_then_drop():
            self.clock.real -= 3600 * SECOND
            self.drop('hidden.md')
        self.clock.at(1, step_back_then_drop)
        self.assertEqual(self.watch('--max', '300'), self.rearm())
        self.assertEqual(self.seats_rule(reading), [])
        self.clock = WatchClock()
        reading = self.clock.real_ns()

        def small_step_back_then_drop():
            self.clock.real -= 2 * SECOND
            self.drop('seen.md')
        self.clock.at(1, small_step_back_then_drop)
        self.assertEqual(self.watch('--max', '300'), self.wake('seen.md'))
        self.assertEqual(self.seats_rule(reading), ['seen.md'])


class HelpTests(unittest.TestCase):
    def test_the_help_says_the_default_cap_is_provisional_and_the_time_past_10_minutes_untested(self):
        world = World()
        self.addCleanup(world.close)
        result = world.run('watch', '--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        text = ''.join(result.stdout.split())  # argparse wraps the text, even at a hyphen
        self.assertIn(''.join('default 3000, provisional until the gate'.split()), text)
        self.assertIn(''.join(UNTESTED.split()), text)

    def test_the_readme_says_the_time_past_10_minutes_is_untested(self):
        with open(os.path.join(REPOSITORY, 'src', 'README.md'), encoding='utf-8') as f:
            text = ' '.join(f.read().split()).lower()
        self.assertIn(UNTESTED.lower(), text)
        self.assertIn('provisional', text)

    @staticmethod
    def readme():
        with open(os.path.join(REPOSITORY, 'src', 'README.md'), encoding='utf-8') as f:
            return ' '.join(f.read().split())

    def test_the_readme_sets_the_margin_against_the_worst_lag_on_record_and_names_its_runs(self):
        # D4v's finding 5: 2 s against 1.849 ms, D4v's worst, is about 1,080 times.
        text = self.readme()
        self.assertEqual(round(2 / 1.849e-3, -1), 1080)
        self.assertIn('2 s is about 1,080 times the worst lag on record, 1.849 ms', text)
        self.assertNotIn('1,700', text)
        for run in ('3,000 of 3,000, worst 0.64 ms', '2,000 of 2,000, worst 1.141 ms',
                    '2,000 of 2,000, worst 1.006 ms',
                    '6,000 of 6,000 in three batches of 2,000, worst 1.849 ms (D4v'):
            self.assertIn(run, text)

    def test_the_readme_says_a_step_back_of_the_real_clock_hides_later_files_from_both(self):
        # D4v's finding 6, which GapTests' step-back case shows.
        self.assertIn("**A step back of the real clock** by more than 2 s during a watch can hide "
                      "later files from the watch, and from the seat's rule alike", self.readme())


if __name__ == '__main__':
    unittest.main()
