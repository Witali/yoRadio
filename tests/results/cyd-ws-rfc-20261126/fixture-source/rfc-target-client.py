"""Private, explicitly released loopback WS/WSS application conformance client.

No QEMU/process/credential management. --self-test never contacts a guest.
Network cases run only with --execute and an explicit loopback endpoint.
This client is independent of the firmware's parser and command dispatch.
"""
import argparse
import base64
import collections
import contextlib
import dataclasses
import hashlib
import http.client
import json
from pathlib import Path
import re
import secrets
import socket
import ssl
import struct
import sys
import threading
import time
import urllib.parse


GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
ROOT = Path(__file__).resolve().parents[3]  # Private draft is one directory deeper.
PRIVATE_ROOT = ROOT / ".build/cpbuf24"
MAX_MESSAGE = 5120
MAX_HTTP = 16384
MAX_EVENTS = 96
MAX_FRAME_EVENTS = 128
NORMAL_TIMEOUT = 12.0


class CheckFailure(Exception):
    def __init__(self, category, scope="project"):
        super().__init__(category)
        self.category, self.scope = category, scope


class NotExercised(Exception):
    pass


class PeerEOF(Exception):
    def __init__(self, clean_tls=None):
        self.clean_tls = clean_tls


def require(value, category, scope="project"):
    if not value:
        raise CheckFailure(category, scope)


def digest(body):
    return hashlib.sha256(body).hexdigest()


def error_category(error):
    # Avoid serializing arbitrary socket/TLS error strings or private paths.
    return getattr(error, "category", type(error).__name__)


@dataclasses.dataclass
class Budget:
    seconds: float
    clock: object = time.monotonic

    def __post_init__(self):
        self.end = self.clock() + self.seconds

    def remaining(self):
        left = self.end - self.clock()
        if left <= 0:
            raise CheckFailure("host-deadline-expired", "transport")
        return left


class WireIO:
    def __init__(self, sock, secure=False):
        self.sock, self.secure = sock, secure
        self.buffer = bytearray()
        self.sent_bytes = self.received_bytes = 0

    def send(self, body, budget):
        view = memoryview(body)
        while view:
            self.sock.settimeout(budget.remaining())
            sent = self.sock.send(view)
            require(0 < sent <= len(view), "invalid-send-progress", "transport")
            self.sent_bytes += sent
            view = view[sent:]
        budget.remaining()

    def _receive(self, budget, maximum=4096):
        self.sock.settimeout(budget.remaining())
        try:
            body = self.sock.recv(maximum)
        except ssl.SSLEOFError as error:
            raise PeerEOF(False) from error
        if not body:
            raise PeerEOF(True if self.secure else None)
        self.received_bytes += len(body)
        self.buffer.extend(body)
        budget.remaining()

    def exact(self, size, budget):
        require(0 <= size <= MAX_MESSAGE + MAX_HTTP, "client-read-bound", "client")
        while len(self.buffer) < size:
            self._receive(budget)
        result = bytes(self.buffer[:size])
        del self.buffer[:size]
        return result

    def peek(self, size, budget):
        require(0 <= size <= MAX_MESSAGE + MAX_HTTP, "client-read-bound", "client")
        while len(self.buffer) < size:
            self._receive(budget)
        return bytes(self.buffer[:size])

    def http_headers(self, budget):
        while True:
            end = self.buffer.find(b"\r\n\r\n")
            if end >= 0:
                require(end + 4 <= MAX_HTTP, "http-header-bound", "client")
                body = bytes(self.buffer[:end + 4])
                del self.buffer[:end + 4]
                return parse_http_headers(body)
            require(len(self.buffer) < MAX_HTTP, "http-header-bound", "client")
            self._receive(budget, min(4096, MAX_HTTP - len(self.buffer)))


def parse_http_headers(body):
    require(body.endswith(b"\r\n\r\n"), "http-unterminated", "client")
    lines = body[:-4].split(b"\r\n")
    match = re.fullmatch(rb"HTTP/(\d+)\.(\d+) (\d{3})(?: [\x20-\x7e]*)?", lines[0])
    require(match is not None, "http-status-line", "rfc")
    headers = collections.defaultdict(list)
    for line in lines[1:]:
        require(b":" in line and not line[:1].isspace(), "http-response-header", "rfc")
        key, value = line.split(b":", 1)
        require(re.fullmatch(rb"[!#$%&'*+.^_`|~0-9A-Za-z-]+", key) is not None,
                "http-response-header-name", "rfc")
        headers[key.decode("ascii").lower()].append(value.strip().decode("latin-1"))
    return int(match[3]), dict(headers)


def encode_frame(opcode, payload=b"", *, final=True, mask=True, rsv=0,
                 length_kind=None, declared_length=None, mask_key=None):
    require(0 <= opcode <= 15 and 0 <= rsv <= 7, "encoder-fields", "client")
    size = len(payload) if declared_length is None else declared_length
    require(0 <= size < 1 << 64, "encoder-length", "client")
    kind = length_kind if length_kind is not None else 0 if size < 126 else 16 if size <= 65535 else 64
    first = (128 if final else 0) | (rsv << 4) | opcode
    if kind == 0:
        require(size < 126, "encoder-short-length", "client")
        header = bytes((first, (128 if mask else 0) | size))
    elif kind == 16:
        require(size <= 65535, "encoder-u16-length", "client")
        header = bytes((first, (128 if mask else 0) | 126)) + struct.pack("!H", size)
    elif kind == 64:
        header = bytes((first, (128 if mask else 0) | 127)) + struct.pack("!Q", size)
    else:
        raise CheckFailure("encoder-length-kind", "client")
    if not mask:
        return header + payload
    key = secrets.token_bytes(4) if mask_key is None else mask_key
    require(len(key) == 4, "encoder-mask-width", "client")
    return header + key + bytes(value ^ key[index & 3] for index, value in enumerate(payload))


class FrameReader:
    def __init__(self, wire, expect_mask=False, maximum=MAX_MESSAGE):
        self.wire, self.expect_mask, self.maximum = wire, expect_mask, maximum

    def read(self, budget):
        first, second = self.wire.peek(2, budget)
        final, rsv, opcode = bool(first & 128), (first >> 4) & 7, first & 15
        require(rsv == 0, "server-unnegotiated-rsv", "rfc")
        require(opcode in (0, 1, 2, 8, 9, 10), "server-reserved-opcode", "rfc")
        masked, short = bool(second & 128), second & 127
        require(masked == self.expect_mask, "server-mask-direction", "rfc")
        size = short
        offset = 2
        if short == 126:
            size = struct.unpack("!H", self.wire.peek(4, budget)[2:4])[0]
            offset = 4
            require(size >= 126, "server-nonminimal-u16", "rfc")
        elif short == 127:
            size = struct.unpack("!Q", self.wire.peek(10, budget)[2:10])[0]
            offset = 10
            require(size >= 65536 and not size & (1 << 63), "server-invalid-u64", "rfc")
        if opcode >= 8:
            require(final and size <= 125, "server-control-shape", "rfc")
        require(size <= self.maximum, "server-message-policy-bound", "project")
        total = offset + (4 if masked else 0) + size
        complete = self.wire.peek(total, budget)
        key = complete[offset:offset + 4] if masked else None
        body = complete[offset + (4 if masked else 0):]
        self.wire.exact(total, budget)
        if key is not None:
            body = bytes(value ^ key[index & 3] for index, value in enumerate(body))
        return dict(opcode=opcode, final=final, payload=body, length_kind=short)


def close_payload(code=1000, reason=b""):
    return struct.pack("!H", code) + reason


def parse_close(body):
    require(len(body) != 1, "server-one-byte-close", "rfc")
    if not body:
        return None
    code = struct.unpack("!H", body[:2])[0]
    valid = 1000 <= code <= 1003 or 1007 <= code <= 1014 or 3000 <= code <= 4999
    require(valid, "server-forbidden-close-code", "rfc")
    try:
        body[2:].decode("utf-8")
    except UnicodeDecodeError as error:
        raise CheckFailure("server-invalid-close-utf8", "rfc") from error
    return code


def strict_context(cafile):
    require(cafile is not None, "wss-ca-required", "setup")
    context = ssl.create_default_context(cafile=str(cafile))
    context.minimum_version = context.maximum_version = ssl.TLSVersion.TLSv1_2
    require(context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname,
            "strict-tls-context-required", "setup")
    return context


@dataclasses.dataclass
class Endpoint:
    url: str
    ca: object = None
    expected_certificate_sha256: object = None

    def __post_init__(self):
        parsed = urllib.parse.urlsplit(self.url)
        require(parsed.scheme in ("ws", "wss"), "endpoint-scheme", "setup")
        require(parsed.username is None and parsed.password is None, "endpoint-userinfo", "setup")
        require(parsed.path == "/ws" and not parsed.query and not parsed.fragment,
                "endpoint-route", "setup")
        host = parsed.hostname
        require(host in ("localhost", "127.0.0.1", "::1"), "loopback-endpoint-required", "setup")
        self.host, self.port = host, parsed.port or (443 if parsed.scheme == "wss" else 80)
        require(0 < self.port < 65536, "endpoint-port", "setup")
        self.secure = parsed.scheme == "wss"
        self.connect_host = "127.0.0.1" if host == "localhost" else host
        authority = "[::1]" if host == "::1" else host
        self.authority = authority + ":" + str(self.port)
        self.context = strict_context(self.ca) if self.secure else None
        self.owned_sockets, self.aborted = [], False

    def abort_owned(self):
        self.aborted = True
        for sock in list(self.owned_sockets):
            with contextlib.suppress(OSError):
                sock.shutdown(socket.SHUT_RDWR)
            with contextlib.suppress(OSError):
                sock.close()

    def dial(self, budget, *, context=None, name=None):
        require(not self.aborted, "mode-watchdog-expired", "transport")
        raw = socket.create_connection((self.connect_host, self.port), timeout=budget.remaining())
        self.owned_sockets.append(raw)
        raw.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        if not self.secure:
            return raw, None
        selected = self.context if context is None else context
        require(selected.verify_mode == ssl.CERT_REQUIRED and selected.check_hostname,
                "weak-tls-context", "setup")
        tls = None
        try:
            raw.settimeout(budget.remaining())
            tls = selected.wrap_socket(raw, server_hostname=self.host if name is None else name,
                                       suppress_ragged_eofs=False)
            self.owned_sockets.append(tls)
            require(tls.version() == "TLSv1.2", "unexpected-tls-version", "transport")
            certificate = tls.getpeercert(binary_form=True)
            require(bool(certificate), "missing-peer-certificate", "transport")
            fingerprint = digest(certificate)
            if self.expected_certificate_sha256:
                require(fingerprint == self.expected_certificate_sha256,
                        "unexpected-peer-certificate", "transport")
            return tls, dict(version=tls.version(), cipher=tls.cipher()[0],
                             certificate_sha256=fingerprint, verify_mode="CERT_REQUIRED",
                             verification_flags=int(selected.verify_flags),
                             hostname_checked=True, verification_name=self.host if name is None else name,
                             host_date_verification_enabled=True)
        except BaseException:
            if tls is not None:
                tls.close()
            raw.close()
            raise


