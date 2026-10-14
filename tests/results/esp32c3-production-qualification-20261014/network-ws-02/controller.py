import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import Board,require
b=Board('http://192.168.100.4');require(not b.status()['audio'],'Board must initially be stopped')
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
sys.argv=['quiet_acceptance.py','--board',b.origin,'--host','192.168.100.253','--firmware','firmware/development/esp32c3-idf61-production-20261013/app.bin','--suite','network','--suite','websocket','--output','.build/c3-production-qualification-20261014/network-ws-02']
runpy.run_path('tools/esp32c3_tests/quiet_acceptance.py',run_name='__main__')
