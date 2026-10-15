import sys
from pathlib import Path
sys.path.insert(0,'tools/esp32c3_tests')
import public_file_acceptance as runner
import audio_test_server.fixtures as fixture_module
fixture_module.ROOT=Path('C:/Work/yoRadio')
suite=sys.argv[1]
assert suite in ('flac-1','flac-2','flac-3')
original=runner.load_references
def only_flac(path):
    manifest=original(path)
    manifest['sources']={'flac':manifest['sources']['flac']}
    return manifest
runner.load_references=only_flac
sys.argv=['public_file_acceptance.py','--board','http://192.168.100.4',
    '--firmware','firmware/development/esp32c3-idf61-flac-output-diagnostic/app.bin',
    '--references','.build/c3-input-tail-quiet-20261015/public-references/references.json',
    '--output','.build/c3-flac-output-diagnostic-20261015/physical/'+suite]
raise SystemExit(runner.main())
