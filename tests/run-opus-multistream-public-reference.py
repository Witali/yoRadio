"""Qualify RFC packet framing with independent public creator decoder handles."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
SOURCES=['tests/fixtures/opus_multistream_public/framing.py','tests/native/opus_multistream_public_reference.c',
         'tests/native/opus_family1_public.h','tests/fixtures/opus_family1/generate.py',
         'tests/test-opus-multistream-framing.py','tests/run-opus-multistream-public-reference.py']
def need(value,why):
    if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path):return dict(bytes=Path(path).stat().st_size,sha256=sha(path))
def host(path):
    value=Path(path).resolve().as_posix();return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--family1-reference',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();baseline=args.family1_reference.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists() and baseline.is_relative_to(ROOT/'.build'),'fresh capture and local qualified input')
    original=json.loads((baseline/'report.json').read_bytes());published=json.loads((ROOT/'tests/results/cyd-opus-family1-20261101/manifest.json').read_bytes())
    need(sha(baseline/'report.json')==published['actual_reference_report_sha256'] and original['passed'] and original['completed'],'exact existing creator-valid complete fixtures')
    out.mkdir(parents=True);report=dict(passed=False,completed=False,commands=[],sources=[],fixtures={},private_abi_used=False,native_vendor_executed=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(path,relative):
        path=Path(path);destination=out/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(path.read_bytes())
        report['sources'].append(dict(path=str(path.resolve()),snapshot=relative.as_posix(),**pin(path)))
    def command(name,argv):
        full=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+list(map(str,argv));row=dict(name=name,argv=full,state='starting',timeout_seconds=120)
        report['commands'].append(row);save();start=time.monotonic()
        with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
            child=subprocess.Popen(full,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr);row.update(state='running',pid=child.pid);save()
            try:status=child.wait(timeout=120)
            except subprocess.TimeoutExpired:child.kill();status=child.wait();row['timed_out']=True
            row.update(state='complete',exit_status=status,elapsed_seconds=round(time.monotonic()-start,3))
        for stream in ('stdout','stderr'):
            path=out/(name+'.'+stream+'.log');row[stream]=dict(path=path.name,**pin(path))
        save();need(status==0 and not row.get('timed_out'),'actual terminal zero: '+name);return (out/(name+'.stdout.log')).read_bytes()
    save()
    try:
        for name in SOURCES:freeze(ROOT/name,Path('sources')/name)
        freeze(baseline/'report.json',Path('sources/family1-reference/report.json'))
        framing=module(out/'sources/tests/fixtures/opus_multistream_public/framing.py','reviewed_framing')
        reader=module(out/'sources/tests/fixtures/opus_family1/generate.py','reviewed_original_transport')
        report['compiler_version']=command('compiler-version',['/usr/bin/gcc','--version']).decode().splitlines()[0]
        compiler=command('compiler-path',['readlink','-f','/usr/bin/gcc']).decode().strip();report['compiler_identity']=command('compiler-sha',['sha256sum',compiler]).decode().strip()
        lib=command('libopus-link-path',['/usr/bin/gcc','-print-file-name=libopus.so.0']).decode().strip();need(lib.startswith('/usr/') and '\n' not in lib,'installed public libopus')
        lib=command('libopus-path',['readlink','-f',lib]).decode().strip();report['libopus_identity']=command('libopus-sha',['sha256sum',lib]).decode().strip()
        binary=out/'reference';command('reference-build',['/usr/bin/gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-Wpedantic','-Wformat=2',
            '-fsanitize=address,undefined','-fno-omit-frame-pointer','-fno-pie','-no-pie',host(out/'sources/tests/native/opus_multistream_public_reference.c'),
            '-l:libopus.so.0','-lm','-o',host(binary)]);report['executable']=dict(path=binary.name,local_only=True,**pin(binary));save()
        for channels in (3,6,8):
            name='channels'+str(channels);source=baseline/(name+'.packets');need(pin(source)=={k:original['fixtures'][name]['files'][source.name][k] for k in ('bytes','sha256')},'exact original public multistream packet bytes')
            freeze(source,Path('sources/family1-reference')/source.name);freeze(baseline/(name+'-raw.pcm'),Path('sources/family1-reference')/(name+'-raw.pcm'))
            body,account=framing.prepare(source.read_bytes(),reader.packets);transport=out/(name+'.packets');transport.write_bytes(body)
            measured=json.loads(command(name+'-reference',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',
                host(binary),host(transport),host(out/name)]))
            need(measured['creator']=='libopus 1.4' and measured['channels']==channels and measured['packets']==11 and measured['frames_per_stream']==10560 and
                measured['exact_creator_multistream_match'] and measured['maximum_mapped_float_difference']==0,'creator independent elementary handles exactly reproduce original mapped multistream floats')
            mapped=out/(name+'-mapped.pcm');need(pin(mapped)==pin(baseline/(name+'-raw.pcm')),'full mapped PCM equals original independent reference byte-for-byte')
            report['fixtures'][name]=dict(framing=account,measurements=measured,transport=dict(path=transport.name,local_only=True,**pin(transport)),
                pcm={p.name:dict(local_only=True,**pin(p)) for p in [mapped,*sorted(out.glob(name+'-stream*.pcm'))]});save()
        report['framing_tests']=json.loads(command('framing-tests',['/usr/bin/python3','-B',host(out/'sources/tests/test-opus-multistream-framing.py'),
            '--module',host(out/'sources/tests/fixtures/opus_multistream_public/framing.py')]))
        need(report['framing_tests']['passed'] and report['framing_tests']['cases']==32,'independent expected-byte framing and malformed controls')
        need(command('libopus-post-sha',['sha256sum',lib]).decode().strip()==report['libopus_identity'],'unchanged creator library')
        need(command('compiler-post-sha',['sha256sum',compiler]).decode().strip()==report['compiler_identity'],'unchanged compiler')
        for row in report['sources']:need(pin(row['path'])==pin(out/row['snapshot'])==dict(bytes=row['bytes'],sha256=row['sha256']),'all frozen source/input bindings current')
        report.update(passed=True,completed=True,all_source_bindings_current=True);print(json.dumps(dict(passed=True,capture=out.relative_to(ROOT).as_posix(),framing_cases=32)));return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));print(json.dumps(dict(passed=False,failure=report['failure'])));return 1
    finally:save()
if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