class Session:
    def __init__(self, wire, metadata=None):
        self.wire, self.tls_metadata = wire, metadata
        self.reader = FrameReader(wire)
        self.events, self.frames = [], []
        self.events_observed = self.frames_observed = 0
        self.opcode, self.pending = None, bytearray()
        self.close_sent = False
        self.close_received = None
        self.close_seen = False
        self.closed_transport = False
        self.application_pongs = 0
        self.responses = collections.Counter()

    def record_frame(self, direction, opcode, final, payload):
        self.frames_observed += 1
        if len(self.frames) < MAX_FRAME_EVENTS:
            self.frames.append(dict(direction=direction, opcode=opcode, final=final,
                                    bytes=len(payload), sha256=digest(payload)))

    def send_raw(self, body, budget):
        self.wire.send(body, budget)

    def send(self, opcode, payload=b"", final=True, budget=None):
        budget = Budget(NORMAL_TIMEOUT) if budget is None else budget
        self.send_raw(encode_frame(opcode, payload, final=final), budget)
        self.record_frame("client", opcode, final, payload)
        if opcode == 8:
            self.close_sent = True

    def event(self, budget):
        while True:
            frame = self.reader.read(budget)
            opcode, final, body = frame["opcode"], frame["final"], frame["payload"]
            self.record_frame("server", opcode, final, body)
            if self.close_seen:
                require(opcode >= 8, "server-data-after-close", "rfc")
            if opcode == 9:
                if not self.close_seen:
                    self.send(10, body, budget=budget)
                return "ping", body
            if opcode == 10:
                return "pong", body
            if opcode == 8:
                parse_close(body)
                self.close_seen, self.close_received = True, body
                return "close", body
            require(not self.close_seen, "server-data-after-close", "rfc")
            if opcode == 0:
                require(self.opcode is not None, "server-unexpected-continuation", "rfc")
            else:
                require(self.opcode is None, "server-interleaved-data", "rfc")
                self.opcode = opcode
            require(len(self.pending) + len(body) <= MAX_MESSAGE, "server-logical-message-bound", "project")
            self.pending.extend(body)
            if not final:
                continue
            kind, complete = self.opcode, bytes(self.pending)
            self.opcode, self.pending = None, bytearray()
            if kind == 2:
                raise CheckFailure("unexpected-server-binary-application", "project")
            try:
                obj = json.loads(complete.decode("utf-8"))
            except UnicodeDecodeError as error:
                raise CheckFailure("server-text-invalid-utf8", "rfc") from error
            except (ValueError, TypeError) as error:
                raise CheckFailure("server-text-invalid-json", "project") from error
            require(isinstance(obj, dict), "server-json-not-object", "project")
            label = "other-json"
            if type(obj.get("pong")) is int and obj["pong"] == 1:
                self.application_pongs += 1
                label = "application-pong"
            elif "status" in obj:
                status, payload = obj["status"], obj.get("payload")
                require(isinstance(status, dict) and isinstance(payload, list), "incomplete-server-status")
                require(type(status.get("audio")) is bool and type(status.get("generation")) is int,
                        "server-status-types")
                require(all(isinstance(status.get(key), str) for key in ("station", "title", "format")),
                        "server-status-strings")
                try:
                    values = {entry["id"]: entry["value"] for entry in payload}
                except (KeyError, TypeError) as error:
                    raise CheckFailure("server-status-payload") from error
                require(values.get("meta") == status["title"] and values.get("fmt") == status["format"],
                        "server-status-consistency")
                label = "status"
            elif "commandError" in obj:
                label = "command-error"
            elif "capabilities" in obj:
                label = "capabilities"
            elif "current" in obj:
                label = "current"
            elif "playermode" in obj:
                label = "playermode"
            elif "file" in obj:
                label = "playlist-event"
            if label in ("application-pong", "command-error", "capabilities"):
                self.responses[label] += 1
            if len(self.events) < MAX_EVENTS:
                self.events.append(dict(event=label, bytes=len(complete), sha256=digest(complete)))
            self.events_observed += 1
            return label, obj

    def wait(self, kind, predicate=None, budget=None):
        budget = Budget(NORMAL_TIMEOUT) if budget is None else budget
        while True:
            event, value = self.event(budget)
            require(event != "close" or kind == "close", "unexpected-server-close")
            if event == kind and (predicate is None or predicate(value)):
                return value

    def command(self, text, response="application-pong", budget=None):
        budget = Budget(NORMAL_TIMEOUT) if budget is None else budget
        self.send(1, text, budget=budget)
        return self.wait(response, budget=budget)

    def assert_no_application_pong(self, seconds=0.12):
        before = dict(self.responses)
        budget = Budget(seconds)
        while True:
            try:
                event, _ = self.event(budget)
                require(event != "close", "closed-before-message-fin")
            except (socket.timeout, TimeoutError):
                break
            except CheckFailure as error:
                if error.category == "host-deadline-expired":
                    break
                raise
        require(dict(self.responses) == before, "application-dispatched-before-fin")

    def expect_close(self, code, *, payload=None, clean_tls=False, allow_bare_eof=False, budget=None):
        budget = Budget(NORMAL_TIMEOUT) if budget is None else budget
        try:
            body = self.close_received if self.close_seen else self.wait("close", budget=budget)
        except PeerEOF:
            if allow_bare_eof:
                return dict(observed_code=None, project_close_policy=False, disconnected=True)
            raise CheckFailure("missing-required-close", "rfc")
        observed = parse_close(body)
        matches = observed in code if isinstance(code, (tuple, list, set)) else observed == code
        policy = matches and (payload is None or body == payload)
        if not self.close_sent:
            with contextlib.suppress(OSError, PeerEOF):
                self.send(8, body, budget=budget)
        while True:
            try:
                kind, _ = self.event(budget)
                require(kind in ("close", "ping", "pong"), "server-data-after-close", "rfc")
            except PeerEOF as ended:
                if clean_tls and self.wire.secure:
                    require(ended.clean_tls is True, "clean-close-missing-tls-alert")
                break
        return dict(observed_code=observed, project_close_policy=policy, disconnected=True)

    def normal_close(self, budget=None):
        budget = Budget(NORMAL_TIMEOUT) if budget is None else budget
        previous_responses = dict(self.responses)
        body = close_payload()
        self.send(8, body, budget=budget)
        result = self.expect_close(1000, payload=body, clean_tls=True, budget=budget)
        require(result["project_close_policy"], "normal-close-payload-policy")
        require(dict(self.responses) == previous_responses, "extra-application-response-before-close")

    def close_transport(self):
        if not self.closed_transport:
            self.closed_transport = True
            self.wire.sock.close()

    def summary(self):
        return dict(frames=self.frames, events=self.events,
                    frames_observed=self.frames_observed, events_observed=self.events_observed,
                    evidence_truncated=self.frames_observed > MAX_FRAME_EVENTS or self.events_observed > MAX_EVENTS,
                    sent_bytes=self.wire.sent_bytes, received_bytes=self.wire.received_bytes,
                    application_pongs=self.application_pongs, close_sent=self.close_sent,
                    application_responses=dict(self.responses),
                    close_seen=self.close_seen, observed_close_code=parse_close(self.close_received) if self.close_seen else None,
                    tls=self.tls_metadata, handshake=getattr(self, "handshake_metadata", None))


def request_bytes(authority, key, *, method="GET", version="1.1", modifications=None):
    headers = [("Host", authority), ("Upgrade", "websocket"), ("Connection", "Upgrade"),
               ("Sec-WebSocket-Key", key), ("Sec-WebSocket-Version", "13")]
    if modifications is not None:
        headers = modifications(headers)
    return (f"{method} /ws HTTP/{version}\r\n" +
            "".join(f"{name}: {value}\r\n" for name, value in headers) + "\r\n").encode("ascii")


def validate_declined_negotiation(headers, offered_protocols, offered_deflate):
    """Validate only the two existing H19/H21 offers; no extension data decoder."""
    protocol = headers.get("sec-websocket-protocol")
    extension = headers.get("sec-websocket-extensions")
    if protocol is not None:
        require(len(protocol) == 1 and protocol[0] in offered_protocols,
                "unexpected-negotiation", "rfc")
    if extension is not None:
        require(offered_deflate and len(extension) == 1, "unexpected-negotiation", "rfc")
        parts = [part.strip(" \t") for part in extension[0].split(";")]
        require(parts[0] == "permessage-deflate", "unexpected-negotiation", "rfc")
        # RFC7692 response parameters for H21's fixed client_max_window_bits
        # offer: no numeric hint and no server window limit were imposed.
        seen = set()
        for part in parts[1:]:
            field = part.split("=", 1)
            name = field[0].strip(" \t")
            require(name not in seen, "unexpected-negotiation", "rfc")
            seen.add(name)
            if name in ("server_no_context_takeover", "client_no_context_takeover"):
                require(len(field) == 1, "unexpected-negotiation", "rfc")
            else:
                require(name in ("server_max_window_bits", "client_max_window_bits") and len(field) == 2,
                        "unexpected-negotiation", "rfc")
                value = field[1].strip(" \t")
                if re.fullmatch(r'"(?:\\?[0-9])+"', value):
                    value = value[1:-1].replace("\\", "")
                require(re.fullmatch(r"8|9|1[0-5]", value) is not None,
                        "unexpected-negotiation", "rfc")
    return protocol is not None or extension is not None


