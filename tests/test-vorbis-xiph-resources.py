"""ASan/UBSan resource regressions and every original31 PCM sample via WSL.

Only the declared upstream source edits are selected. All source snapshots,
owned Linux process-group receipts and measured failures are retained.
"""
import argparse,ast,hashlib,importlib.util,json,os,re,struct,subprocess,sys,time,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'idf/components/native_vorbis_xiph'
PORT=ROOT/'idf/components/native_vorbis_xiph_port'
PREP=ROOT/'.build/vorbis-xiph-prep-20261025-01'
MODEL='a12fcb6fea905027f9af4b1d1e5b5b561fa447f457d236cd5d004fd948b07883'
def need(ok,why):
    if not ok:raise ValueError(why)
def sha(body):return hashlib.sha256(body).hexdigest()
def linux(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:]if sys.platform=='win32'else value

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--port-manifest-sha256',required=True);args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build')and out!=ROOT/'.build'and not out.exists(),'fresh task-local output')
    need(sha((PORT/'port-manifest.json').read_bytes())==args.port_manifest_sha256,'reviewed port manifest')
    out.mkdir(parents=True);(out/'sources').mkdir();(out/'objects').mkdir();ledger={}
    report=dict(completed=False,passed=False,sanitizers=['address','undefined'],commands=[],inputs=ledger,physical_device=False,target_executed=False,production_radio_integration=False,general_OOM_qualified=False,general_16KiB_stack_bound=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,name):
        body=path.read_bytes();destination=out/'sources'/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(body);ledger[str(path.resolve())]=dict(sha256=sha(body),snapshot=destination.relative_to(out).as_posix());return body
    def run(name,argv):
        nonce=uuid.uuid4().hex;request=out/(name+'.request.json');receipt=out/(name+'.receipt.json');stop=out/(name+'.stop')
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=60,receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command=(['wsl.exe','--exec','python3']if sys.platform=='win32'else[sys.executable])+[linux(out/'supervisor.py'),linux(request)]
        row=dict(name=name,argv=command,child_argv=list(map(str,argv)),nonce=nonce,request_sha256=sha(request.read_bytes()));report['commands'].append(row);save();child=None;error=None;start=time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb')as so,(out/(name+'.stderr.log')).open('xb')as se:
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
        for name in('vorbis_xiph_alloc.h','vorbis_xiph_alloc_inject.h','vorbis_xiph_alloc.c','vorbis_xiph_arena.c','vorbis_xiph_books.c','vorbis_xiph_bits.c','vorbis_xiph_residue.c','vorbis_xiph_headers.c','vorbis_xiph_dsp.c','vorbis_xiph_host.c'):freeze(ROOT/'tests/native'/name,'native/'+name)
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py');tree=ast.parse(origin)
        supervisors=[ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SUPERVISOR'for t in n.targets)]
        need(len(supervisors)==1,'one reviewed nonce-owned Linux supervisor');(out/'supervisor.py').write_text(supervisors[0],encoding='utf-8',newline='\n');report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes())
        model=json.loads(freeze(PREP/'cases.json','cases/cases.json'));need(sha(json.dumps(model,sort_keys=True,separators=(',',':')).encode())==MODEL,'unchanged original31 model')
        header=freeze(PREP/'cases.h','native/cases.h');need(sha(header)=='9e3baa93c34094ba50f2e837d23c7e600f7b81fe8e0894e979d3fe9b352c1a23','unchanged complete raw cases header')
        references={}
        for case in model['cases']:
            body=freeze(PREP/case['reference_path'],'cases/'+case['reference_path']);need(sha(body)==case['reference_pcm_sha256'],'qualified original reference PCM');references[case['id']]=body
        preparer=out/'sources/components/native_vorbis_xiph_port/prepare.py';spec=importlib.util.spec_from_file_location('owned_xiph_resource_prepare',preparer);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        generated=out/'generated';porting=module.materialize(out/'sources/components/native_vorbis_xiph',out/'sources/components/native_vorbis_xiph_port',generated);report['porting']=porting
        need(porting['port_manifest_sha256']==args.port_manifest_sha256,'executed frozen port identity')
        report['compiler_version']=run('compiler-version',['gcc','--version']);report['compiler_machine']=run('compiler-machine',['gcc','-dumpmachine'])
        native=out/'sources/native';includes=[generated/'base/upstream/libvorbis/include',generated/'base/upstream/libogg/include',generated/'base/platform',generated/'base/upstream/libvorbis/lib',generated/'ported',native]
        common=['gcc','-std=c11','-O1','-g','-UNDEBUG','-D_GNU_SOURCE=1','-DHAVE_ALLOCA_H=1','-fno-fast-math','-ffp-contract=off','-fno-pie','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-ffunction-sections','-fdata-sections',*['-I'+linux(p)for p in includes]]
        objects=[]
        for index,unit in enumerate(porting['compiled_units']):
            obj=out/'objects'/f'library-{index:02d}.o';objects.append(obj)
            run('compile-library-'+str(index).zfill(2),[*common,'-include',linux(native/'vorbis_xiph_alloc_inject.h'),'-c',linux(generated/unit['compiled']),'-o',linux(obj)])
        for stem in('alloc','arena','books','bits','residue','headers','dsp','host'):
            obj=out/'objects'/('fixture-'+stem+'.o');objects.append(obj)
            run('compile-fixture-'+stem,[*common,'-Wall','-Wextra','-Werror','-c',linux(native/('vorbis_xiph_'+stem+'.c')),'-o',linux(obj)])
        binary=out/'resource-tests';run('link',['gcc','-fsanitize=address,undefined','-fno-sanitize-recover=all','-no-pie','-Wl,--gc-sections',*[linux(p)for p in objects],'-lm','-o',linux(binary)])
        output=out/'pcm.bin';text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',linux(binary),linux(output)])
        result=re.fullmatch(r'RESOURCE_CHECKS arena=11 books=(200864) bits=(124754) residue=(3997) headers=(1598) dsp=([1-9][0-9]*) live=0\s+RESOURCE_PASS arena=11 books=\1 cases=31 packets=434 pcm_bytes=738560 live=0\s*',text);need(result is not None,'complete asserted resource and raw corpus result')
        data=output.read_bytes();need(data[:8]==b'XIPHRES1','complete binary capture signature');at=8
        def u32():
            nonlocal at
            need(at+4<=len(data),'whole capture field');value=struct.unpack_from('<I',data,at)[0];at+=4;return value
        need(u32()==31,'all original cases');measurements=[];targets={};total=packets=0
        for index,case in enumerate(model['cases']):
            need([u32()for _ in range(4)]==[index,case['rate'],case['channels'],14],'actual original format/packet identity');parts=[]
            for p,frames in enumerate(case['frames']):
                need([u32()for _ in range(3)]==[p,frames,frames*4],'whole original packet count');body=data[at:at+frames*4];at+=frames*4;need(len(body)==frames*4,'every original PCM packet byte');parts.append(body);packets+=1
            actual=b''.join(parts);reference=references[case['id']];need(len(actual)==len(reference)==case['pcm_bytes'],'whole unshifted S16 comparison')
            aa=struct.unpack('<'+'h'*(len(actual)//2),actual);bb=struct.unpack('<'+'h'*(len(reference)//2),reference);maximum=max((abs(a-b)for a,b in zip(aa,bb)),default=0)
            measurements.append(dict(id=case['id'],max_abs_error=maximum,pcm_bytes=len(actual),sha256=sha(actual)));targets[case['id']]=actual;total+=len(actual)
        need(at==len(data)and total==738560 and packets==434,'full capture without extra/missing bytes')
        report.update(measurement_completed=True,cases=31,packets=packets,pcm_bytes=total,
                      measurements=measurements,max_abs_error=max(r['max_abs_error']for r in measurements))
        save()
        need(all(r['max_abs_error']<=2 for r in measurements),'unchanged fixed2-S16 bound')
        for relation in model['relations']:
            names=relation['cases'];equal=all(targets[n]==targets[names[0]]for n in names[1:]);need(equal==(relation['kind']=='equal'),'all14 original exact relations')
        need(all(sha(Path(path).read_bytes())==pin['sha256']==sha((out/pin['snapshot']).read_bytes())for path,pin in ledger.items()),'all original/frozen inputs unchanged')
        report.update(completed=True,passed=True,arena_scenarios=11,book_assertions=int(result[1]),bitreader_assertions=int(result[2]),residue_scenarios=int(result[3]),header_scenarios=int(result[4]),dsp_scenarios=int(result[5]),relations=14,binary_sha256=sha(binary.read_bytes()),capture_sha256=sha(data));save();print(json.dumps({k:report[k]for k in('completed','passed','arena_scenarios','book_assertions','bitreader_assertions','residue_scenarios','header_scenarios','dsp_scenarios','cases','packets','pcm_bytes','max_abs_error')}));return 0
    except BaseException as error:report.update(completed=report.get('measurement_completed',False),passed=False,error=repr(error));save();raise

if __name__=='__main__':raise SystemExit(main())
