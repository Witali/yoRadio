import argparse, hashlib, json, struct, subprocess, sys
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--version',required=True)
p.add_argument('--codec',choices=['mp3','flac','vorbis','opus'])
a=p.parse_args()
b=Path(f'idf/esp32c3-oled-native/build-idf-{a.version}-qemu-aac').resolve()
o=Path(f'.build/idf-upgrade/qemu-{a.version}-aac'+('-'+a.codec if a.codec else '')).resolve()
o.mkdir(exist_ok=False)
flash=o/'flash.bin'
cmd=[sys.executable,'-m','esptool','--chip','esp32c3','merge-bin','-o',str(flash),
 '--flash-mode','dio','--flash-freq','80m','--flash-size','4MB','--pad-to-size','4MB']
for offset,name in [('0x0','bootloader/bootloader.bin'),('0x8000','partition_table/partition-table.bin'),
 ('0xe000','ota_data_initial.bin'),('0x10000','yoradio_esp32c3_oled_native.bin'),('0x3b0000','spiffs.bin')]:
 cmd += [offset,str(b/name)]
(o/'merge.log').write_bytes(subprocess.check_output(cmd,stderr=subprocess.STDOUT))
fixture=None
if a.codec:
 folder=Path('tests/fixtures/esp32c3_calibration')
 fixture=next(f for f in json.loads((folder/'manifest.json').read_text())['fixtures'] if f['codec']==a.codec)
 data=(folder/fixture['file']).read_bytes()
 assert len(data)==fixture['bytes'] and hashlib.sha256(data).hexdigest()==fixture['sha256']
 assert len(data)+16<=0x1d0000
 with flash.open('r+b') as f:
  f.seek(0x1e0000);f.write(struct.pack('<4I',0x5143414c,fixture['id'],len(data),0)+data)
guest=subprocess.check_output(['wsl.exe','--exec','wslpath','-a',str(o)],text=True).strip()
cmd=['wsl.exe','--exec','timeout','--kill-after=2','600',
 '/mnt/c/Work/yoRadio/.worktree/esp32c3-stream-format/.build/qemu-cache-host/qemu-system-riscv32',
 '-M','esp32c3,audiodev=audio0','-nographic','-no-reboot','-snapshot',
 '-audiodev',f'wav,id=audio0,path={guest}/audio.wav,out.frequency=48000',
 '-icount','shift=0,align=off,sleep=off','-L','/mnt/c/Work/QEMU-ESP32/share/qemu',
 '-drive',f'file={guest}/flash.bin,if=mtd,format=raw']
with (o/'qemu.log').open('wb') as f:
 result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,timeout=620)
log=(o/'qemu.log').read_text(errors='replace')
markers=['QEMU_SMOKE_PASS','QEMU_OLED_PASS','QEMU_AUDIO_PASS',
 'QEMU_AAC_FORMAT_PASS','QEMU_AAC_WORK_PASS','QEMU_AAC_CAL_PASS']
if a.codec:markers.append('QEMU_CODEC_CAL_PASS codec='+a.codec)
checks={m:m in log for m in markers}
checks['audio_file']=(o/'audio.wav').exists() and (o/'audio.wav').stat().st_size>44
report={'idf':a.version,'returncode':result.returncode,'checks':checks,
 'passed':result.returncode==0 and all(checks.values()),'command':cmd,
 'app_sha256':hashlib.sha256((b/'yoradio_esp32c3_oled_native.bin').read_bytes()).hexdigest(),
 'sdkconfig_sha256':hashlib.sha256((b/'sdkconfig').read_bytes()).hexdigest(),
 'fixture':fixture,
 'measurements':[line for line in log.splitlines() if 'QEMU_AAC_' in line or 'QEMU_CODEC_' in line]}
(o/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'passed':report['passed'],'checks':checks,'returncode':result.returncode}),flush=True)
sys.exit(0 if report['passed'] else 1)
