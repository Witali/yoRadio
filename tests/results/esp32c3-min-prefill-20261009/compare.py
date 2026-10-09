"""Compare matched queue-profiling observations without upgrading their verdicts."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p / 'tools/esp32c3_tests/common.py').is_file())
BASE = REPO / 'tests/results/esp32c3-staged-flow-20261009'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--summary', type=Path, default=ROOT / 'summary.json')
parser.add_argument('--output', type=Path, default=ROOT / 'comparison.json')
args = parser.parse_args()

baseline_blob = (BASE / 'summary.json').read_bytes()
expected = json.loads((BASE / 'index.json').read_text())['files']['summary.json']
assert len(baseline_blob) == expected['bytes']
assert hashlib.sha256(baseline_blob).hexdigest() == expected['sha256']
baseline = json.loads(baseline_blob)
candidate_blob = args.summary.read_bytes()
candidate = json.loads(candidate_blob)
assert not baseline['incomplete'] and not candidate['incomplete']
assert candidate['controller_initial']['images']['control'] == baseline['controller_initial']['images']['profile']

def compact(case):
    original = next(c for c in case['original_acceptance'] if c['name'] == case['observation'])
    return dict(
        observation=case['observation'], phase=case['mode'],
        original_verdict=original['result'],
        telemetry_complete=case['telemetry_complete'], flow_complete=case['flow_complete'],
        seconds=case['seconds'], cpu_busy_percent=case['cpu']['busy_mean_percent'],
        heap=case['heap'], minimum_rssi=case['minimum_rssi'], median_rssi=case['median_rssi'],
        faults=case['fault_rows'], maximum_http_ms=case['maximum_http_ms'],
        selected_dma=case['dma']['delta'],
        whole_observed_dma_overruns=sum(r['overruns'] for r in case['whole_observed_dma_events']),
        flow_input=case['flow_decoder']['input'],
        flow_pcm_full=case['flow_decoder']['pcm'],
        flow_pcm_empty=case['flow_staged_output']['empty'],
        prefill=[r['line'] for r in case['prefill_rows']],
        first_full_pcm_seconds=(original.get('evidence') or {}).get('first_full_pcm_seconds'),
        stack_minimum_free=case['stack_minimum_free'])

before = {(c['mode'], c['observation']): c for c in baseline['cases'] if c['mode'].startswith('profile')}
comparisons = []
for case in candidate['cases']:
    prior = before.get((case['mode'], case['observation']))
    comparisons.append(dict(baseline=compact(prior) if prior else None, candidate=compact(case)))

result = dict(
    scope='Sequential physical observations; no randomized or acoustic qualification. Missing baselines remain null.',
    baseline_summary_sha256=expected['sha256'],
    candidate_summary_sha256=hashlib.sha256(candidate_blob).hexdigest(),
    baseline_image=baseline['controller_initial']['images']['profile'],
    candidate_image=candidate['controller_initial']['images']['profile'],
    comparisons=comparisons)
args.output.write_text(json.dumps(result, indent=2) + '\n')
for item in comparisons:
    after, prior = item['candidate'], item['baseline']
    print(after['phase'], after['observation'],
          'DMA selected:', prior['selected_dma']['q_overruns'] if prior else None,
          '->', after['selected_dma']['q_overruns'],
          'whole:', prior['whole_observed_dma_overruns'] if prior else None,
          '->', after['whole_observed_dma_overruns'],
          'CPU:', round(after['cpu_busy_percent'], 3))
