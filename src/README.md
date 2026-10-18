# src: the Diogenes source

This is where the project's source code lives. Today it holds one file, `dio`, written for build steps 1 and 3 of cycle 0.0-min ([`../meta/roadmap/0.0/MIN.md`](../meta/roadmap/0.0/MIN.md)): `dio who` and `dio register` (step 1), and `dio watch` (step 3). It uses the Python standard library only (DQ-2).

## Running it

```sh
src/dio who                              # every session in both config dirs
src/dio who --prefix probe-t             # live sessions named probe-t…, by trailing _N
src/dio who --address team-seat          # a role, an exact live name, or a bare prefix
src/dio who --address probe-t --highest  # a bare prefix with several live: the highest _N
src/dio register <name>                  # the fallback: this seat's roster entry
src/dio watch <dir>                      # the seat runs it in the background: WAKE or REARM
src/dio watch <dir> --every 60 --max 3000  # the same, with its defaults written out
```

- **The shebang is `#!/usr/bin/python3 -IB`.**
  - `/usr/bin/python3`, not `/usr/bin/env python3`: the `python3` first on `PATH` on this machine is a Workspace virtual environment, and `dio` needs none of it. The system interpreter is the same for both accounts.
  - `-I`, isolated mode: Python ignores every `PYTHON*` environment variable and the user site directory, and leaves the script's own directory off `sys.path`.
  - `-B`: no bytecode is written. `dio` is a single file and imports nothing from `src/`, so no `__pycache__` appears in the repository either way.
  - Linux hands `-IB` to the interpreter as one argument, which Python reads as `-I -B`.
- **Nothing is installed.** `PATH`, settings and hooks are step 6, all `[author]`.

## The overrides

The defaults are `MIN.md`'s. Every test points all of them at temporary directories, and also sets `HOME` to one, so a forgotten flag cannot reach a real path.

