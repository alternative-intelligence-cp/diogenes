<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-r5-access-and-sandboxes-2026-10-10.md: a read-only API-credits job (claude-sonnet-5-5,claude-haiku-5-5, 22/200 turns, $0.3601 by the CLI (the bill is about two-thirds)). Its prompt is prompts/dio-r5-access-and-sandboxes-2026-10-10.md. -->

# Diogenes access layers, sandbox reachability and secret handling

Job: dio-r5-access-and-sandboxes-2026-10-10 · Date: 2026-10-10 · Model: Sonnet 5.5 · Tools: Read, WebFetch, WebSearch (no command execution)

**Limits:**
- I measured nothing. Every reachability claim below is from documentation, not from a test.
- I could not fetch `unix(7)` (the proxy refused it), so `SO_PEERCRED` and `SO_PEERPIDFD` details come from my own knowledge and are **UNVERIFIED** here.
- Biscuit's attenuation and revocation, and the standard audit-log mitigations (hash chains, append-only storage, WORM), I could not confirm from the pages fetched. Treat them as background knowledge.
- Antigravity's sandbox and permission details come from search-result summaries of `antigravity.google/docs` plus third-party pages. I did not read the primary pages in full.
- The Claude Code sandbox page was 90 KB. I read the network, localhost and troubleshooting sections and a grep of the rest.
- I could not find Codex's per-mode network defaults or its MCP-versus-sandbox rule in the pages fetched. Gemini's page does not say whether MCP servers run inside its sandbox.
- Gemini and Codex are not installed on this machine, so nothing was tried there.

## 1. The layer model

**Mapping the four layers to models**

| Need | Model that fits | Why |
|---|---|---|
| Org, project and team scopes (who may write where) | RBAC: roles `org-reader`, `proj-X-writer`, `team-T-writer`, `auditor` | Few roles, easy to read in an audit. |
| "Agent A writes only rows it owns, only on a board it holds the lock for" | ABAC: attributes such as `agent_id`, `team`, `project`, `lock_holder` | Needed where a role is too coarse. |
| Handing a scope to one agent for one task | Capability tokens (Biscuit, macaroons, signed JWTs) | The token is the grant, it can be narrowed (attenuated) and it expires. |

I recommend RBAC for the stable structure, a few ABAC predicates for locks and ownership, and short-lived capabilities where an agent needs a narrow grant.

**How real systems express it**

- **PostgreSQL**
  - Roles are the unit. `CREATE ROLE ... NOLOGIN NOINHERIT` makes a group role. `CREATE USER` makes a login role.
  - `VALID UNTIL` and `CONNECTION LIMIT` are role options. `VALID UNTIL` expires the password only, not the role, and is not enforced for non-password authentication.
  - `BYPASSRLS` is off by default. Auditors can get `BYPASSRLS`, or just `SELECT` through a policy.
  - Row-level security is enabled per table and is default-deny with no policy. Superusers, `BYPASSRLS` roles and the table owner bypass it unless `FORCE ROW LEVEL SECURITY` is set. Policies can be restrictive (ANDed). Referential-integrity checks always bypass it.
  - Sources, read 2026-10-10: https://www.postgresql.org/docs/current/ddl-rowsecurity.html and https://www.postgresql.org/docs/current/sql-createrole.html
- **Redis ACL users** (6.0 and later)
  - `ACL SETUSER alice on >pw ~board:proj1:* &events:proj1:* +get +set ...` sets a user. New users start with no commands, no keys and no channels.
  - Per-key read and write patterns (`%R~`, `%W~`), subcommand rules (`+config|get`) and selectors need Redis 7.0 or later. Channel patterns (`&`) need 6.2 or later, and the default is `resetchannels` from 7.0. The installed 7.0.15 has all of these.
  - Key patterns do not restrict commands that take no key arguments. A user with `~tenant1:* +@all` can still `FLUSHALL`, so deny `flushall`, `flushdb` and `swapdb` explicitly.
  - `off` blocks new logins but, per the docs, existing connections keep working. Revocation therefore needs a connection kill as well. `ACL DELUSER` and `CLIENT KILL USER` are my knowledge, not fetched.
  - `PSUBSCRIBE` needs a literal match to the allowed channel pattern, not a glob match.
  - Source, read 2026-10-10: https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/
