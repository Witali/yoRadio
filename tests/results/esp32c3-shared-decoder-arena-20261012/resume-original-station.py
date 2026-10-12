"""Restore the initial campaign's playing state using its unchanged playlist selection."""
import json,sys,time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require
from production_health import HealthBoard,check_health
root=Path('.build/c3-decoder-arena')
initial=json.loads((root/'physical-96b/initial.json').read_text())
b=Board('http://192.168.100.4')
require(b.info()['app_elf_sha256']==initial['restore']['app_elf_sha256'],'Wrong final firmware')
require(initial['original']['audio'],'Original playing state was not enabled')
with b.websocket() as ws:
    ws.send('getindex')
    current=None
    deadline=time.perf_counter()+5
    while time.perf_counter()<deadline:
        message=json.loads(ws.recv(timeout=5))
        if 'current' in message: current=message['current'];break
    require(type(current) is int and current>0,'Missing saved playlist index')
    ws.send('play='+str(current))
    time.sleep(1)
b=HealthBoard(b.origin)
states=[]
for _ in range(5):
    time.sleep(4);states.append(b.status())
require(all(s['audio'] and s['pcm_sample_rate']>0 for s in states[-3:]),'Final station did not resume')
(root/'final-state.json').write_text(json.dumps(dict(identity=b.info(),
    original_playing_state_restored=True,saved_playlist_selection_resumed=True,
    states=states,health=check_health(b.health_samples)),indent=2)+'\n')
print('Verified original application and resumed saved playlist station')
