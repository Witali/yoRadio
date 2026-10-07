import argparse
from pathlib import Path
import subprocess
import sys

p=argparse.ArgumentParser()
p.add_argument('--version', required=True)
a=p.parse_args()
root=Path('.build/idf-upgrade')
qemu='/mnt/c/Work/yoRadio/.worktree/esp32c3-stream-format/.build/qemu-cache-host/qemu-system-riscv32'
bios='/mnt/c/Work/QEMU-ESP32/share/qemu'
base=['--build',f'idf/esp32c3-oled-native/build-idf-{a.version}-qemu-vorbis',
      '--deps','C:/Work/yoRadio/.idf','--qemu',qemu,'--bios',bios]
raw=root/f'qemu-{a.version}-vorbis-raw'
def run(name, script, args):
    print('START',name,flush=True)
    with (root/f'qemu-{a.version}-{name}.log').open('xb') as log:
        result=subprocess.run([sys.executable,'-X','utf8',script,*map(str,args)],
                              stdout=log,stderr=subprocess.STDOUT,timeout=7200)
    print('END',name,result.returncode,flush=True)
    if result.returncode: raise SystemExit('QEMU phase failed: '+name)
run('raw-run','tools/codec_benchmark/run_vorbis_output.py',base+
    ['--raw-reference','--reference',root/'qemu-6.0.3-vorbis-raw','--output',raw])
run('output-run','tools/codec_benchmark/run_vorbis_output.py',base+
    ['--reference',raw,'--output',root/f'qemu-{a.version}-vorbis-output'])
run('lifecycle-run','tools/codec_benchmark/run_vorbis_lifecycle.py',base+
    ['--wsl','--cycles','100','--pcm-reference',raw,'--output',root/f'qemu-{a.version}-vorbis-lifecycle'])
for codec in (None,'mp3','flac','vorbis','opus'):
    run('cal-'+(codec or 'aac'),'.build/idf-upgrade/qemu-aac.py',
        ['--version',a.version]+(['--codec',codec] if codec else []))
print('QEMU_COMPLETE',flush=True)
