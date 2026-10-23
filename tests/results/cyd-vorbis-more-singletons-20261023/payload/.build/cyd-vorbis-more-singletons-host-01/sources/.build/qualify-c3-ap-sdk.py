from pathlib import Path
import hashlib
import json
import re
import struct
import subprocess
import sys

root=Path(__file__).resolve().parents[1]
out=root/'tests/results/c3-ap-timeout-20261020'
folder=root/'firmware/development/esp32c3-oled-native-ap-timeout'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,str(root/'tools'))
from export_cyd_production import partition_slots
manifest=json.loads((folder/'manifest.json').read_text())
assert manifest['source_commit']=='e78b154da' or manifest['source_commit'].startswith('e78b154da')
assert manifest['source_dirty'] is False and manifest['physical_tested'] is False
assert manifest['target']=='esp32c3' and manifest['build_check']=='PASS'
for filename,key in [('app.bin','app_sha256'),('sdkconfig.json','sdkconfig_sha256'),('sdkconfig','sdkconfig_text_sha256')]:
    assert sha(folder/filename)==manifest[key],filename
for filename,expected in manifest['build_metadata_sha256'].items():assert sha(folder/filename)==expected,filename
assert sha(Path(manifest['compiler']))==manifest['compiler_sha256']
assert sha(root/manifest['additional_host_evidence']['path'])==manifest['additional_host_evidence']['sha256']
image=(folder/'app.bin').read_bytes()
assert len(image)>=288 and image[0]==0xe9 and 1<=image[1]<=16
assert struct.unpack_from('<I',image,32)[0]==0xabcd5432
descriptor={'elf_sha256':image[176:208].hex(),
            'version':image[48:80].split(b'\0',1)[0].decode('utf-8')}
assert len(image)==manifest['app_bytes'] and struct.unpack_from('<H',image,12)[0]==5
assert descriptor['elf_sha256']==manifest['elf_sha256'] and descriptor['version']==manifest['app_version']
assert manifest['source_commit'][:8] in descriptor['version'] and not descriptor['version'].endswith('-dirty')
position,checksum=24,0xef
for segment in range(image[1]):
    size=struct.unpack_from('<I',image,position+4)[0];position+=8
    assert size and position+size<=len(image)
    for value in image[position:position+size]:checksum^=value
    position+=size
at=((position+16)//16)*16-1
assert image[at]==checksum and image[23]==1
assert len(image)==at+33 and hashlib.sha256(image[:at+1]).digest()==image[at+1:]
slots=partition_slots((folder/'partition-table.bin').read_bytes(),4*1024*1024)
limit=min(row['bytes'] for row in slots);assert limit==0x1d0000 and len(image)<=limit
config=json.loads((folder/'sdkconfig.json').read_text())
previous=json.loads((root/'firmware/development/esp32c3-oled-native-network-power/sdkconfig.json').read_text())
assert config==previous
build=root/manifest['build_directory'];description=json.loads((build/'project_description.json').read_text())
elf=build/description['app_elf'];raw=elf.read_bytes()
assert raw[:6]==b'\x7fELF\x01\x01' and struct.unpack_from('<H',raw,18)[0]==243
assert sha(elf)==manifest['elf_sha256']
nm=Path(manifest['compiler']).with_name('riscv32-esp-elf-nm.exe')
symbols=subprocess.check_output([str(nm),'--defined-only',str(elf)])
(out/'sdk-symbols.log').write_bytes(symbols)
assert b'websocket_service_reboot_restart_reserved_now' in symbols
assert b'softap_reboot_callback' not in symbols
git=lambda *args:subprocess.check_output(['git','-c','core.longpaths=true',*args],cwd=root,text=True).strip()
unchanged=['idf/esp32c3-oled-native/main/audio_service.c','idf/esp32c3-oled-native/main/app_main.c',
           'idf/esp32c3-oled-native/main/board_config.h','idf/esp32c3-oled-native/sdkconfig.defaults',
           'idf/esp32c3-oled-native/sdkconfig.radio-tested.defaults','idf/esp32-cyd2usb-native']
assert not git('diff','1256de595',manifest['source_commit'],'--',*unchanged)
sources={name:sha(root/name) for name in unchanged if (root/name).is_file()}
sdk=Path(description['idf_path']);sdk_head=git('-C',str(sdk),'rev-parse','HEAD')
assert sdk_head.startswith('9a97f6c54ec6') and not git('-C',str(sdk),'status','--porcelain','--untracked-files=no')
logs='\n'.join((folder/name).read_text(errors='replace') for name in ('build.log','build-stderr.log'))
warnings=re.findall(r'^.*(?:warning:|CMake Warning).+$',logs,re.M)
result=dict(passed=True,source_commit=manifest['source_commit'],variant=manifest['variant'],
    app_bytes=len(image),ota_slot_bytes=limit,ota_spare_bytes=limit-len(image),
    image_checksum_and_sha256_verified=True,elf_architecture='RISC-V32',image_chip_id=5,
    sdk_commit=sdk_head,sdkconfig_identical_to_n4=True,task_audio_hardware_sources_unchanged=sources,
    cyd_production_sources_unchanged=True,reserved_restart_symbol_present=True,
    direct_ap_timer_callback_absent=True,compiler_sha256=manifest['compiler_sha256'],
    nm_sha256=sha(nm),symbols_sha256=sha(out/'sdk-symbols.log'),
    manifest_sha256=sha(folder/'manifest.json'),warnings=warnings,physical_tested=False)
(out/'SDK.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
