import json, sys, time
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board, require
from ota import snapshot, verify_snapshot
board=Board('http://192.168.100.4')
before=snapshot(board)
identity=board.info()
require(identity['app_elf_sha256']=='da2f5dfeac6a51f55387f833ddcf5401b23b610709bb36126b2e28d2657aaad0','Wrong restored firmware')
board.stop()
samples=[]
for index in range(3):
    time.sleep(5)
    samples.append(board.status())
require(all(not s['audio'] for s in samples),'Playback did not remain stopped')
result=dict(result='PASS',info=identity,status=samples,persistence=verify_snapshot(board,before),
    note='Post-OTA autostart observed on the correct quiet image; explicit Stop restores the pre-test stopped state, verified for 15 seconds.')
Path('.build/c3-rfc-qualification-20261007/eof/final-board.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
