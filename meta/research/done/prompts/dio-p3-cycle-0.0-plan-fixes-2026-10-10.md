# dio-p3-cycle-0.0-plan-fixes-2026-10-10

You amend Diogenes' cycle 0.0 plan against its independent plan verifier's findings. Read, in full:

1. `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md`: the context, the author's messages, and the corrections at its end.
2. `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-firsthand-2026-10-10.md`: measurements M1–M5. They outrank every document.
3. **The plan:** every file in `/home/randy/Workspace/REPOS/diogenes/meta/roadmap/0.0/`.
4. **The re-verifier's report:** `/home/randy/Workspace/REPOS/diogenes/meta/research/done/dio-v2-reverify-0.0-plan-2026-10-10.md`. Its verdict is PASS WITH FIXES, with findings R-1 … R-10 to fix. The plan was already amended once against V-1 … V-29: see `VERIFY-2026-10-10.md` in the plan, and the first verifier's report `/home/randy/Workspace/REPOS/diogenes/meta/research/done/dio-v1-verify-0.0-plan-2026-10-10.md`. Change ONLY what R-1 … R-10 require.
5. As needed, the filed plan the cycle must satisfy, in `/home/randy/Workspace/REPOS/diogenes/meta/`: `REQUIREMENTS.md`, `DESIGN.md`, `roadmap/ROADMAP.md`, `OPEN_QUESTIONS.md`, `EXPERIMENTS.md`, `PROJECT_RULES.md` and `README.md`. Also the credits runner `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/run.sh` and its `README.md`, which V-3 concerns.

## Do

- **Fix every blocking and major finding.** If you judge a finding wrong, decline it and give the reason, with evidence from the files.
- **Fix minor findings where it is cheap.**
- **Keep everything that is right.** Do not rewrite for style. Keep the subcycle names and the gate and acceptance identifiers. If you must add a test or a step, append it; if you must drop one, leave a line saying "withdrawn: <reason>".
- **Check your own arithmetic and expected values against the code you specify.** Several findings were tests whose expected values contradicted their own code. Re-derive every number you touch.
- **Keep the safety rules:**
  - private instances only;
  - nothing touches the system databases, the default ports, the author's `~/.claude` files (the meters file `~/.claude/usage-latest.json` above all), or another session's sockets;
  - any change to the author's settings, any widened sandbox, and any install is written as a step **for the author**;
  - no step spends API credits unless it says so, with a stated cap;
  - nothing asks the author for SQL.

## Output

- Output **only the files you changed**, each in full, each starting with a line of exactly `=== FILE: meta/roadmap/0.0/<name>.md ===`. Unchanged files stay as they are.
- Your output **must** include the existing file `=== FILE: meta/roadmap/0.0/VERIFY-2026-10-10.md ===`, in full: its current text, unchanged, plus a new section at the end, "Second amendment (R-1 … R-10)". The section lists every R-finding with what you did: fixed (where), fixed in part, or declined (why).
- Output no file that R-1 … R-10 do not require you to change.
- Write nothing before the first marker. Never stop a file mid-sentence.
