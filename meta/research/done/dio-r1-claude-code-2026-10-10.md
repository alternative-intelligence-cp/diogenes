<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-r1-claude-code-2026-10-10.md: a read-only API-credits job (claude-sonnet-5-5,claude-haiku-5-5, 46/200 turns, $1.0649 by the CLI (the bill is about two-thirds)). Its prompt is prompts/dio-r1-claude-code-2026-10-10.md. -->

# Claude Code (2.1.x) integration surfaces for an external coordination hub

Job: dio-r1-claude-code-2026-10-10 · Date: 2026-10-10 · Model: Sonnet 5.5 (`claude-sonnet-5-5`) · Tools: Read, Grep, Glob, WebFetch, WebSearch (read-only, no command execution)

**Limits:**
- Everything is from documentation and changelog text. I measured nothing, and no behaviour here was run on the machine.
- WebFetch summarised large pages in chunks. The hooks page (262 KB) was read only up to character ~200,000, so the per-event input schemas for SubagentStart/Stop, PermissionRequest, TaskCreated and others are incomplete.
- The CHANGELOG (986 KB) was read only in its first 100,000 characters, which reach back to about 2.1.288–2.1.296. Older entries were not read.
- I did not read `scheduled-tasks`, `agent-view`, `sub-agents` or `sessions`.
- The Agent SDK docs were read at the overview level only.
- Dates are all 2026-10-10 unless noted. Pages carry no "last updated" stamp, so claims are marked "as fetched".
- Two secondary sources (blogs, a support article) are labelled as such.

Source key:
- hooks = https://code.claude.com/docs/en/hooks
- xsm = https://code.claude.com/docs/en/cross-session-messaging
- chan = https://code.claude.com/docs/en/channels
- chref = https://code.claude.com/docs/en/channels-reference
- mcp = https://code.claude.com/docs/en/mcp
- sbx = https://code.claude.com/docs/en/sandboxing
- tools = https://code.claude.com/docs/en/tools-reference
- sl = https://code.claude.com/docs/en/statusline
- hl = https://code.claude.com/docs/en/headless
- teams = https://code.claude.com/docs/en/agent-teams
- iam = https://code.claude.com/docs/en/iam
- rc = https://code.claude.com/docs/en/remote-control
- plug = https://code.claude.com/docs/en/plugins/components
- cl = https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md
- sdk = https://code.claude.com/docs/en/agent-sdk/overview

---

## Summary

Claude Code offers four usable ways for a hub to get a message into a session, and several ways for a session to talk to a hub.

**Receiving**
1. **`asyncRewake` hook.** A background hook that exits 2 wakes an idle session. It is documented, available now, and works the same on every plan.
2. **Channel MCP server (`claude/channel`).** It pushes into a live session. It is a research preview, needs an allowlist or a development flag, and needs an org switch on Team accounts.
3. **Plugin monitor, or the Monitor tool.** A background command's output lines reach Claude as notifications.
4. **Native `SendMessage` socket.** It is per OS user. Whether it crosses config directories is untested and not documented.

**Sending**
- An HTTP hook POSTs hook events to the hub.
- An MCP tool lets Claude call the hub deliberately.
- Hook-run scripts can call a hub CLI.

**Locking**
- A hub-side lease, enforced by a `PreToolUse` hook. This is feasible from documented fields.

**Cross-account**
- Same-machine sockets are per OS user, not per account, and the docs key nothing to `CLAUDE_CONFIG_DIR`. This is the only transport that could cross two accounts by design, and it is **UNVERIFIED**.
- Remote Control, cloud messaging and push notifications are tied to one claude.ai account, so they cannot cross accounts.

---

## 1. Hooks

### 1.1 Events and when they fire

(hooks, as fetched 2026-10-10)

