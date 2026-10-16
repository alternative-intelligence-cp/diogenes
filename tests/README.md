# tests: the tests that persist

This is where the tests that are meant to persist go. Today they cover `src/dio`, build step 1 of cycle 0.0-min ([`../meta/roadmap/0.0/MIN.md`](../meta/roadmap/0.0/MIN.md)): `dio who`, `dio register`, their fixtures, and gate row M7a's strace test. They use `unittest` from the standard library.

## The command

From the repository root:

```sh
TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -v
```

- **`TMPDIR` must name an existing scratch directory, and the tests refuse to run without it.** Every fixture, grace cache, roster and trace is made by `tempfile` under it, and removed when its test (or, for M7a, its test class) ends. Each `dio` run the tests start gets `HOME` set inside that same temporary tree, and none of the running session's `CLAUDE_*` variables, so neither a flag nor a default can reach a real sessions directory or the real `~/.local/share/diogenes/`. No test hard-codes a scratch, cache, roster or trace path. One test reads this repository's own `meta/ROLES.md` on purpose, to show that it is the default role file.
- `-I -B`: isolated mode, and no bytecode, so no `__pycache__` appears in the repository.
- The tests need Linux's `/proc` and `strace` (for M7a). No test sleeps: the grace is tested with an injected clock.

Gate row M7a alone, in either form:

```sh
TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -p 'test_m7a*.py' -v
TMPDIR=<scratch dir> /usr/bin/python3 -I -B tests/test_m7a_strace.py
```

The second form prints the command it ran, the evidence lines from the trace (every line naming `123.json`, the half-written file or any `.key` path, and every `readlink`), the two rows' states, and `M7a: PASS` or `M7a: FAIL`, and exits 0 only on PASS.

## The strace command (gate row M7a)

`test_m7a_strace.py` builds the standard world below and runs, from the repository root:

```sh
strace -f -e trace=openat,open,readlink -o <scratch>/m7a.trace \
    src/dio who --sessions-root max=<scratch>/cfg-max/sessions \
                --sessions-root team=<scratch>/cfg-team/sessions \
                --state-root <scratch>/state
```

This is `MIN.md`'s command with `-o` added, so the trace goes to a file and not into `dio`'s stderr. strace prints path arguments in full. It passes when:

1. no `openat` or `open` line names any `.key` path;
2. the symlink `123.json` is refused: its one `openat` carries `O_NOFOLLOW` and returns `-1 ELOOP`, no `readlink` names it, and its row reads `unknown (refused: symlink)`;
3. the half-written file is opened (its `openat` returns a file descriptor), and its row reads `unknown (sessions format: …)`.

A further case checks that the detector flags `.key` paths in synthetic trace lines, so a pass is not a blind one. No test reads a `.key` file: the fixture builder only creates the canaries.

## The fixtures

`fixtures.py` generates them under `$TMPDIR`, and nothing is committed. The standard world is `MIN.md` step 1's list plus live entries:

| Where | Entry | What it shows |
|---|---|---|
| team `sessions/` | `123.key`, a canary holding one marker line | never opened |
| team `sessions/` | `123.json`, a symlink to the canary | refused, target never read |
| team `sessions/` | a stale file for a dead pid (`probe-t_2`) | the process check fails: no process |
| team `sessions/` | a reused pid with a different `procStart` (`probe-t_1`) | the process check fails: start time differs |
| team `sessions/` | `7777777.json`, a half-written JSON | `unknown (sessions format: …)` |
| team `sessions/` | a live entry, `status` busy (`probe-t_3`) | `live` |
| team `sessions/` | a live entry, `status` idle (`probe-t_4`) | `live-idle` |
| team `sessions/` | names that do not match `^[0-9]+\.json$`, and a second canary named like Claude Code's key files | discarded, never opened or logged |
| max `sessions/` | a live entry (`probe-m_1`) | the second account |
| `ROLES.md` | a test role line, with lines outside the fence | role resolution |

A live entry is a child process the test owns, blocked reading its stdin, with a real Unix socket file bound in the temporary tree. A socket's address may hold at most 108 bytes, and a long `TMPDIR` passes that, so `World.listen` binds each socket by its short name from inside its directory and restores the working directory at once. The socket file still sits at its full path, which `dio` only stats, and stat has no such limit. A dead pid is a child that has exited and been reaped. Linux hands out pids in rising order, so it is not reused while the tests run unless the pid counter wraps.

## What each file covers

- `test_dio.py`:
  - `ReaderTests`: the name filter, nothing else opened or logged, `O_NOFOLLOW` relative to the listed directory, the symlink, a FIFO (without blocking), a directory and a socket named like a sessions file, an unreadable file, a missing sessions directory.
  - `ParseTests`: the torn file, the version record, every listed field and type, duplicate keys, `NaN`, non-UTF-8, trailing data, more than 64 KiB, leading zeros, unlisted keys ignored, a null or absent name.
  - `ProcessCheckTests`: `live`, `live-idle`, the four `status` values, a reused pid, a dead pid, a missing socket, a path that is not a socket, a live session whose socket and sessions directory sit under a path longer than 108 bytes (read as `live`, and resolved by `--address`), the account as the directory read, `procStart` as field 22.
  - `GraceTests`: `unknown (checking)` until 60 seconds and then `gone`, the stored absolute times, the key by config dir and pid, removal on a passing check, a restarted grace for a new process, the first writer winning a race, pruning, an unwritable cache, a symlinked cache.
  - `OutputTests`: the columns, `--prefix` and its order, `--address` by role, exact name and bare prefix, `ambiguous: <n> live` with exit 1, `--highest`, roles with no live holder or several, lines outside the fence, sessions that are not live, a malformed or missing role file, `--highest` without `--address`.
  - `RegisterTests`: the roster entry and its fields, the fallback label, every refusal, the config dir key, a re-registration, and the roster in `dio who`, `--prefix` and `--address`, hidden behind a parsed sessions file, shown beside a mismatched one, through the grace when its process dies, and ignored when not in the format.
  - `CraftedNumberTests`: numbers in a crafted file that a float or `int()` cannot hold, each run through the built `dio`, with `--prefix` and `--address`: a 400-digit integer `startedAt` or `updatedAt` reads as `unknown (sessions format: …)`; a 400-digit integer in a roster entry leaves the entry out, with the warning; and a name ending in `_` and 5,000 digits gives its row, from a sessions file and from a roster entry.
  - `DefaultsTests`: the defaults are `MIN.md`'s paths, and `dio` uses them under `HOME` when no flag is given.
  - `EntryPointTests`: `src/dio` runs through its shebang in isolated mode (a module planted on `PYTHONPATH` is never imported), and writes no bytecode under `src/`.
  - `StaticTests`: `src/dio` holds no `.key` literal, and no file in `src/` or `tests/` holds a path under the Team tree.
- `test_m7a_strace.py`: gate row M7a, as above.
