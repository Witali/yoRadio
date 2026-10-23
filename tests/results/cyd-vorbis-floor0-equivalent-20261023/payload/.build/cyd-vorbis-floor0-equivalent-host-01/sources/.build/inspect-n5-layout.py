import hashlib
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parents[1]
folder = root / 'firmware/development/esp32-cyd2usb-native-network-settings-pdm'
manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
build = Path(manifest['build_directory'])
if not build.is_absolute():
    build = root / build
description = json.loads((build / 'project_description.json').read_text(encoding='utf-8'))
path = build / description['app_elf']
sha = hashlib.sha256(path.read_bytes()).hexdigest()
assert sha == manifest['elf_sha256']
found = {name: set() for name in ['native_network_power_snapshot_t', 'wifi_config_t',
    'network_owner_t', 'network_snapshot_t', 'network_profiles_t', 'network_settings_t', 'network_settings_runtime_t']}

def size(die):
    seen = set()
    while die is not None and die.offset not in seen:
        seen.add(die.offset)
        if 'DW_AT_byte_size' in die.attributes:
            return die.attributes['DW_AT_byte_size'].value
        die = die.get_DIE_from_attribute('DW_AT_type') if 'DW_AT_type' in die.attributes else None
    return None

with path.open('rb') as stream:
    dwarf = ELFFile(stream).get_dwarf_info()
    for unit in dwarf.iter_CUs():
        for die in unit.iter_DIEs():
            name = die.attributes.get('DW_AT_name')
            if name and name.value.decode(errors='replace') in found:
                value = size(die)
                if value is not None:
                    found[name.value.decode()].add(value)
assert all(len(values) == 1 for values in found.values()), found
previous = json.loads((root / 'tests/results/network-power-transfer-20261019/SDK-layout.json').read_text(encoding='utf-8'))['targets']['cyd']
report = dict(passed=True, source_commit=manifest['source_commit'], elf_sha256=sha,
    bytes={name: next(iter(values)) for name, values in found.items()}, prior_network_power_layout=previous,
    physical_memory_measured=False,
    scope='Actual final PDM Xtensa ELF DWARF byte sizes; prior linked N4 layout retained for comparison. Struct/static size is not allocator/RTOS overhead, simultaneous heap peaks or measured task stack headroom.')
(root / 'tests/results/cyd-network-settings-20261020/SDK-layout.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
