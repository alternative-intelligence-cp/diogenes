<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-r8-requirements-from-practice-2026-10-10.md: a read-only API-credits job (claude-sonnet-5-5, 64/200 turns, $0.7010 by the CLI (the bill is about two-thirds)). Its prompt is prompts/dio-r8-requirements-from-practice-2026-10-10.md. -->

# What Diogenes must do, from the author's actual practice

Job: dio-r8-requirements-from-practice-2026-10-10 · Date: 2026-10-10 · Model: Sonnet 5.5 · Tools: Read, Grep, Glob only (no shell, no web)

**Limits:**
- `BOARD.md` and `RECORD.md` are over 1 MB each, so I searched them rather than read them. I read the board's lines 1–60 and 360–470, `RECORD.md` 7703–7742 and 11780–11804, and the grep hits in between. Other entries could contain pains I did not find.
- I only grepped these files and did not read them whole: the `skills/check/` skill, `README.md`, the worker skill, the devTeam README, the devTeam skills and agents, and all but three of the 23 Gemini inbox files.
- I read the `orchestrate` skill only at lines 30–80 and 130–180.
- `CLAUDE.md` has no hits for "nonce", "authenticat" or "SendMessage". The authentication-by-content practice is cited from the context file, the handoff memory and `RECORD.md:7709`.
- "Subagents cannot receive cross-session messages" is the prompt's premise. I found no source stating it. The one related fact I found is at R-9 below.
- Memory files carry no line numbers, so I cite them by name and the line where the quoted text sits.
- Nothing was run or measured. Every behaviour of `SendMessage`, hooks and Claude Code is as the sources describe it.
- Every quotation below was checked against the file that holds it.

---

## 1. The pains, with evidence

**P-1. The author is the relay.**
- The Claude↔Gemini channel is a file inbox. The author tells Gemini to check its inbox and tells Claude when Gemini has written (memory `gemini-file-inbox-channel`, line 17).
- His own `diogenes-idea` memory calls this "the file inbox's weak point" (line 25).
- Across 23 files in `META/NITPICK/messages/`, a 2026-10-02 message asks Gemini to say "when you are at a clean point", and "Randy restarts the machine once all work in every session is finished" (`gemini-inbox/2026-10-02T1944-…:55`). Clean-point and restart timing therefore ride on the author as well.
- He does not want to be the relay between his own sessions (memory `ask-peer-sessions-directly`, lines 19–23).
- `run-live-tests-in-session` records that shuttling work between sessions "might be error prone" (line 15) and that a vague instruction made him restart a terminal, which killed the writing session (lines 32–55).

**P-2. Messages are lost, or delivery is unconfirmed.**
- `nitpick-compiler_37` "LOGS this workbench's messages WITHOUT replying" at the author's word, so for delivery confirmation "ask the author" (`BOARD.md:17`, the handoff block's compiler bullet).
- `RECORD.md:11787` gives the cause: "He expects it to go on logging whether or not it replies" and `_37` "took it literally".
- Compiler seats were told the new seat's name and "none acknowledged" (`RECORD.md:8263`).
- A rotation notice reached the library listener with none sent. `_s13` had compacted once or twice before a clean handoff (memory `session-handoff-brief-the-successor`, lines 222–226).

**P-3. A lock built from a markdown line fails in many ways.** The board's own hazard list:
- (1) The guard permits any session while the line reads `none`, so its silence is not proof the lock is free (`RECORD.md:7709`).
- (2) `CLAUDE_SESSION_ID` is empty in a Bash tool call, so the marker command writes a 0-byte file (`RECORD.md:7709`).
- (3) "A free lock is not the same as a clean tree": the outgoing session nearly answered from memory and found an uncommitted deletion it had not made (`RECORD.md:7709`).
- (4) A peer nobody mentioned appears, and one message settles who it is (`RECORD.md:7709`).
- (5) "Taking the lock is not done until it is pushed." Local `HEAD` showed the lock held while `origin/main` advertised `none` (`RECORD.md:7709`).
- (6) The sweep that clears the lock counted seven trees when there were eight (`RECORD.md:7709`).
- (7) The lock is a mutex over one shared checkout, which was observed passively by an idle session (`BOARD.md:377`).
- (13) A release announced by message while the token and marker still named the old holder (`BOARD.md:463`).
- A devTeam finding from the same family: the writer lock used a substring test, and `me` inside `names` matched (`DESIGN.md:811–813`).

