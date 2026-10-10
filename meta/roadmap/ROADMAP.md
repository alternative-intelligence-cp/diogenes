# Diogenes: roadmap

Drafted 2026-10-10, revised the same day. Cycles are numbered `0.0`, `0.1`, `0.2` … as `meta/README.md` describes; each cycle's subcycles (`0.0.0.0`, `0.0.0.1` …) are planned later as execution-grade plans under `meta/roadmap/<cycle>/`. A finished cycle moves to `meta/roadmap/done/`.

Sizes are rough and are in **seat-days**: working days of one Claude Code seat with its subagents, including verification.

## Day zero: the day the Team seat arrives, if 0.0 is not built

The Team seat is hoped for by Wednesday 2026-10-14 20:00, and the author reviews this plan next week, so the seat may arrive before any code exists. Everything below exists today [c1 C-14].

1. **Run DX-4 first (15 minutes).** If native messaging crosses config dirs, use `SendMessage` for pointer-only nudges ("task file at `meta/tasks/t-0001.md`, commit `abc123`"), with the work itself in tracked task files.
2. **Otherwise, a file inbox per account** under `/home/randy/Workspace/META/NITPICK/messages/{max-inbox,team-inbox}`, in the Gemini convention (one file per message, never edited), plus the seat-started background `until` loop that was observed to work: `until ls <inbox>/*.md 2>/dev/null | grep -q .; do sleep 60; done` run with `run_in_background` in the idle worker.
3. **Tasks are tracked Markdown files** with acceptance commands in `meta/tasks/`, committed before dispatch; the worker re-reads the file from git; **reports are commits** named in an inbox file; the orchestrator re-runs the acceptance commands before accepting.
4. **Roles are a line the author writes**, not something a session claims.
5. **Team meters are a manual estimate** the author states once per session; the worker runs Opus or smaller and is rotated by the author when context grows.
6. Run DX-5 and DX-26 on the first Team session, so 0.0's Team half is informed by measurement.

## Experiments before 0.0

These must run before 0.0 starts (DX-7 is a check, not a pass-or-fail). All can run today on this machine except the ones that need the second account. See `EXPERIMENTS.md`.

| Experiment | Decides | Can run today |
|---|---|---|
| DX-1 (revised) SQLite compare-and-set between a host writer and a sandboxed writer, with contested rounds | the 0.0 store shape | yes |
| DX-7 Ubuntu 3.45.1 WAL-reset fix (the FTS5 half is DONE, M4) | whether the file store is safe | yes |
| DX-2 `UserPromptSubmit` and `PostToolUse` injection, caps, and what a peer message looks like to the hook | the 0.0 delivery hook | yes |
| DX-3 Identity fields in hook stdin, Bash and subagent Bash (the socket variable), and the status line; host `/proc` visibility from Bash | registration, DR-107, DR-108 | yes |
| DX-13 (moved up) A background `until` loop's wake and lifetime cap | `dio wait` (DR-105) | yes, plus the wait |
| DX-6 Status-line fields on Max | meters publish | yes |
| DX-5 The same under the Team config dir, the managed settings, and the meters-file hazard | the Team adapter, DR-109 | needs the second account |
| DX-26 `$.session.usage()` and `session.measure` on the Team seat | a measured Team meter | needs the second account; Node |
| DX-4 Cross-account native messaging | DQ-8 and the day-zero doorbell; not blocking | needs the second account |

## Cycle 0.0: the P0 slice

