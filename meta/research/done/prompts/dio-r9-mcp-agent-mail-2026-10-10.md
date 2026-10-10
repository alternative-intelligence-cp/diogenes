# dio-r9-mcp-agent-mail-2026-10-10

First read `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md`: the context, the author's messages, and the correction at its end. Then read these, in the filed Diogenes plan at `/home/randy/Workspace/REPOS/diogenes/meta/`:
- `REQUIREMENTS.md`, especially the ★ P0 set and DR-100 … DR-112;
- `DESIGN.md` §8 (prior art) and §10 (the P0 slice);
- `OPEN_QUESTIONS.md` DQ-16: build the small core, or trial MCP Agent Mail first?
- `research/done/dio-r6-prior-art-2026-10-10.md`, the first look at prior art.

**Your job: answer DQ-16 with evidence.** How much of Diogenes' P0 would **MCP Agent Mail** cover, and is the right move to adopt it, adapt it, borrow from it, or ignore it? Check **Beads** briefly too, the same way, since r6 named both.

Use primary sources: the project repositories, their READMEs, docs, source tree, issues and releases (fetch raw files from raw.githubusercontent.com, and use GitHub's web pages for issues and releases), plus the authors' own write-ups. Fetch large files several times with narrow prompts. Quote where the verdict rests on the wording.

Settle each of these, or mark it UNVERIFIED and say what you tried:

1. **What it is today** (October 2026): the language and runtime, the licence (is it compatible with Diogenes' AGPL-3.0?), the latest release and its date, activity (commits, issues, maintainers), and its dependencies.
2. **Its model:**
   - identities and naming;
   - mailboxes and threads;
   - how a message is sent and read: an MCP tool, a CLI, HTTP?
   - push or poll;
   - acknowledgements and read state;
   - **file reservations or leases:** semantics, expiry, fencing, enforcement (advisory or a hook?);
   - its store and its audit (git-backed? SQLite? FTS?);
   - any web UI;
   - multi-project scoping.
3. **Where it runs, and who can reach it:**
   - it is an MCP server. Stdio or HTTP? Which port and which auth?
   - can two Claude Code accounts with different `CLAUDE_CONFIG_DIR`s on one machine both use one instance?
   - can a SANDBOXED shell reach it? It cannot by socket or loopback, by the measurements in the first-hand file. Is the harness's MCP connection enough?
   - Gemini (Antigravity, `agy`) and Codex support.
4. **The mapping:** a table of every ★ P0 requirement and DR-100 … DR-112 against MCP Agent Mail: **covered**, **partial** (what is missing), **missing**, or **conflicts**. In particular:
   - delegation (tasks with claim, report and verify);
   - each account's room and meters;
   - waking an idle session;
   - presence;
   - the lease guard;
   - the author never writing SQL.
5. **The cost of each path:**
   - adopting it as the P0 core: what Diogenes must add around it, and the risk of depending on an outside project;
   - forking or adapting it;
   - borrowing its ideas (which ones) for a small native core.

End with a recommendation on DQ-16, with its reasons, and the experiments that would confirm it: exact install and test steps on this machine, using private instances and never the system databases.
