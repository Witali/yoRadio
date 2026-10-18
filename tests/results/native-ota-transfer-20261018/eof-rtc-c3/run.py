"""Capture existing EOF/RTC regressions at the frozen C3 maintenance checkpoint."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
MAIN=ROOT/'idf/esp32c3-oled-native/main'
files=[Path(__file__),ROOT/'tests/run-esp32c3-eof.py',ROOT/'tests/run-esp32c3-deep-sleep-clock.py',
       ROOT/'tests/native/esp32c3_eof_test.c',ROOT/'tests/native/esp32c3_deep_sleep_clock_test.c',
       ROOT/'tests/native/esp32c3_sleep_mock.h',MAIN/'audio_service.c',MAIN/'native_state.c',
       MAIN/'rtc_wake_stub_clock.c',*sorted(MAIN.glob('*.h')),
       *sorted((ROOT/'idf/components/native_stream/include').glob('*.h')),
       ROOT/'tools/codec_benchmark/run_output_dma_host.py']
hashes={f.relative_to(ROOT).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in files}
for f in files:
    dest=OUT/'sources'/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(f.read_bytes())
rtc=ROOT/'tests/run-esp32c3-deep-sleep-clock.py'
commands={'eof':[sys.executable,str(ROOT/'tests/run-esp32c3-eof.py')],
          'rtc':['wsl.exe','--exec','python3','/mnt/c'+rtc.as_posix()[2:]]}
report={'passed':False,'physical_hardware':False,'source_sha256':hashes,'commands':commands,'results':{}}
for name,command in commands.items():
    result=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
    (OUT/(name+'.log')).write_bytes(result.stdout)
    report['results'][name]={'exit_code':result.returncode,'output':result.stdout.decode(errors='replace').strip()}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(result.stdout.decode(errors='replace'),end='')
    if result.returncode:raise SystemExit(result.returncode)
report['source_files_still_match_snapshot']=all(hashlib.sha256(f.read_bytes()).hexdigest()==hashes[f.relative_to(ROOT).as_posix()] for f in files)
assert report['source_files_still_match_snapshot']
report['passed']=True
(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
