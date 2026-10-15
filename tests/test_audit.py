"""Tests from the cross-platform audit: the usage watcher end to end, reconnects, bad
ipc-info.json, and clipboard fallbacks. Run from the repo root: python -m unittest discover -s tests"""

import json
import os
import tempfile
import unittest
from unittest import mock

from test_scripts import item, menus  # also puts scripts/ on sys.path
import kando_context  # noqa: E402
import kando_usage  # noqa: E402
import kando_ws  # noqa: E402


def event(interaction, path=()):
    return {"type": "menu-interaction", "interaction": interaction, "path": list(path)}


class FakeSocket:
    """Plays back a list of messages, then a closed connection."""

    def __init__(self, messages):
        self.messages, self.sent, self.closed = list(messages), [], False

    def send(self, message):
        self.sent.append(message)

    def receive(self, idle=None):
        return self.messages.pop(0) if self.messages else None

    def close(self):
        self.closed = True


class WatchTest(unittest.TestCase):
    def test_watch_logs_every_pick_and_survives_kando_restarts(self):
        first = FakeSocket([event("openMenu"), event("hoverButton", [2]), event("selectButton", [2]),
                            event("closeMenu"), ["not", "a", "dict"]])
        second = FakeSocket([event("openMenu"), event("openSubmenu", [1]),
                             event("selectButton", [1, 0]), event("closeMenu")])
        sockets = iter([kando_ws.KandoIPCError("not running"), first,
                        ConnectionResetError("Kando quit"), second, KeyboardInterrupt()])

        def connect():
            nxt = next(sockets)
            if isinstance(nxt, BaseException):
                raise nxt
            return nxt

        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "claude-usage", "usage.jsonl")
            clock = iter(range(1000, 100000, 1000))
            with mock.patch.object(kando_ws, "KandoSocket", side_effect=connect), \
                    mock.patch.object(kando_usage.time, "sleep"), \
                    mock.patch.object(kando_usage.time, "time", side_effect=lambda: next(clock)), \
                    mock.patch.object(kando_usage, "foreground_app", return_value="maya.exe"), \
                    mock.patch("sys.stdout"):
                self.assertEqual(kando_usage.watch(log), 0)
            with open(log, encoding="utf-8") as f:
                rows = [json.loads(line) for line in f]
        self.assertEqual([r["ev"] for r in rows], ["openMenu", "selectButton", "closeMenu"] * 2)
        self.assertEqual(rows[4]["path"], [1, 0])          # the full path into the submenu
        self.assertEqual(rows[0]["app"], "maya.exe")
        self.assertEqual([r["t"] for r in rows], sorted(r["t"] for r in rows))
        self.assertEqual(first.sent, [{"type": "start-observing"}])
        self.assertTrue(first.closed and second.closed)

    def test_report_from_a_fake_log(self):
        data = menus(item("Frame", 0), item("Isolate", 90), item("Save", 180), item("Export", 270),
                     shortcut="Control+4", conditions={"appName": "maya"})
        data["menus"][0]["root"]["name"] = "Maya"
        rows, t = [], 0
        for _ in range(12):   # Save then Export, 3 s apart: one job in two flicks
            for path in ([2], [3]):
                rows += [{"t": t, "ev": "openMenu", "path": [], "app": "maya.exe"},
                         {"t": t + 400, "ev": "selectButton", "path": path},
                         {"t": t + 401, "ev": "closeMenu", "path": []}]
                t += 3000
            t += 60000
        lines = kando_usage.report(rows, data)
        self.assertTrue(lines[0].startswith("Most used: Save (12), Export (12)"))
        self.assertTrue(any("'Save' then 'Export' within 10 s 12 times" in l for l in lines))
        self.assertTrue(any(l.startswith("Never used in Maya (24 opens): Frame, Isolate") for l in lines))


class IpcInfoTest(unittest.TestCase):
    def check(self, text):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "ipc-info.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            with mock.patch.object(kando_ws, "find_kando_file", return_value=path):
                return kando_ws.ipc_port()

    def test_good_and_bad_files(self):
        self.assertEqual(self.check('{"port": 4321, "apiVersion": 2}'), 4321)
        for bad in ('{"port": 43', '[]', '{"apiVersion": 2}', '{"port": 1, "apiVersion": 1}'):
            with self.assertRaises(kando_ws.KandoIPCError):
                self.check(bad)

    def test_reset_connection_reads_as_closed(self):
        ws = kando_ws.KandoSocket.__new__(kando_ws.KandoSocket)
        ws.buffer = b""
        ws.sock = mock.Mock(recv=mock.Mock(side_effect=ConnectionResetError(10054, "reset")))
        self.assertIsNone(ws.receive())


