# tests: the tests that persist

This is where the tests that are meant to persist go. Today they cover `src/dio`, build steps 1, 3 and 7 of cycle 0.0-min ([`../meta/roadmap/0.0/MIN.md`](../meta/roadmap/0.0/MIN.md), and for step 7 [`../meta/roadmap/0.0/FINISH.md`](../meta/roadmap/0.0/FINISH.md)): `dio who`, `dio register`, their fixtures, gate row M7a's strace test, `dio watch`, and `dio meters`. They also cover what can be checked in build step 5's [`../docs/USING.md`](../docs/USING.md), with step 4's inbox, and [`../docs/TASK-TEMPLATE.md`](../docs/TASK-TEMPLATE.md): their rules and lines against `MIN.md`'s, and their documented commands, each run against a scratch tree. They use `unittest` from the standard library.

## The command

From the repository root:

```sh
TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -v
```

- **`TMPDIR` must name an existing scratch directory, and the tests refuse to run without it.** Every fixture, grace cache, roster, watched directory and trace is made by `tempfile` under it, and removed when its test (or, for M7a, its test class) ends. Each `dio` run the tests start gets `HOME` set inside that same temporary tree, and none of the running session's `CLAUDE_*` variables, so neither a flag nor a default can reach a real sessions directory, the real `~/.local/share/diogenes/`, or a real usage file, context directory or ledger. No test watches a directory outside its temporary tree. Each line from `docs/USING.md` that `test_using.py` runs gets `HOME` set to a scratch home in that tree, which holds the zone's inbox at mode 0700, and the test refuses to run a line that names the zone other than through `~`, so no run reaches the real inbox. No test hard-codes a scratch, cache, roster or trace path. One test reads this repository's own `meta/ROLES.md` on purpose, to show that it is the default role file.
- `-I -B`: isolated mode, and no bytecode, so no `__pycache__` appears in the repository.
- The tests need Linux's `/proc` and `strace` (for M7a, for the reader test that traces every system call taking a path, for `dio watch`'s strace case, for the `printf` line's, and for `dio meters`' `MetersStraceTests`); `test_meters.py` runs `FINISH.md`'s M5 aging line as printed, with `/usr/bin/python3`; and `test_using.py` needs `/bin/bash`, GNU findutils' `find`, `date`, `sort`, `sha256sum` and `cut`; `test_template.py` needs `git`, which it runs only in a scratch repository it makes, with `GIT_CONFIG_NOSYSTEM` set and `GIT_CONFIG_GLOBAL` at `/dev/null`. No test sleeps: the grace is tested with an injected clock, and once through the built `dio` on the real clock, with the cache entry's times moved back. `dio watch` runs on `fixtures.WatchClock`, whose sleep only moves its clocks on and drops the files a test sets, and `dio`'s real sleep is patched to fail in every case that runs `dio watch` in-process. The built `dio watch` runs only where it exits at once: its refusals and its help.

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

`test_meters.py` builds its own usage files, context files and ledgers under the same temporary tree, from `FINISH.md`'s shapes and the Team status line writer's, and copies none from a real file.

`WatchClock` is `dio watch`'s injected clocks: a real clock that starts at 2026-10-16T07:00:00Z, a monotonic one, and a sleep that records the seconds asked for, moves both clocks on by them, and then runs the actions set for the end of that sleep (`at(n, action)`, counting sleeps from 1). A test drops a file in such an action, with its mtime set from the clock, so a watch sees it arrive.

## What each file covers

