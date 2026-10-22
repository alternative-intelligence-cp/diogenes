# 0.0-min: the finishing plan — ACCEPTED (2026-10-21)

> **Status, 2026-10-21.** Proposed by the Team seat's D6 on `team/diogenes-0.0-finish-plan` from `a2e48db`, for a plan verifier and the merger. Scope: the merger's message that arrived at 09:20:10 EDT (`/home/randy/Team/META/diogenes/briefs/scope-D6-2026-10-21-from-diogenes_1.txt`), and `management_1`'s ledger choice, arrived 09:22:39 (step 7). [`MIN.md`](MIN.md) governs, unedited; a bare `:<n>` is its line at `a2e48db`. **Accepted 2026-10-21** by the merger's review, after D6v's PASS, and merged at `fbbbb7e`; the merger's rulings are in the last section. **Step 7 is merged** at `eac55d8` on 2026-10-22 ("Step 7's merge", at the end). The `docs/`, `src/` and `tests/` lines this file cites are `a2e48db`'s, where those trees are as at `29acd64`; step 7 moved some, so a brief that uses one re-resolves it by its text.
>
> - **Numbering.** F1–F10 are this plan's decisions; U7 and U8 change `USING.md`, T6 the template; the build's own choices continue `src/README.md`'s at 23. No new experiment: a RESULT for DX-13 or DX-18 goes at the end of `meta/EXPERIMENTS.md`, with a pointer on the experiment's line.
> - **Out:** all that :296 leaves to 0.1; DQ-26's scrub; the merger's four items (:156), commit A of step 7's branch.

## Step 7. `dio meters`

**Fixed by** :41, "a read-only printer of both accounts' usage files, context files and the credits ledger"; DR-109 (:69); DR-56 and 57 (:75), context "per session id, with the name where `dio who` has it"; DR-59 (:76); P0 criterion 6 (:83); M5 (:202); 1.5 h (:283).

**Who.** One fresh Team worker on `team/diogenes-0.0-dio-meters` from `main`, standard library only (DQ-2), reading this section, `src/README.md` and `tests/README.md`; its REPORT gives each commit's sha, the suite under two `TMPDIR` lengths, and its decisions from 23. **Commits:** A, the merger's four items; B, `dio meters` in `src/dio` with `tests/test_meters.py` and both READMEs; C, T6 and its test.

**The command.** `dio meters [--max-usage PATH] [--team-usage PATH] [--context-root LABEL=PATH]… [--ledger LABEL=PATH]… [--sessions-root LABEL=PATH]…`: M5's two flags, and the rest for `src/README.md`:26's rule that tests override every default. A repeatable flag replaces its defaults. The defaults sit under `~`, so a test's `HOME` catches a forgotten flag and `src/` holds no Team path (`tests/test_dio.py`:1042–1048): `~/.claude/usage-latest.json`; `~/Team/CONFIG/usage-latest.json` (`/home/randy/Team/CONFIG/statusline.sh`:13–30); `max=~/.claude/context`, `team=~/Team/CONFIG/context` (`statusline.sh`:32–41); `management=~/Workspace/MANAGEMENT/credits/LEDGER.md`, `libs=~/Workspace/REPOS/nitpick-libs/.internal/credits/LEDGER.md`; `dio who`'s sessions roots.

**Output.** One record per line, tab-separated (two spaces here), the first field naming it; every field from a file takes decision 20's escapes (`src/README.md`:108), so a tab or newline prints as `\x09` or `\x0a`.

- `usage  <account>  <state>  <age s>  <five_hour %>  <its reset>  <seven_day %>  <its reset>`, `max` first, resets in ISO 8601 UTC with `Z`. A `null` window, as the Team writer leaves an expired one (`statusline.sh`:15–21), prints `-`.
- `model_limits  <account>  <JSON>`: compact, one line, file order, where present; the Team writer leaves it out (`statusline.sh`:10–11).
- `context  <account>  <session id>  <name>  <used %>  <age s>  <state>`, per `<id>.json` matching the writer's `^[A-Za-z0-9_-]+$` (`statusline.sh`:34), so `.ctx.*` files are skipped. `<name>` is the `name` of the sessions file, read and parsed by `dio who`'s reader, whose `sessionId` is `<id>`, else `-`.
- `credits  <source>  <pool>  uncorrected  <row>`: each row as it is; `<pool>` is `team-org` when the job cell ends with ` (team)`, else `individual-org`.

