"""Add seven-app SDK evidence without changing the frozen initial host archive."""
from pathlib import Path
import hashlib
import json
import re

root = Path.cwd()
base = root / 'tests/results/cyd-input-reclaim-20261020'
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
load = lambda path: json.loads(Path(path).read_text())
report = load(base / 'SDK.json')
assert report['passed'] and len(report['images']) == 7
marker_path = root / '.build/input-reclaim-production-source.json'
marker = load(marker_path)
assert report['source_commit'] == marker['source_commit']
assert report['source_marker_sha256'] == sha(marker_path)
manifest_path = base / 'manifest.json'
initial_bytes = manifest_path.read_bytes()
manifest = json.loads(initial_bytes)
old = dict(manifest['files'])
for name, value in old.items():
    assert sha(base / name) == value['sha256'] and (base / name).stat().st_size == value['bytes']
tools = base / 'appendix-tools'
tools.mkdir(exist_ok=False)
(tools / 'initial-host-manifest.json').write_bytes(initial_bytes)
for relative, digest in marker['qualifier_tools_sha256'].items():
    original = root / relative
    assert sha(original) == digest
    (tools / original.name).write_bytes(original.read_bytes())
for name in ('input-reclaim-production-source.json', 'input-reclaim-production-profiles.json',
             'finish-input-reclaim-sdk-evidence.py', 'input-reclaim-production-run.out.log',
             'input-reclaim-production-run.err.log'):
    (tools / name).write_bytes((root / '.build' / name).read_bytes())
for name in ('cyd-input-reclaim-sdk-review-01', 'cyd-input-reclaim-sdk-review-02',
             'input-reclaim-sdk-contract-tests-02'):
    original = root / '.build' / name
    for path in original.rglob('*'):
        if not path.is_file():
            continue
        data = path.read_bytes()
        assert not (data.startswith(b'\x7fELF') or data.startswith(b'MZ'))
        target = tools / name / path.relative_to(original)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

# These are explicitly post-build reconstructions, not newly claimed pre-build
# file captures. SHA equality binds them to the actual frozen seed identities.
profiles = load(root / '.build/input-reclaim-production-profiles.json')
seed_dir = tools / 'prepared-seed-reconstruction'
seed_dir.mkdir()
for profile in profiles:
    raw = (Path(profile['baseline']) / 'sdkconfig').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == profile['baseline_sdkconfig_sha256']
    lines = [line for line in raw.decode().splitlines()
             if not re.match(r'^(?:# )?CONFIG_YORADIO_TLS_INPUT_RECLAIM(?:=| )', line)]
    lines.append('CONFIG_YORADIO_TLS_INPUT_RECLAIM=y' if profile['enabled']
                 else '# CONFIG_YORADIO_TLS_INPUT_RECLAIM is not set')
    data = ('\n'.join(lines) + '\n').encode()
    assert hashlib.sha256(data).hexdigest() == profile['prepared_sdkconfig_sha256']
    receipt = load(root / 'firmware/development' / profile['variant'] / 'manifest.json')
    assert receipt['sdkconfig_seed']['source_sha256'] == hashlib.sha256(data).hexdigest()
    (seed_dir / (profile['name'] + '.sdkconfig')).write_bytes(data)

audit = load(root / 'tests/results/cyd-vorbis-xtensa-audit-20261020/raw/report.json')
codec = {}
for name, value in audit['installed_identity']['archives'].items():
    if not name.startswith('esp32/'):
        continue
    path = Path(value['path'])
    assert sha(path) == value['sha256'] and path.stat().st_size == value['bytes']
    codec[name] = value
(base / 'SDK-codec-identity.json').write_text(json.dumps(dict(passed=True, archives=codec,
    scope='Post-build current ESP32 codec archive identities equal the pre-build audited binaries. No new decoder execution.'), indent=2) + '\n')

rows = ['# CYD opt-in TLS input reclaim: application qualification\n',
        'All seven GCC applications were built/exported from clean source `' + report['source_commit'] + '` on pinned SDK6.0.2. No board operation was performed.\n',
        '| Profile | Reclaim | App bytes | OTA free bytes | Compiler warnings |',
        '| --- | --- | ---: | ---: | ---: |']
