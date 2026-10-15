import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
import common
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
sys.argv=['local_sustained.py','--board','http://192.168.100.4','--host','192.168.100.253','--firmware','firmware/development/esp32c3-idf61-production-20261013/app.bin','--fixtures','.build/c3-production-qualification-20261014/ogg-fixtures/manifest.json','--fixture','stress-opus-48000-2ch-16bit-610s','--seconds','600','--output','.build/c3-production-qualification-20261014/opus-600-01']
runpy.run_path('tools/esp32c3_tests/local_sustained.py',run_name='__main__')
