"""Diagnose bounded TLS delivery gaps on the exact record-test image."""
import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
require(sys.argv[1]=='pauses','Unknown pause campaign')
trust=Path('.build/c3-confirm-tls-lab-20261015/trust')
sys.argv=['local_sustained.py','--board','http://192.168.100.4','--host','192.168.100.253',
    '--firmware','firmware/development/esp32c3-idf61-aac-prefill2-lab/app.bin',
    '--fixtures','.build/c3-aac-pause-ab-20261014/fixtures/manifest.json','--fixture','aac-lc-44100-128k',
    '--ca',str(trust/'ca.pem'),'--cert',str(trust/'server.pem'),'--key',str(trust/'server.key'),
    '--output','.build/c3-aac-prefill2-20261015/tls-pauses/pauses',
    '--seconds','90','--send-buffer-bytes','4096',
    '--delivery-pause','414279:0.5','--delivery-pause','745703:1.0','--delivery-pause','1077126:1.5']
runpy.run_path('tools/esp32c3_tests/local_sustained.py',run_name='__main__')
