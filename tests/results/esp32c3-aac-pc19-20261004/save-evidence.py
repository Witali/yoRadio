from pathlib import Path
import gzip,hashlib,json,sys
root=Path.cwd();sys.path.insert(0,str(root/'tools/codec_benchmark'))
import compare_aac_sbr_gap_pcm as gaps
import compare_aac_late_sbr_pcm as late
import summarize_aac_pc19 as work
out=root/'tests/results/esp32c3-aac-pc19-20261004';out.mkdir(parents=True,exist_ok=True)
base=root/'.build/aac-gap-pc19'
def save(source,target,compress=False):
    dest=out/target;dest.parent.mkdir(parents=True,exist_ok=True)
    data=source.read_bytes();dest.write_bytes(gzip.compress(data,mtime=0) if compress else data)
def json_file(name,data):
    p=out/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
logs={}
for name,folder,build_name in [('baseline','bench18','build-qemu-aac-late-capture'),
 ('candidate','final19','build-qemu-aac-gap-pc19-side'),('inline','final-inline','build-qemu-aac-gap-pc19'),
 ('reference','final-reference','build-qemu-aac-late-reference')]:
    run=base/folder;build=root/'idf/esp32c3-oled-native'/build_name
    saved=json.loads((run/'result.json').read_text())
    elf=build/'yoradio_esp32c3_oled_native.elf'
    assert hashlib.sha256(elf.read_bytes()).hexdigest()==saved['provenance']['elf_sha256']
    for f in ('result.json','merge.log'):save(run/f,f'{name}/{f}')
    save(run/'qemu.log',f'{name}/qemu.log.gz',True)
    save(root/'.build/aac-late-sbr'/f'{build_name}.log',f'{name}/build.log.gz',True)
    save(build/'sdkconfig',f'{name}/sdkconfig');save(build/'config/sdkconfig.h',f'{name}/sdkconfig.h')
    for f in (build/'esp-idf/main/compact5').glob('*.json'):save(f,f'{name}/compact5/{f.name}')
    logs[name]=gaps.read_log(run/'qemu.log')
for directory,compare in [('pcm',gaps.compare),('previous-pcm',late.compare)]:
    result,left,right=compare(logs['reference'],logs['candidate']);assert result['precision_pass']
    json_file(directory+'/comparison.json',result)
    for name,data in [('reference',left),('candidate',right)]:
        (out/directory/(name+'.pcm.gz')).write_bytes(gzip.compress(data,mtime=0))
    same,a,b=compare(logs['inline'],logs['candidate']);assert a==b
summary=work.compare_work(logs['baseline'],logs['candidate']);json_file('work.json',summary)
json_file('all-memory.json',{name:work.parse_work(log) for name,log in logs.items()})
for name in ('build.log','test.log','result.json'):save(root/'.build/aac-storage19-host'/name,'host/'+name)
for name in ('test.log','packed_complex_storage.h'):save(base/'unsigned-mask-failure'/name,'unsigned-mask-failure/'+name)
for p in (base/'regression').glob('*.log'):save(p,'regression/'+p.name)
for name in ('first-build-guard.log',):
    if (base/name).exists():save(base/name,name+'.gz',True)
sources=['.gitattributes','idf/esp32c3-oled-native/main/CMakeLists.txt',
 'idf/esp32c3-oled-native/main/Kconfig.projbuild',
 'idf/esp32c3-oled-native/main/aac_high_history.c','idf/esp32c3-oled-native/main/aac_high_history.h',
 'idf/esp32c3-oled-native/main/aac_high_history_abi.h',
 'idf/esp32c3-oled-native/main/aac_compact_owner.c','idf/esp32c3-oled-native/main/aac_compact_owner.h',
 'idf/esp32c3-oled-native/main/native_aac_decoder.c','idf/esp32c3-oled-native/main/native_aac_decoder.h',
 'idf/esp32c3-oled-native/main/qemu_aac_pc19.c','idf/esp32c3-oled-native/main/qemu_aac_late_sbr.c',
 'idf/esp32c3-oled-native/main/qemu_aac_sbr_gap.c','idf/esp32c3-oled-native/main/packed_complex_storage.h',
 'idf/esp32c3-oled-native/main/packed_complex16.h','idf/esp32c3-oled-native/main/packed_complex16_fast.h',
 'tools/codec_benchmark/aac_asymmetric_owner_layout.c','tools/codec_benchmark/run_aac_late_sbr_capture.py',
 'tools/codec_benchmark/run_aac_late_sbr.py','tools/codec_benchmark/summarize_aac_pc19.py',
 'tools/codec_benchmark/compare_aac_sbr_gap_pcm.py','tools/codec_benchmark/compare_aac_late_sbr_pcm.py',
 'tests/native/aac_storage19_test.c','tests/run-aac-storage19.py','tests/test-aac-pc19.py']
for name in sources:save(root/name,'sources/'+name)
save(Path(__file__),'save-evidence.py')
checksums={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
 for p in sorted(out.rglob('*')) if p.is_file() and p.name!='checksums.json'}
json_file('checksums.json',checksums)
print('Saved',len(checksums),'files; PC19 passes this synthetic precision corpus only')
