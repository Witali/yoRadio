"""Authenticate saved fallback HOST evidence only; never execute capture code."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path,PurePosixPath
import re
import zipfile

FOLDER=Path(__file__).resolve().parent
ROOT=FOLDER.parents[2]
REPO=ROOT.parent.parent if ROOT.parent.name=='.worktree' else ROOT

def need(value,reason):
    if not value:raise ValueError(reason)

def sha(body):return hashlib.sha256(body).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--require-current',action='store_true');args=parser.parse_args()
    manifest=json.loads((FOLDER/'manifest.json').read_bytes())
    need(manifest['HOST_qualified'] and manifest['sanitizers']==['ASan','UBSan'] and not any(manifest[key] for key in
        ('native_word_access_qualified','native_ESP_OOM_qualified','production_task_executed','physical_hardware_qualified','PCM_files_produced')),'bounded HOST qualification')
    need(not any(manifest[key] for key in ('originals_rewritten','scanner_semantic_override','archived_code_executed')) and
        manifest['capture']['status']=='PASS' and manifest['predecessor']['selected_records_only'] and not manifest['predecessor']['rerun'] and
        not manifest['predecessor']['modified'],'unchanged originals and historical selected predecessor scope')
    for key in ('verifier','readme'):
        row=manifest[key];body=(FOLDER/row['path']).read_bytes();need(len(body)==row['bytes'] and sha(body)==row['sha256'],'exact package companion')
    row=manifest['archive'];need(row['path']=='captures.zip','declared data archive');body=(FOLDER/row['path']).read_bytes()
    need(len(body)==row['bytes'] and sha(body)==row['sha256'],'exact archive bytes')
    files=manifest['files'];need(len(files)==manifest['logical_files']==len({r['path'] for r in files}),'complete logical inventory')
    blobs={}
    with zipfile.ZipFile(FOLDER/row['path']) as archive:
        entries=archive.infolist();need(len(entries)==manifest['physical_blobs']==len({r['blob'] for r in files}) and len(entries)==len({r.filename for r in entries}),'complete deduplicated physical inventory')
        for entry in entries:
            value=archive.read(entry);need(entry.filename=='blobs/'+sha(value),'content-addressed unchanged original')
            need(not value.startswith((b'MZ',b'\x7fELF',b'!<arch>\n',b'OggS',b'OFAM101\0')) and b'\0' not in value,'no executable/object/media payload')
            value.decode('utf-8');blobs[entry.filename]=value
    data={}
    for row in files:
        path=PurePosixPath(row['path']);value=blobs[row['blob']]
        need(not path.is_absolute() and '..' not in path.parts and path.as_posix()==row['path'] and len(value)==row['bytes'] and sha(value)==row['sha256'],'contained exact text record')
        data[row['path']]=value
    omitted=manifest['omitted_local_files']
    need(omitted and all(path not in data and row['original_retained_locally'] and row['byte_payload_published'] is False and row['bytes']>0 and
        re.fullmatch('[a-f0-9]{64}',row['sha256']) and row['origin'] and row['reason'] for path,row in omitted.items()),'whole-local-original omission provenance')
    def take(path):need(path in data,'required original '+path);return data[path]
    def identity(path,pin):
        if path in data:need(len(data[path])==pin['bytes'] and sha(data[path])==pin['sha256'],'exact retained identity '+path)
        else:need(path in omitted and all(omitted[path][key]==pin[key] for key in ('bytes','sha256')),'exact whole-omitted identity '+path)
    report=json.loads(take('fallback01/report.json'));identity('fallback01/report.json',manifest['capture']['report'])
    need(report['passed'] and report['completed'] and report['all_source_bindings_current'] and report['actual_wrapper'] and report['creator_synthesis_real'] and
        report['scripted_host_status_controls'] and not any(report[key] for key in ('native_executed','native_esp_oom_qualified','production_task_executed')),'genuine successful HOST-only capture')
    expected_commands=['compiler-version','compiler-path','compiler-sha','libopus.so.0-link','libopus.so.0-path','libopus.so.0-sha','libogg.so.0-link','libogg.so.0-path','libogg.so.0-sha',
        'build-byte','test-byte','build-word','test-word','libopus.so.0-post-sha','libogg.so.0-post-sha','compiler-post-sha']
    need([row['name'] for row in report['commands']]==expected_commands,'complete actual tool/build/test sequence')
    commands={row['name']:row for row in report['commands']}
    for row in report['commands']:
        need(row['state']=='complete' and row['pid']>0 and row['exit_status']==0 and not row.get('timed_out') and row['elapsed_seconds']>=0,'authoritative terminal zero')
        for stream in ('stdout','stderr'):identity('fallback01/'+row[stream]['path'],row[stream])
    for tool,field in (('compiler','compiler_identity'),('libopus.so.0','libopus.so.0_identity'),('libogg.so.0','libogg.so.0_identity')):
        before=take('fallback01/'+tool+'-sha.stdout.log');need(before.decode().strip()==report[field] and before==take('fallback01/'+tool+'-post-sha.stdout.log'),'unchanged actual compiler/creator library')
    records={}
    for variant in ('byte','word'):
        build=commands['build-'+variant]['argv'];run=commands['test-'+variant]['argv']
        need('/usr/bin/gcc' in build and '-fsanitize=address,undefined' in build and '-O2' in build and '-g' in build and '-Werror' in build and '-fno-omit-frame-pointer' in build and
            not any('-DNDEBUG' in arg for arg in build) and ('-DDISPATCH_WORD_STORAGE=1' in build)==(variant=='word') and
            any(arg.endswith('/sources/tests/native/ogg_family1_dispatch_host.c') for arg in build),'actual assertion-enabled sanitizer build of the frozen dispatcher')
        need('env' in run and 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1' in run and 'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1' in run and
            any(arg.endswith('/dispatch-'+variant) for arg in run),'actual halt-on-error sanitizer execution')
        need(not take('fallback01/build-'+variant+'.stderr.log') and not take('fallback01/build-'+variant+'.stdout.log') and not take('fallback01/test-'+variant+'.stderr.log'),'no compiler/sanitizer/assertion diagnostics')
        rows=[json.loads(line) for line in take('fallback01/test-'+variant+'.stdout.log').decode().splitlines()];item=report['variants'][variant];records[variant]=rows
        need(rows==item['test_records'] and all(row['passed'] for row in rows),'whole original successful runtime records')
        census=Counter(row.get('kind') for row in rows if 'kind' in row)
        need(census['family1']==39 and census['chain']==4 and census['close-control']==3 and census['failure-control']==8 and census['tag-control']==1,'same complete43/12 baseline')
        baseline=[row for row in rows if row.get('suite')=='ogg-family1-dispatch'];need(len(baseline)==1 and baseline[0]==item['measurements'],'one complete original baseline summary')
        result=baseline[0]
        need(result['positive_schedules']==43 and result['host_controls']==12 and result['creator_pcm_samples_exact']==12983296 and result['family1_output_chunks']==20052 and
            result['legacy_output_chunks']==552 and result['gain_layout_forwarded'] and result['close_retry_preserves_cfg_page_planes'] and
            not result['native_oom_qualified'] and not result['production_task_executed'],'unchanged exact baseline scope/counts')
        storage=rows[-1];enabled=variant=='word'
        need(storage==item['word_storage_measurements'] and storage['suite']=='ogg-family1-word-storage' and storage['enabled']==enabled and
            storage['controls']==(23 if enabled else 0) and storage['creator_pcm_samples_exact']==(383992 if enabled else 0) and storage['peak_live_planes']==(16 if enabled else 0) and
            storage['allocation_attempts']==(186 if enabled else 0) and not storage['native_oom_qualified'] and not storage['native_word_access_qualified'] and len(rows)==(80 if enabled else 57),'separate complete storage/fallback census')
        identity('fallback01/'+item['executable']['path'],item['executable']);identity('fallback01/'+item['compiler_dependencies']['path'],item['compiler_dependencies'])
        fatal=[row for row in rows if row.get('kind')=='failure-control' and row['mode']==4]
        need(len(fatal)==1 and fatal[0]['status']==fatal[0]['expected']==2 and fatal[0]['cause']==15360 and fatal[0]['published_frames']==0,'unchanged fatal allocation result after explicit backend exhaustion')
    need(report['variants']['byte']['measurements']==report['variants']['word']['measurements'],'identical baseline summaries')
    extra=[row for row in records['word'] if row.get('kind','').startswith('word-')]
    need(len(extra)==23 and extra[-4:]==[
        dict(kind='word-storage-control',name='complete-creator-small-byte-refusal-fallback',ordinal=960,passed=True,native_oom_qualified=False),
        *[dict(kind='word-storage-control',name='small-byte-and-word-growth-refusal',ordinal=ordinal,passed=True,native_oom_qualified=False) for ordinal in (1,4,8)]],'new complete-creator fallback and all three old-byte retention outcomes')
    old_body=take('predecessor/manifest.json');identity('predecessor/manifest.json',manifest['predecessor']['manifest']);need(sha(old_body)=='675068ed8ab5be57c3fefaa62fc678eab949b151fd2ff8a24f8132fbf82fdb64','exact already-published predecessor manifest')
    old=json.loads(old_body);need(old['archive']==dict(path='captures.zip',bytes=250910,sha256='4abaf00af8a181533f0bb046a3b93e8c0f9905442fc4e933483a9b2447b260f1'),'recorded predecessor archive identity, not a replay')
    need(manifest['predecessor']['archive']==old['archive'],'same declared historical predecessor archive')
    for name in ('report.json','test-word.stdout.log'):
        original='host04/'+name;rows=[row for row in old['files'] if row['path']==original];need(len(rows)==1,'one selected published predecessor record')
        identity('predecessor/host04/'+name,rows[0])
    previous=json.loads(take('predecessor/host04/report.json'));previous_rows=[json.loads(line) for line in take('predecessor/host04/test-word.stdout.log').decode().splitlines()]
    need(previous['passed'] and previous['completed'] and previous_rows==previous['variants']['word']['test_records'] and all(row['passed'] for row in previous_rows),'authentic successful historical predecessor records')
    prior=[row for row in previous_rows if row.get('kind','').startswith('word-')]
    need(len(prior)==19 and extra[:19]==prior and previous['word_measurements']['controls']==19 and previous['word_measurements']['creator_pcm_samples_exact']==307192 and
        report['word_measurements']['creator_pcm_samples_exact']-previous['word_measurements']['creator_pcm_samples_exact']==76800,'all previous19 event contracts retained exactly, plus complete9600-frame C8 creator comparison')
    for row in report['sources']:identity('fallback01/'+row['snapshot'],row)
    for name,pin in report['fixtures'].items():identity('fallback01/fixtures/'+name,pin)
    need(len(report['sources'])==36,'all exact consumed source/input bindings')
    fixture_manifest=json.loads(take('provenance/reference-fixtures-manifest.json'))
    for channels in (3,6,8):
        name='channels'+str(channels)+'.packets';pin=fixture_manifest['reference_fixtures']['channels'+str(channels)]['files'][name]
        need(all(report['fixtures'][name][key]==pin[key] for key in ('bytes','sha256')),'complete original20ms corpus identity')
    need(report['fixtures']['stereo120.packets']['complete_original_packets']==92 and report['fixtures']['stereo120.packets']['source_sha256']=='b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679' and
        report['fixtures']['channels8-120ms.packets']['sha256']=='c6a06d1bf954c9119f844167d43b3f080bdbe4e7c2a305318109e524cf3b6757','unchanged complete120ms corpus provenance')
    stress=json.loads(take('fallback01/sources/stress/report.json'));need(stress['passed'] and stress['creator_full_float_exact'] and stress['every_coded_frame_preserved'] and stress['durations']==[5760,4800] and not stress['new_tolerance_applied'] and not stress['native_executed'],'original creator repacketizer proof')
    expected={}
    for row in report['sources']:
        snapshot=row['snapshot'];relative=None;scope='worktree'
        if snapshot.startswith(('sources/idf/','sources/tests/')):relative=snapshot.removeprefix('sources/')
        elif snapshot.startswith('sources/vendor/include/'):
            scope='repository';relative='.idf/esp-adf-libs/esp_audio_codec/include/'+snapshot.removeprefix('sources/vendor/include/')
        elif snapshot=='sources/stress/prepare.py':relative='tests/fixtures/opus_family1_120ms/prepare.py'
        if relative is not None:expected[(scope,relative)]=(snapshot,row['bytes'],row['sha256'])
    declared={(row['scope'],row['relative']):(row['snapshot'],row['bytes'],row['sha256']) for row in manifest['current_sources']}
    need(len(expected)==len(declared)==len(manifest['current_sources'])==30 and expected==declared,'complete current source graph derived from actual inputs')
    for row in manifest['current_sources']:
        if args.require_current:
            relative=PurePosixPath(row['relative']);need(not relative.is_absolute() and '..' not in relative.parts and row['scope'] in ('worktree','repository'),'contained current source root/path')
            value=((ROOT if row['scope']=='worktree' else REPO)/relative).read_bytes();need(len(value)==row['bytes'] and sha(value)==row['sha256'],'current consumed source '+row['relative'])
    frozen={'idf/esp32-cyd2usb-native/main/opus_family1_playback.h':'fc69e41e960db72bf11c941a13f1c4d3ea2d618c239fac22e334e2a8e2804e27',
        'idf/components/native_stream/include/pcm_word_plane.h':'8b3c80edffd3298e2ccd1816fe20aa1cf6cbf30c367aad7035448f35ce868b6b',
        'tests/native/opus_family1_playback_host.c':'4c01663162f714868c70ddb50f04ee1cb8f042669288bd89af2df7581030f2f2'}
    for path,digest in frozen.items():need(sha(take('fallback01/sources/'+path))==digest,'exact frozen fallback/helper/lower-harness source')
    dispatcher=take('fallback01/sources/tests/native/ogg_family1_dispatch_host.c');control=take('fallback01/sources/tests/native/ogg_family1_word_controls.h')
    need(b'plane_alloc.refuse=1;expected=OGP_MEMORY;' in dispatcher and b'dispatch_words.refuse=1;' in dispatcher and b'if(mode==4)assert(dispatch_words.calls==1 && dispatch_word_empty());' in dispatcher,'explicit dual-backend exhaustion in the word-enabled fatal baseline')
    need(b'.fallback_word_planes=8,.fallback_word_capacity=1920' in control and b'c.fallback_word_witnesses==c.outputs' in control and
        b'f->word_mode && !f->planes && f->plane_count==c->fallback_word_planes && f->word_capacity==c->fallback_word_capacity' in dispatcher and
        b'dispatch_words.live==c->fallback_word_planes && plane_alloc.calls==1 && plane_alloc.refuse==1 && !plane_alloc.pointer' in dispatcher and
        b'++c->fallback_word_witnesses;' in dispatcher,'assertion-enabled8x1920 word-storage witness on every actual creator output callback')
    need(b's.capacity==7680' in control and b'plane_alloc.refuse=byte_calls+1u;dispatch_words.refuse=ordinal;' in control and
        b'!word_stage(&s,960)' in control and b'dispatch_snapshot_equal(&s,&previous);' in control and
        b'assert(s.planes[byte]==(uint8_t)(byte*59u+17u))' in control,'exact old-byte pointer/capacity/content preservation under failed small growth')
    print(json.dumps(dict(checkpoint_verified=True,current_sources_required=args.require_current,source_input_bindings=36,current_source_code_bindings=30,baseline_variants=2,
        positive_schedules_each=43,HOST_controls_each=12,creator_samples_each=12983296,word_extra_controls=23,word_extra_exact_samples=383992,word_allocation_attempts=186,
        predecessor_event_records_equal=19,native_word_access_qualified=False,native_ESP_OOM_qualified=False,production_task_executed=False,physical_hardware_qualified=False,omitted_payload_bytes_read=False)))

if __name__=='__main__':main()
