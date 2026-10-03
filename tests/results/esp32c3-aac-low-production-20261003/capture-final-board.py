from datetime import datetime,timezone
import json,sys,time
from pathlib import Path
root=Path.cwd()
sys.path.insert(0,str(root/'tools/esp32c3_tests'))
from common import Board,require
board=Board('http://192.168.100.4')
expected=json.loads((root/'firmware/development/esp32c3-aac-low-workspace/manifest.json').read_text())['image']
info=board.info()
require(info['app_elf_sha256']==expected['app_elf_sha256'],'Unexpected final firmware')
deadline=time.monotonic()+25
status=board.status()
while not status.get('audio') and time.monotonic()<deadline:
    time.sleep(1)
    status=board.status()
result=dict(created_utc=datetime.now(timezone.utc).isoformat(),board=info,status=status)
(root/'.build/aac-low-production/final-board.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
require(status.get('audio'),'Saved station did not resume')
print('Verified target firmware and resumed saved station')
