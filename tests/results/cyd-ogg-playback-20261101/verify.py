"""Verify original wrapper captures as data; execute no archived code/tools."""
import argparse
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import zipfile

FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]
RAW={'opus20':(2115840,'a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b','b63b58b563d2a20d90a7bef235e5c1099dc52433db19083492d9c7098345469f'),
     'opus120':(2119680,'670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684','4110db997c16a05c329284bb6105468752c25d67818e3a99b8c9d47c5f481fd0'),
     'vorbis':(2112000,'e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910','e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910')}


def need(condition,reason):
    if not condition:raise ValueError(reason)
def sha(body):return hashlib.sha256(body).hexdigest()


def analyze(text):
    text=text.replace('\r\n','\n')
    need(not re.search(r'Guru Meditation|assert failed|Backtrace:|CORRUPT HEAP|watchdog.*triggered',text,re.I),'no actual native panic')
    lines=[line for line in text.splitlines() if line.startswith('OGP_')]
    need(lines[0]=='OGP_BEGIN sdk=6.0.2 coordinator=0 worker=1 priority=3 stack=16384 initial_capacity=12288 fixtures=3 hardware=0','known actual worker')
    groups={key:[] for key in ('OGP_LINK','OGP_CASE','OGP_RESIZE','OGP_GUARD','OGP_FAILURE')}
    for line in lines[1:-1]:
        values=line.split();need(values[0] in groups,'known record')
        row=dict(pair.split('=',1) for pair in values[1:]);need(len(row)==len(values)-1,'unique fields')
        for key in row:
            if key not in ('case','id','fixture','raw_sha','sha','window_sha'):row[key]=int(row[key])
        groups[values[0]].append(row)
    links=groups['OGP_LINK'];cases=groups['OGP_CASE'];resizes=groups['OGP_RESIZE']
    expected=[f'{name}_{chunk}' for name in RAW for chunk in (0,4096,257,1)]+['opus20_offset_preskip','opus120_offset_preskip','opus_vorbis_opus_chain']
    need([row['id'] for row in cases]==expected and len(links)==17 and len(resizes)==6,'complete actual case/link/resize inventory')
    for row in links:
        raw_bytes,raw_sha,pcm_sha=RAW[row['fixture']]
        modified=row['case'].endswith('_offset_preskip')
        first=0 if row['fixture']=='vorbis' else (512 if modified else 312)*4
        end=2112000 if row['fixture']=='vorbis' else 528312*4
        need(row['raw']==raw_bytes and row['raw_sha']==raw_sha and row['pcm']==end-first and
             row['begin']==first and row['end']==end and row['sha']==row['window_sha'] and
             re.fullmatch('[a-f0-9]{64}',row['sha']) and (modified or row['sha']==pcm_sha), 'all raw/trimmed bytes and playback alignment windows')
        need(row['close_before_ack']==row['match']==1 and row['calls']>0 and row['outputs']>0 and
             row['resizes']==int(row['fixture']=='opus120'),'genuine per-link close/call/resize observations')
    for row in cases:
        own=[x for x in links if x['case']==row['id']]
        need(len(own)==row['links']==(3 if row['id'].endswith('_chain') else 1) and
             [x['link'] for x in own]==list(range(1,len(own)+1)) and
             sum(x['pcm'] for x in own)==row['pcm'] and sum(x['calls'] for x in own)==row['calls'] and
             sum(x['resizes'] for x in own)==row['resizes'] and row['core']==1 and row['priority']==3 and
             0<row['stack_free']<=16384 and row['before']>0 and row['after']>0,'independent complete case accounting')
    need([x['fixture'] for x in links if x['case']=='opus_vorbis_opus_chain']==['opus20','vorbis','opus120'],'ordered cross-codec chain')
    for row in resizes:
        need(row['capacity']==12288 and row['needed']==23040 and row['consumed']==row['decoded']==0 and row['result']==-8,'actual public resize arguments/results')
    guards=groups['OGP_GUARD'];failures=groups['OGP_FAILURE']
    need(len(guards)==len(failures)==1 and guards[0]['id']=='bad_crc_never_vendor' and
         guards[0]['calls_before']==guards[0]['calls_after']==2 and guards[0]['outputs']==0 and guards[0]['rejected']==1 and
         failures[0]['case']=='bad_crc_never_vendor' and failures[0]['status']==3 and failures[0]['cause']==-1,'CRC failure never submitted to vendor')
    final=re.fullmatch(r'OGP_COMPLETE cases=(\d+) heap_free=(\d+) heap_min=(\d+) stack_free=(\d+) core=1 priority=3 heap_integrity=1',lines[-1])
    need(final and int(final[1])==16 and all(int(final[i])>0 for i in (2,3,4)),'complete original terminal/integrity record')
    return groups


