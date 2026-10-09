"""Replay TLS/OTA gates; preserve failures and distinguish telemetry from playback."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import statistics
import sys

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
SOURCES=ROOT/'sources' if (ROOT/'sources/tools').is_dir() else REPO
sys.path.insert(0,str(SOURCES/'tools/esp32c3_tests'))
from heap_receive_correlation import paired_metrics
from tls_records import record_evidence
from ota_diagnostic import serial_health
from common import matches
from staged_dma import parse as parse_dma

HELPER=SOURCES/'tests/results/esp32c3-qio80-recheck-20261008/sustained_summary.py'
spec=importlib.util.spec_from_file_location('sustained_evidence',HELPER)
helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
PHASES=('records-short','records-long','framing','certificate-rejection','ota','records-after-ota')


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'summary.json')
    args=parser.parse_args()
    path=ROOT/'physical/phases.json'
    completed=json.loads(path.read_text()) if path.is_file() else []
    phases={p['name']:p for p in completed}
    summary=dict(phases={},sustained=[],incomplete=[],
        scope='Original gates, strict CPU/DMA replay and TLS record evidence. No analog capture.')
    for name in PHASES:
        folder=ROOT/'physical'/name
        if name not in phases:
            summary['incomplete'].append(name);continue
        paths={key:folder/(key+'.json') for key in ('report','performance','status')}
        data={key:json.loads(p.read_text()) for key,p in paths.items() if p.is_file()}
        hashes={key:sha(p) for key,p in paths.items() if p.is_file()}
        if not all(k in data for k in ('report','performance')):
            summary['incomplete'].append(name);continue
        original=data['report']['cases']
        item=dict(board=data['report']['board'],original_acceptance=original,
            passed=sum(c['result']=='PASS' for c in original),total=len(original),
            failures=[c for c in original if c['result']!='PASS'],
            controller=phases[name],input_sha256=hashes)
        summary['phases'][name]=item
        if name.startswith('records-'):
            timing=ROOT/'physical'/(name+'-request-phases.jsonl')
            if timing.is_file():
                requests=[json.loads(line) for line in timing.read_text().splitlines()]
                item['transport']=dict(source_sha256=sha(timing),
                    requests=max((r['request'] for r in requests),default=0),
                    failures=[r for r in requests if r['result']!='PASS'],
                    max_ms_by_phase={phase:max(r['ms'] for r in requests if r['phase']==phase)
                                     for phase in sorted({r['phase'] for r in requests})})
            item['pacing_ratio']=data['report']['pacing_ratio']
            item['record_observations']={}
            for mode,observation in data['report'].get('record_observations',{}).items():
                try:
                    result=record_evidence(observation['events'],mode)
                    if any(e.get('pacing_ratio')!=item['pacing_ratio'] for e in observation['events']):
                        raise ValueError('Mismatched pacing evidence')
                    result.update(result='PASS',pacing_ratio=item['pacing_ratio'])
                except (AssertionError,ValueError) as error:
                    result=dict(result='FAIL',reason=str(error))
                item['record_observations'][mode]=result
            reports={c['name']:c for c in original}
            item['idle']={}
            for label in ('idle-before','idle-recovery'):
                samples=reports.get(label,{}).get('evidence',{}).get('samples',[])
                item['idle'][label]=({k:statistics.median(r[k] for r in samples)
                                      for k in ('heap','largest','tasks')} if samples else None)
            for batch in data.get('status',[]):
                if not batch['case'].startswith('tls-record:'): continue
                result=helper.summarize_batch(name,folder,batch,data,hashes)
                result['prefill_rows']=[r for r in data['performance']
                    if batch['started_at']-1<=r['at']<=batch['ended_at'] and 'PERF INPUT_PREFILL:' in r['line']]
                try:
                    points=[p for row in data['performance'] if (p:=parse_dma(row)) is not None
                            and batch['started_at']<=p['at']<=batch['ended_at']]
                    result['dma_service_events']=[dict(start=a['at'],end=b['at'],
                        overruns=b['q_overruns']-a['q_overruns'],errors=b['errors']-a['errors'])
                        for a,b in zip(points,points[1:]) if b['q_overruns']!=a['q_overruns'] or b['errors']!=a['errors']]
                except ValueError as error:
                    result['dma_service_events_error']=str(error)
                result['selected_dma_zero']=result['telemetry_complete'] and all(
                    result.get('dma',{}).get('delta',{}).get(k)==0 for k in ('q_overruns','errors'))
                try:
                    result['paired_memory']=paired_metrics(data['performance'],result['measured_start'],result['measured_end'])
                except (ValueError,TypeError) as error:
                    result['paired_memory']=dict(metrics_available=False,issues=[str(error)])
                summary['sustained'].append(result)
        elif name=='ota':
            health=serial_health(data['performance'])
            assert health==json.loads((folder/'serial-health.json').read_text())
            item['serial_health']=health
            extra=[r for r in data['performance'] if re.search(
                r'allocation failed|decode (?:error|failed)|TLS failure:',r['line'])]
            item['allocation_decoder_tls_faults']=extra
            item['extended_runtime_review']=dict(
                result='REVIEW_REQUIRED' if extra else 'PASS',
                note='Keep original serial-health verdict; generic TLS rows need error codes and reboot timing.')
            playing=next((c for c in original if c['name']=='ota:while-playing'),{})
            state=playing.get('evidence',{}).get('playback_before',{})
            item['full_hev2_before_ota']=matches(state,dict(rate=44100,channels=2,bits=16,label='HE-AACv2 '))
            capture=json.loads((folder/'capture.json').read_text())
            item['playback_transport']=capture['transport']
            item['tls_server_events']=capture['server_events']
    for name in ('initial','installed','fractional-clock','phases','settings-after-tests',
                 'restoration','restoration-failure','controller-failure'):
        path=ROOT/'physical'/(name+'.json')
        if path.is_file(): summary['controller_'+name]=json.loads(path.read_text())
    summary['all_original_gates_passed']=not summary['incomplete'] and all(
        p['passed']==p['total'] and p['total']>0 and p['controller']['code']==0
        for p in summary['phases'].values())
    summary['sources_sha256']={str(p.relative_to(REPO)):sha(p) for p in
        (Path(__file__),HELPER,SOURCES/'tools/esp32c3_tests/heap_receive_correlation.py')}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(incomplete=summary['incomplete'],phases={n:dict(
        passed=p['passed'],total=p['total'],failures=[c['name'] for c in p['failures']])
        for n,p in summary['phases'].items()},sustained=[dict(phase=c['mode'],case=c['observation'],
        telemetry=c['telemetry_complete'],cpu=c['cpu'].get('busy_mean_percent'),heap=c.get('heap'),
        dma=c.get('dma',{}).get('delta'),dma_unavailable=c.get('dma_unavailable'))
        for c in summary['sustained']]),indent=2))


if __name__=='__main__': main()
