<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-r1b-claude-code-deep-2026-10-10.md: a read-only API-credits job (claude-opus-5-5,claude-haiku-5-5, 80/250 turns, $4.2446 by the CLI (the bill is about two-thirds)). Its prompt is prompts/dio-r1b-claude-code-deep-2026-10-10.md. -->

# Claude Code (2.1.296): deep second pass on cross-session coordination surfaces

Job: dio-r1b-claude-code-deep-2026-10-10 · Date: 2026-10-10 · Model: Opus 5.5 (`claude-opus-5-5`) · Tools: Read, Grep, Glob, WebFetch (read-only; no command execution)

**Limits**
- **Docs only.** Everything here comes from documentation and CHANGELOG text read on 2026-10-10. I ran nothing, so no behaviour was measured.
- **Raw pages read whole.** The `.md` form of most doc pages came back as raw Markdown. I read these complete:
  - cross-session-messaging, channels, channels-reference;
  - scheduled-tasks, sessions, authentication, agent-sdk/overview, legal-and-compliance;
  - plugins/mods overview, events, api, reference, interface and admin.
- **Large pages read in 100 000-character chunks.** I read every chunk of hooks (262 610 characters) and tools-reference. Of sandboxing, env-vars and claude-directory, I read the sections I cite.
- **Partly read:**
  - settings-reference: characters 0–400 000 of 419 872.
  - agent-view: the whole page, in two calls.
  - sub-agents: characters 0–100 000 of 108 415.
  - errors: only its lookup table. The sections themselves fell outside the chunk I read.
- **CHANGELOG** (986 110 characters): read in 100k chunks with keyword prompts, from 2.1.296 back to 1.0.6. The summariser caps quotes at 125 characters, so some changelog lines are opening fragments (marked "…"). Three lines were recovered in full by asking for them in segments.
- **Not read:**
  - the claude.ai consumer or commercial terms themselves;
  - the `mods/types/claude-code.d.ts` declarations;
  - the remote-control page (the first report covered it);
  - the plugin `manifest-reference#monitors` `when` details.
- Pages carry no "last updated" stamp. Every quote is "as fetched 2026-10-10".

**Source key** (all fetched 2026-10-10; I used the `.md` forms):

| Key | URL |
|---|---|
| xsm | https://code.claude.com/docs/en/cross-session-messaging.md |
| hooks | https://code.claude.com/docs/en/hooks.md |
| chan | https://code.claude.com/docs/en/channels.md |
| chref | https://code.claude.com/docs/en/channels-reference.md |
| tools | https://code.claude.com/docs/en/tools-reference.md |
| sched | https://code.claude.com/docs/en/scheduled-tasks.md |
| av | https://code.claude.com/docs/en/agent-view.md |
| sess | https://code.claude.com/docs/en/sessions.md |
| sub | https://code.claude.com/docs/en/sub-agents.md |
| cdir | https://code.claude.com/docs/en/claude-directory.md |
| env | https://code.claude.com/docs/en/env-vars.md |
| sref | https://code.claude.com/docs/en/settings-reference.md |
| sbx | https://code.claude.com/docs/en/sandboxing.md |
| auth | https://code.claude.com/docs/en/authentication.md |
| sdk | https://code.claude.com/docs/en/agent-sdk/overview.md |
| legal | https://code.claude.com/docs/en/legal-and-compliance.md |
| mods | https://code.claude.com/docs/en/plugins/mods/overview.md |
| mev | https://code.claude.com/docs/en/plugins/mods/events.md |
| mapi | https://code.claude.com/docs/en/plugins/mods/api.md |
| mref | https://code.claude.com/docs/en/plugins/mods/reference.md |
| mui | https://code.claude.com/docs/en/plugins/mods/interface.md |
| madm | https://code.claude.com/docs/en/plugins/mods/admin.md |
| plugc | https://code.claude.com/docs/en/plugins/components.md |
| sl | https://code.claude.com/docs/en/statusline.md |
| mcp | https://code.claude.com/docs/en/mcp.md |
| cl | https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md |

---

## Headline findings (what changes from round 1)

1. **Mods give a second documented way to wake an idle session, and they can draw a Diogenes UI.**
   - Mods are in-process JavaScript plugins, on since v2.1.287.
   - A mod's timer can call `$.prompt.submit`, which "waits until the session is idle and then starts a new turn" (mapi).
   - Mods run unsandboxed and have panes, a band above the prompt, a status line, toasts, `$.session.send`, and `$.session.usage()` (which includes rate limits).
   - **This beats `asyncRewake` as the primary receive path.** It has no hook timeout to re-arm, and it can draw the inbox, roster and locks.
2. **`CLAUDE_CONFIG_DIR` relocates "All settings, session history, and plugins" (env).** That includes:
   - the `sessions/` registry (cdir);
   - the agent-view supervisor, which "runs as a separate instance with its own sessions" (av);
   - the mods `$.store` (mui).

   **The docs never key the messaging socket directory to it.** The socket is restricted per OS user, and its fallback is `/tmp/cc-socks-<uid>` (xsm). So both accounts very likely share one socket directory. Whether `ListAgents` lists across config dirs is still **UNVERIFIED** (E1).
3. **Resuming a live session interleaves its transcript**, verbatim (sess). Round 1's warning is confirmed.
4. **Channels never say they wake an idle session.** A channel is a stdio MCP server. On a Team org it needs an Owner switch. A custom channel needs the dev flag, which is interactive-only, unless the org allowlists it.
5. **The `Monitor` tool's WebSocket source** denies "private, link-local, or cloud-metadata" addresses. Loopback is not named. Monitor's idle behaviour is not stated.
6. **The SDK and subscription text is now quoted from the legal page**, including: "Advertised usage limits for Pro and Max plans assume ordinary, individual usage of Claude Code and the Agent SDK." (legal)

