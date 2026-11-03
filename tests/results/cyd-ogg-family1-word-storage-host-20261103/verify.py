"""Verify retained HOST data only; never compile, execute captures or decode PCM."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
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
    need(manifest['HOST_qualified'] and manifest['sanitizers']==['ASan','UBSan'] and
        not any(manifest[key] for key in ('native_word_access_qualified','native_ESP_OOM_qualified','production_task_executed','physical_hardware_qualified','PCM_files_produced')),'bounded HOST scope')
    for key in ('verifier','readme'):
        row=manifest[key];body=(FOLDER/row['path']).read_bytes();need(len(body)==row['bytes'] and sha(body)==row['sha256'],'exact package companion '+key)
    row=manifest['archive'];need(row['path']=='captures.zip','one declared data archive');body=(FOLDER/row['path']).read_bytes()
    need(len(body)==row['bytes'] and sha(body)==row['sha256'],'exact archive bytes')
    files=manifest['files'];need(len(files)==manifest['logical_files']==len({r['path'] for r in files}),'complete logical inventory')
    blobs={}
    with zipfile.ZipFile(FOLDER/row['path']) as archive:
        entries=archive.infolist();need(len(entries)==manifest['physical_blobs']==len({r['blob'] for r in files}) and len(entries)==len({r.filename for r in entries}),'exact deduplicated physical inventory')
        for entry in entries:
            value=archive.read(entry);need(entry.filename=='blobs/'+sha(value),'content-addressed original bytes')
            need(not value.startswith((b'MZ',b'\x7fELF',b'!<arch>\n',b'OggS',b'OFAM101\0')) and b'\0' not in value,'no executable/media/object payload')
            value.decode('utf-8');blobs[entry.filename]=value
    data={}
    for row in files:
        path=PurePosixPath(row['path']);value=blobs[row['blob']]
        need(not path.is_absolute() and '..' not in path.parts and path.as_posix()==row['path'] and len(value)==row['bytes'] and sha(value)==row['sha256'],'contained exact original text record')
        data[row['path']]=value
    omitted=manifest['omitted_local_files']
    for path,row in omitted.items():
        need(path not in data and row['original_retained_locally'] and row['byte_payload_published'] is False and
            row['bytes']>0 and re.fullmatch('[a-f0-9]{64}',row['sha256']) and row['origin'] and row['reason'],'whole local-original omission/provenance')
    def take(path):need(path in data,'required retained original '+path);return data[path]
    def identity(path,pin):
        if path in data:need(len(data[path])==pin['bytes'] and sha(data[path])==pin['sha256'],'retained original identity '+path)
        else:need(path in omitted and all(omitted[path][key]==pin[key] for key in ('bytes','sha256')),'declared whole omitted identity '+path)
    def commands(label,report,failed=False):
        for command in report['commands']:
            need(command['state']=='complete' and command['pid']>0 and not command.get('timed_out') and command['elapsed_seconds']>=0,'authoritative terminal child')
            expected=1 if failed and command['name']=='build-word' else 0
            need(command['exit_status']==expected,'genuine expected terminal status')
            for stream in ('stdout','stderr'):identity(label+'/'+command[stream]['path'],command[stream])
        names=[c['name'] for c in report['commands']]
        need(len(names)==len(set(names)),'unique original command identities')
        required=['compiler-version','compiler-path','compiler-sha','libopus.so.0-link','libopus.so.0-path','libopus.so.0-sha','libogg.so.0-link','libogg.so.0-path','libogg.so.0-sha','build-byte','test-byte','build-word']
        need(names==required+([] if failed else ['test-word','libopus.so.0-post-sha','libogg.so.0-post-sha','compiler-post-sha']),'complete original build/test/tool sequence')
        byname={c['name']:c for c in report['commands']}
        for variant in ('byte','word'):
            command=byname['build-'+variant];argv=command['argv']
            need('/usr/bin/gcc' in argv and '-fsanitize=address,undefined' in argv and '-O2' in argv and '-g' in argv and
                '-fno-omit-frame-pointer' in argv and '-Werror' in argv and not any('-DNDEBUG' in item for item in argv) and
                ('-DDISPATCH_WORD_STORAGE=1' in argv)==(variant=='word') and any(item.endswith('/sources/tests/native/ogg_family1_dispatch_host.c') for item in argv),'actual sanitizer build of the frozen same dispatcher')
            if failed and variant=='word':continue
            need(not take(label+'/build-'+variant+'.stdout.log') and not take(label+'/build-'+variant+'.stderr.log'),'zero successful build diagnostics')
            argv=byname['test-'+variant]['argv']
            need('env' in argv and 'ASAN_OPTIONS=detect_leaks=1:halt_on_error=1' in argv and 'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1' in argv and
                any(item.endswith('/dispatch-'+variant) for item in argv),'real halt-on-error ASan/UBSan invocation')
            need(not take(label+'/test-'+variant+'.stderr.log'),'no runtime sanitizer/assertion diagnostics')
        for tool,field in (('compiler','compiler_identity'),('libopus.so.0','libopus.so.0_identity'),('libogg.so.0','libogg.so.0_identity')):
            need(take(label+'/'+tool+'-sha.stdout.log').decode().strip()==report[field],'original compiler/library identity')
            if not failed:need(take(label+'/'+tool+'-post-sha.stdout.log')==take(label+'/'+tool+'-sha.stdout.log'),'unchanged actual compiler/library')
    def baseline(label,report,variant,extras):
        item=report['variants'][variant];rows=[json.loads(line) for line in take(label+'/test-'+variant+'.stdout.log').decode().splitlines()]
        need(rows==item['test_records'] and all(row['passed'] for row in rows),'whole original runtime records')
        census=Counter(row.get('kind') for row in rows if 'kind' in row)
        need(census['family1']==39 and census['chain']==4 and census['close-control']==3 and census['failure-control']==8 and census['tag-control']==1,'unchanged complete43/12 baseline')
        summaries=[row for row in rows if row.get('suite')=='ogg-family1-dispatch'];need(len(summaries)==1 and summaries[0]==item['measurements'],'one original baseline summary')
        result=summaries[0]
        need(result['positive_schedules']==43 and result['host_controls']==12 and result['creator_pcm_samples_exact']==12983296 and result['family1_output_chunks']==20052 and
            result['legacy_output_chunks']==552 and result['gain_layout_forwarded'] and result['close_retry_preserves_cfg_page_planes'] and
            not result['native_oom_qualified'] and not result['production_task_executed'],'exact unchanged baseline measurements')
        storage=rows[-1];need(storage==item['word_storage_measurements'] and storage['suite']=='ogg-family1-word-storage' and storage['enabled']==(variant=='word') and
            storage['controls']==extras and storage['creator_pcm_samples_exact']==(307192 if extras else 0) and storage['peak_live_planes']==(16 if extras else 0) and
            not storage['native_oom_qualified'] and not storage['native_word_access_qualified'],'separate exact HOST storage summary')
        need(len(rows)==57+extras,'all baseline/extra records retained')
        identity(label+'/'+item['executable']['path'],item['executable']);identity(label+'/'+item['compiler_dependencies']['path'],item['compiler_dependencies'])
        if extras:
            extra=[r for r in rows if r.get('kind')=='word-storage-control'];found={}
            for row in extra:
                need(not row['native_oom_qualified'],'scripted HOST allocation status');found.setdefault(row['name'],[]).append(row['ordinal'])
            required={'initial-refusal':[1,4,8],'byte-upgrade-refusal':[1,4,8],'word-growth-refusal':[1,4,8],
                'unaligned-candidate-refusal':[4],'atomic-replacement-reuse-and-clear':[0],'odd-offset-unaligned-DRAM-alias-silence-gather':[0],
                ('complete-creator-odd-pre-skip-duplicate-silence' if label=='host04' else 'complete-creator-odd-pre-skip'):[313]}
            if extras==19:required['wrapper-allocation-error-and-real-handle-cleanup']=[1,4,8]
            need(found==required,'every distinct allocation/growth/gather/trim/error contract')
            close=[row for row in rows if row.get('kind')=='word-close-control']
            need(len(close)==3 and [row['mode'] for row in close]==[0,1,2] and [row['status'] for row in close]==[0,1,4] and
                [row['close_witness'] for row in close]==[1,1,0] and [row['close_calls'] for row in close]==[6,7,7] and
                all(row['raw_created']==row['raw_destroyed']==5 and row['published_frames']==9600 for row in close),'three complete real-creator close/retention schedules')
    reports={}
    for label,expected in (('host01','NONPASS'),('host02','PASS'),('host03','PASS'),('host04','PASS')):
        report=json.loads(take(label+'/report.json'));reports[label]=report;need(manifest['captures'][label]['status']==expected,'honest historical status')
        identity(label+'/report.json',manifest['captures'][label]['report'])
        need(report['actual_wrapper'] and report['creator_synthesis_real'] and report['scripted_host_status_controls'] and
            not any(report[key] for key in ('native_executed','native_esp_oom_qualified','production_task_executed')),'actual HOST-only wrapper scope')
        failed=label=='host01';commands(label,report,failed)
        for source in report['sources']:identity(label+'/'+source['snapshot'],source)
        for name,pin in report['fixtures'].items():identity(label+'/fixtures/'+name,pin)
        baseline(label,report,'byte',0)
        if failed:
            need(not report['passed'] and not report['completed'] and report['failure']['reason']=='actual terminal zero: build-word' and
                b'invalid initializer' in take(label+'/build-word.stderr.log') and 'test-word' not in [c['name'] for c in report['commands']],'retained original new-harness failure, no word run')
        else:
            need(report['passed'] and report['completed'] and report['all_source_bindings_current'],'genuine historical successful capture')
            baseline(label,report,'word',16 if label=='host02' else 19)
    final=reports['host04'];need(final['word_measurements']['allocation_attempts']==164 and len(final['sources'])==36,'current complete source and allocator census')
    fixture_manifest=json.loads(take('provenance/reference-fixtures-manifest.json'))
    for channels in (3,6,8):
        name='channels'+str(channels)+'.packets';pin=fixture_manifest['reference_fixtures']['channels'+str(channels)]['files'][name]
        need(all(final['fixtures'][name][key]==pin[key] for key in ('bytes','sha256')),'original complete20ms fixture identity')
    need(final['fixtures']['stereo120.packets']['complete_original_packets']==92 and final['fixtures']['stereo120.packets']['source_sha256']=='b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679' and
        final['fixtures']['channels8-120ms.packets']['sha256']=='c6a06d1bf954c9119f844167d43b3f080bdbe4e7c2a305318109e524cf3b6757','unchanged full120ms corpus provenance')
    stress=json.loads(take('host04/sources/stress/report.json'))
    need(stress['passed'] and stress['creator_full_float_exact'] and stress['every_coded_frame_preserved'] and stress['durations']==[5760,4800] and not stress['new_tolerance_applied'] and not stress['native_executed'],'original creator repacketizer provenance')
    expected_current={}
    for row in final['sources']:
        snapshot=row['snapshot'];scope='worktree';relative=None
        if snapshot.startswith(('sources/idf/','sources/tests/')):relative=snapshot.removeprefix('sources/')
        elif snapshot.startswith('sources/vendor/include/'):
            scope='repository';relative='.idf/esp-adf-libs/esp_audio_codec/include/'+snapshot.removeprefix('sources/vendor/include/')
        elif snapshot=='sources/stress/prepare.py':relative='tests/fixtures/opus_family1_120ms/prepare.py'
        if relative is not None:expected_current[(scope,relative)]=(snapshot,row['bytes'],row['sha256'])
    declared_current={(row['scope'],row['relative']):(row['snapshot'],row['bytes'],row['sha256']) for row in manifest['current_sources']}
    need(len(expected_current)==len(declared_current)==len(manifest['current_sources'])==30 and declared_current==expected_current,'complete current-source graph derived from actual final consumed inputs')
    for row in manifest['current_sources']:
        identity('host04/'+row['snapshot'],row)
        if args.require_current:
            relative=PurePosixPath(row['relative']);need(not relative.is_absolute() and '..' not in relative.parts,'contained current source path')
            base=ROOT if row['scope']=='worktree' else REPO;need(row['scope'] in ('worktree','repository'),'declared current source root')
            value=(base/relative).read_bytes();need(len(value)==row['bytes'] and sha(value)==row['sha256'],'current consumed source '+row['relative'])
    required={'idf/esp32-cyd2usb-native/main/opus_family1_playback.h':'2788893b580c1852f9626256e31613271b26eb492710fe6478f85ba200adb9eb',
        'idf/components/native_stream/include/pcm_word_plane.h':'8b3c80edffd3298e2ccd1816fe20aa1cf6cbf30c367aad7035448f35ce868b6b',
        'tests/native/opus_family1_playback_host.c':'4c01663162f714868c70ddb50f04ee1cb8f042669288bd89af2df7581030f2f2'}
    for path,digest in required.items():need(sha(take('host04/sources/'+path))==digest,'exact frozen production/helper/lower-harness contract')
    control=take('host04/sources/tests/native/ogg_family1_word_controls.h')
    need(b'const uint8_t map[8]={0,7,0,7,OF1_SILENCE,5,6,OF1_SILENCE};' in control and b'assert(dispatch_words.calls==4);' in control and
        b'cause==92160' in control,'current full-creator four-plane alias/silence and wrapper refusal assertions')
    print(json.dumps(dict(checkpoint_verified=True,current_sources_required=args.require_current,source_input_bindings=36,current_source_code_bindings=len(manifest['current_sources']),
        baseline_variants=2,positive_schedules_each=43,HOST_controls_each=12,creator_samples_each=12983296,word_extra_controls=19,word_extra_exact_samples=307192,
        native_word_access_qualified=False,native_ESP_OOM_qualified=False,production_task_executed=False,physical_hardware_qualified=False,omitted_payload_bytes_read=False)))

if __name__=='__main__':main()
