import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
import common
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
sys.argv=['local_sustained.py','--board','http://192.168.100.4','--host','192.168.100.253','--firmware','firmware/development/esp32c3-idf61-production-20261013/app.bin','--fixtures','C:/Work/yoRadio/.worktree/esp32c3-idf-upgrade/.build/c3-reserve-soak-20261008/fixtures/manifest.json','--fixture','stress-flac-48000-2ch-16bit-610s','--seconds','600','--output','.build/c3-production-qualification-20261014/flac-600-01']
runpy.run_path('tools/esp32c3_tests/local_sustained.py',run_name='__main__')
