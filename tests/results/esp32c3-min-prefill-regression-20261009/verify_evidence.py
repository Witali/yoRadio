"""Verify regression provenance, coverage and restoration; preserve failed gates."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zlib

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
sys.path.insert(0,str(ROOT/'sources/tools/esp32c3_tests'))
from pdm_clock import parse
from summarize import PHASES

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--summary',type=Path,default=ROOT/'summary.json')
parser.add_argument('--output',type=Path,default=ROOT/'verified.json')
args=parser.parse_args()
s=json.loads(args.summary.read_text());initial=s['initial']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not s['incomplete'] and [p['name'] for p in s['controller_phases']]==list(PHASES)
assert 'controller_controller-failure' not in s and 'controller_restoration-failure' not in s
sources=json.loads((ROOT/'sources.json').read_text())
for path,digest in sources.items():assert sha(ROOT/'sources'/path)==digest,path
for path,digest in initial['test_sources_sha256'].items():assert sources[path]==digest,path
app=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250/app.bin'
blob=app.read_bytes();expected=initial['candidate']
assert sha(app)==expected['sha256'] and len(blob)==expected['bytes']
assert blob[176:208].hex()==expected['app_elf_sha256']
manifest=json.loads(app.with_name('manifest.json').read_text())
assert manifest['image']==expected
for path,digest in manifest['source_overlay_sha256'].items():assert sources[path]==digest,path
clock=s['controller_fractional-clock']
assert clock['identity']['app_elf_sha256']==expected['app_elf_sha256']
lines=[r['line'] for r in clock['rows']]
clocks=[p for line in lines if (p:=parse(line)) is not None]
assert len(clocks)==1 and clocks[0]['exact_nominal_48khz']
env=[line for line in lines if line.startswith('FLASH_PROBE_ENV ')]
assert len(env)==1 and 'expected=qio ctrl=0x012c2008 ' in env[0] and 'actual_mhz=80 ' in env[0]
reads=[re.fullmatch(r'FLASH_PROBE_READ pass=(\d+) offset=(0x[0-9a-f]+) bytes=(\d+) crc32=(0x[0-9a-f]+)',line)
       for line in lines if line.startswith('FLASH_PROBE_READ ')]
assert len(reads)==4 and all(reads) and [int(r[1]) for r in reads]==[1,2,3,4]
offset={'app0':0x10000,'app1':0x1e0000}[clock['identity']['partition']]
assert all(int(r[2],16)==offset and int(r[3])==len(blob) and int(r[4],16)==zlib.crc32(blob) for r in reads)
verified=dict(scope='Provenance and exact coverage; PASS here does not override continuity findings.',phases={})
for name,item in s['phases'].items():
    folder=ROOT/'physical'/name
    report=json.loads((folder/'report.json').read_text())
    assert item['board']['app_elf_sha256']==expected['app_elf_sha256'],name
    assert report['test_sources_sha256']==initial['test_sources_sha256'],name
    assert item['original_acceptance']==report['cases'],name
    assert item['passed']==sum(c['result']=='PASS' for c in report['cases'])
    assert (item['passed']==item['total'])==(item['controller']['code']==0)
    for key,digest in item['input_sha256'].items():assert sha(folder/(key+'.json'))==digest
    if name!='short-pcm-tails':
        assert report['config']['sha256']==sha(app.with_name('sdkconfig'))
        assert report['server_options']==dict(unpaced_files=True,delivery_stats=True,pacing_ratio=1.0)
        assert report['cpu_budget_percent'] is None
    if name.startswith('matrix-'):
        assert item['expected_cases_match'] and item['fixture_hashes_match']
        assert len(item['independent_format_replay'])==22
    verified['phases'][name]=dict(passed=item['passed'],total=item['total'],
        runtime=item['extended_runtime']['result'],transport_failure_phase_records=len(item.get('transport',{}).get('failures',[])),
        failed_transport_requests=item.get('transport',{}).get('failed_requests',[]))
    replay_failures=[]
    for key in ('independent_format_replay','independent_eof_replay','transition_replay','recovered_playback_replay'):
        replay_failures.extend(r for r in item.get(key,[]) if r['result']!='PASS')
    if 'switch_replay' in item:
        switch=item['switch_replay']
        if switch['result']!='PASS':replay_failures.append(switch)
        else:
            replay_failures.extend(r for r in switch['evidence']['stations'] if r['result']!='PASS')
            if switch['evidence']['heap']['result']!='PASS':replay_failures.append(switch['evidence']['heap'])
    verified['phases'][name]['independent_replay_failures']=replay_failures
assert s['phases']['short-pcm-tails']['submission_replay']['measured_cases']==60
assert s['phases']['eof-http']['expected_cases_match']
assert len(s['phases']['eof-http']['independent_eof_replay'])==22
assert len(s['sustained'])==1
case=s['sustained'][0]
verified['heavy_flac']=dict(telemetry_complete=case['telemetry_complete'],
    decoder_flow_complete=case['flow_decoder']['complete'],output_flow_complete=case['flow_output']['complete'],
    selected_dma_events=case['dma']['delta']['q_overruns'],
    whole_observed_dma_events=sum(e['overruns'] for e in case['whole_observed_dma_events']),
    continuity=case['continuity_review']['result'])
restored=s['controller_restoration']
assert restored['identity']['app_elf_sha256']==initial['identity']['app_elf_sha256']
assert len(restored['states'])==3 and all(r['audio']==initial['status']['audio'] for r in restored['states'])
for p in (restored['persistence'],s['controller_settings-after-tests'],s['controller_installed']['persistence']):
    assert p and all(v is True for v in p.values())
verified.update(result='PASS',source_files=len(sources),restored=True,mapped_crc_checks=4,
                fractional_clock_analog_qualified=False)
args.output.write_text(json.dumps(verified,indent=2)+'\n')
print(json.dumps(verified,indent=2))