def upgrade(endpoint, budget, *, modifications=None, method="GET", version="1.1",
            first_frame=b"", bytewise=False, offered_protocols=(), offered_deflate=False):
    sock, tls = endpoint.dial(budget)
    wire = WireIO(sock, endpoint.secure)
    key = base64.b64encode(secrets.token_bytes(16)).decode("ascii")
    request = request_bytes(endpoint.authority, key, method=method, version=version,
                            modifications=modifications)
    try:
        if bytewise:
            for value in request:
                wire.send(bytes((value,)), budget)
                time.sleep(0.001)
            if first_frame:
                wire.send(first_frame, budget)
        else:
            wire.send(request + first_frame, budget)
        status, headers = wire.http_headers(budget)
        session = Session(wire, tls)
        session.handshake_metadata = dict(request_bytes=len(request), request_sha256=digest(request),
                                          http_status=status, bytewise_writes=bytewise,
                                          combined_first_frame_bytes=len(first_frame))
        if status == 101:
            require(headers.get("sec-websocket-accept") == [base64.b64encode(hashlib.sha1(key.encode() + GUID).digest()).decode()],
                    "incorrect-upgrade-accept", "rfc")
            require("websocket" in [token.strip().lower() for token in ",".join(headers.get("upgrade", [])).split(",")],
                    "missing-response-upgrade", "rfc")
            require("upgrade" in [token.strip().lower() for token in ",".join(headers.get("connection", [])).split(",")],
                    "missing-response-connection", "rfc")
            if validate_declined_negotiation(headers, offered_protocols, offered_deflate):
                session.handshake_metadata["valid_offered_negotiation_selected"] = True
        return session, status, headers
    except BaseException:
        sock.close()
        raise


class DirectHTTPConnection(http.client.HTTPConnection):
    def __init__(self, endpoint):
        super().__init__(endpoint.host, endpoint.port, timeout=NORMAL_TIMEOUT)
        self.endpoint = endpoint

    def connect(self):
        self.sock, self.tls_metadata = self.endpoint.dial(Budget(NORMAL_TIMEOUT))


class Health:
    def __init__(self, endpoint):
        self.endpoint, self.connection = endpoint, None

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def read(self, path="/api/native/health"):
        if self.connection is None:
            self.connection = DirectHTTPConnection(self.endpoint)
        try:
            self.connection.request("GET", path, headers={"Host": self.endpoint.authority})
            response = self.connection.getresponse()
            require(response.status == 200, "health-http-status", "resource")
            body = response.read(MAX_HTTP + 1)
            require(len(body) <= MAX_HTTP, "health-body-bound", "resource")
            obj = json.loads(body)
            require(isinstance(obj, dict), "health-contract", "resource")
            if path == "/api/native/health":
                require(isinstance(obj.get("boot_id"), str), "health-contract", "resource")
            return obj
        except BaseException:
            self.close()
            raise


def health_summary(value):
    if value is None:
        return None
    driver, output = value.get("output_driver", {}), value.get("output", {})
    return dict(boot_id=value.get("boot_id"), uptime_ms=value.get("uptime_ms"),
                heap=value.get("heap"), largest=value.get("largest"), minimum_heap=value.get("minimum_heap"),
                allocation_failures=value.get("allocation_failures"),
                decoder_sequence=value.get("decoder_failure", {}).get("sequence"),
                stream_sequence=value.get("stream_failure", {}).get("sequence"),
                output_failures=output.get("failures"), write_errors=driver.get("errors"),
                write_timeouts=driver.get("timeouts"), short_writes=driver.get("short_writes"),
                completion_queue_drops=driver.get("completion_queue_drops"))


def health_verdict(before, after):
    if before is None or after is None:
        return "NOT_EXERCISED"
    if before["boot_id"] != after["boot_id"]:
        return "FAIL"
    for key in ("allocation_failures", "decoder_sequence", "stream_sequence", "output_failures",
                "write_errors", "write_timeouts", "short_writes"):
        if type(before.get(key)) is not int or type(after.get(key)) is not int:
            return "NOT_EXERCISED"
        if after[key] != before[key]:
            return "FAIL"
    if before.get("completion_queue_drops") is not None and (
            after.get("completion_queue_drops") != before["completion_queue_drops"]):
        return "FAIL"
    return "PASS"


CASE_TITLES = {}
for prefix, titles in {
    "H": ["canonical", "header-token-OWS", "bytewise-upgrade", "upgrade-plus-first-frame", "missing-host",
          "duplicate-host", "missing-key", "wrong-nonce-length", "bad-key-base64", "duplicate-key",
          "unsupported-version", "malformed-version", "duplicate-version", "http10", "post-method",
          "missing-connection", "wrong-connection", "missing-upgrade", "other-upgrade", "subprotocol-declined",
          "duplicate-subprotocol", "extension-declined", "malformed-extension", "ordinary-GET", "empty-content-length"],
    "D": ["ping", "ping-flag", "two-fragments", "four-fragments", "empty-fragments", "two-messages",
          "split-euro", "overlong-UTF8", "surrogate-UTF8", "truncated-UTF8", "NUL-command", "empty-command",
          "ASCII96", "fragments96", "ASCII97", "fragments97", "binary-policy", "split-four-byte-scalar",
          "above-unicode-range", "stray-continuation", "UTF8-96", "UTF8-97"],
    "C": ["empty-ping", "binary-ping125", "interleaved-controls", "unsolicited-pong", "fragmented-ping", "control126"],
    "F": ["unmasked", "unnegotiated-RSV", "reserved-data-op", "reserved-control-op", "orphan-CONT",
          "nested-TEXT", "nested-BINARY", "nonminimal16", "nonminimal64", "high-bit-length", "canonical126-limit", "canonical65536-limit"],
    "R": ["twenty-clean-cycles", "error-reconnect-no-stale-pong", "two-client-admission", "partial-frame-EOF",
          "bytewise-frame", "fragment-expiry", "bounded-slow-reader"],
}.items():
    for index, title in enumerate(titles):
        CASE_TITLES[f"{prefix}{index:02d}"] = title
for key, title in [("K00", "empty-close"), ("K01", "close-reason"), ("K02", "private-close"),
                   ("K03", "one-byte-close"), ("K04a", "reserved1004"), ("K04b", "reserved1005"),
                   ("K04c", "reserved1006"), ("K04d", "reserved1015"), ("K05", "invalid-close-UTF8"),
                   ("K06", "data-after-close"), ("K07", "concurrent-close-attempt"),
                   ("K08", "close-mid-message"), ("K09", "abrupt-EOF")]:
    CASE_TITLES[key] = title
CASE_IDS = [key for prefix in "HDCFKR" for key in sorted(CASE_TITLES) if key.startswith(prefix)]
assert len(CASE_IDS) == len(set(CASE_IDS)) == 85


class CaseContext:
    def __init__(self, endpoint, health, key):
        self.endpoint, self.health, self.key = endpoint, health, key
        seconds = 120 if key == "R00" else 30 if key in ("R03", "R05", "R06") else NORMAL_TIMEOUT
        self.budget = Budget(seconds)
        self.sessions, self.notes = [], []
        self.project_policy = True

    def session(self, **options):
        budget = options.pop("_budget", self.budget)
        session, status, headers = upgrade(self.endpoint, budget, **options)
        self.sessions.append(session)
        require(status == 101, "valid-upgrade-rejected", "rfc")
        return session

    def error_close(self, session, code, *, clean_tls=False):
        previous_responses = dict(session.responses)
        outcome = session.expect_close(code, clean_tls=clean_tls, allow_bare_eof=True, budget=self.budget)
        require(dict(session.responses) == previous_responses, "malformed-message-dispatched")
        self.project_policy &= outcome["project_close_policy"]
        self.notes.append(outcome)

    def cleanup(self):
        for session in self.sessions:
            session.close_transport()


def run_case(context):
    group = context.key[0]
    handler = {"H": handshake_case, "D": data_case, "C": control_case,
               "F": framing_case, "K": close_case, "R": recovery_case}.get(group)
    if handler is None:
        raise NotExercised("case-group-not-implemented")
    return handler(context)


def drop_headers(headers, *names):
    omitted = {name.lower() for name in names}
    return [(name, value) for name, value in headers if name.lower() not in omitted]


def replace_header(headers, name, value):
    return [(key, value if key.lower() == name.lower() else old) for key, old in headers]


