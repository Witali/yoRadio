"""Replay minimum-prefill TLS/EOF/OTA without hiding original failures."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'sources/tools/esp32c3_tests'))
from common import check_playback, check_recovery_heap, check_certificate_rejection, matches
from ota_diagnostic import serial_health
from tls_records import record_evidence
from staged_dma import parse as parse_dma
from flow_windows import helper, strict_flow
from eof_replay import verdict, eof_evidence

PHASES = ('framing','certificate-rejection','eof-https-all','ota','records-after-ota')
FAULT = re.compile(r'allocation failed|decode (?:error|failed)|assert failed|Guru Meditation|'
    r'CORRUPT HEAP|PANIC|serial capture interrupted|Runtime watchdog timeout|'
    r'PERF watchdog: task_timeouts=[1-9][0-9]*\b|task_wdt: Task watchdog got triggered')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def ota_reset_review(timeline, resets):
    windows=[]
    for name in ('ota:roundtrip:1','ota:roundtrip:2','ota:while-playing','ota:slow','restore-saved-station'):
        start_action=name+(':reboot-request' if name=='restore-saved-station' else ':upload')
        starts=[r['at'] for r in timeline if r['action']==start_action and r['event']=='begin']
        ends=[r['at'] for r in timeline if r['action']==name+':verify-boot' and r['event']=='returned']
        if len(starts)==len(ends)==1: windows.append(dict(action=name,start=starts[0],end=ends[0]))
    reviewed=[]
    for row in resets:
        owners=[w['action'] for w in windows if w['start']<=row['at']<=w['end']]
        software_reset=bool(re.match(r'^rst:0xc \((?:RTC_SW_CPU_RST|SW_CPU)\),boot:',row['line']))
        reviewed.append(dict(row=row,actions=owners,expected=len(owners)==1 and software_reset))
    return dict(windows=windows,rows=reviewed,
                result='REVIEW_REQUIRED' if any(not r['expected'] for r in reviewed) else 'PASS',
                note='Host-received reset banners inside explicit upload/reboot intervals; no inference for missing banners.')


def framing_replay(data, catalog):
    results = []
    for batch in data['status']:
        mode = batch['case'].removeprefix('framing:')
        def check():
            assert not batch.get('interrupted'), 'Interrupted observation'
            events = data['report']['observations'][mode]
            assert len(events) == 1
            event = events[0]
            assert event['complete'] and 'error' not in event
            assert event['dropped_records'] == event['dropped_writes'] == 0
            spec = catalog[event['fixture']]
            assert event['fixture_sha256'] == spec['sha256']
            samples = batch['samples']
            full = [s for s in samples if matches(s,spec)]
            assert len(full) >= 3
            assert all(matches(s,spec) for s in samples if s['seconds'] >= full[0]['seconds'] and s['audio'])
            expected = 'stream read failed' if mode in ('length-short','chunked-short','close-raw') else 'stream ended'
            assert len(samples) >= 3 and all(not s['audio'] and s['format'] == expected and
                not s['pcm_sample_rate'] and not s['pcm_channels'] for s in samples[-3:])
            return dict(terminal=expected, full_format_samples=len(full))
        results.append(verdict(mode,check))
    return results


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=ROOT/'summary.json')
    args = p.parse_args()
    catalog = json.loads((ROOT/'case-catalog.json').read_text())
    phase_path = ROOT/'physical/phases.json'
    completed = json.loads(phase_path.read_text()) if phase_path.exists() else []
    done = {p['name']:(ROOT/'physical',p) for p in completed}
    continuation = ROOT/'continuation/phases.json'
    if continuation.exists():
        for phase in json.loads(continuation.read_text()):
            assert phase['name'] not in done, 'Do not replace earlier failed results'
            done[phase['name']] = (ROOT/'continuation',phase)
    summary = dict(scope='Original gates and independent replay; no acoustic qualification.',
                   phases={}, sustained=[], incomplete=[])
    for name in PHASES:
        if name not in done:
            summary['incomplete'].append(name)
            continue
        capture,phase = done[name]
        folder = capture/name
        paths = {n:folder/(n+'.json') for n in ('report','performance','status')}
        data = {n:json.loads(p.read_text()) for n,p in paths.items() if p.exists()}
        hashes = {n:sha(p) for n,p in paths.items() if p.exists()}
        original = data['report']['cases']
        faults = [r for r in data['performance'] if FAULT.search(r['line']) or
            (name!='ota' and re.match(r'^(?:ESP-ROM:|rst:|waiting for download)',r['line']))]
        tls = [r for r in data['performance'] if 'TLS failure:' in r['line']]
        item = dict(controller=phase, capture_directory=capture.name, board=data['report']['board'], input_sha256=hashes,
            original_acceptance=original, passed=sum(c['result']=='PASS' for c in original), total=len(original),
            failures=[c for c in original if c['result']!='PASS'], runtime_faults=faults, tls_rows=tls,
            runtime_review='REVIEW_REQUIRED' if faults or (tls and name not in ('framing','certificate-rejection')) else 'PASS',
            tls_scope='Intentional TLS negatives need their own original and independent gates.' if name in ('framing','certificate-rejection') else 'Unexpected TLS rows retained for review.')
        summary['phases'][name] = item
        trace = capture/(name+'-request-phases.jsonl')
        if trace.exists():
            rows = [json.loads(line) for line in trace.read_text().splitlines()]
            item['transport'] = dict(sha256=sha(trace), failures=[r for r in rows if r['result']!='PASS'],
                failed_requests=sorted({r['request'] for r in rows if r['result']!='PASS'}))
        if name == 'framing':
            item['independent_framing'] = framing_replay(data,catalog)
            item['tls_context'] = []
            for row in tls:
                batches = [b['case'] for b in data['status'] if b['started_at']<=row['at']<=b['ended_at']]
                expected = (len(batches)==1 and batches[0] in ('framing:length-short','framing:chunked-short','framing:close-raw') and
                    row['line']=='TLS failure: component=esp-tls-mbedtls operation=read mbedtls_return=-29312')
                item['tls_context'].append(dict(row=row, observations=batches, expected_incomplete_response_eof=expected))
            if any(not c['expected_incomplete_response_eof'] for c in item['tls_context']): item['runtime_review']='REVIEW_REQUIRED'
        elif name == 'certificate-rejection':
            def check_rejection_only():
                assert len(data['status'])==1
                batch=data['status'][0]
                assert batch['case']=='untrusted-tls' and not batch.get('interrupted')
                assert batch['ended_at']-batch['started_at']>=12
                assert batch['samples'] and all(not r['audio'] for r in batch['samples'])
                errors=[e['reason'] for e in data['report']['tls_events'] if e['mode']=='tls-handshake-failure']
                check_certificate_rejection(errors,data['performance'])
                return dict(samples=len(batch['samples']),alerts=errors,
                    scope='Certificate rejection only. HTTP recovery and cleanup remain failed.')
            item['rejection_only_replay']=verdict('certificate-rejection-only',check_rejection_only)
        elif name == 'eof-https-all':
            names = list(data['report']['fixture_hashes'])
            expected = ['eof:https:'+n+':'+hint for n in names for hint in ('auto',catalog[n]['codec'])]
            item['expected_order'] = [c['name'] for c in original] == expected+['restore-board']
            item['fixture_hashes_match'] = data['report']['fixture_hashes'] == {n:catalog[n]['sha256'] for n in catalog}
            item['eof_replay'] = []
            item['format_replay'] = []
            for i,n in enumerate(n for n in names for _ in range(2)):
                item['eof_replay'].append(verdict(expected[i],lambda i=i,n=n:
                    eof_evidence(data['status'][2*i],data['status'][2*i+1],n)))
                item['format_replay'].append(verdict(expected[i],lambda i=i,n=n:
                    check_playback(data['status'][2*i]['samples'],catalog[n])))
        elif name == 'ota':
            health = serial_health(data['performance'])
            assert health == json.loads((folder/'serial-health.json').read_text())
            item['serial_health'] = health
            timeline = data['report']['timeline']
            item['timeline'] = timeline
            item['resets'] = [r for r in data['performance'] if r['line'].startswith('rst:')]
            item['reset_review'] = ota_reset_review(timeline,item['resets'])
            if item['reset_review']['result']!='PASS': item['runtime_review']='REVIEW_REQUIRED'
            item['tls_context'] = []
            for r in tls:
                previous = [e for e in timeline if e['at'] <= r['at']]
                following = [e for e in timeline if e['at'] > r['at']]
                resets = [e for e in item['resets'] if e['at'] >= r['at']]
                item['tls_context'].append(dict(row=r, previous_action=previous[-1] if previous else None,
                    next_action=following[0] if following else None,
                    seconds_before_next_reset=resets[0]['at']-r['at'] if resets else None))
            case = next(c for c in original if c['name']=='ota:while-playing')
            item['full_hev2_before_ota'] = matches(case.get('evidence',{}).get('playback_before',{}),catalog['hev2-44100-stereo'])
            capture = json.loads((folder/'capture.json').read_text())
            item['transport_kind'] = capture['transport']
            item['tls_server_events'] = capture['server_events']
        elif name == 'records-after-ota':
            item['record_replay'] = {mode:verdict(mode,lambda mode=mode,obs=obs:record_evidence(obs['events'],mode))
                for mode,obs in data['report']['record_observations'].items()}
            item['pacing_ratio'] = data['report']['pacing_ratio']
            cases = {c['name']:c for c in original}
            item['heap_replay'] = verdict('idle-recovery',lambda:check_recovery_heap(
                cases['idle-before']['evidence']['samples'],cases['idle-recovery']['evidence']['samples']))
            for batch in data['status']:
                if not batch['case'].startswith('tls-record:'): continue
                measured = helper.summarize_batch(name,folder,batch,data,hashes)
                start,end = measured['measured_start'],measured['measured_end']
                measured['flow_decoder'] = strict_flow(data['performance'],start,end,'DEC')
                measured['flow_output'] = strict_flow(data['performance'],start,end,'STAGED_OUT')
                points = [p for r in data['performance'] if (p:=parse_dma(r)) is not None and batch['started_at']<=p['at']<=end]
                measured['whole_dma_events'] = [dict(start=a['at'],end=b['at'],overruns=b['q_overruns']-a['q_overruns'],errors=b['errors']-a['errors'])
                    for a,b in zip(points,points[1:]) if b['q_overruns']!=a['q_overruns'] or b['errors']!=a['errors']]
                summary['sustained'].append(measured)
    for path in sorted((ROOT/'physical').glob('*.json')):
        if path.stem != 'running': summary['controller_'+path.stem] = json.loads(path.read_text())
    for path in sorted((ROOT/'continuation').glob('*.json')):
        if path.stem != 'running': summary['continuation_'+path.stem] = json.loads(path.read_text(encoding='utf-8-sig'))
    args.output.write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(dict(incomplete=summary['incomplete'], phases={n:dict(passed=p['passed'],total=p['total'],
        runtime=p['runtime_review'],tls_rows=len(p['tls_rows']),failures=[c['name'] for c in p['failures']]) for n,p in summary['phases'].items()}),indent=2))


if __name__ == '__main__': main()
