"""Check provenance, coverage and restoration without overriding failed gates."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import zlib

ROOT = Path(__file__).resolve().parent
REPO = next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
sys.path.insert(0, str(ROOT/'sources/tools/esp32c3_tests'))
from pdm_clock import parse
from summarize import PHASES

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--summary', type=Path, default=ROOT/'summary.json')
p.add_argument('--output', type=Path, default=ROOT/'verified.json')
args = p.parse_args()
s = json.loads(args.summary.read_text())
initial = s['controller_initial']
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert not s['incomplete'] and [p['name'] for p in s['controller_phases']+s['continuation_phases']] == list(PHASES)
assert 'controller_restoration-failure' not in s
assert 'continuation_controller-failure' not in s and 'continuation_restoration-failure' not in s
assert s['controller_controller-failure']['exception_chain'], 'Retain the original campaign abort'
assert initial['test_sources_sha256']==s['continuation_initial']['test_sources_sha256']
assert initial['candidate']==s['continuation_initial']['candidate']
sources = json.loads((ROOT/'sources.json').read_text())
for path,digest in sources.items(): assert sha(ROOT/'sources'/path) == digest,path
for path,digest in initial['test_sources_sha256'].items(): assert sources[path] == digest,path
manifest = json.loads((ROOT/'artifacts/manifest.json').read_text())
assert initial['candidate'] == manifest['image']
assert sha(ROOT/'artifacts/sdkconfig') == manifest['sdkconfig_sha256']
image = REPO/'firmware/development/esp32c3-idf-6.1-r9a97-prefill-min250/app.bin'
blob = image.read_bytes()
assert sha(image) == initial['candidate']['sha256']
assert len(blob) == initial['candidate']['bytes'] and blob[176:208].hex() == initial['candidate']['app_elf_sha256']
clock = s['controller_fractional-clock']
assert clock['identity']['app_elf_sha256'] == initial['candidate']['app_elf_sha256']
rows = [r['line'] for r in clock['rows']]
clocks = [p for r in rows if (p:=parse(r)) is not None]
assert len(clocks) == 1 and clocks[0]['exact_nominal_48khz']
env = [r for r in rows if r.startswith('FLASH_PROBE_ENV ')]
assert len(env)==1 and 'expected=qio ctrl=0x012c2008 ' in env[0] and 'actual_mhz=80 ' in env[0]
reads = [re.fullmatch(r'FLASH_PROBE_READ pass=(\d+) offset=(0x[0-9a-f]+) bytes=(\d+) crc32=(0x[0-9a-f]+)',r)
         for r in rows if r.startswith('FLASH_PROBE_READ ')]
assert len(reads)==4 and all(reads) and [int(r[1]) for r in reads]==[1,2,3,4]
offset = {'app0':0x10000,'app1':0x1e0000}[clock['identity']['partition']]
assert all(int(r[2],16)==offset and int(r[3])==len(blob) and int(r[4],16)==zlib.crc32(blob) for r in reads)
second=s['continuation_fractional-clock']
assert second['identity']['app_elf_sha256']==initial['candidate']['app_elf_sha256']
second_rows=[r['line'] for r in second['rows']]
second_clocks=[p for r in second_rows if (p:=parse(r)) is not None]
assert len(second_clocks)==1 and second_clocks[0]['exact_nominal_48khz']
second_env=[r for r in second_rows if r.startswith('FLASH_PROBE_ENV ')]
assert len(second_env)==1 and 'expected=qio ctrl=0x012c2008 ' in second_env[0] and 'actual_mhz=80 ' in second_env[0]
second_reads=[re.fullmatch(r'FLASH_PROBE_READ pass=(\d+) offset=(0x[0-9a-f]+) bytes=(\d+) crc32=(0x[0-9a-f]+)',r)
    for r in second_rows if r.startswith('FLASH_PROBE_READ ')]
assert len(second_reads)==4 and all(second_reads) and [int(r[1]) for r in second_reads]==[1,2,3,4]
second_offset={'app0':0x10000,'app1':0x1e0000}[second['identity']['partition']]
assert all(int(r[2],16)==second_offset and int(r[3])==len(blob) and int(r[4],16)==zlib.crc32(blob) for r in second_reads)
verified = dict(scope='Evidence integrity and coverage, not an all-gates or analog PASS.', phases={},
    first_campaign='ABORTED', first_campaign_failure=s['controller_controller-failure'])
for name,item in s['phases'].items():
    folder = ROOT/item['capture_directory']/name
    report = json.loads((folder/'report.json').read_text())
    assert item['board']['app_elf_sha256'] == initial['candidate']['app_elf_sha256']
    assert report['test_sources_sha256'] == initial['test_sources_sha256']
    assert item['original_acceptance'] == report['cases']
    assert item['passed'] == sum(c['result']=='PASS' for c in report['cases'])
    expected_code = 0 if item['passed']==item['total'] else 1
    if name=='ota' and item['serial_health']['result']!='PASS': expected_code=1
    assert item['controller']['code']==expected_code
    for key,digest in item['input_sha256'].items(): assert sha(folder/(key+'.json'))==digest
    verified['phases'][name] = dict(passed=item['passed'], total=item['total'], runtime_review=item['runtime_review'],
        tls_rows=len(item['tls_rows']), transport_failures=item.get('transport',{}).get('failed_requests',[]))
framing = s['phases']['framing']
assert len(framing['independent_framing'])==8
verified['framing_replay'] = framing['independent_framing']
verified['framing_tls_context'] = framing['tls_context']
verified['certificate_rejection_only'] = s['phases']['certificate-rejection']['rejection_only_replay']
eof = s['phases']['eof-https-all']
assert eof['expected_order'] and eof['fixture_hashes_match'] and len(eof['eof_replay'])==22
verified['eof_replay'] = dict(passed=sum(c['result']=='PASS' for c in eof['eof_replay']),total=22,
    format_passed=sum(c['result']=='PASS' for c in eof['format_replay']))
ota = s['phases']['ota']
assert ota['full_hev2_before_ota'] and ota['transport_kind']=='https'
timeline = ota['timeline']
assert all(a['at']<=b['at'] for a,b in zip(timeline,timeline[1:]))
actions = {}
for row in timeline: actions.setdefault(row['action'],[]).append(row)
assert all([r['event'] for r in rows] in (['begin','returned'],['begin','raised']) for rows in actions.values())
expected_actions_completed=len(actions)==32 and all(rows[-1]['event']=='returned' for rows in actions.values())
if ota['passed']==ota['total']: assert expected_actions_completed
expected_uploads = {c['name']+':upload' for c in ota['original_acceptance'] if c['name'].startswith('ota:')}
assert {a for a in actions if a.endswith(':upload')} == expected_uploads
assert {'restore-saved-station:reboot-request','restore-saved-station:verify-boot',
        'ota:while-playing:play-request','ota:while-playing:stable-playback'} <= actions.keys()
assert actions['ota:while-playing:stable-playback'][1]['at'] <= actions['ota:while-playing:upload'][0]['at']
verified['ota'] = dict(timed_actions=len(actions),expected_actions_completed=expected_actions_completed,serial_health=ota['serial_health']['result'],
    runtime_review=ota['runtime_review'],tls_context=ota['tls_context'],observed_reset_banners=len(ota['resets']),reset_review=ota['reset_review'])
record = s['phases']['records-after-ota']
assert record['pacing_ratio']==1.0 and list(record['record_replay'])==['grow']
assert len(s['sustained'])==1
c = s['sustained'][0]
verified['records_after_ota'] = dict(original=record['original_acceptance'], record_replay=record['record_replay'],
    heap_replay=record['heap_replay'],telemetry_complete=c['telemetry_complete'],
    decoder_flow_complete=c['flow_decoder']['complete'],output_flow_complete=c['flow_output']['complete'],
    selected_dma=c.get('dma',{}).get('delta'),whole_dma_events=c['whole_dma_events'])
for prefix in ('controller_','continuation_'):
    restored = s[prefix+'restoration']
    assert restored['identity']['app_elf_sha256']==initial['quiet']['app_elf_sha256']==initial['identity']['app_elf_sha256']
    assert len(restored['states'])==3 and all(r['audio']==initial['status']['audio'] for r in restored['states'])
    for state in (restored['persistence'],s[prefix+'installed']['persistence']):
        assert state and all(v is True for v in state.values())
assert all(v is True for v in s['continuation_settings-after-tests'].values())
verified.update(result='PASS',restored=True,source_files=len(sources),mapped_crc_checks=8,
                nominal_48khz=True,qio80=True,analog_qualified=False)
args.output.write_text(json.dumps(verified,indent=2)+'\n')
print(json.dumps(verified,indent=2))
