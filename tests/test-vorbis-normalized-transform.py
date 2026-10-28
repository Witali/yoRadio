"""Guarded binary64 IMDCT entry; exact old-route parity and FFT comparison.

The unchanged Xiph kernel is shared. This checks a new representation entry,
not floor0 gain policy, window/overlap, PCM or production/native integration.
The normwise bound is 5e-12*L1(input)+32*n*DBL_TRUE_MIN; the absolute term
accounts for arithmetic underflow when callers supply subnormal spectra.
"""
import argparse, ast, hashlib, importlib.util, json, math, os
from pathlib import Path
import re, struct, subprocess, sys, time, uuid
from fractions import Fraction

ROOT=Path(__file__).resolve().parents[1]
COMPONENTS=('native_vorbis_numeric','native_vorbis_packet_frame',
            'native_vorbis_floor1_product','native_vorbis_transform')
BOUND=5e-12
SELECTED=(1,31,32,33,52,53,54,55,63,64,65,1079,1134,1151)
EXPONENTS=(-(1<<63),(1<<63)-1,-788,0,512)

def need(value,message):
    if not value: raise ValueError(message)

def sha(body): return hashlib.sha256(body).hexdigest()
def linux(path):
    name=Path(path).resolve().as_posix()
    return '/mnt/'+name[0].lower()+name[2:] if sys.platform=='win32' else name

def bits(value): return struct.unpack('<Q',struct.pack('<d',value))[0]

