# dio-r7-research-cache-and-memory-2026-10-10

First read `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md` in full. Then answer the question below as a dated, sourced digest, in the format that file gives.

**Your question:** how should Diogenes design a shared, queryable, freshness-checked research cache, and shared memory, for agents across models and harnesses? The aims: the same facts are not looked up again and again, and stale or poisoned entries do not spread.

Cover:

1. **What a cached research entry must hold:**
   - the question and the answer digest;
   - the sources: URL, title, publisher, published date, retrieved date, and a content hash or ETag/Last-Modified;
   - the model and harness that produced it;
   - its verification status, and who verified it;
   - a time-to-live by category (the author's practice: security-sensitive digests go stale after 90 days);
   - supersession links.

   Look for existing schemas: citation formats, W3C PROV, research-log tools.
2. **Lookup:**
   - exact key;
   - full-text search (SQLite FTS5, PostgreSQL tsvector);
   - semantic search (sqlite-vec, pgvector). Which embedding models could run locally or cheaply? Anthropic offers no embeddings API, so check what it recommends.
   - Is semantic search needed for v0 at all?
3. **Freshness:**
   - revalidation by ETag or Last-Modified;
   - scheduled rechecks;
   - "check local first, fetch only when stale" as a tool contract: `lookup` returns hit, stale or miss.
4. **Shared memory and context beyond research.**
   - Existing systems: Letta, mem0, Zep/Graphiti, basic-memory, the MCP reference "memory" server, Claude Code's file-based auto-memory, and Claude's API memory tool.
   - How each scopes memory (agent, project, organization), and whether any works across harnesses.
5. **Poisoning and injection.** A shared store written by one agent and read by another is a prompt-injection channel. Find guidance on:
   - provenance labels and trust levels;
   - quarantine for unverified entries;
   - making readers treat entries as data.
6. **How an agent would use it:**
   - an MCP tool or CLI interface sketch: `research.lookup`, `research.put`, `research.verify`, and `memory.get`/`memory.put` by scope;
   - how a subagent with no network could still benefit.

End with a schema sketch, a freshness and trust policy, and the interface, each tied to sources.
