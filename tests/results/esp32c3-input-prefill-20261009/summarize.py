"""Replay initial-prefill evidence without changing original verdicts."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import statistics
import sys

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
sys.path.insert(0, str(REPO/'tools/esp32c3_tests'))
from heap_receive_correlation import inspect
from staged_dma import parse as parse_dma

HELPER = REPO/'tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py'
spec = importlib.util.spec_from_file_location('sustained_evidence', HELPER)
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
PHASES = ('hev2-ten-minutes','matrix','heavy-flac','transitions-faults-websocket','switch')
PREFILL = re.compile(r'PERF INPUT_PREFILL: generation=(\d+) elapsed_ms=(\d+) full=([01]) cancelled=([01])$')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'summary.json')
    args = parser.parse_args()
    summary = dict(phases={}, sustained=[], incomplete=[],
        scope='Original test gates retained. DMA queue overruns are service-delay evidence, '
              'not measured audible gaps. No analog capture or listening test.')
    for phase in PHASES:
        folder = ROOT/'physical'/phase
        paths = {n:folder/(n+'.json') for n in ('report','status','performance')}
        if not all(p.is_file() for p in paths.values()):
            summary['incomplete'].append(phase)
            continue
        data = {n:json.loads(p.read_text()) for n,p in paths.items()}
        hashes = {n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in paths.items()}
        prefill, malformed_prefill = [], []
        for row in data['performance']:
            if 'PERF INPUT_PREFILL:' not in row['line']:
                continue
            match = PREFILL.search(row['line'])
            if not match or row['line'].count('PERF ') != 1:
                malformed_prefill.append(row)
                continue
            prefill.append(dict(at=row['at'], **dict(zip(
                ('generation','elapsed_ms','full','cancelled'),map(int,match.groups())))))
        original = data['report']['cases']
        summary['phases'][phase] = dict(board=data['report']['board'],
            original_acceptance=original,
            passed=sum(c['result']=='PASS' for c in original), total=len(original),
            failures=[c for c in original if c['result']!='PASS'],
            prefill=prefill, malformed_prefill=malformed_prefill,input_sha256=hashes)
        for batch in data['status']:
            if not batch['case'].startswith('load:'):
                continue
            item = helper.summarize_batch(phase,folder,batch,data,hashes)
            case = batch['case'].removeprefix('load:')
            correlation = inspect(folder,case)
            item['paired_memory'] = correlation['paired']
            item['server'] = correlation['server']
            dma, damaged = [], []
            for row in data['performance']:
                try:
                    point = parse_dma(row)
                except ValueError as error:
                    damaged.append(dict(row=row,reason=str(error)))
                    continue
                if point and item['measured_start'] <= point['at'] <= item['measured_end']:
                    dma.append(point)
            item['damaged_dma'] = damaged
            item['dma_intervals'] = [dict(start=a['at'],end=b['at'],
                q_overruns=b['q_overruns']-a['q_overruns'],
                written_bytes=b['written_bytes']-a['written_bytes']) for a,b in zip(dma,dma[1:])]
            if len(dma)>=2:
                keys=('q_overruns','writes','written_bytes','write_us','errors')
                monotonic=all(b['at']>a['at'] and all(b[k]>=a[k] for k in keys)
                              for a,b in zip(dma,dma[1:]))
                item['readable_dma_endpoints']=dict(first=dma[0],last=dma[-1],
                    monotonic_readable_samples=monotonic,
                    delta={k:dma[-1][k]-dma[0][k] for k in keys} if monotonic else None,
                    note='Readable boundaries only; strict telemetry verdict remains unchanged.')
            reports = {c['name']:c for c in original}
            item['idle']={}
            for label, prefix in (('before','load-idle-baseline:'),('after','load-idle-recovery:')):
                rows=reports.get(prefix+case,{}).get('evidence',{}).get('samples',[])
                item['idle'][label]=({k:statistics.median(r[k] for r in rows)
                                     for k in ('heap','largest','tasks')} if rows else None)
            summary['sustained'].append(item)
    for name in ('restoration','restoration-failure','controller-failure','phases'):
        path=ROOT/'physical'/(name+'.json')
        if path.is_file(): summary['controller_'+name]=json.loads(path.read_text())
    summary['all_original_gates_passed']=(not summary['incomplete'] and
        all(p['total']>0 and p['passed']==p['total'] for p in summary['phases'].values()))
    summary['sources_sha256']={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (HELPER,Path(__file__),REPO/'tools/esp32c3_tests/heap_receive_correlation.py')}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(incomplete=summary['incomplete'],
        phases={k:dict(passed=v['passed'],total=v['total'],prefill_events=len(v['prefill']),
                      failures=[c['name'] for c in v['failures']]) for k,v in summary['phases'].items()},
        sustained=[dict(case=c['case'],original=c['original_gates_passed'],
                       telemetry=c['telemetry_complete'],cpu=c['cpu'].get('busy_mean_percent'),
                       heap=c.get('heap'),dma=c.get('dma',{}).get('delta')) for c in summary['sustained']]),indent=2))


if __name__=='__main__': main()
