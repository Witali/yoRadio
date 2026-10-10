"""Validate PCM-tail evidence identity; a valid archive can contain failed tests."""
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
summary=json.loads(args.summary.read_text())
audit=json.loads((ROOT/'build-audit.json').read_text())
expected=audit['image']
app=(REPO/'firmware/development/esp32c3-idf-6.1-r9a97-pcm-tail/app.bin').read_bytes()
assert hashlib.sha256(app).hexdigest()==expected['sha256'] and len(app)==expected['bytes']
readback=json.loads((ROOT/'physical/fractional-clock.json').read_text())
identity=readback['identity']
assert identity['app_elf_sha256']==expected['app_elf_sha256']
lines=[r['line'] for r in readback['rows']]
clocks=[c for line in lines if (c:=parse(line)) is not None]
assert len(clocks)==1 and clocks[0]['exact_nominal_48khz']
assert clocks[0]=={k:v for k,v in readback['clocks'][0].items() if k!='at'}
env=[line for line in lines if line.startswith('FLASH_PROBE_ENV ')]
assert len(env)==1 and 'expected=qio ctrl=0x012c2008 ' in env[0]
assert 'actual_mhz=80 cpu_hz=160000000 ' in env[0]
reads=[re.fullmatch(r'FLASH_PROBE_READ pass=(\d+) offset=(0x[0-9a-f]+) bytes=(\d+) crc32=(0x[0-9a-f]+)',line)
       for line in lines if line.startswith('FLASH_PROBE_READ ')]
assert len(reads)==4 and all(reads)
assert [int(r[1]) for r in reads]==[1,2,3,4]
offset={'app0':0x10000,'app1':0x1e0000}[identity['partition']]
assert all(int(r[2],16)==offset and int(r[3])==len(app) and int(r[4],16)==zlib.crc32(app) for r in reads)
phases=json.loads((ROOT/'physical/phases.json').read_text())
expected_phases=['short-pcm-tails','hev2-ten-minutes','matrix','heavy-flac','transitions-faults-websocket','switch']
assert [p['name'] for p in phases]==expected_phases and not summary['incomplete']
result=dict(kind='Evidence identity and arithmetic, not playback or analog quality acceptance',phases={})
for phase in phases:
    name=phase['name']
    report=json.loads((ROOT/'physical'/name/'report.json').read_text())
    item=summary['phases'][name]
    assert report['board']==identity
    assert report['cases']==item['original_acceptance']
    assert phase['code']!=124
    assert all(c['result']=='PASS' for c in report['cases'])==(phase['code']==0)
    if name!='short-pcm-tails':
        assert item['prefill'], 'Missing proof that prefill executed in '+name
    else:
        assert item['measured_cases']==60 and item['total']==62
    result['phases'][name]=dict(identity_matches=True,original_verdicts_preserved=True,
        passed=item['passed'],total=item['total'],prefill_events=len(item.get('prefill',[])))
for case in summary['sustained']:
    if case['damaged_dma']:
        assert not case['telemetry_complete'] and not case['acceptance_passed']
    endpoints=case.get('readable_dma_endpoints')
    if endpoints and endpoints['monotonic_readable_samples']:
        assert sum(r['q_overruns'] for r in case['dma_intervals'])==endpoints['delta']['q_overruns']
initial=json.loads((ROOT/'physical/initial.json').read_text())
restored=json.loads((ROOT/'physical/restoration.json').read_text())
assert restored['identity']['app_elf_sha256']==initial['identity']['app_elf_sha256']
assert len(restored['states'])==3 and all(s['audio']==initial['status']['audio'] for s in restored['states'])
assert restored['persistence'] and all(v is True for v in restored['persistence'].values())
result.update(result='PASS',mapped_crc_checks=4,clock_matches=True,restored=True)
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
