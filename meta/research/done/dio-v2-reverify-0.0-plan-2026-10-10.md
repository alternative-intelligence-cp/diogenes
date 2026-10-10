<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-v2-reverify-0.0-plan-2026-10-10.md: the re-verification of cycle 0.0 after its first amendment (claude-opus-5-5, 23 turns, $1.73 by the CLI). Its prompt is prompts/dio-v2-reverify-0.0-plan-2026-10-10.md. -->

# Re-verification of the amended cycle 0.0 plan (`meta/roadmap/0.0/`), 2026-10-10

## Verdict: **PASS WITH FIXES**

I read all 13 files in `meta/roadmap/0.0/`, the first verifier's report, M1–M5 and `run.sh`, and checked the relevant DRs in REQUIREMENTS. I ran nothing; every judgement comes from reading.

**What holds:**
- **The blocking fixes.** V-1, V-2 and V-4 are fixed in the text. V-3's stale-output half is fixed; its failed-run half is only partly fixed (R-4).
- **The four mismatched expected values** (V-4 to V-6, V-16) are right once re-derived.
- **Test totals** are consistent everywhere: 18 → 31 → 42 → 60 → 70 → 87. I counted each subcycle's table.
- **Safety is intact:**
  - every experiment uses private files, and no step touches a database server or a default port;
  - no step connects to a socket, and nothing writes the author's `~/.claude` files;
  - every settings change, install and sandbox widening is marked `[author]`;
  - the author types no SQL;
  - the only spending step is announced with a cap: 0.0.4.0 step 5, five one-turn Haiku jobs. The README records $0.0017 for one Haiku smoke job, so about $0.01 in total.

**What must be fixed first:**
- **Three new defects will fail a correct implementation or its gate:**
  - R-1: the credits half of G1 is refused at its first `register`;
  - R-2: the latency from process start can read up to a second high;
  - R-3: the handoff test fails whenever two commands share a second.
