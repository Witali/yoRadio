"""Independent replay of matched delivery pauses; retain failed gates."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'sources/tools/esp32c3_tests'))
from common import check_playback, check_recovery_heap, sha
from public_streams import no_runtime_faults
from staged_dma import summarize as dma_summary
from flow_windows import helper, strict_flow

def verdict(action):
    try: return dict(result='PASS', evidence=action())
    except (AssertionError, ValueError) as error: return dict(result='FAIL', reason=str(error))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT/'review.json')
    a = p.parse_args()
    completed = json.loads((ROOT/'physical/phases.json').read_text())
    catalog = json.loads((ROOT/'case-catalog.json').read_text())
    result = dict(phases={}, sustained=[], missing=[],
        note='CPU informational; zero measured DMA events required separately from original runner gates. No analog capture. Saved integer-clock pair with identical host pause positions and send-buffer request. Host writes are not board arrival times.')
    for label in ('control-before', 'expanded', 'control-after'):
        done = next((c for c in completed if c['name']==label), None)
        if done is None: result['missing'].append(label); continue
        folder = ROOT/'physical'/label
        data = {n: json.loads((folder/(n+'.json')).read_text()) for n in ('report', 'performance', 'status')}
        hashes = {n: sha((folder/(n+'.json')).read_bytes()) for n in data}
        rows, report = data['performance'], data['report']
        requests = [json.loads(line) for line in (folder/'request-phases.jsonl').read_text().splitlines()]
        connections = [r for r in requests if r['phase']=='connect']
        phase = dict(controller=done, original_cases=report['cases'],
            passed=sum(c['result']=='PASS' for c in report['cases']), total=len(report['cases']),
            runtime=verdict(lambda: no_runtime_faults(rows)),
            connections=len(connections), connection_failures=[r for r in connections if r['result']!='PASS'],
            max_connect_ms=max((r['ms'] for r in connections), default=None),
            all_request_failures=[r for r in requests if r['result']!='PASS'],
            recovery={k: verdict(lambda k=k: check_recovery_heap(report['idle']['before'], report['idle'][k])) for k in report['idle'] if k!='before'},
            idle=report['idle'], growth=[r for r in rows if 'PERF FLAC_INPUT:' in r['line']], input_sha256=hashes)
        result['phases'][label] = phase
        for batch in data['status']:
            if not batch['case'].startswith('load:'): continue
            measured = helper.summarize_batch(label, folder, batch, data, hashes)
            start, end = measured['measured_start'], measured['measured_end']
            name = batch['case'][5:]
            measured.update(variant=done['variant'],
                flow_decoder=strict_flow(rows, start, end, 'DEC'),
                flow_output=strict_flow(rows, start, end, 'STAGED_OUT'),
                whole_observed_dma=verdict(lambda: dma_summary(rows, batch['started_at'], end)),
                playback=verdict(lambda: check_playback(batch['samples'], catalog[name], minimum=max(5, int(180*.6)), warmup=5)))
            measured['zero_dma_events'] = bool(measured.get('dma', {}).get('coverage_complete') and
                measured['dma']['delta']['q_overruns']==0 and measured['dma']['delta']['errors']==0)
            measured['digital_acceptance'] = bool(measured['acceptance_passed'] and measured['flow_decoder']['complete'] and
                measured['flow_output']['complete'] and measured['zero_dma_events'] and measured['playback']['result']=='PASS')
            result['sustained'].append(measured)
    restored = ROOT/'physical/restoration.json'
    result['restoration'] = json.loads(restored.read_text()) if restored.is_file() else None
    a.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(missing=result['missing'], phases={k: {n: v[n] for n in ('passed', 'total', 'runtime', 'connection_failures', 'recovery')} for k, v in result['phases'].items()},
        sustained=[dict(phase=c['mode'], case=c['observation'], cpu=c['cpu']['busy_mean_percent'],
            dma=c.get('dma', {}).get('delta'), whole=c['whole_observed_dma'],
            input_wait=c['flow_decoder'].get('input'), empty_wait=c['flow_output'].get('empty'),
            telemetry=c['telemetry_complete'], digital_acceptance=c['digital_acceptance'],
            heap=c.get('heap'), rssi=c['median_rssi']) for c in result['sustained']]), indent=2))

if __name__ == '__main__': main()
