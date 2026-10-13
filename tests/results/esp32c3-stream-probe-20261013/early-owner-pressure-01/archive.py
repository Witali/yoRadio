from pathlib import Path
import gzip, hashlib, json, shutil, subprocess

root=Path.cwd()
source=root/'.build/early-owner-real-pressure-ab-01'
build=root/'idf/esp32c3-oled-native/build-idf-6.1-head9a97-qemu'
dest=root/'tests/results/esp32c3-stream-probe-20261013/early-owner-pressure-01'
dest.mkdir(parents=True,exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,value):(dest/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
report=json.loads((source/'result.json').read_text())
assert report['faults_pass'] and report['early_owner_pressure']['heap_restored']
assert sha(source/'qemu.log')==report['provenance']['qemu_log_sha256']
assert sha(build/'sdkconfig')==report['provenance']['sdkconfig_sha256']
assert sha(build/'yoradio_esp32c3_oled_native.elf')==report['provenance']['elf_sha256']
(dest/'.gitattributes').write_text('* -text\n')
(dest/'qemu.log.gz').write_bytes(gzip.compress((source/'qemu.log').read_bytes(),mtime=0))
shutil.copyfile(source/'result.json',dest/'result.json')
shutil.copyfile(build/'sdkconfig',dest/'sdkconfig')
for rel in (
 'idf/esp32c3-oled-native/main/aac_compact_owner.c',
 'idf/esp32c3-oled-native/main/native_aac_decoder.c',
 'idf/esp32c3-oled-native/main/qemu_aac_faults.c',
 'tests/test-aac-faults.py','tests/run-aac-compact-reserve.py',
 'tools/codec_benchmark/run_aac_faults.py','tools/codec_benchmark/run_aac_bfp16.py',
 'tools/codec_benchmark/run_aac_metadata.py'):
 target=dest/'sources'/rel;target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(root/rel,target)
host=root/'.build/aac-compact-reserve-host'
for name in ('report.json','run.log','adapter-run.log','build.log','adapter-build.log'):
 target=dest/'host'/name;target.parent.mkdir(exist_ok=True);shutil.copyfile(host/name,target)
save('summary.json',dict(passed=True,physical_test=False,production_qualified=False,
 base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 pressure_cases=42,lc_success_control=13,lc_success_early=13,pressure_recovery_frames=630,
 late_injected_oom_cases=4,malformed_cases=4,
 scope='Real RV32 AAC allocator/DSP in QEMU. Same binary with test-only early-preparation bypass for control. Pressure removed before HEv2 recovery. No network/TLS/timing or broad memory-minimum claim.'))
shutil.copyfile(__file__,dest/'archive.py')
save('sha256.json',{p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file() and p.name!='sha256.json'})
print('Saved verified QEMU pressure results and source snapshots:',dest)
