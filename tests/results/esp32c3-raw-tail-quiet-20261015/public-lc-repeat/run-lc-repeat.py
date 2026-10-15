"""Public HTTPS profiles on the exact corrected quiet image; bounded 10-min heavy run."""
import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
suite=sys.argv[1];require(suite == 'aac-lc','Unknown suite')
base=Path('.build/c3-raw-tail-quiet-20261015')
reference=Path('C:/Work/yoRadio/.worktree/esp32c3-idf-upgrade/.build/c3-prefill1000-public-20261010/faad-reference-command.json')
require(reference.is_file(),'Independent AAC reference command unavailable')
names=['groovesalad-128-aac']
sys.argv=['quiet_acceptance.py','--board','http://192.168.100.4','--host','192.168.100.253',
    '--firmware','firmware/development/esp32c3-idf61-raw-tail-quiet/app.bin',
    '--output',str(base/'https-lc-repeat'/suite),'--suite','public',
    '--seconds','600','--aac-reference-command',str(reference)]
for name in names:sys.argv+=['--public-case',name]
runpy.run_path('tools/esp32c3_tests/quiet_acceptance.py',run_name='__main__')