def handshake_case(ctx):
    index = int(ctx.key[1:])
    accepted = index in (0, 1, 2, 3, 19, 21)
    modifications = None
    options = {}
    if index == 1:
        def modifications(headers):
            result = []
            for key, value in reversed(headers):
                if key.lower() == "connection":
                    value = "keep-alive, Upgrade"
                elif key.lower() == "upgrade":
                    value = "WebSocket"
                elif key.lower() == "sec-websocket-key":
                    value = "\t" + value + " \t"
                result.append((key.swapcase(), value))
            origin = ("https" if ctx.endpoint.secure else "http") + "://" + ctx.endpoint.authority
            return result + [("Origin", origin)]
    elif index == 2:
        options["bytewise"] = True
    elif index == 3:
        options["first_frame"] = encode_frame(1, b"ping")
    elif index == 4:
        modifications = lambda h: drop_headers(h, "Host")
    elif index == 5:
        modifications = lambda h: h + [("Host", ctx.endpoint.authority)]
    elif index == 6:
        modifications = lambda h: drop_headers(h, "Sec-WebSocket-Key")
    elif index == 7:
        modifications = lambda h: replace_header(h, "Sec-WebSocket-Key", base64.b64encode(b"short").decode())
    elif index == 8:
        modifications = lambda h: replace_header(h, "Sec-WebSocket-Key", "!invalid!")
    elif index == 9:
        modifications = lambda h: h + [("Sec-WebSocket-Key", base64.b64encode(b"0123456789abcdef").decode())]
    elif index == 10:
        modifications = lambda h: replace_header(h, "Sec-WebSocket-Version", "12")
    elif index == 11:
        modifications = lambda h: replace_header(h, "Sec-WebSocket-Version", "013")
    elif index == 12:
        modifications = lambda h: h + [("Sec-WebSocket-Version", "13")]
    elif index == 13:
        options["version"] = "1.0"
    elif index == 14:
        options["method"] = "POST"
    elif index == 15:
        modifications = lambda h: drop_headers(h, "Connection")
    elif index == 16:
        modifications = lambda h: replace_header(h, "Connection", "keep-alive")
    elif index == 17:
        modifications = lambda h: drop_headers(h, "Upgrade")
    elif index == 18:
        modifications = lambda h: replace_header(h, "Upgrade", "h2c")
    elif index == 19:
        modifications = lambda h: h + [("Sec-WebSocket-Protocol", "chat, radio")]
        options["offered_protocols"] = ("chat", "radio")
    elif index == 20:
        modifications = lambda h: h + [("Sec-WebSocket-Protocol", "chat, chat")]
    elif index == 21:
        modifications = lambda h: h + [("Sec-WebSocket-Extensions", "permessage-deflate; client_max_window_bits")]
        options["offered_deflate"] = True
    elif index == 22:
        modifications = lambda h: h + [("Sec-WebSocket-Extensions", 'private; p="two words"')]
    elif index == 23:
        modifications = lambda h: drop_headers(h, "Upgrade", "Connection")
    elif index == 24:
        modifications = lambda h: h + [("Content-Length", "")]
    elif index != 0:
        raise NotExercised("handshake-vector-not-implemented")
    session, status, headers = upgrade(ctx.endpoint, ctx.budget, modifications=modifications, **options)
    ctx.sessions.append(session)
    ctx.notes.append(dict(http_status=status, expected_upgrade=accepted))
    if accepted:
        require(status == 101, "valid-upgrade-rejected", "rfc")
        if session.handshake_metadata.get("valid_offered_negotiation_selected"):
            ctx.project_policy = False
            ctx.notes.append(dict(valid_offered_negotiation=True, project_decline_policy=False,
                                  application_exchange_not_exercised=True))
            # This client does not implement the offered alternate application
            # protocol or compressed data. Stop before claiming that exchange.
            session.close_transport()
            return
        if index == 3:
            session.wait("application-pong", budget=ctx.budget)
        else:
            session.command(b"ping", budget=ctx.budget)
        session.normal_close(ctx.budget)
    else:
        require(status != 101, "invalid-upgrade-accepted", "rfc")
        if index == 10:
            require(status == 426, "unsupported-version-status-policy")
            offered = [part.strip() for value in headers.get("sec-websocket-version", []) for part in value.split(",")]
            require("13" in offered, "unsupported-version-response-missing-supported-version", "rfc")
        if index in (11, 20, 22, 23, 24):
            require(status == 400, "bad-request-status-policy")
        # HTTP rejection can legally keep an ordinary HTTP connection alive.
        # Close it locally; session/resource cleanup is observed separately.
        session.close_transport()


def note_raw(ctx, session, body):
    ctx.notes.append(dict(raw_input_bytes=len(body), raw_input_sha256=digest(body)))
    session.send_raw(body, ctx.budget)


def finish_unknown(ctx, session, payload, expected_error=None):
    session.send(1, payload, budget=ctx.budget)
    obj = session.wait("command-error", budget=ctx.budget)
    if expected_error is not None:
        require(obj.get("commandError") == expected_error, "application-error-policy")
    session.command(b"ping", budget=ctx.budget)
    session.normal_close(ctx.budget)


def fragments(ctx, session, parts, *, opcode=1, no_early=True):
    require(bool(parts), "client-empty-fragment-plan", "client")
    for index, body in enumerate(parts):
        final = index == len(parts) - 1
        session.send(opcode if index == 0 else 0, body, final=final, budget=ctx.budget)
        if not final and no_early:
            session.assert_no_application_pong(0.06)


def data_case(ctx):
    index, session = int(ctx.key[1:]), ctx.session()
    if index in (0, 1):
        session.command(b"ping" if index == 0 else b"ping=1", budget=ctx.budget)
    elif index == 2:
        fragments(ctx, session, [b"pi", b"ng"])
        session.wait("application-pong", budget=ctx.budget)
    elif index == 3:
        fragments(ctx, session, [b"p", b"i", b"n", b"g"])
        session.wait("application-pong", budget=ctx.budget)
    elif index == 4:
        fragments(ctx, session, [b"", b"ping", b"", b""])
        session.wait("application-pong", budget=ctx.budget)
    elif index == 5:
        note_raw(ctx, session, encode_frame(1, b"ping") + encode_frame(1, b"ping"))
        session.wait("application-pong", budget=ctx.budget)
        session.wait("application-pong", budget=ctx.budget)
        require(session.application_pongs == 2, "two-message-dispatch-count")
        session.assert_no_application_pong(0.08)
    elif index in (6, 17):
        parts = [b"x=\xe2", b"\x82", b"\xac"] if index == 6 else [b"x=\xf0", b"\x9f", b"\x98", b"\x80"]
        fragments(ctx, session, parts)
        session.wait("command-error", budget=ctx.budget)
        session.command(b"ping", budget=ctx.budget)
    elif index in (7, 8, 9, 18, 19):
        payload = {7: b"\xc0\xaf", 8: b"\xed\xa0\x80", 9: b"\xe2\x82",
                   18: b"\xf4\x90\x80\x80", 19: b"\x80"}[index]
        session.send(1, payload, budget=ctx.budget)
        ctx.error_close(session, 1007)
        return
    elif index == 10:
        finish_unknown(ctx, session, b"\0", "Invalid command")
        return
    elif index == 11:
        finish_unknown(ctx, session, b"", "Empty command")
        return
    elif index in (12, 20):
        payload = b"x" * 96 if index == 12 else b"x=" + b"\xe2\x82\xac" * 31 + b"x"
        require(len(payload) == 96, "client-boundary-vector", "client")
        finish_unknown(ctx, session, payload, "Unsupported command or invalid value")
        return
    elif index == 13:
        fragments(ctx, session, [b"x" * 48, b"y" * 48])
        session.wait("command-error", budget=ctx.budget)
        session.command(b"ping", budget=ctx.budget)
    elif index in (14, 21):
        payload = b"x" * 97 if index == 14 else b"x=" + b"\xe2\x82\xac" * 31 + b"xx"
        require(len(payload) == 97, "client-boundary-vector", "client")
        session.send(1, payload, budget=ctx.budget)
        ctx.error_close(session, 1009)
        return
    elif index == 15:
        fragments(ctx, session, [b"x" * 48, b"y" * 49])
        ctx.error_close(session, 1009)
        return
    elif index == 16:
        session.send(2, b"\xff", budget=ctx.budget)
        ctx.error_close(session, 1003)
        return
    else:
        raise NotExercised("data-vector-not-implemented")
    session.normal_close(ctx.budget)


def control_case(ctx):
    index, session = int(ctx.key[1:]), ctx.session()
    if index in (0, 1):
        body = b"" if index == 0 else b"\0\xff" + bytes(range(123))
        session.send(9, body, budget=ctx.budget)
        session.wait("pong", lambda got: got == body, ctx.budget)
    elif index == 2:
        session.send(1, b"pi", final=False, budget=ctx.budget)
        session.assert_no_application_pong(0.08)
        body = b"\0\xff"
        session.send(9, body, budget=ctx.budget)
        session.wait("pong", lambda got: got == body, ctx.budget)
        session.send(10, b"unsolicited", budget=ctx.budget)
        session.assert_no_application_pong(0.08)
        session.send(0, b"ng", budget=ctx.budget)
        session.wait("application-pong", budget=ctx.budget)
    elif index == 3:
        session.send(10, b"unsolicited", budget=ctx.budget)
        session.command(b"ping", budget=ctx.budget)
        ctx.notes.append(dict(unsolicited_pong_response_required=False))
    elif index == 4:
        session.send(9, b"", final=False, budget=ctx.budget)
        ctx.error_close(session, 1002)
        return
    elif index == 5:
        note_raw(ctx, session, encode_frame(9, declared_length=126))
        ctx.error_close(session, 1002)
        return
    else:
        raise NotExercised("control-vector-not-implemented")
    session.normal_close(ctx.budget)


def framing_case(ctx):
    index, session = int(ctx.key[1:]), ctx.session()
    if index == 0:
        wire = encode_frame(1, b"ping", mask=False)
    elif index == 1:
        wire = encode_frame(1, b"ping", rsv=1)
    elif index == 2:
        wire = encode_frame(3, b"x")
    elif index == 3:
        wire = encode_frame(11, b"")
    elif index == 4:
        wire = encode_frame(0, b"x")
    elif index in (5, 6):
        wire = encode_frame(1, b"p", final=False) + encode_frame(1 if index == 5 else 2, b"x")
    elif index == 7:
        wire = encode_frame(1, b"x", length_kind=16)
    elif index == 8:
        wire = encode_frame(1, declared_length=126, length_kind=64)
    elif index == 9:
        wire = encode_frame(1, declared_length=1 << 63, length_kind=64)
    elif index == 10:
        wire = encode_frame(1, declared_length=126)
    elif index == 11:
        wire = encode_frame(1, declared_length=65536)
    else:
        raise NotExercised("framing-vector-not-implemented")
    note_raw(ctx, session, wire)
    ctx.error_close(session, 1009 if index in (10, 11) else 1002)


