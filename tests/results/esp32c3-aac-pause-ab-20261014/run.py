import json,runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
import common  # Adds the shared tools directory to the import path.
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
name,firmware=sys.argv[1:]
base=Path('.build/c3-aac-pause-ab-20261014')
args=['local_sustained.py','--board','http://192.168.100.4','--host','192.168.100.253',
      '--firmware',firmware,'--fixtures',str(base/'fixtures/manifest.json'),
      '--fixture','aac-lc-44100-128k','--seconds','80','--send-buffer-bytes','4096',
      '--output',str(base/name)]
for offset,seconds in json.loads((base/'fixtures/schedule.json').read_text()):
    args+=['--delivery-pause',f'{offset}:{seconds}']
sys.argv=args
runpy.run_path('tools/esp32c3_tests/local_sustained.py',run_name='__main__')