def frame(payload):
    """An unmasked server text frame."""
    return bytes([0x81, len(payload)]) + payload


class RobustTest(unittest.TestCase):
    """From the PC test: Ctrl+C while idle, a log with a BOM, and frames that aren't JSON."""

    def socket_with(self, recv):
        ws = kando_ws.KandoSocket.__new__(kando_ws.KandoSocket)
        ws.buffer, ws.timeout = b"", None
        ws.sock = mock.Mock(recv=mock.Mock(side_effect=recv))
        return ws

    def test_idle_receive_wakes_up_and_restores_the_timeout(self):
        ws = self.socket_with([kando_ws.socket.timeout(), frame(b'{"a": 1}')])
        self.assertIs(ws.receive(idle=1), kando_ws.IDLE)
        self.assertEqual(ws.receive(idle=1), {"a": 1})
        self.assertEqual(ws.sock.settimeout.call_args_list[-1], mock.call(None))

    def test_frames_that_are_not_json_are_skipped(self):
        ws = self.socket_with([frame(b"hello") + frame(b"\xff\xfe") + frame(b'{"b": 2}')])
        self.assertEqual(ws.receive(), {"b": 2})

    def test_watch_keeps_going_while_idle(self):
        sock = FakeSocket([kando_ws.IDLE, kando_ws.IDLE, event("openMenu"), kando_ws.IDLE,
                           event("selectButton", [0])])
        sockets = iter([sock, KeyboardInterrupt()])

        def connect():
            nxt = next(sockets)
            if isinstance(nxt, BaseException):
                raise nxt
            return nxt

        with tempfile.TemporaryDirectory() as d:
            log = os.path.join(d, "usage.jsonl")
            with mock.patch.object(kando_ws, "KandoSocket", side_effect=connect), \
                    mock.patch.object(kando_usage.time, "sleep"), \
                    mock.patch.object(kando_usage, "foreground_app", return_value="maya.exe"), \
                    mock.patch("sys.stdout"):
                self.assertEqual(kando_usage.watch(log), 0)
            with open(log, encoding="utf-8") as f:
                self.assertEqual([json.loads(l)["ev"] for l in f], ["openMenu", "selectButton"])

    def test_report_reads_a_log_that_starts_with_a_bom(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "menus.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(menus(item("Save", 0), item("Export", 180)), f)
            os.makedirs(os.path.join(d, "claude-usage"))
            rows = [{"t": i, "ev": "openMenu", "path": []} for i in range(20)]
            rows[0:1] = [{"t": 0, "ev": "openMenu", "path": []},
                         {"t": 1, "ev": "selectButton", "path": [1]}]
            with open(os.path.join(d, kando_usage.LOG), "w", encoding="utf-8-sig") as f:
                f.write("".join(json.dumps(r) + "\n" for r in rows))
            with mock.patch("sys.stdout") as out:
                self.assertEqual(kando_usage.main(["report", path]), 0)
        printed = "".join(c.args[0] for c in out.write.call_args_list)
        self.assertIn("Export (1)", printed)


class ContextTest(unittest.TestCase):
    def test_help_exits_cleanly(self):
        with mock.patch("sys.stdout"):
            self.assertEqual(kando_context.main(["--help"]), 0)

    @unittest.skipIf(os.name == "nt", "Windows uses the Win32 clipboard")
    def test_copy_falls_back_through_clipboard_tools(self):
        calls = []

        def run(cmd, **kwargs):
            calls.append(cmd[0])
            if cmd[0] in ("wl-copy", "pbcopy"):
                raise FileNotFoundError(cmd[0])

        with mock.patch.object(kando_context.subprocess, "run", side_effect=run):
            ok = kando_context.copy_text("C:/scenes/hero.mb")
        if kando_context.sys.platform == "darwin":
            self.assertFalse(ok)
        else:
            self.assertTrue(ok)
            self.assertEqual(calls, ["wl-copy", "xclip"])
        with mock.patch.object(kando_context.subprocess, "run", side_effect=FileNotFoundError):
            self.assertFalse(kando_context.copy_text("x"))


if __name__ == "__main__":
    unittest.main()
