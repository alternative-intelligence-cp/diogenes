<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-v3-reverify-0.0-plan-2026-10-10.md: the final re-verification of cycle 0.0 after its second amendment (claude-opus-5-5, 27 turns, $1.72 by the CLI). Its prompt is prompts/dio-v3-reverify-0.0-plan-2026-10-10.md. -->

# Re-verification of the cycle 0.0 plan after its second amendment, 2026-10-10

## Verdict: **PASS**

All ten of the first re-verifier's findings (R-1 … R-10) are fixed in the text. I re-derived every expected value the second amendment touched, and each one holds. None of the 29 findings V-1 … V-29 has regressed. The safety rules hold across the whole plan.

I found nine new defects, all minor. Each has an obvious fix, and none of them is a safety or spending risk. The executor should fix them with dated notes while executing. The nearest to major is R-11, a missing space in the credits wrapper. It makes one of the plan's own tests fail if the wrapper is copied verbatim, but it fails safe (nothing is claimed or spent) and the error message names the cause.

**About numbering:** the earlier report's R-1 … R-10 appear in tables below, so I number the new findings **R-11 … R-19** rather than starting again at R-1. (See R-18: `R-n` labels already collide once in this plan.)

I ran nothing. Every judgement comes from reading:
- all 13 files in `meta/roadmap/0.0/`;
- both earlier reports and the measurements M1–M5;
- `run.sh`;
- the relevant parts of REQUIREMENTS and ROADMAP.

---

## R-1 … R-10 (the second amendment)

