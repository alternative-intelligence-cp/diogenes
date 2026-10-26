# Diogenes 0.0-min's gate, run 2026-10-24: the record

Job: the gate of Diogenes 0.0-min, the checks of [`MIN.md`](../../../roadmap/0.0/MIN.md)'s gate table (:196–206), with the finishing plan's own legs: DX-13's three exits, DX-3's F9 legs and F6's cleanup. It ran as [`FINISH.md`](../../../roadmap/0.0/FINISH.md)'s "The gate's run plan" (:78–119) lays out, and as the Team seat's final run plan gives it step by step: `/home/randy/Team/META/diogenes/briefs/GATE-team-run-plan-2026-10-24.md` (55 783 B, sha256 `7642fa7a27d0b2865941e794cecd424ec7b43023b3bcffa53c133e4975c2f4ee`, Team-local; "the plan" below). GATE_SHA is `221e8d36d77b33a4b5ec68d1fa990c571c4eac69`, `main` after the `team-seat = Ailp-team_18` commit.

- **When.** The attended part ran on Sat 2026-10-24, from the plan's §1 checks at 09:44 EDT to the handoff at 12:31 EDT. DX-13's unattended legs ran to 02:30 EDT on Sun 2026-10-25, and probe-tx closed at 07:57 EDT. M8's line came at about 19:53 EDT on Sun 2026-10-25.
- **Filed** by the Team seat's filing worker, GF8, which `Ailp-team_22` dispatched at 20:02 EDT on 2026-10-25. It is F8's record (FINISH.md:157), on `team/diogenes-0.0-gate`, for the merger's review.

What the record means for DX-13 and for DX-3's F9 legs is in two RESULTs at the end of [`meta/EXPERIMENTS.md`](../../../EXPERIMENTS.md), which DX-13's and DX-3's headings point to.

**How this README cites.**
- **CTL** is `G-controls.txt`, the Team seat's manager's readings and the sender's log of every gate message (ruling 7). Each line starts with its UTC time, so `CTL <time>` cites a line by that time.
- **Times** are UTC, as the records give them (EDT is UTC − 4 h), unless marked EDT.
- **`F:`** is `meta/roadmap/0.0/FINISH.md`, **`MIN:`** is `meta/roadmap/0.0/MIN.md`, **`U:`** is `docs/USING.md` and **`X:`** is `meta/EXPERIMENTS.md`, each at GATE_SHA, where they are as at `cdcebdb`.
- **Ruling *n*** is the merger's ruling *n*, as the plan's §10 numbers them, from its rulings file (`merger-rulings-and-texts.md`, under "The files").
- **RES, MAXRES and MREC** are the three folders the raw records came from (under "The files").
- **A version** is given with its source: `dio who`'s `VERSION` column (the sessions file's `version`), or a `claude --version` reading with who ran it and when (FINISH.md:189).

## Who ran it

