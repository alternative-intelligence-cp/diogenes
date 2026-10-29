"""docs/USING.md (MIN.md steps 4 and 5): its nine binding rules against MIN.md's, the caveats'
labels, the one printf line run against a scratch inbox, the seat's find line, and the roster
entry's removal against an entry that dio register wrote.

Every documented line runs under /bin/bash with HOME set to a scratch home inside the test's
temporary tree, which holds .local/share/diogenes/inbox/max/ and inbox/team/ at mode 0700. Each
line names the zone through ~, and run_line refuses one that does not, so no run reaches the real
inbox. Each bash gets /dev/null on stdin: at shell level 1, `bash -c` with a socket on stdin takes
itself for a remote shell and reads /etc/bash.bashrc and ~/.bashrc, so what the test's bash reads
would depend on what stdin the test was given. No test sleeps: dio watch runs in-process on an
injected clock whose sleep runs the line.

Run from the repository root, with TMPDIR set to a scratch directory (tests/README.md):

    TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -v
"""

import contextlib
import io
import os
import re
import shutil
import subprocess
import time
import unittest
from datetime import datetime, timedelta, timezone
from unittest import mock

import fixtures
from fixtures import REPOSITORY, WatchClock, World

dio = fixtures.load_dio()
USING = os.path.join(REPOSITORY, 'docs', 'USING.md')
MIN = os.path.join(REPOSITORY, 'meta', 'roadmap', '0.0', 'MIN.md')
BASH = '/bin/bash'
# A POSIX TZ 14 hours east of UTC, so a line that named the local time would name another hour.
FAR_ZONE = 'DIO-14'
FAR_OFFSET = timedelta(hours=14)
SECOND = 10 ** 9
CALL = re.compile(r'^(?:[0-9]+ +)?([a-z0-9_]+)\(')

# The filled-in example's parts (USING.md, "The one printf line").
SENDER, SUBJECT, ACCOUNT = 'probe-t_1', 'ready-to-merge', 'max'
LINES = ['to: merger', 'team/diogenes-0.0-using-template is verified.', 'It is ready to merge.']


def setUpModule():
    fixtures.require_tmpdir()


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def section(text, start, end):
    return text[text.index(start):text.index(end)]


def sh_lines(text):
    """The one-line bodies of the ```sh blocks in `text`."""
    found = re.findall(r'^```sh\n(.*?)^```$', text, re.M | re.S)
    for body in found:
        assert body.count('\n') == 1, 'a documented line is one line: %r' % body
    return [body.rstrip('\n') for body in found]


PRINTF, FIND, RM = "printf '", ' -newermt ', 'rm -- '


def documented(marker, placeholder):
    """The one ```sh line in USING.md that holds `marker` and holds (or, with a false
    `placeholder`, lacks) the text `<`. A line is found by what it holds, not by how it
    starts, so a changed line is still the one that is run."""
    lines = [line for line in sh_lines(read(USING)) if marker in line
             and (('<' in line) == placeholder)]
    assert len(lines) == 1, (marker, lines)
    return lines[0]


def quoted(lines):
    """The lines as single-quoted shell words, a single quote written '\\''."""
    return ' '.join("'%s'" % line.replace("'", "'\\''") for line in lines)


def utc_minute(moment=None):
    return (moment or datetime.now(timezone.utc)).strftime('%Y-%m-%dT%H%M')


def never_sleep(seconds):
    raise AssertionError('a test reached the real sleep (%r s)' % seconds)