| Event | Fires | Output control |
|---|---|---|
| `Setup` | `--init-only`, or `-p` with `--init`/`--maintenance` | none |
| `SessionStart` | start, resume, clear, compact, fork | context only: `additionalContext`, `initialUserMessage`, `sessionTitle`, `watchPaths`, `reloadSkills`. Can't block |
| `UserPromptSubmit` | prompt submitted, including turns Claude starts itself. It also fires for scheduled tasks, background-subagent reports and **cross-session messages** | block (exit 2 or `decision:"block"`), `additionalContext`, `sessionTitle`. Can't rewrite the prompt |
| `UserPromptExpansion` | a typed command expands | block, `additionalContext` |
| `PreToolUse` | before a tool call | `permissionDecision` (allow/deny/ask/defer), `updatedInput`, `additionalContext`. Exit 2 blocks |
| `PermissionRequest` / `PermissionDenied` | permission decision needed / auto-mode denial | allow or deny with `updatedInput`. `PermissionDenied` can `retry` |
| `PostToolUse` / `PostToolUseFailure` | after a successful or failed call | `decision:"block"`, `updatedToolOutput`, `additionalContext`. Exit 2 shows stderr to Claude |
| `PostToolBatch` | after a parallel batch, before the next model call | exit 2 stops the loop |
| `Notification` | notification types `permission_prompt` (~6 s inactivity) and `idle_prompt` (~60 s after the turn ends, if no background agent runs) | none. `systemMessage` and `continue` are discarded |
| `MessageDisplay` | assistant text displays | display only |
| `SubagentStart` / `SubagentStop` | subagent spawned / finished | Start: context only. Stop: `decision:"block"` or exit 2 keeps it running |
| `TaskCreated`, `TaskCompleted`, `TeammateIdle` | agent-teams and task events | exit 2 blocks or keeps working |
| `Stop` | Claude finishes responding | `decision:"block"` or exit 2 continues the conversation, plus `additionalContext`. Capped at 8 consecutive continuations (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`) |
| `StopFailure` | turn ends on an API error | output ignored |
| `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove` | as named | various |
| `PreCompact` / `PostCompact` | before / after compaction | `PreCompact` can block |
| `PreModelSwitch` / `PostModelSwitch` | model switch | allow/deny/block, `additionalContext` |
| `Elicitation` / `ElicitationResult` | MCP server asks the user for input | auto-answer, or block |
| `SessionEnd` | termination. Reasons seen: `clear`, `resume`, `logout`, `prompt_input_exit`, `other` | none. Default budget **1.5 s** |

Two more events are named in the changelog: `agent.spawn` (2.1.289) and `prompt.autocomplete` (2.1.292). Both are "mod" events (cl). I did not read the mods docs, so their semantics are UNVERIFIED.

### 1.2 Hook input

Every event receives this JSON on stdin (command hooks) or as the POST body (HTTP hooks):
- `session_id`
- `transcript_path`
- `cwd`
- `hook_event_name`
- `prompt_id`
- `scratchpad_dir` (v2.1.257+)
- `permission_mode`
- `effort`

`agent_id` and `agent_type` are present **only inside a subagent** or with `--agent`.

Event-specific extras:
- `tool_name`, `tool_input`, `tool_use_id` on tool events.
- `last_assistant_message`, `background_tasks` and `session_crons` on `Stop`. The docs say the transcript may lag the current turn, so use `last_assistant_message`.
- `stop_hook_active` on `Stop`.
- `source`, `model`, `agent_type`, `session_title` on `SessionStart`. On resume or fork it also carries `seconds_since_last_response`, `context_tokens`, `prompt_cache_likely_expired` and `estimated_cache_write_usd`.
- `prompt` and `session_title` on `UserPromptSubmit`.
- `message`, `title`, `notification_type` on `Notification`.

**Session name.** No hook field is called `session_name`. Hooks get `session_title`, which is the custom title (`--name` or `/rename`).
- The status line has `session_name`. The docs state the auto-generated default display name (for example `my-app-3f`) is **not** populated there (sl).
- Whether `ListAgents` shows a name a hook can see is UNVERIFIED for auto-named sessions.
- A hook can read `CLAUDE_CODE_MESSAGING_SOCKET`, which Claude Code exports "before any hook runs, including `SessionStart`" (env-vars, xsm). The socket path is a reliable per-session identity, and it is what other sessions address.
- Do not depend on a name. Register `{session_id, socket, session_title}` with the hub at `SessionStart`.

### 1.3 Hook types

- `command` (fields `command`, `args`, `async`, `asyncRewake`, `shell`, `onFailure`; default timeout 600 s).
- `http` (POST with `url`, `headers`, `allowedEnvVars`; a 2xx JSON body uses the same output schema).
- `mcp_tool` (calls a named MCP tool; not available for `SessionStart` or `Setup`).
- `prompt` and `agent` (model-evaluated, the latter marked experimental).
- `onFailure: "block"` is new in v2.1.295 (cl).
- Settings keys: `allowedHttpHookUrls`, `httpHookAllowedEnvVars` (HTTP hooks can be restricted); `disableAllHooks`; `allowManagedHooksOnly`.
- **Hooks run outside the sandbox** (sbx, "What runs outside the sandbox").

### 1.4 Async and waking an idle session

- `async: true` runs the command in the background. Results (`additionalContext`, `systemMessage`) arrive "on the next conversation turn". "If the session is idle, the response waits until the next user interaction."
- **Exception:** "an `asyncRewake` hook that exits with code 2 wakes Claude immediately even when the session is idle." Stderr (or stdout if stderr is empty) is delivered as a system reminder.
- Claude Code still enforces `timeout` on `asyncRewake` hooks (the default is 600 s), so a hook cannot wait forever.
- Async hooks are killed at teardown in `-p` mode (hooks).
- **Inference, UNVERIFIED:** a long-poll listener started by `SessionStart` or `Stop` with `asyncRewake: true` and a hub long-poll is a push-to-idle mechanism. It must be re-armed after each wake and after each timeout. `Stop` fires after every turn, so it is a natural re-arm point, but this needs an experiment.
- Changelog fixes that touch this area:
  - 2.1.290: an endless reply loop from a plugin's async Stop hook with an unquoted script path.
  - 2.1.295: async SessionStart context re-added on every resume, and multi-line async hook JSON being ignored.

### 1.5 Hooks and subagents

Settings, managed and plugin hooks also run inside subagents, with `agent_id` and `agent_type` populated on tool events. Subagent-frontmatter hooks run only while that subagent is active. Project subagent frontmatter hooks need the workspace trust dialog accepted (v2.1.218+).

### 1.6 What can inject into an idle session

From a hook, only `asyncRewake` exit 2 (§1.4). Everything else waits for the next activity. `Notification` `idle_prompt` can observe idleness but has no output control.

---

## 2. Pushing into a running or idle session from outside

### 2.1 Native cross-session messaging (`SendMessage` / `ListAgents`)

Source: xsm. It requires v2.1.224+ on macOS and Linux, and v2.1.234+ on native Windows. On Bedrock/Vertex/Foundry, or with feature-flag fetching off, it requires v2.1.248+.

- **Addressing.** `ListAgents` lists subagents, this session's teammates, other local sessions, and (via Remote Control) cloud and other-machine sessions. A session answers to its `/rename` or `--name`, otherwise to a Claude-generated name. Duplicate names are renamed to a variant. Claude adds a short ID to the address when several share a name. `/list-agents` (alias `/peers`) shows them. `@name` mention typeahead requires v2.1.232+.
- **Scope on one machine.** Per-session Unix socket on macOS and Linux (named pipe on native Windows). It is "restricted to your operating-system user". The docs describe a private per-user directory `/tmp/cc-socks-<uid>` as the fallback. The author has observed `/run/user/1000/cc-socks/`.
- **Not documented.** Nothing I read says the socket path or listing is keyed by `CLAUDE_CONFIG_DIR` or by account. By the text, scope is "same OS user, same machine". Cross-config-dir behaviour is **UNVERIFIED**; the author's experiment E1 remains the arbiter.
- **Delivery.** The message is read between tool calls during a turn. If the session is idle, "Claude Code starts a new turn with the message." So native messaging does wake an idle session. Messages count toward usage like a typed prompt.
- **Inbound control.** `crossSessionInbound` is `accept`, `hold` or `refuse`. With no value set, the default depends on the permission-mode class of the two sessions:
  - A bypass-permissions receiver holds the message for approval unless the sender also bypasses.
  - A prompting receiver delivers.
  - Held messages show an approval dialog, which expires after `dialogExpiry` (default 5 min). The cap is 100 held messages.
  - A `-p` session cannot show the dialog, so it holds for `dialogExpiry`. To take messages unattended, start it with `crossSessionInbound: accept` via `--settings`.
  - This matches the author's observation about paused seats that only log.
- **Idle notice.** `SendMessage` `notify_when_idle` (v2.1.236+, both sessions) gives a one-shot notice when the target next goes idle or exits. It lasts 12 h, is main conversation to local sessions only, and does not work for teammates or subagents.
- **Limits.**
  - Plain text only.
  - About 1M characters.
  - Rapid bursts are refused at the sender.
  - Per-sender rate limits, with at most 50 queued messages.
  - Identical repeats are dropped.
- **A message cannot** approve a permission prompt, change config, or run a slash command. Claude is told it came from another session.
- **Posting by script.** A script can post to a socket. `CLAUDE_CODE_MESSAGING_SOCKET` and `CLAUDE_CODE_MESSAGING_TOKEN` are exported to hooks and Bash. The token is sent as `{"type":"auth","token":"..."}` as the first line (required on Windows, optional on Linux). The connection must send a complete line within 30 s.
  - A message verified as from the session's own child process is delivered even with no `crossSessionInbound` value. Verification uses process evidence on Linux.
  - The message wire format is **not documented** in the pages I read. A hub would have to reverse it, which is fragile.
- **Disabled by managed settings.** `permissions.deny: ["SendMessage","ListAgents"]` plus `crossSessionInbound: refuse`. Denying `SendMessage` also removes subagent and teammate messaging.
- **Related changes (cl).**
  - 2.1.288: delivery reporting made accurate.
  - 2.1.290: `--restricted` sessions no longer open the socket.
  - 2.1.292: similar names no longer merge.
- **Not bound.** `--bare` sessions bind no socket.
- Secondary: https://claudefa.st/blog/guide/mechanics/cross-session-messaging and similar blogs match the above and add nothing authoritative.

### 2.2 MCP channels (push)

Source: chan, chref. This is a research preview. The flags are hidden from `--help`.

- **Contract.** A stdio MCP server declares `capabilities.experimental['claude/channel']: {}` and emits `notifications/claude/channel` with `{content, meta}`. Claude sees `<channel source="..." k="v">content</channel>`. `meta` keys must be identifiers.
- **Delivery.**
  - Claude Code does not ack. Events queue in order. If Claude is busy they are batched into the next turn.
  - "Events only arrive while the session is open."
  - The docs imply idle delivery (the telegram demo wakes an idle session) but do not state it outright. **Treat as documented-by-example.**
- **Opt-in.** The server must be named in `--channels plugin:<n>@<mkt>` or `--dangerously-load-development-channels server:<n>`.
  - Being in `.mcp.json` is not enough.
  - The development flag shows a confirmation dialog, so it works only in interactive sessions. In `-p` or SDK sessions the flag is ignored and the channel doesn't register.
  - During the preview, `--channels` accepts only the Anthropic allowlist (or the org's `allowedChannelPlugins`).
- **Auth and plan.**
  - Requires claude.ai or Console API-key auth. Not available on Bedrock, Vertex or Foundry.
  - **Pro/Max without an org skip the org checks.**
  - **claude.ai Team/Enterprise: blocked until an Owner enables it** (`channelsEnabled: true`, via Admin settings > Claude Code > Channels).
  - So a Team seat needs the org Owner (the author, if they own the Team) to flip that switch.
- **Reply path.** A two-way channel exposes a normal MCP tool.
- **Permission relay.** `claude/channel/permission` plus `notifications/claude/channel/permission_request` and `.../permission`. Anyone who can reply can approve tools in the session, so the sender gate matters. Requires v2.1.234+.
- **Sender gating.** The docs say an ungated channel is a prompt-injection vector.
- **v2 MCP runtime caveat.** A channel server that negotiates protocol 2026-07-28 is not registered as a channel. Set `MCP_PROTOCOL_NEGOTIATION=legacy` (mcp). The v2 runtime is the default in some sessions from v2.1.274.
- **Host.** The server is spawned by Claude Code, so it runs outside the Bash sandbox and can reach a localhost or Unix-socket hub. It can also run an HTTP listener.
- **Changelog.** 2.1.290 hardened the permission relay against repeated reply IDs.
- **Status risk.** The contract "may change".

### 2.3 Monitor tool and plugin monitors

Source: tools, plug, sbx.

- **Monitor.** Runs a command in the background, and "each output line" is fed to Claude. It can also open a `ws://`/`wss://` URL, with each text frame becoming an event.
  - The deadline is 5 min by default, at most 30 min, and at most 10 min in `-p`.
  - Claude gets one notice at the deadline and must re-arm.
  - It is unavailable on Bedrock/Vertex/Foundry, and when `DISABLE_TELEMETRY` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set.
  - Monitor commands are sandboxed (sbx) and follow Bash permission rules. In auto mode `Monitor` allow rules are dropped, so the classifier reviews them.
  - The WebSocket source **denies private, link-local and metadata addresses**, so a loopback hub is likely denied. I only read "private, link-local, or cloud-metadata" and am inferring loopback is covered: UNVERIFIED.
  - Whether Monitor output wakes an idle session is stated only as "Claude interjects when an event arrives". Idle behaviour is UNVERIFIED.
- **Plugin monitors.** A plugin's `monitors/monitors.json` lists `{name, command, description, when}` and "runs in the background for the whole session". What it prints reaches Claude as notifications.
  - It runs with full user permissions **outside the sandbox**.
  - It starts only in **interactive** sessions, never in `-p`.
  - It receives no `${user_config.*}`.
  - Disabling the plugin mid-session does not stop a running monitor.
  - I did not read the `when` trigger details.
  - **This is a strong candidate for a hub subscriber:** `diogenes listen` unsandboxed for the session's lifetime. Idle wake is UNVERIFIED (experiment E5).

### 2.4 Remote Control and push notifications

- **Remote Control.** Connects claude.ai/code or the mobile app to a local session. It requires a claude.ai subscription (Pro, Max, Team, Enterprise). **API keys are not supported**, and on Team and Enterprise an Owner must enable the toggle (rc).
  - `claude remote-control` is a server mode. It has `--spawn same-dir|worktree|session` and `--capacity` (default 32). Auto-connect "signs in with your own claude.ai account" and grants no one else access.
  - `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`) "can't establish Remote Control sessions" (iam).
  - **Not a cross-account path.** Sessions belong to one account. Cross-machine `SendMessage` goes through Anthropic via Remote Control and is also same-account.
  - I found no public API for programmatic injection.
