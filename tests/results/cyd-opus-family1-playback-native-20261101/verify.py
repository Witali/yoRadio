"""Check saved standalone native evidence as data; execute no archived/native code or binary payload."""
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
def events(text,reference):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack overflow',text,re.I),'no native runtime fault')
    rows=[]
    for line in text.replace('\r\n','\n').splitlines():
        if not line.startswith('AF_'):continue
        parts=line.split();values=dict(p.split('=',1) for p in parts[1:]);need(len(values)==len(parts)-1,'unique real fields');rows.append(dict(tag=parts[0],**{k:v if k in ('sdk','sha') else int(v) for k,v in values.items()}))
    begin=rows[0];need(begin==dict(tag='AF_BEGIN',sdk='6.0.2',coordinator=0,worker=1,priority=5,stack=16384,fixtures=12,adapter_bytes=632,decoder_bytes=244,tags_bytes=56,zero_bytes=2048,hardware=0),'exact target ABI/profile observation')
    results=[r for r in rows if r['tag']=='AF_RESULT'];need(len(results)==34 and not any(r['tag']=='AF_FAILURE' for r in rows),'all complete genuine reference/adapter cases')
    refs={};observations=[];total_opens=total_calls=0
    for row in results:
        key=(row['kind'],row['fixture'],row['schedule']);source=reference['fixtures'][row['fixture']];selected=source['needed_streams'] if row['kind'] else list(range(source['streams']))
        own=[r for r in rows if r['tag'] in ('AF_OPEN','AF_CALL','AF_CLOSE','AF_FRAMES') and (r['kind'],r['fixture'],r['schedule'])==key];opened=[r for r in own if r['tag']=='AF_OPEN'];calls=[r for r in own if r['tag']=='AF_CALL'];closed=[r for r in own if r['tag']=='AF_CLOSE'];frames=[r for r in own if r['tag']=='AF_FRAMES']
        need(row['complete']==1 and row['driver']==row['close_errors']==row['live']==0 and row['integrity']==row['lifetime']==1 and row['core']==1 and row['priority']==5 and
            row['before']==row['after']==283212 and 0<row['stack_free']<=16384 and row['heap_min']>0,'actual successful cleanup/lease/resources')
        need(row['opens']==len(opened)==row['closes']==len(closed)==len(selected) and [r['stream'] for r in opened]==[r['stream'] for r in closed]==[r['stream'] for r in frames]==selected,'all genuine selected handles/close/frame records')
        need(all(r['result']==0 and r['handle']==1 and r['rate']==48000 and r['channels']==(2 if r['stream']<source['coupled'] else 1) and r['self_delimited']==int(r['stream']+1<source['streams']) for r in opened) and
            all(r['result']==r['pending']==0 for r in closed) and all(r['frames']==source['raw'] for r in frames),'public configuration, actual return and complete per-stream frames')
        need(row['calls']==len(calls) and [r['call'] for r in calls]==list(range(1,len(calls)+1)) and row['consumed']==sum(r['consumed'] for r in calls) and row['decoded']==sum(r['decoded'] for r in calls) and row['outputs']==sum(r['decoded']>0 for r in calls),'exact original public call accounting')
        for stream in selected:
            actual=[r for r in calls if r['stream']==stream];width=2 if stream<source['coupled'] else 1
            need(sum(r['consumed'] for r in actual)==sum(p['parts'][stream]['bytes'] for p in source['packets']) and sum(r['decoded'] for r in actual)==source['raw']*width*2,'complete original selected input and PCM')
        need(all(r['consumed']<=r['len'] and r['decoded']<=r['capacity'] and r['result'] in (0,-8) for r in calls) and all(not r['decoded'] and r['needed']>r['capacity'] and r['needed']<=23040 for r in calls if r['result']==-8),'actual public output resize protocol')
        need(row['pcm']==source['logical']*source['channels']*2 and 0<row['max_chunk']<=128*source['channels']*2 and re.fullmatch('[a-f0-9]{64}',row['sha']),'full clipped output digest and bounded geometry')
        if row['kind']:
            shape=source['split' if row['style'] else 'whole'];need(row['input_used']==shape['bytes'] and row['acks']==len(shape['pages']) and row['fixture'] in refs and
                row['sha']==refs[row['fixture']]['sha'] and row['pcm']==refs[row['fixture']]['pcm'],'complete real page retirement and exact independent direct-native PCM integration oracle')
        else:refs[row['fixture']]=row
        total_opens+=len(opened);total_calls+=len(calls);observations.append(dict(measurements=row,opens=opened,calls=calls,closes=closed,frames=frames,same_vendor_integration_oracle=True,independent_creator_numeric_conformance=False))
    expected={(0,f,0) for f in range(12)}|{(1,f,s) for f in range(12) for s in (range(4) if f<3 else range(2) if f==11 else range(1))}
    need({(r['kind'],r['fixture'],r['schedule']) for r in results}==expected and total_opens==116 and total_calls==1522 and sum(r['result']==-8 for r in rows if r['tag']=='AF_CALL')==3,'exact finite case/handle/call/long resize inventory')
    terminal=rows[-1];need(terminal==dict(tag='AF_COMPLETE',references=12,adapters=22,complete=1,before=283212,after=283212,heap_min=129648,stack_free=2364,live=0,core=1,priority=5,integrity=1),'exact authoritative terminal resources')
    controls=[r for r in rows if r['tag']=='AF_HASH_CONTROL'];need(controls==[dict(tag='AF_HASH_CONTROL',group=0,iterations=32,before=283312,after=283212),dict(tag='AF_HASH_CONTROL',group=1,iterations=32,before=283212,after=283212)],'separate genuine observer warm-up controls without codec attribution')
    return observations,begin,terminal,controls
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--require-current',action='store_true');args=parser.parse_args();manifest=json.loads((FOLDER/'manifest.json').read_bytes());pin=manifest['archive'];archive=FOLDER/pin['path']
    need(archive.name=='captures.zip' and sha(archive.read_bytes())==pin['sha256'] and archive.stat().st_size==pin['bytes'],'exact package archive');logical=manifest['files'];blobs={}
    need(len(logical)==manifest['logical_files']==len({r['path'] for r in logical}),'unique logical census')
    with zipfile.ZipFile(archive) as z:
        need(len(z.infolist())==manifest['physical_blobs']==len({r['blob'] for r in logical}),'physical census')
        for entry in z.infolist():
            body=z.read(entry);need(re.fullmatch('blobs/[a-f0-9]{64}',entry.filename) and entry.filename=='blobs/'+sha(body),'physical identity')
            need(not body.startswith((b'\x7fELF',b'MZ',b'!<arch>\n',b'OggS',b'OFAM101\0')),'no executable/encoded payload');blobs[entry.filename]=body
    data={}
    for row in logical:
        p=PurePosixPath(row['path']);body=blobs[row['blob']];need(not p.is_absolute() and '..' not in p.parts and p.as_posix()==row['path'] and len(body)==row['bytes'] and sha(body)==row['sha256'],'all contained logical identities');data[row['path']]=body
    omitted=manifest['omitted_local_files'];need(all(name not in data and row['original_retained_locally'] and row['byte_payload_published'] is False for name,row in omitted.items()),'explicit payload omissions')
    def take(name):need(name in data,'required original evidence '+name);return data[name]
    def identity(name,digest,size=None):
        if name in data:need(sha(data[name])==digest and (size is None or len(data[name])==size),'included original identity')
        else:need(name in omitted and omitted[name]['sha256']==digest and (size is None or omitted[name]['bytes']==size),'omitted identity; payload not read')
    reports={label:json.loads(take(label+'/report.json')) for label in ('native01','native02','syntax01','syntax02','audit01','replay01')}
    for label in ('native01','native02','replay01'):
        for command in reports[label]['commands']:
            need(command['state']=='complete' and command['pid']>0 and isinstance(command['exit_status'],int),'genuine terminal native/tool process')
            for stream in ('stdout','stderr'):identity(label+'/'+command['name']+'.'+stream+'.log',command[stream+'_sha256'])
    first=reports['native01'];need(not first['passed'] and not first['target_executed'] and any(c['name']=='build' and c['exit_status']==1 for c in first['commands']) and b'mbedtls/sha256.h' in take('native01/sdk-build.stdout.log'),'original diagnostic legacy-hash-header NONPASS preserved')
    child=json.loads(take('native01/sdk-child.json').decode('utf-8-sig'));need(child['pid']>0 and child['exit_status']==2,'original SDK nonzero child')
    second=reports['native02'];child=json.loads(take('native02/sdk-child.json').decode('utf-8-sig'));need(not second['passed'] and not second['target_executed'] and second['failure']=='actual target immutable zero storage' and child['exit_status']==0,'original SDK zero / observer NONPASS preserved')
    for label in ('native01','native02'):
        sources=json.loads(take(label+'/source-manifest.json'))
        for row in sources.values():identity(label+'/'+row['snapshot'],row['sha256'],row['bytes'])
    bundle=json.loads(take('native02/execution-bundle.json'))
    for path,digest in bundle['artifacts'].items():identity('native02/'+path,digest)
    closure=json.loads(take('native02/actual-compiler-closure.json'));need({'main.c','direct_reference.c'}<={Path(r['file']).name for r in closure['translation_units']},'actual diagnostic TUs')
    direct=next(r for r in closure['translation_units'] if Path(r['file']).name=='direct_reference.c');need(not {'opus_family1_playback.h','opus_family1_decoder.h','opus_family1_mapping.h','opus_multistream_framing.h','opus_pcm_trim.h','ogg_page_input.h'}&{Path(p).name for p in direct['actual_dependency_paths']},'independent direct reference component closure')
    need(not reports['syntax01']['passed'] and reports['syntax01']['commands'][0]['exit_status']==1 and take('syntax01/main.c.stderr.log').count(b'error: format')==5,'five actual diagnostic type errors preserved')
    need(reports['syntax02']['passed'] and reports['syntax02']['syntax_only'] and not reports['syntax02']['target_executed'] and len(reports['syntax02']['commands'])==2 and all(c['exit_status']==0 for c in reports['syntax02']['commands']),'actual fresh syntax-only PASS')
    need(not reports['audit01']['passed'] and not reports['audit01']['target_executed'] and 'No space left on device' in reports['audit01']['failure'],'original storage NONPASS before execution')
    replay=reports['replay01'];need(replay['passed'] and replay['completed'] and replay['target_executed'] and not replay['sdk_build_executed'] and replay['artifacts_read_in_place'] and all(c['exit_status']==0 for c in replay['commands']),'authoritative exact-image replay terminal zero')
    need(replay['artifacts']==bundle['artifacts'] and replay['sources']==bundle['sources'],'all exact original02 artifact/source provenance retained')
    audit=replay['image_audit'];need(audit['passed'] and audit['own_symbol']['bytes']==audit['own_input_section']['bytes']==2048 and audit['own_input_section']['flags']==2 and
        audit['aggregate_output_section']['name']=='.flash.rodata' and audit['aggregate_output_section']['flags']==3 and audit['nm_class']=='d' and
        audit['drom_origin']<=audit['own_symbol']['value']<audit['own_symbol']['value']+2048<=audit['drom_end'] and audit['elf_zero_sha256']==sha(bytes(2048)),'actual non-W input / aggregate WA / nm d and DROM object audit, without relabelling')
    need(b'.rodata.ofp_zero_chunk' in take('replay01/own-object-sections.stdout.log') and b'drom0_0_seg (R)' in take('replay01/audit/memory.ld') and b'REGION_ALIAS("default_rodata_seg", drom0_0_seg)' in take('replay01/audit/memory.ld'),'primary actual section/region evidence')
    reference=json.loads(take('native02/fixture-preparation.json'));text=take('replay01/qemu.stdout.log').decode().replace('\r\n','\n');cases,begin,terminal,controls=events(text,reference);measured=replay['measurements']
    need(cases==measured['cases'] and begin==measured['begin'] and terminal==measured['terminal'] and controls==measured['hash_controls'] and measured['gate_passed'] and
        not measured['creator_numeric_conformance_claim'] and not measured['new_tolerance_applied'] and not measured['production_selected'],'all saved claims join original complete native events')
    changed=[text.replace('consumed=580','consumed=581',1),text.replace('result=0 handle=1','result=-7 handle=1',1),text.replace('AF_CLOSE kind=0 fixture=0 schedule=0 slot=0 stream=0 result=0 pending=0\n','',1),text.replace('frames=10560','frames=10559',1),text.replace('lifetime=1','lifetime=0',1),text.replace('after=283212','after=283211',1)]
    for contradiction in changed:
        need(contradiction!=text,'contradictory control changes actual evidence')
        try:events(contradiction,reference)
        except ValueError:pass
        else:raise ValueError('contradictory native evidence accepted')
    if args.require_current:
        for path,digest in manifest['canonical_source_sha256'].items():need(sha((ROOT/path).read_bytes())==digest,'current canonical source '+path)
    need(manifest['production_selected'] is False and manifest['full_application_qualified'] is False and manifest['native_oom_injected'] is False and manifest['universal_conformance_claim'] is False,'bounded standalone scope')
    print(json.dumps(dict(native_checkpoint_verified=True,current_sources_required=args.require_current,direct_references=12,adapter_cases=22,public_handles=116,public_calls=1522,rejected_controls=len(changed),retained_bytes=0,omitted_binary_or_PCM_payload_read=False,full_application_qualified=False)))
if __name__=='__main__':main()
