import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
b=Board('http://192.168.100.4');require(not b.status()['audio'],'Expected idle board')
sys.argv=['quiet_acceptance.py','--board',b.origin,'--host','192.168.100.253',
          '--firmware','firmware/development/esp32c3-idf61-production-20261013/app.bin',
          '--suite','public','--public-case','groovesalad-128-aac','--seconds','120',
          '--aac-reference-command','C:/Work/yoRadio/.worktree/esp32c3-idf-upgrade/.build/c3-prefill1000-public-20261010/faad-reference-command.json',
          '--output','.build/c3-aac-pause-ab-20261014/baseline-public-120']
runpy.run_path('tools/esp32c3_tests/quiet_acceptance.py',run_name='__main__')
