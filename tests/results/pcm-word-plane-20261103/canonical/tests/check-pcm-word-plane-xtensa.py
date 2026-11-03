"""Compile/disassemble same-helper LX6 probes; no SDK build, link or execution."""
import argparse,hashlib,importlib.util,json,os,struct,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HEADER=ROOT/'idf/components/native_stream/include/pcm_word_plane.h'
PROBE=ROOT/'tests/native/pcm_word_plane_xtensa_probe.c'
INSPECTOR=ROOT/'tests/fixtures/pcm_word_plane/inspect_xtensa.py'
REPOSITORY=ROOT.parent.parent if ROOT.parent.name=='.worktree' else ROOT
TOOLS=REPOSITORY/'.idf/tools-v6.0.2/tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--tool-directory',type=Path,default=TOOLS)
    parser.add_argument('--historical-capture',type=Path,help='Optional retained O2.o/report.json directory for readonly L32R reinspection')
    args=parser.parse_args();out=args.output.resolve();assert out.is_relative_to(ROOT/'.build') and not out.exists();out.mkdir(parents=True);(out/'tmp').mkdir();(out/'sources').mkdir()
    compiler=args.tool_directory/'xtensa-esp32-elf-gcc.exe';objdump=args.tool_directory/'xtensa-esp32-elf-objdump.exe';assert compiler.is_file() and objdump.is_file()
    report=dict(passed=False,SDK_started=False,QEMU_started=False,object_executed=False,linked=False,sources=[],commands=[],probes={},historical_reinspection_requested=args.historical_capture is not None)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def execute(name,argv):
        start=time.monotonic();process=subprocess.Popen(list(map(str,argv)),stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                env=dict(os.environ,TMP=str(out/'tmp'),TEMP=str(out/'tmp')),creationflags=subprocess.CREATE_NO_WINDOW)
        row=dict(name=name,argv=list(map(str,argv)),pid=process.pid,state='running');report['commands'].append(row);save()
        try:stdout,stderr=process.communicate(timeout=60)
        except subprocess.TimeoutExpired:
            process.kill();stdout,stderr=process.communicate(timeout=15);row['timed_out']=True
        for label,body in (('stdout',stdout),('stderr',stderr)):
            path=out/(name+'.'+label+'.log');path.write_bytes(body);row[label]=dict(path=path.name,bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
        row.update(state='complete',exit_status=process.returncode,seconds=time.monotonic()-start);save();assert process.returncode==0 and not row.get('timed_out'),name
        return stdout.decode('utf-8')
    save()
    try:
        for path in (HEADER,PROBE,INSPECTOR,Path(__file__).resolve()):
            target=out/'sources'/path.name;target.write_bytes(path.read_bytes());report['sources'].append(dict(path=str(path),snapshot=target.relative_to(out).as_posix(),bytes=path.stat().st_size,sha256=sha(path)))
        report['tools']={str(path):dict(bytes=path.stat().st_size,sha256=sha(path)) for path in (compiler,objdump)}
        execute('compiler-version',[compiler,'--version']);execute('objdump-version',[objdump,'--version'])
        spec=importlib.util.spec_from_file_location('frozen_word_inspector',out/'sources'/INSPECTOR.name);inspector=importlib.util.module_from_spec(spec);spec.loader.exec_module(inspector)
        flags=['-std=c11','-Wall','-Wextra','-Werror','-ffreestanding','-fno-builtin','-fno-stack-protector','-ffunction-sections','-fdata-sections','-fno-lto','-fstrict-volatile-bitfields','-I'+str(out/'sources')]
        for optimization in ('-O2','-O3'):
            label=optimization[1:];obj=out/(label+'.o')
            execute(label+'-compile',[compiler,*flags,optimization,'-c',out/'sources'/PROBE.name,'-o',obj])
            text=execute(label+'-disassemble',[objdump,'-dr',obj])
            need_names=('pcm_word_probe_clear','pcm_word_probe_store','pcm_word_probe_load')
            report['probes'][label]=dict(object=dict(path=obj.name,bytes=obj.stat().st_size,sha256=sha(obj)),
                    inspection=inspector.inspect(text,need_names))
        mutant=out/'sources/forbidden_width_probe.c'
        mutant.write_text('#include <stdint.h>\n__attribute__((noinline,used)) uint8_t forbidden_byte(const volatile uint8_t *p){return *p;}\n__attribute__((noinline,used)) void forbidden_half(volatile uint16_t *p,uint16_t bits){*p=bits;}\n__attribute__((noinline,used)) float forbidden_float(const volatile float *p,float gain){return *p+gain;}\n',encoding='utf-8')
        obj=out/'forbidden.o';execute('forbidden-compile',[compiler,*flags,'-O2','-c',mutant,'-o',obj]);text=execute('forbidden-disassemble',[objdump,'-dr',obj]);controls=[]
        for name in ('forbidden_byte','forbidden_half','forbidden_float'):
            try:inspector.inspect(text,(name,))
            except ValueError as error:controls.append(dict(probe=name,rejected=True,reason=str(error)))
            else:raise AssertionError('Forbidden-width object was accepted: '+name)
        if args.historical_capture is not None:
            # Optional evidence is independent of the current helper gates.
            # Its original overstrict NONPASS result/header stay unchanged.
            original=args.historical_capture.resolve()
            assert original.is_relative_to(ROOT/'.build') and not original.is_relative_to(out) and not out.is_relative_to(original)
            historical=original/'O2.o';body=historical.read_bytes();assert body[:4]==b'\x7fELF' and body[4:6]==b'\x01\x01' and struct.unpack_from('<H',body,18)[0]==94
            offset=struct.unpack_from('<I',body,32)[0];size,count,names=struct.unpack_from('<HHH',body,46)
            sections=[struct.unpack_from('<10I',body,offset+index*size) for index in range(count)]
            names_row=sections[names];strings=body[names_row[4]:names_row[4]+names_row[5]]
            literals={}
            for section in sections:
                name=strings[section[0]:].split(b'\0',1)[0].decode()
                if name=='.literal.pcm_word_probe_store':
                    contents=body[section[4]:section[4]+section[5]]
                    assert section[1]==1 and section[2]&2 and not section[2]&1 and section[8]>=4 and contents==b'\xff\xff\0\0'
                    literals[name]=dict(readonly=True,bytes=len(contents),alignment=section[8],value_u32=65535,
                        contents_sha256=hashlib.sha256(contents).hexdigest(),ELF_section_flags=section[2])
            assert len(literals)==1
            text=execute('historical01-disassemble',[objdump,'-dr',historical])
            report['historical01_readonly_literal_reinspection']=dict(original_status='NONPASS',original_report_sha256=sha(original/'report.json'),
                object=dict(path=str(historical),bytes=len(body),sha256=hashlib.sha256(body).hexdigest()),
                inspection=inspector.inspect(text,('pcm_word_probe_clear','pcm_word_probe_store','pcm_word_probe_load'),literals),
                original_capture_mutated=False,object_executed=False)
            assert historical.read_bytes()==body
        assert all(sha(row['path'])==row['sha256'] and sha(out/row['snapshot'])==row['sha256'] for row in report['sources'])
        assert all(sha(path)==pin['sha256'] for path,pin in report['tools'].items())
        report.update(passed=True,all_source_tool_bindings_unchanged=True,forbidden_width_controls=controls)
    except BaseException as error:report['error']=type(error).__name__+': '+str(error);raise
    finally:save()
    print(json.dumps(dict(passed=True,optimization_profiles=list(report['probes']),forbidden_width_controls=3,SDK_started=False,QEMU_started=False,object_executed=False)))
if __name__=='__main__':main()
