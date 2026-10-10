# Diogenes: ideas parking lot

Drafted 2026-10-10, revised the same day. The author said "we can get as creative with the plans as we want right now." Each idea is one or two lines: what, why it might matter, where it came from, and **speculative** where it is. Nothing here is planned until it moves to a cycle.

## Delivery and waking

- **Pointer-only wakes.** A wake carries "n unread from X; 1 task reported" and nothing else; bodies come by pull. Keeps messages data and wake text small. [r1 §A.1].
- **The seat's own wait, moved into the plan.** The background `until` loop that was observed to work (firsthand §2) is now `dio wait --for-me` in cycle 0.0 (DR-105), polling `PRAGMA data_version`, which M4 measured. What stays speculative: its lifetime cap (DX-13) and whether a pinned background session keeps it alive (DQ-29).
- **A Diogenes mod pane.** Inbox, roster, tasks and locks tabs inside Claude Code, `$.ui.status` showing "3 unread · 1 task reported · lock: workbench held by `_18`", a `/dio` command to reply. Documented API [r1b §6]; mods are a moving target. **Speculative.**
- **Mirror native `SendMessage` into the store** through a mod's `session.receive` and `session.send`, for audit without changing the fast path [r1b §6].
- **`notify_when_idle` as a handoff aid.** The successor subscribes to the outgoing seat's idle notice instead of asking "are you done". It works only for sessions on this machine [r1b §1]; whether it works across config dirs is untested (DX-4).
- **Reply-expected and task-stale escalation ladder.** A `reply-expected` message with no reply, or a claimed task with no progress, after N hours becomes an alert event; after M, it is shown to the author with the category `quality`. From agent-loom's claim reminders [r6 §2].
- **A sidecar that wakes Gemini** with `agentapi send-message` when its inbox has `reply-expected` mail or a task. Documented command; unattended behaviour unknown; each ping is a quota turn [r2 §2.6]. **Speculative.**
- **OpenCode as a fourth harness** through its HTTP server's `prompt_async`, which is true push [r3 §3]. Nobody asked for it; it is the cheapest push of any harness.
- **The spool as a general trick.** Any sandboxed process on this machine can talk to any host service through a watched directory, since M1 and M3 close every other route. The credits runner, devTeam workers and a future Gemini sandbox could all use the same request-and-reply file format (DR-110).

## Locks and state

