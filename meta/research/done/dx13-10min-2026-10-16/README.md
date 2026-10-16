# DX-13, the 10-minute leg (2026-10-16): the record

Job: DX-13's 10-minute leg, which Diogenes 0.0-min build step 2 runs before `dio watch` ships ([`../../../roadmap/0.0/MIN.md`](../../../roadmap/0.0/MIN.md), step 2), run by the Team seat's manager `Ailp-team_5` on its own session; filed by the Team seat's `D4-diogenes-dio-watch`, dispatched by `Ailp-team_6` · Date: 2026-10-16 · Model: not recorded for the run's session; the filing ran on Claude Opus 5.5 (`claude-opus-5-5`) · Tools: in the run, the session's Bash tool (a `run_in_background` task for the loop, `setsid` for the timer, `date`, `ps`, `ls`) and its transcript's metadata, read afterwards; in the filing, `cp -p`, `cmp`, `sha256sum`, `tail`, `grep` and the reference checker of `PROJECT_RULES.md` §7

What the record means for DX-13 is in `meta/EXPERIMENTS.md`, in the **RESULT (10-minute leg), 2026-10-16** bullet under DX-13. This folder holds the file that bullet rests on.

**Limits:**
- **One trial, on a working seat.** The probe was the manager's own session, at 46–47 % of a 1 M context (the record's deviation 1), not a fresh small probe. So the wake's cost is a working seat's.
- **The 2-hour and overnight legs did not run.** They run at the gate (`MIN.md` step 2; the author's steps, B3), so any lifetime cap of a background loop is still unmeasured, and so is a wake's cost past the cache's life.
- **Some of the record is not filed.** The transcript it reads, `~/.claude-team/projects/-home-randy-Team/b0982a56-a9c5-4b99-b0d0-e60a75b8b05c.jsonl`, holds the session's conversation and stays where it is. The run's directory, `/home/randy/Team/TMP/dx13`, was removed at 01:04:15 EDT, so the raw record and the go file's mtime survive only in this file (its lines 92–94).
- **Several readings in it are `diogenes_0`'s, and say so** (lines 42, 69–70, 72–73, 78–79, 81 and 84–85): `diogenes_0` read the same transcript's metadata.
- **Its line 11 cites `meta/EXPERIMENTS.md:137`,** DX-13's `- Steps:` line when the record was written. The RESULT bullet filed with it sits above that line and moves it down. The citation stays, since the file is filed byte for byte.
- **Nothing was redacted.** No line holds the value of anything whose name contains `TOKEN`, `KEY` or `SECRET`: "token" occurs only in usage field names and their counts, such as `cache_read_input_tokens` (D4's case-insensitive `grep`, before the copy was filed).
- **The ps lines (124–127) carry harness paths:** the shell snapshot under `/home/randy/.claude-team/shell-snapshots/`, the `/tmp/claude-*-cwd` files the Bash tool writes, and the manager's scratchpad under `/tmp/claude-1000/`. They stay, byte for byte. The §7 check's leak pattern matches none of them. Its 14 matches in the file are all `/home/randy` paths, the known class the §7 line counts and does not fail on.

## The file

| File | What it is | Lines | sha256 |
|---|---|---|---|
| `DX13-10min-leg-2026-10-16.txt` | The Team seat's record of the leg: its account (lines 1–108), revised on 2026-10-16 after `diogenes_0`'s six corrections (line 3), and the raw record (lines 112–134), below the header and rule at lines 110–111, appended byte for byte from `/home/randy/Team/TMP/dx13/record.txt`. A byte-for-byte copy of `/home/randy/Team/REPORTS/DX13-10min-leg-2026-10-16.txt` | 134 | `24fa9e61581b2ed2b4878b469406d8d6b13351d9238d38f5dc9e70e36cb5a2cf` |
| `README.md` | This file | | |

- The copy was checked against its source with `cmp` and `sha256sum` at 03:39:09 EDT: identical. The raw record alone, lines 112–134 (`tail -n +112`), has sha256 `98784e7f17577b73fc35cf1b8d0d211c47a1e4b8edafaa78ce46912fe6cd9822`, the revised copy's, as D4's brief gives it (it begins `98784e7f`).
- The file has no trailing spaces and no tabs.

## Who made each line

| Lines | Made by | How |
|---|---|---|
| 1–108, the account | `Ailp-team_5`, the Team seat's manager, after the run | From the raw record, the loop task's own output, `ps`, and the transcript's metadata. Revised after `diogenes_0`'s six corrections (line 3), with `diogenes_0`'s readings marked as its own |
| 110–111 | `Ailp-team_5` | The header and rule above the raw record |
| 112–133, the raw record | `Ailp-team_5`'s own Bash, in the setup turn, from 00:52:02 to 00:52:21 EDT | Its setup commands and the timer script `dx13-timer.sh` in its scratchpad, which the ps line at 125 shows running |
| 134 | The detached timer | Its `date`, run just before its `touch` of the go file, at 01:02:09.957 EDT |

In the raw record, each `date` reading carries its offset, `-0400` (EDT); the `ps` start times (lines 124–127 and 130) are EDT without one; and the two status-line readings (lines 120–121) are UTC, with a `Z`. The account gives EDT times without a zone, and UTC ones with a `Z` (lines 88–91).

## Clock times, EDT, 2026-10-16

- **Setup:** 00:52:02.117 (line 113). The loop task started at 00:52:05 (line 130), and the timer at 00:52:09.949 (line 122). The setup turn's last tool call was at 00:52:21.066 (line 133), and the turn ended at 00:52:46.003 (line 67).
- **The timer's clock line:** 01:02:09.957 (line 134), and the go file's mtime 01:02:09.958 (line 56).
- **The loop's exit line:** 01:02:35.612 (line 57). **The wake:** the task-notification's enqueue at 01:02:35.622, the turn's start at 01:02:35.671, and its first `date` at 01:02:44.571 (lines 60–65).
- **The run's directory removed:** 01:04:15 (line 92).

## Claude Code version

2.1.301, by the session's own sessions file's `version` (line 13).

## Provenance of this filing

- Filed by `D4-diogenes-dio-watch` (Claude Opus 5.5), which `Ailp-team_6`, the Team seat's manager, dispatched on 2026-10-16 (its brief: `date` read 03:02:16 just before the dispatch), on branch `team/diogenes-0.0-dio-watch`. Its brief is `/home/randy/Team/META/diogenes/briefs/D4-diogenes-dio-watch.txt`, with its amendment 1.
- **Source:** `/home/randy/Team/REPORTS/DX13-10min-leg-2026-10-16.txt`, read whole before it was filed.
- **The §7 check ran on the filed copy first** (03:39:09 EDT), before this file or the RESULT bullet was written: exit 0, with the copy's 14 `/home/randy` matches counted among the known paths and nothing else flagged.
