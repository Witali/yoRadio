"""Unsigned-rate identification/comment metadata under host ASan/UBSan.

No setup header, DSP initialization, audio packet decoder or deferred target
fixture executes. Complete sources and owned process receipts are retained.
"""
import argparse,ast,hashlib,importlib.util,json,os,re,subprocess,sys,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'idf/components/native_vorbis_xiph'
PORT=ROOT/'idf/components/native_vorbis_xiph_port'
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def linux(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:]if sys.platform=='win32'else value
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--port-manifest-sha256',required=True)
    args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build')and out!=ROOT/'.build'and not out.exists(),'fresh task-local output')
    need(sha((PORT/'port-manifest.json').read_bytes())==args.port_manifest_sha256,'reviewed port manifest')
    out.mkdir(parents=True);(out/'sources').mkdir();(out/'objects').mkdir();inputs={}
    report=dict(completed=False,passed=False,sanitizers=['address','undefined'],commands=[],inputs=inputs,
                physical_device=False,raw_header_decoder_executed=True,identification_header_executed=True,comment_header_executed=True,setup_header_executed=False,dsp_executed=False,packet_decoder_executed=False,
                deferred_DSP_gate_resumed=False,full_decoder_qualified=False,production_radio_integration=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,name):
        body=path.read_bytes();destination=out/'sources'/name;destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes(body);inputs[str(path.resolve())]=dict(sha256=sha(body),snapshot=destination.relative_to(out).as_posix());return body
    def run(name,argv):
        nonce=uuid.uuid4().hex;request=out/(name+'.request.json');receipt=out/(name+'.receipt.json');stop=out/(name+'.stop')
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=60,receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command=(['wsl.exe','--exec','python3']if sys.platform=='win32'else[sys.executable])+[linux(out/'supervisor.py'),linux(request)]
        row=dict(name=name,argv=command,child_argv=list(map(str,argv)),nonce=nonce,request_sha256=sha(request.read_bytes()))
        report['commands'].append(row);save();child=None;error=None;start=time.monotonic()
        try:
            with(out/(name+'.stdout.log')).open('xb')as so,(out/(name+'.stderr.log')).open('xb')as se:
                child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=so,stderr=se,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt'else 0)
                row['transport_pid']=child.pid;child.wait(timeout=80)
        except BaseException as caught:error=caught;row['parent_error']=repr(caught)
        finally:
            if child is not None and child.poll()is None:
                stop.write_text(nonce,encoding='ascii')
                try:child.wait(timeout=15)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5);row['forced_transport_stop']=True
            observed=json.loads(receipt.read_text())if receipt.exists()else{}
            row.update(elapsed_seconds=time.monotonic()-start,supervisor=observed,transport_exit=None if child is None else child.poll())
            for stream in('stdout','stderr'):
                path=out/(name+'.'+stream+'.log');row[stream+'_sha256']=sha(path.read_bytes())if path.exists()else None
            save()
        need(error is None and row['transport_exit']==0 and not row.get('forced_transport_stop'),'owned transport terminal '+name)
        need(observed.get('nonce')==nonce and observed.get('request_sha256')==row['request_sha256']and observed.get('state')=='terminal'and observed.get('final')is True and observed.get('child_reaped')is True and observed.get('group_gone')is True and observed.get('new_session')is True and observed.get('child_pid')==observed.get('owned_pgid')and observed.get('child_returncode')==0,'owned Linux command terminal '+name)
        return(out/(name+'.stdout.log')).read_text('utf-8',errors='replace')
    save()
    try:
        freeze(Path(__file__),'runner.py')
        for folder,label in((BASE,'components/native_vorbis_xiph'),(PORT,'components/native_vorbis_xiph_port')):
            for path in sorted(folder.rglob('*')):
                if path.is_file():freeze(path,label+'/'+path.relative_to(folder).as_posix())
        for name in('vorbis_xiph_alloc.h','vorbis_xiph_alloc_inject.h','vorbis_xiph_alloc.c','vorbis_xiph_rate.c','vorbis_xiph_rate_host.c'):
            freeze(ROOT/'tests/native'/name,'native/'+name)
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py');tree=ast.parse(origin)
        supervisors=[ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SUPERVISOR'for t in n.targets)]
        need(len(supervisors)==1,'one owned nonce-bound Linux supervisor')
        (out/'supervisor.py').write_text(supervisors[0],encoding='utf-8',newline='\n');report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes())
        preparer=out/'sources/components/native_vorbis_xiph_port/prepare.py'
        spec=importlib.util.spec_from_file_location('owned_xiph_rate_prepare',preparer);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        generated=out/'generated';porting=module.materialize(out/'sources/components/native_vorbis_xiph',out/'sources/components/native_vorbis_xiph_port',generated)
        report['porting']=porting;need(porting['port_manifest_sha256']==args.port_manifest_sha256,'executed frozen port identity')
        report['compiler_version']=run('compiler-version',['gcc','--version']);report['compiler_machine']=run('compiler-machine',['gcc','-dumpmachine'])
        native=out/'sources/native'
        includes=[generated/'ported/include',generated/'base/upstream/libogg/include',generated/'base/platform',generated/'base/upstream/libvorbis/lib',generated/'ported',native]
        common=['gcc','-std=c11','-O1','-g','-UNDEBUG','-D_GNU_SOURCE=1','-DHAVE_ALLOCA_H=1','-fno-fast-math','-ffp-contract=off','-fno-pie','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-ffunction-sections','-fdata-sections','-MMD',*['-I'+linux(p)for p in includes]]
        objects=[]
        for index,unit in enumerate(porting['compiled_units']):
            obj=out/'objects'/f'library-{index:02d}.o';objects.append(obj)
            run('compile-library-'+str(index).zfill(2),[*common,'-include',linux(native/'vorbis_xiph_alloc_inject.h'),'-c',linux(generated/unit['compiled']),'-o',linux(obj)])
        for stem in('alloc','rate','rate_host'):
            obj=out/'objects'/('fixture-'+stem+'.o');objects.append(obj)
            run('compile-fixture-'+stem,[*common,'-Wall','-Wextra','-Werror','-c',linux(native/('vorbis_xiph_'+stem+'.c')),'-o',linux(obj)])
        binary=out/'rate-tests';run('link',['gcc','-fsanitize=address,undefined','-fno-sanitize-recover=all','-no-pie','-Wl,--gc-sections',*[linux(p)for p in objects],'-lm','-o',linux(binary)])
        text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',linux(binary)])
        match=re.fullmatch(r'RATE_PASS scenarios=([1-9][0-9]*) live=0 bytes=0\s*',text)
        need(match is not None and not(out/'execute.stderr.log').read_bytes(),'complete asserted identification/comment metadata result without sanitizer diagnostics')
        dependencies={}
        for index,unit in enumerate(porting['compiled_units']):
            path=out/'objects'/f'library-{index:02d}.d'
            tokens=path.read_text().replace('\\\n',' ').split()
            selected=[value for value in tokens if value.endswith('/vorbis/codec.h')]
            if selected:need(set(selected)=={linux(generated/'ported/include/vorbis/codec.h')},'selected owned public header in '+unit['compiled'])
            dependencies[unit['original']]=dict(sha256=sha(path.read_bytes()),codec_header=selected)
        need(dependencies['upstream/libvorbis/lib/info.c']['codec_header'] and dependencies['upstream/libvorbis/lib/block.c']['codec_header'],'rate consumers select owned public header')
        report['library_dependencies']=dependencies
        need(all(sha(Path(path).read_bytes())==pin['sha256']==sha((out/pin['snapshot']).read_bytes())for path,pin in inputs.items()),'all frozen/original source inputs unchanged')
        report.update(completed=True,passed=True,scenarios=int(match[1]),binary_sha256=sha(binary.read_bytes()),library_units=len(porting['compiled_units']),fixture_units=3)
        save();print(json.dumps({k:report[k]for k in('completed','passed','scenarios','library_units','fixture_units','dsp_executed','packet_decoder_executed')}));return 0
    except BaseException as error:report.update(passed=False,error=repr(error));save();raise
if __name__=='__main__':raise SystemExit(main())
