<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-v1-verify-0.0-plan-2026-10-10.md: the independent plan verifier of cycle 0.0 (claude-opus-5-5, 33 turns, $2.48 by the CLI). Its prompt is prompts/dio-v1-verify-0.0-plan-2026-10-10.md. -->

I've finished reading the plan. Writing up the report now.

# Verification of the cycle 0.0 plan (`meta/roadmap/0.0/`), 2026-10-10

Verifier: Opus 5.5, read-only (Read, Grep, Glob). I ran no commands, so every "as written" judgement is from reading.

## Verdict: **PASS WITH FIXES**

The plan's structure is sound:
- It is ordered experiments first, then store, primitives, delegation, install and gate.
- It covers the ★ set.
- It is honest about what was not rehearsed.
- It obeys M1 and M3: the store is a file, and nothing connects to a socket from inside the sandbox.

The six **blocking** findings (V-1 to V-6) must be fixed in the text before an executor gets the plan. V-1 is a role-capture hole. V-2 can overwrite the Max meters file. V-3 can spend real credits or report a stale output. V-4 to V-6 are tests whose stated expected values contradict the stated code, so a correct implementation fails its own gate. The **major** findings should be fixed in the same pass. None of them needs a re-cut.

---

## Findings

### V-1 · blocking · `0.0.1.0.md` §3 step 5 (`role assign`); G5 in `README.md` §2 and `0.0.4.0.md` step 8

**Problem.** Any identity that is not a worker can assign any role, including to itself. That lets a seat capture a role with one command. G5 tests only the registration path, so it passes while this hole stays open. DR-106 says a role moves only "at handoff or by the author".

**Evidence.**
- "`role assign`: … refuses when the caller is a worker (kind `worker` or `job`)". No other caller check exists.
- "any other name registers as a seat" (`0.0.2.2.md` §1.4). So `probe-capture` is a seat and may run `dio role assign libs-seat --to probe-capture`.

**Fix.** Replace the refusal clause with:
> refuses unless the caller is `author`, or the caller is the role's current holder (a handoff); a role with no holder may be assigned only by `author` (`refused: only the holder or the author assigns <role>`).

Add the test `test_role_assign_by_non_holder_refused`, so `0.0.1.0` has 17 tests and every later running total grows by one. Add a G5 live step: `probe-capture` attempts `dio role assign libs-seat --to probe-capture` and expects the refusal.

### V-2 · blocking (safety) · `0.0.0.1.md` §1 step 4, together with `0.0.0.0.md` §5 step 1

**Problem.**
- The Team probe reuses `dx3-status.sh`.
- In 0.0.0.0, that script pipes into "THE AUTHOR'S EXISTING statusLine COMMAND", which writes `~/.claude/usage-latest.json`.
- Under the Team config dir, that write overwrites the Max meters that Max seats read before dispatching. This is the hazard DX-5 exists to detect.
- The step also claims the opposite of the script it copies.

**Evidence.**
- "copy `0.0.0.0.md` §5's `dx3.sh`, `dx3-status.sh` and the DX-2 `dx2.sh`…"
- "The probe status line only tees; it runs no writer of that path."
- 0.0.0.0's script: `tee -a <P>/log/dx3-status.jsonl | <THE AUTHOR'S EXISTING statusLine COMMAND>`.

The same step also says to copy the scripts "into the Team probe project's `.claude/settings.json`", which is garbled: scripts are not copied into a settings file.

**Fix.** Replace the sentence with:
> For the Team probe use a tee-only status line, `dx5-status.sh`: `#!/bin/sh` / `umask 077; tee -a <TEAM_P>/log/dx5-status.jsonl >/dev/null; echo probe-t`. Never pipe into the author's command under `~/.claude-team`. Copy the three scripts into `<TEAM_P>/` and reference them from `<TEAM_P>/.claude/settings.json`.

