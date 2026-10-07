import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
sys.path.insert(0,'tools/esp32c3_tests')
from ota import image_info

p=argparse.ArgumentParser()
p.add_argument('--version',required=True)
p.add_argument('--variant',required=True)
a=p.parse_args()
build=Path(f'idf/esp32c3-oled-native/build-idf-{a.version}-{a.variant}')
target=Path(f'firmware/development/esp32c3-idf-{a.version}-{a.variant}')
target.mkdir(parents=True,exist_ok=True)
for source,name in (('yoradio_esp32c3_oled_native.bin','app.bin'),('sdkconfig','sdkconfig')):
    shutil.copyfile(build/source,target/name)
data=(target/'app.bin').read_bytes()
description=json.loads((build/'project_description.json').read_text())
manifest={'idf':a.version,'profile':a.variant,'source_head_at_capture':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
          'embedded_project_version':data[48:80].split(b'\0')[0].decode(),
          'idf_from_image':data[144:176].split(b'\0')[0].decode(),
          'image':image_info(data),'build_directory':str(build),'qualification':'build only; see separate physical reports',
          'sdkconfig_sha256':hashlib.sha256((target/'sdkconfig').read_bytes()).hexdigest(),
          'elf_sha256':hashlib.sha256((build/'yoradio_esp32c3_oled_native.elf').read_bytes()).hexdigest(),
          'project_version_at_build':description['project_version']}
assert manifest['idf_from_image'].startswith('v'+a.version),manifest
(target/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
print(json.dumps({'variant':a.variant,'idf':manifest['idf_from_image'],'bytes':len(data),'elf':manifest['image']['app_elf_sha256']}))
