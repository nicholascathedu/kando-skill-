#!/usr/bin/env python3
"""Change the text you just copied and paste it back, from a Kando item.

    pythonw kando_text.py snake      # 'Crate Lid v2' -> crate_lid_v2, pasted over the selection
    pythonw kando_text.py search     # search the web for it instead

The item copies first and then runs this: close-menu, simulate-hotkey ControlLeft+KeyC,
delay 0.15, execute-command `pythonw kando_text.py snake`. The script reads the clipboard,
changes the text, puts the result on the clipboard and presses Ctrl+V itself, so the paste
always comes after the change (Kando doesn't wait for commands to finish).

Actions: upper, lower, title, sentence, snake, kebab, pascal, camel, join, trim (each pastes),
search, translate (each opens the browser). Each line is changed on its own.
Windows only for the clipboard and paste; the text changes themselves work anywhere.
Standard library only.
"""

import argparse
import os
import re
import sys
import time
import urllib.parse
import webbrowser

# Splits CrateLid, crate_lid and HDRMap2 into words; a number stays on the word before it (v2).
WORD = re.compile(r"[A-Z]+(?![a-z])\d*|[A-Z]?[a-z]+\d*|\d+")


def words(line):
    return WORD.findall(re.sub(r"['’]", "", line))


def per_line(fn):
    return lambda text: "\n".join(fn(line) for line in text.split("\n"))


def sentence_case(line):
    out = line.lower()
    return re.sub(r"(^\s*|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), out)


CHANGES = {
    "upper": str.upper,
    "lower": str.lower,
    "title": per_line(lambda s: re.sub(r"(?<![\w'’])([a-z])", lambda m: m.group(1).upper(),
                                       s.lower())),
    "sentence": per_line(sentence_case),
    "snake": per_line(lambda s: "_".join(w.lower() for w in words(s))),
    "kebab": per_line(lambda s: "-".join(w.lower() for w in words(s))),
    "pascal": per_line(lambda s: "".join(w[:1].upper() + w[1:].lower() for w in words(s))),
    "camel": per_line(lambda s: (lambda p: p[:1].lower() + p[1:])(
        "".join(w[:1].upper() + w[1:].lower() for w in words(s)))),
    "join": lambda text: " ".join(text.split()),
    "trim": lambda text: re.sub(r"\n{3,}", "\n\n",
                                "\n".join(line.strip() for line in text.strip().split("\n"))),
}
SEARCH = {
    "search": "https://www.google.com/search?q={}",
    "translate": "https://translate.google.com/?sl=auto&tl=en&op=translate&text={}",
}


def change(action, text):
    """The pasted result for `action`. Keeps Windows line endings if the text had them."""
    crlf = "\r\n" in text
    out = CHANGES[action](text.replace("\r\n", "\n"))
    return out.replace("\n", "\r\n") if crlf else out


# ------------------------------------------------------------------- Windows only --

def _api():
    import ctypes
    from ctypes import wintypes
    u, k = ctypes.windll.user32, ctypes.windll.kernel32
    u.GetClipboardData.restype = k.GlobalLock.restype = k.GlobalAlloc.restype = ctypes.c_void_p
    k.GlobalLock.argtypes = k.GlobalUnlock.argtypes = [ctypes.c_void_p]
    k.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    u.SetClipboardData.argtypes = [wintypes.UINT, ctypes.c_void_p]
    u.SetClipboardData.restype = ctypes.c_void_p
    u.OpenClipboard.argtypes = [wintypes.HWND]
    return ctypes, u, k


def _open(u):
    for _ in range(20):  # another app may hold the clipboard for a moment
        if u.OpenClipboard(None):
            return
        time.sleep(0.025)
    raise OSError("the clipboard is busy")


def get_clipboard():
    ctypes, u, k = _api()
    _open(u)
    try:
        h = u.GetClipboardData(13)  # CF_UNICODETEXT
        if not h:
            return ""
        p = k.GlobalLock(h)
        try:
            return ctypes.wstring_at(p)
        finally:
            k.GlobalUnlock(h)
    finally:
        u.CloseClipboard()


def set_clipboard(text):
    ctypes, u, k = _api()
    data = (text + "\0").encode("utf-16-le")
    h = k.GlobalAlloc(0x0002, len(data))  # GMEM_MOVEABLE
    ctypes.memmove(k.GlobalLock(h), data, len(data))
    k.GlobalUnlock(h)
    _open(u)
    try:
        u.EmptyClipboard()
        u.SetClipboardData(13, h)  # the clipboard owns h now
    finally:
        u.CloseClipboard()


def paste():
    """Wait (up to 1 s) until no modifier is held, then press Ctrl+V."""
    _, u, _ = _api()
    for _ in range(40):
        if not any(u.GetAsyncKeyState(vk) & 0x8000 for vk in (0x10, 0x11, 0x12, 0x5B, 0x5C)):
            break
        time.sleep(0.025)
    u.keybd_event(0x11, 0, 0, 0)
    u.keybd_event(0x56, 0, 0, 0)
    u.keybd_event(0x56, 0, 2, 0)
    u.keybd_event(0x11, 0, 2, 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("action", choices=sorted(CHANGES) + sorted(SEARCH))
    args = ap.parse_args(argv)
    if os.name != "nt":
        sys.exit("kando_text.py reads and pastes the Windows clipboard.")
    text = get_clipboard()
    if not text.strip():
        return 1  # nothing was selected: change nothing
    if args.action in SEARCH:
        webbrowser.open(SEARCH[args.action].format(urllib.parse.quote(text.strip()[:500])))
        return 0
    set_clipboard(change(args.action, text))
    paste()
    return 0


if __name__ == "__main__":
    sys.exit(main())