def close_case(ctx):
    key, session = ctx.key, ctx.session()
    if key in ("K00", "K01", "K02"):
        body = b"" if key == "K00" else close_payload(1000, "done-€".encode()) if key == "K01" else close_payload(4000)
        session.send(8, body, budget=ctx.budget)
        outcome = session.expect_close(parse_close(body), payload=body, clean_tls=True, budget=ctx.budget)
        ctx.project_policy &= outcome["project_close_policy"]
        ctx.notes.append(outcome)
    elif key == "K03":
        session.send(8, b"x", budget=ctx.budget)
        ctx.error_close(session, 1002)
    elif key.startswith("K04"):
        code = {"K04a": 1004, "K04b": 1005, "K04c": 1006, "K04d": 1015}[key]
        session.send(8, close_payload(code), budget=ctx.budget)
        ctx.error_close(session, 1002)
    elif key == "K05":
        session.send(8, close_payload(1000, b"\xff"), budget=ctx.budget)
        ctx.error_close(session, 1007)
    elif key == "K06":
        body = close_payload()
        note_raw(ctx, session, encode_frame(8, body) + encode_frame(1, b"ping"))
        session.close_sent = True
        result = session.expect_close(1000, payload=body, clean_tls=True, budget=ctx.budget)
        ctx.project_policy &= result["project_close_policy"]
        require(session.application_pongs == 0, "post-close-command-dispatched")
    elif key == "K07":
        # Queue our Close without waiting for the server's size-policy Close.
        # Do not claim a particular ordering of host/guest processing.
        session.send(1, b"x" * 97, budget=ctx.budget)
        try:
            session.send(8, close_payload(), budget=ctx.budget)
        except OSError as error:
            raise NotExercised("client-close-not-queued-before-server-disconnect") from error
        outcome = session.expect_close((1000, 1009), allow_bare_eof=False, budget=ctx.budget)
        require(outcome["project_close_policy"], "concurrent-close-code-policy")
        ctx.notes.append(dict(client_close_queued_before_receiving_server_close=True,
                              observed_code=outcome["observed_code"], processing_order_proven=False))
    elif key == "K08":
        session.send(1, b"pi", final=False, budget=ctx.budget)
        session.assert_no_application_pong(0.08)
        body = close_payload()
        session.send(8, body, budget=ctx.budget)
        outcome = session.expect_close(1000, payload=body, clean_tls=True, budget=ctx.budget)
        ctx.project_policy &= outcome["project_close_policy"]
        require(not session.application_pongs, "partial-message-dispatched-on-close")
    elif key == "K09":
        session.close_transport()
        fresh = ctx.session()
        fresh.command(b"ping", budget=ctx.budget)
        fresh.normal_close(ctx.budget)
    else:
        raise NotExercised("close-vector-not-implemented")


def recovery_case(ctx):
    index = int(ctx.key[1:])
    if index == 0:
        for iteration in range(20):
            step = Budget(min(NORMAL_TIMEOUT, ctx.budget.remaining()))
            session = ctx.session(_budget=step)
            session.command(b"ping", budget=step)
            session.normal_close(step)
            session.close_transport()
            ctx.notes.append(dict(clean_cycle=iteration + 1))
    elif index == 1:
        old = ctx.session()
        old.send(1, b"\xc0\xaf", budget=ctx.budget)
        ctx.error_close(old, 1007)
        old.close_transport()
        fresh = ctx.session()
        fresh.command(b"getactive", "capabilities", ctx.budget)
        require(fresh.application_pongs == 0, "stale-pong-crossed-session")
        fresh.assert_no_application_pong(0.12)
        fresh.command(b"ping", budget=ctx.budget)
        require(fresh.application_pongs == 1, "fresh-command-count")
        fresh.normal_close(ctx.budget)
    elif index == 2:
        ctx.health.close()  # Do not consume secure HTTPD's third client slot.
        first, second = ctx.session(), ctx.session()
        first.command(b"ping", budget=ctx.budget)
        second.command(b"ping", budget=ctx.budget)
        try:
            third, status, _ = upgrade(ctx.endpoint, ctx.budget)
            ctx.sessions.append(third)
            require(status != 101, "third-websocket-client-admitted")
            ctx.notes.append(dict(third_http_status=status))
            third.close_transport()
        except (PeerEOF, ConnectionResetError, ssl.SSLError):
            ctx.notes.append(dict(third_connection_closed_before_upgrade=True))
        first.command(b"ping", budget=ctx.budget)
        second.command(b"ping", budget=ctx.budget)
        first.normal_close(ctx.budget)
        second.normal_close(ctx.budget)
    elif index == 3:
        complete = encode_frame(1, b"ping")
        for cut in (1, 4, len(complete) - 1):
            partial = ctx.session()
            note_raw(ctx, partial, complete[:cut])
            partial.close_transport()
            fresh = ctx.session()
            fresh.command(b"ping", budget=ctx.budget)
            fresh.normal_close(ctx.budget)
            fresh.close_transport()
    elif index == 4:
        session = ctx.session()
        for byte in encode_frame(1, b"ping"):
            session.send_raw(bytes((byte,)), ctx.budget)
            time.sleep(0.001)
        session.wait("application-pong", budget=ctx.budget)
        session.normal_close(ctx.budget)
    elif index == 5:
        fragment_expiry_case(ctx)
    elif index == 6:
        slow_reader_case(ctx)
    else:
        raise NotExercised("recovery-vector-not-implemented")


def fragment_expiry_case(ctx):
    session = ctx.session()
    session.send(1, b"p", final=False, budget=ctx.budget)
    session.send(9, b"assembly-started", budget=ctx.budget)
    session.wait("pong", lambda body: body == b"assembly-started", ctx.budget)
    initial = ctx.health.read()
    require(type(initial.get("uptime_ms")) is int, "guest-uptime-unavailable", "resource")
    last_ping, closed = time.monotonic(), False
    while ctx.budget.remaining():
        try:
            event, body = session.event(Budget(min(0.2, ctx.budget.remaining())))
            if event == "close":
                observed = parse_close(body)
                require(observed == 1008, "fragment-timeout-close-policy")
                closed = True
                break
            require(event not in ("application-pong", "command-error"), "unfinished-message-dispatched")
        except (socket.timeout, TimeoutError):
            pass
        except CheckFailure as error:
            if error.category != "host-deadline-expired":
                raise
        if time.monotonic() - last_ping > 0.35:
            session.send(9, b"keep-control", budget=ctx.budget)
            last_ping = time.monotonic()
        now = ctx.health.read()
        require(now["boot_id"] == initial["boot_id"], "guest-reset-during-fragment-policy", "resource")
        if now["uptime_ms"] - initial["uptime_ms"] > 6500:
            try:
                event, body = session.event(Budget(min(2, ctx.budget.remaining())))
                closed = event == "close" and parse_close(body) == 1008
            except PeerEOF:
                closed = False
            break
    require(closed, "fragment-message-budget-not-enforced")
    outcome = session.expect_close(1008, budget=ctx.budget)
    ctx.project_policy &= outcome["project_close_policy"]
    ctx.notes.append(dict(assembly_started_before_guest_ms=initial["uptime_ms"],
                          control_frames_do_not_reset_policy=True, observed_close_code=1008))


def slow_reader_case(ctx):
    ctx.health.close()
    slow, fast = ctx.session(), ctx.session()
    slow.wire.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2048)
    actual_receive = slow.wire.sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
    fast.command(b"ping", budget=ctx.budget)
    capabilities = fast.command(b"getactive", "capabilities", ctx.budget)
    # Bound the total provoked output using the actual fixed response schema.
    response_bytes = len(json.dumps(capabilities, separators=(",", ":")).encode())
    require(response_bytes <= 200, "capabilities-response-exceeds-burst-assumption", "client")
    before = ctx.health.read()
    # At most 512 responses of the fixed capabilities object (<=200 bytes each).
    # All outbound command bytes remain bounded, and no state mutation occurs.
    burst = b"".join(encode_frame(1, b"getactive") for _ in range(512))
    require(len(burst) < 16384, "client-slow-burst-bound", "client")
    slow.send_raw(burst, Budget(min(2, ctx.budget.remaining())))
    fast.command(b"getactive", "capabilities", ctx.budget)
    after = ctx.health.read()
    while after["uptime_ms"] - before["uptime_ms"] < 3000:
        time.sleep(0.1)
        after = ctx.health.read()
        ctx.budget.remaining()
    ended, drained = False, 0
    drain_budget = Budget(min(3, ctx.budget.remaining()))
    while drained < 128 * 1024:
        try:
            event, value = slow.event(drain_budget)
            drained = slow.wire.received_bytes
            if event == "close":
                # Close means CLOSING, not observed TCP termination. Complete
                # our half of the exchange, then keep the existing finite read
                # and byte bounds until EOF rather than closing it locally.
                if not slow.close_sent:
                    with contextlib.suppress(OSError, PeerEOF):
                        slow.send(8, value, budget=drain_budget)
        except PeerEOF:
            ended = True
            break
        except (socket.timeout, TimeoutError):
            break
        except CheckFailure as error:
            if error.category == "host-deadline-expired":
                break
            raise
    fast.command(b"ping", budget=ctx.budget)
    fast.normal_close(ctx.budget)
    ctx.notes.append(dict(actual_receive_buffer_bytes=actual_receive, commands=512,
                          input_bytes=len(burst), late_drain_bytes=drained,
                          slow_close_received=slow.close_seen, slow_tcp_eof_observed=ended,
                          slow_connection_terminated=ended, healthy_peer_progress=True,
                          backpressure_observed=False, guest_send_deadline_observed=False))
    if not ended:
        raise NotExercised("backpressure-or-slow-closure-not-observed")
    # EOF proves finite termination only. This client has no server send/queue
    # witness attributing it to pressure or to the guest's send deadline.
    raise NotExercised("slow-closure-observed-backpressure-not-proven")


