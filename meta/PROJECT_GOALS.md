# Diogenes: project goals

Drafted 2026-10-10 from the round-1 research digests ([r1] to [r8], [r1b]) and the author's request of the same day. Revised the same day against the independent critique ([c1]), the measurements M1–M5 in the first-hand file, and the author's follow-up of about 13:00, which makes **delegation across accounts** the first priority. This is a planning draft for the author's review. Where it recommends, it says why; where a choice is his, it points at `OPEN_QUESTIONS.md`.

## 1. What Diogenes is

Diogenes is a **hub** that lets AI coding agents, running on different models, in different harnesses and under different accounts, **work together on the author's projects safely and with less of his attention**.

In the author's own words (2026-10-10): "a hub where we can facilitate work between various models running in various different harnesses in any way we can while keeping things safe and manageable."

It does five things:

| Job | What it means today | What it replaces |
|---|---|---|
| **Carry tasks** | A task is posted by the orchestrator, claimed by an executor (the acknowledgement), worked, reported, and verified by someone other than the reporter. One path for every kind of executor: this account's subagents, Team-seat sessions, API-credit jobs, later Gemini and GPT | Briefs typed into a session, reports read in a session's context, and the author carrying both between accounts |
| **Carry messages** | A send is stored, delivered, and acknowledged, between any two agents on the machine, across accounts and harnesses | `SendMessage` (same account only, no durable record) and file inboxes that the author relays by hand |
| **Hold shared state** | Who is live, who holds which lock, what is claimed, what each account's meters and room say | A `BOARD.md` lock line, a roster written by hand, `usage-latest.json` read per seat |
| **Record handoffs and audit** | Seat rotation as structured records; an append-only log of who did what | Briefs that live only in a session's context |
| **Share knowledge** | A research cache that answers "stored, fresh, here" before any fetch; shared memory in layers | The same facts fetched again in every session and repository |

It is layered the way the author described: an **organization** layer (rules and expectations for every project), a **project** layer (boards, locks, memory, research for one project), and **teams** inside a project (so only the entities that need write access have it, while everything stays readable for audit).

## 2. What Diogenes is not

- **Not a second source of truth for code or plans.** Git and GitHub keep that role. Diogenes is a lookup and coordination layer beside them. "The brief is the channel; the tracked document is the storage" stays the rule [r8 §3.2]. A task's specification is a tracked file; the task record points at it.
- **Not an orchestrator.** It does not decide what to dispatch or to whom, does not choose models, and does not wake sessions on its own. It carries tasks and their state between the orchestrator and any executor, and records the result. The author calls rotations and wakes seats [r8 §3.8]; a seat may start its own wait on mail addressed to it (DQ-7). devTeam and the orchestrate skill stay the orchestrators; Diogenes gives them a shared store and the task path.
  - **Amended 2026-10-15 by cycle 0.0-min's decision 2, approved by the author:** two wakes are permitted in 0.0, the seat's own `dio watch` and a native message from a peer session that `dio who` lists; Diogenes itself still wakes nothing (`roadmap/0.0/MIN.md`).
- **Not a harness.** It does not run models. Ruflo and Gas Town are harnesses and are not adopted [r6 §5].
- **Not a judge.** It records claims and verifications. The "honest man" rule is that every claim is verified before it is relayed; Diogenes makes that cheap to record, not optional. A task's `verified` state needs a verifier who is not the reporter.
- **Not an identity authority in v0.** Both Claude accounts run as the same Linux user, so no kernel fact tells them apart [r5 §1]. Identity is a server-issued token from cycle 0.1, and in 0.0 a recorded registration plus the socket path the harness exports (DR-107). The nonce check (a nonce in one transcript) guards against confusion between honest sessions; it does not stop a hostile same-uid process [c1 C-9].

## 3. The problem it solves

The author's practice, measured in [r8], fails in fourteen recorded ways. The ones that matter most:

- **The author is the relay** (P-1). Every Claude-to-Gemini alert, every "check your inbox", and every delivery confirmation to a logging-only seat goes through him.
- **Delivation has no path** (the follow-up). The Max-account orchestrator must hand a self-contained task to a Team-seat session or a credits job, know it was received, have it worked, get a report it verifies, and see each account's room before routing. Today none of that exists across accounts.
- **Delivery is unconfirmed** (P-2). A `SendMessage` result means queued, not read [r1b §1, changelog 2.1.271]. Compiler seats were told a new address and none acknowledged.
- **The lock is a markdown line** (P-3). Thirteen recorded take hazards: `none` permits anyone, a lock held locally but not pushed, a release announced while the token still named the old holder.
- **Context is lost at compaction and rotation** (P-4). Conventions that lived only in a session died at the first handoff.
- **Identity is confused** (P-5, P-6). Renames, skipped successors, refs that change at restart, and a silent peer that may be paused or dead.
- **Meters are read by hand** (P-8). The Fable share is asked of the author and computed in the seat's head. The Team seat's meters have no documented source at all [r1b disposition 14].
- **The second account is coming** (P-13). Nothing in Claude Code's hooks, sandbox, plugins or memory crosses `CLAUDE_CONFIG_DIR`, and cross-account messaging is untested.

