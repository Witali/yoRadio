"""Optional real loopback WebSocket peers for the full-application QEMU gate.

The installed websockets client handles framing and control messages. Readers
continuously drain server messages so the probe doesn't manufacture backpressure.
Only bounded receipt metadata is retained, never complete status payloads.
"""
from collections import deque
import hashlib
import json
import threading
import time

import websockets
from websockets.sync.client import connect


class WebSocketPeers:
    def __init__(self, count):
        if count not in (1, 2):
            raise ValueError('Expected one or two WebSocket peers')
        self.count = count
        self.clients = []
        self.threads = []
        self.stop = threading.Event()
        self.condition = threading.Condition()
        self.history = [deque(maxlen=64) for _ in range(count)]
        self.receipts = [0] * count
        self.errors = []
        self.phases = {}

    def _read(self, index, client):
        try:
            while not self.stop.is_set():
                try:
                    text = client.recv(timeout=0.25)
                except TimeoutError:
                    continue
                if not isinstance(text, str):
                    raise RuntimeError('Unexpected binary status message')
                message = json.loads(text)
                if 'status' not in message:
                    continue
                status = message['status']
                if not (isinstance(status['audio'], bool) and type(status['generation']) is int
                        and 0 <= status['generation'] <= 0xffffffff
                        and all(isinstance(status[key], str) for key in ('station', 'title', 'format'))):
                    raise RuntimeError('Incomplete WebSocket status')
                payload = {entry['id']: entry['value'] for entry in message['payload']}
                if payload.get('meta') != status['title'] or payload.get('fmt') != status['format']:
                    raise RuntimeError('Inconsistent WebSocket status payload')
                encoded = text.encode('utf-8')
                with self.condition:
                    self.receipts[index] += 1
                    self.history[index].append(dict(receipt=self.receipts[index], audio=status['audio'],
                        generation=status['generation'], network_online=status['network_online'],
                        rssi_valid=status['rssi_valid'], rssi=status['rssi'],
                        json_bytes=len(encoded), sha256=hashlib.sha256(encoded).hexdigest()))
                    self.condition.notify_all()
        except Exception as error:
            if not self.stop.is_set():
                with self.condition:
                    self.errors.append(dict(client=index, category=type(error).__name__))
                    self.condition.notify_all()

    def open(self, port):
        for index in range(self.count):
            try:
                client = connect(f'ws://127.0.0.1:{port}/ws', compression=None, proxy=None,
                    open_timeout=8, close_timeout=2, ping_interval=None, max_size=5120, max_queue=4)
            except Exception as error:
                raise RuntimeError('WebSocket peer handshake failed') from error
            self.clients.append(client)
            reader = threading.Thread(target=self._read, args=(index, client), daemon=True)
            self.threads.append(reader)
            reader.start()

    def require_status(self, phase, *, audio, generation=None):
        deadline = time.monotonic() + 8
        with self.condition:
            while True:
                if self.errors:
                    raise RuntimeError('A live WebSocket peer failed')
                selected = [next((item for item in reversed(history) if item['audio'] == audio
                    and (generation is None or item['generation'] == generation)), None) for history in self.history]
                if all(item is not None for item in selected):
                    self.phases[phase] = selected
                    return
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise RuntimeError('Missing WebSocket status at ' + phase)
                self.condition.wait(min(remaining, 0.25))

    def close(self):
        self.stop.set()
        for index, client in enumerate(self.clients):
            try:
                client.close()
                if client.close_code != 1000:
                    self.errors.append(dict(client=index, category='unexpected-close-code', code=client.close_code))
            except Exception as error:
                self.errors.append(dict(client=index, category=type(error).__name__))
        for index, reader in enumerate(self.threads):
            reader.join(timeout=3)
            if reader.is_alive():
                self.errors.append(dict(client=index, category='reader-did-not-stop'))
        return not self.errors and len(self.clients) == self.count

    def summary(self):
        with self.condition:
            return dict(clients=self.count, client_library='websockets', client_version=websockets.__version__,
                continuously_drained=True, compression=False, proxy=False,
                status_receipts=list(self.receipts), phases=dict(self.phases), errors=list(self.errors),
                close_codes=[client.close_code for client in self.clients],
                readers_stopped=all(not thread.is_alive() for thread in self.threads))