def self_test(output):
    """Only pure data, scripted I/O and an owned local socket pair are used."""
    import os
    from unittest import mock
    output.mkdir(parents=True, exist_ok=False)
    results = []
    source_hash = digest(Path(__file__).read_bytes())

    def local_watchdog():
        (output / "watchdog.json").write_text(json.dumps(dict(state="NONPASS",
            category="local-self-test-watchdog", source_sha256=source_hash,
            guest_traffic=False, target_cases_exercised=0)) + "\n", encoding="utf-8")
        os._exit(1)
    watchdog = threading.Timer(30, local_watchdog)
    watchdog.daemon = True
    watchdog.start()

    def check(name, action):
        (output / "progress.json").write_text(json.dumps(dict(running=name, completed=results,
            source_sha256=source_hash, target_cases_exercised=0), indent=2) + "\n", encoding="utf-8")
        try:
            action()
            results.append(dict(id=name, state="PASS"))
        except BaseException as error:
            results.append(dict(id=name, state="FAIL", category=error_category(error)))

    def rejects(action, category):
        try:
            action()
        except CheckFailure as error:
            require(error.category == category, "self-test-wrong-rejection", "client")
        else:
            raise CheckFailure("self-test-missing-rejection", "client")

    class ScriptedSocket:
        def __init__(self, incoming=(), send_limit=None, advance=None):
            self.incoming, self.sent = collections.deque(incoming), bytearray()
            self.timeouts, self.send_limit, self.advance = [], send_limit, advance
        def settimeout(self, seconds):
            self.timeouts.append(seconds)
        def recv(self, maximum):
            if self.advance:
                self.advance()
            if not self.incoming:
                return b""
            item = self.incoming.popleft()
            if isinstance(item, BaseException):
                raise item
            self.incoming.appendleft(item[maximum:]) if len(item) > maximum else None
            return item[:maximum]
        def send(self, body):
            if self.advance:
                self.advance()
            count = len(body) if self.send_limit is None else min(len(body), self.send_limit)
            self.sent.extend(body[:count])
            return count
        def close(self):
            pass

    def read_frame(body, masked=False):
        return FrameReader(WireIO(ScriptedSocket([body])), expect_mask=masked).read(Budget(1))

    def known_mask_vector():
        expected = bytes.fromhex("818537fa213d7f9f4d5158")
        require(encode_frame(1, b"Hello", mask_key=bytes.fromhex("37fa213d")) == expected,
                "self-test-known-mask-vector", "client")
        require(read_frame(expected, True)["payload"] == b"Hello", "self-test-known-unmask", "client")
    check("known-RFC-Hello-mask-vector", known_mask_vector)
    for length in (0, 1, 96, 125, 126, 127, 5120):
        def roundtrip(length=length):
            body = bytes(index & 255 for index in range(length))
            for key in (b"\0" * 4, b"\xff\x80\x01\x7f"):
                require(read_frame(encode_frame(1, body, mask_key=key), True)["payload"] == body,
                        "self-test-mask-roundtrip", "client")
        check(f"mask-roundtrip-{length}", roundtrip)
    for size, expected in ((125, b"\x81\xfd"), (126, b"\x81\xfe\x00\x7e"),
                           (65535, b"\x81\xfe\xff\xff"),
                           (65536, b"\x81\xff\0\0\0\0\0\x01\0\0")):
        check(f"declared-length-boundary-{size}",
              lambda size=size, expected=expected: require(
                  encode_frame(1, declared_length=size, mask_key=b"\0" * 4).startswith(expected),
                  "self-test-length-header", "client"))
    malformed = [
        (b"\xc1\0", "server-unnegotiated-rsv"),
        (b"\x83\0", "server-reserved-opcode"),
        (b"\x8b\0", "server-reserved-opcode"),
        (b"\x81\x80" + b"\0" * 4, "server-mask-direction"),
        (b"\x81\x7e\0\x01x", "server-nonminimal-u16"),
        (b"\x81\x7f" + struct.pack("!Q", 126), "server-invalid-u64"),
        (b"\x81\x7f" + struct.pack("!Q", 1 << 63), "server-invalid-u64"),
        (b"\x09\0", "server-control-shape"),
        (b"\x89\x7e\0\x7e", "server-control-shape"),
        (b"\x81\x7e\x14\x01", "server-message-policy-bound"),
    ]
    for index, (wire, category) in enumerate(malformed):
        check(f"reject-frame-{index:02d}-{category}",
              lambda wire=wire, category=category: rejects(lambda: read_frame(wire), category))
    for code in (1000, 1001, 1002, 1003, 1007, 1014, 3000, 4000, 4999):
        check(f"valid-close-{code}", lambda code=code: require(
            parse_close(close_payload(code, "€".encode())) == code, "self-test-close-code", "client"))
    for code in (999, 1004, 1005, 1006, 1015, 2999, 5000):
        check(f"invalid-close-{code}", lambda code=code: rejects(
            lambda: parse_close(close_payload(code)), "server-forbidden-close-code"))
    check("empty-close-code-absent", lambda: require(parse_close(b"") is None, "self-test-empty-close", "client"))
    check("one-byte-close-rejected", lambda: rejects(lambda: parse_close(b"x"), "server-one-byte-close"))
    check("invalid-close-UTF8-rejected", lambda: rejects(
        lambda: parse_close(close_payload(1000, b"\xed\xa0\x80")), "server-invalid-close-utf8"))

    def timeout_resume():
        scripted = ScriptedSocket([b"\x81", socket.timeout(), b"\x04", b"pi", socket.timeout(), b"ng"])
        wire, reader = WireIO(scripted), None
        reader = FrameReader(wire)
        for expected in (b"\x81", b"\x81\x04pi"):
            try:
                reader.read(Budget(0.1))
            except socket.timeout:
                require(bytes(wire.buffer) == expected, "self-test-transactional-buffer", "client")
            else:
                raise CheckFailure("self-test-expected-read-timeout", "client")
        require(reader.read(Budget(0.1))["payload"] == b"ping" and not wire.buffer,
                "self-test-timeout-resume", "client")
    check("partial-header-and-payload-timeout-resume", timeout_resume)

    def absolute_read_budget():
        clock = [0.0]
        def advance():
            clock[0] += 0.4
        scripted = ScriptedSocket([b"a", b"b", b"c"], advance=advance)
        wire = WireIO(scripted)
        rejects(lambda: wire.exact(3, Budget(1, lambda: clock[0])), "host-deadline-expired")
        require(scripted.timeouts[0] > scripted.timeouts[1] > scripted.timeouts[2],
                "self-test-read-budget-reset", "client")
    check("absolute-deadline-across-partial-receives", absolute_read_budget)

    def absolute_send_budget():
        clock = [0.0]
        def advance():
            clock[0] += 0.4
        scripted = ScriptedSocket(send_limit=1, advance=advance)
        rejects(lambda: WireIO(scripted).send(b"abcd", Budget(1, lambda: clock[0])), "host-deadline-expired")
        require(bytes(scripted.sent) == b"abc", "self-test-partial-send-accounting", "client")
    check("absolute-deadline-across-partial-sends", absolute_send_budget)

    def http_overread():
        wire = WireIO(ScriptedSocket([b"HTTP/1.1 101 Switching Protocols\r\nX-Test: yes\r\n\r\n\x81\x02{}"] ))
        status, headers = wire.http_headers(Budget(1))
        require(status == 101 and headers["x-test"] == ["yes"] and bytes(wire.buffer) == b"\x81\x02{}",
                "self-test-http-overread", "client")
        require(FrameReader(wire).read(Budget(1))["payload"] == b"{}", "self-test-overread-frame", "client")
    check("HTTP-header-overread-retains-first-frame", http_overread)
    for raw, category in ((b"HTTP/1.1 xyz\r\n\r\n", "http-status-line"),
                          (b"HTTP/1.1 200 OK\r\n broken\r\n\r\n", "http-response-header")):
        check(f"reject-{category}", lambda raw=raw, category=category: rejects(lambda: parse_http_headers(raw), category))

    def session_for(*frames, secure=False):
        return Session(WireIO(ScriptedSocket([b"".join(frames)]), secure))

    def fragmented_controls():
        body = '{"pong":1}'.encode()
        session = session_for(encode_frame(1, body[:4], final=False, mask=False),
                              encode_frame(9, b"\0\xff", mask=False),
                              encode_frame(0, body[4:], mask=False))
        require(session.event(Budget(1)) == ("ping", b"\0\xff"), "self-test-interleaved-ping", "client")
        require(session.event(Budget(1))[0] == "application-pong", "self-test-final-dispatch", "client")
        reflected = read_frame(bytes(session.wire.sock.sent), True)
        require(reflected["opcode"] == 10 and reflected["payload"] == b"\0\xff",
                "self-test-masked-pong", "client")
    check("fragmented-server-message-interleaved-Ping", fragmented_controls)
    check("orphan-server-CONT-rejected", lambda: rejects(lambda: session_for(
        encode_frame(0, b"{}", mask=False)).event(Budget(1)), "server-unexpected-continuation"))
    check("nested-server-message-rejected", lambda: rejects(lambda: session_for(
        encode_frame(1, b"{", final=False, mask=False), encode_frame(1, b"{}", mask=False)).event(Budget(1)),
        "server-interleaved-data"))
    for payload in (b"\xc0\xaf", b"\xed\xa0\x80", b"\xe2\x82", b"\xf4\x90\x80\x80", b"\x80"):
        check("server-invalid-UTF8-" + payload.hex(), lambda payload=payload: rejects(lambda: session_for(
            encode_frame(1, payload, mask=False)).event(Budget(1)), "server-text-invalid-utf8"))

    def data_after_close():
        session = session_for(encode_frame(8, close_payload(), mask=False),
                              encode_frame(1, b'{"pong":1}', mask=False))
        require(session.event(Budget(1))[0] == "close", "self-test-initial-close", "client")
        rejects(lambda: session.event(Budget(1)), "server-data-after-close")
    check("data-after-server-Close-rejected", data_after_close)
    check("bare-error-EOF-preserves-project-nonpass", lambda: require(
        session_for().expect_close(1002, allow_bare_eof=True)["project_close_policy"] is False,
        "self-test-bare-EOF-policy", "client"))
    check("required-Close-missing-rejected", lambda: rejects(lambda: session_for().expect_close(1000),
                                                            "missing-required-close"))

    def TLS_shutdown(clean):
        incoming = [encode_frame(8, close_payload(), mask=False)]
        if not clean:
            incoming.append(ssl.SSLEOFError())
        session = Session(WireIO(ScriptedSocket(incoming), True))
        if clean:
            require(session.expect_close(1000, clean_tls=True)["project_close_policy"],
                    "self-test-clean-TLS-close", "client")
        else:
            rejects(lambda: session.expect_close(1000, clean_tls=True), "clean-close-missing-tls-alert")
    check("clean-TLS-alert-distinguished", lambda: TLS_shutdown(True))
    check("ragged-TLS-EOF-not-clean-close", lambda: TLS_shutdown(False))

    def no_premature_dispatch():
        session = Session(WireIO(ScriptedSocket([encode_frame(1, b'{"commandError":"bad"}', mask=False),
                                               socket.timeout()])))
        rejects(lambda: session.assert_no_application_pong(), "application-dispatched-before-fin")
    check("premature-command-error-is-not-silent", no_premature_dispatch)
    for url, category in (("ws://example.invalid/ws", "loopback-endpoint-required"),
                          ("ws://localhost/other", "endpoint-route"),
                          ("ws://u:p@localhost/ws", "endpoint-userinfo"),
                          ("http://localhost/ws", "endpoint-scheme")):
        check("reject-endpoint-" + category, lambda url=url, category=category: rejects(lambda: Endpoint(url), category))
    check("WSS-requires-explicit-CA", lambda: rejects(lambda: strict_context(None), "wss-ca-required"))

    def strict_TLS_options():
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        with mock.patch.object(ssl, "create_default_context", return_value=context) as factory:
            returned = strict_context(Path("public-test-ca-placeholder.pem"))
        require(returned.verify_mode == ssl.CERT_REQUIRED and returned.check_hostname and
                returned.minimum_version == returned.maximum_version == ssl.TLSVersion.TLSv1_2,
                "self-test-strict-TLS-options", "client")
        factory.assert_called_once_with(cafile="public-test-ca-placeholder.pem")
    check("strict-host-CA-name-date-policy-no-fixture-read", strict_TLS_options)

    def health_oracles():
        baseline = dict(boot_id="test", allocation_failures=0, decoder_sequence=0,
                        stream_sequence=0, output_failures=0, write_errors=0,
                        write_timeouts=0, short_writes=0, completion_queue_drops=0)
        require(health_verdict(baseline, dict(baseline)) == "PASS", "self-test-health-baseline", "client")
        for name in baseline:
            changed = dict(baseline)
            changed[name] = "changed" if name == "boot_id" else baseline[name] + 1
            require(health_verdict(baseline, changed) == "FAIL", "self-test-health-fault-not-detected", "client")
        incomplete = dict(baseline)
        del incomplete["write_timeouts"]
        require(health_verdict(incomplete, incomplete) == "NOT_EXERCISED" and
                health_verdict(baseline, None) == "NOT_EXERCISED", "self-test-missing-health-not-pass", "client")
    check("resource-fault-reset-missing-and-queue-drop-oracles", health_oracles)

    def provenance_filter():
        data = {key: "a" * size for key, size in (("source_commit", 40), ("sdk_commit", 40),
                ("app_sha256", 64), ("qemu_sha256", 64), ("sdkconfig_sha256", 64),
                ("fixture_sha256", 64), ("rom_manifest_sha256", 64), ("certificate_sha256", 64))}
        data.update(backend="pdm", unrecognized_private_note="do-not-copy-placeholder")
        path = output / "synthetic-binding.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        selected, fingerprint = load_binding(path)
        require(selected["state"] == "PASS" and fingerprint == "a" * 64 and
                "do-not-copy-placeholder" not in json.dumps(selected), "self-test-provenance-filter", "client")
        require(load_binding(None)[0]["state"] == "NOT_EXERCISED", "self-test-missing-binding-not-pass", "client")
    check("provenance-whitelist-and-missing-binding-not-pass", provenance_filter)

    def bootstrap_oracle():
        class Connection:
            def getpeercert(self):
                return dict(notBefore="synthetic-before", notAfter="synthetic-after")
            def close(self):
                pass
        class FakeEndpoint:
            secure = True
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            def __init__(self):
                self.calls = []
            def dial(self, budget, *, context=None, name=None):
                self.calls.append(dict(context=context, name=name))
                if context is not None:
                    require(context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname,
                            "self-test-bootstrap-weakened-verifier", "client")
                    error = ssl.SSLCertVerificationError(1, "synthetic verification failure")
                    error.verify_code = 62 if name is not None else 20
                    raise error
                return Connection(), dict(version="TLSv1.2")
        endpoint = FakeEndpoint()
        outcome = TLS_bootstrap(endpoint)
        require(outcome["state"] == "PASS" and len(endpoint.calls) == 3 and
                endpoint.calls[1]["name"] == "rfc-target.invalid" and
                all(item["HTTP_bytes_sent"] == 0 for item in outcome["negatives"]),
                "self-test-bootstrap-negative-oracle", "client")
    check("TLS-bootstrap-negative-oracle-scripted-no-network", bootstrap_oracle)

    def extra_application_response():
        session = session_for(encode_frame(1, b'{"pong":1}', mask=False),
                              encode_frame(8, close_payload(), mask=False))
        rejects(lambda: session.normal_close(Budget(1)), "extra-application-response-before-close")
    check("extra-command-response-during-Close-not-silent", extra_application_response)
    check("boolean-pong-not-integer-application-response", lambda: require(session_for(
        encode_frame(1, b'{"pong":true}', mask=False)).event(Budget(1))[0] == "other-json",
        "self-test-invalid-pong-oracle", "client"))
    check("invalid-JSON-not-application-success", lambda: rejects(lambda: session_for(
        encode_frame(1, b"not-json", mask=False)).event(Budget(1)), "server-text-invalid-json"))
    check("inconsistent-status-not-ignored", lambda: rejects(lambda: session_for(
        encode_frame(1, json.dumps(dict(status=dict(audio=False, generation=1, station="test", title="a", format="b"),
            payload=[dict(id="meta", value="wrong"), dict(id="fmt", value="b")])).encode(), mask=False)).event(Budget(1)),
        "server-status-consistency"))

    def local_socket_application():
        # Windows' socket.socketpair fallback can block forever in accept when
        # sandbox loopback routing is unavailable. Every setup step is bounded.
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client, server = None, None
        try:
            listener.settimeout(2)
            listener.bind(("127.0.0.1", 0))
            listener.listen(1)
            client = socket.create_connection(listener.getsockname(), timeout=2)
            server, peer = listener.accept()
            require(peer[0] == "127.0.0.1", "self-test-owned-loopback-peer", "client")
        except BaseException:
            if client is not None:
                client.close()
            if server is not None:
                server.close()
            raise
        finally:
            listener.close()
        failures, observations = [], []
        def responder():
            try:
                server.settimeout(2)
                data = bytearray()
                while b"\r\n\r\n" not in data:
                    part = server.recv(4096)
                    require(bool(part), "self-test-mock-request-EOF", "client")
                    data.extend(part)
                end = data.index(b"\r\n\r\n") + 4
                headers = dict(line.split(b":", 1) for line in bytes(data[:end - 4]).split(b"\r\n")[1:])
                accept = base64.b64encode(hashlib.sha1(headers[b"Sec-WebSocket-Key"].strip() + GUID).digest())
                mock_wire = WireIO(server)
                mock_wire.buffer.extend(data[end:])
                first = FrameReader(mock_wire, True).read(Budget(2))
                require(first["opcode"] == 1 and first["payload"] == b"ping", "self-test-real-masked-command", "client")
                status = dict(status=dict(audio=False, generation=1, station="test", title="", format="idle"),
                              payload=[dict(id="meta", value=""), dict(id="fmt", value="idle")])
                messages = [dict(current=1), dict(file="ready"), status, dict(pong=1)]
                response = b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Accept: " + accept + b"\r\n\r\n"
                server.sendall(response + b"".join(encode_frame(1, json.dumps(obj).encode(), mask=False) for obj in messages))
                close = FrameReader(mock_wire, True).read(Budget(2))
                require(close["opcode"] == 8 and parse_close(close["payload"]) == 1000,
                        "self-test-real-client-Close", "client")
                server.sendall(encode_frame(8, close["payload"], mask=False))
                server.shutdown(socket.SHUT_WR)
                observations.append("validated-masked-command-and-close")
            except BaseException as error:
                failures.append(error_category(error))
            finally:
                server.close()
        class PairEndpoint:
            authority, secure = "localhost:1", False
            def dial(self, budget):
                return client, None
        worker = threading.Thread(target=responder, daemon=True)
        worker.start()
        try:
            session, code, _ = upgrade(PairEndpoint(), Budget(3), first_frame=encode_frame(1, b"ping"))
            require(code == 101, "self-test-mock-upgrade", "client")
            session.wait("application-pong", budget=Budget(3))
            require([item["event"] for item in session.events] == ["current", "playlist-event", "status", "application-pong"],
                    "self-test-unsolicited-app-events", "client")
            session.normal_close(Budget(3))
        finally:
            client.close()
            worker.join(3)
        require(not worker.is_alive() and not failures and observations,
                "self-test-local-responder-nonpass", "client")
    check("owned-local-socket-upgrade-status-playlist-pong-close", local_socket_application)
    check("frozen-case-manifest-85", lambda: require(len(CASE_IDS) == len(set(CASE_IDS)) == 85 and
        collections.Counter(key[0] for key in CASE_IDS) == dict(H=25, D=22, C=6, F=12, K=13, R=7),
        "self-test-case-manifest", "client"))
    report = dict(schema=1, kind="CLIENT_LOCAL_SELF_TEST_ONLY", source_sha256=digest(Path(__file__).read_bytes()),
                  external_network=False, guest_traffic=False, compiled=False, target_cases_exercised=0,
                  results=results, state="PASS" if all(item["state"] == "PASS" for item in results) else "FAIL")
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (output / "cases.json").write_text(json.dumps([dict(id=key, title=CASE_TITLES[key]) for key in CASE_IDS], indent=2) + "\n", encoding="utf-8")
    watchdog.cancel()
    print(json.dumps(dict(state=report["state"], local_checks=len(results), target_cases_exercised=0)))
    if report["state"] != "PASS":
        raise SystemExit(1)