---

## 1. Cross-session messaging (xsm, read in full)

**Transport and scope**
- "On this machine | Over a per-session socket on macOS and Linux, or a per-session named pipe on native Windows, never through Anthropic servers". Other machines go "Through Anthropic servers, arriving over that machine's Remote Control connection"; cloud sessions go "Through Anthropic servers, straight to the cloud session".
- "On macOS and Linux, Claude Code restricts the socket to your operating-system user. … Either way, on a shared machine another user's sessions can't deliver to it."
- "A session inside a container and a session on the host can't reach each other. Two sessions inside the same container can still message each other". So **a docker-sandboxed agent cannot use native messaging with host sessions.**
- **Account and `CLAUDE_CONFIG_DIR`:** the page never mentions either for local sessions. The listing describes "Your other local sessions: Claude Code sessions running on the same machine, including background sessions. A session appears only when it binds an inbox socket."
- Only beyond-machine reach is account-bound: "Claude finds your cloud sessions and your sessions on other machines from a session that is connected to Remote Control, which needs a claude.ai sign-in as this session's active authentication… Claude can't find those sessions with an API key".

**How the socket directory is chosen**
- The default directory is **not documented**. The only text: "Claude Code also refuses to create the socket in a directory it can't accept, for example one that another user owns, and uses a private per-user directory, `/tmp/cc-socks-<uid>`, instead. When it can't accept any directory, the session runs without an inbox: … `/status` shows `unavailable` and the reason in its `Peer address` row".
- cl 2.1.248, in full: "Improved cross-session messaging: falls back to a private per-user `/tmp` directory when the default one can't be used, and the notice and `/status` name the directory to fix".
- cl 2.1.233, in full: "Hardened the auto-generated cross-session messaging socket directory on shared `/tmp`: a pre-planted symlink or another user's directory is now refused instead of used".
- cl 2.1.162 (paraphrase forced by the 125-character cap): `SendMessage` silently broke when the temporary-directory variable `CLAUDE_CODE_TMPDIR` pointed to a deeply nested path.
- **Inference (UNVERIFIED):** the default is a per-uid runtime directory. The author sees `/run/user/1000/cc-socks/`, which looks like `$XDG_RUNTIME_DIR`. The temp directory has played a part at some point. Nothing in the docs or changelog ties the socket directory to `CLAUDE_CONFIG_DIR`.

**The permission-mode hold** (quoted)
- "When no value applies, Claude Code decides per message from the two sessions' permission modes. It groups sessions that bypass permission prompts into one class, and every other session into the other. Plan mode counts as bypassing in interactive terminal sessions with bypass permissions available, and auto, `acceptEdits`, and `dontAsk` count as prompting".
- "The receiving session prompts for permissions: Claude Code delivers each message. It holds one for your approval only when the sending session identifies itself as bypassing permission prompts."
- "The receiving session bypasses permission prompts: Claude Code holds each message for your approval. It delivers one only when the sending session identifies itself as also bypassing."
- Dialog: "unanswered past the `dialogExpiry` deadline, Claude Code closes it and drops the message. The deadline defaults to five minutes." Background sessions: "While no terminal is attached to a background session, Claude Code leaves the dialog open past the deadline."
- "Claude Code holds at most 100 messages, and past that drops the oldest."
- `-p`: "Set `dialogExpiry` to `"never"` to keep default-held messages until the session ends. A message held by an explicit `hold` setting doesn't expire".
- **Precedence** (sref): "Claude Code reads managed settings first, then the `--settings` flag, then user settings, and applies the first value found. … When none of the trusted sources sets a value, a project or local `hold` or `refuse` still applies". An unrecognised value "holds inbound messages".
- `dialogExpiry` (sref): "string, one of `"60s"`, `"5m"`, `"10m"`, or `"never"`… Default: `"5m"`". Scope "User or managed". `CLAUDE_CODE_USER_DIALOG_TIMEOUT_MS` overrides it per session.

**Remote Control and cloud**
- "`offline`: that session's Remote Control connection has dropped. The message goes through, but arrives only after that session's machine reconnects."
- "If this session isn't connected to Remote Control when Claude sends to a session beyond this machine, the message still goes through, but without a reply address".
- `isolatePeerMachines: true` requires approval for every beyond-machine send. "Claude Code doesn't prompt for messages between sessions on the same machine."

**`notify_when_idle`**
- "Idle here means the session finished a turn with nothing queued." It "Requires Claude Code v2.1.236 or later in both sessions."
- "On its own, Claude Code subscribes without starting a turn or spending tokens in the watched session, and sends the notice right away if that session is already idle."
- "If the asking session is idle, Claude Code starts a new turn with the notice."
- "If no notice arrives within 12 hours, Claude Code drops the subscription".
- "`refuse` on either side: nothing arrives… `hold` on either side: … the asking session shows the notice in your transcript without delivering it to Claude."
- "Only the Claude in your main conversation can subscribe, and only to your sessions on this machine."

**Size and rate limits**
- "Claude Code refuses a message to a session on this machine once its serialized form passes about a million characters."
- "Rapid bursts to one session are refused at the sender".
- "rate-limits repeated messages per sender, drops identical repeats arriving within a short window, and queues at most 50 accepted messages".
- `summary` (tools): "Claude Code truncates a summary longer than 200 characters".

