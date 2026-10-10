<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-r6-prior-art-2026-10-10.md: a read-only API-credits job (claude-sonnet-5-5,claude-haiku-5-5, 25/200 turns, $0.7587 by the CLI (the bill is about two-thirds)). Its prompt is prompts/dio-r6-prior-art-2026-10-10.md. -->

# Prior art for coordinating AI coding agents, and what Diogenes should take from it

Job: dio-r6-prior-art-2026-10-10 · Date: 2026-10-10 · Model: Sonnet 5.5 · Tools: Read, WebSearch, WebFetch (no shell)

**Limits:**
- Nothing was run or measured. Every claim comes from README pages, docs and search summaries read today (2026-10-10).
- Several GitHub pages were truncated by the fetcher (MCP Agent Mail Python and Rust READMEs past about 100k characters). Some release or licence fields were not shown. Those are marked **UNVERIFIED**.
- Star counts are as scraped and should be rechecked.
- Framework items (LangGraph, CrewAI, AG2, Microsoft Agent Framework, Letta, mem0, OpenAI) come from secondary sources only. I did not open their primary repos.
- I did not read the A2A spec text or the Claude Code `hooks` and `settings` reference pages. The Claude Code docs I did read are cited per claim.
- **Question 4 (cross-account messaging) is not settled by any source. It needs a ten-minute experiment.**

## 1. Headline findings

1. **Claude Code now has native cross-session messaging, and its scope is the OS user, not the account.** It arrived in v2.1.224, early August 2026 (the version is from the docs, the month from a secondary summary). The docs say the socket is "restricted to your operating-system user". They never mention `CLAUDE_CONFIG_DIR`.
   - Two accounts on one Linux user should therefore see each other, but this is **UNVERIFIED**.
   - A hook or script can post into a session's socket. See §4.
2. **MCP Agent Mail is the closest prior art to Diogenes' coordination core.** It has mailboxes, advisory leases with TTLs, a git-backed audit and a human web UI. The Python original is now unmaintained and superseded by a Rust port, with a release two days ago.
3. **Beads is the leading task and board layer.** It is MIT, about 28k stars, backed by Dolt, with a release on 30 Sep 2026. It has no real lock beyond an atomic `--claim`.
4. **Nearly every tool is advisory and poll-based.** Push into a live session exists in two places only: Claude Code's own messaging, and Claude Code *channels*. Channels are an MCP-based push mechanism and a research preview. This matches the author's hook-or-poll instinct.
5. **Human alerting is solved by small, standard pieces.** The Notification and Stop hooks plus ntfy or Pushover work today. Claude Code also has Remote Control push to the Claude mobile app. Existing multi-agent tools mostly show state in dashboards and do not alert well.

## 2. Inventory of existing tools

Licence, maturity and harness support first, then the mechanics.

### MCP Agent Mail (Dicklesworthstone)

