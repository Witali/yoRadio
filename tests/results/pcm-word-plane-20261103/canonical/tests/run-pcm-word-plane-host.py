"""Qualify packed word storage on HOST; no native32-only-memory claim."""
import argparse,hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCES=('idf/components/native_stream/include/pcm_word_plane.h','tests/native/pcm_word_plane_host.c')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);out=parser.parse_args().output.resolve()
    assert out.is_relative_to(ROOT/'.build') and not out.exists();out.mkdir(parents=True)
    report=dict(passed=False,HOST_only=True,SDK_started=False,QEMU_started=False,native_memory_access_qualified=False,sources=[],commands=[])
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def execute(name,argv):
        command=(['wsl.exe','--exec'] if sys.platform=='win32' else [])+argv
        started=time.monotonic();process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        row=dict(name=name,argv=command,pid=process.pid,state='running');report['commands'].append(row);save()
        try:stdout,stderr=process.communicate(timeout=90)
        except subprocess.TimeoutExpired:
            process.kill();stdout,stderr=process.communicate(timeout=15);row['timed_out']=True
        for stream,body in (('stdout',stdout),('stderr',stderr)):
            path=out/(name+'.'+stream+'.log');path.write_bytes(body);row[stream]=dict(path=path.name,bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
        row.update(state='complete',exit_status=process.returncode,seconds=time.monotonic()-started);save()
        assert process.returncode==0 and not row.get('timed_out'),name
        return stdout
    save()
    try:
        for name in (*SOURCES,Path(__file__).relative_to(ROOT).as_posix()):
            source=ROOT/name;target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
            report['sources'].append(dict(path=name,snapshot=target.relative_to(out).as_posix(),sha256=sha(source),bytes=source.stat().st_size))
        execute('compiler-version',['gcc','--version'])
        execute('compiler-path',['which','gcc'])
        compiler=(out/'compiler-path.stdout.log').read_text().strip();execute('compiler-sha',['sha256sum',compiler])
        binary=out/'word-plane-host'
        execute('build',['gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-fno-omit-frame-pointer','-fno-pie','-no-pie',
                        '-fsanitize=address,undefined','-I'+host(out/'sources/idf/components/native_stream/include'),
                        host(out/'sources/tests/native/pcm_word_plane_host.c'),'-o',host(binary)])
        stdout=execute('test',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1','timeout','60',host(binary)])
        result=json.loads(stdout);assert result['passed'] and result['groups']==127 and result['exhaustive_bit_patterns']==65536
        assert result['immutable_DRAM'] and result['word_canaries'] and not result['timer_dependency'] and not result['native_memory_access_qualified']
        assert all(sha(ROOT/row['path'])==row['sha256'] and sha(out/row['snapshot'])==row['sha256'] for row in report['sources'])
        report.update(passed=True,all_source_bindings_unchanged=True,measurements=result,binary=dict(path=binary.name,bytes=binary.stat().st_size,sha256=sha(binary)))
    except BaseException as error:report['error']=type(error).__name__+': '+str(error);raise
    finally:save()
    print(json.dumps(dict(passed=True,groups=report['measurements']['groups'],exhaustive_bit_patterns=65536,
                         checked_samples=report['measurements']['checked_samples'],HOST_only=True,native_memory_access_qualified=False)))
if __name__=='__main__':main()
