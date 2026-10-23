import hashlib
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile

root=Path(__file__).resolve().parents[1]
targets={'cyd':root/'idf/esp32-cyd2usb-native/build-c3-transfer/yoradio_cyd2usb_native.elf',
         'c3':root/'idf/esp32c3-oled-native/build-c3-transfer/yoradio_esp32c3_oled_native.elf'}
names=['native_wifi_request_io','wifi_http_payload_t','private_workspace_t',
       'native_wifi_edit_t','native_wifi_metadata_t','native_time_sntp_config_t']
result={}
def size(die):
    seen=set()
    while die is not None and die.offset not in seen:
        seen.add(die.offset)
        if 'DW_AT_byte_size' in die.attributes: return die.attributes['DW_AT_byte_size'].value
        die=die.get_DIE_from_attribute('DW_AT_type') if 'DW_AT_type' in die.attributes else None
    return None
for board,path in targets.items():
    found={name:set() for name in names + (['time_settings_t','time_snapshot_t'] if board=='cyd' else ['runtime_time_settings_t'])}
    with path.open('rb') as file:
        dwarf=ELFFile(file).get_dwarf_info()
        for unit in dwarf.iter_CUs():
            for die in unit.iter_DIEs():
                name=die.attributes.get('DW_AT_name')
                if name and name.value.decode(errors='replace') in found:
                    value=size(die)
                    if value is not None: found[name.value.decode()].add(value)
    assert all(len(values)==1 for values in found.values()),(board,found)
    result[board]={'elf_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                   'bytes':{name:next(iter(values)) for name,values in found.items()}}
out=root/'tests/results/native-runtime-transfer-20261018/SDK-layout.json'
out.write_text(json.dumps({'passed':True,'physical_memory_measured':False,'targets':result,
    'scope':'DWARF byte sizes from the actual final linked target ELF. These exclude allocator/RTOS overhead and do not establish simultaneous allocation peaks or physical heap/stack headroom.'},indent=2)+'\n')
print(json.dumps(result,indent=2))