def negative_controls(text):
    source=text.replace('\r\n','\n')
    lines=source.splitlines();first=next(line for line in lines if line.startswith('OGP_LINK'))
    resize=next(line for line in lines if line.startswith('OGP_RESIZE'))
    guard=next(line for line in lines if line.startswith('OGP_GUARD'))
    controls=[source.replace(first+'\n','',1),source.replace('close_before_ack=1','close_before_ack=0',1),
              source.replace('raw=2115840','raw=2115836',1),source.replace('pcm=2112000','pcm=2111996',1),
              source.replace('begin=1248','begin=1244',1),source.replace('window_sha=b63b','window_sha=0000',1),
              source.replace(resize+'\n','',1),source.replace(resize,resize.replace('consumed=0','consumed=1'),1),
              source.replace(resize,resize.replace('needed=23040','needed=23039'),1),
              source.replace(guard,guard.replace('calls_after=2','calls_after=3'),1),
              source.replace('core=1 priority=3\n','core=0 priority=3\n',1),
              source.replace('OGP_COMPLETE cases=16','OGP_COMPLETE cases=15',1)]
    for altered in controls:
        need(altered!=source,'effective contradictory control')
        try:analyze(altered)
        except (ValueError,IndexError,KeyError):continue
        raise ValueError('contradictory native witness accepted')
    return len(controls)


