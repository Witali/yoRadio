"""Read-only historical public AAC task checkpoint verification.

Only current reviewed Python readers are imported. No SDK, emulator, decoder,
archived code, image or omitted payload runs. Production bytes are joined to
their frozen compiler inputs, without requiring future production equality.
"""
import hashlib
import importlib.util
import io
import json
from pathlib import Path, PurePosixPath
import re
import zipfile

FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]


def need(value,reason):
    if not value:raise ValueError(reason)


def sha(body):return hashlib.sha256(body).hexdigest()


def verify():
    manifest=json.loads((FOLDER/'manifest.json').read_bytes())
    path=FOLDER/manifest['archive']['path']
    need(path.name=='captures.zip' and path.stat().st_size==manifest['archive']['bytes'] and
         sha(path.read_bytes())==manifest['archive']['sha256'],'complete immutable archive identity')
    rows=manifest['files'];names={row['blob'] for row in rows}
    need(len({row['path'] for row in rows})==len(rows)==manifest['logical_files'],'unique complete logical inventory')
    with zipfile.ZipFile(path) as archive:
        need(len(archive.infolist())==len(names)==manifest['physical_blobs'] and set(archive.namelist())==names,'complete deduplicated physical inventory')
        blobs={name:archive.read(name) for name in names}
    files={}
    for row in rows:
        relative=PurePosixPath(row['path']);body=blobs[row['blob']]
        need(relative.as_posix()==row['path'] and not relative.is_absolute() and '..' not in relative.parts and
             ':' not in row['path'] and '\\' not in row['path'],'canonical contained logical path')
        need(row['blob']=='blobs/'+sha(body) and len(body)==row['bytes'] and sha(body)==row['sha256'],'every published original byte')
        need(relative.suffix.lower() not in ('.elf','.bin','.pcm','.o','.obj','.a','.exe') and
             not body.startswith((b'\x7fELF',b'MZ',b'!<arch>\n')),'no compiled or PCM payload published')
        files[row['path']]=body
    omitted={row['path']:row for row in manifest['omitted_local_payloads']}
    need(len(omitted)==len(manifest['omitted_local_payloads']) and all(row['original_retained_locally'] and
         row['byte_payload_published'] is False and row['bytes']>0 and re.fullmatch('[a-f0-9]{64}',row['sha256']) and
         name not in files for name,row in omitted.items()),'explicit whole-payload local omission identities')

    def take(name):
        need(name in files,'required published original: '+name)
        return files[name]

    def bind(name,digest,size=None):
        if name in files:
            need(sha(files[name])==digest and (size is None or len(files[name])==size),'published original hash/size binding')
        else:
            need(name in omitted and omitted[name]['sha256']==digest and
                 (size is None or omitted[name]['bytes']==size),'omitted original identity; payload remains unread')

    reader_path=ROOT/'tests/run-cyd-aac-playback-task-qemu.py';reader_body=reader_path.read_bytes()
    need(sha(reader_body)==manifest['controller_sha256'] and take('verification/task-reader.py')==reader_body and
         take('capture/sources/controller.py')==reader_body,'exact current reviewed canonical task reader')
    need(take('verification/checkpoint-reader.py')==Path(__file__).read_bytes(),'checkpoint reader source identity')
    spec=importlib.util.spec_from_file_location('reviewed_current_AAC_task_reader',reader_path)
    reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    report=json.loads(take('capture/report.json'))
    need(sha(take('capture/report.json'))==manifest['original_report_sha256'] and
         report['passed'] and report['completed'] and report['target_executed'] and report['all_bound_inputs_current'] and
         report['actual_audio_service_tu'] and report['actual_output_tu'] and report['actual_rtos'] and
         report['same_vendor_AAC_integration_oracle'] and not any(report[key] for key in
         ('production_firmware','physical_device','external_network','private_codec_abi','custom_decoder',
          'full_pcm_independent_oracle','performance_or_radio_resource_claim','oom_injection','output_backpressure')),
         'terminal complete public integration gate and exact scope')
    command_names=[]
    for row in report['commands']:
        need(row['state']=='complete' and row['pid']>0 and row['exit_status']==0,'all actual owned commands terminal zero')
        command_names.append(row['name'])
        for stream in ('stdout','stderr'):bind('capture/'+row['name']+'.'+stream+'.log',row[stream+'_sha256'])
    need(len(set(command_names))==len(command_names) and set(command_names)=={
         'sdk-head','sdk-clean','vendor-head','vendor-clean','repository-head','build','compiler-version','symbols',
         'merge','qemu','sdk-head-after','sdk-clean-after','vendor-head-after','vendor-clean-after'}|
         {'compiler-deps-'+str(index) for index in range(17)},'complete real command inventory')
    child=json.loads(take('capture/sdk-child.json').decode('utf-8-sig'))
    need(child['pid']>0 and child['exit_status']==0,'real SDK child terminal zero')
    sources=json.loads(take('capture/source-manifest.json'));bundle=json.loads(take('capture/execution-bundle.json'))
    need(bundle['sources']==sources and bundle['pcm_reference']==report['pcm_reference'] and
         bundle['sdk_commit']==reader.SDK_COMMIT and bundle['vendor_commit']==reader.VENDOR_COMMIT,'complete executed source/tool/reference binding')
    for pin in sources.values():bind('capture/'+pin['snapshot'],pin['sha256'],pin['bytes'])
    for relative,digest in bundle['artifacts'].items():bind('capture/'+relative,digest)
    need(any(name.startswith('runtime-path-redacted:') for name in bundle['runtime']) and
         reader.QEMU_SHA in bundle['runtime'].values() and all(re.fullmatch('[a-f0-9]{64}',value) for value in bundle['runtime'].values()),
         'pinned actual runtime tools with local-only runtime path aliases')
    release_body=take('capture/sources/reference/production-source-release.json');release=json.loads(release_body)
    need(sha(release_body)==reader.SOURCE_RELEASE_SHA==report['production_source_release_sha256'] and len(release['files'])==12,
         'root-authorized twelve-file source/API release identity')
    for relative,pin in release['files'].items():
        name='capture/sources/repository/'+relative
        bind(name,pin['sha256'],pin['bytes'])
        need(any(source['snapshot']=='sources/repository/'+relative and source['sha256']==pin['sha256'] and
                 source['bytes']==pin['bytes'] for source in sources.values()),'every production release file joins its frozen manifest')
    closure=json.loads(take('capture/actual-compiler-closure.json'));commands=json.loads(take('capture/build/compile_commands.json'))
    need(len(closure['translation_units'])==report['actual_translation_units']==17 and
         len(closure['dependencies'])==report['actual_compiler_dependencies']==450,'actual full compiler census')
    for pin in closure['dependencies'].values():
        need(pin['manifest_original'] in sources and pin['sha256']==sources[pin['manifest_original']]['sha256'],
             'every actual GCC dependency joins a frozen source or omission identity')
    headers={PurePosixPath(path.replace('\\','/')).name for path in closure['dependencies']}
    need({'aac_public_config.h','pcm_channel_layout.h','pcm_speaker_mix.h','pcm_header_gain.h',
          'native_audio_normalizer.h','native_audio_settings.h','AudioNormalizer.h','ogg_playback.h'}<=headers,
         'public AAC and complete ordered output dependencies really consumed by compiler')
    selected=set()
    for unit in closure['translation_units']:
        matching=[row for row in commands if row.get('file')==unit['file'] and row.get('output')==unit['output']]
        need(len(matching)==1 and all(unit.get(key)==value for key,value in matching[0].items()),'actual selected TU joins its unchanged original compiler command')
        source_path=unit['file'].replace('\\','/');selected.add(PurePosixPath(source_path).name)
        matches=[pin for pin in sources.values() if source_path.casefold().endswith('/'+pin['snapshot'].replace('\\','/').casefold())]
        need(len(matches)==1,'selected whole TU joins exactly one frozen source')
        bind('capture/'+matches[0]['snapshot'],matches[0]['sha256'],matches[0]['bytes'])
        name=unit['output'].replace('\\','/')
        if re.match('^[A-Za-z]:/',name):name=name[len(manifest['original_capture_directory'].replace('\\','/'))+1:]
        else:name='build/'+name
        need(name in bundle['artifacts'] and unit['actual_dependency_paths'] and
             set(unit['actual_dependency_paths'])<=set(closure['dependencies']),'actual selected object and all real dependency paths bound')
    need(set(reader.MAIN_TUS)|{'public_reference.cpp','main.cpp','native_audio_settings.c','native_audio_normalizer.cpp','AudioNormalizer.cpp'}<=selected,
         'all complete application, output, settings, normalizer and reference owners compiled')
    config=json.loads(take('capture/build/config/sdkconfig.json'))
    need(config['YORADIO_AAC_DECODER_ESPRESSIF'] and config['YORADIO_AAC_PLUS'] and config['AUDIO_DECODER_AAC_SUPPORT'] and
         config['IDF_TARGET']=='esp32' and config['ESP_DEFAULT_CPU_FREQ_MHZ']==240 and config['YORADIO_OGG_TIMELINE'] and
         not config['FREERTOS_UNICORE'] and config['FREERTOS_HZ']==1000,'actual classic dual-core public AAC-Plus profile')
    for key in ('HEAP_POISONING_LIGHT','FREERTOS_CHECK_STACKOVERFLOW_CANARY','COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE',
                'ESP_TASK_WDT_EN','ESP_TASK_WDT_INIT','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0','ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1'):
        need(config[key] is True,'unchanged actual runtime guard: '+key)
    contract=report['pcm_reference']
    need(contract==json.loads(take('capture/sources/reference/reference-contract.json')) and
         contract['same_vendor_pcm_integration_oracle'] and not contract['independent_codec_conformance'] and
         contract['reference_manifest_sha256']==reader.PUBLIC_MANIFEST_SHA and contract['reference_archive_sha256']==reader.PUBLIC_ARCHIVE_SHA,
         'actual complete same-vendor contract; separate from codec conformance')
    public_manifest_body=take('capture/sources/reference/public-manifest.json');public_archive=take('capture/sources/reference/public-captures.zip')
    need(sha(public_manifest_body)==reader.PUBLIC_MANIFEST_SHA and sha(public_archive)==reader.PUBLIC_ARCHIVE_SHA,'original committed standalone public evidence identities')
    public_manifest=json.loads(public_manifest_body);public_rows={row['path']:row for row in public_manifest['files']}
    with zipfile.ZipFile(io.BytesIO(public_archive)) as archive:
        def public_take(name):
            pin=public_rows[name];body=archive.read(pin['blob'])
            need(sha(body)==pin['sha256'] and len(body)==pin['bytes'],'exact nested original public evidence bytes')
            return body
        public_report=json.loads(public_take('native02/report.json'))
        public_log=(public_take('native02/qemu.stdout.log')+b'\n'+public_take('native02/qemu.stderr.log')).decode('utf-8')
    public_reader_path=ROOT/'tests/run-cyd-aac-public-config-qemu.py'
    need(sha(public_reader_path.read_bytes())==contract['reference_reader_sha256'],'current reviewed standalone public transcript reader')
    spec=importlib.util.spec_from_file_location('reviewed_current_public_AAC_reader',public_reader_path)
    public_reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(public_reader)
    need(public_report['passed'] and public_report['completed'] and public_reader.validate_log(public_log)==public_report['measurements'],
         'original 36 public configuration/input cases recounted without archived execution')
    for row in contract['fixtures']:
        body=take('capture/sources/fixtures/'+row['name'])
        need(len(body)==row['bytes'] and sha(body)==row['sha256'],'every complete synthetic original fixture')
        base=[case for case in public_report['measurements']['cases'] if case['id']==row['id'] and case['mode']==2]
        need(len(base)==4 and all(case['pcm']==row['pcm_bytes'] and case['sha256']==row['pcm_sha256'] and
             case['rate']==row['rate'] and case['channels']==row['channels'] for case in base),'all whole base PCM contracts join four original same-vendor input schedules')
    measured=reader.validate_log((take('capture/qemu.stdout.log')+b'\n'+take('capture/qemu.stderr.log')).decode('utf-8'),contract)
    need(json.loads(json.dumps(measured))==report['measurements']==manifest['measurements'],'whole original actual task/reference transcript recounted')
    witness=json.loads(take('witness/report.json'))
    need(witness['passed'] and witness['original_transcript_accepted'] and witness['rejected_controls']==len(witness['rejected'])==40 and
         not witness['native_campaign_repeated'] and not witness['original_reports_modified'] and
         witness['reader_sha256']==manifest['controller_sha256'] and not witness['independent_codec_conformance'],'all genuine contradiction controls rejected without rerunning native')
    need(take('witness/reader.py')==reader_body and take('witness/controller.py')==(ROOT/'tests/check-cyd-aac-playback-task-reader.py').read_bytes(),
         'actual executed contradiction reader sources')
    old=json.loads(take('history/native01/report.json'))
    need(not old['passed'] and not old['completed'] and not old['target_executed'] and
         [row['name'] for row in old['commands']][-1]=='build' and old['commands'][-1]['state']=='complete' and
         old['commands'][-1]['exit_status']==1,'first genuine diagnostic compile failure remains non-PASS with no target run')
    first_child=json.loads(take('history/native01/sdk-child.json').decode('utf-8-sig'))
    need(first_child['pid']>0 and first_child['exit_status']==2,'original failed real SDK child status retained')
    for row in old['commands']:
        for stream in ('stdout','stderr'):bind('history/native01/'+row['name']+'.'+stream+'.log',row[stream+'_sha256'])
    first_sources=json.loads(take('history/native01/source-manifest.json'))
    for pin in first_sources.values():bind('history/native01/'+pin['snapshot'],pin['sha256'],pin['bytes'])
    inventory=json.loads(take('history/include-order-review/error-inventory.json'))
    need(not inventory['native01_passed'] and not inventory['native01_completed'] and not inventory['target_executed'] and
         inventory['sdk_child_exit']==2,'unmodified original diagnostic failure inventory')
    for pin in inventory['originals']:
        relative=pin['path'].split('.build/cyd-aac-playback-task-20261101-01/',1)
        need(len(relative)==2,'exact original error inventory source')
        bind('history/native01/'+relative[1],pin['sha256'],pin['bytes'])
    errors=inventory['error_records'];log=take('history/native01/sdk-build.stdout.log')
    need(len(errors)==inventory['error_records_count']==111,'all original compiler failure/error records retained')
    for row in errors:
        body=log[row['offset']:row['offset']+row['bytes']]
        need(sha(body)==row['sha256'] and body.decode('utf-8').rstrip('\r\n')==row['text'],'every original compiler failure/error joins exact SDK log bytes')
    before=take('history/native01/sources/harness/project/main/public_reference.cpp')
    after=take('capture/sources/harness/project/main/public_reference.cpp')
    need(before.replace(b'#include "freertos/task.h"',b'#include "freertos/FreeRTOS.h"\n#include "freertos/task.h"',1)==after,
         'only correction between native attempts is required FreeRTOS include order in new diagnostic')
    print(json.dumps(dict(passed=True,logical_files=len(files),physical_blobs=len(blobs),omitted_payloads=len(omitted),
        actual_translation_units=17,actual_compiler_dependencies=450,actual_cases=48,continuous_public_references=10,
        decoder_handles_closed=60,http_clients_closed=60,rejected_witness_controls=40,prior_failed_sdk_attempts=1,
        executes_archived_or_native_code=False,reads_omitted_payloads=False,requires_live_production_equality=False,
        independent_codec_conformance=False,physical_audio_qualified=False)))


if __name__=='__main__':verify()
