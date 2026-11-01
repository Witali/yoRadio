"""Data-only complete gain-task evidence reader; no compiler, emulator or archived code.

Images, full PCM/hex logs and contact-bearing header bytes are omitted. Their recorded hash bindings
are checked without claiming to read those omitted original payloads.
"""
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]


def need(value,reason):
    if not value: raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def verify():
    manifest=json.loads((FOLDER/'manifest.json').read_bytes())
    archive_path=FOLDER/manifest['archive']['path']
    need(archive_path.name=='captures.zip' and archive_path.stat().st_size==manifest['archive']['bytes'] and
         sha(archive_path.read_bytes())==manifest['archive']['sha256'],'complete archive bytes')
    rows=manifest['files'];blob_names={row['blob'] for row in rows}
    need(len({row['path'] for row in rows})==len(rows)==manifest['logical_files'],'unique complete logical inventory')
    with zipfile.ZipFile(archive_path) as archive:
        need(len(archive.infolist())==len(blob_names)==manifest['physical_blobs'] and set(archive.namelist())==blob_names,'exact deduplicated physical inventory')
        blobs={name:archive.read(name) for name in blob_names}
    files={}
    for row in rows:
        relative=PurePosixPath(row['path']);body=blobs[row['blob']]
        need(relative.as_posix()==row['path'] and not relative.is_absolute() and '..' not in relative.parts and
             ':' not in row['path'] and '\\' not in row['path'],'canonical logical path')
        need(re.fullmatch(r'blobs/[a-f0-9]{64}',row['blob']) and row['blob']=='blobs/'+sha(body) and
             sha(body)==row['sha256'] and len(body)==row['bytes'],'every published byte')
        need(relative.suffix.lower() not in ('.elf','.bin','.pcm') and
             not (body.startswith(b'\x7fELF') and int.from_bytes(body[16:18],'little')!=1),'no executable or PCM image payload published')
        files[row['path']]=body
    omitted={row['path']:row for row in manifest['omitted_local_payloads']}
    need(len(omitted)==len(manifest['omitted_local_payloads']) and all(row['original_retained_locally'] and
         row['byte_payload_published'] is False and row['bytes']>0 and re.fullmatch('[a-f0-9]{64}',row['sha256'])
         and name not in files for name,row in omitted.items()),'explicit whole-payload omission provenance')

    def take(name):
        need(name in files,'required original byte payload: '+name)
        return files[name]

    def bind(name,digest,size=None):
        if name in files:
            need(sha(files[name])==digest and (size is None or len(files[name])==size),'published original hash/size binding')
        else:
            need(name in omitted and omitted[name]['sha256']==digest and
                 (size is None or omitted[name]['bytes']==size),'omitted original hash/size binding; bytes remain unread')

    reader_path=ROOT/'tests/run-cyd-ogg-gain-task-qemu.py'
    reader_body=reader_path.read_bytes()
    need(sha(reader_body)==manifest['controller_sha256'] and take('verification/task-reader.py')==reader_body,
         'current pinned canonical data reader')
    need(take('verification/checkpoint-reader.py')==Path(__file__).read_bytes(),'checkpoint verifier source identity')
    spec=importlib.util.spec_from_file_location('reviewed_ogg_gain_task_reader',reader_path)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    report=json.loads(take('capture/report.json'))
    need(report['passed'] and report['completed'] and report['target_executed'] and report['all_bound_inputs_current'] and
         report['actual_audio_service_tu'] and report['actual_rtos'] and not report['production_firmware'] and
         not report['physical_device'] and not report['external_network'] and not report['private_codec_abi'] and
         not report['custom_decoder'],'actual complete native gate and scope')
    need(sha(take('capture/report.json'))==manifest['original_report_sha256'],'unmodified original outer report')
    for row in report['commands']:
        need(row['state']=='complete' and row['pid']>0 and row['exit_status']==0,'actual native command terminal zero')
        for stream in ('stdout','stderr'):
            bind('capture/'+row['name']+'.'+stream+'.log',row[stream+'_sha256'])
    names=[row['name'] for row in report['commands']]
    need(len(set(names))==len(names) and all(name in names for name in
        ('sdk-head','sdk-clean','vendor-head','vendor-clean','repository-head','build','compiler-version','symbols','merge','qemu',
         'sdk-head-after','sdk-clean-after','vendor-head-after','vendor-clean-after')),'complete original native process inventory')
    child=json.loads(take('capture/sdk-child.json').decode('utf-8-sig'))
    need(child['pid']>0 and child['exit_status']==0,'actual SDK build driver terminal zero')
    sources=json.loads(take('capture/source-manifest.json'))
    bundle=json.loads(take('capture/execution-bundle.json'))
    need(bundle['sources']==sources and bundle['pcm_reference']==report['pcm_reference'] and
         bundle['sdk_commit']==reader.SDK_COMMIT and bundle['vendor_commit']==reader.VENDOR_COMMIT,
         'actual execution source/SDK/vendor/reference binding')
    for original,pin in sources.items(): bind('capture/'+pin['snapshot'],pin['sha256'],pin['bytes'])
    for relative,digest in bundle['artifacts'].items(): bind('capture/'+relative,digest)
    bind('capture/sources/controller.py',manifest['controller_sha256'])
    closure=json.loads(take('capture/actual-compiler-closure.json'))
    commands=json.loads(take('capture/build/compile_commands.json'))
    need(len(closure['translation_units'])==report['actual_translation_units']>=16 and
         len(closure['dependencies'])==report['actual_compiler_dependencies']>=421,'actual compiler selected TU/dependency census')
    for path,pin in closure['dependencies'].items():
        need(pin['manifest_original'] in sources and pin['sha256']==sources[pin['manifest_original']]['sha256'],
             'actual GCC dependency joins its original frozen source binding')
    actual_headers={PurePosixPath(path.replace('\\','/')).name for path in closure['dependencies']}
    need({'ogg_playback.h','ogg_page_input.h','opus_pcm_trim.h','ogg_opus_timeline.h','aac_public_config.h','pcm_header_gain.h','native_audio_normalizer.h','native_audio_settings.h','AudioNormalizer.h'}<=actual_headers,
         'actual compiler consumes the complete new playback/header path')
    for unit in closure['translation_units']:
        matching=[row for row in commands if row.get('file')==unit['file'] and row.get('output')==unit['output']]
        need(len(matching)==1 and all(unit.get(key)==value for key,value in matching[0].items()),
             'selected TU joins the original actual compiler command')
        path=unit['file'].replace('\\','/')
        matches=[pin for pin in sources.values() if path.casefold().endswith('/'+pin['snapshot'].replace('\\','/').casefold())]
        need(len(matches)==1,'selected TU joins exactly one frozen whole source')
        bind('capture/'+matches[0]['snapshot'],matches[0]['sha256'],matches[0]['bytes'])
        object_path=unit['output'].replace('\\','/')
        if re.match('^[A-Za-z]:/',object_path):
            object_path=object_path[len(manifest['original_capture_directory'].replace('\\','/'))+1:]
        else:
            object_path='build/'+object_path
        need(object_path in bundle['artifacts'],'actual selected object retained and bound')
        need(unit['actual_dependency_paths'] and set(unit['actual_dependency_paths'])<=set(closure['dependencies']),
             'each original compiler dependency record has a frozen byte/omission identity')
    config=json.loads(take('capture/build/config/sdkconfig.json'))
    need(config['YORADIO_OGG_TIMELINE'] is True and not config['FREERTOS_UNICORE'] and config['FREERTOS_HZ']==1000,
         'actual current dual-core timeline-enabled application profile')
    for key in ('HEAP_POISONING_LIGHT','FREERTOS_CHECK_STACKOVERFLOW_CANARY','COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE',
                'ESP_TASK_WDT_EN','ESP_TASK_WDT_INIT','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1'):
        need(config[key] is True,'actual original runtime guard: '+key)
    selected={PurePosixPath(row['file'].replace('\\','/')).name for row in closure['translation_units']}
    need(set(reader.MAIN_TUS)|{'native_audio_settings.c','native_audio_normalizer.cpp','AudioNormalizer.cpp'}<=selected,'all actual output/settings/normalizer owners compiled whole')
    refs=report['pcm_reference'];measured=report['measurements']
    need(not refs['normalization_enabled'] and not refs['numeric_conformance_claim'] and
         measured['actual_output_tu'] and not measured['normalization_enabled'] and not measured['vorbis_oracle_pending'],
         'whole rendering gate and independently completed stock Vorbis oracle')
    public=json.loads(take('capture/public-observations.json'))
    need(public['source_path']=='qemu.stdout.log' and public['source_sha256']==omitted['capture/qemu.stdout.log']['sha256'] and
         public['source_bytes']==omitted['capture/qemu.stdout.log']['bytes'] and public['omitted_stock_records']>8000 and
         public['omitted_stock_bytes']==2112000 and public['omitted_stock_sha256']==reader.PCM_SHA,
         'original complete console omission and explicit locally validated stock extraction identities')
    observations=[];previous=0
    for row in public['records']:
        body=row['text'].encode('utf-8')
        need(row['offset']>=previous and row['offset']+row['bytes']<=public['source_bytes'] and row['bytes']==len(body) and
             sha(body)==row['sha256'] and row['text'].startswith('CYD_OGG_GAIN_') and not row['text'].startswith('CYD_OGG_GAIN_STOCK '),
             'genuine non-PCM record byte identities, ordered positions and no stock payload')
        previous=row['offset']+row['bytes'];observations.append(row['text'].rstrip('\r\n'))
    need(observations[0]=='CYD_OGG_GAIN_TASK_BOOT actual_audio_service_tu=1 actual_output_tu=1 sdk=v6.0.2 coordinator=0 hardware=0',
         'current actual task/output observation scope')
    profiles=[line for line in observations if line.startswith('CYD_OGG_GAIN_TASK_PROFILE ')]
    need(profiles==['CYD_OGG_GAIN_TASK_PROFILE role=stream core=0 priority=3 stack=6144','CYD_OGG_GAIN_TASK_PROFILE role=decode core=1 priority=5 stack=16384','CYD_OGG_GAIN_TASK_PROFILE role=output core=1 priority=6 stack=4096'],'original actual task profiles')
    def rows(tag):return [reader.fields(line,tag) for line in observations if line.startswith(tag+' ')]
    for tag,key in [('CYD_OGG_GAIN_TASK_CASE','cases'),('CYD_OGG_GAIN_RENDER_CASE','render_cases'),('CYD_OGG_GAIN_LINK','source_links'),('CYD_OGG_GAIN_RENDER_LINK','render_links'),('CYD_OGG_GAIN_MEMORY','memory')]:
        need(rows(tag)==measured[key],'all published exact native records recount their original report')
    need(rows('CYD_OGG_GAIN_TASK_CHAIN')==[measured['chain']] and rows('CYD_OGG_GAIN_TASK_COMPLETE')==[measured['complete']], 'exact complete same-HTTP chain and final owner census')
    complete=measured['complete'];chain=measured['chain']
    need(complete['cases']==24 and complete['actual_audio_service_tu']==complete['actual_output_tu']==1 and complete['opens']==complete['closes']==38 and
         complete['http_cleanup']==30 and complete['live_decoders']==complete['live_clients']==0 and complete['resizes']==complete['retries']==13 and
         complete['output_flushes']==24 and complete['driver_created']==complete['driver_deleted']>0 and complete['preloads']>0 and complete['gain_stamps']>0 and
         complete['heap_integrity']==1,'real public decoder/client/driver/metadata/control census')
    need(chain['links']==9 and chain['one_http']==chain['same_generation']==chain['single_eof']==1 and chain['cross_link_reads']>0 and
         chain['pcm_bytes']==19008000 and chain['mono_bytes']==9504000,'nine ordered logical links and one final PCM terminal')
    plans={row['name']:row for row in [*refs['lifecycles'],*refs['full_cases'],refs['chain']]}
    expected=[(row['name'],case) for row in refs['lifecycles'] for case in ('T0','T1','T2')]+[(row['name'],'FULL') for row in refs['full_cases']]
    need([(row['fixture'],row['id']) for row in measured['cases']]==expected and len(measured['cases'])==23 and
         len(measured['source_links'])==len(measured['render_links'])==32,'complete full/lifecycle/chain matrix')
    post=report['vorbis_post_oracle'];need(post['passed'] and post['stock_bytes']==2112000 and post['stock_sha256']==reader.PCM_SHA and not post['production_helper_reused'],'actual independent post-run stock oracle completed')
    for source,render in zip(measured['source_links'],measured['render_links']):
        need(source['fixture']==render['fixture'] and source['index']==render['index'] and source['codec']==render['codec'],'ordered source/driver link correspondence')
        plan=plans[source['fixture']];link=plan['links'][source['index']]
        need(source['bytes']==2112000 and source['sha256']==link['source_sha'] and render['bytes']==1056000 and render['gain_q8']==link['gain_q8'] and render['volume']==plan['volume'],'whole unchanged source and actual ordered gain metadata')
        expected_hash=link['mono_sha'] if link['mono_sha'] else post['expected_mono_hashes'][str(plan['volume'])]
        need(render['sha256']==expected_hash,'every actual complete mono output agrees with its independent golden')
    for case in measured['cases']:
        need(case['pcm_bytes']==2112000 and case['writes']>0 and case['metadata']==1,'complete source extent')
        if case['id']=='T1':need(case['stop_reopen']==1 and case['stop_generation']>0 and case['discard_after_request']==case['stop_quiet']==1 and 0<case['partial_pcm']<2112000,'real partial Stop/discard/reopen')
        if case['id']=='T2':need(all(case[key]==1 for key in ('maintenance_resume','held_quiet','play_blocked','token_consumed','stale_rejected')) and 0<case['partial_pcm']<2112000,'real partial maintenance/token/resume')
    controls=[]
    for line in observations:
        tag=line.split(' ',1)[0]
        if tag.startswith('CYD_OGG_GAIN_CONTROL_'):controls.append([tag.removeprefix('CYD_OGG_GAIN_CONTROL_'),reader.fields(line,tag)])
    need(controls==measured['public_controls'],'every original genuine public Stop/discard control event recounted')
    need([row for tag,row in controls if tag=='CAPTURE_WAIT']==[dict(fixture='LIFE_VORBIS',fixed_budget_ms=90000,ordinary_budget_ms=30000,whole_qemu_budget_ms=600000)],'exact fixed first-capture observer deadline; ordinary lifecycle and whole-QEMU bounds unchanged')
    discards=[row for tag,row in controls if tag=='DISCARD']
    need([row['sequence'] for row in discards]==list(range(1,len(discards)+1)) and all(row['core']==1 and row['priority']==6 and row['real_returned']==1 for row in discards),'original output owner forwards and completes every real discard')
    for plan in refs['lifecycles']:
        name=plan['name'];parts={tag:[row for found,row in controls if found==tag and row['fixture']==name] for tag in ('STOP_REQUEST','STOP_RETURN','STOP_QUIET')}
        need(all(len(rows)==1 for rows in parts.values()),'one genuine request/return/quiet interval per Stop')
        request,returned,quiet=(parts[tag][0] for tag in ('STOP_REQUEST','STOP_RETURN','STOP_QUIET'))
        matching=[row for row in discards if row['sequence']==request['before_sequence']+1]
        need(len(matching)==1,'one real later discard');discard=matching[0]
        need(request['before_generation']+1==returned['stop_generation']==quiet['stop_generation'] and
             request['time_us']<=returned['time_us']<=quiet['time_us'] and request['time_us']<=discard['time_us']<=quiet['time_us'] and
             discard['fixture']==name and quiet['discard_sequence']==discard['sequence'] and quiet['discard_snapshot_generation']==discard['snapshot_generation'],
             'real discard belongs to this Stop interval without a fabricated generation label')
        need(quiet['live_clients']==quiet['live_decoders']==quiet['input_ready']==quiet['input_reading']==quiet['input_writing']==0 and
             quiet['input_available']==quiet['input_leased']==quiet['no_eof']==1 and quiet['quiet_ticks']>=25 and
             all(quiet[key]==discard[key] for key in ('pcm_bytes','mono_bytes','writes','driver_writes')),'all three owners/input and real source/driver counters remain quiet before reopen')
    for role,size in [('stream',6144),('decode',16384),('output',4096)]:need(0<complete[role+'_stack_free']<=size,'actual original owner stack margin')
    witness=json.loads(take('witness/report.json'))
    need(witness['queued_gain_transition_proven'],'original whole-capture witness proves real queued gain overlap')
    need(witness['passed'] and witness['original_transcript_accepted'] and witness['rejected_controls']==len(witness['rejected'])==31 and
         not witness['native_campaign_repeated'] and not witness['original_reports_modified'] and witness['reader_sha256']==manifest['controller_sha256'], 'all real-data contradiction controls reject')
    need(take('witness/reader.py')==reader_body and take('witness/controller.py')==(ROOT/'tests/check-cyd-ogg-gain-task-reader.py').read_bytes(),'original executed witness sources')
    opened=source_complete=render_complete=0;queued=[]
    for line in observations:
        if ' fixture=GAIN_CHAIN ' not in line:continue
        tag=line.split(' ',1)[0]
        if tag=='CYD_OGG_GAIN_OBS_OPEN':
            if opened and source_complete<opened and refs['chain']['links'][opened-1]['gain_q8']!=refs['chain']['links'][opened]['gain_q8']:
                queued.append(dict(next_index=opened,source_links_complete=source_complete,render_links_complete=render_complete))
            opened+=1
        elif tag=='CYD_OGG_GAIN_LINK':source_complete+=1
        elif tag=='CYD_OGG_GAIN_RENDER_LINK':render_complete+=1
    need(opened==source_complete==render_complete==9 and queued,'actual later-gain decode overlaps earlier queued source PCM at output owner')
    host=json.loads(take('host/report.json'))
    need(host['passed'] and host['all_source_bindings_unchanged'] and host['test_records'][-1]['cases']==136 and
         all(row['passed'] for row in host['test_records']) and not host['test_records'][-1]['live_allocations'], 'original metadata wrapper ASan/UBSan host suite')
    for pin in host['sources']:bind('host/'+pin['snapshot'],pin['sha256'],pin['bytes'])
    bind('host/'+host['binary']['path'],host['binary']['sha256'],host['binary']['bytes'])
    for command in host['commands']:
        need(command['state']=='complete' and command['exit_status']==0 and command['pid']>0,'original host command terminal zero')
        for stream in ('stdout','stderr'):
            pin=command[stream];bind('host/'+pin['path'],pin['sha256'],pin['bytes'])
    need([json.loads(line) for line in take('host/test.stdout.log').decode().splitlines()]==host['test_records'] and
         not take('host/test.stderr.log') and any('-fsanitize=address,undefined' in command['argv'] for command in host['commands']), 'original exact host records and clean sanitizer execution')
    for number in (1,2,3):
        prefix='history/native'+str(number).zfill(2)+'/'
        earlier=json.loads(take(prefix+'report.json'))
        need(not earlier['passed'] and not earlier['completed'] and earlier['target_executed']==(number>1),'all earlier non-PASS statuses preserved without reclassification')
        expected_build_status=1 if number==1 else 0
        build_commands=[row for row in earlier['commands'] if row['name']=='build']
        need(len(build_commands)==1 and build_commands[0]['exit_status']==expected_build_status,'original activation versus completed SDK outcomes')
        for command in earlier['commands']:
            for stream in ('stdout','stderr'):bind(prefix+command['name']+'.'+stream+'.log',command[stream+'_sha256'])
    print(json.dumps(dict(passed=True,logical_files=len(files),physical_blobs=len(blobs),actual_translation_units=report['actual_translation_units'],
        actual_compiler_dependencies=report['actual_compiler_dependencies'],actual_cases=24,logical_links_in_one_http=9,decoder_handles_closed=38,
        http_clients_closed=30,rejected_witness_controls=31,host_wrapper_cases=136,queued_gain_boundaries=len(queued),executes_archived_or_native_code=False,
        omitted_bytes_read=False,omitted_pcm_mono_hashes_recomputed=False,physical_hardware_qualified=False,enabled_normalizer_qualified=False)))


if __name__=='__main__':verify()