| Flag | Command | What it points at | Default |
|---|---|---|---|
| `--sessions-root LABEL=PATH` | `who` | One sessions directory and the account label its rows carry. Repeatable. Given at all, it replaces both defaults | `max=~/.claude/sessions` and `team=~/.claude-team/sessions` |
| `--state-root PATH` | `who`, `register` | The directory that holds `cache/` (the grace cache) and `roster/` (`dio register`'s entries) | `~/.local/share/diogenes` |
| `--roles PATH` | `who --address` | The role file | `meta/ROLES.md` in the repository `dio` sits in |
| `--config-dir PATH` | `register` | The config dir that keys the entry | `$CLAUDE_CONFIG_DIR`, else `~/.claude` |
| `--pid N` | `register` | The session's pid | The number in the socket's file name, `<pid>.sock` |

`dio watch` has no default path to override: it watches only the directory it is given. Its tests inject its clocks and its sleep through `main`'s `clock` argument instead (`WatchClock` in `../tests/fixtures.py`), so no test sleeps.

## What `dio who` reads

- **Each sessions directory**, listed with `os.scandir`. It keeps only names matching `^[0-9]+\.json$`. Every other entry is dropped as `os.scandir` returns it, and is never opened, stat'ed or logged. It opens each match relative to the directory it listed, with `O_NOFOLLOW` and `O_NONBLOCK`, and refuses it unless `fstat` calls it a regular file: the kernel refuses a symlink before following it, and a FIFO cannot block the reader. There is no glob and no shell, and the source holds no `.key` literal (a test checks it).
- **The strict parse.** Required: `pid`, an integer equal to the number in the file's name, which has at most 10 digits (decision 4); `procStart`, a string of decimal digits; `messagingSocketPath`, an absolute path. Optional, and checked only when present: `sessionId` and `cwd` (strings), `name` (text or null), `status` (`busy`, `shell`, `idle` or `waiting`), `startedAt` and `updatedAt` (finite numbers, not negative, that a float can hold, so a 400-digit integer is a mismatch), and `version` (text). Any other key is ignored. The bytes must be UTF-8 JSON with no duplicate key and no `NaN` or `Infinity`, and the file at most 64 KiB. A file caught mid-rewrite fails this parse, so it counts as a mismatch for that pass.
- **The process check (DR-108).** `/proc/<pid>/stat` exists; its field 22, the process start time in clock ticks after boot, equals `procStart`; and `messagingSocketPath` is a socket. On this machine `procStart` is exactly that field: the Team seat's manager's file read `"5104572"`, and so did field 22 of its process's `/proc/3868039/stat` (checked 2026-10-15).
- **The account** is the label of the directory read.
- **The roster**, `roster/` under the state root, in `dio register`'s format. A roster entry is shown only when no strictly parsed sessions file in this pass has the same config dir and pid.
- **What `dio` opens, all told.** Besides what the Python interpreter opens to start, to read `src/dio` and to load the standard library, `dio` opens only: the sessions directories it lists, and in them only the names that match `^[0-9]+\.json$`, relative to the directory; `/proc/<pid>/stat` for each pid it checks, and `/proc/stat` for the boot time the `STARTED` column needs; the role file, under `--address`; and the state root, its `cache/` and `roster/`, the files in them named in its own formats, and the temporary files it makes there to publish an entry. Each temporary file is named `.tmp-<pid>-<12 hex>`, from `dio`'s own pid and six random bytes, and created with `O_CREAT`, `O_EXCL` and `O_NOFOLLOW`, mode 0600. `dio` writes the entry into it, then renames it over the entry's name, or, for a new grace entry, hard-links it to that name (so the first writer's time stands) and removes it. If the rename or the link fails, it removes the temporary file. `dio watch` opens only the directory it watches, at the start and at each poll, with `O_DIRECTORY` and `O_NOFOLLOW`; it lists the directory and stats the names that were not in it at the start, and opens none of them.
- **What it stats and prints from a file.** It stats, but never opens, the socket path that a sessions file or a roster entry names, once the entry has parsed and its pid and start time have passed the process check. It prints that path in the row's `SOCKET` column, and `--address` can print it, whatever the path is. So a crafted file from the same uid can make `dio` stat and print a `.key` path, though never open one. That is the same-uid risk `MIN.md` names as Risk 3: a hostile process of the same uid is not stopped.

## The output

`dio who` prints a table, two spaces between columns, with `STATE` last:

```text
ACCOUNT  NAME  PID  STARTED  VERSION  SOCKET  STATE
```

- `STARTED` is the process start time, worked out from `procStart` and `/proc/stat`'s `btime`, in UTC to the second. It is shown, never stored, and it is right only for a process of the current boot.
- `VERSION` is the file's own `version`, the version of the Claude Code that wrote it. In Claude Code 2.1.301 the writer sets it from its own `VERSION` constant.
- `STATE` is one of:

| State | When |
|---|---|
| `live` | The process check passed, and `status` is `busy`, `shell` or `waiting`, or absent |
| `live-idle` | The process check passed, and `status` is `idle`: the file's own idle flag, not DR-17's heartbeat age |
| `unknown (checking)` | The process check failed, less than 60 seconds ago by the grace cache |
| `gone` | The process check failed, and the 60-second grace has passed |
| `unknown (sessions format: <version>)` | The strict parse failed, a torn file included |
| `unknown (refused: symlink)`, `unknown (refused: not a regular file)` | The name matched, but the entry is not a regular file. Nothing behind it was read |
| `unknown (unreadable: <errno>)` | The file could not be opened or read |
| `unknown (no process check: <errno>)` | `/proc` or the socket could not be examined, so there is no evidence either way |

- **Every line that is not the sessions file's says so.** A roster row ends with `fallback: register`, and the grace cache's verdicts read `unknown (checking)` and `gone`.
- **`--prefix P`** prints the same table, holding only the live rows (`live` or `live-idle`) whose name starts with `P`, sorted by the trailing `_N`, with names that have none first.
- **`--address X`** prints one socket path, followed by `  fallback: register` if the row came from the roster. It tries, in this order:
  1. `X` as a role on the role line: the live holder's socket;
  2. `X` as an exact live name: its socket;
  3. `X` as a bare prefix, meaning a live name is `X_N`: the one match's socket.

  With several live matches it prints each as `<socket>  <name>  <account>`, then `ambiguous: <n> live`, and exits 1. Under `--highest`, a bare prefix resolves to the highest `_N` instead, and a note on stderr names the pick.
- **Exit status:** 0 for success; 1 when nothing live matches, a role has no live holder, an address is ambiguous, or `dio register` refuses; 2 for a usage error (a name with control characters given to `dio register` included) or a role file that cannot be read or parsed.

## What `dio` writes

`dio who` and `dio register` write only under the state root, and `dio watch` writes nothing. Each of the two opens the state root and its leaf directory with `O_NOFOLLOW`, so neither can be a symlink, and makes the leaf with mode 0700 if it is missing. Each file is created with mode 0600. Every stored time is a clock reading taken as the file is written, in ISO 8601 UTC with a `Z`, to the microsecond (`PROJECT_RULES.md` §5).

- **The grace cache**, `cache/grace-<config key>-<pid>.json`, written by `dio who`. The config key is the first 16 hex digits of the sha256 of the config dir's path, so the file is keyed by config dir and pid, and both accounts' runs share one file set. The fields are `configDir`, `pid`, `procStart`, `failedCheck` (which part failed), `firstFailedAt`, `graceSeconds` (60) and `goneAt`, an absolute time with the grace beside it.
  - The first failed check publishes the entry with `link()`, which never replaces an existing file, so when two runs race, the first writer's time stands.
  - An entry for an earlier process with the same pid (another `procStart`) is replaced, and its grace starts again.
  - A passing check removes the entry. After each pass, for each config dir whose sessions directory the pass listed, entries for pids with neither a sessions file nor a roster entry are removed, which keeps the cache small.
- **The roster**, `roster/<config key>-<pid>.json`, written by `dio register`. Its fields are `configDir`, `messagingSocketPath`, `name`, `pid`, `procStart` and `registeredAt`. A new registration from the same session replaces the old one.
  - The socket is `$CLAUDE_CODE_MESSAGING_SOCKET`. Claude Code 2.1.301 builds it from its own pid as `$XDG_RUNTIME_DIR/cc-socks/<pid>.sock`, and every socket observed so far has that form, so the pid is taken from the file name unless `--pid` is given.
  - The start time is `procStart` read from `/proc/<pid>/stat`, in the same unit as the sessions file's, so `dio who` runs the same process check on a roster entry.
  - `dio register` refuses when the variable is unset or not an absolute path, when the socket's file name gives no pid and `--pid` is not given, when there is no such process, or when the path is not a socket. A `--pid` so long that the kernel refuses `/proc/<pid>/stat` as too long a path (from 4,085 digits on this machine, where shorter ones read as no such file) gets the same `no process` refusal and exit 1 (D3v2's finding 2).

## `dio watch` (build step 3)

- **What the seat runs:** `dio watch <dir>` itself, with its Bash tool's `run_in_background` (decision 14). The process is the background `until` loop: until a new regular file is in `<dir>` or the cap has passed, it sleeps `--every` seconds. Its exit starts the idle seat's next turn, which is the mechanism DX-13's 10-minute leg measured ([`../meta/research/done/dx13-10min-2026-10-16/`](../meta/research/done/dx13-10min-2026-10-16/)). On a `WAKE` or a `REARM` it prints one line, as it exits, and nothing before.
- **The start.** It lists `<dir>` with `os.scandir`, then reads the real clock. That reading is the start, and the names listed are the files present at the start. A name present at the start never wakes the watch, whatever its mtime, even if the file is touched later, or removed and made again under that name (decision 15).
- **What wakes it.** It polls at once, then every `--every` seconds. Each poll opens `<dir>` again, checks that it is the same directory (device and inode), lists it, and stats each name that was not present at the start, relative to the directory and without following a symlink. The first regular file among them whose mtime is later than the start less 2 seconds ends the watch (decision 16). With several, it is the one with the earliest mtime, then the name that sorts first (decision 21). A symlink (even to a regular file), a directory, a FIFO or a socket never wakes it. No entry is ever opened or read: the seat reads the message, not `dio watch`.
- **The cap.** After `--max` seconds on the monotonic clock with no such file, it ends with `REARM <dir>`, and the seat re-arms (decision 17). The last sleep is cut to the cap, and a poll follows it, so a file that lands in the last interval still wakes it.
- **Output and exit status:**

| Exit | Standard output | When |
|---|---|---|
| 0 | `WAKE <path>` | A new regular file. `<path>` is `<dir>`, made absolute, joined with the file's name |
| 1 | `REARM <dir>` | The cap passed with no new regular file: re-arm |
| 2 | Nothing; the reason on stderr, a `dio watch: …` line, or argparse's usage and error for a usage error | A refusal at the start: no such directory, not a directory, a symlink (even to a directory), a directory it cannot read, or a usage error such as a bad flag. Or, during the watch, the directory gone, replaced by another, or unreadable, on a line that begins `dio watch: during the watch,` |

- **One line.** In a printed path, a backslash becomes `\\`, a byte that is not UTF-8 becomes `\xNN` of that byte, and a control character (C0, DEL or C1), U+2028 or U+2029 becomes `\xNN` or `\uNNNN`, so a crafted file name cannot add a line (decision 20). Any other path prints as it is.
- **Flags.** `--every` and `--max` take whole seconds from 1 to 86400 (decision 22). An `--every` longer than `--max` sleeps once, to the cap.
- **Only for an inbox.** `dio watch` lists whatever directory it is given. Pointed at a `sessions/` directory, it would list that directory, which `MIN.md`'s `USING.md` rule 7 ("Nobody runs a shell listing of any `sessions/` directory") keeps seats from doing, and it could print a new `.key` file's path in its `WAKE` line. So [`USING.md`](../docs/USING.md), build step 5, names the inbox as its one target ("Watching the inbox").

### How it compares times

- Both times are integer nanoseconds: the start from `time.time_ns()`, and the file's `st_mtime_ns`. A new name counts when its mtime is later than the start less `MTIME_MARGIN_NS`, which is 2 seconds.
- **Why a margin.** The kernel stamps a file's mtime from its coarse clock, which trails `time.time_ns()`. `clock_getres(CLOCK_REALTIME_COARSE)` is 1 ms here (`CONFIG_HZ=1000`), yet the lag can pass one tick: the worst on record, below, is 1.849 ms. On this machine's ext4 (`/`, which holds `/home`), every file made right after a `time.time_ns()` reading carried an mtime before it, on 2026-10-16, in four runs: 3,000 of 3,000, worst 0.64 ms (`diogenes_0`); 2,000 of 2,000, worst 1.141 ms (the Team seat's manager, at 03:06); 2,000 of 2,000, worst 1.006 ms (D4, at 03:19); and 6,000 of 6,000 in three batches of 2,000, worst 1.849 ms (D4v, build step 3's verifier, between 03:52 and 04:17, its finding 5; `MIN.md`'s status block names its report). So "newer than start", against the start itself, would miss a file made within that lag of the start.
- **Why 2 seconds is safe.** The names present at the start, not the mtime, keep out every file present at the start. So the margin can only let in a new name whose mtime is at most 2 s before the start, which is a file that arrived after the listing. 2 s is about 1,080 times the worst lag on record, 1.849 ms in D4v's run, the highest of the four runs above. It also covers a filesystem that keeps whole seconds, whose truncation stays under 1 s. A new name with an older mtime, such as a file moved in with its own, does not count until its mtime is later.
- **The cap's clock.** The cap is timed on the monotonic clock, so a step of the real clock neither stretches the watch nor cuts it short.
- **A step back of the real clock** by more than 2 s during a watch can hide later files from the watch, and from the seat's rule alike (D4v's finding 6). A file that lands while the real clock reads earlier than the start less 2 s carries an mtime the watch does not count, and no later watch reports it, since its name is present at their start. The seat's rule (below) compares mtimes with its own reading, taken just before that watch, so it misses a file that lands while the real clock reads earlier than that reading less 2 s. With the real clock stepped back an hour, D4v's run ended in `REARM`, and so does `GapTests`' case of it in `../tests/test_watch.py`.

### The cap, provisional

- `--max` defaults to 3000 s, 50 minutes. **It is provisional until the gate's DX-13 legs**, the 2-hour and overnight waits (`MIN.md` step 2; the author's steps, B3), which decide it.
- **The time past 10 minutes is untested until the gate's 2-hour leg.** The one background loop measured lived about 10 minutes (00:52:05 to 01:02:35 EDT on 2026-10-16) before its exit woke the seat. `dio watch --help` says the same.
- **Why 50 minutes,** from the 10-minute leg's record. Each exit of the loop wakes the seat for one model turn (DX-13; the 10-minute leg measured one), so a capped exit costs one too. That wake's recorded request read about 467 k cached tokens, for a working seat at 46–47 % of its context. A 10-minute cap would wake an idle seat six times an hour, and 50 minutes about once. The record also found every request asking for a one-hour cache life (the usage labels it five minutes), with the wake reading the cache 9 min 56 s after its last write, and it expects a wake past an hour to write the context again, about 467 k tokens for that seat. 50 minutes keeps each capped wake inside the hour, with 10 minutes to spare.

