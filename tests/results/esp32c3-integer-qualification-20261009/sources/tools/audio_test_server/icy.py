"""Board-independent ICY metadata fixture server with synthetic song titles.

Audio repeats as ADTS AAC. Only metadata is fragmented explicitly; TCP may
coalesce writes, so exhaustive parser boundary coverage belongs in host tests.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import time

INTERVAL = 1024
INITIAL_TITLE = 'ICY initial title'
PROGRAMS = {
    'quoted': (b"StreamTitle='Don't Stop';StreamUrl='test';", "Don't Stop"),
    'long': ((b"StreamTitle='" + b'A' * 4000 + b"';").ljust(4080, b'\0'), 'A' * 191),
    'empty': (b"StreamTitle='';", ''),
    'missing': (b"StreamUrl='test';", INITIAL_TITLE),
    'fallback': (b"StreamTitle='Fallback' trailing text", 'Fallback'),
    'utf8': ("StreamTitle='ёRadio — 音楽';".encode(), 'ёRadio — 音楽'),
    'nul': (b"\0StreamTitle='hidden';", INITIAL_TITLE),
}


def metadata_block(payload):
    blocks = (len(payload) + 15) // 16
    if blocks > 255:
        raise ValueError('ICY metadata exceeds 4080 bytes')
    return bytes([blocks]) + payload.ljust(blocks * 16, b'\0')


def stream_blocks(data, payload, interval=INTERVAL):
    """Yield complete audio/metadata pairs without dropping bytes at loop end."""
    if not data or interval < 1:
        raise ValueError('Nonempty audio and a positive interval are required')
    first = metadata_block(("StreamTitle='" + INITIAL_TITLE + "';").encode())
    subsequent = metadata_block(payload)
    offset = 0
    index = 0
    while True:
        audio = bytearray()
        while len(audio) < interval:
            take = min(interval - len(audio), len(data) - offset)
            audio.extend(data[offset:offset + take])
            offset = (offset + take) % len(data)
        yield bytes(audio), first if index < 2 else subsequent
        index += 1


class IcyServer:
    def __init__(self, host, port, fixture, programs=None):
        if fixture['codec'] != 'aac':
            raise ValueError('Repeating ICY fixtures require ADTS AAC')
        self.events = []
        self.closed = threading.Event()
        programs = PROGRAMS if programs is None else programs
        outer = self

        class Handler(BaseHTTPRequestHandler):
            protocol_version = 'HTTP/1.1'

            def log_message(self, *_):
                pass

            def do_GET(self):
                name = self.path.removeprefix('/')
                if name not in programs:
                    self.send_error(404)
                    return
                event = dict(case=name, audio_bytes=0, metadata_bytes=0, blocks=0,
                             clock='time.perf_counter',
                             metadata_requested=self.headers.get('Icy-MetaData') == '1')
                outer.events.append(event)
                self.send_response(200)
                self.send_header('Content-Type', fixture['mime'])
                self.send_header('icy-metaint', str(INTERVAL))
                self.send_header('Connection', 'close')
                self.end_headers()
                started = time.perf_counter()
                bps = len(fixture['data']) / fixture['seconds'] * 1.02
                try:
                    for audio, metadata in stream_blocks(fixture['data'], programs[name][0]):
                        if outer.closed.is_set() or time.perf_counter() - started > 30:
                            return
                        self.wfile.write(audio)
                        # Deliberately split the length, key and a title byte.
                        for begin, end in ((0, 1), (1, 8), (8, 15), (15, len(metadata))):
                            self.wfile.write(metadata[begin:end])
                            self.wfile.flush()
                        event['audio_bytes'] += len(audio)
                        event['metadata_bytes'] += len(metadata)
                        event['blocks'] += 1
                        if outer.closed.wait(max(0, started + event['audio_bytes'] / bps - time.perf_counter())):
                            return
                except (BrokenPipeError, ConnectionError, TimeoutError, OSError):
                    pass
                finally:
                    self.close_connection = True
                    event['seconds'] = time.perf_counter() - started

        self.http = ThreadingHTTPServer((host, port), Handler)
        self.http.daemon_threads = True

    def __enter__(self):
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.closed.set()
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(timeout=2)
