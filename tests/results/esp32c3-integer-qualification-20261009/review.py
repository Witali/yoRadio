"""Replay formats, lifetime recovery and sustained TLS without hiding failures."""
import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'sources/tools/esp32c3_tests'))
from common import check_playback, check_recovery_heap, check_transitions, require, sha
from public_streams import no_runtime_faults
from staged_dma import summarize as dma_summary
from tls_records import record_evidence
from flow_windows import helper, strict_flow


def verdict(action):
    try:
        return dict(result='PASS', evidence=action())
    except (AssertionError, ValueError) as error:
        return dict(result='FAIL', reason=str(error))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'review.json')
    args = parser.parse_args()
    completed = json.loads((ROOT/'physical/phases.json').read_text())
    catalog = json.loads((ROOT/'case-catalog.json').read_text())
    initial = json.loads((ROOT/'physical/initial.json').read_text())
    result = dict(phases={}, missing=[],
        note='Measured acceptance is separate from full-window/startup DMA and acoustic continuity. Original failures are retained; CPU has no ceiling.')
    for label in ('matrix-https', 'transitions-switch', 'tls-record-grow'):
        phase = next((p for p in completed if p['name'] == label), None)
        if phase is None:
            result['missing'].append(label)
            continue
        folder = ROOT/'physical'/label
        data = {n:json.loads((folder/(n+'.json')).read_text()) for n in ('report', 'status', 'performance')}
        hashes = {n:sha((folder/(n+'.json')).read_bytes()) for n in data}
        report, batches, rows = data['report'], data['status'], data['performance']
        require(report['board']['app_elf_sha256'] == initial['candidate']['app_elf_sha256'], 'Unexpected test image')
        require(report['test_sources_sha256'] == initial['test_sources_sha256'], 'Test sources changed')
        require(report['host_clock'] == initial['host_clock'], 'Clock changed')
        requests = [json.loads(line) for line in (ROOT/'physical'/(label+'-request-phases.jsonl')).read_text().splitlines()]
        connections = [r for r in requests if r['phase'] == 'connect']
        item = dict(controller=phase, original=report['cases'],
            passed=sum(c['result']=='PASS' for c in report['cases']), total=len(report['cases']),
            runtime=verdict(lambda:no_runtime_faults(rows)), input_sha256=hashes,
            connections=len(connections), connection_failures=[r for r in connections if r['result']!='PASS'],
            request_failures=[r for r in requests if r['result']!='PASS'],
            max_connect_ms=max((r['ms'] for r in connections), default=None), checks=[])
        result['phases'][label] = item
        if label == 'matrix-https':
            cases = [c for c in report['cases'] if c['name'].startswith('https:')]
            names = [n for n in catalog if 'sequence' not in catalog[n]]
            require(len(cases) == 22 and len(batches) == 44, 'Incomplete format matrix')
            require([c['name'] for c in cases] == [f'https:{n}:{h}' for n in names for h in ('auto', catalog[n]['codec'])], 'Wrong matrix order')
            for index, case in enumerate(cases):
                name = case['name'].split(':')[1]
                play, eof = batches[2*index:2*index+2]
                def check(play=play, eof=eof, name=name):
                    require(play['case']==name and eof['case']==name+':eof', 'Wrong observation')
                    require(not play.get('interrupted') and not eof.get('interrupted'), 'Interrupted observation')
                    checked = check_playback(play['samples'], catalog[name])
                    require(any(not s['audio'] for s in eof['samples']), 'No stopped EOF observation')
                    return checked
                item['checks'].append(dict(name=case['name'], **verdict(check)))
        elif label == 'transitions-switch':
            for batch in batches:
                name = batch['case']
                if name.startswith('switch:'):
                    fixture = name.split(':', 2)[2]
                    item['checks'].append(dict(name=name, **verdict(lambda b=batch,n=fixture:check_playback(b['samples'], catalog[n]))))
                elif name in catalog and 'sequence' in catalog[name]:
                    item['checks'].append(dict(name=name, **verdict(lambda b=batch,n=name:check_transitions(b['samples'], [catalog[x] for x in catalog[n]['sequence']]))))
            require(sum(c['name'].startswith('switch:') for c in item['checks']) == 33, 'Incomplete station switching')
            switching = json.loads((folder/'switching.json').read_text())
            item['switching'] = switching
            item['heap_recovery'] = verdict(lambda:check_recovery_heap(switching['checkpoints'][0], switching['checkpoints'][-1]))
            item['scope'] = 'Saved REST formats and idle checkpoints replayed. WebSocket and stop-generation results remain original runner assertions.'
        else:
            selected = [b for b in batches if b['case']=='tls-record:grow']
            require(len(selected) == 1, 'Missing sustained TLS observation')
            batch = selected[0]
            measured = helper.summarize_batch('integer4', folder, batch, data, hashes)
            start, end = measured['measured_start'], measured['measured_end']
            measured.update(flow_decoder=strict_flow(rows, start, end, 'DEC'),
                flow_output=strict_flow(rows, start, end, 'STAGED_OUT'),
                whole_dma=verdict(lambda:dma_summary(rows, batch['started_at'], batch['ended_at'])),
                playback=verdict(lambda:check_playback(batch['samples'], catalog['hev2-44100-stereo'], warmup=5)),
                records=verdict(lambda:record_evidence(report['record_observations']['grow']['events'], 'grow')))
            measured['zero_dma_events'] = bool(measured.get('dma', {}).get('coverage_complete') and
                measured['dma']['delta']['q_overruns']==0 and measured['dma']['delta']['errors']==0)
            measured['digital_acceptance'] = bool(measured['acceptance_passed'] and measured['zero_dma_events'] and
                measured['flow_decoder']['complete'] and measured['flow_output']['complete'] and
                measured['playback']['result']=='PASS' and measured['records']['result']=='PASS')
            item['sustained'] = measured
            original = {c['name']:c for c in report['cases']}
            def qualified_recovery():
                require(original['idle-before']['result']=='PASS', 'Original initial-idle gate failed; no qualified baseline')
                require(original['idle-recovery']['result']=='PASS', 'Original idle-recovery gate failed')
                return check_recovery_heap(original['idle-before']['evidence']['samples'],
                                           original['idle-recovery']['evidence']['samples'])
            item['heap_recovery'] = verdict(qualified_recovery)
            idle = []
            for window in batches:
                if window['case'] != 'settled-idle': continue
                samples = []
                for row in rows:
                    if not window['started_at'] <= row['at'] <= window['ended_at']: continue
                    match = re.search(r'PERF CPU:.*heap=(\d+) largest=(\d+) tasks=(\d+)', row['line'])
                    if match:
                        samples.append(dict(zip(('heap','largest','tasks'),map(int,match.groups()))))
                idle.append(dict(interrupted=window.get('interrupted',False),samples=samples))
            item['raw_idle_observations'] = idle
            item['raw_idle_scope'] = 'Diagnostic CPU samples inside recorded idle windows; these do not repair failed HTTP or original recovery gates.'
    restore = ROOT/'physical/restoration.json'
    result['restoration'] = json.loads(restore.read_text()) if restore.exists() else None
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(missing=result['missing'], phases={n:dict(passed=p['passed'],total=p['total'],
        runtime=p['runtime'],failed_checks=[c for c in p['checks'] if c['result']!='PASS'],
        heap_recovery=p.get('heap_recovery'), connections=p['connections'],connection_failures=p['connection_failures'],
        digital_acceptance=p.get('sustained',{}).get('digital_acceptance'),
        dma=p.get('sustained',{}).get('dma',{}).get('delta'),whole_dma=p.get('sustained',{}).get('whole_dma'))
        for n,p in result['phases'].items()}),indent=2))


if __name__ == '__main__':
    main()
