<#
.SYNOPSIS
  Opens a Kando menu with a mouse side button, using only what ships with Windows.

.DESCRIPTION
  While this script runs, pressing the chosen side button holds a modifier and taps a key
  (Ctrl+F13 by default). Releasing the button releases the modifier. Give a Kando menu the
  shortcut "Control+F13" and the side button opens it. Because the modifier stays held while
  the button is down, Kando's turbo mode works: hold the button, move toward an item, let go.

  The side button stops doing Back / Forward while the script runs. Stop it with Ctrl+C in its
  window, or from any other window with -Stop. The modifier is always released when it stops,
  so it can't leave Ctrl stuck down. Nothing is installed: -InstallStartup only adds a shortcut
  to your Startup folder so it starts when you log in, and -RemoveStartup takes it away again.

  Limits: it can't send keys to apps running as administrator unless it runs as administrator
  too. Some games' anti-cheat block or flag simulated keys, so stop it before playing those.
  Antivirus can warn about it, because a mouse hook is also what spyware uses; the whole hook
  is the C# block below.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File kando-mouse-buttons.ps1
  powershell -ExecutionPolicy Bypass -File kando-mouse-buttons.ps1 -Button Back -Key F14
  powershell -ExecutionPolicy Bypass -File kando-mouse-buttons.ps1 -InstallStartup
  powershell -ExecutionPolicy Bypass -File kando-mouse-buttons.ps1 -Stop
#>
param(
  [ValidateSet('Back', 'Forward')] [string] $Button = 'Forward',
  [ValidateSet('Control', 'Alt', 'Shift', 'None')] [string] $Modifier = 'Control',
  [ValidatePattern('^F(1[3-9]|2[0-4])$')] [string] $Key = 'F13',
  [switch] $InstallStartup,
  [switch] $RemoveStartup,
  [switch] $Stop,
  [switch] $SelfTest
)

$ErrorActionPreference = 'Stop'

$source = @'
using System;
using System.Runtime.InteropServices;
using System.Threading;

public static class KandoMouseButtons {
  const int WH_MOUSE_LL = 14, WM_XBUTTONDOWN = 0x020B, WM_XBUTTONUP = 0x020C, WM_QUIT = 0x0012;
  const uint LLMHF_INJECTED = 1, KEYEVENTF_KEYUP = 2, INPUT_KEYBOARD = 1;

  delegate IntPtr HookProc(int code, IntPtr wParam, IntPtr lParam);

  [StructLayout(LayoutKind.Sequential)]
  struct MSLLHOOKSTRUCT { public int x, y; public uint mouseData, flags, time; public IntPtr extra; }

  [StructLayout(LayoutKind.Sequential)]
  struct MSG { public IntPtr hwnd; public uint message; public UIntPtr wParam; public IntPtr lParam; public uint time; public int x, y; }

  // INPUT with its union laid out as the largest member (MOUSEINPUT), so the size is right on both bitnesses.
  [StructLayout(LayoutKind.Sequential)]
  struct INPUT { public uint type; public KEYBDINPUT ki; public uint pad1, pad2; }
  [StructLayout(LayoutKind.Sequential)]
  struct KEYBDINPUT { public ushort vk, scan; public uint flags, time; public IntPtr extra; }

  [DllImport("user32.dll", SetLastError = true)]
  static extern IntPtr SetWindowsHookEx(int id, HookProc proc, IntPtr module, uint thread);
  [DllImport("user32.dll")] static extern IntPtr CallNextHookEx(IntPtr hook, int code, IntPtr wParam, IntPtr lParam);
  [DllImport("user32.dll")] static extern bool UnhookWindowsHookEx(IntPtr hook);
  [DllImport("user32.dll")] static extern int GetMessage(out MSG msg, IntPtr hwnd, uint min, uint max);
  [DllImport("user32.dll")] static extern bool PostThreadMessage(uint thread, uint msg, UIntPtr wParam, IntPtr lParam);
  [DllImport("user32.dll")] static extern uint SendInput(uint count, INPUT[] inputs, int size);
  [DllImport("user32.dll")] static extern uint MapVirtualKey(uint code, uint mapType);
  [DllImport("kernel32.dll")] static extern IntPtr GetModuleHandle(string name);
  [DllImport("kernel32.dll")] static extern uint GetCurrentThreadId();

