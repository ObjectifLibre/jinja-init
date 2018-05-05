import os
import shutil
import tempfile
import unittest

import run


TEMPLATE = """foo from secrets: {{ foo }}
bar from envvars: {{ bar }}
baz overloaded by envvars: {{ baz }}"""

EXPECTED = """foo from secrets: FOO
bar from envvars: BAR
baz overloaded by envvars: BAZ"""


class TestRunner(unittest.TestCase):
    def setUp(self):
        self.src_dir = tempfile.mkdtemp()
        self.dest_dir = tempfile.mkdtemp()
        self.secrets_dir = tempfile.mkdtemp()

        self.src_file = os.path.join(self.src_dir, 'template.j2')
        self.dest_file = os.path.join(self.dest_dir, 'output.cfg')

        with open(self.src_file, 'w') as fd:
            fd.write(TEMPLATE)
        with open(os.path.join(self.secrets_dir, 'foo'), 'w') as fd:
            fd.write('FOO')
        with open(os.path.join(self.secrets_dir, 'baz'), 'w') as fd:
            fd.write('NOT FINAL BAZ')

        os.environ['JINJA_VAR_bar'] = 'BAR'
        os.environ['JINJA_VAR_baz'] = 'BAZ'

        self.runner = run.Runner(self.src_file, self.dest_file,
                                 self.secrets_dir, False)

    def tearDown(self):
        shutil.rmtree(self.src_dir)
        shutil.rmtree(self.dest_dir)
        shutil.rmtree(self.secrets_dir)

    def test_attributes(self):
        self.assertEqual(self.runner.src_file, self.src_file)
        self.assertEqual(self.runner.dest_file, self.dest_file)
        self.assertEqual(self.runner.secrets_dir, self.secrets_dir)
        self.assertEqual(self.runner.verbose, False)

    def test_run(self):
        self.runner.run()
        with open(self.dest_file) as fd:
            output = fd.read()
        self.assertEqual(EXPECTED, output)
