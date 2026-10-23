import hashlib,json,shutil,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
build=root/'idf/esp32c3-oled-native/build-c3-transfer'
variant='esp32c3-oled-native-web-transfer'
subprocess.run([sys.executable,str(root/'.build/export-stage02.py'),str(build),variant,'stereo-pdm',
                '--evidence','tests/results/native-web-transfer-20261018/HOST.md'],check=True,
               stdout=(root/'.build/export-web-c3.log').open('w'))
out=root/'firmware/development'/variant
manifest=json.loads((out/'manifest.json').read_text())
description=json.loads((build/'project_description.json').read_text())
assert description['target']=='esp32c3'
files={'sdkconfig':build/'sdkconfig','partition-table.bin':build/'partition_table/partition-table.bin',
       'project_description.json':build/'project_description.json','flasher_args.json':build/'flasher_args.json',
       'build.log':root/'.build/web-production-c3.out.log','build-stderr.log':root/'.build/web-production-c3.err.log'}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
metadata={}
for name,source in files.items():
    shutil.copyfile(source,out/name);metadata[name]=digest(out/name)
manifest.update(build_metadata_sha256=metadata,compiler=description['c_compiler'],
                compiler_sha256=digest(Path(description['c_compiler'])),ota_slot_bytes=0x1d0000,
                sdkconfig_sha256_file='sdkconfig.json',sdkconfig_text_sha256=digest(out/'sdkconfig'),
                source_dirty=False)
extra='tests/results/native-web-transfer-20261018/HOST_GCC.md'
manifest['additional_host_evidence']={'path':extra,'sha256':digest(root/extra)}
assert manifest['app_bytes']<=manifest['ota_slot_bytes']
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Archived C3 image/config/metadata/logs:',manifest['app_bytes'],'bytes;',manifest['ota_slot_bytes']-manifest['app_bytes'],'spare bytes')