  static readonly HookProc proc = OnMouse;  // kept in a field so it isn't garbage collected
  static readonly object gate = new object();
  static IntPtr hook;
  static uint hookThread;
  static int xbutton;
  static byte modifier, key;
  static volatile bool held;
  static int startError;
  static readonly ManualResetEvent started = new ManualResetEvent(false);
  static readonly ManualResetEvent stopped = new ManualResetEvent(true);

  public static bool IsRunning { get { return !stopped.WaitOne(0); } }

  // xbutton: 1 = Back, 2 = Forward. modifierVk 0 = none. Installs the hook on its own thread
  // and returns at once: 0 on success, else the Win32 error from SetWindowsHookEx.
  public static int Start(int xbuttonNumber, byte modifierVk, byte keyVk) {
    lock (gate) {
      if (IsRunning) return 0;
      xbutton = xbuttonNumber; modifier = modifierVk; key = keyVk; held = false; startError = 0;
      started.Reset(); stopped.Reset();
      AppDomain.CurrentDomain.ProcessExit -= OnProcessExit;
      AppDomain.CurrentDomain.ProcessExit += OnProcessExit;
      Thread t = new Thread(Pump);
      t.IsBackground = true;
      t.Start();
      started.WaitOne();
      if (startError != 0) stopped.Set();
      return startError;
    }
  }

  // Removes the hook and lets go of the modifier if the button was still down.
  public static void Stop() {
    lock (gate) {
      if (!IsRunning) return;
      if (hook != IntPtr.Zero) { UnhookWindowsHookEx(hook); hook = IntPtr.Zero; }
      ReleaseModifier();
      PostThreadMessage(hookThread, WM_QUIT, UIntPtr.Zero, IntPtr.Zero);
      stopped.WaitOne(2000);
    }
  }

  static void Pump() {
    hookThread = GetCurrentThreadId();
    hook = SetWindowsHookEx(WH_MOUSE_LL, proc, GetModuleHandle(null), 0);
    startError = hook == IntPtr.Zero ? Marshal.GetLastWin32Error() : 0;
    started.Set();
    if (startError != 0) return;
    MSG msg;
    while (GetMessage(out msg, IntPtr.Zero, 0, 0) > 0) { }
    if (hook != IntPtr.Zero) { UnhookWindowsHookEx(hook); hook = IntPtr.Zero; }
    ReleaseModifier();
    stopped.Set();
  }

  static void OnProcessExit(object sender, EventArgs e) { ReleaseModifier(); }

  static void ReleaseModifier() {
    if (held) { held = false; if (modifier != 0) Send(modifier, true); }
  }

  // Sends one key with its scan code too, which apps that read scan codes (games) need.
  static void Send(byte vk, bool up) {
    INPUT[] input = new INPUT[1];
    input[0].type = INPUT_KEYBOARD;
    input[0].ki.vk = vk;
    input[0].ki.scan = (ushort)MapVirtualKey(vk, 0);
    input[0].ki.flags = up ? KEYEVENTF_KEYUP : 0;
    SendInput(1, input, Marshal.SizeOf(typeof(INPUT)));
  }

