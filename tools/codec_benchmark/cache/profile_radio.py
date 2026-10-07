"""Serve only known AAC fixtures, exercise a board, save CPU logs and status.

Requires a no-sleep radio build with USB logs and FreeRTOS runtime statistics.
Does not flash, reset, persist a playlist or change Wi-Fi settings. Stops the
temporary stream at exit; restart the radio afterward to resume its station.
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import time
from urllib.request import Request, urlopen

import serial

ROOT = Path(__file__).resolve().parents[3]
CASES = {"lc-48000-stereo": (48000, 26624), "he-48000-stereo": (48000, 30720),
         "hev2-44100-stereo": (44100, 30720)}
FIXTURES = {name: (ROOT / "tests/fixtures/aac_stream_format" / (name + ".aac")).read_bytes()
            for name in CASES}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def do_GET(self):
        name = self.path.removeprefix("/").removesuffix(".aac")
        if name not in CASES and name != "changing":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "audio/aac")
        self.send_header("Connection", "close")
        self.end_headers()
        started = time.monotonic()
        try:
            count = 0
            while time.monotonic() - started < 180:
                case = list(CASES)[(count // 12) % 3] if name == "changing" else name
                self.wfile.write(FIXTURES[case])
                self.wfile.flush()
                rate, samples = CASES[case]
                # Feed slightly faster than playback; bounded fixture writes
                # and TCP backpressure keep memory use small.
                time.sleep(0.9 * samples / rate)
                count += 1
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", required=True, help="Board HTTP origin")
    parser.add_argument("--host", required=True, help="Local LAN IPv4 for fixture server")
    parser.add_argument("--http-port", type=int, default=8769)
    parser.add_argument("--serial-port", required=True)
    parser.add_argument("--seconds", type=int, default=35)
    parser.add_argument("--case", choices=(*CASES, "changing"), action="append")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.seconds < 25:
        parser.error("Use at least 25 seconds per case for stable 5-second CPU windows")
    args.output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((args.host, args.http_port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = serial.Serial(port=None, baudrate=115200, timeout=0.2)
    port.dtr = port.rts = False
    port.port = args.serial_port
    port.open()
    finished = threading.Event()
    phase = {"name": "startup", "started": time.monotonic()}
    lock = threading.Lock()
    saved = []

    def capture():
        while not finished.is_set():
            line = port.readline().decode("utf-8", errors="replace").strip()
            # Keep perf/failure evidence only. Startup logs can contain SSIDs.
            if any(marker in line for marker in ("PERF ", "assert failed", "Guru Meditation", "CORRUPT HEAP",
                                                  "AAC", "aac", "decoder", "decode failed")):
                with lock:
                    saved.append(dict(case=phase["name"], seconds=time.monotonic() - phase["started"], line=line))

    thread = threading.Thread(target=capture, daemon=True)
    thread.start()

    def request(path, data=None):
        with urlopen(Request(args.board.rstrip("/") + path, data=data), timeout=8) as response:
            return json.load(response)

    statuses = []
    try:
        for case in (args.case or (*CASES, "changing")):
            request("/api/native/stop", b"")
            time.sleep(2)
            with lock:
                phase.update(name=case, started=time.monotonic())
            url = f"http://{args.host}:{args.http_port}/{case}.aac"
            request("/api/native/play?codec=aac", url.encode())
            deadline = time.monotonic() + args.seconds
            while time.monotonic() < deadline:
                state = request("/api/native/status")
                # Keep technical fields only; station names/SSID are irrelevant.
                state = {k: v for k, v in state.items() if k in (
                    "audio", "format", "sample_rate", "channels", "bits_per_sample",
                    "pcm_sample_rate", "pcm_channels", "format_is_pcm", "channels_are_core", "rssi")}
                statuses.append(dict(case=case, seconds=time.monotonic() - phase["started"], **state))
                time.sleep(1)
            print(f"Completed {case}: {statuses[-1]}", flush=True)
    finally:
        try:
            request("/api/native/stop", b"")
        finally:
            finished.set()
            thread.join(timeout=2)
            port.close()
            server.shutdown()
            server.server_close()
            (args.output / "radio-perf.json").write_text(json.dumps(saved, indent=2) + "\n", encoding="utf-8")
            (args.output / "radio-status.json").write_text(json.dumps(statuses, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