### The re-arm gap, and the seat's rule

- **The gap.** A file that lands between one watch's exit (`WAKE` or `REARM`) and the next watch's start is present at that start, so no later watch reports it. So is a second file that lands within one poll of the first: the watch reports one, and exits. `MIN.md` is silent on this, in step 3 and in the `USING.md` rules.
- **The choice: the seat covers it, and `dio watch` prints only step 3's lines** (decision 18). The rule, which [`USING.md`](../docs/USING.md) carries ("The seat's rule"):
  1. Just before arming each watch, read the clock, and note the reading in the log.
  2. After every exit, `WAKE` or `REARM`, re-arm first.
  3. Then read every regular file in the directory whose mtime is later than the reading taken before the watch that just exited, less 2 seconds.
- **Why it misses nothing.** By the margin argument above, a file that lands after a reading has an mtime later than that reading less 2 s. So a wake's read finds every file that landed after the reading before the watch that just exited, and up to the read itself. A file that lands later is found by the next wake, `WAKE` or `REARM`, at most `--max` later. That includes a file that lands after the read but before the new watch's listing, which that watch never reports. A file can be read twice, and the seat skips one it has handled.
- **The other way, not taken:** each exit line could carry that watch's start (`diogenes_0`'s suggestion). It needs no reading kept by the seat, but it would change the `WAKE` line, which step 3 fixes as "`WAKE <path>` on one line", or add a line beside it. And a start that `dio watch` reads comes after the seat's own reading. If the seat's read ever ran before the new watch's listing, a file landing between the two would be covered only by the margin, while the seat's own reading covers it in either order. Taking it instead is `diogenes_0`'s call.