### V-3 · blocking · `0.0.2.0.md` §2 (`dio_credits_run.sh`) and §3 `test_credits_wrapper_dry`; `0.0.4.0.md` step 5

**Problem.** There are two defects.
1. **The test cannot use a stub.** `RUN`, `OUT` and `LEDGER` are hard-coded to the real runner, so "with `RUN` pointed at a stub" is impossible without editing the script. A literal implementation runs the real `run.sh`, which spends credits and appends to the real `LEDGER.md`.
2. **A failed run can be reported as a success.** `run.sh` exits 2 *before spending* when `out/$JOB.json` already exists or the job file is missing. The wrapper then still reports `out/$JOB.md`, which may be an **older run's output**. The gate's acceptance, `grep -q OK <out path>`, then passes on the stale file.

**Evidence.**
- `RUN=/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/run.sh`
- `OUT=…/out/$JOB.md`
- `$DIO --session "$SID" task report "$TASK" --ref "$OUT" --note "rc=$RC; …"` runs unconditionally.
- `run.sh` line 20: `[ ! -e "$D/out/$JOB.json" ] || { echo "out/$JOB.json exists…"; exit 2; }`

**Fix.**
- Use `CREDITS=${DIO_CREDITS_DIR:-/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits}`, `RUN=${DIO_CREDITS_RUN:-$CREDITS/run.sh}`, `OUT=$CREDITS/out/$JOB.md` and `LEDGER=$(tail -1 "$CREDITS/LEDGER.md")`.
- Before the claim: `[ -e "$CREDITS/out/$JOB.json" ] && { echo "out/$JOB.json exists; pick a new job name" >&2; exit 2; }`.
- After the run: if `RC -ne 0` or `$OUT` is older than the claim, run `task progress "$TASK" --note "run failed rc=$RC; not reported"` and exit `$RC` without reporting.
- The test sets both environment variables to a temporary directory and asserts that the real `LEDGER.md` is unchanged (compare its size before and after).

### V-4 · blocking · `0.0.2.1.md` §1 (`meters` example) and §2 `test_meters_room_max`; `CHECKLIST.md` 0.0.2.1

**Problem.** The expected room is arithmetically wrong. Code that implements DR-56's formula correctly fails the test as specified.

**Evidence.** The plan says "`room 5.0 = 95 − 61 − 0.5 × (100 − 68)`" and "`61/68 → room 5.0`". In fact 95 − 61 − 16 = **18.0**.

**Fix.** Replace `5.0` with `18.0` in all three places.

### V-5 · major (executability) · `0.0.1.0.md` §3 step 7 (`tests/helpers.py`)

**Problem.** The executor runs the suite from a Claude Code session's Bash, where `CLAUDE_CODE_MESSAGING_SOCKET` is set (DX-3 expects this). `run_dio` with `env=None` inherits it. Resolution rule 3 then answers `refused: socket not registered` (exit 1) where these tests expect exit 3:
- `test_resolve_refuses_without_socket`;
- `test_hazard_2_identity_supplied_not_env`;
- every test that relies on "no socket".

**Evidence.** "`run_dio(args, env=None, stdin=None)` runs `python3 -I src/dio.py --home <tmp> …` by subprocess".

**Fix.** Add:
> `run_dio` builds its environment from `os.environ` minus `CLAUDE_CODE_MESSAGING_SOCKET`, `CLAUDE_SESSION_ID` and `DIO_HOME`, then applies `env` overrides, and passes `stdin=subprocess.DEVNULL` unless `stdin` is given (so `isatty()` is false).

### V-6 · major (executability) · `0.0.1.0.md` §3 step 3 against `0.0.1.2.md` §2

**Problem.** The lease-id regex requires at least two characters in the project part, so two tests' fixtures are refused as usage errors before they test anything.

**Evidence.**
- Regex: `^[a-z][a-z0-9-]+/[a-z]+/[a-z0-9._-]+$`
- Fixtures: "a lease on `p/tree/me` is not matched by … `p/tree/m`" and "`a/tree/nitpick-posix` and `b/tree/nitpick-posix`".