class Base(unittest.TestCase):
    """A scratch home, inside the temporary tree, holding the zone's inbox at mode 0700."""

    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)
        self.home = self.world.home
        self.zone = os.path.join(self.home, '.local', 'share', 'diogenes')
        self.inbox = {}
        for account in ('max', 'team'):
            self.inbox[account] = os.path.join(self.zone, 'inbox', account)
            os.makedirs(self.inbox[account])
        for directory in (self.zone, os.path.dirname(self.inbox['max']),
                          self.inbox['max'], self.inbox['team']):
            os.chmod(directory, 0o700)
        patcher = mock.patch.dict(os.environ, {'HOME': self.home})
        patcher.start()
        self.addCleanup(patcher.stop)

    def environment(self, **extra):
        environment = {'HOME': self.home, 'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8',
                       'TZ': FAR_ZONE}
        environment.update(extra)
        return environment

    def run_line(self, line, command=(BASH, '-c'), **extra):
        """Run a documented line under bash, with HOME at the scratch home and /dev/null on
        stdin. It must name the zone through ~, so the scratch home holds every path it writes."""
        if '.local/share/diogenes' in line:
            self.assertIn('~/.local/share/diogenes/', line)
            self.assertNotIn('/home/', line)
        tmpdir = os.path.realpath(os.environ['TMPDIR'])
        self.assertTrue(os.path.realpath(self.home).startswith(tmpdir + os.sep))
        expanded = subprocess.run([BASH, '-c', 'printf %s ~/.local/share/diogenes/inbox/'],
                                  env=self.environment(**extra), stdin=subprocess.DEVNULL,
                                  capture_output=True, text=True, timeout=60).stdout
        self.assertEqual(expanded, os.path.join(self.zone, 'inbox') + '/')
        return subprocess.run(list(command) + [line], env=self.environment(**extra),
                              stdin=subprocess.DEVNULL, cwd=self.world.base, capture_output=True,
                              text=True, timeout=60)

    def names(self, account):
        return sorted(os.listdir(self.inbox[account]))


