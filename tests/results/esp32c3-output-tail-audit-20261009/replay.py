"""Reproduce the recorded baseline bug with frozen C; never accesses the board."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
output=args.output.resolve()
assert not output.is_relative_to(ROOT), 'Keep archived evidence unchanged'
output.mkdir(parents=True,exist_ok=False)
index=json.loads((ROOT/'index.json').read_text())
for relative,expected in index['files'].items():
    blob=(ROOT/relative).read_bytes()
    assert hashlib.sha256(blob).hexdigest()==expected['sha256']
def host(path):
    text=Path(path).resolve().as_posix()
    return '/mnt/'+text[0].lower()+text[2:] if sys.platform=='win32' else text
def run(args):
    return subprocess.check_output((['wsl.exe','--exec'] if sys.platform=='win32' else [])+args,stderr=subprocess.STDOUT)
binary=output/'probe'
command=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Wno-unused-function',
         '-Wno-unused-variable','-fsanitize=address,undefined','-fno-omit-frame-pointer',
         '-fno-pie','-no-pie','-I'+host(ROOT/'sources/tests/native/output_dma'),
         host(ROOT/'unit.c'),'-o',host(binary)]
(output/'build.log').write_bytes(run(command))
result=run(['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1',
            'UBSAN_OPTIONS=halt_on_error=1',host(binary),host(output/'probe.pcm')])
(output/'result.log').write_bytes(result)
assert result==(ROOT/'result.log').read_bytes()
assert (output/'probe.pcm').read_bytes()==(ROOT/'probe.pcm').read_bytes()
print(result.decode())
