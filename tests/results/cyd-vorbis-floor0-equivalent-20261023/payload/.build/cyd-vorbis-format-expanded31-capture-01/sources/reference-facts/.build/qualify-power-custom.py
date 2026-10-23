from pathlib import Path
import hashlib
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'tools'))
from export_cyd_production import image_descriptor
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
base = root / 'firmware/development/esp32-cyd2usb-native-network-power-pdm'
custom = root / 'firmware/development/esp32-cyd2usb-native-network-power-custom-flac-pdm'
before = json.loads((base / 'sdkconfig.json').read_text(encoding='utf-8'))
after = json.loads((custom / 'sdkconfig.json').read_text(encoding='utf-8'))
changes = {k: {'previous': before.get(k), 'current': after.get(k)} for k in sorted(set(before)|set(after)) if before.get(k) != after.get(k)}
assert changes == {'YORADIO_FLAC_DECODER_CUSTOM': {'previous': False, 'current': True},
                   'YORADIO_FLAC_DECODER_ESPRESSIF': {'previous': True, 'current': False}}
manifest = json.loads((custom / 'manifest.json').read_text(encoding='utf-8'))
assert manifest['build_check'] == 'PASS' and not manifest['physical_tested'] and not manifest['source_dirty']
assert manifest['source_commit'] == json.loads((base / 'manifest.json').read_text())['source_commit']
assert sha(custom / 'app.bin') == manifest['app_sha256']
descriptor = image_descriptor((custom / 'app.bin').read_bytes())
assert descriptor['elf_sha256'] == manifest['elf_sha256'] and descriptor['version'] == manifest['app_version']
assert sha(custom / 'sdkconfig') == manifest['sdkconfig_sha256']
assert sha(custom / 'sdkconfig.json') == manifest['sdkconfig_json_sha256']
for name, key in [('partition-table.bin','partition_table_sha256'),('flasher_args.json','flasher_args_sha256'),('project_description.json','project_description_sha256')]:
    assert sha(custom / name) == manifest[key]
for entry in manifest['evidence']:
    assert sha(Path(entry['path'])) == entry['sha256']
for entry in manifest['build_logs']:
    assert sha(custom / entry['file']) == entry['sha256']
results = []
for name, folder in [('vendor', base), ('custom', custom)]:
    m = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    build = Path(m['build_directory']); build = build if build.is_absolute() else root / build
    description = json.loads((build / 'project_description.json').read_text(encoding='utf-8'))
    elf = build / description['app_elf']; assert sha(elf) == m['elf_sha256']
    tool = Path(description['c_compiler']).with_name('xtensa-esp32-elf-nm.exe')
    command = [str(tool), '--defined-only', str(elf)]
    raw = subprocess.check_output(command, text=True)
    names = {line.split()[-1] for line in raw.splitlines() if line.split()}
    has_custom = 'custom_flac_decoder_feed' in names
    has_vendor = 'esp_flac_dec_register' in names
    assert has_custom == (name == 'custom') and has_vendor == (name == 'vendor'), (name, has_custom, has_vendor)
    results.append({'selection': name, 'elf_sha256': m['elf_sha256'], 'command': command,
                    'custom_feed_defined': has_custom, 'vendor_flac_registration_defined': has_vendor})
report = {'passed': True, 'source_commit': manifest['source_commit'], 'physical_tested': False,
          'variant': manifest['variant'], 'app_bytes': manifest['app_bytes'],
          'ota_free_bytes': min(p['bytes'] for p in manifest['ota_slots']) - manifest['app_bytes'],
          'sdkconfig_changes': changes, 'linked_selections': results, 'manifest_sha256': sha(custom / 'manifest.json'),
          'scope': 'Actual Xtensa GCC application link/export with custom FLAC, image/config/evidence integrity and selected ELF symbols. Decoder PCM/lifetime uses the independent current host report; QEMU and physical performance remain open.'}
out = root / 'tests/results/network-power-transfer-20261019/SDK-custom.json'
out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'passed':True,'app_bytes':report['app_bytes'],'ota_free_bytes':report['ota_free_bytes'],'linked_selections':results}, indent=2))