class RuleTests(unittest.TestCase):
    def test_the_nine_rules_are_min_md_s_word_for_word_in_its_order_but_rule_4_names_the_merger_line(self):
        found = dict(re.findall(r'^([1-9])\. (.+)$', section(
            read(MIN), '**`USING.md`, binding rules.**', '- **Note 2026-10-15, Team seat (D2b):** for'), re.M))
        rules = re.findall(r'^([1-9])\. (.+)$', section(
            read(USING), '## The binding rules', '### Four caveats'), re.M)
        self.assertEqual([number for number, _ in rules], [str(n) for n in range(1, 10)])
        self.assertEqual(sorted(found), [str(n) for n in range(1, 10)])
        old = 'for this repository it is `diogenes_0`.'
        new = ('for this repository it is the holder of the `merger` line of '
               '[`meta/ROLES.md`](../meta/ROLES.md) (`dio who --address merger`).')
        for number, text in rules:
            with self.subTest(rule=number):
                if number == '4':
                    self.assertEqual(found[number].count(old), 1)
                    self.assertEqual(text, found[number].replace(old, new))
                else:
                    self.assertEqual(text, found[number])

    def test_rule_4_s_wording_is_a_decision_with_min_md_s_two_precedents(self):
        decision = section(read(USING), '- **U1.', '- **U2.')
        text = ' '.join(read(MIN).split())
        for quote in ('Decision 3\'s starting lines below name `_1`, the holder when this plan was written',
                      'the holder when they were written; the `merger` line\'s holder acts in its place',
                      'for this repository it is `diogenes_0`'):
            with self.subTest(quote=quote):
                self.assertIn(quote, text)  # MIN.md says it
                self.assertIn(quote, ' '.join(decision.split()))  # and U1 quotes it
        self.assertIn('11:11:52', decision)

    def test_each_caveat_is_min_md_s_and_carries_its_labels_ii_and_iii_part_by_part_from_the_gate(self):
        # FINISH.md:118 and "The gate's merge" (U8): (ii) and (iii) take the gate's labels part by
        # part, departing from MIN.md's note, which keeps its own, as U1 departs from rule 4.
        note = section(read(MIN), '- **Note 2026-10-15, Team seat (D2b):** for `docs/USING.md`',
                       '**The task template, required lines, in order:**')
        caveats = section(read(USING), '### Four caveats', '## Messages')
        labels = {'(i)': ('Measured from working seats', ['*Measured*']),
                  '(ii)': ('This is documented, not measured', [
                      '**The `Edit(…)` rule:** *Measured* both ways, once each, at the gate.',
                      "(the record's M2, W)", "(`REPLY write=written`; the record's M4, \"The round\")",
                      '**"never `Write(...)`":** *Documented, not measured*: no leg at the gate '
                      'tested a `Write(...)` rule.',
                      "**The gate's stop:** under dontAsk, a sandboxed Bash write needs a permission "
                      'rule for its target too. *Measured* at 2.1.310 on the results directory',
                      '(the record\'s "The stop, and the R variants")',
                      '**The inbox:** *A reading, not a measurement*: it follows by the same rule, so '
                      "a dontAsk seat needs the inbox's rule for either route, the Write tool or Bash.",
                      '*Documented, not measured*. Related:']),
                  '(iii)': ('This is by the documentation, not measured', [
                      '**The Write-tool route:** *Measured* once, at the gate.',
                      '*Measured* once with the rule: probe-mw\'s sandboxed `touch` into '
                      '`inbox/team/` exited 0, and the file landed (M4\'s TOUCH, 15:42:39Z)',
                      'The reason is *Documented*', "the record's `G-F9-touch-docs.txt`",
                      "**Without the rule, its Bash's refusal:** *By the documentation, not measured*",
                      'No closed path was measured']),
                  '(iv)': (None, ['*Documented*: `MIN.md`\'s note gives (iv) no label of its own'])}
        for mark, (min_label, ours_labels) in labels.items():
            with self.subTest(caveat=mark):
                # The bold lead ends at the ** that a space follows: (ii)'s lead holds a ** in code.
                lead = r'\*\*%s (.+?)\*\*(?= )' % re.escape(mark)
                ours = re.search(r'^- ' + lead, caveats, re.M)
                theirs = re.search(r'^  - ' + lead + r'(.*)$', note, re.M)
                self.assertEqual(ours.group(1), theirs.group(1))  # the caveat itself, word for word
                block = re.search(r'^- \*\*%s .*?(?=^- \*\*\(|\Z)' % re.escape(mark), caveats,
                                  re.M | re.S).group(0)
                for label in ours_labels:
                    self.assertIn(label, ' '.join(block.split()))
                if min_label:
                    self.assertIn(min_label, theirs.group(2))  # MIN.md's note keeps its own label
                else:
                    self.assertNotIn('measured', theirs.group(2).lower())
        intro = ' '.join(section(caveats, '### Four caveats', '- **(i)').split())
        self.assertIn("(ii) and (iii) are labelled part by part by what the gate measured, departing "
                      "from the note's labels as decision U1 departs from rule 4, by the merger's U8",
                      intro)

    def test_u7_gives_the_gate_legs_answer_for_exits_1_and_2_labelled_measured_with_its_source(self):
        # FINISH.md's U7 ("The gate's merge"), citing DX-13's RESULT; the cache's hour is a
        # reading, not a measurement (the merger's term 2 on D9's brief).
        text = ' '.join(read(USING).split())
        part = section(text, '- **What is measured.**', "### The seat's rule")
        for words in ('The gate\'s legs answered what that left (`MIN.md`, step 3\'s note, "For the '
                      'gate"): an exit with status 1 or 2 wakes an idle seat in the same way. '
                      '*Measured* once each, on probe-tx',
                      "(DX-13's RESULT (the gate's exit-2, 2-hour and overnight legs))",
                      'exit 2 woke it 6.5 s after its watched directory was removed',
                      'exit 1 woke it 5 s after each cap, at 2 hours and at 12 hours',
                      "a re-arm past the cache's life writes the context again",
                      '51 424 and 53 538 tokens',
                      'That the cache lives an hour is a reading, not a measurement'):
            with self.subTest(words=words):
                self.assertIn(words, part)
        self.assertNotIn('is left to the gate', part)

    def test_u9_s_three_notes_on_dio_who_carry_their_labels_and_sources(self):
        # FINISH.md's U9 ("The gate's merge"), with the merger's term 4 on D9's brief: a plain
        # kill measured once (M6's first run), kill -9 once (M6b), a crash not, nor the remover.
        text = ' '.join(read(USING).split())
        part = section(text, '## Presence: `dio who`', '### Removing a roster entry')
        for words in ('**A session that ends cleanly, or by a plain `kill`, leaves no row.**',
                      "For a plain `kill`: *Measured* once, at the gate's first M6 run (the "
                      "record's M6)",
                      'For a clean exit: *Measured* once, untimed',
                      'Only a `kill -9` or a crash leaves the file, and then the row reads '
                      '`unknown (checking)` and then `gone`: *Measured* once for a `kill -9`, by '
                      'M6b (probe-mk, Claude Code 2.1.310); a crash is *not measured*.',
                      '**A `gone` row lasts only until the leftover file is removed.** *Measured* '
                      "once, by M6b's note (the record's `G-M6b-merger-note.txt`)",
                      'What removed it is *not measured*',
                      '**Run `dio who` unsandboxed.** From sandboxed Bash, every row reads '
                      '`unknown (checking)`',
                      "*Measured* at the gate's F9 legs",
                      "DX-3's RESULT, (d)"):
            with self.subTest(words=words):
                self.assertIn(words, part)

    def test_the_printf_line_carries_the_gates_note_for_dontask_seats(self):
        # FINISH.md's U8, open point 2 (U74): the line as written was refused at its one try under
        # dontAsk, and such a seat makes the file with the Write tool, after checking the name.
        text = ' '.join(read(USING).split())
        part = section(text, '### The one `printf` line', '### Made in place')
        for words in ('**A seat started in dontAsk can have the line itself refused.** *Measured* '
                      'once, at the gate (the record\'s "U74\'s outcome, for U8")',
                      '(G-M4TR), on Claude Code 2.1.310, ran the line once as written, and it was '
                      'refused before it ran',
                      'no file landed',
                      'one `printf … > <path>` with no subshell and no `set -C` ran five times',
                      'Such a seat makes the file with the Write tool instead, as the next bullet '
                      'says, after checking that no file has that name.'):
            with self.subTest(words=words):
                self.assertIn(words, part)
        notes = re.findall(r'^- \*\*(.+?)\*\*', section(read(USING), '### The one `printf` line',
                                                       '### Made in place'), re.M)
        self.assertEqual(notes[notes.index('A seat started in dontAsk can have the line itself '
                                           'refused.') + 1],
                         'A seat whose Bash cannot write the zone,')  # "the next bullet"

    def test_the_file_carries_the_six_items_from_min_md_s_notes_and_its_decisions(self):
        text = ' '.join(read(USING).split())
        for words in ('After every exit, `WAKE` or `REARM`, re-arm first',  # decision 18
                      'A seat points `dio watch` only at its own account\'s inbox',  # rule 7
                      '### Made in place, never moved in',  # D4v's finding 7
                      '`REARM <dir>` | The cap passed with no new file. **This is not an error.**',
                      '**A step back of the real clock** by more than 2 s during a watch can hide '
                      'later files from the watch, and from the seat\'s rule alike',  # finding 6
                      '### Removing a roster entry'):  # step 1's note
            with self.subTest(words=words):
                self.assertIn(words, text)
        for decision in ('U1', 'U2', 'U3', 'U4', 'U5', 'U6'):
            self.assertEqual(text.count('- **%s. ' % decision), 1, decision)

    def test_the_write_tool_route_is_labelled_measured_with_what_was_measured(self):
        # MIN.md's note after step 5 (D5v's finding 11), with the merger's term: the claim is
        # labelled and says what was measured. From a sandboxed seat, the gate's M4 measured the
        # route once (FINISH.md, "The gate's merge", U8), and not whether a temporary file came first.
        text = ' '.join(read(USING).split())
        route = section(text, '- **A seat whose Bash cannot write the zone,**', '### Made in place')
        for words in ('*Measured* by the merger at 04:54:26 on 2026-10-18, under Claude Code 2.1.301, '
                      "from a Max seat's Write tool into a scratch directory, by inotify",
                      'created `<name>.tmp.<pid>.<12 hex digits>` in that directory',
                      'renamed it to `<name>` 8 ms later',
                      'a watch that polls in that window wakes under the temporary name',
                      'From a sandboxed seat, the seat this route is for, the gate measured it once',
                      "woke on the reply's final name, not a `<name>.tmp.<pid>.<12 hex digits>` name",
                      'Whether that tool made a temporary file first, in a sandboxed seat, is not '
                      'measured'):
            with self.subTest(words=words):
                self.assertIn(words, route)
        self.assertIn('it writes `<name>.tmp.<pid>.<12 hex digits>` in the target directory and '
                      'renames it to `<name>` about 8 ms later', ' '.join(read(MIN).split()))

    def test_no_line_of_the_file_ends_in_whitespace(self):
        # D5v's finding 10: git diff --check flagged two whitespace-only lines.
        for number, line in enumerate(read(USING).split('\n'), 1):
            with self.subTest(line=number):
                self.assertEqual(line, line.rstrip())


