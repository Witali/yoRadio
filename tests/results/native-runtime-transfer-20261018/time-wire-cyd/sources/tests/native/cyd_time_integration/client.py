"""Independent HTTP/1.1 client; TLS requires a trusted CA and localhost SAN."""
import argparse
import json
import socket
import ssl
import time

def response(peer, pending=b''):
    while b'\r\n\r\n' not in pending:
        data=peer.recv(4096);assert data,'EOF before response';pending+=data
    head,pending=pending.split(b'\r\n\r\n',1);lines=head.split(b'\r\n')
    status=int(lines[0].split()[1]);headers={}
    for line in lines[1:]:
        key,value=line.split(b':',1);headers[key.lower()]=value.strip()
    size=int(headers[b'content-length'])
    while len(pending)<size:
        data=peer.recv(4096);assert data,'EOF in response';pending+=data
    return status,headers,pending[:size],pending[size:]

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,required=True)
    parser.add_argument('--mode',required=True);parser.add_argument('--ca',default='');args=parser.parse_args();mode=args.mode
    valid='utc_offset_minutes=345&sync_interval_minutes=15&server1=pool.ntp.org&server2='
    query=valid;method='POST';route='/api/native/time';body=b'';declared=0
    if mode.startswith('get-') or mode=='unavailable':method='GET';query=''
    if mode=='missing':query=valid.rsplit('&server2=',1)[0]
    elif mode=='duplicate':query+='&server1=evil.example'
    elif mode=='encoded-duplicate':query+='&server%31=evil.example'
    elif mode=='nul':query=query.replace('pool.ntp.org','pool%00.ntp.org')
    elif mode=='bad-percent':query=query.replace('pool.ntp.org','pool%GG.ntp.org')
    elif mode=='unknown':query+='&unexpected=1'
    elif mode=='numeric':query=query.replace('=345','=1e2')
    elif mode=='bounds':query=query.replace('=345','=855')
    elif mode=='host-limit':query=query.replace('pool.ntp.org','a'*35)
    elif mode=='get-query':query='unexpected=1'
    elif mode=='uri-limit':query='x'*520
    elif mode=='wrong-route':route+='/other';query='';method='GET'
    elif mode=='wrong-method':method='PUT'
    elif mode=='post-two':query+='time.nist.gov'
    if mode.startswith('body-'):
        method='GET' if mode=='body-get' else 'POST';query='' if method=='GET' else valid
        body=b'x';declared=1
        if mode in ('body-unread-large','body-slow'):declared=1024*1024;body=b'x'
    target=route+('?' + query if query else '')
    header=(f'{method} {target} HTTP/1.1\r\nHost: localhost\r\nContent-Length: {declared}\r\nConnection: keep-alive\r\n\r\n').encode()
    if mode=='body-post':assert len(header)%128!=0 # one complete buffered byte for the semantic purge control
    raw=socket.create_connection(('127.0.0.1',args.port),timeout=10);peer=raw
    if args.ca:
        context=ssl.create_default_context(cafile=args.ca);context.minimum_version=context.maximum_version=ssl.TLSVersion.TLSv1_2
        peer=context.wrap_socket(raw,server_hostname='localhost',suppress_ragged_eofs=False)
        assert context.verify_mode==ssl.CERT_REQUIRED and context.check_hostname and peer.getpeercert() and peer.version()=='TLSv1.2'
    with peer:
        started=time.monotonic()
        if mode=='body-slow':
            peer.sendall(header);time.sleep(.25);peer.sendall(body)
        else:peer.sendall(header+body)
        # The pinned SDK dispatches a nonempty request only after its first
        # body byte. Keep all remaining 1 MiB-1 bytes unsent in these cases.
        status,headers,data,pending=response(peer)
        expected=503 if mode=='unavailable' else 500 if mode=='commit-failure' else 414 if mode=='uri-limit' else 404 if mode=='wrong-route' else 405 if mode=='wrong-method' else 400 if mode not in ('get-null','get-valid','post-pending','post-two') else 200
        assert status==expected,(mode,status,data)
        if expected not in (414,404,405):
            assert headers[b'content-type']==b'application/json; charset=utf-8' and headers[b'cache-control']==b'no-store'
            value=json.loads(data)
            if mode=='get-null':assert value['clock_valid'] is False and value['utc_epoch'] is None and value['local_time'] is None
            elif mode=='get-valid':assert value['clock_valid'] is True and value['local_time']=='2023-12-31T23:30:00' and value['last_apply_error']==263
            elif mode in ('post-pending','post-two'):assert value=={'saved':True,'application_pending':True}
            else:assert isinstance(value['error'],str)
        if mode.startswith('body-'):
            assert headers[b'connection']==b'close' and time.monotonic()-started<2
        if mode=='post-pending':
            peer.sendall(b'GET /api/native/time HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n')
            status,headers,data,pending=response(peer,pending);value=json.loads(data)
            assert status==200 and value['utc_offset_minutes']==345 and value['sync_interval_minutes']==15 and value['server2']==''
            assert value['desired_revision']>value['applied_revision'] and value['synchronized_this_boot'] is False
        assert not pending
        try:
            assert peer.recv(1)==b'' # TLS requires actual close_notify, not a ragged EOF
        except ConnectionResetError:
            # Linux may reset a raw TCP socket with unread kernel input after
            # the complete error response. TLS must still deliver close_notify.
            assert not args.ca and (mode.startswith('body-') or mode=='uri-limit')

if __name__=='__main__':main()