**P-4. Compaction and rotation lose conventions.**
- "A session that compacts ONCE is 'a bit iffy'. … MORE THAN ONCE is 'pretty much a guarantee …' … 'What you put in is probably not what you will get out.'" (memory `session-handoff-brief-the-successor`, lines 217–221).
- A convention that was merely practised was lost at the first handoff. A protocol handed over as a quoted value with a procedure survived three (same memory, lines 177–182).
- The memory's own conclusion: "every convention and every check's reference value must live in a tracked document, never only in a session's context" (lines 237–240).

**P-5. Identity confusion.**
- A session was renamed (`claud-` → `claude-`) while a board note tracked the old name. The note "became a confident, load-bearing falsehood" (memory `session-naming-convention`, lines 27–47).
- A parked successor was skipped (`_s8` → `_s10`), and the author renamed `_s9` forward (same memory, lines 106–119).
- A closed spare returned under the same name with a new `ListAgents` ref, and two seats recorded it as an anomaly (same memory, lines 170–184).
- After update restarts, the ref changed while the session id and name stayed (memory `restarts-are-by-hand-for-now`, line 15).
- `nitpick-posix` resolves to three directories, and two report an identical `origin` (`BOARD.md:378–394`).
- Session ids cannot be had from the environment. They come from the transcript path, a scratchpad path and `~/.claude/context/<id>.json`, cross-checked by a nonce (`BOARD.md:20`).

**P-6. A silent peer may be paused or dead, and the two look the same.**
- "Absence of a signal is not a signal" (memory `silent-peer-may-be-paused-not-gone`, line 47).
- A quota-paused seat returns under the same name with a cold cache. A power cut kills one outright (same memory, lines 11–29).
- A seat that "went quiet" is read as done. The closing handoff needs two signals, and silence counts as one (memory `session-handoff-brief-the-successor`, lines 124–135).

**P-7. Seats that only log, and context pollution.**
- The author keeps a spent predecessor as a logging sink so incidental information never lands in the working seat (memory `dont-pollute-the-working-seat`, lines 11–22).
- "Short-lived information should die with the seat that generated it, and only durable information should travel upward." (same memory, lines 40–42).
- The same preference appears in the context file and in the board's compiler-seat bullet (`BOARD.md:17`).

**P-8. Meters and context read by hand, or only through local files.**
- `usage-latest.json` holds only `five_hour` and `seven_day`. Fable's meter and cloud credits are not in it (memory `session-handoff-brief-the-successor`, lines 282–285).
- The Fable share is asked of the author and then computed by hand: "95 − the meter − 0.5 × (100 − Fable %)" (`BOARD.md:28`; memory `flag-the-weekly-burn-rate`, lines 13–14).
- The API-credit balance is read from the Console page. The CLI's figure overstates it by about a third (`.internal/credits/README.md:36–47`).
- A worker never receives the context warning, because subagent calls carry `agent_id` (memory `session-handoff-brief-the-successor`, line 276).
- The author has ADHD and wants tasks externalised: "any way i can externalize and automate a task is very helpful as it frees up the limited working memory for other more useful things" (same memory, lines 262–264).

**P-9. Background work is invisible.**
- "A completed task and a stalled one present identically" (memory `name-the-live-background-task`, lines 17–19). Partial progress "is not visible" (lines 34–38).
- devTeam: "a supervisor doing its job is indistinguishable from a hung one" (`DESIGN.md:862–864`).
- A subagent belongs to the session that spawned it and "dies with it" (memory `session-handoff-brief-the-successor`, lines 39–42).
- After a restart, every claim is stale, because `ListAgents` shows only the current session's agents (`orchestrate/SKILL.md:162–164`).

