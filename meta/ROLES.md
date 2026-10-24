# diogenes: the role line

Who holds each role in this repository. `dio who --address <role>` resolves a role to its holder from this file, and a worker refuses a task whose `posted-by` is not on the `poster` line ([`roadmap/0.0/MIN.md`](roadmap/0.0/MIN.md), decision 3; [`tasks/README.md`](tasks/README.md)).

- **Only the merger writes this file, on `main`.** A holder who hands over asks the merger by message. The merger checks the successor's name before committing: with `dio who`'s process check, or, until `dio who` exists, `test -S` on a Team seat's socket plus the from-name on the successor's own message, or `ListAgents` for a Max seat. The outgoing merger's last commit writes its successor's `merger` line.
- **The commit history is the role history.** Each commit message names the request it answers and the check made.
- **Format:** one role per line, `<role> = <holder>[, <holder>…]`, inside the fenced block below. Parsers read only the lines inside that block, so nothing outside it is a role line.

```text
team-seat = Ailp-team_18
merger = diogenes_3
poster = management_2, diogenes_3
probe-seat = probe-t_3
```

What each role is:

- `team-seat`: the Team seat's manager session, on the Team account. It builds on `team/diogenes-<task>` branches and never pushes `main`.
- `merger`: diogenes' one writer of `main`. It verifies and merges branches, and commits the task files and this file.
- `poster`: the holders whose task files the merger commits and the Team seat works.
- Gate M1 adds `probe-seat` for its overlap round.
