"""Generate complete creator family1 fixtures and independently decode every channel.

The two host executables use only opaque public libopus APIs. The Python writer
owns headers/CRC/granules independently. Full raw and stereo reference PCM stay
in the fresh ignored capture. Exact failed processes and source bytes survive.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
SOURCES=['tests/native/opus_family1_public.h','tests/native/opus_family1_encode.c',
         'tests/native/opus_family1_reference.c','tests/native/opus_family1_ogg_check.c','tests/fixtures/opus_family1/generate.py',
         'tests/test-opus-family1.py','tests/run-opus-family1-reference.py']
PUBLIC='idf/components/native_vorbis_xiph/upstream/libogg'
CONFIG='idf/components/native_vorbis_xiph/platform'
SOURCES += [PUBLIC+'/include/ogg/ogg.h',PUBLIC+'/include/ogg/os_types.h',PUBLIC+'/COPYING',CONFIG+'/ogg/config_types.h']


def need(value,why):
    if not value:raise ValueError(why)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pin(path):return dict(bytes=Path(path).stat().st_size,sha256=sha(path))


def host(path):
    value=Path(path).resolve().as_posix();return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh ignored capture')
    out.mkdir(parents=True);report=dict(passed=False,completed=False,commands=[],sources=[],fixtures={},native_vendor_executed=False,
        production_sources_changed=False,private_abi_used=False,universal_conformance_claim=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def command(name,argv,timeout=120):
        argv=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+list(map(str,argv));row=dict(name=name,argv=argv,state='starting',timeout_seconds=timeout)
        report['commands'].append(row);save();started=time.monotonic()
        with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
            child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr)
            row.update(pid=child.pid,state='running');save()
            try:status=child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                child.kill();status=child.wait();row['timed_out']=True
            row.update(state='complete',exit_status=status,elapsed_seconds=round(time.monotonic()-started,3))
        for stream in ('stdout','stderr'):
            path=out/(name+'.'+stream+'.log');row[stream]=dict(path=path.name,**pin(path))
        save();need(status==0 and not row.get('timed_out'),'actual terminal zero: '+name)
        return (out/(name+'.stdout.log')).read_bytes()
    save()
    try:
        for name in SOURCES:
            destination=out/'sources'/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes((ROOT/name).read_bytes())
            report['sources'].append(dict(path=name,snapshot=destination.relative_to(out).as_posix(),**pin(destination)))
        report['compiler_version']=command('compiler-version',['/usr/bin/gcc','--version']).decode().splitlines()[0]
        compiler=command('compiler-path',['readlink','-f','/usr/bin/gcc']).decode().strip()
        report['compiler_identity']=command('compiler-sha',['sha256sum',compiler]).decode().strip()
        library=command('libopus-link-path',['/usr/bin/gcc','-print-file-name=libopus.so.0']).decode().strip()
        need(library.startswith('/usr/') and '\n' not in library,'installed public libopus')
        library=command('libopus-path',['readlink','-f',library]).decode().strip()
        report['libopus_identity']=command('libopus-sha',['sha256sum',library]).decode().strip()
        libogg=command('libogg-path',['readlink','-f','/lib/x86_64-linux-gnu/libogg.so.0']).decode().strip()
        need(libogg.startswith('/usr/lib/') and '\n' not in libogg,'installed creator libogg')
        report['libogg_identity']=command('libogg-sha',['sha256sum',libogg]).decode().strip()
        report['libogg_version']=command('libogg-version',['/usr/bin/dpkg-query','-W','-f=${Version}\n','libogg0:amd64']).decode().strip()
        flags=['-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-Wpedantic','-Wformat=2','-fsanitize=address,undefined',
               '-fno-omit-frame-pointer','-fno-pie','-no-pie']
        for name in ('encode','reference'):
            binary=out/name;source=out/'sources/tests/native'/('opus_family1_'+name+'.c')
            command(name+'-build',['/usr/bin/gcc',*flags,host(source),'-l:libopus.so.0','-lm','-o',host(binary)])
            report[name+'_executable']=dict(path=name,local_only=True,**pin(binary));save()
        command('ogg-check-build',['/usr/bin/gcc',*flags,'-I'+host(out/'sources'/PUBLIC/'include'),'-I'+host(out/'sources'/CONFIG),
            host(out/'sources/tests/native/opus_family1_ogg_check.c'),libogg,'-o',host(out/'ogg-check')])
        report['ogg_check_executable']=dict(path='ogg-check',local_only=True,**pin(out/'ogg-check'));save()
        generator_path=out/'sources/tests/fixtures/opus_family1/generate.py'
        spec=importlib.util.spec_from_file_location('family1_frozen_data_writer',generator_path)
        generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)
        for channels in (3,6,8):
            name='channels'+str(channels);transport=out/(name+'.packets')
            env=['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1']
            encoded=json.loads(command(name+'-encode',[*env,host(out/'encode'),str(channels),host(transport)]))
            body,accounting=generator.make(transport.read_bytes());fixture=out/(name+'.ogg');fixture.write_bytes(body)
            need(encoded['channels']==accounting['channels']==channels and encoded['packets']==accounting['count']==11 and
                 encoded['mapping']==accounting['mapping'] and all(v>0 for v in encoded['input_channel_energy']),'genuine full creator encoding')
            raw=out/(name+'-raw.pcm');stereo=out/(name+'-stereo.pcm');trim=out/(name+'-stereo-trim.pcm')
            reference=json.loads(command(name+'-reference',[*env,host(out/'reference'),host(transport),host(raw),host(stereo),host(trim)]))
            container_checks=[json.loads(line) for line in command(name+'-ogg-check',[*env,host(out/'ogg-check'),host(fixture),host(transport)]).decode().splitlines()]
            need(len(container_checks)==2 and [r['chunk'] for r in container_checks]==[len(body),257] and all(
                r['channels']==channels and r['pages']==13 and r['audio_packets']==11 and r['input_bytes']==len(body) and
                r['exact_original_packets'] and r['eos'] and r['sync_errors']==r['packet_holes']==0 for r in container_checks),
                'independent creator libogg complete framing/CRC/granules and exact original packet reconstruction')
            need(reference['channels']==channels and reference['raw_frames']==10560 and reference['trim_frames']==9600 and
                 all(v>0 for v in reference['channel_energy']) and all(v>0 for v in reference['channel_downmix_contribution_energy']) and
                 raw.stat().st_size==10560*channels*2 and stereo.stat().st_size==10560*4 and trim.stat().st_size==9600*4,
                 'complete independent multistream decode and every speaker contributes to full stereo matrix')
            report['fixtures'][name]=dict(encoding=encoded,accounting=accounting,reference=reference,creator_libogg_checks=container_checks,
                files={p.name:dict(local_only=True,**pin(p)) for p in (transport,fixture,raw,stereo,trim)});save()
        report['data_tests']=json.loads(command('data-tests',[host(Path(sys.executable)) if sys.platform!='win32' else '/usr/bin/python3',
            '-B',host(out/'sources/tests/test-opus-family1.py'),'--generator',host(generator_path)]))
        need(report['data_tests']['passed'] and report['data_tests']['cases']>=15,'focused framing and malformed-input controls')
        need(command('libopus-post-sha',['sha256sum',library]).decode().strip()==report['libopus_identity'],'unchanged public library')
        need(command('libogg-post-sha',['sha256sum',libogg]).decode().strip()==report['libogg_identity'],'unchanged creator libogg')
        need(command('compiler-post-sha',['sha256sum',compiler]).decode().strip()==report['compiler_identity'],'unchanged compiler')
        for source in report['sources']:
            need(pin(ROOT/source['path'])==pin(out/source['snapshot'])==dict(bytes=source['bytes'],sha256=source['sha256']),'frozen source closure remains current')
        report.update(passed=True,completed=True,all_source_bindings_current=True)
        print(json.dumps(dict(passed=True,capture=out.relative_to(ROOT).as_posix(),channels=list(report['fixtures']))));return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));print(json.dumps(dict(passed=False,failure=report['failure'])));return 1
    finally:save()


if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