**Delivery guarantees**
- "The receiving Claude reads the message between tool calls during an active turn… When the receiving session is idle, Claude Code starts a new turn with the message."
- Three outcomes: "Delivered", "Held", "Refused".
- Nothing promises durability across a receiver restart. Held messages live in the running process. Expired held messages are reported "as expired to a sender it can reach".
- cl 2.1.271: "`SendMessage` results no longer imply it was read" (fragment). So **a send result is a queueing acknowledgement, not proof the message was read.** Diogenes needs its own read receipts.

**Posting by script** (unchanged from round 1, now quoted)
- "Claude Code closes a connection that hasn't sent a complete line within 30 seconds".
- An auth line is "optional" on Linux.
- Own-child messages are verified "by process evidence even for a child that has already exited" on Linux.
- A non-child post "asserts no permission class, so a session that bypasses permission prompts holds it".
- The message wire format beyond "a complete line" is **not documented**.

---

## 2. Channels (chan, chref, read in full)

**What a channel is**
- "A channel is an MCP server that pushes events into your running Claude Code session". In chref: "Claude Code spawns it as a subprocess and communicates over stdio."
- There is **no WebSocket, file or Unix-socket channel source.** The server may itself listen on anything; the example binds `hostname: '127.0.0.1'` port 8788.
- The v2 MCP runtime caveat still applies (mcp, quoted): "a channel server that negotiates MCP protocol revision 2026-07-28 can't deliver channel messages… set `MCP_PROTOCOL_NEGOTIATION` to `legacy`".

**Who can write to one**
- Whoever the server lets through: "An ungated channel is a prompt injection vector. Anyone who can reach your endpoint can put text in front of Claude."
- Official plugins: "only IDs you've added can push messages, and everyone else is silently dropped."
- "Being in `.mcp.json` isn't enough to push messages: a server also has to be named in `--channels`."

**Opt-in, plan and flags**
- "claude.ai Team and Enterprise: channels are blocked until an Owner enables them."
- "Pro and Max users without an organization skip these checks entirely".
- With `channelsEnabled` off, "the MCP server still connects and its tools work, but channel messages won't arrive."
- **Dev flag:** "Run the development flag in an interactive session… If you pass it in non-interactive mode with `-p` or through the Agent SDK, Claude Code ignores the flag and the channel doesn't register."
- **Allowlisted plugins:** these work in `-p`: "When you run channels in non-interactive mode with `-p`, tools that need terminal input… are disabled".
- **Org allowlist:** "On Team and Enterprise plans, an admin can instead include your plugin in the organization's own `allowedChannelPlugins` list". That would remove the dev-flag problem on the Team account.

**Address restrictions.** None on channels themselves. (The WebSocket address rule belongs to the `Monitor` tool; see §4.)

**Does an event wake an idle session?**
- **Not stated.** The page says: "Events only arrive while the session is open"; "Events queue into the session and are processed in order. If several notifications arrive while Claude is busy, they're delivered together on the next turn". In the walkthrough: "You'll then see Claude start responding".
- "Claude Code doesn't acknowledge notifications… drops the events silently" when the channel isn't registered. Idle wake remains **UNVERIFIED** (E3).

---

## 3. Hooks (hooks, read in full)

**Full event list** (lifecycle table, verbatim names):
- `SessionStart`, `Setup`, `UserPromptSubmit`, `UserPromptExpansion`
- `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`
- `Notification`, `MessageDisplay`
- `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `Stop`, `StopFailure`, `TeammateIdle`
- `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`
- `PreCompact`, `PostCompact`, `PreModelSwitch`, `PostModelSwitch`
- `Elicitation`, `ElicitationResult`, `SessionEnd`

`agent.spawn` and `prompt.autocomplete` are **mod** events, not settings-hook events (§6).

**`asyncRewake`: exact text**
- Field: "If `true`, runs in the background and wakes Claude on exit code 2. The hook's stderr, or stdout if stderr is empty, is shown to Claude as a system reminder so it can react to a long-running background failure".
- Timeout: "Once an async hook is running in the background, Claude Code doesn't enforce `timeout` on it. Claude Code still enforces `timeout` on a hook you run with `asyncRewake`."
- Default `timeout` "600 for `command`". **No maximum is documented.**
- Limitation: "If the session is idle, the response waits until the next user interaction. Exception: an `asyncRewake` hook that exits with code 2 wakes Claude immediately even when the session is idle." Also: "Each execution creates a separate background process."
- `-p`: "Claude Code kills any async hook still running at teardown and finalizes it with outcome `cancelled`".
- `onFailure` "has no effect on… command hooks that set `async` or `asyncRewake`".
- **Re-arming is not documented.** Each firing of the configured event starts a fresh process.
- cl (top of the 2.1.28x section, fragment): "Fixed hooks configured with `asyncRewake` waking Claude over and over with "found issues" notifications". This is a recent fix in exactly the path we would use.

**Can any settings hook start a turn in an idle session?**
- Only `asyncRewake` exiting 2.
- `Stop` can block, which continues the current turn before it goes idle, with "an 8-consecutive-continuation cap… The count of consecutive continuations resets each time Claude calls a tool".
- `UserPromptSubmit` also "runs them on" scheduled-task fires, background-subagent reports, and "A message another session sends to your main conversation". Channel events are not listed.

**What a hook gets inside a subagent**
- "When a subagent calls a tool, tool events such as `PreToolUse` and `PostToolUse` fire the same configured hooks as in the main conversation, and the input carries the `agent_id` and `agent_type`". `agent_id`: "Present only when the hook fires inside a subagent call."
- `SubagentStart`: `{session_id, transcript_path, cwd, hook_event_name, agent_id, agent_type}`.
- `SubagentStop` adds `stop_hook_active`, `agent_transcript_path`, `last_assistant_message`, `background_tasks`, `session_crons`. "Both arrays are scoped to the parent session".
- `Stop`'s `background_tasks` and `session_crons` "let hooks distinguish "session is done" from "session is paused waiting for background work to wake it back up"."

**Can a hook read the session's name?**
- Only a custom title. "`session_title`: The session's custom title, present when one is set, for example with `--name`, `/rename`, a hook's `sessionTitle` output, or the Agent SDK's `renameSession()`."
- "A session you haven't named can still have a generated title. That title isn't a custom title and doesn't appear in `session_title`."
- The default display name (`my-app-3f`) is in no hook field.
- Route: `claude agents --json` entries carry `sessionId` and `name`, and "An interactive session's `name` is its default display name until you name the session" (av). A hook can map `session_id` to a name that way, within its own config dir (inference).

**Other relevant hook facts**
- `UserPromptSubmit` default timeout is 30 s.
- `SessionEnd` budget is 1.5 s, raised by per-hook `timeout` "up to 60 seconds" or by `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`.
- "`-p` or SDK session: Claude Code never shows the [trust] dialog and treats the folder as trusted".
- **Env scrub (env):** with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`, `CLAUDE_CONFIG_DIR` is "Remove[d]" from hook, Bash and MCP environments. **A hook must not rely on reading `CLAUDE_CONFIG_DIR` to learn its account.**

