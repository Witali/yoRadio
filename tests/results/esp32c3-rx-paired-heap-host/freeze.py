import hashlib,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parent
dest=Path('tests/results/esp32c3-rx-paired-heap-host')
assert not dest.exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads(Path('.build/codec-owner/host/report.json').read_text())
target=json.loads((root/'target-review.json').read_text())
assert report['pass'] and target['result']=='PASS'
for name,digest in report['source_sha256'].items():assert sha(Path(name))==digest,name
assert target['source_sha256']==sha(Path('idf/esp32c3-oled-native/main/rx_buffer_diagnostic.c'))
sources=['idf/esp32c3-oled-native/main/rx_buffer_diagnostic.c',
    'idf/esp32c3-oled-native/main/rx_buffer_diagnostic.h',
    'idf/esp32c3-oled-native/main/Kconfig.projbuild',
    'idf/esp32c3-oled-native/main/CMakeLists.txt',
    'tools/esp32c3_tests/rx_ownership.py','tests/native/rx_buffer_diagnostic_test.c',
    'tests/test-rx-buffer-diagnostic.py','tests/test-rx-ownership.py',
    'tests/test-rx-ownership-evidence.py','tests/test-rx-transport-evidence.py',
    'docs/ESP32C3_TESTING.md']
def copy(source,relative):
    path=dest/relative;path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,path)
for name in sources:copy(Path(name),Path('sources')/name)
for name in ('report.json','run.log','build.log','test.c'):
    copy(Path('.build/codec-owner/host')/name,Path('host')/name)
for name in ('target-review.json','target-compile.log','rx_buffer.su'):
    copy(root/name,Path('target')/name)
copy(Path('.build/check-rx-paired-target.py'),'target/check-rx-paired-target.py')
copy(Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-radio-wifi-probe/sdkconfig'),'target/sdkconfig.base')
copy(Path(__file__),'freeze.py')
summary=dict(scope='Observed session test outcomes; native/target logs retained separately',
    python_cases=[dict(test=name,cases=count,result='PASS',sha256=sha(Path(name))) for name,count in
        [('tests/test-rx-ownership.py',6),('tests/test-rx-ownership-evidence.py',5),('tests/test-rx-transport-evidence.py',6)]],
    host_sanitizers=['address','undefined'],rv32_poll_stack_bytes=target['poll_stack_bytes'],
    initial_target_launch='Compiler was not launched: POSIX parsing removed Windows path separators; corrected path compile passed',
    physical_attribution=False,production_changed=False)
(dest/'validation-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
verify=Path('.build/c3-production-radio-mp3-http/verify_commit.py').read_text().replace(
    'tests/results/esp32c3-production-radio-mp3-http','tests/results/esp32c3-rx-paired-heap-host')
(dest/'verify_commit.py').write_text(verify)
(dest/'.gitattributes').write_text('* -text -filter -whitespace\n')
index={p.relative_to(dest).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))
    for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(index),'RX pairing evidence files')
