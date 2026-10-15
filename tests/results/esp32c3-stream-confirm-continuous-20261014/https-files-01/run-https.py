"""Exact-image public HTTPS regression with independent format references."""
import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
suite=sys.argv[1]
require(suite in ('public-files','public-radio'),'Unknown campaign')
base='.build/c3-continuous-confirm-20261014'
args=['--board','http://192.168.100.4',
      '--firmware','firmware/development/esp32c3-idf61-continuous-confirm/app.bin',
      '--output',base+'/https/'+suite]
if suite=='public-files':
    script='public_file_acceptance.py'
    args+=['--references',base+'/public-references/references.json']
else:
    script='quiet_acceptance.py'
    args+=['--host','192.168.100.253','--suite','public','--seconds','60',
           '--aac-reference-command','C:/Work/yoRadio/.worktree/esp32c3-idf-upgrade/.build/c3-prefill1000-public-20261010/faad-reference-command.json']
sys.argv=[script,*args]
runpy.run_path('tools/esp32c3_tests/'+script,run_name='__main__')
