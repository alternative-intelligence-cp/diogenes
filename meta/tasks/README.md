# meta/tasks — task files

This folder holds the task files of Diogenes 0.0-min ([`../roadmap/0.0/MIN.md`](../roadmap/0.0/MIN.md), gate M3) and after. Their convention:

- **One file per task:** `meta/tasks/<date>-<item>.md`, a tracked path, with the task template's required lines in order (`MIN.md`, "Decisions, rules and size"). The template itself, `docs/TASK-TEMPLATE.md`, is written by the build.
- **`diogenes_0`, diogenes' one writer of `main`, commits each task file on `main` for its poster.** `posted-by` names the poster, and the commit message names the poster's message: its sender and its clock time.
- **The Team seat works a Team task in its own clone,** `/home/randy/Team/REPOS/diogenes`. It fills `report:` on its branch `team/diogenes-<item>` and pushes, and it never edits the Workspace copy.
- **For a credits-job or subagent task, the poster's seat fills `report:`** on a Workspace branch, from the runner's output path or the subagent's REPORT block.
- **`verified-by:` is filled on `main` at merge by the verifier:** `diogenes_0` for a Team task; for a credits-job or subagent task, a seat or verifier subagent other than the reporter.
- **The poster line is in `meta/ROLES.md`,** which `diogenes_0` commits on `main`. Outside the gate, `diogenes_0` commits no task file from a sender off the poster line: it holds the file and asks `management_0`. The one exception is M3's fourth task, posted by `probe-m`, which is not on the poster line: `diogenes_0` commits it all the same, so that the Team seat's refusal (`refused: poster`) is what gets tested.
