"""Stateful overlap qualification against full-window/scatter geometry.

The output is two already-rounded binary64 terms with independent exponents.
Window-product underflow is measured explicitly; this is not full-range PCM.
"""
import argparse, ast, hashlib, importlib.util, json, math, os, re, struct, subprocess, sys, time, uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COMPONENTS=('native_vorbis_numeric','native_vorbis_packet_frame','native_vorbis_floor1_product',
            'native_vorbis_transform','native_vorbis_window','native_vorbis_overlap')
WINDOW_SHA='c2fbcc21f1236b2c4b95d7e4f77a5498d4eb427fb2ec5ec5777c0447b0ed69d9'
BOUND=2e-15
SEQUENCE=(0,0,1,1,0,1,0,0)
EXPONENTS=(-(1<<63),(1<<63)-1,(1<<63)-1,(1<<63)-1,1074,1074,-788,512)


def need(test,message):
    if not test:raise ValueError(message)


def sha(body):return hashlib.sha256(body).hexdigest()
def bits(value):return struct.pack('<d',value)
def linux(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def reference():
    path=ROOT/'tests/test-vorbis-window.py';need(sha(path.read_bytes())==WINDOW_SHA,'pinned Decimal window oracle')
    return load(path,'overlap_window_reference')


def sample(pattern,step,i,n,actual_coefficients):
    if pattern==1:
        if step==2 and i>=n//2:return actual_coefficients[n][i-n//2]
        if step==3 and i<n//2:return -actual_coefficients[n][n//2-i-1]
        return ((i*37+step*19)%257-128)/128
    if pattern==2:return 0.0 if step&1 else ((i*37+step*19)%257-128)/128
    v=i+step*17
    choices=(sys.float_info.max,-sys.float_info.max,math.ulp(0.0),-math.ulp(0.0),
             0.0,-0.0,float.fromhex('0x1p-1000'),-float.fromhex('0x1p800'),1.0,-1.0)
    return choices[v%12] if v%12<10 else (v%1021-510)*.03125


def full_window(n,preceding,following,coefficients):
    # Construct and scatter a complete window, independently of production's
    # three overlap branches and its stored-right-half indexing.
    p,q=min(n,preceding),min(n,following)
    out=[1.0]*n
    left=n//4-p//4;right=3*n//4-q//4
    out[:left]=[0.0]*left
    out[left:left+p//2]=coefficients[p]
    out[right:right+q//2]=coefficients[q][::-1]
    out[right+q//2:]=[0.0]*(n-right-q//2)
    return out


def inspect_capture(body,oracle=None):
    oracle=oracle or reference();offset=0
    def raw(count):
        nonlocal offset
        need(count<=len(body)-offset,'complete capture field')
        value=body[offset:offset+count];offset+=count;return value
    def u32():return struct.unpack('<I',raw(4))[0]
    def values(count):return struct.unpack('<'+str(count)+'d',raw(8*count))
    need(raw(8)==b'VOVERL01' and u32()==8,'overlap capture header')
    actual_coefficients={};coefficients={};coefficient_count=0;coefficient_error=0.0
    for n in (64,128,256,512,1024,2048,4096,8192):
        need(u32()==n,'all configured lookup sizes')
        actual=values(n//2);wanted=oracle.coefficients(n);actual_coefficients[n]=actual;coefficients[n]=wanted
        for a,b in zip(actual,wanted):
            need(math.isfinite(a) and 0<a<=1 and abs(a-b)<=BOUND,'independent Decimal window coefficient')
            coefficient_error=max(coefficient_error,abs(a-b));coefficient_count+=1
    need(u32()==864,'complete sequence corpus')
    blocks=emitted=priming=terms=history_values=cancellation_values=zero_current=0
    exact_plateau=exact_support=underflow=scaled_underflow=0;normal_error=subnormal_error=0.0
    transitions=set()
    for small in range(8):
        for large in range(small,8):
            s,l=64<<small,64<<large
            for pattern in range(3):
                previous=None;previous_exponent=0
                for step in range(8):
                    if step==4:previous=None;previous_exponent=0
                    n=l if SEQUENCE[step] else s;a=len(previous) if previous is not None else 0
                    count=(a+n)//4 if a else 0
                    need(tuple(u32() for _ in range(7))==(s,l,pattern,step,a,n,count),'complete ordered row identity')
                    ep,ec=struct.unpack('<qq',raw(16))
                    need((ep,ec)==(previous_exponent,EXPONENTS[step]),'independent retained exponents')
                    source,got_previous,got_current,history=values(n),values(count),values(count),values(n//2)
                    need(tuple(bits(v) for v in source)==tuple(bits(sample(pattern,step,i,n,actual_coefficients)) for i in range(n)),
                         'every declared source bit')
                    need(tuple(bits(v) for v in history)==tuple(bits(v) for v in source[n//2:]),'exact retained unwindowed history')
                    history_values+=len(history)
                    if not a:priming+=1
                    else:
                        emitted+=1;transitions.add((a==l,n==l) if s!=l else ('equal','equal'))
                        window_previous=full_window(a,a,n,coefficients)
                        window_current=full_window(n,a,n,coefficients)
                        for t in range(count):
                            indices=(a//2+t,t+(n-a)//4)
                            for actual,block,window,index,exponent in (
                                (got_previous[t],previous,window_previous,indices[0],ep),
                                (got_current[t],source,window_current,indices[1],ec)):
                                factor=window[index] if 0<=index<len(window) else 0.0
                                operand=block[index] if 0<=index<len(block) else 0.0
                                expected=operand*factor if factor else 0.0
                                need(math.isfinite(actual),'finite contribution')
                                if not factor:
                                    need(bits(actual)==bytes(8),'canonical zero outside full-window support');exact_support+=1
                                elif factor==1:
                                    need(bits(actual)==bits(operand),'exact plateau');exact_plateau+=1
                                elif operand==0:
                                    need(bits(actual)==bits(operand),'signed zero under positive slope')
                                error=abs(actual-expected)
                                need(error<=BOUND*abs(operand)+4*math.ulp(0.0),'fixed contribution error bound')
                                if operand:
                                    if abs(operand)<sys.float_info.min:subnormal_error=max(subnormal_error,error/abs(operand))
                                    else:normal_error=max(normal_error,error/abs(operand))
                                if operand and factor and actual==0:
                                    underflow+=1
                                    if exponent>=1074:scaled_underflow+=1
                                terms+=1
                        if pattern==1 and step==3:
                            need(ep==ec==(1<<63)-1,'extreme scale cancellation case')
                            need(all(struct.unpack('<Q',bits(p))[0]==(struct.unpack('<Q',bits(q))[0]^(1<<63))
                                     for p,q in zip(got_previous,got_current)),'every cancellation term retained')
                            cancellation_values+=count
                        if pattern==2 and step&1:
                            need(all(v==0 for v in got_current) and any(v!=0 for v in got_previous),'absent current preserves prior tail')
                            zero_current+=1
                    blocks+=1;previous=source;previous_exponent=ec
    need(offset==len(body),'no trailing or missing capture bytes')
    need(underflow>0 and scaled_underflow>0,'retained explicit window-product underflow witnesses')
    need({(False,False),(False,True),(True,False),(True,True)}<=transitions,'all four unequal-size transitions')
    return dict(passed=True,blocks=blocks,emitting_blocks=emitted,priming_blocks=priming,
        configurations=36,patterns=3,steps=8,reset_count=108,coefficient_count=coefficient_count,
        coefficient_error=coefficient_error,contribution_values=terms,history_values=history_values,
        cancellation_values=cancellation_values,absent_current_rows=zero_current,
        exact_plateau_values=exact_plateau,exact_support_values=exact_support,
        nonzero_operands_rounded_to_zero=underflow,underflow_terms_with_exponent_at_least1074=scaled_underflow,
        maximum_normal_operand_error=normal_error,maximum_subnormal_operand_error=subnormal_error,
        coefficient_bound=BOUND,absolute_underflow_bound='4*DBL_TRUE_MIN',
        full_range_PCM_qualified=False)


def corruption_controls(body,oracle=None):
    oracle=oracle or reference();first=16+sum(4+4*n for n in (64,128,256,512,1024,2048,4096,8192))
    active=first+44+64*8+32*8
    changes=[('header',0,b'X'),('coefficient',16,struct.pack('<d',math.nan)),
        ('identity',first+20,struct.pack('<I',63)),('exponent',first+36,bytes(8)),
        ('source',first+44,bytes(8)),('previous',active+44+64*8,struct.pack('<d',math.nan)),
        ('current',active+44+64*8+32*8,struct.pack('<d',math.nan)),
        ('history',first+44+64*8,struct.pack('<d',math.nan))]
    cases=[(name,body[:offset]+value+body[offset+len(value):]) for name,offset,value in changes]
    cases.extend([('truncated',body[:-1]),('trailing',body+b'X')])
    for name,bad in cases:
        try:inspect_capture(bad,oracle)
        except (ValueError,struct.error):continue
        raise ValueError('damaged capture accepted: '+name)
    return [name for name,_ in cases]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--verify-capture',type=Path);args=parser.parse_args()
    if args.verify_capture:
        body=args.verify_capture.read_bytes();oracle=reference();result=inspect_capture(body,oracle)
        result['corruption_controls']=corruption_controls(body,oracle)
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result));return 0
    out=args.output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh local output');out.mkdir(parents=True)
    report=dict(completed=False,passed=False,commands=[],sources={},sanitizers=['address','undefined'],
        native_executed=False,production_selected=False,PCM_executed=False,full_range_PCM_qualified=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,label):
        body=path.read_bytes();target=out/'sources'/label;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
        report['sources'][label]=sha(body);return body
    def run(name,argv):
        nonce=uuid.uuid4().hex;request,receipt,stop=(out/(name+x) for x in ('.request.json','.receipt.json','.stop'))
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=60,receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command=(['wsl.exe','--exec','python3'] if os.name=='nt' else [sys.executable])+[linux(out/'supervisor.py'),linux(request)]
        row=dict(name=name,nonce=nonce,argv=command,child_argv=list(map(str,argv)),request_sha256=sha(request.read_bytes()))
        report['commands'].append(row);save();child=None;started=time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
                child=subprocess.Popen(command,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                row['transport_pid']=child.pid;child.wait(timeout=80)
        finally:
            if child is not None and child.poll() is None:
                stop.write_text(nonce,encoding='ascii')
                try:child.wait(timeout=15)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5);row['forced_transport_stop']=True
            receipt_body=json.loads(receipt.read_bytes()) if receipt.exists() else {}
            row.update(elapsed_seconds=time.monotonic()-started,supervisor=receipt_body,transport_exit=None if child is None else child.poll());save()
        need(row['transport_exit']==0 and not row.get('forced_transport_stop'),'owned transport terminal: '+name)
        need(receipt_body.get('nonce')==nonce and receipt_body.get('request_sha256')==row['request_sha256'] and
             receipt_body.get('state')=='terminal' and receipt_body.get('final') and receipt_body.get('child_reaped') and
             receipt_body.get('group_gone') and receipt_body.get('new_session') and
             receipt_body.get('child_pid')==receipt_body.get('owned_pgid') and receipt_body.get('child_returncode')==0,'owned command terminal: '+name)
        return (out/(name+'.stdout.log')).read_text(encoding='utf-8')
    save()
    try:
        freeze(Path(__file__),'runner.py')
        for component in COMPONENTS:
            folder=ROOT/'idf/components'/component
            for path in sorted(folder.rglob('*')):
                if path.is_file():freeze(path,'components/'+component+'/'+path.relative_to(folder).as_posix())
        freeze(ROOT/'tests/native/vorbis_overlap_host.c','native/vorbis_overlap_host.c')
        helper=freeze(ROOT/'tests/test-vorbis-window.py','window-oracle.py');need(sha(helper)==WINDOW_SHA,'frozen pinned window helper')
        oracle=load(out/'sources/window-oracle.py','frozen_overlap_window')
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py')
        supervisors=[ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node,ast.Assign) and
            any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(supervisors)==1,'one owned supervisor');(out/'supervisor.py').write_text(supervisors[0],encoding='utf-8',newline='\n')
        report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes());save()
        report['compiler_version']=run('compiler-version',['gcc','--version'])
        common=['gcc','-std=c11','-O1','-g','-UNDEBUG','-fno-fast-math','-ffp-contract=off','-fno-pie',
            '-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-Wall','-Wextra','-Werror',
            *['-I'+linux(out/'sources/components'/name/'include') for name in COMPONENTS]]
        run('compile',[*common,linux(out/'sources/components/native_vorbis_window/window.c'),
            linux(out/'sources/components/native_vorbis_overlap/overlap.c'),linux(out/'sources/native/vorbis_overlap_host.c'),
            '-no-pie','-lm','-o',linux(out/'overlap')])
        text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',
            linux(out/'overlap'),linux(out/'capture.bin')])
        match=re.fullmatch(r'OVERLAP_CAPTURE cases=(\d+) refusals=(\d+) checks=(\d+) cancellations=(\d+) resets=(\d+)\s*',text)
        need(match is not None and not (out/'execute.stderr.log').read_bytes(),'guarded capture without diagnostics')
        controls=dict(zip(('cases','refusals','checks','cancellations','resets'),map(int,match.groups())))
        measurement=inspect_capture((out/'capture.bin').read_bytes(),oracle)
        need(controls['cases']==measurement['blocks'] and controls['cancellations']==measurement['cancellation_values'] and
             controls['resets']==measurement['reset_count'],'actual fixture counters match capture')
        damaged=corruption_controls((out/'capture.bin').read_bytes(),oracle)
        for name,digest in report['sources'].items():need(sha((out/'sources'/name).read_bytes())==digest,'frozen sources unchanged')
        report.update(completed=True,passed=True,controls=controls,measurements=measurement,corruption_controls=damaged,
            capture_sha256=sha((out/'capture.bin').read_bytes()),binary_sha256=sha((out/'overlap').read_bytes()))
        save();print(json.dumps({name:report[name] for name in ('completed','passed','controls','measurements')}));return 0
    except BaseException as error:report['error']=repr(error);save();raise


if __name__=='__main__':raise SystemExit(main())
