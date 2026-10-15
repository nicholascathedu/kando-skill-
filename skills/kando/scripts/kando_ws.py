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

from kando_layout import KandoFileError, find_kando_file, read_json

API_VERSION = 2  # Kando 3.0's IPC version


IDLE = object()  # what receive(idle=...) returns when nothing arrived in time


class KandoIPCError(Exception):
    pass


def ipc_port():
    path = find_kando_file("ipc-info.json")
    if not path:
        raise KandoIPCError("ipc-info.json was not found. Is Kando running?")
    try:
        info = read_json(path)
    except KandoFileError as e:  # Kando may be rewriting it right now
        raise KandoIPCError(f"ipc-info.json {e.reason}") from e
    if not isinstance(info, dict) or info.get("apiVersion") != API_VERSION:
        version = info.get("apiVersion") if isinstance(info, dict) else None
        raise KandoIPCError(f"Kando's IPC version is {version}, this script speaks "
                            f"{API_VERSION}. Update the skill or Kando.")
    try:
        return int(info["port"])
    except (KeyError, TypeError, ValueError) as e:
        raise KandoIPCError("ipc-info.json has no port. Is Kando running?") from e


class KandoSocket:
    def __init__(self, port=None, timeout=None):
        port = port or ipc_port()
        try:
            self.sock = socket.create_connection(("127.0.0.1", port), timeout=5)
        except OSError as e:
            raise KandoIPCError(f"Kando's IPC port {port} refused the connection ({e}). "
                                "Is Kando running?") from e
        try:
            self._handshake(port)
        except OSError as e:  # reset or timed out: an old port, or Kando quitting
            self.sock.close()
            raise KandoIPCError(f"Kando's IPC port {port} stopped answering ({e}).") from e
        self.timeout = timeout
        self.sock.settimeout(timeout)

    def _handshake(self, port):
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

    def receive(self, idle=None):
        """The next JSON message from Kando, or None when Kando closes the connection. With
        idle=seconds, returns IDLE if nothing starts arriving in that time. Frames that aren't
        valid JSON are skipped."""
        parts = []
        try:
            if idle is not None and not self.buffer:
                self.sock.settimeout(idle)
                try:
                    chunk = self.sock.recv(65536)
                except socket.timeout:
                    return IDLE
                finally:
                    self.sock.settimeout(self.timeout)
                if not chunk:
                    return None
                self.buffer += chunk
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
                        try:
                            return json.loads(b"".join(parts).decode("utf-8"))
                        except ValueError:  # not JSON (or not UTF-8): skip it
                            parts = []
        except (EOFError, ConnectionError):  # Kando quit; on Windows that's often a reset
            return None

    def close(self):
        try:
            self._frame(0x8, b"")
        except OSError:
            pass
        self.sock.close()
