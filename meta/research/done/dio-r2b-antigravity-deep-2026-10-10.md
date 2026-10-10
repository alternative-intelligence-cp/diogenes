<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-r2b-antigravity-deep-2026-10-10.md: a read-only API-credits job (claude-opus-5-5,claude-haiku-5-5, 43/200 turns, $1.8694 by the CLI (the bill is about two-thirds)). Its prompt is prompts/dio-r2b-antigravity-deep-2026-10-10.md. -->

# Google Antigravity, deep second pass: hooks, MCP, waking agents, sandbox, identity and quota, for a Diogenes integration

Job: dio-r2b-antigravity-deep-2026-10-10 · Date: 2026-10-10 · Model: Opus 5.5 (claude-opus-5-5) · Tools: Read, WebSearch, WebFetch. I ran nothing and measured nothing.

**Limits:**
- WebFetch answers through a small summarising model. I read the large pages in several narrow passes, and I give quotes only where the tool returned them verbatim.
- I could not read:
  - the GitHub-rendered `CHANGELOG.md` (HTTP 503), so I read the raw file and the docs changelog instead;
  - the last ~42 KB of the docs changelog (the older IDE/SDK entries);
  - the Medium post "Elevating Antigravity agent skills, Part 4" (HTTP 403; only its search summary);
  - any official reference for the in-agent `send_message` tool or for `agentapi` output.
- I found no Antigravity docs page that states:
  - the environment a hook gets;
  - its working directory;
  - its exit-code rules;
  - whether it runs sandboxed.

  Those points rest on third-party captures, labelled as such.
- I only own claims as current as the pages read today, 2026-10-10. The latest versions in the changelogs are agy CLI 1.3.3 and the app 2.21.1 (2026-10-07). Pages read for the first time today are cited "read 2026-10-10".
- All the hands-on evidence about hooks I found comes from macOS (darwin-arm64) captures. **Nothing here is confirmed on Linux.**

## 0. Corrections to the first report (dio-r2)