---

## 4. The `Monitor` tool (tools, read in full)

**Semantics**
- "Runs a command in the background and feeds each output line back to Claude".
- "You keep working in the same session and Claude interjects when an event arrives."
- **Idle wake is not stated.** Indirect hints only:
  - sched: Monitor "avoids polling altogether" for a dynamic `/loop`.
  - av: "A running subagent, workflow, or monitor counts as working".
  - cl 2.1.274: "a script's final output and its exit now arrive as one notification".

  **UNVERIFIED** (E5).

**Limits and timeouts**
- "Every watch Claude starts has a deadline: 5 minutes by default, at most 30 minutes, and at most 10 minutes in a non-interactive run given a single prompt with `-p`. At the deadline the watch ends. Claude gets one notice, so it can start the watch again".
- cl (2.1.27x section): "Changed Monitor watches to always have a deadline…".
- WebSocket source:
  - "Text messages: each one becomes one event".
  - "Messages larger than 1 MiB: the watch ends".
  - "Opening a WebSocket prompts for approval… The prompt doesn't offer an option to skip future prompts for the same host."
- Address rule: "Claude Code denies URLs that point at a private, link-local, or cloud-metadata address, including hostnames that resolve to one." **Loopback is not named**, so `ws://127.0.0.1` stays **UNVERIFIED**.
- Availability: "not available when `DISABLE_TELEMETRY` or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set."

**Sandbox**
- sbx: "the limits apply to Bash, PowerShell, and Monitor commands and the processes they start."
- So a Monitor command on Linux cannot reach a host loopback port (§8).
- Monitor uses Bash permission rules. In auto mode, `Monitor` allow rules are set aside.

**Plugin monitors** (plugc)
- "runs in the background for the whole session. What it prints reaches Claude as notifications".
- "plugin monitors start in an interactive session and never in non-interactive mode with the `-p` flag".
- They are unsandboxed (sbx).
- Idle wake: **not stated**.

---

## 5. The other unread pages

**scheduled-tasks (sched)**
- "The scheduler checks every second for due tasks and enqueues them at low priority. A scheduled prompt fires between your turns… If Claude is busy when a task comes due, the prompt waits until the current turn ends."
- "Tasks only fire while Claude Code is running and idle." **So a cron task does start a turn in an idle session.**
- Limits:
  - "A session can hold up to 50 scheduled tasks at once."
  - Recurring jitter up to 30 minutes, "including when the session is idle".
  - "Recurring tasks automatically expire 7 days after creation."
  - "No catch-up for missed fires."
  - Minimum interval 1 minute.
  - A self-paced `/loop` picks "between one minute and one hour".
  - "Backgrounding the session carries `/loop` tasks over to a background session".
  - `CLAUDE_CODE_DISABLE_CRON=1` turns the scheduler off.

**agent-view (av)**
- What it is: "Each background session is a full Claude Code conversation that keeps running without a terminal attached". "The supervisor is a background service that runs your background sessions".
- **Per config dir:** "Session state is stored under your Claude Code config directory. If you set `CLAUDE_CONFIG_DIR`, the supervisor uses that directory instead of `~/.claude` and runs as a separate instance with its own sessions."
- Idle reaping: "Finished or waiting for your next message, and unattached for about an hour: the supervisor stops the process… Pin a session with `Ctrl+T` to keep its process running." **An idle background seat's process may be stopped. Whether its inbox socket stays bound while stopped is not stated: UNVERIFIED.**
- Roster API:
  - "`claude agents --json` is the supported way to read session state from outside Claude Code".
  - Fields: `cwd, kind, startedAt, id, state (working|blocked|done|failed|stopped), pid, status (busy|waiting|idle), waitingFor, sessionId, name`.
  - cl 2.1.257: "Fixed `claude agents` not saying that a background session is waiting for you to approve a message from another session". The row shows `approve message from`.
