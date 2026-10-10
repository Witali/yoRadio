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
sys.path.insert(0,str(ROOT/'sources/tools/esp32c3_tests'))
from pdm_clock import parse
from summarize import PHASES

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--summary',type=Path,default=ROOT/'summary.json')
p.add_argument('--output',type=Path,default=ROOT/'verified.json')
a=p.parse_args()
s=json.loads(a.summary.read_text()); initial=s['initial']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not s['incomplete']
assert [p['name'] for p in s['controller_phases']]==list(PHASES)
assert 'controller_controller-failure' not in s and 'controller_restoration-failure' not in s
sources=json.loads((ROOT/'sources.json').read_text())
for path,digest in sources.items():assert sha(ROOT/'sources'/path)==digest,path
for path,digest in initial['test_sources_sha256'].items():assert sources[path]==digest,path
artifacts={v:json.loads((ROOT/'artifacts'/v/'manifest.json').read_text()) for v in ('0','4')}
assert artifacts['0']['source_overlay_sha256']==artifacts['4']['source_overlay_sha256']
for v,m in artifacts.items():
    assert m['image']==initial['images'][v]
    for path,digest in m['source_overlay_sha256'].items(): assert sources[path]==digest,path
    assert sha(ROOT/'artifacts'/v/'sdkconfig')==m['sdkconfig_sha256']
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
c0,c4=(config(ROOT/'artifacts'/v/'sdkconfig') for v in ('0','4'))
diff={k:dict(before=c0.get(k),after=c4.get(k)) for k in c0.keys()|c4.keys() if c0.get(k)!=c4.get(k)}
assert diff=={'CONFIG_YORADIO_FLAC_INPUT_EXTRA_SLOTS':dict(before='0',after='4')}
verified=dict(scope='Provenance and complete evidence, not production or analog qualification.',
              configuration_difference=diff,phases={},clocks={})
for label,v in (('flac-control-before','0'),('flac-candidate','4'),('flac-control-after','0'),('switch-candidate','4')):
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
    if name!='records-after-switch':
        assert report['test_sources_sha256']==initial['test_sources_sha256']
        assert report['config']['sha256']==sha(ROOT/'artifacts'/v/'sdkconfig')
        assert report['server_options']==dict(unpaced_files=True,delivery_stats=True,pacing_ratio=1.0)
        assert report['cpu_budget_percent'] is None
    assert not item['malformed_growth']
    if v=='0':assert not item['growth']
    verified['phases'][name]=dict(passed=item['passed'],total=item['total'],runtime=item['extended_runtime']['result'],
        transport_failures=len(item['transport_failures']),growth=item['growth'],
        independent_failures=[r for key in ('independent_eof','independent_formats','record_observations') for r in item.get(key,[]) if r['result']!='PASS'])
assert len(s['sustained'])==4
assert len(s['phases']['flac-candidate']['growth'])==1
for row in s['phases']['flac-candidate']['growth']:
    assert {k:v for k,v in row.items() if k!='at'}==dict(resident=8,minimum=4,limit=8,target=8,capacity=16480)
assert not s['phases']['records-after-switch']['growth'],'AAC must not expand the queue'
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