**P-10. Waking is manual.**
- "i should probably start everything manually until i have an actual system for doing the whole thing in place" (memory `restarts-are-by-hand-for-now`, line 13).
- He must wake the seat, its successor and the compiler family so "everyone can communicate".
- Claude Code updates force repeated restarts (same memory, line 15).

**P-11. Agent self-reports are unreliable, so every claim is re-measured.**
- Gemini's files "were consistently more accurate than its messages". Its messages invented a figure, reversed a result, called partial work complete, and one run overwrote the whole baseline (memory `gemini-file-inbox-channel`, lines 33–41; `gemini-inbox/2026-10-02T1944-…:13`).
- Gemini's "committed" was wrong (`gemini-inbox/2026-10-03T1655-…:19`).
- A round finished by a different model "is where half-done edits hide" (memory `gemini-file-inbox-channel`, line 55).
- The author's own recollections are claims to check (memory `verify-even-the-authors-own-claims`, lines 29–36).
- A digest checked against a stale build output gives a "confident FALSE NEGATIVE" (`BOARD.md:437–454`, hazard 11).

**P-12. Research is re-fetched, and a URL written into a brief was a premise that turned out wrong.**
- The context file says "the same facts get looked up repeatedly across sessions and repositories".
- A URL in a dispatch was 404 (`RECORD.md:8613`).

**P-13. Account and plan constraints.**
- Cross-account `SendMessage` is untested (context file; memory `subscription-beats-api-for-randy`, lines 90–92).
- Hooks, sandbox, permissions, plugin and memory do not carry across `CLAUDE_CONFIG_DIR`s (same memory, lines 25–27 and 44–50).
- The author keeps projects apart on purpose: "not doing so is a guaranteed clusterfuck" (memory `library-sessions-write-scope`, lines 91–93).
- The terms question about handing work across accounts is still open (memory `subscription-beats-api-for-randy`, lines 94–101).

**P-14. Environment events masquerade as results.** A kill by earlyoom (exit 143 or 137) is an environment event, not a defect (`BOARD.md:463`, hazard 12).

---

## 2. Requirements

P0 = needed when the second Claude account arrives. P1 = Gemini via Antigravity. P2 = a GPT auditor. P3 = devTeam and later.

### Messaging

- **R-1 (P0).** A send to a peer must write a durable record before any delivery attempt, so a message is never lost with the receiver's context. Motivation: P-2, P-4; the inbox convention, with "never edited once sent" (memory `gemini-file-inbox-channel`, lines 19–22).
- **R-2 (P0).** The receiver must be able to confirm receipt with a one-call acknowledgement that the sender can query. A paused or logging-only seat is marked "delivered, not acknowledged" rather than silently assumed read. Motivation: `BOARD.md:17`; `RECORD.md:8263`, `RECORD.md:11787`.
- **R-3 (P0).** Delivery to a Claude Code session must work with no hook support beyond one of UserPromptSubmit, PostToolUse or Stop, by injecting unread rows as context. Polling must serve harnesses with no hooks. Motivation: the author's request; the 2026-10-08 sketch (memory `diogenes-idea`, lines 29–35).
- **R-4 (P0).** The messaging layer must state that a hook runs at a session's next turn or tool call. It must not imply it can wake an idle session. Motivation: memory `diogenes-idea`, line 31, "A hook can't be fired by the database itself".
- **R-5 (P0).** Cross-account delivery must work with no `SendMessage` and no shared `CLAUDE_CONFIG_DIR`. Motivation: the context file; memory `subscription-beats-api-for-randy`, line 92 ("with a file inbox if it does not").
- **R-6 (P0).** A message from another agent must be delivered wrapped and labelled as data, with the sender's identity and the authentication it carries. It must never be delivered as an instruction. Motivation: the context file's discipline list; the existing `<cross-session-message from=...>` wrapper.
- **R-7 (P0).** Every message must be attributable and carry an authentication field the receiver can check against content it already holds, for example digests against a prior baseline or a nonce in one transcript. Diogenes must not substitute a sender-asserted identity for that check. Motivation: the context file; `RECORD.md:7709` ("confirmed BY CONTENT"); `RECORD.md:7729–7741` (`tools/ladder.py`).
- **R-8 (P1).** A reply must name the message it answers, and a message must be immutable. A correction is a new message. Motivation: memory `gemini-file-inbox-channel`, lines 19–22; `gemini-inbox/2026-10-02T1944-…:1` ("Answers: …").
- **R-9 (P0).** A message addressed to a subagent or a background task must route to its spawning seat, or be refused with an explicit "not reachable" answer. I could not confirm that subagents cannot receive cross-session messages. The only related fact I found is that a spawning session resumes its own agent with `SendMessage` to the agent's id (`orchestrate/SKILL.md:166–173`). Motivation: the prompt; P-9.
- **R-10 (P0).** The sender must be able to say a message is `no-reply-needed`, `reply-expected` or `ack-only`, and the system must track which. Motivation: `RECORD.md:8263` ("each marked 'no reply needed'").
- **R-11 (P0).** A routing rule must let a message go to a role address such as `libs-seat` or `compiler-seat`, not only to a numbered seat. Motivation: P-5; `BOARD.md:17` ("the libraries' address is now `_18`").
- **R-12 (P0).** A send must be able to target a logging sink instead of a working seat, with a per-message flag "do not interrupt". Motivation: P-7; memory `dont-pollute-the-working-seat`.
- **R-13 (P2).** Messages must be exportable as one-Markdown-file-per-message, named `YYYY-MM-DDTHHMM-<sender>-<subject>.md`, so a harness that can only read files participates unchanged. Motivation: memory `gemini-file-inbox-channel`; the author's request ("hooks plus some way to poll").