- **`PushNotification` tool.** Sends a desktop notification, plus a phone push when Remote Control is connected (tools). That is a push to the human, not into a session. It is unavailable on Bedrock/Vertex/Foundry. Changelog fixes in 2.1.293 and 2.1.295.
- **Scheduled wakeups.** `CronCreate` and `/loop` provide session-scoped recurring or one-shot prompts, restored on `--resume` or `--continue` if unexpired (tools; cl 2.1.290–2.1.295). They are pull, token-costing polls. I did not read `scheduled-tasks`.
- **`-p` with `--resume` or `--continue`, and stream-json.**
  - `claude -p ... --resume <id>` can continue any session by ID from any directory (v2.1.223+), or by transcript path (hl).
  - I found no statement on resuming a session that is concurrently live in another process. That risks interleaved transcript writers, so I recommend not doing it.
  - `--input-format stream-json` exists. I did not read its schema.
  - Sessions may be resumed by a short-lived `-p` worker as a poll-and-act pattern, but only for idle or ended sessions.

### 2.5 Which of these work between two accounts on one machine

| Mechanism | Cross-account on one machine | Basis |
|---|---|---|
| `asyncRewake` hook, plugin monitor, channel server, HTTP/MCP hooks | Yes. Each account's session talks to the hub independently, so no Claude-to-Claude path is needed | design: the hub is the shared point |
| Native `SendMessage` socket | **UNVERIFIED.** The socket is per OS user, and nothing documented keys it to config dir | xsm; experiment E1 |
| Remote Control, cloud messaging, `PushNotification` phone | No (single account) | rc, xsm |
| Channels | Per session. A Team account needs `channelsEnabled` set by the org | chan |

