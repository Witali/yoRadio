"""Cross-check completed clock evidence without contacting the board."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zlib

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
sys.path.insert(0, str(REPO/'tools/esp32c3_tests'))
from pdm_clock import parse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--summary', type=Path, default=ROOT/'summary.json')
parser.add_argument('--output', type=Path, default=ROOT/'verified.json')
args = parser.parse_args()
audit = json.loads((ROOT/'build-audit.json').read_text())
summary = json.loads(args.summary.read_text())
cases = {c['mode']:c for c in summary['cases']}
result = dict(kind='Evidence identity and arithmetic checks, not acoustic qualification', modes={})
for mode in ('integer','fractional'):
    readback = json.loads((ROOT/'physical'/(mode+'-clock.json')).read_text())
    identity = readback['identity']
    expected = audit['images'][mode]['image']
    app = (REPO/f'firmware/development/esp32c3-idf-6.1-r9a97-pdm-{mode}/app.bin').read_bytes()
    assert hashlib.sha256(app).hexdigest() == expected['sha256']
    assert len(app) == expected['bytes']
    assert identity['app_elf_sha256'] == expected['app_elf_sha256']
    lines = [r['line'] for r in readback['rows']]
    clocks = [c for line in lines if (c:=parse(line)) is not None]
    assert len(clocks) == 1
    assert clocks[0] == {k:v for k,v in readback['clocks'][0].items() if k!='at'}
    assert clocks[0]['exact_nominal_48khz'] == (mode=='fractional')
    probe = [line for line in lines if line.startswith('FLASH_PROBE_ENV ')]
    assert len(probe)==1 and 'expected=qio ctrl=0x012c2008 ' in probe[0]
    assert 'actual_mhz=80 cpu_hz=160000000 ' in probe[0]
    reads = [re.fullmatch(r'FLASH_PROBE_READ pass=(\d+) offset=(0x[0-9a-f]+) bytes=(\d+) crc32=(0x[0-9a-f]+)', line)
             for line in lines if line.startswith('FLASH_PROBE_READ ')]
    assert len(reads)==4 and all(reads)
    assert [int(r[1]) for r in reads] == [1,2,3,4]
    offset = {'app0':0x10000,'app1':0x1e0000}[identity['partition']]
    assert all(int(r[2],16)==offset and int(r[3])==len(app) and int(r[4],16)==zlib.crc32(app) for r in reads)
    case = cases[mode]
    report = json.loads((ROOT/'physical'/mode/'report.json').read_text())
    assert report['board']==identity
    assert case['original_acceptance']==report['cases']
    if case['damaged_dma']:
        assert not case['telemetry_complete'] and not case['acceptance_passed']
        assert 'dma_unavailable' in case
    boundaries = case.get('readable_dma_endpoints')
    if boundaries and boundaries['monotonic_readable_samples']:
        assert sum(r['q_overruns'] for r in case['dma_intervals']) == boundaries['delta']['q_overruns']
    result['modes'][mode] = dict(identity_matches=True, clock_matches=True,
        mapped_crc_checks=4, original_verdicts_preserved=True,
        telemetry_complete=case['telemetry_complete'],
        original_gates_passed=case['original_gates_passed'])
restored = json.loads((ROOT/'physical/restoration.json').read_text())
initial = json.loads((ROOT/'physical/initial.json').read_text())
assert restored['identity']['app_elf_sha256']==initial['identity']['app_elf_sha256']
assert all(s['audio']==initial['status']['audio'] for s in restored['states'])
result['restoration_identity_and_playback']=True
result['result']='PASS'
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