- **Goal.** The Max orchestrator posts tasks that a Team-seat session and the credits runner claim, work, and report, and that a different identity verifies; two Claude seats on two accounts exchange acknowledged messages, hold the workbench lease, and see each other's state and room per account; an idle worker that chose to wait picks up its task; all through Diogenes, with no relay by the author.
- **In.** The SQLite schema for identities, sessions, roles, messages, deliveries, cursors, tasks, leases, presence and meters. The `dio` CLI with the commands in `DESIGN.md` §10.1, including `dio task`, `dio role assign` and `dio wait`. The `SessionStart` and injection hooks and the status-line call, installed under both config dirs, with the Team cost estimate. The credits runner's `--task` claim-and-report. Agent teams off. The acceptance tests for hazards 1, 2, 5 and 13, the role-capture test, and the task-path test. A one-page `docs/USING.md` for seats and workers.
- **Out.** A daemon, an MCP server, tokens, the spool transport, wake paths other than `dio wait`, the structured handoff and the nonce calls, subagent addressing, cross-account route configuration (the tag stays in), the audit table, the file-inbox export, research, memory, boards, claims, tree-state checks in `dio lock status`, alerts, any Gemini or Codex work.
- **Requirements.** The ★ set in `REQUIREMENTS.md`: DR-1 to DR-7, DR-10, DR-11, DR-14, DR-16, DR-17, DR-20, DR-24, DR-30 to DR-34, DR-36, DR-39, DR-55 to DR-57, DR-59, DR-91 (0.0 subset), DR-92, DR-98, DR-99 to DR-109.
- **Gate (measured).**
  1. **The task path:** 10 tasks posted by the Max orchestrator, 5 worked by a Team session and 5 by credits jobs, each claimed, reported, and verified by an identity other than the reporter, with zero hand relays.
  2. A scripted exchange of 10 messages each way between a Max seat and a Team seat, each acknowledged, with `permissions.deny: ["SendMessage"]` on both for the test.
  3. The lease race test from DX-1: a host writer and a sandboxed writer, contested rounds, exactly one winner each round and `fence == rounds`; the four hazard tests pass.
  4. `dio who` from each account shows the other account's sessions with state, name, session id, context % and the account's meters; an idle session reads `live-idle`; the Team room is an `estimate` with a method and date, or `unknown` with the missing input named.
  5. A second registration claiming `libs-seat` receives none of `libs-seat`'s mail or tasks.
  6. An idle worker with `dio wait` picks up a task in 10 of 10 trials; a worker without one is never woken.
  7. The injection hook completes in under 300 ms at the 95th percentile over a day's prompts, and `PostToolUse` injects at most once per change.
  8. The author reports zero hand relays between the two accounts on a normal working day.
- **Dependencies.** The second account exists with its config dir; DX-1, DX-2, DX-3, DX-6, DX-7, DX-13 run; DX-5 passed or the manual Team estimate accepted.
- **Size.** 3 to 5 seat-days (one more than the first draft, for the task path and `dio wait`).

## Cycle 0.1: the hub, two transports, tokens and the lease guard

- **Goal.** The store moves behind `diogenesd` as the sole writer; processes outside the sandbox reach it by Unix socket and processes inside it by a spool directory the hub ingests; agents get per-identity tokens through an MCP server and hooks; the lease is enforced, not only recorded; the audit chain becomes meaningful; the structured handoff and nonce calls arrive.
- **In.** `diogenesd` with the same operations as `dio`; the spool ingester (inotify) and the request-and-reply file format; `dio` switched to the socket outside the sandbox and the spool inside it; the store directory removed from `allowWrite` and added to `denyRead` in both accounts; the MCP server `diogenes` over stdio with the same tool set; tokens in 0600 files per config dir with `permissions.deny` on Read and `denyRead` on both accounts' paths in both accounts, and `allowUnsandboxedCommands: false`; the `PreToolUse` lease guard with `onFailure: "block"` and `agent_id` attribution; the `Stop` heartbeat and `SessionEnd` goodbye hooks; `dio lock status` with the tree checks and the denominator; the hash-chained audit log and its anchor; the nonce calls with hashed storage; the structured handoff and two-signal close; subagent addressing; cross-account route configuration; rename and ref-change events; the rolling-pool view; facts as value plus procedure; counts with denominators; the usage ledger and credit expiry; `dio status` with the task board.
- **Out.** Wake paths, alerts, research, memory, Gemini, Codex, Streamable HTTP for the MCP server.
- **Requirements.** DR-8, DR-9, DR-12, DR-15, DR-18, DR-19, DR-22, DR-23, DR-35, DR-41, DR-42, DR-43, DR-45, DR-48, DR-49, DR-50, DR-60, DR-74, DR-77, DR-80 (route half), DR-81, DR-82, DR-83, DR-84, DR-85, DR-86, DR-93, DR-96, DR-110, DR-111.
- **Gate.**
  1. Every 0.0 gate test passes against the hub, with the Bash-side calls going through the spool and the store file unwritable from the sandbox.
  2. A spool request round-trips within the latency measured in DX-8 at the 95th percentile; `dio lock take` from Bash is refused with `use the MCP tool`.
  3. A sandboxed `cat` of either token file fails from either account; the MCP tools work with sandboxing on; a grep of all transcripts for the token shape finds nothing; the same holds in bypass permission mode.
  4. A write in a governed tree without the lease is denied in the main session and in a subagent; with the hub stopped, the deny holds.
  5. `dio audit verify` passes; one edited row fails it.
  6. `dio lock status` prints the right denominator for a project with eight recorded checkouts.
  7. One real rotation recorded with `dio handoff`, both signals present, the role moved by assignment, and the successor re-verifies every claim by the recorded commands.
- **Dependencies.** 0.0 done; DX-8 (narrowed: spool latency and the remaining network settings), DX-9 (guard), DX-10 (`SessionEnd` and crash), DX-15 (token file, bypass mode), DX-16 passed.
- **Size.** 5 to 7 seat-days (one more than the first draft, for the spool transport).

