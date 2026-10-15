"""Use measured 1 KiB/16 KiB TLS records at real-time AAC-LC pacing."""
import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
require(sys.argv[1]=='records','Unknown controlled test')
base=Path('.build/c3-confirm-tls-lab-20261015')
sys.argv=['quiet_tls_records.py','--board','http://192.168.100.4','--host','192.168.100.253',
    '--firmware','firmware/development/esp32c3-idf61-confirm-tls-lab/app.bin',
    '--ca',str(base/'trust/ca.pem'),'--cert',str(base/'trust/server.pem'),'--key',str(base/'trust/server.key'),
    '--output',str(base/'controlled-tls/records'),'--case','lc-44100-stereo','--seconds','75',
    '--mode','small','--mode','large','--mode','grow','--mode','alternate']
runpy.run_path('tools/esp32c3_tests/quiet_tls_records.py',run_name='__main__')
