# Diogenes: project constraints

Drafted 2026-10-10, revised the same day. Facts about the machine come from the shared context file and from first-hand observation in a live Claude Code 2.1.296 session, including the measurements M1–M5 made in that session's Bash sandbox at 12:48. Facts about tools come from the digests, with their UNVERIFIED marks kept. **Where a measurement and a document disagree, the measurement wins.**

## 1. The machine and what is installed

| Item | Value | Note |
|---|---|---|
| Host | One Linux workstation, Ubuntu 24.04, x86-64, 157 GiB RAM | Everything in v0 runs here |
| OS user | One, `randy`; both Claude accounts run under it | So `SO_PEERCRED` and file modes cannot tell the accounts apart [r5 §1] |
| Claude Code | 2.1.296 | Mods (2.1.287+), cross-session messaging (2.1.224+), `asyncRewake`, channels preview are all present |
| Claude accounts | Max 20x (personal), plus a Team premium seat hoped for by Wednesday 2026-10-14 20:00 | Each gets its own `CLAUDE_CONFIG_DIR` |
| Models | Fable 5.1, Opus 5.5, Sonnet 5.5 | Fable has its own `model_limits` line in the status-line JSON, with `used_percentage` and `resets_at` (firsthand §3) |
| `sqlite3` | 3.45.1 | **FTS5 and `PRAGMA data_version` across connections in WAL mode measured working (M4).** Older than the WAL-reset backport 3.50.7; whether Ubuntu carries the fix is UNVERIFIED [r4 §3] (DX-7) |
| `redis-server`, `redis-cli` | 7.0.15 | BSD licence; **stream consumer groups with `XACK`, and keyspace notifications, measured working over loopback TCP within one sandboxed call (M5)**; keyspace events are lossy by design [r4 §1]; ACL v2 selectors and Functions present (unmeasured) |
| PostgreSQL 16 | **server installed and running** (`postgresql@16-main`). `ss` showed no TCP 5432 listener, so it is on another port or socket-only. It holds the author's old test databases (`aria_test`, `nitpick_test`, `semantic_archive`) | **Corrected 2026-10-10 13:4x:** the first check looked only on `PATH`. Its existing databases are not Diogenes' to touch. A new database or a private cluster with per-agent roles and RLS needs no install |
| MySQL, the system Redis | **running and idle:** MySQL on 127.0.0.1:3306; Redis 7.0.15 on 127.0.0.1:6379, holding 6 156 old keys. The author's account: old experiments from an early "Aria-X" build of this machine | Diogenes and its experiments never use or touch them. Probes start private throwaway instances (finding C-5) |
| docker | installed | A Postgres container is possible, with the same reach problem from sandboxes as any port |
| Go, Rust/cargo, Node, Python 3.12 | installed | Candidate languages |
| Gemini CLI, `agy`, Codex CLI | **not installed** | P1 and P2 experiments need installs |
| VPS | 6 vCPU, 11 GiB | Fallback for anything remote (P3) |
| Messaging sockets | Observed in `/run/user/1000/cc-socks/`, keyed by pid | Docs describe `/tmp/cc-socks-<uid>` as the fallback only; nothing keys it to the config dir [r1b §1]; firsthand observation wins on the path. **Not reachable from sandboxed Bash (M1)** |

## 2. One machine first

