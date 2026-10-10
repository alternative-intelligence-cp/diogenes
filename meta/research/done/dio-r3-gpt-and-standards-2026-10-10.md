<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-r3-gpt-and-standards-2026-10-10.md: a read-only API-credits job (claude-sonnet-5-5,claude-haiku-5-5, 56/200 turns, $0.8295 by the CLI (the bill is about two-thirds)). Its prompt is prompts/dio-r3-gpt-and-standards-2026-10-10.md. -->

# Integrating OpenAI harnesses and cross-harness standards with Diogenes, and the lowest common denominator

Job: dio-r3-gpt-and-standards-2026-10-10 · Date: 2026-10-10 · Model: Sonnet 5.5 (claude-sonnet-5-5) · Tools: Read, WebSearch, WebFetch (no shell, so nothing was run or measured)

**Limits:**
- Every claim below comes from docs read today (2026-10-10), not from running software. Nothing was tested.
- OpenAI's docs moved from `developers.openai.com/codex/*` to `learn.chatgpt.com/docs/*` (308 redirects). I cite the new URLs.
- The Codex AGENTS.md page returned 404 on every URL I tried, so Codex's AGENTS.md discovery rules are **UNVERIFIED** here.
- Several long pages were truncated by the fetch tool: Claude Code hooks, Claude Code MCP, the Codex config reference, and the Codex app-server page. Claims about their unread tails are marked.
- The Antigravity, Cline, Aider and A2A-support rows lean on secondary sources or thin pages. They are marked.
- The Codex `notify` payload shape is from third-party write-ups, not the official docs.

## 1. OpenAI Codex CLI

