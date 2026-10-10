<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-r2-gemini-antigravity-2026-10-10.md: a read-only API-credits job (claude-sonnet-5-5,claude-haiku-5-5, 46/200 turns, $0.8743 by the CLI (the bill is about two-thirds)). Its prompt is prompts/dio-r2-gemini-antigravity-2026-10-10.md. -->

# Gemini CLI and Google Antigravity: integration surfaces for an external coordination hub

Job: dio-r2-gemini-antigravity-2026-10-10 · Date: 2026-10-10 · Model: Sonnet 5.5 · Tools: Read, WebSearch, WebFetch (read-only; nothing was run or measured)

**Limits:**
- Nothing was executed, so every behavioural claim is from documentation or third-party write-ups, not measured.
- WebFetch summarises pages through a small model. Anything that matters should be re-read on the page itself before it goes into a roadmap.
- I could not read these pages:
  - the Gemini CLI `settings.json` reference and `GEMINI_SANDBOX` proxy details;
  - Antigravity "Knowledge" docs (I found none);
  - the Antigravity SDK triggers and hooks example code;
  - any Gemini CLI or `agy` release notes with version numbers beyond those quoted.
- Several third-party blogs (Medium, DataCamp, agenticcontrolplane.com) are cited only where marked as secondary.
- Antigravity docs change quickly: the MCP config path, workflow location and model list all differ across sources. Treat anything older than about 90 days as stale.

## 0. Headline finding: the author's Gemini harness is `agy`, not Gemini CLI