| # | Reviser's claim | Result | Evidence (new text) and re-derivation |
|---|---|---|---|
| R-1 | Fixed | **Confirmed** | 0.0.4.0 §2: "`stamp=$(date -u +%Y%m%d-%H%M%S)`: **digits and hyphens only**". The credits job is "`<base>` without its `credits-job-` part". So base `gate-credits-job-20261012-093000-1` gives job `gate-20261012-093000-1`, which registers as `credits:gate-20261012-093000-1`. That matches `^credits:[a-z0-9-]+$`. `test_credits_wrapper_dry` now says "Run twice … `gate-20261012-093000-1`". The wrapper's session id keeps its `T…Z` stamp, and 0.0.1.0 step 3 has no session-id validator, so the claim is true. |
| R-2 | Fixed | **Confirmed** | 0.0.2.2 §2.5: "`elapsed_ms = (time.clock_gettime(time.CLOCK_BOOTTIME) − starttime / CLK_TCK) × 1000`". Field 22 counts boot-clock ticks on current kernels, so both ends are on one clock.<br>Re-derived: tick truncation can only make `elapsed_ms` 0–10 ms too high, so `elapsed_ms ≥ in_process_ms` holds. `< 1000` holds for a hook run. The 20 ms cross-check against bash's `real` is consistent: they differ by the 0–10 ms tick plus interpreter teardown.<br>The checks are in block V, 0.0.4.0 step 10 ("both on one clock since R-2") and CHECKLIST 0.0.2.2. |
| R-3 | Fixed | **Confirmed** (follow-on: R-16) | Schema: "`poster_role TEXT NOT NULL, poster_event INTEGER NOT NULL`". Post step 1: "The newest `role_event` for that role, which names the caller as `new_holder`, is recorded". Claim step 2: "must be a `role_event` row whose `role` is `poster_role` and whose `new_holder` is `from_identity`".<br>Re-derived: A is made holder by event e₁ and posts with `poster_event = e₁`. The author's handoff to B in the same second writes e₂. At claim, e₁ still names A for that role, so the claim succeeds. A bogus or other-holder seq is refused. Still 18 tables. |
| R-4 | Fixed | **Confirmed, but the amended wrapper carries a typo (R-11)** | 0.0.2.0 §2: "`python3 -I -c 'import json,sys;r=json.load(open(sys.argv[1]));sys.exit(0 if not r.get("is_error") and r.get("subtype")=="success" else 1)'`", then "`if [ "$RC" -ne 0 ]; then exit "$RC"; fi; exit 5`".<br>Checked against `run.sh`: lines 46–92 are the epilogue. It writes `out/$JOB.md` and the ledger line whatever the CLI's exit code, and reads the same `is_error` and `subtype` fields. A max-turns stop (`subtype ≠ success`) is also refused. The failure test adds "`{"is_error": true}` … the wrapper exits 5". |
| R-5 | Fixed | **Confirmed** | 0.0.4.0 step 8(a) and (c): "`dio --session <uuid> role assign …; dio --session <uuid> inbox`" and "`dio --session <uuid> task list --reported; dio --session <uuid> task verify …`". 0.0.1.0 step 5: "updates `pid, pid_start, socket_path` … **only when `--pid` or `--socket` is given**". `test_register_refreshes_same_session` gains "a third register with neither leaves `pid`, `socket_path` and `pid_ns` unchanged". |
| R-6 | Fixed, partly differently (`given` records the caller's namespace) | **Decline sound; one edge left (R-15)** | 0.0.1.0 step 5: "`ancestor-walk`; or `given`, since a `--pid` from `$$` or `ps` is a pid in the caller's namespace … A non-hook call never overwrites a non-NULL `pid_ns` that a hook wrote".<br>The reasoning is right: a `given` pid is observed in the caller's own view, so recording the caller's namespace is more exact than NULL. With it, a host-side check reads `impossible` → `unknown`, which is honest (0.0.2.0 §5). |
| R-7 | Fixed | **Confirmed** (leftover: R-13) | Step 8(c): "posts one task … `dio task claim <t> --label g5` and `dio task report <t> --ref none --label g5` … Expected: an empty list … and `refused: not the poster or the role's holder`, exit 1".<br>Re-derived against 0.0.2.0: `--reported` lists only tasks posted by the caller or a predecessor in a role it holds, which is empty for `probe-capture`. Verify allows only the poster, the holder or `author`, so it is refused. The project is `nitpick-libs`, so block V's `--project diogenes` excludes it. |
| R-8 | Fixed | **Confirmed** (stdout issue: R-14) | §2: "`--commit-only` runs (1) and (2) and prints the N paths … `--post-only` runs only (3)". Step 3: "`tasks_post.sh --commit-only 10 team-session team > tests/gate/trial-specs.txt`". Step 0b: "**three pushes in the whole gate** … none inside the G6 trials". Re-derived: 10 trial specs, then `gate-reject`, then 5 credits specs = 3 pushes. |
| R-9 | Fixed | **Confirmed** | 0.0.0.1 step 1: "`<TEAM_P>` = `/tmp/dio-probe-team` … **the literal path, not `$TMPDIR`**". Step 3: "`/tmp/dio-probe-dx4`". 0.0.3.0 step 6: "**The executor writes** `/tmp/dio-probe-nohooks/.claude/settings.json` with the Write tool … the probe's project file, never the user's". |
| R-10 | Fixed, all five | **Confirmed** | (1) README G3: "`fence == 2 × wins` (wins = wins_A + wins_B …)".<br>(2) 0.0.2.0 claim step 4: "`poster nitpick-libs_18 (libs-seat)` … the **full 40-hex blob id**".<br>(3) The withdrawn test is now prose below the table: "Withdrawn at the first amendment, not to be written". I counted 18 table rows.<br>(4) Size: 4.5 + 5.5 + 3 + 3 + 5.5 + 3 + 3.5 + 3 + 5 = **36 h**, /8 = **4.5 seat-days**, inside ROADMAP's "3 to 5" (ROADMAP line 50). Through 0.0.2.0: 4.5 + 5.5 + 3 + 3 + 5.5 = **21.5 h**; the 24-hour trigger fires at +2.5 h, which is 11.6 %, "about 12 %". All correct.<br>(5) 0.0.0.0 DX-13 step 3: "0.0.2.2 §3 step 2's `--reconnect` flag", which exists there. |

## V-1 … V-29

| # | Reviser's claim | Result | Evidence |
|---|---|---|---|
| V-1 | Fixed | **Confirmed** | 0.0.1.0 step 5: "**refuses unless the caller is `author`, or the caller is the role's current holder**". The test row and G5 step 8(a) (now with `--session`) are present. |
| V-2 | Fixed | **Confirmed** | 0.0.0.1: "`umask 077; tee -a <TEAM_P>/log/dx5-status.jsonl >/dev/null; echo probe-t`" and "**Never pipe into your Max status-line command under `~/.claude-team`**". |
| V-3 | Fixed | **Confirmed** (with R-4; typo R-11) | The overrides `DIO_CREDITS_DIR`/`DIO_CREDITS_RUN`/`DIO_SRC` are there, both early exits come before the claim, and the success-JSON check is added. "The real `LEDGER.md`'s size … identical before and after". |
| V-4 | Fixed | **Confirmed** | 95 − 61 − 0.5 × 32 = **18.0**. For cost-ratio, 61/30 × 5 × 4 = 40.67, giving room 54.33. 0.0.2.1 is untouched. |
| V-5 | Fixed | **Confirmed** | "`os.environ` minus `CLAUDE_CODE_MESSAGING_SOCKET`, `CLAUDE_SESSION_ID` and `DIO_HOME` … `stdin=subprocess.DEVNULL`". |
| V-6 | Fixed | **Confirmed** | `pa/tree/me`, `pa/tree/names`, `pa/tree/m`, `pa/…`/`pb/tree/nitpick-posix` (0.0.1.2 §2). |
| V-7 | Fixed, and further | **Confirmed** | `<PDB>` is reached only through probe `allowWrite`. Racers run in `probe-a`/`probe-b`, and `ns` and `first`/`last` are printed. "`max(first_A, first_B) + 10 ≤ min(last_A, last_B)`". |
| V-8 | Fixed, different mechanism | **Confirmed** (R-6 gap closed except R-15) | "`impossible` when … `pid_ns` is set and differs … an `impossible` result writes nothing". |
| V-9 | Fixed | **Confirmed** | "**Run the three queries once at once, before any sleep**"; per-category `wait_seen`. 10 + 7 = 17 tests. |
| V-10 | Fixed; revocation clause declined | **Decline sound; the mechanism is now R-3's** | "A later handoff of the role does not refuse the task". The reason stands: an author assignment is also the routine handoff, so it cannot mark a revocation. |
| V-11 | Fixed | **Confirmed** | Re-derived block V: 10 trial tasks + 5 credits tasks = "`verified 15 {'team-session': 10, 'credits-job': 5} … rejected 1`". The `gate-reject` spec passes the `meta/tasks/gate-` filter. The G5 task is excluded by project. |
| V-12 | Fixed | **Confirmed** (R-1 fixed) | Step 0b is `[author]` and covers pushes and job files. The wrapper runs "from a terminal". |
| V-13 | Fixed | **Confirmed** | "This is the only thing the author types into the worker until step 11"; "**G6 passes only if all 10 re-arms were the worker's own**". |
| V-14 | Fixed | **Confirmed** (R-5, R-7 fixed; leftover R-13) | Steps 8(a)–(d) as quoted under R-5 and R-7. The `anon-<sid8>` fallback is tested in 0.0.2.2. |
| V-15 | Fixed | **Confirmed** (R-2 fixed) | Boot-clock formula, quoted under R-2. |
| V-16 | Fixed | **Confirmed** | 20 takes + 20 bumping takeovers (19 between rounds + 1 final; round 1's is a no-op on an absent lease) = "`fence == 2 × 20 == 40`". |
| V-17 | Fixed | **Confirmed** | "the executor **reads** … **absent** … **deletes the file** … **present** … removes only those two entries". |
| V-18 | Fixed | **Confirmed**, now also carried into G5 | "`dio --session <that id> send author …`"; 0.0.4.0 step 8 likewise. |
| V-19 | Fixed | **Confirmed** | "**only after DX-13's last leg is filed**". DX-4 uses `/tmp/dio-probe-dx4`; the replay uses `diogenes-race`. |
| V-20 | Fixed | **Confirmed** | `grep -rE 'TOKEN=[^<]' … \| wc -l` → 0 in §8, §9, 0.0.4.0 §4.1 and CHECKLIST. |
| V-21 | Fixed | **Confirmed** | I counted 18 tables in the schema; "the 18 tables in §2 exist". |
| V-22 | Fixed | **Confirmed** (see R-19 on `register --session`) | "`parents=[common]` … `default=argparse.SUPPRESS` on the subparser copies". |
| V-23 | Fixed | **Confirmed** | "the project is the one whose `orchestrator_role` equals ROLE". |
| V-24 | Fixed | **Confirmed** | DQ-4 widened; DQ-15 "**Deviates** … **The author confirms**"; DQ-16 row present. |
| V-25 | Fixed | **Confirmed** | "scoped to the `nitpick-libs` project, **not set in the Team account's user settings**". |
| V-26 | Fixed, partly differently | **Decline sound** | "`sh /home/randy/.local/share/diogenes-probe/dx13-touch.sh` (a script run by name; the author writes no SQL, DR-112)". The executor's sandbox cannot write `<PDB>`. |
| V-27 | Fixed, all six | **Confirmed** | The README §3 `run.sh --task` row, §9.5 push policy, §4 dependencies, G2 yes/no, worker regex and Team grep are all present. |
| V-28 | Fixed | **Confirmed**, re-sized at R-10 | "36 hours, about 4.5 seat-days"; four cuts; trigger at 24 h. |
| V-29 | Fixed, all five | **Confirmed**; the nit stands | `head -20` per changelog in DX-7 block 2 still caps the output. That is harmless for a grep of matching lines, but a long changelog could hide a match. |

## Regressions

- **Cross-references.** All of these resolve:
  - claim line (0.0.2.0 §1 step 4) ↔ setup prompt (0.0.4.0 step 1);
  - `--json` keys ↔ block V (the `poster_event` key added);
  - 0.0.1.0 refresh rule ↔ 0.0.4.0 step 8 and 0.0.3.0 step 3;
  - DX-13 step 3 ↔ 0.0.2.2 §3 step 2;
  - 0.0.2.0 §5 ↔ 0.0.4.0 step 5;
  - README G3/G5/G7 ↔ CHECKLIST.
  
  Two exceptions: `dio sent --state` (R-12) and the `R-n` label clash (R-18).
- **Identifiers.**
  - Test names agree across the subcycle files, README and CHECKLIST.
  - `credits:gate-…`, `dio-worker_1`, `anon-<sid8>`, `racer-*` and `pa/…` satisfy their regexes.
- **Checklist vs subcycles.** Every new item is present:
  - the three wrapper failure cases;
  - the gate-form job name;
  - the bogus `poster_event`;
  - the no-flags refresh;
  - the boot clock;
  - the G5 `--reported` and verify checks;
  - the G6 single push;
  - `/tmp/dio-probe-nohooks`.
- **Test totals.** 18 → 31 → 42 → 60 → 70 → 87. I counted 0.0.1.0 (4 + 14), 0.0.2.0 (18 rows) and 0.0.2.2 (10 + 7).
- **Size.** 36 h, as re-derived under R-10.

## Safety, across the whole plan

- **Private instances only.** Every experiment uses throwaway SQLite files: `<PDB>`, `diogenes-race-home`, temp homes and `/tmp/dio-probe-*`. No step touches a database server or a default port.
- **Sockets and the author's files.** No step connects to another session's socket. The only `SendMessage` uses are between the author's own probe sessions (DX-4) and one deliberate deny probe per gate side. Nothing writes the author's `~/.claude` files:
  - DX-3's Max probe runs the author's own status-line command, which is acknowledged;
  - `usage-latest.json` is only read;
  - user-settings merges are `[author]` in 0.0.3.0.
- **Spend.** The only spending step is 0.0.4.0 step 5, announced with a cap: "five one-turn Haiku jobs, expected under $0.05 … stop if `dio credits` shows under $1". Both wrapper tests use stubs and assert that the real `LEDGER.md` is unchanged. Re-runs after a failure are not explicitly capped (R-17).
- **`[author]` steps.** Settings changes, `PATH` installs, sandbox widening (0.0.4.0 step 0b, `allowedDomains`) and the job files are all written as `[author]` steps. The new no-hooks settings file belongs to a probe project.
- **No SQL for the author.** Raw SQL appears only in scripts run by name (`reset.sh`, `dx13-touch.sh`) and in `setup.sh`, which the probe session runs.

---

## New findings (all minor)

### R-11 · minor (a verbatim copy fails its own test) · `0.0.2.0.md` line 67
**Problem.** The wrapper's second pre-check reads:

`{ echo"out/$JOB.json exists; pick a new job name; nothing claimed, nothing spent" >&2; exit 2; }`

With no space after `echo`, the shell sees the single word `echoout/<job>.json exists; …`, which is not a command. Under `set -eu`, the wrapper then exits **127**, not 2, and prints "not found". `sh -n` does not catch this. `test_credits_wrapper_failure_not_reported` expects "the wrapper exits 2 before any claim". It still fails safe: nothing is claimed and nothing is spent.

**Fix.** Write `echo "out/$JOB.json exists; …"`.

### R-12 · minor (the gate's commands fail as typed) · 0.0.4.0 step 2 and step 8(b); README G2; CHECKLIST G2 and G5; against `0.0.1.1.md` line 15
**Problem.** 0.0.1.1 defines `dio sent [--state stored|delivered|acked] [--json]`, so `--state` takes a value. The gate types the following:
- `dio sent --state --json`: argparse answers "expected one argument", exit 2.
- `dio sent --state` with nothing after it: the same error.

**Fix.** Either:
- in 0.0.1.1, give `--state` `nargs='?'` (bare `--state` = show states, which also matches DR-2's own wording); or
- write `dio sent --json` in G5 and `dio sent --state acked` in G2.

### R-13 · minor (the G5 task stays in the real role) · 0.0.4.0 step 8(c) and step 12
**Problem.**
- The G5 task is left `reported` in project `nitpick-libs`.
- `withdraw` accepts only `posted|claimed|working`, so the task can never be withdrawn.
- After step 12 hands `libs-seat` back, the real holder's `inject` count, its `--reported` list and its `dio wait` (a seat's `reported` query) will all point at this gate artefact.

**Fix.** In step 12, before the handback, the Max seat runs `dio task verify <t> --verdict fail --evidence none --label gate-verifier`. The label differs from `g5`, so this is not a self-verify. The task moves to `rejected`, and the record notes it.

### R-14 · minor (the push prompt is swallowed) · 0.0.4.0 §2 and step 3
**Problem.**
- Step 3 redirects stdout: `tasks_post.sh --commit-only … > tests/gate/trial-specs.txt`.
- Under the by-hand push option, the script "prints `push needed: git push origin main`". If that goes to stdout, the line lands in the file:
  - the author never sees it, and the 5-minute poll times out;
  - `wait_trials.sh` would read the line as a path.
- `tests/gate/trial-specs.txt` is also an untracked file in the checkout.

**Fix.**
- State that every diagnostic (`push needed`, poll progress) goes to stderr, and only the paths go to stdout.
- Put the file under the gitignored `.internal/gate/`.

### R-15 · minor (R-6 leaves one inconsistent pair) · `0.0.1.0.md` step 5
**Problem.** Consider a non-hook refresh with `--pid`, for example a by-hand `register --pid $$` on a session that the hook registered:
- `pid` (and `pid_start`) change to the caller's view;
- but "a non-hook call never overwrites a non-NULL `pid_ns` that a hook wrote".

The row then pairs a sandbox pid with the host namespace. A host-side check reads a stranger's `/proc/<pid>` and gets `alive` or `dead`, which is exactly what R-6 meant to prevent.

The plan also records no marker for "a hook wrote it".

**Fix.**
- `pid`, `pid_start` and `pid_ns` always change together. A refresh that changes `pid` writes `pid_ns` by the same rule (`given` → the caller's namespace).
- The no-overwrite rule applies only when `pid` is not changed.
- Use `session_id_how = 'hook-stdin'` with `pid_how = 'socket-basename'` as the marker.

### R-16 · minor (R-3 follow-on and a test that cannot happen as written) · `0.0.2.0.md` §1 `repost`; §3 `test_task_survives_orchestrator_handoff`
**Problem.**
- **`repost`** "creates a new task copying the spec and route", but the plan does not say whose `from_identity`, `poster_role` and `poster_event` the new row carries. If B (the current holder) reposts A's task and the row copies A's event while naming B, every claim is refused as a forged poster.
- **The handoff test** says "B verifies; A's `verify` is also accepted". Once B verifies, the task is `verified`, and verify only moves `reported →`. So A's verify of the same task must be refused.

**Fix.**
- `repost` sets `from_identity` to the reposter and computes `poster_event` exactly as `post` does.
- In the test, A's verify is checked on a second reported task.

### R-17 · minor (the failure path in step 5 is incomplete) · 0.0.4.0 step 5
**Problem.** "the author withdraws it and runs a fresh job name". A withdrawn task cannot be claimed or reposted: `repost` needs `stale` or `rejected`. So a fresh run needs:
- a new `credits-job` task (`tasks_post.sh 1 credits-job credits`, which means one more push);
- a new job file.

Retries also have no stated bound inside the spend cap.

**Fix.** Spell out that sequence, and add "at most five retries in total, within the step's cap".

### R-18 · minor (an identifier clash the amendment introduced) · every amended file
**Problem.** `R-n` already names the r8 practice requirements:
- REQUIREMENTS: "Source: R-1 [r8]";
- 0.0.1.2's hazards: "R-24", "R-18", "R-23", "R-22".

The plan text now also cites "(R-1)" … "(R-10)" for the re-verifier's findings. "(R-4)" in 0.0.2.0 can be read as r8's R-4 (delivery wording).

**Fix.** In the plan files, write the re-verifier's findings as `v2 R-n`, or `RV-n`. This report's numbers would then be `v3 R-11` … `v3 R-19`.

### R-19 · minor (pre-existing, not caught before) · `0.0.1.0.md` steps 2, 4 and 5
**Problem.** `register` has its own `--session ID`, and `--session` is also a global option given to every subparser through `parents=[common]`.
- Defining it twice raises `argparse.ArgumentError: conflicting option string`.
- If `register` resolved its caller by rule 2, an unregistered id would be refused with "unknown session; register first".

This affects 0.0.1.2's `setup.sh`, the wrapper and every by-hand registration.

**Fix.** State that:
- `register` uses the global `--session` as the session to create or refresh;
- `register` does no caller resolution (apart from `--terminal`'s tty check).

---

**Could not check without running:**
- the kernel's field-22 clock on 7.0 (block V's 20 ms cross-check settles it, and the plan has the fallback);
- any behaviour of Claude Code 2.1.296, which the plan already assigns to experiments.