def verify(require_current=False):
    manifest=json.loads((FOLDER/'manifest.json').read_bytes());pin=manifest['archive'];path=FOLDER/pin['path']
    need(path.name=='captures.zip' and path.parent==FOLDER and path.stat().st_size==pin['bytes'] and sha(path.read_bytes())==pin['sha256'],'exact archive')
    with zipfile.ZipFile(path) as archive:
        need(len(archive.namelist())==len(set(archive.namelist()))==manifest['physical_blobs'],'unique blob inventory')
        blobs={name:archive.read(name) for name in archive.namelist()}
    for name,body in blobs.items():need(name=='blobs/'+sha(body) and not (body.startswith(b'\x7fELF') and int.from_bytes(body[16:18],'little')!=1),'exact published bytes and no executable image')
    files={}
    for row in manifest['files']:
        name=row['path'];logical=PurePosixPath(name);body=blobs[row['blob']]
        need(not logical.is_absolute() and '..' not in logical.parts and name not in files and
             len(body)==row['bytes'] and sha(body)==row['sha256'],'unique contained logical bytes')
        files[name]=body
    need(len(files)==manifest['logical_files'],'complete logical inventory')
    omissions={row['path']:row for row in manifest['omitted_payloads']}
    need(all(name not in files and row['original_retained_locally'] and row['byte_payload_published'] is False for name,row in omissions.items()),'explicit excluded local payloads')
    def check(name,digest,size=None):
        if name in omissions:
            need(omissions[name]['sha256']==digest and (size is None or omissions[name]['bytes']==size),'omitted identity binding; omitted bytes not read')
        else:need(name in files and sha(files[name])==digest and (size is None or len(files[name])==size),'published source/artifact identity')
    for label,campaign in manifest['campaigns'].items():
        prefix=label+'/';check(prefix+'report.json',campaign['original_report_sha256'])
        report=json.loads(files[prefix+'report.json'])
        need(report['passed'] and report.get('all_source_bindings_unchanged',report.get('all_bound_inputs_current')),'original passing terminal and source bindings')
        for command in report['commands']:
            need(command['state']=='complete' and command['pid']>0 and command['exit_status']==0,'all original native commands terminal zero')
            for stream in ('stdout','stderr'):
                if campaign['kind']=='native':check(prefix+command['name']+'.'+stream+'.log',command[stream+'_sha256'])
                else:check(prefix+command[stream]['path'],command[stream]['sha256'],command[stream]['bytes'])
        if campaign['kind']=='host':
            need(report['actual_wrapper'] and not report['vendor_executed'],'explicit host API seams')
            for row in report['sources']:check(prefix+row['snapshot'],row['sha256'],row['bytes'])
            rows=[json.loads(line) for line in files[prefix+'test.stdout.log'].decode().splitlines()]
            need(rows==report['test_records'] and len(rows)==109 and all(row['passed'] for row in rows) and
                 rows[-1]['cases']==108 and rows[-1]['live_allocations']==0,'all actual wrapper host seam cases')
            continue
        need(report['completed'] and report['target_executed'] and not report['bound_input_failures'] and not report['actual_audio_service_tu'],'actual wrapper rather than complete production-task claim')
        check(prefix+'execution-bundle.json',campaign['original_bundle_sha256'])
        check(prefix+'source-manifest.json',campaign['original_source_manifest_sha256'])
        sources=json.loads(files[prefix+'source-manifest.json'])
        for original,row in sources.items():check(prefix+row['snapshot'],row['sha256'],row['bytes'])
        for name,digest in campaign['artifacts'].items():check(prefix+name,digest)
        closure=json.loads(files[prefix+'actual-compiler-closure.json'])
        need(len(closure['translation_units'])==report['actual_translation_units']==5 and
             len(closure['dependencies'])==report['actual_compiler_dependencies']==206,'actual five-TU/206-GCC-dependency closure')
        for row in closure['dependencies'].values():need(row['manifest_original'] in sources and sources[row['manifest_original']]['sha256']==row['sha256'],'every dependency resolves to exact source binding')
        commands=json.loads(files[prefix+'build/compile_commands.json'])
        for row in closure['translation_units']:
            need(any(all(row.get(k)==v for k,v in original.items()) for original in commands),'each TU joins original compile command')
            normalized=row['file'].replace('\\','/');object_name=row['output'].replace('\\','/')
            snapshot=normalized.split('/'+campaign['path']+'/',1)[-1]
            need(any(pin['snapshot']==snapshot for pin in sources.values()),'each selected TU has exact frozen source')
            if '/build/' in object_name:object_name=object_name.split('/build/',1)[1]
            need('build/'+object_name in campaign['artifacts'],'each selected TU has exact compiled object')
            need(normalized.casefold() in {p.replace('\\','/').casefold() for p in row['actual_dependency_paths']},'compiler dependency includes its selected source')
        child=json.loads(files[prefix+'sdk-child.json'].decode('utf-8-sig'));need(child['pid']>0 and child['exit_status']==0,'actual SDK driver child terminal zero')
        config=json.loads(files[prefix+'build/config/sdkconfig.json']);need(not config['FREERTOS_UNICORE'] and config['FREERTOS_HZ']==1000,'actual dual-core scheduler profile')
        for key in ('HEAP_POISONING_LIGHT','COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE','ESP_TASK_WDT_EN','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1'):need(config[key] is True,'actual guard enabled: '+key)
        transcript=files[prefix+'qemu.stdout.log'].decode()
        analyzed=analyze(transcript);need(len(analyzed['OGP_CASE'])==15 and negative_controls(transcript)==12,'complete PCM proof and rejected contradictory transcripts')
        if label=='native02':
            bundle=json.loads(files[prefix+'execution-bundle.json'])
            need(bundle['sources']==sources and bundle['artifacts']==campaign['artifacts'],'original public-safe final bundle joins source/artifact maps')
            need(any(key.startswith('runtime-path-redacted:') for key in bundle['runtime']),'explicit runtime identity alias')
            if require_current:
                for original,row in sources.items():need(sha(Path(original).read_bytes())==row['sha256'],'explicit current source binding')
    return dict(passed=True,logical_files=len(files),physical_blobs=len(blobs),native_cases=16,full_links=17,host_cases=108,
                rejected_transcript_controls=12,current_sources_compared=require_current,archived_code_executed=False,
                omitted_payload_bytes_read=False,production_audio_service_qualified=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--require-current',action='store_true')
    print(json.dumps(verify(parser.parse_args().require_current)))