## 4. Who uses it

| User | How | What they call most |
|---|---|---|
| **The orchestrator seat** (a long-lived Claude Code session on the Max account, for example `nitpick-libs_18`) | Through hooks that register it and inject unread and reported counts, through `dio` from Bash (file transport), and through MCP tools from 0.1 | task post and verify, acknowledged send, lock take with the checks, who is live, meters and room per account |
| **Its subagents** (planners, workers, verifiers) | They have **no inbox of their own**: a subagent's send goes out under its parent's address and replies land in the parent's conversation (observed 2026-10-10, firsthand §1). Their `dio` calls are attributed to the seat; `agent_id` is recorded only where a hook sees it [r1b §3] | task claim and report, research lookup, scope-bounded writes |
| **Team-seat worker sessions** (Claude Code on the Team account, Opus or smaller, rotated often) | Same adapter installed under the Team config dir; a seat-started `dio wait` while idle; the task record is their only state, so a rotation needs no handoff | task list, claim, progress, report; inbox and ack |
| **API-credit jobs** (`claude -p` through the credits runner) | The runner, not the model, claims the task at start and reports at exit; no hooks or MCP needed | claim, report |
| **Seats that rotate** (`<project>_<N>` → `<project>_<N+1>`) | A stable **role** is moved to the successor by a recorded assignment at handoff, never by registration | handoff brief, two-signal close, nonce check by content (0.1) |
| **Gemini in Antigravity** (P1) | MCP tools plus a `PreInvocation` hook, with the file inbox as fallback [r2 §5] | inbox, send, lock status, research lookup, task claim and report |
| **A GPT auditor** (P2) | Codex CLI with a read-only token; audits ingested as structured JSON [r3 §What this means, 8] | read state, write only its own findings |
| **devTeam supervisors and workers** (P3) | Attenuated tokens with declared write scopes [r5 §Growing] | claims, scoped writes, progress |
| **The author** | One status surface, alerts that earn their place, commands that name their session; his own sends come from a terminal identity registered once | `dio status`, the task board, the meters |

## 5. Goals by horizon

Priorities follow the author's words: the Team seat is hoped for by the weekly reset on Wednesday 2026-10-14 20:00 and is priority one; Gemini via Antigravity is intermediate; a GPT model is later.

### P0: delegation from the Max orchestrator to the Team seat and to credits

**Goal.** The orchestrator on the Max account hands self-contained tasks to sessions on the Team seat and to API-credit jobs through Diogenes, knows each was received, gets a report back that it verifies, and sees each account's remaining room before routing, with no relay by the author and no dependence on `SendMessage` crossing accounts.

**Amended 2026-10-15 by cycle 0.0-min's decision 1(c), approved by the author:** "no dependence on `SendMessage` crossing accounts" has the inbox as its proof. `SendMessage` is the default path; the file inbox is the required fallback, proved in M4 as one exchange each way with `SendMessage` denied on both sides (`roadmap/0.0/MIN.md`).

**Why the shape is this.** The author keeps Fable's normal half of the Max account for the compiler; the other half is reserved for the library orchestrator. The Team seat is, by his estimate, roughly a quarter of a Max's usage, so it runs Opus or smaller on well-defined tasks and rotates often. Delegation with good tooling is what "stretches that 50 % out a ways" (the follow-up).

**Success criteria (measured):**

1. **The task path.** 10 tasks posted by the Max orchestrator, 5 worked by a Team-seat session and 5 by credits jobs, each claimed (the acknowledgement), reported, and verified by an identity other than the reporter, with zero hand relays.
2. **Messages.** A message sent from a seat on account A is stored, injected as an unread notice into a seat on account B at its next turn, and acknowledged by B with one call, with the sender able to query the state. Target: 10 of 10 messages, both directions, in a scripted test.
3. **Waiting without the author.** An idle Team worker that has started `dio wait` picks up a posted task within the wait's poll interval, and an idle orchestrator that has started one picks up a report the same way, in 10 of 10 trials; a seat with no `dio wait` is never woken.
   - **Amended 2026-10-15 by cycle 0.0-min's decision 2, approved by the author:** 5 of 5 file wakes (M4) and 5 of 5 native wakes (M2); "never woken" narrows to "never by a file without a watch". The full count is 0.1 (`roadmap/0.0/MIN.md`).
