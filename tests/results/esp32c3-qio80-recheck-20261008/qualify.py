"""Attach the completed physical outcomes to the saved laboratory artifacts."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
summary = json.loads((root / 'summary.json').read_text())
assert summary['complete'] and summary['phases_complete'] and summary['restored']
for mode, variant in summary['variants'].items():
    artifact = Path('firmware/development/esp32c3-idf-6.1-r9a97-flash-' + mode + '80')
    result = 'QUALIFIED_WITHIN_LAB_SCOPE' if variant['qualified_within_scope'] else 'NOT_QUALIFIED'
    qualification = dict(
        result=result,
        physical_tests=True,
        laboratory_only=True,
        bus_mode_clock_image_crc='PASS',
        finite_file_matrix=variant['matrix_counts'],
        original_failures=variant['failures'],
        runtime=variant['runtime'],
        settings_preserved=variant['persistence'],
        original_firmware_restored=summary['restored'],
        restoration_recovery=summary['restoration_recovery'],
        acoustic_continuity_qualified=False,
        report='docs/ESP32C3_QIO80_RECHECK_20261008.md',
        evidence='tests/results/esp32c3-qio80-recheck-20261008',
        scope=summary['scope'])
    (artifact / 'qualification.json').write_text(json.dumps(qualification, indent=2) + '\n')
    path = artifact / 'manifest.json'
    manifest = json.loads(path.read_text())
    manifest['qualification'] = result + '; see qualification.json and physical recheck report'
    path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(mode, result)
