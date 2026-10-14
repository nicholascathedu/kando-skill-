#!/usr/bin/env python3
"""Start Claude Code on what you just copied: a video link, a page, an error, some text.

    pythonw kando_claude.py slides                  # slide deck from the copied YouTube link
    pythonw kando_claude.py explain                 # explain the copied text
    pythonw kando_claude.py summary                 # sum up the copied web page
    pythonw kando_claude.py --prompt "Turn this into a Maya MEL script: {clip}"
    pythonw kando_claude.py slides --dir "%USERPROFILE%\\Projects\\talks"

From a Kando item: copy first (in a browser, ControlLeft+KeyL then ControlLeft+KeyC copies
the address), delay 0.15, then execute-command with one of the lines above. It opens a new
terminal window running `claude "<prompt>"` in --dir (default: your home folder), so you see
Claude start and can answer it. {clip} in a prompt is replaced with the clipboard text.
Windows only. Standard library only.
"""

import argparse
import os
import shutil
import subprocess
import sys

PROMPTS = {
    "slides": ("Make a slide deck from this YouTube video: {clip}\n"
               "First get its transcript: if yt-dlp is installed, run yt-dlp --skip-download "
               "--write-auto-subs --sub-langs en --sub-format vtt on it; otherwise ask me to "
               "paste the transcript. Then pull out the main points in order and build the "
               "deck, one idea per slide, with the timestamp each slide comes from."),
    "explain": "Explain this in plain words, and what I should do about it:\n\n{clip}",
    "summary": "Read this page and sum it up in a few bullet points, then say what's worth "
               "trying: {clip}",
}
LIMIT = 6000  # Windows caps a command line at 32,767 characters; keep well under it


def build(template, clip):
    clip = clip.strip()
    if len(clip) > LIMIT:
        clip = clip[:LIMIT] + "\n[cut off: the copied text was longer]"
    return template.replace("{clip}", clip)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("kind", nargs="?", choices=sorted(PROMPTS))
    ap.add_argument("--prompt", help="your own prompt; {clip} becomes the clipboard text")
    ap.add_argument("--dir", default=os.path.expanduser("~"), help="folder Claude starts in")
    args = ap.parse_args(argv)
    if not args.kind and not args.prompt:
        ap.error("pick slides, explain or summary, or give --prompt")
    if os.name != "nt":
        sys.exit("kando_claude.py is for Windows.")
    from kando_text import get_clipboard
    clip = get_clipboard()
    if not clip.strip():
        return 1  # nothing copied: don't start Claude on an empty prompt
    claude = shutil.which("claude")
    if not claude:
        sys.exit("Claude Code isn't on PATH. Install it, or start it once from a terminal.")
    prompt = build(args.prompt or PROMPTS[args.kind], clip)
    folder = os.path.expandvars(args.dir)
    if not claude.lower().endswith(".exe"):
        # claude.cmd (the npm install) runs through cmd, which would read & | ^ in the
        # copied text as commands. Only start the real program.
        sys.exit("Found " + claude + ", which runs through cmd. Install Claude Code with the "
                 "native installer (claude.exe) so copied text can't run as a command.")
    # A new console of its own (Windows Terminal on Windows 11). The prompt goes as one
    # argument, never through a shell.
    subprocess.Popen([claude, prompt], cwd=folder if os.path.isdir(folder) else None,
                     creationflags=subprocess.CREATE_NEW_CONSOLE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
