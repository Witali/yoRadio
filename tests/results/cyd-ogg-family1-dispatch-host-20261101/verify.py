"""Verify saved creator-backed dispatcher and unchanged legacy HOST evidence as data only."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import zipfile
FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]
def need(value,why):
    if not value:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--require-current',action='store_true');args=parser.parse_args();manifest=json.loads((FOLDER/'manifest.json').read_bytes());pin=manifest['archive'];archive=FOLDER/pin['path']
    need(archive.name=='captures.zip' and sha(archive.read_bytes())==pin['sha256'] and archive.stat().st_size==pin['bytes'],'exact archive identity');rows=manifest['files'];need(len(rows)==manifest['logical_files']==len({r['path'] for r in rows}),'logical census');blobs={}
    with zipfile.ZipFile(archive) as z:
        need(len(z.infolist())==manifest['physical_blobs']==len({r['blob'] for r in rows}),'physical census')
        for entry in z.infolist():
            body=z.read(entry);need(re.fullmatch('blobs/[a-f0-9]{64}',entry.filename) and entry.filename=='blobs/'+sha(body),'physical identities');need(not body.startswith((b'\x7fELF',b'MZ',b'!<arch>\n',b'OggS',b'OFAM101\0')),'no binary payload');blobs[entry.filename]=body
    data={}
    for row in rows:
        path=PurePosixPath(row['path']);body=blobs[row['blob']];need(not path.is_absolute() and '..' not in path.parts and path.suffix.lower()!='.pyc' and path.as_posix()==row['path'] and len(body)==row['bytes'] and sha(body)==row['sha256'],'all contained non-bytecode logical identities');data[row['path']]=body
    omitted=manifest['omitted_local_files'];need(all(name not in data and r['original_retained_locally'] and r['byte_payload_published'] is False for name,r in omitted.items()),'explicit local omissions')
    def take(name):need(name in data,'required original evidence '+name);return data[name]
    def identity(name,digest,size=None):
        if name in data:need(sha(data[name])==digest and (size is None or len(data[name])==size),'included original identity')
        else:need(name in omitted and omitted[name]['sha256']==digest and (size is None or omitted[name]['bytes']==size),'omitted identity; bytes not read')
    reports={}
    for label in ('dispatch01','dispatch02','legacy01','gain01'):
        report=json.loads(take(label+'/report.json'));reports[label]=report
        for row in report['sources']:identity(label+'/'+row['snapshot'],row['sha256'],row['bytes'])
        for command in report['commands']:
            need(command['state']=='complete' and command['pid']>0 and isinstance(command['exit_status'],int),'actual terminal HOST child')
            for stream in ('stdout','stderr'):
                pin=command[stream];identity(label+'/'+pin['path'],pin['sha256'],pin['bytes'])
        for key in ('executable','binary','compiler_dependencies'):
            if key in report:
                row=report[key];identity(label+'/'+row['path'],row['sha256'],row['bytes'])
    failed=reports['dispatch01'];need(not failed['passed'] and failed['commands'][-1]['name']=='build' and failed['commands'][-1]['exit_status']==1 and b'misleading-indentation' in take('dispatch01/build.stderr.log'),'original new-harness warning-as-error preserved')
    final=reports['dispatch02'];need(final['passed'] and final['completed'] and final['all_source_bindings_current'] and all(c['exit_status']==0 for c in final['commands']),'complete actual integrated HOST capture')
    records=[json.loads(line) for line in take('dispatch02/test.stdout.log').splitlines()];need(records==final['test_records'] and len(records)==56 and all(r['passed'] for r in records),'all unchanged original case records')
    summary=records[-1];need(summary==final['measurements']==manifest['measurements'] and summary['positive_schedules']==43 and summary['host_controls']==12 and
        summary['creator_pcm_samples_exact']==12983296 and summary['family1_output_chunks']==20052 and summary['legacy_output_chunks']==552 and summary['gain_layout_forwarded'] and
        summary['close_retry_preserves_cfg_page_planes'] and not summary['native_oom_qualified'] and not summary['production_task_executed'],'exact real creator sample/dispatch inventory')
    positive=[r for r in records[:-1] if r['kind'] in ('family1','chain')];need([r['case'] for r in positive]==list(range(1,44)) and len([r for r in positive if r['kind']=='family1'])==39,'all positive schedules')
    for row in positive:
        need(row['simple_opens']==row['simple_closes'],'actual simple cleanup')
        if row['kind']=='family1':need(row['raw_created']==row['raw_destroyed'] and row['simple_opens']==row['prepared_simple'] and row['frames'] in (9600,528000),'actual raw ownership and full logical frames')
    close=[r for r in records if r.get('kind')=='close-control'];need([(r['mode'],r['status'],r['close_witness'],r['raw_created'],r['raw_destroyed'],r['close_calls'],r['published_frames']) for r in close]==[(0,0,1,5,5,6,9600),(1,1,1,5,5,7,9600),(2,4,0,5,5,7,9600)],'real creator-backed retry/reset-refusal observations')
    failure=[r for r in records if r.get('kind')=='failure-control'];need([r['mode'] for r in failure]==list(range(8)) and all(r['status']==r['expected'] for r in failure) and [r['published_frames'] for r in failure]==[256,256,0,0,0,0,0,0],'partial-send/cancel/allocation/container controls')
    need(failure[4]['cause']==15360 and failure[5]['cause']==11520 and len([r for r in records if r.get('kind')=='tag-control' and not r['public_raw_opens'] and not r['public_simple_opens']])==1,'ordinary allocator request details and invalid Tags rejected before either public decoder')
    for label,cases,suite in (('legacy01',108,'ogg-playback-host'),('gain01',136,'ogg-playback-gain-host')):
        report=reports[label];records=[json.loads(line) for line in take(label+'/test.stdout.log').splitlines()];need(report['passed'] and report['state']=='complete' and report['all_source_bindings_unchanged'] and
            records==report['test_records'] and len(records)==cases+1 and all(r['passed'] for r in records) and records[-1]['suite']==suite and records[-1]['cases']==cases and not records[-1]['live_allocations'],'unchanged full legacy regression records')
        names={Path(r['path']).name for r in report['sources']};need({'esp_audio_types.h','esp_audio_dec.h','esp_audio_dec_reg.h','esp_opus_dec.h','esp_audio_simple_dec.h','ogg_legacy_raw_unselected.c'}<=names and
            not any('/host_include/' in r['snapshot'] for r in report['sources']),'actual official header ABI and abort-only unselected seam, no invented stub selected')
    lower=json.loads((ROOT/'tests/results/cyd-opus-family1-playback-tags-20261101/manifest.json').read_bytes())['canonical_source_sha256']['tests/native/opus_family1_playback_host.c']
    helper=next(r for r in final['sources'] if r['path'].replace('\\','/').endswith('/tests/native/opus_family1_playback_host.c'));need(helper['sha256']==lower,'immutable real creator lower helper')
    stress=json.loads(take('stress01/results/report.json'));driver=json.loads(take('stress01/driver.json'));need(driver['passed'] and driver['completed'] and driver['state']=='complete' and driver['pid']>0 and driver['exit_status']==0 and
        stress['passed'] and stress['libopus_version']=='libopus 1.4' and len(stress['cat_events'])==55 and all(r['result']==0 for r in stress['cat_events']) and len(stress['outputs'])==10 and
        stress['durations']==[5760,4800] and stress['raw_frames']==10560 and stress['logical_frames']==9600 and stress['pre_skip']==312 and stress['every_coded_frame_preserved'] and stress['creator_full_float_exact'] and not stress['new_tolerance_applied'],'actual public creator repacketizer preserves every coded body/time/complete float output')
    for row in driver['sources']:identity('stress01/'+row['snapshot'],row['sha256'],row['bytes'])
    identity('stress01/results/channels8-120ms.packets',stress['transport']['sha256'],stress['transport']['bytes'])
    need(stress['transport']['sha256']=='c6a06d1bf954c9119f844167d43b3f080bdbe4e7c2a305318109e524cf3b6757','exact active C8 stress transport')
    if args.require_current:
        for path,digest in manifest['canonical_source_sha256'].items():need(sha((ROOT/path).read_bytes())==digest,'current reviewed checkpoint '+path)
    need(not manifest['native_executed'] and not manifest['native_esp_oom_qualified'] and not manifest['production_task_executed'],'bounded HOST-only qualification scope')
    print(json.dumps(dict(dispatch_checkpoint_verified=True,current_sources_required=args.require_current,positive_schedules=43,host_controls=12,legacy_cases=108,gain_cases=136,creator_samples=12983296,
        native_executed=False,omitted_binary_or_PCM_bytes_read=False,PCM_comparisons_recomputed=False)))
if __name__=='__main__':main()
