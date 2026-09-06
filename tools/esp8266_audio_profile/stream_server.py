#!/usr/bin/env python3
"""Serve a selected audio fixture at its encoded real-time bitrate."""

from __future__ import annotations

import argparse
import http.server
import pathlib
import time


class PacedAudioHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    fixture_dir: pathlib.Path
    chunk_bytes: int

    def do_GET(self) -> None:
        if self.path.split("?", 1)[0] != "/stream.bin":
            self.send_error(http.HTTPStatus.NOT_FOUND)
            return
        audio_path = self.fixture_dir / "stream.bin"
        bitrate_path = self.fixture_dir / "stream.kbps"
        mime_path = self.fixture_dir / "stream.mime"
        try:
            bitrate = int(bitrate_path.read_text(encoding="ascii").strip())
            mime = mime_path.read_text(encoding="ascii").strip()
            size = audio_path.stat().st_size
        except (OSError, ValueError) as error:
            self.send_error(http.HTTPStatus.SERVICE_UNAVAILABLE, str(error))
            return
        if bitrate <= 0:
            self.send_error(http.HTTPStatus.SERVICE_UNAVAILABLE, "invalid bitrate")
            return

        self.send_response(http.HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(size))
        self.send_header("Connection", "close")
        self.end_headers()

        interval_per_byte = 8.0 / (bitrate * 1000.0)
        deadline = time.monotonic()
        try:
            with audio_path.open("rb") as stream:
                while chunk := stream.read(self.chunk_bytes):
                    self.wfile.write(chunk)
                    deadline += len(chunk) * interval_per_byte
                    delay = deadline - time.monotonic()
                    if delay > 0:
                        time.sleep(delay)
        except (BrokenPipeError, ConnectionResetError):
            pass
        self.close_connection = True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=pathlib.Path, required=True)
    parser.add_argument("--bind", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--chunk-bytes", type=int, default=256)
    args = parser.parse_args()

    PacedAudioHandler.fixture_dir = args.directory.resolve()
    PacedAudioHandler.chunk_bytes = args.chunk_bytes
    server = http.server.ThreadingHTTPServer((args.bind, args.port), PacedAudioHandler)
    print(f"Serving {PacedAudioHandler.fixture_dir} on {args.bind}:{args.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()