## Decisions the build made

The plan is silent on these points. Each is listed for `diogenes_0`'s review. Decisions 1–13 are build step 1's, and 14–22 are build step 3's.

1. **One file, `src/dio`.** No package, no `sys.path` change under `-I`, no bytecode in the tree. Later commands (`dio watch`, `dio meters`) can be added to it or split out.
2. **"Strict" means types and presence, not a closed key set.** The Team seat manager's sessions file holds 18 keys, and `MIN.md` lists 9. Rejecting unknown keys would turn every real file into a mismatch. The checks also come from 2.1.301's own code: its reader accepts exactly the four `status` values above, and its writer sets `startedAt` and `updatedAt` from `Date.now()`. Any other `status` value is a mismatch, so a format change shows instead of being guessed at.
3. **The version record.** Each row records its file's `version` when the file is read, which is once per pass. A mismatched file shows its own `version` if that could be read. Otherwise it shows the `version` of the first file in the same directory, in pid order, that parsed in the same pass and carries one, or else `version unknown`. Nothing is persisted, because `dio who` writes only its grace cache (`MIN.md`, the DR-107 row).
4. **`pid` must equal the file's name, and the name has at most 10 digits.** `0123.json`, a file whose `pid` is another number, and a file whose name has more than 10 digits, whatever its `pid`, are mismatches. The bound: Linux's `pid_t` is a signed 32-bit integer, so no pid passes 2147483647, which has 10 digits, and the kernel's own ceiling is lower (`/proc/sys/kernel/pid_max` reads 4194304 on this machine). The roster, grace-cache and socket names already allowed 1 to 10 digits. **Changed in build step 3** (D4), on D3v2's finding 1: until then the name had no bound, so a file named with up to 250 digits, the filesystem's limit for the name, passed the parse, and from 228 digits its grace-cache file's name passed 255 bytes, so its row read `unknown (checking)` for ever, with a warning on every run.
5. **A refused or unreadable entry is a row**, as `unknown (refused: …)` or `unknown (unreadable: …)`, not a silent skip. An entry whose name does not match is still discarded silently.
6. **The socket must be a socket**, not merely a path that exists.
7. **The grace cache is one file per entry**, published with `link()` and timed by `goneAt`. If the cache cannot be written, a failed check stays `unknown (checking)`, with a warning, because nothing can time the grace.
8. **A bare prefix is the name without its trailing `_N`**, so `--address probe-t` matches `probe-t_3` but not `probe-tx_1`, and `--address probe-t_1` never falls through to `probe-t_10`. `--prefix` matches any name that starts with `P`, as `MIN.md` words it.
9. **`--highest` applies to a bare prefix only**, as `MIN.md` words it. A role with several live holders, or an exact name live twice, is reported as ambiguous.
10. **The role file defaults to `meta/ROLES.md` in the clone `dio` runs from**, its working tree. A clone that has not pulled `main` reads an older role line. A missing role file gives a note and leaves names and prefixes working; an unreadable or malformed one is exit 2.
11. **`dio register` keys the entry by the config dir from `$CLAUDE_CONFIG_DIR`** (else `~/.claude`), or `--config-dir`. `PROJECT_RULES.md` §7 warns that the environment can be scrubbed, so a scrubbed variable keys a Team seat's entry under `~/.claude`.
12. **`--prefix` with no live match exits 1,** as `grep` does.
13. **A name that ends in a very long `_N` is shown like any other name, from a sessions file or a roster entry.** `dio` sorts by `N` as text, fewer digits after any leading zeros first and then digit by digit, which is numeric order at any length. It does not use `int()`, which refuses more than 4300 digits by default. So a name ending in `_` and 5,000 digits gives its ordinary row, sorted by that `N`, and `--prefix`, `--address` and `--highest` treat it as they treat any name. From a roster entry, the row ends `fallback: register`, as every roster row does. The reason: the name is text with no control characters and no lone surrogates, which is all the strict parse asks of `name` and all `dio register` asks of the name it registers, and `dio register` writes such an entry and reports it registered. Leaving the entry out would hide a seat that `dio register` has just confirmed.

