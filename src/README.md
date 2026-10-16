# src: the Diogenes source

This is where the project's source code lives. Today it holds one file, `dio`, written for build step 1 of cycle 0.0-min ([`../meta/roadmap/0.0/MIN.md`](../meta/roadmap/0.0/MIN.md)): `dio who` and `dio register`. It uses the Python standard library only (DQ-2).

## Running it

```sh
src/dio who                              # every session in both config dirs
src/dio who --prefix probe-t             # live sessions named probe-t…, by trailing _N
src/dio who --address team-seat          # a role, an exact live name, or a bare prefix
src/dio who --address probe-t --highest  # a bare prefix with several live: the highest _N
src/dio register <name>                  # the fallback: this seat's roster entry
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

## What `dio who` reads

- **Each sessions directory**, listed with `os.scandir`. It keeps only names matching `^[0-9]+\.json$`, and discards every other entry unread, unstat'ed and unlogged. It opens each match relative to the directory it listed, with `O_NOFOLLOW` and `O_NONBLOCK`, and refuses it unless `fstat` calls it a regular file: the kernel refuses a symlink before following it, and a FIFO cannot block the reader. There is no glob and no shell. No code path lists, opens or names a key file, and the source holds no `.key` literal (a test checks it).
- **The strict parse.** Required: `pid`, an integer equal to the number in the file's name; `procStart`, a string of decimal digits; `messagingSocketPath`, an absolute path. Optional, and checked only when present: `sessionId` and `cwd` (strings), `name` (text or null), `status` (`busy`, `shell`, `idle` or `waiting`), `startedAt` and `updatedAt` (finite numbers, not negative, that a float can hold, so a 400-digit integer is a mismatch), and `version` (text). Any other key is ignored. The bytes must be UTF-8 JSON with no duplicate key and no `NaN` or `Infinity`, and the file at most 64 KiB. A file caught mid-rewrite fails this parse, so it counts as a mismatch for that pass.
- **The process check (DR-108).** `/proc/<pid>/stat` exists; its field 22, the process start time in clock ticks after boot, equals `procStart`; and `messagingSocketPath` is a socket. On this machine `procStart` is exactly that field: the Team seat's manager's file read `"5104572"`, and so did field 22 of its process's `/proc/3868039/stat` (checked 2026-10-15).
- **The account** is the label of the directory read.
- **The roster**, `roster/` under the state root, in `dio register`'s format. A roster entry is shown only when no strictly parsed sessions file in this pass has the same config dir and pid.

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

Both commands write only under the state root. Each opens the state root and its leaf directory with `O_NOFOLLOW`, so neither can be a symlink, and makes the leaf with mode 0700 if it is missing. Each file is created with mode 0600. Every stored time is a clock reading taken as the file is written, in ISO 8601 UTC with a `Z`, to the microsecond (`PROJECT_RULES.md` §5).

- **The grace cache**, `cache/grace-<config key>-<pid>.json`, written by `dio who`. The config key is the first 16 hex digits of the sha256 of the config dir's path, so the file is keyed by config dir and pid, and both accounts' runs share one file set. The fields are `configDir`, `pid`, `procStart`, `failedCheck` (which part failed), `firstFailedAt`, `graceSeconds` (60) and `goneAt`, an absolute time with the grace beside it.
  - The first failed check publishes the entry with `link()`, which never replaces an existing file, so when two runs race, the first writer's time stands.
  - An entry for an earlier process with the same pid (another `procStart`) is replaced, and its grace starts again.
  - A passing check removes the entry. After each pass, for each config dir whose sessions directory the pass listed, entries for pids with neither a sessions file nor a roster entry are removed, which keeps the cache small.
- **The roster**, `roster/<config key>-<pid>.json`, written by `dio register`. Its fields are `configDir`, `messagingSocketPath`, `name`, `pid`, `procStart` and `registeredAt`. A new registration from the same session replaces the old one.
  - The socket is `$CLAUDE_CODE_MESSAGING_SOCKET`. Claude Code 2.1.301 builds it from its own pid as `$XDG_RUNTIME_DIR/cc-socks/<pid>.sock`, and every socket observed so far has that form, so the pid is taken from the file name unless `--pid` is given.
  - The start time is `procStart` read from `/proc/<pid>/stat`, in the same unit as the sessions file's, so `dio who` runs the same process check on a roster entry.
  - `dio register` refuses when the variable is unset or not an absolute path, when the socket's file name gives no pid and `--pid` is not given, when there is no such process, or when the path is not a socket.

## Decisions this step made

The plan is silent on these points. Each is listed for `diogenes_0`'s review.

1. **One file, `src/dio`.** No package, no `sys.path` change under `-I`, no bytecode in the tree. Later commands (`dio watch`, `dio meters`) can be added to it or split out.
2. **"Strict" means types and presence, not a closed key set.** The Team seat manager's sessions file holds 18 keys, and `MIN.md` lists 9. Rejecting unknown keys would turn every real file into a mismatch. The checks also come from 2.1.301's own code: its reader accepts exactly the four `status` values above, and its writer sets `startedAt` and `updatedAt` from `Date.now()`. Any other `status` value is a mismatch, so a format change shows instead of being guessed at.
3. **The version record.** Each row records its file's `version` when the file is read, which is once per pass. A mismatched file shows its own `version` if that could be read. Otherwise it shows the `version` of the first file in the same directory, in pid order, that parsed in the same pass and carries one, or else `version unknown`. Nothing is persisted, because `dio who` writes only its grace cache (`MIN.md`, the DR-107 row).
4. **`pid` must equal the file's name.** `0123.json`, or a file whose `pid` is another number, is a mismatch.
5. **A refused or unreadable entry is a row**, as `unknown (refused: …)` or `unknown (unreadable: …)`, not a silent skip. An entry whose name does not match is still discarded silently.
6. **The socket must be a socket**, not merely a path that exists.
7. **The grace cache is one file per entry**, published with `link()` and timed by `goneAt`. If the cache cannot be written, a failed check stays `unknown (checking)`, with a warning, because nothing can time the grace.
8. **A bare prefix is the name without its trailing `_N`**, so `--address probe-t` matches `probe-t_3` but not `probe-tx_1`, and `--address probe-t_1` never falls through to `probe-t_10`. `--prefix` matches any name that starts with `P`, as `MIN.md` words it.
9. **`--highest` applies to a bare prefix only**, as `MIN.md` words it. A role with several live holders, or an exact name live twice, is reported as ambiguous.
10. **The role file defaults to `meta/ROLES.md` in the clone `dio` runs from**, its working tree. A clone that has not pulled `main` reads an older role line. A missing role file gives a note and leaves names and prefixes working; an unreadable or malformed one is exit 2.
11. **`dio register` keys the entry by the config dir from `$CLAUDE_CONFIG_DIR`** (else `~/.claude`), or `--config-dir`. `PROJECT_RULES.md` §7 warns that the environment can be scrubbed, so a scrubbed variable keys a Team seat's entry under `~/.claude`.
12. **`--prefix` with no live match exits 1,** as `grep` does.
13. **A name that ends in a very long `_N` is shown like any other name, from a sessions file or a roster entry.** `dio` sorts by `N` as text, fewer digits after any leading zeros first and then digit by digit, which is numeric order at any length. It does not use `int()`, which refuses more than 4300 digits by default. So a name ending in `_` and 5,000 digits gives its ordinary row, sorted by that `N`, and `--prefix`, `--address` and `--highest` treat it as they treat any name. From a roster entry, the row ends `fallback: register`, as every roster row does. The reason: the name is text with no control characters and no lone surrogates, which is all the strict parse asks of `name` and all `dio register` asks of the name it registers, and `dio register` writes such an entry and reports it registered. Leaving the entry out would hide a seat that `dio register` has just confirmed.

## Not in this step

The `claude agents --json` fallback (built last, by `MIN.md`'s size table), `dio watch`, `dio meters`, `docs/USING.md`, the task template, and any install. The `SessionStart` hook design is not built.
