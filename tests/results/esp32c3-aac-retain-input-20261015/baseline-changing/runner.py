import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
trust=Path('.build/c3-confirm-tls-lab-20261015/trust')
sys.argv=['stream_probe.py','--board','http://192.168.100.4','--host','192.168.100.253',
 '--candidate','firmware/development/esp32c3-idf61-confirm-tls-lab/app.bin',
 '--restore','firmware/development/esp32c3-idf61-production-20261013/app.bin',
 '--output','.build/c3-aac-retain-input-20261015/baseline-changing',
 '--tls-ca',str(trust/'ca.pem'),'--tls-cert',str(trust/'server.pem'),'--tls-key',str(trust/'server.key'),
 '--transitions','--codec-transitions',
 '--case-filter','changing']
runpy.run_path('tools/esp32c3_tests/stream_probe.py',run_name='__main__')
