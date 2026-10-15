import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-read512-20261015');src=base/'physical'
dest=Path('tests/results/esp32c3-read512-20261015/physical')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
c=json.loads((src/'controller.json').read_text())
assert c['restored']['stopped'] and 'restoration_failure' not in c
assert all(c['restored']['settings'].values())
assert c['restored']['identity']['app_elf_sha256']==c['original']['app_elf_sha256']
assert (src/'summary.json').is_file() and (src/'packing.json').is_file()
assert not dest.exists();shutil.copytree(src,dest)
old=json.loads(Path('tests/results/esp32c3-decode-probe-20261015/physical/control1/test-source-reference.json').read_text())
assert sha(base/'deploy.py')==c['controller_sha256']
for p in dest.rglob('report.json'):
    r=json.loads(p.read_text());assert sha(base/'run.py')==r['runner_sha256'];mapping={}
    for name,digest in r['test_sources_sha256'].items():
        saved=Path(old[name]['path']) if name in old else dest/'sources'/name
        if not saved.is_file() or sha(saved)!=digest:
            assert sha(Path(name))==digest,name
            saved=dest/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,saved)
        mapping[name]=dict(path=saved.as_posix(),sha256=digest)
    (p.parent/'test-source-reference.json').write_text(json.dumps(mapping,indent=2)+'\n')
for name in ('deploy.py','run.py','summarize.py','freeze-physical.py','inspect-packing.py','inspect-frame-window.py','frame-window.json'):
    shutil.copyfile(base/name,dest/name)
for name in ('common.py','ota.py'):
    saved=dest/'controller-sources'/name;saved.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(Path('tools/esp32c3_tests')/name,saved)
for name in ('idf/esp32c3-oled-native/components/custom_flac/custom_flac_adapter.cpp','yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp'):
    saved=dest/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,saved)
artifact=Path('firmware/development/esp32c3-idf61-read512-diagnostic')
m=json.loads((artifact/'manifest.json').read_text());m['hardware_tested']=True
m['physical_evidence']=dest.as_posix()
m['qualification']='Experimental HTTP read-size comparison; see physical reports, including failed output gates. Not production-qualified; default remains 2048 B.'
(artifact/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
shutil.copyfile(artifact/'manifest.json',dest/'firmware-manifest.json')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():sha(p) for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Saved read-size comparison with exact sources and verified restoration')