## Cycle 0.2: wake, alerts and the author's surface

- **Goal.** A seat that opts in is woken when a message or task addressed to it arrives, by a mechanism beyond its own `dio wait`; the author gets alerts that earn their place; background work and handoffs are visible.
- **In.** `dio listen` (long-poll on the hub); the opt-in `asyncRewake` hook on `SessionStart` and `Stop` with the pointer-only wake text; optionally the mod with `$.process.spawn` and `$.prompt.submit`, if DX-12 passes; mirroring native `SendMessage` into the store if the mod is built; alert events to `PushNotification`, then ntfy; lease and task reminders at 2 h and 8 h; the 80 % and 90 % thresholds wired to `dio handoff start`; scratchpad stash; background task states with expected durations; `dio wake-family` as a printed, author-triggered sequence; file-inbox export of messages; a self-reporting `-p` worker (DX-25) if wanted.
- **Out.** Any automatic wake without opt-in; two-way approval from the phone; channels as a dependency; cron as a poll unless the author chooses it.
- **Requirements.** DR-13, DR-21, DR-25, DR-26, DR-27, DR-28, DR-29 (export half), DR-51, DR-52, DR-53, DR-87, DR-88, DR-90.
- **Gate.**
  1. With opt-in, a message to an idle seat starts a turn within the long-poll timeout in 10 of 10 trials; without opt-in, 0 of 10.
  2. The wake text is under 300 characters and contains no message or task body.
  3. A `lease-expired` or `task-stale` event produces exactly one notification.
  4. A seat crossing 80 % gets one warning and the handoff suggestion.
  5. `dio tasks` shows a deliberately stalled background task as `stalled` within its expected duration plus grace.
- **Dependencies.** 0.1 done; DX-11 passed; DX-12 for the mod option.
- **Size.** 3 to 5 seat-days.

## Cycle 0.3: Gemini via Antigravity

- **Goal.** A Gemini agent in Antigravity receives and sends through Diogenes, takes tasks through the same path, holds leases, and keeps the file inbox as fallback, with no relay by the author.
- **In.** `agy` installed; the `mcp_config.json` entry (`command` for stdio, `serverUrl` for Streamable HTTP, which the MCP server gains here); the `PreInvocation` hook returning `injectSteps` with the pointer; the `PreToolUse` guard; hook configuration from a file; `mcp(diogenes/*)` pre-approved; the file-inbox projection kept in sync both ways; `AGENTS.md` with the protocol notice and the `CLAUDE.md` shim if needed; the `unverified until reproduced` flag on Gemini-token writes; a sidecar experiment for idle wake, not relied on.
- **Out.** The supervisor-around-`agy -p` pattern unless DQ-11 chooses it; Gemini CLI.
- **Requirements.** DR-29 (ingest half), DR-78, DR-94, DR-97.
- **Gate.**
  1. A scripted exchange of 5 messages each way between a Claude seat and an Antigravity agent, each acknowledged, with the author relaying nothing.
  2. One task claimed, reported and verified through the Gemini adapter.
  3. A Gemini write carries the flag; a Claude verification row clears it.
  4. With the hub stopped, a file written to the Gemini inbox is ingested within 5 s of the hub's return.
  5. The hook's crash behaviour is measured: a deliberate non-zero exit blocks the tool call (fail closed), and the hub-outage path does not.
- **Dependencies.** 0.1 done; DX-22 passed (injection into the model, MCP reach, hook env); DX-19 for the shim.
- **Size.** 3 to 5 seat-days, plus the author's time to install and configure `agy`.

## Cycle 0.4: research cache and shared memory

- **Goal.** A lookup answers "stored, fresh, here" before any fetch; shared memory in org, project and team scopes works across both accounts and both harnesses.
- **In.** The research schema with sources, verifications and FTS5; three-valued `lookup`; quarantine and the different-verifier rule; TTLs by category; revalidation with validators; `dio research` and the MCP tools; memory scopes with compare-and-set; export and import of Claude auto-memory directories between accounts, unless DQ-27 chose a shared directory; backfill of the existing `meta/research/` digests across the Nitpick repositories, with their UNVERIFIED marks kept.
- **Out.** Vectors; a graph store; the `/memories` shim.
- **Requirements.** DR-63 to DR-73.
- **Gate.**
  1. 20 real questions: second lookups return `hit` with no fetch; a 91-day-old security entry returns `stale` with validators.
  2. `put` by identity A then `verify` by A is refused; by B it is accepted.
  3. Two memory writers on the same base version: the second is refused.
  4. The lookup log records every miss, for the vectors decision later.
- **Dependencies.** 0.1 done; FTS5 measured (M4); DQ-13 answered for TTLs and verifiers.
- **Size.** 3 to 4 seat-days.

