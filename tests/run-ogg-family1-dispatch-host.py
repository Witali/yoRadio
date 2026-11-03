"""Qualify current Ogg dispatcher, stable raw cleanup and legacy transitions using real creator synthesis."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent.parent if ROOT.parent.name=='.worktree' else ROOT
VENDOR=REPO/'.idf/esp-adf-libs/esp_audio_codec'
PUBLIC='idf/components/native_vorbis_xiph/upstream/libogg'
CONFIG='idf/components/native_vorbis_xiph/platform'
SOURCES=['idf/esp32-cyd2usb-native/main/'+n for n in ('ogg_playback.h','opus_family1_playback.h','opus_family1_decoder.h')]
SOURCES+=['idf/components/native_stream/include/'+n for n in ('ogg_opus_audio_packets.h','ogg_page_input.h','ogg_opus_timeline.h','opus_pcm_trim.h','opus_family1_mapping.h','opus_multistream_framing.h','opus_tags_stream.h','decoder_pending_input.h','pcm_channel_layout.h','pcm_word_plane.h')]
SOURCES+=['tests/native/ogg_family1_dispatch_host.c','tests/native/ogg_family1_word_allocator.h','tests/native/ogg_family1_word_controls.h','tests/native/opus_family1_playback_host.c','tests/native/opus_family1_public.h','tests/fixtures/opus_header_gain/generate.py','tests/run-ogg-family1-dispatch-host.py',PUBLIC+'/include/ogg/ogg.h',PUBLIC+'/include/ogg/os_types.h',PUBLIC+'/COPYING',CONFIG+'/ogg/config_types.h']
LONG=ROOT/'tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg'
LONG_SHA='b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679'
STRESS=ROOT/'.build/opus-family1-120ms-probe-20261101-01/results/channels8-120ms.packets'
STRESS_SHA='c6a06d1bf954c9119f844167d43b3f080bdbe4e7c2a305318109e524cf3b6757'
def need(value,why):
    if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path):return dict(bytes=Path(path).stat().st_size,sha256=sha(path))
def host(path):
    value=Path(path).resolve().as_posix();return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--reference',required=True,type=Path);args=parser.parse_args();out=args.output.resolve();reference=args.reference.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists() and reference.is_relative_to(ROOT/'.build'),'fresh ignored capture');need(sha(LONG)==LONG_SHA and sha(STRESS)==STRESS_SHA,'complete original stereo120 and actual creator-repacketized active C8 stress')
    originals=json.loads((ROOT/'tests/results/cyd-opus-family1-20261101/manifest.json').read_bytes())['reference_fixtures'];out.mkdir(parents=True)
    report=dict(passed=False,completed=False,commands=[],sources=[],fixtures={},actual_wrapper=True,creator_synthesis_real=True,scripted_host_status_controls=True,native_executed=False,native_esp_oom_qualified=False,production_task_executed=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(path,relative):
        destination=out/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(Path(path).read_bytes());report['sources'].append(dict(path=str(Path(path).resolve()),snapshot=relative.as_posix(),**pin(path)))
    def command(name,argv):
        full=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+list(map(str,argv));row=dict(name=name,argv=full,state='starting',timeout_seconds=180);report['commands'].append(row);save();started=time.monotonic()
        with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
            child=subprocess.Popen(full,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);row.update(pid=child.pid,state='running');save()
            try:status=child.wait(timeout=180)
            except subprocess.TimeoutExpired:child.kill();status=child.wait();row['timed_out']=True
            row.update(state='complete',exit_status=status,elapsed_seconds=round(time.monotonic()-started,3))
        for stream in ('stdout','stderr'):
            path=out/(name+'.'+stream+'.log');row[stream]=dict(path=path.name,**pin(path))
        save();need(status==0 and not row.get('timed_out'),'actual terminal zero: '+name);return (out/(name+'.stdout.log')).read_bytes()
    save()
    try:
        for name in SOURCES:freeze(ROOT/name,Path('sources')/name)
        for name in ('esp_audio_types.h','decoder/esp_audio_dec.h','decoder/esp_audio_dec_reg.h','decoder/impl/esp_opus_dec.h','simple_dec/esp_audio_simple_dec.h'):freeze(VENDOR/'include'/name,Path('sources/vendor/include')/name)
        paths=[]
        for c in (3,6,8):
            name='channels'+str(c)+'.packets';path=reference/name;expected=originals['channels'+str(c)]['files'][name];need(pin(path)=={k:expected[k] for k in ('bytes','sha256')},'complete original20ms multistream packet bodies')
            freeze(path,Path('fixtures')/name);paths.append(out/'fixtures'/name);report['fixtures'][name]=pin(path)
        freeze(LONG,Path('sources/fixtures/stereo-510-120ms.ogg'));reader_path=out/'sources/tests/fixtures/opus_header_gain/generate.py';spec=importlib.util.spec_from_file_location('dispatch_complete_ogg_reader',reader_path);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
        body=LONG.read_bytes();pages,packets=reader.parse(body);audio=packets[2:];need(len(audio)==92,'all original stereo120ms packets');pre=int.from_bytes(packets[0][10:12],'little');logical=int.from_bytes(body[pages[-1]['offset']+6:pages[-1]['offset']+14],'little')-pre
        transport=struct.pack('<8s6I8s',b'OFAM101\0',2,1,1,pre,logical,len(audio),bytes((0,1,0,0,0,0,0,0)))+b''.join(struct.pack('<I',len(p))+p for p in audio)
        path=out/'fixtures/stereo120.packets';path.write_bytes(transport);paths.append(path);report['fixtures'][path.name]=dict(**pin(path),complete_original_packets=92,source_sha256=LONG_SHA)
        stress_report=STRESS.parent/'report.json';stress=json.loads(stress_report.read_bytes());need(stress['passed'] and stress['creator_full_float_exact'] and stress['every_coded_frame_preserved'] and stress['durations']==[5760,4800],'real creator public repacketizer proof')
        freeze(STRESS,Path('fixtures/channels8-120ms.packets'));paths.append(out/'fixtures/channels8-120ms.packets');report['fixtures'][paths[-1].name]=pin(STRESS);freeze(stress_report,Path('sources/stress/report.json'));freeze(ROOT/'tests/fixtures/opus_family1_120ms/prepare.py',Path('sources/stress/prepare.py'))
        report['compiler_version']=command('compiler-version',['/usr/bin/gcc','--version']).decode().splitlines()[0];compiler=command('compiler-path',['readlink','-f','/usr/bin/gcc']).decode().strip();report['compiler_identity']=command('compiler-sha',['sha256sum',compiler]).decode().strip();libraries=[]
        for name in ('libopus.so.0','libogg.so.0'):
            library=command(name+'-link',['/usr/bin/gcc','-print-file-name='+name]).decode().strip();need(library.startswith('/usr/') and '\n' not in library,'installed creator library');library=command(name+'-path',['readlink','-f',library]).decode().strip();identity=command(name+'-sha',['sha256sum',library]).decode().strip();libraries.append((name,library,identity));report[name+'_identity']=identity
        report['variants']={}
        stress_logical=struct.unpack_from('<I',STRESS.read_bytes(),24)[0]
        for variant,word_enabled in (('byte',False),('word',True)):
            binary=out/('dispatch-'+variant);dependency=out/('dispatch-'+variant+'.d')
            command('build-'+variant,['/usr/bin/gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-Wpedantic','-Wformat=2','-Wshadow','-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie','-MMD','-MF',host(dependency),
                *(['-DDISPATCH_WORD_STORAGE=1'] if word_enabled else []),
                *['-I'+host(out/'sources/vendor/include'/name) for name in ('','decoder','decoder/impl','simple_dec')],'-I'+host(out/'sources/idf/esp32-cyd2usb-native/main'),'-I'+host(out/'sources/idf/components/native_stream/include'),
                '-I'+host(out/'sources'/PUBLIC/'include'),'-I'+host(out/'sources'/CONFIG),host(out/'sources/tests/native/ogg_family1_dispatch_host.c'),'-l:libopus.so.0','-l:libogg.so.0','-lm','-o',host(binary)])
            item=dict(executable=dict(path=binary.name,local_only=True,**pin(binary)),compiler_dependencies=dict(path=dependency.name,**pin(dependency)))
            report['variants'][variant]=item;save()
            rows=[json.loads(line) for line in command('test-'+variant,['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',host(binary),*[host(p) for p in paths]]).decode().splitlines()]
            summaries=[row for row in rows if row.get('suite')=='ogg-family1-dispatch'];need(len(summaries)==1,'one complete baseline inventory');result=summaries[0]
            need(all(r['passed'] for r in rows) and result['positive_schedules']==43 and result['host_controls']==12 and result['creator_pcm_samples_exact']==12983296 and
                result['gain_layout_forwarded'] and result['close_retry_preserves_cfg_page_planes'] and not result['native_oom_qualified'] and not result['production_task_executed'],'unchanged complete creator-backed43/12 corpus in '+variant)
            word=rows[-1];need(word['suite']=='ogg-family1-word-storage' and word['enabled']==int(word_enabled) and word['controls']==(19 if word_enabled else 0) and
                word['creator_pcm_samples_exact']==((4*stress_logical-1)*8 if word_enabled else 0) and word['peak_live_planes']==(16 if word_enabled else 0) and
                (word['allocation_attempts']>0)==word_enabled and not word['native_oom_qualified'] and not word['native_word_access_qualified'],'separate tracked HOST word-storage coverage')
            need(len(rows)==(76 if word_enabled else 57),'every baseline and extra control record retained')
            item.update(test_records=rows,measurements=result,word_storage_measurements=word);save()
        report['executable']=report['variants']['byte']['executable'];report['compiler_dependencies']=report['variants']['byte']['compiler_dependencies']
        report['test_records']=report['variants']['byte']['test_records'];report['measurements']=report['variants']['byte']['measurements'];report['word_measurements']=report['variants']['word']['word_storage_measurements'];result=report['measurements']
        for name,library,identity in libraries:need(command(name+'-post-sha',['sha256sum',library]).decode().strip()==identity,'unchanged creator library')
        need(command('compiler-post-sha',['sha256sum',compiler]).decode().strip()==report['compiler_identity'],'unchanged compiler')
        for row in report['sources']:need(pin(row['path'])==pin(out/row['snapshot'])=={k:row[k] for k in ('bytes','sha256')},'all initial/final actual source bytes unchanged')
        report.update(passed=True,completed=True,all_source_bindings_current=True);print(json.dumps(dict(passed=True,capture=out.relative_to(ROOT).as_posix(),measurements=result)));return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));print(json.dumps(dict(passed=False,failure=report['failure'])));return 1
    finally:save()
if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