class PrintfTests(Base):
    def example(self):
        return documented(PRINTF, placeholder=False)

    def template(self):
        return documented(PRINTF, placeholder=True)

    def filled(self, lines, account=ACCOUNT, sender=SENDER, subject=SUBJECT):
        """The template, with its placeholders filled in."""
        line = self.template()
        self.assertEqual(line.count("'to: <receiver>' '<line>' '<line>'"), 1)
        return (line.replace("'to: <receiver>' '<line>' '<line>'", quoted(lines))
                .replace('<account>', account).replace('<sender>', sender)
                .replace('<subject>', subject))

    def test_the_filled_in_example_is_the_template_with_its_parts(self):
        self.assertEqual(self.example(), self.filled(LINES))

    def test_the_example_writes_one_message_in_place_named_in_utc_with_its_lines_as_its_bytes(self):
        before = datetime.now(timezone.utc)
        result = self.run_line(self.example())
        after = datetime.now(timezone.utc)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, '', ''))
        names = self.names('max')
        self.assertEqual(len(names), 1, names)
        self.assertIn(names[0], {'%s-%s-%s.md' % (utc_minute(moment), SENDER, SUBJECT)
                                 for moment in (before, after)})
        # TZ is 14 hours east of UTC, so the local time names another hour.
        self.assertNotIn(names[0][:15], {utc_minute(moment + FAR_OFFSET) for moment in (before, after)})
        with open(os.path.join(self.inbox['max'], names[0]), 'rb') as f:
            self.assertEqual(f.read(), ('\n'.join(LINES) + '\n').encode())
        self.assertEqual(self.names('team'), [])  # the other account's inbox only

    def test_each_quoted_line_is_written_byte_for_byte_a_single_quote_as_written_in_the_table(self):
        lines = ['to: merger', '100% done, %s and %d stay', 'a \\n and a \\\\ stay', '$HOME and `date` stay',
                 "it's here", 'café']
        result = self.run_line(self.filled(lines, subject='bytes'))
        self.assertEqual(result.returncode, 0, result.stderr)
        [name] = self.names('max')
        with open(os.path.join(self.inbox['max'], name), 'rb') as f:
            self.assertEqual(f.read(), ('\n'.join(lines) + '\n').encode('utf-8'))

    def test_a_second_message_with_the_same_name_is_refused_and_the_first_stays_as_it_was(self):
        first = b'to: merger\nthe first message\n'
        now = datetime.now(timezone.utc)
        taken = ['%s-%s-%s.md' % (utc_minute(moment), SENDER, SUBJECT)
                 for moment in (now, now + timedelta(minutes=1))]  # whichever minute the line reads
        for name in taken:
            with open(os.path.join(self.inbox['max'], name), 'wb') as f:
                f.write(first)
        result = self.run_line(self.example())
        self.assertIn(utc_minute(), {name[:15] for name in taken}, 'the run took over a minute')
        self.assertEqual(result.returncode, 1)
        self.assertIn('cannot overwrite existing file', result.stderr)
        self.assertEqual(self.names('max'), sorted(taken))
        for name in taken:
            with open(os.path.join(self.inbox['max'], name), 'rb') as f:
                self.assertEqual(f.read(), first)

    def test_set_c_refuses_a_link_to_a_regular_file_or_a_dangling_link_and_writes_through_one_to_dev_null(self):
        # Decision U4's limit: a name held by a link to something that is not a regular file.
        target = self.world.write(self.world.base, 'target.md', b'the target\n')
        now = datetime.now(timezone.utc)
        for case, link_to, status in (('a link to a regular file', target, 1),
                                      ('a dangling link', os.path.join(self.world.base, 'nowhere.md'), 1),
                                      ('a link to /dev/null', os.devnull, 0)):
            with self.subTest(case=case):
                for name in os.listdir(self.inbox['max']):
                    os.unlink(os.path.join(self.inbox['max'], name))
                links = ['%s-%s-%s.md' % (utc_minute(moment), SENDER, SUBJECT)
                         for moment in (now, now + timedelta(minutes=1))]
                for name in links:
                    os.symlink(link_to, os.path.join(self.inbox['max'], name))
                result = self.run_line(self.example())
                self.assertEqual(result.returncode, status, result.stderr)
                self.assertEqual(self.names('max'), sorted(links))
                for name in links:
                    self.assertTrue(os.path.islink(os.path.join(self.inbox['max'], name)))
        with open(target, 'rb') as f:
            self.assertEqual(f.read(), b'the target\n')

    def test_the_line_opens_the_final_name_once_with_o_excl_and_never_renames_or_links(self):
        # Decision U3, under strace: the file is made in place, at its final name.
        self.assertIsNotNone(shutil.which('strace'), 'strace is required')
        trace = os.path.join(self.world.base, 'printf.trace')
        calls = 'trace=open,openat,creat,rename,renameat,renameat2,link,linkat,symlink,symlinkat'
        result = self.run_line(self.example(), command=('strace', '-f', '-e', calls, '-o', trace,
                                                        BASH, '-c'))
        self.assertEqual(result.returncode, 0, result.stderr)
        [name] = self.names('max')
        with open(trace, encoding='utf-8', errors='replace') as f:
            lines = [line for line in f.read().splitlines() if CALL.match(line)]
        moves = [line for line in lines if CALL.match(line).group(1) not in ('open', 'openat')]
        self.assertEqual(moves, [])
        named = [line for line in lines if self.inbox['max'] in line]
        self.assertEqual(len(named), 1, named)
        self.assertIn('"%s"' % os.path.join(self.inbox['max'], name), named[0])
        for flag in ('O_WRONLY', 'O_CREAT', 'O_EXCL'):
            self.assertIn(flag, named[0])
        self.assertNotIn('O_TRUNC', named[0])
        self.assertRegex(named[0], r'= [0-9]+$')

    def test_a_message_the_line_writes_wakes_a_dio_watch_on_the_scratch_inbox(self):
        # Files present at the start, as in an inbox that already holds messages, never wake it.
        for name, offset in (('2026-10-16T0700-probe-m_1-old.md', -3600), ('present.md', 3600)):
            path = os.path.join(self.inbox['max'], name)
            with open(path, 'wb') as f:
                f.write(b'to: merger\nan older message\n')
            moment = time.time_ns() + offset * SECOND
            os.utime(path, ns=(moment, moment))
        example = self.example()
        test = self

        class Clock:
            """The real clock for the start, so the message's own mtime counts; a monotonic
            clock that moves only in sleep(), whose first call runs the documented line."""

            def __init__(self):
                self.sleeps, self.monotonic = [], 0

            @staticmethod
            def real_ns():
                return time.time_ns()

            def monotonic_ns(self):
                return self.monotonic

            def sleep(self, seconds):
                self.sleeps.append(seconds)
                self.monotonic += round(seconds * SECOND)
                if len(self.sleeps) == 1:
                    test.assertEqual(test.run_line(example).returncode, 0)

        clock = Clock()
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(dio.SystemClock, 'sleep', staticmethod(never_sleep)), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            status = dio.main(['watch', self.inbox['max'], '--every', '60', '--max', '120'], clock=clock)
        [name] = [name for name in self.names('max') if name.endswith('-%s-%s.md' % (SENDER, SUBJECT))]
        self.assertEqual((status, out.getvalue(), err.getvalue()),
                         (0, 'WAKE %s\n' % os.path.join(self.inbox['max'], name), ''))
        self.assertEqual(clock.sleeps, [60.0])


