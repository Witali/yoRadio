import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
import common
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
suite=sys.argv[1]
common.require(suite in ('transitions','http'),'Unknown campaign')
sys.argv=['quiet_acceptance.py','--board','http://192.168.100.4','--host','192.168.100.253',
    '--firmware','firmware/development/esp32c3-idf61-continuous-confirm/app.bin',
    '--suite',suite,'--output','.build/c3-continuous-confirm-20261014/physical/'+suite]
runpy.run_path('tools/esp32c3_tests/quiet_acceptance.py',run_name='__main__')
