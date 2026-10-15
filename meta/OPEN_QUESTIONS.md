# Diogenes: open questions for the author

Drafted 2026-10-10, revised the same day. Each question is one the author must decide, or must ask someone else. Each gives why it matters, the options with their trade-offs, a recommendation with its reason, and what it blocks. Policy questions are listed as questions, without interpreting any terms. Identifiers are stable; DQ-14 is withdrawn, DQ-27 to DQ-29 are appended.

## Architecture and build

**DQ-1. Does cycle 0.0 ship a daemon, or a CLI that opens the SQLite file directly?**
- Why it matters: it decides the size of the first slice. After M1 and M3, a daemon is reachable from sandboxed Bash only through a spool directory, so the reach question is no longer "socket or not" but "file or spool".
- Options: (a) CLI opens the file, daemon with socket and spool in 0.1. Smallest; isolation no worse than today since both seats share one uid; depends on DX-1 (revised). (b) A minimal spool-ingesting daemon from 0.0, as [r4] and [r5] recommend in spirit. Cleaner audit and tokens from day one; about two more seat-days; its socket half would still serve only hooks and MCP.
- Recommendation: (a), because it is buildable in a few days and buys the same protection; switch to (b) only if DX-1 fails across the sandbox boundary.
- Blocks: cycle 0.0 planning.

