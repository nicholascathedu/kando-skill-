"""The Windows side-button helper (kando-mouse-buttons.ps1). The hook is Windows only, but the
script's text can be checked anywhere, and the C# block compiles wherever a PowerShell is on
the PATH (pwsh on Linux and macOS too). Run from the repo root:
python -m unittest discover -s tests"""

import os
import re
import shutil
import subprocess
import unittest

from test_scripts import SCRIPTS

PS1 = os.path.join(SCRIPTS, "windows", "kando-mouse-buttons.ps1")
with open(PS1, encoding="utf-8") as f:
    TEXT = f.read()
CSHARP = TEXT.split("@'", 1)[1].split("'@", 1)[0]
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell")


class MouseButtonsTextTest(unittest.TestCase):
    def test_modifier_is_released_on_every_way_out(self):
        # The hook thread, Stop(), process exit and the PowerShell finally block all let go of
        # Ctrl, so a stopped script can't leave the modifier stuck down.
        self.assertEqual(CSHARP.count("ReleaseModifier();"), 3)
        self.assertIn("ProcessExit += OnProcessExit", CSHARP)
        self.assertRegex(TEXT, r"finally \{\s*\[KandoMouseButtons\]::Stop\(\)")

    def test_hook_runs_on_its_own_thread_so_ctrl_c_works(self):
        self.assertIn("new Thread(Pump)", CSHARP)
        self.assertIn("IsBackground = true", CSHARP)
        self.assertIn("WaitOne(250)", TEXT)  # the main thread only waits in short slices
        self.assertNotIn("Ctrl+C doesn't reach it", TEXT)

    def test_only_the_chosen_physical_side_button_is_swallowed(self):
        self.assertIn("(info.mouseData >> 16) == xbutton", CSHARP)
        self.assertIn("(info.flags & LLMHF_INJECTED) == 0", CSHARP)
        self.assertIn("return (IntPtr)1;", CSHARP)
        self.assertIn("return CallNextHookEx(hook, code, wParam, lParam);", CSHARP)

    def test_keys_go_out_with_scan_codes(self):
        self.assertIn("SendInput(", CSHARP)
        self.assertIn("MapVirtualKey(vk, 0)", CSHARP)
        self.assertNotIn("keybd_event", CSHARP)

    def test_stop_switch_uses_a_named_event_the_hidden_copy_watches(self):
        self.assertIn("[switch] $Stop", TEXT)
        self.assertIn("TryOpenExisting($stopEventName", TEXT)
        self.assertIn("$stopSignal.WaitOne(250)", TEXT)

    def test_startup_shortcut_targets_the_powershell_that_is_running(self):
        self.assertIn("'pwsh.exe' } else { 'powershell.exe' }", TEXT)
        self.assertIn("$link.TargetPath = Join-Path $PSHOME $exe", TEXT)
        self.assertIn('-File `"$PSCommandPath`"', TEXT)

    def test_parameters_are_validated(self):
        self.assertIn("[ValidateSet('Back', 'Forward')]", TEXT)
        self.assertIn("[ValidatePattern('^F(1[3-9]|2[0-4])$')]", TEXT)
        self.assertEqual(re.search(r"0x7C \+ \[int\]\$Key\.Substring\(1\) - 13", TEXT) is not None, True)

    def test_compiled_once_per_session(self):
        self.assertIn("if (-not ('KandoMouseButtons' -as [type])) { Add-Type", TEXT)


@unittest.skipUnless(POWERSHELL, "no PowerShell on the PATH")
class MouseButtonsCompileTest(unittest.TestCase):
    def ps(self, *args):
        return subprocess.run([POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
                               "-File", PS1, *args], capture_output=True, text=True, timeout=300)

    def test_hook_compiles_and_key_codes_are_right(self):
        r = self.ps("-SelfTest")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("OK: hook compiled; Forward button -> Control+F13 (vk 0x7C)", r.stdout)
        r = self.ps("-SelfTest", "-Button", "Back", "-Modifier", "Alt", "-Key", "F24")
        self.assertIn("Back button -> Alt+F24 (vk 0x87)", r.stdout)

    def test_bad_key_is_refused(self):
        self.assertNotEqual(self.ps("-SelfTest", "-Key", "F5").returncode, 0)