### Presence and roster

- **R-14 (P0).** Presence must record, for each seat, a stable role identity, a session id, a current name, a `ListAgents` ref where one exists, and a state of `live`, `parked-on-purpose`, `quota-paused` or `gone`. Motivation: P-5, P-6; memory `silent-peer-may-be-paused-not-gone`.
- **R-15 (P0).** Presence must distinguish "no signal" from "gone". A status of `gone` must need positive evidence, such as a closed-by-owner or heartbeat-timeout record. Silence alone may only produce `unknown`. Motivation: memory `silent-peer-may-be-paused-not-gone`, line 47.
- **R-16 (P0).** A rename or ref change must be recorded as an event linking old and new identity, and must not break routing by role. Motivation: P-5; memory `session-naming-convention`, lines 125–128 and 170–184.
- **R-17 (P0).** An identity claim must be checkable by content. A seat proves it is session X by showing a nonce that appears only in X's transcript. Diogenes must provide a nonce-issue and nonce-check call. Motivation: `BOARD.md:20`; `RECORD.md:7709`.
- **R-18 (P0).** Identity must be derivable without `CLAUDE_SESSION_ID`, which is empty in a Bash tool call. The registration call must accept an id supplied by the seat, and must record how it was obtained. Motivation: `RECORD.md:7709`, hazard 2.
- **R-19 (P1).** A paused seat must be able to register its own wake condition, such as "after reset 2026-10-14 20:00", so another seat or the author can see "resumes at T". Motivation: memory `restarts-are-by-hand-for-now`; `BOARD.md:14`.
- **R-20 (P0).** The roster must be displayable as the rolling pool: working seat, designated successor, spare, and logging sink. Motivation: memory `session-naming-convention`, lines 78–95; memory `dont-pollute-the-working-seat`.

### Locks and claims

