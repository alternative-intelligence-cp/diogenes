<!-- Filed 2026-10-10 from nitpick-libs/.internal/credits/out/dio-r4-event-backends-2026-10-10.md: a read-only API-credits job (claude-sonnet-5-5,claude-haiku-5-5, 21/200 turns, $0.4047 by the CLI (the bill is about two-thirds)). Its prompt is prompts/dio-r4-event-backends-2026-10-10.md. -->

# Storage and event backends for Diogenes: Redis/Valkey, PostgreSQL, SQLite, NATS, others, and the hub-API pattern

Job: dio-r4-event-backends-2026-10-10 · Date: 2026-10-10 · Model: Sonnet 5.5 · Tools: Read, WebSearch, WebFetch (no shell)

**Limits:**
- I ran nothing on the machine. Footprints, latencies and `redis-server` 7.0.15 behaviour are not measured.
- Fetched and read in full: the Redis keyspace-notification, ACL and Streams pages (Streams only the first 100k of 277k characters), the Postgres NOTIFY, SELECT and RLS pages, the SQLite `update_hook` and WAL pages, the NATS JetStream and authorization pages, and Redis's AGPL announcement.
- Search-snippet only: the Redis/Valkey version numbers and the NATS licence history.
- Not fetched, so marked **UNVERIFIED (from memory)**: Valkey's feature parity with Redis 7.2 (Streams, ACL), Postgres/SQLite/Mosquitto/ZeroMQ licences and footprints, SQLite `PRAGMA data_version` and FTS5, Postgres logical replication and advisory locks, NATS account details beyond the permissions page, MQTT, and git. The Mosquitto licence page returned 404, the ZeroMQ page said nothing about licence, and the GNU licence FAQ returned 429.

## Verdict on the two recollections

- **(a) "Redis lets you run actions when things happen": partly true.**
  - Redis delivers events. It does not run actions for you: it has no server-side trigger that executes a handler on a write.
  - The one product that did run handlers is RedisGears / Triggers and Functions, which is dead (see below).
  - Redis events reach a subscriber process, and that process runs the action.
  - In effect it is the hub pattern from (b), with Redis as the event bus.
- **(b) "Any database can have hooks if you route calls through an API": correct, and the stronger design.**
  - It is the only pattern that works the same across every backend.
  - It is also the only one that puts acknowledgement, ordering and audit under your control.
  - Database-native triggers are narrower: Postgres `LISTEN/NOTIFY` and Redis keyspace events both lose events when nobody is listening.

## 1. Redis and Valkey

