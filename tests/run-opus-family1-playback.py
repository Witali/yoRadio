"""Qualify the unselected family1 adapter through actual held pages and public creator APIs."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys
import time
import zipfile
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent.parent if ROOT.parent.name=='.worktree' else ROOT
VENDOR=REPO/'.idf/esp-adf-libs/esp_audio_codec'
PUBLIC='idf/components/native_vorbis_xiph/upstream/libogg'
CONFIG='idf/components/native_vorbis_xiph/platform'
SOURCES=['idf/esp32-cyd2usb-native/main/'+n for n in ('opus_family1_playback.h','opus_family1_decoder.h')]
SOURCES+=['idf/components/native_stream/include/'+n for n in ('ogg_opus_audio_packets.h','ogg_page_input.h','ogg_opus_timeline.h','opus_pcm_trim.h','opus_family1_mapping.h','opus_multistream_framing.h','opus_tags_stream.h')]
SOURCES+=['tests/native/opus_family1_playback_host.c','tests/native/opus_family1_playback_size.c','tests/native/opus_family1_public.h','tests/fixtures/opus_header_gain/generate.py','tests/run-opus-family1-playback.py',PUBLIC+'/include/ogg/ogg.h',PUBLIC+'/include/ogg/os_types.h',PUBLIC+'/COPYING',CONFIG+'/ogg/config_types.h']
LONG=ROOT/'tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg'
LONG_SHA='b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679'
def need(value,why):
    if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path):return dict(bytes=Path(path).stat().st_size,sha256=sha(path))
def host(path):
    value=Path(path).resolve().as_posix();return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--reference',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();reference=args.reference.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists() and reference.is_relative_to(ROOT/'.build'),'fresh ignored capture')
    need(sha(LONG)==LONG_SHA,'exact complete original120ms fixture');evidence=json.loads((ROOT/'tests/results/cyd-opus-family1-20261101/manifest.json').read_bytes())['reference_fixtures']
    gain=json.loads((ROOT/'tests/results/cyd-opus-header-gain-20261101/manifest.json').read_bytes())
    need(sha(ROOT/'tests/fixtures/opus_header_gain/generate.py')==gain['canonical_source_sha256']['tests/fixtures/opus_header_gain/generate.py'],'pinned data-only complete Ogg packet reader')
    out.mkdir(parents=True);report=dict(passed=False,completed=False,commands=[],sources=[],fixtures={},native_executed=False,production_selected=False,
        host_public_api_test_double=True,creator_synthesis_real=True,creator_libogg_crc_and_packet_walk=True,scripted_host_status_controls=True,
        owner_allocator_host_seam=True,native_esp_oom_qualified=False)
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
        for name in ('include/decoder/impl/esp_opus_dec.h','include/decoder/esp_audio_dec_reg.h','include/decoder/esp_audio_dec.h','include/esp_audio_types.h'):
            freeze(VENDOR/name,Path('sources/vendor')/name)
        checkpoint=ROOT/'tests/results/cyd-opus-family1-playback-20261101';old=json.loads((checkpoint/'manifest.json').read_bytes());archive=checkpoint/old['archive']['path']
        need(pin(archive)=={k:old['archive'][k] for k in ('bytes','sha256')},'immutable prior adapter checkpoint archive');old_sha=old['canonical_source_sha256']['idf/esp32-cyd2usb-native/main/opus_family1_playback.h']
        with zipfile.ZipFile(archive) as z:before=z.read('blobs/'+old_sha)
        need(hashlib.sha256(before).hexdigest()==old_sha,'prior public adapter source identity, layout-only compilation')
        before_header=out/'layout-before/opus_family1_playback.h';before_header.parent.mkdir();before_header.write_bytes(before)
        report['layout_reference']=dict(snapshot='layout-before/opus_family1_playback.h',**pin(before_header),checkpoint_manifest_sha256=sha(checkpoint/'manifest.json'),checkpoint_archive_sha256=sha(archive))
        paths=[]
        for c in (3,6,8):
            name='channels'+str(c)+'.packets';path=reference/name;expected=evidence['channels'+str(c)]['files'][name]
            need(pin(path)=={k:expected[k] for k in ('bytes','sha256')},'complete original20ms multistream packet bodies');freeze(path,Path('fixtures')/name);paths.append(out/'fixtures'/name);report['fixtures'][name]=pin(path)
        freeze(LONG,Path('sources/fixtures/stereo-510-120ms.ogg'));reader_path=out/'sources/tests/fixtures/opus_header_gain/generate.py'
        spec=importlib.util.spec_from_file_location('reviewed_original_ogg_reader',reader_path);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
        body=LONG.read_bytes();pages,packets=reader.parse(body);audio=packets[2:];need(len(audio)==92 and packets[0][9]==2,'all92 original full120ms audio packets')
        pre_skip=int.from_bytes(packets[0][10:12],'little');logical=int.from_bytes(body[pages[-1]['offset']+6:pages[-1]['offset']+14],'little')-pre_skip
        transport=struct.pack('<8s6I8s',b'OFAM101\0',2,1,1,pre_skip,logical,len(audio),bytes([0,1,0,0,0,0,0,0]))
        transport+=b''.join(struct.pack('<I',len(p))+p for p in audio);path=out/'fixtures/stereo120.packets';path.write_bytes(transport);paths.append(path)
        report['fixtures'][path.name]=dict(**pin(path),complete_original_packets=len(audio),coded_bodies_unchanged=True,source_sha256=LONG_SHA,pre_skip=pre_skip,logical_frames=logical)
        report['compiler_version']=command('compiler-version',['/usr/bin/gcc','--version']).decode().splitlines()[0];compiler=command('compiler-path',['readlink','-f','/usr/bin/gcc']).decode().strip()
        report['compiler_identity']=command('compiler-sha',['sha256sum',compiler]).decode().strip()
        libraries=[]
        for name in ('libopus.so.0','libogg.so.0'):
            library=command(name+'-link',['/usr/bin/gcc','-print-file-name='+name]).decode().strip();need(library.startswith('/usr/') and '\n' not in library,'installed creator library')
            library=command(name+'-path',['readlink','-f',library]).decode().strip();identity=command(name+'-sha',['sha256sum',library]).decode().strip();report[name+'_identity']=identity;libraries.append((name,library,identity))
        binary=out/'playback'
        command('build',['/usr/bin/gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-Wpedantic','-Wformat=2','-Wshadow','-fsanitize=address,undefined',
            '-fno-omit-frame-pointer','-fno-pie','-no-pie','-MMD','-MF',host(out/'playback.d'),'-I'+host(out/'sources/idf/components/native_stream/include'),
            '-I'+host(out/'sources/idf/esp32-cyd2usb-native/main'),'-I'+host(out/'sources/vendor/include'),'-I'+host(out/'sources/vendor/include/decoder'),
            '-I'+host(out/'sources/vendor/include/decoder/impl'),'-I'+host(out/'sources'/PUBLIC/'include'),'-I'+host(out/'sources'/CONFIG),
            host(out/'sources/tests/native/opus_family1_playback_host.c'),'-l:libopus.so.0','-l:libogg.so.0','-lm','-o',host(binary)])
        report['executable']=dict(path=binary.name,local_only=True,**pin(binary));report['compiler_dependencies']=dict(path='playback.d',**pin(out/'playback.d'));save()
        includes=['-I'+host(out/'sources/idf/esp32-cyd2usb-native/main'),'-I'+host(out/'sources/idf/components/native_stream/include'),'-I'+host(out/'sources/vendor/include'),
            '-I'+host(out/'sources/vendor/include/decoder'),'-I'+host(out/'sources/vendor/include/decoder/impl')]
        report['layout_executables']=[];report['host_layout']={}
        for label in ('before','after'):
            executable=out/('layout-'+label+'-owner');prefix=['-I'+host(out/'layout-before')] if label=='before' else []
            command('layout-'+label+'-build',['/usr/bin/gcc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Wpedantic',*prefix,*includes,host(out/'sources/tests/native/opus_family1_playback_size.c'),'-o',host(executable)])
            report['layout_executables'].append(dict(path=executable.name,local_only=True,**pin(executable)));report['host_layout'][label]=json.loads(command('layout-'+label+'-run',[host(executable)]))
        before_size=report['host_layout']['before'];after_size=report['host_layout']['after']
        need(before_size['adapter_bytes']-after_size['adapter_bytes']==1992 and before_size['static_zero_bytes']==0 and after_size['static_zero_bytes']==2048,'measured HOST owner shrink2048B minus56B streamed Tags state')
        nm=command('nm-path',['readlink','-f','/usr/bin/nm']).decode().strip();report['nm_identity']=command('nm-sha',['sha256sum',nm]).decode().strip()
        symbol=next(line for line in command('static-zero-symbol',[nm,'-S','--defined-only',host(binary)]).decode().splitlines() if line.endswith(' ofp_zero_chunk'))
        need(int(symbol.split()[1],16)==2048 and symbol.split()[2]=='r','actual read-only static zero symbol');report['static_zero_symbol']=symbol
        result=json.loads(command('test',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',host(binary),*[host(p) for p in paths]]))
        need(result['passed'] and result['positive_schedules']==34 and result['host_contract_controls']==27 and result['eos_close_retry']==1 and
            result['maximum_unique_plane_bytes']==92160 and result['maximum_output_chunk_bytes']==2048 and result['whole_original_120ms_packets']==92 and
            result['gain_metadata_only'] and result['scripted_host_statuses'] and result['native_esp_oom_qualified'] is False,'complete real synthesis/held-page/close/refusal inventory')
        report['measurements']=result
        for name,library,identity in libraries:need(command(name+'-post-sha',['sha256sum',library]).decode().strip()==identity,'unchanged creator library')
        need(command('compiler-post-sha',['sha256sum',compiler]).decode().strip()==report['compiler_identity'],'unchanged compiler')
        need(command('nm-post-sha',['sha256sum',nm]).decode().strip()==report['nm_identity'],'unchanged symbol reader')
        for row in report['sources']:need(pin(row['path'])==pin(out/row['snapshot'])==dict(bytes=row['bytes'],sha256=row['sha256']),'all original/frozen inputs current')
        need(pin(before_header)=={k:report['layout_reference'][k] for k in ('bytes','sha256')},'unchanged layout-only historical source')
        report.update(passed=True,completed=True,all_source_bindings_current=True);print(json.dumps(dict(passed=True,capture=out.relative_to(ROOT).as_posix(),measurements=result,host_layout=report['host_layout'])));return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));print(json.dumps(dict(passed=False,failure=report['failure'])));return 1
    finally:save()
if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