**States.** `measured` while the age, the clock less `written_at` in seconds, is at most 600; past it `stale (<N> min)`, N whole minutes rounded down (F4); else `unknown (<reason>)`, the reason `absent`, `refused: …`, `unreadable: <errno>`, `usage format` or `context format`, with `-` figures. A ledger without the header below, or a row of other than 8 cells, prints `credits  <source>  -  unknown (ledger format)  <line>`.

**The parse.** Files open by `dio who`'s `read_regular` (relative, `O_NOFOLLOW`, regular, 64 KiB, or 1 MiB for a ledger), and JSON by its `strict_json`. A usage file needs an integer `written_at`, and a `rate_limits` whose `five_hour` and `seven_day` are `null` or hold a number `used_percentage` and an integer `resets_at`; other keys are ignored (decision 2). Both accounts' files held these names and types on 2026-10-21. A ledger's line 1 is `| started | ended | job | model | turns | cost | status | rc |`, line 2 a separator, and each later line starting `|` a row.

**Writes: none:** nothing opened for writing, no rename, link, unlink or directory, so no process check and no grace cache. `parse_session` also returns `sessionId` (`src/dio`:277–279 drops it); `dio who`'s output is unchanged. **Exit:** 0 when both `usage` lines read `measured`, 1 when either does not, 2 for a usage error; other lines never change it.

**The ledgers are `management_1`'s choice** (its message that arrived at 09:22:39 on 2026-10-21): both, each labelled by source, split by pool. A row with ` (team)` after the job name bills the Team org's API credits ($120, with a $120 limit); every other row, in both, the individual org's grant ($200 a month, $103.48 left on 10-21). Both runners write the 8 columns, and the cost is the CLI's `total_cost_usd`. Checked on 2026-10-21: both paths exist, both line 1s are that header, every row has 8 cells; management's has 30 rows, one with ` (team)` in its job cell, and the libraries' 61, none (`meta/PROJECT_INDEX.md`:38 names it). No total: a balance is 0.1's (:76).

**T6.** `docs/TASK-TEMPLATE.md`:41's `room-at-post` row gains: for a task on an account's plan, the poster copies that account's `usage` line, `measured` if its state is, else `unknown`, as in the cut form (:294); for a credits job, `unknown`, naming the pool.

**Tests, `tests/test_meters.py`:** `TMPDIR` only, `HOME` inside it, every flag into the scratch tree; none writes outside it, sleeps, or reads a real file it covers. Usage: fresh; aged by M5's line to `stale (12 min)`; absent; symlink; FIFO; over 64 KiB; duplicate key; `NaN`; non-integer `written_at`; `null` window; exits 0, 1, 2. `model_limits` on one line, none for a Team-shaped file. Context: a name by `sessionId`, `-`, skipped names, bad JSON. Credits: both pools, escapes, another header, a 7-cell row, no ledger. No flag: only paths under `HOME`. **`MetersStraceTests`, the one new test that runs strace:** the standard world (`fixtures.py`) under `strace -f -e trace=%file`, with no `.key` path opened, nothing opened for writing, no rename, link, unlink or directory. The four that run strace today stay as they are (`tests/README.md`:15): `test_m7a_strace.py`, and `test_dio.py`'s `ReaderTests`, `test_watch.py`'s `StraceTests` and `test_using.py`'s `PrintfTests`.

**Acceptance**, from the root:

```sh
TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -v
TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -p 'test_meters.py' -v
src/dio meters > /dev/null; echo $?    # 0 or 1, and no traceback
```

