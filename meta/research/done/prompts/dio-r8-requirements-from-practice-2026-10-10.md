# dio-r8-requirements-from-practice-2026-10-10

First read `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md` in full. Then answer the question below as a report, in the format that file gives. You have no web access, so the "primary sources" are the files below.

**Your question:** from the author's actual practice, what must Diogenes do? Extract a numbered inventory of requirements, each traced to the file and line, or the memory, that motivates it.

**Read these sources.** Use Grep to find passages rather than reading huge files whole: `BOARD.md` and `RECORD.md` in the workbench are over 1 MB each, so search them.

- **The library workbench,** `/home/randy/Workspace/REPOS/nitpick-libs`:
  - `CLAUDE.md`, `README.md` and `WORKSTREAMS.md` (the rules W-1 … W-28, especially W-8, W-16, W-19, W-21, W-23, W-24 and W-25);
  - `skills/orchestrate/SKILL.md`, `skills/worker/SKILL.md` and `skills/check/`;
  - `BOARD.md`: the writer line at line 14, the handoff block from line 17, and the take hazards (grep "hazard");
  - `RECORD.md`: grep for "SendMessage", "inbox", "relay", "delivery", "acknowledg", "rotation", "handoff", "lock" and "logs without replying";
  - `.internal/credits/README.md`.
- **The author's memory directory,** `/home/randy/.claude/projects/-home-randy-Workspace-REPOS-nitpick-libs/memory/` (`MEMORY.md` is the index). Read every memory about sessions, handoffs, messaging, peers, quotas, Gemini, the test VM, diogenes, devTeam, verification, and the author's attention.
- **The Gemini file inboxes,** `/home/randy/Workspace/META/NITPICK/messages/`: how the convention works in practice, and where it hurt.
- **The devTeam plugin,** `/home/randy/Workspace/REPOS/claude-skills/plugins/devteam/`: `README.md`, `DESIGN.md` and `PROTOCOL.md`, plus its skills and agents as needed. Look at its board, writer lock, write scopes, escalation, sandbox and permission grant.
- **The diogenes skeleton,** `/home/randy/Workspace/REPOS/diogenes`: `meta/README.md` and `.internal/README.md`.

**Produce:**

1. **The pains, each with its evidence.** What has gone wrong in coordination, or cost the author attention? Examples to check, not to assume:
   - manual relays;
   - lost or unconfirmed messages;
   - the lock hazards;
   - compaction losing conventions;
   - identity confusion after renames;
   - seats that only log;
   - meters read by hand.
2. **Requirements R-1 … R-n.**
   - Each one states what Diogenes must do in one testable sentence, cites the motivating file:line or memory name, and carries a priority:
     - **P0:** needed when the second Claude account arrives;
     - **P1:** Gemini via Antigravity;
     - **P2:** a GPT auditor;
     - **P3:** devTeam and later.
   - Group them as: messaging; presence and roster; locks and claims; boards and state; handoffs; telemetry; research and memory; access and audit; human surfaces.
3. **What must NOT change.** The practices that work and that Diogenes must preserve rather than replace: authentication by content, records as the storage, verification before relay, and any others you find.
4. **What the orchestrator seat and its subagents would use most,** concretely. For example: subagents cannot receive cross-session messages today, and a background agent's progress is invisible until it reports.

Check every quotation against its file before you cite it.