  // Must stay fast: Windows drops a low-level hook that takes too long to answer.
  static IntPtr OnMouse(int code, IntPtr wParam, IntPtr lParam) {
    int message = (int)wParam.ToInt64();
    if (code >= 0 && (message == WM_XBUTTONDOWN || message == WM_XBUTTONUP)) {
      MSLLHOOKSTRUCT info = (MSLLHOOKSTRUCT)Marshal.PtrToStructure(lParam, typeof(MSLLHOOKSTRUCT));
      if ((int)(info.mouseData >> 16) == xbutton && (info.flags & LLMHF_INJECTED) == 0) {
        if (message == WM_XBUTTONDOWN && !held) {
          held = true;
          if (modifier != 0) Send(modifier, false);
          Send(key, false);
          Send(key, true);
        } else if (message == WM_XBUTTONUP && held) {
          held = false;
          if (modifier != 0) Send(modifier, true);
        }
        return (IntPtr)1;  // swallow the click so the app doesn't also go Back / Forward
      }
    }
    return CallNextHookEx(hook, code, wParam, lParam);
  }
}
'@

$mutexName = 'Local\KandoMouseButtons'
$stopEventName = 'Local\KandoMouseButtons.Stop'

function Get-StartupLink {
  Join-Path ([Environment]::GetFolderPath('Startup')) 'Kando mouse buttons.lnk'
}

if ($Stop) {
  $signal = $null
  if ([System.Threading.EventWaitHandle]::TryOpenExisting($stopEventName, [ref] $signal)) {
    [void] $signal.Set(); $signal.Dispose(); 'Stopped.'
  } else { 'It was not running.' }
  return
}

if ($RemoveStartup) {
  $startupLink = Get-StartupLink
  if (Test-Path $startupLink) { Remove-Item $startupLink; 'Removed the Startup shortcut.' }
  else { 'There was no Startup shortcut to remove.' }
  return
}

if ($InstallStartup) {
  $startupLink = Get-StartupLink
  # Point at the PowerShell that is running now: powershell.exe (Windows PowerShell) or pwsh.exe (7+).
  $exe = if ($PSVersionTable.PSEdition -eq 'Core') { 'pwsh.exe' } else { 'powershell.exe' }
  $shell = New-Object -ComObject WScript.Shell
  $link = $shell.CreateShortcut($startupLink)
  $link.TargetPath = Join-Path $PSHOME $exe
  $link.Arguments = "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PSCommandPath`" " +
                    "-Button $Button -Modifier $Modifier -Key $Key"
  $link.WindowStyle = 7  # minimized
  $link.Save()
  "Added '$startupLink'. It starts at your next login; run this script once now to use it today."
  return
}

if (-not ('KandoMouseButtons' -as [type])) { Add-Type -TypeDefinition $source }  # once per session
$modifierVk = @{ Control = 0x11; Alt = 0x12; Shift = 0x10; None = 0 }[$Modifier]
$keyVk = 0x7C + [int]$Key.Substring(1) - 13    # VK_F13 is 0x7C
$xbutton = @{ Back = 1; Forward = 2 }[$Button]

if ($SelfTest) {
  "OK: hook compiled; $Button button -> $Modifier+$Key (vk 0x{0:X2})." -f $keyVk
  return
}

$mutex = New-Object System.Threading.Mutex($false, $mutexName)
if (-not $mutex.WaitOne(0)) { 'Already running. Use -Stop to stop it.'; return }
$stopSignal = New-Object System.Threading.EventWaitHandle($false, 'ManualReset', $stopEventName)
try {
  $err = [KandoMouseButtons]::Start($xbutton, [byte]$modifierVk, [byte]$keyVk)
  if ($err) { throw "Windows refused the mouse hook (error $err)." }
  "The $Button side button now sends $Modifier+$Key. Give a Kando menu that shortcut. Ctrl+C or -Stop to stop."
  # Waiting in short slices keeps Ctrl+C working, and the finally below always releases the modifier.
  while ([KandoMouseButtons]::IsRunning -and -not $stopSignal.WaitOne(250)) { }
} finally {
  [KandoMouseButtons]::Stop()
  $stopSignal.Dispose()
  $mutex.ReleaseMutex()
  $mutex.Dispose()
}
'Stopped.'
