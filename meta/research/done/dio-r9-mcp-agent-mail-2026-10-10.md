<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-r9-mcp-agent-mail-2026-10-10.md: a read-only API-credits job (claude-opus-5-5, 29 turns, $1.62 by the CLI). Its prompt is prompts/dio-r9-mcp-agent-mail-2026-10-10.md. -->

# DQ-16: MCP Agent Mail and Beads against Diogenes' P0

Job: dio-r9-mcp-agent-mail-2026-10-10 · Date: 2026-10-10 · Model: Claude Opus 5.5 · Tools: Read, Grep, Glob, WebFetch, WebSearch (no shell)

**Limits:**
- **Nothing was installed, run or measured.** Every behaviour below comes from READMEs, the LICENSE files, release notes and issue pages, all read 2026-10-10.
- The fetcher summarises pages, and it caps verbatim quotes at about 125 characters. So the licence is quoted in pieces, not in full. **The author should read `LICENSE` himself** before acting on §1.2.
- I did not read the Rust source tree. Several statements about runtime behaviour are therefore README-level only and are marked as such:
  - how the `am` CLI shares the store with a running server;
  - whether names are validated;
  - the exact semantics of a reservation conflict.
- The GitHub summary pages did not show a contributor count or the last commit date for either project: **UNVERIFIED**.
- I read only a few Beads issues, picked by search.
- Not a legal opinion. The licence findings are the text and its plain reading. Whether the text applies is the author's question.

## 1. Headline findings

1. **The licence on both MCP Agent Mail repositories is "MIT License (with OpenAI/Anthropic Rider)"**, and the rider names Anthropic. This applies to the Rust port and to the unmaintained Python original. Source: [Rust LICENSE](https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail_rust/main/LICENSE) and [Python LICENSE](https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail/main/LICENSE).
   - It defines "Restricted Parties" as "OpenAI, L.L.C.; Anthropic, PBC; any of their respective Affiliates; and any person or entity / acting directly or indirectly on behalf of, for the benefit of, or under the direction of any of the foregoing / (including any officer, director, employee, contractor, agent, consultant, service provider, or representative)".
   - It states that "no rights are granted to any Restricted Party".
   - It defines "use" broadly, including "executing", "analyzing", and "incorporating … into any dataset, training corpus, evaluation harness, or pipeline for machine learning or other automated systems".
   - A breach "automatically and immediately terminates the permissions granted by this License".
   - This settles the "rider unread" item in `DESIGN.md` §8, DQ-16 and r6 open question 5.