def expected_rows():
    for shift in range(8):
        n=64<<shift
        for width in range(1,1152) if shift==0 else SELECTED:
            raw=[]
            for i in range(n//2):
                absolute=((1<<width)-1,1,1<<(width-1),0)[i%4]
                raw.append(-absolute if i%8&4 else absolute)
            yield dict(n=n,kind=0,index=width,exponent=(-(1<<31) if width&1 else (1<<31)-1)+512,
                       values=[float(Fraction(value,1<<512)) for value in raw])
        for pattern in range(12):
            values=[]
            for i in range(n//2):
                sign=-1.0 if i&1 else 1.0
                value=(sign*0.0,sign*2.0**639,2.0**639 if i==n//2-1 else 0.0,
                       sign*2.0**-1074,sign*sys.float_info.min,
                       2.0**639 if i==0 else sign*2.0**-1074,
                       (i%11-5)/8,sign*math.nextafter(2.0**639,0.0),
                       2.0**-1074 if i==0 else 0.0,sign*2.0**-512,
                       -0.0 if i==0 else 0.0,sign*(1+(i%31)/64))[pattern]
                values.append(value)
            for exponent in EXPONENTS:
                yield dict(n=n,kind=1,index=pattern,exponent=exponent,values=values)

def compare(body,oracle):
    need(body[:8]==b'VNORM001','complete capture magic');offset=8
    cases=values_count=matched=zero_blocks=subnormal_rows=0;maximum=normal_maximum=subnormal_maximum=0.0
    for row in expected_rows():
        n=row['n'];bins=n//2
        need(offset+20+(bins+n)*8<=len(body),'complete capture row')
        got_n,kind,index,exponent=struct.unpack_from('<IIIq',body,offset);offset+=20
        need((got_n,kind,index,exponent)==(n,row['kind'],row['index'],row['exponent']),'ordered row identity/exponent')
        source_bits=struct.unpack_from('<'+str(bins)+'Q',body,offset);offset+=bins*8
        need(source_bits==tuple(bits(x) for x in row['values']),'independent exact source bits')
        actual=struct.unpack_from('<'+str(n)+'d',body,offset);offset+=n*8
        need(all(math.isfinite(value) for value in actual),'all output values finite')
        largest=max(abs(x) for x in row['values'])
        if not largest:
            need(all(bits(value)==0 for value in actual),'specified canonical positive-zero output')
            zero_blocks+=1
        else:
            # Compare in a safe scale without discarding the original kernel's
            # underflow allowance. Tiny terms beside a huge term remain below
            # the fixed normwise bound, not a claimed relative-bin guarantee.
            scale=math.frexp(largest)[1]
            normalized=[math.ldexp(value,-scale) for value in row['values']]
            reference=oracle.imdct_oracle(normalized)
            norm=math.fsum(abs(value) for value in normalized)
            allowance=BOUND*norm+math.ldexp(32.0*n,-1074-scale)
            for value,expected in zip(actual,reference):
                error=abs(math.ldexp(value,-scale)-expected)
                need(error<=allowance,'fixed FFT normwise/absolute bound')
                maximum=max(maximum,error/norm)
                if scale < -1021: subnormal_maximum=max(subnormal_maximum,error/norm)
                else: normal_maximum=max(normal_maximum,error/norm)
            subnormal_rows+=scale < -1021
        if row['kind']==0: matched+=n
        cases+=1;values_count+=n
    need(offset==len(body),'no trailing/unread capture bytes')
    return dict(passed=True,cases=cases,time_values=values_count,old_route_bit_values=matched,
                zero_blocks=zero_blocks,subnormal_rows=subnormal_rows,block_sizes=8,
                exponent_endpoints=[-(1<<63),(1<<63)-1],normwise_bound=BOUND,
                underflow_absolute_term='32*n*DBL_TRUE_MIN',maximum_normalized_error=maximum,
                maximum_normal_input_error=normal_maximum,maximum_subnormal_input_error=subnormal_maximum)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out!=ROOT/'.build' and not out.exists(),'fresh task-local output')
    out.mkdir(parents=True);(out/'objects').mkdir()
    report=dict(completed=False,passed=False,commands=[],inputs={},
                sanitizers=['address','undefined'],target_executed=False,
                production_integration=False,floor0_gain_executed=False,
                deferred_scopes_resumed=False)
    def save():
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,name):
        target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True)
        body=path.read_bytes();target.write_bytes(body)
        report['inputs'][path.relative_to(ROOT).as_posix()]=dict(sha256=sha(body),snapshot=target.relative_to(out).as_posix())
        return body
    def run(name,argv):
        nonce=uuid.uuid4().hex
        request,receipt,stop=(out/(name+suffix) for suffix in ('.request.json','.receipt.json','.stop'))
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=60,
            receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command=(['wsl.exe','--exec','python3'] if sys.platform=='win32' else [sys.executable])+[linux(out/'supervisor.py'),linux(request)]
        row=dict(name=name,argv=command,child_argv=list(map(str,argv)),nonce=nonce,request_sha256=sha(request.read_bytes()))
        report['commands'].append(row);save();child=error=None;started=time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
                child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                row['transport_pid']=child.pid;child.wait(timeout=80)
        except BaseException as caught:
            error=caught;row['parent_error_type']=type(caught).__name__
        finally:
            if child is not None and child.poll() is None:
                stop.write_text(nonce,encoding='ascii')
                try: child.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    child.kill();child.wait(timeout=5);row['forced_transport_stop']=True
            observed=json.loads(receipt.read_text()) if receipt.exists() else {}
            row.update(elapsed_seconds=time.monotonic()-started,supervisor=observed,
                       transport_exit=None if child is None else child.poll())
            for stream in ('stdout','stderr'):
                path=out/(name+'.'+stream+'.log')
                row[stream+'_sha256']=sha(path.read_bytes()) if path.exists() else None
            save()
        need(error is None and row['transport_exit']==0 and not row.get('forced_transport_stop'),'owned transport terminal: '+name)
        need(observed.get('nonce')==nonce and observed.get('request_sha256')==row['request_sha256'] and
             observed.get('state')=='terminal' and observed.get('final') is True and observed.get('child_reaped') is True and
             observed.get('group_gone') is True and observed.get('new_session') is True and
             observed.get('child_pid')==observed.get('owned_pgid') and observed.get('child_returncode')==0,
             'owned command terminal: '+name)
        return (out/(name+'.stdout.log')).read_text('utf-8',errors='replace')
    save()
    try:
        freeze(Path(__file__),'runner.py')
        for name in COMPONENTS:
            folder=ROOT/'idf/components'/name
            for path in sorted(folder.rglob('*')):
                if path.is_file(): freeze(path,'components/'+name+'/'+path.relative_to(folder).as_posix())
        freeze(ROOT/'tests/native/vorbis_normalized_transform_host.c','native/vorbis_normalized_transform_host.c')
        freeze(ROOT/'tests/test-vorbis-transform.py','oracle.py')
        spec=importlib.util.spec_from_file_location('normalized_transform_oracle',out/'sources/oracle.py')
        oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)
        report['anchors']=oracle.oracle_anchors();save()
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py')
        values=[ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node,ast.Assign) and
                any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(values)==1,'one owned-process supervisor')
        (out/'supervisor.py').write_text(values[0],encoding='utf-8',newline='\n')
        report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes())
        report['compiler_version']=run('compiler-version',['gcc','--version'])
        report['compiler_machine']=run('compiler-machine',['gcc','-dumpmachine'])
        components=out/'sources/components'
        common=['gcc','-std=c11','-O1','-g','-UNDEBUG','-D_GNU_SOURCE=1','-fno-fast-math','-ffp-contract=off',
                '-fno-pie','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer',
                '-ffunction-sections','-fdata-sections','-MMD','-Wall','-Wextra','-Werror',
                *['-I'+linux(components/name/'include') for name in COMPONENTS]]
        units=[components/'native_vorbis_transform/spectrum.c',components/'native_vorbis_transform/transform.c',
               out/'sources/native/vorbis_normalized_transform_host.c']
        objects=[]
        for index,source in enumerate(units):
            target=out/'objects'/f'{index:02}.o';objects.append(target)
            run(f'compile-{index:02}',[*common,'-c',linux(source),'-o',linux(target)])
        binary=out/'normalized-transform'
        run('link',['gcc','-fsanitize=address,undefined','-fno-sanitize-recover=all','-no-pie','-Wl,--gc-sections',
                    *[linux(path) for path in objects],'-lm','-o',linux(binary)])
        captured=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1',
                              'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',linux(binary),linux(out/'capture.bin')])
        match=re.fullmatch(r'NORMALIZED_CAPTURE cases=(\d+) matched=(\d+) refusals=(\d+) checks=(\d+)\s*',captured)
        need(match is not None and not (out/'execute.stderr.log').read_bytes(),'complete guarded capture without diagnostics')
        controls=dict(zip(('cases','matched','refusals','checks'),map(int,match.groups())))
        measurement=compare((out/'capture.bin').read_bytes(),oracle)
        need(controls['cases']==measurement['cases'] and controls['matched']==measurement['old_route_bit_values'],
             'captured/independent corpus counts')
        need(controls['refusals']==336,'all refusal controls on all eight sizes')
        (out/'measurement.json').write_text(json.dumps(measurement,indent=2)+'\n',encoding='utf-8',newline='\n')
        for name,pin in report['inputs'].items():
            need(sha((ROOT/name).read_bytes())==pin['sha256'] and sha((out/pin['snapshot']).read_bytes())==pin['sha256'],
                 'executed original/frozen sources unchanged')
        report.update(completed=True,passed=True,controls=controls,measurements=measurement,
                      capture_sha256=sha((out/'capture.bin').read_bytes()),binary_sha256=sha(binary.read_bytes()))
        save();print(json.dumps(dict(passed=True,controls=controls,measurements=measurement)));return 0
    except BaseException as error:
        report['error_type']=type(error).__name__;report['error_message']=str(error);save();raise

if __name__=='__main__': raise SystemExit(main())