---

## 3. MCP

Source: mcp, as fetched. Everything below is in the first 100 KB or the tail I read, except where marked.

- **Transports.**
  - `http` is recommended, and `streamable-http` is accepted as an alias.
  - SSE is deprecated. Since v2.1.265 Claude Code tries HTTP first and falls back to SSE.
  - `stdio` for local processes.
  - **WebSocket (`type: "ws"`)** is supported "for servers that push events unprompted". It takes `headers` and `headersHelper`, **not OAuth**, and cannot be added through `claude mcp add --transport`, only `add-json`.
  - An entry with a `url` but no `type` is treated as stdio and skipped.
- **Scopes.** Local (default, `~/.claude.json` under the project path), project (`.mcp.json`) and user (`~/.claude.json`). Precedence is local, then project, then user, then plugin, then claude.ai connectors. The whole entry from the winning source is used, with no field merge. Managed servers (`managedMcpServers`) rank above all.
  - Project servers prompt for approval interactively, but in `-p` and SDK sessions they load **without** asking unless blocked by `disabledMcpjsonServers`.
- **Tools, resources, prompts.**
  - Tools are deferred by default behind tool search. `alwaysLoad` loads a server's tools upfront. Per-tool `_meta["anthropic/alwaysLoad"]` and `requiresUserInteraction` are honoured.
  - Resources are referenced as `@server:protocol://path`. Claude Code provides list and read resource tools automatically.
  - Prompts appear as `/mcp__server__prompt`.
- **Notifications.** On `list_changed`, interactive sessions refresh the list without reconnecting. In `-p` and the SDK only the **tool** list is refreshed. A failed refresh keeps the old list.
- **Resource subscriptions.** Not mentioned in what I read: **UNVERIFIED**. I do not know whether `resources/subscribe` is honoured, and even if it is, no documented path turns an update into a model turn.
- **Elicitation.** Form and URL modes, with an `Elicitation` hook to auto-answer. With `--permission-prompts none` (v2.1.259+) unanswered elicitations are cancelled.
- **OAuth.** `/mcp`, `claude mcp login`, `--client-id`/`--client-secret`/`--callback-port`, and `oauth.authServerMetadataUrl`/`scopes`. A 401 triggers one refresh and retry.
- **Env and headers.**
  - `${VAR}` and `${VAR:-default}` expansion in `command`, `args`, `env`, `url`, `headers`.
  - **Credential variables** such as `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` are not expanded into remote `url`/`headers`.
  - `headersHelper` is a script with a 10 s limit that runs on every connection. Per-session secrets belong there.