for image in report['images']:
    label = image['backend'] + ' / ' + ('custom FLAC' if image['custom_flac'] else 'vendor FLAC')
    rows.append('| ' + label + ' | ' + ('on' if image['reclaim_enabled'] else 'off control') + ' | ' +
                str(image['app_bytes']) + ' | ' + str(image['ota_free_bytes']) + ' | ' + str(len(image['warnings'])) + ' |')
rows.extend(['',
    'Saved hand-offs are under `firmware/development/esp32-cyd2usb-native-tls-input-reclaim-<profile>/`: application, actual sdkconfig/text+JSON, partition table, flash recipe, logs and manifest. Six opt-in profiles cover vendor/custom FLAC with PDM/continuous/legacy; the seventh is a disabled vendor/PDM control. Older development images and versioned releases are preserved.',
    '',
    'Relative to each matching immutable output-telemetry image, the only normalized configuration difference is the new `YORADIO_TLS_INPUT_RECLAIM` bool (true for six images, false for control). Production default remains off. Hardware clocks/pins, DMA geometry, quiet diagnostics, codec selections, task cores/priorities/stacks, board configuration and both OTA slots retain their baseline.',
    '',
    'All seven actual ELF images retain ordinary SDK free. Six allocator initializers point to the production reclaim wrapper, and the disabled control points to the original SDK allocator. The exact canonical module and wrap/retention flags appear only in enabled compile/link inputs; no free wrapper or static TLS reserve is linked. Correct FLAC and HTTP-buffer-release symbols remain present. PDM telemetry helpers remain in IRAM and the prior metrics state/lock in DRAM. These checks establish linkage/layout, not physical heap savings, IRQ latency or audio continuity.',
    '',
    'The pre-build marker freezes the complete clean exporter source snapshot, profile identities, raw prepared seed hashes, required evidence sets and exact local helper hashes. The final qualifier rechecks source content and tools before and after all seven receipts; every baseline text/JSON/receipt is byte-equal to its committed Git blob. Four pre-run metadata review gaps were corrected before any build; 14 exact invalid-data controls and the final independent review cover those guards. SDK/code/image checks still execute on the real outputs.',
    '',
    '`appendix-tools/prepared-seed-reconstruction/` was generated after the builds from immutable baseline bytes and the frozen preparation recipe. Every byte hash equals the pre-build profile and actual exporter seed receipt. These are exact reconstructions, not a claim that new files were captured before compilation.',
    '',
    'The complete actual-SDK QEMU allocator gate is preserved separately in `../cyd-input-reclaim-qemu-20261020/`; its five cases/four exact controls do not run full radio/TLS handshakes or output hardware. Initial host README/HOST and all raw reports remain unchanged. Full opt-in Clang remains54 units/86 baseline warnings/0errors, with no new warnings.',
    '',
    'Any retained legacy diagnostics are the known IDF5.5.4 APLL deprecation warnings, listed exactly in `SDK.json`; environment activation-cleanup warnings are recorded separately. No new warning is suppressed.',
    '',
    'Physical HTTP/HTTPS, WebUI/OTA pressure, fragmentation/resource recovery, stack margins, DMA/IRQ behavior, audio quality and prolonged playback remain open. TLS RX remains16KiB. This application checkpoint does not close the remaining reserve/MPI/IRAM/stack work in stage13 or stages12/14/physical acceptance.',
    '',
    '`SDK.json` binds all seven receipt/image/ELF/config/tool/evidence identities, configuration deltas, pointer words and selected link/compile symbols. `SDK-codec-identity.json` rechecks the installed ESP32 codec archive identities. The additive manifest preserves every initial archive record.'])
(base / 'SDK.md').write_text('\n'.join(rows) + '\n')
for file in sorted(base.rglob('*')):
    if not file.is_file() or file == manifest_path:
        continue
    name = file.relative_to(base).as_posix()
    if name not in old:
        manifest['files'][name] = dict(sha256=sha(file), bytes=file.stat().st_size)
assert all(manifest['files'][name] == value for name, value in old.items())
manifest['file_count'] = len(manifest['files'])
manifest['indexed_bytes'] = sum(value['bytes'] for value in manifest['files'].values())
manifest['sdk_appendix'] = dict(source_commit=report['source_commit'], profiles=7, physical_tested=False,
                              initial_manifest_sha256=hashlib.sha256(initial_bytes).hexdigest(),
                              qualification_sha256=sha(base / 'SDK.json'))
manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
print('Extended', len(old), 'immutable initial records to', manifest['file_count'], 'records; seven-app SDK appendix complete')