**Fix.** Change the fixtures to `pa/tree/me`, `pa/tree/names`, `pa/tree/m`, `pa/tree/nitpick-posix` and `pb/tree/nitpick-posix`. Keep the regex in step with the project-id rule `^[a-z][a-z0-9-]{1,40}$`.

### V-7 · major (gate validity) · `0.0.0.0.md` §2 (DX-1), "Found at planning (1)"; `0.0.1.2.md` §3 (replay)

**Problem.** There are three gaps.
1. **The real setup is never tested.** DX-1 is meant to test the configuration 0.0 will run: a store directory reached through an `allowWrite` entry. The B racer runs in the **executor's** Bash, so `$P/.claude/settings.json` has no effect on it. `$P` sits in the per-user temp directory, which is writable by default (CONSTRAINTS §3), so no `allowWrite` entry is ever exercised.
2. **No positive control.** Nothing shows that B actually ran sandboxed in a different namespace. An unsandboxed retry would pass all four legs vacuously.
3. **No check that the racers overlap.** The free-running leg's `fence == W_A + W_B` holds even if A and B never ran at the same time.

**Evidence.**
- "the probe directory is the probe project's own working directory, which the sandbox writes by default … one is added anyway for explicitness."
- "The executor, in the same moment, as a background Bash call…"

**Fix.**
- Put `probe.db` in `~/.local/share/diogenes-probe/` and add that path to `allowWrite` in **`$P/.claude/settings.json`** (probe-scoped), as `EXPERIMENTS.md` has it.
- Run every sandboxed racer in `probe-a`, whose cwd is `$P`, not in the executor's Bash.
- In `take.py`, print `os.readlink('/proc/self/ns/net')`, `os.readlink('/proc/self/ns/mnt')` and the first and last take times.
- Acceptance: the host and sandbox namespace ids differ (as in M3), and the take intervals overlap by at least 10 s.
- Apply the same to `0.0.1.2.md` block R, whose "the probe project's cwd as in 0.0.0.0 §1" refers to a directory deleted in 0.0.0.0 §8.

### V-8 · major (correctness and safety) · `0.0.1.0.md` §3 step 6 (`process_check`, `who`); `0.0.1.2.md` `takeover`; `0.0.2.2.md` §3 (`wait_pid`)

**Problem.** A check made from inside the sandbox can mark a live session `dead`, and then `gone`. DX-3 has not established that the socket file under `/run/user/1000/cc-socks/` is visible from inside the sandbox.
- A missing socket path yields `dead`, then `gone` after the grace. Only `PermissionError` yields `impossible`.
- Every `who` writes `last_check_result` for every open session, so a sandboxed `who` stores false `dead` results.
- `takeover` is allowed when the holder reads `gone`, so a sandboxed seat could take over a live holder's lease.
- `wait_pid = os.getpid()` taken inside a sandbox with its own PID namespace is meaningless to a host-side `who`. A sandboxed `who` would show the wait as gone, and `wait_trials.sh` would hang waiting for `wait`.

**Evidence.** "`alive` when … `os.path.exists(socket_path)`. `dead` otherwise." "Every `who` … writes `last_check_at, last_check_result, last_check_by` for every open session."

**Fix.**
> Return `impossible` when `os.path.isdir(os.path.dirname(socket_path))` is false, or when `/proc/1/comm` differs from the host's (a PID namespace); write `last_check_*` only for a result that is not `impossible`; record `wait_pidns = os.readlink('/proc/self/ns/pid')` with `wait_pid` and test its liveness only from the same namespace, otherwise trust `wait_since`.

Add a unit test with a socket path whose directory does not exist, expecting `unknown`, not `gone`.

### V-9 · major (correctness and cost) · `0.0.2.2.md` §3 (`dio wait`)

