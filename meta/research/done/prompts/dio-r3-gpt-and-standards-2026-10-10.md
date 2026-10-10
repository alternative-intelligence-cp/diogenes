# dio-r3-gpt-and-standards-2026-10-10

First read `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md` in full. Then answer the question below as a dated, sourced digest, in the format that file gives.

**Your question has two parts:**
- how can OpenAI's agent harnesses, and the cross-harness standards, be integrated with an external coordination hub?
- what is the lowest common denominator across harnesses?

Cover:

1. **OpenAI Codex CLI** (github.com/openai/codex, developers.openai.com/codex):
   - MCP client support (`config.toml` `mcp_servers`, transports), and running Codex itself as an MCP server;
   - the `notify` setting, and any hooks;
   - `AGENTS.md`;
   - `codex exec` (non-interactive) and resume;
   - the sandbox modes (read-only, workspace-write, danger-full-access) and their network policy;
   - approval policies and profiles;
   - Codex cloud and the IDE extension, briefly;
   - which ChatGPT plans include Codex CLI usage.
2. **The OpenAI Agents SDK and Responses API:** MCP support, hosted and local, and handoffs. This matters only if a GPT auditor would run as a small program rather than as an interactive CLI.
3. **A quick survey** of other harnesses' integration surfaces, one row each, so that the design does not over-fit: Cursor (hooks, MCP), OpenCode, Goose, Cline, Aider, and Zed (Agent Client Protocol).
4. **The standards:**
   - MCP's current specification version, and the features that matter here: tools, resources and subscriptions, notifications, elicitation, sampling, long-running tasks, authorization;
   - `AGENTS.md`;
   - A2A (Agent2Agent) and its governance;
   - the Agentic AI Foundation, or any similar body, if it exists.

   Which of these do Claude Code, Gemini CLI, Antigravity and Codex CLI support?
5. **The lowest common denominator:** a table of harnesses × mechanisms (shell CLI, MCP tool, MCP push or notification, lifecycle hook, file inbox, HTTP) saying which work where, with sources.

End with a recommendation:
- which mechanism Diogenes should treat as the universal baseline;
- which mechanisms are per-harness accelerators;
- the experiments that would confirm it.
