"""Check saved HOST component evidence; execute no archived/native code or payload."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import zipfile
ROOT=Path(__file__).resolve().parents[1]
FOLDERS={'helpers':'cyd-opus-family1-helpers-20261101','packets':'cyd-opus-packet-owner-20261101','decoder':'cyd-opus-decoder-owner-20261101'}
def need(value,why):
    if not value:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--checkpoint',required=True,choices=FOLDERS);args=parser.parse_args()
    folder=ROOT/'tests/results'/FOLDERS[args.checkpoint];manifest=json.loads((folder/'manifest.json').read_bytes());pin=manifest['archive'];archive=folder/pin['path']
    need(manifest['kind']==args.checkpoint and archive.name=='captures.zip' and sha(archive.read_bytes())==pin['sha256'] and archive.stat().st_size==pin['bytes'],'exact checkpoint/archive identity')
    rows=manifest['files'];need(len({r['path'] for r in rows})==len(rows)==manifest['logical_files'],'unique logical census');blobs={}
    with zipfile.ZipFile(archive) as z:
        need(len(z.infolist())==manifest['physical_blobs']==len({r['blob'] for r in rows}),'physical census')
        for entry in z.infolist():
            body=z.read(entry);need(re.fullmatch('blobs/[a-f0-9]{64}',entry.filename) and entry.filename=='blobs/'+sha(body),'physical byte identities')
            need(not body.startswith((b'\x7fELF',b'MZ',b'!<arch>\n',b'OggS',b'OFAM101\0')),'no executable/audio payload');blobs[entry.filename]=body
    data={}
    for row in rows:
        p=PurePosixPath(row['path']);body=blobs[row['blob']];need(not p.is_absolute() and '..' not in p.parts and p.as_posix()==row['path'],'contained logical paths')
        need(sha(body)==row['sha256'] and len(body)==row['bytes'],'all logical identities');data[row['path']]=body
    omitted=manifest['omitted_local_files'];need(all(name not in data and row['original_retained_locally'] and row['byte_payload_published'] is False and row['bytes']>=0 for name,row in omitted.items()),'explicit payload omissions')
    def take(name):need(name in data,'required original evidence '+name);return data[name]
    def identity(name,digest,size=None):
        if name in data:need(sha(data[name])==digest and (size is None or len(data[name])==size),'included original identity')
        else:need(name in omitted and omitted[name]['sha256']==digest and (size is None or omitted[name]['bytes']==size),'omitted identity, bytes not read')
    for path,digest in manifest['canonical_source_sha256'].items():need(sha((ROOT/path).read_bytes())==digest,'current reviewed canonical component '+path)
    reports={}
    for label,digest in manifest['report_sha256'].items():
        report=json.loads(take(label+'/report.json'));need(sha(take(label+'/report.json'))==digest,'exact original capture report');reports[label]=report
        for source in report['sources']:identity(label+'/'+source['snapshot'],source['sha256'],source['bytes'])
        for command in report['commands']:
            need(command['state']=='complete' and command['pid']>0 and isinstance(command['exit_status'],int),'genuine terminal child record')
            for stream in ('stdout','stderr'):
                pin=command[stream];identity(label+'/'+pin['path'],pin['sha256'],pin['bytes'])
        for key in ('executable','compiler_dependencies'):
            if key in report:
                pin=report[key];identity(label+'/'+pin['path'],pin['sha256'],pin['bytes'])
        for name,pin in report.get('fixtures',{}).items():identity(label+'/fixtures/'+name,pin['sha256'],pin['bytes'])
    final_label=manifest['final_capture'];final=reports[final_label]
    need(final['passed'] and final['completed'] and final['all_source_bindings_current'] and all(c['exit_status']==0 for c in final['commands']),'qualified final HOST capture')
    stdout=take(final_label+'/test.stdout.log');measurements=final['measurements'];kind=args.checkpoint
    if kind=='helpers':
        rows=[json.loads(line) for line in stdout.splitlines()];need(rows==measurements and len(rows)==16,'unchanged full helper inventory')
        need(rows[0]['valid_nm_pairs']==16511 and rows[0]['all_channel_counts']==132088 and rows[0]['all_decoded_indices']>2000000 and
            rows[-1]['assertions']==9498670 and rows[-1]['creator_cases']==11 and rows[-1]['passed'],'explicit N/M/C and single-index/selected-map coverage')
        active=[r for r in rows if r['suite']=='creator-differential'];extreme=[r for r in rows if r['suite']=='creator-extreme-plc']
        need(len(active)==11 and all(v['bounded_gather_exact'] and v['float_samples_exact']>0 and v['needed_handles']<=8 for v in active),'real active creator map differentials')
        need([(r['streams'],r['coupled'],r['decoded_channels']) for r in extreme]==[(255,0,255),(128,127,255)] and all(v['exact'] for v in extreme),'labelled maximum-count PLC cases')
    elif kind=='packets':
        rows=[json.loads(line) for line in stdout.splitlines()];need(rows[-1]==measurements and rows[:-1]==final['realloc_controls'] and len(rows)==19,'original final packet/fault records')
        need(final['allocation_failure_injected'] is True and measurements['owner_schedules']==65 and measurements['creator_libogg_walks']==18 and
            measurements['borrowed_packets']==202 and measurements['copied_packets']==148 and measurements['realloc_ordinals']==measurements['retry_cases']==measurements['abandon_cases']==9,'complete bounded host packet-owner coverage')
        need([(r['ordinal'],r['retry']) for r in rows[:-1]]==[(i,retry) for i in range(1,10) for retry in (False,True)] and all(
            r['held_page_preserved'] and r['cursor_prefix_token_preserved'] and r['cleanup_live_bytes']==0 and r['packets']==int(r['retry']) for r in rows[:-1]),'all host realloc ordinals retry/abandon with no premature page retirement')
        original=reports['host01'];need(original['passed'] and original['allocation_failure_injected'] is False and original['measurements']['owner_schedules']==46 and
            not original['measurements']['allocation_failure_injected'],'initial genuine PASS retained without fault coverage')
        interim=reports['host02'];need(interim['passed'] and interim['allocation_failure_injected'] is False and interim['measurements']['allocation_failure_injected'] is True,
            'interim reporting mismatch preserved and excluded from final qualification')
        need(not final['decoder_executed'] and not final['decoder_drain_claimed'] and not measurements['decoder_drain_claimed'],'metadata ownership does not assert decoder drain')
    else:
        actual=json.loads(stdout);need(actual==measurements and actual['passed'] and actual['positive_cases']==13 and actual['host_contract_controls']==22 and
            actual['creator_pcm_samples_exact']==2679360 and actual['stable_cfg_addresses'],'complete real creator synthesis and anchored cfg contract inventory')
        need(final['host_public_api_test_double'] and final['creator_synthesis_real'] and actual['scripted_host_statuses'] and actual['owner_allocator_host_seam'] and
            actual['native_esp_oom_qualified'] is False and final['native_esp_oom_qualified'] is False,'scripted HOST error models are never native allocation evidence')
        failed=reports['host01'];need(not failed['passed'] and failed['commands'][-1]['name']=='build' and failed['commands'][-1]['exit_status']==1 and
            b'esp_audio_dec_reg.h' in take('host01/build.stderr.log'),'original missing-public-header build failure preserved')
        long_case=final['fixtures']['stereo120.packets'];need(long_case['complete_original_packets']==92 and long_case['coded_bodies_unchanged'],'complete original120ms stream retained')
    need(measurements==manifest['final_measurements'] and manifest['native_executed'] is False and manifest['production_selected'] is False and
        manifest['native_esp_oom_qualified'] is False and manifest['all_standard_layouts_qualified'] is False,'bounded HOST-only qualification scope')
    print(json.dumps(dict(checkpoint_verified=kind,native_executed=False,production_selected=False,omitted_binary_or_PCM_bytes_read=False,
        logical_files=len(data),preserved_captures=len(reports))))
if __name__=='__main__':main()