**Problem.** The wait has two defects.
1. **It misses work that is already waiting.** It only looks after `data_version` changes, so a task or message that arrived before the wait started is never seen. That includes a second task already posted when a worker re-arms after finishing the first. The worker sleeps until `--max`.
2. **It can loop.** For a seat, "`reported` tasks I posted" stays true until verify, and an unread `reply-expected` message stays true until acked. Every re-arm exits on the next change, costing one model turn each time.

**Evidence.** "read `PRAGMA data_version`; sleep `--every`; re-read; on change, run the three queries".

**Fix.**
> On start, record `wait_seen_seq` = the session's last notified seq. Run the three queries once immediately, and again on every `data_version` change. A hit is an item whose `seq` (or task-event seq) is greater than `wait_seen_seq`; on a hit, store the new high-water mark before exiting.

Add tests `test_wait_sees_task_posted_before_start` and `test_wait_rearm_does_not_refire_on_same_item`.

### V-10 · major (design gap the plan creates) · `0.0.2.0.md` §1 `claim` step 2 and `verify`

**Problem.** Tasks are orphaned whenever the orchestrator seat rotates.
- Seats rotate often (`_18` → `_19`), and the role moves by assignment.
- After a handoff, every open task posted by the old seat fails the poster check at claim time.
- Every reported task can then be verified only by the old poster or the author.

DR-102 needs the poster to *be* the orchestrator. It does not need the poster to *still be* the orchestrator at claim time.

**Evidence.**
- "`poster_role` must still resolve to `from_identity`; else … `refused: poster`"
- "Only the poster, the poster's labelled subagent, or `author` may verify".

**Fix.**
- Claim check: "`from_identity` held `poster_role` at `task.at` (the newest `role_event` for that role at or before `at` names it) and the role has not since been assigned by `author` to revoke it."
- Verify: allow "the current holder of `poster_role`" alongside the poster.
- Add a test `test_task_survives_orchestrator_handoff`.

If the author prefers the strict reading, ask him; it is an author choice.

### V-11 · major (gate passes vacuously) · `0.0.4.0.md` §2 (`tasks_post.sh`, `tasks_verify.sh`) and §5 block V

**Problem.** G1 has three problems.
1. **Verification cannot fail.** A team task's acceptance command is `test -f meta/tasks/gate-…md`, which is true in any checkout whether the worker did anything or not. The worker "commits nothing" and reports the spec's own commit.
2. **The `rejected` path is never exercised live.**
3. **The expected count is wrong.** Step 3 claims and reports 10 team tasks (10 G6 trials), and `tasks_verify.sh` verifies "every task of mine in `reported`". Block V would therefore print `team-session: 10`, not the expected `5`.

**Fix.**
- The team spec tells the worker to write `.internal/gate/out-<task id>.txt` containing the task id and its blob, and to report that path. Acceptance: `grep -qx "<task id> <blob>" .internal/gate/out-<task id>.txt`.
- Add one deliberately failing task (acceptance `false`) and assert it reaches `rejected`.
- Change block V's expectation to `team-session ≥ 5, credits-job 5, self-verified []`, or keep `wait_trials` tasks out of the G1 count with a distinct spec prefix (`gate-g6-…`).

### V-12 · major (writes and network the plan does not state; measurement item 3) · `0.0.4.0.md` §2 and step 5

**Problem.** Three things need access the plan never states.
- **Unique spec files.** `wait_trials.sh` calls `tasks_post.sh 1 team-session team` ten times, and each call rewrites the same `meta/tasks/gate-team-session-1.md`. From the second trial on, `git commit` has nothing to commit and the script fails.
- **Push from the sandbox.** `tasks_post.sh` pushes from sandboxed Bash. That needs `github.com` on the proxy allowlist, and HTTPS credentials (an SSH remote cannot pass the HTTP proxy). Neither is stated.
- **Credits runner writes.** Step 5 creates `jobs/gate-<i>.md` in **nitpick-libs'** `.internal/credits/`, another project's tree (RULES §4). It runs `run.sh` from the diogenes seat's sandbox, and `run.sh` writes `out/`, `home/`, `config/` and `LEDGER.md` there, reads `~/.config/nitpick-credits/key`, and reaches the API. None of this is on the diogenes sandbox's allow list, and none of it is marked `[author]`.

