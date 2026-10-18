# Diogenes: project index

> **Start with [`roadmap/0.0/MIN.md`](roadmap/0.0/MIN.md):** Diogenes 0.0-min, the plan the build follows for cycle 0.0, approved by the author on 2026-10-15. Where this index or `OVERVIEW.md` differs from it, `MIN.md` governs.
>
> **Then [`OVERVIEW.md`](OVERVIEW.md):** one page on what matters, what is waiting on you, and what you can skip (written 2026-10-10, for the full P0 plan).

A cheat sheet: where everything is, in this repository and outside it. Paths outside the repository are as recorded on 2026-10-10 and should be re-checked when they are used; the Gemini inbox path is as the shared context file gives it.

## In this repository

| What | Where |
|---|---|
| What Diogenes is, who uses it, goals by horizon (P0 is delegation), non-goals | `meta/PROJECT_GOALS.md` |
| The machine, sandboxes (with the measurements M1–M5), licence, languages, budget, deadlines, practices that must not change | `meta/PROJECT_CONSTRAINTS.md` |
| Rules for agents working on and using Diogenes; when a task may be acted on; names and identifiers | `meta/PROJECT_RULES.md` |
| Requirements DR-1 to DR-111, with the P0 slice marked ★ (tasks are DR-99 onward) | `meta/REQUIREMENTS.md` |
| Architecture (two transports), data model (tasks in §2.3), delivery modes, backend choice, access model, threat model, prior art, the P0 slice | `meta/DESIGN.md` |
| Day zero, cycles 0.0 to 0.8 with gates, dependencies and sizes | `meta/roadmap/ROADMAP.md` |
| Subcycle plans, when written | `meta/roadmap/<cycle>/`; finished cycles in `meta/roadmap/done/` |
| Task files, one per task, committed on `main` by the merger (from cycle 0.0-min's gate M3), and their convention | `meta/tasks/`, `meta/tasks/README.md` |
| The role line: who holds `team-seat`, `merger`, `poster` and any other role, written on `main` by the merger alone; `dio who --address <role>` resolves from it | `meta/ROLES.md` |
| Decisions for the author, DQ-1 to DQ-30 (DQ-14 withdrawn); those cycle 0.0-min decided or deferred carry a dated note | `meta/OPEN_QUESTIONS.md` |
| Feasibility probes, DX-1 to DX-26, ordered by what they unblock, with the measured ones marked DONE | `meta/EXPERIMENTS.md` |
| The creative parking lot | `meta/IDEAS.md` |
| Round-1 research digests, their prompts, the critique, the review of this revision, and the index | `meta/research/done/`, `meta/research/done/prompts/`, `meta/research/done/README.md`, `meta/research/done/REVIEW-2026-10-10.md` |
| Research still to do | `meta/research/todo/` |
| Known issues | `meta/issues/open/`, `meta/issues/closed/` |
| Per-agent private files, the shared space, scratch | `.internal/agent/<identity>/`, `.internal/shared/`, `.internal/scratch/` (gitignored) |
| Code, docs, tests, vendored code | `src/dio` (`dio who` and `dio register`, 0.0-min's build step 1, and `dio watch`, build step 3; `src/README.md` gives its layout, output and decisions) and `tests/` (`tests/README.md`). `docs/USING.md` (the rules every seat follows, the inbox and its one `printf` line, and the seat's rule; build steps 4 and 5) and `docs/TASK-TEMPLATE.md` (the task template; build step 5). `vendors/` is an empty skeleton today |
| Licence | `LICENSE` (AGPL-3.0) |

## Outside this repository

| What | Where | Note |
|---|---|---|
| The library workbench: board, record, workstreams | `/home/randy/Workspace/REPOS/nitpick-libs/BOARD.md`, `RECORD.md`, `WORKSTREAMS.md` | The `Workbench writer:` line in `BOARD.md` is today's lock; `RECORD.md:7709` holds the take hazards |
| The orchestrate skill | `/home/randy/Workspace/REPOS/nitpick-libs/skills/orchestrate/SKILL.md` | Lock, claim and recovery procedure as practised |
| The credits runner, jobs, outputs, ledger | `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/` (`run.sh`, `jobs/`, `out/`, `LEDGER.md`, `README.md`) | These digests came from `out/dio-r*.md`; `context/file_diogenes.py` filed them; the runner gains `--task` in 0.0 (DR-104) |
| The two context files | `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md` and `diogenes-firsthand-2026-10-10.md` | Copies in `meta/research/done/prompts/`; the firsthand file's last section holds M1–M5 |
| The Gemini and Claude file inboxes | `/home/randy/Workspace/META/NITPICK/messages/gemini-inbox/`, `claude-inbox/` | One Markdown file per message, never edited; the fallback and export format (DR-13); the day-zero model for a per-account inbox |
| The devTeam plugin | `/home/randy/Workspace/REPOS/claude-skills/plugins/devteam/` (`DESIGN.md`, `PROTOCOL.md`, `README.md`) | Charter, task graph, writer lock, write scopes; the P3 client |
| The author's agent memory (Claude Code auto-memory) | `/home/randy/.claude/projects/-home-randy-Workspace-REPOS-nitpick-libs/memory/` (also `-home-randy-Workspace-REPOS-nitpick/` and `-nitpick-fuzz/`) | Memories cited by [r8]: `diogenes-idea`, `session-handoff-brief-the-successor`, `restarts-are-by-hand-for-now`, `silent-peer-may-be-paused-not-gone`, `gemini-file-inbox-channel`, `session-naming-convention`, `subscription-beats-api-for-randy`; per config dir, so the Team seat will not see them unless DQ-27 shares the directory (DR-72) |
| Claude Code status-line outputs | `~/.claude/usage-latest.json`, `~/.claude/context/<session_id>.json` | Meters and context per session; the P0 meter source; the Team copy must write its own file (DX-5) |
| Claude Code transcripts | `~/.claude/projects/<slug>/<uuid>.jsonl` (per config dir) | Where a nonce is found; the session id is the file name |
| Messaging sockets | `/run/user/1000/cc-socks/<pid>.sock` (observed) | Per OS user; config-dir behaviour untested (DX-4); the path in `CLAUDE_CODE_MESSAGING_SOCKET` is how a Bash call names its session (DR-107); not connectable from sandboxed Bash (M1) |
| Sandbox settings per project | `.claude/settings.local.json` in each repository | `allowWrite`, `allowedDomains`, `excludedCommands`; probes use a probe project's `.claude/settings.json` only |
| The Diogenes repository on GitHub | `alternative-intelligence-cp/diogenes` (internal) | Created 2026-09-27 |
| Claude Code documentation used by the digests | `https://code.claude.com/docs/en/…` (hooks, cross-session-messaging, channels, mcp, sandboxing, statusline, headless, plugins/mods) | Fetched 2026-10-10; pages carry no date stamp |
| Antigravity documentation | `https://antigravity.google/docs/…` (hooks, mcp, sidecars, cli/headless, plans) | Fetched 2026-10-10 |
| Codex documentation | `https://learn.chatgpt.com/docs/…` (hooks, extend/mcp, app-server, non-interactive-mode) | Moved from `developers.openai.com` |
| Prior art | MCP Agent Mail (Rust), Beads, agent-loom, agent-mailbox-mcp | Links in `meta/research/done/dio-r6-prior-art-2026-10-10.md` |

## Quick answers

- **Where is the lock today?** The first backticked token of the `Workbench writer:` line in `nitpick-libs/BOARD.md`, with a marker file. It is replaced by `dio lock` in cycle 0.0.
- **How do two seats talk today?** `SendMessage` on one account; file inboxes with the author relaying for Gemini. Diogenes 0.0 replaces both for Claude seats; 0.3 for Gemini.
- **How does the orchestrator hand work to the Team seat?** Through a task record that points at a tracked spec: `dio task post`, the worker's `dio task claim` (the acknowledgement), `dio task report`, and a `dio task verify` by someone other than the reporter (DR-99 to DR-104). Before 0.0 exists: the day-zero practice in `ROADMAP.md`, which is tracked task files, a file inbox per account, and the worker's own background `until` loop.
- **Can a sandboxed shell reach a hub on this machine?** Not by Unix socket or loopback TCP (M1, M3, measured 2026-10-10). Only through the filesystem: the store file in 0.0, the spool directory from 0.1 (DR-110). The HTTP proxy route is untested (DX-8).
- **What is unverified and matters most?** Whether SQLite's locking holds between a host writer and a sandboxed writer (DX-1, revised), whether a hook's context injection reaches the model on prompt and after a tool call (DX-2), and how long a background `dio wait` lives (DX-13). All three block 0.0's gate. Whether native messaging crosses accounts (DX-4) does not block anything but shapes day zero.
- **What is the author's next step?** Review these files; answer DQ-1 to DQ-5, DQ-7, DQ-27, DQ-28 and DQ-29; run DX-1, DX-2, DX-3, DX-6, DX-7 and DX-13 on this machine now; on the first Team session run DX-4, DX-5 and DX-26; and include DQ-5's open questions (3 to 5) the next time you write to support. Questions 1 and 2 are answered: you proceed on support's answer.
