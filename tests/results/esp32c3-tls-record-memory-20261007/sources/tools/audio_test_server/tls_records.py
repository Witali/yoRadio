"""Board-independent AAC server with measured TLS 1.2 application-record sizes.

Only record types/lengths and completed socket-write counts are retained.
No plaintext requests, ciphertext, TLS secrets or private keys enter reports.
"""
import socketserver
import ssl
import threading
import time
from urllib.parse import urlsplit

MAX_RECORD_PLAINTEXT = 16384
SMALL_RECORD_PLAINTEXT = 1024


class Channel:
    def __init__(self, sock, context, event):
        self.sock, self.event = sock, event
        self.incoming, self.outgoing = ssl.MemoryBIO(), ssl.MemoryBIO()
        self.tls = context.wrap_bio(self.incoming, self.outgoing, server_side=True)
        self.pending = bytearray()
        self.phase = 'handshake'

    def drain(self):
        data = self.outgoing.read()
        if not data:
            return
        self.pending.extend(data)
        while len(self.pending) >= 5:
            length = int.from_bytes(self.pending[3:5], 'big')
            if len(self.pending) < length + 5:
                break
            if len(self.event['records']) < 4096:
                self.event['records'].append(dict(phase=self.phase, type=self.pending[0],
                    wire_payload_bytes=length, at=time.monotonic()))
            else:
                self.event['dropped_records'] += 1
            del self.pending[:length + 5]
        self.sock.sendall(data)
        self.event['completed_socket_bytes'] += len(data)

    def incoming_data(self):
        data = self.sock.recv(32768)
        if not data:
            raise EOFError('TLS peer closed')
        self.incoming.write(data)

    def operation(self, function):
        while True:
            try:
                result = function()
                self.drain()
                return result
            except ssl.SSLWantReadError:
                self.drain()
                self.incoming_data()
            except ssl.SSLWantWriteError:
                self.drain()

    def handshake(self):
        self.operation(self.tls.do_handshake)
        self.event.update(version=self.tls.version(), cipher=self.tls.cipher()[0])

    def request(self):
        data = bytearray()
        while b'\r\n\r\n' not in data:
            chunk = self.operation(lambda: self.tls.read(1024))
            if not chunk:
                raise EOFError('TLS request ended before headers')
            data.extend(chunk)
            if len(data) > 8192:
                raise ValueError('Request too large')
        parts = bytes(data).split(b'\r\n', 1)[0].split()
        if len(parts) != 3 or parts[0] != b'GET':
            raise ValueError('Expected GET request')
        return parts[1].decode('ascii')

    def write(self, payload, phase):
        self.phase = phase
        written = self.operation(lambda: self.tls.write(payload))
        if written != len(payload):
            raise ValueError('TLS write was partial')
        if len(self.event['writes']) < 4096:
            self.event['writes'].append(dict(phase=phase, plaintext_bytes=written, at=time.monotonic()))
        else:
            self.event['dropped_writes'] += 1


class RecordServer:
    def __init__(self, host, port, fixtures, cert, key, *, seconds=90, grow_seconds=30):
        if not 0 <= grow_seconds <= seconds or not 0 < seconds <= 600:
            raise ValueError('Invalid bounded test duration')
        self.closed = threading.Event()
        self.events = []
        outer = self
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = context.maximum_version = ssl.TLSVersion.TLSv1_2
        # This yields 24 bytes of explicit nonce/tag overhead per record, so
        # measured encrypted lengths prove the selected plaintext record size.
        context.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256')
        context.load_cert_chain(cert, key)

        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                event = dict(records=[], writes=[], dropped_records=0, dropped_writes=0,
                             completed_socket_bytes=0, audio_bytes=0, complete=False)
                outer.events.append(event)
                self.request.settimeout(10)
                channel = Channel(self.request, context, event)
                try:
                    channel.handshake()
                    parts = urlsplit(channel.request()).path.strip('/').split('/')
                    if len(parts) != 2 or parts[0] not in ('small', 'large', 'grow', 'alternate') or parts[1] not in fixtures:
                        channel.write(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n', 'headers')
                        return
                    mode, name = parts
                    spec = fixtures[name]
                    if spec['codec'] != 'aac' or not spec['data'] or spec['seconds'] <= 0:
                        raise ValueError('Repeated record fixture requires ADTS AAC')
                    event.update(mode=mode, fixture=name, fixture_sha256=spec['sha256'])
                    headers = ('HTTP/1.1 200 OK\r\nContent-Type: audio/aac\r\nConnection: close\r\n\r\n').encode()
                    channel.write(headers, 'headers')
                    started = time.monotonic()
                    event['started_at'] = started
                    data, offset, index = spec['data'], 0, 0
                    bps = len(data) / spec['seconds'] * 1.02
                    while not outer.closed.is_set() and time.monotonic() - started < seconds:
                        large = mode == 'large' or mode == 'grow' and time.monotonic() - started >= grow_seconds or mode == 'alternate' and index % 2
                        count = MAX_RECORD_PLAINTEXT if large else SMALL_RECORD_PLAINTEXT
                        payload = bytearray()
                        while len(payload) < count:
                            take = min(count - len(payload), len(data) - offset)
                            payload.extend(data[offset:offset + take])
                            offset = (offset + take) % len(data)
                        channel.write(payload, 'body-large' if large else 'body-small')
                        event['audio_bytes'] += count
                        index += 1
                        if outer.closed.wait(max(0, started + event['audio_bytes'] / bps - time.monotonic())):
                            return
                    event['complete'] = True
                except ssl.SSLError as error:
                    event['error'] = type(error).__name__
                    event['tls_reason'] = error.reason
                except (OSError, EOFError, ValueError) as error:
                    event['error'] = type(error).__name__
                finally:
                    event['ended_at'] = time.monotonic()

        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
            daemon_threads = True

        self.server = Server((host, port), Handler)

    def __enter__(self):
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.closed.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)


def main():
    import argparse
    import json
    from pathlib import Path
    try:
        from .fixtures import load_fixtures
    except ImportError:
        from fixtures import load_fixtures
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8772)
    parser.add_argument('--cert', type=Path, required=True)
    parser.add_argument('--key', type=Path, required=True)
    parser.add_argument('--fixture-manifest')
    parser.add_argument('--seconds', type=float, default=90)
    parser.add_argument('--grow-seconds', type=float, default=30)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Use a new report path')
    with RecordServer(args.host, args.port, load_fixtures(args.fixture_manifest),
                      args.cert, args.key, seconds=args.seconds, grow_seconds=args.grow_seconds) as server:
        print('Serving /small/NAME, /large/NAME, /grow/NAME and /alternate/NAME; Ctrl+C saves numeric record evidence.', flush=True)
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(server.events, indent=2)+'\n')


if __name__ == '__main__':
    main()