- **Two fixes are incomplete:** R-4 (V-3, part 2) and R-5 (V-18's fix not carried into G5).

None of these needs a re-cut.

## V-1 … V-29

| # | Reviser's claim | Result | Evidence (new text) |
|---|---|---|---|
| V-1 | Fixed | **Confirmed** | 0.0.1.0 step 5: "refuses unless the caller is `author`, or the caller is the role's current holder (a handoff); a role with no holder, or one that does not exist yet, may be assigned only by `author`". Test row present, 18 tests. G5 live step in 0.0.4.0 step 8. The worker check comes first; the holder hand-on in `test_role_assign_records_event` still passes. |
| V-2 | Fixed | **Confirmed** | 0.0.0.1 step 4: "`umask 077; tee -a <TEAM_P>/log/dx5-status.jsonl >/dev/null; echo probe-t`" and "**Never pipe into your Max status-line command under `~/.claude-team`**". The settings sentence is repaired. A read-only check of `written_by` is added. |
| V-3 | Fixed | **Partly fixed (R-4)** | Overrides `DIO_CREDITS_DIR`/`DIO_CREDITS_RUN`/`DIO_SRC`, both early exits repeated before the claim, and "`[ "$(stat -c %Y "$OUT")" -lt "$T0" ]` … `task progress … run failed`". The stale-output case is closed. **However, `run.sh` exits 0 after an API error** (its last command is the Python epilogue, which always writes a fresh `out/JOB.md`). So "a run that fails … is **never reported**" is false for API failures. |
| V-4 | Fixed | **Confirmed** | "`room 18.0 = 95 − 61 − 0.5 × (100 − 68)`" in §1, the test and CHECKLIST. Re-derived: 95 − 61 − 16 = 18.0. Cost-ratio: 61/30 × 5 × 4 = 40.67, room 54.33. Manual 31 → room 64. All correct. |
| V-5 | Fixed | **Confirmed** | "an environment built from `os.environ` minus `CLAUDE_CODE_MESSAGING_SOCKET`, `CLAUDE_SESSION_ID` and `DIO_HOME` … `stdin=subprocess.DEVNULL`". `register_author()` uses a pty and has a stated fallback. |
| V-6 | Fixed | **Confirmed** | Fixtures `pa/tree/me`, `pa/tree/names`, `pa/tree/m`, `pa/tree/nitpick-posix`, `pb/tree/nitpick-posix`. The regex note says the project part "is at least two characters". |
| V-7 | Fixed, and further | **Confirmed** | `<PDB>` is reached only through probe `allowWrite`. Every racer runs in `probe-a`/`probe-b`. `take.py` prints the `net`/`mnt`/`pid` namespaces and first/last take times. Acceptance: "`max(first_A, first_B) + 10 ≤ min(last_A, last_B)`"; "A leg's namespaces are identical … the leg is void". The replay has its own `<P2>`/`<H>`. |
| V-8 | Fixed, different mechanism | **Confirmed, with one gap (R-6)** | "`impossible` when … the session's `pid_ns` is set and differs … `os.path.isdir(os.path.dirname(socket_path))` is false"; "an `impossible` result writes nothing". `wait_pidns` is added. The reason for not using `/proc/1/comm` is sound. Gap: a sandboxed re-`register` overwrites the host `pid_ns` (R-6). |
| V-9 | Fixed | **Confirmed** | "Run the three queries once at once, before any sleep"; per-category `wait_seen` `{"m","t","e"}`; both tests added. Totals: hooks 10 + wait 7 = 17. |
| V-10 | Fixed; revocation clause declined | **Decline sound; fix defective (R-3)** | "the newest `role_event` for that role with `at <= task.at` names it as `new_holder`". The decline is sound: an author assignment is also the routine handoff, so it cannot mean revocation. But second-resolution `at` breaks the new test (R-3). |
| V-11 | Fixed | **Confirmed** | Acceptance: `grep -qx "<base> $(git rev-parse HEAD:meta/tasks/<base>.md)"`; a `gate-reject` task with `acceptance: false`. Block V expects "`verified 15 {'team-session': 10, 'credits-job': 5} … rejected 1`". Re-derived: 10 trials + 5 credits = 15 verified, plus 1 rejected. Correct. `.internal` is in `.gitignore` (checked). |
| V-12 | Fixed | **Confirmed, but regression R-1** | Step 0b `[author]` covers both push options and the credits job files; the wrapper runs from the author's terminal. The new UTC stamp `%Y%m%dT%H%M%SZ` produces job names the identity regex refuses (R-1). |
| V-13 | Fixed | **Confirmed** | "This is the only thing the author types into the worker until step 11"; "G6 passes only if all 10 re-arms were the worker's own". |
| V-14 | Fixed (the task post replaced by a list check) | **Partly: task half vacuous (R-7); live step not executable as typed (R-5)** | Holder precondition, `to_identity` = holder, and the `--name libs-seat` → `anon-<sid8>` fallback with its test are all present. But for a seat, `task list --mine` means "tasks I posted", so `probe-capture`'s empty list proves nothing. |
| V-15 | Fixed | **Fixed in form, wrong in value (R-2)** | "`start = btime + starttime / CLK_TCK`". `btime` in `/proc/stat` is whole seconds, so `elapsed_ms` is overstated by a constant 0–999 ms per boot. |
| V-16 | Fixed | **Confirmed** | Re-derived: round 1's takeover finds the lease absent and is a no-op; 20 takes, then 19 takeovers plus 1 final, give fence = 40, ending `free`. "`fence == 2 × 20 == 40`". `ref.sh` adds the "final" takeover. R2: "`F == 2 × (wins_A + wins_B)`". |
| V-17 | Fixed | **Confirmed** | "the executor **reads** … **absent** … **deletes the file** at step 12; **present** … removes only those two entries". |
| V-18 | Fixed | **Confirmed in 0.0.3.0**, but the same defect remains in 0.0.4.0 step 8 (R-5) | "`dio --session <that id> send author …`"; "the probe session's Claude runs the commands". |
| V-19 | Fixed | **Confirmed** | "**only after DX-13's last leg is filed**". 0.0.0.1 has `dio-probe-dx4`; the 0.0.1.2 replay has `diogenes-race`. |
| V-20 | Fixed | **Confirmed** | `grep -rE 'TOKEN=[^<]' … \| wc -l` → 0 in §8, §9, 0.0.4.0 §4.1 and CHECKLIST. |
| V-21 | Fixed | **Confirmed** | "Eighteen tables (…)" listed; the test says "the 18 tables in §2". I counted 18. |
| V-22 | Fixed | **Confirmed** | "`parents=[common]` … `default=argparse.SUPPRESS` on the subparser copies". Note: these need two parent-parser instances, because argparse shares action objects between parents. |
| V-23 | Fixed | **Confirmed** | "the project is the one whose `orchestrator_role` equals ROLE … `refused: which project? pass --project`". |
| V-24 | Fixed | **Confirmed** | The DQ-4 row is widened, DQ-15 is marked "**Deviates** … **The author confirms**", and a DQ-16 row is added. |
| V-25 | Fixed | **Confirmed** | "scoped to the `nitpick-libs` project, **not set in the Team account's user settings** … else `deferred`". |
| V-26 | Fixed, differently | **Decline sound** | `dx13-touch.sh` is run by name. The executor's sandbox cannot write `<PDB>` after V-7, so the verifier's form is unusable. README §7.2 states the rule. |
| V-27 | Fixed, all six | **Confirmed** | `run.sh --task` row; "every subcycle commits locally and pushes … at its end"; the dependency table now matches the subcycle gates (0.0.2.1 needs 0.0.2.0 and DX-6; 0.0.2.2 needs 0.0.2.1, DX-2 and DX-13); the pointer is a yes/no; the worker regex is in both places; the Team-side `AGENT_TEAMS` grep is added. |
| V-28 | Fixed | **Confirmed** (see R-10 on re-sizing) | "§6 … passes 24 hours"; a fourth cut; "33 hours, about 4.1 seat-days: within the ROADMAP's range and over the brief's". |
| V-29 | Fixed, all five | **Confirmed** | Both changelogs are grepped; bash `time` is used; fixtures are listed in §0; the spec template is exact; the `--json` keys are listed. Nit: `… \| head -20` still caps the DX-7 output. |

## New findings

### R-1 · major (G1 credits half fails at its first command) · `0.0.4.0.md` §2 `tasks_post.sh` (line 23) against `0.0.1.0.md` step 3 (line 176)
**Problem.** `stamp=$(date -u +%Y%m%dT%H%M%SZ)` gives job names like `gate-20261012T093000Z-1`. The wrapper then runs `register --name "credits:$JOB"`, and the identity regex is `^credits:[a-z0-9-]+$`, which refuses the uppercase `T` and `Z`.
- Under `set -eu`, all five wrapper runs exit before the claim. This fails safe: nothing is claimed and nothing is spent.
- The unit tests use their own job names, so they do not catch it.

**Fix.**
- Use `stamp=$(date -u +%Y%m%d-%H%M%S)` (lowercase-safe).
- Add a case to `test_credits_wrapper_dry` that uses a job name of the gate's form.

### R-2 · major (G7 and two acceptance checks measure wrong) · `0.0.2.2.md` §2.5 (line 43)
**Problem.**
- `btime` in `/proc/stat` is whole seconds, so `time.time() − (btime + starttime/CLK_TCK)` overstates every `elapsed_ms` by the same 0–999 ms for a whole boot.
- The checks "within 20 ms of the `real` figures" in 0.0.2.2 block V, 0.0.4.0 step 10 and CHECKLIST will fail about 98 % of the time.
- G7's p95 < 300 ms can fail even when the hook is fast.

**Fix.** Use one clock for both ends: `elapsed_ms = (time.clock_gettime(time.CLOCK_BOOTTIME) − starttime / CLK_TCK) × 1000`. Field 22 counts ticks since boot on the boot clock, and Python 3.12 exposes `CLOCK_BOOTTIME`.

### R-3 · major (a correct implementation fails its own test) · `0.0.2.0.md` §1 claim step 2 (line 39); `test_task_survives_orchestrator_handoff` (line 98)
**Problem.** `role_event.at` and `task.at` have one-second resolution. In the test, "A posts; the author assigns the role to B" runs within one second. The newest `role_event` with `at <= task.at` is then the A→B event, which names B. The claim is refused as a forged poster.

**Fix.**
- At `post`, store `poster_event` (the `role_event.seq` that made the poster the holder) in the task row.
- At `claim`, check that this event exists, is for `poster_role`, and names `from_identity` as `new_holder`.
- Keep `test_claim_refuses_forged_poster`, with a bogus `poster_event`.

### R-4 · major (V-3, part 2 only partly fixed) · `0.0.2.0.md` §2 (lines 72–82)
**Problem.**
- `run.sh` saves the CLI's exit code in `RC` but never exits with it. Its last command is the Python epilogue, which writes a fresh `out/JOB.md`, error text included, and exits 0.
- So a run that hits an API error or the turn limit passes all three of the wrapper's checks and is reported.
- The gate's `grep -q OK` probably rejects it at verify time, but the plan's claim that a failed run is "never reported" is false.

**Fix.**
- After the run, require that `python3 -I -c 'import json,sys;r=json.load(open(sys.argv[1]));sys.exit(0 if not r.get("is_error") and r.get("subtype")=="success" else 1)' "$CREDITS/out/$JOB.json"` exits 0. Otherwise record the same `task progress … run failed` note and exit 5.
- Have the failure test's stub also write `{"is_error": true}` with rc 0.

### R-5 · major (G5 live step not executable as typed) · `0.0.4.0.md` step 8 (line 61)
**Problem.** `probe-capture`'s typed commands `dio role assign libs-seat --to probe-capture`, `dio inbox` and `dio task list --mine` carry no `--session`. They resolve by rule 3, through the socket. If the preceding `dio register … --session <uuid>` refresh (sent without `--socket`) clears `socket_path`, each answers `refused: socket not registered`, not the expected refusal. This is V-18's defect, fixed in 0.0.3.0 and not here.

**Fix.**
- Add `dio --session <uuid>` to all three commands.
- State in 0.0.1.0 step 5 that a refresh leaves `pid`, `socket_path` and `pid_ns` unchanged when their flags are absent.

### R-6 · minor (presence) · `0.0.1.0.md` step 5 `register` rules (lines 207–209)
**Problem.**
- A refresh from sandboxed Bash writes the sandbox's PID namespace into `pid_ns`, while `pid` still holds a host pid (the socket's basename). Examples: the DQ-4 fallback in 0.0.3.0 step 3, and a worker registering by hand.
- Every later check, including a hook's on the host, then reads `impossible`.
- So such a session stays `unknown` forever (assuming DX-3 finds a separate PID namespace).

