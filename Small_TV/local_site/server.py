"""Local Small_TV HTTP API emulator; Python standard library only."""

from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
from pathlib import Path
import re
import threading
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT.parent / "assets"
MAX_PHOTO = 100 * 1024
MAX_BODY = 16 * 1024
DEFAULTS = {
    "connected": False, "ssid": "", "password": "", "city": "Shenzhen,CN",
    "ntp": "pool.ntp.org", "openweathermapKey": "", "clickCount": 0,
    "clocktype": 0, "gif": 0, "timemode": 2,
    "led_brightness": 100, "night_brightness": 50,
    "night_start": 22, "night_stop": 9, "display_time": 5,
    "colors": ["#ff0000", "#ffff00", "#ffffff"],
    "settings": {"tempUnit": 0, "hourFormat": 0, "mileDisplay": 0, "timeSync": 0, "nightmode": 0},
    "photo_enabled": [True] * 5, "custom_photos": [False] * 5, "restart_count": 0,
}
NETWORKS = [{"ssid": "Small_TV Demo", "rssi": -38},
            {"ssid": "Home Wi-Fi Demo", "rssi": -57},
            {"ssid": "Guest Demo", "rssi": -72}]
GET_TEXT = {"/getclocktype": "clocktype", "/getgifvalue": "gif",
            "/GetTimeModeValue": "timemode", "/GetNightStartTime": "night_start",
            "/GetNightStopTime": "night_stop"}
SET_INTEGER = {"/setclocktype": ("clocktype", "clocktype", 0, 3),
               "/setgifvalue": ("gif", "gif", 0, 4),
               "/SetTimeModeValue": ("timemode", "timemode", 0, 2),
               "/SetNightStartTime": ("StartTime", "night_start", 18, 23),
               "/SetNightStopTime": ("StopTime", "night_stop", 5, 12),
               "/set_display_time": ("display_time", "display_time", 3, 60),
               "/set_led_brightness": ("ledBrightness", "led_brightness", 0, 100),
               "/set_night_brightness": ("NightBrightness", "night_brightness", 0, 100)}


