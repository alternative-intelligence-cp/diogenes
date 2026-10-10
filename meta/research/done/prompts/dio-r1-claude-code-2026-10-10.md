# dio-r1-claude-code-2026-10-10

First read `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md` in full. Then answer the question below as a dated, sourced digest, in the format that file gives.

**Your question:** what are all the surfaces by which **Claude Code** (the CLI, version 2.1.x as of October 2026) can be integrated with an external coordination hub? The hub must deliver messages to sessions, and sessions must send, query and take locks through it.

Sources:
- the code.claude.com documentation;
- the anthropics/claude-code repository and its `CHANGELOG.md` (fetch raw.githubusercontent.com when a page is large, and ask WebFetch targeted questions);
- the Claude Agent SDK documentation.

Cover:

1. **Hooks.**
   - Every hook event as of now: PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStop, SessionStart, SessionEnd, Notification, PreCompact, and any newer ones.
   - For each event:
     - when it fires;
     - its JSON input (`session_id`, `transcript_path`, `cwd`, and an agent id for subagents?);
     - what its output can do: block, inject `additionalContext`, add a system message, continue or stop.
   - Can a hook run asynchronously, or wake a session?
   - Do hooks fire for subagents?
   - Can anything inject a message into an IDLE session (one waiting for user input), or only at the session's next activity?
2. **Pushing into a running or idle session from outside.** List every mechanism, whether documented or only in the changelog:
   - MCP server notifications, and any MCP "channels" or push feature;
   - the `Monitor` tool;
   - `SendMessage` and `ListAgents`: how they are addressed, and their scope (same machine? same user? same config directory? same account?);
   - Remote Control;
   - `-p` with `--resume` or `--continue`, and stream-json input;
   - scheduled wakeups;
   - push notifications to the user.

   Which of these work between two different accounts on one machine, by documentation or by design?
3. **MCP.**
   - Its transports (stdio, streamable HTTP, SSE), scopes, tools, resources and prompts.
   - Resource subscriptions and `list_changed` notifications, elicitation, OAuth, and per-server env and headers.
   - Does an MCP server run inside or outside the Bash sandbox?
   - Can a plugin bundle an MCP server, hooks and skills together?
4. **Headless use and the SDK.**
   - `claude -p`: its output formats, `--resume`, session ids and `--max-turns`.
   - The Claude Agent SDK (TypeScript and Python): can a small daemon built on it host or drive sessions? Does it accept subscription auth, or API keys only?
5. **Several accounts on one machine.**
   - What `CLAUDE_CONFIG_DIR` relocates: credentials, settings, sessions, memory, plugins, the cross-session sockets?
   - Login per config directory.
   - What the documentation says about Claude Code on Team or Enterprise seats (premium seats and their limits).
6. **The sandbox.**
   - Its settings: filesystem allow and deny lists, `network.allowedDomains`, Unix-socket and local-binding options, excluded commands.
   - Can a sandboxed shell command reach a local Unix socket or a localhost TCP port, and how is that allowed?
7. **Identity and telemetry** available to a hook or a status line:
   - session id, model, cost, context-window figures and rate-limit figures;
   - the status line's JSON input schema;
   - can a hook learn the session's NAME, as `ListAgents` shows it?
8. **Built-in multi-agent coordination**, such as "agent teams" or shared task lists and mailboxes:
   - what exists, and its status;
   - whether Diogenes could reuse it, or would conflict with it.

End with a **recommended integration design for Claude Code**, ranked by robustness:
- how a session RECEIVES (push by hook, pull by MCP tool or CLI, waking when idle);
- how it SENDS;
- how it holds a LOCK through a hub.

Add the experiments that would confirm the design, with exact settings or commands.