class SeatRuleTests(Base):
    """The seat's read (USING.md, "The seat's rule", step 3). Each run defines a shell function
    named find, which fails, in the same shell just before the documented line, as Claude Code's
    Bash tool defines one that runs bfs: `command find` must run the find on PATH instead. (The
    function is not given through BASH_ENV, which a bash with a socket on stdin skips.)"""

    TRAP = 'find() { echo "the shell function find ran" >&2; return 97; }; '

    def find_line(self, reading, account='team'):
        line = documented(FIND, placeholder=True)
        for placeholder in ('<own account>', '<reading>'):
            self.assertEqual(line.count(placeholder), 1, placeholder)
        return line.replace('<own account>', account).replace('<reading>', reading)

    def run_find(self, line):
        trapped = self.run_line(self.TRAP + 'find; echo "after the trap"')
        self.assertEqual((trapped.stdout, trapped.stderr),
                         ('after the trap\n', 'the shell function find ran\n'))  # the trap works
        return self.run_line(self.TRAP + line)

    def stamp(self, path, mtime_ns, symlink=False):
        os.utime(path, ns=(mtime_ns, mtime_ns), follow_symlinks=not symlink)

    def test_the_find_line_lists_regular_files_strictly_later_than_the_reading_less_2_seconds(self):
        reading = '2026-10-16T07:00:00Z'
        at = int(datetime(2026, 10, 16, 7, 0, 0, tzinfo=timezone.utc).timestamp()) * SECOND
        inbox = self.inbox['team']
        for name, mtime in (('a-3s-before.md', at - 3 * SECOND), ('b-exactly-2s-before.md', at - 2 * SECOND),
                            ('c-1ns-inside.md', at - 2 * SECOND + 1), ('d-5s-after.md', at + 5 * SECOND)):
            self.stamp(self.world.write(inbox, name, b'to: team-seat\n'), mtime)
        os.symlink('d-5s-after.md', os.path.join(inbox, 'e-link.md'))
        self.stamp(os.path.join(inbox, 'e-link.md'), at + 5 * SECOND, symlink=True)
        os.mkdir(os.path.join(inbox, 'f-sub'))
        self.stamp(self.world.write(os.path.join(inbox, 'f-sub'), 'nested.md', b'x\n'), at + 5 * SECOND)
        self.stamp(os.path.join(inbox, 'f-sub'), at + 5 * SECOND)
        result = self.run_find(self.find_line(reading))
        self.assertEqual((result.returncode, result.stderr), (0, ''))
        self.assertEqual(result.stdout, ''.join('%s\n' % os.path.join(inbox, name)
                                                for name in ('c-1ns-inside.md', 'd-5s-after.md')))

    def test_the_find_line_reads_every_file_the_re_arm_gap_hides_from_dio_watch(self):
        # GapTests' case (test_watch.py), with the documented line as the seat's read.
        inbox = self.inbox['team']
        clock = WatchClock()

        def drop(name, mtime_ns=None):
            path = self.world.write(inbox, name, b'to: team-seat\n')
            self.stamp(path, clock.real_ns() if mtime_ns is None else mtime_ns)

        def watch(*flags):
            out = io.StringIO()
            with mock.patch.object(dio.SystemClock, 'sleep', staticmethod(never_sleep)), \
                    contextlib.redirect_stdout(out):
                status = dio.main(['watch', inbox] + list(flags), clock=clock)
            return status, out.getvalue()

        drop('old.md', clock.real_ns() - 3600 * SECOND)
        first_reading = clock.real_ns()  # step 1: the seat reads the clock, then arms
        clock.at(1, lambda: drop('first.md'))
        self.assertEqual(watch(), (0, 'WAKE %s\n' % os.path.join(inbox, 'first.md')))
        clock.advance(5)
        drop('gap.md')  # between the first watch's exit and the next start
        clock.advance(5)
        second_reading = clock.real_ns()
        drop('window.md', second_reading + 1000)  # after that reading, before the next listing
        self.assertEqual(watch('--max', '300'), (1, 'REARM %s\n' % inbox))
        as_logged = datetime.fromtimestamp(first_reading // SECOND, timezone.utc).strftime(
            '%Y-%m-%dT%H:%M:%SZ')  # date -u +%FT%TZ: to the second
        result = self.run_find(self.find_line(as_logged))
        self.assertEqual((result.returncode, result.stderr), (0, ''))
        self.assertEqual(result.stdout, ''.join('%s\n' % os.path.join(inbox, name)
                                                for name in ('first.md', 'gap.md', 'window.md')))