- **R-21 (P0).** A lock must be a single record with exactly one holder, acquired by an atomic compare-and-set, and releasable only by the holder or by recorded takeover. Motivation: P-3; `WORKSTREAMS.md:181–188` (W-16).
- **R-22 (P0).** A release must be one operation that changes the token and the marker together. A message announcing a release must be generated from that operation, never written by hand. Motivation: `BOARD.md:463`, hazard 13.
- **R-23 (P0).** Acquisition must be refused unless the lock reads free on the authoritative store. A local or cached read must not satisfy it. Motivation: `RECORD.md:7709`, hazard 5 ("A peer reading `origin` sees a free lock; a peer reading the local tree sees a held one").
- **R-24 (P0).** An absent lock must be a distinct state from a held one. The state `none` must not permit every session. Motivation: `RECORD.md:7709`, hazard 1.
- **R-25 (P0).** A lock must match by exact id. A substring or prose match must not count. Motivation: `DESIGN.md:811–813`; `orchestrate/SKILL.md:48–51` ("only that token is the lock").
- **R-26 (P0).** The lock check must report the tree state it covers, with dirty and ahead/behind counts for every tree it governs, and print the denominator. The set of trees must be discovered, not listed. Motivation: `RECORD.md:7709`, hazards 3 and 6; `orchestrate/SKILL.md:67–79`.
- **R-27 (P1).** A claim must record the work unit, the agent label, the start time and the model. A claim whose live agent cannot be shown must read "stale" and trigger recovery. Motivation: `WORKSTREAMS.md:199–203` (W-19); `orchestrate/SKILL.md:149–164`.
- **R-28 (P1).** Claims must carry a declared write scope, and a claim whose scope intersects a live claim must be refused before dispatch. Motivation: devTeam `PROTOCOL.md:222–226` (P-12).
- **R-29 (P0).** Locks must be keyed by project and layer, because each project's checkout is a separate mutex. A lock must not be inferred from names that can collide, such as three directories called `nitpick-posix`. Motivation: `BOARD.md:376–394`.
- **R-30 (P3).** A lock's holder, release and takeover history must be queryable as one audit log (devTeam: "a claim is a commit", `PROTOCOL.md:216–220`).

### Boards and state

- **R-31 (P0).** Live state must have one writer per state record. Others submit proposals, and the owner lands them. Motivation: `WORKSTREAMS.md:140–143` (W-8) and `181–188` (W-16).
- **R-32 (P0).** Every fact an agent relies on, such as a convention, a check reference value or a baseline, must be stored as a value with a procedure, in a queryable record. It must not live only in a session's memory. Motivation: P-4; memory `session-handoff-brief-the-successor`, lines 237–240.
- **R-33 (P1).** State records must be append-only where they record an event. A correction is a new record that supersedes the old one. Motivation: `WORKSTREAMS.md:255–275` (W-28).
- **R-34 (P0).** A published count must carry its denominator and exemptions. Motivation: `WORKSTREAMS.md:264–270`.
- **R-35 (P1).** State must expose "blocked, done, in flight, blocked-by" per work unit so a stopped stream stops only itself. Motivation: `WORKSTREAMS.md:219–223` (W-23).
- **R-36 (P2).** Verification before release must be a recorded step in the record, with the verifier's evidence attached. Motivation: `WORKSTREAMS.md:209–212` (W-21).

### Handoffs

- **R-37 (P0).** A handoff must be a structured record, not a free message. It holds the lock state, claims, owed items, state as values, the peer roster, and the commands to re-verify each claim. Motivation: `BOARD.md:17–59`; memory `session-handoff-brief-the-successor`, lines 113–116.
- **R-38 (P0).** The two-signal close must be explicit state: the incoming seat's "done with you" and the outgoing seat's "safe to close", each a distinct recorded event. Silence must not stand in for either. Motivation: memory `session-handoff-brief-the-successor`, lines 124–135.
- **R-39 (P0).** The handoff must tell each peer the new address once, and record who was told and who acknowledged. Motivation: `BOARD.md:53` ("`_17` told `_37`"); `RECORD.md:8263`.
- **R-40 (P0).** The system must warn at the author's thresholds (80 %, 90 %) and make a handoff-before-compaction a first-class action. Motivation: memory `session-handoff-brief-the-successor`, lines 186–195 and 288–303.
- **R-41 (P1).** Anything held only in a session scratchpad must be movable into shared state at handoff. A subagent's in-flight output must be flagged as "dies with the session". Motivation: memory `session-handoff-brief-the-successor`, lines 39–44.
- **R-42 (P1).** After a long silence, a returning peer must be re-authenticated by content, not assumed continuous. Motivation: memory `silent-peer-may-be-paused-not-gone`, lines 33–44.
- **R-43 (P2).** A successor on a quota-exhausted model must be detectable before the handoff. Motivation: memory `session-handoff-brief-the-successor`, lines 160–165.

