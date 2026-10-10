"""Confirm that the output-task regression rejects the original staged task."""
from pathlib import Path
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/codec_benchmark/run_output_dma_host.py').is_file())
sys.path.insert(0,str(REPO/'tools/codec_benchmark'))
from run_output_dma_host import host,run
OUT=ROOT/'negative-control';OUT.mkdir(exist_ok=False)
original=(REPO/'idf/esp32c3-oled-native/main/audio_service.c').read_text()
candidate=(ROOT/'candidate/idf/esp32c3-oled-native/main/audio_service.c').read_text()
def task(text):
    first=text.index('static void output_task(')
    return text[first:text.index('\n}',first)+2]
unit=(ROOT/'candidate-tests-task2/test.c').read_text()
assert unit.count(task(candidate))==1
unit=unit.replace(task(candidate),task(original))
(OUT/'test.c').write_text(unit)
binary=OUT/'baseline'
(OUT/'build.log').write_bytes(run(['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror',
    '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',
    host(OUT/'test.c'),'-o',host(binary)]))
command=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+[
    'env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1',host(binary)]
result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(OUT/'result.log').write_bytes(result.stdout)
assert result.returncode!=0 and b'expected=CWRFER actual=CWRER' in result.stdout
(OUT/'report.json').write_text(json.dumps(dict(result='EXPECTED REJECTION',returncode=result.returncode,
    reason='Original staged output_task does not call flush before publishing EOF',
    output=result.stdout.decode()),indent=2)+'\n')
print('PASS negative control: original staged output_task rejected for missing EOF flush')
