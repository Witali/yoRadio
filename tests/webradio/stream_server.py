#!/usr/bin/env python3
"""Loop reproducible MP3/AAC fixtures for the physical WebRadio test."""

from __future__ import annotations

import argparse
import http.server
import json
import pathlib


class StreamHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"
    fixtures: dict[str, tuple[str, bytes]]
    counters = {"mp3": 0, "aac": 0}

    def do_GET(self) -> None:
        route = self.path.split("?", 1)[0]
        if route == "/stats":
            payload = json.dumps(self.counters).encode("ascii")
            self.send_response(http.HTTPStatus.OK)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        prefix = "/stream."
        codec = route[len(prefix) :] if route.startswith(prefix) else ""
        if codec not in self.fixtures or route != f"/stream.{codec}":
            self.send_error(http.HTTPStatus.NOT_FOUND)
            return

        content_type, data = self.fixtures[codec]
        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Connection", "close")
        self.end_headers()
        offset = 0
        try:
            while True:
                length = min(1460, len(data) - offset)
                chunk = data[offset : offset + length]
                offset = (offset + length) % len(data)
                self.wfile.write(chunk)
                self.counters[codec] += len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, _format: str, *_args: object) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=pathlib.Path, required=True)
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=18080)
    args = parser.parse_args()
    fixture_root = args.root / "tests" / "webradio" / "fixtures"
    StreamHandler.fixtures = {
        "mp3": ("audio/mpeg", (fixture_root / "mono-64.mp3").read_bytes()),
        "aac": ("audio/aac", (fixture_root / "mono-64.aac").read_bytes()),
    }
    server = http.server.ThreadingHTTPServer((args.bind, args.port), StreamHandler)
    print(f"WebRadio fixture server listening on {args.bind}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
