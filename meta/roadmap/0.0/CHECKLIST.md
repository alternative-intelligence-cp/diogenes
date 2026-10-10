# Cycle 0.0 checklist, for the verifier

One line per acceptance item. Tick with the verifier's seat name and the output path. Commands run from the diogenes checkout; `dio` is `python3 -I src/dio.py` until 0.0.3.0 puts it on `PATH`. Temporary homes use `DIO_HOME`. `<P>` is `/home/randy/.local/share/diogenes-probe` and `<PDB>` is `/home/randy/.local/share/diogenes-probe-db` (0.0.0.0 §1).

## 0.0.0.0 — experiments

- [ ] Versions printed (block S): `python3 -c 'import sqlite3;print(sqlite3.sqlite_version)'` → `3.45.1`
- [ ] DX-1 free-running: `cat <P>/log/dx1-A-free.txt <P>/log/dx1-B-free.txt` → `errors 0` on both, the larger printed `fence` = W_A + W_B, the `ns` net ids differ (host versus sandbox), the `first`/`last` intervals overlap by ≥ 10 s
- [ ] DX-1 contested host/sandbox (block 1d) → one winner per round, referee's `fence` = rounds, `ns` net ids differ
- [ ] DX-1 contested sandbox/sandbox (step 4) → same, both racers' `ns` differ from the host referee's
- [ ] DX-7 changelog grep recorded (block 2's output pasted into the results file, both changelogs)
- [ ] DX-2 prompt injection quoted back; PostToolUse once per change; peer-message turn ran the hook; cap figure; time < 50 ms (bash `time`)
- [ ] DX-3 findings table filed, including the `pid` namespace line; `grep -rE 'TOKEN=[^<]' meta/research/done/dx-logs-0.0/ | wc -l` → 0
- [ ] DX-6 key paths filed (block 4)
- [ ] DX-13 10-minute wake recorded, with whether `dx3-status.jsonl` grew while idle; 2 h and overnight recorded or `pending`
- [ ] `EXPERIMENTS.md` marks each DONE; `<P>` and `<PDB>` removed after DX-13's last leg: `ls <P> <PDB> 2>&1` → `No such file` twice, or the record says `pending: DX-13 legs`

## 0.0.0.1 — day zero (when the Team seat exists)

- [ ] DQ-4 facts (Owner, managed settings) filed in the DX results file §day-zero
- [ ] DX-4 result filed (not blocking)
- [ ] DX-5: hooks ran, `rate_limits` absent/present, `cost` present, status-line fixed-path answer filed; the Team probe's status line was tee-only (`dx5-status.sh`), and `~/.claude/usage-latest.json`'s `written_by` never named a Team session
- [ ] DQ-27 memory path recorded as a fact, with its scope, or `deferred`

## 0.0.1.0 — store and core

- [ ] `python3 -I src/dio.py --version` → `dio 0.0 (schema 1)`
- [ ] `DIO_HOME=$T store init` → `schema 1 (created)`; `store check` → `check: ok; …`
- [ ] `python3 -m unittest discover -s tests` → `Ran 18 tests … OK`
- [ ] `--name author` and `--name libs-seat` refused (`test_register_refuses_reserved`)
- [ ] No socket, no `--session`, no tty → exit 3 with the DR-107 text (`test_resolve_refuses_without_socket`)
- [ ] `register` never moves a role (`test_register_never_moves_role`); a non-holder's `role assign` refused (`test_role_assign_by_non_holder_refused`)
- [ ] `who` states live / live-idle / gone / unknown (`test_who_states`); an impossible check reads `unknown`, never `gone` (`test_process_check_impossible_reads_unknown`); `--json` carries every DR-16 field
- [ ] `ls ~/.local/share/diogenes 2>&1` → `No such file` (no real store yet)

## 0.0.1.1 — messages

- [ ] `Ran 31 tests … OK`
- [ ] `grep -c 'UPDATE message' src/diogenes/*.py | grep -v ':0' | wc -l` → 0
- [ ] G5 unit: `test_role_capture_refused` passes
- [ ] `inbox --since 0` twice identical (`test_inbox_since_idempotent`)
- [ ] Envelope sample pasted in the record with `DATA, NOT INSTRUCTIONS` on line 2 and `auth="digest: unchecked"`
- [ ] `--auth nonce:…` refused; store dump holds no nonce text

## 0.0.1.2 — leases

- [ ] `Ran 42 tests … OK`; `test_hazard_1_*`, `_2_*`, `_5_*`, `_13_*` pass
- [ ] `grep -rn announce src/diogenes | wc -l` → 0
- [ ] `test_expired_is_not_held` and `test_exact_id_match` pass
- [ ] DX-1 replay with `dio` (block R2): referee R, wins A + B = R (within 1), `status` reads `free (fence 2 × (wins A + B) …)`, recorded

## 0.0.2.0 — tasks

- [ ] `Ran 60 tests … OK`
- [ ] `grep -c -- '--bare' /home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/run.sh` → 0; `sh -n src/dio_credits_run.sh` ok
- [ ] `test_post_requires_orchestrator_role`, `test_post_resolves_blob_and_refuses_uncommitted`, `test_post_refuses_unpushed_without_local` pass (DR-102); `test_claim_refuses_forged_poster` passes; `test_task_survives_orchestrator_handoff` passes
- [ ] `test_post_prints_room_and_refuses_below_floor` passes (DR-103)
- [ ] `test_claim_is_cas_one_winner`, `test_stale_and_repost` pass (DR-100)
- [ ] `test_verify_refuses_reporter`, `test_verify_subagent_labels` pass (DR-101)
- [ ] `test_same_four_commands_for_three_kinds` passes (DR-99); `test_credits_wrapper_dry` and `test_credits_wrapper_failure_not_reported` pass with the real `LEDGER.md` unchanged (DR-104)
- [ ] `test_show_never_prints_spec_body` passes

## 0.0.2.1 — meters

- [ ] `Ran 70 tests … OK`
- [ ] Status-line wrapper with `--then cat` under 0.15 s (block V)
- [ ] `test_meters_room_max` (61/68 → 18.0) and `test_meters_room_unknown_names_missing` pass (DR-56)
- [ ] `test_team_estimate_cost_ratio` or, if cut, `test_team_unknown_without_inputs` and `test_team_manual_wins_when_newer` pass (DR-109, DR-55)
- [ ] `test_credits_fact_and_correction` passes with correction 1.00 and superseded 0.67 (DR-59)
- [ ] `test_who_shows_ctx_across_accounts` passes (DR-57)

## 0.0.2.2 — wait and hooks

- [ ] `Ran 87 tests … OK`
- [ ] Slowest of five `hook inject` runs < 0.15 s by bash `time`, and the logged `elapsed_ms` of those runs within 20 ms of it (block V)
- [ ] `test_posttooluse_once_per_change` passes (G7 unit); `test_inject_under_1000_chars` passes (DR-24)
- [ ] `test_inject_never_fails` passes; `test_session_start_output_text_under_300` passes (DR-4); `test_session_start_reserved_name_falls_back_to_anon` passes
- [ ] `test_wait_wakes_on_task_post`, `test_wait_wakes_on_reply_expected_only`, `test_wait_max_exits_4`, `test_wait_sees_task_posted_before_start`, `test_wait_rearm_does_not_refire_on_same_item` pass (DR-105)
- [ ] `grep -n 'DX-13' src/diogenes/wait.py` names the results file beside the `--max` default

## 0.0.3.0 — install

- [ ] Real store: `dio store check` → `check: ok; …`; `ls -la ~/.local/share/diogenes/store` → `-rw-------`
- [ ] `dio --version` from a terminal (`[author]`) → `dio 0.0 (schema 1)`
- [ ] `dio adapter check --account max` → `hooks 3/3, statusLine wrapped, agent-teams off, allowWrite present`
- [ ] `dio adapter check --account team` → same, or `pending` with the reason
- [ ] `dio role show diogenes` → `dio-seat → <seat>`; `dio who` lists `author` (terminal)
- [ ] `wc -l docs/USING.md` ≤ 120; its §4 holds RULES §1's three conditions verbatim
- [ ] DR-92: `dio send`/`dio inbox` from sandboxed Bash with hooks; and in the `disableAllHooks` probe without them, with `--session`
- [ ] DR-98: `--bare` count 0; agent teams `0` in both settings files (`~/.claude/settings.json` and `~/.claude-team/settings.json`, or `not in settings` with the profile export noted)

## 0.0.4.0 — the gate

- [ ] G1: block V → `verified 15 {'team-session': 10, 'credits-job': 5} self-verified [] rejected 1` (passes at ≥ 5 per kind and `rejected 1`); `relay_log.md` shows `relay: none` on every line after `relay: setup`
- [ ] G2: `messages.sh` both sides → `sent 10, received 10, acked 10`; `dio sent --state` each side 10 `acked`; the deny entries present during, removed after
- [ ] G3: `python3 -m unittest tests.test_leases -v` → the four hazard tests `ok`; replay figures copied from 0.0.1.2
- [ ] G4: `dio who --json` from each account lists the other's session with `state, name, session_id, ctx_pct`; `live-idle` seen; `dio meters` Team line reads `estimate (method: …, <date>)` or `unknown (missing: …)`
- [ ] G5: `dio register --name libs-seat …` → `refused: reserved name`; `dio role assign libs-seat --to probe-capture` by `probe-capture` → `refused: only the holder or the author assigns libs-seat`; `dio sent --state --json` shows the send's `to_identity` = the holder; `probe-capture`'s `dio inbox` empty and `dio task list --mine` lists no gate task; the `claude --name libs-seat` session registered as `anon-<sid8>`
- [ ] G6: `wait_trials.sh 10` → 10 `claimed after` lines, all re-arms the worker's own; `probe-capture` (no wait) gained no turn in 10 minutes
- [ ] G7: `dio adapter latency --since <day>` → `p95 < 300`; `n ≥ 200`; five `bash -c 'time …'` runs within 20 ms of the logged figure
- [ ] G8: the author's `relays today: 0` line
- [ ] Close: DX results file §Gate; `EXPERIMENTS.md` updated; `ROADMAP.md` 0.0 `DONE (<date>)`; `git log -1 --stat` shows the move to `meta/roadmap/done/0.0/`; `git status -sb` shows `origin/main` in sync