class RosterRemovalTests(Base):
    def who_rows(self, pid):
        result = self.world.run('who')
        self.assertEqual(result.returncode, 0, result.stderr)
        return [line for line in result.stdout.splitlines() if ' %d ' % pid in line]

    def test_the_rm_line_removes_the_entry_dio_register_wrote_and_the_grace_entry_goes_with_it(self):
        for config in ('.claude', '.claude-team'):
            os.makedirs(os.path.join(self.home, config, 'sessions'))
        roster = os.path.join(self.zone, 'roster')
        cache = os.path.join(self.zone, 'cache')
        for case, config_env, config_dir in (
                ('CLAUDE_CONFIG_DIR set', {'CLAUDE_CONFIG_DIR': os.path.join(self.home, '.claude-team')},
                 os.path.join(self.home, '.claude-team')),
                ('CLAUDE_CONFIG_DIR unset', {}, os.path.join(self.home, '.claude'))):
            with self.subTest(case=case):
                pid = self.world.live_process()
                child = self.world.children[-1]
                sock = self.world.listen('%d.sock' % pid)
                result = self.world.run('register', 'probe-t_5', CLAUDE_CODE_MESSAGING_SOCKET=sock,
                                        **config_env)
                self.assertEqual(result.returncode, 0, result.stderr)
                entry = '%s-%d.json' % (dio.config_key(config_dir), pid)
                self.assertEqual(os.listdir(roster), [entry])
                [row] = self.who_rows(pid)
                self.assertTrue(row.endswith('live  fallback: register'), row)
                child.stdin.close()
                child.wait()  # the session ends; its entry stays
                [row] = self.who_rows(pid)
                self.assertTrue(row.endswith('unknown (checking)  fallback: register'), row)
                grace = 'grace-%s-%d.json' % (dio.config_key(config_dir), pid)
                self.assertIn(grace, os.listdir(cache))
                line = documented(RM, placeholder=True)
                self.assertEqual(line.count('<pid>'), 1)
                result = self.run_line(line.replace('<pid>', str(pid)), **config_env)
                self.assertEqual((result.returncode, result.stderr), (0, ''))
                self.assertEqual(os.listdir(roster), [])
                self.assertEqual(self.who_rows(pid), [])
                self.assertNotIn(grace, os.listdir(cache))

    def test_a_trailing_slash_gives_the_rm_line_another_key_and_the_ls_line_shows_the_entry(self):
        # MIN.md's note after step 5: the line hashes $CLAUDE_CONFIG_DIR as it is set, while dio
        # register keys the entry by its abspath, which drops the slash.
        os.makedirs(os.path.join(self.home, '.claude-team', 'sessions'))
        roster = os.path.join(self.zone, 'roster')
        config_dir = os.path.join(self.home, '.claude-team')
        config_env = {'CLAUDE_CONFIG_DIR': config_dir + '/'}
        pid = self.world.live_process()
        sock = self.world.listen('%d.sock' % pid)
        result = self.world.run('register', 'probe-t_5', CLAUDE_CODE_MESSAGING_SOCKET=sock, **config_env)
        self.assertEqual(result.returncode, 0, result.stderr)
        entry = '%s-%d.json' % (dio.config_key(config_dir), pid)
        self.assertEqual(os.listdir(roster), [entry])
        self.assertNotEqual(dio.config_key(config_dir + '/'), dio.config_key(config_dir))
        result = self.run_line(documented(RM, placeholder=True).replace('<pid>', str(pid)), **config_env)
        self.assertEqual(result.returncode, 1)
        self.assertIn('No such file or directory', result.stderr)
        self.assertEqual(os.listdir(roster), [entry])  # the entry stays
        ls = 'ls ~/.local/share/diogenes/roster/'
        self.assertIn('`%s`' % ls, read(USING))
        result = self.run_line(ls, **config_env)
        self.assertEqual((result.returncode, result.stdout), (0, entry + '\n'))


if __name__ == '__main__':
    unittest.main()