| Round-1 claim | Correction | Source |
|---|---|---|
| "Legacy `url`… NOT supported" in `mcp_config.json` | The MCP page still says "Legacy fields like `url` or `httpUrl` aren't supported". But the changelog says the CLI "Added support for `url` in `mcp_config.json`" in **agy 1.0.5 (2026-06-03)**, and that the app's "`mcp_config.json` schema now accepts url in addition to serverUrl" in **2.1.4 (2026-06-11)**. **Use `serverUrl`, which works under both readings.** | [MCP](https://antigravity.google/docs/mcp/), [changelog](https://antigravity.google/docs/changelog/) |
| "Scheduled tasks" | Renamed: "Scheduled Tasks are now called Automations" in **app 2.21.1 (2026-10-07)**. | [changelog](https://antigravity.google/docs/changelog/) |
| Sidecars presented as a general `agy` facility | The sidecars page says **"Available on: Antigravity 2.0"**, meaning the desktop app. The CLI only shows indirect traces: plugin sidecar processes are mentioned in agy 1.2.7, and the `remote-control` daemon "still holds the plugin open" in 1.3.1. | [sidecars](https://antigravity.google/docs/sidecars/), [raw CHANGELOG](https://raw.githubusercontent.com/google-antigravity/antigravity-cli/main/CHANGELOG.md) |
| `--print-timeout` default 5 m | The docs page still says 5 m. The changelog for **agy 1.2.6 (2026-09-18)** says "Changed the default timeout for headless (`-p` / `--prompt`) runs from 5 minutes to unlimited". **The docs are stale. Set the flag explicitly.** | [headless](https://antigravity.google/docs/cli/headless/), [changelog](https://antigravity.google/docs/changelog/) |
| "No file path" for the sandbox engine | Two pages disagree. The settings page says "On Linux, it uses `nsjail`". The sandbox page says only "kernel namespaces". | [settings](https://antigravity.google/docs/settings/), [sandbox](https://antigravity.google/docs/sandbox/) |
| Sidecar or `agentapi` as the way an outside process wakes an agent | `agentapi` needs a language-server address and a CSRF token. According to third parties, these exist **only inside the agent's own shell, or inside a sidecar the app starts**. An arbitrary outside process is refused (§3.2). | [acc PR #181](https://github.com/automatis-tools/agents-can-communicate/pull/181) (secondary) |

## 1. Hooks in Antigravity

### 1.1 File, location, scope

Official [hooks docs](https://antigravity.google/docs/hooks/), read 2026-10-10:

| Product | Workspace | Global (user) | Plugin |
|---|---|---|---|
| Antigravity 2.0 (app) | "`.agents/hooks.json` in your workspace root" | "`~/.gemini/config/hooks.json`" | — |
| Antigravity CLI (`agy`) | "`.agents/hooks.json` at your project root" | "`~/.gemini/config/hooks.json` or inside your primary `~/.gemini/antigravity-cli/settings.json` file" | "Packaged inside an installed plugin's `hooks.json` file" |
| Antigravity IDE | "`.agents/hooks.json` in your open project" | `~/.gemini/config/hooks.json` | — |

- **Folder trust.** The hooks page does not mention it. The changelog does, in **agy 1.1.1 (2026-07-10)**: "Fixed workspace-local hooks defined in `/.agents/hooks.json` not loading after trusting a folder". So **workspace hooks are gated on folder trust.** The global file is not.
  - Secondary, PR #181 (agy 1.2.7): "In a newly trusted folder, the first TUI session gets an empty `workspacePaths`."
- **Merge order** across workspace, global and plugin files is **not documented**.
- **Shape.** The top level is keyed by *hook name*, and each name maps to event keys. `PreToolUse` and `PostToolUse` take `[{matcher, hooks:[…]}]`. `PreInvocation` takes "a list of handlers directly under the event key". The handler fields:
  - `type`: "Currently only `"command"` is supported";
  - `command` (required);
  - `timeout`: "Defaults to `30`" seconds;
  - `enabled: false` disables a hook without removing it.
- **Tooling:** `/hooks` lists the active hooks, and print mode answers `-p "/hooks"` "without starting an agent turn" (agy 1.1.12).

### 1.2 Every event and its payload

All of this is quoted from the official docs. Every hook receives these **common stdin fields**, in camelCase:
- `conversationId`: "The unique UUID of the active agent conversation";
- `workspacePaths`;
- `transcriptPath`: "the persistent `transcript.jsonl`";
- `artifactDirectoryPath`;
- `modelName`.

| Event | Docs wording | Extra input | Output |
|---|---|---|---|
| `PreToolUse` | "Fires before a tool is executed." Regex `matcher` on the tool name. | `toolCall.name`, `toolCall.args`, `stepIdx` | `decision` (required): `allow`, `deny` ("Hard blocks execution immediately"), `ask`, `force_ask`, `deny_unless_prior_grant`. Optional `reason`: "shown to the agent or to you". Optional `permissionOverrides`, e.g. `["read_file(/path)", "command(args)"]`. |
| `PostToolUse` | "Fires after a tool completes." | `toolCall` (name, args), `stepIdx`, optional `error` | "Returns an empty JSON object `{}`" — **no injection.** |
| `PreInvocation` | "Fires before the model is called." | `invocationNum` (0-indexed), `initialNumSteps` | `injectSteps` |
| `PostInvocation` | "Fires immediately after each model invocation completes." | same as `PreInvocation` | `injectSteps`, plus `terminationBehavior`: `"force_continue"` ("Forces the loop to continue"), `"terminate"`, or `""` |
| `Stop` | "Fires when execution terminates." | `executionNum`, `terminationReason`, optional `error`, and `fullyIdle`: "`true` if the agent is completely finished and all background commands or asynchronous tasks have completed" | `decision: "continue"` ("prevent the agent from stopping and re-enter the execution loop. Any other value allows the stop"), and `reason`: "If `decision` is `"continue"`, this message is injected as a system message into the conversation." |

- **Payload gaps**, all secondary:
  - There is no `hook_event_name` field, so pass the event as an argv argument ([acc #177](https://github.com/automatis-tools/agents-can-communicate/issues/177), agy 1.2.7).
  - `PostToolUse` "carries no tool output" ([agenticcontrolplane](https://agenticcontrolplane.com/controls/antigravity), agy 1.1.21).
  - The `PreInvocation` and `PostInvocation` payloads are byte-identical, and the prompt has to be read from the transcript tail ([search summaries of oboete, untether and kaoiro issues](https://github.com/littlebearapps/untether/issues/981)).
- **Undocumented `SessionStart`.** A third party reports that `SessionStart` fires for new conversations on agy 1.1.27 and 1.2.7. There is no `SessionEnd` (acc #177). Treat it as unofficial.

### 1.3 `injectSteps`, quoted

- **Definition.** It is "**Optional.** List of steps to inject into the conversation trajectory before the model is called." Each item has exactly one of these:
  - "**`toolCall`** (object): A tool call to execute";
  - "**`userMessage`** (string): A message from you";
  - "**`ephemeralMessage`** (string): A transient system message".
- **Documented example:** `{"injectSteps": [{"ephemeralMessage": "Remember to lint"}]}`.
- **No example exists** for `toolCall`. Its schema is undocumented (UNVERIFIED).

### 1.4 Can a hook feed text to the model? **Yes, by two documented paths and one more that is documented but untested.**

1. **`PreInvocation` → `injectSteps[].ephemeralMessage`.** Third parties verified this live:
   - acc #177 on agy 1.2.7 (2026-09-20), print mode;
   - a kaoiro capture on agy 1.2.11: the hook returned `PROBE-INJECTED-412`, "and the model's reply was exactly that marker" (search summary of [kaoiro #412](https://github.com/sakuraiyuta/kaoiro/issues/412)).
2. **`Stop` → `decision:"continue"` + `reason`.** This is documented as a system message, and was verified on agy 1.2.7 ("the model reproduced the token from `reason`").
   - It is **bounded**: since **agy 1.1.9**, "after a configurable number of consecutive continuations, the hook can no longer block". The ceiling value and its setting name are UNVERIFIED.
   - **app 2.6.0**: "Agents no longer hang forever when a stop hook keeps blocking."
   - **agy 1.3.3** fixed `/btw` side questions running hooks, "which could make hooks such as stop hooks loop".
3. **`userMessage`** and **`PostInvocation` + `force_continue`** are documented but **not observed** by anyone I found (UNVERIFIED).

A hook **cannot wake an idle conversation**. It only runs while the agent loop is already running. PR #181 says so directly: "Hooks alone cannot wake an idle session."

### 1.5 Sandbox and environment

- **Official:** the hooks page says nothing on the environment, working directory, sandboxing, exit codes or fail behaviour.
- **Environment (secondary):**
  - "The hook environment is sanitized. Only whitelisted variables reach the subshell" ([agenticcontrolplane](https://agenticcontrolplane.com/controls/antigravity), agy 1.1.21, 2026-08-26).
  - "A hook gets only `ANTIGRAVITY_CONVERSATION_ID`" ([acc PR #181](https://github.com/automatis-tools/agents-can-communicate/pull/181), agy 1.2.7).
  - **Use absolute paths** for the hook binary. Read the hub token from a file. Assume `HOME` and `PATH` may be missing (UNVERIFIED: whether `HOME` survives).
- **Exit codes (secondary, agy 1.1.21):**
  - "Denials must travel as JSON with exit 0 — there is no exit-code deny channel";
  - "A failing hook blocks the call… `pre-tool hook failed`", so a broken `PreToolUse` hook **fails closed**.
- **Later changes:**
  - agy 1.1.23: "Fixed CLI crashes caused by prompt hooks by catching hook panics";
  - app 2.12.0 (2026-09-02): "A failing custom hook no longer ends the session; it is now reported as an error and the conversation continues."
  - Whether a failing `PreInvocation` hook now fails open or closed in the CLI is **UNVERIFIED**.
- **`--dangerously-skip-permissions`:** "the hook layer is **not invoked at all**" (secondary A/B test, agy 1.1.21).
- **Sandboxing of hooks:** not documented. Every capture describes hooks as host commands run by the harness, and nothing says they are inside the terminal sandbox. **UNVERIFIED**; experiment E3 below settles it.

### 1.6 When it arrived, and how stable it is

- **Hooks predate the CLI changelog's hook fixes.** I found **no official "hooks added" entry**, so the arrival release is UNVERIFIED. The milestones:
  - Google's 2.0 launch list includes "JSON Hooks" ([@antigravity on X, 2026-05-27](https://x.com/antigravity/status/2059707024301072804), secondary).
  - agy 1.0.8 (2026-06-12) fixed "the `/hooks` command [writing] configurations to `~/.gemini/antigravity-cli/hooks.json`".
  - agy 1.0.16 (2026-07-02) fixed "empty decision strings returned by pre-tool hooks".
- **Stability: active churn.** Hook fixes landed in:
  - the CLI: 1.0.8, 1.0.16, 1.1.1, 1.1.7, 1.1.9 (twice), 1.1.10, 1.1.23, 1.2.3, 1.2.4 ("`hooks.json` configurations being silently dropped when customization token budget truncation is active"), 1.3.1 and 1.3.3;
  - the app: 2.6.0 ("Custom hooks you define now run at the end of a turn instead of being skipped"), 2.12.0 and 2.17.0 (custom agents "can declare their own hooks").
- **A conflict that matters for lock enforcement:**
  - acc #177 (agy 1.2.7, print mode, 2026-09-20) reports that `PreToolUse` and `PostToolUse` were "Silently dropped": "there is not even an advisory interception point".
  - agenticcontrolplane verified a `PreToolUse` deny live on agy 1.1.21.
  - Possible causes are a config-shape difference, a print-mode difference or a regression. **UNVERIFIED.** Do not rely on `PreToolUse` as the only guard.

## 2. MCP in Antigravity

All from the official [MCP docs](https://antigravity.google/docs/mcp/), read 2026-10-10, unless marked.

- **Configuration:**
  - CLI and IDE: `~/.gemini/config/mcp_config.json` (global) and `.agents/mcp_config.json` (workspace).
  - SDK: discovers the workspace file.
  - App: "Installed MCP Servers" under Settings > Customizations, with no documented file path.
- **Transports:** stdio (`command`), and Streamable HTTP, SSE and **WebSocket** via `serverUrl`. Round 1 missed WebSocket. For the `url` key, see §0.
- **Other fields:** `disabled` and `disabledTools`. Timeouts:
  - agy 1.0.15: "Increased the MCP connection timeout to 60 seconds";
  - app 2.4.3 added "a timeout for MCP server connections and tool calls".
- **Calling an MCP tool without per-call approval: yes.** The default is Ask ("in Ask mode, requiring your approval before execution"). Allow rules pre-approve it: `mcp(server/tool)`, `mcp(server/*)` or `mcp(*)`.
  - In the CLI these rules live in `~/.gemini/antigravity-cli/settings.json`, and they are honoured in headless runs (agy 1.1.4: "honor persisted `settings.json` policies, including `permissions`").
  - **There is no per-server trust flag.**
  - Enterprise admin policies can impose "MCP allowlists" (app 2.5.0).
- **Server push:**
  - **Notifications, sampling, elicitation and prompts are not mentioned anywhere.** The docs mention "resources and tools" (IDE).
  - The changelog shows only "Fixed MCP progress callbacks being dropped" (agy 1.1.11) and "MCP tool results containing embedded resources being silently dropped" (1.1.5).
  - **Conclusion: no documented way for an MCP server to push a message that wakes or reaches the model.** UNVERIFIED either way; experiment E6 settles `notifications/message` and `resources/updated`.
- **Identity for an MCP server: not provided.** Nothing documents the server receiving the `conversationId` (§5).

## 3. Waking an agent without the human

### 3.1 Inventory

| Mechanism | Product | What it does | Can outside code drive it? | Evidence |
|---|---|---|---|---|
| **Headless `agy -p`** | CLI | Starts a new conversation, or resumes one with `--conversation <id>`. Its JSON carries `conversation_id`: "ID of the conversation, for resuming later". | **Yes.** It is a plain process the hub launches. | [headless](https://antigravity.google/docs/cli/headless/) (official) |
| **`--input-format stream-json`** | CLI ≥ 1.1.15 | One long-lived process. Each stdin line `{"event":"user","message":{"content":"…"}}` runs a turn and emits `result`. | **Yes.** The hub owns stdin, so this is a true push into a live agent. | official |
| **Sidecar + `agentapi`** | App ("Available on: Antigravity 2.0") | The app starts the sidecar and restarts it. `agentapi new-conversation <prompt>` needs a `projectId`; `agentapi send-message <conversation_id> <prompt>` also exists. | Only the sidecar the app spawned. Its environment carries the endpoint, and `agentapi` "is automatically added to the sidecar's path". | [sidecars](https://antigravity.google/docs/sidecars/) (official) |
| **Automations** (formerly Scheduled Tasks) | App | cron → each run opens a new conversation. Implemented as `language_server multicall schedule "<cron>" agentapi new-conversation …`. | Only by editing the config. Each run is a new conversation, not a resume. | [#682](https://github.com/google-antigravity/antigravity-cli/issues/682) (user report, IDE 2.4.2, Windows) |
| **`schedule` tool / `/schedule`** | CLI, app, SDK | The *agent* sets timers or cron inside its own conversation ("Set timers or recurring cron jobs"). Reported to be cancelled when the agy process is killed. | No. The agent arms it itself, but it can be told to poll every N minutes. | [hooks tool list](https://antigravity.google/docs/hooks/); [Medium](https://medium.com/google-cloud/scheduling-tasks-in-antigravity-b37f6c9b61ca) (secondary) |
| **In-agent `send_message` tool** | runtime | Targets a recipient `conversationID` and "triggers an immediate reactive wakeup". | Only agent to agent. **Bug #1022** (agy 1.2.2, open): an idle interactive CLI session stages the message "silently… only ingested when the user submits a prompt". | Medium Part 4 (secondary, 403 to me); [#1022](https://github.com/google-antigravity/antigravity-cli/issues/1022) |
| **`agy agentapi send-message` from the agent's shell** | CLI ≥ 1.2.7 (macOS) | A relay process the agent starts inherits `ANTIGRAVITY_LS_ADDRESS` and `ANTIGRAVITY_CSRF_TOKEN`. An idle TUI session "woke within a second". A busy one held the message "25 seconds until the running answer finished". Pushed text appears as a HIGH-priority `SYSTEM_MESSAGE`. | Indirectly. The agent must run the relay once, and the human approves it once. From outside: "refuses at once: ANTIGRAVITY_LS_ADDRESS is not set"; with the address but no token: "missing CSRF token". | [acc PR #181](https://github.com/automatis-tools/agents-can-communicate/pull/181) (secondary, certified 1.2.7 darwin-arm64) |
| **Remote Control** | CLI ≥ 1.2.0 | `agy remote-control start` = "an always-on headless CLI instance", run as a systemd user service. | **No API.** Web dashboard only, under the same Google account. Feature-flagged per account. | [remote control](https://antigravity.google/docs/remote-control?tab=cli) |
| **File watcher** | — | None documented. | — | — |
| **SDK triggers** (`every(60, fn)`) | Python SDK | In-process, while the host runs. | Yes, but the SDK documents only `GEMINI_API_KEY` or Vertex auth: **API-billed, not AI Pro** (inferred from the SDK page omitting sign-in; UNVERIFIED). | [SDK overview](https://antigravity.google/docs/sdk/overview/) |

Related secondary failure: [deaddrop #18](https://github.com/forgeaura/deaddrop/issues/18) (open). `agentapi send-message --title=… <id> …` fails when run from a long-lived MCP server process, but works by hand. The reporter refers to a `.antigravity_session.json` carrying the PID, `address` and `csrf_token`.

### 3.2 Can anything start or resume an agent conversation from outside?

- **Yes, two ways that are documented and robust:**
  1. **`agy -p … --conversation <id>`**, which starts a new process per message on a stored conversation.
  2. **A hub-owned `agy` in stream-json mode**, which is a persistent process.
- **Into a human's live interactive session (TUI or app) from an arbitrary outside process: no documented way.**
  - The only working route found is a relay the agent starts (secondary, macOS, needs one human approval).
  - In the app, a sidecar is a second route: it receives the `agentapi` endpoint by design, but per-conversation `send-message` from a sidecar is **UNVERIFIED** on Linux.
- **Unattended permission handling for conversations created by `agentapi`: undocumented** (UNVERIFIED).
- **Whether sidecars and Automations run with the app closed:** secondary sources conflict. #682 shows scheduler children outliving the IDE but losing the language server's port after a restart, so their triggers fail. **UNVERIFIED and fragile.**

## 4. The terminal and the sandbox

Official [permissions](https://antigravity.google/docs/permissions/) and [sandbox](https://antigravity.google/docs/sandbox/) pages, read 2026-10-10.

### 4.1 Approval policy and the allow/deny lists

- **Rule types and syntax:**
  - `read_file(path)` and `write_file(path)`: a directory grants recursive access, and `write_file` implies read.
  - `read_url(domain)`: matches subdomains and ignores paths.
  - `execute_url(domain)`.
  - `command(prefix)`, `command(regex:…)` or `command(*)`.
  - `mcp(server/tool)`.
  - `unsandboxed(prefix|regex:…|*)`: "Windows and CLI only".
- **Precedence:** "Deny > Ask > Allow".
- **Matching:**
  - Commands match word by word as prefixes.
  - Commands containing `$(...)` or brace expansion need an exact match "Otherwise they fall back to Ask".
  - agy 1.0.13 made "Always Approve" matching strict.
- **App presets** (macOS/Linux):

  | Preset | Sandbox | Terminal commands | File access | MCP and Web |
  |---|---|---|---|---|
  | Default | on | allowed in sandbox, ask outside | workspace + temp dirs | Ask |
  | Request Review | off | always ask | workspace only | Ask |
  | Turbo | off | unrestricted | full filesystem | Allowed |

  Projects can override the preset under Settings > Projects.
- **CLI:**
  - The rules live in `~/.gemini/antigravity-cli/settings.json` (global), with the `/permissions` panel and the autonomy levels `request-review`, `always-proceed` and `strict` ([features](https://antigravity.google/docs/cli/features/)).
  - The changelog says "CLI permissions now merges project level permissions" (1.0.5) and mentions "permission config merging priorities… project-specific configurations" (1.0.12). The project-level file's name is **UNVERIFIED**.
  - Headless: an unanswerable Ask is "soft-denied: the run continues, exits `0`".

### 4.2 Network policy

- "Sandboxed commands run without network access by default" (2.0, macOS/Linux).
- The app has a "Sandbox Network Access" / "Sandbox Allow Network" toggle ([settings](https://antigravity.google/docs/settings/)).
- Domains granted with `read_url` are "compiled directly into the sandbox's outbound network allowlist" (search summary of the permissions page).
- Blocked network requests are recorded (agy 1.1.6, 1.1.10).
- **Loopback and Unix-socket access from inside the sandbox: not documented (UNVERIFIED).** This decides whether a sandboxed `dio` can reach a local hub.
- The CLI defaults `enableTerminalSandbox: false`. With it off, commands run on the host with full network access.

### 4.3 Can an agent run `dio` and write outside its workspace?

- **Run `dio`: yes.**
  - `command(dio)` in `permissions.allow` runs it without a prompt.
  - With the CLI sandbox on, add `unsandboxed(dio)` so it runs on the host: "The CLI also runs them without prompting".
  - Otherwise it runs sandboxed, with no network, and possibly no hub socket (UNVERIFIED).
- **Write outside the workspace: yes, if granted.**
  - Outside-workspace access "requires approval" by default.
  - `write_file(/home/randy/Workspace/META/NITPICK/messages)` grants it, and in the sandbox, "Paths allowed under `write_file` are also writable".
  - Always blocked in the sandbox: `~/.ssh` and `.env`. `.git` is read-only (agy 1.1.10).
- **What the sandbox does not cover:** whether MCP servers, hooks, sidecars and the file-edit tools are inside it is not stated. Round 1's "likely outside" remains UNVERIFIED.

## 5. Identity: can a hub address a conversation?

- **Yes, by the conversation UUID:**
  - `conversationId` is in **every hook payload** ("The unique UUID of the active agent conversation"; official);
  - `conversation_id` is in **every headless JSON result** (official);
  - `ANTIGRAVITY_CONVERSATION_ID` is in the hook environment (secondary, agy 1.2.7).
- Titles exist: agy 1.1.27 added `conversation_title` to the status-line script payload. Subagents carry `conversation_id` in `subagent_info` (agy 1.1.8).
- **Stability caveats:**
  - `/fork` "allocates a new unique session ID".
  - CLI histories are scoped to the launch directory ([conversations](https://antigravity.google/docs/cli/conversations/)).
  - An undocumented `agentapi get-conversation-metadata <id>` was seen in a probe (search summary of [browser-ide-rally #22](https://github.com/carllx/browser-ide-rally/issues/22); UNVERIFIED).
- **An MCP server cannot read the conversation id** under anything documented. The bridge: a `PreInvocation` hook on `invocationNum == 0` registers `{conversationId, workspacePaths, modelName}` with the hub and injects the participant name the hub assigned. The agent then passes that name in its MCP calls, and the hub checks it against the hook-registered record.

## 6. AI Pro limits that bear on polling or repeated waking

- **Official ([plans](https://antigravity.google/docs/plans/)):**
  - "refreshed every five hours until the weekly limit is reached";
  - limits "correlate with the amount of work done by the agent"; "complex tasks consume more quota";
  - "primarily determined by available capacity and exist to prevent abuse… subject to modification";
  - overage through purchased AI credits ("Never" or "Always");
  - **no BYOK on Pro**;
  - "scheduled tasks and the CLI" are on all plans.
  - **No published numbers, and no concurrency or Automation limits.**
- **From the changelog:**
  - "improved quota messaging for concurrent stream limits" (agy 1.1.21);
  - "per-minute `429` rate limits" (1.2.1);
  - "stop immediately when the Gemini API reports an exhausted daily quota" (1.2.12);
  - **`-p "/usage"`** shows quota and reset times (1.2.15), and the quota appears in the status line (1.0.8).
  - So a hub can probably read the meter without a model turn. That `-p "/usage"` spends nothing is UNVERIFIED; experiment E7.
- **Implications:**
  - A hook that reads a local file costs **no** quota.
  - An injected message only adds tokens to a turn that was happening anyway.
  - Every `-p` run, `agentapi` wake, `Stop` continue or Automation run **is a turn**, and spends quota.
  - **A polling agent wastes Pro quota. Event-driven waking by the hub does not.**
  - March 2026 lockouts were reported (round 1, secondary).

## 7. Gemini CLI, briefly, for contrast

- **Access.** "On June 18, 2026, Gemini CLI and Gemini Code Assist IDE extensions will stop serving requests" for AI Pro, Ultra and free individuals. Google AI Pro and Ultra users lose access. Paid "Gemini and Gemini Enterprise Agent Platform API keys" and Code Assist Standard/Enterprise keep it ([Developers Blog, 2026-05-19](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)).
  - What the two CLIs share, per that post: "Agent Skills, Hooks, Subagents, and Extensions", the latter now "Antigravity plugins", with "won't be 1:1 feature parity".
  - Gemini CLI's headless docs carry the banner "Gemini CLI was replaced by Antigravity CLI on June 18th, 2026" ([headless](https://geminicli.com/docs/cli/headless/)).
- **Hooks:** 11 snake_case events. `BeforeAgent` and `AfterTool` can return `additionalContext`, and an `AfterAgent` deny re-prompts. Exit 2 blocks. This is round 1's reading of [geminicli.com/docs/hooks](https://geminicli.com/docs/hooks/reference/), which I did not re-verify.
  - The hook model is richer and better documented than agy's, and it is open source.
- **MCP:** `trust: true` per server; stdio, SSE and HTTP.
- **Headless:** `-p` with JSON or JSONL. The headless page does not document approval mode or resume (UNVERIFIED).
- **Verdict.** On the author's AI Pro plan, Gemini CLI is **not usable without a separately paid API key**, and it would not draw on the Pro quota. It is better *engineered* for a hub, with open source, mature hooks and a trust flag, but it is **not the better way for this author** unless he decides to pay for API usage. If he does, the same three adapters (MCP, hook injector, headless supervisor) port across with an event-name and casing translation.

## 8. Recommended Antigravity integration for Diogenes, ranked by robustness

**Today's gap:** the author relays every alert by hand. The fix is: the hub knows which Gemini conversation owns a task, delivers to it without the author, and gets a report back through the same path as every other executor.

1. **Hub-run headless executor: `agy -p`, one process per task (most robust; build first).**
   - **How it works:**
     - The Diogenes dispatcher runs `agy -p "<task envelope>" --output-format json --print-timeout 30m [--conversation <id>]` in a worktree.
     - It records `conversation_id` from the JSON, and parses `status`, `response` and `usage`.
     - Exit code and `status` give "received" and "done"; the report is `response` or a `dio report` call.
   - **Pre-grants in `~/.gemini/antigravity-cli/settings.json`:** `command(dio)`, `mcp(diogenes/*)`, the specific test and build commands, and `write_file(<handoff dir>)`. **Never use `--dangerously-skip-permissions`**: it removes hooks.
   - **Why it ranks first:**
     - every piece is official: the flags, the JSON `conversation_id`, settings honoured in headless (1.1.4), soft-deny with a stderr note;
     - it needs no desktop app;
     - it is quota-efficient, since a turn runs only when there is work;
     - it fits P0's "delegate a self-contained task, know it was received, get a report".
   - **Variant:** one persistent `--input-format stream-json` process per Gemini worker, with the hub writing each message to stdin. That is real push with no relay.
   - **Weakness:** it is not the author's interactive app session, so the author watches transcripts rather than a live UI.
2. **In-session delivery for a running agent: global `PreInvocation` + `Stop` hooks, plus a `diogenes` MCP server.**
   - **Hook file:** use `~/.gemini/config/hooks.json`, the global file, because it avoids the folder-trust gate:
     - `PreInvocation` → `/abs/path/dio-hook pre <args>`, which reads a local per-conversation inbox spool (the hub writes it) and returns `{"injectSteps":[{"ephemeralMessage":"<untrusted-message from=…>…</untrusted-message>"}]}`. On `invocationNum==0` it registers the `conversationId`.
     - `Stop` → returns `continue` only when mail is pending, bounded by the harness ceiling.
   - The hook must read from a file and never call the network on the hot path: it is time-bounded, always exits 0, and reads its token from a file.
   - **MCP server** (`serverUrl` or stdio) provides `send`, `inbox`, `report`, `lease`, with `mcp(diogenes/*)` allowed.
   - **Why second:** injection is verified by third parties on 1.2.7 to 1.2.11, but it is undocumented in places, and it **cannot wake an idle session**.
   - **Do not make `PreToolUse` the lock guard** (§1.6). Enforce write scope through `write_file` rules and worktree separation, and have the hub validate leases on `dio report`.
3. **Waking the author's idle interactive session (least proven; only if 1 and 2 are not enough).**
   - **(a) CLI:** at session start, the agent runs a `dio relay` once (one human approval, or a `command(dio relay)` allow rule). The relay inherits `ANTIGRAVITY_LS_ADDRESS` and `ANTIGRAVITY_CSRF_TOKEN`, subscribes to the hub, and calls `agy agentapi send-message <conversationId> "<notice>"`.
   - **(b) App:** a Diogenes sidecar (`~/.gemini/config/sidecars/diogenes/sidecar.json`, enabled in `config.json`) subscribes to the hub and calls `agentapi send-message`.
   - **Evidence:** secondary, macOS only. There is an open bug (#1022) on idle wakeups via `send_message`, and the fragility in #682.
4. **Baseline:** keep the file inbox plus an `AGENTS.md` rule ("run `dio inbox` at the start of each task") as the fallback when everything else fails.

## 9. Experiments to confirm it

None of these was run; the commands are written for the Linux workstation. Record `agy --version` for each.

- **E1. Headless loop (validates option 1).**
  1. Put `{"permissions":{"allow":["command(echo)","write_file(/tmp/dio-e1)"]}}` in `~/.gemini/antigravity-cli/settings.json`.
  2. Run `agy -p "Write 'hello' to /tmp/dio-e1/out.txt with a shell command, then reply DONE" --output-format json --print-timeout 10m > r1.json; echo $?`.
  3. Read `.conversation_id` from `r1.json`, then run `agy -p "What file did you write?" --conversation <id> --output-format json`.
  4. **Pass:** the file exists, exit is 0, the second reply names the file, and `usage` is present.
  5. Repeat without the allow rule and confirm the soft-deny note on stderr.
- **E2. Hook injection on Linux.**
  1. Write `~/.gemini/config/hooks.json`:

     ```json
     {"dio-probe":{"PreInvocation":[{"type":"command","command":"/home/randy/bin/probe.sh pre","timeout":5}],"Stop":[{"type":"command","command":"/home/randy/bin/probe.sh stop","timeout":5}]}}
     ```

  2. `probe.sh` saves stdin to `/tmp/dio-e2/<event>-<n>.json`, saves `env` to `/tmp/dio-e2/env-<event>.txt` and `pwd` to `/tmp/dio-e2/cwd.txt`. On `pre` it prints `{"injectSteps":[{"ephemeralMessage":"PROBE-7731: reply with this token"}]}`.
  3. Run `agy -p "Say hi" --output-format json`, then once interactively.
  4. **Pass:** the reply contains PROBE-7731.
  5. **Record:** the payload fields, the environment variables (is `ANTIGRAVITY_CONVERSATION_ID` the only one? `HOME`? `PATH`?), the working directory, and whether `SessionStart` fires if added.
  6. Repeat with `userMessage` in place of `ephemeralMessage`.
- **E3. Hook sandboxing and failure.**
  1. With `"enableTerminalSandbox": true`, have `probe.sh` run `touch /home/randy/dio-e3-outside` and `curl -s http://127.0.0.1:<hub-port>/health`. Check whether both succeed: if so, hooks run outside the sandbox.
  2. Make the `PreInvocation` hook exit 1, then make it sleep past its timeout. Does the turn proceed, error or block?
  3. Add a `PreToolUse` `{matcher:"run_command", hooks:[…]}` returning `{"decision":"deny","reason":"E3"}`, and ask for `ls`. Is the call blocked (settles the 1.2.7 "silently dropped" conflict), in both `-p` and interactive mode?
- **E4. `Stop` continuation ceiling.** Make a `Stop` hook always return `{"decision":"continue","reason":"keep going #n"}`. Count continuations until the harness overrides it, and note the quota used (`agy -p "/usage"` before and after).
- **E5. Sandbox reach for `dio`.**
  1. With the sandbox on, use `command(regex:nc .*)`, `curl 127.0.0.1:<port>` and a Unix socket in `/tmp`, from a shell tool. Then grant `unsandboxed(dio)` and rerun.
  2. **Record** whether loopback or sockets work in the sandbox without "Sandbox Network Access".
  3. Grant `write_file(/home/randy/Workspace/META/NITPICK/messages)` and confirm an unprompted write there.
- **E6. MCP auto-approval and push.**
  1. Run a stdio test server via `~/.gemini/config/mcp_config.json` with `command`, and an HTTP one with `serverUrl`.
  2. Set `mcp(diogenes/*)` to allow. In `-p` mode, call a tool and confirm there is no soft-deny.
  3. Have the server emit `notifications/message` and `notifications/resources/updated` mid-session. Does anything reach the model or the UI?
- **E7. Quota visibility.** Does `agy -p "/usage" --output-format json` return machine-readable numbers? Does it consume quota (compare before and after)?
- **E8. Waking an idle session (option 3a).**
  1. In an interactive `agy` session, have the agent run `env | grep ANTIGRAVITY_ > /tmp/dio-e8/env` (approve it once).
  2. From a terminal *without* those variables, run `agy agentapi send-message <conversationId> "E8 ping"` and expect a refusal.
  3. Then from a process started *by the agent* (`nohup sh -c 'sleep 60; agy agentapi send-message $ANTIGRAVITY_CONVERSATION_ID "E8 ping"' &`). Does the idle TUI wake?
  4. Repeat while the agent is mid-turn, and once from the `send_message` tool between two sessions (bug #1022).
- **E9. App sidecar (option 3b).**
  1. Create `~/.gemini/config/sidecars/dio-probe/sidecar.json` with `{"command":"/bin/bash","args":["-c","env > $ANTIGRAVITY_EXECUTABLE_DATA_DIR/env.txt; sleep infinity"],"restart_policy":"on-failure"}`.
  2. Enable it in `~/.gemini/config/config.json` under `sidecars.dio-probe.enabled`, and restart the app.
  3. Inspect `env.txt`, then call `agentapi send-message <id of an open conversation> "E9"` from the sidecar.
  4. **Record:** does it wake an idle conversation, and do Ask prompts block it? Close the window, quit the app and reboot, checking whether the sidecar keeps running and whether `send-message` still works after each.

## What this means for Diogenes

- **Make the Gemini executor a hub-run `agy -p` process first** (§3.1, §8.1). It is the one path that is fully documented, needs no human, reports `conversation_id` and `usage`, and maps directly onto P0's delegate, acknowledge, work and report loop. The same pattern fits Claude `-p` and the credits runner.
- **The hub is the waker; agents never poll the model** (§6). Hooks read a local spool for free, and the hub spends a model turn only when there is work.
- **The executor key is the `conversationId` UUID** (§5). A first-invocation hook registers it, and the hub maps it to a Diogenes participant name. Forks get new ids, so treat a fork as a new participant.
- **Delivery adapter = local spool + global hook** (§1.1, §1.4, §1.5). The hub writes `~/.diogenes/spool/<conversationId>/`, and a tiny hook injects it wrapped as untrusted data. This avoids network calls, the sanitised environment and folder trust, and it degrades to "no injection" rather than to a blocked agent.
- **Do not rest locks on Antigravity's `PreToolUse`** (§1.6). Use OS-level write scopes (worktrees, `write_file` rules) plus hub leases that are checked when work is submitted. This also generalises to harnesses that have no hooks.
- **Configure MCP with `serverUrl` or stdio and `mcp(diogenes/*)`** (§2). Expect no server push, so MCP is for request and response only.
- **Plan the sandbox around `unsandboxed(dio)` or a file spool** until E5 shows whether loopback works (§4.2).
- **Expose each Gemini executor's quota** via `-p "/usage"` in the hub's account-room view, if E7 confirms it is free (§6).
- **Pin and re-test on every `agy` update.** Hooks changed in more than ten releases in four months (§1.6). Keep E2, E3 and E8 as an adapter-certification suite tied to `agy --version`.

## Open questions

- Does `PreToolUse` actually fire on agy 1.3.x, on Linux, in `-p` and interactive mode (E3)?
- What environment, working directory and sandbox do hooks get on Linux, and does a failing `PreInvocation` hook now fail open (E2, E3)?
- What is the `Stop` continuation ceiling, and how is it configured (E4)?
- Can a sandboxed command reach loopback or a Unix socket (E5)?
- Do MCP notifications reach anything (E6)?
- Is `-p "/usage"` free and machine-readable (E7)?
- Can a sidecar `send-message` into an idle conversation on Linux, and do sidecars survive the app closing (E9)? Is bug #1022 fixed?
- Does the Python SDK accept a Google AI Pro sign-in? The docs list only an API key or Vertex.
- **For the author:** is a paid Gemini API key acceptable? It would reopen Gemini CLI and the SDK, but not on the Pro quota. Should the Gemini executor run headless in a hub-owned worktree rather than in the app he watches?

## Outside my question

- Antigravity exposes Claude models on AI Pro (round 1). An "independent" Gemini audit should pin `--model` to a Gemini model and record `modelName` from the hook payload as evidence.

Sources, all read 2026-10-10:
- official: [hooks](https://antigravity.google/docs/hooks/), [docs changelog](https://antigravity.google/docs/changelog/), [CLI CHANGELOG (raw)](https://raw.githubusercontent.com/google-antigravity/antigravity-cli/main/CHANGELOG.md), [sidecars](https://antigravity.google/docs/sidecars/), [permissions](https://antigravity.google/docs/permissions/), [sandbox](https://antigravity.google/docs/sandbox/), [settings](https://antigravity.google/docs/settings/), [CLI features](https://antigravity.google/docs/cli/features/), [MCP](https://antigravity.google/docs/mcp/), [headless](https://antigravity.google/docs/cli/headless/), [conversations](https://antigravity.google/docs/cli/conversations/), [remote control](https://antigravity.google/docs/remote-control?tab=cli), [plans](https://antigravity.google/docs/plans/), [SDK overview](https://antigravity.google/docs/sdk/overview/), [Developers Blog transition post](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/), [Gemini CLI headless](https://geminicli.com/docs/cli/headless/);
- issues on Google's repo (user reports): [#682](https://github.com/google-antigravity/antigravity-cli/issues/682), [#1022](https://github.com/google-antigravity/antigravity-cli/issues/1022);
- secondary: [acc #177](https://github.com/automatis-tools/agents-can-communicate/issues/177), [acc PR #181](https://github.com/automatis-tools/agents-can-communicate/pull/181), [agenticcontrolplane](https://agenticcontrolplane.com/controls/antigravity), [deaddrop #18](https://github.com/forgeaura/deaddrop/issues/18), [untether #981](https://github.com/littlebearapps/untether/issues/981), [kaoiro #412](https://github.com/sakuraiyuta/kaoiro/issues/412), [browser-ide-rally #22](https://github.com/carllx/browser-ide-rally/issues/22), [Medium: Scheduling Tasks](https://medium.com/google-cloud/scheduling-tasks-in-antigravity-b37f6c9b61ca), [Medium: Part 4](https://medium.com/google-cloud/elevating-antigravity-agent-skills-part-4-subagent-messaging-42bd72d44600) (search summary only), [@antigravity on X](https://x.com/antigravity/status/2059707024301072804).