- `test_dio.py`:
  - `ReaderTests`: the name filter, nothing else opened or logged, no non-matching name or canary named by any system call that takes a path (an strace of `%file`, which holds the stat calls, so none is stat'ed), `O_NOFOLLOW` relative to the listed directory, the symlink, a FIFO (without blocking), a directory and a socket named like a sessions file, an unreadable file, a missing sessions directory.
  - `ParseTests`: the torn file, the version record, every listed field and type, duplicate keys, `NaN`, non-UTF-8, trailing data, more than 64 KiB, leading zeros, a name of more than 10 digits (a mismatch row, with no grace entry and no warning, while 10 digits still parse; through the built `dio`), unlisted keys ignored, a null or absent name.
  - `ProcessCheckTests`: `live`, `live-idle`, the four `status` values, a reused pid, a dead pid, a missing socket, a path that is not a socket, a socket path `dio` cannot examine (`unknown (no process check: EACCES)`, with no grace started), a live session whose socket and sessions directory sit under a path longer than 108 bytes (read as `live`, and resolved by `--address`), the account as the directory read, `procStart` as field 22.
  - `GraceTests`: `unknown (checking)` until 60 seconds and then `gone`, asserted as those literal texts (gate row M6's), in-process and as the built `dio` prints them, the stored absolute times, the key by config dir and pid, removal on a passing check, a restarted grace for a new process, the first writer winning a race, pruning, an unwritable cache, a symlinked cache.
  - `OutputTests`: the columns, `--prefix` and its order, `--address` by role, exact name and bare prefix, in that order (a role before a live name equal to it, an exact name before a bare prefix), `ambiguous: <n> live` with exit 1, an exact name live twice (ambiguous, even with `--highest`), `--highest`, roles with no live holder or several, lines outside the fence, sessions that are not live, a malformed or missing role file, `--highest` without `--address`.
  - `RegisterTests`: the roster entry and its fields, the zone directories `cache/` and `roster/` made with mode 0700, the fallback label, every refusal (a `--pid` of 4,200 digits, too long for `/proc` to name, among them: `no process`, exit 1, no traceback, through the built `dio`), the config dir key, a re-registration, and the roster in `dio who`, `--prefix` and `--address`, hidden behind a parsed sessions file, shown beside a mismatched one, through the grace when its process dies, and ignored when not in the format.
  - `TemporaryFileTests`: each grace or roster entry is published through one `.tmp-<pid>-<12 hex>` file, made with `O_EXCL` and `O_NOFOLLOW`, mode 0600, which is hard-linked (a new grace entry) or renamed over the name (a replaced grace entry, a roster entry), and none is left in `cache/` or `roster/`.
  - `CraftedNumberTests`: numbers in a crafted file that a float or `int()` cannot hold, each run through the built `dio`, with `--prefix` and `--address`: a 400-digit integer `startedAt` or `updatedAt` reads as `unknown (sessions format: …)`; a 400-digit integer in a roster entry leaves the entry out, with the warning; and a name ending in `_` and 5,000 digits gives its row, from a sessions file and from a roster entry.
  - `DefaultsTests`: the defaults are `MIN.md`'s paths, and `dio` uses them under `HOME` when no flag is given.
  - `EntryPointTests`: `src/dio` runs through its shebang in isolated mode (a module planted on `PYTHONPATH` is never imported), and writes no bytecode under `src/`.
  - `StaticTests`: `src/dio` holds no `.key` literal, `src/README.md`'s "What `dio` opens, all told" names the `.tmp-<pid>-<12 hex>` files and what `dio` does with them, and no file in `src/` or `tests/` holds a path under the Team tree.
- `test_m7a_strace.py`: gate row M7a, as above.
- `test_watch.py`, `dio watch` (`MIN.md` step 3), each case on an inbox in the temporary tree that holds files present at the start:
  - `WakeTests`: a new regular file ends the watch with `WAKE <path>` and exit 0; a relative directory prints as an absolute path; files present at the start never wake it, with mtimes an hour before the start, at it and an hour after it, touched or replaced during the watch; a new file stamped 1 ms before the start wakes it; the start lists the directory before it reads the clock (a file that the clock's one reading drops wakes it at the first poll, which a watch that read the clock first would never report; D4v's finding 1); the 2-second margin, at its edge and 1 ns inside it; a new name with an hour-old mtime wakes it only once touched; only a regular file wakes it (not a symlink to one, a directory, a FIFO or a socket); the first of several is the earliest mtime, then the first name; a file in the last interval still wakes it; a name gone between the listing and its stat is skipped.
  - `CapTests`: `REARM <dir>` and exit 1 at the cap; the defaults, every 60 s and a 3000 s cap; the last sleep cut to the cap; an `--every` longer than `--max`; one day for both; the cap on the monotonic clock, unmoved by a step of the real clock either way.
  - `RefusalTests`: exit 2 for a missing directory, a regular file, a FIFO, a socket, a symlink to a directory and a directory it cannot read, each with its message; bad flags (0, negative, decimal, text, past 86400, non-ASCII digits, empty; no `DIR`, an unknown flag, two `DIR`s); the built `dio` refusing at once, with no traceback.
  - `DuringTests`: exit 2 when the directory is removed, replaced by another, or made unreadable during the watch.
  - `OneLineTests`: a name with a newline prints on one line, escaped; a byte that is not UTF-8, a backslash, U+2028 and a C1 control are escaped; an ordinary path prints as it is.
  - `NeverOpenedTests`: in-process, `dio watch` opens only the directory, with `O_DIRECTORY` and `O_NOFOLLOW`, stats only the names new since the start, each relative to the directory without following, and never stats a file present at the start. Two dangling symlinks, one present at the start and one new, never wake it: neither is opened or read through, the one present at the start is never stat'ed, the new one is stat'ed unfollowed, and neither target is named (D4v's finding 8).
  - `StraceTests`: `dio watch` in a child process under `strace -e trace=%file`, whose injected sleep runs a second, untraced process that drops a FIFO, a symlink to a canary, a dangling symlink, a directory, a socket and then a regular file, with a dangling symlink present at the start: the trace opens only the directory, writes nothing, names no file present at the start, no link's target and not the canary, and stats each new name with `AT_SYMLINK_NOFOLLOW`.
  - `GapTests`: the re-arm gap. A file dropped between two watches, one dropped after the seat's reading but before the next listing, and a second file within one poll of the first wake no later watch, and the seat's rule (src/README.md) reads each of them. A step back of the real clock by an hour hides a later file from the watch and from the seat's rule; after a step back of 2 s, a minute in, a later file still wakes it (D4v's finding 6).
  - `HelpTests`: `dio watch --help` and `src/README.md` say the default cap is provisional and that the time past 10 minutes is untested until the gate's 2-hour leg. `src/README.md` sets the 2-second margin against the worst lag on record, 1.849 ms (about 1,080 times), names the four runs it rests on (D4v's finding 5), and says that a step back of the real clock by more than 2 s can hide later files from the watch and from the seat's rule (D4v's finding 6).
