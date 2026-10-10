"""Verify provenance and report counts while retaining continuity failures."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zlib

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
from references import PRIOR, verify_references
verify_references()
sys.path.insert(0,str(PRIOR/'sources/tools/esp32c3_tests'))
from pdm_clock import parse
from summarize import PHASES, TRIALS

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--summary',type=Path,default=ROOT/'summary.json')
p.add_argument('--output',type=Path,default=ROOT/'verified.json')
a=p.parse_args()
s=json.loads(a.summary.read_text()); initial=s['initial']
catalog=json.loads((ROOT/'case-catalog.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sdk=json.loads((ROOT/'sdk.json').read_text())
assert sdk['git_revision']=='9a97f6c54ec638111ce55cd36581b3c192f15207'
for path,digest in sdk['files'].items(): assert sha(ROOT/'sdk'/path)==digest,path
assert not s['incomplete']
assert [p['name'] for p in s['controller_phases']]==list(PHASES)
assert 'controller_controller-failure' not in s and 'controller_restoration-failure' not in s
sources=json.loads((PRIOR/'sources.json').read_text())
for path,digest in sources.items():assert sha(PRIOR/'sources'/path)==digest,path
for path,digest in initial['test_sources_sha256'].items():assert sources[path]==digest,path
artifacts={v:json.loads((PRIOR/'artifacts'/v/'manifest.json').read_text()) for v in ('0','4')}
assert artifacts['0']['source_overlay_sha256']==artifacts['4']['source_overlay_sha256']
for v,m in artifacts.items():
    assert m['image']==initial['images'][v]
    for path,digest in m['source_overlay_sha256'].items(): assert sources[path]==digest,path
    assert sha(PRIOR/'artifacts'/v/'sdkconfig')==m['sdkconfig_sha256']
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
c0,c4=(config(PRIOR/'artifacts'/v/'sdkconfig') for v in ('0','4'))
diff={k:dict(before=c0.get(k),after=c4.get(k)) for k in c0.keys()|c4.keys() if c0.get(k)!=c4.get(k)}
assert diff=={'CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS':dict(before='0',after='4')}
verified=dict(scope='Provenance and complete evidence, not production or analog qualification.',
              configuration_difference=diff,phases={},clocks={})
for label,v in TRIALS:
    expected=initial['images'][v]
    app=REPO/('firmware/development/esp32c3-idf-6.1-r9a97-flac-input'+v)/'app.bin'
    blob=app.read_bytes()
    assert sha(app)==expected['sha256'] and len(blob)==expected['bytes']
    assert blob[176:208].hex()==expected['app_elf_sha256']
    clock=s['controller_'+label+'-clock']
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
    assert all(v is True for v in s['controller_installed-'+label]['persistence'].values())
    verified['clocks'][label]=dict(variant=v,qio80=True,nominal_48khz=True,mapped_crc_checks=4)
for name,item in s['phases'].items():
    report=json.loads((ROOT/'physical'/name/'report.json').read_text())
    v=item['controller']['variant']
    assert item['board']['app_elf_sha256']==initial['images'][v]['app_elf_sha256']
    assert item['original_acceptance']==report['cases']
    assert (item['passed']==item['total'])==(item['controller']['code']==0)
    for key,digest in item['input_sha256'].items():assert sha(ROOT/'physical'/name/(key+'.json'))==digest
    assert report['test_sources_sha256']==initial['test_sources_sha256']
    assert report['cpu_budget_percent'] is None
    for case,digest in report.get('fixture_hashes',{}).items():
        assert catalog[case]['sha256']==digest
    if not name.endswith('-records'):
        assert report['config']['sha256']==sha(PRIOR/'artifacts'/v/'sdkconfig')
        assert report['server_options']==dict(unpaced_files=True,delivery_stats=True,pacing_ratio=1.0)
    else:
        assert report['firmware_sha256']==initial['images'][v]['sha256']
        assert report['sdkconfig_sha256']==sha(PRIOR/'artifacts'/v/'sdkconfig')
        assert report['test_ca_sha256']==initial['ca_sha256']
        assert report['leaf_certificate_sha256']==initial['leaf_sha256']
        assert report['seconds']==75 and report['pacing_ratio']==1.0
        if not report.get('record_observations'):
            assert any(c['name']=='tls-record:grow' and c['result']=='FAIL' for c in report['cases'])
            assert item['record_observations']==[dict(name='grow',result='FAIL',
                reason='Runner did not freeze record acceptance evidence; interrupted observations cannot pass.')]
    assert not item['malformed_growth']
    if v=='0':assert not item['growth']
    verified['phases'][name]=dict(passed=item['passed'],total=item['total'],runtime=item['extended_runtime']['result'],
        transport_failures=len(item['transport_failures']),growth=item['growth'],
        independent_failures=[r for key in ('independent_eof','independent_formats','record_observations') for r in item.get(key,[]) if r['result']!='PASS'])
assert len(s['sustained'])==4
for trial,v in TRIALS:
    switch=s['phases'][trial+'-switch']
    eof=s['phases'][trial+'-eof']
    records=s['phases'][trial+'-records']
    assert [switch['total'],eof['total'],records['total']]==[2,5,5]
    assert len(switch['independent_formats'])==9 and len(eof['independent_eof'])==4
    assert len(switch['switching']['checkpoints'])==3
    assert len(records['record_observations'])==1
    assert not records['growth'],'AAC must not expand the queue'
    if v=='4':
        assert len(switch['growth'])==3
        assert len(eof['growth'])==2
        for row in switch['growth']+eof['growth']:
            assert {k:value for k,value in row.items() if k!='at'}==dict(resident=8,minimum=4,limit=8,target=8,capacity=16480)
verified['original_entries']=dict(passed=sum(p['passed'] for p in s['phases'].values()),
                                  total=sum(p['total'] for p in s['phases'].values()))
verified['independent_heap']={n:p.get('heap_recovery',[]) for n,p in s['phases'].items() if p.get('heap_recovery')}
verified['sustained']=[dict(phase=c['mode'],variant=c['variant'],telemetry=c['telemetry_complete'],
    decoder_flow=c['flow_decoder']['complete'],output_flow=c['flow_output']['complete'],
    selected_dma_events=c['dma']['delta']['q_overruns'],
    whole_observed_dma_events=sum(e['overruns'] for e in c['whole_observed_dma_events'])) for c in s['sustained']]
restored=s['controller_restoration']
assert restored['identity']['app_elf_sha256']==initial['identity']['app_elf_sha256']
assert len(restored['states'])==3 and all(r['audio']==initial['status']['audio'] for r in restored['states'])
for value in (restored['persistence'],s['controller_settings-after-tests']):assert value and all(v is True for v in value.values())
verified.update(result='PASS',restored=True,source_files=len(sources),production_qualified=False,analog_qualified=False)
a.output.write_text(json.dumps(verified,indent=2)+'\n')
print(json.dumps(verified,indent=2))
