"""Refresh validation metadata from the tested archive and a full passing suite."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
ARCHIVE = REPO / 'firmware/development/small-tv-esp32c2-reconstructed'
BUILD = REPO / '.build/small-tv-esp32c2'


def read(path):
    """Accept PowerShell JSON with or without its UTF-8 BOM."""
    return json.loads(path.read_text(encoding='utf-8-sig'))


def require(condition, message):
    """Reject stale evidence even when Python runs with assertions disabled."""
    if not condition:
        raise ValueError(message)


def main():
    """Derive sizes/counts dynamically; never turn missing checks into successes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', type=Path, default=ROOT / 'tests/functional-validation.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'validation.json')
    args = parser.parse_args()
    suite, manifest = read(args.suite), read(ARCHIVE / 'manifest.json')
    require(suite['passed'] and suite['automatic_profile'] == 'host_machine_qemu',
            'A full passing suite is required')
    groups = {row['name']: row['result'] for row in suite['groups'] if row['status'] == 'passed'} \
        if 'groups' in suite else suite
    for name in ('native', 'platform', 'frontend', 'integrity', 'machine', 'machine_control', 'machine_classic', 'machine_weather', 'machine_calendar', 'qemu'):
        require(name in groups and groups[name]['passed'], 'Missing passing group: ' + name)
    for item in suite['test_inputs']:
        require(hashlib.sha256((REPO / item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Test changed since execution: ' + item['file'])
    for item in groups['frontend']['inputs']:
        require(hashlib.sha256((REPO / item['file']).read_bytes()).hexdigest() == item['sha256'],
                'Frontend changed since execution: ' + item['file'])
    app = (ARCHIVE / 'app.bin').read_bytes()
    app_sha = hashlib.sha256(app).hexdigest()
    require(suite['app_sha256'] == app_sha and suite['source_sha256'] == manifest['source_sha256'],
            'Suite tested a different application/source archive')
    require(app == (BUILD / 'small_tv_reconstructed.bin').read_bytes(), 'Build and archive differ')
    generated = BUILD / 'verification-resources'
    subprocess.run([sys.executable, str(ROOT / 'tools/prepare_resources.py'), '--output', str(generated)], check=True)
    source = read(generated / 'source-manifest.json')
    require(source == read(ARCHIVE / 'source-manifest.json') and
            source['aggregate_sha256'] == manifest['source_sha256'], 'Production sources changed after build')
    require((generated / 'assets.bin').read_bytes() == (ARCHIVE / 'assets.bin').read_bytes(),
            'Generated assets differ from the archive')
    subprocess.run([sys.executable, str(ROOT / 'tests/artifact_test.py'),
                    '--output', str(generated / 'integrity.json')], check=True)
    integrity = read(generated / 'integrity.json')
    require(integrity['passed'] and integrity['app_sha256'] == app_sha, 'Artifact integrity failed')
    size = json.loads(subprocess.check_output([sys.executable, '-m', 'esp_idf_size', '--format', 'json2',
                                              str(BUILD / 'small_tv_reconstructed.map')], text=True))
    diram = next(row for row in size['layout'] if row['name'] == 'DIRAM')
    table = (ARCHIVE / 'partition-table.bin').read_bytes()
    partitions = {}
    for position in range(0, len(table), 32):
        entry = table[position:position + 32]
        if struct.unpack_from('<H', entry)[0] != 0x50aa:
            break  # MD5/footer and all bounds were independently checked above.
        _, _, _, _, length, label, _ = struct.unpack('<HBBII16sI', entry)
        partitions[label.split(b'\0')[0].decode()] = length
    symbols = read(ROOT / 'symbol-map.json')
    definitions = re.compile(r'(?m)^[A-Za-z_][\w \t*]*?\b(\w+)\s*\([^;{}]*\)\s*\{')
    function_count, marked_count = 0, 0
    for path in (ROOT / 'app').rglob('*.c'):
        text = path.read_text()
        for match in definitions.finditer(text):
            comment = text[match.end():].lstrip()
            require(comment.startswith('/*'), 'Missing entry comment: ' + match[1])
            function_count += 1
            if re.search(r'FIXED_FACTORY|FIXED_RECONSTRUCTION|REQUESTED_CHANGE', comment.split('*/', 1)[0]):
                marked_count += 1
    classic = groups['machine_classic']
    report = read(args.output) if args.output.exists() else {}
    report.update(target=manifest['target'], date=suite['finished_utc'][:10], sdk_revision=manifest['idf_revision'],
                  source_sha256=manifest['source_sha256'], app_sha256=app_sha, app_bytes=len(app),
                  app_partition_bytes=partitions['factory'], app_partition_free_bytes=partitions['factory'] - len(app),
                  media_bytes=partitions['assets'], original_routes=34, registered_routes=len(groups['native']['routes']),
                  reference_functions=len(symbols['functions']), named_globals=len(symbols['globals']),
                  named_local_parameter_aliases=sum(len(item['names']) for item in symbols['locals']),
                  host_result=f"PASS: {groups['native']['checks']} checks; all registered HTTP contracts",
                  asset_pack_matches_sanitized_exports=True, compiled_source_hashes_match_archive=True,
                  partition_table_md5_valid=True, original_flash_dump_unchanged=True,
                  static_diram_bytes=diram['used'], linker_diram_remaining_bytes=diram['free'],
                  runtime_memory_measured=False, hardware_tested=False, device_flashed=False, ota=False,
                  production_functions_with_entry_comments=function_count, production_functions_with_correction_markers=marked_count,
                  correction_markers_document='CORRECTION_MARKERS.md',
                  host_platform_scenarios=len(groups['platform']['cases']),
                  host_platform_checks=sum(row['checks'] for row in groups['platform']['cases']),
                  machine_classic_report='../qemu/parity/classic-validation.json',
                  machine_classic_cases=classic['renderer_cases'] if isinstance(classic['renderer_cases'], int) else len(classic['renderer_cases']),
                  machine_animation_transitions=classic.get('animation_transitions', len(classic.get('animation', {}).get('cases', []))),
                  machine_backlight_comparisons=groups['machine_control']['backlight']['comparisons'],
                  machine_glyph_geometry_checks=len(classic['glyph_geometry_checks']))
    weather = groups['machine_weather']
    require(weather['app_sha256'] == app_sha and weather['source_sha256'] == manifest['source_sha256'],
            'Weather gate tested different application/source inputs')
    report['machine_weather_report'] = '../qemu/parity/weather-render-validation.json'
    report['machine_weather_cases'] = sum(weather['case_counts'].values()) if 'case_counts' in weather else len(weather['cases'])
    calendar = groups['machine_calendar']
    require(calendar['app_sha256']==app_sha and calendar['source_sha256']==manifest['source_sha256'],
            'Calendar gate tested different application/source inputs')
    require(groups['qemu']['field_http']['passed'],'Real QEMU field update/scroll gate failed')
    report['machine_calendar_report'] = '../qemu/parity/calendar-validation.json'
    report['machine_calendar_cases'] = calendar['renderer_cases'] if 'renderer_cases' in calendar else len(calendar['cases'])
    report['qemu_field_report'] = '../qemu/field-http-validation.json'
    report['work_status'] = 'Reconstructed firmware; confirmed factory corrections are marked and tested'
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Verified application {app_sha}: {len(app)} bytes, {partitions["factory"] - len(app)} bytes free')
    print(f'Entry comments: {function_count}; correction markers: {marked_count}; DIRAM: {diram["used"]} bytes')


if __name__ == '__main__':
    main()