**The verifier checks** the code against this section and `management_1`'s rule; the suite at each commit and under two `TMPDIR` lengths; an strace audit of the suite's writes (nothing outside `TMPDIR`: none under `~/.local/share/diogenes/`, none in `/home/randy/Team` from a `TMPDIR` outside it); M7a; `dio who`'s output as at `a2e48db`; the README against the code. **Hours:** 1.5. **Risk:** names rest on the context file's `session_id` equalling the sessions file's `sessionId`, which nothing on file measures; M5 checks it.

**If cut** (:294; it is not, below): `USING.md` gives the two paths and one `/usr/bin/python3 -I -B -c` line printing per file its path, `five_hour <p>%`, `seven_day <p>%` (`-` if `null`), `age <s> s` and F4's state; `room-at-post` copies it, and M5 runs it from each account and on the aged copies (F3).

## Step 8. The `claude agents --json` fallback

Fixed by :101; :112, "built last"; M7b (:205); 0.5 h (:284). DX-18 has no RESULT (`meta/EXPERIMENTS.md`:252–256), so the step starts with it.

**8a. DX-18's listing, `[author]`, 5 minutes.** In a plain terminal, while named seats are open on both accounts, the author runs the run sheet's two lines (`/home/randy/Team/META/diogenes/probes/DX3-run-sheet.md`:264–265); "It may start Claude Code's background-session supervisor" (`DX3-run-sheet.md`:270). In that minute the Team seat runs `dio who`, then files per config dir the count of rows by `kind`, and whether each live `dio who` row is listed by pid with `kind` `interactive`; the raw files stay local (`DX3-run-sheet.md`:350). The RESULT goes at `EXPERIMENTS.md`'s end, pointed to from `EXPERIMENTS.md`:252.

**8b. Built only if** each config dir's listing holds every live interactive session `dio who` lists there, by pid (F5). One fresh Team worker on `team/diogenes-0.0-agents-fallback`, one commit:

- `dio who --agents` runs `claude agents --json --all` per sessions root's config dir, timeout 10 s: for `max` with `CLAUDE_CONFIG_DIR` removed from the child's environment (`EXPERIMENTS.md`:199), for `team` set to it. `--agents-command PATH` replaces `claude` in tests.
- The listing is a JSON array whose rows have an integer `pid`, a string `kind`, a `status` of `busy`, `waiting` or `idle`, and a string or null `name` (`meta/research/done/dio-r1b-claude-code-deep-2026-10-10.md`:272); else that dir gives one `unknown (agents format)` row.
- A row shows only when no parsed sessions file or roster entry has its config dir and pid (`src/README.md`:44), ending `fallback: claude agents`: `live-idle` for `idle`, else `live`, while `/proc/<pid>/stat` exists, else `gone`. Its socket is `-` (the listing has none), so `--address` never resolves to it.
- Tests: a fake `claude` in `TMPDIR` that prints fixtures and records its environment; covered and uncovered rows, each `kind`, bad output, a non-zero exit, the timeout. No real `claude`, no strace.
- Acceptance: the suite. Verifier: as for step 7, and no process without `--agents`. **Hours:** 0.5.

**8c. Else not built:** the cut order's second item, 0.5 h saved; M7b compares no listing, and the merger notes it on `src/README.md`:166's line.

## Step 6: what is left

A1 and A2 are applied (:6–7), and D2c's ruling (:177–191) dropped the rest for bypass seats. Three things were left; this plan settles each, so step 6 needs no build worker.

