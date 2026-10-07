import gzip,hashlib,json,shutil,subprocess
from pathlib import Path
root=Path.cwd();run=root/'.build/aac-asymmetric-production'
out=root/'tests/results/esp32c3-aac-asymmetric-production-20261004'
out.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(src,dst):
    path=out/dst;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,path)
def save(dst,value):
    path=out/dst;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
for folder in ('baseline-load','baseline-load-retry','candidate-load','ota-transition','ota-repeat','local','https','https-relocated','http','candidate-load-relocated'):
    assert (run/folder/'report.json').is_file(),folder
    for path in (run/folder).glob('*.json'):copy(path,folder+'/'+path.name)
for name in ('build-verification.json','physical-low-wrapper.asm','inspect-build.py','save-evidence.py','capture-final-board.py','baseline-post-failure.json','reposition-probe.json','physical-patch-audit.json','run-board.py','run-qemu.py','remaining-suite-exits.json','network-allocation-audit.json'):
    copy(run/name,name)
if (run/'final-board.json').is_file():copy(run/'final-board.json','final-board.json')
for name in ('synthetic','abba64','groovesalad16','groovesalad32','groovesalad64','groovesalad128'):
    for file in ('qemu.log','result.json'):copy(run/'qemu'/name/file,f'qemu/{name}/{file}')
build=root/'idf/esp32c3-oled-native/build-qemu-aac-asymmetric-production'
for name in ('sdkconfig','esp-idf/main/compact5/audit.json','esp-idf/main/compact5/layout.o'):
    copy(build/name,'qemu/'+Path(name).name)
(out/'qemu/control-candidate.wav.gz').write_bytes(gzip.compress((run/'qemu/synthetic/audio.wav').read_bytes(),mtime=0))
fw=root/'firmware/development/esp32c3-aac-asymmetric-owner'
image=json.loads((fw/'manifest.json').read_text())['image']
reports={name:json.loads((out/name/'report.json').read_text()) for name in
         ('baseline-load','baseline-load-retry','candidate-load','ota-transition','ota-repeat','local','https','https-relocated','http','candidate-load-relocated')}
summary=dict(image=image,production_default=False,
    cases={name:[dict(name=c['name'],result=c['result'],**({'reason':c['reason']} if 'reason' in c else {}))
                 for c in report['cases']] for name,report in reports.items()},
    bounded_suites_all_pass=all(c['result']=='PASS' for report in reports.values() for c in report['cases']),
    objective_complete=False,
    note='Bounded physical checks only. Public failures remain failures; no long soak, malformed-stream or every-stream claim.')
save('summary.json',summary)
main='idf/esp32c3-oled-native/main/'
sources=[main+n for n in ('CMakeLists.txt','Kconfig.projbuild','aac_high_history.c','aac_high_history.h',
    'aac_high_history_abi.h','aac_high_reset.h','aac_pointer_audit.c','aac_pointer_audit.h',
    'aac_smoothing_history.c','aac_smoothing_history.h','aac_compact_owner.c','aac_compact_owner.h',
    'aac_sbr_abi.h','native_aac_decoder.c','qemu_aac_compact_adapter.c','qemu_aac_test.c',
    'packed_complex_storage.h','audio_service.c')]
sources += ['idf/esp32c3-oled-native/sdkconfig.aac-asymmetric-owner.defaults',
            'tools/codec_benchmark/run_aac_asymmetric_owner.py','tools/codec_benchmark/run_aac_low_workspace.py','tools/codec_benchmark/compact_asymmetric_owner.py','tools/codec_benchmark/aac_asymmetric_owner_layout.c','tools/codec_benchmark/compact_low_workspace.py',
            'tools/codec_benchmark/aac_low_workspace_layout.c','tests/test-aac-asymmetric-production.py']
sources += [p.relative_to(root).as_posix() for folder in ('tools/esp32c3_tests','tools/audio_test_server')
            for p in sorted((root/folder).glob('*.py'))]
manifest=dict(base_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),files={},evidence={})
for path in sources:
    dst='sources/'+path;copy(root/path,dst)
    manifest['files'][path]=dict(snapshot=dst,sha256=sha(out/dst))
# Retain the exact runner source for both the earlier failure and current runs.
manifest['runner_sources']={}
for report in reports.values():
    for name,digest in report.get('test_sources_sha256',{}).items():
        key=name+'@'+digest
        if key in manifest['runner_sources']:continue
        current=root/name
        data=current.read_bytes()
        if hashlib.sha256(data).hexdigest()!=digest:
            data=(root/'tests/results/esp32c3-aac-low-production-20261003/sources'/name).read_bytes()
            if hashlib.sha256(data).hexdigest()!=digest:
                data=subprocess.check_output(['git','show','afa4a1ba:'+name])
        assert hashlib.sha256(data).hexdigest()==digest,(name,digest)
        dst='runner-sources/'+digest+'/'+Path(name).name
        path=out/dst;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        manifest['runner_sources'][key]=dst
for path in out.rglob('*'):
    if path.is_file() and 'sources' not in path.relative_to(out).parts and path.name!='implementation.json':
        manifest['evidence'][path.relative_to(out).as_posix()]=sha(path)
save('implementation.json',manifest)
print(json.dumps(summary,indent=2))
