"""Data-only actual-task evidence reader; no compiler, emulator or archived code.

Image/contact-bearing header bytes are omitted. Their recorded hash bindings
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

    reader_path=ROOT/'tests/run-cyd-ogg-playback-task-qemu.py'
    reader_body=reader_path.read_bytes()
    need(sha(reader_body)==manifest['controller_sha256'] and take('verification/task-reader.py')==reader_body,
         'current pinned canonical data reader')
    need(take('verification/checkpoint-reader.py')==Path(__file__).read_bytes(),'checkpoint verifier source identity')
    spec=importlib.util.spec_from_file_location('reviewed_ogg_actual_task_reader',reader_path)
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
    need(len(closure['translation_units'])==report['actual_translation_units']==11 and
         len(closure['dependencies'])==report['actual_compiler_dependencies']==421,'actual compiler selected TU/dependency census')
    for path,pin in closure['dependencies'].items():
        need(pin['manifest_original'] in sources and pin['sha256']==sources[pin['manifest_original']]['sha256'],
             'actual GCC dependency joins its original frozen source binding')
    actual_headers={PurePosixPath(path.replace('\\','/')).name for path in closure['dependencies']}
    need({'ogg_playback.h','ogg_page_input.h','opus_pcm_trim.h','ogg_opus_timeline.h','aac_public_config.h'}<=actual_headers,
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
    refs=report['pcm_reference']
    need(list(refs['fixtures'])==['OPUS20','OPUS120','VORBIS'] and refs['independent_opus_sample_position'] and not refs['numeric_conformance_claim'],
         'logical integration references are separate from universal numeric conformance')
    position=json.loads(take('capture/sources/reference/position/evidence/oracle/report.json'))
    vendor=json.loads(take('capture/sources/reference/position/evidence/native/report.json'))
    for name,key in [('OPUS20','F20'),('OPUS120','F120')]:
        need(position['fixtures'][key]['comparison']['best_offset']==312 and position['fixtures'][key]['comparison']['best_ties']==1 and
             refs['fixtures'][name]['pcm_bytes']==2112000 and refs['fixtures'][name]['pcm_sha256']==vendor['measurements']['cases'][key]['window_sha256'],
             'exact logical vendor windows have independent full-stream sample positions')
    need(refs['fixtures']['VORBIS']['pcm_sha256']==reader.PCM_SHA and refs['fixtures']['VORBIS']['pcm_bytes']==2112000,
         'original complete Vorbis reference preserved')
    measured=reader.validate_log((take('capture/qemu.stdout.log')+b'\n'+take('capture/qemu.stderr.log')).decode('utf-8'),refs)
    need(measured==report['measurements']==manifest['measurements'],'actual complete task transcript independently recounted')
    witness=json.loads(take('witness/report.json'))
    need(witness['passed'] and witness['original_transcript_accepted'] and witness['rejected_controls']==len(witness['rejected'])==18 and
         not witness['native_campaign_repeated'] and not witness['original_reports_modified'] and witness['reader_sha256']==manifest['controller_sha256'],
         'all actual contradiction controls rejected without altering native evidence')
    need(take('witness/reader.py')==reader_body and take('witness/controller.py')==(ROOT/'tests/check-cyd-ogg-playback-task-reader.py').read_bytes(),
         'actual executed witness-control sources preserved')
    print(json.dumps(dict(passed=True,logical_files=len(files),physical_blobs=len(blobs),
        actual_translation_units=11,actual_compiler_dependencies=421,actual_cases=10,logical_links_in_one_http=3,
        decoder_handles_closed=18,http_clients_closed=16,rejected_witness_controls=18,
        executes_archived_or_native_code=False,omitted_bytes_read=False,physical_hardware_qualified=False,
        full_radio_tls_resource_margins_qualified=False)))


if __name__=='__main__': verify()
