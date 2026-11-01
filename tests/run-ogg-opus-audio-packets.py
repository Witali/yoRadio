"""Exercise real verified-page audio packet ownership against creator libogg."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
PUBLIC='idf/components/native_vorbis_xiph/upstream/libogg'
CONFIG='idf/components/native_vorbis_xiph/platform'
SOURCES=['idf/components/native_stream/include/'+name for name in ('ogg_opus_audio_packets.h','ogg_page_input.h','ogg_opus_timeline.h','opus_family1_mapping.h','opus_multistream_framing.h')]
SOURCES += ['tests/native/ogg_opus_audio_packets_host.c','tests/run-ogg-opus-audio-packets.py',PUBLIC+'/include/ogg/ogg.h',PUBLIC+'/include/ogg/os_types.h',PUBLIC+'/COPYING',CONFIG+'/ogg/config_types.h']
def need(value,why):
    if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path):return dict(bytes=Path(path).stat().st_size,sha256=sha(path))
def host(path):
    value=Path(path).resolve().as_posix();return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--reference',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();reference=args.reference.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists() and reference.is_relative_to(ROOT/'.build'),'fresh ignored capture')
    inputs=json.loads((ROOT/'tests/results/cyd-opus-family1-20261101/manifest.json').read_bytes())['reference_fixtures']
    out.mkdir(parents=True);report=dict(passed=False,completed=False,commands=[],sources=[],fixtures={},native_executed=False,production_selected=False,
        decoder_executed=False,decoder_drain_claimed=False,allocation_failure_injected=None,
        allocation_failure_scope='new public Opus packet owner host seam only')
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(path,relative):
        destination=out/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(Path(path).read_bytes());report['sources'].append(dict(path=str(Path(path).resolve()),snapshot=relative.as_posix(),**pin(path)))
    def command(name,argv):
        full=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+list(map(str,argv));row=dict(name=name,argv=full,state='starting',timeout_seconds=120);report['commands'].append(row);save();start=time.monotonic()
        with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
            child=subprocess.Popen(full,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);row.update(pid=child.pid,state='running');save()
            try:status=child.wait(timeout=120)
            except subprocess.TimeoutExpired:child.kill();status=child.wait();row['timed_out']=True
            row.update(state='complete',exit_status=status,elapsed_seconds=round(time.monotonic()-start,3))
        for stream in ('stdout','stderr'):
            path=out/(name+'.'+stream+'.log');row[stream]=dict(path=path.name,**pin(path))
        save();need(status==0 and not row.get('timed_out'),'actual terminal zero: '+name);return (out/(name+'.stdout.log')).read_bytes()
    save()
    try:
        for name in SOURCES:freeze(ROOT/name,Path('sources')/name)
        for c in (3,8):
            name='channels'+str(c)+'.packets';path=reference/name;expected=inputs['channels'+str(c)]['files'][name]
            need(pin(path)=={k:expected[k] for k in ('bytes','sha256')},'unchanged complete creator-valid audio packets');freeze(path,Path('fixtures')/name);report['fixtures'][name]=pin(path)
        report['compiler_version']=command('compiler-version',['/usr/bin/gcc','--version']).decode().splitlines()[0];compiler=command('compiler-path',['readlink','-f','/usr/bin/gcc']).decode().strip()
        report['compiler_identity']=command('compiler-sha',['sha256sum',compiler]).decode().strip();library=command('libogg-path',['readlink','-f','/lib/x86_64-linux-gnu/libogg.so.0']).decode().strip()
        need(library.startswith('/usr/lib/') and '\n' not in library,'installed creator libogg');report['libogg_identity']=command('libogg-sha',['sha256sum',library]).decode().strip()
        report['libogg_version']=command('libogg-version',['/usr/bin/dpkg-query','-W','-f=${Version}\n','libogg0:amd64']).decode().strip();binary=out/'packets'
        command('build',['/usr/bin/gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-Wpedantic','-Wformat=2','-Wshadow','-fsanitize=address,undefined',
            '-fno-omit-frame-pointer','-fno-pie','-no-pie','-MMD','-MF',host(out/'packets.d'),'-I'+host(out/'sources/idf/components/native_stream/include'),
            '-I'+host(out/'sources'/PUBLIC/'include'),'-I'+host(out/'sources'/CONFIG),host(out/'sources/tests/native/ogg_opus_audio_packets_host.c'),library,'-o',host(binary)])
        report['executable']=dict(path=binary.name,local_only=True,**pin(binary));report['compiler_dependencies']=dict(path='packets.d',**pin(out/'packets.d'));save()
        rows=[json.loads(line) for line in command('test',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',host(binary),
            host(out/'fixtures/channels3.packets'),host(out/'fixtures/channels8.packets')]).decode().splitlines()];result=rows[-1];controls=rows[:-1]
        need(len(rows)==19 and result['passed'] and result['owner_schedules']==65 and result['creator_libogg_walks']==18 and result['borrowed_packets']==202 and result['copied_packets']==148 and
            result['maximum_packet']==61440 and result['over_limit_policy']==61441 and result['allocation_failure_injected'] and not result['decoder_drain_claimed'] and
            result['realloc_ordinals']==result['retry_cases']==result['abandon_cases']==9,'real packet ownership plus each new host realloc ordinal/retry/abandon inventory')
        need([(v['ordinal'],v['retry']) for v in controls]==[(ordinal,retry) for ordinal in range(1,10) for retry in (False,True)] and all(
            v['held_page_preserved'] and v['cursor_prefix_token_preserved'] and v['cleanup_live_bytes']==0 and v['packets']==int(v['retry']) for v in controls),
            'all actual host allocation seams preserve the held page/cursor/prefix/token and cleanly retry or abandon')
        report['measurements']=result;report['realloc_controls']=controls;report['allocation_failure_injected']=result['allocation_failure_injected']
        need(command('libogg-post-sha',['sha256sum',library]).decode().strip()==report['libogg_identity'],'unchanged creator library')
        need(command('compiler-post-sha',['sha256sum',compiler]).decode().strip()==report['compiler_identity'],'unchanged compiler')
        for row in report['sources']:need(pin(row['path'])==pin(out/row['snapshot'])==dict(bytes=row['bytes'],sha256=row['sha256']),'all original/frozen input bytes unchanged')
        report.update(passed=True,completed=True,all_source_bindings_current=True);print(json.dumps(dict(passed=True,capture=out.relative_to(ROOT).as_posix(),measurements=result)));return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));print(json.dumps(dict(passed=False,failure=report['failure'])));return 1
    finally:save()
if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