1. **The gate's probe settings** (:161's printed fragments), each a B1 staged file plus one entry. The bases are `staged/settings.L0-without.json` (sha256 `5556bda4…c106`) and `staged/settings.M4-nosend.json` (`45974e66…e844`, L0 plus `"deny": ["SendMessage"]`), byte-identical in `/home/randy/Team/PROBES/dio-probe/` and `/home/randy/Workspace/MANAGEMENT/probes/dio-probe/` on 2026-10-21: `dontAsk`, the sandbox on, bypass disabled (F6).
   - **G-M2** (Max: M2, caveat (ii) without its rule, M3's fourth post): L0 with `"SendMessage"` in `permissions.allow`.
   - **G-M4T** (Team: M4's dropper): M4-nosend with `"allowWrite": ["/home/randy/.local/share/diogenes/inbox/max"]` in `sandbox.filesystem`.
   - **G-M4M** (Max: M4's watcher and idle probe): M4-nosend with `"Edit(//home/randy/.local/share/diogenes/inbox/**)"` in `permissions.allow`, never `Write(…)` (caveat (ii)). With no `allowWrite`, its sandbox gives Bash no write to the zone: caveat (iii)'s strict-sandbox seat.

   M1's and DX-13's probes use L0. The Team seat writes G-M4T, and sends G-M2 and G-M4M to `management_1` to write (:201). The author copies the variant over `.claude/settings.local.json` before each start, as for B1 (:209–211).
2. **No status-line override.** M5's live half reads the real files, rewritten as the status line re-runs every 60 s (:202); its stale half, copies by the two flags. At 09:44:52, `refreshInterval` was at `~/.claude/settings.json`:53 and `~/.claude-team/settings.json`:50 (M5 says line 46), and :192's line numbers held for the Team file only; the Max file had `crossSessionInbound` at line 68 and `defaultMode` at line 10.
3. **The `SessionStart` hook design** (:101): F1.

Nothing else is left; step 6's 0.75 h is spent within this pass.

## The gate's run plan

**Before M1.** Steps 7 and 8 are merged, or 8 cut. The Team seat runs `timeout 60 git pull --ff-only` on `main`, checks `HEAD` against the merger's sha, and keeps its clone on `main` to the gate's end, working in a worktree under `/home/randy/Team/WT/` (F2), since `dio` reads the role line from its own clone (decision 10, :110). Max seats and the author run `/home/randy/Workspace/REPOS/diogenes/src/dio`, Team seats and probes `/home/randy/Team/REPOS/diogenes/src/dio`. A probe acts only on the Team seat's messages, one simple command per Bash call (B1's S1 line 1 ran sandboxed under `dontAsk`; compound line 2 was refused, `EXPERIMENTS.md`:109), and starts each turn by logging the clock time in `results/` (rule 3). Records: F8.

| Row | Who runs it | `[author]` | Probes |
|---|---|---|---|
| M1 | The merger, told no name, runs `--prefix probe-t` and `--address probe-t` after each start and sends one message. Before `_4` it commits `probe-seat = probe-t_3` (`meta/ROLES.md`:20) and pushes, the Team clone pulls, and it runs `--address probe-t` and `--address probe-seat`. The Team seat's manager compares its `ListAgents` with `dio who` | B4: four starts, three closes, 30 min | `probe-t_1`–`_4`, L0 |
| M2 | The Team seat's manager sends five messages to `dio who --address probe-m`, each after its log line, 10 minutes after probe-m's last turn, and records the mode pair, bypass to `dontAsk` (:208), and `crossSessionInbound`, `accept` on both. Then probe-m's Write-tool file in `inbox/team/`, caveat (ii) without its rule, should be refused | B5: start probe-m, attend five idle ends, 60 min | `probe-m`, G-M2 |
| M3 | The merger commits four task files from the template; the Team seat works the first and refuses the fourth (T5); the merger fills `verified-by` and `merged-at` (T2) | none | — |
| M4 | The Team seat's manager pre-seeds `inbox/max/` with ten messages (`USING.md`'s line). probe-td and probe-mw each try one `SendMessage`, which must be refused. probe-mw arms `dio watch ~/.local/share/diogenes/inbox/max --every 60`; probe-td drops five files, each after probe-mw's last turn; probe-mi, unwatched, is observed 10 minutes spanning a drop; then probe-td watches `inbox/team/` and drops once, and probe-mw replies by the Write tool | B6: three starts, 30 min | `probe-td`, G-M4T; `probe-mw`, `probe-mi`, G-M4M |
| M5 | The Team seat and the merger run `dio meters` in their own sessions; the Team seat runs the aged copies (F3, F4) and checks its own context row's name | none | — |
| M6 | After M4, the author kills probe-mi once `ps -o comm=,args= -p <pid>` confirms it; probe-td should read `live-idle` | B7: `watch -n 15 /home/randy/Workspace/REPOS/diogenes/src/dio who`, 5 min | — |
| M7a | The Team seat; the merger at the merge | none | — |
| M7b | The Team seat's manager and the merger, a half each, at one Claude Code version; the listing only after 8b | none | — |
| M8 | The author; `management_1` relays the line to the merger | B8: a working day | — |
| DX-13 | The Team seat directs probe-tx (F7): an exit-2 leg, watching an empty directory under `results/` that the Team seat removes after 10 minutes; then `--max 7200`, re-armed with `--max 43200` on its wake, or on the Team seat's message if none comes | start and close probe-tx, 5 min | `probe-tx`, L0 |

**The scope's six items.**

1. Decision 10: the pull and clones above.
2. `probe-seat`: the merger commits it before `_4` and removes it in the gate's records commit.
3. M3's task files, from `docs/TASK-TEMPLATE.md`, committed by the merger; probe-m sends the fourth after M2 (`meta/tasks/README.md`:11's exception). Their spec is this list at this plan's merge commit (F10); `room-at-post` by T6; `cross-account` is `no` for (3) only, `credits` being an account (`meta/PROJECT_RULES.md` §7).
   - (1) `management_1` to the Team seat: run M7a at the gate's sha and file its output. Acceptance: `TMPDIR=<scratch dir> /usr/bin/python3 -I -B tests/test_m7a_strace.py` prints `M7a: PASS`, exit 0.
   - (2) `management_1` to a credits job, the cut order's third item: write `git show a2e48db:meta/ROLES.md | sed -n '9,13p'` to the runner's output file. Acceptance: `cmp` of the two.
   - (3) `diogenes_1` to a Max subagent: the same with `git show a2e48db:docs/TASK-TEMPLATE.md | sed -n '18,28p'`.
   - (4) probe-m to the Team seat: `refused: poster`.
