"""Condense matched observations; preserve every original failed acceptance."""
import argparse
import json
from pathlib import Path
from statistics import median
import sys

from references import PRIOR, verify_references
verify_references()
sys.path.insert(0,str(PRIOR))
sys.path.insert(0,str(PRIOR/'sources/tools/esp32c3_tests'))
from common import check_recovery_heap
from eof_replay import verdict

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--summary', type=Path, default=ROOT/'summary.json')
parser.add_argument('--output', type=Path, default=ROOT/'comparison.json')
args = parser.parse_args()
summary = json.loads(args.summary.read_text())
assert not summary['incomplete']

def heap(samples):
    if not samples:
        return None
    return {key: median(row[key] for row in samples) for key in ('heap','largest','tasks')}

trials = []
for name, variant in (('control-1','0'),('expanded-1','4'),('expanded-2','4'),('control-2','0')):
    switch, eof, records = (summary['phases'][name+'-'+kind] for kind in ('switch','eof','records'))
    measured = next(row for row in summary['sustained'] if row['mode'] == name+'-records')
    def cross_phase_recovery(key):
        final = records['idle_heap'].get(key)
        assert final is not None, 'Missing original settled idle evidence'
        return check_recovery_heap(switch['switching']['checkpoints'][0], final)
    trials.append(dict(
        name=name, extra_slots=int(variant),
        original_passed=sum(row['passed'] for row in (switch,eof,records)),
        original_total=sum(row['total'] for row in (switch,eof,records)),
        original_failures=[c for row in (switch,eof,records) for c in row['failures']],
        switch_idle=[heap(c) for c in switch['switching']['checkpoints']],
        records_idle={key: heap(value) for key,value in records['idle_heap'].items()},
        cross_phase_recovery=[verdict(key,lambda key=key:cross_phase_recovery(key))
                              for key in ('idle-before','idle-recovery')],
        independent_formats=switch['independent_formats'],
        independent_eof=eof['independent_eof'],
        tls_record_observations=records['record_observations'],
        records_cpu_busy_percent=measured['cpu']['busy_mean_percent'],
        records_observation_interrupted=measured['interrupted'],
        records_observed_seconds=measured['seconds'],
        records_minimum_rssi=measured['minimum_rssi'],
        records_median_rssi=measured['median_rssi'],
        maximum_successful_status_request_ms=measured['maximum_http_ms'],
        records_heap=measured['heap'],
        records_telemetry_complete=measured['telemetry_complete'],
        decoder_flow_complete=measured['flow_decoder']['complete'],
        output_flow_complete=measured['flow_output']['complete'],
        selected_dma_events=measured['dma']['delta']['q_overruns'],
        selected_dma_errors=measured['dma']['delta']['errors'],
        whole_observed_dma_events=sum(e['overruns'] for e in measured['whole_observed_dma_events']),
        whole_observed_dma_errors=sum(e['errors'] for e in measured['whole_observed_dma_events']),
        runtime_review=[row for phase in (switch,eof,records) for row in phase['extended_runtime']['rows']],
        transport_failures=[row for phase in (switch,eof,records) for row in phase['transport_failures']],
    ))
result = dict(
    scope='Two fresh boots per variant in 0/4/4/0 order; no acoustic qualification or causal proof.',
    trials=trials,
    original_passed=sum(t['original_passed'] for t in trials),
    original_total=sum(t['original_total'] for t in trials),
    cross_phase_passed=sum(c['result']=='PASS' for t in trials for c in t['cross_phase_recovery']),
    cross_phase_total=sum(len(t['cross_phase_recovery']) for t in trials),
)
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
