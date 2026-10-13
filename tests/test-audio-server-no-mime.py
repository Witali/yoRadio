"""Missing Content-Type does not change fixture bytes or the default behavior."""
from pathlib import Path
import sys
from urllib.request import urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audio_test_server.server import Server

for mime in (None,'audio/aac'):
    data=b'\xff\xf1\x4c\x80\x01\x9f\xfc'+bytes(range(128))
    spec=dict(data=data,seconds=.01,codec='aac',mime=mime)
    with Server('127.0.0.1',0,{'sample':spec},unpaced_files=True,
                delivery_pauses=[(1,.01),(3,.01)]) as server:
        with urlopen(f'http://127.0.0.1:{server.http.server_port}/file/sample',timeout=3) as response:
            assert response.headers.get('Content-Type')==mime
            assert response.read()==data
    assert server.events[0]['sent']==len(data) and server.events[0]['complete']
print('PASS: missing/default MIME, fragmented delivery and exact bytes')