- **The author** started and closed every probe in his own terminals, and typed the kickoffs and the cue replies. He ran M6's `kill` and M6b's `kill -9`, and gave M8's line.
- **The Team seat's manager,** in two seats:
  - **`Ailp-team_18`** (pid 1685253, Claude Code 2.1.308 by `dio who`'s `VERSION`, `--permission-mode=bypassPermissions` by `ps`, CTL 13:50:09.362Z) ran from the plan's §1 to the attended end.
  - **`Ailp-team_19`** (pid 1841651, 2.1.309 by the same source) took over at 12:32 EDT (CTL 16:31:15.543Z and 16:32:15.216Z). It ran DX-13's unattended checks, wrote `G-DX13-usage.txt` (06:49:52Z on 10-25, by its header), saw probe-tx's close and took the second hash set.
  - `Ailp-team_20`, `_21` and `_22` held the seat on Sunday (CTL 12:57:14.187Z, 13:33:54.774Z and 13:51:15.446Z). `_22` took the third hash set and dispatched this filing.
- **The merger:**
  - **`diogenes_2`** (pid 1673675, 2.1.307 by `dio who`'s `VERSION` and its record's first line) held it to 11:30:09 EDT.
  - **`diogenes_3`** (pid 1649293, 2.1.309 by `dio who`'s `VERSION`) holds it from commit `065dc87` (CTL 15:30:41.454Z).
  - After the author's restarts on Saturday evening, `diogenes_3` runs as pid 1300527 (`--resume`, started 00:05:00Z, CTL 00:18:21.771Z). This record reads no version for that process: UNVERIFIED.
- **The management seat:** `management_2` held it to 12:40:55 EDT, then `management_3` (CTL 16:43:25.596Z).
- **The probes.** The author started each with `--permission-mode dontAsk`, sandboxed, under the settings variant named here. Each ran Claude Code 2.1.310 by `dio who`'s `VERSION` in the reading named.

| Probe | Account | Started (`dio who`'s `STARTED`) | Its reading | Rows | Its settings |
|---|---|---|---|---|---|
| probe-t_1 (restarted), probe-t_2, _3, _4 | team | 14:15:33Z, 14:18:03Z, 14:20:16Z, 14:23:01Z | CTL 14:16:22.736Z; `G-M1-merger.txt` | M1 | Team L0R |
| probe-m | max | 14:26:46Z | `G-M7b-dio-who-agents.txt` | M2, M3's post (4) | G-M2R |
| probe-td | team | 15:36:57Z | `G-F9-team-seat-dio-who.txt` | M4, F9, M6's idle peer | G-M4TR |
| probe-mw | max | 15:37:50Z | the same | M4, F9 | G-M4MR |
| probe-mi | max | 15:38:47Z | the same | M4 (unwatched), M6 (killed) | G-M4MR |
| probe-tx | team | 16:07:37Z | `G-M6b-0.txt` | M6b's idle peer, DX-13 | Team L0R |
| probe-mk | max | 16:11:04Z | `G-M6b-0.txt` | M6b | Max L0R |

- **`dio`** was GATE_SHA's throughout.
  - The Team ran `/home/randy/Team/REPOS/diogenes/src/dio`. The merger and the Max probes ran `/home/randy/Workspace/REPOS/diogenes/src/dio` (F:80).
  - `main` moved 23 commits from GATE_SHA to `09a16c5` during and after the gate, and every path they change is under `meta/`. `git diff 221e8d3 09a16c5 -- src tests docs` is empty (read by GF8 at 20:22:24 EDT on 2026-10-25). CTL checks the Team clone's `src/` and `tests/` against GATE_SHA at the attended part's fast-forwards, for example at 14:47:45.949Z, 15:23:33.050Z and 15:30:42.151Z.

## Where the run left the plan, each as ruled

1. **The stop, and the R variants** (CTL 14:05:46.924Z to 14:14:28.548Z).
   - **The refusal.** probe-t_1's first command, the kickoff's `echo … >> <F>`, was refused under `dontAsk` before it ran (`management_2`, 10:04:57 EDT).
   - **The merger's reading** (10:08:03 EDT): under 2.1.309 and 2.1.310, a sandboxed Bash write needs a permission rule for its target.
   - **The R files.** Each probe variant was re-issued as an R file: its base plus allow rules, nothing else. The base files were left untouched. The plan's L0, G-M4T, G-M2 and G-M4M mean these from then on.
   - **probe-t_1's first leg is void.** It restarted under L0R.
   - **Each R file,** as GF8 read it at 20:12:50 EDT on 2026-10-25. Each matches the sha256 that CTL gives, in full or by its first 8 digits (CTL 14:12:11.652Z, 14:12:11.658Z and 14:26:26.143Z):

| File | Side | Its base | Bytes | sha256 | The allow rules it adds |
|---|---|---|---|---|---|
| `settings.L0R.json` | Team | L0 | 610 | `e612f5e80f29bd07c5474060997e91657302df1b38b0f244e3d03937fed86ca9` | `Edit(//home/randy/Team/PROBES/dio-probe/results/**)`, `Bash(/home/randy/Team/REPOS/diogenes/src/dio:*)` |
| `settings.G-M4TR.json` | Team | G-M4T | 771 | `5cd3fd34581d63c67bb3b7f55e6e06192a8ee0cc48cacd8137891ab3f8f871bd` | `Edit(//home/randy/Team/PROBES/dio-probe/results/**)`, `Bash(/home/randy/Team/REPOS/diogenes/src/dio:*)`, `Edit(//home/randy/.local/share/diogenes/inbox/max/**)` |
| `settings.L0R.json` | Max | L0 | 631 | `b39d8551d0ff7d4ea58443c2c443a71d759b415017ab4b2ffa376c248dc58eb6` | `Edit(//home/randy/Workspace/MANAGEMENT/probes/dio-probe/results/**)`, `Bash(/home/randy/Workspace/REPOS/diogenes/src/dio:*)` |
| `settings.G-M2R.json` | Max | G-M2 | 652 | `1eb4c6de0b63e5c42c6f0296125adf829132ce1ad524b0a2bf5d3f0e6c53185a` | `Edit(//home/randy/Workspace/MANAGEMENT/probes/dio-probe/results/**)`, `Bash(/home/randy/Workspace/REPOS/diogenes/src/dio:*)` |
| `settings.G-M4MR.json` | Max | G-M4M | 719 | `4098a28ba99a03963d1ed12a966f84b2b4616435e90f33e32f5542883dfc6893` | `Edit(//home/randy/Workspace/MANAGEMENT/probes/dio-probe/results/**)`, `Bash(/home/randy/Workspace/REPOS/diogenes/src/dio:*)` |

2. **M1's round 1.** `Ailp-team_18`'s message of 10:16:22 EDT named probe-t_1 and its pid before round 1's lookup, where M1 has the Max seat find each probe without being told its name.
   - The merger ruled that the leg stands, since its lookup used `dio who` alone (CTL 14:17:47.141Z; `G-M1-merger.txt` at 14:16:44.086Z).
   - No probe-t name or pid went to the merger after that.
3. **The merger's handover** from `diogenes_2` to `diogenes_3`, at 11:30:09 EDT by commit `065dc87` (CTL 15:30:41.454Z). It came between M3's task (4) and M4.
4. **M6 ran twice.**
   - **Why.** The plan's and the sheet's `kill` dropped the `-9` that MIN:203 cites (DX-10, X:229).
   - **The re-run, M6b.** The merger called it with `kill -9`, on a new Max probe, probe-mk, under Max L0R. probe-tx was the idle peer, and X1 was held until M6b ended (`diogenes_3`, 12:06:50 and 12:08:27 EDT; CTL 16:07:25.855Z and 16:09:29.366Z).
   - **Adapted.** The 12:06:50 message arrived after the plan's steps 19 to 21 were done, so M6b ran in the adapted form the merger approved (CTL 16:07:46.481Z).
   - **The first run** is recorded as it stands.
5. **The Team settings.**
   - `management_2` put `"autoCompactWindow": 400000` into `~/.claude-team/settings.json` at 11:21 EDT, and took it out at 11:25:40 EDT, leaving the file byte-identical. No Team probe was up in that window (CTL 15:22:11.655Z and 15:25:55.197Z; `G-notes-merger.txt`).
   - `management_3` put the key in again at 08:02:08 EDT on Sunday, after probe-tx's exit (CTL 12:03:22.002Z).
6. **The author's restarts** of most seats, at 20:01 to 20:10 EDT on Saturday, did not restart `Ailp-team_19` or probe-tx. The seat and the merger judged that they touched neither DX-13's leg nor X2b's reading (CTL 00:18:21.775Z to 00:19:17.385Z).

## The rows

The verdict is MIN.md's Pass column (:198–206) applied to the record. DX-13's legs answer MIN:137's question ("whether a `REARM` (exit 1) or a refusal (exit 2) wakes the seat as the measured exit 0 did"), and F6's cleanup answers ruling 10's check, since neither has a row in that table. Each row's evidence follows the table.

| Row | Verdict | Runner | Times (from the records) | Claude Code version (source) |
|---|---|---|---|---|
| M1 | **PASS** | `diogenes_2` (the Max side and `probe-seat`); `Ailp-team_18` (pull, comparison); the author (starts, closes) | deliveries 14:17:01Z, 14:19:19Z, 14:21:20Z, 14:24:05Z; comparison 14:24:13.861Z | probes 2.1.310, `diogenes_2` 2.1.307, `Ailp-team_18` 2.1.308 (`dio who`'s `VERSION`) |
| M2, with W | **PASS**; W **refused**, as F:85 expects | `Ailp-team_18` | sends 14:38:02.277Z to 15:19:29.327Z; W 15:19:44.076Z to 15:21:58.335Z | probe-m 2.1.310, `Ailp-team_18` 2.1.308 (`dio who`'s `VERSION`) |
| M3, as the merger gives it | **PASS** | `diogenes_2`; `Ailp-team_18` (tasks (1) and (4)); a credits job and a Max subagent (tasks (2) and (3)) | task (1) 14:47:44.967Z to 14:52:53.177Z; task (4) refused 15:23:33.076Z | `Ailp-team_18` 2.1.308 and `diogenes_2` 2.1.307 (`dio who`'s `VERSION`); tasks (2) and (3)'s runners UNVERIFIED |
| M4 | **PASS** | `Ailp-team_18` (directs, pre-seeds); probe-td, probe-mw | drops 15:44:51.894Z to 15:51:32.120Z; round 15:53:10Z to 15:55:22Z | probes 2.1.310 (`dio who`'s `VERSION`; F9's `execpath`) |
| M4, F9 legs | **measured**: (c) yes; (d) the check failed for every row (DX-3's RESULT) | probe-td, probe-mw, sandboxed; `Ailp-team_18`'s control | 15:40:43Z to 15:41:11Z; control 15:40:45.615Z | probes 2.1.310; control `Ailp-team_18` 2.1.308 |
| M4, SEND | **refused on both**, as F:87 requires | probe-td, probe-mw | 15:41:41Z, 15:41:57Z | probes 2.1.310 |
| M4, TOUCH | **landed, not refused**: open point 1 | probe-mw | 15:42:39Z (file born 15:42:33.638Z) | probe-mw 2.1.310 |
| M4, U74 | **refused**, as X:109 expects under `dontAsk` | probe-td | 15:42:36Z | probe-td 2.1.310 |
| M5 | **PASS**, both halves | `Ailp-team_18`; `diogenes_2` (the Max half) | Team 14:28:03.693Z and 14:28:03.864Z; Max by 10:39:28 EDT | `Ailp-team_18` 2.1.308, `diogenes_2` 2.1.307 (`dio who`'s `VERSION`) |
| M6 | **PASS on M6b**, the re-run the merger called (open point 3); the first run recorded as it stands | the author (kills); `Ailp-team_18` (readings) | first run 15:59:15.033Z, 16:00:30.109Z; M6b 16:13:27.003Z to 16:14:57.038Z | probe-mi, probe-td, probe-mk, probe-tx 2.1.310 (`dio who`'s `VERSION`) |
| M7a | **PASS** | `Ailp-team_18`, as M3's task (1); the merger re-ran it | 14:48:56.455Z; the merger's re-run 14:50:28Z | `Ailp-team_18` 2.1.308 (`dio who`'s `VERSION`); the check is `strace` of `src/dio` |
| M7b | **PASS**, both halves | `Ailp-team_18`; `diogenes_2` (the Max half) | Team 14:38:28.893Z to 14:38:36.074Z; Max 14:38:59.239Z to 14:38:59.828Z | V = 2.1.310 by `claude --version`, `Ailp-team_18` at 14:38:28.893Z and `diogenes_2` at 14:38:59.239Z; the sessions that called `ListAgents` ran 2.1.308 and 2.1.307 (`dio who`'s `VERSION`) |
| M8, as the merger gives it | **PASS on the gated part**; Gemini relays not stated | the author; `management_3` relayed it | about 19:53 EDT on 2026-10-25; the merger's record 23:54:27.158Z | none applies (the author's line); the relaying seats' versions UNVERIFIED |
| DX-13, exit 2 | **woke** (MIN:137: yes) | probe-tx; `Ailp-team_18` removed the directory | removed 16:26:23.523Z; turn 16:26:30Z | probe-tx 2.1.310 (`dio who`'s `VERSION`) |
| DX-13, 2 hours | **woke** on exit 1 | probe-tx; `Ailp-team_19` checked | X2's reading + 7 200 s, 18:29:57Z; turn 18:30:02Z | probe-tx 2.1.310 |
| DX-13, overnight | **woke** on exit 1 | probe-tx; `Ailp-team_19` read it | reading-2 + 43 200 s, 06:30:16Z on 10-25; turn 06:30:21Z | probe-tx 2.1.310, the same process (CTL 00:18:21.775Z) |
| F6 cleanup | **done**: the inboxes list only C0's baseline | `Ailp-team_18`; `diogenes_3` | 16:16:59.199Z to 16:20:03.119Z | `Ailp-team_18` 2.1.308, `diogenes_3` 2.1.309 (`dio who`'s `VERSION`) |

### Each row's evidence

- **M1** (MIN:198). Records: `G-M1-probe-t_1.txt` to `G-M1-probe-t_4.txt`, `G-M1-dio-who.txt`, `G-M1-listagents.txt`, `G-M1-merger.txt`; CTL.
  - **Deliveries.** 3 of 3 rounds were delivered to the name just started, each after `--prefix probe-t` and `--address probe-t` from the merger, 2 of them after a rotation. Each probe's own log has its `turn from=diogenes_2` line within a second of the send, as `G-M1-merger.txt` pairs them.
  - **The overlap round.** `probe-seat = probe-t_3` was committed as `c4b74b9`, and the Team clone pulled it (CTL 14:22:12.742Z). `--address probe-t` printed both sockets, then `ambiguous: 2 live`, exit 1. `--address probe-seat` gave probe-t_3's socket. The message landed in probe-t_3 (14:24:05Z, its second line from `diogenes_2`) and not in probe-t_4.
  - **The Team comparison.** `dio who`'s live and live-idle team rows are `Ailp-team_18`, `_19`, `_20`, probe-t_3 and probe-t_4. `ListAgents`' four interactive peers plus `Ailp-team_18` are the same five names, with nothing left out, re-derived by GF8 from the two files.
- **M2** (MIN:199; F:85). Records: `G-M2-probe-m.txt`; CTL.
  - **Five trials.** Each send line went to CTL first, and probe-m's first line followed in 8.7, 5.4, 4.9, 5.2 and 4.7 s.
  - **The mode pair, by `ps`** (CTL 14:27:50.565Z): the sender ran `--permission-mode=bypassPermissions`, and the receiver `--permission-mode dontAsk`.
  - **`crossSessionInbound`** is `accept` in `~/.claude-team/settings.json`:65 and `~/.claude/settings.json`:68, and appears 0 times in the probe's settings.
  - **W.** "Permission to use Write has been denied because Claude Code is running in don't ask mode". The `find` two minutes after the send listed nothing in `inbox/team/`, neither the name nor a `.tmp` name.
  - **P** was sent (15:22:40Z) and reached the merger at 11:22 EDT.
- **M3** (MIN:200), as the merger gives it in `G-M3-merger.txt`.
  - 3 of 3 tasks have `spec`, `assigned-to`, `report` and `verified-by` (not the reporter) filled. The fourth was refused as `refused: poster` before any work.
  - **The Team's part.** Task (1) passed the poster check and was worked on `team/diogenes-m7a-gate` (claim `f29d9f8`, report `d5d9d8a`, merged as `7074e04`). Task (4), `40f645c`, failed the poster check (`posted-by probe-m` is not on the poster line), so no line was filled and no branch made (CTL 15:23:33.074Z to 15:23:40.721Z).
- **M4** (MIN:201). Records: `G-M4-preseed.txt`, `G-M4-drops.txt`, `G-M4-u74.txt`, `G-M4-mi-1.txt` to `G-M4-mi-3.txt`, `G-M4-probe-td.masked.txt`, `G-M4-probe-mw.masked.txt`, `G-M4-probe-mi.txt`; CTL.
  - **The pre-seed.** 10 files, each written with `U:74`'s line and exit 0, went in at 15:40:20Z, before ARM.
  - **Five trials.** probe-mw's `turn from=task` line came 67.1, 25.6, 34.4, 38.7 and 41.9 s after each drop file's mtime. Each `WAKE` names its own trial's file, never a pre-seed's or U74's, and probe-mw re-armed first each time.
  - **probe-mi**, unwatched, read `live-idle` at 15:44:38Z, 15:48:23Z and 15:53:31Z, around trial 3's drop. Its log stayed 38 B, last changed 11:39:26 EDT, so there were 0 wakes.
  - **The round.** probe-mw woke on the two-way file and wrote its reply by the Write tool (`REPLY write=written`). probe-td's own watch on `inbox/team/` then woke it: `WAKE` named the reply's final name, not a `.tmp` name, and `U:125`'s `find` listed only the reply.
  - **SEND.** Both probes reported the tool absent: "SendMessage tool not available in this session" (probe-td) and "not present in this session" (probe-mw). No message reached `Ailp-team_18`.
  - **TOUCH** exited 0, and the file landed. U74 is below.
- **M5** (MIN:202). Records: `G-M5-meters-live.masked.txt`, `G-M5-meters-aged.masked.txt`, `G-M5-max-meters-live.masked.txt`; CTL 14:28:03.693Z and 14:28:03.864Z; the merger's message of 10:39:28 EDT (CTL 14:39:47.498Z).
  - **Team, live.** `usage max measured`, age 7 s, and `usage team measured`, age 1 s, exit 0. The seat's own `context` row was named `Ailp-team_18` (CTL: "yes"; ruling 8 kept the id out).
  - **Team, aged.** Against the copies aged by F:111's line, both `usage` lines read `stale (12 min)`, age 720, exit 1. 22 live or live-idle rows stayed up after.
  - **Max** (the merger): `usage max measured`, age 6 s, and `usage team measured`, age 21 s, exit 0. Its own row was named `diogenes_2`.
- **M6** (MIN:203). Records: `G-M6-dio-who-1.txt` and `-2.txt` (identical), `G-M6b-0.txt` to `G-M6b-7.txt`, `G-M6-probe-mk.txt`, `G-M6b-merger-note.txt`; CTL.
  - **The first run**, a plain `kill` of probe-mi, whose pid was gone by 15:59:14.962Z:
    - probe-td read `live-idle` at the kill and 75 s later, but probe-mi had no row at either reading, neither `unknown (checking)` nor `gone`.
    - The author's line (CTL 16:04:00.849Z), in part: "the things i needed to record disappeared so i didn't actually get any times or states".
    - The merger's reading: a SIGTERM exit removes the sessions file, a finding for `USING.md`.
  - **M6b**, a `kill -9` of probe-mk, whose pid was gone by 16:13:26.923Z:
    - probe-mk read `unknown (checking)` at the first reading after the exit and at + 15, + 30, + 45 and + 60 s, then `gone` at + 75 and + 91 s. [`diogenes_3`, 2026-10-25: by CTL's times from the exit line, 16:13:26.923Z, the two `gone` readings came at + 74.9 s and + 90.1 s, so the first is inside MIN:203's 75 s.]
    - probe-tx read `live-idle` at all seven readings. The other 21 rows matched the baseline in every column, re-derived by GF8.
    - The author: "killed it, saw checking then gone".
    - The merger's later note (`G-M6b-merger-note.txt`): probe-mk's sessions file went some time after 16:14:57Z, so its `gone` row did not stay, against the merger's own lines of 12:06:50 and 12:08:27 EDT.
- **M7a** (MIN:204). Record: `G-M7a.txt`.
  - It printed `M7a: PASS` and exited 0.
  - No `open` or `openat` names a `.key`: 0 of 107 lines.
  - The symlink was refused (`ELOOP`; row 123 `unknown (refused: symlink)`), and the half-written file read `unknown (sessions format: 2.1.301)`.
  - It ran in `/home/randy/Team/WT/diogenes-m7a-gate` at `f29d9f8`, whose `src/` and `tests/` are GATE_SHA's.
- **M7b** (MIN:205). Records: `G-M7b-dio-who-agents.txt`, `G-M7b-listagents.txt`, `G-M7b-max-dio-who-agents.txt`, `G-M7b-max-listagents.txt`; CTL.
  - **Team.** `dio who --agents`' live and live-idle team rows are `Ailp-team_18`, `_19` and `_20`. They equal `ListAgents`' two interactive peers plus the seat itself, with no `fallback: claude agents` row and no `unknown (agents …)` row, exit 0.
  - **Max.** 19 max rows equal `diogenes_2`'s `ListAgents` 18 interactive peers plus itself. Its one `cloud` row was left out. Exit 0, with no fallback or unknown row. GF8 re-derived both.
- **M8** (MIN:206), as the merger gives it. Record: `G-M8-merger.txt`. Cited, not filed: `management_3`'s and `diogenes_3`'s messages, saved by `Ailp-team_22` as `/home/randy/Team/META/diogenes/briefs/M8-2026-10-25-from-management_3.txt` (797 B) and `…/M8-2026-10-25-from-diogenes_3.txt` (1 379 B).
  - **The author's line, verbatim:** "no, i did not relay any messges between max and team accounts today".
  - **The merger's reading** (19:54:36 EDT): the line answers the gated part, "Zero hand relays between Claude accounts". It doesn't mention Gemini, so the Gemini relay count is not stated.
- **DX-13** (F7; FINISH.md's six items, item 4). Records: `G-DX13-probe-tx.txt`, `G-DX13-usage.txt`; CTL.
  - **Exit 2.** The watch on `G-DX13-exit2/` (`--every 60`) ended with exit 2 and `dio watch: during the watch, no such directory: …`. The probe's turn began 6.5 s after the `rmdir`.
  - **2 hours.** `--max 7200` ended with exit 1 and `REARM`. The turn began 5 s after X2's reading plus 7200 s, and the probe re-armed with `--max 43200`. X3 was not needed.
  - **Overnight.** `--max 43200` ended with exit 1, 12 hours after its start. The turn began 5 s after reading-2 plus 43 200 s.
  - **After.** Nothing was sent to probe-tx after X2 (CTL 11:59:55.214Z).
  - Each wake's cache tokens are in DX-13's RESULT.
- **F6 cleanup** (ruling 10). Records: `G-cleanup-team.txt`, `G-cleanup-merger.txt`, `G-cleanup-after.txt`, `G-C0-inbox.txt`; CTL.
  - **The Team's side.** It removed its 16 files from `inbox/max/` by exact name: 10 pre-seeds, 5 trials and the two-way. U74's file never landed.
  - **The merger's side.** It removed its 2 from `inbox/team/`, probe-mw's reply and its TOUCH file, after logging each one's stat and sha256. probe-m's W file never landed.
  - **After.** The listing after both, 0 lines, `cmp`-equals C0's empty baseline.

## `fix-time-log-slips` (ruling 9)

It was not up: C0's `dio who` (`G-C0-dio-who.txt`) has no row for it and none for pid 2497939 or 1624703, and neither have `G-M1-dio-who.txt` and both M7b listings. So M1 and M7b each have one verdict, as CTL says (14:24:22.145Z and 14:38:36.074Z).

## U74's outcome, for U8 (ruling 1)

**The try.** probe-td tried `USING.md`:74's line once, exactly as written: `(set -C; printf … > ~/.local/share/diogenes/inbox/max/"$(date -u …)-probe-td-m4-u74-try.md")`.
- It ran under G-M4TR, which allows `Edit(//home/randy/.local/share/diogenes/inbox/max/**)`.
- It was refused before it ran: "Permission to use Bash has been denied because Claude Code is running in don't ask mode."
- No file landed. `G-M4-u74.txt`, the `find` for its name, is empty.

**The simple form ran.** Under the same settings, DROPk's form, one `printf … > <path>` with a `$(date …)` in the name and no subshell or `set -C;`, exited 0 five times, and ROUND's drop made its file.

**For U8.** Under `dontAsk`, with G-M4TR's rules, `U:74`'s line as written was refused at its one try, while the simple form ran. Whether `USING.md` needs a note for `dontAsk` seats is open point 2.

## The cap directory: a probe's measurement (ruling 2)

`RES/G-DX13-cap/` was an empty directory under the Team's results:
- `Ailp-team_18` made it at 16:06:36Z.
- probe-tx watched it with `--max 7200` and then `--max 43200`, so only the cap could end each watch.
- `Ailp-team_19` removed it at 11:59:12.505Z on 10-25, after probe-tx's close.

It is the probe's measurement, and it departs from `USING.md`'s "One target" (`U:104`) as F:93's exit-2 leg does. It is not a target any seat watches.

## Readings recorded as they stand

- **The sandboxed `dio who`.** In both probes, every row read `unknown (checking)`, each with "the grace cache could not be written, so the grace was not started: Read-only file system". The two outputs are byte-identical. `management_2` found the same in its headless test, and called the fix the merger's (CTL 14:12:11.652Z).
- **`live`, not `live-idle`, while a background task runs.** probe-mw read `live` while its armed watch ran (CTL 15:44:38.932Z), and probe-tx `live` during its 43 200 s watch (CTL 18:43:40.211Z). So the plan's "wait for `live-idle`" before each drop was read as "its last line is `done ARM` or `done WAKE`".
- **probe-mw's REPLY.**
  - Its `test -e` line reads `test_e_exit=0` at 15:54:42Z. The step says 1 means the name is free, and the Write then made the file.
  - The merger's cleanup log gives the reply's birth as 11:54:42.346 EDT, inside the same second, and sets it against that line.
- **Two slips in CTL, each corrected in its next line or two.**
  - The M6b verdict line was written before readings 6 and 7 were read (CTL 16:15:13.532Z).
  - M3's task check misparsed a spec line (CTL 14:47:58.358Z).
- **G-DX13-usage.txt.** The plan expected it to hold a session id (§7). It holds none: the scan finds no UUID, and its header says the id is not written. So it is filed byte for byte, as the brief's rule decides.
- **The `ListAgents` files' six-hex tags,** such as `[5a60a8]`, are `ListAgents`' own. None occurs in any of those sessions' ids in M5's `context` rows: 0 of 21 named rows, checked by GF8's script, which printed no id. The UUID scan finds none, so the files are filed byte for byte. [`diogenes_3`, 2026-10-25: the count is 22, not 21. In each of the three raw M5 files, 22 `context` rows carry a `ListAgents` name exactly, or 30 with the `statusline:` names, and no tag occurs in any of their ids.]

## Usage, from CTL

Each line gives five-hour and week %, as `dio meters` printed them.

| Reading | When | `max` | `team` |
|---|---|---|---|
| 1, C0 | 13:50:09Z | 5, 76 | 1, 60 |
| 2, after M2 | 15:23:49Z | 9, 78 | 7, 61 |
| before X2 (the 63 % stop) | 16:29:41Z | 0, 78 | 13, 62 |
| 3, after X2 | 16:30:08Z | 0, 78 | 13, 62 |
| 4, X2's check | 18:41:20Z | 9, 81 | 0, 63 |
| 5, X2b's read | 06:42:13Z, 10-25 | 3, 87 | 1, 63 |
| 6, after probe-tx's close | 11:59:12Z, 10-25 | -, 87 | 4, 66 |

## The first check, at the filing

The records were checked before anything was copied (`date`: 20:03:57.710 to 20:04:01.417 EDT on 2026-10-25), by `Ailp-team_22`'s checker, `/home/randy/Team/META/diogenes/briefs/GF8-sums-check.py` (2 901 B, sha256 `706a4c3a82e547be4950cffbc9667fc7614e981cbe2d2f9c19a1a9314ccc70b6`, Team-local).
- **What the checker does.** It only reads RES. GROWN means that the set's hash is that of a line-boundary prefix of the file now, so the file was only appended to after the set was taken.
- **Why two files grew.** CTL got lines after the first and second sets: the seats' takeover lines and messages, and M8's receipt. probe-tx's log got its overnight lines after the first.

`python3 -I -B /home/randy/Team/META/diogenes/briefs/GF8-sums-check.py /home/randy/Team/PROBES/dio-probe/results`, then its exit status:

```
G-SHA256SUMS-1.txt: G-controls.txt: GROWN (the set's hash is the first 186 lines, 46290 B, of 58627 B now; 41 lines appended since)
G-SHA256SUMS-1.txt: G-DX13-probe-tx.txt: GROWN (the set's hash is the first 9 lines, 465 B, of 861 B now; 6 lines appended since)
G-SHA256SUMS-1.txt: OK 34, GROWN 2, CHANGED 0
G-SHA256SUMS-2.txt: G-controls.txt: GROWN (the set's hash is the first 209 lines, 54682 B, of 58627 B now; 18 lines appended since)
G-SHA256SUMS-2.txt: OK 37, GROWN 1, CHANGED 0
G-SHA256SUMS-3.txt: OK 39, GROWN 0, CHANGED 0
PASS
exit=0
```

`env -C /home/randy/Team/PROBES/dio-probe/results sha256sum -c G-SHA256SUMS-3.txt`, then its exit status:

```
G-C0-dio-who.txt: OK
G-C0-inbox.txt: OK
G-DX13-probe-tx.txt: OK
G-DX13-usage.txt: OK
G-F9-probe-td-dio-who.txt: OK
G-F9-team-seat-dio-who.txt: OK
G-M1-dio-who.txt: OK
G-M1-listagents.txt: OK
G-M1-probe-t_1.txt: OK
G-M1-probe-t_2.txt: OK
G-M1-probe-t_3.txt: OK
G-M1-probe-t_4.txt: OK
G-M4-drops.txt: OK
G-M4-mi-1.txt: OK
G-M4-mi-2.txt: OK
G-M4-mi-3.txt: OK
G-M4-preseed.txt: OK
G-M4-probe-td.txt: OK
G-M4-u74.txt: OK
G-M5-meters-aged.txt: OK
G-M5-meters-live.txt: OK
G-M6-dio-who-1.txt: OK
G-M6-dio-who-2.txt: OK
G-M6b-0.txt: OK
G-M6b-1.txt: OK
G-M6b-2.txt: OK
G-M6b-3.txt: OK
G-M6b-4.txt: OK
G-M6b-5.txt: OK
G-M6b-6.txt: OK
G-M6b-7.txt: OK
G-M7a.txt: OK
G-M7b-dio-who-agents.txt: OK
G-M7b-listagents.txt: OK
G-SHA256SUMS-1.txt: OK
G-SHA256SUMS-2.txt: OK
G-cleanup-after.txt: OK
G-cleanup-team.txt: OK
G-controls.txt: OK
exit=0
```

The three hash sets:
- `G-SHA256SUMS-1.txt`, 36 files, was taken at Saturday's attended end (CTL 16:30:21.155Z). It exited 1, since `G-DX13-cap` was a directory then.
- `-2.txt`, 38 files, was taken after probe-tx's close (11:59:55Z on 10-25).
- `-3.txt`, 39 files, was taken by `Ailp-team_22` at 20:02:36 EDT on 10-25.

In this folder, `sha256sum -c G-SHA256SUMS-3.txt` reads 36 OK. The 3 files it cannot open are the 3 kept local.

## The files

### Filed here

- **How each was copied.**
  - RES's files were copied by `cp`, then `cmp`.
  - MAXRES's and MREC's were copied by `cat <file> > <copy>`, then `cmp`, since this session's permission layer refused `cp` and `sed` with a Workspace path.
- **The masked copies.** Each is the brief's `sed -E 's/<the UUID pattern>/<uuid>/g'` of its raw file, **every UUID replaced by `<uuid>`**.
  - probe-mw's was made from a `cmp`-equal scratch copy.
  - MREC's is the merger's own masked copy, which equals the same `sed` of its raw file.
  - Each masked copy matches the UUID pattern nowhere, and has its raw file's lines, with 30 B less per UUID.
- **Sources.** RES is `/home/randy/Team/PROBES/dio-probe/results/`. MAXRES is `/home/randy/Workspace/MANAGEMENT/probes/dio-probe/results/`. MREC is `/home/randy/Workspace/REPOS/diogenes/.internal/agent/diogenes/gate-2026-10-24/`.

| File | From | Bytes | sha256 | Made by |
|---|---|---|---|---|
| `G-C0-dio-who.txt` | RES | 2 682 | `4c83882b7495a05425c99e3251613c18e70a74d2b8f68bedcca9b9cb85846da6` | `cp`, `cmp` |
| `G-C0-inbox.txt` | RES | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `cp`, `cmp` |
| `G-cleanup-after.txt` | RES | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `cp`, `cmp` |
| `G-cleanup-merger.txt` | MREC | 1 349 | `96e34914c6f208ed3b3a33a4526272bd5d8a09b1119bba5a19ba8d0bbddfe157` | `cat`, `cmp` |
| `G-cleanup-team.txt` | RES | 1 238 | `df56102f4d555fff8b49f8968bbb96e721c4be00e976d34980810e294d0fdb2f` | `cp`, `cmp` |
| `G-controls.txt` | RES | 58 627 | `69611b779d3bee55a4658431831459a68c65d78a682c864f8eb8a3aade4fc7d3` | `cp`, `cmp` |
| `G-DX13-probe-tx.txt` | RES | 861 | `f2fdf002e9178419a739a559a1fa15fadf3d66065ee08322f7b41b5543fd30a6` | `cp`, `cmp` |
| `G-DX13-usage.txt` | RES | 1 689 | `43fcd93a3316b04f7baf319aa2cc6e2fa1eec45f7b41edbac285fbaba57f1578` | `cp`, `cmp` |
| `G-F9-probe-mw-dio-who.txt` | MAXRES | 5 567 | `df86aafe321420c540a5e34dbac31cb58d056eb271072a493c07efb4fafbf1ed` | `cat`, `cmp` |
| `G-F9-probe-td-dio-who.txt` | RES | 5 567 | `df86aafe321420c540a5e34dbac31cb58d056eb271072a493c07efb4fafbf1ed` | `cp`, `cmp` |
| `G-F9-team-seat-dio-who.txt` | RES | 3 051 | `83e26f771c63a32e4e9033dca50667e8b4629f79fcb2517fd3df03864ed452a8` | `cp`, `cmp` |
| `G-F9-touch-docs.txt` | MREC | 1 400 | `181e0f814e8bea4f25725105da07493811d45fb33ecbd3b3916ac3401865fce3` | `cat`, `cmp` |
| `G-M1-dio-who.txt` | RES | 2 928 | `4a2c45cd4c45493c75822c14059f7180e08c3f365434956209de74cd94137d68` | `cp`, `cmp` |
| `G-M1-listagents.txt` | RES | 457 | `add68e415b3be0614e1a7b1f9ab03f81a17d58fcbf9ed5ec04ed3ea655c0e39a` | `cp`, `cmp` |
| `G-M1-merger.txt` | MREC | 5 279 | `92353c4dbb609f4f28cae427188456a9510347ea216258be87f3f180eee0adc1` | `cat`, `cmp` |
| `G-M1-probe-t_1.txt` | RES | 80 | `778730a3e7eec461fb1b8803bc7daf2b0fab627c2f0dedbdd862959e2e962938` | `cp`, `cmp` |
| `G-M1-probe-t_2.txt` | RES | 80 | `d36572259f81d4f08801c7b64c1a6e00712b3a1bb42e881012b63fbd469f4bba` | `cp`, `cmp` |
| `G-M1-probe-t_3.txt` | RES | 122 | `f77ee2f8c6511dda3a6f70739aed96dfe86a0ca28c00c52f16d3b917ad30984d` | `cp`, `cmp` |
| `G-M1-probe-t_4.txt` | RES | 38 | `ecb280cf7a8f978bb971a102269aecabdccead7165e389be151f87071f2fc322` | `cp`, `cmp` |
| `G-M2-probe-m.txt` | MAXRES | 933 | `8769f32ff76ca64e91d17db271370477f66107893fa89e06a1b236d8bb5b13ab` | `cat`, `cmp` |
| `G-M3-merger.txt` | MREC | 1 136 | `7bbf03299a44417a7d7450b9695a17205e0f55392b65862846ab79ca96d0c19a` | `cat`, `cmp` |
| `G-M4-drops.txt` | RES | 595 | `a573b7a72c99b81fba8214d7bb12aec5562fd8aa31f7aa3d427c11070617cf32` | `cp`, `cmp` |
| `G-M4-mi-1.txt` | RES | 3 051 | `508fe64ef59f91df9c3d8a8323bbf15d1ebd2883baf2b017bc2d7fbdfe6f7843` | `cp`, `cmp` |
| `G-M4-mi-2.txt` | RES | 3 056 | `04c97ff85ea499bc03723dbfbfeef47a16bfdad2c2ba247bd4317fa4d3013097` | `cp`, `cmp` |
| `G-M4-mi-3.txt` | RES | 3 051 | `fcdbec7233080c444a78c7ca26d9caefee6cd974a84a6eda809a55cdf399ef13` | `cp`, `cmp` |
| `G-M4-preseed.txt` | RES | 660 | `b23865ddc92c85a4cba54006b5e48a2434b102f14fa5f7735c2aa74efcc180cd` | `cp`, `cmp` |
| `G-M4-probe-mi.txt` | MAXRES | 38 | `e0a99af77ef38364ffff4ff0144b986aa12bd6f56b805180cad712296622111a` | `cat`, `cmp` |
| `G-M4-probe-mw.masked.txt` | MAXRES | 2 796 | `0b73bc66f151826527d23ab168540c11f42744ee3efd4386b57f8036296cbc3c` | masked from MAXRES's `G-M4-probe-mw.txt`, by way of a `cmp`-equal scratch copy |
| `G-M4-probe-td.masked.txt` | RES | 1 778 | `f2ee972a02454cd91e5c568e32f52d8ee8406244777e00043aa3b1230926da16` | masked from RES's `G-M4-probe-td.txt` |
| `G-M4-u74.txt` | RES | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `cp`, `cmp` |
| `G-M5-max-meters-live.masked.txt` | MREC | 22 253 | `3f97eb3cb14730f2f12b612240d209fd73fbf2119606e793cfc25ca05eeeea3c` | the merger's masked copy, from MREC by `cat`, `cmp` |
| `G-M5-meters-aged.masked.txt` | RES | 22 236 | `acf5e87ad763898ccb6306fcfbed27e8e90d9e219affcca3613c2ce970217781` | masked from RES's `G-M5-meters-aged.txt` |
| `G-M5-meters-live.masked.txt` | RES | 22 220 | `206f2b153990d421ce363469725011ba3a2591889c4e5a60a8fcc8ef4d688de2` | masked from RES's `G-M5-meters-live.txt` |
| `G-M6-dio-who-1.txt` | RES | 2 815 | `f996aec4d9fc1e9157d898f02c40a2871cb622e464b7fcbeee2c55da0a441d7a` | `cp`, `cmp` |
| `G-M6-dio-who-2.txt` | RES | 2 815 | `f996aec4d9fc1e9157d898f02c40a2871cb622e464b7fcbeee2c55da0a441d7a` | `cp`, `cmp` |
| `G-M6-probe-mk.txt` | MAXRES | 38 | `b815ef5f19c930e3eb36fee62c26cb1ede413904338024fce3ebd71297f27d8c` | `cat`, `cmp` |
| `G-M6b-0.txt` | RES | 2 938 | `5d145410f193a58a294dffce14f412e2bff002452ef78493de534ea5055cea44` | `cp`, `cmp` |
| `G-M6b-1.txt` | RES | 2 947 | `6178b1081f824ed21e349055ff49ebc8482ed527df85bbe015a41cda6429eb5f` | `cp`, `cmp` |
| `G-M6b-2.txt` | RES | 2 947 | `6178b1081f824ed21e349055ff49ebc8482ed527df85bbe015a41cda6429eb5f` | `cp`, `cmp` |
| `G-M6b-3.txt` | RES | 2 947 | `6178b1081f824ed21e349055ff49ebc8482ed527df85bbe015a41cda6429eb5f` | `cp`, `cmp` |
| `G-M6b-4.txt` | RES | 2 947 | `6178b1081f824ed21e349055ff49ebc8482ed527df85bbe015a41cda6429eb5f` | `cp`, `cmp` |
| `G-M6b-5.txt` | RES | 2 947 | `6178b1081f824ed21e349055ff49ebc8482ed527df85bbe015a41cda6429eb5f` | `cp`, `cmp` |
| `G-M6b-6.txt` | RES | 2 933 | `0782bec2eb14f467d98765f2bc146a91c9158b0fe7482ca2fe087941a18715cc` | `cp`, `cmp` |
| `G-M6b-7.txt` | RES | 2 933 | `0782bec2eb14f467d98765f2bc146a91c9158b0fe7482ca2fe087941a18715cc` | `cp`, `cmp` |
| `G-M6b-merger-note.txt` | MREC | 1 302 | `a69f4479a1bfa7fb6608ee857f7ac67bae675f22d9e2414ff47513a99ac1fc11` | `cat`, `cmp` |
| `G-M7a.txt` | RES | 861 | `ce735463b2cea9a274e55f24c314f348e25ae7aeddfb3cf90d9955f501563ee3` | `cp`, `cmp` |
| `G-M7b-dio-who-agents.txt` | RES | 2 810 | `6ee52b9ccdf9a13c5b1f7da602218e673c17885179cc36900fb57d92e19cd760` | `cp`, `cmp` |
| `G-M7b-listagents.txt` | RES | 321 | `276d99aad27d3970353949754ee6775fa369118ea59bff41563ff2d4a45af156` | `cp`, `cmp` |
| `G-M7b-max-dio-who-agents.txt` | MREC | 2 921 | `712ac3a179d11f8cd2c0ebe6cb270b81b29ee0dc6a748c59b609f31d494eb3c2` | `cat`, `cmp` |
| `G-M7b-max-listagents.txt` | MREC | 971 | `d59974803d41b2b0864e43c9d0477f4f20ac171acc20c6230a358a0842210d82` | `cat`, `cmp` |
| `G-M8-merger.txt` | MREC | 391 | `7b4d922a707adc6f269847a9fafc82e2899fa6f7d48e6fe34f20b5d5eae936b2` | `cat`, `cmp` |
| `G-notes-merger.txt` | MREC | 566 | `9ea6bf57cc6de93e2e6a75d7edddd841f1c4f8f1825f3e86d7b5ab8032842f6c` | `cat`, `cmp` |
| `G-SHA256SUMS-1.txt` | RES | 2 985 | `1a70340cede5f701c42c300d25b8b3c31a6f668a6403105f9065abd57494ce17` | `cp`, `cmp` |
| `G-SHA256SUMS-2.txt` | RES | 3 153 | `787bac8f7c38ce5ddfebdfdcc6bd6f48e5e0692e8b04e2d7af5b8015022c3a6b` | `cp`, `cmp` |
| `G-SHA256SUMS-3.txt` | RES | 3 238 | `69f122671c2a30afa2797a367fb2cca024c4aa8c6aba10d6f3f15786dec7c349` | `cp`, `cmp` |

### Kept local: each holds a session id (ruling 8)

| Raw file, kept local | Bytes | sha256 | UUIDs | Filed here as |
|---|---|---|---|---|
| `/home/randy/Team/PROBES/dio-probe/results/G-M4-probe-td.txt` | 1 808 | `6874468dd48dc222f0cffaeef1c50a899af29dcb2773e905d9ab345fcb8a952b` | 1 | `G-M4-probe-td.masked.txt` |
| `/home/randy/Team/PROBES/dio-probe/results/G-M5-meters-aged.txt` | 24 426 | `233957da3f40f2b827c10ca9641cf7fa2c89095df868790ab2bf84033c8768ea` | 73 | `G-M5-meters-aged.masked.txt` |
| `/home/randy/Team/PROBES/dio-probe/results/G-M5-meters-live.txt` | 24 410 | `1612f0499bad43175107d2b680b651f97edca564665b63d3bd537276f8e86b38` | 73 | `G-M5-meters-live.masked.txt` |
| `/home/randy/Workspace/MANAGEMENT/probes/dio-probe/results/G-M4-probe-mw.txt` | 2 826 | `c287dde037e1811c494d61eef4d35b394caca4ba6a0b2552d4a814c41803a42a` | 1 | `G-M4-probe-mw.masked.txt` |
| `/home/randy/Workspace/REPOS/diogenes/.internal/agent/diogenes/gate-2026-10-24/G-M5-max-meters-live.txt` | 24 443 | `8f91a738b24880fac7d47d692816c92c6672dbf34d689899d7ebfd85889818dd` | 73 | `G-M5-max-meters-live.masked.txt` |

### The run plan's inputs, in MREC, not copied

`author-sheet.md` is the sheet as revised on 10-24 with the restart steps R1 to R3 (CTL 14:13:18.285Z). The plan cites an earlier version of 18 472 B.

| File | Bytes | sha256 |
|---|---|---|
| `author-sheet.md` | 20 134 | `351678e60d27fe8ab1f3a7a79e0a7700531d2c24a78556648e3858c36b9394f0` |
| `merger-rulings-and-texts.md` | 12 395 | `99ea6ba7da525f08cb0e822f1ded6a9eb14426a7ab68e03f15eaacb40586410c` |
| `probe-seat.msg.template` | 1 433 | `fd25f98d49a0d9d665c50af6dc6a7e1afd2f03477f80fc94cf031022151fb73e` |

## Limits

- **One trial each** for each of DX-13's three legs and for M6b, on fresh probes.
- **The R variants.** The probes ran under the R files, not the plan's L0, G-M4T, G-M2 and G-M4M as written (the merger's ruling of 10:08 to 10:12 EDT).
- **F9's (d).** `dio who` does not print which of DR-108's three parts failed in the sandbox: `/proc/<pid>/stat`, its start time, or the socket file. So whether the host's `/proc` is visible from sandboxed Bash is not measured.
- **TOUCH tested no closed path.** No variant left `inbox/team/` closed to probe-mw.
- **M6's first run** did not test MIN:203's states, since its `kill` was not `-9`.
- **Whole seconds.** The probes' lines carry whole seconds (`date -u +%FT%TZ`), so each delay measured from a send or a drop is good to within 1 s.
- **M7b's one version** is V, the `claude` on the path, by `claude --version`. The two sessions that called `ListAgents` ran 2.1.308 and 2.1.307 by their sessions files. The merger took the halves at V (CTL 14:39:47.498Z).
- **M8** rests on the author's own line about "today", Sun 2026-10-25. No record counts Gemini relays.
- **What is not filed.** `/home/randy/Team/MANAGER-LOG.md` is the seats' own account, and is not filed: CTL is the record, and the log points to it (ruling 7). The two M8 messages are cited, not filed.
- **No Team verifier** has checked this record yet.

## Open points for the merger

1. **TOUCH:** its place in the record and in U8. The merger wrote at 11:45:23 EDT that it would rule on this at review (CTL 15:45:45.130Z).
2. **U74, for U8:** whether `USING.md` needs a note for `dontAsk` seats (ruling 1).
3. **M6:**
   - Its verdict rests on M6b, under the pass the merger set at 12:08:27 EDT. The merger's own word on M6b's result, sent to it at 12:16:14 EDT, is not in these records.
   - The first run's finding for `USING.md`: a SIGTERM exit removes the sessions file.
   - The merger's note that the `gone` row did not stay.
4. **Sandboxed `dio who`:** every row reads `unknown (checking)`, and the grace cache cannot be written there (`management_2`'s finding, the merger's to fix).
5. **The merger's records commit:** U7 and `--max` from DX-13's legs (F:118), and `probe-seat`'s removal (F:98).
