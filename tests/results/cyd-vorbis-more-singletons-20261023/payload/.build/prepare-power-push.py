import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
archive = root / 'tests/results/network-power-transfer-20261019'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

old = json.loads((archive / 'manifest.json').read_text(encoding='utf-8'))
for name, entry in old.items():
    data = (archive / name).read_bytes()
    assert len(data) == entry['bytes'] and digest(archive / name) == entry['sha256'], name
assert subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', 'idf', 'tests/native', 'tests/run-*'], cwd=root).strip() == b''

sdk = json.loads((archive / 'SDK.json').read_text(encoding='utf-8'))
custom = json.loads((archive / 'SDK-custom.json').read_text(encoding='utf-8'))
images = json.loads((archive / 'SDK-images.json').read_text(encoding='utf-8'))
assert sdk['passed'] and custom['passed'] and images['passed']
assert len(sdk['images']) == 4 and len(images['images']) == 5
expected_manifests = {entry['variant']: entry['manifest_sha256'] for entry in sdk['images']}
expected_manifests[custom['variant']] = custom['manifest_sha256']
for image in images['images']:
    dest = root / 'firmware/development' / image['variant']
    manifest_path = dest / 'manifest.json'
    assert digest(manifest_path) == expected_manifests[image['variant']]
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['source_commit'] == sdk['source_commit'] == custom['source_commit']
    assert manifest['source_dirty'] is False and manifest['physical_tested'] is False
    assert manifest['build_check'] == 'PASS'
    assert digest(dest / 'app.bin') == manifest['app_sha256'] == image['image_sha256']
    assert (dest / 'app.bin').stat().st_size == manifest['app_bytes'] == image['app_bytes']
    assert (dest / 'app.bin').read_bytes()[176:208].hex() == manifest['elf_sha256']
    if manifest['target'] == 'esp32c3':
        for name, expected in manifest['build_metadata_sha256'].items():
            assert digest(dest / name) == expected, name
        evidence = manifest['additional_host_evidence']
        assert digest(root / evidence['path']) == evidence['sha256']
        assert digest(dest / 'sdkconfig.json') == manifest['sdkconfig_sha256']
    else:
        for name, key in [('sdkconfig', 'sdkconfig_sha256'), ('sdkconfig.json', 'sdkconfig_json_sha256'), ('partition-table.bin', 'partition_table_sha256'), ('flasher_args.json', 'flasher_args_sha256'), ('project_description.json', 'project_description_sha256')]:
            assert digest(dest / name) == manifest[key], name
        for entry in manifest['evidence']:
            assert digest(Path(entry['path'])) == entry['sha256']
        for entry in manifest['build_logs']:
            assert digest(dest / entry['file']) == entry['sha256']

entries = {}
for path in sorted(archive.rglob('*')):
    if path.is_file() and path.name != 'manifest.json':
        entries[path.relative_to(archive).as_posix()] = {'sha256': digest(path), 'bytes': path.stat().st_size}
# Only the root manifest is excluded; nested evidence manifests remain covered.
for path in sorted(archive.rglob('manifest.json')):
    if path != archive / 'manifest.json':
        entries[path.relative_to(archive).as_posix()] = {'sha256': digest(path), 'bytes': path.stat().st_size}
assert all(entries[name] == entry for name, entry in old.items())
entries = dict(sorted(entries.items()))
(archive / 'manifest.json').write_text(json.dumps(entries, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'passed': True, 'unchanged_prior_evidence_files': len(old), 'archive_entries': len(entries), 'qualified_firmware_variants': len(images['images'])}))