**Fix.**
- Set `pid_ns` to the registering process's namespace only when `pid_how = 'ancestor-walk'`. For `socket-basename` or `given`, leave it NULL, unless the registering process's own namespace equals the one recorded.
- Never overwrite a non-NULL `pid_ns` recorded with `how = hook-stdin` from a non-hook call.

### R-7 · minor (V-14's task half partly and wrongly declined) · `0.0.4.0.md` step 8; `CHECKLIST.md` G5
**Problem.** For a seat, `task list --mine` means "tasks I posted", so it is empty whether or not a capture worked.

**Fix.**
- Have the Max seat, holding `libs-seat` by the precondition, post one `subagent` task to `nitpick-libs` and report it with a label.
- Then check that `probe-capture`'s `dio --session <uuid> task list --reported` is empty, and that its `task verify <t>` exits 1 with `refused: not the poster or the role's holder`.

### R-8 · minor (author load inside G6) · `0.0.4.0.md` step 0b(a) and `wait_trials.sh`
**Problem.** Under the "push by hand" option, each of the 12 posts blocks for the author's terminal push, ten of them inside the G6 trials.

**Fix.** Let `tasks_post.sh` take `--commit-only` and `--post-only PATHS`. Before step 3, write and push all ten trial specs in one push; `wait_trials.sh` then only posts.

### R-9 · minor (ambiguous paths) · `0.0.0.1.md` step 1 (`<TEAM_P>` = `${TMPDIR:-/tmp}/dio-probe-team`); `0.0.3.0.md` step 6 ("a probe project under `$TMPDIR`")
**Problem.** A seat writing these files with the Write tool sees the sandbox's `TMPDIR`, not the author's terminal's. V-7's own reasoning says the two may differ.

**Fix.** Give literal paths, for example `/tmp/dio-probe-team` and `/tmp/dio-probe-nohooks`, and say who writes the `disableAllHooks` settings file.

### R-10 · minor (consistency and size)
- **G3 wording.** README G3 says "`fence == 2 × rounds`". 0.0.1.2's replay and CHECKLIST say `2 × (wins_A + wins_B)`, which can differ by 1 at the edges. Use "2 × wins" in README.
- **The setup prompt asks for something the claim line does not print.** The prompt in 0.0.4.0 step 1 says "check that the claim line shows the poster", but 0.0.2.0's claim line names no poster. Either add `poster <from_identity> (<poster_role>)` to the claim line, or drop the clause. Also state that the claim line prints the full 40-hex blob, which the out file needs.
- **Withdrawn test row.** 0.0.2.0 §3 still lists `test_claim_refuses_when_poster_lost_role` as a "withdrawn" row. Delete the row so an executor does not write that test.
- **Size.** The amendment added seven tests, the namespace restructure of DX-1 and the replay, the wrapper rework, and gate steps 0b, 4b and an expanded 8, but the total stays at 33 h. Re-estimate it; about +2 h seems likely, still inside the ROADMAP's 3–5 seat-days. Re-check the 24-hour trigger against the new running total.
- **Loose references.** 0.0.0.0 DX-13 step 3's "0.0.2.2 step 1 has both" should read "0.0.2.2 §3 step 2" (`--reconnect`).

## Regressions checked and found sound
- **Cross-references.** README §8's last row ↔ 0.0.3.0 step 0; 0.0.1.0 step 3 ↔ 0.0.2.2 §1.4; 0.0.2.0 §5 ↔ 0.0.4.0 step 5; 0.0.1.0 step 6 ↔ 0.0.2.2 §3; 0.0.0.1 ↔ 0.0.3.0 step 3; the `--json` keys ↔ 0.0.4.0 block V. All resolve, apart from the nit in R-10.
- **Identifiers.** Every new test name matches across the subcycle files, README G5 and CHECKLIST. `dio-worker_1`, `anon-<sid8>`, `racer-a/b/ref` and `pa/…` satisfy their regexes. The only identifier that does not is R-1's.
- **Checklist.** It covers every subcycle's acceptance items and the new tests.
- **Safety.** No new step widens a sandbox without `[author]`. The new scripts (`reset.sh`, `rounds.sh`, `dx13-touch.sh`, `setup.sh`) touch only the throwaway probe stores. The real `LEDGER.md` is protected by the tests and by `run.sh`'s missing-job-file exit.