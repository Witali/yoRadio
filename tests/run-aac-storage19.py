#!/usr/bin/env python3
"""Compile/run the real PC19 header with a wide integer oracle under ASan/UBSan."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_faad_history_comparison import host_path,host_command

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=ROOT/'.build/aac-storage19-host')
args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
exe=out/'arithmetic';source=ROOT/'tests/native/aac_storage19_test.c'
header=ROOT/'idf/esp32c3-oled-native/main/packed_complex_storage.h'
cmd=['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-Wno-misleading-indentation',
     '-fsanitize=address,undefined','-fno-sanitize-recover=all',
     '-I'+host_path(header.parent),host_path(source),'-o',host_path(exe)]
result=subprocess.run(host_command(cmd),capture_output=True)
(out/'build.log').write_bytes(result.stdout+result.stderr);result.check_returncode()
result=subprocess.run(host_command([host_path(exe)]),capture_output=True)
(out/'test.log').write_bytes(result.stdout+result.stderr);result.check_returncode()
if not result.stdout.startswith(b'STORAGE19_ARITHMETIC_PASS ') or result.stderr:raise ValueError('Incomplete/unsafe arithmetic result')
record=dict(command=cmd,exit_code=result.returncode,stdout=result.stdout.decode(),
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
            (source,header,header.parent/'packed_complex16_fast.h',header.parent/'packed_complex16.h')})
(out/'result.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
print(result.stdout.decode(),end='')
