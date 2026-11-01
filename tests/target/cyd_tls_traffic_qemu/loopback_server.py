"""Local TLS1.2 peer with actual TLS-record observations, no external listener.

Generated keys are supplied by an ignored test campaign, never embedded here.
This module is a diagnostic peer, not firmware or a production web server.
"""
import hashlib
import json
from pathlib import Path
import socket
import ssl
import threading
import time


PAYLOAD = bytes((i * 73 + (i >> 8) * 19 + 11) & 255 for i in range(65536))
PAYLOAD_SHA256 = hashlib.sha256(PAYLOAD).hexdigest()


class LoopbackTLS:
    def __init__(self, material, log, ports=(18443, 18444, 18445)):
        self.material, self.log = Path(material), Path(log)
        if self.log.exists() or len(ports) != 3 or len(set(ports)) != 3:
            raise ValueError('fresh log and three distinct loopback endpoints required')
        self.ports = ports
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.minimum_version = ssl.TLSVersion.TLSv1_2
        self.context.maximum_version = ssl.TLSVersion.TLSv1_2
        self.context.set_ciphers('ECDHE-RSA-AES128-GCM-SHA256')
        self.context.load_cert_chain(self.material / 'server.pem', self.material / 'server-key.pem')
        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.listeners, self.accept_threads, self.threads, self.connections = [], [], [], set()
        self.ordinal = 0
        self.parallel = threading.Barrier(2, timeout=20)
        self.log.parent.mkdir(parents=True, exist_ok=True)
        self.stream = self.log.open('x', encoding='utf-8', newline='\n')

    def record(self, **value):
        with self.lock:
            value['monotonic_ns'] = time.monotonic_ns()
            self.stream.write(json.dumps(value, sort_keys=True) + '\n')
            self.stream.flush()

    def __enter__(self):
        try:
            for mode, port in zip(('normal', 'handshake_close', 'truncated_record'), self.ports):
                listener = socket.socket()
                listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                listener.bind(('127.0.0.1', port))
                listener.listen(8)
                listener.settimeout(0.2)
                self.listeners.append(listener)
                thread = threading.Thread(target=self.accept, args=(listener, mode), daemon=True)
                self.accept_threads.append(thread)
                thread.start()
            self.record(event='listening', host='127.0.0.1', ports=self.ports,
                        payload_bytes=len(PAYLOAD), payload_sha256=PAYLOAD_SHA256,
                        tls='TLSv1.2', cipher='ECDHE-RSA-AES128-GCM-SHA256')
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def accept(self, listener, mode):
        while not self.stop.is_set():
            try:
                connection, _ = listener.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            with self.lock:
                self.ordinal += 1
                number = self.ordinal
                self.connections.add(connection)
            thread = threading.Thread(target=self.serve, args=(connection, number, mode), daemon=True)
            with self.lock:
                self.threads.append(thread)
            thread.start()

    def serve(self, connection, number, mode):
        incoming, outgoing = ssl.MemoryBIO(), ssl.MemoryBIO()
        tls = self.context.wrap_bio(incoming, outgoing, server_side=True)
        wire_pending = bytearray()
        record_number = 0

        def wire(data):
            nonlocal record_number
            wire_pending.extend(data)
            while len(wire_pending) >= 5:
                size = int.from_bytes(wire_pending[3:5], 'big')
                if len(wire_pending) < size + 5:
                    break
                record_number += 1
                self.record(event='server_record', connection=number, ordinal=record_number,
                            content_type=wire_pending[0], record_bytes=size, header_bytes=5)
                del wire_pending[:size + 5]

        def flush(truncate=False):
            data = outgoing.read()
            if truncate:
                if len(data) < 6 or data[0] != 23:
                    raise ValueError('actual application TLS record required before truncation')
                advertised = int.from_bytes(data[3:5], 'big')
                cut = min(len(data) - 1, 5 + max(1, advertised // 2))
                connection.sendall(data[:cut])
                self.record(event='record_truncated', connection=number,
                            advertised_record_bytes=advertised, sent_wire_bytes=cut)
                return
            if data:
                wire(data)
                connection.sendall(data)

        def progress(function):
            while True:
                try:
                    value = function()
                    flush()
                    return value
                except ssl.SSLWantWriteError:
                    flush()
                except ssl.SSLWantReadError:
                    flush()
                    data = connection.recv(32768)
                    if not data:
                        incoming.write_eof()
                    else:
                        incoming.write(data)

        try:
            connection.settimeout(20)
            self.record(event='accepted', connection=number, mode=mode)
            if mode == 'handshake_close':
                data = connection.recv(4096)
                self.record(event='handshake_closed', connection=number, received_bytes=len(data))
                return
            progress(tls.do_handshake)
            self.record(event='handshake', connection=number, version=tls.version(), cipher=tls.cipher()[0])
            request = bytearray()
            while b'\r\n\r\n' not in request:
                data = progress(lambda: tls.read(1024))
                if not data or len(request) + len(data) > 4096:
                    raise ValueError('bounded complete diagnostic HTTP request required')
                request.extend(data)
            first = bytes(request).split(b'\r\n', 1)[0]
            if not first.startswith(b'GET /case/') or not first.endswith(b' HTTP/1.1'):
                raise ValueError('explicit diagnostic GET path required')
            label = first[10:-9].decode('ascii')
            if not label or not all(c.isalnum() or c == '_' for c in label):
                raise ValueError('synthetic case identifier required')
            parallel = label in ('parallel_a', 'parallel_b')
            if parallel:
                self.record(event='parallel_ready', connection=number, case=label)
                self.parallel.wait()
            response = b'HTTP/1.1 200 OK\r\nContent-Length: 65536\r\nConnection: close\r\n\r\n'
            progress(lambda: tls.write(response))
            sent = 0
            for at in range(0, len(PAYLOAD), 16384):
                chunk = PAYLOAD[at:at + 16384]
                if parallel:
                    self.parallel.wait()
                    self.record(event='parallel_round', connection=number, case=label, round=at//16384)
                if mode == 'truncated_record':
                    written = tls.write(chunk)
                    if written != len(chunk):
                        raise ValueError('complete plaintext write required for truncated-record control')
                    flush(truncate=True)
                    return
                written = progress(lambda: tls.write(chunk))
                if written != len(chunk):
                    raise ValueError('complete full-record plaintext write required')
                sent += written
                self.record(event='plaintext_write', connection=number, case=label, bytes=written)
            self.record(event='response_complete', connection=number, case=label,
                        bytes=sent, sha256=PAYLOAD_SHA256)
            try:
                progress(tls.unwrap)
            except (ssl.SSLError, OSError):
                # The data result and explicit close behavior are recorded
                # separately; a peer may close TCP without a TLS close_notify.
                self.record(event='peer_closed_after_response', connection=number)
            if wire_pending:
                raise ValueError('partial generated server record after normal flush')
        except (ssl.SSLError, OSError, ValueError, threading.BrokenBarrierError) as error:
            self.record(event='peer_error', connection=number, mode=mode,
                        error_type=type(error).__name__, reason=str(error))
        finally:
            with self.lock:
                self.connections.discard(connection)
            connection.close()
            self.record(event='connection_closed', connection=number, mode=mode)

    def __exit__(self, *_):
        self.stop.set()
        for listener in self.listeners:
            listener.close()
        with self.lock:
            connections = list(self.connections)
        for connection in connections:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            connection.close()
        # Accept threads can append workers until they join. Join those first,
        # then the stable worker inventory before closing their shared log.
        for thread in self.accept_threads:
            thread.join(timeout=2)
        with self.lock:
            threads = list(self.threads)
        for thread in threads:
            thread.join(timeout=21)
        if any(thread.is_alive() for thread in threads):
            raise RuntimeError('diagnostic peer worker did not terminate')
        self.record(event='server_stopped', connections=self.ordinal)
        self.stream.close()
