# dio-o1-overview-2026-10-10

Write **`meta/OVERVIEW.md`** for Diogenes: a short, plain-language overview for the author, who will review the whole plan next week.

**The author's situation:**
- He has ADHD, and his attention is the scarcest resource in the project.
- The plan is now about 60 files. He needs one page that tells him what matters, what is waiting on him, and what he can skip.
- He dislikes database chores, and never writes SQL (DR-112).
- He values candour over comfort: say plainly what is uncertain.

Read, under `/home/randy/Workspace/REPOS/diogenes/meta/`:
- `PROJECT_GOALS.md`;
- `roadmap/ROADMAP.md`, especially "Day zero" and cycle 0.0;
- `roadmap/0.0/README.md`: its status, its gate and its assumptions table;
- `OPEN_QUESTIONS.md`;
- `DESIGN.md` §10 and §11;
- `EXPERIMENTS.md`, only the list of experiments and what each decides;
- `PROJECT_INDEX.md`.

Also read the author's own words, in `/home/randy/Workspace/REPOS/nitpick-libs/.internal/credits/context/diogenes-2026-10-10.md`.

**Write about 1 000 to 1 500 words, in these sections:**
1. **What Diogenes is,** in three or four sentences, in his terms.
2. **What happens on day zero,** the day the Team seat arrives, if cycle 0.0 is not built yet. Give the concrete steps.
3. **What cycle 0.0 builds, and how we will know it works:** the gate in plain words, and its size.
4. **The decisions waiting for you,** most urgent first. Include only the ones that block cycle 0.0 or day zero. For each: the question in one line, the plan's recommendation, and what happens if he says nothing (the default the plan assumes). Then name the rest in one line, as "can wait until later cycles".
5. **What you can run or check yourself, if you want to:** at most five items, each one line.
6. **What you can skip reading,** and **where to look** for each kind of detail.
7. **What is uncertain,** in three to five bullets: the biggest unknowns, and the experiment that settles each.

**Style:** plain words, short sections, bullets. Explain each piece of jargon once, or avoid it. Use no internal identifier unless it helps him find something, and gloss it when you do: "DQ-3 (where the data lives)".

**Output:** your final message is the file. Its first line is `=== FILE: meta/OVERVIEW.md ===`, and nothing comes before it.
