from pathlib import Path
import hashlib,json,shutil
root=Path.cwd(); dest=root/'tests/results/cyd-flac-runtime-20261019';dest.mkdir(parents=True,exist_ok=False)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for group,folder in [('host','.build/cyd-flac-runtime-qualified-final'),('vendor-regression','.build/cyd-flac-vendor-regression-01')]:
 source=root/folder
 for p in source.rglob('*'):
  if p.is_file() and p.suffix in {'.c','.cpp','.h','.py','.inc','.json','.log'}:
   target=dest/group/p.relative_to(source); target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
 report=json.loads((source/'report.json').read_text()); assert report['passed']
 if group=='vendor-regression':
  for relative,expected in report['source_sha256'].items():
   p=root/relative;assert sha(p)==expected,relative
   target=dest/group/'sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
for mode in ['custom','vendor']:
 build=root/('.build/cyd-flac-runtime-sdk-'+mode); folder=dest/'sdk'/mode;folder.mkdir(parents=True)
 names=['integration-compile.json','sdkconfig','config/sdkconfig.json','config/sdkconfig.h','toolchain/cflags','toolchain/cxxflags','build.out.log','build.err.log']
 names += [p.name for p in build.glob('*.compile.log')]+[p.name for p in build.glob('*.nm.log')]
 for name in names:
  p=build/name
  if p.is_file(): target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
 report=json.loads((build/'integration-compile.json').read_text()); assert report['passed']
 for row in report['units']:
  p=root/row['source'];assert sha(p)==row['sha256'];target=dest/'sdk'/'sources'/row['source'];target.parent.mkdir(parents=True,exist_ok=True)
  if target.exists():assert sha(target)==sha(p)
  else:shutil.copyfile(p,target)
for name in ['run-cyd-flac-runtime-sdk.ps1','compile-cyd-flac-integration.py','check-cyd-flac-metadata-only.py']:
 shutil.copyfile(root/'.build'/name,dest/name)
# The complete metadata-only control input is tiny and contains no credentials.
shutil.copyfile(root/'.build/cyd-flac-runtime-qualified-final/metadata-only.flac',dest/'host/metadata-only.flac')
report=dict(passed=True,source_inputs_frozen_by_host_runner=True,sdk_scope='Actual Xtensa GCC compilation and object-symbol inspection; no application link, QEMU, physical performance or vendor binary execution.',source_sha256={p.relative_to(root).as_posix():sha(p) for p in [root/'idf/esp32-cyd2usb-native/main/audio_service.c',root/'idf/esp32-cyd2usb-native/main/decoder_registration.c',root/'idf/esp32-cyd2usb-native/main/Kconfig.projbuild']},reports={p.relative_to(dest).as_posix():sha(p) for p in dest.rglob('*.json') if p.name in {'report.json','integration-compile.json','metadata-only-boundaries.json'}})
(dest/'qualification.json').write_text(json.dumps(report,indent=2)+'\n')
print('Archived',sum(p.is_file() for p in dest.rglob('*')),'files')