- **Python original:** [mcp_agent_mail](https://github.com/Dicklesworthstone/mcp_agent_mail), read 2026-10-10.
  - About 2.2k stars and 871 commits.
  - The README says it is **superseded by a Rust version and no longer maintained**.
  - Licence: **UNVERIFIED** (the page links a LICENSE file without naming it).
- **Rust port:** [mcp_agent_mail_rust](https://github.com/oysteinkrog/mcp_agent_mail_rust) (the page read was a fork) and its [releases page](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/releases).
  - Latest release **v0.3.38 on 2026-10-08**. Earlier ones were v0.3.37 on 6 Oct, v0.3.36 on 16 Sep and v0.3.35 on 9 Sep.
  - Licence: the badge says "MIT with a rider". The full text was not read, so treat it as **UNVERIFIED**.
  - The README says 45 tools and 25 resources. The About blurb says 34 tools, so the figures conflict.
  - A source build needs Rust nightly and a sibling `frankensearch` checkout.
  - Release archives have a minisign-signed manifest from v0.3.31.
- **Harnesses:** Claude Code, Codex CLI, Gemini CLI, Copilot CLI, Oh My Pi and any MCP client. It runs over stdio or HTTP. MCP config files for Cline, Cursor and Windsurf are also in the repo.
- **Identity:** agents register per project and get adjective-noun names such as "GreenCastle".
  - Identity is self-asserted by default.
  - An optional Ed25519 registration-proof gate is off by default.
- **Addressing:** names within a project. Cross-project messaging needs an approved contact link. Threads use `thread_id`. There is no broadcast-to-all, by design.
- **Delivery: poll.** `fetch_inbox` and inbox resources. Durable event cursors let monitors poll without consuming bodies. Messages carry importance and ack-requested flags. I found no push.
- **Leases:** advisory reservations on path globs, exclusive or shared, with TTL expiry. An optional **pre-commit guard** blocks commits that touch another agent's exclusive reservation.
- **Audit:** every message and reservation is written as Markdown in a per-project git repo. SQLite with WAL and FTS5 indexes it for search.
- **Human surface:**
  - A server-rendered `/mail` web UI behind a bearer token, with a "Human Overseer" composer for high-priority messages to agents.
  - A 16-screen terminal console with toasts.
  - No phone alerts.
- **A fork worth noting:** [mateusz-klatt/mcp_agent_mail](https://github.com/mateusz-klatt/mcp_agent_mail) ("Iris"). It is HTTP-only and separates a durable Agent that owns the mailbox from per-session executions. That fits seat rotation.

### Beads

- **Source:** [gastownhall/beads](https://github.com/gastownhall/beads), read 2026-10-10, and its [releases page](https://github.com/gastownhall/beads/releases).
- **What it is:** a graph issue tracker for agents, backed by Dolt.
  - The `bd` CLI has `ready` (unblocked work) and `update --claim` (atomic assign plus in-progress).
  - Hash IDs avoid merge collisions.
  - A message issue type has threading, ephemeral lifecycle and mail delegation.
- **Licence:** MIT. About 27.8k stars.
- **Maturity:** stable **v1.3.1 on 2026-09-30**. Pre-release v1.3.2-rc.2 on 10 Oct. v1.3.0 was 15 Sep. Very active.
- **Harnesses:** Claude Code, Codex, Factory Droid, Cursor, Copilot. Other agents use an `AGENTS.md` snippet.
- **Concurrency:**
  - Embedded Dolt is single-writer.
  - Server mode allows multiple writers.
  - Sync is `bd dolt push` and `pull` against a git remote.
  - `issues.jsonl` is an export only.
- **Identity, delivery, audit:** assignee string. Poll via CLI. Dolt gives commit history, so audit is inherent.
- **UI:** none built in. Community TUIs and web UIs are listed in its `docs/community-tools.md`.
- **Related:** Agent Mail's pre-commit guard exempts `.beads/**`, so the two are designed to coexist.

### Gas Town (Yegge's orchestrator on Beads)

- **Source:** [gastownhall/gastown](https://github.com/gastownhall/gastown).
- **Basics:** MIT, about 18.3k stars. The release field was empty in my capture, so the last release is **UNVERIFIED**.
- **Harnesses:** Claude Code by default, plus Copilot, Codex, Gemini, Cursor, Kiro, Amp, OpenCode and others as presets.
- **Messaging:** per-role mailboxes (`gt mail`) and `gt nudge`, which pushes a prompt to an agent. Escalations are routed by severity.
- **Identity:** persistent identity with ephemeral sessions. This is a close match to the author's seat rotation.
- **Locking:** none described.
- **Human surface:** a web dashboard (`gt dashboard`) and a terminal feed (`gt feed`) with a stuck-agent view.
- **Overall:** it is a whole opinionated orchestration world, not a library.

### agent-loom (formerly agent-mail, osteele)

- **Source:** [osteele/agent-mail](https://github.com/osteele/agent-mail), renamed to agent-loom in Oct 2026 per the page.
- **Basics:** MIT, 4 stars, 198 commits. Small and personal, and the Linux status is thin.
- **Push into live sessions:** it is the only third-party project I found that does this. It uses Claude Code **channels** (§3).
  - It needs the plugin, `channelsEnabled` in managed settings, and `claude --channels=plugin:...` on every session.
- **Other features:**
  - Path claims are advisory, atomic across files, with a one-time release token. A session's claims survive a disconnect for 15 minutes, and the daemon reminds the owner at 2 h, 8 h and then daily.
  - Work leases record who is responsible for a logical unit.
  - A Slack echo, and a read-only local dashboard at `127.0.0.1:8377`.
- **Config-dir note:** it moves `~/.claude/agent-mail` to its own path and leaves symlinks. That is a hazard when two config dirs are in play.
- **Caveat:** the daemon installer is macOS-only. CLI and MCP are tested on macOS and Linux.

### Small MCP mailboxes and buses

All are single-author and young. I did not verify licences or last-commit dates.

| Project | Notes |
|---|---|
| [therapietech/mcp-agent-bus](https://github.com/therapietech/mcp-agent-bus), [josesuarezcordova/mcp-agent-bus](https://github.com/josesuarezcordova/mcp-agent-bus) | Same-machine, filesystem-only: a JSON inbox per session, a broadcast folder, `fs.watch`. Reading consumes messages. Zero infrastructure. |
| [alessandrobologna/agent-bus-mcp](https://github.com/alessandrobologna/agent-bus-mcp) | stdio MCP over SQLite: named topics, stable peer names, server-side cursors. |
| [brumschlag/agent-mailbox-mcp](https://github.com/brumschlag/agent-mailbox-mcp) | The page read was a fork (0 stars, 23 commits); it forks Kipachu-1/agent-mailbox-mcp. It is the closest to Diogenes' layered model: Streamable HTTP MCP, SQLite or Postgres, **bearer token mapped server-side to one identity and workspace** (keys hashed), tasks, notes, artifacts, heartbeat presence, advisory locks, an admin overview API, and creator notifications when a task goes done, blocked or cancelled. It is polling only: `watch_updates` cannot wake a sleeping agent. No UI. Licence **UNVERIFIED**. |

### Claude Code's own features

- **Subagents:** within one session. Subagents that Claude names can message each other and be resumed by name. Source: [agent-teams doc](https://code.claude.com/docs/en/agent-teams).
- **Agent teams** (experimental, off by default, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`): same doc.
  - One lead and teammates, with a shared task list that uses file locking for claims, pending, in-progress and completed states, and dependencies.
  - Each mailbox is a JSON file at `~/.claude/teams/<team>/inboxes/<agent>.json`, validated on read.
  - Hooks: `TeammateIdle`, `TaskCreated` and `TaskCompleted`. Exit code 2 sends feedback or blocks.
  - **Limits:** one team per session, no sharing across sessions, no nesting, no resume of in-process teammates.
  - Team state lives under `~/.claude/`, so it is per config dir and in-session only.
- **Cross-session messaging:** [doc](https://code.claude.com/docs/en/cross-session-messaging), v2.1.224 or later on Linux and macOS.
  - **Delivery:** push-like. The message is read between tool calls, or starts a new turn if the session is idle.
  - **Idle notice:** `notify_when_idle`, v2.1.236 or later, one-shot, expires after 12 h.
  - **Receiving controls:** `crossSessionInbound` is `accept`, `hold` or `refuse`.
    - With no value set, the default depends on the permission-mode class of both sessions. A bypass-permissions receiver holds messages for approval unless the sender also bypasses.
    - Held messages: at most 100. Unanswered ones expire after 5 minutes (`dialogExpiry`) in non-interactive sessions.
  - **Limits:** plain text only, about 1M characters, burst refusal, loop throttling.
  - **Reach:** the machine's sessions, plus cloud and other-machine sessions via Remote Control. A container and its host cannot reach each other.
  - **Identity:** the session name from `/rename` or `--name`. Colliding names get a variant, or a short id.
  - **Audit:** none beyond the transcripts. Nothing is logged durably as a mailbox.
  - **Trust:** messages are marked as from another session and cannot approve permissions or change config.
- **Agent view** (`claude agents`, research preview, [doc](https://code.claude.com/docs/en/agent-view)): one terminal screen for *background* sessions with states (Working, Needs input, Idle, Completed, Failed, Stopped). `claude agents --json --all` exposes `state` and `waitingFor`. The `Notification` hook fires with `agent_needs_input` or `agent_completed`.
  - **It does not span config dirs:** the supervisor uses `CLAUDE_CONFIG_DIR`, so there is one supervisor and one list per account. Interactive sessions in other terminals don't appear until backgrounded.
  - The introduction version was not shown (the table was truncated), so **UNVERIFIED**.
- **Channels** (research preview, [doc](https://code.claude.com/docs/en/channels)): see §3.

### Orchestrators (claude-flow / Ruflo)

- **Sources:** [ruvnet/ruflo](https://github.com/ruvnet/ruflo) and secondary sources, read 2026-10-10.
- **Basics:** MIT, about 74k stars per the page (a July secondary source said about 64k).
  - Renamed from claude-flow in Jan 2026 after a trademark conversation with Anthropic.
  - A secondary source gave **v3.42.0 on 2026-09-15** (page-reported, not seen on the repo).
  - Very fast release cadence, which one reviewer called a production risk.
- **Scope:** swarms, AgentDB vector memory and a cross-machine "federation" with mTLS and Ed25519, trust scoring and PII scanning. The console is `/ruflo` inside Claude Code.
- **Harnesses:** Claude Code, Codex and Hermes.
- **Locks:** none mentioned.
- **For Diogenes:** it is a harness, not a hub. Its scope is wide and its claims hard to verify. It cuts against "systems are simple".

### Protocols

- **A2A** (Agent2Agent):
  - **Governance:** it is a Linux Foundation project. It was announced as joining the Agentic AI Foundation (beside MCP) on 17 or 20 Aug 2026; the sources disagree on the date.
  - **Releases:** [v1.0.0 on 2026-03-12 and v1.0.1 on 2026-05-28](https://github.com/a2aproject/A2A/releases). The licence is not shown on the page; Apache-2.0 is commonly cited, so **UNVERIFIED** here.
  - **Design:** JSON-RPC, HTTP and gRPC bindings with agent cards for discovery, tasks, `tasks/list`, push-notification configs and multi-tenancy. v1.0 was breaking against 0.3. SDKs exist in five languages.
  - **Merger:** IBM's ACP merged into A2A in Aug 2025 (secondary source, [Tyk](https://tyk.io/learning-center/agent-protocols-a-complete-guide-to-mcp-a2a-and-acp/)). Unrelated: Zed's "ACP" is an editor-to-agent protocol.
  - **Fit:** it is for opaque, networked agent services. No coding harness speaks it natively that I found, so it is a possible future facade, not a v0 dependency.
- **MPAC** ([arXiv 2604.09744](https://arxiv.org/pdf/2604.09744)): argues MCP is the wrong layer for agent-to-agent coordination. I only saw the search summary.

### Frameworks (brief; secondary sources: [Morph](https://www.morphllm.com/ai-agent-framework) and similar, as of about 16 Aug 2026)

These are libraries for building agent programs. None coordinates *existing coding CLIs*. The versions below are scraped and need a PyPI check.

- **LangGraph:** 1.0 in Oct 2025, 1.2.11 on 2026-08-11. Graph state, checkpoints and human-in-the-loop interrupts.
- **CrewAI:** 1.15.16 on 2026-08-14, with pluggable memory backends.
- **Microsoft Agent Framework:** 1.0 GA on 2026-04-03. It merges AutoGen and Semantic Kernel, and AutoGen is in maintenance.
- **AG2:** the AutoGen fork, v1.0.x, Apache-2.0.
- **OpenAI Agents SDK:** handoffs let one agent pass control to another within a process. The Agents API reached public beta on 2026-09-10 (secondary). Codex multi-agent v2 and `codex mcp-server` (as the secondary guides describe) make Codex usable as an MCP tool.

### Memory (brief)

- **Letta:** Apache-2.0. A secondary source says that from 16 Mar 2026 it began retiring server-side memory tools, identities and MCP integrations in favour of **git-backed memory files** and client-side orchestration. That supports Diogenes' choice of files plus git.
- **mem0:** Apache-2.0 core. Multi-agent sharing is "scoped" and needs custom work. Graph memory moved to the paid platform.
- **Governed Shared Memory** ([arXiv 2606.24535](https://arxiv.org/pdf/2606.24535)): research on shared memory for multi-agent systems. I read only the title, not the paper.

## 3. Human surfaces and alerting

**Dashboards, as shipped**

| Tool | Surface |
|---|---|
| MCP Agent Mail (Rust) | `/mail` web UI with an overseer composer, plus a 16-screen terminal console with toasts |
| Gas Town | web dashboard (htmx) plus `gt feed` terminal view and a stuck-agent panel |
| agent-loom | localhost dashboard (read-only), Slack echo, and an in-place-updated Slack dashboard message |
| Claude Code agent view | one-terminal list by state ("needs input" first); JSON via `claude agents --json --all` |
| Agent teams | the agent panel under the prompt, and tmux or iTerm2 split panes |
| Ruflo | `/ruflo` console inside Claude Code |
| Beads | none built in; community UIs |

**Alerting, as shipped**

- **Claude Code mobile push:** with Remote Control active, Claude can push to the Claude mobile app. `/config` has *Push when Claude decides* and *Push when actions required*. It is skipped while you type in the terminal. Source: [Melta, 2 Oct 2026](https://getmelta.app/blog/claude-code-notifications-on-phone/) (secondary). I did not find the primary doc.
  - Remote Control needs a claude.ai sign-in, so it is **per account**. Two accounts means two app logins.
- **Hooks:** the `Notification` event fires on a permission prompt or question, and `Stop` fires on finish. A `curl` to **ntfy** (free, self-hostable, native apps, one-way) or **Pushover** ($5 per platform, priorities and receipts) is a dozen lines. Sources: [claude-ntfy-hook](https://github.com/nickknissen/claude-ntfy-hook), [AvAl4nch/claude-ntfy](https://github.com/AvAl4nch/claude-ntfy), [DEV post](https://dev.to/coa00/how-i-built-a-mobile-approval-system-for-claude-code-so-i-can-finally-leave-my-desk-1ida).
  - **Two-way approve or deny from the phone:** ntfy action buttons, Tailscale callbacks and SSE. Treat that as a security surface.
- **Channels:** Telegram, Discord and iMessage plugins push events *into* a running session. Replies go back through the same bridge. Source: [channels doc](https://code.claude.com/docs/en/channels).
  - Requirements: claude.ai or Console auth, Bun, the `--channels` flag, and a **sender allowlist** per plugin.
  - Team and Enterprise orgs must enable `channelsEnabled` explicitly. Pro and Max users skip that check.
  - Tool permissions can be relayed remotely, so an allowlisted sender can approve tool use. That is a trust decision.
  - **It is a research preview** whose flags and protocol may change. The channel plugins must be on an Anthropic allowlist unless you use the development flag.
- **Agent view notifications:** `agent_needs_input` and `agent_completed` go through the terminal's notification channel and can trigger the same `Notification` hook.

**Gap:** none of the multi-agent tools alert the *human* well. Alerts come from Claude Code's hooks, not from the coordination layer. That is where Diogenes can add value cheaply: **the hub emits alert events, and a small sink forwards them to ntfy.**

**Gemini and Codex:** I did not research their notification hooks. Gemini in Antigravity may have none, so a Diogenes-side watcher is the safer assumption (**UNVERIFIED**).

## 4. The near-term case: two Claude Code accounts on one machine

**Is there an existing tool that "just works"?** Not confirmed. In order of likelihood:

1. **Native cross-session messaging** is the likeliest to work as is.
   - The doc scopes the socket to the *OS user* (Unix socket, per session) and says nothing about config dirs or accounts. That points to it working across two `CLAUDE_CONFIG_DIR`s as the same Linux user.
   - **Counter-points to test:**
     - Socket *location*: the doc says `/tmp/cc-socks-<uid>` as a fallback. The author already observed `/run/user/1000/cc-socks/`. Check that both accounts bind in the same directory.
     - `crossSessionInbound` is a *per-config-dir* user setting. A bypass-permissions session will **hold** messages from a prompting sender. The author's seats may differ in mode. Set `accept` explicitly on both accounts.
     - A Team account's managed settings could set `refuse` or deny the tools. The doc says admins can do this.
     - Names are probably not unique across accounts, so use distinct `--name`s.
     - Remote Control is account-bound, so "sessions beyond this machine" would not cross accounts. It matters only for the cloud path.
   - **The experiment:**
     - Start `claude --name probe-a` under config dir A and `claude --name probe-b` under B.
     - Run `/list-agents` in each, then send a message and check delivery.
     - Do it again with one side idle and one mid-turn, and with one side in bypass mode.
2. **Posting from outside Claude.** A hook or script can write to a session's socket: the `CLAUDE_CODE_MESSAGING_SOCKET` and `CLAUDE_CODE_MESSAGING_TOKEN` env vars are exported to hooks and Bash. The doc describes posting into *its own* session's socket as the supported case. Posting into *another* session's socket is plausible but not documented (**UNVERIFIED**). If it works, Diogenes could inject messages into any local seat, push-style.
   - A sandboxed Bash must be allowed the Unix socket (`sandbox.network.allowUnixSockets`).
3. **An MCP mailbox** (Agent Mail Rust or the small buses) works across config dirs by construction: it is a separate local process and the DB is shared. The cost is polling, plus the author's `CLAUDE_CONFIG_DIR` MCP config must point both accounts at it. The agent must *call* `fetch_inbox`, so delivery depends on a hook or habit. Combine it with a `UserPromptSubmit` or `PostToolUse` hook that checks the inbox.
4. **File inboxes** (the current Gemini convention) work today with no dependency.
5. **Not options:**
   - Agent teams: one team per session and files under one config dir, so they cannot span accounts.
   - Agent view: per config dir.

## 5. Adopt / borrow / avoid

| Item | Verdict | Why |
|---|---|---|
| Claude Code `SendMessage` and `ListAgents` | **Adopt now (verify first)** | Push-like delivery, a trust model, idle notices, the author already uses it. Cross-account behaviour untested. |
| Hooks plus ntfy for human alerts | **Adopt** | A dozen lines, free, self-hostable. Covers the manual relay. |
| Agent Mail (Rust) | **Borrow design; trial as optional backend** | Best prior art for TTL advisory leases, the pre-commit guard, git-plus-SQLite audit and the human overseer inbox. Licence rider and a heavy 45-tool surface. The Python version is dead. |
| Beads | **Borrow** (or interoperate) | Atomic claim, a dependency "ready" query and hash IDs. Dolt is a heavy dependency, and the layered write-access model is not there. |
| Agent Mailbox MCP (brumschlag) | **Borrow design** | Token-to-identity-and-workspace maps to the org, project and team layers. Young with a thin community, so do not depend on it. |
| Claude Code channels | **Watch** | The only sanctioned push into a live session. Research preview, Anthropic allowlist, account-bound. Good for the human-to-agent path later. |
| A2A v1.0 | **Borrow vocabulary; avoid as v0 transport** | Task states and agent cards are worth copying. No coding harness speaks it, and the surface is large. |
| agent-loom | **Borrow ideas** (claim reminders at 2 h and 8 h, release tokens, work leases) | Tiny and macOS-leaning, and it mutates `~/.claude`. |
| Ruflo / claude-flow, Gas Town | **Avoid as dependency** | Opinionated whole-stack harnesses with a fast-changing surface and big claims. Mine Gas Town's persistent-identity-with-ephemeral-session pattern. |
| LangGraph, CrewAI, MAF/AG2, OpenAI handoffs | **Avoid** | They orchestrate in-process agents, not existing CLIs. |
| Letta, mem0 | **Avoid for v0** | Letta itself is moving to git-backed memory files. |
| Advisory locks as the only enforcement | **Avoid** | Every surveyed lock is advisory. The author's thirteen take hazards show the failure modes. Diogenes needs a server-side check, with hooks that deny writes outside a lease. |
| Self-asserted identity | **Avoid** | Agent Mail defaults to it. Diogenes should use server-issued tokens, and keep content-based identity checks for seat handoffs. |

## 6. Build or adopt for v0: short argument

**Build a small core, and adopt around it.** A small hub is a few hundred lines on SQLite or Redis, with a poll CLI and thin hooks.

- No surveyed tool covers the combination the author wants: a layered org, project and team model, with write access per team, server-issued per-agent credentials, one hook-or-poll interface for Claude, Gemini and GPT, and an alert sink. The nearest, Agent Mailbox MCP, is young and has no UI or push. Agent Mail has no layers and its identity is self-asserted.
- Everything else is adoptable. Use the native `SendMessage` for the Claude-to-Claude fast path, ntfy for alerts, Beads or a plain table for tasks, and git for audit.
- Adopting Agent Mail wholesale is the main alternative. It could be trialled in an afternoon. The cost is a large tool surface that agents must be taught, and a licence rider to read. If the cross-account experiment fails, a trial of Agent Mail is a good day-one fallback.
- The priority-one need is two accounts talking. The cheapest path is the experiment in §4 plus file inboxes with a `UserPromptSubmit` hook. That needs no new server.
- The real risks are leases that fail silently and human-alert fatigue. Neither is solved by an off-the-shelf tool.

## What this means for Diogenes

- **Do the §4 experiment before writing any code.** Native messaging may already solve priority one. (Finding 1.)
- **Keep one message envelope with two delivery modes.** Push is available only inside Claude Code (sockets, channels). Poll via a CLI and a cursor works everywhere, as Agent Mail's event cursors and `agent-bus-mcp` show. (Findings 1 and 4.)
- **Make leases server-checked, with TTL and a crash-release path, and enforce them with a hook.** Copy Agent Mail's TTLs and pre-commit guard and agent-loom's long-hold reminders. Do not copy markdown-line locks. (§2, §5.)
- **Issue credentials per agent.** Token-to-identity-and-workspace mapping, as in `agent-mailbox-mcp`, with database-level privileges behind it, answers the author's sandbox question. It is also how to implement "write access per team". (§2.)
- **Separate durable identity from session.** The Iris fork and Gas Town both do this, and it matches seat rotation. (§2.)
- **Make alerting a first-class event stream:** needs-human, task-blocked, lease-expired and handoff-done go to an ntfy sink with priorities. Keep two-way approval out of v0. (§3.)
- **Keep messages as data.** Claude Code's own rule (a cross-session message cannot approve anything) is the template. (§2.)
- **Keep git as the audit trail.** Agent Mail's git-plus-SQLite split is the proven shape. (§2.)
- **Use A2A's task states and Beads' atomic claim as vocabulary.** Do not depend on either. (§2.)

## Open questions

1. Does `SendMessage` work between sessions under two `CLAUDE_CONFIG_DIR`s as the same OS user? Which socket directory does each bind? How do `hold` and the permission-mode default behave? (Experiment.)
2. Can a hook post into *another* session's socket, and does that raise approval prompts? (Experiment.)
3. Will the Team account's managed settings set `channelsEnabled`, `crossSessionInbound` or deny rules? (Only the author can see this.)
4. Does `claude agents --json` offer anything useful per config dir for a combined view? Run it once with each `CLAUDE_CONFIG_DIR`.
5. What are the Rust Agent Mail licence rider's terms? Diogenes is AGPL-3.0, so compatibility matters if it embeds any of the code.
6. Which Gemini and Codex hook or notify points exist? Not researched here.

## Outside my question

- The Claude Code docs describe features (channels, agent view, cross-session messaging) that are research previews, with flag names that may change. Pin the Claude Code version in any Diogenes docs that rely on them.
- AutoGen is in maintenance mode, and Letta has dropped parts of its server-side API, so any framework dependency is a churn risk.

Sources: [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging), [agent teams](https://code.claude.com/docs/en/agent-teams), [agent view](https://code.claude.com/docs/en/agent-view), [channels](https://code.claude.com/docs/en/channels), [mcp_agent_mail](https://github.com/Dicklesworthstone/mcp_agent_mail), [mcp_agent_mail_rust](https://github.com/oysteinkrog/mcp_agent_mail_rust), [Rust releases](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/releases), [beads](https://github.com/gastownhall/beads), [beads releases](https://github.com/gastownhall/beads/releases), [gastown](https://github.com/gastownhall/gastown), [osteele/agent-mail](https://github.com/osteele/agent-mail), [agent-mailbox-mcp](https://github.com/brumschlag/agent-mailbox-mcp), [mcp-agent-bus](https://github.com/therapietech/mcp-agent-bus), [agent-bus-mcp](https://github.com/alessandrobologna/agent-bus-mcp), [ruflo](https://github.com/ruvnet/ruflo), [A2A releases](https://github.com/a2aproject/A2A/releases), [Tyk protocols guide](https://tyk.io/learning-center/agent-protocols-a-complete-guide-to-mcp-a2a-and-acp/), [Morph frameworks](https://www.morphllm.com/ai-agent-framework), [Melta notifications](https://getmelta.app/blog/claude-code-notifications-on-phone/), [claude-ntfy-hook](https://github.com/nickknissen/claude-ntfy-hook), [MPAC](https://arxiv.org/pdf/2604.09744), [Governed Shared Memory](https://arxiv.org/pdf/2606.24535).