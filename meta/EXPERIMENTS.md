# Diogenes: experiments

Drafted 2026-10-10, revised the same day. Feasibility probes, ordered by what they unblock. Each gives its hypothesis, the exact commands or settings, the expected result, what each outcome decides, its cost, and its prerequisites. "Today" means runnable now on this machine with one account; "second account" means it needs the Team seat. Record every result as a Diogenes fact once the store exists, or in `meta/research/done/` before then, with the clock time and the Claude Code version.

**Safety rules for every probe** [c1 C-5, C-12]: use throwaway directories and `--name` for probe sessions; never run a probe in a working seat; put probe settings in the probe project's `.claude/settings.json`, never in user settings, so a working seat's status line, hooks and guards are never replaced; never touch the system Redis; never `kill -9` a pid you have not checked by name; write probe logs to a private directory (`umask 077`) and redact anything with `TOKEN` in its name.

**Already measured (2026-10-10 12:48, `nitpick-libs_18`, Claude Code 2.1.296, the workbench's sandbox settings):** M1 Unix sockets refused in sandboxed Bash; M2 loopback TCP works within one call; M3 loopback TCP across two calls fails, each call has a private network namespace; M4 SQLite 3.45.1 FTS5 and cross-connection `PRAGMA data_version` work; M5 Redis 7.0.15 stream consumer groups and keyspace notifications work over loopback within one call. The experiments below that these answer are marked **DONE (measured 2026-10-10)**.

## Before cycle 0.0

**DX-1 (revised). Two processes in different namespaces can take one SQLite lease by compare-and-set without error, with exactly one winner per contested round.**
- **RESULT, the sandbox-to-sandbox leg: PASS (measured 2026-10-10 15:31 by `nitpick-libs_18`; files in `research/done/dx1-probe-2026-10-10/`).**
  - **Setup:** three processes, each in its own sandboxed Bash call, with distinct mount, PID and network namespaces: writers A and B, and a referee that freed the lease twice a second. They shared one WAL-mode file under `$TMPDIR`, on SQLite 3.45.1 through Python's `sqlite3`, with `BEGIN IMMEDIATE` and `busy_timeout` 5000.
  - **Free-running phase** (1 ms TTL): A made 1 789 takes and won 1 279; B made 6 696 and won 2 411.
  - **Contested phase** (60 s TTL): A won 10 of 7 860 attempts and B 27 of 8 197, over 37 lease rounds (36 resets plus the initial one).
  - **Result:**
    - **No round had more than one winner;**
    - the fence (3 727) equals the sum of all wins, so no update was lost or doubled;
    - 0 errors and 0 busy timeouts;
    - `PRAGMA integrity_check` returned `ok`.
  - **Still open:** the host-to-sandbox leg, with one writer outside any sandbox, which the commands below run from the author's terminal. It rests on the same kernel locks, over a bind mount of the same inode.
- Hypothesis: SQLite 3.45.1 in WAL mode serialises `BEGIN IMMEDIATE` writers across processes, and the same holds between a writer on the host and a writer inside a sandboxed Bash call, which M3 shows runs in its own namespaces, on a directory in `allowWrite`.
- Commands (outside the sandbox, in the author's terminal):
  ```sh
  mkdir -p ~/.local/share/diogenes-probe && cd ~/.local/share/diogenes-probe
  python3 -c 'import sqlite3;print("python sqlite", sqlite3.sqlite_version)'   # dio uses this library, not the CLI
  sqlite3 probe.db 'PRAGMA journal_mode=wal; CREATE TABLE lease(id TEXT PRIMARY KEY, holder TEXT, fence INTEGER NOT NULL DEFAULT 0, expires_at REAL);'
  sqlite3 probe.db "INSERT INTO lease VALUES('t', NULL, 0, 0);"
  cat > take.py <<'EOF'
  import os, sqlite3, sys, time
  me, mode, seconds = sys.argv[1], sys.argv[2], float(sys.argv[3])
  wins = rounds = 0; end = time.time() + seconds
  def take(ttl):
      c = sqlite3.connect('probe.db', timeout=5, isolation_level=None)
      c.execute('PRAGMA busy_timeout=5000'); c.execute('BEGIN IMMEDIATE')
      r = c.execute("UPDATE lease SET holder=?, fence=fence+1, expires_at=? WHERE id='t' AND (holder IS NULL OR expires_at<?)",
                    (me, time.time()+ttl, time.time())).rowcount
      c.execute('COMMIT'); c.close(); return r
  if mode == 'free':                       # free-running: short TTL, as many takes as possible
      while time.time() < end: wins += take(0.001); rounds += 1
  else:                                    # contested: wait for a shared start file per round, one take each
      while time.time() < end:
          rounds += 1
          while not os.path.exists(f'go.{rounds}'):
              if time.time() > end: break
              time.sleep(0.005)
          wins += take(60)
  print(me, mode, 'rounds', rounds, 'wins', wins)
  EOF
  cat > rounds.sh <<'EOF'
  #!/bin/sh
  # referee: opens one round per second, clearing the lease between rounds
  i=1; end=$(( $(date +%s) + $1 ))
  while [ "$(date +%s)" -lt "$end" ]; do
    sqlite3 probe.db "UPDATE lease SET holder=NULL, expires_at=0 WHERE id='t';"
    touch "go.$i"; sleep 1; i=$((i+1))
  done
  EOF
  chmod +x rounds.sh
  ```
- Steps:
  1. Add `~/.local/share/diogenes-probe` to `sandbox.filesystem.allowWrite` in the probe project's `.claude/settings.json` (not user settings).
  2. **Free-running, overlapping:** on the host, `python3 -I take.py A free 20 &`; at the same moment, in the probe session, ask Claude to run `python3 -I ~/.local/share/diogenes-probe/take.py B free 20` as a background Bash call. Both loops must overlap in time. Afterwards `sqlite3 probe.db 'SELECT fence FROM lease;'` must equal the sum of wins.
  3. **Contested rounds:** reset the lease, then start `./rounds.sh 30 &` on the host, `python3 -I take.py A contested 30 &` on the host, and the same with `B` as a background sandboxed Bash call. Assert one winner per round (`wins_A + wins_B == rounds` and `fence == rounds`).
  4. Repeat step 3 with both racers inside sandboxed Bash calls (two background calls), which models two accounts' sandboxes.
- Expected: no `database is locked` errors; the fence equals the wins; one winner per contested round in every placement.
- Decides: pass → the 0.0 file-backed CLI (DQ-1 option a). Fail on the host alone → a spool-ingesting hub moves into 0.0. Fail only across the sandbox boundary → in 0.0 Bash use of `dio` is dropped in favour of hooks, and the spool hub moves into 0.0.
- Cost: 30 minutes. Prerequisites: none.

**DX-7. Ubuntu's sqlite3 3.45.1 carries the WAL-reset fix.** (The FTS5 half is **DONE (measured 2026-10-10)**: M4's FTS5 match returned 1 row on this build, and `PRAGMA data_version` went 2 → 3 on a second connection after the first committed in WAL mode.)
- Commands:
  ```sh
  apt-get changelog sqlite3 2>/dev/null | grep -i -n -E 'wal|3\.45\.1' | head
  zcat /usr/share/doc/sqlite3/changelog.Debian.gz | head -40
  ```
- Expected: a changelog line naming the WAL-reset race (upstream fixed in 3.51.3, backports 3.44.6 and 3.50.7 [r4 §3]) or none.
- Decides: no backport → keep the hub as the sole writer from 0.1 and avoid long concurrent reads in 0.0. This is a check, not a pass-or-fail.
- **RESULT, the WAL half (checked 2026-10-10 15:32 by `nitpick-libs_18`): NO BACKPORT FOUND.**
  - The installed package is `libsqlite3-0 3.45.1-1ubuntu2.8` (noble-security, 2026-09-03).
  - Its `changelog.Debian.gz` lists security backports for CVE-2026-39113, CVE-2026-50812/50813, CVE-2026-11822/11824, CVE-2025-7709, CVE-2025-6965, CVE-2025-29087 and earlier. No entry names a WAL-reset race. A search for `wal`, `reset`, `race` and `corrupt` finds only unrelated lines.
  - **So, by this experiment's rule:** the hub is the sole writer from 0.1, and 0.0 avoids long concurrent reads. DX-1's sandbox-to-sandbox pass does not change this, because the race concerns a WAL reset during concurrent reads, which DX-1 did not exercise.
- Cost: 5 minutes. Prerequisites: none. UNVERIFIED claims resolved: [r4 §3] (WAL half still open); [r7 §2] FTS5 and [r4 §3] `data_version` now measured.

**DX-2. A `UserPromptSubmit` hook's `additionalContext` reaches the model, within the cap, including on turns started by a cross-session message; a `PostToolUse` hook's `additionalContext` reaches it mid-turn; and the hook sees what a peer message looks like.**
- Settings in a probe project's `.claude/settings.json` (never user settings):
  ```json
  {"hooks":{"UserPromptSubmit":[{"hooks":[{"type":"command","command":"/tmp/dx2.sh","timeout":5}]}],
            "PostToolUse":[{"hooks":[{"type":"command","command":"/tmp/dx2.sh","timeout":5}]}]}}
  ```
  `/tmp/dx2.sh`:
  ```sh
  #!/bin/sh
  ev=$(tee -a "$HOME/.cache/dx2/stdin.jsonl" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("hook_event_name",""))')
  n=$(cat "$HOME/.cache/dx2/count" 2>/dev/null || echo 0); last=$(cat "$HOME/.cache/dx2/last" 2>/dev/null || echo -1)
  if [ "$ev" = "PostToolUse" ] && [ "$n" = "$last" ]; then exit 0; fi
  echo "$n" > "$HOME/.cache/dx2/last"
  printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":"DIOGENES PROBE: %s unread (m1 notice from probe-b, ack-only). Run dio inbox."}}\n' "$ev" "$n"
  ```
  with `umask 077; mkdir -p ~/.cache/dx2` first.
- Steps: start `claude --name probe-a`; type a prompt; ask Claude what Diogenes context it saw. Mid-turn (give Claude a multi-step task), `echo 1 > ~/.cache/dx2/count` and see whether the next tool call carries the new count exactly once. From a second session `probe-b` on the same account, `SendMessage` to `probe-a`; inspect the log for the `prompt` field and any sender field. Then make the hook print 12,000 characters and observe truncation. Time the hook with `time`.
- Expected: the probe line is quoted back; the message turn also ran the hook [r1b §3]; the `PostToolUse` injection appears once after the count changes; truncation near 10,000 characters [r3 §What this means, 3]; under 300 ms.
- Decides: pass → DR-3 on `UserPromptSubmit` plus `PostToolUse` on change. Fail → `Stop` with `decision: block` [r1 §A.2].
- Cost: 25 minutes. Prerequisites: none.

**DX-3. The identity fields available to a hook, to Bash, to a subagent's Bash, and to the status line; whether the host's `/proc` is visible from sandboxed Bash.** *RESULT (the gate's F9 legs), 2026-10-24: at this file's end, under "DX-3's RESULT".*
- **RESULT (partial, 2026-10-15): the run stopped at S1, and A2's write question was measured from the working seats instead.** B1 ran from 14:36 to 14:47 EDT: the author started the probes, and the Team seat's manager, `Ailp-team_2`, ran the exchange and the control readings from its own session. The probes ran Claude Code 2.1.300, by the run sheet. The files are in `research/done/dx3-probe-2026-10-15/`, whose README says who made each line. This is the narrowed DX-3 of `roadmap/0.0/MIN.md` step 2. Filed by the Team seat (D2b).
  - **Setup** (the run sheet, `/home/randy/Team/META/diogenes/probes/DX3-run-sheet.md` §1–§2): three probe sessions, each started with `--permission-mode dontAsk` in a probe directory whose `.claude/settings.local.json` turns the sandbox on: `probe-t` (Team, named), `probe-m` (Max, named) and an unnamed Team probe. The manager sent S1 to each as a cross-session message. probe-t's S1, as sent, is `s1-as-sent.txt`.
  - **The stop** (the manager's record, `D2b-controls.txt` lines 11–13, 18 and 19):
    - **probe-t** ran S1 line 1. Line 2, a compound command (an `echo` with `$(test -w … && echo yes || echo no)`), was refused before it ran: "Permission to use Bash has been denied because Claude Code is running in don't ask mode". The manager's reading: under dontAsk a compound command is not auto-allowed, even sandboxed (`MANAGER-LOG.md`, 14:42:54).
    - **probe-m's** response to S1 was stopped by a safety classifier (the notice at 18:43:10Z). probe-m then stopped of its own judgment (18:43:57Z), and wrote and sent nothing.
    - **The unnamed probe** never processed S1. Its conversation had moved to a background session shown as `DX-3 Diogenes probe` (pid 3809505, a `--fork-session --resume` of its conversation, started at 14:40:23 EDT).
    - So the run stopped, as the run sheet's §1.4 requires on a refusal, and no step was improvised. No write leg ran, and nothing was written to either inbox (C4 at 18:47:25Z: `inbox_files=0`, line 14).
  - **(a) and (b), from the manager's readings only** (C1-pre, lines 10 and 11, 18:42:16Z: `ps`, each sessions file read unsandboxed by its exact name, and the manager's own `ListAgents`):
    - **(a)** Every probe's `messagingSocketPath` is `/run/user/1000/cc-socks/<pid>.sock`: probe-t `3794894.sock`, probe-m `3803991.sock`, the unnamed probe `3807871.sock` (line 10; `MANAGER-LOG.md`, 15:01:19). Its comparison with `$CLAUDE_CODE_MESSAGING_SOCKET` in a probe's own Bash, S1 line 3, did not run.
    - **(b)** `name` and `nameSource`: probe-t `probe-t` and `user`; probe-m `probe-m` and `user`; the unnamed probe `dio-probe-71` and `derived`. The two background sessions, shown as `DX-3 Diogenes probe` and `c42c46c8`, have `nameSource` `auto` and null.
    - **`kind`:** `interactive` for probe-t and the unnamed probe, `bg` for the two background sessions. No `kind` was read for probe-m (the manager's `jq` filter for the Max file did not select it).
    - **`ListAgents`:** the manager's, at 14:41, listed probe-t and the background `DX-3 Diogenes probe`, and **not the unnamed interactive probe, `dio-probe-71`** (line 11), nor `c42c46c8` (`MANAGER-LOG.md`, 14:41–14:42). For probe-t, the sessions file's `name` and the name `ListAgents` listed agree: `probe-t`.
  - **probe-t's S1 line 1, the one sandboxed reading** (`DX3-team-probe-t.txt`, 18:42:46Z). Its own pid, net and mount namespaces, `pid:[4026535439]`, `net:[4026534885]` and `mnt:[4026535433]`, all differ from the host's in C0 (`pid:[4026531836]`, `net:[4026531833]`, `mnt:[4026531832]`, line 5). `lo` is its only network device.
  - **A2's write leg, measured instead from the working seats on both accounts:** bypassPermissions, unsandboxed Bash, the settings as they stood that day, under `management_0`'s test-write OK (`MANAGER-LOG.md`, 14:48:41).
    - **Team,** by `Ailp-team_2` (lines 20–24, 18:49:20Z–18:49:27Z): a Bash `touch` of `inbox/max/DX3-team-bypass-bash-20261015T184920Z.probe` exited 0, and the Write tool created `inbox/max/DX3-team-bypass-write-20261015T184920Z.probe` (45 B, mode 664). Both were removed (`after=gone`), and the inboxes ended with 0 files.
    - **Max,** by `diogenes_0` (line 25, its report as the manager received it): a Bash `touch` and a Write-tool file in `inbox/team/`, at `T=20261015T185301Z`, each removed at once (14:53:04 and 14:53:09 EDT); both inboxes were empty after. Its caveat: a Max seat started without the bypass flag runs dontAsk, which this does not cover.
    - **So a bypass-launched seat on either account needs no `allow`, `allowWrite` or sandbox entry to write the inbox** (`MANAGER-LOG.md`, 14:53:52). A2's answer is in `roadmap/0.0/MIN.md`, step 6's note.
  - **Still open, for the gate:** the sandboxed (c) and (d) (`sessions/` and `/proc` from sandboxed Bash), S1 line 3's `CLAUDE_PID` and `CLAUDE_CODE_SESSION_ID` in a probe's own Bash (D2a's finding 4, third item, `/home/randy/Team/REPORTS/D2a-diogenes-dx3-prep.md:87`), DX-18, DX-13's 10-minute leg, and the dontAsk and sandbox legs (`MANAGER-LOG.md`, 15:01:19, and its current state's Diogenes lane, which also sends the classifier finding and the unnamed session's move to the background to the gate). The gate re-runs them as fewer, plain, script-run steps (that current state; `MANAGER-LOG.md`, 14:48:14). `MIN.md` step 2 runs DX-13's 10-minute leg before `dio watch` ships. **Note 2026-10-16, `diogenes_0`:** DX-13's 10-minute leg has run and is filed, in DX-13's RESULT (10-minute leg) below.
- Settings (probe project only): a `SessionStart` hook `/tmp/dx3.sh`:
  ```sh
  #!/bin/sh
  umask 077; mkdir -p "$HOME/.cache/dx3"
  { echo "--- $(date -u +%FT%TZ) ppid=$PPID $(ps -o comm= -p $PPID)"; cat; env | grep -E '^CLAUDE_' | sed -E 's/(TOKEN=).*/\1<redacted>/'; } >> "$HOME/.cache/dx3/session-start.log"
  ```
  and a status-line command that appends its stdin to `~/.cache/dx3/status.jsonl` and then runs the author's existing status-line script, so nothing is replaced.
- Steps: start one session with `--name probe-c` and one without a name; in each run in Bash `echo "sid=[$CLAUDE_SESSION_ID] sock=[$CLAUDE_CODE_MESSAGING_SOCKET]"`, then `ls /proc/<the ppid from the log>/ && stat -c %Y /proc/<ppid>` (is the host process visible from the sandbox?), then `/status`, `/list-agents`; dispatch a subagent and have it run the same `echo` in its Bash; repeat once with `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1`; compare `session_id`, `session_title`, the socket path, the status line's `session_name`, and the transcript path.
- Expected: hooks give `session_id` and `session_title` (custom names only) and the socket path; `CLAUDE_SESSION_ID` is empty in Bash (observed); `CLAUDE_CODE_MESSAGING_SOCKET` is documented as exported to Bash [r1 §2.1] and is expected in a subagent's Bash too (its sends go out under the parent's address, firsthand §1); whether the scrub removes it is unknown; whether `/proc/<host pid>` is visible from the sandbox is unknown; the status line gives `session_name` for named sessions only [r1b disposition 2].
- Decides: which fields `dio register` reads from where, the `--how` values, whether DR-107's socket mapping works from Bash and from subagents, and whether DR-108's process check can run from inside the sandbox.
- Cost: 20 minutes. Prerequisites: none.

**DX-13 (moved before 0.0). A background Bash `until` loop wakes the session when it exits, every time, and its lifetime cap.** *RESULT (the gate's exit-2, 2-hour and overnight legs), 2026-10-24: at this file's end, under "DX-13's RESULT".*
- **RESULT (10-minute leg), 2026-10-16: one idle wake by the session's own background `until` loop, measured on a working seat.** The Team seat's manager, `Ailp-team_5`, ran the leg on its own session from 00:52:02 to 01:02:44 EDT: Claude Code 2.1.301, the `~/.claude-team` config dir, bypass permissions. `roadmap/0.0/MIN.md` step 2 runs this leg before `dio watch` ships, and the author's steps give it (B2) to the seat, with no author step. The record, revised after `diogenes_0`'s six corrections, is in `research/done/dx13-10min-2026-10-16/`, whose README says who made each line. A "raw line" below is a line of its raw record, lines 112–134 of the file. Filed by the Team seat (D4).
  - **Measured.** The loop's exit woke the idle session once. The task-notification was enqueued 0.010 s after the loop's exit line, and the turn began 0.049 s after the enqueue. Nothing else started a turn in the 9 min 49.6 s the session was idle. The wake was one model turn.
  - **How the run differs from the steps below,** each with its reason (the record's seven deviations):
    - The probe was the working manager session, not a probe session: B2 gives the leg to the seat, so the seat was the probe.
    - The go file was `/home/randy/Team/TMP/dx13/go`, not `~/.cache/dx13/go`: the Team seat writes only in `/home/randy/Team`.
    - A detached timer touched it, not a hand, since there was no author step: `setsid --fork sh -c 'sleep 600; date "+timer clock …" >> record.txt; touch /home/randy/Team/TMP/dx13/go'`.
    - The loop was the steps' own command with the Team path, plus a `date` after `echo WAKE` to time its exit, run as a Bash-tool background task (`run_in_background`).
    - The cost comes from named sources, not "status-line cost before and after", because the Team status line's files carry no `cost.total_cost_usd`: the wake turn's `.message.usage` in the session transcript, `~/.claude-team/projects/-home-randy-Team/b0982a56-a9c5-4b99-b0d0-e60a75b8b05c.jsonl`, matched to its `api-request` entry by `requestRef` and `id`; `.rate_limits.five_hour.used_percentage` and `.rate_limits.seven_day.used_percentage` in `/home/randy/Team/CONFIG/usage-latest.json`; and `.context_window.total_input_tokens` and `.used_percentage` in the session's file in `/home/randy/Team/CONFIG/context/`.
    - The session was idle 9 min 49.6 s, not a full 10 minutes: the timer counted 600 s from its own start, and the setup turn went on 36.1 s past that.
    - The SQLite polling leg is moot for 0.0-min, which has no database (`roadmap/0.0/MIN.md`, "Left to 0.1").
  - **The evidence, quoted from the record:**
    - **go was absent when the loop started:** "go present at setup? no" (00:52:02.117, raw line 114, with the directory's listing in raw lines 115–119), and "go present after timer start? no" (raw line 132).
    - **The timer's process,** by `ps -o pid,sid,pgid,ppid,lstart,args` (raw line 126): `2282834 2282834 2282834   18467 Fri Oct 16 00:52:09 2026 sh -c sleep 600; date "+timer clock %Y-%m-%dT%H:%M:%S.%N%z" >> /home/randy/Team/TMP/dx13/record.txt; touch /home/randy/Team/TMP/dx13/go`. Two things show that it was no task of the session. Its parent, pid 18467, is `/usr/lib/systemd/systemd --user` (raw line 129), while every task the session runs has the session's own pid, 800537, as its parent (the loop task, raw line 130). And "the turn began 25.65 s after the timer's touch, at the loop's exit, with no transcript entry at the timer's own end" (the record's deviation 3). [`diogenes_0`, 2026-10-16: 25.65 s runs from the touch to the loop's exit line. The turn began 25.71 s after the touch. The slip was `diogenes_0`'s, in its fix 4, which the record and amendment 1 carried (D4v's finding 9).] Its session id shows nothing, because the Bash tool runs every command in a session of its own: the loop task's (2282422) and the setup shell's (2282830) differ from the session process's (28467) too (raw lines 124–131).
    - **The timer's clock line:** "timer clock 2026-10-16T01:02:09.957313591-0400" (raw line 134). The go file's mtime was 01:02:09.958413609.
    - **The WAKE:** the loop's output (task bv3n5sym1) was "WAKE", then "loop exit 2026-10-16T01:02:35.612058481-0400", exit code 0: 25.65 s after the touch, inside the 30 s poll.
    - **The new turn's first `date`:** "new turn first date 2026-10-16T01:02:44.571499247-0400".
    - **Every turn start in the window, from the transcript (EDT):** the setup turn ended at 00:52:46.003 (`turn_duration`). At 00:55:53.028 a harness `away_summary` entry was logged, with no user, queue or assistant entry after it and no `api-request` for it, so whether it made a model call is not shown; it started no turn. The next entry is the notification's enqueue at 01:02:35.622, and the turn started with its prompt at 01:02:35.671. No other entry lies between 00:52:46.003 and 01:02:35.622, and no peer message, prompt or subagent event arrived.
  - **The cost, named for what it is: one working seat's wake, not a fresh small probe's.** The wake turn logged two `api-request` entries before its first output, at 01:02:35.746 and 01:02:35.978. Its assistant entries carry the second one's usage: `input_tokens` 4, `cache_creation_input_tokens` 851, `cache_read_input_tokens` 466 857 and `output_tokens` 729, 169 of them thinking. The first recorded no usage, so its cost is not known. Every request asked for a cache ttl of "1h", yet the usage labels every cache write in the session `ephemeral_5m`; the wake read the cache 9 min 56 s after its last write, which fits the requested hour, not the label. The meters, in whole percents, did not move: five-hour 41 % → 41 %, week 48 % → 48 %. The context file's `total_input_tokens` went from 457 819 (46 %) to 467 712 (47 %), a rise that includes the setup turn's own calls. A fresh small probe, as M2 uses, would read far less.
  - **Still open, for the gate** (`MIN.md` step 2; the author's steps, B3): the 2-hour and overnight legs, and so any lifetime cap of a background loop; whether the wake comes "every time", since this was one trial; and a wake's cost past the cache's life. The record expects a wake past an hour to write the context again, about 467 k tokens for this seat, and asks the 2-hour leg to record its wake request's `cache_read` and `cache_creation`. The polling leg stays moot for 0.0-min.
  - **Used by `dio watch`** (build step 3): its `--max` default, 3000 s, takes its reasons from this record and is provisional until the gate's legs (`src/README.md`, "The cap, provisional", and decision 17). [`diogenes_4`, 2026-10-29: no longer provisional, and the heading is now "The cap". The merger kept 3000 s at the gate's merge, and D9's C (`4d66f99`) made it final (`roadmap/0.0/FINISH.md`, "D9's merge").]
- Steps: in a probe session ask Claude to run, in the background, `until [ -f ~/.cache/dx13/go ]; do sleep 30; done; echo WAKE`; leave the session idle; after 10 minutes `touch ~/.cache/dx13/go` and record whether a turn starts and what it costs (status-line cost before and after). Repeat with the wait at 2 hours, then overnight, to find any cap. Then repeat with the loop polling `python3 -c 'import sqlite3; …data_version…'` against the DX-1 probe database every 30 s, which is the shape of `dio wait`.
- Expected: the completion re-invokes the idle session, as observed once on 2026-10-10 (firsthand §2; the observation records no duration); the cap is untested; each exit costs one model turn.
- Decides: DR-105's poll interval and re-arm rule; whether the 0.0 worker gate ("10 of 10") is reachable; the cheapest wake path for a seat that opts in.
- Cost: the wait. Prerequisites: none.

**DX-6. Status-line fields on the Max account.**
- Commands: the status-line command from DX-3 (which tees and then runs the existing script); then `jq '.rate_limits, .model_limits, .context_window.used_percentage, .cost' ~/.cache/dx3/status.jsonl | tail -20`.
- Expected: `rate_limits.five_hour` and `seven_day` with `used_percentage` and `resets_at`; a `model_limits` line for Fable (observed in `usage-latest.json`); context percentage; `cost.total_cost_usd` and token totals [r1 §7].
- Decides: `dio meters publish` input; the Fable source (DR-56); the Max cost-to-percentage ratio that DR-109's Team estimate uses.
- Cost: 5 minutes after DX-3. Prerequisites: DX-3.

**DX-5. The same under the Team config dir, what its managed settings say, and the meters-file hazard.**
- Commands: `CLAUDE_CONFIG_DIR=~/.claude-team claude --name probe-t` with the DX-2 and DX-3 hooks installed in a probe project's `.claude/settings.json`; `/status`; `/config`; the status line as in DX-6; `claude agents --json`. Before installing any status-line script under the Team config dir, read the author's script and confirm whether it writes the fixed path `~/.claude/usage-latest.json`; if it does, confirm the Team copy is changed to write its own file before it runs, so Max seats' meters are never overwritten [c1 C-4].
- Expected: hooks run (unless `allowManagedHooksOnly` is set); `rate_limits` absent (documented for Team [r1b disposition 14]); `cost.total_cost_usd` present; the socket directory the same as Max's or different.
- Decides: the Team half of DR-91; whether DR-55 reads `estimate` or `unknown` for the Team meters; the inputs of DR-109; DQ-4's facts.
- Cost: 20 minutes. Prerequisites: the second account.

**DX-26 (appended; the critique's "DX-12a"). A mod's `$.session.usage()` and the `session.measure` event carry rate limits on the Team seat.**
- Setup: a local-directory plugin in a probe project with `register.js` that, on `session.measure`, writes `JSON.stringify($.session.usage())` to `~/.cache/dx26/usage.jsonl` (private directory). No `$.prompt.submit`, no timer that starts a turn, so DQ-7 is not involved.
- Steps: run it under the Max config dir and under the Team config dir; send two prompts in each; compare `rateLimits` between the two.
- Expected: unknown on the Team seat; the status line is documented to lack `rate_limits` there, and the mod API returns `{ startedAt, context, rateLimits, cost }` [r1b §6, E14].
- Decides: whether DR-109's estimate is superseded by a measured Team meter, and whether a mod is installed on the Team seat for telemetry alone.
- Cost: 30 minutes. Prerequisites: Node; the second account; the Team org not setting `allowManagedModsOnly` (DQ-4).

**DX-4. Native `SendMessage` across two config dirs (the round-1 E1).**
- **RESULT: PASS, BOTH WAYS (measured 2026-10-12 05:06 by `nitpick-libs_18`, at the author's request).**
  - **Setup.** The Team account's session, "Team workspace setup and configuration" `[a4a10f]`, is a Claude Desktop session working in `/home/randy/Team`. It appeared in the Max-account seat's `ListAgents` as "another Claude session on this machine".
  - **Max → Team:** a test message was sent to it by name and ref, and delivered to its inbox.
  - **Team → Max:** it replied by `SendMessage`. The reply arrived here as `<cross-session-message from="uds:/run/user/1000/cc-socks/242635.sock" from-session="local_c64ba531-…" from-mode="bypass">`. A longer follow-up message also went through.
  - **Approval:** the receiving side reported the message *"was delivered straight into my conversation with no approval step on my end"*. Both sessions ran in bypass mode. A session in a different mode would hold messages for its user's approval [r1b §1].
  - **Caveat:** in this setup the two accounts share one `~/.claude` (the Team seat's own account). Whether separate `CLAUDE_CONFIG_DIR`s would also see each other is not tested. One socket directory per OS user suggests they would.
- Commands:
  ```sh
  # terminal 1 (the Max side: leave CLAUDE_CONFIG_DIR unset, so nothing about the default login changes)
  claude --name probe-a
  # terminal 2
  CLAUDE_CONFIG_DIR=~/.claude-team claude --name probe-b
  # in a third shell
  ls -la /run/user/1000/cc-socks /tmp/cc-socks-1000 2>&1
  claude agents --json; CLAUDE_CONFIG_DIR=~/.claude-team claude agents --json
  ```
  In each session: `/status` (note `Peer address`), `/list-agents`; ask probe-a to message probe-b; repeat with one side idle, one side in bypass mode, with `crossSessionInbound: "accept"` in both user settings, and with `notify_when_idle: true` from each side.
- Expected: unknown. The socket is per OS user and nothing documented keys it to the config dir [r1b §1, §7]. `~/.claude.json` "appears to move with" the config dir [r1 §5], so setting `CLAUDE_CONFIG_DIR=~/.claude` explicitly may not behave like leaving it unset; it is left unset [c1 C-12].
- Decides: DQ-8 and the day-zero doorbell. Diogenes does not depend on either result (R-5).
- Cost: 15 minutes. Prerequisites: the second account.

## Before cycle 0.1

**DX-8 (narrowed). What a sandboxed Bash can still reach, and how fast the spool round-trips.**
- **DONE (measured 2026-10-10), the default case:** M1, `socket(AF_UNIX)` is refused outright under the default settings, so the seccomp filter is installed; M3, a loopback listener started in one Bash call is not reachable from another, each call having its own network namespace; M2, loopback within one call works. A hub on a Unix socket or host loopback is therefore unreachable from sandboxed Bash by default.
- Still open, each under a setting in a probe project's `.claude/settings.json`:
  1. `"sandbox":{"network":{"allowAllUnixSockets":true}}`: can `python3 -c "import socket;s=socket.socket(socket.AF_UNIX);s.connect('/tmp/hub.sock');print('unix ok')"` connect to a socket served by a 10-line Python server started outside Claude, and is the socket path visible through the mounts (UNVERIFIED [r1b disposition 15])?
  2. `"network":{"allowedDomains":["127.0.0.1:8788","diogenes.localhost"]}`: does `curl -s -m 3 http://127.0.0.1:8788/` or `curl -s -m 3 http://diogenes.localhost:8788/` reach `python3 -m http.server 8788 --bind 127.0.0.1` on the host through the filtering proxy? (M3's "one remaining network path".)
  3. `"sandbox":{"excludedCommands":["dio *"]}`: does an excluded `dio` reach the host socket, at the cost of running unsandboxed?
  4. **Spool latency:** with a 20-line Python inotify ingester on the host watching `~/.local/share/diogenes-probe/spool/`, have sandboxed Bash write 100 request files and read the reply files; record the median and 95th-percentile round trip, and whether inotify events from a bind-mounted write arrive at all (if not, measure a 50 ms polling ingester instead).
- Expected from the docs: 1 unknown; 2 may work ([r1b §8] names `"127.0.0.1:8080"` in `allowedDomains` as the documented route for proxied localhost); 3 works [r1b §8]; 4 unknown.
- Decides: whether the 0.1 spool is the only Bash path or whether a proxied HTTP transport can join it; the 0.1 gate's latency figure; whether the hub listens on HTTP as well as the socket.
- Cost: 40 minutes. Prerequisites: none.

**DX-9. A `PreToolUse` guard denies Edit, Write and Bash without the lease, inside a subagent too, and fails closed with `onFailure: "block"`.**
- Settings, in the probe project's `.claude/settings.json` only (a user-level deny guard would block every working seat):
  ```json
  {"hooks":{"PreToolUse":[{"matcher":"Edit|Write|MultiEdit|Bash","hooks":[{"type":"command","command":"/tmp/dx9.sh","timeout":5,"onFailure":"block"}]}]}}
  ```
  `/tmp/dx9.sh` reads stdin, logs `session_id` and `agent_id` to a private file, checks `~/.cache/dx9/lease` for the session id, and prints `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"no lease"}}` when absent.
- Steps: ask Claude to edit a file (denied); write the session id to the lease file (allowed); dispatch a subagent that edits (log shows `agent_id`; same decision); `chmod -x /tmp/dx9.sh` and edit again (blocked by `onFailure`).
- Expected: as listed [r1 §C], [r1b §3].
- Decides: DR-41's shape. If `onFailure: "block"` does not block, the guard denies on any error by printing a deny before doing work.
- Cost: 20 minutes. Prerequisites: none.

**DX-10. `SessionEnd` finishes in 1.5 s, and a `kill -9` leaves the lease to its TTL.**
- Settings (probe project): a `SessionEnd` hook that sleeps 3 s then writes a file; then with `"timeout": 10`.
- Steps: exit normally; observe the file; take a lease in a probe session; record the probe's pid from its `SessionStart` hook (`$PPID`, as in DX-3) and confirm with `ps -o comm=,args= -p <pid>` that it is the probe's `claude` process and not a working seat; `kill -9` that pid only; confirm `SessionEnd` did not run and the lease expires only at its TTL.
- Expected: truncation at 1.5 s by default; up to 60 s with `timeout` [r1b §3]; no hook on `kill -9`.
- Decides: `dio goodbye` is best-effort; TTL plus the process check (DR-108) is the real release path.
- Cost: 10 minutes. Prerequisites: none.

**DX-15. The token file is unreadable to the model and the sandbox from either account, in bypass permission mode too, the unsandboxed retry is ignored, and the proxy's `mask` feature works on 2.1.296.**
- Settings (both accounts' user settings, since this is the real adapter configuration, after the probes above): a 0600 file `~/.claude/diogenes.token` and `~/.claude-team/diogenes.token`; in **each** account: `"permissions":{"deny":["Read(~/.claude/diogenes.token)","Read(~/.claude-team/diogenes.token)"]}`, `"sandbox":{"filesystem":{"denyRead":["~/.claude/diogenes.token","~/.claude-team/diogenes.token"]},"allowUnsandboxedCommands":false}`; then the proxy `mask` configuration from the sandboxing docs with `injectHosts` set to a probe host.
- Steps: from a session on each account, ask Claude to Read both files (denied), to `cat` both in Bash (denied), to retry the `cat` with `dangerouslyDisableSandbox` (ignored), and to `curl` the probe host with the masked header (the server sees the real value, the transcript the sentinel). **Repeat the whole sequence in bypass permission mode**, which the author's seats use: no digest says whether `permissions.deny` holds there [c1 C-11].
  - **Note 2026-10-15, Team seat (D2b):** whether `permissions.deny` holds in bypass mode now has a documented answer. The permission-modes page (code.claude.com/docs/en/permission-modes, "Available modes") says: "Deny rules block in every mode, including `bypassPermissions`."
    - **Its reach in Bash is limited,** as D2c found on the permissions page (code.claude.com/docs/en/permissions, "Read and Edit"): "Read and Edit deny rules apply to Claude's built-in file tools, to file commands Claude Code recognizes in Bash, such as `cat`, `head`, `tail`, `sed`, and `tee`, and to the targets of Bash redirections such as `> file` and `< file`. They don't apply to a command that reads files without naming them, such as `grep -r pattern .` run from the directory that holds the file, or to arbitrary subprocesses that read or write files indirectly, like a Python or Node script that opens files itself."
    - **D2c also found** that none of the seven pages it searched lists `jq` as such a command ("such as" leaves the set open), and that the pages don't say whether a glob that expands to the file is covered (`/home/randy/Team/REPORTS/D2c-diogenes-a2-deny-rules.md`, (1)).
    - **Checked twice.** The Team seat's manager re-fetched both quotes from code.claude.com after D2c (17:00:27–17:02:11, `/home/randy/Team/MANAGER-LOG.md`), and D2b fetched both pages again at 17:14:58 and found both quotes verbatim.
    - **Documented, not measured.** D2c's canary is staged and will not be run (`management_0`, 17:07:37, `MANAGER-LOG.md`). The rest of DX-15 stays open as written: the token file, the unsandboxed retry and the proxy's `mask`.
- Expected: deny, deny, ignored, masked [r5 §4], [r1 §6]. The `mask` behaviour on this version and the bypass-mode behaviour are UNVERIFIED.
- Decides: DR-82's enforcement; whether `mask` replaces the token file for HTTP; whether bypass mode needs a different control.
- Cost: 30 minutes. Prerequisites: the second account.

**DX-16. `SO_PEERCRED` reports one uid for both accounts.**
- Commands: a 15-line Python Unix socket server printing `SO_PEERCRED`, run outside Claude; connect from a hook (not Bash: M1) in a session on each account.
- Expected: the same uid and gid; different pids.
- Decides: confirms that 0.1 needs tokens, not peer credentials (DQ-6).
- Cost: 10 minutes. Prerequisites: the second account for the second half.

**DX-18. `claude agents --json --all` under each config dir, as a presence source.** *RESULT (the listing half), 2026-10-22: at this file's end, under "DX-18's RESULT".*
- Commands: `claude agents --json --all` with and without `CLAUDE_CONFIG_DIR`; start a background session with `claude --bg`; leave it idle an hour; re-run.
- Expected: per-config-dir listings; `status` and `waitingFor` fields; the idle background session's process stopped after about an hour unless pinned [r1b §5]; whether its socket stays bound is UNVERIFIED.
- Decides: whether `dio who` polls this for background seats, whether Team workers can be background sessions (DQ-29), and whether seats must be pinned.
- Cost: 10 minutes plus the wait. Prerequisites: none; the second account for the cross part.

## Before cycle 0.2

**DX-11. An `asyncRewake` hook wakes an idle session, re-arms on `Stop` without stacking, and its timeout ceiling.**
- Settings (probe project):
  ```json
  {"hooks":{"SessionStart":[{"hooks":[{"type":"command","command":"/tmp/wake.sh","asyncRewake":true,"timeout":90}]}],
            "Stop":[{"hooks":[{"type":"command","command":"/tmp/wake.sh","asyncRewake":true,"timeout":90}]}]}}
  ```
  `/tmp/wake.sh`: `sleep 45; echo "DIOGENES WAKE: 1 unread; run dio inbox" >&2; exit 2`. Then `"timeout": 3600` to find the ceiling, and a lockfile keyed by `session_id` in the script to prevent stacked listeners.
- Expected: a new turn starts on its own after 45 s; one wake per message, not repeated (a recent changelog fix touched this path [r1b §3]); the ceiling is undocumented.
- Decides: DR-25's first mechanism and the long-poll length `dio listen` may use.
- Cost: 30 minutes. Prerequisites: DQ-7 permits the probe.

**DX-12. A mod's `$.prompt.submit` wakes an idle session, and `$.http.fetch` reaches loopback.** (The usage half moved to DX-26, which has no wake and no DQ-7 dependency.)
- Setup: a local-directory plugin with `register.js`: `$.clock.after(60000, () => $.prompt.submit({ text: 'DIOGENES MOD TEST' }))`, plus a handler that logs `$.http.fetch('http://127.0.0.1:8788/')` to a private file.
- Expected: a new turn after 60 s with the mod named as sender [r1b §6]; loopback reach unknown [r1b E11, E12].
- Decides: whether 0.2 builds the mod; whether `$.process.spawn(['dio','listen'])` is needed instead of fetch.
- Cost: 30 minutes. Prerequisites: Node; DQ-7 permits.

**DX-14. A cron task fires while idle, and what one fire costs.**
- Steps: in a probe session, create a one-shot `CronCreate` 2 minutes out with the prompt `run dio inbox --count`; leave idle; read the status line's cost before and after.
- Expected: it fires while idle [r1b §5]; the cost of one turn over the whole context.
- Decides: whether cron is ever an acceptable poll, and at what interval. Not a dependency of any cycle.
- Cost: 10 minutes. Prerequisites: DQ-7 permits.

## Before cycle 0.3 and later

**DX-19. Does Claude Code 2.1.296 read `AGENTS.md`?**
- Steps: a probe project with only an `AGENTS.md` containing a canary sentence; start `claude`; ask what project instructions it has.
- Decides: whether the `CLAUDE.md` shim is needed (DR-97) [r3 §4].
- Cost: 5 minutes. Prerequisites: none.

**DX-22. Antigravity: `injectSteps` feeds the model, MCP reaches the hub, hooks run with a sanitised environment, a sidecar runs unattended, and the sandbox's default and network policy.**
- Setup: install `agy`; a probe workspace with `.agents/hooks.json` containing a `PreInvocation` command hook that prints `{"injectSteps":[{"userMessage":"DIOGENES PROBE: 1 unread; call diogenes/inbox"}]}` and logs `env` (redacted as in DX-3) to a private file; a `mcp_config.json` entry for a stub MCP server with `command` (stdio) and another with `serverUrl` on `127.0.0.1:8788`; `permissions.allow` with `mcp(diogenes/*)`; a `schedule` sidecar running `agentapi send-message <conversation_id> "ping"`.
- Steps: ask the agent what Diogenes context it has (does the injected message appear, and mid-turn or at the next invocation?); call each MCP server; make the hook exit 1 (is the tool call blocked?); list the variables the hook saw; for the sidecar, **send at most 3 pings in total** (each is a turn against the AI Pro five-hour and weekly limits [r2 §2.8, §5]), one with the desktop app closed and only `agy` running, one with neither, then **disable the sidecar**; record whether the terminal sandbox is on or off by default ([r2 §2.2] and [r5 §3] disagree) and, with `enableTerminalSandbox` on, `curl` the stub from the shell tool.
- Expected: documented for the hook events and the MCP config [r2 §2.3, §2.5]; the injection reaching the model is from secondary sources; the sidecar's unattended behaviour and the sandbox's network policy are UNVERIFIED [r2 §2.6, §2.2].
- Decides: DQ-11 (hooks and MCP versus supervisor); whether a sidecar can wake Gemini; DR-94's config-from-file rule; which transport the 0.3 MCP entry uses.
- Cost: 1 to 2 hours plus the install, and 3 Antigravity turns. Prerequisites: `agy` installed and signed in on the AI Pro plan; the stub MCP server from 0.1.

**DX-23. Codex: sandbox reach, hook injection and the cap, `exec --output-schema`, and the credential path.**
- Setup: install Codex CLI; `~/.codex/config.toml` with a stdio `[mcp_servers.diogenes]` and an HTTP one on `127.0.0.1:8788` using `bearer_token_env_var` [r3 §9]; `~/.codex/hooks.json` with a `UserPromptSubmit` command hook printing a canary line; review it with `/hooks`.
- Steps: in a default `workspace-write` session, run `curl http://127.0.0.1:8788/` from the shell tool, call the HTTP MCP tool, call the stdio MCP tool; repeat with `[sandbox_workspace_write] network_access = true`; make the hook print 3,000 characters; from the shell tool run `env | grep -c <the variable name>` to see whether the bearer variable is visible to the agent's shell (the leak path in [r5 §4]); run `codex exec --json --output-schema audit.json "audit the README for unverified claims"` and validate the output against the schema.
- Expected: shell and HTTP fail by default, stdio works [r3 §1]; truncation near 2,500 characters; a JSON result that validates; the variable's visibility unknown.
- Decides: DR-95's transport and credential path; whether a headless `exec` runs hooks under trust review.
- Cost: 1 hour plus the install. Prerequisites: Codex installed on a plan or API key (DQ-12).

**DX-17 (revised). Redis 7.0.15 as an optional transport behind the hub: per-user ACL with key and channel patterns, an explicit deny of `FLUSHALL`, `off` leaving a live connection, and a Lua lock script under key patterns.** (Streams with consumer groups and keyspace notifications are **DONE (measured 2026-10-10)**: M5 created a group with `XGROUP CREATE … MKSTREAM`, read with `XREADGROUP … BLOCK`, saw pending go 1 → 0 after `XACK`, and received `xgroup-create` and `xadd` keyspace events on `PSUBSCRIBE __keyspace@0__:mbox:*`, all over loopback TCP within one sandboxed call.)
- **Never touch the system instance.** The first draft's steps ran `ACL SETUSER` on the live `redis-server` and, if its prerequisite were skipped, a failed `--user` AUTH could fall through to the `default` user (`nopass ~* &* +@all` out of the box [r5 §2]) and `FLUSHALL` would wipe it [c1 C-5]. Start a throwaway server instead. A Unix socket is refused from sandboxed Bash (M1), so the throwaway server uses a loopback port **in the same call** (M2, M5) or runs from the author's own terminal outside Claude:
  ```sh
  redis-server --port 6390 --bind 127.0.0.1 --save '' --appendonly no --daemonize yes --pidfile /tmp/dx17.pid
  alias r='redis-cli -p 6390'
  r ACL SETUSER default off                       # the throwaway's default user, not the system's
  r ACL SETUSER agt1 on '>pw1' resetkeys resetchannels -@all '%R~org:*' '%W~proj:p:team:t:*' '&proj:p:events' +get +set +xadd +xreadgroup +xack +eval -flushall -flushdb -swapdb
  r --user agt1 --pass pw1 FLUSHALL
  r --user agt1 --pass pw1 EVAL "return redis.call('set', KEYS[1], ARGV[1], 'NX')" 1 proj:p:team:t:lock me
  r --user agt1 --pass pw1 EVAL "return redis.call('set', KEYS[1], ARGV[1], 'NX')" 1 org:lock me
  r ACL SETUSER agt1 off     # while a --user agt1 connection stays open in the same call
  r SHUTDOWN NOSAVE
  ```
  (Note that once `default` is off, the admin commands need `--user` of an admin account you create first, or run them before switching `default` off; the point of the first line is that the throwaway's `default` can be disabled without consequence.)
- Expected: `FLUSHALL` refused; the first `EVAL` sets, the second is refused by the write pattern; the open connection keeps working after `off` [r5 §2]; the Lua-under-ACL interaction is UNVERIFIED.
- Decides: whether Redis is a viable transport behind the 0.1 hub beside SQLite; the revocation procedure (`CLIENT KILL USER`). After M1 and M3 no agent process inside the sandbox would ever talk to Redis directly.
- Cost: 20 minutes. Prerequisites: none; the throwaway server only.

**DX-20. Channels: a development channel registers under both accounts and whether an event wakes an idle session (the round-1 E3).**
- Steps: copy the `webhook.ts` from the channels reference; `claude --dangerously-load-development-channels server:webhook` under each config dir (the Team org needs `channelsEnabled` from its Owner); `curl -X POST localhost:8788 -d "ping"` from outside Claude (M3: not from sandboxed Bash) while idle; retry with `MCP_PROTOCOL_NEGOTIATION=legacy` if registration fails.
- Expected: idle wake is never stated in the docs [r1b §2]; registration fails on a 2026-07-28 negotiation unless legacy is set.
- Decides: whether channels become a 0.2+ option for the human-to-agent path. Low priority.
- Cost: 45 minutes. Prerequisites: Bun or Node; DQ-4 answered for the Team side.

**DX-21. A plugin monitor's output reaches an idle session (the round-1 E5).**
- Setup: a local plugin with `monitors/monitors.json`: `[{"name":"hub","command":"sleep 60; echo HUB-PING","description":"probe"}]`.
- Expected: unknown; the docs say output "reaches Claude as notifications" and never address idle [r1b §4].
- Decides: a third wake option; not needed if DX-11 or DX-13 pass.
- Cost: 15 minutes. Prerequisites: none.

**DX-24. Posting into another session's socket from a script (research only, the round-1 E10).**
- Steps: only if DX-4 passes and DQ-8 chooses the doorbell: `strace -f -e trace=connect,write,sendto -s 2000 -p <sender pid>` during a `SendMessage`, to read the wire format. Run from the author's terminal, never from a sandboxed shell.
- Expected: an undocumented format that may change [r1b §1].
- Decides: nothing in the plan; it would let the hub inject into a local seat push-style, at the cost of depending on an undocumented format. Recorded so nobody repeats the question.
- Cost: 30 minutes. Prerequisites: DX-4 pass; DQ-8.

**DX-25. A `-p` worker launched by the credits runner loads the Diogenes hooks and MCP server with `--settings`, `--mcp-config` and `--plugin-dir`, without `--bare`.** (Not needed for 0.0: the runner claims and reports on the job's behalf, DR-104. Needed only if a credits job should itself call `dio`.)
- Steps: run one smoke job through `run.sh` with those flags and a `dio register` in its `SessionStart` hook; check `dio who` for the worker and the job's `system/init` event for the MCP server. Note that a `-p` launched from a seat's Bash runs inside that seat's sandbox (observed), so the worker's own `dio` calls would go through the spool.
- Expected: documented as the way to load them [r1 §4]; `-p` binds an inbox socket and kills async hooks at teardown.
- Decides: whether API-credit jobs can call Diogenes themselves in 0.2.
- Cost: 15 minutes and one smoke job's credits. Prerequisites: 0.1's MCP server.

## DX-18's RESULT (the listing half), 2026-10-22

Pointed to from DX-18's heading (:252). It is `roadmap/0.0/FINISH.md` step 8a, and its record is `research/done/dx18-probe-2026-10-22/`.

- **RESULT: each config dir's listing holds every live interactive session that `dio who` lists there, by pid: 18 of 18 under `~/.claude` (`max`) and 3 of 3 under `~/.claude-team` (`team`), each with `kind` `interactive`.** So step 8b's condition (F5) holds.
  - **The run.** The author ran the run sheet's two lines (`DX3-run-sheet.md`:264–265) in a plain terminal at 07:27:00 EDT. The files' mtimes read 07:27:00.39 to 07:27:00.87, and both `.err` files are empty (`management_2`'s relay of 07:27:14). In the same minute the Team seat's manager, `Ailp-team_16`, ran `src/dio who` at `dfe29c4` twice, at 07:27:15.63 and 07:27:45.84, each exit 0 with an empty stderr. The two outputs are byte-identical: 21 rows, all live. Claude Code was 2.1.307 on the Team seat. [`diogenes_1`, 2026-10-22: the listing's own `claude` was most likely 2.1.308. `~/.local/bin/claude`, the one `claude` on the merger's path and in the usual install places, has linked to 2.1.308 since 00:59:08; the terminal's own path is UNVERIFIED. By `dio who`'s `VERSION` column, the listed sessions ran 2.1.307 (15) and 2.1.308 (6).]
  - **`max`:** 18 rows, all `kind` `interactive`, with `status` `busy` 3 and `idle` 15, and an integer `pid` and a `sessionId` in each. Each matches a live `dio who` row by pid, and none is left over.
  - **`team`:** 4 rows, `interactive` 3 and `background` 1. The three `interactive` rows are `dio who`'s three live team rows, by pid. The `background` row is the DX-3 probe's conversation of 2026-10-15 (started 14:40:23 that day), with `state` `stopped`, `status` null and `pid` null. [`diogenes_1`, 2026-10-22: the row has no `status` or `pid` key at all. Its keys are `cwd`, `id`, `kind`, `name`, `sessionId`, `startedAt` and `state`, and `null` is what `jq` prints for an absent key, as in `result.txt`'s last row.] `dio who` has no row for it, which is right, since it has no process.
  - **`status` against `dio who`'s state:** in all 21 matched rows, `busy` goes with `live` and `idle` with `live-idle`.
  - **Keys:** each `max` row has `cwd`, `kind`, `name`, `pid`, `sessionId`, `startedAt` and `status`. The `team` listing's `background` row alone adds `id` and `state`. No row has `waitingFor`.
  - **The supervisor:** no process the listing started was running at 07:27:48, by `ps`. UNVERIFIED: whether one started and exited within those 48 seconds.
  - **Still open:** DX-18's other half (a `claude --bg` session left idle for an hour, then listed again), a running background session's row, and the listing from sandboxed Bash. The raw files stay local in `/home/randy/Team/PROBES/dio-probe/results/`, since they carry every session's `sessionId`, and the record gives their sha256.

## DX-13's RESULT (the gate's exit-2, 2-hour and overnight legs), 2026-10-24

Pointed to from DX-13's heading (:136). It is `roadmap/0.0/FINISH.md`'s F7, the DX-13 row of that file's gate plan (its line 93), and its record is `research/done/gate-0.0-min-2026-10-24/`, whose README calls the Team seat's manager's log of the run, `G-controls.txt`, CTL, and gives the settings variants named below. Filed by the Team seat (GF8), for the merger's review.

- **RESULT: a refusal (exit 2) and a `REARM` (exit 1) each woke the idle probe, as the measured exit 0 did (`roadmap/0.0/MIN.md`:137).** Each leg's background `dio watch` ended once, with exit 2 when its directory was removed, and with exit 1 at its 2-hour and at its 12-hour `--max`, and each exit started one turn. probe-tx's own lines show no other turn while a watch ran.
  - **The probe.** probe-tx, a fresh Team probe (F7), which the author started with `--permission-mode dontAsk`, sandboxed, under the Team variant L0R. Claude Code 2.1.310 by `dio who`'s `VERSION` (CTL 16:09:35.423Z). One process, pid 3238726, from its start at 16:07:37Z to its exit at 11:57:26Z on 10-25: the author's restarts of most seats at 20:01–20:10 EDT on 10-24 left it running (CTL 00:18:21.771Z, 00:18:21.775Z and 11:59:55.214Z). The Team seat's manager directed it, `Ailp-team_18` to the attended end and `Ailp-team_19` after. Its own lines are the record's `G-DX13-probe-tx.txt`.
  - **Exit 2.** probe-tx ran `dio watch` on the empty directory `G-DX13-exit2/` with `--every 60`, as a background task (`done X1 armed`, 16:16:28Z). `Ailp-team_18` removed the directory at 16:26:23.523Z, X1's reading plus 10 minutes. The wake's prompt entered probe-tx's transcript at 16:26:26.509Z, 3.0 s after the removal. Its `turn from=task` line reads 16:26:30Z, and the next gives `watch_exit=2` and `dio watch: during the watch, no such directory: …`.
  - **2 hours.** It then ran `--max 7200` on the empty directory `G-DX13-cap/` (X2's reading 16:29:57Z, `done X2 armed` 16:30:02Z). The directory stayed empty, its mtime still its creation's at the close (CTL 11:59:55.214Z), so only the cap could end the watch. The wake's prompt is at 18:30:00.063Z, and its turn line at 18:30:02Z, 5 s after the reading plus 7 200 s, with `watch_exit=1` and `REARM`. It re-armed itself with `--max 43200` at 18:30:20Z; X3, the seat's message if no wake came, was not sent (CTL 18:43:40.211Z).
  - **Overnight.** The `--max 43200` watch, a background child of the probe started at 18:30:18Z (CTL 18:43:40.211Z), ended with exit 1 and `REARM`. The wake's prompt is at 06:30:18.639Z on 10-25, and its turn line at 06:30:21Z, 5 s after reading-2 (18:30:16Z) plus 43 200 s (CTL 06:42:51.686Z). So nothing ended either background task before its own `--max`: the 12-hour one ran its whole 43 200 s and still woke the session. It was not re-armed, and nothing was sent to probe-tx after X2 (CTL 11:59:55.214Z).
  - **Each wake's cache tokens,** for each distinct assistant message of the wake turn, from `G-DX13-usage.txt`. `Ailp-team_19` wrote it at 06:49:52Z on 10-25 from probe-tx's transcript, which is not filed. The file writes a missing key as `missing`, and no value reads so.
    - **X1** (exit 2, about 10 minutes idle): 4 messages. `cache_read_input_tokens` 48 022, 48 388, 48 619 and 48 829 (sum 193 858); `cache_creation_input_tokens` 366, 231, 210 and 247 (sum 1 054).
    - **X2** (2 hours idle): 7 messages. The first read 0 and created 51 424; the next six read 51 424 to 52 920 and created 175 to 585. Sums: read 312 675, creation 53 102.
    - **X2b** (12 hours idle): 4 messages. The first read 0 and created 53 538; the next three read 53 538 to 53 910 and created 175 to 327. Sums: read 161 161, creation 54 237.
    - **So** the 10-minute wake read the context from the cache, and the 2-hour and 12-hour wakes, past the cache's life, wrote it again: 51 424 and 53 538 tokens for this probe, as F7 expects.
  - **Limits.** One trial per leg, on one probe. The probe's lines carry whole seconds; the prompt times are the transcript's, as `G-DX13-usage.txt` gives them.
  - **Still open, for the merger:** U7 and `--max` (`roadmap/0.0/FINISH.md`:118).

## DX-3's RESULT (the gate's F9 legs), 2026-10-24

Pointed to from DX-3's heading (:105). It is `roadmap/0.0/FINISH.md`'s F9 (that file's line 158), run before M4's trials, and its record is `research/done/gate-0.0-min-2026-10-24/`, with CTL as above. It answers what DX-3's partial RESULT left for the gate (:123): the sandboxed (c) and (d), and S1 line 3's variables in a probe's own Bash. Filed by the Team seat (GF8), for the merger's review.

- **RESULT: (c) yes: from sandboxed Bash, `dio who` listed the control's 24 sessions, on both accounts. (d) no session confirmed: there every row read `unknown (checking)`, the probe's own included.** So, as `dio` stands at GATE_SHA, its process check confirms no session from sandboxed Bash. In each probe's own Bash all five variables were set, the session id among them, except `CLAUDE_CONFIG_DIR` in the Max probe.
  - **The run.** probe-td (Team, variant G-M4TR) and probe-mw (Max, variant G-M4MR), each started by the author with `--permission-mode dontAsk`, sandboxed, ran the plan's F9 step at 15:40:43Z and 15:40:58Z, on `Ailp-team_18`'s message. Both ran Claude Code 2.1.310 by `dio who`'s `VERSION`, as their `CLAUDE_CODE_EXECPATH` agrees. `dio` was GATE_SHA's: probe-td ran the Team clone's `src/dio`, probe-mw the Workspace clone's. The control is `Ailp-team_18`'s unsandboxed `dio who` at 15:40:45.615Z (CTL; `G-F9-team-seat-dio-who.txt`), on Claude Code 2.1.308 by `dio who`'s `VERSION`.
  - **(c)** Each probe's `dio who` exited 0 and listed 24 rows: the control's 24 sessions, equal in every column but `STATE` (account, name, pid, start, version and socket). So sandboxed Bash read the sessions files under both `~/.claude-team` and `~/.claude`. Both variants also allow `Read(~/.claude-team/sessions/*.json)` and `Read(~/.claude/sessions/*.json)`; no variant without those rules was run.
  - **(d)** Every row read `unknown (checking)`, where the control read each `live` or `live-idle`. The output, which takes stderr too, holds `dio: the grace cache could not be written, so the grace was not started: Read-only file system` 24 times, as many as the rows. The two probes' outputs are byte-identical (`G-F9-probe-td-dio-who.txt`, `G-F9-probe-mw-dio-who.txt`). `dio who` does not say which part of DR-108's check failed (the `/proc/<pid>/stat` read, its start time or the socket file), so whether the host's `/proc` is visible from sandboxed Bash is still not measured.
  - **The five variables,** each printed as `${NAME:-UNSET}` (the plan's F9 step 1):
    - `CLAUDE_CODE_MESSAGING_SOCKET`: probe-td `/run/user/1000/cc-socks/3146018.sock`, probe-mw `/run/user/1000/cc-socks/3147973.sock`, each the socket in its own `dio who` row.
    - `CLAUDE_PID`: 3146018 and 3147973, each the pid in its own row.
    - `CLAUDE_CODE_SESSION_ID`: present in both. Its value is not written here.
    - `CLAUDE_CODE_EXECPATH`: `/home/randy/.local/share/claude/versions/2.1.310` in both.
    - `CLAUDE_CONFIG_DIR`: probe-td `/home/randy/.claude-team`; probe-mw UNSET.
  - **The sandbox leg.** probe-mw's sandboxed `touch` into `inbox/team/`, which F9 expected to be refused, exited 0 at 15:42:39Z, and the file landed. The merger's reading (`G-F9-touch-docs.txt`, from the sandboxing docs it fetched at 15:45:23.796Z): G-M4M's allow rule `Edit(//home/randy/.local/share/diogenes/inbox/**)` gives sandboxed Bash write access there, as `allowWrite` would. No variant left the path closed, so the leg measured no refusal. Its place in the record and in U8 is the record's open point 1.
  - **The classifier.** F9 watched for a safety classifier's stop. None is in either probe's lines or in CTL.
  - **Still open:** whether the host's `/proc` is visible from sandboxed Bash; the grace cache in the sandbox, the merger's to fix (the record's open point 4); the unnamed session's move to the background, not re-run, since all probes were named (F9).