- **Gemini CLI is retired for the author's plan.**
  - On 2026-06-18 Gemini CLI and the Code Assist IDE extensions stopped serving requests for free, Google AI Pro and Ultra personal accounts.
  - The replacement is the Antigravity CLI. It is a closed-source Go binary called `agy`, and it shares the desktop app's agent harness.
  - Gemini CLI is still usable with a paid Gemini or Gemini Enterprise Agent Platform API key, or through a Code Assist Standard/Enterprise licence.
  - Sources, read 2026-10-10:
    - [Google Developers Blog, "Transitioning Gemini CLI to Antigravity CLI"](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/) (I saw only the search summary of this page, not the page itself);
    - [The Register, 2026-05-20](https://www.theregister.com/ai-ml/2026/05/20/bye-bye-gemini-cli-google-nudges-devs-toward-antigravity/5243605);
    - the banner on [geminicli.com/docs/extensions](https://geminicli.com/docs/extensions/).
- **Gemini CLI source status.** The [GitHub repo](https://github.com/google-gemini/gemini-cli) is Apache-2.0 with weekly preview and stable builds, and the page I read carried no deprecation banner.
- **Consequence for the author.** The AI Pro plan means the practical surface is Antigravity (2.0 desktop app, `agy` CLI, Python SDK). Gemini CLI is a secondary option that needs a paid API key.
  - Gemini CLI is still documented in §1 because it has the richest, best-documented hook and A2A surface, and it is the only Gemini route that is open source.

## 1. Gemini CLI (still available via API key or enterprise licence)

| Area | Finding | Source (read 2026-10-10) |
|---|---|---|
| MCP client | Three transports: stdio (`command`), SSE (`url`), Streamable HTTP (`httpUrl`). Config is `mcpServers` in `settings.json`, with `args`, `env`, `cwd`, `headers`, `timeout` (default 10 min), `includeTools` and `excludeTools`. `trust: true` skips confirmation for that server. OAuth for remote servers, with `/mcp auth`. Host env vars matching token, secret or key patterns are redacted from spawned servers unless listed in `env`. Docs do not mention MCP notifications or sampling. | [MCP docs](https://geminicli.com/docs/tools/mcp-server/) |
| Hooks | Yes. 11 events: `SessionStart`, `SessionEnd`, `BeforeAgent`, `AfterAgent`, `BeforeModel`, `AfterModel`, `BeforeToolSelection`, `BeforeTool`, `AfterTool`, `PreCompress`, `Notification`. Hooks are enabled by default as of v0.26.0 (2026-01-28 weekly update); the PR "enable hooks system by default" (#17247) appears in v0.27.0's notes. I could not confirm the release in which hooks first shipped as experimental. | [hooks](https://geminicli.com/docs/hooks/), [v0.27.0](https://github.com/google-gemini/gemini-cli/releases/tag/v0.27.0), [Developers Blog](https://developers.googleblog.com/tailor-gemini-cli-to-your-workflow-with-hooks/) |
| Hook I/O | Hooks read JSON on stdin and write one JSON object on stdout. Common input fields: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `timestamp`. Exit 0 means parse stdout; exit 2 blocks the action and uses stderr as the reason; any other exit is a warning. Config merges project `.gemini/settings.json`, user, `/etc/gemini-cli/settings.json`, then extensions. | [hooks](https://geminicli.com/docs/hooks/), [reference](https://geminicli.com/docs/hooks/reference/) |
| Hook injection | `BeforeAgent` can return `additionalContext`, which is added to the prompt for that turn. `AfterTool` can return `additionalContext` or `tailToolCallRequest`. `AfterAgent` can return `decision: deny` with a `reason`, which is sent as a new prompt and forces another turn (the Ralph-loop pattern). `SessionStart` can inject context; in non-interactive mode it is prepended to the prompt. `Notification` is observability only and cannot grant permission. | [reference](https://geminicli.com/docs/hooks/reference/) |
| Context files | `GEMINI.md` loads at global (`~/.gemini/`), workspace and just-in-time scopes, concatenated, with `@file` imports. `context.fileName` accepts a list such as `["AGENTS.md","GEMINI.md"]`. `/memory show` and `/memory reload`. | [GEMINI.md docs](https://geminicli.com/docs/cli/gemini-md/) |
| Extensions | Package prompts, MCP servers, commands, themes, hooks, sub-agents and skills. Install from a GitHub URL or local path. I could not read the manifest field list. | [extensions](https://geminicli.com/docs/extensions/) |
| Headless | `-p/--prompt`, and headless is automatic when there is no TTY. `--output-format` gives `json` (`response`, `stats`, `error`) or a streaming JSONL form with events `init`, `message`, `tool_use`, `tool_result`, `error`, `result`. Exit codes: 0 success, 1 error, 42 input error, 53 turn limit. The docs page does not describe stdin or approval behaviour in headless mode (UNVERIFIED). | [headless](https://geminicli.com/docs/cli/headless/) |
| Checkpointing | Off by default. Enable via `general.checkpointing.enabled`. Shadow git repo at `~/.gemini/history/<hash>` and JSON in `~/.gemini/tmp/<hash>/checkpoints`; `/restore`. The `--checkpointing` flag was removed in 0.11.0. Session resume was not on the page I read (UNVERIFIED). | [checkpointing](https://geminicli.com/docs/cli/checkpointing/) |
| Sandbox | macOS Seatbelt, Docker/Podman (default image `ghcr.io/google/gemini-cli:latest`), gVisor/`runsc` (Linux), experimental LXC, and a Windows native option. Enable with `-s`, `GEMINI_SANDBOX` or `tools.sandbox`. Seatbelt profiles are `{permissive,restrictive,strict}-{open,proxied}`, with the default `permissive-open` (network allowed). The `-proxied` profiles route traffic through a proxy; the page does not explain how to configure one. `SANDBOX_MOUNTS` is `from:to:opts`, with `ro` as default. On Linux the usual route is therefore Docker or Podman, and the network allowlist there is not documented on this page. | [sandbox](https://geminicli.com/docs/cli/sandbox/) |
| A2A | Client side only: remote subagents are `.md` files with YAML frontmatter in `.gemini/agents/` or `~/.gemini/agents/`. Fields are `kind: remote`, `name`, `agent_card_url` or `agent_card_json`, and `auth`. Auth types: `apiKey`, `http` (Bearer/Basic), `google-credentials` (only for `*.googleapis.com` and `*.run.app`), and `oauth` (PKCE). Secrets can be `$ENV` or `!command`. Honours `general.proxy` and `HTTP(S)_PROXY`. Enabled by default; `/agents list\|reload\|enable\|disable`. | [remote agents](https://geminicli.com/docs/core/remote-agents/), [subagents](https://geminicli.com/docs/core/subagents/) |

## 2. Google Antigravity (as of 2026-10-10)

### 2.1 What it is

- **Announced 2026-05-19 at I/O** ([Antigravity blog](https://antigravity.google/blog/google-io-2026/), [TechCrunch](https://techcrunch.com/2026/05/19/google-launches-antigravity-2-0-with-an-updated-desktop-app-and-cli-tool/)). It has four parts:
  - **Antigravity 2.0**, a standalone desktop "command center". It runs agents across projects, workspaces and worktrees, with parallel local subagents, scheduled tasks and voice.
  - **The Antigravity IDE**, the editor, which still exists with an agent side panel and a review-changes editor. One secondary source says the initial 2.0 release removed the built-in IDE and drew backlash (UNVERIFIED).
  - **The browser**, a Chrome-based agent browser with an allowlist and denylist, recordings and a separate Chrome profile ([docs home](https://antigravity.google/docs/home/)).
  - **`agy`**, the CLI, and a **Python SDK** in preview (`pip install google-antigravity`) ([SDK overview](https://antigravity.google/docs/sdk/overview/)). One secondary source claims Python, TypeScript and Go; the official page says Python only.
- **Gemini API Managed Agents.** The Antigravity harness is also hosted in the Gemini API ([quickstart](https://ai.google.dev/gemini-api/docs/managed-agents-quickstart), via search summary): `client.interactions.create(agent="antigravity-preview-09-2026", environment="remote", …)`. See §3.

### 2.2 Tools, approval and sandbox

- **Permissions** ([agy features](https://antigravity.google/docs/cli/features/), [agenticcontrolplane.com, secondary](https://agenticcontrolplane.com/controls/antigravity)):
  - Autonomy levels (`/permissions`): `request-review`, `always-proceed`, `strict`.
  - `allow`, `ask` and `deny` rules in `~/.gemini/antigravity-cli/settings.json`, in the form `action(target)`. Actions are `read_file`, `write_file`, `read_url`, `execute_url`, `command`, `mcp`, `unsandboxed`. Deny beats ask beats allow.
  - Files inside the workspace are auto-allowed. Commands, MCP tools, URLs and out-of-workspace files default to ask.
  - `--dangerously-skip-permissions` approves everything. One secondary source says it also skips hooks, verified on agy 1.1.21.
  - Modes via `--mode`: `default` (diff review), `accept-edits`, `plan` ([modes](https://antigravity.google/docs/cli/modes/)).
- **Terminal sandbox.** `enableTerminalSandbox` is off by default. It uses `nsjail` on Linux. The approval prompt then offers "run without sandbox restrictions". The network policy is not documented (UNVERIFIED). Read, write and MCP tools are likely outside it, as in Claude Code, but I did not find that stated.

### 2.3 MCP

Source: [MCP docs](https://antigravity.google/docs/mcp/), read 2026-10-10.

- Config is `~/.gemini/config/mcp_config.json` (global, shared by IDE, CLI and SDK) or `.agents/mcp_config.json` (workspace).
- The file has a single `mcpServers` key. Each entry has either `command` (stdio) or `serverUrl` (Streamable HTTP or SSE). Legacy `url` and `httpUrl` are NOT supported, so a Gemini CLI config copied over will fail silently. Third-party migration guides say the same.
- Optional fields: `args`, `env`, `cwd`, `headers`, `authProviderType: "google_credentials"`, `oauth`, `disabled`, `disabledTools`.
- Auth is OAuth (tokens in `~/.gemini/antigravity/mcp_oauth_tokens.json`), ADC, or a static bearer token in `headers`.
- MCP tools default to Ask. Pre-approve with `mcp(server/tool)`, `mcp(server/*)` or `mcp(*)`.
- **No documented trust flag and no documented MCP notification or sampling support.**
- The 2.0 desktop app manages servers in a settings UI instead of a file path.

### 2.4 Rules, skills, workflows, knowledge

Source: [rules](https://antigravity.google/docs/rules/), read 2026-10-10.

- `AGENTS.md` or `GEMINI.md` in any directory, with no frontmatter, always on. Also `.agents/rules/*.md`, which require `trigger: always_on|model_decision|glob|manual` frontmatter and are silently discarded without it.
- Global files: `~/.gemini/{AGENTS,GEMINI}.md` and `~/.gemini/config/rules/`.
- Limits: 24 KB per rule file, and a shared 20,000-token budget for global and `always_on` rules. `.agents/rules.json` can `inherits` other rule sets.
- Skills are in `.agents/skills/<name>/` or `~/.gemini/config/skills/`. Workflows are in `.agents/workflows/`, and a "workflows to skills" migration page exists, so workflows may be being absorbed into skills.
- **Knowledge files: I found no official documentation (UNVERIFIED).**
- Plugins (the old Gemini CLI extensions) bundle skills, agents, rules, MCP servers, hooks and sidecars. Install with `agy plugin install|list|enable|disable|uninstall`.

### 2.5 Hooks

Source: [hooks docs](https://antigravity.google/docs/hooks/), read 2026-10-10. This is the first official Google hook surface for `agy`, and it is documented.

- Files: `.agents/hooks.json` (workspace; one secondary source says it is behind folder trust), `~/.gemini/config/hooks.json`, and a plugin's `hooks.json`.
- Events:
  - `PreToolUse` and `PostToolUse` take a regex matcher on the tool name.
  - `PreInvocation` and `PostInvocation` run before and after each model call.
  - `Stop` runs when the execution loop terminates.
- Handler: `type: "command"` only, default timeout 30 s. Stdin and stdout are JSON in camelCase. Common fields: `conversationId`, `workspacePaths`, `transcriptPath`, `artifactDirectoryPath`, `modelName`.
- **Injection (the key capability for a hub):**
  - `PreInvocation` and `PostInvocation` can return `injectSteps`, an array of items that each carry a `toolCall`, `userMessage` or `ephemeralMessage`. This delivers a hub message into the agent's context at the next model call.
  - `PostInvocation` can return `terminationBehavior: force_continue`.
  - `Stop` can return `decision: "continue"` plus a `reason`, which is injected as a system message and keeps the agent running. `fullyIdle` is provided as input. A secondary source reports a cap on consecutive continuations.
  - `PreToolUse` returns `decision` (`allow`, `deny`, `ask`, `force_ask`, `deny_unless_prior_grant`) and can grant `permissionOverrides`.
- Caveats (secondary source, agy 1.1.21): there is no exit-code deny channel; a crash, timeout or non-zero exit fails closed and blocks the tool call; hooks get a sanitised environment (only whitelisted variables), so a hook must read its configuration from a file; the `PostToolUse` payload lacks tool output.

### 2.6 Unattended triggers, so an agent can check an inbox without a human

Source: [sidecars](https://antigravity.google/docs/sidecars/), read 2026-10-10.

- **Sidecars** are background processes that Antigravity starts and restarts.
  - Config is `~/.gemini/config/sidecars/<name>/sidecar.json` with `command` or `builtin: "schedule"`, `args`, `restart_policy`, `env`.
  - Each sidecar is disabled by default and must be enabled in `~/.gemini/config/config.json`, with an optional `projectId`.
  - The built-in `schedule` takes a five-field cron expression followed by a command.
  - **Sidecars get an `agentapi` command: `agentapi new-conversation <prompt>` and `agentapi send-message <conversation_id> <prompt>`.** The sidecar's working data is under `~/.gemini/antigravity/sidecar_data/<id>/` (`data/`, `logs/`, `events/`).
  - This is the officially documented way for an external process (a hub poller or watcher) to start or message a conversation without a human.
- **Not documented:** whether sidecars and schedules run when the app or CLI is closed, and how permission prompts are handled in unattended runs. Secondary sources contradict each other: one says it needs the Antigravity runtime active, another says it runs with the app closed. Treat as UNVERIFIED.
- **Scheduled tasks** in the desktop app and a `/schedule` command (one-off or cron). Available on all plans, with no limits stated ([plans](https://antigravity.google/docs/plans/)). The first-party docs do not describe a callable "schedule" tool, though the hooks page mentions one.
- **SDK triggers:** `LocalAgentConfig(triggers=[every(60, check_status)])`, which runs while the agent is active. Sessions can be persisted (`save_dir`, `conversation_id` of at least 32 characters). Docs do not say how arbitrary external events are delivered ([SDK lifecycle](https://antigravity.google/docs/sdk/lifecycle/)).
- **Background subagents and tasks:** asynchronous subagents, `/agents`, `/tasks`. These are internal to one agent and are not external triggers.
- **Remote Control:** `agy remote-control start` registers a systemd user service on Linux that starts at boot, and `/remote-control` or `agy --remote-control` does it for one session. It exposes sessions to a web dashboard under the same Google account. The docs describe no API and no external-program input channel ([remote control](https://antigravity.google/docs/remote-control?tab=cli)). It depends on an account or organisation policy flag.
- **No file watcher is documented.** A sidecar running a watch loop is the substitute.

### 2.7 Headless, resume, SDK

Source: [agy headless](https://antigravity.google/docs/cli/headless/), read 2026-10-10.

- Flags: `-p/--print`, `--output-format text|json|stream-json`, `--input-format stream-json` (multi-turn over stdin, requires `stream-json` output), `--json-schema`, `--model`, `--effort`, `--agent`, `--print-timeout` (default 5m), `--sandbox`, `--dangerously-skip-permissions`.
- Resume: `-c/--continue` (latest thread for the workspace, since histories are directory-scoped) and `--conversation <id>`. `/fork`, `/rewind` and `/resume` exist interactively. No checkpoint feature is documented ([conversations](https://antigravity.google/docs/cli/conversations/)).
- Headless permissions: no prompts. An ask that cannot be answered is soft-denied, the run exits 0, and a stderr note names the rule needed. Shell commands default to Ask, so they are denied unless granted in `permissions.allow`.
- Exit codes: 0 success (including soft-denials), 1 and 2 for specific input errors. Unauthenticated runs fail with an error instead of hanging.
- Python SDK: hooks (`pre_turn`, `on_tool_error`), triggers, policies, MCP, subagents and persistence. Auth is `GEMINI_API_KEY` or Vertex. Subscription auth is not described, so assume the SDK bills API usage, not the AI Pro quota (UNVERIFIED).

### 2.8 Models and AI Pro limits

Sources: [models](https://antigravity.google/docs/models/), [plans](https://antigravity.google/docs/plans/), read 2026-10-10.

- **Models on AI Pro:**
  - Gemini 3.8, 3.7 and 3.6 Flash, and Gemini 3.1 Pro.
  - Claude Sonnet 5.5 and Opus 5.5 (thinking), for non-trial subscriptions only.
  - Claude Sonnet 4.6 and Opus 4.6, and GPT-OSS-120b, are marked for removal on 2026-11-02.
  - Gemini and Claude/GPT models have separate quota pools.
  - The I/O post said Gemini 3.5 Flash was the default; the docs home says 3.8 Flash powers local agents, so the default is inconsistent across pages.
- **Pro limits.**
  - There is a five-hour limit that refreshes every five hours until the weekly limit is reached.
  - There is a weekly limit. No absolute numbers are published; Google says usage tracks "work done".
  - Overage credits can be bought, with a Never/Always setting.
  - Pro users reported multi-day lockouts in March 2026 ([PiunikaWeb, secondary](https://piunikaweb.com/2026/03/12/google-antigravity-pro-weekly-limits-multi-day-quota-lockouts/)). Google reset weekly quotas on 2026-05-22.
  - `agy` shares one usage pool with the desktop app.
  - Concurrency limits and scheduled-task limits are not stated. Polling hooks and sidecars that spawn model turns will draw on this meter.
- Ultra tiers are $99.99 (5x Pro) and $199.99 (20x). All figures are from secondary sources apart from the plans page.

## 3. Other Google products with an API

- **Jules** ([sessions](https://jules.google/docs/api/reference/sessions/), [activities](https://jules.google/docs/api/reference/activities/), read 2026-10-10).
  - Base URL `https://jules.googleapis.com/v1alpha`, API key in `x-goog-api-key` (max 3 keys; the key is created in the Jules web app).
  - Endpoints: `POST /sessions` (prompt, `sourceContext`, `requirePlanApproval`, `automationMode`), `GET /sessions`, `GET /sessions/{id}`, `DELETE`, `POST /sessions/{id}:sendMessage`, `:approvePlan`, `GET /sessions/{id}/activities`.
  - States: QUEUED, PLANNING, AWAITING_PLAN_APPROVAL, AWAITING_USER_FEEDBACK, IN_PROGRESS, PAUSED, COMPLETED, FAILED.
  - Activity types include `agentMessaged`, `userMessaged`, `progressUpdated` and `sessionCompleted`, plus artifacts (git patch, bash output).
  - No webhooks and no documented rate limits. The API is alpha and polls only. It works on GitHub repos via the Jules GitHub app, so it fits "dispatch a contained task, poll for a PR". It is a worker, not a peer.
- **Gemini API Managed Agents** ([quickstart](https://ai.google.dev/gemini-api/docs/managed-agents-quickstart), [Google blog](https://blog.google/innovation-and-ai/technology/developers-tools/expanding-managed-agents-gemini-api/); via search summary, not fully read).
  - `interactions.create(agent=…, environment="remote", background=True)`, with remote MCP, environment hooks, a `network.allowlist` with header transforms, and repository, GCS or inline sources.
  - Multi-turn use passes `previous_interaction_id`. It looks like the cleanest programmatic channel, but it is API-billed and the sandbox is remote, so it cannot touch the author's local checkout.

## 4. Capability matrix per surface

"Receive" means the agent gets a hub message by push or poll. "Hub" is Diogenes.

| Surface | Receive | Send | Query state | Hold a lock | Still needs a human |
|---|---|---|---|---|---|
| **agy MCP client** (`mcp_config.json`) | Poll only: the agent must decide to call a hub tool. No documented MCP notification support. | Yes, via a tool call. | Yes, via tool calls. | Yes, if the hub exposes lock tools (the hub owns the lock; the agent only calls it). | MCP tools default to Ask. Pre-approve with `mcp(diogenes/*)` in settings. First-time OAuth if used. |
| **agy hooks** (`PreInvocation`, `PostInvocation`, `Stop`) | **Push-like**: a command hook polls the hub (or a local inbox file) and returns `injectSteps` or `Stop` `continue`, at every model call. | Yes, because a hook is a process that can call the hub. | Yes. | A hook can refuse (`PreToolUse` deny) when the hub says the lock is not held. It does not hold the lock itself. | Workspace hooks may need folder trust. A hook crash blocks tool calls (fail closed). The sanitised env means the hub token must live in a file. |
| **agy sidecars + `agentapi`** | **True push for an idle agent**: a sidecar watches the hub (poll loop, cron or Redis subscribe) and calls `agentapi send-message <conversation_id>` or `new-conversation`. | Yes. | Yes. | The sidecar can hold a lease for the agent. | Must be enabled once in `config.json`. Unknown whether it runs with the app closed and how permission prompts resolve unattended. Burns AI Pro quota. |
| **agy headless** (`-p`, `--conversation`, `stream-json`) | Yes: a supervisor launches or resumes a turn per message, or feeds a long-lived process via stdin `stream-json`. | Yes (output JSON, or tool calls). | Via MCP or hooks. | Via the supervisor. | Shell commands are soft-denied unless pre-granted. Avoid `--dangerously-skip-permissions`; it removes hooks too. |
| **agy rules or `AGENTS.md`** | Static only: tells the agent to check the inbox. | No. | No. | No. | Nothing, but it relies on the model obeying. |
| **agy Remote Control** | No external input API documented. | No. | No. | No. | Web UI only. |
| **Antigravity SDK** (Python) | Yes: the hub is the host process, and `chat()`, triggers and hooks all work in-process. | Yes. | Yes. | Yes (host-held). | Needs an API key or Vertex, billed separately from AI Pro (UNVERIFIED). |
| **Gemini CLI MCP** | Poll only. | Yes. | Yes. | Via tools. | `trust: true` or confirmations. |
| **Gemini CLI hooks** (`BeforeAgent`, `AfterTool`, `AfterAgent`, `SessionStart`) | Push-like: `additionalContext` injected on the next turn; `AfterAgent` deny re-prompts. | Yes. | Yes. | A hook can deny a tool. | Needs a paid API key or enterprise licence now. |
| **Gemini CLI headless** | Same as `agy` headless. Stdin and approval behaviour UNVERIFIED. | Yes. | Via MCP or hooks. | No. | Approval mode in headless mode UNVERIFIED. |
| **Gemini CLI A2A** | The CLI is an A2A client only. Hub could be an A2A server with an agent card. | Yes (CLI calls the hub agent). | Via the hub agent. | Via the hub agent. | Per-call permission for the remote agent not documented. |
| **Jules API** | Poll `activities`, or send with `:sendMessage`. | Yes. | No. | No. | Plan approval if enabled. Alpha API, GitHub-only. |
| **Managed Agents API** | `background: true` plus polling. | Yes. | Remote MCP. | Via remote MCP. | API key and billing. |

**Cross-cutting.** No surface lets a Gemini agent *wake up itself* on a hub event except sidecars and `agentapi`. Everything else is either a poll at a moment the agent is already running (MCP tool call, hooks) or a supervisor you build (headless, SDK).

## 5. Recommended integration design

### Antigravity (`agy`), ranked by robustness

1. **Supervisor plus headless `agy` (recommended first build).**
   - A small Diogenes-side process polls or subscribes (Redis stream, SQLite or an HTTP API) and runs `agy -p "<task>" --conversation <id> --output-format json`.
   - Pre-grant `command(...)`, `write_file(...)` and `mcp(diogenes/*)` in `permissions.allow`.
   - Reasons: it is fully documented, it has no dependence on the desktop app, it uses the stable exit-code and JSON surface, and one turn per message is easy to audit.
   - It costs a process start per message and spends quota. It is not a conversation held open in the UI.
2. **Hooks plus MCP inside an interactive or long-lived session.**
   - A `PreInvocation` hook reads a file or hub endpoint and returns `injectSteps` with a `userMessage` containing the hub message, wrapped as untrusted data. A `Stop` hook returns `continue` while messages are pending.
   - A `PreToolUse` hook enforces write scopes and locks by asking the hub, and fails closed (documented behaviour).
   - A `diogenes` MCP server exposes `send`, `inbox`, `board`, `lock/acquire`, `lock/release`, with `mcp(diogenes/*)` pre-approved.
   - Reasons: this is the closest analogue to the Claude Code message-at-next-tool-round model, and all the pieces are documented. Risks: the hook environment is sanitised (use a token file), a bug blocks every tool call, and hooks are skipped under `--dangerously-skip-permissions`.
3. **Sidecar with `agentapi` (best to wake an idle agent, least proven).**
   - A sidecar polls the hub and calls `agentapi send-message <conversation_id> "<inbox notice>"`. It removes the author's manual relay.
   - Do not rely on it until experiment 1 below passes. The unattended permission handling and the app-closed behaviour are undocumented.
4. **File inbox plus `AGENTS.md` instruction (today's baseline).** It works with no new code, but the author must relay alerts, and it depends on model compliance. Keep it as the fallback.

### Gemini CLI (only if a paid API key or enterprise licence is available), ranked

1. **MCP server plus `BeforeAgent` and `AfterTool` hooks.** The hooks documentation is the richest of the two harnesses: `BeforeAgent` adds the pending hub messages as `additionalContext`, and `BeforeTool` enforces write scopes.
2. **Headless `-p` supervisor**, with the same pattern as `agy` option 1. Verify stdin and approval behaviour first.
3. **A2A**: expose the hub as an A2A server so Gemini CLI can delegate to it as a remote subagent. This helps with query and send, not with receiving.

### Experiments that would confirm this (no command was run here)

1. **Sidecar unattended run.** Create a `schedule` sidecar every minute that runs `agentapi send-message <id> "ping"` in a conversation. Test with the desktop app closed, with only `agy` running, and with the daemon from `agy remote-control start`. Observe whether the message is processed, and whether a shell tool call stalls at an Ask prompt.
2. **`injectSteps` delivery.** Add a `PreInvocation` hook that reads a file and returns a `userMessage`. Confirm the model sees it, whether it fires mid-turn or only per invocation, and what it costs in quota.
3. **Hook fail-closed and env.** Make a hook exit non-zero and one time out. Confirm tool calls are blocked, and list the environment variables visible to the hook.
4. **MCP over HTTP.** Connect a local Diogenes MCP server through `serverUrl` and test with `mcp(diogenes/*)` pre-approved. Check that an unattended `-p` run can call it without an Ask.
5. **Headless multi-turn.** Test `--input-format stream-json --output-format stream-json` as a persistent worker, and `--conversation` resume across runs.
6. **Quota burn.** Measure the five-hour and weekly quota used by a 1-per-minute poll versus an event-driven one on AI Pro.
7. **Sandbox network.** With `enableTerminalSandbox` on, check whether `curl` to the hub on localhost works from a shell tool, and whether MCP and hooks are outside the sandbox.
8. **Gemini CLI.** Confirm that the CLI still authenticates with a paid API key, then test `BeforeAgent additionalContext` in `-p` mode and stdin handling.

## What this means for Diogenes

- **Design for `agy`, not Gemini CLI.** The AI Pro plan makes `agy` the only Gemini harness (§0). Use Gemini CLI hook docs as a design reference only.
- **Offer all three channels.** The hub should expose (a) a stdio and HTTP MCP server, (b) a hook adapter that reads the hub and emits `injectSteps` or `additionalContext`, and (c) a supervisor loop that wraps `agy -p`. This matches the author's "hooks plus poll" intent. Hooks give push-like delivery inside a running agent, polling covers everything else (§2.5, §2.6, §2.7).
- **The hook calls the hub, so the hub owns the lock.** An agent cannot hold a lock itself. The hub grants a lease to a holder id, and the `PreToolUse` hook denies writes outside the lease. This is stronger than the markdown-line lock and its recorded "take hazards".
- **Config translation is needed.** A Gemini CLI `mcpServers` entry using `url` or `httpUrl` does not work in `agy`; it must use `serverUrl` (§2.3). Hook payloads differ between the two harnesses (snake_case versus camelCase, different event names). Diogenes should hide this behind one adapter per harness.
- **Treat injected messages as data.** `injectSteps` and `additionalContext` put text in the agent's context. Wrap hub messages in a fenced "untrusted message from X" envelope, as the cross-session convention does.
- **Plan for fail-closed hooks.** `agy` hooks that crash block tool calls. The adapter must be tiny, time-bounded and tolerant of a hub outage, or a hub restart stops every Gemini agent.
- **Hub tokens go in a file, not an env var.** The sanitised hook environment (§2.5) and Gemini CLI's token-pattern redaction (§1) both strip secrets from the environment.
- **Pre-grant permissions narrowly.** Use `mcp(diogenes/*)` and specific `command(...)` rules. `--dangerously-skip-permissions` also removes hooks, so it would silently disable lock enforcement.
- **Quota is a hub concern.** AI Pro limits are opaque (§2.8), and every poll that wakes the model spends them. The hub should do the polling and wake an agent only when there is work (sidecar or supervisor), and should expose the agent's last known meter the way the Claude status-line does.
- **Jules is a worker, not a peer.** Use its REST API for contained PR tasks, polled through `activities` (§3).
- **Gemini harnesses with no hook support can still use the MCP inbox.** If a harness only has MCP, the fallback is polling by instruction in `AGENTS.md`.

## Open questions

- Do sidecars and scheduled tasks run unattended with the desktop app closed? How are permission prompts resolved in that case? (Experiment 1.)
- Does `injectSteps` interrupt a turn, or only apply at the next model call? Is there a documented cap on `Stop` continuation?
- Does the Antigravity SDK use the AI Pro quota or an API key? Does `agentapi` need the desktop app?
- Is there any MCP notification, sampling or resource-subscription support in `agy`? I found none.
- What is Antigravity's "Knowledge" feature, if it still exists? I found no documentation.
- How does the `nsjail` sandbox treat network access and MCP traffic?
- Which Gemini model is the default? The pages say 3.5, 3.6 and 3.8 Flash in different places.
- Does Gemini CLI still work for the author's account with a paid API key, and in which release did hooks first ship?
- Is there an `agy` A2A or ACP server mode? The one "ACP" I found is a third-party "Agentic Control Plane", not Agent Client Protocol.
- The author must decide whether to pay for a Gemini API key or Code Assist licence, which would reopen the Gemini CLI route.

## Outside my question

- The Antigravity models page lists Claude Opus 5.5 and Sonnet 5.5 as available on AI Pro (non-trial). A Gemini-harness agent could therefore run an Anthropic model, which changes the "different perspective" audit assumption: an audit run through Antigravity may not be independent of the Claude seats. Separate Gemini and Claude pools were stated on the models page.
- The Gemini CLI sandbox page and the `agy` sandbox docs both leave network policy unstated. For the devTeam sandboxing question, Docker or Podman with the hub on a Unix socket or a loopback port is the only documented-compatible shape.

Sources read 2026-10-10 are linked inline above.