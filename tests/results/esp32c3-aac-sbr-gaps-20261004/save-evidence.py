from pathlib import Path
import gzip,hashlib,json,shutil,subprocess,sys

root=Path.cwd();work=root/'.build/aac-sbr-gaps';out=root/'tests/results/esp32c3-aac-sbr-gaps-20261004'
out.mkdir(parents=True,exist_ok=True)
def save(source,target,compress=False):
    dest=out/target;dest.parent.mkdir(parents=True,exist_ok=True)
    data=source.read_bytes();dest.write_bytes(gzip.compress(data,mtime=0) if compress else data)
for mode,build_name in [('candidate','build-qemu-aac-late-capture'),('reference','build-qemu-aac-late-reference')]:
    build=root/'idf/esp32c3-oled-native'/build_name
    for name in ('result.json','merge.log'):save(work/mode/name,f'{mode}/{name}')
    save(work/mode/'qemu.log',f'{mode}/qemu.log.gz',True)
    save(root/'.build/aac-late-sbr'/f'{build_name}.log',f'{mode}/build.log.gz',True)
    save(build/'sdkconfig',f'{mode}/sdkconfig')
    save(build/'config/sdkconfig.h',f'{mode}/sdkconfig.h')
    for p in (build/'esp-idf/main/compact5').glob('*.json'):save(p,f'{mode}/compact5/{p.name}')
for directory in ('faad','pcm','previous-pcm','first-failure'):
    for p in (work/directory).iterdir():
        if p.is_file() and p.suffix in ('.json','.frames','.state','.log','.gz','.c'):save(p,f'{directory}/{p.name}')
for name in ('build-command.json','build.log','encoder.log'):
    save(work/'generator'/name,f'generator/{name}')
save(work/'generator/syntax-trace.c','generator/syntax-trace.c.gz',True)
save(Path(__file__),'save-evidence.py')
sources=['.gitattributes','idf/esp32c3-oled-native/main/CMakeLists.txt',
 'idf/esp32c3-oled-native/main/Kconfig.projbuild',
 'idf/esp32c3-oled-native/main/qemu_aac_late_sbr.c','idf/esp32c3-oled-native/main/qemu_aac_sbr_gap.c',
 'idf/esp32c3-oled-native/main/native_aac_decoder.c','idf/esp32c3-oled-native/main/native_aac_decoder.h',
 'idf/esp32c3-oled-native/main/aac_compact_owner.c','idf/esp32c3-oled-native/main/aac_compact_owner.h',
 'idf/esp32c3-oled-native/main/aac_high_history.c','idf/esp32c3-oled-native/main/packed_complex_storage.h',
 'tools/codec_benchmark/run_aac_late_sbr_capture.py','tools/codec_benchmark/run_aac_late_sbr.py',
 'tools/codec_benchmark/compare_aac_late_sbr_pcm.py','tools/codec_benchmark/compare_aac_sbr_gap_pcm.py',
 'tools/codec_benchmark/generate_aac_sbr_gaps.py','tools/codec_benchmark/check_aac_sbr_gap_reference.py',
 'tools/codec_benchmark/faad_fil_probe.c','tests/test-aac-sbr-gaps.py']
sources += [p.relative_to(root).as_posix() for p in (root/'tests/fixtures/aac_sbr_gap').iterdir() if p.is_file()]
for name in sources:save(root/name,'sources/'+name)
cmd=[sys.executable,'-X','utf8','tools/codec_benchmark/compare_aac_sbr_gap_pcm.py',
 '--reference-log',str(work/'reference/qemu.log'),'--candidate-log',str(work/'candidate/qemu.log'),
 '--output',str(work/'pcm')]
result=subprocess.run(cmd,capture_output=True)
assert result.returncode==2,result.stderr
(out/'live-precision-gate.json').write_text(json.dumps(dict(exit_code=result.returncode,expected_limit_lsb=3,
    qualified=False,stdout=result.stdout.decode()),indent=2)+'\n',encoding='utf-8',newline='\n')
checksums={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*'))
           if p.is_file() and p.name!='checksums.json'}
(out/'checksums.json').write_text(json.dumps(checksums,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Saved',len(checksums),'checksummed evidence files; precision candidate REJECTED')
