"""Trace board HTTP transport phases without changing requests or retry policy.

Only numeric timings, local ports and exception types/codes are retained. URLs,
headers, response bodies, station names and credentials are never recorded.
"""
import argparse
import hashlib
import http.client
import importlib
import json
from pathlib import Path
import sys
import threading
import time
from urllib.parse import urlsplit


class TransportTrace:
    def __init__(self, host, stream):
        self.host, self.stream = host, stream
        self.connections = 0
        self.lock = threading.Lock()

    def __enter__(self):
        owner = self
        self.original = original = http.client.HTTPConnection

        class TracedConnection(original):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.trace_number = None
                if self.host == owner.host:
                    with owner.lock:
                        owner.connections += 1
                        self.trace_number = owner.connections

            def measured(self, phase, action):
                if self.trace_number is None:
                    return action()
                started = time.monotonic()
                row = dict(request=self.trace_number, phase=phase, at=started)
                try:
                    result = action()
                    row['result'] = 'PASS'
                    if phase == 'connect' and self.sock is not None:
                        row['local_port'] = self.sock.getsockname()[1]
                    return result
                except BaseException as error:
                    row.update(result='FAIL', error_type=type(error).__name__)
                    for key in ('errno', 'winerror'):
                        value = getattr(error, key, None)
                        if type(value) is int:
                            row[key] = value
                    raise
                finally:
                    row['ms'] = (time.monotonic() - started) * 1000
                    with owner.lock:
                        owner.stream.write(json.dumps(row) + '\n')
                        owner.stream.flush()

            def connect(self):
                return self.measured('connect', lambda: super(TracedConnection, self).connect())

            def request(self, *args, **kwargs):
                return self.measured('request_including_connect',
                    lambda: super(TracedConnection, self).request(*args, **kwargs))

            def getresponse(self):
                response = self.measured('response_headers',
                    lambda: super(TracedConnection, self).getresponse())
                if self.trace_number is not None:
                    read = response.read
                    response.read = lambda *a, **kw: self.measured('response_body', lambda: read(*a, **kw))
                return response

        http.client.HTTPConnection = TracedConnection
        return self

    def __exit__(self, *exception):
        http.client.HTTPConnection = self.original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runner', required=True, choices=('diagnostic', 'tls_records', 'tls_framing'))
    args, forwarded = parser.parse_known_args()
    if forwarded[:1] == ['--']:
        forwarded.pop(0)
    output = Path(forwarded[forwarded.index('--output') + 1])
    board = urlsplit(forwarded[forwarded.index('--board') + 1])
    host = board.hostname
    if not host or board.scheme != 'http':
        parser.error('Tracing requires the native board HTTP endpoint')
    output.parent.mkdir(parents=True, exist_ok=True)
    trace_path = output.with_name(output.name + '-request-phases.jsonl')
    with trace_path.open('x', encoding='utf-8') as stream:
        trace = TransportTrace(host, stream)
        original_args = sys.argv
        try:
            with trace:
                sys.argv = [args.runner + '.py', *forwarded]
                return importlib.import_module(args.runner).main()
        finally:
            sys.argv = original_args
            output.with_name(output.name + '-transport-timing.json').write_text(json.dumps(dict(
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                python=sys.version, runner=args.runner, connection_instances=trace.connections,
                note='Original HTTP transport, caller timeouts and exceptions; no retries or connection reuse added. Connect is included in request duration.'
            ), indent=2) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
