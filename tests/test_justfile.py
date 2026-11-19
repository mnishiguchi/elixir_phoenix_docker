"""just の引数処理と実行環境を Docker なしで確認します。"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
JUST = shutil.which("just")


@unittest.skipUnless(JUST, "just が未導入のため、ラッパーのテストを省略します")
class JustfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        shutil.copy2(ROOT / "justfile", self.root / "justfile")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.child = self.root / "subdir"
        self.child.mkdir()
        self.log = self.root / "calls.json"
        recorder = (
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "from pathlib import Path\n"
            "Path(os.environ['CALL_LOG']).write_text(json.dumps(\n"
            "    {'args': sys.argv[1:], 'cwd': os.getcwd()}))\n"
            "sys.exit(int(os.environ.get('COMMAND_EXIT', '0')))\n"
        )
        for name in ("docker", "new", "setup"):
            script = self.bin / name
            script.write_text(recorder)
            script.chmod(0o755)
        self.env = dict(os.environ, CALL_LOG=str(self.log))
        self.env["PATH"] = f"{self.bin}:{Path(JUST).parent}:{self.env['PATH']}"

    def run_just(self, *args):
        return subprocess.run(
            [JUST, *args], cwd=self.child, env=self.env,
            text=True, capture_output=True,
        )

    def test_default_lists_commands_without_docker(self):
        result = self.run_just()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("new name", result.stdout)
        self.assertIn("ボリュームは保持", result.stdout)
        self.assertFalse(self.log.exists())

    def test_new_passes_shell_characters_as_one_literal_argument(self):
        name = "bad'; touch injected; $(touch injected); #"
        result = self.run_just("new", name)
        self.assertEqual(result.returncode, 0, result.stderr)
        call = json.loads(self.log.read_text())
        self.assertEqual(call, {"args": [name], "cwd": str(self.root)})
        self.assertFalse((self.root / "injected").exists())

    def test_test_uses_test_environment_and_down_preserves_volumes(self):
        for recipe, expected in (
            ("test", ["compose", "run", "--rm", "-e", "MIX_ENV=test", "web", "mix", "test"]),
            ("down", ["compose", "--profile", "livebook", "down"]),
        ):
            with self.subTest(recipe=recipe):
                result = self.run_just(recipe)
                self.assertEqual(result.returncode, 0, result.stderr)
                call = json.loads(self.log.read_text())
                self.assertEqual(call["args"], expected)
                self.assertEqual(call["cwd"], str(self.root))

    def test_setup_failure_is_not_ignored(self):
        self.env["COMMAND_EXIT"] = "23"
        self.assertNotEqual(self.run_just("setup").returncode, 0)
