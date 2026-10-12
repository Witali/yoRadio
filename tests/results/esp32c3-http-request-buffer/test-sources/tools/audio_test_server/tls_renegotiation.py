"""TLS 1.2 server-initiated renegotiation with bounded, metadata-only evidence.

Optional dependency: pyOpenSSL. It is needed only when this module is used;
ordinary record tests retain Python's standard ssl implementation.
"""
import ssl
import time

from OpenSSL import SSL
import OpenSSL
from .tls_records import Channel, RecordServer


def backend_versions():
    return dict(pyopenssl=OpenSSL.__version__,openssl=SSL.SSLeay_version(SSL.SSLEAY_VERSION).decode('ascii'))


def handshake_done(connection, where, result):
    if where & SSL.SSL_CB_HANDSHAKE_DONE:
        event = connection.get_app_data()
        # OpenSSL also emits HANDSHAKE_DONE after sending HelloRequest, while
        # renegotiation is still pending. Retain it, but never count it as a
        # completed peer handshake.
        event['handshake_callbacks'].append(dict(at=time.perf_counter(),
            renegotiations=connection.total_renegotiations(),pending=connection.renegotiate_pending(),
            version=connection.get_protocol_version_name(),cipher=connection.get_cipher_name()))


class RenegotiationChannel(Channel):
    def __init__(self,sock,context,event):
        self.sock,self.event = sock,event
        self.tls = SSL.Connection(context,None)
        self.tls.set_accept_state()
        self.tls.set_app_data(event)
        event.update(handshake_callbacks=[],renegotiation_requests=[],renegotiation_completions=[],
                     session_cache_enabled=False,session_tickets_enabled=False,**backend_versions())
        self.pending = bytearray()
        self.phase = 'handshake'

    def drain(self):
        while True:
            try:data = self.tls.bio_read(65536)
            except SSL.WantReadError:return
            self.pending.extend(data)
            while len(self.pending)>=5:
                size = int.from_bytes(self.pending[3:5],'big')
                if len(self.pending)<size+5:break
                if len(self.event['records'])<4096:
                    self.event['records'].append(dict(phase=self.phase,type=self.pending[0],
                        wire_payload_bytes=size,at=time.perf_counter()))
                else:self.event['dropped_records']+=1
                del self.pending[:size+5]
            self.sock.sendall(data)
            self.event['completed_socket_bytes']+=len(data)

    def incoming_data(self):
        data = self.sock.recv(32768)
        if not data:raise EOFError('TLS peer closed')
        if self.tls.bio_write(data)!=len(data):raise ValueError('Partial BIO input')

    def operation(self,function):
        while True:
            try:
                value = function();self.drain();return value
            except SSL.WantReadError:
                self.drain();self.incoming_data()
            except SSL.WantWriteError:self.drain()
            except SSL.Error as error:
                # Keep private peer/certificate details out of server reports.
                raise ssl.SSLError('OpenSSL operation failed') from error

    def handshake(self):
        self.operation(self.tls.do_handshake)
        self.event.update(version=self.tls.get_protocol_version_name(),cipher=self.tls.get_cipher_name())

    def renegotiate(self):
        self.phase = 'renegotiation'
        before = self.tls.total_renegotiations()
        self.event['renegotiation_requests'].append(dict(at=time.perf_counter(),before=before))
        if not self.tls.renegotiate():raise ValueError('Renegotiation was not started')
        self.operation(self.tls.do_handshake)
        # Server do_handshake may only send HelloRequest. Drive reads until
        # the peer's handshake actually completes, without waiting for a new
        # HTTP request (this is one long-running response).
        deadline = time.perf_counter()+10
        while self.tls.renegotiate_pending():
            if time.perf_counter()>=deadline:raise TimeoutError('Renegotiation deadline')
            try:
                data = self.tls.recv(1)
                if data:raise ValueError('Unexpected HTTP data during renegotiation')
                raise EOFError('TLS peer closed during renegotiation')
            except SSL.WantReadError:
                self.drain()
                if not self.tls.renegotiate_pending():break
                self.incoming_data()
            except SSL.WantWriteError:self.drain()
            except SSL.Error as error:
                raise ssl.SSLError('OpenSSL renegotiation failed') from error
        self.drain()
        self.event['renegotiation_completions'].append(dict(at=time.perf_counter(),
            after=self.tls.total_renegotiations(),pending=self.tls.renegotiate_pending()))

    def close_write(self):
        self.phase = 'close'
        try:self.tls.shutdown()
        except (SSL.WantReadError,SSL.WantWriteError):pass
        except SSL.Error as error:raise ssl.SSLError('OpenSSL shutdown failed') from error
        self.drain()


class RenegotiationServer(RecordServer):
    def __init__(self,host,port,fixtures,cert,key,*,renegotiate_seconds=30,**kwargs):
        context = SSL.Context(SSL.TLS_SERVER_METHOD)
        context.set_min_proto_version(SSL.TLS1_2_VERSION)
        context.set_max_proto_version(SSL.TLS1_2_VERSION)
        context.set_cipher_list(b'ECDHE-RSA-AES128-GCM-SHA256')
        context.use_certificate_file(str(cert));context.use_privatekey_file(str(key))
        context.check_privatekey()
        context.set_session_cache_mode(SSL.SESS_CACHE_OFF)
        context.set_options(SSL.OP_NO_TICKET)
        context.set_info_callback(handshake_done)
        super().__init__(host,port,fixtures,cert,key,tls_context=context,
            channel_type=RenegotiationChannel,renegotiate_seconds=renegotiate_seconds,**kwargs)