2. **The rider cannot be combined with AGPL-3.0 code.** It restricts who may receive the software. The AGPL forbids adding restrictions to a covered work (its §7 "further restrictions" and §10). So no Agent Mail code can be borrowed into Diogenes. Ideas are not covered by copyright, so borrowing *design* is unaffected. Running Agent Mail as a separate program is not a combination, but its own rider then governs that use.
3. **The Rust port's store is not stock SQLite, and it has open corruption reports.**
   - The runtime engine is FrankenSQLite, the author's own engine: "FrankenSQLite `=0.4.10` is the runtime `DbConn`". Stock SQLite is used for "verification and recovery cross-checks only" ([AGENTS.md](https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail_rust/main/AGENTS.md)).
   - [#278](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues/278) reports "database disk image is malformed" under parallel agent load, on 0.3.30 to 0.3.36. It is open. On 4 Oct the maintainer wrote "the fixed engine line has not shipped yet".
   - [#257](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues/257) reports a rebuilt database that re-corrupted within 61 minutes on Ubuntu. It is open.
   - Two of the last three releases were emergency fixes:
     - v0.3.37 (6 Oct): v0.3.36 rows were misread after a column was added, causing "empty inboxes".
     - v0.3.38 (8 Oct): a descriptor leak made tool calls fail with "RESOURCE_BUSY".
   - Both releases tell users to stop every process before upgrading, and v0.3.37 also asks for a backup first ([releases](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/releases)).
4. **On P0, Agent Mail covers messaging and file reservations, and little else.** Of the 42 requirements mapped in §4:
   - it **covers** 5;
   - it **partly covers** 13;
   - **12** are **missing**;
   - **7** **conflict**;
   - **5** are **not applicable** (they are Diogenes' own documentation or harness settings).

   It has no task path, no roles, no meters, no process-based presence, no wake, no fencing token, and no route for a sandboxed shell. Identity is self-asserted: "any caller may `register_agent` under any well-formed name" (README).
5. **Beads is cleanly MIT and very active, but it is a task tracker, not a hub.** Its "atomic" claim has an open report of double claims under concurrency: [#4657](https://github.com/gastownhall/beads/issues/4657), "the claim is NOT a hard single-writer CAS under true sub-second concurrency", measured on bd 0.58.0, open with no maintainer reply. Borrow its ideas; do not take it as a dependency in P0.

**Answer to DQ-16: build the small core. Borrow Agent Mail's ideas but none of its code, and drop "trial Agent Mail" as the fallback.** Reasons in §6.

## 2. What MCP Agent Mail is today (Rust port)

| Item | Finding | Source |
|---|---|---|
| Repository | `Dicklesworthstone/mcp_agent_mail_rust`. About 5,200 commits, 186 stars, 37 forks, 19 open issues | [repo page](https://github.com/Dicklesworthstone/mcp_agent_mail_rust) |
| Language and runtime | Rust, 2024 edition. Source builds "require Rust nightly". Code is `#![forbid(unsafe_code)]`. Prebuilt binaries for Linux x86_64 (musl and glibc), aarch64, macOS and Windows. A GHCR container image | [README](https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail_rust/main/README.md) |
| Binaries | `am` (the operator CLI), `mcp-agent-mail` (the MCP server), `mcp-agent-mail-guard` (the pre-commit guard) | README |
| Licence | MIT with the OpenAI/Anthropic rider (§1). Not an OSI licence. Not combinable with AGPL code | LICENSE |
| Latest release | **v0.3.38, 2026-10-08**. Before it: v0.3.37 (6 Oct), v0.3.36 (16 Sep), and seven releases from 19 Aug to 9 Sep. All published by the owner, built on "DSR native lanes rather than GitHub Actions". Manifests are minisign-signed from v0.3.31 | [releases](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/releases) |
| Activity | Very high. 8 of the 19 open issues were filed 4–9 Oct, mostly by the owner and tagged with beads ids (`br-…`) | [issues](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues) |
| Maintainers | One owner. "I do not accept outside contributions for any of my projects": PRs serve as illustrations and are not merged. Contributor count **UNVERIFIED** | README §About Contributions |
| Dependencies | Mostly the same author's own stack: asupersync ("no Tokio, reqwest, hyper, or axum"), FrankenSQLite 0.4.10 via SQLModel 0.5.0, frankensearch 0.6.1 pinned to a commit, FastMCP 0.10.0 pinned to a revision, embedded `beads_rust =0.6.0` (on FrankenSQLite 0.3.18), FrankenTUI. It calls the system `git`, and warns against git 2.51.0 ("index race") | README, AGENTS.md |
| Tool count | Inconsistent across its own pages: the About line says 34, the README tool list gives 45, a later README passage says 38. All give 25 resources | repo page, README |
| Python original | `Dicklesworthstone/mcp_agent_mail`: "superseded … no longer maintained" [r6]. Same rider | Python LICENSE |

Release cadence and dependency churn bear on DR-112. Each upgrade has been an operator procedure ("stop all `am` processes", back up, schema v31 migration), which is exactly the kind of store chore the author does not want.

## 3. Its model

| Aspect | Agent Mail (Rust), as documented |
|---|---|
| **Identity and naming** | CamelCase names such as `GreenCastle`, "memorable … but ephemeral by design". Registration is per project with `register_agent(project_key, program, model)`. "Any caller may `register_agent` under any well-formed name": self-asserted by default. A `registration_token` is returned and is required for lifecycle calls over HTTP. `create_agent_identity(return_registration_token: false)` keeps the token out of the transcript. An optional Ed25519 proof gate is **off** by default (`AM_REGISTRATION_PROOF_GATE_ENABLED=false`). Opt-in `MESSAGING_SESSION_IDENTITY=true` binds identity to the `Mcp-Session-Id`; issue [#279](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues/279) is still open on session-bound identity |
| **Mailboxes and threads** | Per-agent inbox and outbox. `thread_id` and `reply_message`. A `project:<slug>` shared mailbox. No broadcast-to-all (by design, [r6]). Cross-project addressing (`Name@project`) needs an approved contact link, otherwise `CONTACT_REQUIRED` |
| **Send and read** | MCP tools (`send_message`, `fetch_inbox`, `fetch_inbox_events`, `acknowledge_message`, `mark_message_read` …), MCP resources (`resource://inbox/{Agent}?project=…`), and the `am robot` CLI ("non-interactive, agent-first", output in `toon`, `json` or `md`). The README gives no agent-facing HTTP API other than MCP |
| **Push or poll** | **Poll only.** No notifications and no resource subscriptions are described. `fetch_inbox_events` is a body-free delivery feed with a durable cursor: "`after` is a delivery cursor, never a message ID"; persist `next_cursor` only after processing. Errors `CURSOR_EXPIRED` and `CURSOR_AHEAD` |
| **Acknowledgement and read state** | `ack_required` on send. `acknowledge_message`, `mark_message_read`. `get_message_delivery_receipt` gives per-recipient read and ack state. An `ack-overdue` view and `am acks pending|remind|overdue` exist, with "overdue" left undefined in the README |
| **File reservations** | `file_reservation_paths(paths, exclusive, ttl_seconds, reason)` on globs ("symmetric fnmatch"). The response has `granted` and `conflicts`, and grants can be partial. TTL is set per call, with no default or maximum stated. Crashed holders are reclaimed "only by TTL expiry" when ATC is off. `renew_`, `release_` and `force_release_file_reservation`; a session "cannot request a forced release as another agent". **No fencing token** (artifact files carry a database generation stamp, which is not a holder fence). **Advisory**: "Advisory file reservations instead of hard locks", and agents "can override if needed" |
| **Enforcement** | A git **pre-commit** guard blocks commits that touch another agent's exclusive reservation (`.beads/**` exempt). It **fails open** when no matching archive is found ("warns and allows the commit"). A **pre-push** hook fails closed (exit 2) on a truncated scan while another agent holds a lease, unless `AGENT_MAIL_GUARD_MODE=warn`. No Claude Code `PreToolUse` guard. Build slots (`acquire_build_slot` …) are gated by `WORKTREES_ENABLED=false` by default |
| **Store and audit** | **Git archive**: per project, `projects/{slug}/messages/{YYYY}/{MM}/`, `agents/{name}/inbox|outbox/`, `file_reservations/`, `build_slots/`. **Index**: FrankenSQLite (WAL, pooled) at `<STORAGE_ROOT>/storage.sqlite3`. **Search**: "Search V3 via frankensearch", lexical by default, semantic as a build feature. The README describes no hash chain. The archive's batched publication has open issues [#344](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues/344) and [#345](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues/345), whose titles say reservation requests "wait on the archive publication fence without a deadline" |
| **Web UI** | Server-rendered `/mail/…`: unified inbox, projects, threads, search, reservations, attachments. A "HumanOverseer" composer at `/mail/{project}/overseer/compose`: always high importance, bypasses contact policies. A 16-screen TUI. "Set `HTTP_BEARER_TOKEN` for production"; `HTTP_ALLOW_LOCALHOST_UNAUTHENTICATED=true` for local browsing |
| **Multi-project** | `project_key` = "the absolute repo path". A "product bus" links projects (`ensure_product`, `products_link`, `fetch_inbox_product` …). Contact policies (`open`, `block_all`, …); the default is not stated. **No org, project and team layers with per-team write scopes** |
| **Liveness** | "ATC", a runtime with a tick loop. "Tool-dispatch hooks … update ATC activity timestamps." Its default state is unclear; the README's "default-flip" work is listed as remaining. Open issues [#258](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues/258) and [#264](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues/264) concern it |
| **Tasks** | None. It pairs with Beads (`br`, the author's `beads_rust`): `br ready --json`, reserve with `reason="br-123"`, a thread named after the bead. `am beads ready|list|show|status`. `am verify` runs code-quality gates (fmt, clippy, test), **not task verification** |

## 4. Where it runs and who can reach it

| Question | Finding |
|---|---|
| **Transport** | **stdio**: `mcp-agent-mail` with no subcommand. **HTTP**: `mcp-agent-mail serve` or `am serve-http`, on **127.0.0.1:8765**, path `/mcp/`. **Auth**: `HTTP_BEARER_TOKEN` (`Authorization: Bearer …`), plus "Bearer/JWT" in the README; `--no-auth` exists. `HTTP_ALLOWED_HOSTS` is empty, meaning loopback only |
| **Single writer** | "A stdio `mcp-agent-mail` refuses to start for a storage root that a running `am` server is already serving." The README does not say what two *stdio* servers on one root do, and FrankenSQLite's multi-writer behaviour is where the corruption reports sit. So two accounts should share **one HTTP server**, not two stdio servers. *Inference from the README* |
| **Two `CLAUDE_CONFIG_DIR`s on one instance** | Yes by construction: each account gets an HTTP MCP entry pointing at `http://127.0.0.1:8765/mcp/` with its own bearer header. The server knows nothing about config dirs. **UNVERIFIED by test** (X2). Identity across accounts is still self-asserted, so nothing stops a Team session from registering under the orchestrator's name (conflicts with DR-106) |
| **Installer hazard** | "The installer and `am` command auto-detect installed agents and write their configs in HTTP URL mode", and `am serve-http --setup` updates clients. Running the installer or bare `am` **would edit the author's live `~/.claude` and `~/.codex` configs.** Any trial must avoid it (§8) |
| **A sandboxed shell** | **No.** Each sandboxed Bash call has a private network namespace (M3), so `curl` to 8765 is refused. A Unix socket is also refused (M1), and the README offers no file-ingest route. `am` CLI from Bash would have to open the FrankenSQLite file directly, which needs the store on `allowWrite`. That adds a second process on an engine with open lock-related issues ([#343](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues/343) "can drop live FrankenSQLite -shm locks", [#298](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues/298)) |
| **Is the harness's MCP connection enough?** | For an **interactive** seat, yes: the MCP client lives in the harness process, outside the shell sandbox (context file; [r1b §8]). It is **not enough** for: <br>• a seat's own background wait (DR-105), which is sandboxed Bash; <br>• the credits runner when launched from a seat's Bash (`claude -p` runs inside the caller's sandbox, firsthand). Such a job's MCP client would sit in the sandbox's namespace and should fail like M3: *inference*, **UNVERIFIED** (X3); <br>• subagents' Bash calls, the same way. |
| **Gemini (Antigravity, `agy`)** | The README documents **Gemini CLI** (`~/.gemini/settings.json`, `"command": "mcp-agent-mail"`, `scripts/register_gemini.sh`). **Antigravity is not mentioned.** `agy` has an MCP client [r2], so an HTTP entry should work, but this is **UNVERIFIED** |
| **Codex** | Documented: `~/.codex/config.toml`, `[mcp_servers.mcp_agent_mail]` with `url` and `http_headers`, auto-written by the installer. The Python original also shipped a Codex `PostToolUse` inbox hook (search summary of the [Python repo](https://github.com/dicklesworthstone/mcp_agent_mail)). The Rust README describes **no hooks for any harness**. [r3] notes HTTP MCP may be blocked by Codex's sandbox network default |

## 5. The mapping: every ★ P0 requirement and DR-100 to DR-112

Key: **C** covered · **P** partial (what is missing) · **M** missing · **X** conflicts · **n/a** Diogenes' own rule.

| DR | Requirement (short) | Agent Mail | Note |
|---|---|---|---|
| 1 ★ | durable record with seq before delivery | **C** | DB row plus git archive; the delivery cursor is the sequence |
| 2 ★ | one-call ack; sender sees stored/delivered/acked | **C** | `acknowledge_message`, `get_message_delivery_receipt` |
| 3 ★ | `UserPromptSubmit` + `PostToolUse` pointer hook | **M** | Rust ships no hooks. Diogenes writes them; a hook runs outside the sandbox, so it can reach 8765 |
| 4 ★ | docs say delivery is at the next turn; no wake except `dio wait` | **n/a** | consistent: Agent Mail never wakes anything |
| 5 ★ | cross-account without `SendMessage` | **C** | by construction (UNVERIFIED, X2) |
| 6 ★ | data envelope with sender, trust, auth | **X** | `fetch_inbox` returns bodies straight to the model with no data-not-instructions wrapper. A hook can wrap the pointer, but a direct tool call bypasses the wrapper |
| 7 ★ | auth field (digest, nonce, none), never filled from a sender name | **M** | only by convention in the body |
| 10 ★ | reply expectation; replies owed | **P** | `ack_required` only; no `reply-expected` or owed list |
| 11 ★ | role addresses resolved at delivery | **M** | `project:<slug>` mailbox is the nearest |
| 14 ★ | idempotent `--since` cursor | **C** | `fetch_inbox_events` with a delivery cursor |
| 16 ★ | presence fields (pid, socket, account, session id, executor, state) | **P** | program, model and ATC activity only |
| 17 ★ | `gone` needs evidence; `live-idle`; `unknown` | **M** | ATC liveness comes from tool activity, which an idle session never produces |
| 20 ★ | session id with how it was obtained | **M** | |
| 24 ★ | inject a pointer under 1,000 chars; pull bodies | **P** | possible with `fetch_inbox_events` (body-free) in a Diogenes hook |
| 30 ★ | one holder, atomic CAS, release by holder only | **P** | exclusive reservations with partial grants; "agents can override"; whether a conflicting path is refused is unclear from the README |
| 31 ★ | release bumps fence and announces | **M** | no fence |
| 32 ★ | authoritative read at take | **C** | server-side |
| 33 ★ | `absent` distinct from `free` | **X** | an unreserved path is simply free |
| 34 ★ | exact-id match only | **X** | glob matching ("symmetric fnmatch"): the substring-type hazard R-25 forbids |
| 36 ★ | TTL, absolute expiry, fence per take | **P** | TTL yes, fence no |
| 39 ★ | keyed by project, layer and resource | **P** | absolute repo path plus glob; no layer; one repo's two checkouts are two projects |
| 55 ★ | per-account meters, readable cross-account | **M** | |
| 56 ★ | Fable share and room | **M** | |
| 57 ★ | context % by name | **M** | |
| 59 ★ | credits balance with correction | **M** | |
| 91 ★ | Claude Code adapter (SessionStart, inject, status line) | **M** | an MCP entry only; Diogenes would still write the whole adapter |
| 92 ★ | baseline: MCP or a writable file path | **P** | MCP yes; no file transport. The git archive is a read projection, not an ingest |
| 98 ★ | agent teams off; no `--bare` for self-reporting workers | **n/a** | |
| 99 ★ | one task record and state machine for all executors | **M** | Beads is the intended partner, through a second store |
| 100 ★ | claim = ack; one claimant; stale and repost | **M** | (Beads: claim yes, stale no, race #4657) |
| 101 ★ | report ref; verify by another identity only | **M** | |
| 102 ★ | task is a spec pointer at a blob hash; poster must be the orchestrator role | **M / X** | no roles to check the poster against |
| 103 ★ | print route room before posting | **M** | |
| 104 ★ | runner claims and reports credits jobs | **M** | and the runner, run from sandboxed Bash, cannot reach the server |
| 105 ★ | `dio wait` from a background Bash | **M** | the server is unreachable from the sandbox. The only route is watching `agents/{name}/inbox/` in the archive, whose publication is batched (#344): UNVERIFIED latency |
| 106 ★ | roles move only by recorded assignment | **X** | self-asserted registration under "any well-formed name" |
| 107 ★ | Bash `dio` resolves its session from the socket variable | **M** | identity is a token per call or an MCP session |
| 108 ★ | `/proc` process check at no model turn | **M** | |
| 109 ★ | Team room estimate from cost fields | **M** | |
| 110 | spool transport for sandboxed shells (0.1) | **X** | the design assumes MCP or loopback reach; nothing to ingest a file |
| 111 | store off `allowWrite` (0.1) | **n/a** | only relevant if Diogenes owned the store |
| 112 | the author never writes SQL | **P** | the web UI and TUI answer reading questions with no SQL. But upgrades and corruption recovery have been operator procedures (stop all processes, back up, rebuild; #257 and #278 runs) |
| 80 (tag half) ★ | cross-account tag | **n/a** | Agent Mail does not know accounts; it could go in the body |

**Tally (42 rows):**
- 5 covered (DR-1, 2, 5, 14, 32);
- 13 partial: 10, 16, 24, 30, 36, 39, 92 and 112 above, plus five where only part is meant here (the message half of 4, and 7, 10, 30, 36 as fallbacks);
- 12 missing;
- 7 conflicts (6, 33, 34, 102, 106, 110, and 4's honesty about pull-only delivery, which is fine but needs a Diogenes hook);
- 5 not applicable.

In the six areas the brief asked about:

- **Delegation: missing.** No task, claim, report or verify. Pairing with Beads gives claim and list, with no verify-by-another and no stale handling.
- **Each account's room and meters: missing.**
- **Waking an idle session: missing.** Nothing wakes, and the seat's own `dio wait` cannot reach the server from the sandbox.
- **Presence: partial.** Activity-based only, so it cannot tell `live-idle` from `gone`.
- **Lease guard: partial.** Git hooks only, with pre-commit failing open, no `PreToolUse` guard and no fence. Agent Mail is better than today's markdown line, worse than DR-30 to DR-36.
- **The author never writes SQL: partial.** Good read surface; store chores have been his to run.

## 6. The cost of each path

**Adopt it as the P0 core.**
- **What Diogenes must still add:**
  - the whole task path (DR-99 to DR-104) in a second store, or through Beads, a third;
  - roles and role routing over self-asserted names;
  - meters, room and credits;
  - presence with process checks;
  - the Claude Code adapter (all hooks);
  - the envelope;
  - `dio wait`;
  - a file transport for sandboxed Bash and for runner-launched jobs;
  - fencing beside the reservations.
- **What adoption saves:** the message table, the cursor, the ack and receipts, the reservation table and a web UI. That is perhaps a quarter of the 0.0 slice, and the cheapest quarter (the design calls the core "a few hundred lines").
- **What adoption costs:**
  - a 45-tool surface for agents to learn;
  - two sources of truth (Agent Mail for messages, `dio` for tasks and meters);
  - one maintainer who takes no contributions;
  - nightly Rust and a single-author dependency stack;
  - weekly releases, some with migrations;
  - open corruption reports on the storage engine.
- **The licence risk on top:** the work would be installed, run and tested by Claude agents. Whether those sessions fall under "acting … under the direction of" Anthropic is a question I cannot settle and should not interpret. It is a needless one to raise for a tool that covers so little.

**Fork or adapt it.**
- Forking carries the rider into every derivative.
- A fork cannot be merged into an AGPL repository or distributed with one.
- It means owning roughly 5,200 commits' worth of Rust with a custom async runtime and a custom SQLite engine.
- **Not viable.**

**Borrow ideas for a small native core (recommended).** No code or text is copied; the ideas below re-expressed in Diogenes' own design:

1. **A body-free delivery feed with an opaque cursor**, separate from message bodies. Persist the cursor only after handling a page. Distinct errors for a cursor that has expired or run ahead. This sharpens DR-14 and DR-24: the hook reads the feed and never bodies.
2. **Per-recipient delivery receipts and an ack-overdue view.** This gives `dio sent --state` and `dio owed` (DR-2, DR-10).
3. **The reservation response shape `{granted, conflicts}`.** Diogenes would refuse all-or-nothing (DR-30), but report the conflicting holder and fence, as Agent Mail reports conflicts instead of waiting.
4. **Git guards in two layers, with the right failure mode.**
   - A pre-push guard that fails closed when its check is incomplete (Agent Mail's exit 2 on a truncated scan).
   - Not Agent Mail's fail-open pre-commit when the archive is missing; that is DR-96's lesson stated in reverse.
   - A declared exemption list, like `.beads/**`.
5. **A one-file-per-message archive as a read projection**, in dated directories. This matches DR-13 and DR-29, and Agent Mail shows it works at scale beside a DB index.
6. **An overseer identity:** the author's terminal sends as `author`, at high importance, bypassing nothing but contact policy. This fits DESIGN §8's "no `--as` flag".
7. **Credentials kept out of transcripts.** `return_registration_token: false`, and the open proposal #279 for MCP-session-bound identity, both point at DR-82's rule that tokens are never model-visible.
8. **Contact links between projects** as the model for DR-80's 0.1 routes: a cross-project or cross-account send fails with an explicit `CONTACT_REQUIRED`-style refusal until a route exists.
9. **One-call bootstrap**, like `macro_start_session`. `dio hook session-start` already does this; a `dio start` for harnesses without hooks would do the same.
10. **An agent-first CLI** with `--format json|md`, like `am robot`. This is DESIGN's `--json` everywhere, plus a Markdown mode for model-facing output.
11. **A single-writer guard:** a second server on the same store refuses to start. Diogenes' `diogenesd` should do the same.
12. **Build slots:** leases on non-file resources such as "one build at a time". These are DR-39's `layer/resource` keys.
13. **What not to copy:**
    - self-asserted names;
    - glob matching for leases;
    - advisory overrides;
    - activity-only liveness;
    - a custom storage engine.

    Agent Mail's open issues are a free list of failure modes. Diogenes stays on stock SQLite, as M4 measured.

**Beads, the same way.**
- **What it is:** MIT, plain: "Copyright (c) 2025 Beads Contributors", no rider ([LICENSE](https://raw.githubusercontent.com/gastownhall/beads/main/LICENSE)). Go. About 27.8k stars and 11,246 commits. Stable **v1.3.1 on 2026-09-30**, with v1.3.2-rc.2 on 10 Oct ([releases](https://github.com/gastownhall/beads/releases)).
- **What it covers:**
  - a dependency graph with `bd ready`;
  - `bd update --claim`, documented as "atomically claim … idempotent if already claimed by you";
  - hash ids;
  - a message issue type;
  - `bd setup claude` hooks;
  - a `beads-mcp` package.
- **What it lacks for P0:**
  - no lease, TTL or stale claim;
  - no verify-by-another;
  - no meters, roles or presence.
- **Its identity:** an actor string (`--actor`, `$BEADS_ACTOR`, git `user.name`, `$USER`) that must match exactly, which bites with pool aliases (#6611).
- **Its claim race:** #4657 is open.
- **Its store:** embedded Dolt is single-writer, and multiple writers need a `dolt sql-server`. Sandboxed Bash reaching Dolt raises the same transport problem.
- **Verdict:** **borrow, and possibly interoperate later.**
  - Borrow the `ready` query: unblocked, unclaimed, in priority order.
  - Borrow conditional updates (`--if-status`, `--if-assignee`) with a distinct exit code (13 in bd 1.3) for "condition failed".
  - Borrow hash ids.
  - Learn from #4657: Diogenes' claim must be one conditional `UPDATE … WHERE state='posted'` with a rows-affected check inside `BEGIN IMMEDIATE`, and DR-100's test should be an 8-way race, not 2-way.
  - An export to Beads' JSONL could come later if the author wants its community UIs.

## 7. Recommendation on DQ-16

**Build the small core. Treat Agent Mail as a source of design ideas only. Remove it as the fallback trial, and do not take Beads as a dependency in P0.**

Reasons, each tied to a finding:
1. **It covers the wrong part.** P0 is delegation across accounts: tasks, room, wait and verify. Agent Mail covers messaging and reservations and none of the task path (§5: DR-99 to DR-109 are all missing or conflicting). Adopting it would still leave Diogenes building most of 0.0, now around two stores.
2. **It cannot reach where Diogenes must work.** Sandboxed Bash, background waits, and runner-launched `claude -p` jobs cannot reach a loopback MCP server (M1, M3). Agent Mail has no file transport, and DR-110's spool is the design's answer.
3. **Its identity model conflicts with DR-106 and DR-107.** Names are self-asserted, and any session can take any name.
4. **Its store is a risk Diogenes does not need.** It uses a custom engine with open corruption issues and recent releases that emptied inboxes or exhausted descriptors. Diogenes' measured stock SQLite (M4) is the safer base.
5. **Its licence names Anthropic** and cannot be combined with AGPL. Code borrowing is closed off (DQ-26 is answered for Agent Mail: no). Even running it raises a question the author would have to settle, for little gain.
6. **The old fallback reasoning no longer holds.** "Trial Agent Mail if 0.0 slips" assumed it would rescue P0. It would not, by (1) and (2). If 0.0 slips, the better fallback is the smallest `dio` subset: `send`, `inbox`, `ack`, and `task post|claim|report|verify` on one SQLite file, plus the file inboxes that already work.

**Suggested edits to the plan:**
- **DQ-16:** recommendation "build". Fallback: the minimal `dio` subset, not Agent Mail.
- **DESIGN §8, Agent Mail row:** "ideas only; licence rider read 2026-10-10: names Anthropic, not AGPL-combinable".
- **DESIGN §8, Beads row:** add #4657 as the reason the claim test is an 8-way race.
- **DQ-26:** note that no Agent Mail code may be borrowed under any answer.

## 8. Experiments that would confirm it

All of these are optional. The recommendation does not depend on them, and **X0 comes first**. Every step uses a private instance under a new directory and never touches the author's `~/.claude`, `~/.codex` or `~/.config`, or the system Redis, PostgreSQL or MySQL. Run from the author's own terminal, or a seat with the probe directory on `allowWrite`.

- **X0 (the author, 10 minutes).** Read the Agent Mail `LICENSE` and decide whether a trial is acceptable to him at all, given the rider's "Restricted Parties" clause. If not, skip X1 to X5. Only X6 (Diogenes' own claim race) remains.

- **X1: install without the installer.**
  1. `mkdir -p /tmp/dio-x16/{dl,bin,data,config,probe}`.
  2. Download the v0.3.38 Linux x86_64 glibc archive and its minisign manifest from the [releases page](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/releases) into `/tmp/dio-x16/dl`.
  3. Verify the manifest with `minisign -V` against the key published in the README.
  4. Extract only `mcp-agent-mail` into `/tmp/dio-x16/bin`.
  5. **Do not run `install.sh`, bare `am`, `am setup`, or `serve-http --setup`:** they auto-write agent configs.
  6. Start the server:
     ```
     env -i HOME=/tmp/dio-x16 XDG_DATA_HOME=/tmp/dio-x16/data XDG_CONFIG_HOME=/tmp/dio-x16/config \
       STORAGE_ROOT=/tmp/dio-x16/data/store HTTP_PORT=18765 HTTP_BEARER_TOKEN=$(openssl rand -hex 24) \
       PATH=/usr/bin:/bin /tmp/dio-x16/bin/mcp-agent-mail serve --no-tui
     ```
  7. **Pass:** it listens on 127.0.0.1:18765, and nothing under the real `~/.claude*`, `~/.codex` or `~/.config/mcp-agent-mail` changed (compare `stat` mtimes before and after).

- **X2: two config dirs, one instance.**
  1. Put a **project-scoped** `/tmp/dio-x16/probe/.mcp.json` with `{"type":"http","url":"http://127.0.0.1:18765/mcp/","headers":{"Authorization":"Bearer …"}}`. User settings stay untouched.
  2. Open `claude` in `/tmp/dio-x16/probe` under the Max config dir, and (once it exists) under the Team config dir.
  3. In each session: `register_agent`, send one way, `fetch_inbox_events` and `acknowledge_message` on the other, then `get_message_delivery_receipt` on the sender.
  4. **Pass:** read and ack states are visible on both sides.
  5. Also try registering the *other* session's name from the second account. Expect success, which confirms the DR-106 conflict.

- **X3: the sandbox boundary.** From a probe seat with the sandbox on:
  1. sandboxed Bash `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:18765/mcp/`: expect a connection failure (M3);
  2. the same session's MCP tool call: expect success;
  3. `claude -p` launched from sandboxed Bash with the probe `.mcp.json`: record whether its MCP connection succeeds. Expected failure; this is the DR-104 risk.
  4. One more attempt with `127.0.0.1:18765` allowlisted in the sandbox proxy settings settles DX-8's proxy question as a side effect.

- **X4: reservation semantics.**
  1. From two MCP clients (or two `curl` Streamable-HTTP sessions from the terminal), race `file_reservation_paths(["probe/x"], exclusive=true, ttl_seconds=60)` for 50 rounds. Count rounds where both get `granted`.
  2. Try `release_file_reservations` and `force_release_file_reservation` from the non-holder.
  3. Wait 61 s and check reacquisition.
  4. **Records:** double grants, non-holder release, expiry behaviour, and whether any fence-like value changes.

- **X5: wait via the archive.**
  1. From a sandboxed background Bash call, poll `/tmp/dio-x16/data/store/projects/<slug>/agents/<Name>/inbox/` every second (read-only; the path must be readable inside the sandbox).
  2. Send 20 messages.
  3. Record send-to-file latency. This tests the only Agent Mail route to DR-105, and #344's batching.
  4. Then kill the server with a checked pid mid-burst, restart it, and run `sqlite3 'file:<copy>?mode=ro' 'PRAGMA integrity_check'` on a **copy** of `storage.sqlite3`.

- **X6: Diogenes' own claim (needed whatever DQ-16's answer).**
  1. On a fresh `/tmp/dio-x16/claim.db`, run the planned `BEGIN IMMEDIATE; UPDATE task SET state='claimed', claimed_by=? WHERE id=? AND state='posted'; -- check changes()=1; COMMIT` from 8 processes at once, half on the host and half in sandboxed Bash calls.
  2. Repeat for 100 rounds.
  3. **Pass:** exactly one claimant per round. This is DX-1 with Beads #4657's lesson built in.

- **Teardown:** stop the server by its recorded pid, then `rm -rf /tmp/dio-x16` after looking at it.

## What this means for Diogenes

- **DQ-16 → build** (§7). Drop the Agent Mail fallback and replace it with the minimal `dio` subset. *(Findings 1, 3, 4; §5, §6.)*
- **DQ-26:** no Agent Mail or `beads_rust`-adjacent code in the repository under any answer. Beads (plain MIT) code is legally borrowable but not needed. *(Finding 2.)*
- **DR-14 and DR-24:** model the hook's read on a body-free delivery feed with an opaque cursor. The hook never fetches bodies. *(§6 borrow item 1.)*
- **DR-30 and DR-100:** write the claim as one conditional `UPDATE` with a rows-affected check, and test it with an 8-way race across the sandbox boundary. *(Beads #4657.)*
- **DR-33 and DR-34:** keep exact-id leases. Agent Mail's glob reservations are the substring hazard in another form. *(§3.)*
- **DR-96 and the 0.5 git guard:** fail closed on an incomplete check. Agent Mail's pre-commit fails open when its archive is missing. *(§3.)*
- **DR-110:** the spool stays essential. A pure-MCP hub (Agent Mail's shape) leaves background waits, subagent Bash and runner jobs unreachable. *(§4, M1, M3.)*
- **DR-112:** choose stock SQLite and agent-run backups. Agent Mail's upgrade notes show how a custom engine turns store upkeep into operator chores. *(§2.)*
- **Installer hygiene:** never run third-party installers that "auto-detect installed agents and write their configs" on this machine. Treat it as a project rule for every trial. *(§4.)*

## Open questions

1. Does the author accept running software whose licence names Anthropic and "any … agent … acting … under the direction of" it? Only he can settle that, and he may want advice. It decides whether X1 to X5 run at all.
2. Does a `claude -p` launched from sandboxed Bash get its MCP HTTP connection out of the sandbox's network namespace? (X3.) This affects Diogenes' own MCP plans for runner jobs, not just Agent Mail.
3. Does an allowlisted `host:port` in the sandbox proxy reach a loopback HTTP service? (X3, DX-8.)
4. What do two stdio `mcp-agent-mail` processes on one storage root do? The README covers only stdio beside a running `am` server. Moot if Agent Mail is not adopted.
5. Is bd 1.3's `--if-status` claim path free of the #4657 race? It is reported on 0.58.0 only. Moot unless Beads is interoperated with.

## Outside my question

- Agent Mail's README names a third-party tool, "RCH", that "is hooked into Claude Code's PreToolUse automatically" on install (AGENTS.md). If the author ever runs that author's installers (the "ACFS" installer appears in #342), check `~/.claude*/settings.json` afterwards for hooks he did not add.
- [r6] said the Rust port has about 2.2k stars. That figure is the Python original's; the Rust repository shows 186.

Sources (all read 2026-10-10):
- Agent Mail, Rust: [repo](https://github.com/Dicklesworthstone/mcp_agent_mail_rust), [README](https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail_rust/main/README.md), [AGENTS.md](https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail_rust/main/AGENTS.md), [LICENSE](https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail_rust/main/LICENSE), [releases](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/releases), [issues](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues), [#257](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues/257), [#278](https://github.com/Dicklesworthstone/mcp_agent_mail_rust/issues/278).
- Agent Mail, Python original: [repo](https://github.com/dicklesworthstone/mcp_agent_mail), [LICENSE](https://raw.githubusercontent.com/Dicklesworthstone/mcp_agent_mail/main/LICENSE).
- Beads: [repo](https://github.com/gastownhall/beads), [LICENSE](https://raw.githubusercontent.com/gastownhall/beads/main/LICENSE), [releases](https://github.com/gastownhall/beads/releases), [#4657](https://github.com/gastownhall/beads/issues/4657), [#6611](https://github.com/gastownhall/beads/issues/6611), [#3575](https://github.com/gastownhall/beads/issues/3575), [PR #6890](https://github.com/gastownhall/beads/pull/6890), [`bd update` docs](https://beads.gascity.com/cli-reference/update).
- Related: [gascity PR #37](https://github.com/aphexcx/gascity/pull/37), [agent-inbox #80](https://github.com/trebizondoculpepper/agent-inbox/issues/80), [Claude Code hooks reference](https://code.claude.com/docs/en/hooks).