4. DX-13's legs, which decide `--max` and whether exits 1 and 2 wake an idle session ("For the gate", :137). Each wake's `cache_read` and `cache_creation` come from the probe's transcript (`EXPERIMENTS.md`:144; `EXPERIMENTS.md`:155).
5. `EXPERIMENTS.md`:123's open items: F9.
6. The Write-tool route from a strict-sandbox seat (caveat (iii); :155, :157): probe-mw's reply. The record gives probe-td's `WAKE` line, final name or `<name>.tmp.<pid>.<12 hex digits>`, and what `USING.md`:124's line lists.

**M5's aging line**, run on each copy in `/home/randy/Team/TMP/dio-m5/`, then `src/dio meters --team-usage <copy> --max-usage <copy>` within the minute:

```sh
/usr/bin/python3 -I -B -c 'import json,sys,time;p=sys.argv[1];d=json.load(open(p));t=int(time.time())-720;d["written_at"]=t;d["written_at_iso"]=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(t));json.dump(d,open(p,"w"))' <copy>
```

**The author's steps** against :290. Done: A1, A2, the line-37 edit, B1's starts. Left: DX-18 (5 minutes), M1 (30), M2 (60 of wall-clock, attended at each idle end), M4 (30, one start more than :290), M6 (5), DX-13's probe (5, then 2 hours and a night unattended; :290 has the 2-hour leg only), M8's day: about 75 minutes hands-on, besides M2's waits.

**The merger's parts:** this plan's merge and status-block pointer; steps 7 and 8; M1's Max side and `probe-seat`; M3's commits, `verified-by`, `merged-at`; M5's and M7b's Max halves; M7a at merges; the `--max`, U7 and U8 rulings; the Max probe files; the record's merge and the cycle's status line. **`management_1`'s:** posts (1) and (2), the Max variants, M8's relay.

**After the gate**, on `team/diogenes-0.0-gate`, in the 1.0 h row (:286): **U7**, `USING.md`:113, leaving exits 1 and 2 to the gate, gives the legs' answer, citing the RESULT; **U8**, caveats (ii) and (iii) take the label *Measured* where M2 and M4 measured them, departing from `MIN.md`'s note as U1 departs from rule 4, with `test_using.py`'s label check; **`--max`** as the merger rules, in `src/dio`:827, its help (`src/dio`:1048–1053), `src/README.md`:122–124 and `HelpTests`; and each writer's account removes its own probe files from the other's inbox (F6).

