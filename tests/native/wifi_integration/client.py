"""Independent HTTP client; TLS uses OpenSSL CA and hostname verification."""
import argparse
import json
import socket
import ssl
import time


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',type=int,required=True)
    p.add_argument('--ca')
    p.add_argument('--mode',required=True)
    p.add_argument('--revision',required=True)
    a=p.parse_args();mode=a.mode
    path='/api/native/wifi';method='POST';kind='application/json'
    revision=a.revision[:-1]+('1' if a.revision[-1]!='1' else '2') if mode=='stale' else a.revision
    body=json.dumps({'revision':revision,'profiles':[{'id':'r2','password_action':'keep'},{'ssid':' new ','password_action':'set','password':'NEW_REQUEST_CANARY'}]},separators=(',',':')).encode()
    if mode=='malformed':body=b'{"password":"NEW_REQUEST_CANARY"}'
    if mode=='info':method='GET';body=b''
    if mode=='get-body':method='GET';body=b'x'*100000
    if mode.startswith('private:') or mode in ['public','head']:
        path=mode.split(':',1)[1] if mode.startswith('private:') else '/data/playlist.csv?download=1'
        method='HEAD' if mode=='head' else 'GET';body=b''
    if mode.startswith('import-'):
        path='/upload' if 'upload' in mode else '/webboard' if 'board' in mode else '/recovery/wifi'
        kind='multipart/form-data; boundary=wifi'
        csv=b'invalid' if mode=='import-board-invalid' else b' new \tIMPORT_REQUEST_CANARY\n'
        if 'recovery' in mode:
            body=b'--wifi\r\nContent-Disposition: form-data; name="ssid"\r\n\r\n new \r\n--wifi\r\nContent-Disposition: form-data; name="pass"\r\n\r\nIMPORT_REQUEST_CANARY\r\n--wifi--\r\n'
        else:
            body=(b'--wifi\r\nContent-Disposition: form-data; name="www"; filename="theme.css.gz"\r\n\r\nNEW\r\n' if mode=='import-board-busy' else b'')
            body+=b'--wifi\r\nContent-Disposition: form-data; name="'+(b'wifile' if path=='/upload' else b'data')+b'"; filename="wifi.csv"\r\n\r\n'+csv+b'\r\n--wifi--\r\n'
    headers=f'{method} {path} HTTP/1.1\r\nHost: localhost\r\nContent-Type: {kind}\r\nContent-Length: {len(body)}\r\nConnection: keep-alive\r\n\r\n'.encode()
    raw=socket.create_connection(('127.0.0.1',a.port),timeout=45);peer=raw
    if a.ca:
        ctx=ssl.create_default_context(cafile=a.ca);ctx.minimum_version=ctx.maximum_version=ssl.TLSVersion.TLSv1_2
        peer=ctx.wrap_socket(raw,server_hostname='localhost',suppress_ragged_eofs=False)
        assert ctx.verify_mode==ssl.CERT_REQUIRED and ctx.check_hostname and peer.getpeercert() and peer.version()=='TLSv1.2'
    with peer:
        if mode in ['pause-2s','import-upload-pause']:
            peer.sendall(headers+body[:37]);time.sleep(2);peer.sendall(body[37:])
        elif mode=='idle-10s':peer.sendall(headers+body[:37]);time.sleep(10.25)
        elif mode=='overall-30s':
            peer.sendall(headers+body[:1])
            for i in range(5):time.sleep(5.01);peer.sendall(body[1+i:2+i])
        elif mode in ['get-body','reboot-busy','foreign']:
            peer.sendall(headers+body[:37])
        else:peer.sendall(headers+body)
        response=b''
        try:
            while True:
                chunk=peer.recv(4096)
                if not chunk:break
                response+=chunk
        except ssl.SSLEOFError:
            # The existing C3 static worker performs raw shutdown after its
            # complete chunked body; this is outside the typed edit close path.
            assert mode=='public' or 'response-oom' in mode
        if 'response-oom' in mode:assert not response;return
        expected=408 if mode in ['idle-10s','overall-30s'] else 409 if mode=='stale' else 503 if mode in ['reboot-busy','foreign','import-board-busy'] else 400 if mode in ['malformed','get-body','import-board-invalid'] else 404 if mode.startswith('private:') or mode=='head' else 303 if mode.startswith('import-') and 'upload' not in mode else 200
        assert response.startswith(f'HTTP/1.1 {expected} '.encode()),(mode,response)
        header,data=response.split(b'\r\n\r\n',1)
        assert not any(secret in response for secret in [b'OLD_PRIVATE',b'NEW_REQUEST_CANARY',b'IMPORT_REQUEST_CANARY'])
        if mode=='public':
            assert b'Transfer-Encoding: chunked' in header and data.endswith(b'0\r\n\r\n') and b'PUBLIC_PLAYLIST' in data
        else:
            n=int(next(line.split(b':',1)[1] for line in header.split(b'\r\n') if line.lower().startswith(b'content-length:')))
            assert len(data)==n,(mode,data,n)
        if mode=='info':
            meta=json.loads(data);assert meta['revision']==a.revision and len(meta['profiles'])==2 and 'password' not in data.decode()
        elif expected==200 and not mode.startswith('import-') and mode!='public':assert json.loads(data)=={'saved':True,'rebooting':True}


if __name__=='__main__':main()
