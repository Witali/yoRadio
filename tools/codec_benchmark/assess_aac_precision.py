#!/usr/bin/env python3
"""Apply today's accuracy gate to unchanged, validated historical measurements."""
import argparse
import json
from pathlib import Path
import aac_precision as policy
import run_aac_bfp16 as common
import run_aac_qmf_storage as qmf
import run_aac_ps_storage as ps
import run_aac_area_storage as areas

ROOT = Path(__file__).resolve().parents[2]
NAMES = ('synthetic', 'abba64', 'groovesalad16', 'groovesalad32', 'groovesalad64', 'groovesalad128')
SOURCES = {
    'qmf': ('esp32c3-aac-storage18-20261002/qmf', qmf.parse_log, range(1, 6)),
    'ps': ('esp32c3-aac-storage18-20261002/ps', ps.parse_log, range(1, 6)),
    'other_arrays': ('esp32c3-aac-area-storage-20261002', areas.parse_log, range(1, 9)),
}


def assess():
    rows, provenance = [], {}
    for kind, (directory, parser, variants) in SOURCES.items():
        results = []
        for name in NAMES:
            path = ROOT/'tests/results'/directory/name
            saved = json.loads((path/'result.json').read_text())
            parsed = parser((path/'qemu.log').read_text())
            if any(saved[k] != value for k, value in parsed.items()):
                raise ValueError('Saved evidence differs from log: '+str(path))
            if common.sha256(path/'qemu.log') != saved['provenance']['qemu_log_sha256']:
                raise ValueError('Changed evidence log: '+str(path))
            for file in ('result.json', 'qemu.log'):
                provenance[(path/file).relative_to(ROOT).as_posix()] = common.sha256(path/file)
            results.append(saved)
        for variant in variants:
            measured = [r for d in results for r in d['runs'] if r['variant'] == variant]
            maximum = max(max(r['max_l'], r['max_r']) for r in measured)
            rows.append(dict(kind=kind, variant=variant,
                name=areas.AREAS[variant] if kind=='other_arrays' else qmf.FORMATS[variant],
                paired_comparisons=len(measured), max_pcm_error_lsb=maximum,
                production_precision_limit_lsb=policy.PRODUCTION_LIMIT,
                production_precision_pass=maximum <= policy.PRODUCTION_LIMIT,
                development_precision_pass=maximum <= policy.DEVELOPMENT_LIMIT,
                production_qualified=False,
                note='Accuracy on the retained corpus only; allocation, speed and full-format gates remain separate.'))
    return dict(production_precision_limit_lsb=policy.PRODUCTION_LIMIT,
                development_precision_limit_lsb=policy.DEVELOPMENT_LIMIT,
                policy_file=policy.POLICY_FILE.relative_to(ROOT).as_posix(),
                policy_sha256=common.sha256(policy.POLICY_FILE),
                historical_files_modified=False, rows=rows, evidence_sha256=provenance)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = assess()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    for row in result['rows']:
        print(row['kind'], row['name'], row['max_pcm_error_lsb'],
              'PASS' if row['production_precision_pass'] else 'FAIL')
