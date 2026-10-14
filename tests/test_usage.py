"""Tests for kando_usage.py and kando_ws.py. Run from the repo root: python -m unittest discover -s tests"""

import json
import unittest

from test_scripts import item, menus  # also puts scripts/ on sys.path
import kando_usage  # noqa: E402
import kando_ws  # noqa: E402


class UsageTest(unittest.TestCase):
    def data(self):
        maya = menus(item("Frame", 0), item("Save", 225),
                     item("Display", 90, "submenu", [item("Wire", 0), item("Shaded", 180)]),
                     shortcut="Control+4", conditions={"appName": "maya"})
        maya["menus"][0]["root"]["name"] = "Maya"
        desk = menus(item("Browser", 0), item("Files", 180), shortcut="Control+Space")
        maya["menus"] += desk["menus"]
        return maya

    def rows(self, app, path, ms, t):
        out = [{"t": t, "ev": "openMenu", "path": [], "app": app}]
        if path is not None:
            out.append({"t": t + ms, "ev": "selectButton", "path": path})
        return out + [{"t": t + ms + 1, "ev": "closeMenu", "path": []}]

    def test_report_moves_slow_and_unused(self):
        rows = []
        for i in range(30):
            rows += self.rows("maya.exe", [1], 400, i * 10000)        # Save, a diagonal
        for i in range(10):
            rows += self.rows("maya.exe", [2, 0], 3000, 400000 + i * 10000)  # slow submenu pick
        for i in range(8):
            rows += self.rows("maya.exe", None, 900, 600000 + i * 10000)    # cancels
        lines = " ".join(kando_usage.report(rows, self.data()))
        self.assertIn("Move: 'Save' in Maya", lines)
        self.assertIn("Slow: 'Display > Wire'", lines)
        self.assertIn("Never used in Maya (48 opens): Display > Shaded, Frame", lines)
        self.assertIn("Hard to find: Maya", lines)
        self.assertNotIn("Test", lines)  # the desktop menu was never opened from Maya
        self.assertIn("Only 0 menu opens", kando_usage.report([], self.data())[0])

    def test_regex_conditions_match_like_kando(self):
        self.assertTrue(kando_usage.matches("/^maya/i", "Maya.exe"))
        self.assertFalse(kando_usage.matches("/^maya/", "Maya.exe"))
        self.assertTrue(kando_usage.matches("MAYA", "maya.exe"))


class WebSocketTest(unittest.TestCase):
    def test_round_trip_with_a_local_server(self):
        import base64, hashlib, socket, threading
        srv = socket.socket()
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        got = {}

        def serve():
            conn, _ = srv.accept()
            head = b""
            while b"\r\n\r\n" not in head:
                head += conn.recv(1024)
            key = [l.split(b": ")[1] for l in head.split(b"\r\n") if l.lower().startswith(b"sec-websocket-key")][0]
            accept = base64.b64encode(hashlib.sha1(key + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest())
            conn.sendall(b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
                         b"Sec-WebSocket-Accept: " + accept + b"\r\n\r\n")
            b0, b1 = conn.recv(2)
            mask, n = conn.recv(4), b1 & 0x7F
            got["msg"] = json.loads(bytes(b ^ mask[i % 4] for i, b in enumerate(conn.recv(n))))
            body = json.dumps({"type": "menu-interaction", "interaction": "selectButton", "path": [1]}).encode()
            conn.sendall(bytes([0x89, 0]) + bytes([0x81, len(body)]) + body + bytes([0x88, 0]))
            conn.close()

        t = threading.Thread(target=serve)
        t.start()
        ws = kando_ws.KandoSocket(port=srv.getsockname()[1], timeout=5)
        ws.send({"type": "start-observing"})
        self.assertEqual(ws.receive()["path"], [1])
        self.assertIsNone(ws.receive())
        ws.sock.close()
        t.join(5)
        srv.close()
        self.assertEqual(got["msg"], {"type": "start-observing"})


if __name__ == "__main__":
    unittest.main()
