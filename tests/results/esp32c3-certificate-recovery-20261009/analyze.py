"""Replay framing, untrusted-certificate recovery and following full HE-AACv2."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import ssl
import sys
from datetime import datetime

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=read(ROOT/'sources.json')
for name,digest in sources['files'].items(): assert sha(REPO/sources['dependency']/name)==digest,name
sys.path.insert(0,str(REPO/sources['dependency']/'tools/esp32c3_tests'))
old=REPO/'tests/results/esp32c3-min250-tls-ota-20261009'
sys.path.insert(0,str(old))
spec=importlib.util.spec_from_file_location('previous_tls_analysis',old/'summarize.py')
previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
from common import check_certificate_rejection, check_playback, check_recovery_heap, matches
from pdm_clock import parse as clock_parse

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=ROOT/'summary.json')
args=p.parse_args()
catalog=read(ROOT/'case-catalog.json')
initial=read(ROOT/'physical/initial.json')
assert initial['test_sources_sha256']==sources['files']
manifest=read(ROOT/'artifacts/manifest.json')
assert initial['candidate']==manifest['image']
assert sha(ROOT/'artifacts/sdkconfig')==manifest['sdkconfig_sha256']
summary=dict(scope='Original failures retained; controlled recovery is not public-station or analog qualification.',phases={},incomplete=[])
phases=read(ROOT/'physical/phases.json')
for name in ('framing','certificate-rejection','records-after-rejection'):
    phase=next((r for r in phases if r['name']==name),None)
    if phase is None:
        summary['incomplete'].append(name)
        continue
    folder=ROOT/'physical'/name
    paths={n:folder/(n+'.json') for n in ('report','status','performance')}
    data={n:read(p) for n,p in paths.items() if p.exists()}
    report=data['report']
    assert report['test_sources_sha256']==sources['files']
    assert report['board']['app_elf_sha256']==initial['candidate']['app_elf_sha256']
    rows=data['performance']
    faults=[r for r in rows if previous.FAULT.search(r['line']) or
            re.search(r'^(ESP-ROM:|rst:|waiting for download)|TCP_POOL:.*\baction=invalid-free',r['line'])]
    tls=[r for r in rows if r['line'].startswith('TLS failure:')]
    transport=[json.loads(line) for line in (ROOT/'physical'/(name+'-request-phases.jsonl')).read_text().splitlines()]
    item=dict(controller=phase,original=report['cases'],passed=sum(c['result']=='PASS' for c in report['cases']),
              total=len(report['cases']),runtime_faults=faults,tls=tls,
              transport_failures=[r for r in transport if r['result']!='PASS'],
              input_sha256={n:sha(p) for n,p in paths.items() if p.exists()})
    assert phase['code']==(0 if item['passed']==item['total'] else 1)
    summary['phases'][name]=item
    if name=='framing':
        item['replay']=previous.framing_replay(data,catalog)
        contexts=[]
        for row in tls:
            names=[b['case'] for b in data['status'] if b['started_at']<=row['at']<=b['ended_at']]
            expected=(len(names)==1 and names[0] in ('framing:length-short','framing:chunked-short','framing:close-raw') and
                      row['line']=='TLS failure: component=esp-tls-mbedtls operation=read mbedtls_return=-29312')
            contexts.append(dict(row=row,observations=names,expected=expected))
        item['tls_context']=contexts
        item['runtime_review']='PASS' if not faults and all(r['expected'] for r in contexts) else 'REVIEW_REQUIRED'
    elif name=='certificate-rejection':
        batches={b['case']:b for b in data['status']}
        # A valid self-signed certificate for the right address isolates trust,
        # rather than expiry or a wrong-hostname failure.
        cert_path=ROOT/'public-certificates/untrusted.pem'
        if not cert_path.exists():
            cert_path=REPO/'.build/c3-tls-final-gates-20261009/untrusted/cert.pem'
        cert=ssl._ssl._test_decode_cert(str(cert_path))
        created=datetime.fromisoformat(report['created_utc']).timestamp()
        assert ssl.cert_time_to_seconds(cert['notBefore'])<=created<ssl.cert_time_to_seconds(cert['notAfter'])
        assert cert['issuer']==cert['subject'] and ('IP Address','192.168.100.253') in cert['subjectAltName']
        assert sha(cert_path)==initial['untrusted_cert_sha256']
        item['certificate_control']=dict(valid_at_test=True,self_signed=True,address_matches=True,
                                        sha256=sha(cert_path))
        def rejection():
            batch=batches['untrusted-tls']
            assert not batch.get('interrupted') and batch['ended_at']-batch['started_at']>=12
            assert len(batch['samples'])>=3 and all(not r['audio'] for r in batch['samples'])
            alerts=[e['reason'] for e in report['tls_events'] if e['mode']=='tls-handshake-failure']
            check_certificate_rejection(alerts,rows)
            return dict(samples=len(batch['samples']),alerts=alerts)
        item['rejection_replay']=previous.verdict('rejection',rejection)
        def recovery():
            batch=batches['after-tls-rejection']
            assert not batch.get('interrupted') and batch['started_at']>batches['untrusted-tls']['ended_at']
            assert report['fixture_hashes']['lc-48000-stereo']==catalog['lc-48000-stereo']['sha256']
            result=check_playback(batch['samples'],catalog['lc-48000-stereo'])
            assert not any(batch['started_at']<=r['at']<=batch['ended_at'] for r in tls)
            return result
        item['recovery_replay']=previous.verdict('http-recovery',recovery) if 'after-tls-rejection' in batches else dict(result='MISSING')
        counts={line:sum(r['line']==line for r in tls) for line in sorted({r['line'] for r in tls})}
        item['tls_counts']=counts
        item['recovery_samples']=len(batches.get('after-tls-rejection',{}).get('samples',[]))
        item['server_events']=report.get('server_events',[])
        alerts=[e['reason'] for e in report.get('tls_events',[]) if e['mode']=='tls-handshake-failure']
        expected_counts={
            'TLS failure: component=esp-tls':len(alerts),
            'TLS failure: component=esp-tls-mbedtls operation=handshake mbedtls_return=-12288':len(alerts),
            'TLS failure: component=esp-x509-crt-bundle certificate_verification_failed=true':len(alerts)}
        recovery_start=batches.get('after-tls-rejection',{}).get('started_at')
        expected_tls=bool(alerts and counts==expected_counts and recovery_start is not None and
                          all(r['at']<recovery_start for r in tls) and item['rejection_replay']['result']=='PASS')
        item['runtime_review']='PASS' if expected_tls and not faults else 'REVIEW_REQUIRED'
    else:
        item['record_replay']={mode:previous.verdict(mode,lambda mode=mode,obs=obs:previous.record_evidence(obs['events'],mode))
                              for mode,obs in report['record_observations'].items()}
        cases={c['name']:c for c in report['cases']}
        item['heap_replay']=previous.verdict('idle-recovery',lambda:check_recovery_heap(
            cases['idle-before']['evidence']['samples'],cases['idle-recovery']['evidence']['samples']))
        item['idle_before']=cases['idle-before'].get('evidence')
        item['idle_after']=cases['idle-recovery'].get('evidence')
        batch=next(b for b in data['status'] if b['case']=='tls-record:grow')
        metrics=previous.helper.summarize_batch(name,folder,batch,data,item['input_sha256'])
        start,end=metrics['measured_start'],metrics['measured_end']
        metrics['flow_decoder']=previous.strict_flow(rows,start,end,'DEC')
        metrics['flow_output']=previous.strict_flow(rows,start,end,'STAGED_OUT')
        points=[v for r in rows if (v:=previous.parse_dma(r)) is not None and batch['started_at']<=v['at']<=end]
        metrics['whole_dma_events']=[dict(start=a['at'],end=b['at'],overruns=b['q_overruns']-a['q_overruns'],errors=b['errors']-a['errors'])
            for a,b in zip(points,points[1:]) if b['q_overruns']!=a['q_overruns'] or b['errors']!=a['errors']]
        item['metrics']=metrics
        item['pacing_ratio']=report['pacing_ratio']
        item['runtime_review']='PASS' if not faults and not tls else 'REVIEW_REQUIRED'
for path in sorted((ROOT/'physical').glob('*.json')):
    if path.stem!='running' and not path.name.endswith('-transport-timing.json'):
        summary['controller_'+path.stem]=read(path)
restored=summary.get('controller_restoration')
summary['restored']=bool(restored and restored['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256'] and
    all(v is True for v in restored['persistence'].values()) and len(restored['states'])==3 and
    all(s['audio']==initial['status']['audio'] for s in restored['states']))
assert summary['restored'],'Restoration must be verified'
assert not summary.get('controller_restoration-failure')
clock=summary['controller_fractional-clock']
clocks=[v for r in clock['rows'] if (v:=clock_parse(r['line'])) is not None]
assert len(clocks)==1 and clocks[0]['exact_nominal_48khz']
assert any('expected=qio ctrl=0x012c2008 ' in r['line'] and 'actual_mhz=80 ' in r['line'] for r in clock['rows'])
summary['result']='PASS'
summary['result_scope']='Integrity and replay, not an all-firmware-gates verdict.'
args.output.write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(dict(incomplete=summary['incomplete'],restored=summary['restored'],phases={name:dict(
    passed=s['passed'],total=s['total'],tls=len(s['tls']),runtime_faults=len(s['runtime_faults']),
    transport_failures=len(s['transport_failures'])) for name,s in summary['phases'].items()}),indent=2))
