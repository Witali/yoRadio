import hashlib,json,shutil
from pathlib import Path
root=Path('.build/c3-radio-wifi-probe');dest=Path('tests/results/esp32c3-web-wifi-probe-build');assert not dest.exists()
assert json.loads((root/'build-audit.json').read_text())['result']=='PASS'
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-radio-wifi-probe');manifest=json.loads((art/'manifest.json').read_text())
manifest.update(build_report='tests/results/esp32c3-web-wifi-probe-build/build/build-audit.json',source_capture_head=(root/'source-head.txt').read_text().strip(),host_tests=dict(parser_cases=10,backlog_variants=[0,1],frames_per_variant=73,sanitizers=['address','undefined']),disabled_probe_comparison='tests/results/esp32c3-web-wifi-probe-build/disabled/report.json')
(art/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(art/'.gitattributes').write_text('*.json -text -whitespace\nsdkconfig -text -whitespace\n')
for name in ('manifest.json','sdkconfig'):shutil.copyfile(art/name,root/('artifact-'+name))
for path in Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-radio-wifi-probe/log').glob('*'):
    if path.is_file():
        target=root/'idf-logs'/path.name;target.parent.mkdir(exist_ok=True);shutil.copyfile(path,target)
for name in ('tests/test-web-tcp.py','tools/esp32c3_tests/web_tcp.py','docs/ESP32C3_TESTING.md'):
    path=Path(name);target=root/'test-sources'/path;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,target)
verify=Path('.build/c3-production-radio/verify_commit.py').read_text().replace('tests/results/esp32c3-production-radio-build','tests/results/esp32c3-web-wifi-probe-build')
(root/'verify_commit.py').write_text(verify)
for source_root,label in ((root,'build'),(Path('.build/c3-web-wifi-probe-host-final'),'host'),(Path('.build/c3-web-wifi-probe-off'),'disabled')):
    for source in sorted(source_root.rglob('*')):
        if not source.is_file() or '__pycache__' in source.parts or source.suffix=='.obj':continue
        if label=='host' and source.name in ('backlog-0','backlog-1'):continue
        target=dest/label/source.relative_to(source_root);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
(dest/'.gitattributes').write_text('* -text -filter -whitespace\n')
index={p.relative_to(dest).as_posix():dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'index.json').write_text(json.dumps(index,indent=2)+'\n');print('Frozen',len(index),'files')