**DQ-2. Which language for `dio` and the hub?**
- Options: Python 3.12 (fast to write, stdlib `sqlite3`, hooks pay interpreter start on every prompt; measure it in DX-2); Go (one static binary per account, better for a long-running socket server and spool ingester, a second language); Rust (the author's ecosystem, slowest first slice).
- Recommendation: Python for 0.0 and 0.1; re-do the daemon in Go only if hook latency exceeds the 300 ms gate or a static binary matters.
- Blocks: 0.0.

**DQ-3. Where do the store and the spool live, and who owns them?**
- Why it matters: they must survive either account's config dir being replaced [r8 open questions], be writable from both accounts' sandboxes (the spool from 0.1, the store in 0.0 only), and not be a project checkout.
- Options: `~/.local/share/diogenes/` (outside both config dirs, one `allowWrite` entry per account; from 0.1 the store moves out of `allowWrite` and only `spool/` stays in); inside the diogenes repository's `.internal/shared/` (gitignored, but tied to one checkout); a path under one config dir (lost if that dir is replaced).
- Recommendation: `~/.local/share/diogenes/` with `store/` and `spool/` as siblings, with a nightly `dio export` of messages, tasks and audit into a tracked file in the diogenes repository for durability.
- Blocks: 0.0 setup.

**DQ-16. Build the small core, or trial MCP Agent Mail (Rust) first?**
- Options: build (recommended by [r6 §6]; fits the layers, the task path and the identity model; a few hundred lines); trial Agent Mail for an afternoon (45 tools to teach, a licence rider unread, self-asserted identity, no layers, no task path, and its MCP transport would not reach a sandboxed shell).
- Recommendation: **build** (confirmed by [r9], 2026-10-10). If 0.0 slips, the fallback is the smallest `dio` subset, not an MCP Agent Mail trial: `send`, `inbox`, `ack` and `task post|claim|report|verify` on one SQLite file, plus the existing file inboxes. [r9 §7]'s reasons for dropping the trial:
  - Agent Mail covers none of the task path (DR-99 … DR-109);
  - it has no file transport, so sandboxed shells cannot reach it (M1, M3);
  - its names are self-asserted, which conflicts with DR-106 and DR-107;
  - its store has open corruption issues;
  - its licence rider names Anthropic, and by [r9]'s reading cannot be combined with AGPL. **The author should read that `LICENSE` himself before any trial ([r9] X0).**
- Blocks: nothing today.

**DQ-23. Should the lease be enforced (a `PreToolUse` deny) or only recorded in the first cycles?**
- Options: record only in 0.0 (seats obey by discipline, as today); enforce from 0.1 with fail-closed behaviour (a hub outage then blocks writes in governed trees).
- Recommendation: record in 0.0, enforce in 0.1, because enforcement without the hub's availability guarantees would stop work on every restart.
- Blocks: 0.1 scope.

**DQ-24. Retention and export cadence for messages, tasks and audit rows.**
- Options: keep everything (the file grows slowly; fine for a year); prune delivered messages and verified tasks after N days with the audit kept; export daily to git.
- Recommendation: keep everything in 0.0; export daily from 0.1; decide pruning when the file passes 1 GB.
- Blocks: nothing before 0.1.

**DQ-25. Is the diogenes repository itself a Diogenes project from day one, with its own role and lease?**
- Recommendation: yes, dogfood it; the seat building 0.0 is assigned `dio-seat` and takes `diogenes/tree/main`; its subagents take their work as tasks.
- Blocks: nothing; a convention.

**DQ-26. Does the repository stay internal, or will Diogenes be published or offered as a service?**
- Why it matters: AGPL-3.0 obligations apply on distribution or network service to others, and the licence of borrowed code (Agent Mail's rider) matters only then.
- Recommendation: decide before any code is borrowed; assume internal until then.
- Blocks: borrowing code from prior art.

**DQ-28. The routing floor: what does `dio task post` do when the route's room is low, an `estimate`, or `unknown`?**
- Why it matters: the Team room is an estimate until DX-26 (DR-109); refusing on `unknown` would block delegation on day one, while never refusing lets a worker run into the Team limit mid-task.
- Options: refuse below a floor the author sets per account (recommended; `estimate` and `unknown` are printed and recorded on the task, and only a measured or estimated figure below the floor refuses); never refuse, only print; ask the author on every `unknown` (a recurring human step with no safety category).
- Recommendation: a floor of 15 % room per account, overridable with `--force`, which is recorded.
- Blocks: DR-103's default.

**DQ-29. Are Team worker sessions interactive terminals the author opens, or background sessions (`claude --bg`)?**
- Why it matters: an idle background session's process may be stopped after about an hour unless pinned [r1b §5], which would end its `dio wait`; an interactive terminal stays alive but costs the author a window per worker. Background sessions are listed by `claude agents --json` (DX-18), which could feed presence.
- Options: interactive terminals, rotated by hand (matches the author's current practice); background sessions pinned with `Ctrl+T`; background sessions unpinned, with the orchestrator treating `stopped` as "re-post the task".
- Recommendation: interactive terminals for day zero and 0.0; try pinned background sessions in 0.2 when DX-18's result is in.
- Blocks: the worker half of the 0.0 gate.

## Accounts and policy

**DQ-4. Are you the Owner of the Team organization, and what do its managed settings say?**
- Why it matters: `channelsEnabled`, `allowedChannelPlugins`, `allowManagedHooksOnly`, `allowManagedModsOnly`, `crossSessionInbound` and `permissions.deny` can all be set by an Owner and would decide whether the Team seat can run the adapter's hooks, a mod, or channels [r1 §5, r1b §6].
- Options: you are the Owner (set what the adapter needs); someone else is (ask them); the seat is on another organization's plan (the adapter must work with hooks denied).
- Recommendation: check `/status` and the admin settings on the first Team session, and record the answers as facts in Diogenes. If hooks are denied, the Team seat uses `dio` from Bash only, with presence from the process check and no injection; no recurring human step is added.
- Blocks: the Team half of 0.0 (DX-5), and 0.2's mod option.

**DQ-5. Policy questions to put to Anthropic support in writing.** These are questions, not interpretations.
1. **ANSWERED for planning (the author, 2026-10-10):** a personal Max account and a Team seat working on different parts of one project is "not itself a violation", and "coordinating across them is a workflow matter, not a terms one" (Anthropic's support assistant, 2026-10-10; the support conversation's ID is the record). The author proceeds on that answer. A human's written confirmation is a nice-to-have he will still seek; it is not a blocker.
2. **ANSWERED for planning, by the same decision:** delegation between the Max account and the Team seat, each account's own session doing the work it is given, is how the author plans to use the two accounts (his words: *"since i'm cleared to use the subscriptoin and seat in the same project"*). Do not re-raise it.
3. Is a solo developer's own long-running process that drives `claude` sessions on subscription credentials, for that developer's own use, within the terms? The SDK and legal pages quoted in [r1b §9] address third-party products and say to "contact sales".
4. Does a hook or a local process that starts a new turn in an idle session (an `asyncRewake` hook, a mod's `$.prompt.submit`) count as ordinary use? A background command the session itself started, whose exit re-invokes it, is the product's documented `run_in_background` behaviour and is not asked about.
5. Does the Team seat's status line expose `rate_limits`, and if not, is there a supported way to read a Team seat's meters?
- Recommendation: questions 3 to 5 stay open. Include them in the message when the author next writes to support for his human confirmation. Keep each reply as a Diogenes fact with its date. Cross-account delegation proceeds now, tagged and recorded as all traffic is.
- Blocks: nothing in 0.0 (every cross-account task is tagged, and the author can stop routing to `team` in one setting); 0.2's wake paths should wait for answer 4.

**DQ-6. Will the Team account run as a different Linux user?**
- Why it matters: a second uid would let `SO_PEERCRED` and file modes separate the accounts, which the same uid cannot [r5 §1].
- Options: same user (simplest; the store is one file both can write); separate user (kernel separation; the store needs group permissions or the hub; `allowWrite`, the spool and sockets per user).
- Recommendation: same user for 0.0 and 0.1; revisit at 0.7 when devTeam sandboxes need separation.
- Blocks: nothing now.

**DQ-8. If DX-4 shows native `SendMessage` crosses accounts, is it used?**
- Options: not at all (every message through Diogenes; simplest audit); as a doorbell for pointer-only nudges ("check dio"), mirrored into the store (lower latency, same-mode sessions only, held messages when modes differ [r1b §1]); as the only path (rejected: no durable record, no task state, result means queued).
- **DX-4 PASSED on 2026-10-12, both ways, with no approval step in bypass mode,** and DQ-5's first two questions are answered. So this is now a live choice.
- Recommendation, revised: **use native `SendMessage` now for Claude↔Claude conversation and nudges** (briefs, questions, "task at X, commit Y"). Keep **tasks, claims, reports, leases and the audit record in Diogenes** (or in git until 0.0 exists), because native messages leave no durable record and no task state, and subagents cannot receive them. Set `crossSessionInbound: accept` explicitly on both accounts. Gemini and GPT still need Diogenes.
- **Decided 2026-10-15 by cycle 0.0-min's decision 4(c), which the author approved as recommended:** the revised recommendation is adopted for conversation and nudges, with tasks, claims and reports in git under the task template; leases and the audit record are 0.1. `crossSessionInbound` stays `accept` on both accounts, as already set, as a stated acceptance that any session of the same Linux user can put text into either seat's turn with no approval step; `USING.md` records it (`roadmap/0.0/MIN.md`).
- Blocks: nothing in 0.0; the day-zero practice uses it if available.

**DQ-17. Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` in both accounts' settings?**
- Recommendation: yes, so Claude does not turn named subagents into teammates and the one `SendMessage` tool name is not shared between two systems [r1 §8].
- Blocks: 0.0 setup.

**DQ-20. Does an audit run through Antigravity on a Claude model count as a "different perspective"?**
- Why it matters: Antigravity offers Opus 5.5 and Sonnet 5.5 on AI Pro [r2 outside note].
- Recommendation: record the model on every audit finding and require a non-Claude model for the "different perspective" tag.
- Blocks: 0.6's policy.

**DQ-27. Should both accounts' Claude Code auto-memory point at one directory from day zero?**
- Why it matters: auto-memory lives under `CLAUDE_CONFIG_DIR`, so the Team seat will not see the Max account's memory notes for the same project; `autoMemoryDirectory` or `CLAUDE_CODE_PROJECT_DIR_NAME` (v2.1.234+) can point both at one place with no code [r7 §4], and a Team worker that rotates often would benefit at once [c1 C-22]. With `CLAUDE_CODE_PROJECT_DIR_NAME`, `CLAUDE_CONFIG_DIR` must also be set [r1b §5].
- Options: share one directory now (immediate; two accounts' sessions then write one memory tree, with the usual last-write hazards); keep them separate and export through Diogenes in 0.4 (DR-72); share read-only by copying at rotation.
- Recommendation: share one directory now for the project-scoped memory, and record it as a fact; revisit if two sessions' writes collide.
- Blocks: day-zero setup.

## Delivery and waking

**DQ-7. Which wake mechanisms are permitted, and from when?**
- Why it matters: the rule today is that the author wakes seats by hand and no wakeup is unexpected [r8 R-68]. A background command's exit re-invoking the idle session that started it was observed on 2026-10-10 (firsthand §2); whether a seat's own wait on its own mail counts as "expected" is the author's call [c1 C-2].
- Options: none ever (poll at turn boundaries only; the author stays the relay for an idle worker, which the P0 gate cannot meet); a seat may start its own background `dio wait` in 0.0 and nothing else wakes it; opt-in `asyncRewake` or a mod with `$.prompt.submit` in 0.2 (documented wakes started by a hook or mod, not by the seat's turn); cron and `/loop` (token cost per fire).
- Recommendation: 0.0: a seat may start its own background `dio wait`, visible in `dio who`; nothing else wakes it. `asyncRewake` hooks, mods and cron stay out until 0.2, and then only for messages and tasks addressed to that seat, never for sink or notice traffic.
- **Decided 2026-10-15 by cycle 0.0-min's decision 2(b), which the author approved as recommended:** two wakes are permitted in 0.0, the seat's own `dio watch` and a native message from a peer session that `dio who` lists; Diogenes itself still wakes nothing. Cron, `asyncRewake` and mods stay out until 0.2. The risk against DQ-5 question 4 is stated with the decision (`roadmap/0.0/MIN.md`).
- Blocks: 0.0's worker gate and 0.2's scope.

**DQ-11. The first Gemini build: hooks and MCP inside an interactive Antigravity session, or a supervisor around `agy -p`?**
- Options: hooks and MCP (closest to the Claude model; depends on `injectSteps` feeding the model, UNVERIFIED; fails closed on a hook crash); supervisor (fully documented; one process start and one turn per message; not a conversation in the UI; changes how the author works with Gemini) [r2 §5].
- Recommendation: hooks and MCP, with the supervisor as the fallback if DX-22 fails.
- Blocks: 0.3 planning.

**DQ-18. Where do the file-inbox exports go?**
- Options: the existing `META/NITPICK/messages/{gemini-inbox,claude-inbox}` paths (Gemini already reads them); a directory under the store; both.
- Recommendation: the existing paths, so nothing changes for Gemini, with the projection two-way from 0.3.
- Blocks: 0.2's export.

**DQ-21. Which alert sink?**
- Options: `PushNotification` only (exists today, per account, skipped when at the terminal); ntfy (free, self-hostable, native apps, one more service); Pushover (paid per platform, priorities and receipts).
- Recommendation: `PushNotification` in 0.2, ntfy if the author wants alerts away from the desk, and no two-way approval from the phone in any cycle planned here.
- Blocks: 0.2's alert sink.

## Identity and access

**DQ-9. Token scheme for 0.1 and attenuation for 0.7.**
- Options: random bearer mapped server-side with scopes (simplest; no attenuation; re-issue a narrower token for a subagent); HMAC macaroons (attenuation without the issuer; one key; little code); Biscuit (public-key verification, policy language, Rust reference implementation; third-party blocks unsupported in Go) [r5 §1].
- Recommendation: bearer in 0.1; macaroons in 0.7 if subagent attenuation is wanted; Biscuit only if a remote verifier appears.
- Blocks: 0.1 design detail.

**DQ-22. The names: roles, projects, teams, workers.**
- Recommendation: the table in `PROJECT_RULES.md` §7, with `libs-seat`, `compiler-seat`, `libs-sink` and `dio-seat` as the first roles, `libs-worker_<N>` for Team sessions, and project ids equal to repository names.
- Blocks: 0.0's first registrations.

**DQ-19. Where is the audit chain's head anchored?**
- Options: a file under the other account's config dir, written by that account's hook; a weekly commit to a tracked file in the diogenes repository; an external service.
- Recommendation: both of the first two; no external service.
- Blocks: 0.1's audit design.

## Meters and research

**DQ-14. Withdrawn:** settled by first-hand observation, not a decision. `usage-latest.json` carries a `model_limits` Fable line with `used_percentage` and `resets_at` on the Max account (firsthand §3); it is DR-56's primary source, with manual entry as the fallback [c1 C-17].

**DQ-15. The credits correction factor.**
- Recommendation: store "about two-thirds of the CLI figure" as a fact with its measurement date, and re-measure when the Console shows a new balance. Now a P0 fact (DR-59).
- Blocks: DR-59.

**DQ-13. Research TTLs per category, and who may verify.**
- Options for TTL: [r7]'s guesses (60 days for fast-moving tooling, 365 for stable specs, none for history) or the author's six months for non-security digests (R-53).
- Options for verifiers: any other model; only Claude seats; the author for an `author-verified` tier, within an attention budget.
- Recommendation: 90 days security, 180 days other, none for history; any different identity may `peer-verify`; `author-verified` only when he chooses to.
- Blocks: 0.4.

**DQ-10. Gemini route: Antigravity only, or also pay for a Gemini API key to reopen Gemini CLI?**
- Recommendation: Antigravity only; Gemini CLI's hooks are the better-documented design reference, not a target [r2 §0].
- Blocks: nothing; 0.3 assumes Antigravity.

**DQ-12. The GPT auditor's plan and shape.**
- Options: Codex CLI on a ChatGPT plan (Plus has five-hour limits by model; Pro has none); an API key (billed per token, no cloud features); a small Agents SDK program.
- Recommendation: Codex CLI with `exec --json --output-schema` for canned audits; the plan is the author's choice by cost.
- Blocks: 0.6.
