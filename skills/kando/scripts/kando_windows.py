#!/usr/bin/env python3
"""Put app windows where you want them, from one Kando item.

    pythonw kando_windows.py "Painter=left" "PureRef=right"
    pythonw kando_windows.py "maya=left-two-thirds" "/chrome|msedge/i=right-third"
    pythonw kando_windows.py --list        # what it can see: app name and title of each window

Each argument is MATCH=SPOT. MATCH picks the window the way Kando's focus-window does: plain
text is found anywhere in the app name (Task Manager > Details, e.g. 'Adobe Substance 3D
Painter.exe'), case-insensitively, or a /regex/flags; add @text to also match the title, as in
'maya@crate_v3'. The first match (the one used most recently) wins. SPOT is one of
left, right, top, bottom, full, left-third, middle-third, right-third, left-two-thirds,
right-two-thirds, or x,y,w,h in percent of the screen ('0,0,60,100').

All windows go on the monitor the first one is on, inside the taskbar's edge. Windows that
aren't open are skipped and named. The last window listed ends up in front.
Windows only. Standard library only.
"""

import argparse
import os
import re
import sys

from kando_layout import use_utf8_output

SPOTS = {
    "left": (0, 0, 50, 100), "right": (50, 0, 50, 100),
    "top": (0, 0, 100, 50), "bottom": (0, 50, 100, 50), "full": (0, 0, 100, 100),
    "left-third": (0, 0, 100 / 3, 100), "middle-third": (100 / 3, 0, 100 / 3, 100),
    "right-third": (200 / 3, 0, 100 / 3, 100),
    "left-two-thirds": (0, 0, 200 / 3, 100), "right-two-thirds": (100 / 3, 0, 200 / 3, 100),
}


def matches(cond, value):
    """Kando's testStringCondition: /regex/flags, else a case-insensitive 'contains'."""
    if not cond:
        return True
    if cond.startswith("/"):
        m = re.fullmatch(r"/(.*?)/([gimy]*)", cond, re.S)
        if not m:
            raise ValueError(f"{cond!r} starts with '/' but isn't a /regex/flags")
        return re.search(m.group(1), value, re.I if "i" in m.group(2) else 0) is not None
    return cond.lower() in value.lower()


def parse(arg):
    """'Painter@scene=left' -> ('Painter', 'scene', (x, y, w, h) in percent)."""
    target, sep, spot = arg.rpartition("=")
    if not sep or not target:
        raise ValueError(f"{arg!r} needs MATCH=SPOT, like Painter=left")
    app, _, title = target.partition("@")
    if spot in SPOTS:
        box = SPOTS[spot]
    else:
        try:
            box = tuple(float(v) for v in spot.split(","))
        except ValueError:
            box = ()
        if len(box) != 4 or min(box) < 0 or box[0] + box[2] > 100 or box[1] + box[3] > 100 \
                or 0 in box[2:]:
            raise ValueError(f"{spot!r} isn't a spot. Use one of {', '.join(SPOTS)}, or "
                             "x,y,w,h in percent that fit on the screen, like 0,0,60,100")
    return app, title, box


def place(box, work):
    """Pixel rect (left, top, width, height) for a percent box inside a work area
    (left, top, right, bottom). Edges are rounded so neighbours share a line, no gap."""
    l, t, r, b = work
    x0 = l + round((r - l) * box[0] / 100)
    x1 = l + round((r - l) * (box[0] + box[2]) / 100)
    y0 = t + round((b - t) * box[1] / 100)
    y1 = t + round((b - t) * (box[1] + box[3]) / 100)
    return x0, y0, x1 - x0, y1 - y0


def pick(windows, app, title):
    """The first (most recently used) window matching, from [(hwnd, app, title)]."""
    return next((w for w in windows if matches(app, w[1]) and matches(title, w[2])), None)


# ------------------------------------------------------------------- Windows only --