| Topic | Finding | Source (read 2026-10-10) |
|---|---|---|
| Pub/Sub | Fire-and-forget. A client that disconnects and reconnects loses every event delivered meanwhile. | [Keyspace notifications](https://redis.io/docs/latest/develop/pubsub/keyspace-notifications/) |
| Keyspace notifications | Off by default (`notify-keyspace-events`).<br>Each operation publishes two events, `__keyspace@0__:key` (event name) and `__keyevent@0__:event` (key name).<br>The event carries the key and the command name, **not the value**.<br>It fires only if the key really changed. Expired events can lag when the key is not accessed.<br>In a cluster, events are node-local.<br>Same fire-and-forget loss as Pub/Sub. Use them for cache-style nudges, not as a log. | same page |
| Streams and consumer groups | `XGROUP CREATE … MKSTREAM`, `XREADGROUP GROUP g c BLOCK ms STREAMS s >` blocks for new entries.<br>Delivered entries stay in the pending list until `XACK`.<br>`XPENDING` inspects them. `XAUTOCLAIM` (since 6.2) takes over a crashed consumer's idle entries.<br>`XREADGROUP … 0` replays a consumer's own pending entries. A plain `XRANGE`/`XREAD` replays history.<br>That is **at-least-once** delivery, with per-stream ordering.<br>Newer: `XACKDEL` (8.2), idempotent production (8.6), `XNACK` (8.8).<br>The 6.2-era primitives (`XREADGROUP`, `XACK`, `XPENDING`, `XAUTOCLAIM`) exist in the installed 7.0.15. The 8.x additions do not.<br>Caveat: I read only the first 100k characters of the Streams page, so the 8.x claims rest on its command summary. | [Streams](https://redis.io/docs/latest/develop/data-types/streams/) |
| Functions and Lua | Lua scripts and Functions run atomically on the server when a client calls them. They are not triggers, but they enforce an invariant inside a write: check the lock, `XADD` the audit entry and set the key in one step.<br>Lua is unaffected by the Gears deprecation. | [Redis Enterprise 7.4.6 release notes](https://redis.io/docs/latest/operate/rs/release-notes/rs-7-4-2-releases/rs-7-4-6-272/) |
| RedisGears / Triggers and Functions | **Dead.** The Triggers and Functions preview was ended and will not go GA.<br>Docs list it under "Deprecated Redis Open Source features and modules". Gears v1 is deprecated and "not recommended for new users". Stored JS libraries are to be removed.<br>I found no end-of-life date for the feature itself. | [Deprecated features](https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/deprecated-features/), [Triggers and functions](https://redis.io/docs/latest/operate/oss_and_stack/stack-with-enterprise/deprecated-features/triggers-and-functions/), [release notes above](https://redis.io/docs/latest/operate/rs/release-notes/rs-7-4-2-releases/rs-7-4-6-272/) |
| ACL | Users are created with `ACL SETUSER`. Key patterns are `~pat`, `%R~pat` and `%W~pat` (7.0+). Channel patterns are `&pat` (6.2+; from 7.0 the default is `resetchannels`, deny all). Command allow-lists by category, or `+cmd\|sub` (7.0+).<br>Selectors (7.0+) give a second rule set, for example read on one namespace and write on another.<br>Users load from an `aclfile` with `ACL LOAD`/`ACL SAVE`.<br>**Caveat:** key patterns do not limit commands that take no keys. A user with `~tenant1:* +@all` can still run `FLUSHALL`, so deny those explicitly.<br>Key patterns limit key access but not what a stream entry says. | [ACL](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/) |
| Persistence (AOF, RDB) | UNVERIFIED (from memory, not fetched): RDB snapshots, AOF with `appendfsync everysec` (default, up to ~1 s of loss) or `always`. Either is fine for a hub, but it is not a ledger. | none fetched |
| Licence | Redis ≤7.2.4 is BSD. 7.4+ moved to RSALv2/SSPLv1 on 2024-03-20. Redis 8.0 (2025-05-01) added AGPLv3 as an option and folded Stack modules into core. The Redis announcement is dated 2025-05-01 and confirms the AGPL option and the SSPL history.<br>**Valkey:** a Linux Foundation fork of 7.2.4, BSD-3-Clause (launched 2024-03-28). 9.0 came out 2025-10-21 and 9.1 on 2026-05-19, per search snippets, so treat the exact current patch (9.1.1 or 9.1.2) as unconfirmed.<br>Redis version claims disagree across sources (8.2, 8.8, 8.10.2), so check GitHub releases before pinning.<br>**The installed 7.0.15 is BSD and has Streams, ACL v2 selectors and Functions.** | [Redis AGPLv3 post](https://redis.io/blog/agplv3/), [Phoronix](https://www.phoronix.com/news/Redis-8.0-Goes-AGPLv3), [Valkey vs Redis 2026 (secondary)](https://tacnode.io/post/valkey-vs-redis), [Valkey 9 review (secondary)](https://www.cloudmagazin.com/en/2026/04/10/valkey-9-redis-fork-cloud-cache-landscape/) |

Reading for Diogenes:
- Redis 7.0.15 is already installed and covers v0 needs: Streams with acknowledgements, ACL users per agent, Unix socket.
- Keyspace notifications are useful only as a "something changed, go look" nudge.
- Redis is a good transport, but a weak system of record. It is memory-first and has no relational queries or full-text search without modules.
- **Do not build on Triggers and Functions.**

## 2. PostgreSQL

| Topic | Finding | Source |
|---|---|---|
| LISTEN/NOTIFY | Payload under **8000 bytes** by default, so send an id and read the row.<br>Delivered only after commit, in commit order. Duplicate same-channel same-payload notifications in one transaction collapse.<br>**No listener connected:** the docs imply delivery only to sessions that have run `LISTEN`, so the notification reaches no one and raises no error. It is not stored. Same fire-and-forget loss as Redis Pub/Sub.<br>Queue about 8 GB. If it fills, `NOTIFY` transactions fail at commit. | [NOTIFY](https://www.postgresql.org/docs/current/sql-notify.html) |
| Triggers plus NOTIFY | Standard pattern: a trigger inserts into an events table (durable) and calls `pg_notify` with the event id. A reconnecting consumer reads `WHERE id > last_seen`, so NOTIFY is only the wake-up. This gives at-least-once with replay. | design inference from the above |
| Roles, schemas, RLS | `GRANT` per schema and table gives layered access that fits org/project/team.<br>RLS (PG 18 docs; added in 9.5, per the docs page) is default-deny once enabled. Table owners and `BYPASSRLS`/superusers skip it unless `FORCE ROW LEVEL SECURITY`.<br>Only the owner manages policies. Unique and foreign-key checks bypass RLS, a covert-channel risk. | [RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) |
| `SKIP LOCKED` | `SELECT … FOR UPDATE SKIP LOCKED` is documented for "queue-like tables" with several consumers. It gives an inconsistent view, so do not use it for reports. `ORDER BY` plus locking can misorder under READ COMMITTED. | [SELECT](https://www.postgresql.org/docs/current/sql-select.html) |
| Advisory locks | UNVERIFIED (from memory): `pg_advisory_lock` and `pg_try_advisory_lock` are session-scoped and tied to the connection, so a crashed agent releases automatically. This is better than the markdown-line lock and its recorded hazards. A lock table with a lease expiry is the alternative. | none fetched |
| Logical replication | UNVERIFIED (from memory): publications and subscriptions replicate a second machine or an external consumer, and `wal_level=logical` plus decoding gives a change stream. | none fetched |
| Footprint | No server installed. Docker is available, but a container adds a daemon and a bind-mount or socket to reach from the sandbox. A native `apt` install is possible. Idle memory and disk figures not measured. | none |
| Licence | PostgreSQL License, permissive; AGPL-compatible. UNVERIFIED (from memory). | none |

Reading for Diogenes: Postgres is the best fit for the layered permission model, the queryable research store and the audit tables. It costs the most operationally, and its pub/sub is no better than Redis's, so you still need an events table.

## 3. SQLite

| Topic | Finding | Source |
|---|---|---|
| WAL mode, several processes | Readers do not block the writer and vice versa. **One writer at a time.** Readers can be in separate processes through a shared `-shm` file, but **all processes must be on the same host; no network filesystem**.<br>A long reader can stall checkpoints. A WAL-reset race (concurrent write or checkpoint) is fixed in 3.51.3, with backports 3.44.6 and 3.50.7. The installed 3.45.1 is **older than the 3.50.7 backport**, so **verify that the Ubuntu package carries the fix** (Ubuntu may backport; I did not check). | [WAL](https://www.sqlite.org/wal.html) |
| `sqlite3_update_hook` | Registered per connection and reports only changes made through that connection. So **in-process only**: another process's writes never fire it.<br>One hook per connection. Rowid tables only. Some deletes are not reported. Receives table and rowid, not values. Must not modify the connection. | [update_hook](https://www.sqlite.org/c3ref/update_hook.html) |
| Cross-process change detection | Two options. `PRAGMA data_version` changes when another connection commits (UNVERIFIED, from memory), so poll it cheaply. Or inotify on the `-wal` file or db file (also from memory). Both are wake-ups, not event payloads. Writers should insert into an events table, and readers query `WHERE id > ?`. | none fetched |
| FTS5 | Built-in full-text search extension, enabled in standard builds. UNVERIFIED (from memory; confirm with `sqlite3 ':memory:' 'create virtual table t using fts5(x)'`). | none fetched |
| Access control | File permissions only: whoever can open the file can read all of it. A sandbox that can write the file can corrupt it. No per-table grants. | design inference |
| Server in front? | For least-privilege per agent, **yes**: a small hub holds the only write handle, and agents get read-only or API access. WAL needs write access to the directory and `-shm` even for readers. | WAL page above |
| Licence | Public domain. UNVERIFIED (from memory). | none |

## 4. NATS (JetStream, KV, object store)

| Topic | Finding | Source |
|---|---|---|
| JetStream | Streams plus **durable consumers**: server-side cursors, each with its own position. Explicit acks, with redelivery of unacknowledged messages, and replay. Delivery is **at-least-once**; the page says nothing of exactly-once. KV and object store are built on JetStream. | [JetStream](https://docs.nats.io/nats-concepts/jetstream) |
| Subjects and permissions | Per-user publish and subscribe allow/deny lists with `*` and `>` wildcards, so `org.>`, `proj.diogenes.>` and `proj.diogenes.team.devs.>` map directly onto the layers.<br>Deny wins. An empty allow list means unrestricted. Granting `>` exposes the JetStream control plane.<br>**Accounts** give separate subject spaces with explicit import/export. I did not read that page (the permissions page only previews it), so details are UNVERIFIED. | [Authorization](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/authorization) |
| Licence | Apache-2.0. Synadia proposed leaving the CNCF for BUSL in April 2025. The 2025-05-01 CNCF settlement kept the repos and trademarks with CNCF and the server under Apache-2.0. Apache-2.0 is AGPL-3.0-compatible (UNVERIFIED, from memory; the GNU FAQ fetch failed). | [CNCF announcement](https://www.cncf.io/announcements/2025/05/01/cncf-and-synadia-align-on-securing-the-future-of-the-nats-io-project/), [The Register](https://www.theregister.com/2025/05/02/cncf_synadia_nats/) |
| Footprint | Single Go binary. A small footprint is commonly reported but I did not measure it (UNVERIFIED). A new daemon to learn. | none |

Reading for Diogenes: NATS fits the organization, project and team layers best, and has acks, replay and KV natively. It is another service to run and secure, and a sandbox needs a TCP or Unix route to it. It is a strong v1 candidate, and a poor first step for one person this month.

## 5. Others

All rows UNVERIFIED (from memory); my fetches of the Mosquitto and ZeroMQ pages returned nothing usable.

| Option | Verdict |
|---|---|
| MQTT (Mosquitto) | Simple pub/sub with per-topic ACL files and QoS 1/2 with persistent sessions. Broker licence is EPL/EDL (check AGPL compatibility). No query. Weak at replay, and retained messages hold only the last value per topic. Not a store. |
| ZeroMQ | Brokerless library, no persistence, no auth model of its own. Not suitable as the backbone. |
| Plain files plus inotify | Matches today's inbox practice, needs no server and works with every harness that can read files. Atomic rename gives safe delivery. It has no ACL beyond Unix permissions and no ordering guarantee beyond filenames. Fine as the fallback "poll" tier. |
| Git as store | Already in use, with a free audit trail and merge model. Poor for low-latency events and for write contention (the lock hazards already seen). Keep it for durable artifacts, not as the bus. |

## 6. "Hooks through an API": the hub pattern

**Shape.** A small hub service owns the store and every write goes through it. On each accepted write it:
1. appends to an append-only events table, with a monotonic sequence number, in the same transaction as the write;
2. fans out to subscribers by SSE, WebSocket, long-poll or webhook, or runs a configured command.

Each subscriber keeps a cursor of the last acknowledged sequence number.

| Property | Hub plus events table | DB-native triggers |
|---|---|---|
| At-least-once | Yes: the cursor advances only on ack, so the hub redelivers. | Postgres: NOTIFY alone, no. With a trigger-written events table, yes. Redis keyspace events, no. SQLite hook, in-process only. |
| Ordering | Total order by sequence number. | Postgres commit order for NOTIFY; Redis stream order within one stream. |
| Acknowledgements | Defined by you. | Only streams (Redis) or JetStream have them. Postgres and SQLite have none natively. |
| Audit log | The events table is the audit log. Redaction and signing happen in one place. | Needs separate triggers or tables and is bypassable by direct DB access. |
| Per-agent least privilege | Enforced in the hub per token. The hub is the only DB user, so a stolen agent credential cannot reach the DB. | Depends on the engine's ACL, which is strong in Postgres and NATS, weak in SQLite. |
| Cost | You write and maintain the hub (small). | Less code, but the guarantees above are weaker. |

Transports for harnesses:
- **Gemini and GPT** and other harnesses that cannot hold a socket: long-poll or `GET /events?after=<seq>` over HTTP with a bearer token.
- **Claude Code:** poll through a shell command, or a hook that reads the cursor. Claude Code hooks are the harness-side half of "hooks".
- **Webhooks and command-running** hide delivery from harnesses with no inbound listener, but are the riskiest because they execute things.

## Comparison table

| Criterion | Redis/Valkey | Postgres | SQLite (+ hub) | NATS JetStream | Files + inotify | Hub (any store) |
|---|---|---|---|---|---|---|
| Single-machine setup | Already installed | Install or docker | Installed | New binary | None | Write a small service |
| Sandbox reach (Unix socket) | Yes | Yes | File only | TCP, or Unix (UNVERIFIED) | Path in allowlist | HTTP on a Unix socket or localhost |
| Per-agent least privilege | ACL: keys, channels, commands | Roles, schemas, RLS | None (file perms) | Per-user subjects, accounts | Unix perms | Per-token in hub code |
| At-least-once with ack | Streams | Events table + cursor | Events table + cursor | JetStream | Manual | Yes, by design |
| Native event push | Pub/Sub, lossy | NOTIFY, lossy | None cross-process | Yes | inotify | SSE, WS, long-poll |
| Durability / audit | AOF/RDB, not a ledger | Strong (WAL, tables) | Strong, single file | File storage | Files | Events table |
| Query / search | Weak | Strong | FTS5 (UNVERIFIED) | KV only | grep | Backend's |
| Ops for one person | Low | Medium | Lowest | Medium | Lowest | Medium (own code) |
| AGPL-3.0 compatibility | 7.0.15 BSD ok; 7.4+ not OSI until 8 AGPL; Valkey BSD ok | Permissive (UNVERIFIED) | Public domain (UNVERIFIED) | Apache-2.0 | n/a | n/a |
| Clients (Py/Go/Rust/shell) | All, `redis-cli` | All, `psql` | All, `sqlite3` | Py, Go, Rust, `nats` CLI (UNVERIFIED) | shell | HTTP: `curl` anywhere |

## Recommendation

**v0 (this month, one machine): a hub over SQLite, with an HTTP long-poll/SSE endpoint on a Unix socket.**
- SQLite in WAL mode holds the events table, state and research. Only the hub writes. Agents never open the file.
- Reasoning: it uses what is installed, needs no new daemon, and gives an append-only audit log and at-least-once delivery with cursors. It reaches Claude, Gemini and GPT alike through `curl`.
- Keep the schema portable (events, cursors, locks) so the store can change.
- Fall back to the existing file inboxes if the hub is down.
- Verify the SQLite WAL-reset fix status on the installed 3.45.1 before relying on concurrent writers.
- Skip Redis keyspace events and anything built on Triggers and Functions.

**v1 (Gemini, GPT, second machine, a team layer): the same hub API, with the store moved to Postgres, and NATS JetStream only if you need server-to-server fan-out.**
- Reasoning: Postgres adds roles, schemas and RLS for the org/project/team layers, and logical replication for a second machine (UNVERIFIED).
- Because agents talk only to the hub API, swapping the store changes nothing for them.
- Redis Streams remain an option for the event transport if you want the 7.0.15 you already have. NATS is the cleaner fit if you want subject-level permissions without writing them in hub code.

## What this means for Diogenes

- **Put the guarantees in the hub, not the database.** Recollection (b) is right: the hub supplies sequence numbers, acks and audit across any backend, where Pub/Sub, keyspace events and NOTIFY all lose events when no one is listening.
- **Treat native notifications as wake-ups only.** Make the events table the truth and a cursor the delivery mechanism.
- **Do not depend on Redis Gears.** It is deprecated.
- **Do not rely on SQLite's update hook.** It is per-connection, so the hub is the sole writer.
- **Give agents tokens, not store credentials.** Per-agent least privilege then lives in hub code, which is what SQLite needs and what Postgres and NATS offer natively.
- **Replace the markdown-line lock** with a lease row in the hub, or a Postgres advisory lock later. That addresses the recorded take hazards.
- **Run it on a Unix socket** for sandbox reach, and keep a file-inbox fallback for harnesses that cannot hold connections.

## Open questions

- Can the Claude Code and Antigravity sandboxes reach a Unix socket or localhost TCP? Only a test settles this.
- Does the Ubuntu 3.45.1 package include the WAL-reset fix? Only the Ubuntu changelog or a test can say.
- Is a modest webhook or command-runner hook worth the execution risk, given that messages from other agents are data, not instructions?
- Which Valkey and Redis versions are current? The sources disagree, so check GitHub releases.
- How much hub code is acceptable for one person: write it, or adopt NATS or Postgres sooner?

## Outside my question

The Triggers and Functions removal notes say an RDB file containing JS libraries will not load on a server without the module, so never ship that feature in any Diogenes data.