4. **The lock.** The workbench lock is taken, held and released only through Diogenes, and the four acceptance tests derived from hazards 1, 2, 5 and 13 pass [r8 §What this means].
5. **Presence.** `dio who` shows both accounts' sessions with role, name, session id, account and state, shows `live-idle` for a session whose process is alive but silent, and `unknown` only when the process check is impossible.
6. **Room per account.** Each account's five-hour and seven-day meters, the Fable line, and each seat's context percentage are readable by name from the other account; the Team account's room is shown as a dated `estimate` with its method until a measured source exists (DX-26), and `unknown` where no source exists at all.
7. **Roles cannot be captured.** A second registration claiming `libs-seat` does not receive `libs-seat` mail or tasks.
8. The author has relayed zero messages or tasks between the two accounts during a working day of normal use.

A structured handoff with the two-signal close (criterion 5 of the first draft) stays P0 but lands in cycle 0.1: the orchestrator rotates on the Max account, where `SendMessage` already works, and Team workers rotate without a handoff because their state is the task.

### P1: Gemini via Antigravity

**Goal.** A Gemini agent in Antigravity receives and sends through Diogenes, takes tasks through the same path, holds locks through it, and reads the research cache, with the file inbox kept as the fallback.

**Success criteria:**

1. A hub message is injected into a running Antigravity agent through its hook at the next model call, and the agent acknowledges it, without the author's relay. Target: a scripted exchange of 5 messages each way.
2. A Gemini claim ("committed", "all tests pass") is recorded flagged "unverified until reproduced on the Claude side" and a verification row is added by a Claude seat before it is relayed [r8 R-62].
3. The research cache answers hit, stale or miss for 20 real questions, and at least half of repeat lookups are served from the cache rather than fetched.
4. Shared memory in org, project and team scopes is readable from both harnesses, and a write without a version check is refused.

### P2: a GPT auditor

**Goal.** A Codex CLI session (or a small Agents SDK program) reads project state read-only, runs a defined audit, and writes its findings as structured records that a Claude seat verifies.

**Success criteria:**

1. An auditor token cannot write outside its own inbox, proven by a refused write with a literal path.
2. One canned audit runs with `codex exec --json --output-schema`, and its output is ingested into the store without hand editing.
3. The auditor's findings carry provenance and are shown as unverified until a different model confirms them.

### P3: devTeam and later

**Goal.** devTeam supervisors and workers use Diogenes for claims, scoped writes, progress and locks, with per-worker attenuated credentials; the hub can move to a VPS or second machine without changing what agents call.

**Success criteria:**

1. A worker's write outside its declared scope is refused, and the refusal is recorded.
2. A supervisor can see each worker as live, done or stalled against an expected duration.
3. The same `dio` commands work against a remote hub over TLS, and the audit chain verifies end to end.

## 6. Non-goals

- Waking sessions on a schedule the author did not set. He wakes seats by hand for now [r8 R-68]. A wait that a seat starts for itself, on mail or tasks addressed to it, is the seat's own choice, visible in `dio who`, and is the only wake in cycle 0.0 (DQ-7).
  - **Amended 2026-10-15 by cycle 0.0-min's decision 2, approved by the author:** the seat's own `dio watch` and a native message from a peer session that `dio who` lists are the two permitted wakes in 0.0; Diogenes itself still wakes nothing, and cron, `asyncRewake` and mods stay out until 0.2 (`roadmap/0.0/MIN.md`).
- Replacing git, GitHub, worktrees or the per-project checkouts.
- A general chat interface, voice, or a mobile app. Alerts to the author's phone go through what already exists (`PushNotification`, later ntfy) [r6 §3].
- Running the hub on anything but this machine until P3.
- Semantic (vector) search in v0 [r7 §2].
- Cross-account coordination beyond what support's answer covers. That answer covers a Max account and a Team seat on different parts of one project, coordinating as "a workflow matter, not a terms one", and the author proceeds on it (2026-10-10; DQ-5, questions 1 and 2). Cross-account traffic stays explicit and recorded [r8 §3.9].
- Adopting a whole-stack orchestrator or an agent framework [r6 §5].
- A2A or handoff protocols as a transport in v0 [r3 §What this means, 7].