def integer(value, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not re.fullmatch(r"-?\d+", str(value)):
        raise ValueError("Expected an integer")
    number = int(value)
    if not minimum <= number <= maximum:
        raise ValueError(f"Expected a value between {minimum} and {maximum}")
    return number


def rgb565(color: str) -> str:
    if not isinstance(color, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError("Expected #RRGGBB")
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b = r >> 3, g >> 2, b >> 3
    return f"#{(r << 3) | (r >> 2):02x}{(g << 2) | (g >> 4):02x}{(b << 3) | (b >> 2):02x}"


def clean_photo(data: bytes) -> bytes:
    """Keep JPEG coding bytes, remove metadata and check the browser's crop size."""
    if not data.startswith(b"\xff\xd8") or len(data) > MAX_PHOTO:
        raise ValueError("Expected a JPEG up to 100 KiB")
    pieces, pos, dimensions = [data[:2]], 2, None
    while pos < len(data):
        start = pos
        if data[pos] != 255:
            raise ValueError("Invalid JPEG marker")
        while pos < len(data) and data[pos] == 255:
            pos += 1
        if pos >= len(data):
            break
        marker = data[pos]
        pos += 1
        if marker == 0xD9:
            if dimensions != (240, 240):
                raise ValueError("Expected a 240 x 240 JPEG")
            return b"".join(pieces) + data[start:pos]
        if marker == 1 or 0xD0 <= marker <= 0xD7:
            pieces.append(data[start:pos])
            continue
        if pos + 2 > len(data):
            break
        length = int.from_bytes(data[pos:pos + 2], "big")
        end = pos + length
        if length < 2 or end > len(data):
            raise ValueError("Invalid JPEG segment")
        if marker in (0xC0, 0xC1, 0xC2) and length >= 7:
            dimensions = (int.from_bytes(data[pos + 5:pos + 7], "big"),
                          int.from_bytes(data[pos + 3:pos + 5], "big"))
        if not (0xE0 <= marker <= 0xEF or marker == 0xFE):
            pieces.append(data[start:end])
        pos = end
        if marker == 0xDA:
            entropy = pos
            while pos < len(data):
                marker_start = data.find(b"\xff", pos)
                if marker_start < 0:
                    raise ValueError("Missing JPEG end")
                pos = marker_start + 1
                while pos < len(data) and data[pos] == 255:
                    pos += 1
                if pos >= len(data):
                    break
                if data[pos] == 0 or 0xD0 <= data[pos] <= 0xD7:
                    pos += 1
                    continue
                pieces.append(data[entropy:marker_start])
                pos = marker_start
                break
    raise ValueError("Incomplete JPEG")


class State:
    def __init__(self, directory: Path, reset: bool = False):
        self.directory = directory
        self.path = directory / "state.json"
        self.lock = threading.RLock()
        self.upload = None
        self.data = json.loads(json.dumps(DEFAULTS))
        if self.path.exists() and not reset:
            stored = json.loads(self.path.read_text(encoding="utf-8"))
            self.data.update(stored)

    def save(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.data, ensure_ascii=False, indent=2) + "\n",
                             encoding="utf-8", newline="\n")
        temporary.replace(self.path)

    def photo(self, slot: int) -> bytes:
        custom = self.directory / f"photo-{slot}.jpg"
        if self.data["custom_photos"][slot - 1] and custom.exists():
            return custom.read_bytes()
        return (ASSETS / "photos" / f"photo-{slot}.jpg").read_bytes()


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, state: State):
        self.state = state
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    server_version = "SmallTVLocal/1.0"

    def log_message(self, format, *args):
        if not getattr(self.server, "quiet", False):
            super().log_message(format, *args)

    def send(self, body=b"", content_type="text/plain; charset=utf-8", status=200, **headers):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.send_header("X-Content-Type-Options", "nosniff")
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def json(self, value, status=200):
        self.send(json.dumps(value, ensure_ascii=False), "application/json; charset=utf-8", status)

    def local_request(self) -> bool:
        host = urlsplit("http://" + self.headers.get("Host", ""))
        if host.hostname not in ("localhost", "127.0.0.1") or host.port != self.server.server_port:
            self.json({"error": "Use the local server URL"}, 403)
            return False
        origin = self.headers.get("Origin")
        if origin and origin not in (f"http://localhost:{host.port}", f"http://127.0.0.1:{host.port}"):
            self.json({"error": "Origin does not match local server"}, 403)
            return False
        return True

    def do_GET(self):
        try:
            if not self.local_request():
                return
            url = urlsplit(self.path)
            path, query = url.path, parse_qs(url.query)
            state = self.server.state
            with state.lock:
                data = state.data
                pages = {"/setup": "setup", "/setup.html": "setup", "/settings": "settings",
                         "/settings.html": "settings", "/photo": "photo", "/photo.html": "photo",
                         "/": "settings" if data["connected"] else "setup"}
                if path in pages:
                    self.send((ROOT / "pages" / f"{pages[path]}.html").read_bytes(),
                              "text/html; charset=utf-8")
                elif path == "/scan":
                    self.json(NETWORKS)
                elif path in GET_TEXT:
                    self.send(str(data[GET_TEXT[path]]))
                elif path == "/getsettings":
                    self.json(data["settings"])
                elif path == "/get_clock_colors":
                    self.json({f"color{i}": color for i, color in enumerate(data["colors"])})
                elif path in ("/get_led_brightness", "/get_night_brightness"):
                    self.json({"brightness": data["led_brightness" if path == "/get_led_brightness"
                                                  else "night_brightness"]})
                elif path == "/get_display_time":
                    self.json({"displaytime": data["display_time"]})
                elif path == "/get_checkbox_state":
                    self.json({f"file{i + 1}_switch": on for i, on in enumerate(data["photo_enabled"])})
                elif path == "/get_Photo_File":
                    slot = integer(query.get("file", [0])[0], 1, 5)
                    chunk = integer(query.get("chunk", [0])[0], 0, 100)
                    size = integer(query.get("size", [0])[0], 0, 16 * 1024)
                    image = state.photo(slot)
                    if size == chunk == 0:
                        self.json({"exists": True, "size": len(image)})
                    elif size == 0 or chunk * size >= len(image):
                        raise ValueError("Invalid chunk index")
                    else:
                        self.send(image[chunk * size:(chunk + 1) * size], "application/octet-stream")
                elif path == "/_local/health":
                    self.json({"ok": True, "application": "SmallTVLocal", "port": self.server.server_port})
                elif path.startswith("/assets/"):
                    target = (ASSETS / unquote(path[len("/assets/"):])).resolve()
                    if not target.is_relative_to(ASSETS.resolve()) or not target.is_file():
                        self.send("Not found", status=404)
                    else:
                        self.send(target.read_bytes(), mimetypes.guess_type(target.name)[0]
                                  or "application/octet-stream")
                elif path == "/favicon.ico":
                    self.send(status=204)
                else:
                    self.send(status=302, Location="/")
        except (ValueError, KeyError, TypeError) as error:
            self.json({"error": str(error)}, 400)

    def read_body(self) -> bytes:
        length = integer(self.headers.get("Content-Length", "0"), 1, MAX_BODY)
        body = self.rfile.read(length)
        if len(body) != length:
            raise ValueError("Incomplete request")
        return body

    def fields(self, body: bytes) -> dict:
        if self.headers.get("Content-Type", "").startswith("application/json"):
            fields = json.loads(body)
            if not isinstance(fields, dict):
                raise ValueError("Expected a JSON object")
            return fields
        return {key: values[0] for key, values in parse_qs(body.decode("utf-8")).items()}

    def do_POST(self):
        try:
            if not self.local_request():
                return
            path = urlsplit(self.path).path
            body = self.read_body() if path != "/restart" else b"{}"
            state = self.server.state
            with state.lock:
                data = state.data
                if path == "/upload_chunk":
                    self.upload_chunk(body)
                    return
                fields = self.fields(body) if body != b"{}" else {}
                if path in SET_INTEGER:
                    field, key, low, high = SET_INTEGER[path]
                    data[key] = integer(fields[field], low, high)
                elif path == "/settings":
                    updated = {key: integer(fields.get(key, data["settings"][key]), 0, 1)
                               for key in ("tempUnit", "hourFormat", "mileDisplay", "timeSync")}
                    data["settings"].update(updated)
                elif path == "/set_clock_color":
                    index = integer(fields["index"], 0, 2)
                    data["colors"][index] = rgb565(fields["color"])
                elif path == "/set_checkbox_state":
                    match = re.fullmatch(r"file([1-5])-switch", str(fields["checkbox_id"]))
                    if not match or not isinstance(fields["checked"], bool):
                        raise ValueError("Invalid checkbox")
                    data["photo_enabled"][int(match[1]) - 1] = fields["checked"]
                elif path == "/updateCity":
                    value = str(fields["city"]).strip().replace("，", ",")
                    if "," not in value:
                        raise ValueError("Use City,CountryCode, for example London,GB")
                    city, country = (part.strip() for part in value.rsplit(",", 1))
                    if not city or not re.fullmatch(r"[A-Za-z]{2}", country) or len(city.encode()) > 63:
                        raise ValueError("Invalid city or country")
                    data["city"] = f"{city},{country.upper()}"
                elif path in ("/configure", "/wifireset"):
                    ssid, password = str(fields["ssid"]), str(fields.get("password", ""))
                    if not 1 <= len(ssid.encode()) <= 32 or len(password.encode()) > 63:
                        raise ValueError("Invalid Wi-Fi settings")
                    data.update(ssid=ssid, password=password, connected=True)
                    data["restart_count"] += 1
                elif path == "/advancedset":
                    values = {key: str(fields.get(key, data[key])) for key in ("ntp", "openweathermapKey")}
                    if any(len(value.encode()) > 63 for value in values.values()):
                        raise ValueError("Setting too long")
                    count = integer(fields.get("clickCount", 0), 0, 10)
                    data.update(values, clickCount=count)
                elif path == "/restart":
                    state.upload = None
                    data["restart_count"] += 1
                elif path == "/start_upload":
                    slot = integer(fields["file_number"], 1, 5)
                    size = integer(fields["file_size"], 1, MAX_PHOTO)
                    chunks = integer(fields["total_chunks"], 1, 128)
                    state.upload = {"slot": slot, "size": size, "total": chunks, "chunks": {}}
                elif path == "/finish_upload":
                    upload = state.upload
                    if not upload or integer(fields["file_number"], 1, 5) != upload["slot"]:
                        raise ValueError("No matching upload")
                    if set(upload["chunks"]) != set(range(upload["total"])):
                        raise ValueError("Incomplete upload")
                    raw = b"".join(upload["chunks"][i] for i in range(upload["total"]))
                    if len(raw) != upload["size"]:
                        raise ValueError("File length mismatch")
                    image = clean_photo(raw)
                    state.directory.mkdir(parents=True, exist_ok=True)
                    (state.directory / f"photo-{upload['slot']}.jpg").write_bytes(image)
                    data["custom_photos"][upload["slot"] - 1] = True
                    data["photo_enabled"][upload["slot"] - 1] = True
                    state.upload = None
                else:
                    self.send("Unknown firmware endpoint", status=404)
                    return
                state.save()
                self.send("Settings saved" if path == "/advancedset" else "OK")
        except (ValueError, KeyError, TypeError, UnicodeError) as error:
            self.json({"error": str(error)}, 400)

    def upload_chunk(self, body: bytes):
        state = self.server.state
        upload = state.upload
        if not upload:
            raise ValueError("No active upload")
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            raise ValueError("Expected multipart/form-data")
        envelope = (f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n").encode() + body
        message = BytesParser(policy=policy.default).parsebytes(envelope)
        fields = {part.get_param("name", header="content-disposition"): part.get_payload(decode=True)
                  for part in message.iter_parts()}
        if not all(isinstance(fields.get(key), bytes) for key in
                   ("file_number", "chunk_index", "total_chunks", "chunk")):
            raise ValueError("Missing multipart fields")
        slot = integer(fields["file_number"].decode(), 1, 5)
        index = integer(fields["chunk_index"].decode(), 0, upload["total"] - 1)
        total = integer(fields["total_chunks"].decode(), 1, 128)
        chunk = fields["chunk"]
        if slot != upload["slot"] or total != upload["total"] or not 0 < len(chunk) <= 8192:
            raise ValueError("Invalid chunk")
        previous = upload["chunks"].get(index)
        if previous is not None and previous != chunk:
            raise ValueError("Conflicting retry")
        if sum(len(value) for key, value in upload["chunks"].items() if key != index) + len(chunk) > upload["size"]:
            raise ValueError("Upload exceeds declared size")
        upload["chunks"][index] = chunk
        self.send("OK")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--state-dir", type=Path, default=ROOT / ".runtime")
    parser.add_argument("--reset", action="store_true", help="Start with defaults and original photos")
    args = parser.parse_args()
    state = State(args.state_dir, args.reset)
    if args.reset:
        state.save()
    server = Server(("127.0.0.1", args.port), state)
    print(f"Local: http://127.0.0.1:{server.server_port}/", flush=True)
    print("Pages: /settings, /photo, /setup. Stop with Ctrl+C.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
