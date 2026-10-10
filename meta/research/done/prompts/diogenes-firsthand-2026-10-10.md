# Diogenes: first-hand observations from a live Claude Code session (2.1.296), 2026-10-10

Observed by `nitpick-libs_18` (Opus 5.5, interactive, bypass permission mode, on the author's Max account) in its own tool definitions and in events during this session. **These are observations, not documentation.** Where a tool's own description is quoted, that is the product's text as shipped to the model on 2026-10-10.

## Messaging between sessions (`SendMessage`, `ListAgents`)

- **`ListAgents`** prints the caller's own name and ref (`This session is nitpick-libs_18 [7702a1]`) and lists peers, for example `nitpick-libs_17 [2f2cfd] · interactive · idle · started 1d ago` and `Fuzzing session milestone M11 [169d76] · cloud · idle`.
  - Its description: it lists *"other local Claude sessions on this machine, your Claude sessions running in the cloud … and (when Remote Control is connected here) your account's other sessions"*.
  - The local listing is per machine. The remote and cloud listing is per account.
- **Sockets:** a received message's `from` attribute is `uds:/run/user/1000/cc-socks/3361843.sock`, a per-OS-user runtime directory keyed by process id. Nothing visible keys it to the account or to `CLAUDE_CONFIG_DIR`. That is untested.
- **Delivery,** from `SendMessage`'s description:
  - *"messages enqueue and drain at the receiver's next tool round"*.
  - *"A successful send means the message reached that session, not that its Claude read it: a session running in a different permission mode than yours holds cross-session messages for its user's approval (and may let them expire), and a session can refuse them outright"*. For a local session, a `[Cross-session delivery notice]` reports that.
  - *"for a Remote Control, cloud or Claude Desktop session nothing reports back, so never treat silence as agreement"*.
  - A cloud session *"receives your message but cannot message any session back yet"*.
  - `notify_when_idle: true` gives *"exactly one `[Cross-session idle notice]`"* when a session on this machine next goes idle.
  - *"if you are a subagent, your send goes out under your parent session's address, and any reply is delivered to the parent session's conversation, not to you"*. So **subagents have no inbox of their own.**
- **Receiving:**
  - A message arrives wrapped as `<cross-session-message from="uds:…" from-name="nitpick-libs_17" from-mode="bypass">`.
  - The harness adds an instruction to treat it as a teammate's request, never as the user's approval, and to refuse permission laundering.
  - Mid-turn, it arrives inside a system reminder.
- **Measured this session:** a handoff brief, two hazard questions and their answers, and a release message all went through `SendMessage` between three sessions on one account, in the same (bypass) permission mode. No delivery notice appeared.

## Waking and push inside one session

- **A background Bash command's completion re-invoked this session while it was idle,** at the end of its turn (2026-10-10 12:31, the eight credits jobs finishing). The event arrived marked *"automated background-task event, NOT a message from the user"*. So a background `until <a message is waiting>; do sleep N; done` is a working wake-on-message primitive inside one session, by design of `run_in_background` (*"keeps running across turns and re-invokes you when it exits"*). Whether a background command has any lifetime cap is untested.
- **The `Monitor` tool:**
  - It streams events: *"Each stdout line is an event — you keep working and notifications arrive in the chat … Events arrive on their own schedule … even if one lands while you're waiting for the user to answer a question."*
  - It has a **WebSocket source** (`ws: {url}`), where *"the server pushes, you get notified"*.
  - *"Every monitor expires after `timeout_ms` (default 5 minutes, at most 30 minutes) … Re-arm it if you still need the watch"*.
  - *"The script runs in the same shell environment as Bash"*, so it runs inside the sandbox.
  - A firehose is rate-limited and stopped.
  - **Cost note:** every event and every expiry is a model turn over the whole context. A seat that stays armed for days pays one turn per expiry. A one-shot background `until` loop costs one turn per message.
- **`PushNotification`:** *"sends a desktop notification in the user's terminal. If Remote Control is connected, it also pushes to their phone."* It is skipped when the user is at the terminal. This is a human-alert surface.
- **`FetchInboxMessage`:** a per-session inbox fed by Remote Control relays and chat pings. The transcript gets an `<event source="session-inbox" kind="message.received">` with a `file_id`, and content arrives marked `trust="relay"`. Only `from="rc_owner"` is server-verified as the machine's owner. It is claude.ai-side and per account, so it is not a general hub.
- **Also present:** `ScheduleWakeup` (for `/loop` dynamic mode), `CronCreate`/`CronList`/`CronDelete`, `RemoteTrigger`, and `ReadNotifications`. The last *"reads the notifications queued for this session — GitHub activity on subscribed PRs, scheduled triggers … and messages from other Claude sessions"*.
  - The author's rule: no unexpected wakeups; he wakes seats by hand for now (memory `restarts-are-by-hand-for-now`).

## Identity and telemetry

- The status line already publishes the session's NAME. `~/.claude/usage-latest.json` carries `"written_by":"nitpick-libs_18"` alongside `rate_limits.five_hour` and `rate_limits.seven_day` (`used_percentage`, `resets_at`) and `model_limits` (a Fable line with `used_percentage` and `resets_at`). `~/.claude/context/<session_id>.json` carries `session_name` and `context_window.used_percentage`. **So a status-line script can map session id ↔ name ↔ meters, and write them to a hub.**
- `CLAUDE_SESSION_ID` is EMPTY inside a Bash tool call (the workbench's take hazard 2). A session's id comes from its transcript path `~/.claude/projects/<slug>/<uuid>.jsonl`, or from the scratchpad path, both visible to the model.
- Identity was confirmed by content: a nonce written in a tool call was found in exactly one of 494 transcripts.
- Across update restarts a session keeps its name and id, while its `ListAgents` ref changes (memory `restarts-are-by-hand-for-now`).

## Sandbox and tools

- The Bash sandbox (bubblewrap) has a write allowlist and network egress through a filtering proxy with a domain allowlist. Settings files are writable only by the Edit and Write tools, which are not inside the shell sandbox. A path added to `allowWrite` took effect without a restart: diogenes, 2026-10-10 12:4x.
- Headless `claude -p` runs inside the caller's sandbox when launched from Bash. With an API key and its own `CLAUDE_CONFIG_DIR`/`HOME`, it billed the plan's API credits (the workbench's credits runner). About 13.5–15.3 k tokens of the CLI's own prompt go into every job.
- **API list prices** implied by two one-turn smoke tests through the runner (`costBasis: list`): Opus 5.5 cache writes ≈ $5.0/MTok, Fable 5.1 ≈ $12.5/MTok. The billing page has charged cached reads at half the CLI's figure.

## MEASURED in this session's Bash sandbox, 2026-10-10 12:48 (Claude Code 2.1.296 on Ubuntu 24.04; the workbench's sandbox settings, no `allowAllUnixSockets`)

These were run by `nitpick-libs_18` with throwaway sockets under `$TMPDIR`. Nothing outside the sandbox was touched.

| # | Probe | Result |
|---|---|---|
| M1 | `socket(AF_UNIX)`: create, bind and connect inside one sandboxed call (Python) | **FAILED, `PermissionError: [Errno 1] Operation not permitted`.** Unix-domain sockets are refused outright inside the shell sandbox, which agrees with [r1b]'s seccomp finding. `redis-cli -s <socket>` fails the same way. |
| M2 | Loopback TCP within ONE sandboxed call (server and client in one process) | **Works.** |
| M3 | Loopback TCP ACROSS two sandboxed calls: a listener on 127.0.0.1:47811 in a background call, and a client in a separate call | **FAILED, connection refused,** although the listener printed "listening". Each call shows only `lo` and its own network namespace (`net:[4026535784]` for one call). **So each Bash call has a private network namespace: a hub listening on the host's loopback is NOT reachable from a sandboxed shell by TCP or by Unix socket.** The one remaining network path is the filtering HTTP proxy, if a hub's host:port were allowlisted: UNTESTED. |
| M4 | SQLite 3.45.1: FTS5, and `PRAGMA data_version` seen by a second connection after a commit by the first (WAL mode) | **Both work.** The FTS5 match returned 1 row, and `data_version` went 2 → 3 on the reader. |
| M5 | Redis 7.0.15 over loopback TCP within one call: a stream consumer group (`XGROUP CREATE … MKSTREAM`, `XADD`, `XREADGROUP … BLOCK`, `XPENDING`, `XACK`) and keyspace notifications (`notify-keyspace-events KEA`, `PSUBSCRIBE __keyspace@0__:mbox:*`) | **All work.** The message was read; pending went 1 → 0 after `XACK`; keyspace events `xgroup-create` and `xadd` were delivered to the subscriber. The author's recollection, that Redis can act when something happens, is right in two forms: fire-and-forget keyspace notifications, and durable stream consumer groups with acknowledgement. |

**What follows for the design (this seat's reading, for the reviewers to check):**
- From inside Claude Code's Linux shell sandbox, the reliable channel to a hub on the same machine is **the filesystem**: a spool directory on the sandbox's write allowlist, as the existing Gemini file inboxes already prove.
- A **process outside the sandbox** reaches a hub by any transport: an MCP server launched by the harness, a hook, or a mod's spawned process. Which of hooks or MCP servers run outside the sandbox is [r1b] §8's to settle.
- A hub CLI that must work from inside a sandboxed shell should therefore have a **file transport**, writing into a spool that a hub daemon outside the sandbox ingests (inotify or polling), and not only a socket or TCP transport.
