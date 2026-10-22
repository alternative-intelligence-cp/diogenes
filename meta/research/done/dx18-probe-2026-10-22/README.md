# DX-18, the listing half (2026-10-22): the record

Job: DX-18's listing (`claude agents --json --all` under each config dir, as a presence source), which Diogenes 0.0-min's finishing plan runs as step 8a ([`../../../roadmap/0.0/FINISH.md`](../../../roadmap/0.0/FINISH.md), 8a), against `dio who`. Date: 2026-10-22, 07:27 EDT. Run by the author, who ran the two listing lines, and by the Team seat's manager, `Ailp-team_16` (Claude Opus 5.5, Claude Code 2.1.307, the `~/.claude-team` config dir), which ran `dio who` and wrote this record. Tools: `claude agents`, `src/dio who` at `dfe29c4`, `jq`, `ps`, `sha256sum`, and the summary script named in `result.txt`. `management_2` set the minute with the author (its message, 07:22:25 by its `date`) and relayed the author's run (07:27:14 by its `date`).

What the record means for DX-18 is in `meta/EXPERIMENTS.md`, in the RESULT at the file's end, which DX-18's heading points to. This folder holds `result.txt`, which that RESULT rests on.

## What ran

- **The author, 07:27:00,** in a plain terminal, ran the run sheet's two lines (`/home/randy/Team/META/diogenes/probes/DX3-run-sheet.md`:264–265): `claude agents --json --all` once with no `CLAUDE_CONFIG_DIR` (the Max account) and once with `CLAUDE_CONFIG_DIR="$HOME/.claude-team"`, each into `/home/randy/Team/PROBES/dio-probe/results/DX18-{max,team}-agents.{json,err}`. The four files' mtimes read 07:27:00.39 to 07:27:00.87, and both `.err` files are empty.
- **The Team seat, in the same minute,** ran `src/dio who` from its clone at `dfe29c4` twice, at 07:27:15.63 and 07:27:45.84 (each start and end read by `date`), each exit 0 with an empty stderr. The two outputs are byte-identical: 21 rows, all live, 18 `max` and 3 `team`.
- **Then** `ps -eo pid,ppid,lstart,args` (07:27:48) for any process with `claude` in its arguments started since 07:20:00, to see whether the listing left a supervisor running.

## What came back (from `result.txt`)

| Config dir | Listing rows | By `kind` | By `status` | Live `dio who` rows | Listed by pid, `kind` `interactive` | Listing rows with no live `dio who` row |
|---|---|---|---|---|---|---|
| `~/.claude` (`max`) | 18 | `interactive` 18 | `busy` 3, `idle` 15 | 18 | 18 of 18 | 0 |
| `~/.claude-team` (`team`) | 4 | `interactive` 3, `background` 1 | `busy` 1, `idle` 2, null 1 | 3 | 3 of 3 | 1, the `background` row |

- **The `background` row** is the DX-3 probe's conversation of 2026-10-15 (its `name` "DX-3 Diogenes probe", `startedAt` 14:40:23 EDT that day), with `state` `stopped`, `status` null and `pid` null. It has no process, so `dio who` rightly has no row for it.
- **`status` against `dio who`'s state:** in all 21 matched rows, `busy` goes with `live` and `idle` with `live-idle`.
- **Keys:** every `max` row has `cwd`, `kind`, `name`, `pid`, `sessionId`, `startedAt` and `status`, with an integer `pid`. In the `team` listing, its `background` row alone adds `id` and `state`; its three `interactive` rows have neither. No row has `waitingFor`.
- **The supervisor:** besides the Team seat's own shells, the only process with `claude` in its arguments started since 07:20:00 is one Max seat's (pid 1710264, started 07:20:39 with `--name`, and listed by both `dio who` and the Max listing). So no process the listing started was still running at 07:27:48. UNVERIFIED: whether a supervisor started and exited within those 48 seconds.

## The raw files, kept local

They carry every live session's `sessionId` on both accounts, and DX-18's question needs none of it (`DX3-run-sheet.md`:350). They are in `/home/randy/Team/PROBES/dio-probe/results/`, where the run sheet's two lines wrote them, not in `META/diogenes/probes/`, where its :350 says they stay.

| File | Bytes | sha256 |
|---|---|---|
| `DX18-max-agents.json` | 4 501 | `b3b4635607752b1a5e52d6371fa745335f70b7ca3d3e7b4c333e6f0811989852` |
| `DX18-max-agents.err` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `DX18-team-agents.json` | 930 | `f508f6b56a8bc55636c21cbf43d3e722feeab6e02a9624fe1424e1f2d0604032` |
| `DX18-team-agents.err` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `DX18-dio-who-1.txt`, `DX18-dio-who-2.txt` | 2 682 each | `5a8eb3fe0aec1619f5036f54e29bc7c993cabb102a2ca860a0ddce5eaa6b84df` |

## Limits

- **One listing per config dir, in one minute.** Every seat was as it was at 07:27, with three busy and the rest idle. No seat was started, stopped or backgrounded for the run.
- **DX-18's other half did not run:** no `claude --bg` session was started and left idle for an hour, so the background-session lifetime and whether its socket stays bound are still UNVERIFIED (DX-18's "Expected").
- **The only background row was already stopped.** A running background session's row (its `pid`, `status` and `state`) is unmeasured.
- **Sandboxed Bash was not tried.** Both lines ran in a plain terminal, as the run sheet says (`DX3-run-sheet.md`:269), so whether the listing works from inside a seat's sandbox is still a separate question.
- **The summary script is Team-local** (`/home/randy/Team/META/diogenes/probes/dx18_summary.py`, sha256 `98a818fc67785b3421c530031577e37f73fbf9cf2a845bd3cf856d63fcb28705`), not filed here. `result.txt` shows its output whole.
