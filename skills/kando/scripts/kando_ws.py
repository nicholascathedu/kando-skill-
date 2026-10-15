"""A tiny WebSocket client for Kando's local IPC server, standard library only.

Kando writes its port to ipc-info.json in the config folder (it changes every start) and
speaks plain JSON text frames on ws://127.0.0.1:<port>. This covers what Kando needs:
the opening handshake, masked text frames out, text / ping / close frames in.
"""

import base64
import json
import os
import socket
import struct

from kando_layout import find_kando_file, read_json

API_VERSION = 2  # Kando 3.0's IPC version


class KandoIPCError(Exception):
    pass


def ipc_port():
    path = find_kando_file("ipc-info.json")
    if not path:
        raise KandoIPCError("ipc-info.json was not found. Is Kando running?")
    info = read_json(path)
    if info.get("apiVersion") != API_VERSION:
        raise KandoIPCError(f"Kando's IPC version is {info.get('apiVersion')}, this script speaks "
                            f"{API_VERSION}. Update the skill or Kando.")
    return int(info["port"])


class KandoSocket:
    def __init__(self, port=None, timeout=None):
        port = port or ipc_port()
        try:
            self.sock = socket.create_connection(("127.0.0.1", port), timeout=5)
        except OSError as e:
            raise KandoIPCError(f"Kando's IPC port {port} refused the connection ({e}). "
                                "Is Kando running?") from e
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET / HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nUpgrade: websocket\r\n"
                           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\n"
                           "Sec-WebSocket-Version: 13\r\n\r\n").encode())
        head = b""
        while b"\r\n\r\n" not in head:
            chunk = self.sock.recv(1024)
            if not chunk:
                raise KandoIPCError("Kando closed the connection during the handshake.")
            head += chunk
        if b" 101 " not in head.split(b"\r\n", 1)[0]:
            raise KandoIPCError("Kando refused the WebSocket handshake.")
        self.buffer = head.split(b"\r\n\r\n", 1)[1]
        self.sock.settimeout(timeout)

    def _frame(self, opcode, payload):
        head = bytes([0x80 | opcode])
        n = len(payload)
        if n < 126:
            head += bytes([0x80 | n])
        elif n < 65536:
            head += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            head += bytes([0x80 | 127]) + struct.pack(">Q", n)
        mask = os.urandom(4)
        self.sock.sendall(head + mask + bytes(b ^ mask[i % 4] for i, b in enumerate(payload)))

    def send(self, message):
        self._frame(0x1, json.dumps(message).encode())

    def _read(self, n):
        while len(self.buffer) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise EOFError
            self.buffer += chunk
        data, self.buffer = self.buffer[:n], self.buffer[n:]
        return data

    def receive(self):
        """The next JSON message from Kando, or None when Kando closes the connection."""
        parts = []
        try:
            while True:
                b0, b1 = self._read(2)
                opcode, n = b0 & 0x0F, b1 & 0x7F
                if n == 126:
                    n = struct.unpack(">H", self._read(2))[0]
                elif n == 127:
                    n = struct.unpack(">Q", self._read(8))[0]
                mask = self._read(4) if b1 & 0x80 else None
                payload = self._read(n)
                if mask:
                    payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
                if opcode == 0x8:
                    return None
                if opcode == 0x9:
                    self._frame(0xA, payload)
                    continue
                if opcode in (0x0, 0x1):
                    parts.append(payload)
                    if b0 & 0x80:
                        return json.loads(b"".join(parts).decode("utf-8"))
        except EOFError:
            return None

    def close(self):
        try:
            self._frame(0x8, b"")
        except OSError:
            pass
        self.sock.close()