Repo: github.com/openai/codex, Apache-2.0 (read 2026-10-10). The latest release I saw was 0.162.1 on 9 Oct 2026, with 0.163.0 alphas on 9–10 Oct ([releases](https://github.com/openai/codex/releases)). The cadence is very fast, so everything below can drift within weeks.

### MCP client
Source: [MCP page](https://learn.chatgpt.com/docs/extend/mcp?surface=cli) and [config reference](https://learn.chatgpt.com/docs/config-file/config-reference), read 2026-10-10.

- **Config location:** `~/.codex/config.toml`, or `.codex/config.toml` in trusted projects. Each server is a `[mcp_servers.<name>]` table. `codex mcp add|list|login` manage them.
- **Transports:**
  - stdio, with keys `command`, `args`, `env`, `env_vars`, `cwd`.
  - Streamable HTTP, with keys `url`, `bearer_token_env_var`, `http_headers`, `env_http_headers`, `http_headers_helper`.
- **Auth for HTTP servers:** OAuth by default (CIMD or DCR), or the `chatgpt` auth mode.
- **Per-server controls:** `startup_timeout_sec` (default 10), `tool_timeout_sec` (default 60), `enabled_tools`, `disabled_tools`, `tools.<tool>.approval_mode`, `required`.
- **Elicitation:**
  - It is gated by the `granular.mcp_elicitations` approval setting (config reference).
  - A third-party blog says server-driven elicitation arrived in v0.119/0.120, April 2026 ([blog](https://codex.danielvaughan.com/2026/04/11/codex-cli-mcp-maturation-resource-reads-outputschema/)). I did not confirm that against the changelog.
  - Under `danger-full-access`, elicitation is auto-approved (same blog).
- **Server push:** I found **no** documented way for an MCP server to push a message into a running Codex turn. I also found no confirmation that Codex handles `notifications/tools/list_changed`, so treat that as **UNVERIFIED**.
- **MCP spec 2026-07-28:** I found no evidence on whether Codex speaks it. That needs a test.

### Codex as an MCP server: removed
- The old `codex mcp-server` command, which exposed `codex` and `codex-reply` tools, **has been removed**. The docs page says "The `codex mcp-server` command and the standalone `codex-mcp-server` binary have been removed" ([page](https://learn.chatgpt.com/docs/mcp-server.md)).
- A third-party article dated 2026-08-25 had called it deprecated ([ccleaks](https://ccleaks.com/news/codex-mcp-server-deprecated-app-server-aug-2026)). The official page is stronger than that, so use the official wording.
- Many 2026 tutorials, including the OpenAI cookbook pattern via `MCPServerStdio`, are now stale.
- The replacement is **`codex app-server`**, described under "Codex app-server" below.

### `notify` and hooks
- **`notify`** is an argv array. Codex appends a JSON payload as the final argument (argv, not stdin). Sources for the payload and behaviour: [config reference](https://learn.chatgpt.com/docs/config-file/config-reference) for the key, and third-party guides for the rest (e.g. [samwize](https://samwize.com/2026/02/05/setup-codex-cli-notifications-on-macos-iterm2-terminal-notifier/)).
  - The reported fields are `type` (`agent-turn-complete`), `thread-id`, `turn-id`, `cwd`, `input-messages` and `last-assistant-message`.
  - As of August 2026 it fires only on turn completion, and approval requests do not reach it (issue 19921, per a search summary).
  - Third-party sources say it is ignored in a project's `.codex/config.toml`, so set it in the user config.
- **Hooks** are the better mechanism ([hooks page](https://learn.chatgpt.com/docs/hooks)):
  - **Events:** `SessionStart`, `SessionEnd`, `SubagentStart`, `SubagentStop`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `Stop`, `PreCompact`, `PostCompact`, `Interrupt`.
  - **Config locations:** `~/.codex/hooks.json`, `~/.codex/config.toml`, `<repo>/.codex/hooks.json`, `<repo>/.codex/config.toml`, plugin-bundled hooks, and admin `requirements.toml`.
  - **Input and output:** JSON on stdin (`session_id`, `transcript_path`, `cwd`, `hook_event_name`, `model`). Exit code 2 or `decision: block` blocks the action. `PreToolUse` can rewrite input via `updatedInput`.
  - **Context injection:** stdout from `SessionStart` and `UserPromptSubmit` hooks becomes developer context.
  - **Handler types:** command and MCP-tool handlers run. Prompt and agent handlers are parsed but skipped.
  - **Status:** enabled by default. Non-managed hooks must be reviewed with `/hooks` before they run, and project hooks load only when the project is trusted.
  - **Origin:** a third-party source says hooks arrived around 0.144, modelled on Claude Code's. This is not confirmed in the docs.

### AGENTS.md
- OpenAI originated the format. It is now stewarded by AAIF ([agents.md](https://agents.md), read 2026-10-10).
- The agents.md site lists Codex, Gemini CLI, Cursor, Aider, goose, opencode, Zed, Amp and others. It does not list Claude Code (see section 4).
- Codex config keys: `project_doc_max_bytes` and `project_doc_fallback_filenames` (config reference).
- Codex's exact discovery and override rules are **UNVERIFIED** (see Limits).
- In the sandbox, `.agents/`, `.codex/` and `.git` are read-only when they exist ([security doc](https://learn.chatgpt.com/docs/agent-approvals-security)). Codex cannot rewrite its own rules, but a worker in a Codex sandbox also cannot write to those paths.

### `codex exec` (non-interactive) and resume
Source: [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode).

- The final message goes to stdout and progress goes to stderr.
- Flags: `--json` (JSONL events `thread.started`, `turn.*`, `item.*`), `-o/--output-last-message`, `--output-schema`, `--ephemeral`, `--sandbox`, `--skip-git-repo-check`, `--ignore-user-config`, `--ignore-rules`.
- `--full-auto` is deprecated in favour of `--sandbox workspace-write`.
- The default sandbox for exec is **read-only**.
- Resume: `codex exec resume --last "<prompt>"` or `codex exec resume <SESSION_ID> "<prompt>"`.
- Auth: saved CLI credentials, or `CODEX_API_KEY` for a single invocation.

### Sandbox, network, approvals, profiles
Source: [agent approvals & security](https://learn.chatgpt.com/docs/agent-approvals-security) and the config reference.

- **Modes:** `read-only`, `workspace-write`, `danger-full-access`.
- **Network:** off by default for the CLI, app and IDE. In `workspace-write`, enable it with `[sandbox_workspace_write] network_access = true`.
  - An optional `features.network_proxy` (off by default) enforces per-domain allow/deny rules, and deny wins.
  - Local and private destinations are blocked by default (`allow_local_binding = false`).
  - **Implication:** a localhost Diogenes service is likely unreachable from a default Codex sandbox. This is a prediction from the docs, not a test.
- **Linux implementation:** bubblewrap plus seccomp.
- **Approval policies:** `on-request`, `never`, or `granular = {sandbox_approval, rules, mcp_elicitations, request_permissions, skill_approval}`. `untrusted` is retired and can prevent startup. `on-failure` is deprecated. `approvals_reviewer = "auto_review"` routes eligible requests to a reviewer agent.
- **Profiles:** `$CODEX_HOME/<name>.config.toml`, selected with `--profile`. Project-local config ignores `profile`. There are also named `permissions.<name>` profiles, which should not be combined with `sandbox_mode`.

### app-server: the programmatic surface
Source: [app-server page](https://learn.chatgpt.com/docs/app-server), read 2026-10-10 (first 100k characters of 140k).

- It speaks JSON-RPC 2.0 over stdio by default. WebSocket and Unix-socket transports exist but are **experimental and not supported for production**.
- Primitives are thread, turn and item. Methods include `thread/start|resume|fork|list`, `turn/start`, **`turn/steer`** (add input to an active turn) and `turn/interrupt`.
- It sends notifications (`turn/completed`, `item/*`, `thread/status/changed`), and a thread can report `waitingOnApproval`.
- The docs recommend the Codex SDK, not app-server, for CI and automation.
- `turn/steer` plus `thread/status/changed` is the closest thing to a push channel on Codex. It requires running Codex under a wrapper that owns the app-server connection.

### Cloud, IDE and plans
- **IDE extension** ([page](https://learn.chatgpt.com/docs/ide)): VS Code, Cursor, Windsurf, Xcode and JetBrains.
- **Cloud** ([page](https://learn.chatgpt.com/docs/cloud)): parallel tasks in per-task cloud environments with GitHub integration and an internet-access toggle. The default network setting is not stated on the page (**UNVERIFIED**). It is irrelevant to a local hub except that cloud tasks cannot reach `localhost`.
- **Plans** ([pricing](https://learn.chatgpt.com/docs/pricing)):
  - Codex is included in Free, Go, Plus ($20), Pro (from $100), Business, Edu and Enterprise.
  - The CLI is explicitly listed for Plus, Pro, Business, Enterprise/Edu and API key. It is not explicitly listed for Free or Go.
  - Plus limits are per five-hour window and vary by model. Pro currently has no five-hour limit.
  - API-key use is billed at API rates and excludes cloud features.
  - The pricing page names GPT-6.1 Sol and GPT-6 Luna. I did not research those models.

## 2. OpenAI Agents SDK and Responses API

Relevant only if a GPT auditor runs as a small program rather than as the Codex CLI.

- **Agents SDK (Python)** ([MCP docs](https://openai.github.io/openai-agents-python/mcp/)):
  - It offers `MCPServerStdio` and `MCPServerStreamableHttp`, and `MCPServerSse` for legacy servers.
  - Tool filters (static or dynamic) and `require_approval` control which tools run.
  - `HostedMCPTool` pushes the whole round-trip to OpenAI infrastructure.
  - The page documents no notification or push handling.
  - `ignore_initialized_notification_failure` is supported only with `mcp<2`, so the SDK is mid-migration to MCP SDK v2.
- **Responses API remote MCP tool** ([guide](https://developers.openai.com/api/docs/guides/tools-connectors-mcp)):
  - The tool is `type: "mcp"` with `server_url` (Streamable HTTP or HTTP/SSE), `allowed_tools`, `require_approval` and `authorization` (an OAuth token that must be sent on every request).
  - **The server must be reachable on the public internet.** For private servers the page points to a "Secure MCP Tunnel" (`tunnel_id`).
  - A local Diogenes would therefore need the local-MCP path (`MCPServerStreamableHttp` or stdio run by the program), not the hosted tool.
  - The `connector_id` form is deprecated for models released after 2026-09-01.
- **Handoffs** ([docs](https://openai.github.io/openai-agents-python/handoffs/)):
  - A handoff is a tool, `transfer_to_<agent>`, that moves control to another agent.
  - It is scoped to a single run and in-process.
  - It is not a cross-process or cross-vendor mechanism, so it is **not** a way to talk to Claude or Gemini seats.
  - Diogenes should not model coordination on handoffs. If an Agents SDK auditor needs coordination, it calls Diogenes tools like any MCP client.

## 3. Other harnesses (one row each)

| Harness | Integration surface | Source and confidence |
|---|---|---|
| **Cursor** | `hooks.json` (versioned) at project, user, team and enterprise levels. Events: `preToolUse`, `beforeShellExecution`, `beforeMCPExecution`/`afterMCPExecution`, `afterFileEdit`, `subagentStart`, `stop`, `workspaceOpen`. Command hooks (stdin/stdout JSON, exit 2 blocks) and prompt hooks. Cloud agents skip MCP hooks. MCP is supported (implied by the MCP hooks). AGENTS.md is not mentioned on the hooks page, but agents.md lists Cursor. | [Cursor hooks](https://cursor.com/docs/hooks) |
| **OpenCode** | JS/TS plugins (`.opencode/plugins/`) with events such as `session.idle`, `tool.execute.before/after`, `permission.asked`, `message.updated`, plus custom tools. `opencode serve` is a headless HTTP server with OpenAPI, an SSE stream at `/event`, `POST /session/:id/prompt_async`, basic auth via `OPENCODE_SERVER_PASSWORD`, and an ACP page. This is the best pure-HTTP integration of the group. | [plugins](https://opencode.ai/docs/plugins/), [server](https://opencode.ai/docs/server/) |
| **Goose** | MCP "extensions" over stdio or Streamable HTTP, with OAuth for remote ones. Hosted by AAIF (repo moved to `aaif-goose/goose`). Headless mode, recipes, ACP and hooks were not covered by the page I read (**UNVERIFIED**). | [extensions](https://goose-docs.ai/docs/getting-started/using-extensions), [AAIF move](https://goose-docs.ai/blog/2026/04/07/goose-moves-to-aaif/) |
| **Cline** | MCP over stdio, Streamable HTTP (set `"type":"streamableHttp"` explicitly) or legacy SSE. The CLI shares the settings file (`cline mcp add`, `cline config mcp --json`). Hooks and AGENTS.md were not covered by the page (**UNVERIFIED**). | [Cline MCP](https://docs.cline.bot/mcp/mcp-overview) |
| **Aider** | CLI scripting only: `--message`/`-m` runs one instruction and exits, `--yes` auto-confirms, and there is an unsupported Python API. `/run` and `/test` run shell commands. MCP and AGENTS.md support were not found on the pages read (**UNVERIFIED**). agents.md lists Aider. | [scripting](https://aider.chat/docs/scripting.html), [commands](https://aider.chat/docs/usage/commands.html) |
| **Zed / ACP** | Agent Client Protocol: JSON-RPC over stdio to an agent subprocess. Zed hosts Claude Agent, Codex, Gemini CLI, OpenCode, Copilot, Cursor and others as external agents. Zed may forward its MCP servers to agents over ACP. ACP is an editor-to-agent protocol, not agent-to-agent. I could not confirm who maintains it or its version. | [ACP intro](https://agentclientprotocol.com/overview/introduction), [Zed docs](https://zed.dev/docs/ai/external-agents) |

## 4. The standards

### MCP
- **Current spec: 2026-07-28**, read at [spec](https://modelcontextprotocol.io/specification/latest) and [changelog](https://modelcontextprotocol.io/specification/2026-07-28/changelog), 2026-10-10. The previous revision was 2025-11-25.
- **It is a large change, and several features Randy might assume are shifting:**
  - **Stateless.** There is no `initialize` handshake and no `Mcp-Session-Id`. Each request carries its version and capabilities in `_meta`. A new `server/discover` RPC is added.
  - **Subscriptions.** `resources/subscribe` and `unsubscribe` and the HTTP GET stream are replaced by `subscriptions/listen`, one long-lived POST-response stream for opted-in change notifications (`toolsListChanged`, `resourcesListChanged`, `resourceSubscriptions` and so on).
  - **Streams are not resumable.** SSE resumability and `Last-Event-ID` redelivery are removed. A broken stream loses the in-flight request, so **notifications are a hint, not guaranteed delivery.**
  - **Tasks** moved out of core into the extension `io.modelcontextprotocol/tasks`. It uses polling via `tasks/get` and `tasks/update`, and servers may return task handles unsolicited.
  - **Server-to-client requests** are replaced by **multi round-trip requests (MRTR)**. This covers elicitation, sampling and roots. The server returns `resultType: "input_required"` with `inputRequests`, and the client retries with `inputResponses`. The `notifications/elicitation/complete` notification is removed.
  - **Deprecated:** Roots, Sampling and Logging (SEP-2577), HTTP+SSE, and OAuth Dynamic Client Registration in favour of Client ID Metadata Documents. There is a minimum 12-month deprecation window.
  - **Authorization** adds RFC 9207 `iss` validation, credential binding to the issuing authorization server, and `application_type` on registration.
  - **Caching:** `ttlMs` and `cacheScope` are now required on list and read results, which reduces the need to poll.
  - **Governance:** a formal feature lifecycle and SEP process.
- **What this means:**
  - **Sampling is deprecated.** Do not design on it.
  - **Tasks** are an optional extension. Support is negotiated and uneven.
  - Pushing to an idle agent is not something core MCP does at all. Only the opted-in `subscriptions/listen` stream carries change notices, and the client application decides what to do with them.

### AGENTS.md
- A plain-Markdown convention. The nearest file wins and explicit user prompts override it. It is stewarded by AAIF ([agents.md](https://agents.md)).
- **Support:**
  - Codex: yes.
  - Gemini CLI: listed on agents.md.
  - Antigravity: reads GEMINI.md and AGENTS.md (secondary source: [search summary of Gemini API docs and CLI release notes](https://ai.google.dev/gemini-api/docs/antigravity-agent)).
  - **Claude Code: NOT on the agents.md list.** I did not check Claude Code's own docs for AGENTS.md handling, so this is **UNVERIFIED**. The established workaround is a `CLAUDE.md` that points at AGENTS.md. Randy should check what his version 2.1.296 does.

### A2A (Agent2Agent)
- **v1.0.0** is the latest I found. Sources disagree on the date (March 2026 most likely, one says 9 April). It has three bindings (JSON-RPC, gRPC, HTTP/REST), Signed Agent Cards and multi-tenancy ([spec](https://a2a-protocol.org/latest/specification/), secondary summaries).
- Google donated it to the Linux Foundation in June 2025. On 2026-08-17 it joined the AAIF as a hosted project ([AAIF blog](https://aaif.io/blog/a2a-joins-aaif)).
- **Harness support:** I found no evidence that Claude Code, Gemini CLI, Antigravity or Codex CLI act as A2A clients or servers. Treat as **UNVERIFIED, probably not natively**. A2A is aimed at networked agent services, not local CLI sessions.

### AAIF
- The Agentic AI Foundation was formed under the Linux Foundation on 2025-12-09 with MCP, goose and AGENTS.md as founding projects. Platinum members are AWS, Anthropic, Block, Bloomberg, Cloudflare, Google, Microsoft and OpenAI ([LF press release](https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation)).
- agentgateway and A2A were added later. A 2026-05-18 update reported about 190 members (secondary).

### Support matrix: standards

| | MCP (client) | MCP 2026-07-28 | AGENTS.md | A2A |
|---|---|---|---|---|
| Claude Code | Yes: stdio, HTTP, deprecated SSE, `ws` | Yes on the v2 client runtime (default on v2.1.232+ with feature flags, v2.1.274+ otherwise); override with `MCP_PROTOCOL_NEGOTIATION=legacy` | **UNVERIFIED**; not on agents.md list | Not found |
| Gemini CLI | Yes: stdio, SSE, HTTP; resources and prompts; OAuth with `iss` check | **UNVERIFIED** | Listed on agents.md | Not found |
| Antigravity | Yes: `mcp_config.json` with `command` or `serverUrl`; `_meta` `antigravity/alwaysLoad` | **UNVERIFIED** | Reads AGENTS.md and GEMINI.md (secondary) | Not found |
| Codex CLI | Yes: stdio and Streamable HTTP; elicitation gated | **UNVERIFIED** | Yes | Not found |

Sources for the table: Claude Code [MCP docs](https://code.claude.com/docs/en/mcp); Gemini [MCP page](https://geminicli.com/docs/tools/mcp-server/); Antigravity [search summary](https://ai.google.dev/gemini-api/docs/antigravity-agent) (secondary); Codex pages above. Note that Gemini CLI was replaced by Antigravity CLI for unpaid and Google One users on 2026-06-18 (same Gemini page). Randy's Gemini work is already in Antigravity, so I treat Antigravity as the target and Gemini CLI as legacy.

## 5. Lowest-common-denominator table

Legend: ✅ documented, 🟡 partial or conditional, ❌ not found or not available, ? unverified.

| Mechanism | Claude Code | Antigravity / Gemini | Codex CLI | Cursor | OpenCode | Goose | Cline | Aider |
|---|---|---|---|---|---|---|---|---|
| **Shell CLI** (agent runs `diogenes ...` via its shell tool) | ✅ Bash tool, sandboxed network allowlist | ✅ (terminal agent; Antigravity hooks exist) ? sandbox | 🟡 shell tool, but network off by default in the sandbox | ✅ | ✅ | ? | ? | 🟡 `/run` only |
| **MCP tool** (agent calls Diogenes MCP tools) | ✅ | ✅ | ✅ | ✅ (implied) | ✅ (not read) | ✅ | ✅ | ? |
| **MCP push or notification into a live turn** | 🟡 channels: research preview, allowlisted plugins or a dev flag, stdio only, interactive only. **Not registered when the server negotiates 2026-07-28.** `list_changed` refreshes tool lists | ❌ not found | ❌ not found (app-server `turn/steer` is a wrapper-side alternative) | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Lifecycle hook** (can inject context or run a script) | ✅ 33 events; command, http, mcp_tool handlers; `additionalContext` | ✅ Antigravity: PreToolUse, PostToolUse, PreInvocation, PostInvocation, Stop (secondary). Gemini CLI: `BeforeAgent`, `AfterAgent`, `BeforeTool`, `AfterTool`, `Notification`, command only | ✅ 12+ events; command and MCP-tool; stdout becomes context on SessionStart and UserPromptSubmit; needs trust review | ✅ command, prompt; cloud subset | ✅ plugins | ? | ? | ❌ |
| **File inbox** (agent reads a file or directory) | ✅ via Read/Bash | ✅ | ✅ within workspace; `.codex/` and `.git` are read-only to the agent, outside the workspace is blocked | ✅ | ✅ | ✅ | ✅ | ✅ |
| **HTTP** (agent or its hook calls a Diogenes URL) | ✅ `http` hook handler; MCP over HTTP | ✅ MCP `serverUrl` | 🟡 MCP HTTP is native, but a sandboxed shell has no network by default | 🟡 hooks are scripts; MCP URL | ✅ native server API | ✅ MCP HTTP | ✅ MCP HTTP | ❌ |

Sources: the per-harness pages cited in sections 1 to 4. The Cline, Goose and Aider hook cells are unverified because those pages did not cover hooks.

**What holds for every harness:**
1. The agent can read and write files in its workspace, and run a shell command. The sandbox's network and path limits vary.
2. All the harnesses I could confirm, except Aider, speak MCP over stdio and Streamable HTTP as a client.
3. Nothing in the confirmed set offers push into an idle or mid-turn agent except Claude Code channels (restricted) and a Codex app-server wrapper.

**Therefore:** the true lowest common denominator is "the agent can call a tool, and can read what a tool returns". Delivery to an agent that is not currently running a turn does not exist as a common mechanism. It needs a poll at turn boundaries, a hook, or a human or wrapper nudge.

## What this means for Diogenes

1. **The baseline is a pull at turn boundaries, over MCP tools (Streamable HTTP) and a CLI that wraps the same API.** Finding: MCP-as-client is the only mechanism confirmed across all four required harnesses, and nothing common pushes into an idle agent. The CLI equivalent covers Aider and any agent without MCP.
   - Caveat: the Codex default sandbox has network off, and local and private destinations are blocked even with the proxy feature. A localhost-only Diogenes may be unreachable from a Codex sandbox until `network_access = true` or an allowlist is set. Prefer stdio MCP servers, which run outside the shell sandbox, for Codex.
2. **A file inbox is the fallback floor.** Finding: every harness can read a file. The existing `messages/` inbox convention maps directly. Diogenes should write inbox files as a projection of its store so the Gemini and Claude paths keep working if the service is down. This also contains the "agent in a locked-down sandbox" case, where only a mounted directory is reachable.
3. **Hooks are the per-harness accelerator that removes the hand-relay.** Findings:
   - Claude Code, Codex, Cursor, OpenCode and Antigravity all have a hook that can run at session start or prompt submit, and at least Claude Code and Codex inject stdout or `additionalContext` into the model's context.
   - Claude Code and Codex hooks can also call an MCP tool.
   - So the design is: a tiny `diogenes inbox --since` call in `UserPromptSubmit` or `PostToolUse`, with the result injected as context.
   - Remember that injected text is data, not instruction, and has caps (Claude Code: 10,000 characters; Codex: `additionalContextLimit` default 2,500).
4. **Do not depend on MCP notifications or channels for correctness.** Findings:
   - Spec 2026-07-28 removes stream redelivery, so notifications are lossy hints.
   - Channels are a research preview, require an allowlist or dev flag, and **do not register on servers that negotiate the new revision**, which means a channel server must pin the legacy protocol.
   - Treat channels as an optional accelerator for Claude Code only, behind a feature check.
5. **Use a sequence cursor, not event delivery.** Finding: because delivery is unreliable and Codex binds a call to a tool-catalog revision, every Diogenes message needs a monotonic id, and `inbox(since=cursor)` must be idempotent. This also makes the "delivery confirmation needs the author" problem solvable: an ack tool call is the confirmation.
6. **Plan for MCP 2026-07-28 statelessness.** Findings: no sessions, no `initialize`, per-request capabilities. Diogenes MCP tools should carry any state in explicit arguments (for example a `session_token` or handle), as SEP-2567 prescribes. Do not use Sampling (deprecated). If any flow needs human approval, MRTR-style elicitation is the spec pattern, but Codex gates it behind `mcp_elicitations` and a headless Codex will auto-reject it.
7. **Do not target A2A or handoffs now.** Findings: no confirmed harness supports A2A as a client, and Agents SDK handoffs are in-process. A2A is worth a thin adapter later if a GPT auditor runs as a networked service.
8. **A GPT auditor has two shapes:**
   - Interactive Codex CLI: stdio MCP plus hooks, with config distributed via `.codex/config.toml` (trusted projects) and `~/.codex/config.toml`.
   - A small program: the Agents SDK with `MCPServerStreamableHttp` or stdio.
   - Avoid the Responses API hosted MCP tool for a local hub (it needs a public URL).
   - Use `codex exec --json` for one-shot audits, with `-o` and `--output-schema` to get structured results that Diogenes can ingest directly. `exec resume` gives a follow-up path.
9. **Capture identity per harness, because the sandbox models differ.** Findings: Codex protects `.git`, `.agents` and `.codex` even inside a writable root, and Claude Code's MCP servers sit outside its shell sandbox. Per-agent credentials (the per-role database user idea) should be passed via env var or `bearer_token_env_var`, not files in the workspace. Codex supports `bearer_token_env_var`, Claude Code supports `headersHelper`, and Gemini and Cline support header or env config.
10. **Keep instructions in AGENTS.md.** Findings: AGENTS.md is the shared convention, stewarded by AAIF, and Codex, Gemini CLI and Antigravity read it. Put the Diogenes protocol notice there, and add a `CLAUDE.md` shim for Claude Code unless it is confirmed to read AGENTS.md.

### Recommendation

- **Universal baseline:** MCP tools over Streamable HTTP (or stdio for sandboxed harnesses), backed by an idempotent cursor-based `inbox`/`ack` API, with an identical CLI and a file-inbox projection as fallbacks. Every agent polls at turn boundaries, and instructions in AGENTS.md tell it to.
- **Per-harness accelerators (optional, never required):**
  - Claude Code: `UserPromptSubmit`/`PostToolUse` hooks with an `http` or `mcp_tool` handler. Channels as an experiment.
  - Codex: hooks with the MCP-tool handler. `exec resume` for audits. An app-server wrapper with `turn/steer` only if real push is wanted.
  - Antigravity and Gemini: command hooks (PreInvocation or `BeforeAgent`).
  - Cursor: `stop` or `beforeMCPExecution` hooks.
  - OpenCode: `session.idle` plugin event, or `prompt_async` on its HTTP server for true push.

### Experiments that would confirm this (each cheap and runnable next week)

1. **Codex sandbox reachability:** run a stub Diogenes on `127.0.0.1`, then test shell `curl`, HTTP MCP, and stdio MCP from a default `workspace-write` session, then with `network_access = true`. Expect shell and HTTP to fail by default and stdio to work.
2. **Codex hook injection:** a `UserPromptSubmit` command hook that prints a canary line. Confirm the model sees it, the 2,500-character cap, and whether trust review blocks it headless (`codex exec`).
3. **Codex versus MCP 2026-07-28:** point Codex and Antigravity at a spec-2026-07-28 server and a legacy server. Record the negotiated revision and whether `list_changed` or `subscriptions/listen` updates reach the agent.
4. **Claude Code channels:** build the documented webhook channel, run it with the dev flag under two `CLAUDE_CONFIG_DIR`s (the Max and Team accounts), and confirm delivery, and that it fails on a 2026-07-28 negotiation as documented.
5. **Cross-account `SendMessage`:** still the highest priority and still untested per the shared context. Run it first, since it decides whether Diogenes needs a Claude-to-Claude path at all.
6. **Antigravity hooks and AGENTS.md:** verify `PreInvocation` can inject context, and that `AGENTS.md` is read alongside `GEMINI.md`. The evidence here was secondary.
7. **Claude Code and AGENTS.md:** check what 2.1.296 does, and whether a `CLAUDE.md` shim is needed.
8. **`codex exec --output-schema`:** run a canned audit and check the JSON matches a schema Diogenes ingests.

## Open questions

- Will Codex adopt MCP 2026-07-28, and will it ever push or consume subscription notices? I found no signal either way.
- Does Antigravity's hook output feed context to the model, or only gate tool calls? Only secondary sources were available.
- Is Codex's `app-server` stable enough for a wrapper? It is labelled experimental and unsupported for production, while OpenAI is steering integrations toward it.
- Do Cline, Goose and Aider offer any hook or event surface? These pages did not say.
- Does Claude Code read AGENTS.md natively?
- Which ChatGPT plan will Randy use for a GPT auditor? Plus covers CLI use, but limits are per five-hour window and model-dependent, so an audit-heavy workflow may fit better on API-key billing.

**Outside my question:** on 2026-06-18 Gemini CLI was replaced by Antigravity CLI for unpaid and Google One users (Gemini MCP page). If Randy's setup or any docs he follows still say "Gemini CLI", check which binary he actually has.