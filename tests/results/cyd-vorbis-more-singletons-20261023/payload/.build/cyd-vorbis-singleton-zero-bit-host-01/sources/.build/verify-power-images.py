from pathlib import Path
import hashlib
import json
import struct
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from export_cyd_production import partition_slots
variants = ['esp32-cyd2usb-native-network-power-' + v for v in ['pdm', 'continuous', 'legacy']]
variants += ['esp32c3-oled-native-network-power']
variants += ['esp32-cyd2usb-native-network-power-custom-flac-pdm']
results = []
for variant in variants:
    folder = root / 'firmware/development' / variant
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    image = (folder / 'app.bin').read_bytes()
    c3 = manifest['target'] == 'esp32c3'
    assert image[0] == 0xe9 and 1 <= image[1] <= 16
    assert struct.unpack_from('<H', image, 12)[0] == (5 if c3 else 0)
    position, checksum = 24, 0xef
    for segment in range(image[1]):
        assert position + 8 <= len(image)
        size = struct.unpack_from('<I', image, position + 4)[0]; position += 8
        assert size > 0 and position + size <= len(image)
        if segment == 0:
            assert size >= 256 and struct.unpack_from('<I', image, position)[0] == 0xabcd5432
        for value in image[position:position+size]: checksum ^= value
        position += size
    at = ((position + 16) // 16) * 16 - 1
    assert at < len(image) and image[at] == checksum and image[23] == 1
    assert len(image) == at + 1 + 32
    assert hashlib.sha256(image[:at+1]).digest() == image[at+1:]
    build = root / manifest['build_directory']
    description = json.loads((build / 'project_description.json').read_text(encoding='utf-8'))
    elf = (build / description['app_elf']).read_bytes()
    assert elf[:6] == b'\x7fELF\x01\x01'
    assert struct.unpack_from('<H', elf, 18)[0] == (243 if c3 else 94)
    assert hashlib.sha256(elf).hexdigest() == manifest['elf_sha256'] == image[176:208].hex()
    slots = partition_slots((folder / 'partition-table.bin').read_bytes(), 4 * 1024 * 1024)
    limit = min(slot['bytes'] for slot in slots)
    assert limit == (0x1d0000 if c3 else 0x1b0000) and len(image) <= limit
    results.append({'variant': variant, 'chip_id': 5 if c3 else 0,
                    'elf_machine': 243 if c3 else 94, 'app_bytes': len(image),
                    'image_sha256': hashlib.sha256(image).hexdigest(), 'ota_slots': slots})
out = root / 'tests/results/network-power-transfer-20261019/SDK-images.json'
out.write_text(json.dumps({'passed': True, 'physical_tested': False, 'images': results,
    'scope': 'Actual application segment bounds/XOR/SHA256, descriptor/ELF identity, architecture and partition MD5/ranges/OTA slots. No flashing or physical execution.'}, indent=2) + '\n', encoding='utf-8')
print('PASS all five image checksums, target ELF identities and partition/OTA bounds')
