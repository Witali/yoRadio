import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require
b=Board('http://192.168.100.4');require(not b.status()['audio'],'Board must initially be stopped')
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
sys.argv=['quiet_acceptance.py','--board',b.origin,'--host','192.168.100.253','--firmware','firmware/development/esp32c3-idf61-production-20261013/app.bin','--suite','public','--public-case','groovesalad-32-aac','--seconds','600','--aac-reference-command','C:/Work/yoRadio/.worktree/esp32c3-idf-upgrade/.build/c3-prefill1000-public-20261010/faad-reference-command.json','--output','.build/c3-production-qualification-20261014/https-he-600-01']
runpy.run_path('tools/esp32c3_tests/quiet_acceptance.py',run_name='__main__')
