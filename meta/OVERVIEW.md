# Diogenes: one-page overview

Written 2026-10-10 for your review next week. The plan behind it is about 60 files. This page tells you what matters, what is waiting on you, and what you can skip.

## 1. What Diogenes is

In your words, it is "a hub where we can facilitate work between various models running in various different harnesses … while keeping things safe and manageable." The first job is narrow. The library orchestrator on your Max account hands well-defined tasks to sessions on the Team seat and to API-credit jobs. It knows each task was received, gets a report back and checks that report, and sees how much usage each account has left. **You stop carrying messages between accounts.** Gemini comes later, then a GPT auditor, then devTeam. Git and GitHub remain the source of truth: Diogenes coordinates the work but does not store it.

## 2. Day zero: the Team seat arrives before anything is built

The seat is hoped for by **Wednesday 2026-10-14 20:00**, which may be before any code exists. Everything below works with what you already have. The full steps are in `roadmap/0.0/0.0.0.1.md`.

1. **Sign in:** `mkdir -p ~/.claude-team && CLAUDE_CONFIG_DIR=~/.claude-team claude`. (A "config dir" is the folder that holds one account's login and settings.)
2. **Look at `/status` and `/config`.** Note whether you are the organization's Owner and whether any hooks are blocked. This answers DQ-4 (who controls the Team settings).
3. **Optional, 15 minutes:** check whether `SendMessage` works between the two accounts (DX-4). If it does, use it only for short nudges such as "task file at X, commit Y". Nothing depends on it.
4. **Messages are files:** one file per message in `META/NITPICK/messages/{max-inbox,team-inbox}/`. This is the same convention the Gemini inbox already uses.
5. **Tasks are committed Markdown files** in `meta/tasks/`, each with acceptance commands. The worker re-reads the task from git. It reports by making a commit, and the orchestrator re-runs the acceptance commands before accepting the work.
6. **An idle worker watches its inbox** with a background `until … sleep 60` loop that it starts itself. This has been seen to wake a session once.
7. **You write the roles and the Team usage estimate** ("about 30 % used") once per session. Workers run Opus or smaller, and you rotate them.
8. **Before any status-line setup on the Team side,** check whether your Max status-line script writes `~/.claude/usage-latest.json`. If it does, the Team copy must not use it, or it would overwrite the Max usage figures.

## 3. What cycle 0.0 builds, and how we'll know it works

**What it builds:** one database file and a small command-line tool called `dio`, written in Python. Every session uses `dio` to post, claim, report and verify tasks, to send and acknowledge messages, to take the workbench lock, to see who is live, and to read usage per account. Hooks (scripts Claude Code runs at set moments) register each session and add an "N unread" line to its prompt. You never touch the database: backups and checks are agents' work (DR-112).

**The gate, in plain words.** Cycle 0.0 passes when all of these are true:
- 10 tasks are done: 5 by a Team session and 5 by credit jobs. Each is claimed, reported, and verified by someone other than the worker who did it.
- 10 messages go each way between the accounts, all acknowledged, with `SendMessage` switched off.
- Two writers race for the lock, and each round has exactly one winner. The four worst lock failures you recorded in the past can no longer happen.
- Each account can see the other's sessions and usage. The Team usage shows as a dated estimate, or as "unknown" with the reason.
- A session pretending to be the library seat gets none of its mail or tasks.
- An idle worker that is waiting picks up a new task in 10 of 10 trials. A worker that isn't waiting is never woken.
- The prompt hook adds less than 0.3 s of delay.
- **You report zero hand relays during a normal working day.**

**Size:** about 36 seat-hours, roughly 4.5 seat-days. A seat-day is one Claude session and its helpers working for a day, including checking. The plan marks what to cut to bring it to about 31 hours. You also spend time on: about an hour typing commands the experiments prepare for you, the waits for one experiment, opening Team terminals for the gate, and one working day for the last check.

## 4. Decisions waiting for you, most urgent first

If you say nothing, the plan uses its recommendation. Each answer sits in one place, so changing your mind later costs little.

**Needed on day zero**
- **DQ-4: are you the Owner of the Team org, and does it block hooks?** This is a check you make on `/status`, not a choice. *Assumed:* you are the Owner and hooks are allowed. If hooks are blocked, the Team seat uses `dio` by hand, with no unread notices.
- **DQ-27: should both accounts share one auto-memory folder for nitpick-libs?** *Recommended:* yes, set for that project only. *If silent:* nothing is shared, because only you can make this change.
- **DQ-29: are Team workers terminals you open, or background sessions?** *Recommended and assumed:* terminals you open.
- **DQ-7: may a session start its own background wait on its own mail?** *Recommended and assumed:* yes, and nothing else may wake a session. If you say no, the "idle worker picks up a task" gate check can't be met.

**Needed before 0.0 starts** (low stakes: approving the plan's answers as a set is reasonable)
- **DQ-1 (how sessions reach the data):** the tool opens the file directly, with no background server yet. You only revisit this if experiment DX-1 fails.
- **DQ-2 (language):** Python, standard library only.
- **DQ-3 (where the data lives):** `~/.local/share/diogenes/`, outside both accounts' config dirs.
- **DQ-28 (posting a task to a nearly full account):** refuse below 15 % remaining, unless overridden with `--force`, which is recorded.
- **DQ-15 (credits correction):** the plan uses a factor of **1.00**, not the filed "two-thirds", because the bill matched what the CLI reported. **The plan asks you to confirm this.**
- **DQ-17 and DQ-22:** agent teams switched off in both accounts. Roles are named `libs-seat`, `compiler-seat`, `libs-sink` and `dio-seat`; workers are named `libs-worker_N`.

**Settled already:** DQ-5 questions 1 and 2. You go ahead on support's answer. Put questions 3 to 5 into your next message to support.

**Can wait until later cycles:** DQ-6, 8–13, 16, 18–21, 23–26.

## 5. What you can run or check yourself, if you want to

- `/status` and `/config` on the first Team session (DQ-4, 5 minutes).
- DX-4, the cross-account `SendMessage` test (15 minutes, optional).
- Whether your Max status-line script writes `~/.claude/usage-latest.json` (one look).
- Start the DX-13 wait: leave a test session idle, then trigger it after 10 minutes, after 2 hours, and overnight. It costs your waiting time, not effort.
- The pre-build experiments in `roadmap/0.0/0.0.0.0.md`: you run prepared scripts by name and type lines into test sessions. No SQL.

## 6. What you can skip, and where to look

**Skip:** `REQUIREMENTS.md`, the research digests, `VERIFY-2026-10-10.md`, `CHECKLIST.md`, `IDEAS.md`, the subcycle files other than the two named above, the cycles from 0.1 on, and `DESIGN.md` §§1–9.

| If you want… | Look at |
|---|---|
| A normal day once it's built | `DESIGN.md` §10.2 |
| The exact day-zero steps | `roadmap/0.0/0.0.0.1.md` |
| The gate and the assumed answers | `roadmap/0.0/README.md` §2–3 |
| The full text of any decision | `OPEN_QUESTIONS.md` (search for its DQ number) |
| What each experiment decides | `EXPERIMENTS.md`, "Before cycle 0.0" |
| Where anything else lives | `PROJECT_INDEX.md` |

## 7. What is uncertain

- **Can a sandboxed session and a normal process safely share one database file?** If not, a small background server moves into 0.0, adding about 2 seat-days. **DX-1** settles it. *Half measured, 2026-10-10:* writers in separate sandboxes shared one file with exactly one lock winner per round and no errors. A writer outside the sandbox is the leg left.
- **Does the "N unread" line from a hook reach the model,** both at a prompt and in the middle of a turn? If not, a clumsier fallback is used. **DX-2** settles it.
- **Does a session's own background wait wake it every time, and how long can it live?** Waking has been seen once and the time limit was never tested. This decides whether idle workers can pick up tasks without you. **DX-13** settles it.
- **How much room does the Team seat have left?** It likely reports no usage limits, so its usage may stay a rough estimate. **DX-5** and **DX-26** settle it, on the first Team session.
- **The plan itself has never been run.** The planner had no shell, so every "expected" result is a prediction. Reviewers checked it twice and it passed, with nine small fixes still to make. Some findings from the afternoon are not yet folded into the design (`DESIGN.md` §11): PostgreSQL is available locally, plus notes on mods and Antigravity. They do not affect 0.0. The size may go over the estimate. The cut line exists for that.