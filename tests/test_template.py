"""docs/TASK-TEMPLATE.md (MIN.md step 5): the nine required lines in MIN.md's order, what each
holds, who fills it, where and when, decision 5's values, the poster check and its refusal, and
D1v's finding 2 as settled, against meta/tasks/README.md. The poster check's git line runs in a
scratch repository made by the test, whose git reads no user or system configuration.

Run from the repository root, with TMPDIR set to a scratch directory (tests/README.md):

    TMPDIR=<scratch dir> /usr/bin/python3 -I -B -m unittest discover -s tests -v
"""

import os
import re
import subprocess
import unittest

import fixtures
from fixtures import REPOSITORY, World

dio = fixtures.load_dio()
TEMPLATE = os.path.join(REPOSITORY, 'docs', 'TASK-TEMPLATE.md')
MIN = os.path.join(REPOSITORY, 'meta', 'roadmap', '0.0', 'MIN.md')
FINISH = os.path.join(REPOSITORY, 'meta', 'roadmap', '0.0', 'FINISH.md')
TASKS_README = os.path.join(REPOSITORY, 'meta', 'tasks', 'README.md')
COLUMNS = ['Line', 'What it holds', 'Who fills it', 'Where', 'When']
POSTED = ('spec', 'posted-by', 'cross-account', 'room-at-post', 'acceptance')


def setUpModule():
    fixtures.require_tmpdir()


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def required_lines():
    """MIN.md's list: "The task template, required lines, in order: `spec`, ..., `merged-at`."""
    text = read(MIN)
    listed = text.split('**The task template, required lines, in order:**', 1)[1].split('. M3 gates', 1)[0]
    return re.findall(r'`([a-z-]+)`', listed)


def template_lines():
    """The task lines of the template: those in the first fenced block of the file it shows."""
    shown = re.search(r'^````markdown\n(.*?)^````$', read(TEMPLATE), re.M | re.S).group(1)
    block = re.search(r'^```text\n(.*?)^```$', shown, re.M | re.S).group(1)
    return shown, block.splitlines()


def table():
    """{line: {column: cell}} from the table under "## Each line", and the lines in its order."""
    text = read(TEMPLATE)
    part = text[text.index('## Each line'):text.index('## The poster check')]
    rows = [line for line in part.splitlines() if line.startswith('|')]
    header = [cell.strip() for cell in rows[0].strip('|').split('|')]
    cells, order = {}, []
    for row in rows[2:]:
        values = [cell.strip() for cell in row.strip('|').split('|')]
        name = values[0].strip('`')
        order.append(name)
        cells[name] = dict(zip(header, values))
    return header, order, cells


class TemplateTests(unittest.TestCase):
    def test_the_template_holds_min_md_s_nine_lines_in_its_order_after_a_title_line(self):
        self.assertEqual(required_lines(), ['spec', 'posted-by', 'assigned-to', 'cross-account',
                                            'room-at-post', 'acceptance', 'report', 'verified-by',
                                            'merged-at'])
        shown, lines = template_lines()
        self.assertEqual([line.split(':', 1)[0] for line in lines], required_lines())
        self.assertTrue(shown.startswith('# <date>-<item>: '))
        for line in lines:  # a line filled later is empty after its colon
            name, value = line.split(':', 1)
            self.assertEqual(value == '', name not in POSTED, line)

    def test_the_table_says_what_each_line_holds_who_fills_it_where_and_when_in_the_same_order(self):
        header, order, cells = table()
        self.assertEqual(header, COLUMNS)
        self.assertEqual(order, required_lines())
        for name in order:
            for column in COLUMNS:
                with self.subTest(line=name, column=column):
                    self.assertTrue(cells[name][column])

    def test_decision_5_gives_room_at_post_three_values_and_cross_account_yes_or_no(self):
        _, lines = template_lines()
        self.assertIn('cross-account: <yes or no>', lines)
        self.assertTrue(any(line.startswith('room-at-post: <measured, estimate or unknown>')
                            for line in lines))
        _, _, cells = table()
        for word in ('`measured`', '`estimate`', '`unknown`'):
            self.assertIn(word, cells['room-at-post']['What it holds'])
        for word in ('`yes`', '`no`'):
            self.assertIn(word, cells['cross-account']['What it holds'])
        self.assertIn('Neither is checked by a gate item', read(TEMPLATE))

    def test_the_poster_check_refuses_a_poster_off_the_poster_line_as_refused_poster(self):
        text = ' '.join(read(TEMPLATE).split())
        for words in ('the worker checks `posted-by` against the `poster` line of `meta/ROLES.md`',
                      'the worker refuses the task as `refused: poster` (DR-102), before any work',
                      "M3's fourth task, posted by `probe-m`"):
            self.assertIn(words, text)

    def test_the_fillers_are_d1v_s_finding_2_as_settled_and_agree_with_meta_tasks_readme(self):
        _, _, cells = table()
        for name in POSTED:
            with self.subTest(line=name):
                self.assertEqual(cells[name]['Who fills it'], 'The poster')
                self.assertEqual(cells[name]['Where'], 'The task file the merger commits on `main`')
                self.assertEqual(cells[name]['When'], 'At the post')
        self.assertTrue(cells['assigned-to']['Who fills it'].startswith('The worker'))
        self.assertTrue(cells['assigned-to']['Where'].startswith("The first commit of the worker's branch"))
        self.assertIn('the Team seat', cells['report']['Who fills it'])
        self.assertIn("the poster's seat", cells['report']['Who fills it'])
        for name in ('verified-by', 'merged-at'):
            with self.subTest(line=name):
                self.assertTrue(cells[name]['Who fills it'].startswith('The merger'))
                self.assertEqual(cells[name]['Where'], '`main`')
        # The README's words that T1 rests on are still the README's.
        readme = ' '.join(read(TASKS_README).split())
        decision = ' '.join(read(TEMPLATE).split())
        decision = decision[decision.index('**T1.'):decision.index('**T2.')]
        for words in ('each task file on `main` for its poster', 'fills `report:` on its branch',
                      '`verified-by:` is filled on `main` at merge by the verifier'):
            with self.subTest(words=words):
                self.assertIn(words, readme)
                self.assertIn(words, decision)

    def test_room_at_post_carries_finish_md_s_t6_with_the_two_pools(self):
        # FINISH.md step 7's T6: the poster copies the account's usage line, or names the pool.
        _, _, cells = table()
        held = cells['room-at-post']['What it holds']
        finish = ' '.join(read(FINISH).split())
        t6 = finish[finish.index('**T6.**'):finish.index('**Tests, `tests/test_meters.py`:**')]
        for words in ("the poster copies that account's `usage` line",
                      '`measured` if its state is, else `unknown`, as in the cut form',
                      'for a credits job, `unknown`, naming the pool'):
            with self.subTest(words=words):
                self.assertIn(words, t6)  # FINISH.md says it
                self.assertIn(words, held)  # and the row carries it
        for pool in ('`team-org`', '`individual-org`'):
            self.assertIn(pool, held)
        text = ' '.join(read(TEMPLATE).split())
        self.assertEqual(text.count('- **T6. '), 1)
        decision = text[text.index('- **T6. '):]
        cut = 'labelled `measured` for both accounts, or `unknown` if the file is older than 10 minutes'
        self.assertIn(cut, ' '.join(read(MIN).split()))  # MIN.md's cut form says it
        self.assertIn(cut, decision)  # and T6 quotes it
        self.assertIn('"%s"' % t6.split('row gains: ', 1)[1].strip(), decision)  # T6 quotes FINISH.md

    def test_no_line_of_the_template_ends_in_whitespace(self):
        # D5v's finding 10: git diff --check flagged a whitespace-only line.
        for number, line in enumerate(read(TEMPLATE).split('\n'), 1):
            with self.subTest(line=number):
                self.assertEqual(line, line.rstrip())


