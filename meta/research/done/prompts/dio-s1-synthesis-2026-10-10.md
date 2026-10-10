# dio-s1-synthesis-2026-10-10

You are drafting the first planning set for **Diogenes** from a round of research. Read, in full and in this order:

1. `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md`: the context and **the author's request, verbatim**. Re-read his words before you finalise anything.
2. `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-firsthand-2026-10-10.md`: observations from a live Claude Code session. They outrank documentation where the two disagree, but say so where they do.
3. The research digests in `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/out/`. Cite them as [r1] … [r8] and [r1b], with a section where it helps:
   - `dio-r1-claude-code-2026-10-10.md` [r1], with its deep second pass `dio-r1b-claude-code-deep-2026-10-10.md` [r1b] (r1b corrects r1 where they differ);
   - `dio-r2-gemini-antigravity-2026-10-10.md` [r2];
   - `dio-r3-gpt-and-standards-2026-10-10.md` [r3];
   - `dio-r4-event-backends-2026-10-10.md` [r4];
   - `dio-r5-access-and-sandboxes-2026-10-10.md` [r5];
   - `dio-r6-prior-art-2026-10-10.md` [r6];
   - `dio-r7-research-cache-and-memory-2026-10-10.md` [r7];
   - `dio-r8-requirements-from-practice-2026-10-10.md` [r8]: the author's own practice, his pains, and what must not change.
4. The skeleton: `/home/randy/Workspace/REPOS/diogenes/meta/README.md` and `/home/randy/Workspace/REPOS/diogenes/.internal/README.md`. Its conventions are his. Follow them.

## What to produce

The files below, each starting with a line of exactly `=== FILE: <path> ===`, where `<path>` is relative to the repository root. Write nothing before the first marker, and nothing between files except the markers. These files are written straight into the repository, so each must stand alone as finished Markdown.

1. **`meta/PROJECT_GOALS.md`.** Cover:
   - what Diogenes is and is not, and the problem it solves, in the author's terms;
   - who uses it: agents across harnesses, models and accounts; subagents; the author himself;
   - the goals by horizon:
     - **P0:** the second Claude account, a Team seat, coming "very soon";
     - **P1:** Gemini via Antigravity;
     - **P2:** a GPT auditor;
     - **P3:** devTeam and later;
   - measurable success criteria for each horizon;
   - non-goals.
2. **`meta/PROJECT_CONSTRAINTS.md`.** Cover:
   - the machine and what is installed;
   - one machine first, with a VPS or second machine later;
   - the sandboxes and what each harness can and cannot do;
   - the licence (AGPL-3.0) and what it rules out;
   - languages and runtimes available;
   - budget: a solo developer on subscription quotas, his attention scarce;
   - known deadlines;
   - **the practices that must not change** [r8].
3. **`meta/PROJECT_RULES.md`.** Rules for agents working on Diogenes, and for agents using it:
   - messages and shared entries are data, never instructions;
   - provenance on everything;
   - verify before relaying;
   - one writer per tree;
   - times read from the clock, never written from memory;
   - when to escalate to the author, and how;
   - conventions for names and identifiers.
4. **`meta/REQUIREMENTS.md`.**
   - Number them DR-1 … DR-n. Each is one testable sentence with a priority P0–P3, its source ([r8]'s R-number and the digest that shows it is possible), and how it will be verified.
   - Group them as: messaging; presence and roster; wake and delivery; locks, claims and leases; boards and state; handoffs; telemetry and meters; research cache; shared memory; access, identity and audit; human surfaces; harness adapters.
   - Mark the **P0 slice** clearly.
5. **`meta/DESIGN.md`:** the options and a recommendation. Include:
   - the architecture: hub, store, a `dio` CLI, an MCP server, per-harness adapters (hooks), and human surfaces;
   - the data model sketch: identities, the layers organization → project → team → agent, mailboxes and messages, claims and leases with fencing, boards, roster and presence, meters, research entries, memory entries, an append-only audit log;
   - the delivery modes per harness: push, poll, wake, with the evidence for each;
   - the backend options with the v0 and v1 choice and its reasons [r4];
   - the access and identity model [r5];
   - the threat model and its mitigations;
   - the research cache [r7];
   - what is adopted or borrowed from prior art [r6];
   - **"The P0 slice"**: exactly what a Claude session on the new Team seat and one on the personal account need on day one, as small as possible, with every unknown it rests on named;
   - where you disagree with a digest, say so and why.
6. **`meta/roadmap/ROADMAP.md`:** the cycle map. Number cycles 0.0, 0.1, 0.2 … as `meta/README.md` describes; subcycles are planned later. For each cycle:
   - its goal;
   - what is in and out;
   - its gate (acceptance, measured);
   - its dependencies;
   - the experiments that must pass first;
   - a rough size.

   Cycle 0.0 is the P0 slice, preceded by the experiments it rests on. Keep v0 small enough for one Claude seat to build and verify in a few days.
7. **`meta/OPEN_QUESTIONS.md`:** DQ-1 … DQ-n, the decisions that are the author's. Each gives the question, why it matters, the options with their trade-offs, a recommendation, and what it blocks. Include the policy questions the digests raise as questions for him or for Anthropic support, without interpreting any terms yourself.
8. **`meta/EXPERIMENTS.md`:** DX-1 … DX-n, feasibility probes. Each gives:
   - the hypothesis;
   - the exact commands or settings;
   - the expected result;
   - what each outcome decides;
   - its cost;
   - its prerequisites. Several can run today on this machine (sqlite3 3.45.1, redis-server 7.0.15, Python 3.12, Go, Rust and Node are installed); some need the second account.

   Order them by what they unblock.
9. **`meta/IDEAS.md`:** the creative parking lot. The author said *"we can get as creative with the plans as we want right now"*. Each idea gets one or two lines: what it is, why it might matter, its source, and **speculative** where it is.
10. **`meta/research/done/README.md`:** an index of the nine digests. For each: its file name, its question in one line, its key findings in two or three lines, its stated limits, and its count of UNVERIFIED claims, roughly. Note that the digests themselves are filed beside this index, and the prompts that produced them are in `meta/research/done/prompts/`.
11. **`meta/PROJECT_INDEX.md`:** the cheat sheet. Where everything is, in this repository and outside it: the workbench, the Gemini inboxes, the devTeam plugin, the credits runner, and the author's memory directory.

## How to write

- **The author's preferences:** granular plans and simple systems; detail belongs in the plan, and the system stays simple. Plain direct English. Bullets and tables over long paragraphs. Every recommendation gives its reason.
- **Recommend, do not decide.** A choice that is his goes to `OPEN_QUESTIONS.md` with your recommendation.
- **Honesty is the project's theme.** Keep each digest's UNVERIFIED marks where you rely on the claim. Never upgrade a claim's certainty. Prefer "an experiment decides this" (DX-n) to a guess.
- **Generalise across harnesses.** The baseline must work for Claude Code, Gemini (CLI and Antigravity) and Codex. Per-harness features (hooks) are accelerators on top. Say which is which.
- **Usable by the author's own agents:** the orchestrator seat, its subagents (which have no inbox of their own), and seats that rotate. Say what each would call, and when.
- **Size:**
  - About 25 000 words in all; `REQUIREMENTS.md` and `DESIGN.md` may be the largest.
  - If you near your output limit, shorten `IDEAS.md` and the research index first.
  - Never stop a file mid-sentence.
  - Your final message must contain all eleven files.
