"""Summarize public-stream evidence, retaining failed/core-only cases as failures."""
import argparse
import json
from pathlib import Path
import re

from common import sha
from summarize_memory import summarize


def inspect(directory):
    paths = [directory/name for name in ('report.json', 'status.json', 'performance.json')]
    report, status, rows = [json.loads(p.read_text()) for p in paths]
    cases = [c for c in report['cases'] if c['name'].startswith(('https:', 'http:'))]
    # The runner deliberately reboots only after all playback/idle observations.
    # Exclude that saved-station playback; unexpected earlier resets invalidate
    # the one-to-one checkpoint count and must not be silently paired.
    boot = next((r['at'] for r in rows if r['line'].startswith('ESP-ROM:')), float('inf'))
    playback_rows = [r for r in rows if r['at'] < boot]
    adapted = dict(report, cases=[dict(c, name='memory-playback:'+c['name'].split(':', 1)[1])
                                 for c in cases])
    result = summarize(adapted, status, playback_rows)
    result['input_sha256'] = {p.name: sha(p.read_bytes()) for p in paths}
    result['source_sha256'] = sha(Path(__file__).read_bytes())
    by_name = {c['name'].split(':', 1)[1]: c for c in cases}
    for case in result['cases']:
        name = case['name'].removeprefix('memory-playback:')
        original = by_name[name]
        case.update(name=name, transport=original['name'].split(':', 1)[0],
                    reference=report['reference_probes'][name]['spec'],
                    observed_formats=sorted({s['format'] for batch in status if batch['case'] == name
                                             for s in batch['samples'] if s.get('audio')}),
                    acceptance=original)
    result['allocation_failures'] = [r for r in playback_rows if 'allocation failed' in r['line']]
    result['reset_banners'] = [r for r in rows if r['line'].startswith('rst:')]
    result['panic_or_capture_errors'] = [r for r in rows if re.search(
        r'assert failed|Guru Meditation|CORRUPT HEAP|PANIC registers:|serial capture interrupted', r['line'])]
    result['note'] = ('Read observed_formats together with the failure: core-only CPU is not full '
                      'HE-AAC CPU; full PCM can still fail allocation/heap budgets. A 60-second '
                      'live test is not a soak or a frozen PCM equivalence test.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = inspect(args.input)
    args.output.write_text(json.dumps(result, indent=2)+'\n', newline='\n')
    for case in result['cases']:
        print(case['name'], case['playback_result'], case['observed_formats'],
              case['busy_mean'], case['decode_mean'], case['minimum_free'], case['minimum_largest'])
