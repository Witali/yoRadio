"""Verify evidence provenance and arithmetic without promoting a failed test."""
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
from common import check_certificate_rejection

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--summary',type=Path,default=ROOT/'summary.json')
parser.add_argument('--output',type=Path,default=ROOT/'verified.json')
args=parser.parse_args()
summary=json.loads(args.summary.read_text())
initial=summary['controller_initial'];expected=initial['candidate']
artifact=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-pcm-tail'
app=(artifact/'app.bin').read_bytes()
assert hashlib.sha256(app).hexdigest()==expected['sha256'] and len(app)==expected['bytes']
cfg=(artifact/'sdkconfig').read_text()
for line in ('CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN=16384','CONFIG_YORADIO_AAC_PLUS=y',
             'CONFIG_YORADIO_TLS_RX_ONLY_RESERVE=y','CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL=y'):
    assert line in cfg
readback=summary['controller_fractional-clock'];identity=readback['identity']
assert identity['app_elf_sha256']==expected['app_elf_sha256']
lines=[r['line'] for r in readback['rows']]
clocks=[c for line in lines if (c:=parse(line)) is not None]
assert len(clocks)==1 and clocks[0]['exact_nominal_48khz']
env=[line for line in lines if line.startswith('FLASH_PROBE_ENV ')]
assert len(env)==1 and 'expected=qio ctrl=0x012c2008 ' in env[0] and 'actual_mhz=80 ' in env[0]
reads=[re.fullmatch(r'FLASH_PROBE_READ pass=(\d+) offset=(0x[0-9a-f]+) bytes=(\d+) crc32=(0x[0-9a-f]+)',line)
       for line in lines if line.startswith('FLASH_PROBE_READ ')]
assert len(reads)==4 and all(reads) and [int(r[1]) for r in reads]==[1,2,3,4]
offset={'app0':0x10000,'app1':0x1e0000}[identity['partition']]
assert all(int(r[2],16)==offset and int(r[3])==len(app) and int(r[4],16)==zlib.crc32(app) for r in reads)
assert not summary['incomplete']
names=['records-short','records-long','framing','certificate-rejection','ota','records-after-ota']
assert [p['name'] for p in summary['controller_phases']]==names
verified=dict(kind='Evidence identity and original verdict preservation, not production acceptance',phases={})
for name in names:
    item=summary['phases'][name]
    report=json.loads((ROOT/'physical'/name/'report.json').read_text())
    assert item['board']['app_elf_sha256']==expected['app_elf_sha256']
    assert item['original_acceptance']==report['cases']
    passed=all(c['result']=='PASS' for c in report['cases'])
    if name=='ota': passed=passed and item['serial_health']['result']=='PASS'
    assert passed==(item['controller']['code']==0)
    if name.startswith('records-'):
        assert item['pacing_ratio']==1.0
        if passed: assert all(r['result']=='PASS' for r in item['record_observations'].values())
    verified['phases'][name]=dict(passed=item['passed'],total=item['total'],original_verdicts_preserved=True)
cert=summary['phases']['certificate-rejection']
if cert['passed']==cert['total']:
    report=json.loads((ROOT/'physical/certificate-rejection/report.json').read_text())
    rows=json.loads((ROOT/'physical/certificate-rejection/performance.json').read_text())
    alerts=[e['reason'] for e in report['tls_events'] if e['mode']=='tls-handshake-failure']
    rejected=check_certificate_rejection(alerts,rows)
    original=next(c for c in report['cases'] if c['name']=='untrusted-tls-rejected')
    assert rejected==original['evidence']['certificate_bundle_rejected']
ota=summary['phases']['ota']
if ota['passed']==ota['total']:
    assert ota['full_hev2_before_ota'] and ota['playback_transport']=='https'
    assert any(e.get('fixture')=='hev2-44100-stereo' and e.get('tls_version')=='TLSv1.2'
               for e in ota['tls_server_events'])
restored=summary['controller_restoration']
for persistence in (summary['controller_installed']['persistence'],
                    summary['controller_settings-after-tests']):
    assert persistence and all(v is True for v in persistence.values())
assert restored['identity']['app_elf_sha256']==initial['identity']['app_elf_sha256']
assert len(restored['states'])==3 and all(s['audio']==initial['status']['audio'] for s in restored['states'])
assert restored['persistence'] and all(v is True for v in restored['persistence'].values())
verified.update(result='PASS',mapped_crc_checks=4,nominal_clock_verified=True,restored=True)
args.output.parent.mkdir(parents=True,exist_ok=True)
args.output.write_text(json.dumps(verified,indent=2)+'\n')
print(json.dumps(verified,indent=2))