class PosterLineTests(unittest.TestCase):
    """The poster check's git line, run in a scratch repository whose poster line rotates after
    a task file is added."""

    def setUp(self):
        self.world = World()
        self.addCleanup(self.world.close)
        self.repo = self.world.make('repo')
        self.env = {'HOME': self.world.home, 'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8',
                    'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': os.devnull,
                    'GIT_AUTHOR_NAME': 'test', 'GIT_AUTHOR_EMAIL': 'test@example.invalid',
                    'GIT_COMMITTER_NAME': 'test', 'GIT_COMMITTER_EMAIL': 'test@example.invalid'}

    def git(self, *args):
        result = subprocess.run(['git', '-C', self.repo] + list(args), env=self.env,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def commit(self, path, content, message):
        full = os.path.join(self.repo, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, 'w', encoding='utf-8') as f:
            f.write(content)
        self.git('add', path)
        self.git('commit', '-q', '-m', message)

    @staticmethod
    def roles(poster):
        return '# roles\n\n```text\nmerger = diogenes_1\nposter = %s\n```\n\nposter = nobody_0\n' % poster

    def test_the_git_line_prints_roles_md_as_it_stood_in_the_commit_that_added_the_task(self):
        [line] = [line for line in re.findall(r'^```sh\n(.*?)\n^```$', read(TEMPLATE), re.M | re.S)
                  if 'git show' in line]
        self.assertEqual(line.count('<task file>'), 1)
        self.git('init', '-q', '-b', 'main')
        self.commit('meta/ROLES.md', self.roles('management_1, diogenes_1'), 'roles')
        task = 'meta/tasks/2026-10-18-poster-check.md'
        self.commit(task, '# 2026-10-18-poster-check: a test task\n', 'task')
        self.commit('meta/ROLES.md', self.roles('management_2, diogenes_1'), 'rotate')
        result = subprocess.run(['/bin/bash', '-c', line.replace('<task file>', task)], cwd=self.repo,
                                env=self.env, stdin=subprocess.DEVNULL, capture_output=True,
                                text=True, timeout=60)  # stdin: as in test_using.py's run_line
        self.assertEqual((result.returncode, result.stderr), (0, ''))
        self.assertEqual(result.stdout, self.roles('management_1, diogenes_1'))
        shown = os.path.join(self.world.base, 'ROLES-at-the-task.md')
        with open(shown, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        posters = dio.read_roles(shown)['poster']  # the line inside the fenced block, as dio reads it
        self.assertEqual(posters, ['management_1', 'diogenes_1'])
        self.assertIn('management_1', posters)  # its poster then: the task is worked
        self.assertNotIn('probe-m', posters)  # M3's fourth task: refused: poster


if __name__ == '__main__':
    unittest.main()
