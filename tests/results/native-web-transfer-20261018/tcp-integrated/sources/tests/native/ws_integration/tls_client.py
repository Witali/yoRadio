"""Verified OpenSSL client for complete ESP-TLS/HTTPD/application WS path."""
import argparse
import socket
import ssl

REQUEST=(b'GET /ws HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n'
         b'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n\r\n')


def frame(opcode,body=b'',final=True):
    assert len(body)<126
    key=b'\x13\x37\0\xff'
    return bytes([opcode|(128 if final else 0),128|len(body)])+key+bytes(value^key[i%4] for i,value in enumerate(body))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,required=True)
    parser.add_argument('--ca',required=True)
    parser.add_argument('--mode',required=True)
    args=parser.parse_args()
    context=ssl.create_default_context(cafile=args.ca)
    context.minimum_version=context.maximum_version=ssl.TLSVersion.TLSv1_2
    with socket.create_connection(('127.0.0.1',args.port),timeout=8) as raw:
      with context.wrap_socket(raw,server_hostname='localhost',suppress_ragged_eofs=False) as tls:
        assert context.verify_mode==ssl.CERT_REQUIRED and context.check_hostname and tls.getpeercert()
        assert tls.version()=='TLSv1.2'
        def exact(size):
            out=b''
            while len(out)<size:
                chunk=tls.recv(size-len(out));assert chunk;out+=chunk
            return out
        def expect(op,body):
            assert exact(2)==bytes([128|op,len(body)])
            assert exact(len(body))==body
        close=frame(8,b'\x03\xe8bye')
        request=REQUEST
        if args.mode=='fragment-ping':
            data=frame(1,b'pi',False)+frame(9,b'\0\xff')+frame(10,b'unsolicited')+frame(0,b'ng')+close
        elif args.mode=='utf8-fragments':
            data=frame(1,b'A\xe2',False)+frame(9)+frame(0,b'\x82',False)+frame(0,b'\xacZ')+frame(10)+close
        elif args.mode=='invalid-utf8':data=frame(1,b'\xc0\xaf')
        elif args.mode=='rsv':data=bytes([0xc1])+frame(1,b'x')[1:]
        elif args.mode=='close-reason':data=frame(8,b'\x03\xe8\xff')
        elif args.mode=='close-tail':data=close+frame(1,b'forbidden')
        elif args.mode.startswith('http-'):
            extra={'http-plain':b'','http-connection':b'Connection: Upgrade\r\n',
                   'http-other':b'Upgrade: h2c\r\nConnection: Upgrade\r\n',
                   'http-upgrade-only':b'Upgrade: websocket\r\n',
                   'http-keepalive':b'Upgrade: websocket\r\nConnection: keep-alive\r\n'}[args.mode]
            request=(b'GET /ws HTTP/1.1\r\nHost: localhost\r\n'
                b'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\nSec-WebSocket-Version: 13\r\n'+extra+b'\r\n');data=b''
        else:
            extra={'extensions':b'Sec-WebSocket-Extensions: private; p="two words"\r\n',
                   'protocol':b'Sec-WebSocket-Protocol: chat, chat\r\n','empty-length':b'Content-Length: \r\n'}[args.mode]
            request=request[:-2]+extra+b'\r\n';data=b''
        # One SSL application write contains the HTTP upgrade and first frame.
        tls.sendall(request+data)
        if not data:
            if args.mode.startswith('http-') and args.mode!='http-other':
                # Real application selects HTTP400; response formatting alone
                # is a fixed host seam, explicitly outside this gate's scope.
                header=b''
                while not header.endswith(b'\r\n\r\n'):header+=exact(1)
                assert header.startswith(b'HTTP/1.1 400 Bad Request\r\n')
            assert tls.recv(1)==b'';return
        header=b''
        while not header.endswith(b'\r\n\r\n'):header+=exact(1)
        assert header.startswith(b'HTTP/1.1 101 Switching Protocols\r\n')
        assert b'Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=\r\n' in header
        assert b'Sec-WebSocket-Extensions:' not in header and b'Sec-WebSocket-Protocol:' not in header
        if args.mode=='fragment-ping':expect(10,b'\0\xff')
        if args.mode=='utf8-fragments':expect(10,b'')
        body=b'\x03\xef' if args.mode in ('invalid-utf8','close-reason') else b'\x03\xea' if args.mode=='rsv' else b'\x03\xe8bye'
        expect(8,body)
        try:assert tls.recv(1)==b''
        except ssl.SSLEOFError:
            # Invalid incoming data follows the application's fatal shutdown;
            # a valid peer Close must also get a TLS close_notify.
            assert args.mode in ('invalid-utf8','close-reason')


if __name__=='__main__':main()
