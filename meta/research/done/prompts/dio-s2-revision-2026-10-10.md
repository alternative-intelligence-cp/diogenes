# dio-s2-revision-2026-10-10

You revise a planning draft for **Diogenes** against an independent critique and new measurements. Read, in full:

1. `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md`: the context and **the author's request, verbatim**.
2. `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-firsthand-2026-10-10.md`: observations from a live Claude Code session. **Its final section, "MEASURED in this session's Bash sandbox", was added AFTER the draft was written.** Measurements M1–M5 outrank every document and every inference. In particular:
   - Unix sockets are refused inside the shell sandbox;
   - each sandboxed shell call has a private network namespace;
   - Redis streams with keyspace notifications, and SQLite FTS5 with `data_version`, both work here.
3. **The draft:** `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/out/dio-s1-synthesis-2026-10-10.md`. It holds eleven files, each starting `=== FILE: <path> ===`.
4. **The critique:** `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/out/dio-c1-critique-2026-10-10.md`. Its findings are C-1 … C-n.
5. The research digests in `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/out/dio-r*.md`. Use them to check a finding before you apply it.

## Do

- **Apply every blocking and major finding,** unless the digests or the measurements show the finding is wrong. Apply minor findings where they are cheap.
- **Bring the measurements in:** wherever the draft's design, requirements, experiments or roadmap assume that a sandboxed shell can reach a hub by socket or loopback TCP, correct it. Mark the experiments that M1–M5 have already answered as **DONE (measured 2026-10-10)**, with the result.
- **Bring in the author's follow-up** at the end of the context file, which came after the draft:
  - P0 is delegation from the Max-account orchestrator to Team-seat sessions (Opus or smaller, rotated often) and to API-credit jobs;
  - one task path for several kinds of executor;
  - the room is read per account;
  - Fable keeps half of the Max account for the compiler.

  Change the goals, requirements, design, roadmap and open questions where it matters.
- **Keep what is right.** Do not rewrite for style. Keep the identifiers (DR-, DQ-, DX-) stable. If you must add some, append them; if you must drop one, leave its number with "withdrawn: <reason>".
- **Stay faithful:** no new fact without a source, and no claim's certainty upgraded.

## Output

- Output only the files you changed, each in full, each starting with a line of exactly `=== FILE: <path> ===`, using the draft's paths. Unchanged files are kept from the draft automatically, so do not repeat them.
- Your output **must** include a new file, `=== FILE: meta/research/done/REVIEW-2026-10-10.md ===`. It lists every critique finding with what you did (applied, applied in part, or declined with the reason), and every measurement you brought in.
- Write nothing before the first marker. Never stop a file mid-sentence.
