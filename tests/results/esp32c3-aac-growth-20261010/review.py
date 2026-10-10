"""Replay AAC-growth fixture hashes, physical checks and exact restoration offline."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p / 'tools/esp32c3_tests/common.py').is_file())
sys.path.insert(0, str(ROOT / 'test-sources/tools/esp32c3_tests'))
from common import check_recovery_heap
from production_health import check_health
from public_file_acceptance import check_finite_playback
from audio_test_server.generate_aac_growth import generate

sha = lambda data: hashlib.sha256(data).hexdigest()
read = lambda name: json.loads((ROOT / name).read_text())


def review():
    initial = read('physical/initial.json')
    report = read('physical/files/report.json')
    manifest = read('manifest.json')
    references = read('references.json')
    assert sha((ROOT / 'physical.py').read_bytes()) == initial['controller_sha256']
    assert sha((ROOT / 'references.json').read_bytes()) == initial['reference_sha256']
    for name, digest in initial['test_sources_sha256'].items():
        assert sha((ROOT / 'test-sources' / name).read_bytes()) == digest, name
    assert manifest == report['fixtures'] and references == report['references']
    cases = {c['name']: c for c in report['cases']}
    assert len(cases) == len(report['cases']) == 15
    assert all(c['result'] == 'PASS' for c in cases.values())
    assert read('physical/phase.json')['code'] == 0
    generated = {}
    for name, info in manifest.items():
        source = REPO / 'tests/fixtures/aac_stream_format' / (name + '.aac')
        assert sha(source.read_bytes()) == info['source_sha256']
        baseline, growth, metadata = generate(source.read_bytes())
        assert all(info[key] == value for key, value in metadata.items())
        assert references[name]['baseline'] == references[name]['growth']
        for label, data in (('baseline', baseline), ('growth', growth)):
            assert info['files'][label] == dict(bytes=len(data), sha256=sha(data))
        frame_shapes = []
        for label in ('baseline', 'growth'):
            trace = [[int(v) for v in line.split()] for line in
                     (ROOT / name / (label + '.frames')).read_text().splitlines()]
            assert len(trace) == info['frames']
            frame_shapes.append([row[1:] for row in trace])
        assert frame_shapes[0] == frame_shapes[1]
        assert (ROOT / name / 'baseline.state').read_bytes() == (ROOT / name / 'growth.state').read_bytes()
        generated[name] = dict(frames=info['frames'], target_frame_bytes=info['target_frame_bytes'],
            expected_capacity_bytes=info['expected_capacity_bytes'], reference_pcm_unchanged=True)
    health = read('physical/files/health.json')
    rows = []
    labels = {'LC': 'AAC PCM', 'HE-AAC': 'HE-AAC ', 'HE-AACv2': 'HE-AACv2 '}
    for batch in read('physical/files/status.json'):
        if batch['case'].startswith('idle:'):
            continue
        name = batch['case']; source = name.rsplit('-', 1)[0]
        stream = references[source]['growth']['ffprobe']['streams'][0]
        spec = dict(seconds=manifest[source]['seconds'], rate=int(stream['sample_rate']),
            channels=int(stream['channels']), bits=16, label=labels[stream['profile']], container_label='AAC')
        playback = check_finite_playback(batch['samples'], spec)
        assert playback == cases[name]['evidence']['playback']
        start = batch['started_at']
        steady = [h for h in health if start + playback['first_playback_seconds'] + 3 <= h['at'] <=
                  start + playback['first_stopped_seconds'] - 1]
        checked = check_health(steady)
        assert len(steady) >= 10 and checked == cases[name]['evidence']['health']
        assert checked['minimum_heap'] >= 16384 and checked['minimum_largest'] >= 8192
        windows = {}
        for label, lo, hi in (('before_growth', 8, 13), ('after_growth', 23, 30)):
            window = [s for s in steady if lo <= s['at'] - start <= hi]
            assert len(window) >= 5
            windows[label] = {k: statistics.median(s[k] for s in window) for k in ('heap', 'largest', 'tasks')}
        assert windows == cases[name]['evidence']['windows']
        rows.append(dict(case=name, playback=playback, health=checked, windows=windows))
    assert len(rows) == 6
    idle = {}
    for name, samples in report['idle'].items():
        check_recovery_heap(report['idle']['initial'], samples)
        idle[name] = {k: statistics.median(s[k] for s in samples) for k in ('heap', 'largest', 'tasks')}
    lifetime = check_health(health)
    assert lifetime == cases['lifetime-health']['evidence']
    restored = read('physical/restoration.json')
    assert restored['identity']['app_elf_sha256'] == initial['quiet']['app_elf_sha256']
    assert all(restored['persistence'].values())
    assert len(restored['states']) == 3 and all(not s['audio'] for s in restored['states'])
    for variant, image in (('esp32c3-idf-6.1-r9a97-quiet-mpi-health', initial['candidate']),
                           ('esp32c3-idf61-listen-48k', initial['quiet'])):
        app = (REPO / 'firmware/development' / variant / 'app.bin').read_bytes()
        assert sha(app) == image['sha256'] and app[176:208].hex() == image['app_elf_sha256']
    return dict(passed=15, total=15, generated=generated, files=rows, lifetime=lifetime,
        idle=idle, restoration=restored['identity'], settings_preserved=restored['persistence'],
        scope=report['scope'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if (ROOT / 'index.json').exists():
        for name, entry in read('index.json')['files'].items():
            path = (ROOT / name).resolve()
            assert path.is_relative_to(ROOT)
            data = path.read_bytes()
            assert len(data) == entry['bytes'] and sha(data) == entry['sha256'], name
    result = review()
    if (ROOT / 'review.json').exists():
        assert result == read('review.json')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, indent=2) + '\n')
    print('PASS: regenerated fixture hashes, 15 physical checks and exact image/settings restoration')