def load_binding(path):
    """Accept only nonpersonal provenance fields; never copy arbitrary metadata."""
    if path is None:
        return dict(state="NOT_EXERCISED", category="fixture-binding-not-supplied"), None
    raw = path.read_bytes()
    require(len(raw) <= MAX_HTTP, "binding-size", "setup")
    obj = json.loads(raw)
    require(isinstance(obj, dict), "binding-object", "setup")
    selected = {}
    for name, width in (("source_commit", 40), ("sdk_commit", 40), ("app_sha256", 64),
                        ("qemu_sha256", 64), ("sdkconfig_sha256", 64), ("fixture_sha256", 64),
                        ("rom_manifest_sha256", 64), ("certificate_sha256", 64)):
        value = obj.get(name)
        if value is not None:
            require(isinstance(value, str) and re.fullmatch("[a-f0-9]{" + str(width) + "}", value),
                    "binding-hash-field", "setup")
            selected[name] = value
    if "backend" in obj:
        require(obj["backend"] in ("legacy", "pdm", "continuous"), "binding-backend", "setup")
        selected["backend"] = obj["backend"]
    required = {"source_commit", "sdk_commit", "app_sha256", "qemu_sha256", "sdkconfig_sha256",
                "fixture_sha256", "rom_manifest_sha256", "backend"}
    missing = sorted(required - selected.keys())
    selected.update(state="PASS" if not missing else "NOT_EXERCISED", missing=missing,
                    input_metadata_sha256=digest(raw),
                    evidence_limit="caller-supplied hashes; client does not prove guest-image loading")
    return selected, selected.get("certificate_sha256")


