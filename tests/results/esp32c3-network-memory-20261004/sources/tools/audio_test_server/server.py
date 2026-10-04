"""Board-independent HTTP(S) fixture server; no device control or flashing."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import ssl
import threading
import time
from urllib.parse import urlsplit


class Server:
    def __init__(self, host, port, fixtures, cert=None, key=None):
        self.fixtures = fixtures
        self.events = []
        self.closed = threading.Event()
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
                if mode not in ('file','stream','drop','stall','jitter','redirect','error'):
                    self.send_error(404)
                    return
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
                data = spec['data']
                self.send_response(200)
                self.send_header('Content-Type', spec['mime'])
                if mode != 'stream':
                    self.send_header('Content-Length', str(len(data)))
                self.send_header('Connection', 'close')
                self.end_headers()
                event = dict(mode=mode, fixture=name, sent=0, complete=False)
                outer.events.append(event)
                started = time.monotonic()
                deadline = started
                try:
                    while not outer.closed.is_set() and time.monotonic() - started < 86400:
                        for segment in spec.get('segments', [spec]):
                            payload = segment['data']
                            bps = len(payload) / segment['seconds'] * 1.02
                            for offset in range(0, len(payload), 1024):
                                if outer.closed.is_set():
                                    return
                                if mode in ('drop','stall') and time.monotonic()-started >= 3:
                                    if mode == 'stall':
                                        outer.closed.wait(15)
                                    return
                                chunk = payload[offset:offset+1024]
                                self.wfile.write(chunk)
                                self.wfile.flush()
                                event['sent'] += len(chunk)
                                deadline += len(chunk) / bps
                                if mode == 'jitter' and offset % 8192 == 0:
                                    deadline += .035
                                if outer.closed.wait(max(0, deadline - time.monotonic())):
                                    return
                        if mode != 'stream':
                            event['complete'] = True
                            return
                except (BrokenPipeError, ConnectionError, TimeoutError, OSError):
                    pass
                finally:
                    self.close_connection = True
                    event['seconds'] = time.monotonic() - started

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
    args = parser.parse_args()
    specs = load_fixtures(args.fixture_manifest)
    if bool(args.cert) != bool(args.key):
        parser.error('--cert and --key must be supplied together')
    with Server(args.host,args.port,specs,args.cert,args.key):
        print(f"Serving {len(specs)} fixtures on port {args.port}; /manifest.json lists them", flush=True)
        try:
            threading.Event().wait()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
