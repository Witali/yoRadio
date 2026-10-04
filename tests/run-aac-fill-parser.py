"""Build checked FIL parsing with ASan/UBSan and buffers without input padding."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_faad_history_comparison import host_command,host_path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=ROOT/'.build/aac-fill-host')
args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
main=ROOT/'idf/esp32c3-oled-native/main'
sources=[main/'aac_fill_parser.c',main/'aac_fill_parser.h',ROOT/'tests/native/aac_fill_parser_test.c']
exe=out/'aac-fill-test'
command=['gcc','-std=c11','-O3','-g','-Wall','-Wextra','-Werror',
         '-fsanitize=address,undefined','-fno-sanitize-recover=all',
         '-I'+host_path(main),host_path(sources[0]),host_path(sources[2]),'-o',host_path(exe)]
build=subprocess.run(host_command(command),capture_output=True)
(out/'build.log').write_bytes(build.stdout+build.stderr);build.check_returncode()
result=subprocess.run(host_command([host_path(exe)]),capture_output=True)
(out/'test.log').write_bytes(result.stdout+result.stderr);result.check_returncode()
match=re.fullmatch(rb'AAC_FIL_HOST_PASS valid=69376 truncated=(\d+) invalid_state=4 padding=0\n',result.stdout)
if not match or int(match[1])<300000 or result.stderr:raise ValueError('Incomplete/unsafe FIL result')
record=dict(command=command,exit_code=result.returncode,stdout=result.stdout.decode(),
            valid_cases=69376,truncated_cases=int(match[1]),invalid_state_cases=4,
            hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
(out/'result.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print(result.stdout.decode(),end='')
