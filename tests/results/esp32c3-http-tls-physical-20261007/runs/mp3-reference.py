import json,time,ssl
from urllib.request import Request,urlopen
from pathlib import Path
url=json.loads(Path('tools/esp32c3_tests/public_streams.json').read_text())['streams']['groovesalad-256-mp3']
r=dict(purpose='Same public MP3 source with verified TLS, same request metadata, no audio retained',samples=[])
start=time.monotonic();r['started_at']=start
try:
    with urlopen(Request(url,headers={'User-Agent':'yoRadio-native/1','Icy-MetaData':'1','Connection':'close'}),timeout=10,context=ssl.create_default_context()) as response:
        r['headers']={k:response.headers.get(k) for k in ('Content-Length','Transfer-Encoding','Connection','Content-Type','icy-metaint')}
        total=0;last=start
        while time.monotonic()-start<60:
            data=response.read(1024)
            if not data:r['early_eof']=True;break
            total+=len(data);now=time.monotonic()
            if now-last>=1:r['samples'].append(dict(seconds=now-start,bytes=total));last=now
        r.update(bytes=total,seconds=time.monotonic()-start,early_eof=r.get('early_eof',False))
except Exception as e:r['error_type']=type(e).__name__
Path('.build/c3-rfc-qualification-20261007/mp3-reference.json').write_text(json.dumps(r,indent=2)+'\n')
print({k:v for k,v in r.items() if k!='samples'},flush=True)