- **Sandbox.** Local MCP servers, hooks, plugin monitors, LSP servers, status-line commands and `apiKeyHelper` run **outside** the Bash sandbox with the user's full access (sbx). The Read, Write and Edit tools are also outside it.
- **Plugins.** One plugin can bundle skills, agents, hooks, MCP servers and monitors (plug). A plugin MCP server's tools are named `mcp__plugin_<plugin>_<server>__<tool>`. A hook matcher on the bare server key never fires for a plugin-bundled server (mcp).
- **Other limits.**
  - Tool idle timeout is 5 min for HTTP/SSE/WS and 30 min for stdio (`CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`).
  - Calls over 2 min in the main conversation move to background tasks.
  - Output is 25,000 tokens by default (`MAX_MCP_OUTPUT_TOKENS`), and text over 50,000 characters is saved to a file.
  - stdio servers must write logs to stderr only. Over-limit or non-protocol stdout disconnects the server and counts as a crash.
- **Windowing.** `CLAUDE_PROJECT_DIR` is set for stdio servers, and `roots/list` is supported.

---

## 4. Headless use and the SDK

- **`claude -p`** (hl).
  - Exit code 0 on success, 143 on SIGTERM.
  - Output formats: `text`, `json` (result, session ID, `total_cost_usd`, per-model cost), `stream-json` (newline-delimited, with `--verbose` and `--include-partial-messages` for deltas).
  - `--json-schema` returns `structured_output`.
  - The stream's `system/init` event carries model, tools, MCP servers, plugins and `capabilities`. The last line is a `result` message.
  - `--resume <id|transcript path>` and `--continue`. Session IDs are captured from `json` output (`.session_id`).
  - **`--max-turns` exists.** I did not verify it on this page: UNVERIFIED here.
  - Other relevant flags: `--allowedTools`, `--permission-mode`, `--permission-prompts none` (v2.1.259+), `--max-budget-usd`, `--settings`, `--mcp-config`, `--agents`, `--plugin-dir`, `--forward-subagent-text`.
  - Background work at exit: a `-p` run waits for background commands, subagents, Monitor watches and pending `/loop` wakeups, with a 10 min idle ceiling by default (`CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`).
  - **`-p` binds an inbox socket** like an interactive session, so a long-running worker can receive messages (xsm), except in `--bare`.
- **`--bare`.**
  - Skips hooks, plugins, MCP servers, auto memory and CLAUDE.md, and **never reads OAuth or the keychain**, so it needs `ANTHROPIC_API_KEY` or `apiKeyHelper`.
  - It binds no inbox socket and runs no background tasks.
  - The docs say it "will become the default for `-p` in a future release", which would change any `-p` worker that relies on hooks and plugins.
- **Agent SDK** (sdk; TypeScript and Python packages).
  - It "runs the Claude Code binary". It supports hooks, subagents, MCP, permissions, sessions (resume and fork), skills and plugins loaded by local path.
  - It can host a long-lived programmatic session, and a small daemon could drive sessions.
  - **Auth:** the overview carries the note: "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK. Use the API key authentication methods..."
  - That note is about products offered to others. Whether a solo developer's own daemon on their own subscription is permitted is not addressed and is **UNVERIFIED**. This is a question for Anthropic support, in writing.
  - A daemon driven by a subscription OAuth token (`CLAUDE_CODE_OAUTH_TOKEN`) is documented for scripts and CI (iam), but not specifically for the SDK.
  - SDK sessions do not spawn agent-team teammates (teams).
  - Hooks can be callbacks (an SDK-only form), and the SDK can answer permission dialogs via `canUseTool` (hl, mcp).
  - I did not read the SDK pages beyond the overview.

---

## 5. Several accounts on one machine

- **`CLAUDE_CONFIG_DIR`** (iam, sbx, claude-directory).
  - Docs: "Each directory has its own settings, session history, and claude.ai login or API key."
  - Credentials: `.credentials.json` lives under it on Linux. On macOS the keychain entry is keyed to the directory.
  - sbx lists: "In `~/.claude`, or the directory `CLAUDE_CONFIG_DIR` points to: most of its contents, plus `~/.claude.json` and the `.credentials.json` credential store". So `~/.claude.json` (user and local MCP config) appears to move with it.
  - The claude-directory page says every `~/.claude` path lives under it, which covers projects and transcripts, plugins, teams, tasks and channel state (`~/.claude/channels/...`).
  - **Not covered:** the messaging socket directory. The docs describe `/tmp/cc-socks-<uid>` as the fallback and give no config-dir key. UNVERIFIED.
  - **Not relocated:** a Console sign-in without an API key is stored outside the config dir (iam). This is not the author's case.
  - Anthropic profiles live in `~/.config/anthropic`, outside the config dir.
- **Login per config dir.** `CLAUDE_CONFIG_DIR=~/.claude-work claude` runs the login flow for that directory the first time (iam).
  - Changelog 2.1.290: first launch re-asked for a login method when a credentials file was already present (fixed). 2.1.296: claude.ai skill installs hung when several sessions shared one config dir (fixed).
  - Everything installed (the hub plugin, hooks, MCP entries) must be installed per config dir.
