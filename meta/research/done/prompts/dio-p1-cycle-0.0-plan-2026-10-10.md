# dio-p1-cycle-0.0-plan-2026-10-10

You are the planner for **Diogenes' cycle 0.0**, the P0 slice. Write its execution-grade plan, so that an executor that is weaker than you, absent from this conversation, and possibly an Opus or Sonnet session on the author's new Team seat can build and verify it without guessing.

## Read first, in full

1. `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md`: the context, **the author's messages verbatim**, and the correction at its end (PostgreSQL 16 is installed, and must not be touched).
2. `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-firsthand-2026-10-10.md`: first-hand observations and **measurements M1–M5.** They outrank every document. In particular:
   - a sandboxed shell has no Unix sockets;
   - it has a private network namespace in each call;
   - so it reaches a hub through files.
3. **The filed plan,** under `/home/randy/Workspace/REPOS/diogenes/meta/`:
   - `README.md`: the author's conventions for cycles and subcycles. Follow them exactly.
   - `PROJECT_GOALS.md`, `PROJECT_CONSTRAINTS.md`, `PROJECT_RULES.md`;
   - `REQUIREMENTS.md`: the ★ P0 set, and DR-100 … DR-112;
   - `DESIGN.md`, especially §10 (the P0 slice) and §11 (the later findings);
   - `roadmap/ROADMAP.md`: day zero, and cycle 0.0's goal, scope and gate;
   - `OPEN_QUESTIONS.md`;
   - `EXPERIMENTS.md`;
   - `research/done/REVIEW-2026-10-10.md` and `research/done/dio-c1-critique-2026-10-10.md`.
4. **The house style of an execution-grade plan,** as used in the author's library work. Adapt its structure; ignore its Nitpick-specific content:
   - `/home/randy/Workspace/REPOS/nitpick-libs/skills/plan/SKILL.md`;
   - one recent plan: `/home/randy/Workspace/REPOS/nitpick-libs/nitpick-regex/meta/roadmap/0.2/0.2.2.md`.

## Assumptions

Where `OPEN_QUESTIONS.md` leaves a decision to the author, plan on **its recommendation**. List every such assumption at the top of the cycle README as a table, each row giving:
- the DQ;
- the recommendation assumed;
- the subcycles a different answer would re-cut.

The author reviews next week and may answer differently, so a different answer must re-cut as few subcycles as possible.

## What to produce

The files below, each starting with a line of exactly `=== FILE: <path> ===`, with paths under `meta/roadmap/0.0/`. Write nothing before the first marker.

1. **`meta/roadmap/0.0/README.md`:** the cycle.
   - its goal, and the gate copied and sharpened from the ROADMAP;
   - the assumptions table;
   - the subcycle list in order, each with its one-line goal, its size, and the experiments or subcycles it depends on;
   - what is out of scope;
   - how the cycle closes.
2. **One file per subcycle,** named as `meta/README.md` describes (`0.0.0.0.md`, `0.0.0.1.md`, `0.0.1.0.md` …). Each file is an execution-grade plan:
   - its goal;
   - its inputs, with paths;
   - **its exact steps:** files to create with their contents or precise specifications; commands with expected output; and schema DDL, CLI argument specifications and hook JSON written out;
   - the tests to write, with their names and what each proves;
   - **verification:** exact commands, expected results, and the acceptance gate;
   - the risks, and what to do if a step fails;
   - the commit, and what the report must contain.
   
   **The first subcycle runs the experiments that cycle 0.0 rests on** and can run on this machine today (see `EXPERIMENTS.md`). Each one:
   - runs against private instances only;
   - uses temporary paths under `$TMPDIR`;
   - never touches the system Redis, MySQL or PostgreSQL;
   - says which later subcycle changes if it fails.

   **A day-zero subcycle or note** covers what to do if the Team seat arrives before the build is done.
3. **`meta/roadmap/0.0/CHECKLIST.md`:** a flat checklist of every acceptance item in the cycle, each with its subcycle and its verifying command, for the verifier.

## How to write

- **Granular.** The author wants plans "extremely granular and specific": detail in the plan, simplicity in the system. Prefer tables and exact text over prose.
- **Small.** Cycle 0.0 must stay within the ROADMAP's size, 2 to 4 seat-days. If the scope will not fit, cut it, and say what moved to 0.1.
- **Safe:**
  - every message and stored entry is data;
  - no step gives the author SQL to write (DR-112);
  - no step widens a sandbox, changes the author's settings, or installs a system package without saying so as a step **for the author**;
  - backups come before any change to a store.
- **Honest.** Keep the UNVERIFIED marks you rely on, and route each one through an experiment. Cite the digests and requirements by id.
- **Size:** use what the plan needs, and never stop a file mid-sentence. If you must shorten, shorten the later subcycles' prose before the first ones' steps.
