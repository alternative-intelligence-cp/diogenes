# The task template

In Diogenes 0.0-min a task exists only as a committed file under this template ([`USING.md`](USING.md), rule 5). This is build step 5's template ([`MIN.md`](../meta/roadmap/0.0/MIN.md), "The task template, required lines, in order", and decisions 3 and 5). The task files' convention is [`meta/tasks/README.md`](../meta/tasks/README.md):

- one file per task, `meta/tasks/<date>-<item>.md`, a tracked path, with the required lines in order;
- the merger, the holder of the `merger` line of [`meta/ROLES.md`](../meta/ROLES.md), commits each task file on `main` for its poster, and the commit message names the poster's message: its sender and its clock time;
- the merger pushes `main`, and the Team seat pulls `main` before it branches.

This file writes no task file. Those are the merger's commits.

## The template

A task file begins with a title line and then holds the nine lines, in this order, in its first fenced block, as `meta/ROLES.md` holds its role lines. Nothing outside that block is a task line. Every line is there from the post on, and a line not yet filled is left empty after its colon. The angle brackets below are placeholders.

````markdown
# <date>-<item>: <what the task is, in a few words>

```text
spec: <tracked path> at <commit>
posted-by: <the poster's name>
assigned-to:
cross-account: <yes or no>
room-at-post: <measured, estimate or unknown>, <the figures and where they were read>
acceptance: <the acceptance commands, and where the spec gives them>
report:
verified-by:
merged-at:
```
````

## Each line

Every time in a task file comes from a clock, never from memory, and is written in ISO 8601 UTC with a `Z` ([`PROJECT_RULES.md`](../meta/PROJECT_RULES.md) §5). "Main" is this repository's `main`, which only the merger writes ([`USING.md`](USING.md), rule 4).

| Line | What it holds | Who fills it | Where | When |
|---|---|---|---|---|
| `spec` | A tracked path and the commit to read it at, `<path> at <commit>`, with the repository named if it is not this one. The worker reads the spec with `git show <commit>:<path>`, never from the task file | The poster | The task file the merger commits on `main` | At the post |
| `posted-by` | The poster's own name, as it stands on the `poster` line of `meta/ROLES.md` | The poster | The task file the merger commits on `main` | At the post |
| `assigned-to` | The worker's name. It is the claim | The worker; for a credits-job or subagent task, the poster's seat, which also fills `report` | The first commit of the worker's branch, `team/diogenes-<item>` for the Team seat, or a Workspace branch for the poster's seat | When the worker takes the task, after the poster check and before any other work |
| `cross-account` | `yes` if the poster and the worker are on different accounts, else `no` | The poster | The task file the merger commits on `main` | At the post |
| `room-at-post` | The room of the account the task runs on, when it is posted: `measured`, `estimate` or `unknown`, with the figures and where they were read; an `estimate` also gives its method and date. For a task on an account's plan, the poster copies that account's `usage` line from `dio meters`, `measured` if its state is, else `unknown`, as in the cut form (`MIN.md`, "Cut trigger"); for a credits job, `unknown`, naming the pool, `team-org` or `individual-org`, as the `credits` lines of `dio meters` name it (decision T6) | The poster | The task file the merger commits on `main` | At the post |
| `acceptance` | The acceptance commands, as the spec gives them, and where in the spec they are. The verifier re-runs exactly these | The poster | The task file the merger commits on `main` | At the post |
| `report` | The report's path, in git or in a `REPORTS/` folder, and the commit it reports on: a report is a file plus a commit | For a Team task, the Team seat; for a credits-job or subagent task, the poster's seat, from the runner's output path or the subagent's REPORT block | The worker's branch, or the poster's seat's Workspace branch | When the work is done, before it is verified |
| `verified-by` | The verifier's name. The verifier is not the reporter, and it re-ran the acceptance commands | The merger, which names the verifier: itself for a Team task; for a credits-job or subagent task, a seat or verifier subagent other than the reporter | `main` | At the merge, in the merger's first commit after the merge commit (decision T2) |
| `merged-at` | The commit that merged the branch into `main`, and the time it was made | The merger | `main` | At the merge, in the merger's first commit after the merge commit (decision T2) |

`cross-account` and `room-at-post` are decision 5's: `cross-account` is `yes` or `no` (DR-80's tag), and `room-at-post` is `measured`, `estimate` or `unknown` (DR-103). Neither is checked by a gate item, and both are notes: the room floor and its refusal are 0.1, with DQ-28.

M3 gates on four of the lines, `spec`, `assigned-to`, `report` and `verified-by`, and the poster check gates through its fourth task (`MIN.md`, "The task template, required lines, in order", and gate row M3).

## The poster check

