"""The menus.json guard hook must run in every shell Claude Code may use for hooks: sh on
macOS and Linux, Git Bash on Windows, and PowerShell on Windows without Git Bash. Shells that
aren't installed are skipped. Run from the repo root: python -m unittest discover -s tests"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as f:
    HOOKS = json.load(f)["hooks"]

SHELLS = {  # how Claude Code passes the command string to each shell
    "sh": ["-c"], "bash": ["-c"], "dash": ["-c"],
    "pwsh": ["-NoProfile", "-NonInteractive", "-Command"],
    "powershell": ["-NoProfile", "-NonInteractive", "-Command"],
}


def command(event):
    return HOOKS[event][0]["hooks"][0]["command"].replace("${CLAUDE_PLUGIN_ROOT}", ROOT)


class HookShellTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.kando = os.path.join(self.dir, "kando")
        os.makedirs(self.kando)
        self.menus = os.path.join(self.kando, "menus.json")
        with open(self.menus, "w", encoding="utf-8") as f:
            json.dump({"version": "3.0.0", "menus": [], "collections": []}, f)
        with open(os.path.join(self.kando, "config.json"), "w", encoding="utf-8") as f:
            json.dump({"version": "3.0.0"}, f)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def run_hook(self, shell, event, path=None, env=None):
        payload = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": path or self.menus}})
        return subprocess.run([shell] + SHELLS[os.path.basename(shell).split(".")[0]] + [command(event)],
                              input=payload.encode("utf-8"), capture_output=True, timeout=120,
                              env=dict(env or os.environ, CLAUDE_PLUGIN_ROOT=ROOT))

    def check_shell(self, name):
        shell = shutil.which(name)
        if not shell:
            self.skipTest(f"{name} is not installed")
        run = self.run_hook(shell, "PreToolUse")
        self.assertEqual(run.returncode, 0, run.stderr.decode("utf-8", "replace"))
        backups = os.listdir(os.path.join(self.kando, "claude-backups"))
        self.assertEqual(len(backups), 1, f"{name} made no backup")
        with open(self.menus, "w", encoding="utf-8") as f:
            f.write('{"version": "3.0.0", "menus": [')            # a broken edit
        run = self.run_hook(shell, "PostToolUse")
        self.assertEqual(run.returncode, 2, run.stderr.decode("utf-8", "replace"))
        self.assertIn(b"broke menus.json", run.stderr)
        with open(self.menus, encoding="utf-8") as f:
            json.load(f)                                            # the backup is back
        other = self.run_hook(shell, "PostToolUse", path=os.path.join(self.dir, "notes.txt"))
        self.assertEqual(other.returncode, 0)

    def test_sh(self):
        self.check_shell("sh")

    def test_bash(self):
        self.check_shell("bash")

    def test_dash(self):
        self.check_shell("dash")

    def test_pwsh(self):
        self.check_shell("pwsh")

    def test_windows_powershell(self):
        self.check_shell("powershell")

    def test_powershell_without_python_stays_quiet(self):
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell is not installed")
        empty = os.path.join(self.dir, "empty")
        os.makedirs(empty)
        env = dict(os.environ, PATH=empty)
        run = self.run_hook(shell, "PreToolUse", env=env)
        self.assertEqual((run.returncode, run.stdout.strip()), (0, b""), run.stderr)
        self.assertFalse(os.path.isdir(os.path.join(self.kando, "claude-backups")))


if __name__ == "__main__":
    unittest.main()
