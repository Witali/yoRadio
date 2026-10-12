"""Exercise firmware API contracts and a complete, retryable photo upload."""

import csv
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from server import ASSETS, ROOT, Server, State


class ContractTests(unittest.TestCase):
    visited = set()

    def setUp(self):
        self.test_root = ROOT / ".runtime/tests"
        self.test_root.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix="api-", dir=self.test_root)
        self.state = State(Path(self.temporary.name))
        self.server = Server(("127.0.0.1", 0), self.state)
        self.server.quiet = True
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": 0.02}, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        assert Path(self.temporary.name).resolve().is_relative_to(self.test_root.resolve())
        self.temporary.cleanup()

    def request(self, path, data=None, content_type="application/json", headers=None):
        method = "GET" if data is None else "POST"
        self.visited.add((method, path.split("?")[0]))
        if isinstance(data, dict):
            data = json.dumps(data).encode()
        elif isinstance(data, str):
            data = data.encode()
        request = Request(self.url + path, data=data,
                          headers={"Content-Type": content_type, **(headers or {})})
        try:
            with urlopen(request, timeout=3) as response:
                return response.status, response.headers, response.read()
        except HTTPError as error:
            return error.code, error.headers, error.read()

    def get_json(self, path):
        code, _, body = self.request(path)
        self.assertEqual(code, 200)
        return json.loads(body)

    def test_settings_roundtrip_and_disk_persistence(self):
        for path in ["/", "/settings", "/setup", "/photo"]:
            code, headers, body = self.request(path)
            self.assertEqual(code, 200)
            self.assertIn("charset=utf-8", headers["Content-Type"])
            self.assertIn("</html>", body.decode())
        self.assertEqual(self.get_json("/scan")[0]["ssid"], "Small_TV Demo")
        for post, fields, get, expected in [
            ("/setgifvalue", {"gif": "4"}, "/getgifvalue", b"4"),
            ("/setclocktype", {"clocktype": "2"}, "/getclocktype", b"2"),
            ("/SetTimeModeValue", {"timemode": "1"}, "/GetTimeModeValue", b"1"),
            ("/SetNightStartTime", {"StartTime": "23"}, "/GetNightStartTime", b"23"),
            ("/SetNightStopTime", {"StopTime": "6"}, "/GetNightStopTime", b"6"),
        ]:
            self.assertEqual(self.request(post, fields)[0], 200)
            self.assertEqual(self.request(get)[2], expected)
        self.assertEqual(self.request("/settings", {"tempUnit": 1, "hourFormat": 1,
                          "mileDisplay": 0, "timeSync": 1})[0], 200)
        self.assertEqual(self.get_json("/getsettings")["timeSync"], 1)
        for post, value, get in [("/set_led_brightness", "ledBrightness=73", "/get_led_brightness"),
                                 ("/set_night_brightness", "NightBrightness=19", "/get_night_brightness")]:
            self.assertEqual(self.request(post, value, "application/x-www-form-urlencoded")[0], 200)
            self.assertEqual(self.get_json(get)["brightness"], int(value.split("=")[1]))
        self.assertEqual(self.request("/set_clock_color", {"index": 1, "color": "#123456"})[0], 200)
        self.assertEqual(self.get_json("/get_clock_colors")["color1"], "#103452")
        self.assertEqual(self.request("/set_display_time", {"display_time": 17})[0], 200)
        self.assertEqual(self.get_json("/get_display_time"), {"displaytime": 17})
        self.assertEqual(self.request("/set_checkbox_state",
                          {"checkbox_id": "file3-switch", "checked": False})[0], 200)
        self.assertFalse(self.get_json("/get_checkbox_state")["file3_switch"])
        self.assertEqual(self.request("/updateCity", {"city": "Budapest,HU"})[0], 200)
        restored = State(Path(self.temporary.name))
        self.assertEqual(restored.data["city"], "Budapest,HU")
        self.assertEqual(restored.data["display_time"], 17)
        self.assertEqual(restored.data["colors"][1], "#103452")

    def test_setup_advanced_and_restart(self):
        self.assertIn(b"wifiForm", self.request("/")[2])
        self.assertEqual(self.request("/configure", {"ssid": "Test", "password": "test-only"})[0], 200)
        self.assertIn(b"cityForm", self.request("/")[2])
        self.assertEqual(self.request("/wifireset", {"ssid": "Changed", "password": "test-only"})[0], 200)
        self.assertEqual(self.request("/advancedset", {"ntp": "pool.ntp.org",
                          "openweathermapKey": "test-only", "clickCount": 10})[0], 200)
        before = self.state.data["restart_count"]
        self.assertEqual(self.request("/restart", b"")[0], 200)
        self.assertEqual(self.state.data["restart_count"], before + 1)
        self.assertEqual(State(Path(self.temporary.name)).data["ssid"], "Changed")

    def multipart(self, payload, index, count, slot=2):
        boundary = "SmallTVContractBoundary"
        fields = {"file_number": str(slot).encode(), "chunk_index": str(index).encode(),
                  "total_chunks": str(count).encode(), "chunk": payload}
        chunks = []
        for name, value in fields.items():
            filename = '; filename="blob"' if name == "chunk" else ""
            chunks.append((f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"'
                           f'{filename}\r\n\r\n').encode() + value + b"\r\n")
        return self.request("/upload_chunk", b"".join(chunks) + f"--{boundary}--\r\n".encode(),
                            f"multipart/form-data; boundary={boundary}")

    def test_photo_upload_retry_finish_and_download(self):
        original = (ASSETS / "photos/photo-2.jpg").read_bytes()
        payload = (ASSETS / "photos/photo-5.jpg").read_bytes()
        chunks = [payload[index:index + 4096] for index in range(0, len(payload), 4096)]
        info = self.get_json("/get_Photo_File?file=2&chunk=0&size=0")
        self.assertEqual(info, {"exists": True, "size": len(original)})
        self.assertEqual(self.request("/start_upload", {"file_number": 2, "file_size": len(payload),
                          "total_chunks": len(chunks)})[0], 200)
        self.assertEqual(self.multipart(chunks[0], 0, len(chunks))[0], 200)
        self.assertEqual(self.multipart(chunks[0], 0, len(chunks))[0], 200)
        self.assertEqual(self.request("/finish_upload", {"file_number": 2})[0], 400)
        self.assertEqual(self.state.photo(2), original)
        for index, chunk in enumerate(chunks[1:], 1):
            self.assertEqual(self.multipart(chunk, index, len(chunks))[0], 200)
        self.assertEqual(self.request("/finish_upload", {"file_number": 2})[0], 200)
        self.assertEqual(self.state.photo(2), payload)
        downloaded = b"".join(self.request(f"/get_Photo_File?file=2&chunk={i}&size=10240")[2]
                              for i in range((len(payload) + 10239) // 10240))
        self.assertEqual(downloaded, payload)
        self.assertEqual((ASSETS / "photos/photo-2.jpg").read_bytes(), original)
        self.assertEqual(State(Path(self.temporary.name)).photo(2), payload)

    def test_invalid_requests_do_not_change_state(self):
        before = json.dumps(self.state.data, sort_keys=True)
        for path, data in [("/setgifvalue", {"gif": 99}), ("/set_clock_color", {"index": 9, "color": "#123456"}),
                           ("/start_upload", {"file_number": 9, "file_size": 12, "total_chunks": 1}),
                           ("/start_upload", {"file_number": 1, "file_size": 200000, "total_chunks": 1}),
                           ("/settings", {"tempUnit": 1, "hourFormat": 99}),
                           ("/configure", {"ssid": ""})]:
            self.assertEqual(self.request(path, data)[0], 400)
        self.assertEqual(self.request("/settings", b"x" * 20000)[0], 400)
        self.assertEqual(self.request("/get_Photo_File?file=1&size=100000&chunk=0")[0], 400)
        self.assertEqual(self.request("/restart", b"", headers={"Origin": "https://example.com"})[0], 403)
        self.assertEqual(json.dumps(self.state.data, sort_keys=True), before)
        self.assertFalse(self.state.path.exists())

    @classmethod
    def tearDownClass(cls):
        methods = {"1": "GET", "3": "POST"}
        with (ROOT.parent / "analysis/security/registered-routes.tsv").open() as handle:
            registered = {(methods[record["method"]], record["uri"])
                          for record in csv.DictReader(handle, delimiter="\t")}
        missing = registered - cls.visited
        if missing:
            raise AssertionError(f"Untested firmware routes: {missing}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