## Hours and the cut trigger

| Rows (:277–287) | Planned | Now |
|---|---|---|
| DX-3's row to `USING.md`'s | 10.5 | 4.46 through step 5 (:32); DX-3's rest in the gate, DX-18 in 8a |
| Install fragments | 0.75 | in this pass, D6: 0.69 h (09:22:16 to 10:03:29, `date`), which plans all of this |
| `dio meters` | 1.5 | step 7, 1.5 |
| The fallback | 0.5 | step 8, 0.5 by 8b, 0 by 8c |
| Gate M1 to M8 | 3.25 | M1 0.4, M2 0.4, M3 0.75 (credits task 0.5), M4 and DX-3's legs 0.75, M5 0.25, M6 0.1, M7a 0.1, M7b 0.25, DX-13 0.25 |
| Commits, pushes, DX results, close | 1.0 | filing, RESULTs, U7, U8, `--max` |
| Verification | 2.5 | D6's verifier, steps 7 and 8's, the record's |

**The trigger does not fire.** The next checkpoint is the end of install, 13.0 h against 11.25 (:294), and install ends at this plan's merge. The total there is 4.46 h, plus this pass's 0.69 and its verifier's hours, so it reaches 13.0 only if the verifier takes 7.85 h. Nothing in the cut order is cut, and the never-cut list (:294) is untouched.

## What a watchdog would take

`management_1`'s context, not a decision; nothing here is built.

1. **Sources.** Caps: `dio meters`' `usage` and `model_limits` lines; a pool's spend needs a sum of `credits` rows, 0.1's. Waiting on the author: the sessions file's `status` `waiting`, which `dio who` folds into `live` (`src/dio`:65; `USING.md`:135); show it apart as `live-waiting` only with the watchdog (0.25 h): the gate runs on today's states. A dead process: the process check, `unknown (checking)` then `gone`. An unread harness: nothing, as no message is acknowledged (:70); the nearest is an inbox file newer than the seat's last logged reading (`USING.md`:115–131).
2. **State, to speak only of a new problem:** a file per check in the zone's `cache/`, which rule 9 lets both accounts write, with the last verdict and its time; `dio who` prunes only `grace-*` names (`src/dio`:497–514).
3. **How it runs.** A seat's own background loop, as `dio watch` is, whose exit wakes that seat, which messages management; or a timer the author installs. A plain process cannot `SendMessage`, so a timer writes an inbox file per alert, only into the other account's inbox (rule 9): a Team-side timer into `inbox/max/`, where management's `dio watch` wakes it. Reaching the author directly is the author's choice, outside Diogenes.
4. **The cheap model**, only where a verdict needs judgment: through management's runner, billed to the Team org's credits, its row carrying ` (team)`. The runner wrapper is 0.1 (:296).
5. **Hours:** the check with its state and tests, about 2; the timer, `[author]`, about 10 minutes; the model step after the wrapper.

A timed check can compare runs: step 7 fixes `dio meters`' lines and exits, and `dio who`'s (`src/README.md`:48–79) stay.

## The plan's decisions

Each is recommended.

