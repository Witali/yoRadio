"""Independent OpenSSL client for the pinned ESP-TLS transport host test."""
import argparse
import os
import socket
import ssl


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,required=True)
    parser.add_argument('--ca',required=True)
    parser.add_argument('--mode',required=True)
    parser.add_argument('--control',type=int,required=True)
    args=parser.parse_args()
    raw=socket.create_connection(('127.0.0.1',args.port),timeout=8)
    raw.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,4096)
    if args.mode=='silent':
        assert raw.recv(1)==b'';raw.close();return
    context=ssl.create_default_context(cafile=None if args.mode=='untrusted' else args.ca)
    context.minimum_version=ssl.TLSVersion.TLSv1_3 if args.mode=='version' else ssl.TLSVersion.TLSv1_2
    context.maximum_version=context.minimum_version
    try:
        tls=context.wrap_socket(raw,server_hostname='wrong-host.invalid' if args.mode=='hostname' else 'localhost',suppress_ragged_eofs=False)
    except ssl.SSLCertVerificationError:
        assert args.mode in ('untrusted','hostname');return
    except ssl.SSLError:
        assert args.mode=='version';return
    assert args.mode not in ('untrusted','hostname','version') and context.verify_mode==ssl.CERT_REQUIRED and context.check_hostname
    assert tls.version()=='TLSv1.2' and tls.getpeercert()
    if args.mode=='data':
        tls.sendall(bytes(index&255 for index in range(257)))
        assert os.read(args.control,1)==b'R'
        contents=bytearray()
        while len(contents)<131072+4:
            chunk=tls.recv(min(4096,131072+4-len(contents)))
            assert chunk;contents+=chunk
        assert contents[:131072]==bytes(index%251 for index in range(131072))
        assert contents[131072:]==b'TAIL'
        tls.sendall(b'ACK')
        # suppress_ragged_eofs=False distinguishes close_notify from raw EOF.
        assert tls.recv(1)==b''
        tls.close()
    elif args.mode=='peer-close':
        tls.sendall(b'PEER');underlying=tls.unwrap();underlying.close()
    elif args.mode=='fatal':
        tls.sendall(b'READY')
        try:
            tls.recv(1)
        except ssl.SSLEOFError:
            tls.close();return
        raise AssertionError('Fatal raw shutdown unexpectedly looked like a TLS close_notify')
    else:raise AssertionError('Unknown client mode')


if __name__=='__main__':main()