### Telemetry

- **R-44 (P0).** Diogenes must publish each account's `five_hour`, `seven_day`, model limits and `written_at` age, for any account on the machine, readable by any seat. Motivation: the context file; memory `session-handoff-brief-the-successor`, lines 280–285.
- **R-45 (P0).** Telemetry must carry the Fable share as its own field, so a seat need not ask the author. It must expose the computed room, "95 − the meter − 0.5 × (100 − Fable %)". If the source is missing, the field must say `unknown`, never default. Motivation: P-8; `BOARD.md:28`; memory `flag-the-weekly-burn-rate`.
- **R-46 (P0).** A seat's context percentage must be readable by name for every seat, including a seat on the other account. Motivation: the context file; memory `session-handoff-brief-the-successor`, lines 265–270.
- **R-47 (P1).** Telemetry must record observed burn rate and projected threshold day, so the "rate, projected day, one recommendation" report is generated. Motivation: memory `flag-the-weekly-burn-rate`, lines 17–18.
- **R-48 (P1).** Credit balance must be a stored fact with its source and read time. It must not be derived from CLI figures without the author-measured correction, about two-thirds. Motivation: `.internal/credits/README.md:36–47`; memory `use-api-credits-before-expiry`, lines 19–24.
- **R-49 (P1).** The system must hold a per-account, per-model usage ledger and an expiry calendar for credits, so batches are routed before they lapse. Motivation: memory `use-api-credits-before-expiry`.
- **R-50 (P2).** The system must emit an environment-event record, such as an earlyoom kill, so a kill is not read as a result. Motivation: `BOARD.md:463`, hazard 12.
- **R-51 (P2).** Per-agent tokens and wall time must be logged in a form that can later be set against tenure length. Motivation: memory `session-handoff-brief-the-successor`, lines 322–328.

### Research and memory

- **R-52 (P0).** A lookup must check for a stored digest first, report its date and staleness, and fetch only if stale or missing. Motivation: the author's request; memory `diogenes-idea`, lines 17–22.
- **R-53 (P1).** Each digest must carry a date checked, a primary-source URL and a sensitivity tag. Security-sensitive digests go stale after 90 days, others after six months. Motivation: `WORKSTREAMS.md:228–233` (W-25); devTeam `skills/research/SKILL.md:129–130`.
- **R-54 (P1).** Writing into the research store must be the requester's job, not the researcher's. Motivation: `WORKSTREAMS.md:228–233`; `.internal/credits/README.md:15–17`.
- **R-55 (P1).** A fact must have one home. A second index carrying the answer becomes a stale copy. Motivation: devTeam `skills/research/SKILL.md:26`, citing P-34.
- **R-56 (P2).** Agent memories must be copyable between accounts, because a new `CLAUDE_CONFIG_DIR` loses them. Motivation: memory `subscription-beats-api-for-randy`, lines 44–50.
- **R-57 (P1).** A claim in a stored digest that has no checkable source must be tagged `UNVERIFIED` and must not be treated as fact. Motivation: the context file, rule 3.

### Access and audit

- **R-58 (P0).** Access must be per project and per team, so only the entities that need write access have it, and the whole record remains readable for audit. Motivation: the author's request (layers: organization, project, team); memory `library-sessions-write-scope`.
- **R-59 (P1).** A credential must be least-privilege and usable from inside a sandbox where the shell's writes are allowlisted and egress is proxied. MCP servers and Read/Write/Edit sit outside that shell sandbox. Motivation: the author's request; the context file; devTeam `meta/devteam-sandbox-spec-2026-09-05.md:125`.
- **R-60 (P1).** A subagent's writes must be bounded by a declared scope. A write outside it must be refused, and that refusal must be proven by a deliberate one with a literal path. Motivation: devTeam `PROTOCOL.md:102–104`; `DESIGN.md:855–858`.
- **R-61 (P0).** The audit log must record who sent, read, locked or released what, and when. Motivation: the author's request ("viewable for audits and review"); devTeam `PROTOCOL.md:216–220`.
- **R-62 (P1).** Rows from an agent family with known unreliable self-reports, such as Gemini, must be flagged "unverified until reproduced on the Claude side". Motivation: P-11.
- **R-63 (P2).** The GPT auditor must have read-only access to project state and a write path only into its own inbox. Motivation: the context file; memory `model-routing-by-task-not-price`, lines 147–152.
- **R-64 (P0).** Per-account separation must be explicit: nothing crosses accounts by default, and any route is chosen by the author. Motivation: P-13; memory `subscription-beats-api-for-randy`, lines 94–101.