Before any work, the worker checks `posted-by` against the `poster` line of `meta/ROLES.md`, as it stood in the commit that added the task file (decision T3). This line prints `meta/ROLES.md` at that commit, from the repository's root, with the task file's path for `<task file>`:

```sh
git show "$(git log --diff-filter=A --format=%H -1 -- <task file>)":meta/ROLES.md
```

The `poster` line is the one inside its fenced block. If `posted-by` is not one of that line's holders, the worker refuses the task as `refused: poster` (DR-102), before any work: it fills no line, makes no branch for the task, and reports the refusal back to the merger, which committed the file. M3's fourth task, posted by `probe-m`, a session not on the poster line, tests this refusal (`MIN.md`, gate row M3).

`PROJECT_RULES.md` §1, in its note for 0.0-min, names the task's other two conditions: a `spec` line naming a tracked path plus a commit, and acceptance commands that live in the spec. A task that fails one of them is reported back as `refused: <condition>` too.

## Decisions this file makes

`MIN.md` is silent on each of these points, and T6 is the text [`FINISH.md`](../meta/roadmap/0.0/FINISH.md) gives for one of them. Each is listed for the merger's review.

- **T1. Who fills each line: D1v's finding 2, settled.** D1v found that who fills `spec` and `assigned-to` is not stated, and that `verified-by`, "filled on `main` at merge by the verifier" (gate row M3), agrees with rule 4's one writer of `main` only if the merger is the verifier or commits the line for it (`/home/randy/Team/REPORTS/D1v-diogenes-0.0-min-plan-verify.md:88`; `MIN.md`, the note after "The task template, required lines, in order"). This file takes `diogenes_0`'s reading, which agrees with `meta/tasks/README.md` at every point:
  - the poster fills `spec`, with `posted-by`, `cross-account`, `room-at-post` and `acceptance`, in the file the merger commits on `main`, as the README has the merger commit "each task file on `main` for its poster";
  - the worker fills `assigned-to`, the claim, as its branch's first commit, the way it fills `report:` on its branch (the README: the Team seat "fills `report:` on its branch"); for a credits-job or subagent task, the poster's seat fills both, since it fills `report:` (the README);
  - the merger fills `merged-at` at the merge.

  The README's "`verified-by:` is filled on `main` at merge by the verifier" is read so that it agrees with rule 4: the line names the verifier, and the merger commits it on `main`. For a Team task the merger is the verifier, as the README says, and for a credits-job or subagent task it commits the name of the seat or verifier subagent that verified.
- **T2. `merged-at` names the merge commit, in the merger's next commit.** A commit cannot hold its own hash, so the merge commit cannot name itself. The merger fills `merged-at`, and `verified-by` with it, in its first commit on `main` after the merge commit, as it already follows each merge with a records commit (`0cd808a`, then `648c5be`, for build step 3).
- **T3. The poster check reads the poster line as it stood when the task was added.** Holders rotate: the poster line changed twice on 2026-10-16 (`79a9646` and `60cd8c0`). A task that the merger committed for a poster then on the line stays that poster's task after a handover, and the merger commits no task file from a sender off the line outside the gate (`meta/tasks/README.md`). M3's fourth task, from `probe-m`, is refused either way, since `probe-m` is on no poster line.
- **T4. The lines sit in the file's first fenced block,** as `meta/ROLES.md`'s role lines do, so that a Markdown view shows them one per line, and no prose in the file is mistaken for a task line.
- **T5. A refused task gets no line and no branch.** The claim is the branch's first commit, and DR-102's refusal comes before any work, so a refused task is never claimed. The worker reports the refusal to the merger by message. A refusal is a decision, so its log line is written first ([`USING.md`](USING.md), rule 3).
- **T6. `room-at-post` copies the `usage` line of `dio meters`.** This is `FINISH.md`'s text, in its step 7 ("T6"), accepted with that plan at `fbbbb7e`: "for a task on an account's plan, the poster copies that account's `usage` line, `measured` if its state is, else `unknown`, as in the cut form (:294); for a credits job, `unknown`, naming the pool." The `:294` there is `MIN.md`'s line 294, its "Cut trigger": had `dio meters` been cut, `room-at-post` would be a `python3 -c` line's output copied by the poster, "labelled `measured` for both accounts, or `unknown` if the file is older than 10 minutes". `dio meters` reads `measured` while the file is at most 600 s old, and otherwise `stale (<N> min)` or `unknown (<reason>)`, for either of which the poster writes `unknown`. A credits job is billed to an organization's API credits, not to an account's plan (`FINISH.md`, step 7, "The ledgers"), so its room is `unknown`, with the pool it bills, as the `credits` lines of `dio meters` name it: `team-org` for the Team organization's credits, `individual-org` for the individual organization's.