- **NATS**
  - Each user has `publish` and `subscribe` lists with `allow` and `deny`. Deny wins. A user with no permissions block is unrestricted.
  - Accounts give isolated subject spaces. Decentralized auth moves the same permissions into signed JWTs. `allow_responses` lets a service reply to exactly one handed-out reply subject.
  - Source, read 2026-10-10: https://docs.nats.io/running-a-nats-service/configuration/securing_nats/authorization
- **Capability tokens**
  - Macaroons are bearer credentials built from chained HMACs. Caveats attenuate and contextually confine them. Source: Birgisson et al., NDSS 2014, https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/ (read 2026-10-10).
  - Biscuit tokens are verified with public keys and have a logic-based policy language. The Rust implementation is the reference. Third-party blocks are supported in spec v3.2 by Rust, Haskell and C#, with partial support in Java and Python and none in Go. Source: https://github.com/biscuit-auth/biscuit (read 2026-10-10).
  - Attenuation without contacting the issuer is documented for Biscuit, but the page I read did not state it. I am relying on general knowledge for that.
  - Signed JWTs do not attenuate natively. You would have to re-issue a narrower JWT.
- **Unix socket plus OS users**
  - The server calls `getsockopt(SO_PEERCRED)` to get the connecting process's uid, gid and pid, enforced by the kernel. The socket file's mode and ownership add a second gate.
  - **UNVERIFIED here** (`unix(7)` fetch failed). It is a very well-known mechanism, but I am citing it from memory.
  - The weak point is that both Claude accounts run as the same Linux user (`randy`). Peer credentials then cannot tell them apart, and they cannot tell an agent from its subagents.

**Where the layers go**

| Layer | Scope grant |
|---|---|
| Org | Read-only rules and context for everyone. Writes only by the author, or by a `diogenes-admin` role. |
| Project | Boards, locks, memory and research entries, namespaced `proj/<id>/...`. |
| Team | Write on the team's namespaces only. |
| Agent | The identity inside a team. It signs or authenticates each call and is the unit of audit. |
| Auditor or reviewer | Read-only across projects, with no write path at all. |

## 2. The author's question: a generated, least-privilege credential

Yes, this is possible on both backends. The pattern is the same for each: issue, scope, deliver, revoke. A broker (the Diogenes server, not the agent) does the issuing.

**Redis 7.0.15 (installed)**

- **Issue:** the broker runs `ACL SETUSER agt-<id> on >$(ACL GENPASS) resetkeys resetchannels -@all ...`. Everything starts from zero.
- **Scope:**
  - Reads: `%R~org:rules:* %R~proj:P:*`.
  - Writes: `%W~proj:P:team:T:*`.
  - Channels: `&proj:P:events` and `&agent:<id>:inbox`.
  - Commands: an explicit list (`+get +set +xadd +xread +xrange +publish +subscribe +hget +hset ...`), never `+@all`.
  - Keep `-@dangerous -@admin`, and deny `flushall`, `flushdb` and `swapdb`.
  - Locks are the awkward part. A compare-and-set lock needs a Lua script (`EVAL`) or `SET ... NX`. Key patterns still apply to the keys the script touches. I have not verified how ACLs interact with scripts, so check it in an experiment.
- **Deliver:** see §4.
- **Revoke:** `ACL SETUSER agt-<id> off`, then kill the existing connections (`CLIENT KILL USER agt-<id>`), then `ACL DELUSER`. The docs say `off` alone does not drop live connections.
- **Audit:** `ACL LOG` records denials. Use `ACL GETUSER` to dump the exact grant.
- **Residual risks:**
  - Redis ACL passwords are shared secrets, so anyone who reads the file can use it.
  - The `default` user is `nopass ~* &* +@all` out of the box. You must disable it (`ACL SETUSER default off`).
  - Redis has no row-level audit of its own.
  - **Plain Redis does not run server-side hooks on writes in the way the author remembered.** Keyspace notifications and Streams with consumer groups are the closest. This is outside my question, so I did not source it.

