"""Data-only public composition evidence checks; no omitted PCM/native execution."""
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
    lines=[v for v in text.replace('\r\n','\n').splitlines() if v.startswith('MS_')]
    need(lines and lines[0]=='MS_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=3 stack=16384 fixtures=3 modes=2 public_raw_handles=1','known worker')
    need(not any(v.startswith('MS_PCM ') for v in lines),'payload lines excluded from event selection')
    calls={};opens={};closes={};streams={};cases=[];allocs={}
    for line in lines[1:-1]:
        parts=line.split();fields=dict(p.split('=',1) for p in parts[1:]);need(len(fields)==len(parts)-1,'unique complete event fields')
        row={k:int(v) for k,v in fields.items()};tag=parts[0];id=row['id']
        if tag=='MS_CASE':cases.append(row);continue
        need(tag in ('MS_CALL','MS_OPEN','MS_CLOSE','MS_STREAM','MS_ALLOC'),'known public event')
        lookup={'MS_CALL':calls,'MS_OPEN':opens,'MS_CLOSE':closes,'MS_STREAM':streams,'MS_ALLOC':allocs}[tag];lookup.setdefault(id,[]).append(row)
    need([r['id'] for r in cases]==list(range(6)),'complete six fresh cases')
    for id,case in enumerate(cases):
        channels=(3,6,8)[id//2];mode=id%2;info=reference['fixtures']['channels'+str(channels)]['framing'];n=info['streams'];m=info['coupled']
        need((case['encoded_channels'],case['streams'],case['coupled'],case['mode'])==(channels,n,m,mode),'exact independent layouts/framing')
        need(case['api_result_known']==1 and case['api_result']==case['driver_status']==0 and case['geometry_valid']==case['complete']==1 and
            case['opens']==case['close_calls']==n and case['close_errors']==0 and case['before']==case['after']==283704,'real successful per-case API/geometry/cleanup')
        need(case['core']==1 and case['priority']==3 and 0<case['stack_free']<=16384 and case['heap_min']>0,'actual diagnostic resources')
        need([r['stream'] for r in opens[id]]==[r['stream'] for r in closes[id]]==[r['stream'] for r in streams[id]]==list(range(n)) and
            len(allocs[id])==n and all(r['success']==1 for r in allocs[id]),'all simultaneous independent handles/buffers and closes')
        need(len(calls[id])==11*n and [(r['packet'],r['stream']) for r in calls[id]]==[(p,s) for p in range(11) for s in range(n)],'every full packet and elementary stream actually decoded')
        for s in range(n):
            width=2 if s<m else 1;opened=opens[id][s];closed=closes[id][s];summary=streams[id][s];own=[r for r in calls[id] if r['stream']==s]
            expected=sum(p['streams'][s]['common_bytes' if mode else 'original_bytes'] for p in info['packets'])
            need(opened['channels']==width and opened['rate']==48000 and opened['self_delimited']==int(mode==0 and s+1<n) and opened['result']==0 and
                opened['handle']==1 and closed['result']==0,'documented explicit cfg and genuine open/close returns')
            need([v['call'] for v in own]==list(range(1,12)) and all(v['result']==0 and v['consumed']==v['len'] and v['decoded']==960*width*2 and
                v['decoded']<=v['capacity'] and v['rate']==48000 and v['channels']==width and v['bits']==16 for v in own),'all original public decode returns and complete PCM geometry')
            need(summary['calls']==summary['outputs']==11 and summary['expected_input']==summary['consumed']==expected==sum(v['consumed'] for v in own) and
                summary['frames']==10560 and summary['pcm_bytes']==10560*width*2 and summary['last_result']==0 and summary['process_result_known']==1 and
                summary['closes']==1 and summary['close_result']==0,'full per-stream input/frame/output/close accounting')
    final=lines[-1].split();need(final[0]=='MS_COMPLETE','genuine final record');terminal={k:int(v) for k,v in (p.split('=',1) for p in final[1:])}
    need(terminal==dict(cases=6,heap_before=283704,heap_after=283704,retained=0,heap_min=150936,stack_free=3252,core=1,priority=3,heap_integrity=1),'exact honest final resources')
    return cases,calls,opens,closes,streams,terminal
def main():
    manifest=json.loads((FOLDER/'manifest.json').read_bytes());pin=manifest['archive'];archive=FOLDER/pin['path']
    need(archive.name=='captures.zip' and sha(archive.read_bytes())==pin['sha256'] and archive.stat().st_size==pin['bytes'],'exact archive')
    rows=manifest['files'];need(len({r['path'] for r in rows})==len(rows)==manifest['logical_files'],'unique logical census');blobs={}
    with zipfile.ZipFile(archive) as z:
        need(len(z.infolist())==manifest['physical_blobs']==len({r['blob'] for r in rows}),'exact physical census')
        for entry in z.infolist():
            body=z.read(entry);need(re.fullmatch('blobs/[a-f0-9]{64}',entry.filename) and entry.filename=='blobs/'+sha(body),'physical identity')
            need(not body.startswith((b'\x7fELF',b'MZ',b'!<arch>\n',b'OggS',b'OFAM101\0',b'MSPUB01\0')) and
                not re.search(rb'(?m)^MS_PCM id=\d+ stream=\d+ offset=\d+ bytes=\d+ hex=[0-9a-f]+',body),'no binary/audio/PCM payload')
            blobs[entry.filename]=body
    data={}
    for row in rows:
        name=PurePosixPath(row['path']);body=blobs[row['blob']];need(not name.is_absolute() and '..' not in name.parts and name.as_posix()==row['path'],'contained paths')
        need(sha(body)==row['sha256'] and len(body)==row['bytes'],'all logical identities');data[row['path']]=body
    omitted=manifest['omitted_local_files']
    def take(name):need(name in data,'required exact evidence '+name);return data[name]
    def identity(name,digest,size=None):
        if name in data:need(sha(data[name])==digest and (size is None or len(data[name])==size),'included source/artifact identity')
        else:need(name in omitted and omitted[name]['sha256']==digest and (size is None or omitted[name]['bytes']==size),'omitted original identity; bytes not read')
    need(all(name not in data and row['original_retained_locally'] and row['byte_payload_published'] is False and row['bytes']>=0 for name,row in omitted.items()),'honest local omission census')
    for path,digest in manifest['canonical_source_sha256'].items():need(sha((ROOT/path).read_bytes())==digest,'current reviewed canonical source '+path)
    reference=json.loads(take('reference01/report.json'));native=json.loads(take('native01/report.json'))
    need(sha(take('reference01/report.json'))==manifest['reference_original_report_sha256'] and reference['passed'] and reference['completed'] and
        reference['all_source_bindings_current'] and reference['framing_tests']=={'passed':True,'cases':32,'decoder_executed':False},'actual creator-qualified packet framing')
    need(sha(take('native01/report.json'))==manifest['native_original_report_sha256'] and native['passed'] and native['completed'] and native['target_executed'] and native['all_bound_inputs_current'] and
        not native['private_codec_abi'] and native['actual_translation_units']==4 and native['actual_compiler_dependencies']==146,'actual complete public native diagnostic')
    for label,report in (('reference01',reference),('native01',native)):
        for command in report['commands']:
            need(command['state']=='complete' and command['pid']>0 and command['exit_status']==0,'genuine terminal-zero child')
            for stream in ('stdout','stderr'):
                if label.startswith('reference'):
                    pin=command[stream];identity(label+'/'+pin['path'],pin['sha256'],pin['bytes'])
                else:identity(label+'/'+command['name']+'.'+stream+'.log',command[stream+'_sha256'])
    for row in reference['sources']:identity('reference01/'+row['snapshot'],row['sha256'],row['bytes'])
    sources=json.loads(take('native01/source-manifest.json'))
    for row in sources.values():identity('native01/'+row['snapshot'],row['sha256'],row['bytes'])
    bundle=json.loads(take('native01/execution-bundle.json'))
    for path,digest in bundle['artifacts'].items():identity('native01/'+path,digest)
    child=json.loads(take('native01/sdk-child.json').decode('utf-8-sig'));need(child['pid']>0 and child['exit_status']==0,'actual SDK child zero')
    closure=json.loads(take('native01/actual-compiler-closure.json'));original=json.loads(take('native01/build/compile_commands.json'))
    need(len(closure['translation_units'])==4 and len(closure['dependencies'])==146,'real compiler closure')
    for row in closure['translation_units']:need(sum(all(row.get(k)==v for k,v in actual.items()) for actual in original)==1 and
        set(row['actual_dependency_paths'])<=set(closure['dependencies']),'actual compiled source/command/dependency binding')
    need(not {'audio_service.c','native_audio_output.c','ogg_playback.h','decoder_registration.c','pcm_header_gain.h'} & {Path(p).name for p in closure['dependencies']},'no production/private adaptation consumed')
    for name,row in reference['fixtures'].items():
        actual=json.loads(take('reference01/'+name+'-reference.stdout.log'));need(actual==row['measurements'] and actual['creator']=='libopus 1.4' and actual['frames_per_stream']==10560 and
            actual['packets']==11 and actual['maximum_mapped_float_difference']==0 and actual['exact_creator_multistream_match'],'independent creator elementary handles reproduce every original multistream float')
        pin=row['transport'];identity('reference01/'+pin['path'],pin['sha256'],pin['bytes'])
        for path,pin in row['pcm'].items():identity('reference01/'+path,pin['sha256'],pin['bytes'])
    derivation=manifest['derivations'];need(len(derivation)==1,'exact explicit payload-removal derivation');derived=derivation[0]
    identity(derived['source'],derived['source_sha256'],derived['source_bytes']);identity(derived['output'],derived['output_sha256'],derived['output_bytes'])
    need(derived['removed_lines']>0 and derived['removed_bytes']>0 and derived['source_bytes']==derived['output_bytes']+derived['removed_bytes'],'original full UART identity and exact removal accounting')
    text=take('native01/qemu.events.log').decode();cases,calls,opens,closes,streams,terminal=events(text,reference)
    measured=native['measurements'];need(measured==manifest['native_measurements'] and len(measured['cases'])==6 and terminal==measured['complete'],'unchanged original measurement report')
    for id,row in enumerate(measured['cases']):
        need(row['measurements']==cases[id] and row['public_calls']==calls[id] and row['open_events']==opens[id] and row['close_events']==closes[id] and row['public_composition_complete_for_this_fixture'],
            'all saved claims join exact original non-PCM native events')
        for s,stream in enumerate(row['streams']):
            need(stream['measurements']==streams[id][s],'exact native per-stream summary');pin=stream['full_pcm'];identity('native01/'+pin['path'],pin['sha256'],pin['bytes'])
        pin=row['full_mapped_pcm'];identity('native01/'+pin['path'],pin['sha256'],pin['bytes'])
        comparison=row['mapped_comparison'];need(comparison['new_tolerance_applied'] is False and comparison['numeric_conformance_claim'] is False,'saved numeric observation is not a new acceptance threshold')
    for a,b in zip(measured['cases'][::2],measured['cases'][1::2]):
        need(a['full_mapped_pcm']['sha256']==b['full_mapped_pcm']['sha256'] and all(x['full_pcm']['sha256']==y['full_pcm']['sha256'] for x,y in zip(a['streams'],b['streams'])),
            'observed native original/self-delimited and common modes are byte-identical for every complete stream/mapping')
    changed_consumption=re.sub(r'(MS_CALL [^\n]*?consumed=)(\d+)',lambda m:m[1]+str(int(m[2])+1),text,count=1)
    bad=[text.replace('self_delimited=1','self_delimited=0',1),changed_consumption,text.replace('result=0','result=-7',1),
        text.replace('MS_CLOSE id=0 stream=0 result=0\n','',1),text.replace('frames=10560','frames=10559',1),text.replace('complete=1','complete=0',1),text.replace('retained=0','retained=1',1)]
    normalized=text.replace('\r\n','\n');bad=[v.replace('\r\n','\n') for v in bad]
    # The close-line control is applied after newline normalization as well.
    bad[3]=normalized.replace('MS_CLOSE id=0 stream=0 result=0\n','',1)
    for value in bad:
        need(value!=normalized,'contradictory control actually changes evidence')
        try:events(value,reference)
        except ValueError:pass
        else:raise ValueError('contradictory public event evidence accepted')
    need(manifest['mandatory_family1_playback_complete'] is False and manifest['production_integration'] is False and
        manifest['universal_conformance_claim'] is False and manifest['new_tolerance_applied'] is False,'bounded reuse-probe scope')
    print(json.dumps(dict(public_probe_verified=True,cases=6,public_handles=22,decoded_packets=242,framing_controls=32,rejected_controls=len(bad),
        native_framing_modes_byte_identical=True,retained_bytes=0,omitted_binary_or_PCM_bytes_read=False,numeric_observations_recomputed=False,
        mandatory_family1_playback_complete=False)))
if __name__=='__main__':main()
