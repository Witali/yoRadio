"""Repeat the existing 610-second heavy fixtures on this exact quiet application."""
import runpy,sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
from common import require
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
kind=sys.argv[1];require(kind in ('flac','vorbis','opus'),'Unknown codec')
manifest=(Path('C:/Work/yoRadio/.worktree/esp32c3-idf-upgrade/.build/c3-reserve-soak-20261008/fixtures/manifest.json')
          if kind=='flac' else Path('.build/c3-production-qualification-20261014/ogg-fixtures/manifest.json'))
require(manifest.is_file(),'Existing stress fixture manifest is missing')
sys.argv=['local_sustained.py','--board','http://192.168.100.4','--host','192.168.100.253',
    '--firmware','firmware/development/esp32c3-idf61-raw-tail-quiet/app.bin',
    '--fixtures',str(manifest),'--fixture','stress-'+kind+'-48000-2ch-16bit-610s',
    '--seconds','600','--output','.build/c3-raw-tail-quiet-20261015/sustained/'+kind]
runpy.run_path('tools/esp32c3_tests/local_sustained.py',run_name='__main__')