def _win32():
    import ctypes
    from ctypes import wintypes
    user32, kernel32, dwmapi = ctypes.windll.user32, ctypes.windll.kernel32, ctypes.windll.dwmapi
    if not getattr(_win32, "ready", False):  # declare handle types once (64-bit safe)
        H = wintypes.HWND
        user32.GetWindow.restype = H
        user32.GetWindow.argtypes = [H, wintypes.UINT]
        user32.MonitorFromWindow.restype = wintypes.HMONITOR
        user32.MonitorFromWindow.argtypes = [H, wintypes.DWORD]
        user32.GetMonitorInfoW.argtypes = [wintypes.HMONITOR, ctypes.c_void_p]
        user32.SetWindowPos.argtypes = [H, H, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                        ctypes.c_int, wintypes.UINT]
        kernel32.OpenProcess.restype = wintypes.HANDLE
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                                        wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
        dwmapi.DwmGetWindowAttribute.argtypes = [H, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
        try:
            user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))  # per-monitor v2: real pixels
        except (AttributeError, OSError):
            pass
        _win32.ready = True
    return ctypes, wintypes, user32, kernel32, dwmapi


def open_windows():
    """[(hwnd, app, title)] front to back, filtered like Kando's own window list."""
    ctypes, wintypes, user32, kernel32, _ = _win32()
    out = []

    def visit(hwnd, _):
        if not user32.IsWindowVisible(hwnd) or user32.GetWindow(hwnd, 4):  # GW_OWNER
            return True
        n = user32.GetWindowTextLengthW(hwnd)
        if n <= 0:
            return True
        title = ctypes.create_unicode_buffer(n + 1)
        user32.GetWindowTextW(hwnd, title, n + 1)
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        proc = kernel32.OpenProcess(0x1000, False, pid.value)  # QUERY_LIMITED_INFORMATION
        if not proc:
            return True
        buf, size = ctypes.create_unicode_buffer(1024), wintypes.DWORD(1024)
        ok = kernel32.QueryFullProcessImageNameW(proc, 0, buf, ctypes.byref(size))
        kernel32.CloseHandle(proc)
        if ok:
            out.append((hwnd, os.path.basename(buf.value), title.value))
        return True

    proto = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(proto(visit), 0)
    return out


def work_area(hwnd):
    ctypes, wintypes, user32, _, _ = _win32()

    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                    ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]
    info = MONITORINFO(cbSize=ctypes.sizeof(MONITORINFO))
    user32.GetMonitorInfoW(user32.MonitorFromWindow(hwnd, 2), ctypes.byref(info))  # NEAREST
    r = info.rcWork
    return r.left, r.top, r.right, r.bottom


def move(hwnd, rect):
    """Restore the window and set its visible frame to rect (Windows 10/11 windows have an
    invisible resize border, which is added back so windows sit edge to edge)."""
    ctypes, wintypes, user32, _, dwmapi = _win32()
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE: un-maximize / un-minimize first
    outer, frame = wintypes.RECT(), wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(outer))
    if dwmapi.DwmGetWindowAttribute(hwnd, 9, ctypes.byref(frame), ctypes.sizeof(frame)):
        frame = outer  # DWMWA_EXTENDED_FRAME_BOUNDS unavailable: no border correction
    x, y, w, h = rect
    dl, dt = frame.left - outer.left, frame.top - outer.top
    dr, db = outer.right - frame.right, outer.bottom - frame.bottom
    user32.SetWindowPos(hwnd, None, x - dl, y - dt, w + dl + dr, h + dt + db, 0x0004 | 0x0040)
    user32.SetForegroundWindow(hwnd)  # SWP_NOZORDER | SWP_SHOWWINDOW, then bring it up


def main(argv=None):
    use_utf8_output()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("layout", nargs="*", help="MATCH=SPOT, e.g. Painter=left PureRef=right")
    ap.add_argument("--list", action="store_true", help="list the windows it can see")
    args = ap.parse_args(argv)
    try:
        wanted = [parse(a) for a in args.layout]
    except ValueError as e:
        sys.exit(str(e))
    if os.name != "nt":
        sys.exit("kando_windows.py is for Windows.")
    windows = open_windows()
    if args.list or not wanted:
        for _, app, title in windows:
            print(f"{app:32} {title}")
        return 0
    found = [(pick(windows, app, title), box, app) for app, title, box in wanted]
    missing = [app for w, _, app in found if w is None]
    found = [(w, box) for w, box, _ in found if w is not None]
    if found:
        area = work_area(found[0][0][0])
        for (hwnd, _, _), box in found:
            move(hwnd, place(box, area))
    if missing:
        print("Not open: " + ", ".join(missing), file=sys.stderr)
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
