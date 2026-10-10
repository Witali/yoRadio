"""Board-independent HTTP(S) fixture server; no device control or flashing."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import socket
import ssl
import threading
import time
from time import perf_counter
from urllib.parse import urlsplit


class DeliveryStats:
    """Completed host socket writes, not TCP acknowledgements or board input."""
    MAX_WINDOWS = 4096

    def __init__(self, started, event):
        self.result = event['delivery'] = dict(clock='time.perf_counter', started_at=started, finished=False,
                                               windows=[], dropped_windows=0)
        self.started = started
        self.bytes = self.writes = 0
        self.write_seconds = self.max_write_seconds = self.max_late_seconds = 0

    def write(self, size, started, ended, planned=None):
        self.bytes += size
        self.writes += 1
        elapsed = ended-started
        self.write_seconds += elapsed
        self.max_write_seconds = max(self.max_write_seconds, elapsed)
        if planned is not None:
            self.max_late_seconds = max(self.max_late_seconds, started-planned)
        if ended-self.started >= 1:
            self.flush(ended)

    def flush(self, ended):
        if not self.writes:
            return
        row = dict(started_at=self.started, ended_at=ended, bytes=self.bytes,
                   writes=self.writes, write_seconds=self.write_seconds,
                   max_write_seconds=self.max_write_seconds,
                   max_late_seconds=self.max_late_seconds)
        if len(self.result['windows']) < self.MAX_WINDOWS:
            self.result['windows'].append(row)
        else:
            self.result['dropped_windows'] += 1
        self.started = ended
        self.bytes = self.writes = 0
        self.write_seconds = self.max_write_seconds = self.max_late_seconds = 0

    def finish(self, ended):
        self.flush(ended)
        self.result.update(ended_at=ended, finished=True)


class DeliveryPauses:
    """Pause before exact encoded-byte positions; never shift pacing deadlines."""
    MAX_PAUSES = 64
    MAX_SECONDS = 2.0

    @classmethod
    def validate(cls, schedule):
        if not isinstance(schedule, (tuple, list)) or len(schedule) > cls.MAX_PAUSES:
            raise ValueError('delivery_pauses must contain at most 64 byte-offset/duration pairs')
        result, previous = [], -1
        for pair in schedule:
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise ValueError('Each delivery pause needs a byte offset and duration')
            offset, seconds = pair
            if type(offset) is not int or not previous < offset < 2**63:
                raise ValueError('Delivery pause byte offsets must be increasing nonnegative integers')
            if (type(seconds) not in (int, float) or not math.isfinite(seconds) or
                    not 0 < seconds <= cls.MAX_SECONDS):
                raise ValueError('Delivery pause durations must be finite and within (0, 2] seconds')
            result.append((offset, float(seconds)))
            previous = offset
        return tuple(result)

    def __init__(self, schedule, closed, event):
        self.schedule, self.closed = schedule, closed
        self.index = 0
        self.rows = event['pauses'] = []
        event['pause_schedule'] = [dict(after_bytes=n, seconds=s) for n, s in schedule]

    def next_size(self, sent, wanted):
        if self.index == len(self.schedule):
            return wanted
        offset, seconds = self.schedule[self.index]
        if sent > offset:
            raise ValueError('Delivery skipped a scheduled byte boundary')
        if sent == offset:
            row = dict(after_bytes=sent, requested_seconds=seconds,
                       started_at=time.perf_counter(), completed=False)
            self.rows.append(row)
            started = perf_counter()
            interrupted = self.closed.wait(seconds)
            row.update(ended_at=time.perf_counter(), elapsed_seconds=perf_counter()-started,
                       completed=not interrupted)
            self.index += 1
            if interrupted:
                return 0
        if self.index < len(self.schedule):
            wanted = min(wanted, self.schedule[self.index][0]-sent)
        return wanted


def pause_argument(value):
    try:
        offset, seconds = value.split(':')
        return DeliveryPauses.validate([(int(offset), float(seconds))])[0]
    except (ValueError, TypeError):
        raise argparse.ArgumentTypeError('Use BYTE_OFFSET:SECONDS, with a nonnegative offset and 0 < seconds <= 2')


class Server:
    def __init__(self, host, port, fixtures, cert=None, key=None, *, unpaced_files=False,
                 delivery_stats=False, initial_failures=0, pacing_ratio=1.02,
                 delivery_pauses=(), send_buffer_bytes=None):
        if type(initial_failures) is not int or initial_failures < 0:
            raise ValueError('initial_failures must be a nonnegative integer')
        if (type(pacing_ratio) not in (int, float) or
                not math.isfinite(pacing_ratio) or pacing_ratio <= 0):
            raise ValueError('pacing_ratio must be finite and positive')
        delivery_pauses = DeliveryPauses.validate(delivery_pauses)
        if send_buffer_bytes is not None and (type(send_buffer_bytes) is not int or
                                             not 1024 <= send_buffer_bytes <= 1048576):
            raise ValueError('send_buffer_bytes must be an integer within [1024, 1048576]')
        self.fixtures = fixtures
        self.events = []
        self.closed = threading.Event()
        self.recovery_attempts = {}
        self.recovery_lock = threading.Lock()
        outer = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'

            def log_message(self, *_):
                pass

            def do_GET(self):
                if self.path == '/manifest.json':
                    payload = json.dumps({n:{k:v for k,v in s.items() if k not in ('data','segments')}
                                          for n,s in outer.fixtures.items()}).encode()
                    self.send_response(200)
                    self.send_header('Content-Type','application/json')
                    self.send_header('Content-Length',str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                    return
                parts = urlsplit(self.path).path.strip('/').split('/')
                if len(parts) != 2 or parts[1] not in outer.fixtures:
                    self.send_error(404)
                    return
                mode, name = parts
                if mode not in ('file','stream','drop','stall','jitter','redirect','error','recover'):
                    self.send_error(404)
                    return
                recovery = None
                if mode == 'recover':
                    with outer.recovery_lock:
                        attempt = outer.recovery_attempts.get(name, 0) + 1
                        outer.recovery_attempts[name] = attempt
                    status = 503 if attempt <= initial_failures else 200
                    recovery = dict(mode='recover', fixture=name, attempt=attempt,
                                    response_status=status, clock='time.perf_counter',
                                    requested_at=time.perf_counter())
                    if status == 503:
                        outer.events.append(recovery)
                        self.send_response(status)
                        self.send_header('Content-Length', '0')
                        self.send_header('Connection', 'close')
                        self.end_headers()
                        self.close_connection = True
                        return
                    mode = 'file'
                if mode == 'error':
                    self.send_error(503)
                    return
                if mode == 'redirect':
                    self.send_response(302)
                    self.send_header('Location', '/file/' + name)
                    self.send_header('Content-Length', '0')
                    self.end_headers()
                    return
                spec = outer.fixtures[name]
                # Only AAC is repeated indefinitely: FLAC and Ogg concatenation
                # would test another container feature, not continuous playback.
                if mode == 'stream' and spec['codec'] != 'aac':
                    self.send_error(400)
                    return
                actual_send_buffer = None
                if send_buffer_bytes is not None:
                    self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, send_buffer_bytes)
                    actual_send_buffer = self.connection.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
                data = spec['data']
                self.send_response(200)
                self.send_header('Content-Type', spec['mime'])
                if mode != 'stream':
                    self.send_header('Content-Length', str(len(data)))
                self.send_header('Connection', 'close')
                self.end_headers()
                unpaced = unpaced_files and mode == 'file'
                event = dict(mode=mode, fixture=name, sent=0, complete=False,
                             pacing_ratio=None if unpaced else pacing_ratio,
                             clock='time.perf_counter')
                if send_buffer_bytes is not None:
                    event.update(send_buffer_requested=send_buffer_bytes,
                                 send_buffer_actual=actual_send_buffer)
                pauses = DeliveryPauses(delivery_pauses, outer.closed, event) if delivery_pauses else None
                if isinstance(self.connection, ssl.SSLSocket):
                    # Record negotiated algorithms, never certificates/keys.
                    event['tls_version'] = self.connection.version()
                    event['tls_cipher'] = self.connection.cipher()[0]
                if recovery:
                    event.update(recovery)
                outer.events.append(event)
                started = time.perf_counter()
                deadline = started
                delivery = DeliveryStats(started, event) if delivery_stats else None
                try:
                    while not outer.closed.is_set() and time.perf_counter() - started < 86400:
                        for segment in spec.get('segments', [spec]):
                            payload = segment['data']
                            bps = len(payload) / segment['seconds'] * pacing_ratio
                            offset = 0
                            while offset < len(payload):
                                if outer.closed.is_set():
                                    return
                                if mode in ('drop','stall') and time.perf_counter()-started >= 3:
                                    if mode == 'stall':
                                        outer.closed.wait(15)
                                    return
                                size = min(1024, len(payload)-offset)
                                if pauses:
                                    size = pauses.next_size(event['sent'], size)
                                    if not size:
                                        return
                                chunk = payload[offset:offset+size]
                                write_started = time.perf_counter() if delivery else 0
                                self.wfile.write(chunk)
                                self.wfile.flush()
                                event['sent'] += len(chunk)
                                if delivery:
                                    delivery.write(len(chunk), write_started, time.perf_counter(),
                                                   None if unpaced else deadline)
                                deadline += len(chunk) / bps
                                if mode == 'jitter' and offset % 8192 == 0:
                                    deadline += .035
                                offset += len(chunk)
                                if not unpaced and outer.closed.wait(max(0, deadline - time.perf_counter())):
                                    return
                        if mode != 'stream':
                            event['complete'] = True
                            return
                except (BrokenPipeError, ConnectionError, TimeoutError, OSError):
                    pass
                finally:
                    self.close_connection = True
                    event['seconds'] = time.perf_counter() - started
                    if delivery:
                        delivery.finish(time.perf_counter())

        class TrackingServer(ThreadingHTTPServer):
            def get_request(self):
                try:
                    return super().get_request()
                except ssl.SSLError as error:
                    outer.events.append(dict(mode='tls-handshake-failure', reason=error.reason))
                    raise

        self.http = TrackingServer((host, port), Handler)
        self.http.daemon_threads = True
        if cert:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert, key)
            self.http.socket = context.wrap_socket(self.http.socket, server_side=True)

    def __enter__(self):
        threading.Thread(target=self.http.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *_):
        self.closed.set()
        self.http.shutdown()
        self.http.server_close()


def main():
    from fixtures import load_fixtures
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8770)
    parser.add_argument('--cert', help='PEM certificate for HTTPS')
    parser.add_argument('--key', help='PEM private key; never stored in results')
    parser.add_argument('--fixture-manifest', help='Additional generated fixture manifest')
    parser.add_argument('--unpaced-files', action='store_true',
                        help='Serve /file at the speed allowed by TCP; retain pacing for live/fault routes')
    parser.add_argument('--delivery-stats', action='store_true',
                        help='Record bounded host socket-write timing and pacing lag')
    parser.add_argument('--pacing-ratio', type=float, default=1.02,
                        help='Paced audio rate relative to fixture duration (default 1.02; 1 is real time)')
    parser.add_argument('--initial-failures', type=int, default=0,
                        help='On /recover/FIXTURE, return 503 for this many requests, then serve the file')
    parser.add_argument('--delivery-pause', type=pause_argument, action='append', default=[],
                        help='Pause before BYTE_OFFSET:SECONDS; repeat in increasing byte order, up to 64 times')
    parser.add_argument('--send-buffer-bytes', type=int,
                        help='Optional SO_SNDBUF request (1024..1048576); actual OS value is recorded')
    parser.add_argument('--events-output', type=Path,
                        help='Save fixture server events when this process exits normally')
    args = parser.parse_args()
    specs = load_fixtures(args.fixture_manifest)
    if bool(args.cert) != bool(args.key):
        parser.error('--cert and --key must be supplied together')
    with Server(args.host,args.port,specs,args.cert,args.key, unpaced_files=args.unpaced_files,
                delivery_stats=args.delivery_stats, initial_failures=args.initial_failures,
                pacing_ratio=args.pacing_ratio, delivery_pauses=args.delivery_pause,
                send_buffer_bytes=args.send_buffer_bytes) as server:
        print(f"Serving {len(specs)} fixtures on port {args.port}; /manifest.json lists them", flush=True)
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
    if args.events_output:
        args.events_output.parent.mkdir(parents=True, exist_ok=True)
        args.events_output.write_text(json.dumps(server.events, indent=2)+'\n')


if __name__ == '__main__':
    main()
