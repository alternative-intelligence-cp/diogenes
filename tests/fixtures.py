"""Fixtures for the dio tests: a fake machine generated into a temporary directory.

Every path comes from tempfile, which follows $TMPDIR, and every dio run gets HOME set
to a directory inside the same temporary tree, so neither a flag nor a default can
reach a real sessions directory or the real shared zone. (One test reads this
repository's own meta/ROLES.md on purpose, to show it is the default role file.)

The standard world is MIN.md step 1's fixture list plus live entries:
    team sessions/  123.key, a canary holding only a marker line
                    123.json, a symlink to the canary
                    a stale file for a dead pid                 (probe-t_2)
                    a reused pid with a different procStart     (probe-t_1)
                    7777777.json, a half-written JSON
                    a live entry, status busy                   (probe-t_3)
                    a live entry, status idle                   (probe-t_4)
                    names that do not match ^[0-9]+\\.json$, and a second canary
    max sessions/   a live entry                                (probe-m_1)
A live entry is a child process this test owns, blocked reading its stdin, with a real
Unix socket file bound under the temporary tree. Each socket is bound by a short name from
inside its directory (World.listen), so a long $TMPDIR never meets the 108-byte limit on a
socket's address.
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader

sys.dont_write_bytecode = True

REPOSITORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIO = os.path.join(REPOSITORY, 'src', 'dio')
CANARY = b'CANARY: a test marker, not a key. dio must never open this file.\n'
VERSION = '2.1.301'
TORN = '7777777'
TORN_BYTES = b'{"pid": 7777777, "procStart": "51045'
JUNK = ('notes.txt', '123.json.tmp', 'abc.json', '.123.json', '123.JSON', '12a.json', '123.json~')
SECOND_CANARY = '4242.' + '0' * 64 + '.key'
ROLES = """# A test role line

outside = probe-t_4

```text
team-seat = probe-t_3
merger = probe-m_1
poster = probe-m_1, nobody_0
probe-seat = probe-t_4
ghost = nobody_9
```

after = probe-t_4
"""


def require_tmpdir():
    """The tests write only under $TMPDIR, so they refuse to run without it."""
    tmpdir = os.environ.get('TMPDIR')
    if not tmpdir or not os.path.isdir(tmpdir):
        raise RuntimeError('set TMPDIR to a scratch directory: the fixtures, caches, rosters '
                           'and traces all go under it')
    return tmpdir


def load_dio():
    """src/dio as a module, for the in-process tests (it has no .py suffix)."""
    loader = SourceFileLoader('dio', DIO)
    module = module_from_spec(spec_from_loader('dio', loader))
    loader.exec_module(module)
    return module


def proc_start(pid):
    """Field 22 of /proc/<pid>/stat, read here independently of dio."""
    with open('/proc/%d/stat' % pid, 'rb') as f:
        data = f.read()
    return data[data.rindex(b')') + 2:].split()[19].decode('ascii')


class Clock:
    """An injected clock: the grace is tested by moving it, never by sleeping."""

    def __init__(self):
        self.moment = datetime(2026, 10, 16, 1, 0, 0, tzinfo=timezone.utc)

    def __call__(self):
        return self.moment

    def advance(self, seconds):
        self.moment += timedelta(seconds=seconds)


class WatchClock:
    """dio watch's clocks, injected, so no test sleeps. sleep() records the seconds asked for,
    moves the real and the monotonic clock on by them, and then runs the actions set with
    at(n, action) for the end of the n-th sleep, counted from 1 over the clock's life, such as
    a file dropped into the watched directory."""

    START_NS = int(datetime(2026, 10, 16, 7, 0, 0, tzinfo=timezone.utc).timestamp()) * 10 ** 9
    MOST_SLEEPS = 10000  # a watch that never ends fails its test instead of hanging it

    def __init__(self):
        self.real, self.monotonic, self.sleeps, self.actions = self.START_NS, 10 ** 15, [], {}

    def real_ns(self):
        return self.real

    def monotonic_ns(self):
        return self.monotonic

    def advance(self, seconds):
        """Time that passes outside a watch, such as the seat's turn between two watches."""
        step = round(seconds * 10 ** 9)
        self.real += step
        self.monotonic += step

    def sleep(self, seconds):
        if len(self.sleeps) >= self.MOST_SLEEPS:
            raise AssertionError('the watch did not end')
        self.sleeps.append(seconds)
        self.advance(seconds)
        for action in self.actions.pop(len(self.sleeps), []):
            action()

    def at(self, sleep, action):
        self.actions.setdefault(sleep, []).append(action)