**Fix.**
- Name spec files `gate-<EXECUTOR>-$(date -u +%Y%m%dT%H%M%SZ)-<i>.md`.
- Add an `[author]` step 0b:
  > either run step 5 and the pushes from a terminal, or add `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits` to `allowWrite` and `github.com` and `api.anthropic.com` to `allowedDomains` in `diogenes/.claude/settings.local.json` for the gate, and remove them at step 12; the five `jobs/gate-<i>.md` files are created by the author (one line each: `Reply OK.`).

### V-13 · major (G6 and G8 contaminated) · `0.0.4.0.md` steps 2 and 3

**Problem.** The author relays by hand inside the gate that measures "no relay", and the G6 trials may depend on him re-arming the wait.

**Evidence.**
- "the author types into the worker: `Run tests/gate/messages.sh team …`"
- "before each trial the author (or the worker's own re-arm after its claim) restarts `dio wait --for-me`".

**Fix.**
- Give the worker one setup prompt at step 1, logged as `relay: setup` in `relay_log.md`, that states all of its gate duties:
  > when woken by a task: list, claim, check the poster, re-read the spec at the blob, do it, report, then re-arm `dio wait --for-me`; when woken by `reply-expected` messages from the Max seat: run `messages.sh team …`.
- Delete "the author (or …)" from step 3.
- G6 passes only if all 10 re-arms were the worker's own.

### V-14 · major (no positive control) · `0.0.4.0.md` step 8 (G5)

**Problem.**
- If `libs-seat` has no holder at gate time (0.0.3.0 assigns it only "when he chooses"), the send is refused and `probe-capture`'s inbox is empty for the wrong reason.
- The real capture route, the `SessionStart` hook for a session started with `--name libs-seat`, is not exercised.
- The "or tasks" half of G5 is not tested ("posts nothing").

**Fix.**
- Precondition: `dio role show nitpick-libs` names a holder.
- After the send, `dio sent --state` must show `to_identity` equal to the holder.
- Add `claude --name libs-seat` and check that `dio who` shows it as `anon-<sid8>` or refused, never as `libs-seat`. This needs §1.1 of 0.0.2.2 to fall back to `anon-<sid8>` when the name fails validation.
- Post one task to project `nitpick-libs` and show that `probe-capture`'s `dio task list --mine` does not list it.

### V-15 · major (gate understates latency) · `0.0.2.2.md` §2.5; G7

**Problem.** `elapsed_ms` is measured inside the Python process, so it leaves out interpreter start-up and imports, which is most of a hook's cost. G7 can pass while the real hook time exceeds 300 ms.

**Fix.**
> `elapsed_ms` = `(now − process start)`, with process start from `/proc/self/stat` field 22 ÷ `os.sysconf('SC_CLK_TCK')` plus the boot time from `/proc/stat` `btime`.

Also cross-check five runs with `bash -c 'time …'` (not `/usr/bin/time`, which may be absent).

### V-16 · major (wrong expected value) · `0.0.1.2.md` §2 `test_contested_rounds_two_processes`, §3 block R2; `README.md` G3; `CHECKLIST.md`

**Problem.** The referee runs `takeover` *before* each round, and round 1's takeover finds an absent lease. With R rounds each won, that gives R takes plus R − 1 takeovers, so **fence = 2R − 1**, not "2R or 2R + 1". The unit test has the same off-by-one. An executor will stop on the mismatch.

**Fix.** Either have the referee also take over after the last round (and treat a takeover of an absent or free lease as a refused no-op), or state "fence == 2R − 1" everywhere. Say which, in the test and in R2.

