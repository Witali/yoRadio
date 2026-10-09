"""Replay physical PCM tail observations against unmodified serial evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/pcm_tail.py').is_file())
SOURCES = ROOT/'sources' if (ROOT/'sources/tools/esp32c3_tests').is_dir() else REPO
sys.path.insert(0, str(SOURCES/'tools/esp32c3_tests'))
from pcm_tail import terminal_records, check_submission


def summarize():
    folder = ROOT/'physical/short-pcm-tails'
    report = json.loads((folder/'report.json').read_text())
    observations = json.loads((folder/'status.json').read_text())
    rows = json.loads((folder/'performance.json').read_text())
    manifest = json.loads((ROOT/'fixtures/manifest.json').read_text())
    fixtures = {e['name']: e for e in manifest['fixtures']}
    assert len(fixtures) == 30
    for entry in fixtures.values():
        assert hashlib.sha256((ROOT/'fixtures'/entry['file']).read_bytes()).hexdigest() == entry['sha256']
    assert report['fixtures'] == manifest['fixtures']
    expected = ['warmup'] + [f'{protocol}:{e["name"]}'
                            for protocol in ('http','https') for e in manifest['fixtures']] + ['leave-stopped']
    assert [c['name'] for c in report['cases']] == expected
    assert len(observations) == 61
    measured = []
    previous = None
    for index, observation in enumerate(observations):
        end = observations[index+1]['started_at'] if index+1 < len(observations) else float('inf')
        window = [r for r in rows if observation['started_at'] <= r['at'] < end]
        terminals = terminal_records(window)
        assert len(terminals) == 1 and terminals[0] == observation['terminal']
        terminal = terminals[0]
        assert terminal['completion'] == 1 and terminal['result'] == 0
        assert observation['status']['audio'] is False
        case = report['cases'][index]
        if previous is None:
            assert case['evidence'] == dict(warmup=True)
        else:
            assert case['name'] == observation['protocol'] + ':' + observation['name']
            fixture = fixtures[observation['name']]
            result = check_submission(previous, terminal, fixture['frames'], fixture['rate'])
            assert result == case['evidence']
            measured.append(dict(name=case['name'], **result))
        previous = terminal
    return dict(board=report['board'], original_acceptance=report['cases'],
        total=len(report['cases']), passed=sum(c['result']=='PASS' for c in report['cases']),
        failures=[c for c in report['cases'] if c['result']!='PASS'],
        measured_cases=len(measured), measured=measured,
        input_frames=sum(c['input_frames'] for c in measured),
        output_frames=sum(c['output_frames'] for c in measured),
        submitted_bytes=sum(c['submitted_bytes'] for c in measured),
        source_rates=sorted({e['rate'] for e in fixtures.values()}),
        source_channels=sorted({e['channels'] for e in fixtures.values()}),
        source_frame_counts=sorted({e['frames'] for e in fixtures.values()}),
        input_sha256={name:hashlib.sha256((folder/name).read_bytes()).hexdigest()
                      for name in ('report.json','status.json','performance.json')},
        scope='Driver-accepted frame counts and EOF status, not physical DMA drain or analog PCM capture.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'short-summary.json')
    args = parser.parse_args()
    result = summarize()
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('original_acceptance','measured')},indent=2))