- **Fencing tokens in commit messages.** A pre-commit hook writes the lease fence into the commit trailer, so `git log` shows which grant each commit was made under. Borrowed from Agent Mail's pre-commit guard [r6 §2].
- **`dio lock status` prints the hazards it checked.** "free on store: yes; token = marker: yes; trees clean: 7 of 8 (nitpick-posix dirty)". The hazard list becomes the output format.
- **Takeover with a cooling period.** A takeover of an `unknown` holder's lease waits a stated time and sends the old holder an `ack-only` message first, so a quota-paused seat is not overrun. From P-6 in [r8].
- **Beads interop.** Export tasks and claims as Beads issues or read `bd ready` for unblocked work, instead of building a graph tracker [r6 §2]. **Speculative.**
- **Checkout discovery by `origin` hash, not by name.** Three `nitpick-posix` directories become three resources keyed by `sha256(origin url + path)` (R-29).
- **Task specs as a template.** A `meta/tasks/TEMPLATE.md` with sections for scope, branch, acceptance commands and the report shape, so a Team worker on a small model gets the same well-defined shape every time (the author's "well defined tasks").

## Identity and trust

- **A session's signature on every message, from 0.1.** Once a nonce check has passed, the hub records the session as checked; later messages carry `auth: nonce: pass` without the value ever appearing, and a returning peer re-proves with a fresh one (R-42). Honest-session confusion only; not a defence against a hostile same-uid process [c1 C-9].
- **Digest-chained landing notices.** Each landing notice carries the previous notice's hash, so a missed notice is detectable by the receiver. From the compiler seat's six-digest practice.
- **Trust tiers per family.** `claude`, `gemini`, `gpt`, `author` as trust labels in the envelope, with per-family default flags (Gemini writes start `unverified until reproduced`) (R-62).
- **Per-worker macaroons.** A supervisor hands a worker a token with its scope caveats added, offline, and revokes by caveat expiry. [r5 §1]. **Speculative** until 0.7.
- **The other account witnesses the audit head.** Each account's hook writes the chain head under its own config dir once an hour; a mismatch is an alert. [r5 §5].

## Meters and attention

- **Room as a first-class number.** `dio meters` prints the room formula's inputs and result, and refuses to print a number when one input is missing. The author stops being asked (R-45).
- **The Team estimate that corrects itself.** Each Team session's cost totals are kept; when a measured Team meter arrives (DX-26) the stored estimates are compared with it and the method's error is recorded as a fact, so the next estimate on any account without `rate_limits` is calibrated. **Speculative.**
- **A burn-rate forecast line in `dio status`:** "7-day meter 61 %, 2.1 %/h, hits 95 % Tuesday 14:00; recommendation: route verification to the Team seat." (R-47).
- **Credits expiry calendar.** A month-end reminder that credits lapse, with the measured two-thirds correction, so batches are queued in time (R-49).
- **A "do not disturb" roster state** the author sets for himself, so alerts queue and are shown as one digest when it ends. **Speculative.**
- **Expected durations from history.** Every task and background job records its wall time; the next one of the same kind gets an expectation and a `stalled` threshold from it (R-69).

## Research and memory

- **The lookup log as the vectors decision.** Every `miss` is logged with the question; when paraphrase misses pile up, add a local embedding model, not before [r7 §2].
- **`revalidate` as a nightly cron on the hub,** not in any session: conditional fetches with `If-None-Match`, and a `stale` flag when the hash changes, so seats never re-fetch what did not change [r7 §3].
- **Backfill the Nitpick repositories' `meta/research/` digests** into the cache with their dates and UNVERIFIED marks, so the same facts stop being looked up (P-12).
- **A `/memories` shim** so Claude agents reach Diogenes memory through the memory tool they already know, with path validation [r7 §6]. **Speculative.**
- **Memory export at rotation.** A seat's auto-memory directory is snapshotted into Diogenes at handoff, so a successor on the other account inherits it (R-56); or the two accounts simply share one directory (DQ-27).
- **Write-time lint for injected instructions** in research entries, as a backstop behind quarantine, never as the gate [r7 §5].

## Human surfaces

- **`dio status` as the one screen:** live seats and workers, open tasks by state, held leases, owed replies, meters and room per account, and the last alert, under 40 lines (R-65).
- **Commands for the author always carry their session.** The CLI prints "run in `nitpick-libs_18`:" before any command it hands him, with the expected outcome (R-67).
- **A handoff viewer** that shows the brief, both signals and the acks, and a red line for anything owed.
- **ntfy with priorities** for `needs-human` only; everything else stays in `dio status` [r6 §3]. Two-way approval from the phone deliberately out.
- **A `BOARD.md` projection** written by the hub, so the human-readable board stays readable and nobody edits it by hand.
- **Family wake as a printed checklist:** `dio wake-family nitpick` prints the ordered commands, each with its terminal and expected first line, and the author runs them (R-68).

## Further out

- **A2A agent card for the hub,** so a networked auditor could find it; vocabulary now, transport later [r3 §4].
- **Postgres with RLS per team** behind the same hub when a second machine arrives [r4 §2].
- **Redis Streams as the hub's long-poll transport** if its own long-poll proves costly; 7.0.15 has what is needed, and M5 measured the consumer-group cycle working [r4 §1]. Only the hub would talk to it (M1, M3).
- **Jules as a contained worker** polled through its REST API for PR-shaped tasks, as one more executor kind on the task path [r2 §3]. **Speculative.**
- **A credits-runner job that files its own result** into the research cache as `quarantined`, with the requester verifying (R-54).
- **Content-addressed artifacts** (build outputs, digests) stored by hash so a landing notice or a task report can point at them instead of carrying them.
