# dio-r6-prior-art-2026-10-10

First read `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md` in full. Then answer the question below as a dated, sourced digest, in the format that file gives.

**Your question:**
- What already exists for coordinating several AI coding agents (messaging, task boards, locks or leases, shared memory), across harnesses or within one?
- What should Diogenes adopt, borrow from, or avoid?
- How do existing tools show the human what is happening, and alert him?

Cover:

1. **Search widely, current to October 2026.** Candidates to check, not a closed list:
   - "MCP Agent Mail" (`mcp_agent_mail`: mailboxes, file reservations or leases, a git-backed audit);
   - Beads (Steve Yegge's issue tracker for coding agents);
   - Claude Code's own multi-agent features: agent teams, subagents, `SendMessage`;
   - claude-flow / ruflo and similar orchestrators;
   - A2A (Agent2Agent), and the protocols merged into it (IBM's ACP);
   - briefly: LangGraph, CrewAI, AutoGen/AG2 and the Microsoft Agent Framework;
   - briefly: OpenAI Agents SDK handoffs;
   - briefly, for memory: Letta and mem0;
   - any "agent message bus", "agent mailbox" or "multi-agent coding coordination" MCP servers or CLIs that are popular now.
2. **For each:**
   - what it does;
   - its licence;
   - its maturity: last release, activity;
   - the harnesses it supports;
   - how it handles identity, addressing, delivery (push or poll), locking or leases, and audit.
3. **Human surfaces:**
   - how these tools show the human what agents are doing: dashboards, TUIs, web UIs;
   - how they alert him: desktop notifications, phone pushes (ntfy, Pushover, Telegram), Claude Code's push notifications.

   The author relays every Gemini↔Claude alert by hand today.
4. **The near-term case:** two Claude Code accounts on one machine. Is there an existing tool that would just work for messaging between sessions under different `CLAUDE_CONFIG_DIR`s?

End with an **adopt / borrow / avoid** table, and a short argument for building versus adopting for v0.