- `claude daemon status` prints "the socket directory". That is the supervisor's socket, not necessarily the messaging one.
- `disableAgentView` / `CLAUDE_CODE_DISABLE_AGENT_VIEW` turns it off.

**sessions (sess)**
- **Interleave:** "If you resume the same session in two terminals without forking, messages from both interleave into one transcript."
- **Resuming a running background session:** "`claude --resume <session>` runs `claude attach`… A prompt you pass… goes to the session as its next turn first". But "`claude -p --resume <session> "prompt"` typed at a terminal does the same". Flags like `--output-format json` or `--max-turns` make it "exit with status 1". This **confirms `--max-turns` exists.**
- **Names:**
  - Duplicates get "a variant with a two-word suffix, such as `auth-refactor-graceful-unicorn`".
  - Exceptions: no check of "AI-generated titles or default display names" or "the `--name` of a background or `-p` session at startup".
  - Default display name: "combines the working directory's name with a two-character suffix, for example `my-app-3f`… The default isn't a resume handle."
- **Storage:** "Move storage off `~/.claude` | `CLAUDE_CONFIG_DIR`". With `CLAUDE_CODE_PROJECT_DIR_NAME`, `CLAUDE_CONFIG_DIR` must also be set.

**sub-agents (sub)**
- "A background subagent's results reach Claude as a completion notification in a later turn". hooks: `UserPromptSubmit` fires when a background subagent is "reporting back".
- "a foreground subagent inherits [ListAgents] in sessions where cross-session messaging is enabled, and a background subagent doesn't keep it". A background subagent's tool set includes `SendMessage`.
- "By default, when 20 subagents are running in a session, spawning another… fails" (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`).
- "plugin subagents don't support the `hooks`, `mcpServers`, or `permissionMode` frontmatter fields."

---

## 6. Mods and plugin authoring (mods, mev, mapi, mref, mui, madm)

**What they are**
- "A mod is a plugin that changes how Claude Code looks and behaves. It's made of JavaScript or TypeScript event handlers".
- "Mods are on by default. In the terminal, use Claude Code v2.1.287 or later." cl 2.1.287: "Added Claude Mods".
- Where they run: hooks run in the terminal, `claude -p`, the Agent SDK and Remote Control. Drawing appears only in the terminal and Desktop.

**Events relevant to Diogenes** (mref; full table read)
- `agent.spawn`: "A subagent or an agent team teammate is about to start." Returns "`next({ ...e, model })` … or `{ deny: reason }`". cl 2.1.289 adds teammates. cl 2.1.292 adds workflow agents.
- `prompt.autocomplete` (cl 2.1.292): "an event a mod hooks to add its own rows to the prompt box's autocomplete list".
- `session.receive` / `session.send`: a message arriving or leaving. `e.origin.kind` is "`peer` or `peer-send-message`… `task-notification`, or `scheduled-trigger`".
  - "Return `{ consumed: reason }` to keep it from Claude."
  - "A message that's held for your approval reaches the hook first".
  - "The sender's name on a received message is whatever the sender wrote, so don't base a decision on it."
- Also: `session.start`, `session.end`, `session.measure` ("After each turn, and when a plan limit's percent used changes"), `tool.call`, `tool.check`, `prompt.submit`, `turn.start`, `turn.step` and `turn.complete`.
- `classic.<Event>` covers every settings-hook event.

**Waking an idle session** (mapi, verbatim)
- "When a background job finds something that needs Claude's attention, it can start a turn by submitting a prompt with `$.prompt.submit({ text })`. Claude reads the text after a sentence that names your mod as the sender. To send it as the user's own words, without that sentence, add `asUser: true`. **The call waits until the session is idle and then starts a new turn.**"
- Timers: "`$.clock.every` and `$.clock.after` take the place of `setInterval` and `setTimeout`… The timer's callback runs outside any event, so it keeps running between turns and doesn't start one."

**Reach**
- `$.http.fetch` works "over `http` or `https`". Limits: 30 s per call, 4 MiB bodies. Whether `http://127.0.0.1` is allowed is **not stated**.
- `$.process.run` (30 s default timeout, 10 min maximum) and `$.process.spawn`, which "streams a long-running command's output".
- `$.fs`; `$.session.send({ to: { sessionId } })`, which "makes the same delivery the SendMessage tool makes".
- `$.session.id`; `$.session.usage()` returns "`{ startedAt, context, rateLimits, cost }`".
- `$.agent.list()` returns subagents and teammates with status.
- No `$.session` name method is listed.
- **Sandbox:** "Mods aren't sandboxed. … a process that a mod starts runs outside it." (mods)

**Panes and panels**
- "a pane beside the transcript or a band above the prompt, with tabs, buttons, and text fields".
- Elements: `Box`, `Text`, `Button`, `Input`, `Select`, `Markdown`, `Code` and `Raster`.
- A pane "opened by your mod acting by itself, such as from a timer… appears only in a terminal at least 144 columns wide". After the user has opened it once, 110 columns is enough.

**Toasts and status bands** (mapi)
- `$.ui.status(text)`: "One line under the prompt that stays until you change it".
- `$.ui.toast(text)`: "disappears after a few seconds". `$.ui.log`: a dim transcript line "Claude doesn't read".
- `$.ui.notify` raises a native notification (cl 2.1.295).
- The `AbovePrompt` band is "always there, and every mod shares it."

**State**
- `$.store` is "saved as a JSON file of your plugin's own under `~/.claude/plugins/store/`", so it is per config dir by cdir's rule.
- "Every session on your machine that runs your mod shares one `$.store`. A `get` followed by a `set` isn't atomic." **It is not a lock substrate.**

**Team-plan behaviour (madm)**
- A built-in guard, `sec-default`, loads when "The user is signed in to Claude Code with a Team or Enterprise plan". "The guard adds no other restrictions. A user's mod can still read and write files, start processes, make network requests…"
- An admin can stop user mods with `allowManagedModsOnly` in managed settings.
- "If your organization turns off web fetching, or nonessential network traffic is turned off… Claude Code refuses a network request that a mod makes with `$.http.fetch`. The policy doesn't cover a program the mod starts with `$.process.run`."

**Maturity**
- 2.1.288–2.1.296 each ship many mod fixes. Two of them in 2.1.290 are security-relevant: "Fixed a case where a user-installed mod could make an organization's guard skip its check".
- Treat the API as moving.

**Could a "Diogenes" mod show the author his inbox, roster and locks inside Claude Code?** **Yes, by documentation.**
- A `session.start` hook starts `$.clock.every(…)`, or `$.process.spawn(['diogenes','listen',…])`.
- `$.ui.status` shows "Diogenes: 3 unread · lock: libs-workbench held by nitpick-libs_18".
- A `/dio` command (`$.command.register`) opens a pane with Inbox, Roster and Locks tabs, and an `Input` to reply.
- `$.prompt.submit` wakes Claude only for messages addressed to it.
- `session.receive` mirrors native `SendMessage` traffic into the hub log.

Whether the mod's HTTP call can reach a loopback hub is UNVERIFIED (E12). `$.process.spawn` of a CLI avoids the question.

---

## 7. `CLAUDE_CONFIG_DIR`

**Documented as relocated**
- env row: "Override the configuration directory (default: `~/.claude`). All settings, session history, and plugins are stored under this path. … Useful for running multiple accounts side by side… Ignored in project and local settings".
- auth: "Each directory has its own settings, session history, and claude.ai login or API key." Also: "keeps the `.credentials.json` file under that directory".
- cdir: "If you set `CLAUDE_CONFIG_DIR`, every `~/.claude` path on this page lives under that directory instead." That covers:
  - `projects/`, `sessions/` ("one small file per running session, used to detect concurrent sessions and crashes");
  - `tasks/`, `jobs/`, `daemon/`, `plugins/`, `session-env/`, `history.jsonl`.
- sbx: "In `~/.claude`, or the directory `CLAUDE_CONFIG_DIR` points to: most of its contents, plus `~/.claude.json` and the `.credentials.json` credential store".
- av: the supervisor is "a separate instance with its own sessions". mui: `$.store` lives under `~/.claude/plugins/store/`.

**Documented as not relocated**
- Console keyless sign-in ("stores that kind of sign-in outside the configuration directory").
- Anthropic profiles in `~/.config/anthropic`.
- The scratchpad, at `/tmp/claude-<uid>/…` and governed by `CLAUDE_CODE_TMPDIR`.

**Not mentioned at all**
- The messaging socket directory (§1). By xsm it is per uid.
- **Whether `ListAgents`, or `claude agents --json`'s interactive rows, filter by config dir.** UNVERIFIED (E1).

---

## 8. The sandbox's network settings (sbx, sref)

**Settings**
- `sandbox.network.allowUnixSockets`: "List the Unix socket paths sandboxed commands can connect to on macOS. Claude Code ignores this list on Linux and WSL2, where the seccomp filter can't inspect socket paths; use `allowAllUnixSockets` there instead."
- `sandbox.network.allowAllUnixSockets`: "On Linux and WSL2, the sandbox's seccomp filter blocks `socket(AF_UNIX, ...)` calls, so this is the only way to permit Unix sockets there. When the filter is missing… the sandbox doesn't block Unix-socket calls." Default `false`.
- `sandbox.network.allowLocalBinding`: "The key has no effect on Linux and WSL2, where each sandboxed command has its own loopback interface."
- **Localhost on `allowedDomains`:** entries may be "a domain, wildcard pattern, or IP literal, with an optional `:port` suffix".
  - "The names `localhost` and `*.localhost` are allowed to resolve to loopback." "To let a name resolve to a refused address, add that IP address to `allowedDomains`, such as `"127.0.0.1:8080"`."
  - However: "An `allowedDomains` entry for `localhost` applies to connections that go through the proxy, so it doesn't change a direct connection. Claude Code sets `NO_PROXY` for sandboxed commands so that they connect to `localhost` directly".
  - On Linux: "A direct connection to `localhost` or `127.0.0.1` doesn't reach servers on the host, and `allowLocalBinding` has no effect. Run the command that needs the host's server outside the sandbox with `excludedCommands`".
- xsm, for reaching the session's own inbox socket from Bash: "control whether a Bash command can reach the socket from inside the sandbox with… `sandbox.network.allowAllUnixSockets` and `sandbox.network.allowUnixSockets`".

**What runs inside and outside the sandbox**
- "command hooks, local MCP servers, plugin monitors, LSP servers, and helper commands such as your status line command and `apiKeyHelper` run with your full access". Mods also run outside it.
- "subagents… use the same sandbox configuration". "a background session… its Bash commands are sandboxed when its settings enable sandboxing."

---

## 9. Agent SDK authentication (quoted only, not interpreted)

**sdk**
- "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK. Use the API key authentication methods described in the Quickstart instead."
- "Use of the Claude Agent SDK is governed by Anthropic's Commercial Terms of Service".

**legal**
- "Your use of Claude Code is subject to: Commercial Terms of Service - for Team, Enterprise, and Claude API users; Consumer Terms of Service - for Free, Pro, and Max users".
- "Advertised usage limits for Pro and Max plans assume ordinary, individual usage of Claude Code and the Agent SDK."
- "OAuth authentication is intended exclusively for purchasers of Claude Free, Pro, Max, Team, and Enterprise subscription plans and is designed to support ordinary use of Claude Code and other native Anthropic applications."
- "Developers building products or services that interact with Claude's capabilities, including those using the Agent SDK, should use API key authentication… Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, or Max plan credentials on behalf of their users."
- "Nor does it prevent an end user from signing in to the unmodified Claude Code binary with their own Claude subscription".
- "For questions about permitted authentication methods for your use case, please contact sales."

**auth**
- `claude setup-token`: "For CI pipelines, scripts, or other environments where interactive browser login isn't available, generate a one-year OAuth token… This token authenticates with your Claude subscription and requires a Pro, Max, Team, or Enterprise plan. It can only make model requests, so it can't establish Remote Control sessions".
- "`apiKeyHelper`, `ANTHROPIC_API_KEY`, and `ANTHROPIC_AUTH_TOKEN` apply to the CLI and the surfaces that wrap it, including… the Agent SDK".

---

## Round-1 UNVERIFIED claims: disposition

| # | Round-1 claim | Now | Evidence or attempt |
|---|---|---|---|
| 1 | `agent.spawn` and `prompt.autocomplete` semantics | **VERIFIED** | mref: `agent.spawn` "A subagent or an agent team teammate is about to start", returns `next({...e, model})` or `{ deny }`. cl 2.1.292 for `prompt.autocomplete`. Both are mod events, not settings hooks. |
| 2 | Whether `ListAgents`/hooks see a name for auto-named sessions | **CORRECTED** | Hooks never get the generated title or default display name ("doesn't appear in `session_title`", hooks). Status-line `session_name` excludes the default name (sl). `claude agents --json` `name` = "its default display name until you name the session" (av). An unnamed interactive session answers to "the name shown in listings of running sessions" (xsm). |
| 3 | `asyncRewake` long-poll with re-arm on `Stop` | **Still UNVERIFIED** (mechanics now VERIFIED) | Wake on exit 2 and "still enforces `timeout`" are verified (hooks). Re-arm is not documented. A recent changelog fix for repeated wakes. Needs E2. |
| 4 | `asyncRewake` timeout ceiling | **Still UNVERIFIED** | Read the whole hooks page; only defaults are given (600 s command) and no maximum. Plain `async` hooks have no enforced timeout. |
| 5 | Socket listing and delivery across `CLAUDE_CONFIG_DIR` | **Still UNVERIFIED** | xsm, env, cdir, sess, av and cl 1.0.6→2.1.296 read; nothing keys the socket to config dir. The socket is per OS user, with fallback `/tmp/cc-socks-<uid>`. The supervisor and the `sessions/` registry are per config dir. Needs E1. |
| 6 | Channels wake an idle session | **Still UNVERIFIED** | chan and chref read in full; never stated. "delivered together on the next turn" when busy. |
| 7 | Monitor WebSocket denies loopback | **Still UNVERIFIED** | The exact text names "private, link-local, or cloud-metadata"; loopback is not named. |
| 8 | Monitor output wakes an idle session | **Still UNVERIFIED** | "Claude interjects when an event arrives" is all the text says. Hints in sched and av only. |
| 9 | Plugin monitor wakes an idle session | **Still UNVERIFIED** | plugc says output "reaches Claude as notifications"; idle is not addressed. |
| 10 | MCP `resources/subscribe` honoured | **Still UNVERIFIED** | mcp chunk 0–100 000 has no mention; last 19 875 characters not read. |
| 11 | `--max-turns` in `-p` | **VERIFIED** | sess: "Flags that limit or rewind the run, such as `--max-turns` or `--max-budget-usd`". |
| 12 | Solo developer's SDK daemon on a subscription | **Still UNVERIFIED (now quoted)** | §9 quotes sdk, legal and auth verbatim. The docs do not address this case; legal says to "contact sales". |
| 13 | Messaging socket under config dir (§5) | **Still UNVERIFIED** (same as #5) | See #5. Evidence points to per-uid, not per-config-dir. |
| 14 | Team seat shows status-line `rate_limits` | **CORRECTED (documented absent)** | sl: "`rate_limits`: appears only for claude.ai Pro and Max subscribers, or behind a Claude apps gateway". So a Team seat should get none. A mod's `$.session.usage().rateLimits` is an alternative to test (E14). |
| 15 | Socket path reachable through the bwrap mounts | **Still UNVERIFIED** | sref and sbx: on Linux only `allowAllUnixSockets` (or no seccomp filter) permits AF_UNIX. Path visibility is not stated. |
| 16 | `-p --resume` of a live session interleaves | **VERIFIED** | sess: "If you resume the same session in two terminals without forking, messages from both interleave into one transcript." For running background sessions, resume attaches or sends a prompt instead. |
| 17 | Socket wire format | **Still UNVERIFIED (undocumented)** | Only the auth line and "complete line within 30 seconds" are documented (xsm, cl 2.1.243). |

**Round-1 corrections not on the UNVERIFIED list**
- Round 1 called the `-p` worker resume "UNVERIFIED and likely to interleave". It is now verified (row 16).
- Round 1 said `allowUnixSockets` is "ignored on Linux". That is confirmed (sref); xsm's mention of both keys is just a link.

---

## What this means for Diogenes (revised integration design)

**A. Receiving (hub to session)**

1. **New primary: a `diogenes` plugin that bundles a mod, an MCP server and two settings hooks.** Install it per config dir.
   - The mod's `session.start` starts `$.process.spawn(['diogenes','listen','--session',id])`. It reads the session id from `$.session.id()`, with the account baked into `pluginConfigs` or `userConfig`. This is a long-poll that runs unsandboxed, with no 600 s timeout to re-arm.
   - On mail, it updates `$.ui.status`.
   - Only when a message is addressed to this seat does it call `$.prompt.submit({ text: '3 unread from compiler_37; call mcp__diogenes__inbox' })`. Never use `asUser: true`, so Claude sees the mod named as sender; messages stay data.
   - Basis: mapi, "waits until the session is idle and then starts a new turn".
   - Caveats:
     - Mods are 2.1.287+ and fast-moving.
     - On the Team account the `sec-default` guard loads but allows this by default (madm). An Owner could block it with `allowManagedModsOnly`.
     - Drawing doesn't happen in `-p`.
     - `--safe-mode` disables it.
2. **Fallback 1:** `asyncRewake` on `SessionStart` and `Stop`, for sessions where mods are off. Use the same `diogenes wait`. Keep `timeout` under the documented default and re-arm on `Stop` (E2).
3. **Fallback 2:** a `/loop` or `CronCreate` poll. It is documented to fire while idle (sched) but costs tokens per fire and expires after 7 days.
4. **Demoted: channels.** On the Team seat they need Owner `channelsEnabled`, plus either the dev flag (interactive-only) or `allowedChannelPlugins`. Idle wake is undocumented. Revisit if E3 passes.
5. **Monitor and plugin monitors:** not needed if the mod works. Idle wake is still unknown.

**B. Sending (session to hub)**
- Keep the **MCP server** as Claude's deliberate interface (`send`, `inbox`, `ack`, `lock_*`, `roster`). It is portable to Gemini and GPT harnesses in a way mod tools (`$.tool.register`) are not.
- **Telemetry moves into the mod.** `session.measure` plus `$.session.usage()` gives context and rate limits. This replaces the status-line `usage-latest.json` file and may work on the Team seat, where status-line `rate_limits` is documented absent (E14).
- The mod's `session.receive` and `session.send` hooks mirror native `SendMessage` traffic to the hub for audit. Do not use `{consumed}`.
- **Delivery receipts are the hub's job.** `SendMessage` results only mean "queued" (cl 2.1.271).

**C. Locks**
- Unchanged: a hub lease, enforced by a settings `PreToolUse` hook with `onFailure: "block"`, with `agent_id` attribution inside subagents.
- **Do not** use `$.store` (non-atomic, per config dir) or `$.fs.write` (non-atomic) for locks.
- The pane's "Locks" tab only displays hub state.

**D. Identity and roster**
- Register `{account, config_dir, session_id, socket, pid, name}` at `SessionStart` or mod `session.start`.
- **Bake the account into plugin config.** `CLAUDE_CONFIG_DIR` can be scrubbed from hook environments (env).
- The hub can poll `claude agents --json --all` under each `CLAUDE_CONFIG_DIR`, which is "the supported way to read session state from outside". It returns `status` (busy, waiting, idle), `waitingFor`, `sessionId` and `name`.
- An idle background seat may have its process stopped after about an hour unless pinned (av). Pin seats, or treat "stopped" as "wake by `claude attach`/reply".

**E. Cross-account**
- **Assumption until E1:** native messaging is per uid, so it may well cross accounts. Diogenes must not depend on it either way.
- If it does cross, the hold rules still apply. Both seats bypassing permissions means delivery; a mixed pair means held messages.

**F. Subscription automation.** No long-running SDK daemon on subscription credentials until the author has written guidance. The legal text points to "contact sales". Prefer interactive or background `claude` sessions plus the plugin.

---

## Open questions (experiments, revised)

- **E1: cross-config-dir native messaging (unchanged, still priority one).** Run it as in round 1. Also run `claude agents --json` under each `CLAUDE_CONFIG_DIR`, compare `/status` "Peer address" directories, and record whether the Team session's `/list-agents` shows the Max session.
- **E2: `asyncRewake`.** Run as in round 1. Add `"timeout": 3600` to probe for a ceiling, and confirm that a `Stop` re-arm does not stack (given the recent fix).
- **E11: mod wake (new).** A `register.js` with `$.clock.after(60000, () => $.prompt.submit({ text: 'DIOGENES TEST' }))`. Send one prompt, leave the session idle, and confirm a new turn starts.
  - Repeat on the Team account (the guard is loaded) and in a background session (`claude --bg`).
  - Record whether the text is prefixed with the mod-sender sentence.
- **E12: `$.http.fetch('http://127.0.0.1:PORT/')` from a mod.** Is loopback allowed? Compare with `$.process.spawn(['curl', …])`.
- **E13: long-running `$.process.spawn` streaming.** Does it survive module reload and the supervisor's idle stop?
- **E14:** `$.session.usage().rateLimits` on the Team seat versus Max.
- **E3, E5:** channel and Monitor idle wake. Lower priority now.
- **For the author:**
  - Are you the Owner of the Team org? This matters for `channelsEnabled`, `allowedChannelPlugins`, and the risk of `allowManagedModsOnly`.
  - Do you want written guidance from Anthropic on subscription-driven automation (§9)?

**Outside my question**
- Mods see every prompt and tool call and can approve tool calls (madm). A Diogenes mod is privileged code on both accounts: pin it, review it, and load it from a local directory marketplace.
- A mod's `session.receive` can read messages "held for your approval" before you approve them.