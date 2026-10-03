import gzip,hashlib,json,shutil,subprocess
from pathlib import Path
root=Path.cwd();run=root/'.build/aac-asymmetric'
out=root/'tests/results/esp32c3-aac-asymmetric-owner-20261003'
out.mkdir(parents=True,exist_ok=True)
build=root/'idf/esp32c3-oled-native/build-qemu-aac-asymmetric'
binutils=Path('C:/Work/yoRadio/.idf/tools-v6.0.2/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(src,dst):
    p=out/dst;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,p)
def save(dst,data):
    (out/dst).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
runs=('synthetic','abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128')
results={}
for name in runs:
    for file in ('qemu.log','result.json'):copy(run/name/file,name+'/'+file)
    results[name]=json.loads((run/name/'result.json').read_text())
for file in ('qemu.log','result.json'):copy(run/'disabled-control'/file,'disabled-control/'+file)
copy(root/'idf/esp32c3-oled-native/build-qemu-aac-low-production/sdkconfig','disabled-control/sdkconfig')
for file in ('qemu.log','runner.log'):copy(run/'rejected-parser'/file,'rejected-parser/'+file)
for file in ('sdkconfig','esp-idf/main/compact5/layout.o','esp-idf/main/compact5/audit.json'):
    copy(build/file,Path(file).name)
for name in ('save-evidence.py','build.py','run.py'):copy(run/name,'reproduction/'+name)
audit=json.loads((out/'audit.json').read_text())
native=out/'native';native.mkdir(exist_ok=True)
archive=Path('C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec/lib/esp32c3/libesp_audio_codec.a')
assert sha(archive)==audit['codec_sha256']
for symbol,entry in audit['functions'].items():
    name=('pvmp4audiodecoderframe' if symbol=='PVMP4AudioDecodeFrame' else symbol)+'.c.obj'
    subprocess.run([str(binutils/'riscv32-esp-elf-ar.exe'),'x',str(archive),name],cwd=native,check=True)
    assert sha(native/name)==entry['input_sha256']
    copy(build/'esp-idf/main/compact5'/name,'patched/'+name)
elf=build/'yoradio_esp32c3_oled_native.elf'
symbols=subprocess.check_output([str(binutils/'riscv32-esp-elf-nm.exe'),'--defined-only',str(elf)],text=True)
names={line.split()[-1] for line in symbols.splitlines() if line.split()}
linked=dict(elf_sha256=sha(elf),native_symmetric_open_linked='compact5_sbr_open' in names,
            typed_open_linked='__wrap_compact5_sbr_open' in names)
assert linked['typed_open_linked'] and not linked['native_symmetric_open_linked']
save('linked-symbols.json',linked)
(out/'control-candidate.wav.gz').write_bytes(gzip.compress((run/'synthetic/audio.wav').read_bytes(),mtime=0))
summary=dict(experiment='asymmetric SBR channel owner',owner_bytes=32744,previous_owner_bytes=35900,
    requested_saving=35900-32744,allocator_saving=4096,stack_bytes=16384,min_stack_free=2844,
    pointer_totals={key:sum(r['pointers'][key] for r in results.values()) for key in ('checks','copies','allocations','frees')},
    low_bindings=sum(r['low_pointer_bindings'] for r in results.values()),
    control_samples=657540,control_max_additional_error_lsb=max(r['pcm_vs_previous']['max_pcm_error_lsb'] for r in results.values()),
    capture_samples=sum(r.get('capture',{}).get('samples',0) for r in results.values()),
    complete_captures_identical=all(r.get('capture_identical') for n,r in results.items() if n!='synthetic'),
    production_qualified=False,physical_tested=False,
    note='QEMU-only. Actual smaller allocation and exact PCM are verified; network/OTA/physical CPU remain separate gates.')
save('summary.json',summary)
sources=[p for p in subprocess.check_output(['git','diff','--name-only'],text=True).splitlines()
         if p.endswith(('.c','.h','.py')) or p.endswith(('CMakeLists.txt','Kconfig.projbuild'))]
sources+=['tools/codec_benchmark/'+n for n in ('compact_asymmetric_owner.py','aac_asymmetric_owner_layout.c','run_aac_asymmetric_owner.py',
    'compact_sbr_tables.py','compact_high_history.py','compact_smoothing_history.py','compact_low_workspace.py',
    'aac_smoothing_history_layout.c','aac_low_workspace_layout.c','run_aac_pointer_audit.py','run_aac_smoothing_adapter.py','run_aac_bfp16.py')]
sources+=['tests/test-aac-asymmetric-owner.py','idf/esp32c3-oled-native/sdkconfig.qemu-aac-asymmetric-owner.defaults',
    'idf/esp32c3-oled-native/main/aac_sbr_abi.h','idf/esp32c3-oled-native/main/aac_compact_owner.h']
manifest=dict(base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),files={},evidence={})
for path in sorted(set(sources)):
    dst='sources/'+path;copy(root/path,dst);manifest['files'][path]=dict(snapshot=dst,sha256=sha(out/dst))
for path in out.rglob('*'):
    if path.is_file() and 'sources' not in path.relative_to(out).parts and path.name!='implementation.json':
        manifest['evidence'][path.relative_to(out).as_posix()]=sha(path)
save('implementation.json',manifest)
print(json.dumps(summary,indent=2))
