"""Freeze completed deployment/restoration and build evidence, never private settings."""
import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-input-tail-quiet-20261015')
dest=Path('tests/results/esp32c3-input-tail-quiet-20261015')
artifact=Path('firmware/development/esp32c3-idf61-input-tail-quiet')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
control=json.loads((base/'physical/controller.json').read_text())
assert control['restored']['stopped'] and 'restoration_failure' not in control
assert all(control['restored']['settings'].values())
assert control['restored']['identity']['app_elf_sha256']==control['original']['app_elf_sha256']
manifest=json.loads((artifact/'manifest.json').read_text())
assert manifest['image']==control['candidate']
for name,digest in manifest['files'].items():assert sha(artifact/name)==digest,name
manifest['hardware_tested']=True
manifest['qualification']='Quiet finite-file matrix including steady DMA gates retained separately; full production qualification remains open.'
manifest['physical_evidence']='tests/results/esp32c3-input-tail-quiet-20261015/physical'
manifest['original_production_restored']=True
(artifact/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(artifact/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
manifest['files']={p.name:sha(p) for p in artifact.iterdir() if p.is_file() and p.name!='manifest.json'}
(artifact/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for sub in ('build','physical'):
    folder=dest/sub;folder.mkdir(parents=True,exist_ok=True)
    (folder/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
build=dest/'build'
shutil.copytree('idf/esp32c3-oled-native/build-input-tail-quiet-20261015/log',build/'idf-logs')
for name in ('aac-audit.json','aac-audit.log','allocator-audit.json','allocator-audit.log',
             'allocator-audit.disassembly.txt','allocator-audit.rx-object.txt',
             'http-audit.json','http-audit.log','config-comparison.json', 'check-config.py', 'audit-tail-link.py', 'tail-link.json', 'tail-link.disassembly.txt','build-audit.json',
             'build.log','build.ps1','package.py'):
    shutil.copyfile(base/name,build/name)
for name in ('tools/codec_benchmark/verify_aac_network_build.py',
             'tools/esp32c3_tests/verify_adaptive_input_link.py',
             'tools/esp32c3_tests/verify_http_link.py',
             'tests/test-aac-network-build-layout.py'):
    saved=build/'sources'/name;saved.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(name,saved)
physical=dest/'physical'
for name in ('deploy.py','run-candidate.py','freeze-campaign.py'):
    shutil.copyfile(base/name,physical/name)
assert sha(base/'deploy.py')==control['controller_sha256']
shutil.copyfile(base/'physical/controller.json',physical/'controller.json')
shutil.copyfile(artifact/'manifest.json',physical/'firmware-manifest.json')
for folder in (build,physical):
    files={p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*'))
           if p.is_file() and p != folder/'sha256.json'}
    (folder/'sha256.json').write_text(json.dumps(files,indent=2)+'\n')
print(json.dumps(dict(restored=True,tests=control['tests'],image=manifest['image'])))
