"""Verify saved owner study identities, source scope and independent observations."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zlib
from references import verify_references, PRIOR, REPO

verify_references()
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(PRIOR/'sources/tools/esp32c3_tests'))
from ota import image_info
from pdm_clock import parse as parse_clock

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
load=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reviews={'initial':load(ROOT/'review.json'),'fixed':load(ROOT/'review-fixed.json'),
         'confirmed':load(ROOT/'review-confirmed.json')}
catalog=load(ROOT/'case-catalog.json')
assert all(not v['incomplete'] for v in reviews.values())
audits=load(ROOT/'build-audit.json')
assert set(audits)=={'0','4','fixed'} and all(v['result']=='PASS' for v in audits.values())
assert audits['fixed']['config_changes']=={}
expected_changes={'idf/esp32c3-oled-native/main/'+n for n in ('adaptive_input.c','adaptive_input.h','tls_input_reserve.c')}
old,new=load(ROOT/'sources.json'),load(ROOT/'fixed-sources.json')
assert old.keys()==new.keys()
assert {k for k in old if old[k]!=new[k]}==expected_changes
for name in expected_changes:assert sha(ROOT/'fixed-sources'/name)==new[name]
assert all(delta==0 for name,delta in audits['fixed']['section_size_delta'].items() if name.startswith(('.iram0.','.dram0.','.rtc.')))
assert 'resident == (pressure ? 4 : 8)' in (ROOT/'retention-before/failure.log').read_text()
for name in expected_changes:
    assert sha(ROOT/'retention-before/sources'/name)==old[name], ('red regression source',name)
before_test=(ROOT/'retention-before/sources/tests/native/adaptive_input_test.c').read_text()
after_test=(ROOT/'retention-after/sources/tests/native/adaptive_input_test.c').read_text()
assert before_test.split('static void test_retained_baseline(void) {')[1].split('static void test_deferred_limit(void) {')[0]==after_test.split('static void test_retained_baseline(void) {')[1].split('static void test_deferred_limit(void) {')[0]
# The older general retirement check and success label changed with the policy;
# the new failing regression itself is byte-for-byte identical after decoding.
assert before_test.replace('(i == 0 ? 5 : 4)','(i < 4 ? 6 : 9 - i)').replace('ownership, FIFO, deferred limit','ownership, FIFO, retained baseline, deferred limit')==after_test
queue=load(ROOT/'retention-after/report.json')
assert queue['passed'] and queue['stress_packets']==30000
reserve=load(ROOT/'retention-reserve/report.json')
assert len(reserve['variants'])==5 and all(v['passed'] and v['concurrent_allocations']==8000 for v in reserve['variants'])
for folder in ('retention-after','retention-reserve','retention-stream-enabled','retention-stream-disabled','retention-prefill','host'):
    report=load(ROOT/folder/'report.json')
    for name,digest in report.get('sources',report.get('source_sha256',{})).items():
        assert sha(ROOT/folder/'sources'/name)==digest,(folder,name)
    if folder in ('retention-after','retention-reserve'):
        assert all(report['sources'][name]==new[name] for name in expected_changes)

trials=[]
for kind,review in reviews.items():
    folder=ROOT/({'initial':'physical','fixed':'physical-fixed','confirmed':'physical-confirmed'}[kind])
    initial=load(folder/'initial.json')
    runner=ROOT/({'initial':'trial.py','fixed':'trial-fixed.py','confirmed':'trial-final.py'}[kind])
    assert sha(runner)==initial['trial_sha256']
    for path,digest in initial['test_sources_sha256'].items():
        snapshot=ROOT/'capture-sources'/path if kind=='confirmed' and path=='tools/esp32c3_tests/serial_lines.py' else PRIOR/'sources'/path
        assert sha(snapshot)==digest, path
    restoration=load(folder/'restoration.json')
    assert restoration['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256']
    assert all(restoration['persistence'].values())
    assert len(restoration['states'])==3 and all(s['audio']==initial['status']['audio'] for s in restoration['states'])
    assert len(load(folder/'phases.json'))==(1 if kind=='confirmed' else 2)
    for name,item in review['trials'].items():
        report=load(folder/name/'report.json')
        assert report['controller_sha256']==initial['trial_sha256']
        assert report['fixture_hashes']=={n:catalog[n]['sha256'] for n in ('flac-level8','he-48000-stereo','hev2-44100-stereo')}
        installed=load(folder/('installed-'+name+'.json'))
        variant=installed['variant']
        image=initial['images'][str(variant)]
        assert installed['identity']==report['board']
        assert installed['identity']['app_elf_sha256']==image['app_elf_sha256']
        assert all(installed['persistence'].values())
        profile={'expanded-owner':'flac-input4-owner','control-owner':'flac-input0-owner',
                 'original-growth':'flac-input4-owner','retained-growth':'flac-retained-owner',
                 'retained-confirmed':'flac-retained-owner'}[name]
        artifact=REPO/('firmware/development/esp32c3-idf-6.1-r9a97-'+profile)
        blob=(artifact/'app.bin').read_bytes()
        assert image_info(blob)==image
        manifest=load(artifact/'manifest.json')
        assert manifest['image']==image
        assert sha(artifact/'sdkconfig')==manifest['sdkconfig_sha256']==report['sdkconfig_sha256']
        assert report['firmware_sha256']==image['sha256']
        assert manifest['extra_trust_ca_sha256']==initial['ca_sha256']==sha(ROOT/'trust/ca.pem')
        clock=load(folder/(name+'-clock.json'))
        raw=clock['rows']
        parsed=[parse_clock(r['line']) for r in raw if 'PERF PDM_CLOCK:' in r['line']]
        assert len(parsed)==1 and parsed[0]['exact_nominal_48khz']
        env=[r['line'] for r in raw if r['line'].startswith('FLASH_PROBE_ENV')]
        assert len(env)==1 and 'expected=qio ctrl=0x012c2008' in env[0] and 'actual_mhz=80' in env[0]
        reads=[re.search(r'pass=(\d+) offset=0x([0-9a-f]+) bytes=(\d+) crc32=0x([0-9a-f]+)',r['line'])
               for r in raw if r['line'].startswith('FLASH_PROBE_READ')]
        assert len(reads)==4 and all(reads)
        for i,r in enumerate(reads,1):
            assert int(r[1])==i and int(r[3])==len(blob) and int(r[4],16)==zlib.crc32(blob)
            assert int(r[2],16)==(0x10000 if installed['identity']['partition']=='app0' else 0x1e0000)
        assert any(r['line']=='FLASH_PROBE_PASS normal_app_follows=1' for r in raw)
        assert item['owner_analysis']['complete'] and item['total']==(16 if kind=='confirmed' else 15)
        assert len(item['independent_formats'])==9 and all(v['result']=='PASS' for v in item['independent_formats'])
        assert len(item['independent_eof'])==4 and all(v['result']=='PASS' for v in item['independent_eof'])
        if name=='retained-confirmed':
            assert item['independent_records']['result']=='FAIL'
            assert not report.get('record_observation'), 'Interrupted run must not fabricate completed record evidence'
        else:
            assert item['independent_records']['result']=='PASS'
        window=item['quiet_window']
        assert window['ended_at']-window['started_at']>=60 and window['http_polls']==0
        trace=[json.loads(line) for line in (folder/name/'request-phases.jsonl').read_text().splitlines()]
        assert not any(window['started_at']<r['at']<window['ended_at'] for r in trace)
        snapshots=item['owner_analysis']['snapshots']
        assert not any(s['lost'] or s['unknown'] or s['dropped'] for s in snapshots)
        perf=load(folder/name/'performance.json')
        runtime=[r for r in perf if re.search(r'allocation failed|decode (?:error|failed)|TLS failure:|assert failed|Guru Meditation|CORRUPT HEAP|serial capture interrupted',r['line'])]
        trials.append(dict(name=name,passed=item['passed'],total=item['total'],failures=item['failures'],
            initial_raw_free=item['initial_raw_free'],final_raw_free=item['final_raw_free'],
            final_live=snapshots[-1]['live'],runtime=runtime,transport_failures=item['transport_failures'],
            full_capture_runtime=item['full_capture_runtime']))

baseline={t['name']:t for t in trials}
assert [v['name'] for v in baseline['expanded-owner']['failures']]==['cross-stage-recovery','runtime']
assert [v['name'] for v in baseline['control-owner']['failures']]==['runtime']
for name in ('expanded-owner','control-owner'):
    faults=baseline[name]['runtime']
    assert len(faults)==1 and 'mbedtls_return=-29312' in faults[0]['line']
    item=reviews['initial']['trials'][name]
    end=next(v['ended_at'] for v in item['actions'] if v['name']=='tls-record:grow')
    assert 0 <= faults[0]['at']-end < 2
assert baseline['retained-growth']['passed']==15
assert baseline['retained-growth']['full_capture_runtime']['result']=='FAIL'
assert len(baseline['retained-growth']['runtime'])==1
assert baseline['retained-growth']['runtime'][0]['line']=='serial capture interrupted: incomplete final line'
confirmed=baseline['retained-confirmed']
assert confirmed['passed']==15 and confirmed['full_capture_runtime']['result']=='PASS'
assert [v['name'] for v in confirmed['failures']]==['tls-record:grow']
assert confirmed['initial_raw_free']==confirmed['final_raw_free'] and confirmed['final_live']==0
confirmed_metrics=reviews['confirmed']['trials']['retained-confirmed']['record_metrics'][0]
assert confirmed_metrics['interrupted'] and not confirmed_metrics['telemetry_complete']
assert confirmed_metrics['whole_observed_dma_review']['result']=='PASS'
result=dict(result='PASS',scope='Evidence and original verdict validation; does not turn failed runs into passes or qualify analog sound.',
    trials=trials,source_changes=sorted(expected_changes),section_size_delta=audits['fixed']['section_size_delta'],
    host=dict(queue_packets=queue['stress_packets'],reserve_variants=len(reserve['variants']),reserve_allocations=40000,
              stream_enabled=load(ROOT/'retention-stream-enabled/report.json')['cases'],
              stream_disabled=load(ROOT/'retention-stream-disabled/report.json')['cases'],
              prefill_cases=sum(v['cases'] for v in load(ROOT/'retention-prefill/report.json')['variants'].values())),
    capture_source_sha256={name:sha(ROOT/'capture-sources'/name) for name in ('tools/esp32c3_tests/serial_lines.py','tests/test-serial-telemetry.py')})
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
