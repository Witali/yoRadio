"""Mixed-family fixtures preserve bytes and per-segment pacing metadata."""
from pathlib import Path
import sys
from urllib.request import urlopen
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audio_test_server.fixtures import load_fixtures, SEQUENCES, sha
from audio_test_server.server import Server

specs=load_fixtures()
for name in ('mp3-he-mp3','aac-mp3-hev2'):
    spec=specs[name];sequence=SEQUENCES[name]
    assert spec['codec']=='auto' and spec['mime'] is None
    assert spec['sequence']==sequence and spec['segments']==[specs[n] for n in sequence]
    expected=b''.join(specs[n]['data'] for n in sequence)
    assert spec['data']==expected and spec['sha256']==sha(expected)
    assert spec['seconds']==sum(specs[n]['seconds'] for n in sequence)
    with Server('127.0.0.1',0,{name:spec},unpaced_files=True) as server:
        with urlopen(f'http://127.0.0.1:{server.http.server_port}/file/{name}',timeout=5) as response:
            assert response.headers.get('Content-Type') is None
            assert int(response.headers['Content-Length'])==len(expected)
            assert response.read()==expected
    assert server.events[0]['complete'] and server.events[0]['sent']==len(expected)
for name in ('changing','implicit-sbr'):
    assert specs[name]['codec']=='aac' and specs[name]['mime']=='audio/aac'
print('PASS mixed MP3/AAC fixtures: exact HTTP body/length, AUTO hint, per-segment duration, old AAC sequences unchanged')