### Human surfaces

- **R-65 (P0).** Diogenes must show the author, in one place, who is live, what each seat holds, what is awaiting acknowledgement, and the meters. Motivation: P-8, P-10; memory `name-the-live-background-task`.
- **R-66 (P0).** The system must raise an item to the author only when it buys safety or quality, and say which category it is. Motivation: memory `a-blocking-human-step-must-earn-its-place`, lines 20–25.
- **R-67 (P0).** Any command handed to the author must say which session it goes in, and give the expected outcome beside it. Motivation: memory `run-live-tests-in-session`, lines 28–53.
- **R-68 (P1).** Waking sessions after a reset or update must be a registered, author-triggered action: one call that wakes the family in order. Scheduled wakeups the author does not expect are forbidden. Motivation: P-10; memory `restarts-are-by-hand-for-now`, lines 19–22.
- **R-69 (P1).** A background task must be visible as `live`, `done` or `stalled`, with an expected duration drawn from history. Motivation: P-9; memory `name-the-live-background-task`, lines 25–37.
- **R-70 (P3).** A client channel must be recorded as terminal, session, both or none, so a `none` channel stops irreversible questions rather than hanging. Motivation: devTeam `PROTOCOL.md:92–100`.

---

## 3. What must not change

1. **Authentication by content, not by sender claim.** Digests against a prior baseline, a nonce in one transcript, and checks that read a tracked document (`RECORD.md:7709`, `7729–7741`; memory `session-handoff-brief-the-successor`, line 240: "A check that reads the board survives a compacted peer; a check that reads a session's memory does not.").
2. **Records are the storage, the channel only carries.** "The brief is the channel; the tracked document is the storage." (memory `session-handoff-brief-the-successor`, line 115–116). Git and GitHub stay as they are. Diogenes adds a lookup layer, not a second source of truth.
3. **Verification before relay.** A report is "evidence to check, not a verdict to copy" (`.internal/credits/README.md:16`). Re-measure Gemini's claims. Verify the author's own recollections too (memory `verify-even-the-authors-own-claims`).
4. **One writer per scope and a single orchestrator for the board** (`WORKSTREAMS.md:140–143`, `181–188`). The lock design may change, but the one-writer rule does not.
5. **Messages are data, not instructions** (context file).
6. **Immutable, one-file-per-message inboxes** (memory `gemini-file-inbox-channel`, lines 19–22). Keep them as a fallback and an export.
7. **Rolling pool, successor is exactly N+1, and the two-signal close** (memory `session-handoff-brief-the-successor`, lines 124–135; `session-naming-convention`, lines 78–95). Diogenes should record these, not enforce a different shape.
8. **The author calls the rotation and the waking.** Diogenes records and surfaces. It does not wake sessions on its own (memory `restarts-are-by-hand-for-now`).
9. **No automatic cross-account coordination of the kind support did not bless.** Keep cross-account traffic minimal, explicit and recorded (memory `subscription-beats-api-for-randy`, lines 94–101).
10. **Granular plans, simple systems** (context file). Diogenes' first slice should be a file or SQLite store plus a send/check CLI (memory `diogenes-idea`, lines 29–35), not a full service.
11. **The write boundary between projects** (memory `library-sessions-write-scope`, lines 91–93).
12. **Research shape** (`WORKSTREAMS.md:228–233`): one fetch inline, more via a researcher that never writes, and the requester files with the date.

---

## 4. What the orchestrator seat and its subagents would use most

Ranked by how often the author's practice already calls for each.