def TLS_bootstrap(endpoint):
    if not endpoint.secure:
        return dict(state="NOT_APPLICABLE", transport="ws")
    results = []
    untrusted = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    untrusted.minimum_version = untrusted.maximum_version = ssl.TLSVersion.TLSv1_2
    for key, context, name in (("untrusted-CA", untrusted, None),
                               ("wrong-verification-name", endpoint.context, "rfc-target.invalid")):
        try:
            connection, _ = endpoint.dial(Budget(NORMAL_TIMEOUT), context=context, name=name)
        except ssl.SSLCertVerificationError as error:
            results.append(dict(id=key, state="PASS", HTTP_bytes_sent=0,
                                verification_error_code=error.verify_code))
        else:
            connection.close()
            raise CheckFailure("TLS-negative-verifier-accepted", "transport")
    connection, metadata = endpoint.dial(Budget(NORMAL_TIMEOUT))
    try:
        certificate = connection.getpeercert()
        metadata.update(not_before=certificate.get("notBefore"), not_after=certificate.get("notAfter"))
    finally:
        connection.close()
    require(bool(metadata.get("not_before")) and bool(metadata.get("not_after")),
            "verified-certificate-validity-unavailable", "transport")
    return dict(state="PASS", negatives=results, correct_verifier=metadata,
                evidence_limit="no firmware-side date-policy inference from host verification")


def case_requirements(key):
    if key.startswith("H"):
        return dict(rfc=["4.1", "4.2.1", "4.2.2", "9.1"],
                    project=["HTTP rejection/status and declined negotiation"],
                    resource=["stable boot, slot recovery, unchanged fault counters"])
    if key.startswith("D"):
        return dict(rfc=["5.2", "5.4", "5.6", "7.1.7", "8.1"],
                    project=["real command dispatch", "96-byte logical command bound", "binary unsupported"],
                    resource=["stable boot, unchanged fault counters"])
    if key.startswith("C"):
        return dict(rfc=["5.4", "5.5.2", "5.5.3"], project=["interleaved command state"],
                    resource=["stable boot, unchanged fault counters"])
    if key.startswith("F"):
        return dict(rfc=["5.2", "5.3", "5.4", "7.1.7"],
                    project=["expected error Close code", "96-byte receive policy for canonical large lengths"],
                    resource=["stable boot, unchanged fault counters"])
    if key.startswith("K"):
        return dict(rfc=["5.5.1", "7.1", "7.4", "8.1"],
                    project=["full Close payload policy", "clean WSS close-notify for valid Close"],
                    resource=["session release and recovery, unchanged fault counters"])
    return dict(rfc=["5.4", "5.5", "7.1"],
                project=["two WS clients", "frame/message/send deadlines", "session isolation"],
                resource=["stable boot, finite cleanup, healthy peer progress, unchanged fault counters"])


def execute(args):
    output = args.output.resolve()
    binding, certificate_hash = load_binding(args.binding)
    endpoint = Endpoint(args.endpoint, args.ca, certificate_hash)
    output.mkdir(parents=True, exist_ok=False)
    selected = list(dict.fromkeys(args.case or CASE_IDS))
    report = dict(schema=1, kind="ACTUAL_APPLICATION_TARGET_WS_CONFORMANCE", state="INCOMPLETE",
                  client_sha256=digest(Path(__file__).read_bytes()),
                  design_sha256=digest((PRIVATE_ROOT / "rfc-target-design.md").read_bytes()),
                  host_UTC=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                  python_version=list(sys.version_info[:3]), transport="wss" if endpoint.secure else "ws",
                  endpoint=dict(host=endpoint.host, port=endpoint.port, route="/ws"),
                  binding=binding, selected_cases=selected, frozen_case_count=85,
                  full_manifest_selected=set(selected) == set(CASE_IDS), cases=[],
                  case_manifest=[dict(id=key, title=CASE_TITLES[key], state="NOT_EXERCISED",
                                      category="pending" if key in selected else "outside-selected-scope")
                                 for key in CASE_IDS],
                  whole_service_stop=dict(state="NOT_EXERCISED", category="no-public-service-stop-contract"),
                  limits=dict(application_command_bytes=96, receive_message_bytes=MAX_MESSAGE,
                              host_mode_watchdog_seconds=1200, evidence_frame_cap=MAX_FRAME_EVENTS,
                              evidence_event_cap=MAX_EVENTS),
                  evidence_limits=["session lifecycle only; no whole-service Stop/join proof",
                                   "caller supplies immutable image/QEMU/source bindings",
                                   "idle profile only; concurrent audio/resource campaign separate",
                                   "no physical Wi-Fi/audio or C3 target execution proof"],
                  bootstrap=dict(state="NOT_EXERCISED"))
    health = Health(endpoint)
    watchdog = threading.Timer(1200, endpoint.abort_owned)
    watchdog.daemon = True
    start = time.monotonic()
    watchdog.start()

    def save():
        report["elapsed_seconds"] = round(time.monotonic() - start, 3)
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    try:
        save()
        report["bootstrap"] = TLS_bootstrap(endpoint)
        status = health.read("/api/native/status")
        require(status.get("audio") is False, "idle-radio-profile-required", "setup")
        initial = health_summary(health.read())
        report["initial_health"] = initial
        save()
        for key in selected:
            ctx = CaseContext(endpoint, health, key)
            case_start = time.monotonic()
            item = dict(id=key, title=CASE_TITLES[key], requirements=case_requirements(key),
                        raw_outcome="NOT_EXERCISED", rfc="NOT_EVALUATED", project="NOT_EVALUATED",
                        resource="NOT_EXERCISED")
            before, after, fatal = None, None, False
            try:
                require(not endpoint.aborted, "mode-watchdog-expired", "transport")
                before = health_summary(health.read())
                require(before["boot_id"] == initial["boot_id"], "guest-identity-changed", "resource")
                run_case(ctx)
                item.update(raw_outcome="COMPLETED", rfc="PASS",
                            project="PASS" if ctx.project_policy else "FAIL")
            except NotExercised as error:
                item.update(raw_outcome="NOT_EXERCISED", category=str(error))
            except CheckFailure as error:
                item.update(raw_outcome="FAIL", category=error.category, failure_scope=error.scope)
                if error.scope in ("rfc", "project", "resource"):
                    item[error.scope] = "FAIL"
                if error.scope in ("client", "setup", "transport"):
                    fatal = True
            except BaseException as error:
                item.update(raw_outcome="FAIL", category=error_category(error), failure_scope="transport")
                fatal = True
            finally:
                ctx.cleanup()
                try:
                    after = health_summary(health.read())
                    if after["boot_id"] != initial["boot_id"]:
                        fatal = True
                except BaseException as error:
                    item["post_cleanup_health_category"] = error_category(error)
                    fatal = True
                if item["resource"] != "FAIL":
                    item["resource"] = health_verdict(before, after)
                item.update(before_health=before, after_health=after, notes=ctx.notes,
                            sessions=[session.summary() for session in ctx.sessions],
                            elapsed_seconds=round(time.monotonic() - case_start, 3))
                item["state"] = "PASS" if all(item[field] == "PASS" for field in ("rfc", "project", "resource")) else (
                    "FAIL" if "FAIL" in [item[field] for field in ("rfc", "project", "resource")] or item["raw_outcome"] == "FAIL"
                    else "INCOMPLETE")
                report["cases"].append(item)
                entry = next(entry for entry in report["case_manifest"] if entry["id"] == key)
                entry.update(state=item["state"], category=item.get("category", "completed"),
                             evidence_file=key + ".json")
                (output / (key + ".json")).write_text(json.dumps(item, indent=2) + "\n", encoding="utf-8")
                save()
            if fatal:
                report["stop_category"] = "identity-watchdog-or-irrecoverable-transport-cleanup"
                break
        report["final_post_close_health"] = health_summary(health.read())
        report["final_resource"] = health_verdict(initial, report["final_post_close_health"])
        all_pass = len(report["cases"]) == len(selected) and all(item["state"] == "PASS" for item in report["cases"])
        report["selected_scope_state"] = "PASS" if all_pass and report["final_resource"] == "PASS" else (
            "FAIL" if any(item["state"] == "FAIL" for item in report["cases"]) or report["final_resource"] == "FAIL" else "INCOMPLETE")
        report["complete_matrix"] = (report["full_manifest_selected"] and report["selected_scope_state"] == "PASS" and
            binding["state"] == "PASS" and (not endpoint.secure or (
                report["bootstrap"]["state"] == "PASS" and certificate_hash is not None)))
        report["state"] = "PASS" if report["complete_matrix"] else report["selected_scope_state"]
        if not report["complete_matrix"] and report["state"] == "PASS":
            report["state"] = "INCOMPLETE"
    except BaseException as error:
        report.update(state="FAIL", terminal_category=error_category(error))
    finally:
        health.close()
        watchdog.cancel()
        endpoint.abort_owned()
        for entry in report["case_manifest"]:
            if entry["category"] == "pending":
                entry["category"] = "not-reached-before-run-ended"
        save()
    print(json.dumps(dict(state=report["state"], selected_scope_state=report.get("selected_scope_state"),
                          complete_matrix=report.get("complete_matrix", False), cases_exercised=len(report["cases"]))))
    if report["state"] != "PASS":
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--list-cases", action="store_true")
    action.add_argument("--self-test", action="store_true")
    action.add_argument("--execute", action="store_true")
    parser.add_argument("--endpoint")
    parser.add_argument("--ca", type=Path)
    parser.add_argument("--binding", type=Path)
    parser.add_argument("--case", action="append", choices=CASE_IDS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.list_cases:
        print(json.dumps(dict(cases=[dict(id=key, title=CASE_TITLES[key]) for key in CASE_IDS]), indent=2))
        return
    require(args.output is not None, "new-output-required", "setup")
    output = args.output.resolve()
    require(output.is_relative_to(PRIVATE_ROOT.resolve()) and not output.exists(), "new-private-output-required", "setup")
    if args.self_test:
        require(args.endpoint is None, "self-test-has-no-endpoint", "setup")
        self_test(output)
    else:
        require(args.endpoint is not None, "explicit-endpoint-required", "setup")
        execute(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(json.dumps(dict(state="TERMINAL_NONPASS", category=error_category(error))))
        raise SystemExit(1)
