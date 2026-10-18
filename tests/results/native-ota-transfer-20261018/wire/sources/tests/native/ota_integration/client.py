"""Independent HTTP upload client; OpenSSL verifies CA and hostname for TLS."""
import argparse
import json
from pathlib import Path
import socket
import ssl
import time

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,required=True)
    parser.add_argument('--ca')
    parser.add_argument('--image',type=Path,required=True)
    parser.add_argument('--mode',required=True)
    parser.add_argument('--c3',action='store_true')
    args=parser.parse_args()
    image=args.image.read_bytes()
    if args.mode=='wrong-project':image=image.replace(b'native-radio\0',b'wrong--radio\0',1)
    first=b'--ota-boundary\r\nContent-Disposition: form-data; name="updatetarget"\r\n\r\nfw\r\n'
    first+=b'--ota-boundary\r\nContent-Disposition: form-data; name="update"; filename="app.bin"\r\nContent-Type: application/octet-stream\r\n\r\n'
    body=first+image+b'\r\n--ota-boundary--\r\n'
    if args.mode=='bad-footer':body=body[:-6]+b'BADBAD'
    kind=b'multipart/form-data; boundary=ota-boundary'
    if args.mode=='x-boundary':kind=b'multipart/form-data; x-boundary=ota-boundary'
    if args.mode=='duplicate-boundary':kind+=b'; boundary=evil'
    header=b'POST /update HTTP/1.1\r\nHost: localhost\r\nContent-Type: '+kind+b'\r\nContent-Length: '+str(len(body)).encode()+b'\r\nConnection: keep-alive\r\n\r\n'
    raw=socket.create_connection(('127.0.0.1',args.port),timeout=15)
    peer=raw
    if args.ca:
        context=ssl.create_default_context(cafile=args.ca)
        context.minimum_version=context.maximum_version=ssl.TLSVersion.TLSv1_2
        peer=context.wrap_socket(raw,server_hostname='localhost',suppress_ragged_eofs=False)
        assert context.verify_mode==ssl.CERT_REQUIRED and context.check_hostname and peer.getpeercert() and peer.version()=='TLSv1.2'
    with peer:
        if args.mode=='info':peer.sendall(b'GET /api/native/ota HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
        elif args.mode in ['pause-2s','idle-10s']:
            peer.sendall(header+body[:1024])
            time.sleep(2 if args.mode=='pause-2s' else 10.25)
            if args.mode=='pause-2s':peer.sendall(body[1024:])
        elif args.mode=='unread-body':
            # Declare the full upload but keep most of it unsent. Successful
            # HTTP rejection and TLS close_notify must not wait for SDK purge.
            peer.sendall(header+body[:1024])
        else:peer.sendall(header+body)
        response=b''
        try:
            while True:
                chunk=peer.recv(4096)
                if not chunk:break
                response+=chunk
        except ssl.SSLEOFError:
            assert args.mode=='response-oom'
        if args.mode=='response-oom':
            assert not response
            return
        expected=503 if args.mode=='unread-body' else 408 if args.mode=='idle-10s' else 400 if args.mode in ['x-boundary','duplicate-boundary','wrong-project','bad-footer','maintenance-failure'] else 200
        assert response.startswith(f'HTTP/1.1 {expected} '.encode()),(args.mode,response)
        header,body=response.split(b'\r\n\r\n',1)
        if args.mode!='info':assert b'Connection: close\r\n' in header+b'\r\n'
        length=int(next(line.split(b':',1)[1] for line in header.split(b'\r\n') if line.lower().startswith(b'content-length:')))
        assert len(body)==length
        if args.mode=='info':
            metadata=json.loads(body);assert metadata['version']=='integration' and metadata['partition']=='ota_0' and metadata['max_size']==0x1b0000 and metadata['max_body_size']==0x1b0000+4096 and metadata['app_elf_sha256']=='0'*64
        elif expected==200:assert body==b'OK'

if __name__=='__main__':main()
