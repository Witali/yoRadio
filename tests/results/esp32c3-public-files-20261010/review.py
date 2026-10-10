"""Offline review: preserve original verdicts and separately replay the correction."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p / 'tools/esp32c3_tests/common.py').is_file())
sys.path.insert(0, str(ROOT / 'test-sources/tools/esp32c3_tests'))
from common import Failure, check_recovery_heap, matches
from production_health import check_health
from public_file_acceptance import check_finite_playback as original_check

module_spec = importlib.util.spec_from_file_location('corrected_file_check',
    ROOT / 'corrected-sources/tools/esp32c3_tests/public_file_acceptance.py')
corrected = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(corrected)


def read(name):
    return json.loads((ROOT / name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review():
    initial = read('physical/initial.json')
    report = read('physical/files/report.json')
    restore = read('physical/restoration.json')
    reference = read('reference/references.json')
    assert sha(ROOT / 'physical.py') == initial['controller_sha256']
    for name, digest in initial['test_sources_sha256'].items():
        assert sha(ROOT / 'test-sources' / name) == digest, name
    assert sha(ROOT / 'reference/references.json') == initial['reference_sha256']
    assert initial['reference_sha256'] == report['reference_manifest_sha256']
    assert report['references'] == reference
    assert report['image'] == initial['candidate']
    for variant, image in (
        ('esp32c3-idf-6.1-r9a97-quiet-mpi-health', initial['candidate']),
        ('esp32c3-idf61-listen-48k', initial['quiet']),
    ):
        app = REPO / 'firmware/development' / variant / 'app.bin'
        assert sha(app) == image['sha256']
        assert app.read_bytes()[176:208].hex() == image['app_elf_sha256']
    assert restore['identity']['app_elf_sha256'] == initial['quiet']['app_elf_sha256']
    assert all(restore['persistence'].values())
    assert len(restore['states']) == 3 and all(not s['audio'] for s in restore['states'])
    assert read('physical/phase.json')['code'] == 1  # The two original failures remain.
    cases = {c['name']: c for c in report['cases']}
    assert len(cases) == len(report['cases']) == 15
    failures = {n: c['reason'] for n, c in cases.items() if c['result'] == 'FAIL'}
    assert failures == {'https:opus:auto': 'Wrong decoded file format',
                        'https:vorbis:vorbis': 'Wrong decoded file format'}
    health = read('physical/files/health.json')
    rows = []
    for batch in read('physical/files/status.json'):
        name = batch['case']
        if not name.startswith('https:'):
            continue
        spec = reference['sources'][name.split(':')[1]]['spec']
        samples = batch['samples']
        try:
            prior = original_check(samples, spec)
        except Failure as error:
            assert cases[name]['result'] == 'FAIL' and str(error) == cases[name]['reason']
        else:
            assert cases[name]['result'] == 'PASS'
            assert prior == cases[name]['evidence']['playback']
        played = corrected.check_finite_playback(samples, spec)
        steady = [r for r in health if
            batch['started_at'] + played['first_playback_seconds'] + 3 <= r['at'] <=
            batch['started_at'] + played['first_stopped_seconds'] - 1]
        assert len(steady) >= 10
        assert min(r['heap'] for r in steady) >= 16384
        assert min(r['largest'] for r in steady) >= 8192
        for key, tolerance in (('heap', 2048), ('largest', 4096)):
            assert statistics.median(r[key] for r in steady[:3]) - statistics.median(
                r[key] for r in steady[-3:]) <= tolerance
        rows.append(dict(case=name, original=cases[name]['result'],
            corrected_offline='PASS', playback=played, health=check_health(steady),
            initial_unset_metadata=[s for s in samples if s['audio'] and not matches(s, spec)]))
    assert len(rows) == 6
    recovery = {}
    for name, samples in report['idle'].items():
        check_health(samples)
        check_recovery_heap(report['idle']['initial'], samples)
        recovery[name] = {key: statistics.median(s[key] for s in samples)
                          for key in ('heap', 'largest', 'tasks')}
    for item in reference['sources'].values():
        assert item['tls_verify'] is True and item['url'].startswith('https://')
        assert item['resolved_url'] == item['url']
        assert abs(item['decoded_frames'] / item['spec']['rate'] - item['spec']['seconds']) < 1e-6
    return dict(original_passed=13, original_total=15, original_failures=failures,
        corrected_offline_files=rows, lifetime=check_health(health), idle=recovery,
        restoration=restore['identity'], settings_preserved=restore['persistence'],
        scope='Offline replay of recorded format/duration/EOF and health; no new board run or PCM/analog continuity measurement')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    index_path = ROOT / 'index.json'
    if index_path.exists():
        for name, entry in read('index.json')['files'].items():
            path = (ROOT / name).resolve()
            assert path.is_relative_to(ROOT)
            assert path.stat().st_size == entry['bytes'] and sha(path) == entry['sha256'], name
    result = review()
    if (ROOT / 'review.json').exists():
        assert result == read('review.json')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, indent=2) + '\n')
    print('PASS: original failures retained, six corrected file checks, lifetime health and image/settings restoration')
