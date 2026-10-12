"""Bounded diagnostic relay for one configured HTTP(S) audio source.

Forward encoded/ICY bytes without decoding, reconnecting or storing audio.
The relay changes TCP endpoints, buffering and delivery timing; it cannot
prove that a direct client received identical live content at the same time.
"""
import hashlib
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import time
from urllib.parse import urlsplit

from .server import DeliveryStats


class AudioRelay:
    def __init__(self, host, port, source, *, seconds=180):
        url = urlsplit(source)
        if (url.scheme not in ('http','https') or not url.hostname or url.username
                or url.password or url.query or url.fragment):
            raise ValueError('Use a configured HTTP(S) source without credentials, query or fragment')
        if type(seconds) is not int or not 1 <= seconds <= 600:
            raise ValueError('Relay duration must be 1..600 seconds')
        self.events = []
        self.closed = threading.Event()
        owner = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'

            def log_message(self, *_): pass

            def do_GET(self):
                if self.path != '/stream':
                    self.send_error(404)
                    return
                started = time.perf_counter()
                event = dict(started_at=started, clock='time.perf_counter',
                    tls_verified=url.scheme=='https', received=0, sent=0,
                    max_read_seconds=0, ended=False, termination=None)
                owner.events.append(event)
                request_icy = self.headers.get('Icy-MetaData') == '1'
                event['icy_requested'] = request_icy
                cls = http.client.HTTPSConnection if url.scheme=='https' else http.client.HTTPConnection
                upstream = cls(url.hostname, url.port, timeout=5)
                received_hash, sent_hash = hashlib.sha256(), hashlib.sha256()
                delivery = DeliveryStats(started, event)
                response_started = False
                try:
                    headers={'User-Agent':'yoRadio-native/1','Connection':'close'}
                    if request_icy: headers['Icy-MetaData']='1'
                    upstream.request('GET',url.path or '/',headers=headers)
                    response=upstream.getresponse()
                    event['upstream_status']=response.status
                    if response.status!=200:
                        event['termination']='upstream-status'
                        self.send_error(502)
                        return
                    self.send_response(200)
                    # Decode HTTP transfer framing upstream; retain ICY framing.
                    # No Content-Length or Transfer-Encoding: close delimits body.
                    for key in ('Content-Type','icy-metaint','icy-br'):
                        value=response.getheader(key)
                        if value is not None:
                            self.send_header(key,value)
                            if key=='icy-metaint': event['icy_interval']=int(value)
                    self.send_header('Connection','close')
                    self.end_headers()
                    response_started=True
                    self.connection.settimeout(5)
                    while not owner.closed.is_set() and time.perf_counter()-started<seconds:
                        before=time.perf_counter()
                        block=response.read1(2048)
                        after=time.perf_counter()
                        event['max_read_seconds']=max(event['max_read_seconds'],after-before)
                        if not block:
                            event['termination']='upstream-eof'
                            break
                        event['received']+=len(block)
                        received_hash.update(block)
                        self.wfile.write(block)
                        self.wfile.flush()
                        event['sent']+=len(block)
                        sent_hash.update(block)
                        delivery.write(len(block),after,time.perf_counter())
                    else:
                        event['termination']='controller-stop' if owner.closed.is_set() else 'duration-limit'
                except (OSError, http.client.HTTPException, ValueError) as error:
                    # Exception text can contain source metadata; keep types only.
                    event.update(termination='transport-error',error_type=type(error).__name__)
                    if not response_started:
                        try:self.send_error(502)
                        except OSError:pass
                finally:
                    upstream.close()
                    self.close_connection=True
                    delivery.finish(time.perf_counter())
                    event.update(ended=True,ended_at=time.perf_counter(),
                        received_sha256=received_hash.hexdigest(),sent_sha256=sent_hash.hexdigest())

        self.http=ThreadingHTTPServer((host,port),Handler)

    def __enter__(self):
        self.thread=threading.Thread(target=self.http.serve_forever,daemon=True)
        self.thread.start()
        return self

    def __exit__(self,*_):
        self.closed.set()
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(timeout=2)