- **F1. The `SessionStart` hook design stays on file where it is:** not in `docs/` (:101), which holds none of it, but in `meta/DESIGN.md`:372 and `meta/roadmap/0.0/0.0.2.2.md`, kept "as the source for what 0.0-min leaves to 0.1" (`meta/roadmap/0.0/README.md`:3). *Declined:* a copy in `docs/`, used by no seat and scrubbed by DQ-26; a new design. *Reversal:* `DESIGN.md`:372's line added to `docs/README.md` as not installed, 0.1 h.
- **F2. No `PATH` install, and the Team clone stays on `main` through the gate.** `dio` is `src/dio` in a clone (`USING.md`:12). *Declined:* an `[author]` `PATH` link (`src/README.md`:22), silently tying every seat's role line to one clone. *Reversal:* the author's `ln -s` to the Workspace clone, 2 minutes.
- **F3. M5's aged copies go in the checking seat's scratch.** :202 has `/tmp/dio-m5/`, "outside both domains", but the Team seat's brief keeps its writes in `/home/randy/Team` and the zone (§2 line 37, :223), and the place does not change what the flags read. *Declined:* `/tmp`; the zone's `cache/`. *Reversal:* :202's path, if the author allows `/tmp`.
- **F4. `stale` past 600 s, in whole minutes down; the copy is set 12 minutes old.** :294's "older than 10 minutes" is the stale side, and :202's "moves its `written_at` and `written_at_iso` back 12 minutes" is read as setting them to 12 minutes before the edit, so a copy read within the minute prints `stale (12 min)`. *Declined:* subtracting 720 from the file's value, which adds its age at the copy (predicted under 2 minutes, :202) and can print `stale (13 min)`; rounding. *Reversal:* the literal reading, copying a file under a minute old.
- **F5. The fallback is built on DX-18's evidence only, and opt-in,** since a listing "may start Claude Code's background-session supervisor" (`DX3-run-sheet.md`:270), and M6's `watch -n 15` would start two `claude` processes every 15 s. *Declined:* always on; on after a format mismatch, which the gate cannot exercise. *Reversal:* the default, 0.1 h.
- **F6. The gate's probes run `dontAsk`, sandboxed, as B1's did,** so M2 and M4 measure caveat (ii) both ways and caveat (iii)'s route. *Declined:* bypass probes, which measure neither; unsandboxed `dontAsk`, needing an allow rule per Bash form. *Reversal:* a variant without `disableBypassPermissionsMode` and the sandbox, started with `--permission-mode bypassPermissions`. Each writer's account removes its probe files from the other's inbox, as on 2026-10-15 (`EXPERIMENTS.md`:120–121).
- **F7. DX-13's legs run on a fresh Team probe.** A seat would sit idle 2 hours and a night, a peer message would void the leg, and a wake past the cache's life writes the context again, about 467 k tokens for the seat measured (`EXPERIMENTS.md`:155). *Declined:* the Team seat's manager, as in B2. *Reversal:* the 2-hour leg on the seat.
- **F8. The gate's record is one folder,** `meta/research/done/gate-0.0-min-<date>/`, on `team/diogenes-0.0-gate`: a README with each row's verdict, runner, times and Claude Code version, and a `<row>.txt` per check, raw records byte for byte. *Declined:* `MIN.md`; one file. *Reversal:* the merger's layout.
- **F9. `EXPERIMENTS.md`:123's open items.** Before M4's trials, probe-td and probe-mw each run `src/dio who` in sandboxed Bash for (c) and (d), beside the Team seat's unsandboxed run, and print S1 line 3's three variables with `:-UNSET`; probe-mw's sandboxed `touch` into `inbox/team/` is the sandbox leg, expected refused. The `dontAsk` legs are M2's and M4's, DX-18 is 8a, the 10-minute leg is done. The classifier finding is watched for; the unnamed session's move to the background is not re-run, all probes being named (`USING.md`:136). *Declined:* a separate DX-3 session, about 20 author minutes (:290). *Reversal:* one more start under the run sheet.
- **F10. M3's tasks are mechanical.** M3 proves the convention (:77), so each reproduces a command's output at `a2e48db`, checked by `cmp`. *Declined:* real work, whose size and checks vary. *Reversal:* any task whose tracked spec holds its acceptance commands.

## At the merge (`diogenes_1`, 2026-10-21)

The merger accepted this plan at 20:06, after D6v's PASS (`/home/randy/Team/REPORTS/D6v-diogenes-0.0-finish-plan-verify.md`), and merged it at `fbbbb7e`. Its rulings, and where each open point goes:

- **D6's question 2:** keep both `SendMessage` checks, M4's deny control and probe-m's M3 post for the allow, so G-M2's allow stays (D6v's finding 11).
- **D6's question 3, measured on the Max side at 20:05 under Claude Code 2.1.307:** this seat's context file's `session_id` equals its sessions file's `sessionId`, and its `session_name` equals the sessions file's `name`. M5 still checks both accounts. Step 7 joins by id. A context file that no parsed sessions file matches, such as an ended session's, which the writer keeps a week, prints its own `session_name` as `statusline:<name>`, else `-`.
- **D6's question 4:** same-line notes at `MIN.md`:192 and :202 give the settings files' lines as read on 2026-10-21: in the Max file `defaultMode` 10, `refreshInterval` 53 and `crossSessionInbound` 68; in the Team file 3, 50 and 65.
- **D6's question 5 and D6v's finding 3:** before M3 runs, the gate's brief gives task (2) a form the runner's Read, Grep and Glob can do, the file at `a2e48db` exported into a directory the job may read, and the prompt asks for the lines alone.
- **D6v's finding 7:** the merger verifies task (2) by re-running its `cmp`. Task (3), which the merger posts and reports, is verified by another seat, `management_1` by default (T1, T2).
- **Step 7's worker settles D6v's finding 5** in decisions from 23: a `null` figure or name prints `-`; lines go by account, then session id; `credits` prints every row, as :41 says; and the `statusline:` name above.
- **For 8b's brief, if DX-18 builds it** (D6v's finding 4): read pid and status from live rows only; name its test file, its README lines and its hand-off; and cite what shows that `claude` with `CLAUDE_CONFIG_DIR` unset reads `~/.claude`, since `EXPERIMENTS.md`:199 is DX-4's socket line.
- **For the gate's brief:** F9 prints S1 line 3's variables as the run sheet names them (D6v's finding 1); M4's starts are measured against the author's steps' B6, not :290 (finding 2); and the brief states the order of the probe variants between runs, with L0 restored after (finding 12).
- **Accepted as written:** M7b compares a listing only once 8b is built, a narrowing of :205 that F5 implies (finding 6). F10's `cmp` (finding 8) and the hours' cells (finding 9; D6's pass was 0.72 h at its push) stand, with these notes. D6's report's counts (finding 10) are the Team's record.

### Step 7's merge (`diogenes_1`, 2026-10-22)

The merger merged build step 7 at `eac55d8`, after D7v's PASS on `2d5fb71` (`/home/randy/Team/REPORTS/D7v-diogenes-dio-meters-verify.md`) and its own check, which the merge commit's message gives. `src/README.md`'s decisions 23–35 and the template's T6 are accepted. D7v's ten findings, none blocking:

- **To the next diogenes code branch:** a test that pins decision 24's order by session id where the file names sort another way, as the ids `a`, `a-1` and `a_1` do, and for two directories under one label (finding 1); decision 33's "the spaces" written as what `.strip()` removes, any whitespace (finding 3); and a test for the `room-at-post` row's own additions, "from `dio meters`" and "(decision T6)" (finding 9).
- **Stand as built:** a usage window that holds a `null` `used_percentage` reads `unknown (usage format)` (finding 4, D7's first flag), since the ruling's "a `null` figure or name prints `-`" settled D6v's finding 5, on the `context` lines, and step 7's usage parse is explicit; `model_limits` doubles the backslash of JSON's own escapes, by decision 20 (finding 5); a `written_at` later than the clock reads `measured`, by step 7's rule as worded, and a bound on it is 0.1's (finding 8); `src/README.md`'s lead names `diogenes_0` for decisions 1–22, as history (finding 7); and the trailing whitespace in `docs/README.md` and `meta/README.md` is the author's skeleton (`d1ee423`), left as he wrote it (finding 6).
- **Covered at the merge:** the commits' short `TMPDIR` had 27 characters, not 25, as the merge commit's message says (finding 2); the merger's `ls-remote` read `main` at `29acd64` and the branch at `2d5fb71` (finding 10).
- **Hours:** D7 0.57 against step 7's 1.5, and D7v about 0.81 of the verification row's 2.5 ("Hours and the cut trigger", above). Step 7 comes after that section's last checkpoint, the end of install, so the cut trigger is unaffected.