**PostgreSQL (not installed; docker or VPS)**

- **Issue:** the broker connects as an admin role and runs `CREATE ROLE agt_<id> LOGIN PASSWORD '<generated>' VALID UNTIL '<now+8h>' CONNECTION LIMIT 3 NOBYPASSRLS`, then `GRANT team_t_writer TO agt_<id>`. The group roles are `NOLOGIN NOINHERIT`.
- **Scope:**
  - Table `GRANT`s go to the group role.
  - RLS is enabled with `FORCE`. A policy such as `USING (project_id = current_setting('diogenes.project')::uuid AND team = current_user_team())` limits rows.
  - Reads by auditors go through an `auditor` role with `SELECT` only.
  - Writes go through `SECURITY DEFINER` functions (for example `claim_lock(...)`, `append_message(...)`), and direct `INSERT` and `UPDATE` are not granted. That keeps invariants in one place.
  - The docs warn that policies querying other tables can race under `READ COMMITTED` and leak information. Keep policies simple and column-based.
- **Deliver:** see §4. Postgres supports a password in `~/.pgpass` (mode 0600) or a client certificate.
- **Revoke:**
  - `ALTER ROLE agt_<id> NOLOGIN` and `DROP OWNED BY` followed by `DROP ROLE`.
  - `pg_terminate_backend(pid)` for live sessions.
  - `VALID UNTIL` is a backstop, but it only covers password authentication.
- **Reality check:** `psql` is installed and Postgres is not. A native Postgres driver also cannot work inside Claude Code's sandbox (see §3), so a sandboxed agent would not talk to Postgres directly either way.

**What I recommend over either**

Do not give the sandboxed agent a database user at all. Put a Diogenes API in front. It authenticates the agent, applies the layers, writes the database with its own credentials and appends to the audit log. This also answers the author's second thought: the server can do hooks and fan-out regardless of backend. The database user idea remains valid as defence in depth, with the API using one role per team so a bug in the API cannot cross scopes.

## 3. Reachability from sandboxes

