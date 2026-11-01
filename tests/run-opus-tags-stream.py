"""Validate streamed OpusTags fields/UTF-8 using Python strict decoding and real verified pages."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import struct
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
PUBLIC='idf/components/native_vorbis_xiph/upstream/libogg'
CONFIG='idf/components/native_vorbis_xiph/platform'
SOURCES=['idf/components/native_stream/include/'+n for n in ('opus_tags_stream.h','ogg_page_input.h','ogg_opus_timeline.h')]
SOURCES+=['tests/native/opus_tags_stream_host.c','tests/run-opus-tags-stream.py',PUBLIC+'/include/ogg/ogg.h',PUBLIC+'/include/ogg/os_types.h',PUBLIC+'/COPYING',CONFIG+'/ogg/config_types.h']
def need(value,why):
    if not value:raise ValueError(why)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path):return dict(bytes=Path(path).stat().st_size,sha256=sha(path))
def host(path):
    value=Path(path).resolve().as_posix();return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value
def generate(path):
    rows=[];total=0
    with path.open('xb') as f:
        f.write(b'OTUF101\0'+bytes(4))
        def emit(name,values):
            nonlocal total
            row=dict(category=name,cases=0,valid=0,invalid=0)
            for value in values:
                need(len(value)<=8,'bounded generated vector')
                try:value.decode('utf-8','strict');valid=True
                except UnicodeDecodeError:valid=False
                f.write(bytes((len(value),int(valid)))+value);row['cases']+=1;row['valid' if valid else 'invalid']+=1;total+=1
            rows.append(row)
        emit('all_unicode_scalars',(chr(c).encode('utf-8') for c in range(0x110000) if not 0xd800<=c<=0xdfff))
        emit('all_single_bytes',(bytes((a,)) for a in range(256)))
        emit('all_two_byte_sequences',(bytes((a,b)) for a in range(256) for b in range(256)))
        emit('selected_three_byte_sequences',(bytes((a,b,0x80)) for a in range(256) for b in range(256)))
        emit('selected_four_byte_sequences',(bytes((a,b,0x80,0x80)) for a in range(256) for b in range(256)))
        emit('explicit_boundaries',(b'',b'\xc2',b'\xe0',b'\xe0\xa0',b'\xed\xa0\x80',b'\xf0',b'\xf0\x90',b'\xf0\x90\x80',b'\xf4\x90\x80\x80',
            b'\xef\xbf\xbe',b'\xef\xbf\xbf',b'\xed\xa1\x8c\xed\xbe\xb4',b'A\0B',b'\xef\xbb\xbf',b'\xc0\x80',b'\xf8\x88\x80\x80\x80',b'\xfc\x84\x80\x80\x80\x80',b'\xff'))
        f.seek(8);f.write(struct.pack('<I',total))
    need(total==1308946 and rows[0]['cases']==1112064 and not rows[0]['invalid'],'exact strict UTF-8 reference census')
    return dict(cases=total,rows=rows,python=platform.python_version(),python_executable=pin(sys.executable),file=pin(path))
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh ignored capture');out.mkdir(parents=True)
    report=dict(passed=False,completed=False,commands=[],sources=[],decoder_executed=False,native_executed=False,production_selected=False,
        utf8_oracle='Python strict UTF-8 decoder; all Unicode scalars/all one- and two-byte sequences, selected longer sequences and explicit boundaries')
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
        vector_path=out/'utf8-vectors.bin';report['reference']=generate(vector_path);save()
        report['compiler_version']=command('compiler-version',['/usr/bin/gcc','--version']).decode().splitlines()[0];compiler=command('compiler-path',['readlink','-f','/usr/bin/gcc']).decode().strip()
        report['compiler_identity']=command('compiler-sha',['sha256sum',compiler]).decode().strip();library=command('libogg-path',['readlink','-f','/lib/x86_64-linux-gnu/libogg.so.0']).decode().strip()
        need(library.startswith('/usr/lib/') and '\n' not in library,'installed public creator libogg');report['libogg_identity']=command('libogg-sha',['sha256sum',library]).decode().strip();binary=out/'tags'
        command('build',['/usr/bin/gcc','-std=c11','-O2','-g','-Wall','-Wextra','-Werror','-Wpedantic','-Wformat=2','-Wshadow','-fsanitize=address,undefined',
            '-fno-omit-frame-pointer','-fno-pie','-no-pie','-MMD','-MF',host(out/'tags.d'),'-I'+host(out/'sources/idf/components/native_stream/include'),
            '-I'+host(out/'sources'/PUBLIC/'include'),'-I'+host(out/'sources'/CONFIG),host(out/'sources/tests/native/opus_tags_stream_host.c'),library,'-o',host(binary)])
        report['executable']=dict(path=binary.name,local_only=True,**pin(binary));report['compiler_dependencies']=dict(path='tags.d',**pin(out/'tags.d'));save()
        result=json.loads(command('test',['env','ASAN_OPTIONS=detect_leaks=1:halt_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',host(binary),host(vector_path)]))
        need(result['passed'] and result['python_utf8_vectors']==1308946 and result['declared_text_packets']==2617892 and result['parser_schedules']==2618236 and
            result['field_controls']==32 and result['size_policy_controls']==3 and result['verified_page_schedules']==result['creator_libogg_walks']==20 and
            result['maximum_header_bytes']==125829120 and not result['whole_comment_allocation'] and result['binary_tail_permitted'] and not result['decoder_executed'],'complete constant-memory Tags validation inventory')
        report['measurements']=result;need(command('libogg-post-sha',['sha256sum',library]).decode().strip()==report['libogg_identity'],'unchanged creator libogg')
        need(command('compiler-post-sha',['sha256sum',compiler]).decode().strip()==report['compiler_identity'],'unchanged compiler')
        for row in report['sources']:need(pin(row['path'])==pin(out/row['snapshot'])==dict(bytes=row['bytes'],sha256=row['sha256']),'all initial/final source bytes current')
        need(pin(vector_path)==report['reference']['file'] and pin(sys.executable)==report['reference']['python_executable'],'unchanged generated inputs and Python oracle executable')
        report.update(passed=True,completed=True,all_source_bindings_current=True);print(json.dumps(dict(passed=True,capture=out.relative_to(ROOT).as_posix(),measurements=result)));return 0
    except Exception as error:
        report['failure']=dict(type=type(error).__name__,reason=str(error));print(json.dumps(dict(passed=False,failure=report['failure'])));return 1
    finally:save()
if __name__=='__main__':
    sys.dont_write_bytecode=True
    raise SystemExit(main())