- `test_using.py`, `docs/USING.md` (`MIN.md` steps 4 and 5). Each documented line runs under `/bin/bash` with `HOME` at the scratch home above, `TZ` 14 hours east of UTC, and `/dev/null` on stdin, since at shell level 1 a `bash -c` with a socket on stdin reads `/etc/bash.bashrc` and `~/.bashrc`:
  - `RuleTests`: the nine rules are `MIN.md`'s word for word, in its order and with its numbers, but for rule 4's holder, the `merger` line's; decision U1 quotes `MIN.md`'s two precedents; each caveat's bold statement is `MIN.md`'s word for word, (i) to (iii) carry the label `MIN.md`'s note gives each, and (iv), which the note leaves without a label, carries *Documented* and says that the note gives it none; the six items from `MIN.md`'s notes and decisions U1 to U6 are there; the Write-tool route carries the label *Measured*, with what was measured and the note it cites, and says it was not measured from a seat inside a strict sandbox; and no line of the file ends in whitespace.
  - `PrintfTests`: the filled-in example is the template with its parts; it writes one message in place, named in UTC, with its lines as its bytes, in the other account's inbox only; each quoted line is kept byte for byte, `%`, `\`, `$` and a single quote among them; a second message with the same name is refused and the first stays as it was; `set -C` refuses a link to a regular file or a dangling link at the name, and writes through a link to `/dev/null` (decision U4's limit); under strace, the line opens the final name once, with `O_EXCL`, and never renames or links; and a message it writes wakes a `dio watch` on the scratch inbox, run in-process on the real clock with a sleep that runs the line.
  - `SeatRuleTests`: the seat's `command find` line, run just after a shell function named `find` that fails is defined in the same shell, as Claude Code's Bash tool defines one that runs bfs, lists the regular files in the inbox itself whose mtime is strictly later than the reading less 2 s, to the nanosecond, and reads every file that the re-arm gap hides from `dio watch` (`GapTests`' case).
  - `RosterRemovalTests`: the `rm` line removes the entry that `dio register` wrote, with `CLAUDE_CONFIG_DIR` set and unset, after its process has ended; the next `dio who` shows no row for it and drops its grace entry. With `CLAUDE_CONFIG_DIR` set with a trailing slash, the line hashes another key, so its `rm` finds no file and the entry stays, and the `ls` line shows the entry's name.
- `test_template.py`, `docs/TASK-TEMPLATE.md` (`MIN.md` step 5):
  - `TemplateTests`: the template holds `MIN.md`'s nine required lines in its order, after a title line, with the lines filled later left empty; its table says what each line holds, who fills it, where and when, in the same order; decision 5's values for `room-at-post` and `cross-account`; the poster check and its `refused: poster`; the fillers as D1v's finding 2 is settled, with the words of `meta/tasks/README.md` that decision T1 rests on still in that file; and no line of the file ends in whitespace.
  - `PosterLineTests`: the poster check's `git` line, run in a scratch repository whose poster line rotates after a task file is added, prints `meta/ROLES.md` as it stood in the commit that added the task, and `dio`'s own reader takes its `poster` line from inside the fenced block.
- `test_meters.py`, `dio meters` (`FINISH.md` step 7). Every flag points into the temporary tree, and the in-process runs take `fixtures.Clock`:
  - `UsageTests`: a fresh file reads `measured`, with its age, its figures and its resets in UTC; `measured` to 600 s and `stale (<N> min)` past it, N rounded down; a negative age reads `measured` (decision 29); `FINISH.md`'s M5 aging line, run as printed on a Max-shaped and a Team-shaped copy, then the built `dio` within the minute: `stale (12 min)` on both lines; an absent file or directory; a symlink, refused, its target never opened; a FIFO, refused without blocking (through the built `dio`); a path naming a directory; a file of 64 KiB read, and one byte more `usage format`; a duplicate key; `NaN` and `Infinity`; a `written_at` that is not an integer time; every other departure from the format; a `null` window; keys the format does not name; an unreadable file.
  - `ExitTests`: 0 when both `usage` lines read `measured`, 1 when either does not; no other line changes it; a usage error exits 2 through the built `dio`, with no traceback.
  - `ModelLimitsTests`: one compact line in the file's order for a Max-shaped file; none for a Team-shaped file or for a file not in the format, and one for a stale file; `-` for a value JSON cannot hold; decision 20's escapes.
  - `ContextTests`, on the standard world: `parse_session` also returns `sessionId`; the name by `sessionId`; `statusline:<name>` with no match, and `-` with no `session_name` either; `-` for a match whose name is `null`; a sessions file that does not parse names nothing; the highest pid when two carry one id; a `null` or absent figure; the figure as the file gives it; the age and state; only names like the writer's read, the rest, `.ctx.*` among them, never opened; bad JSON and every other departure read `context format`; a symlink, a FIFO and a directory refused (through the built `dio`); the join for a file that reads `unknown`; the order by account, then session id; a context directory that cannot be read; a sessions directory that cannot be read; a file removed after the listing.
  - `CreditsTests`: both pools; every row in the file's order, other lines skipped; both ledgers in the order given, each labelled by its source; decision 20's escapes for a tab, a backslash, a control character, U+2028, a byte that is not UTF-8 and a carriage return; another header, no separator, a separator of 7 cells, an empty file; a separator with alignment colons; a row of 7 or 9 cells among good rows; no ledger, a link and a directory; a ledger of 1 MiB read, and one byte more `ledger format`.
  - `OutputTests`: the kinds in their order, each line with its record's number of fields; a name from either file escaped; `dio meters --help` names every flag and its default.
  - `NoFlagTests`: the defaults are `FINISH.md`'s paths, under `HOME`; with no flag, every path `dio meters` opens is under `HOME` (in-process, by the directories its relative opens name); the built `dio` with no flag reads the files at the defaults.
  - `MetersStraceTests`, the one test here that runs strace: the standard world, with usage, context and ledger files, under `strace -f -e trace=%file`. No traced call names a `.key` path, nothing is opened for writing, no rename, link, unlink, directory or other write-type call is made, and the context directory's other names, a `.ctx.*` file among them, are never named.
