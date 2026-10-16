"""Gate row M7a: `dio who` over the fixture directory, under strace.

The command, run from the repository root, with the fixture paths that tempfile gave
under $TMPDIR (fixtures.World.standard builds them):

    strace -f -e trace=openat,open,readlink -o <scratch>/m7a.trace \\
        src/dio who --sessions-root max=<scratch>/cfg-max/sessions \\
                    --sessions-root team=<scratch>/cfg-team/sessions \\
                    --state-root <scratch>/state

That is MIN.md's command with `-o` added, so the trace goes to a file and not into
dio's stderr. strace prints path arguments in full. M7a passes when no openat or open
names any .key path, the symlink 123.json is refused, and the half-written file is
reported as `unknown (sessions format: ...)`.

In the suite:  TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -v
Alone:         TMPDIR=<scratch dir> /usr/bin/python3 -I -B tests/test_m7a_strace.py
The second form prints the command, the evidence lines and a verdict, and exits 0 on PASS.
"""

import os
import re
import shutil
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # -I leaves this directory off
import fixtures  # noqa: E402
from fixtures import CANARY, DIO, TORN, World  # noqa: E402

STRACE = ['strace', '-f', '-e', 'trace=openat,open,readlink']
OPEN = re.compile(r'^[0-9]+ +(?:open|openat)\(')
READLINK = re.compile(r'^[0-9]+ +readlink\(')


def key_opens(lines):
    """Every traced open or openat whose line names a .key path."""
    return [line for line in lines if OPEN.match(line) and '.key' in line]


def run_m7a(world):
    """Run the M7a command over `world`; returns (command, completed process, trace lines)."""
    if shutil.which('strace') is None:
        raise RuntimeError('strace is required for gate row M7a')
    trace = os.path.join(world.base, 'm7a.trace')
    command = STRACE + ['-o', trace, DIO, 'who'] + world.roots() + ['--state-root', world.state]
    result = subprocess.run(command, env=world.env(), capture_output=True, text=True, timeout=120)
    with open(trace, encoding='utf-8', errors='replace') as f:
        return command, result, f.read().splitlines()


def state_of(output, pid, account='team'):
    """The STATE cell of one row of a dio who table, cut at the header's offset."""
    lines = output.splitlines()
    if not lines or 'STATE' not in lines[0]:
        return None
    start = lines[0].index('STATE')
    for line in lines[1:]:
        cells = line.split()
        if cells[:1] == [account] and cells[2:3] == [str(pid)]:
            return line[start:].strip()
    return None


class M7aStraceTest(unittest.TestCase):
    """M7a's three pass conditions, each its own case, over one strace run."""

    @classmethod
    def setUpClass(cls):
        fixtures.require_tmpdir()
        cls.world = World()
        try:
            cls.world.standard()
            cls.command, cls.result, cls.lines = run_m7a(cls.world)
        except BaseException:
            cls.world.close()  # tearDownClass does not run when setUpClass fails
            raise

    @classmethod
    def tearDownClass(cls):
        cls.world.close()

    def test_dio_who_ran_under_strace_and_exited_0(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertTrue([line for line in self.lines if OPEN.match(line)])

    def test_no_open_or_openat_names_any_key_path(self):
        self.assertEqual(key_opens(self.lines), [])

    def test_the_symlink_named_123_json_is_refused(self):
        named = [line for line in self.lines if '"123.json"' in line]
        opens = [line for line in named if OPEN.match(line)]
        self.assertEqual(len(opens), 1, named)
        self.assertIn('O_NOFOLLOW', opens[0])
        self.assertIn('= -1 ELOOP', opens[0])
        self.assertEqual([line for line in named if READLINK.match(line)], [])
        self.assertEqual(state_of(self.result.stdout, 123), 'unknown (refused: symlink)')

    def test_the_half_written_file_is_reported_as_a_sessions_format_mismatch(self):
        opens = [line for line in self.lines if OPEN.match(line) and '"%s.json"' % TORN in line]
        self.assertEqual(len(opens), 1)
        self.assertRegex(opens[0], r'= [0-9]+$')  # opened and read: it is a regular file
        self.assertTrue(state_of(self.result.stdout, TORN).startswith('unknown (sessions format: '))

    def test_the_canary_marker_never_reaches_the_output(self):
        self.assertNotIn(CANARY.decode().strip(), self.result.stdout + self.result.stderr)

    def test_the_detector_flags_a_key_path_in_a_synthetic_trace(self):
        sample = ['4242 openat(3, "123.key", O_RDONLY|O_CLOEXEC) = 4',
                  '4242 open("/x/4242.' + '0' * 64 + '.key", O_RDONLY) = 5',
                  '4242 openat(AT_FDCWD, "/x/sessions", O_RDONLY|O_DIRECTORY) = 3',
                  '4242 readlink("/x/123.json", "123.key", 4096) = 7']
        self.assertEqual(key_opens(sample), sample[:2])


def main():
    fixtures.require_tmpdir()
    world = World()
    try:
        world.standard()
        command, result, lines = run_m7a(world)
        shown = [line.replace(world.base, '<scratch>') for line in lines
                 if '"123.json"' in line or '"%s.json"' % TORN in line or '.key' in line
                 or READLINK.match(line)]
        print('command:', ' '.join(command).replace(world.base, '<scratch>'))
        print('dio exit status:', result.returncode)
        print('trace lines:', len(lines), '| open/openat lines:',
              len([line for line in lines if OPEN.match(line)]),
              '| open/openat naming .key:', len(key_opens(lines)))
        print('evidence lines (123.json, the torn file, any .key, every readlink):')
        for line in shown:
            print('  ' + line)
        print('row 123:', state_of(result.stdout, 123))
        print('row %s:' % TORN, state_of(result.stdout, TORN))
        refused = [line for line in lines if OPEN.match(line) and '"123.json"' in line]
        verdict = (result.returncode == 0 and not key_opens(lines) and len(refused) == 1
                   and 'O_NOFOLLOW' in refused[0] and '= -1 ELOOP' in refused[0]
                   and state_of(result.stdout, 123) == 'unknown (refused: symlink)'
                   and (state_of(result.stdout, TORN) or '').startswith('unknown (sessions format: '))
        print('M7a:', 'PASS' if verdict else 'FAIL')
        return 0 if verdict else 1
    finally:
        world.close()


if __name__ == '__main__':
    sys.exit(main())
