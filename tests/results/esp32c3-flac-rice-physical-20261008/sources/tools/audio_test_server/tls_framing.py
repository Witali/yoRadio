"""Board-independent HTTPS body-framing and closure fixtures; no secrets logged."""
import socketserver
import ssl
import threading
import time
from urllib.parse import urlsplit

from .tls_records import Channel

MODES = ('length-notify', 'length-raw', 'length-short',
         'chunked-notify', 'chunked-raw', 'chunked-short',
         'close-notify', 'close-raw')


class FramingServer:
    def __init__(self, host, port, fixtures, cert, key):
        self.events = []
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = context.maximum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256')
        context.load_cert_chain(cert, key)
        outer = self

        class Handler(socketserver.BaseRequestHandler):
            def handle(self):
                event = dict(records=[], writes=[], dropped_records=0, dropped_writes=0,
                             completed_socket_bytes=0, complete=False)
                outer.events.append(event)
                self.request.settimeout(10)
                channel = Channel(self.request, context, event)
                try:
                    channel.handshake()
                    parts = urlsplit(channel.request()).path.strip('/').split('/')
                    if len(parts) != 2 or parts[0] not in MODES or parts[1] not in fixtures:
                        channel.write(b'HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n', 'headers')
                        channel.close_write()
                        return
                    mode, name = parts
                    framing, ending = mode.split('-')
                    spec = fixtures[name]
                    data = spec['data']
                    if not data:
                        raise ValueError('Empty fixture')
                    event.update(mode=mode, fixture=name, fixture_sha256=spec['sha256'],
                                 body_bytes=len(data), started_at=time.monotonic())
                    headers = ['HTTP/1.1 200 OK', 'Content-Type: '+spec['mime'], 'Connection: close']
                    if framing == 'length':
                        # Deliver every valid codec frame but deliberately promise
                        # one more byte in the incomplete-Content-Length case.
                        headers.append('Content-Length: '+str(len(data)+(ending == 'short')))
                    if framing == 'chunked':
                        headers.append('Transfer-Encoding: chunked')
                    channel.write(('\r\n'.join(headers)+'\r\n\r\n').encode(), 'headers')
                    for at in range(0, len(data), 1024):
                        payload = data[at:at+1024]
                        if framing == 'chunked':
                            payload = f'{len(payload):x};fixture=1\r\n'.encode()+payload+b'\r\n'
                        channel.write(payload, 'body')
                    if framing == 'chunked' and ending != 'short':
                        channel.write(b'0\r\nX-Fixture: complete\r\n\r\n', 'terminal-chunk')
                    if ending != 'raw':
                        channel.close_write()
                    event['complete'] = True
                except ssl.SSLError as error:
                    event.update(error=type(error).__name__, tls_reason=error.reason)
                except (OSError, EOFError, ValueError) as error:
                    event['error'] = type(error).__name__
                finally:
                    event['ended_at'] = time.monotonic()

        class Server(socketserver.ThreadingTCPServer):
            allow_reuse_address = True
            daemon_threads = True

        self.server = Server((host, port), Handler)
        self.thread = None

    def __enter__(self):
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *unused):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


def main():
    import argparse
    import json
    from pathlib import Path
    from .fixtures import load_fixtures
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host', required=True)
    p.add_argument('--port', type=int, default=8773)
    p.add_argument('--cert', type=Path, required=True)
    p.add_argument('--key', type=Path, required=True)
    p.add_argument('--seconds', type=int, default=600)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if not 1 <= args.seconds <= 600 or args.output.exists():
        p.error('Use 1..600 seconds and a new output file')
    with FramingServer(args.host, args.port, load_fixtures(), args.cert, args.key) as server:
        print('HTTPS framing server ready; routes /MODE/FIXTURE; modes: '+', '.join(MODES), flush=True)
        try:
            threading.Event().wait(args.seconds)
        except KeyboardInterrupt:
            pass
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(server.events, indent=2)+'\n')


if __name__ == '__main__':
    main()
