# dio-v1-verify-0.0-plan-2026-10-10

You are the independent **plan verifier** for Diogenes' cycle 0.0. A plan is not handed to an executor until a verifier has checked it. Your job is to find what would make an executor fail, guess, do harm, or "pass" without the gate really holding.

Read, in full:

1. `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md`: the context, the author's messages, and the correction at its end.
2. `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-firsthand-2026-10-10.md`: measurements M1–M5. They outrank every document.
3. **The plan:** every file in `/home/randy/Workspace/REPOS/diogenes/meta/roadmap/0.0/`, that is the `README.md`, ten subcycle files `0.0.*.md`, and `CHECKLIST.md`.
4. What it must satisfy, in `/home/randy/Workspace/REPOS/diogenes/meta/`:
   - `roadmap/ROADMAP.md` (day zero, and cycle 0.0's goal, scope, gate and size);
   - `REQUIREMENTS.md` (the ★ P0 set, and DR-100 … DR-112);
   - `DESIGN.md` §10 and §11;
   - `OPEN_QUESTIONS.md`;
   - `EXPERIMENTS.md`;
   - `PROJECT_RULES.md`;
   - `README.md` (the cycle and subcycle conventions).

## Check

1. **Coverage.** Does every ★ P0 requirement, and every DR-100 … DR-112 that 0.0 claims, have a subcycle that builds it and a check that proves it? List any that are missing, and any the plan builds that 0.0 should not.
2. **Executability.** Could an executor that is weaker than the planner, and was absent from planning, follow each step without guessing?
   - Flag missing file contents, unspecified arguments, unstated defaults, commands whose expected output is not given, and steps that depend on knowledge only the planner had.
   - Check the shell commands, the SQL DDL, the JSON of hooks and settings, and the Python for correctness **as written** on Ubuntu 24.04 with Python 3.12, sqlite3 3.45.1 and Claude Code 2.1.296.
3. **The measurements:**
   - Does any step assume that a sandboxed shell reaches anything by Unix socket or loopback TCP?
   - Does any step need writes outside the sandbox's allow list without saying so, as a step **for the author**?
4. **Safety:**
   - Does any step touch the system Redis, MySQL or PostgreSQL, the default ports, the author's `~/.claude` settings, or another session's sockets?
   - Does any step widen a sandbox, install a system package, or change the author's settings without saying so as a step **for the author**?
   - Is there a backup before every store change?
   - Is every message and stored entry handled as data?
   - Does any step ask the author for SQL (DR-112)?
5. **The gates.** Is each subcycle's acceptance measurable, and would it fail if the work were wrong? Look for gates that pass vacuously: a test that cannot fail, a check on the wrong side of a write, an unstated denominator. Look for a missing positive control.
6. **The assumptions table.** Does it list every open question the plan relies on? Would a different answer really re-cut only the subcycles named?
7. **Size and order.** Is the cycle within the ROADMAP's size? Is the order right, with experiments first and each dependency built before its use? Is there a cut line?
8. **Consistency** with the filed plan: identifiers, names, paths, commands, and the day-zero section.

## Output

Your final message is the report, in Markdown:
- **A verdict: PASS, PASS WITH FIXES, or FAIL.**
- The findings, V-1 … V-n, most severe first. Each gives:
  - its severity: **blocking**, **major** or **minor**;
  - the file and section;
  - the problem;
  - the evidence, quoted;
  - a concrete fix, with exact replacement text where it is short.
- What you checked and found sound, so that the next reader knows what was covered.
- What you could not check.

You are read-only. Give fixes; do not rewrite the plan.
