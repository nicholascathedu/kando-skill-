<#
.SYNOPSIS
  Opens a Kando menu with a mouse side button, using only what ships with Windows.

.DESCRIPTION
  While this script runs, pressing the chosen side button holds a modifier and taps a key
  (Ctrl+F13 by default). Releasing the button releases the modifier. Give a Kando menu the
  shortcut "Control+F13" and the side button opens it. Because the modifier stays held while
  the button is down, Kando's turbo mode works: hold the button, move toward an item, let go.

  The side button stops doing Back / Forward while the script runs. Nothing is installed:
  -InstallStartup only adds a shortcut to your Startup folder so it starts when you log in,
  and -RemoveStartup takes it away again.

  Limits: it can't send keys to apps running as administrator unless it runs as administrator
  too. Some games' anti-cheat block or flag simulated keys, so stop it before playing those.
  Antivirus can warn about it, because a mouse hook is also what spyware uses; the whole hook
  is the C# block below.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File kando-mouse-buttons.ps1
  powershell -ExecutionPolicy Bypass -File kando-mouse-buttons.ps1 -Button Back -Key F14
  powershell -ExecutionPolicy Bypass -File kando-mouse-buttons.ps1 -InstallStartup
#>
param(
  [ValidateSet('Back', 'Forward')] [string] $Button = 'Forward',
  [ValidateSet('Control', 'Alt', 'Shift', 'None')] [string] $Modifier = 'Control',
  [ValidatePattern('^F(1[3-9]|2[0-4])$')] [string] $Key = 'F13',
  [switch] $InstallStartup,
  [switch] $RemoveStartup,
  [switch] $SelfTest
)

$ErrorActionPreference = 'Stop'

$source = @'
using System;
using System.Runtime.InteropServices;

public static class KandoMouseButtons {
  const int WH_MOUSE_LL = 14, WM_XBUTTONDOWN = 0x020B, WM_XBUTTONUP = 0x020C;
  const uint LLMHF_INJECTED = 1, KEYEVENTF_KEYUP = 2;

  delegate IntPtr HookProc(int code, IntPtr wParam, IntPtr lParam);

  [StructLayout(LayoutKind.Sequential)]
  struct MSLLHOOKSTRUCT { public int x, y; public uint mouseData, flags, time; public IntPtr extra; }

  [StructLayout(LayoutKind.Sequential)]
  struct MSG { public IntPtr hwnd; public uint message; public UIntPtr wParam; public IntPtr lParam; public uint time; public int x, y; }

  [DllImport("user32.dll", SetLastError = true)]
  static extern IntPtr SetWindowsHookEx(int id, HookProc proc, IntPtr module, uint thread);
  [DllImport("user32.dll")] static extern IntPtr CallNextHookEx(IntPtr hook, int code, IntPtr wParam, IntPtr lParam);
  [DllImport("user32.dll")] static extern bool UnhookWindowsHookEx(IntPtr hook);
  [DllImport("user32.dll")] static extern int GetMessage(out MSG msg, IntPtr hwnd, uint min, uint max);
  [DllImport("user32.dll")] static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
  [DllImport("kernel32.dll")] static extern IntPtr GetModuleHandle(string name);

  static readonly HookProc proc = OnMouse;  // kept in a field so it isn't garbage collected
  static IntPtr hook;
  static int xbutton;
  static byte modifier, key;
  static bool held;

  // xbutton: 1 = Back, 2 = Forward. modifierVk 0 = none. Blocks until the message loop ends.
  public static int Run(int xbuttonNumber, byte modifierVk, byte keyVk) {
    xbutton = xbuttonNumber; modifier = modifierVk; key = keyVk;
    hook = SetWindowsHookEx(WH_MOUSE_LL, proc, GetModuleHandle(null), 0);
    if (hook == IntPtr.Zero) return Marshal.GetLastWin32Error();
    MSG msg;
    while (GetMessage(out msg, IntPtr.Zero, 0, 0) > 0) { }
    UnhookWindowsHookEx(hook);
    return 0;
  }

  // Must stay fast: Windows drops a low-level hook that takes too long to answer.
  static IntPtr OnMouse(int code, IntPtr wParam, IntPtr lParam) {
    int message = wParam.ToInt32();
    if (code >= 0 && (message == WM_XBUTTONDOWN || message == WM_XBUTTONUP)) {
      MSLLHOOKSTRUCT info = (MSLLHOOKSTRUCT)Marshal.PtrToStructure(lParam, typeof(MSLLHOOKSTRUCT));
      if ((int)(info.mouseData >> 16) == xbutton && (info.flags & LLMHF_INJECTED) == 0) {
        if (message == WM_XBUTTONDOWN && !held) {
          held = true;
          if (modifier != 0) keybd_event(modifier, 0, 0, UIntPtr.Zero);
          keybd_event(key, 0, 0, UIntPtr.Zero);
          keybd_event(key, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
        } else if (message == WM_XBUTTONUP && held) {
          held = false;
          if (modifier != 0) keybd_event(modifier, 0, KEYEVENTF_KEYUP, UIntPtr.Zero);
        }
        return (IntPtr)1;  // swallow the click so the app doesn't also go Back / Forward
      }
    }
    return CallNextHookEx(hook, code, wParam, lParam);
  }
}
'@

$startupLink = Join-Path ([Environment]::GetFolderPath('Startup')) 'Kando mouse buttons.lnk'

if ($RemoveStartup) {
  if (Test-Path $startupLink) { Remove-Item $startupLink; 'Removed the Startup shortcut.' }
  else { 'There was no Startup shortcut to remove.' }
  return
}

if ($InstallStartup) {
  $shell = New-Object -ComObject WScript.Shell
  $link = $shell.CreateShortcut($startupLink)
  $link.TargetPath = Join-Path $PSHOME 'powershell.exe'
  $link.Arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PSCommandPath`" " +
                    "-Button $Button -Modifier $Modifier -Key $Key"
  $link.WindowStyle = 7  # minimized
  $link.Save()
  "Added '$startupLink'. It starts at your next login; run this script once now to use it today."
  return
}

Add-Type -TypeDefinition $source
$modifierVk = @{ Control = 0x11; Alt = 0x12; Shift = 0x10; None = 0 }[$Modifier]
$keyVk = 0x7C + [int]$Key.Substring(1) - 13    # VK_F13 is 0x7C
$xbutton = @{ Back = 1; Forward = 2 }[$Button]

if ($SelfTest) {
  "OK: hook compiled; $Button button -> $Modifier+$Key (vk 0x{0:X2})." -f $keyVk
  return
}

$mutex = New-Object System.Threading.Mutex($false, 'Local\KandoMouseButtons')
if (-not $mutex.WaitOne(0)) { 'Already running.'; return }
"The $Button side button now sends $Modifier+$Key. Give a Kando menu that shortcut. Ctrl+C to stop."
$err = [KandoMouseButtons]::Run($xbutton, [byte]$modifierVk, [byte]$keyVk)
if ($err) { throw "Windows refused the mouse hook (error $err)." }