- **Auth precedence.** `ANTHROPIC_API_KEY` and `apiKeyHelper` outrank subscription OAuth (iam). An exported API key in the shell silently overrides a seat login. `/status` shows which is active.
- **Team and Enterprise.** (iam; support article "What is the Team plan?" https://support.claude.com/en/articles/9266767-what-is-the-team-plan; fetched 2026-10-10, support page, secondary to docs for Claude Code).
  - Both seat types include Claude Code.
  - Standard seats get 1.25× the Pro per-session allowance, and premium seats 6.25×. Both have a weekly limit across all models, per member and not pooled.
  - Prepaid usage credits can be enabled org-wide.
  - List prices: standard $25 monthly or $20 annual, premium $125 monthly or $100 annual, minimum 2 members.
  - The support page says nothing about a Team seat beside a personal account.
  - Third-party pricing summaries (e.g. https://www.morphllm.com/claude-code-team-pricing) disagree on the weekly-limit promotion window, so ignore them for limits.
  - Status-line `rate_limits` is present only for claude.ai Pro and Max subscribers and gateway spend limits (sl). **A Team seat may show no `rate_limits`.** UNVERIFIED.
- **Team admin features that affect Diogenes:** `channelsEnabled` (managed), `allowedChannelPlugins`, `allowManagedHooksOnly`, server-managed settings, `forceLoginOrgUUID`. A Team org can lock these.

---

## 6. The sandbox

Source: sbx plus the settings reference (as fetched).

- **Scope.** Bubblewrap on Linux. It covers Bash, PowerShell and Monitor commands and their children. Read, Write, Edit, WebFetch, WebSearch, hooks, local MCP servers, plugin monitors, LSP, the status line and `apiKeyHelper` are outside.
- **Filesystem.**
  - Writes default to the working directory, a per-user temp dir and `--add-dir` directories.
  - Settings: `sandbox.filesystem.allowWrite`, `denyWrite`, `denyRead`, `allowRead` (a narrower rule wins; a deny holds inside a wider allow), `allowManagedReadPathsOnly`, `disabled` (v2.1.216+).
  - Reads default to most of the machine.
  - Protected paths cannot be lifted by `allowWrite`.
- **Network.** There is no direct route out. Traffic goes through a proxy filtered by `network.allowedDomains` (starts empty) and `deniedDomains`. Other hosts prompt, or are blocked under `allowManagedDomainsOnly`. Tools that ignore the proxy variables fail even for allowed hosts, which includes most database drivers.
  - `network.httpProxyPort`/`socksProxyPort` route through your own proxy, which then becomes responsible for filtering.
  - A hostname that resolves to a local address is refused unless the IP is listed, e.g. `"127.0.0.1:8080"` in `allowedDomains`. That is the documented route for proxied localhost access (sbx, "Hostnames that resolve to local addresses").
  - `excludedCommands` runs matching commands unsandboxed with no network proxy. It does not apply to a call that adds `cd` or command substitution.
  - `failIfUnavailable`, and `allowUnsandboxedCommands: false` to ignore the `dangerouslyDisableSandbox` retry.
- **Unix sockets and localhost, by platform.**
  - **Linux/WSL2, localhost:** a sandboxed command's `localhost` is private to it, so it **cannot reach a host loopback port**. `allowLocalBinding` is macOS-only and has no effect here (sbx, "A command fails to reach a server on localhost"). The documented answer is `excludedCommands` for the command that needs the host server.
  - **Linux/WSL2, Unix sockets:** `allowUnixSockets` is **ignored on Linux** (macOS only). The seccomp filter blocks `socket(AF_UNIX, ...)`, and `sandbox.network.allowAllUnixSockets: true` is the only way to permit them. If the optional seccomp filter is **not installed** (`npm install -g @anthropic-ai/sandbox-runtime`), the sandbox "doesn't block Unix-socket calls". `/sandbox` shows this on its Dependencies tab.
  - Whether a socket file path is reachable through the bwrap mounts when connect is allowed is not stated: UNVERIFIED.
  - The sbx text warns that opening Unix sockets, such as `docker.sock`, can break the sandbox.
- **Relevance to a hub on this machine.** A Bash-run hub CLI cannot reach a loopback TCP hub by default on Linux. Three routes:
  - (a) Put the hub client in `excludedCommands`, e.g. `"excludedCommands": ["diogenes *"]`.
  - (b) Allow Unix sockets (`allowAllUnixSockets: true`, or no seccomp filter installed) and make the hub listen on a Unix socket.
  - (c) Avoid the shell entirely: hooks, MCP servers and plugin monitors are unsandboxed and can reach the hub directly. This is the cleanest route.
- **Admin-required sandbox.** Under managed settings a repository cannot widen `excludedCommands`, `allowWrite` and socket entries (sbx; requires v2.1.285+ for the current rule).

---

## 7. Identity and telemetry for a hook or status line

- **Status line** (sl). A `statusLine` command receives JSON on stdin. Fields I confirmed:
  - `session_id`, `session_name` (custom name or AI-generated title; absent if neither exists), `transcript_path`, `workspace`, `model`.
  - `cost.total_cost_usd`, `cost.total_duration_ms`, `cost.total_api_duration_ms`.
  - `context_window.{total_input_tokens, total_output_tokens, context_window_size (200000 or 1000000), used_percentage, remaining_percentage, current_usage}` and `exceeds_200k_tokens`. `used_percentage` is input tokens only, and may be null early or after `/compact`.
  - `effort.level`.
  - `rate_limits.{five_hour,seven_day}.{used_percentage, resets_at}` (epoch seconds). These appear only for claude.ai Pro and Max subscribers, only after the first API response, and each window may be absent. `rate_limits.spend_limit.*` applies behind a Claude apps gateway.
  - `agent` (an object, present in subagent or `--agent` contexts). `subagentStatusLine` payloads got `agentType` in 2.1.293.
  - Cost is a client-side list-price estimate.
  - The status line runs unsandboxed.
- **Hooks.** The common fields in §1.2 are all hooks get. Hook input carries no cost, no context figures and no rate limits. A status-line script must write them to a file or the hub for a hook to read, which matches the author's current `~/.claude/usage-latest.json` practice.
- **Name.** See §1.2: `session_title` in hook input for custom titles, `session_name` in the status line, the socket path for addressing. I could not confirm how `ListAgents` renders an auto-named session.
- **Context-window hint.** `SessionStart` on resume reports `context_tokens` (hooks).

---

## 8. Built-in multi-agent coordination

- **Agent teams.** (teams) Experimental, off unless `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.
  - It has a lead, teammates, a shared task list and a mailbox. A subagent that Claude names becomes a teammate while teams are on.
  - Mailbox: `~/.claude/teams/{team}/inboxes/{agent}.json`. Config: `~/.claude/teams/{team}/config.json`. Tasks: `~/.claude/tasks/{team}/`. The team name is `session-` plus the first 8 characters of the session ID.
  - Task claiming uses file locking.
  - Limits: **one team per session, scoped to that session ("You can't ... share a team across sessions")**, no nested teams, no resumption of in-process teammates, a fixed lead, and it does not spawn in `-p` or SDK sessions.
  - Hooks: `TeammateIdle`, `TaskCreated`, `TaskCompleted`.
  - Teammates use the same `SendMessage` tool, and a shared deny rule removes both.
- **Task tools** (`TaskCreate`, `TaskGet`, `TaskList`, `TaskUpdate`) are a session-local list, not a cross-session store.
- **Reuse or conflict for Diogenes.** There is nothing to reuse for cross-session or cross-account locking, since both the team and the task list are one session's. The risk is conflict:
  - With teams on, Claude may turn named subagents into teammates, changing the author's seat-and-subagent model.
  - Both systems use one `SendMessage` tool name.
  - **Recommendation:** leave teams off (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=0` in the seat's settings) so that dispatch stays plain subagents. Diogenes then owns cross-session state. Mirroring the shape of the mailbox (one JSON message each, validated on read) is fine.

---

## What this means for Diogenes

Ranked by robustness, as a recommended design for Claude Code.

**A. Receiving** (hub to session)

1. **Primary: a Diogenes plugin shipping a `SessionStart` + `Stop` `asyncRewake` hook, with an MCP server alongside.**
   - The hook runs `diogenes wait --session $SESSION_ID --timeout 540` and long-polls the hub.
   - When mail arrives it prints a short digest to stderr and exits 2. That wakes an idle session with a system reminder (§1.4). Print only a pointer such as "3 unread, call `inbox`", and let Claude pull the bodies through MCP. That keeps messages data, not instructions, and keeps wake text small.
   - Re-arm on `Stop` (fires after every turn). A lockfile keyed by `session_id` prevents stacked listeners.
   - Why it ranks first: documented wake behaviour, no admin switch, works on both accounts, and it is plain hook machinery that survives the channels preview changing.
   - Weakness: the 600 s default timeout needs a re-arm cadence, and the timeout ceiling is UNVERIFIED.
2. **Piggyback on turn boundaries (always on):**
   - A `UserPromptSubmit` hook injects `additionalContext` with unread counts. It also fires for cross-session messages and scheduled turns.
   - A `PostToolUse` or `PostToolBatch` hook does the same mid-turn.
   - A `Stop` hook may continue the conversation (`decision:"block"`) when mail is pending, capped at 8 continuations.
3. **Secondary: a plugin monitor** (`diogenes listen`, unsandboxed, whole session) as a second push path, once E5 shows it wakes idle.
4. **Tertiary: a channel server**, for a better UX (`<channel source=...>` tags, replies, permission relay) once the preview matures. Today it needs `--dangerously-load-development-channels` (interactive, with a confirmation) plus `channelsEnabled` for the Team account.
5. **Native `SendMessage`** stays as the same-account, same-config-dir path. Do not build on it across accounts until E1 shows it works.
6. **Last-resort pull** is a `/loop` or `CronCreate` poll of `inbox`, which costs tokens each fire.
7. A `-p` worker that `--resume`s a **live** session is unsafe: UNVERIFIED and likely to interleave transcript writes.

**B. Sending** (session to hub)

1. **MCP tools** (`send`, `inbox`, `ack`, `lock_*`, `search_research`), because Claude calls them deliberately and they run outside the sandbox. This is the primary route.
2. **HTTP hooks** for automatic telemetry and delivery acks:
   - A `SessionStart` hook registers `{session_id, socket path, session_title, cwd, account}`.
   - A `UserPromptSubmit` hook acks receipt.
   - A `SessionEnd` hook sends a goodbye (1.5 s budget, so keep it tiny).
   - Use `allowedHttpHookUrls` and `httpHookAllowedEnvVars` to pin the hub URL.
3. A hub CLI via Bash only if it is put in `excludedCommands` or the hub is on a Unix socket with `allowAllUnixSockets` (§6).

**C. Locks**
- The lock lives **in the hub** as a lease: `{resource, holder = (session_id, account), expires, token}`, taken and renewed through MCP tools.
- Enforcement is a `PreToolUse` hook (command or HTTP, matcher `Edit|Write|MultiEdit|Bash`) that asks the hub "does this session hold the writer lease?" and returns `permissionDecision: "deny"` with a reason when it doesn't. This replaces the `BOARD.md` marker (the author's thirteen take hazards: a lock that isn't pushed, a release that is announced but not recorded, and so on). The hub makes take, push and release one transaction. Fail closed with `onFailure: "block"` (v2.1.295+).
- Subagents inherit the hook. Hook input carries `session_id` plus `agent_id`, so attribute leases to the seat and record which subagent acted.
- Release on `SessionEnd`, but rely on **TTL plus heartbeat** because of the 1.5 s budget and crashes. Heartbeat from the status-line script or the `Stop` hook.
- A hook can't see Bash writes it didn't match, and a deny rule is not a sandbox. For real exclusion, pair with `sandbox.filesystem.denyWrite` on the guarded paths or separate worktrees.

**Cross-cutting points**
- Install per config dir. Each account needs its own copy of the plugin, hooks and MCP entries, and each registers with the hub under its own account ID.
- Hook JSON gives `session_id` and the transcript path, but not model, cost or limits. Have the status-line script push those to the hub, and handle `rate_limits` being absent on a Team seat.
- Leave agent teams off.
- `--bare` will become the default for `-p` and skips hooks and plugins. Hub-using `-p` workers must not pass `--bare`, and should pass `--plugin-dir`, `--mcp-config` and `--settings` explicitly (this is the documented way to load them).
- Messages are data. Wrap hub-delivered text in a fixed envelope and use the hook's sender allowlist, as the channels docs advise.
- Gemini and GPT harnesses can use the same hub contract: long-poll or a file-inbox bridge, with locks in the hub.

---

## Open questions

Experiments (read-only so far; the author or a seat should run these). Use throwaway directories and `--name` to tell sessions apart.

**E1. Cross-account `SendMessage`.**
```
# terminal 1
CLAUDE_CONFIG_DIR=~/.claude claude --name probe-a
# terminal 2
CLAUDE_CONFIG_DIR=~/.claude-team claude --name probe-b
```
In each, run `/status` (note `Peer address`) and `/list-agents`. Then ask probe-a to message probe-b. Also run `ls -la /run/user/1000/cc-socks /tmp/cc-socks-1000 2>&1`. Pass: each lists the other and the message arrives.
- If both appear, repeat with `crossSessionInbound: "accept"` in both user settings to separate listing from delivery.
- If neither lists the other, check whether each account's sockets sit in different directories.

**E2. `asyncRewake` wakes an idle session.** Put this in a project `.claude/settings.json`:
```json
{"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"/tmp/wake.sh","asyncRewake":true,"timeout":90}]}]}}
```
`/tmp/wake.sh`: `sleep 45; echo "DIOGENES WAKE TEST: 1 unread" >&2; exit 2`. Start `claude`, send one trivial prompt, leave it idle past 45 s.
- Pass: a new turn starts on its own.
- Next, `"timeout": 3600` to find the ceiling, and a `Stop` re-arm to confirm repeats.
- Also try the same with `-p` and `--input-format stream-json` kept open.

**E3. Channel.** Copy the `webhook.ts` from the channels reference. Run `claude --dangerously-load-development-channels server:webhook` on both accounts (the Team account needs `channelsEnabled: true` from its Owner), then `curl -X POST localhost:8788 -d "ping"` while the session is idle. Record whether an idle session wakes. Repeat with `MCP_PROTOCOL_NEGOTIATION=legacy` if registration fails.

**E4. Sandbox reach (Linux).** In a sandboxed session, ask Claude to run:
```
python3 -c "import socket;s=socket.socket(socket.AF_UNIX);s.connect('/tmp/hub.sock');print('ok')"
curl -s http://127.0.0.1:8788/ -m 3
```
Run each with defaults, then `"sandbox":{"network":{"allowAllUnixSockets":true}}`, then `allowedDomains:["127.0.0.1:8788"]` (proxy route), then `excludedCommands:["curl *"]`. Check `/sandbox` for whether the seccomp filter is installed. Record which succeed.

**E5. Plugin monitor wakes idle.** Build a minimal plugin with `monitors/monitors.json`: `[{"name":"hub","command":"sleep 60; echo HUB-PING","description":"test"}]`. Install it, start a session, send one prompt, then leave it idle. Pass: Claude reacts to `HUB-PING` while idle. Also test `when` after reading `manifest-reference#monitors`.

**E6. Lock hook.** `PreToolUse` command hook, matcher `Edit|Write|Bash`, that reads stdin JSON, queries a stub lock file, and prints `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"no lease"}}`. Verify the deny, that it applies inside a subagent (`agent_id` present), and fail-closed behaviour with `"onFailure":"block"` when the hub is down.

**E7. `SessionEnd` and crash.** Write a `SessionEnd` hook that takes 3 s. Observe truncation at 1.5 s, then with `"timeout"` raised. Kill -9 a session to confirm the TTL path is needed.

**E8. What a peer message looks like to `UserPromptSubmit`.** Log hook stdin to a file, then send a `SendMessage` from another session. Record `prompt`, `prompt_id` and any sender field, to see whether delivery can be acked and attributed by hook.

**E9. Name visibility.** `SessionStart` hook that dumps stdin plus `env | grep CLAUDE_CODE_MESSAGING`. Compare `session_title` and `CLAUDE_CODE_MESSAGING_SOCKET` with `/list-agents` and with the status line `session_name`, for auto-named versus `--name` sessions.

**E10. Socket framing.** If native cross-account works and the author wants to post from the hub: `strace -f -e trace=connect,write,sendto -s 2000 -p <sender pid>` during a `SendMessage` to read the wire format. This is for research only: the format is undocumented and may change.

**For the author.**
- Does a solo developer's SDK daemon on a subscription fit Anthropic's terms? The SDK overview note is about offering claude.ai login to third parties. Ask support in writing, and prefer `claude -p` plus hooks and MCP.
- Is the Team Owner the author? Channels on the Team seat need `channelsEnabled`.
- Does the Team seat's status line produce `rate_limits`?

**Outside my question.**
- **Plugin monitors and `asyncRewake` hooks run with full user access, unsandboxed.** A hub plugin installed per config dir is trusted code on both accounts, so the plugin must be pinned and reviewed like a dependency.
- A channel server accepts messages from whatever the hub forwards, and relayed permission verdicts can approve tool use. Do not declare `claude/channel/permission` unless the sender gate is strong.

Sources (all fetched 2026-10-10):
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/mcp
- https://code.claude.com/docs/en/channels
- https://code.claude.com/docs/en/channels-reference
- https://code.claude.com/docs/en/cross-session-messaging
- https://code.claude.com/docs/en/tools-reference
- https://code.claude.com/docs/en/statusline
- https://code.claude.com/docs/en/sandboxing
- https://code.claude.com/docs/en/settings-reference
- https://code.claude.com/docs/en/env-vars
- https://code.claude.com/docs/en/headless
- https://code.claude.com/docs/en/agent-sdk/overview
- https://code.claude.com/docs/en/agent-teams
- https://code.claude.com/docs/en/iam
- https://code.claude.com/docs/en/remote-control
- https://code.claude.com/docs/en/plugins/components
- https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md
- https://support.claude.com/en/articles/9266767-what-is-the-team-plan
- Secondary: https://claudefa.st/blog/guide/mechanics/cross-session-messaging, https://www.morphllm.com/claude-code-team-pricing