class World:
    def __init__(self):
        require_tmpdir()
        self.base = tempfile.mkdtemp(prefix='dio-test-')
        self.home = self.make('home')
        self.team_root = self.make('cfg-team', 'sessions')
        self.max_root = self.make('cfg-max', 'sessions')
        self.state = self.make('state')
        self.socks = self.make('socks')
        self.roles = os.path.join(self.base, 'ROLES.md')
        self.children = []
        self.listeners = []

    # -- building

    def make(self, *parts):
        path = os.path.join(self.base, *parts)
        os.makedirs(path)
        return path

    def live_process(self):
        child = subprocess.Popen([sys.executable, '-I', '-B', '-c', 'import sys; sys.stdin.buffer.read()'],
                                 stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
        self.children.append(child)
        return child.pid

    def dead_pid(self):
        """A pid whose process has exited and been reaped. Linux hands out pids in rising
        order, so it is not reused while a test runs unless the pid counter wraps."""
        child = subprocess.Popen([sys.executable, '-I', '-B', '-c', ''])
        child.wait()
        return child.pid

    def listen(self, name, directory=None):
        """Bind a Unix socket file at <directory>/<name>, by default in socks/; returns its path.

        A socket's address may hold at most 108 bytes (sun_path), and a long $TMPDIR passes
        that. So the bind uses the short relative name from inside the directory, and the
        working directory is restored at once. The socket file still sits at its full
        absolute path, which is what a sessions record names and what dio stats.
        """
        directory = directory or self.socks
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.listeners.append(listener)
        previous = os.getcwd()
        os.chdir(directory)
        try:
            listener.bind(name)
        finally:
            os.chdir(previous)
        return os.path.join(directory, name)

    def record(self, pid, name, status='busy', start=None, sock=None, **extra):
        """A sessions record shaped like Claude Code 2.1.301's, with extra keys it also writes."""
        record = {'pid': pid, 'procStart': start if start is not None else proc_start(pid),
                  'messagingSocketPath': sock if sock is not None else self.listen('%d.sock' % pid),
                  'name': name, 'status': status, 'version': VERSION,
                  'sessionId': '00000000-0000-4000-8000-%012d' % pid, 'cwd': self.base,
                  'startedAt': 1792112724000, 'updatedAt': 1792112724000,
                  'kind': 'interactive', 'nameSource': 'user', 'peerProtocol': 1}
        record.update(extra)
        return record

    def write(self, root, name, content):
        data = content if isinstance(content, bytes) else json.dumps(content).encode('utf-8')
        with open(os.path.join(root, name), 'wb') as f:
            f.write(data)
        return os.path.join(root, name)

    def session(self, root, record):
        return self.write(root, '%d.json' % record['pid'], record)

    def standard(self):
        team = self.team_root
        self.write(team, '123.key', CANARY)
        self.write(team, SECOND_CANARY, CANARY)
        os.symlink('123.key', os.path.join(team, '123.json'))
        self.busy = self.live_process()
        self.session(team, self.record(self.busy, 'probe-t_3'))
        self.idle = self.live_process()
        self.session(team, self.record(self.idle, 'probe-t_4', status='idle'))
        self.dead = self.dead_pid()
        self.session(team, self.record(self.dead, 'probe-t_2', start='100',
                                       sock=os.path.join(self.socks, 'gone.sock')))
        self.reused = self.live_process()
        self.session(team, self.record(self.reused, 'probe-t_1',
                                       start=str(int(proc_start(self.reused)) + 1)))
        self.write(team, TORN + '.json', TORN_BYTES)
        for name in JUNK:
            self.write(team, name, b'{}')
        self.max_live = self.live_process()
        self.session(self.max_root, self.record(self.max_live, 'probe-m_1'))
        with open(self.roles, 'w', encoding='utf-8') as f:
            f.write(ROLES)
        return self

    # -- running

    def roots(self):
        return ['--sessions-root', 'max=' + self.max_root, '--sessions-root', 'team=' + self.team_root]

    def who_flags(self):
        return self.roots() + ['--state-root', self.state, '--roles', self.roles]

    def env(self, **extra):
        """A minimal environment for a dio subprocess: HOME inside the world, TMPDIR kept,
        and none of the running session's CLAUDE_* variables."""
        env = {'HOME': self.home, 'PATH': os.environ.get('PATH', '/usr/bin:/bin'),
               'TMPDIR': os.environ['TMPDIR'], 'LANG': 'C.UTF-8'}
        env.update(extra)
        return env

    def run(self, *args, timeout=60, **extra_env):
        return subprocess.run([DIO] + list(args), env=self.env(**extra_env), capture_output=True,
                              text=True, timeout=timeout)

    def socket_of(self, pid):
        return os.path.join(self.socks, '%d.sock' % pid)

    def cache_files(self):
        cache = os.path.join(self.state, 'cache')
        return sorted(os.listdir(cache)) if os.path.isdir(cache) else []

    # -- tearing down

    def close(self):
        for child in self.children:
            if child.poll() is None:
                child.stdin.close()
                child.wait()
        for listener in self.listeners:
            listener.close()
        shutil.rmtree(self.base)
