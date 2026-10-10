import argparse, hashlib, json, platform, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--version',required=True);a=p.parse_args()
deps=Path('C:/Work/yoRadio/.idf')
qemu=Path('C:/Work/yoRadio/.worktree/esp32c3-stream-format/.build/qemu-cache-host/qemu-system-riscv32')
gcc=next((deps/f'tools-v{a.version}').glob('tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-gcc.exe'))
def output(cmd):return subprocess.check_output(cmd,text=True).strip()
r={'recorded_utc':datetime.now(timezone.utc).isoformat(),'idf':a.version,
 'sdk_commit':output(['git','-C',str(deps/f'v{a.version}'),'rev-parse','HEAD']),
 'codec_commit':output(['git','-C',str(deps/'esp-adf-libs'),'rev-parse','HEAD']),
 'python':sys.version,'os':platform.platform(),
 'compiler':output([str(gcc),'--version']).splitlines()[0],
 'node':output(['C:/Program Files/nodejs/node.exe','--version']),
 'qemu_version':'9.2.2','qemu_sha256':hashlib.sha256(qemu.read_bytes()).hexdigest(),
 'ffmpeg':output(['ffmpeg','-version']).splitlines()[0]}
Path(f'.build/idf-upgrade/environment-{a.version}.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r))