- v0 and v1 run on the workstation only. Agents reach the hub through **the filesystem** from inside the shell sandbox (0.0: the CLI opens the store file; 0.1: a spool directory the hub ingests) and through **a Unix socket or loopback TCP only from processes outside the sandbox** (hooks, MCP servers, mods, the author's terminal). M1 and M3 rule out a socket or loopback from sandboxed Bash.
- SQLite in WAL mode requires every process on the same host and no network filesystem [r4 §3]. A VPS or second machine (0.8) therefore requires the hub-as-sole-writer shape and a network transport, which is why the `dio` command set, not the file, is the contract from day one.
- The VPS is small. Postgres on it is possible.

## 3. Sandboxes: what each harness can and cannot do

Everything below is from documentation, except where marked observed or measured. Remaining reachability questions are DX-8 (narrowed), DX-22 and DX-23.

### Claude Code (bubblewrap on Linux)

| Inside the shell sandbox | Outside it |
|---|---|
| Bash, PowerShell, `Monitor` commands and their children; `claude -p` launched from Bash (observed) | Read, Write, Edit, WebFetch, WebSearch, hooks, local MCP servers, plugin monitors, mods, LSP, the status line, `apiKeyHelper` [r1 §6, r1b §8] |

**Measured 2026-10-10 12:48 in a sandboxed Bash (the workbench's settings, no `allowAllUnixSockets`):**

| # | Result |
|---|---|
| M1 | `socket(AF_UNIX)` is refused with `EPERM` inside the shell sandbox; `redis-cli -s <socket>` fails the same way. The seccomp filter is installed and active, as [r1b §8] predicted. |
| M2 | Loopback TCP works **within one** sandboxed call (server and client in one process). |
| M3 | Loopback TCP **across two** sandboxed calls fails: each call has its own network namespace and sees only `lo`. A hub listening on the host's loopback is not reachable from a sandboxed shell by TCP or by Unix socket. The one untested network path is the filtering HTTP proxy with the hub's `host:port` allowlisted (DX-8). |

So, from inside the shell sandbox, **the reliable channel to a hub on the same machine is the filesystem**: a spool directory on the write allowlist, as the existing Gemini file inboxes already prove. A process outside the sandbox reaches a hub by any transport.

- Writes: the working directory, a per-user temp dir, `--add-dir` paths, and `sandbox.filesystem.allowWrite`. Adding a path to `allowWrite` took effect without a restart (observed 2026-10-10).
- Network: no direct route; a filtering proxy with `allowedDomains`, empty by default. Most database drivers ignore the proxy and fail [r1 §6]. `allowLocalBinding` has no effect on Linux [r1b §8].
- **Unix sockets:** `allowUnixSockets` is ignored on Linux; only `allowAllUnixSockets: true` permits `socket(AF_UNIX)` [r1b §8]. Whether that setting also makes the socket path visible through the mounts is UNVERIFIED (DX-8).
- `excludedCommands` runs a command fully unsandboxed. Avoid for the hub client where possible; if used, the client's own code joins the trusted base [r5 §3].
- `allowUnsandboxedCommands: false` makes Claude Code ignore the `dangerouslyDisableSandbox` retry [r1 §6]. The adapter sets it in both accounts (DR-82). Whether `permissions.deny` holds in bypass permission mode is in no digest and is tested in DX-15.
- `--bare` skips hooks, plugins and MCP and "will become the default for `-p`" [r1 §4].
- Hooks, MCP servers and mods are **trusted, unsandboxed code** on both accounts. A Diogenes plugin must be pinned and reviewed like a dependency [r1 outside note, r1b outside note].
- `CLAUDE_CODE_MESSAGING_SOCKET` and `CLAUDE_CODE_MESSAGING_TOKEN` are exported to hooks and Bash [r1 §2.1]. The socket path is the per-session identity a Bash-invoked `dio` uses (DR-107); the token is a secret and is never logged (DX-3). Whether `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` removes either is tested in DX-3; it is documented to remove `CLAUDE_CONFIG_DIR` [r1b §3].

### Antigravity (`agy`), the author's Gemini harness

- Gemini CLI stopped serving Google AI Pro accounts on 2026-06-18; `agy` is the harness [r2 §0].
- Terminal sandbox: [r2 §2.2] says `enableTerminalSandbox` is off by default and uses `nsjail`; [r5 §3], from a search summary, says the default preset has the sandbox on. **The two digests disagree**; DX-22 settles it. Its network policy is undocumented (UNVERIFIED).
- Hooks: `PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`; command type only; 30 s default timeout; **sanitised environment**, so configuration must come from a file; a crash or non-zero exit fails closed and blocks the tool call (secondary source) [r2 §2.5].
- MCP config is `mcp_config.json` with `command` or `serverUrl`; a Gemini CLI `url`/`httpUrl` entry fails silently [r2 §2.3]. MCP tools default to Ask; pre-approve with `mcp(diogenes/*)`.
- `--dangerously-skip-permissions` also skips hooks (secondary, agy 1.1.21), which would silently remove lock enforcement [r2 §2.2].
- Sidecars with `agentapi send-message` are the documented way to message an idle conversation; unattended behaviour is UNVERIFIED, and each injected turn draws on the AI Pro quota [r2 §2.6, §5].
- Antigravity can run Claude Opus 5.5 and Sonnet 5.5 on AI Pro, so an "independent" audit run there may not be independent of the Claude seats [r2 outside note].

### Codex CLI (P2)

- Sandbox modes `read-only`, `workspace-write`, `danger-full-access`; network off by default; local and private destinations blocked even with the proxy feature (`allow_local_binding = false`) [r3 §1]. A localhost hub is likely unreachable from a sandboxed shell; stdio MCP servers are the first try. Writes outside the workspace are blocked [r3 §5], so a file transport there must sit inside the workspace.
- Hooks: 12 events, stdout of `SessionStart` and `UserPromptSubmit` becomes context, `additionalContextLimit` default 2,500 characters [r3 §1, §What this means 3].
- `codex mcp-server` is removed; `codex app-server` is the programmatic surface and is experimental [r3 §1].

### Common floor

Every confirmed harness can call an MCP tool and read a file [r3 §5]. Nothing common pushes into an idle agent. That floor is the Diogenes baseline (DR-92); hooks and wake paths are per-harness accelerators. A direct CLI-on-SQLite path from a shell is a Claude Code accelerator for cycle 0.0 only.

## 4. Licence

- Diogenes is **AGPL-3.0** (repository `alternative-intelligence-cp/diogenes`, internal).
- What that rules out or requires:
  - Any embedded code must be AGPL-compatible. Apache-2.0, MIT, BSD, PostgreSQL, public domain and SQLite are fine. Redis 7.4 to 7.x under RSALv2/SSPL is not an OSI licence; the installed 7.0.15 is BSD and Redis 8 adds an AGPL option [r4 §1]. Valkey is BSD-3-Clause. (The GNU compatibility page could not be fetched by [r4]; compatibility of Apache-2.0 with AGPL-3.0 is stated there from memory, UNVERIFIED.)
  - MCP Agent Mail (Rust) is "MIT with a rider" whose text was not read [r6 §2]. Read the rider before borrowing code; borrowing the design is free.
  - basic-memory is AGPL-3.0, so it could be embedded or depended on [r7 §4].
  - Anything closed (the `agy` binary, Claude Code itself) is talked to, never embedded.
- The repository is internal today. AGPL obligations bite only on distribution or network service to others; the author should decide whether that stays true (DQ-26).

## 5. Languages and runtimes

| Candidate | For | Why | Against |
|---|---|---|---|
| Python 3.12 | `dio` CLI, hooks, the spool ingester, MCP server, 0.0 to 0.2 | stdlib `sqlite3`, fast to write, readable by every agent, the credits runner is already Python; inotify through a small dependency or polling | slower start per hook call (measure; hooks run on every prompt) |
| Go | `diogenesd` daemon, single static binary, 0.1+ | one binary per account, no interpreter, good for a long-running socket server and spool ingester | second language to maintain |
| Rust | later, if a daemon must be very small or share code with Nitpick tooling | the author's main language ecosystem | slowest to iterate for a few-days slice |
| Node | only if a Claude Code mod is built (mods are JavaScript or TypeScript) [r1b §6] | required by the platform | nothing else |

The language is the author's choice (DQ-2). The recommendation is Python for everything in 0.0 and 0.1, with the daemon re-done in Go only if hook latency or a static binary matters.

## 6. Budget

- A **solo developer** on subscription quotas. The weekly meters are the real currency; API credits are a monthly extra that paid for this research.
- **The Max account is split by the author's rule:** Fable keeps its normal half, for the compiler; the other half is reserved for the library orchestrator seat. The room formula `95 − meter − 0.5 × (100 − Fable %)` (DR-56) encodes that split.
- **The Team seat** is, by the author's estimate, roughly a quarter of a Max's usage, and it is not pooled with the Max account [r1 §5]. It runs Opus or smaller on well-defined tasks and rotates often to keep context small. Its status line is documented not to carry `rate_limits` [r1b disposition 14], so its room is an estimate until DX-26 finds a measured source (DR-109).
- **API credits** pay for read-only jobs through the credits runner whenever credits exist. The balance is a stored fact with the author-measured correction (DR-59, now P0).
- **His attention is the scarcest resource.** A blocking human step must earn its place, and must say which category of safety or quality it buys [r8 R-66].
- Every poll that reaches a model costs quota. On Claude, a cron or `/loop` fire is a model turn, and each exit of a background `dio wait` is one turn. On Antigravity, a hook's `injectSteps` rides on the next model call, but a sidecar or supervisor that starts a turn draws on an opaque five-hour and weekly limit [r2 §2.5, §2.8]. Diogenes therefore polls with hooks and processes, not with model turns, and wakes a model only when there is work addressed to it.
- Hook latency is a budget too: `UserPromptSubmit` has a 30 s default timeout [r1b §3], and a hook runs on every prompt. The injection hook must complete in well under a second.
- Build size: cycle 0.0 must be buildable and verifiable by one Claude seat in a few days, and a day-zero practice must exist for the day the Team seat arrives (ROADMAP, Day zero).

## 7. Known deadlines

| When | What | Consequence |
|---|---|---|
| Wednesday 2026-10-14 20:00 (the weekly reset; the author's hope) | The Team seat is set up and a session on it takes a task from the Max orchestrator | Day zero runs on what exists today; cycle 0.0 and its experiments come first |
| Next week (week of 2026-10-13) | The author reviews this planning set with more tokens available | Keep the plans granular and the system small |
| 2026-11-02 | Antigravity removes Claude 4.6 models and GPT-OSS-120b [r2 §2.8] | Irrelevant to Diogenes unless an audit relied on them |
| Rolling | Claude Code updates force restarts; mods and channels are previews whose flags may change | Pin versions in any adapter that uses them [r6 outside note] |
| Rolling | Security-sensitive research digests go stale after 90 days (author's practice) | The research cache must carry TTLs from its first version |

## 8. The practices that must not change

From [r8 §3], with the requirement that carries each.

1. **Authentication by content, not by sender claim.** Digests against a prior baseline, a nonce in exactly one transcript, checks that read a tracked document. Diogenes adds a nonce issue-and-check call (0.1); it never substitutes a self-asserted identity for the check, and it never prints a nonce value (DR-7, DR-19).
2. **Records are the storage; the channel only carries.** Git and GitHub stay as they are. A task's specification is a tracked file at a blob hash that the worker re-reads from git (DR-102). Diogenes is a lookup layer, not a second source of truth (DR-43, §2 of GOALS).
3. **Verification before relay.** A report is evidence to check, not a verdict to copy. A task's report is unverified until an identity other than the reporter re-runs its acceptance commands (DR-101). Gemini's claims are re-measured; the author's own recollections too (DR-68, DR-78).
4. **One writer per scope, and a single orchestrator for a board.** The lock design changes; the one-writer rule does not (DR-42).
5. **Messages are data, not instructions** (DR-6). A task is acted on only under the rule in RULES §1.
6. **Immutable, one-file-per-message inboxes** stay as a fallback and an export (DR-8, DR-13, DR-29).
7. **The rolling pool, successor exactly N+1, and the two-signal close.** Diogenes records these; it does not enforce a different shape (DR-22, DR-49). Team workers are not in the pool: they are executors whose state is the task.
8. **The author calls the rotation and the waking.** Diogenes records and surfaces; it never wakes a session on its own (DR-25, DR-87). A seat's own `dio wait` on its own mail is the seat's choice and is visible in the roster (DR-105, DQ-7).
9. **Cross-account work stays within support's answer.** That means a Max account and a Team seat on different parts of one project, coordinating as a workflow matter. The author proceeds on that answer (2026-10-10; DQ-5, questions 1 and 2, answered). Cross-account traffic is explicit and recorded (DR-80).
10. **Granular plans, simple systems.** The first slice is a store plus a send-and-check and task CLI, not a full service (ROADMAP 0.0).
11. **The write boundary between projects** stays (DR-39, DR-74).
12. **The research shape:** one fetch inline, more through a researcher that never writes, and the requester files with the date (DR-65).
