"""Check physical identities and metrics without converting failed cases into passes."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zlib

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
SOURCES=ROOT/'sources' if (ROOT/'sources/tools').is_dir() else REPO
sys.path.insert(0,str(SOURCES/'tools/esp32c3_tests'))
from pdm_clock import parse
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--summary',type=Path,default=ROOT/'summary.json')
parser.add_argument('--output',type=Path,default=ROOT/'verified.json')
args=parser.parse_args()
s=json.loads(args.summary.read_text())
initial=s['controller_initial']
assert not s['incomplete']
assert [p['name'] for p in s['controller_phases']]==['control-short','profile-short','profile-long']
artifacts={'control':'r9a97-pcm-tail','profile':'r9a97-staged-flow'}
for name,variant in artifacts.items():
    expected=initial['images'][name]
    app=(REPO/('firmware/development/esp32c3-idf-6.1-'+variant)/'app.bin').read_bytes()
    assert hashlib.sha256(app).hexdigest()==expected['sha256'] and len(app)==expected['bytes']
    clock=s['controller_'+name+'-clock']
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
    assert all(int(r[2],16)==offset and int(r[3])==len(app) and int(r[4],16)==zlib.crc32(app) for r in reads)
    persistence=s['controller_installed-'+name]['persistence']
    assert persistence and all(v is True for v in persistence.values())
verified=dict(kind='Identity, provenance and verdict preservation; not acoustic qualification',phases={})
for name,item in s['phases'].items():
    report=json.loads((ROOT/'physical'/name/'report.json').read_text())
    expected=initial['images']['control' if name.startswith('control') else 'profile']
    assert item['board']['app_elf_sha256']==expected['app_elf_sha256']
    assert item['original_acceptance']==report['cases']
    passed=all(c['result']=='PASS' for c in report['cases'])
    assert passed==(item['controller']['code']==0)
    assert item['pacing_ratio']==1.0
    if passed: assert all(r['result']=='PASS' for r in item['record_observations'].values())
    verified['phases'][name]=dict(passed=item['passed'],total=item['total'])
for case in s['cases']:
    if case['mode'].startswith('profile'):
        assert 'dma' not in case['flow_staged_output']
        if case['flow_complete']:
            assert case['flow_decoder']['complete'] and case['flow_staged_output']['complete']
restored=s['controller_restoration']
assert restored['identity']['app_elf_sha256']==initial['identity']['app_elf_sha256']
assert len(restored['states'])==3 and all(r['audio']==initial['status']['audio'] for r in restored['states'])
for persistence in (restored['persistence'],s['controller_settings-after-tests']):
    assert persistence and all(v is True for v in persistence.values())
verified.update(result='PASS',mapped_crc_checks=8,nominal_clocks_verified=True,restored=True)
args.output.write_text(json.dumps(verified,indent=2)+'\n')
print(json.dumps(verified,indent=2))