**Claude Code** (docs read 2026-10-10: https://code.claude.com/docs/en/sandboxing and https://code.claude.com/docs/en/mcp)

- **What the sandbox covers:** it applies to shell commands only. File tools, MCP servers and hooks run outside it.
- **Network from inside:** there is no direct route out. Connections go through a proxy on the host, checked against `network.allowedDomains` (empty by default).
- **Non-HTTP clients:** tools that ignore proxy variables, including most database drivers and plain `ssh`, fail even to allowed hosts. Docs name `excludedCommands` as the fix, which runs the command with no filesystem or network limits.
- **Localhost:**
  - On Linux and WSL2, a sandboxed command's `localhost` is private. A direct connection to the host's `127.0.0.1` does not reach host services, and `allowLocalBinding` has no effect there.
  - On macOS, `allowLocalBinding: true` allows connections to any localhost port.
  - `allowedDomains: ["localhost"]` only applies to proxied traffic. The proxy also refuses names that resolve only to local addresses.
- **Unix sockets:**
  - The docs mention `allowUnixSockets` and warn that allowing `/var/run/docker.sock` grants host access.
  - I did not read how it behaves on Linux. **UNVERIFIED:** whether it would let a sandboxed shell reach a Diogenes socket. This is experiment 1 below.
- **HTTP through the proxy:** a Diogenes HTTP endpoint would work from a sandboxed `curl` if the host is allowed. A `*.localhost` name is allowed to resolve to loopback, which may help (experiment 2).
- **Credential masking:** a newer `mask` feature lets the proxy substitute real secrets into outbound requests. A sandboxed command sees only a sentinel value, and `injectHosts` limits where the real value goes. Environment masking needs the sandbox's proxy path. It relates to Claude Code 2.1.221 or later for AWS re-signing and 2.1.229 or later for `claude doctor` checks. I did not check the installed 2.1.296 against this. It is promising for Diogenes tokens, because the agent would never hold the real token.
- **Escape hatch:** the unsandboxed retry and `excludedCommands` both exist. Under an admin-required sandbox, repository settings that loosen it are ignored.

**Gemini CLI** (https://geminicli.com/docs/cli/sandbox/, read 2026-10-10)

- Methods: macOS Seatbelt, Docker or Podman, Windows native, gVisor/runsc and LXC. This is a Linux workstation, so expect Docker, Podman or runsc, not Seatbelt.
- Seatbelt profiles: `permissive-open` (default), `permissive-proxied`, `restrictive-open`, `restrictive-proxied`, `strict-open` and `strict-proxied`. "Proxied" routes network through a proxy. "Open" allows it.
- The page gives no network behaviour for Docker or Podman.
- `SANDBOX_MOUNTS` mounts host paths (read-only by default), which could expose a socket file. `SANDBOX_FLAGS` can add container flags, such as a network mode.
- There is also `security.toolSandboxing`, which sandboxes individual tool executions rather than the whole CLI.
- **UNVERIFIED:** whether MCP servers run inside the sandbox. The page does not say.

**Codex CLI** (https://learn.chatgpt.com/codex/sandboxing and https://learn.chatgpt.com/codex/extend/mcp, read 2026-10-10)

- Modes: `read-only`, `workspace-write` (default for local work) and `danger-full-access`. Approvals: `on-request`, `never`.
- `sandbox_workspace_write.writable_roots` extends writable paths.
- Linux uses bubblewrap. On Ubuntu, unprivileged user namespaces may need an AppArmor profile, which matters on this 24.04 machine.
- The user's brief says some modes turn the network off. The pages I read do not give a per-mode network default. **UNVERIFIED:** which modes block the network, and the key that enables it.
- MCP servers are configured under `[mcp_servers.<name>]` as stdio (`command`, `args`, `env`, `env_vars`) or streamable HTTP (`url`, `bearer_token_env_var`, `http_headers`, `env_http_headers`, `http_headers_helper`). The page does not say whether stdio MCP servers run inside the sandbox.

**Antigravity** (search summary of https://antigravity.google/docs/sandbox/ and https://antigravity.google/docs/permissions/, read 2026-10-10; not read in full)

- Default preset: sandbox on. Commands are allowed inside it and need approval to go outside. Request Review disables the sandbox and always asks. Turbo disables the sandbox and allows everything.
- Rules cover read_file, write_file, read_url, execute_url, command, mcp and unsandboxed. A `command` rule is a prefix or anchored regex. Precedence is deny, then ask, then allow.
- Domains granted under `read_url` become the sandbox's outbound allowlist. A "Sandbox Network Access" toggle exists.
- A `command(...)` allow rule lets a command run without prompts, inside or outside the sandbox. The author's "terminal policy" is therefore a per-command allowlist plus a domain allowlist.
- **UNVERIFIED:** whether `mcp` rules run MCP servers outside the sandbox.

**Where the bridge must sit**

- **Claude Code on Linux (best-grounded):** the bridge must sit outside the shell sandbox. Two placements work:
  - an MCP server the harness launches (it runs outside the sandbox, so it can reach a Unix socket or localhost directly);
  - a CLI such as `diogenes ...`, which only works from the shell if it uses HTTP through the proxy, or if it is excluded via `excludedCommands`. The latter runs with no limits, so the CLI's own code becomes part of the trusted base.
- **MCP is the preferred route**, because the sandbox does not apply to it and it carries structured calls rather than shell strings. It also keeps the secret out of the agent's shell environment (see §4).
- **Gemini and Codex:** assume the same shape (MCP server outside the sandbox, or an HTTP endpoint on an allowed host), but confirm per experiment.
- **Credential consequence:** the secret should live with the bridge process, not the agent's shell. The agent holds only a handle to the MCP server. A compromised agent can still make the calls it is permitted, but cannot copy a long-lived credential away.

## 4. Secret delivery

| Channel | What leaks |
|---|---|
| Environment variables | Inherited by child processes. A sandboxed shell that inherits the env can `env`, `printenv` or `cat /proc/self/environ`. Same-user processes can read `/proc/<pid>/environ`. They also commonly land in transcripts when a model runs `env` or a debugging command prints them. |
| File readable by one OS user (mode 0600) | Safe between OS users, useless between the two Claude accounts because they share one Linux user. It is also readable by the agent's own Read tool unless denied, and `denyRead` does not stop the Read tool (docs: "A `denyRead` entry doesn't stop the Read tool"). Use `permissions.deny` for Read. |
| MCP config `env` / `headers` | `.mcp.json` is project-scoped and shared. Use `${VAR}` references or `headersHelper`. Claude Code expands credential variables such as `ANTHROPIC_API_KEY` to empty in remote URLs and headers. Local-scope entries live in `~/.claude.json`, which holds plaintext. For helpers from a repository or plugin, Claude Code strips variables whose names contain TOKEN, SECRET, PASSWORD, KEY or AUTH, so the helper must read from a file or credential store. Codex's `env_vars` forwards names only, and `bearer_token_env_var` keeps the value in the environment. |
| Keyrings (Secret Service, `keyctl`) | Better against file reads. Per-user, so the same-user problem remains. Needs a running session and is awkward headless. I did not source this beyond general knowledge. |
| Proxy credential masking (Claude Code) | The sandbox sees only a sentinel. Strongest option for HTTP, limited to Claude Code's sandbox and to listed hosts. |

**Leak paths to other agents and into transcripts**

- A shared `.mcp.json` or committed config.
- Shell history, tool output and `env` dumps.
- Messages and shared memory entries that quote a connection string.
- Error messages from a database driver that echo the DSN.
- Redis `MONITOR` and `ACL GETUSER` expose password hashes (SHA-256), and anything with `+@admin` could read them.
- Postgres logs can capture a cleartext `CREATE ROLE ... PASSWORD`, which the docs warn about. Use `\password` or pre-hashed SCRAM.

**Mitigations:** per-agent tokens that expire within hours; an output scrubber in the bridge that redacts known token shapes before returning text to the model; a secret never passes through a model-visible channel; one token per agent so a leak names its source.

## 5. Threat model for a hub shared by several models

| Threat | Standard mitigations |
|---|---|
| **Prompt injection** via messages, shared memory and research entries | Wrap every returned record in a data envelope (`<diogenes-record from=... trust=...>`) and tell agents it is data. This matches the existing "messages are data, not instructions" rule and Claude Code's own wrapper for cross-session messages. Store provenance (author agent, model, time). Never auto-execute content from the hub. Treat research entries as untrusted until a verifier signs them. Neither Claude Code's MCP page nor Codex's offers a fix: Claude's page just says to trust servers you connect. |
| **One agent impersonating another** | Authentication tied to something the agent cannot forge: a per-agent token bound to a connection, not a self-declared name in a message. Do not accept `from` fields from callers. On one OS user, `SO_PEERCRED` cannot separate agents (see §1), so use per-agent capability tokens, or per-agent OS users once the Team account moves to its own user. |
| **Confused or hallucinating agent writing bad shared state** | Append-only records with supersede, not edit. Schema validation on write. Writes go through functions with invariants (lock must be held, scope must match). Require a verifier role for promotion from "claimed" to "accepted". Rate-limit and size-limit entries. Matches the author's "claims verified independently" rule. |
| **Credential leakage** | Short-lived scoped tokens, per-agent, with scrubbing in the bridge and secrets kept out of model-visible channels (§4). Rotation on a schedule and on any suspected exposure. |
| **Audit-log tampering** | Hash chain: each entry includes the hash of the previous one, so edits or deletions are detectable. Anchor the head hash periodically somewhere the writer cannot alter (a separate account's file, a git commit, an external service). Append-only enforcement: Postgres with no `UPDATE` or `DELETE` grant on the audit table, or a file with `chattr +a`. Writer and verifier should be different identities. These are standard practice, but I did not source them in this job. |
| **Denial of service by a runaway agent** | Per-agent rate and size quotas in the API. Postgres `CONNECTION LIMIT`, Redis connection limits, and `maxmemory` on Redis. Per-agent queues with backpressure. A kill switch that revokes a token and drops connections. |

## What this means for Diogenes

1. **Put an API in front of the storage; do not hand out database users to sandboxed agents.** Reason: Claude Code's shell sandbox has no route to database ports, and most database drivers ignore its proxy. The database user pattern is still worth using on the server side, one role per team (§2, §3).
2. **The agent-facing surface is an MCP server launched by the harness.** Reason: MCP servers run outside Claude Code's sandbox (§3). A CLI would need `excludedCommands`, which removes all limits. For harnesses without MCP, fall back to an HTTP endpoint on an allowed host.
3. **Authenticate agents with per-agent capability tokens, not self-declared names or OS user.** Reason: both Claude accounts run as `randy`, so `SO_PEERCRED` cannot distinguish them (§1). A Biscuit or macaroon style token can also be attenuated per task and per subagent.
4. **Keep the secret in the bridge, not in the agent's shell.** Use `headersHelper` or a 0600 file read by the MCP server, and deny the Read tool on that path. Reason: `denyRead` does not cover Read, and environment variables leak into transcripts (§4).
5. **Use RBAC for the layers, ABAC for locks and ownership.** Reason: org, project, team and auditor map to roles. Lock holder and row owner need attributes (§1).
6. **Lock writes behind server-side functions with invariants.** Reason: the thirteen "take hazards" in the context file all come from a lock that was a text line. A server-side compare-and-set with a lease fixes the whole class.
7. **Audit log is append-only and hash-chained, with the head anchored outside the writer's reach.** Reason: it is the only thing that makes "easily viewable for audits" trustworthy (§5).
8. **Every record the hub returns is wrapped as data with provenance.** Reason: prompt injection through shared memory and research entries is the main cross-model risk, and no harness fixes it for you (§5).
9. **Redis is usable for v0 if the `default` user is disabled and key and channel patterns are used with an explicit command list.** Reason: 7.0.15 supports read and write key patterns, channel patterns and selectors. It is not a hook system by itself, so notification comes from the API or from Streams (§2).

**Recommended design for v0 (one machine, two Claude accounts)**

- **Process:** one `diogenesd` daemon, run by `randy`, listening on a Unix socket (mode 0600) in a directory outside the sandbox allowlist, plus loopback HTTP if experiment 2 shows the sandbox proxy can reach it.
- **Storage:** SQLite (installed, 3.45.1) for records, with the daemon as the only writer. It avoids installing Postgres and gives append-only tables through the daemon's own functions. Redis stays optional, for pub/sub and queues.
- **Identity:** the daemon issues one token per agent seat (for example `nitpick-libs_18`) and per account. Tokens carry `org`, `project`, `team`, `agent`, `expiry` and scope. Subagents get an attenuated token from their seat. Verification is by signature (Biscuit, or HMAC macaroons if you want fewer dependencies).
- **Delivery:** a stdio MCP server per harness session, launched with `command` and `env`, which reads the token from a 0600 file under each account's `CLAUDE_CONFIG_DIR`. The Team account's file is in its own directory. The agent never sees the token in its shell.
- **Layers:**
  - `org/*` is read-only to agents;
  - `proj/<p>/*` has per-team write scopes;
  - `auditor` is read-only everywhere.
- **Locks:** server-side leases with holder id and expiry, replacing the `Workbench writer:` line.
- **Audit:** every call is appended to a hash-chained log. The head is written periodically to a file in the Team account's directory, so one account witnesses the other.
- **Limits:** per-token rate and size quotas, and a `revoke` command.

**Growing to Gemini, GPT and devTeam's sandboxes**

- **Gemini via Antigravity:** add the daemon's host to `read_url`, or run an MCP server if Antigravity's `mcp` rule runs outside its sandbox. The file inboxes become a fallback, written by the daemon. Issue Gemini its own token and team.
- **Codex or GPT for audits:** an `auditor` token, read-only. The stdio MCP bridge is the first try, with an HTTP URL and `bearer_token_env_var` as the second. Verify network defaults first.
- **devTeam workers:** each worker gets a token attenuated from its supervisor's, with a declared write scope matching the devTeam scope. Revoke on task end.
- **Remote (VPS):** swap the Unix socket for TLS with client tokens. Move to Postgres with per-team roles and RLS if there are more than a few concurrent writers.

**Experiments that would confirm reachability** (each takes minutes, none run here)

1. From a Claude Code sandboxed Bash on Linux, try to connect to a Unix socket outside the working directory, with and without `sandbox.network.allowUnixSockets` naming it. This settles whether a CLI can reach the daemon without `excludedCommands`.
2. From sandboxed Bash, `curl` an HTTP server on host loopback, once via `localhost` and once via `diogenes.localhost` with `allowedDomains` set. The docs say `localhost` is private on Linux and `*.localhost` may resolve. Check both.
3. Launch a stdio MCP server from Claude Code and have it connect to the Unix socket. Confirm it works with the sandbox on. Run the same under the second account's `CLAUDE_CONFIG_DIR`.
4. Check that a sandboxed `cat` of the token file fails, and that the Read tool is blocked by a `permissions.deny` rule.
5. Test the `mask` feature with a Diogenes token and `injectHosts`: confirm the shell sees only the sentinel and the daemon sees the real value. Check this against the installed 2.1.296.
6. Install Codex and run a stdio MCP server and an HTTP call in each sandbox mode. Record which modes block the network and whether the MCP server runs inside the sandbox.
7. Install Gemini CLI with the Docker sandbox. Try `SANDBOX_MOUNTS` with a socket path, and check whether MCP servers run inside the container.
8. In Antigravity, test whether an `mcp` allow rule runs the server outside the sandbox, and whether a `read_url` domain reaches the daemon.
9. With Redis 7.0.15: create a user with `%R~`, `%W~` and `&` patterns, confirm `FLUSHALL` is blocked by the explicit deny, confirm `ACL SETUSER ... off` leaves a live connection working, and check how a Lua lock script interacts with key patterns.
10. Check that `SO_PEERCRED` reports the same uid for both Claude accounts, to confirm it cannot separate them.

## Open questions

- Is the Team account going to run as a different Linux user? That would let `SO_PEERCRED` and file modes separate the accounts and simplify v0.
- Biscuit or HMAC macaroons or plain signed tokens? This depends on whether subagent attenuation is needed in v0, and I could not fully verify Biscuit's attenuation and revocation from the page read.
- Does `allowUnixSockets` work on Linux for a shell command? Only experiment 1 settles it.
- What are Codex's network defaults per sandbox mode, and does Codex or Gemini run stdio MCP servers inside their sandbox? The docs I read are silent.
- Does Antigravity's `mcp` rule run servers outside its sandbox? I only have a search summary.
- Does the Anthropic Team plan's terms affect two accounts sharing one daemon? The context file records only the support assistant's answer, and I did not check it.

**Outside my question:** Claude Code's cross-account `SendMessage` is untested (per the context file). Diogenes' queue could replace it for v0 messaging if it fails, which would make the daemon's mailbox the main deliverable.

Sources (all read 2026-10-10):
- https://code.claude.com/docs/en/sandboxing
- https://code.claude.com/docs/en/mcp
- https://learn.chatgpt.com/codex/sandboxing
- https://learn.chatgpt.com/codex/extend/mcp
- https://geminicli.com/docs/cli/sandbox/
- https://antigravity.google/docs/sandbox/ and https://antigravity.google/docs/permissions/ (via search summary)
- https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- https://www.postgresql.org/docs/current/sql-createrole.html
- https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/
- https://docs.nats.io/running-a-nats-service/configuration/securing_nats/authorization
- https://github.com/biscuit-auth/biscuit
- https://research.google/pubs/macaroons-cookies-with-contextual-caveats-for-decentralized-authorization-in-the-cloud/