### V-17 · minor (safety) · `0.0.4.0.md` §1 and step 12

**Problem.** "the executor writes it with the Write tool … Removed at the end". No `diogenes/.claude/` exists today, but one may exist by gate time (for example, an executor sandbox setting). Writing it then overwrites the file, and removing it deletes it.

**Fix.**
> Read `.claude/settings.local.json` first; if present, add `"SendMessage","ListAgents"` to `permissions.deny` with Edit and remove only those two entries at step 12; create and delete the file only if it was absent.

### V-18 · minor · `0.0.3.0.md` step 6 (DR-92, no-hooks leg)

**Problem.** The session was registered by hand without `--socket`, but the socket variable is set. `dio send` without `--session` resolves by rule 3 and gets `refused: socket not registered`. It is also unclear who runs the commands (the author or the probe's Claude).

**Fix.** Use `dio --session <id> send author …`, and say "the probe session's Claude runs, in Bash, …".

### V-19 · minor · `0.0.0.0.md` §8 (`rm -rf "$P"`)

**Problem.** These steps still need `$P` after 0.0.0.0 deletes it:
- DX-13's 2-hour and overnight legs "may be pending" when 0.0.0.0 closes;
- 0.0.0.1 step 3 opens `probe-a` "in `<P>`";
- 0.0.1.2 §3 refers to `$P`.

**Fix.** Say "remove `$P` only after DX-13's last leg is filed". Give 0.0.0.1 and 0.0.1.2 their own directories.

### V-20 · minor · `0.0.0.0.md` §8 against §9

**Problem.** The two checks contradict each other. "token lines redacted, `grep -c TOKEN` must print 0" cannot hold, because redacted lines still contain the variable name (`…_TOKEN=<redacted>`). §9 instead checks `grep -r MESSAGING_TOKEN … | grep -v redacted`.

**Fix.** In both places use `grep -rE 'TOKEN=[^<]' <dir> | wc -l` → `0`.

### V-21 · minor · `0.0.1.0.md` §3 step 7 `test_init_creates_schema_v1`

**Problem.** It says "the 16 tables exist", but schema v1 creates **18**, plus `sqlite_sequence`.

**Fix.** Use "the 18 tables in §2 exist".

### V-22 · minor · `0.0.1.0.md` §3 step 2

**Problem.** "Global options: `--home PATH`, `--session ID`, `--json` (accepted everywhere)". With argparse, options defined on the top-level parser are rejected after the subcommand (`dio who --json`), and the plan uses that form throughout.

**Fix.**
> Define them on a parent parser passed as `parents=[common]` to every subparser, with `default=argparse.SUPPRESS` on the subparser copies.

### V-23 · minor · `0.0.1.0.md` §3 step 5

**Problem.** "project from the role's prefix mapping" is never defined. `libs-seat`, `compiler-seat` and `dio-seat` do not match the project ids `nitpick-libs`, `nitpick` and `diogenes`.

**Fix.**
> The project is the one whose `orchestrator_role` equals ROLE; otherwise `--project P` is required (`refused: which project? pass --project`).

### V-24 · minor · `README.md` §3 (assumptions)

**Problem.**
- **DQ-4.** If hooks are denied on the Team seat, the change reaches beyond "0.0.3.0 only". The gate scripts need `--session` on every worker command. G2's "through the injection pointer" fails on the Team side. G4 has no hook-driven presence.
- **DQ-15.** The plan takes `1.00`, against `OPEN_QUESTIONS.md`'s "two-thirds", so the heading "Every row plans on OPEN_QUESTIONS.md's recommendation" is false for this row. The credits README of 17:4x does support `1.00`.
- **DQ-16** (build, not trial Agent Mail) is relied on but not listed.

**Fix.**
- DQ-4 column: "0.0.3.0, and 0.0.4.0's scripts (`--session`) and G2's pointer leg".
- Mark DQ-15 "**deviates** from the filed recommendation on newer evidence; the author confirms".
- Add a DQ-16 row ("build; re-cuts nothing").

### V-25 · minor (author's settings) · `0.0.0.1.md` §1 step 6 (DQ-27)

**Problem.** Setting `autoMemoryDirectory` in the Team account's **user** settings to nitpick-libs' memory directory sends every project's auto-memory on that account into nitpick-libs' directory.

**Fix.**
> Set it in `nitpick-libs/.claude/settings.local.json` for sessions under `~/.claude-team`, or use `CLAUDE_CODE_PROJECT_DIR_NAME` per launch; confirm the scope on 2.1.296 first.

If neither is scoped per project, record DQ-27 as deferred.

### V-26 · minor (DR-112) · `0.0.0.0.md` §7 step 3

**Problem.** The author is handed an SQL statement: "from a terminal: `sqlite3 <P>/probe.db "UPDATE lease …"`". The executor's Bash can write `$P`.

**Fix.** "The executor runs, from its own Bash: …".

### V-27 · minor (consistency)

- **`run.sh --task` vs the wrapper.** ROADMAP's In list, DESIGN §10.1 and DR-104's verification say `run.sh --task t<N>`. The plan ships a wrapper and leaves `run.sh` unchanged. That is a sound reason (RULES §4), but it is not in README §3, so add a row.
- **Push policy contradicts itself.** README §9.5 says "Nothing is pushed to `origin` until the record commit; every subcycle commits locally and pushes at its end", and 0.0.4.0 §4.5 repeats both halves. Task posts also need pushed specs. Pick "push at each subcycle's end".
- **Dependency table vs subcycle gates.** README §4 says 0.0.2.1 depends on "0.0.1.0, DX-6" and 0.0.2.2 on "0.0.1.1, 0.0.2.0…". The subcycle gates require 0.0.2.0 DONE and 0.0.2.1 DONE respectively. Align them.
- **Injection pointer.** README G2 says "received through the injection pointer", but `messages.sh` polls `dio inbox --count` only. Either add a check that the worker's transcript shows the pointer, or drop the phrase.
- **Worker names.** DQ-22 recommends `libs-worker_<N>`; the gate uses `dio-worker_<N>`. Give `0.0.2.2.md` §1.4 the regex `^[a-z][a-z0-9-]*-worker_[0-9]+$`.
- **DR-98, Team side.** The Team half's check is missing from 0.0.3.0 step 6, which greps only `~/.claude/settings.json`. CHECKLIST says "both". Add `~/.claude-team/settings.json`.

### V-28 · minor · `README.md` §4 and §6 (size)

**Problem.** The 33 hours is about 4.1 seat-days. That is within the ROADMAP's 3 to 5, but over the brief's 2 to 4, and the author's DX-13 waits are not counted. The cut line saves only about 3 hours, and its trigger (28 h by the end of 0.0.2.0, against 20 to 21 h planned) fires only after a 35 % overrun.

**Fix.** Trigger at "24 h by end of 0.0.2.0". Add a fourth cut: "0.0.3.0's `adapter print-settings` and `adapter check` (the executor prints the fragment by hand)".

### V-29 · minor (as written)

- **DX-7.** `head -40` of the changelog can miss a backport entry. Grep the whole file, and also check `/usr/share/doc/libsqlite3-0/changelog.Debian.gz`, the library Python uses.
- **0.0.2.2 block V** uses `/usr/bin/time` (package `time`, which may not be installed). Use bash's `time`.
- **`tests/fixtures/hook-userpromptsubmit.json`** and **`statusline-max.json`** are used but not listed in any layout. Add them to 0.0.2.1 and 0.0.2.2.
- **Gate spec template.** `tasks_verify.sh` reads "the line after `acceptance:`", but the spec template is never given. Give its exact text.
- **`dio task list --json` keys.** Block V uses `id` and `*_label`, which are never listed. List them.

---

## Checked and found sound

- **Coverage.** Every ★ requirement (DR-1 … DR-7, 10, 11, 14, 16, 17, 20, 24, 30–34, 36, 39, 55–57, 59, 80 tag, 91 subset, 92, 98, 99–109) has a building subcycle and a test or gate step, apart from the defects above.
  - DR-112 is honoured except for V-26.
  - Nothing out of scope is built. `takeover`, `presence set` and `adapter latency` serve ★ requirements.
  - The ROADMAP's Out list is restated correctly.
- **The measurements.**
  - No step connects to a Unix socket or loopback TCP from sandboxed Bash. The process check only tests whether paths exist (see V-8 for its other problem).
  - The spool is reserved and nothing reads it.
  - Hooks and the status line run outside the sandbox.
- **Safety.**
  - No step touches the system Redis, MySQL or PostgreSQL or a default port.
  - Probe settings stay in probe projects.
  - Every user-settings change and the `PATH` install are `[author]`.
  - Store creation is guarded against widening the sandbox ("Do not widen the sandbox to make it pass").
  - A backup runs before the first real-store use (0.0.3.0 step 0) and at gate start and end. A missing store is refused rather than created silently.
  - The envelope, the pointer-only injection with a `CANARY-BODY` test, and spec-by-blob with the poster check keep messages and tasks as data.
  - `show` never prints a spec body.
- **As written.**
  - Schema v1 parses on 3.45.1. `window` as a column name is accepted by SQLite's context-sensitive WINDOW keyword, and `RETURNING` needs ≥ 3.35.
  - The `dio.py` entry point with `-I` and the `sys.path` insert is correct.
  - The hook JSON shapes match: `hookSpecificOutput.additionalContext` on `UserPromptSubmit`, `PostToolUse` and `SessionStart`; the `statusLine` object; `permissions.deny` tool names.
  - `take.py`, `race.py`, `dx2.sh`, `dx3.sh` and the block 3 and block 4 Python one-liners are syntactically valid.
  - The wrapper's `set +e`/`RC` handling is correct for `sh`.
  - `run.sh` takes `JOB [MODEL] [MAX_TURNS]` and passes no `--bare`, as the plan assumes.
  - The `1.00` credits correction matches the credits README's 17:4x note.
  - Running test totals are consistent: 16 → 29 → 40 → 56 → 66 → 80, before V-1's additions.
- **Order.** Experiments come first; DX-1 and DX-3 gate 0.0.1.0; DX-2 and DX-13's 10-minute leg gate 0.0.2.2; DX-5 is required before the Team half; the `room()` stub avoids a cycle between 0.0.2.0 and 0.0.2.1.
- **Day zero (0.0.0.1)** matches the ROADMAP's six points, apart from V-2 and V-25.

## Could not check

- **Behaviour on Claude Code 2.1.296**, all of which the plan correctly assigns to experiments:
  - whether `$TMPDIR`, `/run/user/1000` and host `/proc` are visible from sandboxed Bash;
  - whether project-level `disableAllHooks` suppresses user hooks;
  - whether `env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS="0"` is honoured;
  - whether `permissions.deny` binds in bypass mode;
  - the `autoMemoryDirectory` scope.
- **Whether the status line refreshes while a session is idle.** If it does, `last_seen_how='status-line'` keeps an idle session `live`, and G4's `live-idle` never appears. DX-3 and DX-6 should record whether `dx3-status.jsonl` grows during an idle stretch. If it does, `live-idle` should ignore status-line refreshes.
- **Whether GNU `install` accepts `/dev/stdin` from a here-document** (0.0.3.0 step 1). A safer form is `printf '%s\n' '#!/bin/sh' 'exec python3 -I …/dio.py "$@"' > ~/.local/bin/dio && chmod 755 ~/.local/bin/dio`.
- **Whether the diogenes remote is SSH or HTTPS** (V-12), and whether the API credits currently have a balance for step 5.