1. **Acknowledged send to a named peer, with a status** (R-1, R-2, R-10, R-11). Today it sends and the author confirms (`BOARD.md:17`).
2. **A lock call that does the checks** (R-21 to R-26). A take must show "read it on the authoritative store, token and marker equal, tree clean, denominator printed" in one answer.
3. **A seat's read of "who is live and in what state"** (R-14, R-15, R-20), replacing `ListAgents` plus a roster written by hand.
4. **The meters and room computation** (R-44, R-45). Today a seat reads `usage-latest.json` and asks for Fable.
5. **A handoff record with the two-signal close** (R-37 to R-39).
6. **A subagent-facing surface** (R-9, R-12, R-60, R-69).
   - The spawning seat sees each subagent's progress and state. Today progress is invisible until the final report (`DESIGN.md:862–864`; memory `name-the-live-background-task`, lines 34–38).
   - The seat sends a message to a subagent through its id. `orchestrate/SKILL.md:166–173` already resumes a dead one that way.
   - A subagent's scope-bounded write path is proven by a refused write (`DESIGN.md:855–858`).
   - A subagent receives no context warning today (memory `session-handoff-brief-the-successor`, line 276), so context pressure is invisible to it.
   - Whether a cross-session message can reach a subagent at all is the prompt's premise, which I could not confirm.
7. **A research lookup that answers "stored, fresh, here" before any fetch** (R-52, R-53).
8. **A claim and recovery view** (R-27). It answers "for each CLAIMED row, who is alive and what state is the tree" without a `ListAgents` scan (`orchestrate/SKILL.md:149–164`).

---

## What this means for Diogenes

- **Build the record first, delivery second.** Messaging, locks and handoffs all failed where something existed only in a session or a message (P-2, P-3, P-4).
  - Concrete: an append-only store with a CLI and a content-authentication field (R-1, R-7, R-32) before any hook delivery.
  - Hooks and polling (R-3, R-4) read from it.
- **Acknowledgement is the P0 gap.** The documented fix for a logging-only seat is "ask the author" (`BOARD.md:17`). R-2 closes that.
- **The lock needs a store with a compare-and-set, and every hazard maps to a test.**
  - Hazards (1), (2), (5) and (13) become acceptance tests: free means a distinct state, ids come from the seat, reads hit the authoritative store, and release is atomic.
  - A shared file or database with a single-row update does this better than a markdown token.
  - That is an inference from the hazards, not something I measured.
- **Make identity a role plus a content check.** A rename or ref change must not break routing (R-14, R-16 to R-18).
- **Treat the author's attention as a metered resource.** R-65 to R-68 exist to put the manual relay, the by-hand waking and the unspecific command in one place, and to refuse a blocking step that does not buy safety.
- **Cross-account is a design constraint, not a feature.** Everything must work with only a shared store plus a CLI (R-5, R-64), because `SendMessage` across `CLAUDE_CONFIG_DIR`s is untested.

## Open questions

- Does `SendMessage` reach across two `CLAUDE_CONFIG_DIR`s, and can a subagent receive any cross-session message? Only an experiment settles it.
- Do the author's rules permit a delegation path between his personal Max and the Team seat on one project? He is awaiting a written answer (memory `subscription-beats-api-for-randy`, lines 94–101).
- Which store should hold locks and messages first: SQLite, Redis, or an API in front of one of them? The sources do not decide it. I only confirmed the tools exist on the machine (context file).
- Where should audit logs of cross-seat messages live so they survive an account's config directory being replaced? I found no source.
- Does a Gemini or GPT harness expose any hook at all? If not, polling is its only route. Unknown.
- Is the Fable share readable by anything other than the author? The status-line file does not carry it (memory `session-handoff-brief-the-successor`, lines 282–285).
- Which of R-1 to R-70 should be slice one? I would suggest R-1, R-2, R-7, R-14, R-15, R-21 to R-25, R-37 to R-39 and R-44 to R-46, but that is a recommendation for the author, not a finding.

**Outside my question:** `BOARD.md` line 14 is a single line of over 10 KB, with a verbatim history of earlier lock holders appended. That is the same defect as hazard 5 in a different form: the "token" is the first backticked word on a very long line. R-21 and R-25 would remove the need for it.