14. **`dio watch` is the background `until` loop itself.** This is the reading of step 3's "Prints the background `until` loop the seat runs": the seat runs `dio watch <dir>` with `run_in_background`, and what `dio watch` prints is its one exit line. Step 3's next sentence, "It records its start time and exits on the first regular file in the directory whose mtime is later than that start, printing `WAKE <path>` on one line", describes a process that waits. So do M4 ("An idle Max probe starts `dio watch ~/.local/share/diogenes/inbox/max --every 60`"), step 4 ("The receiver watches its own directory with `dio watch`") and the summary ("the seat's own background wait on a directory"). A printed shell loop could not hold the names present at the start (decision 15) for the watch's life without writing them somewhere, and could not take an injected clock and sleep in a test. The other reading, a form that prints the line the seat runs, would need a flag beyond step 3's signature, so it is not built. `MIN.md`'s words allow both readings, so this is a choice.
15. **The start lists the directory, then reads the clock, and a name listed then never wakes the watch.** That is M4's "pre-existing files never trigger", which "newer than start" alone would not give, since a file can carry an mtime after the start. The names are kept, not the files: a file touched later, or removed and made again under a listed name, never wakes it either. Listing first means that a file landing between the listing and the reading is new, and its mtime falls inside the margin.
16. **A new name counts when its mtime is later than the start less 2 seconds.** The measurements and the reason are under "How it compares times". Without the margin, "newer than start" misses a file made within the coarse clock's lag of the start, which reached 1.849 ms in the runs on record.
17. **The cap.** `--max` defaults to 3000 s, provisional until the gate's DX-13 legs, for the reasons under "The cap, provisional". A capped exit prints `REARM <dir>` and exits 1, so the seat can tell it from a `WAKE` (exit 0) and from a refusal (exit 2). Exit 1 is "nothing came", as for `--prefix` with no live match (decision 12). The cap runs on the monotonic clock.
18. **The re-arm gap is the seat's to cover**, by the rule under "The re-arm gap, and the seat's rule", which `USING.md` (step 5) carries. It needs nothing from `dio watch` beyond step 3's words, and the seat's reading, taken before it arms, covers a file landing between its read and the new watch's listing in either order. `diogenes_0`'s alternative, exit lines that carry each watch's start, is set out there.
19. **The directory must be a real directory.** It is opened with `O_DIRECTORY` and `O_NOFOLLOW`, so a symlink is refused even to a directory, as `dio` refuses one for the zone's directories; a link put in an inbox's place cannot turn the watch onto another directory. Each poll opens it again, and if it is gone, unreadable, or another directory (another device and inode), the watch ends with exit 2, so the seat hears of it at once rather than at the cap.
20. **A printed path is absolute and on one line.** A relative `<dir>` is joined to the working directory, so the `WAKE` path still names the file after the seat's working directory changes. The escapes keep a crafted name to its line: it still wakes the seat, and the seat sees what is odd about it.
21. **The first of several new files is the one with the earliest mtime, then the name that sorts first**, so the pick does not depend on the order the directory lists them in.
22. **`--every` and `--max` take whole seconds from 1 to 86400.** Step 3's `--every 60` is in whole seconds. The bound of one day is past the overnight leg, the longest the gate will measure, and keeps `time.sleep` far from its limit: `time.sleep(1e20)` raises `OverflowError`, which would be a traceback.

## Not in this step

The `claude agents --json` fallback (built last, by `MIN.md`'s size table), `dio meters`, the task template, and any install. The `SessionStart` hook design is not built. Build step 5's [`docs/USING.md`](../docs/USING.md) carries the inbox's `printf` line and the seat's re-arm rule above.
