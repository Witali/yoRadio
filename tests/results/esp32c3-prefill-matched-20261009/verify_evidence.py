"""Check measured image/configuration identities without overriding failures."""
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
overlays=json.loads((ROOT/'firmware-sources.json').read_text())
for variant,files in overlays.items():
    manifest=json.loads((ROOT/'artifacts'/variant/'manifest.json').read_text())
    assert manifest['image']==initial['images'][variant]
    for path,source in files.items():
        assert sha(ROOT/'firmware-sources'/variant/path)==source['sha256']==manifest['source_overlay_sha256'][path]
    assert sha(ROOT/'artifacts'/variant/'sdkconfig')==manifest['sdkconfig_sha256']
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
zero,minimum=(config(ROOT/'artifacts'/v/'sdkconfig') for v in ('0','250'))
diff={k:dict(before=zero.get(k),after=minimum.get(k)) for k in zero.keys()|minimum.keys() if zero.get(k)!=minimum.get(k)}
assert diff=={'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS':dict(before='0',after='250')}
def without_help(text):
    result=[];help_indent=None
    for line in text.splitlines():
        if not line.strip():continue
        indent=len(line)-len(line.lstrip())
        if help_indent is not None and indent>help_indent:continue
        help_indent=None
        if line.strip()=='help':help_indent=indent
        else:result.append(line.rstrip())
    return result

for path in overlays['0']:
    if path.endswith('/Kconfig.projbuild'):
        assert without_help((ROOT/'firmware-sources/0'/path).read_text())==without_help((ROOT/'firmware-sources/250'/path).read_text())
        continue
    assert overlays['0'][path]['sha256']==overlays['250'][path]['sha256'],path
verified=dict(scope='Provenance/coverage, not acoustic qualification; original and extra failures remain failures.',
    configuration_difference=diff,phases={},clocks={})
for label,variant in (('eof-candidate','250'),('flac-control-before','0'),('flac-candidate','250'),('flac-control-after','0')):
    expected=initial['images'][variant]
    app=REPO/('firmware/development/esp32c3-idf-6.1-r9a97-prefill-min'+variant)/'app.bin'
    blob=app.read_bytes()
    assert sha(app)==expected['sha256'] and len(blob)==expected['bytes'] and blob[176:208].hex()==expected['app_elf_sha256']
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
    persistence=s['controller_installed-'+label]['persistence']
    assert persistence and all(v is True for v in persistence.values())
    verified['clocks'][label]=dict(variant=variant,mapped_crc_checks=4,nominal_48khz=True,qio80=True)
for name,item in s['phases'].items():
    report=json.loads((ROOT/'physical'/name/'report.json').read_text())
    variant=item['controller']['variant']
    assert item['board']['app_elf_sha256']==initial['images'][variant]['app_elf_sha256']
    assert report['test_sources_sha256']==initial['test_sources_sha256']
    assert report['config']['sha256']==sha(ROOT/'artifacts'/variant/'sdkconfig')
    assert report['server_options']==dict(unpaced_files=True,delivery_stats=True,pacing_ratio=1.0)
    assert report['cpu_budget_percent'] is None
    assert item['original_acceptance']==report['cases']
    assert item['passed']==sum(c['result']=='PASS' for c in report['cases'])
    assert (item['passed']==item['total'])==(item['controller']['code']==0)
    for key,digest in item['input_sha256'].items():assert sha(ROOT/'physical'/name/(key+'.json'))==digest
    if name.startswith('eof-'):assert item['expected_cases_match'] and item['protocol_match'] and item['fixture_hashes_match']
    verified['phases'][name]=dict(passed=item['passed'],total=item['total'],runtime=item['extended_runtime']['result'],
        failed_transport_requests=item['transport']['failed_requests'],
        independent_failures=[r for key in ('independent_eof_replay','independent_format_replay') for r in item.get(key,[]) if r['result']!='PASS'])
assert len(s['sustained'])==3
assert [c['variant'] for c in s['sustained']]==['0','250','0']
verified['flac']=[dict(phase=c['mode'],variant=c['variant'],telemetry_complete=c['telemetry_complete'],
    decoder_flow_complete=c['flow_decoder']['complete'],output_flow_complete=c['flow_output']['complete'],
    selected_dma_events=c['dma']['delta']['q_overruns'],whole_observed_dma_events=sum(e['overruns'] for e in c['whole_observed_dma_events']),
    continuity=c['continuity_review']['result'],heap_replay=c['heap_replay']) for c in s['sustained']]
restored=s['controller_restoration']
assert restored['identity']['app_elf_sha256']==initial['identity']['app_elf_sha256']
assert len(restored['states'])==3 and all(r['audio']==initial['status']['audio'] for r in restored['states'])
for p in (restored['persistence'],s['controller_settings-after-tests']):assert p and all(v is True for v in p.values())
verified.update(result='PASS',restored=True,source_files=len(sources),fractional_clock_analog_qualified=False)
args.output.write_text(json.dumps(verified,indent=2)+'\n')
print(json.dumps(verified,indent=2))