## Cycle 0.5: boards, claims and write scopes

- **Goal.** Work units, claims with declared scopes, and proposals replace the hand-written board rows, with one writer per board and a recovery view for stale claims.
- **In.** Board rows with `blocked`, `done`, `in flight`, `blocked-by`; atomic claims with scope globs and intersection refusal; stale detection against presence; proposals landed by the writer; verification records before release; the Agent Mail style pre-commit guard as an option; a `BOARD.md` projection so the human-readable board stays readable.
- **Out.** Replacing the workbench's `BOARD.md` wholesale; task dependency graphs beyond `blocked-by`.
- **Requirements.** DR-37, DR-38, DR-40, DR-44, DR-46, DR-47.
- **Gate.**
  1. Two claims with overlapping globs: the second is refused with the overlap named.
  2. Kill a claimed agent; `dio claims` reads `stale` within the grace and the recovery view names it.
  3. A release without a verification row is refused.
- **Dependencies.** 0.1 done; 0.2 for presence states.
- **Size.** 3 to 4 seat-days.

## Cycle 0.6: the GPT auditor

- **Goal.** A Codex CLI session audits read-only and files structured findings that a Claude seat verifies.
- **In.** Codex installed; the auditor token (read-only, write only to its inbox); stdio MCP entry; `UserPromptSubmit` hook under 2,500 characters; `codex exec --json --output-schema` ingestion into `audit-finding` messages and task reports; a canned audit recipe; the "different perspective" policy from DQ-20.
- **Out.** The Responses API hosted MCP tool (needs a public URL); `app-server` wrappers; A2A.
- **Requirements.** DR-79, DR-95.
- **Gate.**
  1. A write by the auditor token outside its inbox is refused with a literal path in the test.
  2. One canned audit runs end to end as a task and its findings appear as quarantined records with provenance.
  3. The Codex sandbox reach result is recorded (shell, HTTP MCP, stdio MCP), and the adapter uses the first that works.
- **Dependencies.** 0.1 done; DX-23 passed; DQ-12 answered.
- **Size.** 2 to 4 seat-days.

## Cycle 0.7: devTeam and attenuated credentials

- **Goal.** devTeam supervisors and workers use Diogenes for claims, scoped writes, progress and locks, each worker with a credential narrower than its supervisor's.
- **In.** Attenuated tokens (the scheme from DQ-9); scope enforcement with the refused-write proof in the test suite; per-worker progress and expected durations; the charter and task graph read from Diogenes facts; environment-event records (earlyoom kills); per-agent token and wall-time ledger.
- **Out.** Changing devTeam's protocol beyond what it needs to call `dio`.
- **Requirements.** DR-54, DR-58, DR-61, DR-62, DR-75, DR-76, DR-89.
- **Gate.**
  1. A worker's write outside its scope is refused and recorded; the proof command passes.
  2. A supervisor sees each worker as `live`, `done` or `stalled`.
  3. A killed worker (exit 137) is recorded as an environment event, not a result.
- **Dependencies.** 0.5 done; the devTeam plugin updated to call `dio`.
- **Size.** 4 to 6 seat-days.

## Cycle 0.8: a second machine

- **Goal.** The hub serves a VPS or a second workstation without changing what agents call.
- **In.** TLS on the hub with client tokens; Postgres as an alternative store behind the same hub, with per-team roles and RLS; a migration path from the SQLite file; replication or a scheduled export; a remote Claude or Gemini worker as the first client.
- **Out.** Multi-hub federation; NATS unless fan-out is needed.
- **Gate.** Every 0.0 to 0.2 gate test passes against the remote hub; `dio audit verify` passes end to end.
- **Dependencies.** 0.1 done; the VPS; the policy answer on remote use of subscription seats, if any applies.
- **Size.** 4 to 6 seat-days.

## Order and what can move

- Day zero → 0.0 → 0.1 → 0.2 is fixed. 0.3 (Gemini) and 0.4 (research) can swap, and 0.4 can start after 0.1 if Gemini is delayed. 0.5 needs 0.2. 0.6 and 0.7 need 0.5 only loosely and can start after 0.1 if the author wants the auditor earlier. 0.8 is last.
- If DX-1 fails across the sandbox boundary, a minimal spool-ingesting hub moves into 0.0 and 0.0 grows by about two seat-days; the socket transport still waits for 0.1.
- If DX-13 shows a short lifetime cap on background commands, `dio wait` re-arms itself inside the cap and the gate's "10 of 10" is measured against the re-armed loop; if the cap is too short to be useful, the day-zero doorbell (DX-4) or the author's hand remains until 0.2.
- If DX-22 shows Antigravity hooks cannot feed the model, 0.3 falls back to MCP polling plus the file projection, which still removes the hand relay for sends and keeps it for receipt.
