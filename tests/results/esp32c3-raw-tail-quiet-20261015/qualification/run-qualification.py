import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
import common
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
suite=sys.argv[1]
common.require(suite in ('public-files','http','transitions','network','websocket','ota'),'Unknown campaign')
base=Path('.build/c3-raw-tail-quiet-20261015')
artifact='firmware/development/esp32c3-idf61-raw-tail-quiet/app.bin'
out=base/'qualification'/suite
if suite=='public-files':
    sys.argv=['public_file_acceptance.py','--board','http://192.168.100.4',
        '--firmware',artifact,'--references','.build/c3-input-tail-quiet-20261015/public-references/references.json','--output',str(out)]
    runpy.run_path('tools/esp32c3_tests/public_file_acceptance.py',run_name='__main__')
elif suite in ('http','transitions','network','websocket'):
    sys.argv=['quiet_acceptance.py','--board','http://192.168.100.4','--host','192.168.100.253',
        '--firmware',artifact,'--suite',suite,'--output',str(out)]
    runpy.run_path('tools/esp32c3_tests/quiet_acceptance.py',run_name='__main__')
else:
    from audio_test_server.server import Server
    sys.argv=['ota.py','--board','http://192.168.100.4','--firmware',artifact,
        '--suite','negative','--suite','roundtrip','--suite','while-playing','--suite','slow',
        '--play-url','http://192.168.100.253:8772/stream/lc-48000-stereo',
        '--play-fixture','lc-48000-stereo','--output',str(out/'report.json')]
    with Server('192.168.100.253',8772,common.fixtures(),unpaced_files=True,delivery_stats=True,pacing_ratio=1.0):
        runpy.run_path('tools/esp32c3_tests/ota.py',run_name='__main__')
