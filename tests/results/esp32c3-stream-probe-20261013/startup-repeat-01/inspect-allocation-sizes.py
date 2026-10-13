from pathlib import Path
from elftools.elf.elffile import ELFFile
import hashlib,json
root=Path.cwd();dest=root/'tests/results/esp32c3-stream-probe-20261013/startup-repeat-01'
elf=root/'idf/esp32c3-oled-native/build-idf-6.1-r9a97-startup-confirm/yoradio_esp32c3_oled_native.elf'
manifest=json.loads((dest/'candidate.json').read_text());elf_hash=hashlib.sha256(elf.read_bytes()).hexdigest()
assert elf_hash==manifest['image']['app_elf_sha256']
found={};wanted={'owner_t','aac_sbr_control_abi_t','aac_sbr_owner_abi_t','aac_analysis_core_t'}
with elf.open('rb') as stream:
 for cu in ELFFile(stream).get_dwarf_info().iter_CUs():
  name=cu.get_top_DIE().attributes.get('DW_AT_name')
  if not name or not name.value.decode().endswith('aac_compact_owner.c'):continue
  for die in cu.iter_DIEs():
   attr=die.attributes.get('DW_AT_name')
   if not attr or attr.value.decode() not in wanted:continue
   typ=die
   while 'DW_AT_byte_size' not in typ.attributes and 'DW_AT_type' in typ.attributes:
    typ=typ.get_DIE_from_attribute('DW_AT_type')
   if 'DW_AT_byte_size' in typ.attributes:found[attr.value.decode()]=typ.attributes['DW_AT_byte_size'].value
assert set(found)==wanted
record=dict(elf_sha256=elf_hash,compilation_unit='aac_compact_owner.c',dwarf_bytes=found,
 caps=dict(value=6144,flags=['MALLOC_CAP_INTERNAL (1<<11)','MALLOC_CAP_DEFAULT (1<<12)']),
 caps_source='ESP-IDF 9a97f6c54ec638111ce55cd36581b3c192f15207 components/heap/include/esp_heap_caps.h:42-43',
 interpretation='A 32744-byte request equals sizeof(owner_t) in the active compact SBR allocation wrapper; post-failure heap snapshots occur after cleanup and cannot distinguish fragmentation from transient total exhaustion.')
(dest/'allocation-sizes.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
