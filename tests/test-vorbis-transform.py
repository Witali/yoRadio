"""Exact binary64 boundary and independent normwise IMDCT qualification.

The production transform reuses Xiph; this oracle uses a zero-padded complex
DFT with different phase placement, plus independent Decimal cosine anchors.
The predeclared absolute bound is5e-12*L1(rounded input). It is not a relative
error guarantee near cancellation, a final PCM bound, or a native resource gate.
"""
import argparse, ast, cmath, functools, hashlib, importlib.util, io, json, math, os
from pathlib import Path
import re, struct, subprocess, sys, time, uuid, zipfile
from decimal import Decimal, localcontext
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ('native_vorbis_numeric','native_vorbis_packet_frame',
              'native_vorbis_floor1_product','native_vorbis_transform')
NORM_BOUND = 5e-12
ANCHOR_BOUND = 5e-13
PRIOR_SHA = '3b74cc7425b315997011040b6b6a8924b908cdff0404e0d0601cbb81a68a93ea'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(body):
    return hashlib.sha256(body).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def linux(path):
    value = Path(path).resolve().as_posix()
    return '/mnt/' + value[0].lower() + value[2:] if sys.platform == 'win32' else value


def float_bits(value):
    return struct.unpack('<Q',struct.pack('<d',value))[0]


def rounded(value):
    # CPython's rational conversion rounds the quotient directly, ties to even;
    # it never first casts a1151-bit integer to an overflowing double.
    return float(Fraction(value,1 << 512))


def synthetic_cases():
    rows = []
    edges = {1,31,32,33,52,53,54,55,63,64,65,1079,1134,1151}
    for width in range(1,1152):
        maximum = (1 << width)-1
        values = [0,1,-1,maximum,-maximum,1 << (width-1),-(1 << (width-1))]
        if width >= 55:
            shift = width-53
            for parity in (0,1):
                tie = ((1 << 52)+parity) * (1 << shift) + (1 << (shift-1))
                values.extend([tie-1,tie,tie+1,-tie-1,-tie,-tie+1])
        rows.append(dict(id=f'convert-width-{width:04}',kind=0,n=0,width=width,
                         exponent=(-(1 << 31),(1 << 31)-1,-835,291,0)[width%5],
                         values=values,controls=width in edges))
    for width in sorted(edges):
        for sign in (-1,1):
            rows.append(dict(id=f'convert-invalid-{width}-{sign}',kind=0,n=0,width=width,
                             exponent=0,values=[1,-1,sign*(1 << width)],controls=False))
    for bins in (1,32,4096):
        rows.append(dict(id=f'convert-zero-{bins}',kind=0,n=0,width=0,exponent=0,
                         values=[0]*bins,controls=True))
    for n in (64,128,256,512,1024,2048,4096,8192):
        bins = n//2
        rows.append(dict(id=f'imdct-zero-{n}',kind=1,n=n,width=0,exponent=0,
                         values=[0]*bins,controls=True))
        for bin_index in sorted({0,1,bins//2,bins-1}):
            for sign in (-1,1):
                values = [0]*bins
                values[bin_index] = sign
                rows.append(dict(id=f'impulse-{n}-{bin_index}-{sign}',kind=1,n=n,width=1,
                                 exponent=0,values=values,controls=False))
        for width in (1134,1151):
            values = [0]*bins
            values[-1] = (1 << width)-1
            rows.append(dict(id=f'wide-impulse-{n}-{width}',kind=1,n=n,width=width,
                             exponent=-(1 << 31),values=values,controls=False))
        maximum=(1 << 1151)-1
        rows.append(dict(id=f'alternating-{n}',kind=1,n=n,width=1151,
                         exponent=(1 << 31)-1,values=[maximum if i&1 else -maximum for i in range(bins)],controls=True))
        for width in (53,120):
            mask=(1 << width)-1
            values=[(((i+1)*0x9e3779b97f4a7c15*0x100000001b3+0x123456789abcdef)&mask)*(-1 if i%3==0 else 1)
                    for i in range(bins)]
            rows.append(dict(id=f'dense-{n}-{width}',kind=1,n=n,width=width,exponent=-788,
                             values=values,controls=width==53))
        values=[1]*bins
        values[n//8]=(1 << 1079)-1
        values[n//8+1]=-values[n//8]
        rows.append(dict(id=f'cancel-span-{n}',kind=1,n=n,width=1079,exponent=-788,
                         values=values,controls=False))
        for exponent in (-(1 << 31),(1 << 31)-1):
            values=[0]*bins;values[0]=(1 << 63)+1
            rows.append(dict(id=f'exponent-{n}-{exponent}',kind=1,n=n,width=64,
                             exponent=exponent,values=values,controls=False))
        for sign in (-1,1):
            values=[0]*bins;values[-1]=sign*(1 << 1151)
            rows.append(dict(id=f'imdct-invalid-{n}-{sign}',kind=1,n=n,width=1151,
                             exponent=0,values=values,controls=False))
    return rows


def packet_cases(model, expected):
    rows=[]
    for case,frame_row in zip(model['cases'],expected):
        if not frame_row['frame']:
            continue
        for channel,product in enumerate(frame_row['products']):
            if product['product_status']:
                continue
            shape=product['layout'];limbs=shape['limbs'];values=[]
            for index in range(shape['bins']):
                words=product['samples'][index*limbs:(index+1)*limbs]
                value=sum(word << (32*i) for i,word in enumerate(words))
                if words and words[-1]&0x80000000:
                    value-=1 << (limbs*32)
                values.append(value)
            rows.append(dict(id='packet-'+case['id']+'-ch'+str(channel),kind=1,n=2*shape['bins'],
                             width=shape['magnitude_bits'],exponent=shape['exponent'],values=values,
                             controls=False,packet=case['id'],original=case['id'].startswith('original31-')))
    need(len(rows)==1750,'all qualified floor1 packet channels retained')
    return rows


def conversion_status(row):
    return -1 if row['width'] and any(abs(value)>=(1 << row['width']) for value in row['values']) else 0


def encode_input(rows):
    result=bytearray(b'VTRANS01'+struct.pack('<I',len(rows)))
    for row in rows:
        width=row['width'];limbs=(width+32)//32 if width else 0
        result.extend(struct.pack('<IIIIIiI',row['kind'],row['n'],len(row['values']),limbs,width,
                                  row['exponent'],int(row['controls'])))
        mask=(1 << (limbs*32))-1
        for value in row['values'] if limbs else ():
            result.extend((value&mask).to_bytes(limbs*4,'little'))
    return bytes(result)


@functools.lru_cache(maxsize=None)
def fft_shape(n):
    width=n.bit_length()-1
    reverse=[int(f'{i:0{width}b}'[::-1],2) for i in range(n)]
    stages=[]
    size=2
    while size<=n:
        stages.append([complex(math.cos(2*math.pi*j/size),math.sin(2*math.pi*j/size)) for j in range(size//2)])
        size*=2
    # Integer phase reduction avoids unnecessary large trigonometric arguments.
    before=[cmath.exp(1j*(math.pi/(2*n)*(((n+2)*k)%(4*n)))) for k in range(n//2)]
    after=[cmath.exp(1j*(math.pi/(4*n)*((4*j+2+n)%(8*n)))) for j in range(n)]
    return reverse,stages,before,after


def imdct_oracle(values):
    n=2*len(values)
    if not any(values):
        return [0.0]*n
    reverse,stages,before,after=fft_shape(n)
    padded=[value*phase for value,phase in zip(values,before)]+[0j]*(n//2)
    transformed=[padded[index] for index in reverse]
    size=2
    for twiddles in stages:
        half=size//2
        for start in range(0,n,size):
            for index,phase in enumerate(twiddles):
                even=transformed[start+index]
                odd=transformed[start+index+half]*phase
                transformed[start+index]=even+odd
                transformed[start+index+half]=even-odd
        size*=2
    return [(value*phase).real for value,phase in zip(transformed,after)]


def decimal_pi():
    def arctan_inverse(divisor):
        x=Decimal(1)/divisor;power=x;result=Decimal(0);k=0
        while True:
            term=power/(2*k+1)
            result=result-term if k&1 else result+term
            if abs(term)<Decimal('1e-95'):
                return result
            power*=x*x;k+=1
    with localcontext() as context:
        context.prec=105
        return +(16*arctan_inverse(Decimal(5))-4*arctan_inverse(Decimal(239)))


def decimal_cos_phase(n,j,k,pi):
    phase=((4*j+2+n)*(2*k+1))%(8*n)
    if phase>4*n:
        phase-=8*n
    x=pi*phase/(4*n);term=Decimal(1);result=term;index=0
    while True:
        index+=1;term*=-(x*x)/((2*index)*(2*index-1));result+=term
        if abs(term)<Decimal('1e-95'):
            return result


def oracle_anchors():
    checks=0;maximum=0.0
    with localcontext() as context:
        context.prec=100
        pi=decimal_pi()
        for n in (64,128,256,512,1024,2048,4096,8192):
            for k in sorted({0,1,n//4,n//2-1}):
                values=[0.0]*(n//2);values[k]=1.0
                result=imdct_oracle(values)
                for j in sorted({0,1,n//4-1,n//4,n//2,n-1}):
                    reference=float(decimal_cos_phase(n,j,k,pi))
                    error=abs(result[j]-reference)
                    need(error<=ANCHOR_BOUND,'independent Decimal impulse anchor')
                    maximum=max(maximum,error);checks+=1
        for n in (64,128):
            values=[(i%11-5)/8 for i in range(n//2)]
            result=imdct_oracle(values);norm=math.fsum(abs(x) for x in values)
            for j in range(n) if n==64 else (0,1,17,63,64,127):
                exact=sum((Decimal.from_float(x)*decimal_cos_phase(n,j,k,pi) for k,x in enumerate(values)),Decimal(0))
                error=abs(result[j]-float(exact))/norm
                need(error<=ANCHOR_BOUND,'independent Decimal dense anchor')
                maximum=max(maximum,error);checks+=1
    # Explicit rational binary64 ties/carry, positive and negative, independent
    # of the production's bit extraction and sticky implementation.
    for sign in (-1,1):
        for shift in (1,31,32,53,512,1098):
            for parity in (0,1):
                q=(1 << 52)+parity
                value=sign*(q*(1 << shift)+(1 << (shift-1)))
                wanted=math.ldexp(float(sign*(q+(parity&1))),shift-512)
                need(float_bits(rounded(value))==float_bits(wanted),'rational ties-to-even anchor');checks+=1
    return dict(checks=checks,maximum_normalized_error=maximum,bound=ANCHOR_BOUND)


def build_expected(rows):
    result=[]
    for row in rows:
        status=conversion_status(row)
        expected=dict(status=status,converted_bits=[],exponent=None,transformed_bits=[],norm1=None)
        if not status:
            values=[rounded(value) for value in row['values']]
            expected.update(converted_bits=[float_bits(value) for value in values],
                            exponent=row['exponent']+512 if row['width'] else 0)
            if row['kind']:
                time_values=imdct_oracle(values)
                expected.update(transformed_bits=[float_bits(value) for value in time_values],
                                norm1=math.fsum(abs(value) for value in values))
        result.append(expected)
    return result


class Reader:
    def __init__(self,body):
        self.body,self.at=body,0
    def take(self,fmt):
        count=struct.calcsize('<'+fmt)
        need(count<=len(self.body)-self.at,'complete capture field')
        values=struct.unpack_from('<'+fmt,self.body,self.at);self.at+=count
        return values[0] if len(values)==1 else values
    def array(self,fmt,count):
        width=struct.calcsize('<'+fmt)
        need(0<=count<=(len(self.body)-self.at)//width,'complete capture array')
        values=list(struct.unpack_from('<'+str(count)+fmt,self.body,self.at));self.at+=count*width
        return values
    def block(self,count):
        need(self.take('I')==count,'complete output extent')
        return dict(exponent=self.take('q'),bits=self.array('Q',count))


def decode_output(body,rows):
    reader=Reader(body)
    need(reader.take('8s')==b'VTROUT01' and reader.take('I')==len(rows) and reader.take('I')==8,'whole ordered transform capture')
    plans=[]
    for n in (64,128,256,512,1024,2048,4096,8192):
        actual,log2n,tc,bc,wc=reader.take('IIQQQ')
        need((actual,log2n,tc,bc,wc)==(n,n.bit_length()-1,n+n//4,n//4,n+8),'all lookup requirements')
        plans.append(dict(n=n,trig_bits=reader.array('Q',tc),bitrev=reader.array('I',bc)))
    observed=[]
    for index,row in enumerate(rows):
        need(reader.take('I')==index and reader.take('I')==row['kind'],'case identity/order')
        status=reader.take('i')
        result=dict(status=status,converted=None,transform_status=None,transformed=None)
        if status==0:
            result['converted']=reader.block(len(row['values']))
        if row['kind']:
            result['transform_status']=reader.take('i')
            if result['transform_status']==0:
                result['transformed']=reader.block(row['n'])
        observed.append(result)
    controls=dict(refusals=reader.take('Q'),checks=reader.take('Q'))
    need(reader.at==len(body),'no missing/extra capture bytes')
    return observed,plans,controls


def compare(rows,expected,observed,plans):
    need(len(rows)==len(expected)==len(observed),'all transform rows')
    maximum=0.0;converted_count=transformed_count=0;invalid=0
    for row,wanted,got in zip(rows,expected,observed):
        need(got['status']==wanted['status'],'conversion status: '+row['id'])
        if row['kind']:
            need(got['transform_status']==wanted['status'],'transform status: '+row['id'])
        if wanted['status']:
            invalid+=1;continue
        need(got['converted']['exponent']==wanted['exponent'] and
             got['converted']['bits']==wanted['converted_bits'],'every exact rounded binary64 bit: '+row['id'])
        converted_count+=len(row['values'])
        if row['kind']:
            need(got['transformed']['exponent']==wanted['exponent'],'retained transform exponent')
            reference=struct.unpack('<'+str(row['n'])+'d',struct.pack('<'+str(row['n'])+'Q',*wanted['transformed_bits']))
            actual=struct.unpack('<'+str(row['n'])+'d',struct.pack('<'+str(row['n'])+'Q',*got['transformed']['bits']))
            norm=wanted['norm1']
            for value,ref in zip(actual,reference):
                need(math.isfinite(value),'finite transform output')
                error=abs(value-ref)
                need(error<=NORM_BOUND*norm,'fixed normwise transform bound: '+row['id'])
                if norm:
                    maximum=max(maximum,error/norm)
                elif not row['width']:
                    # Only the implicit-zero grid promises canonical +0.
                    # Ordinary Xiph arithmetic may produce -0 from an explicit
                    # all-zero nonzero-width spectrum; its numerical error is0.
                    need(float_bits(value)==0,'canonical positive zero block')
            transformed_count+=row['n']
    lookup_values=0
    for plan in plans:
        n=plan['n'];expected_trig=[0.0]*(n+n//4)
        for i in range(n//4):
            expected_trig[2*i]=math.cos((math.pi/n)*(4*i))
            expected_trig[2*i+1]=-math.sin((math.pi/n)*(4*i))
            expected_trig[n//2+2*i]=math.cos((math.pi/(2*n))*(2*i+1))
            expected_trig[n//2+2*i+1]=math.sin((math.pi/(2*n))*(2*i+1))
        for i in range(n//8):
            expected_trig[n+2*i]=math.cos((math.pi/n)*(4*i+2))*.5
            expected_trig[n+2*i+1]=-math.sin((math.pi/n)*(4*i+2))*.5
        actual=struct.unpack('<'+str(len(expected_trig))+'d',struct.pack('<'+str(len(expected_trig))+'Q',*plan['trig_bits']))
        need(all(math.isfinite(x) and abs(x-y)<=2e-15 for x,y in zip(actual,expected_trig)),'all lookup coefficients')
        bits=n.bit_length()-2;mask=n//2-1;reverse=[]
        for i in range(n//8):
            acc=int(f'{i:0{bits}b}'[::-1],2)
            reverse.extend([((~acc)&mask)-1,acc])
        need(reverse==plan['bitrev'],'all independent bitreverse entries')
        lookup_values+=len(actual)+len(reverse)
    return dict(passed=True,cases=len(rows),conversion_values=converted_count,transformed_values=transformed_count,
                invalid_rows=invalid,magnitude_widths=1151,block_sizes=8,lookup_values=lookup_values,
                maximum_normalized_error=maximum,normwise_bound=NORM_BOUND,
                packet_channels=sum('packet' in row for row in rows),
                original_packet_channels=sum(row.get('original',False) for row in rows),
                original_packets_represented=len({row['packet'] for row in rows if row.get('original')}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--prepare-only',action='store_true')
    args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and out!=ROOT/'.build' and not out.exists(),'fresh task-local output')
    out.mkdir(parents=True);(out/'objects').mkdir()
    inputs={}
    report=dict(completed=False,passed=False,inputs=inputs,commands=[],sanitizers=['address','undefined'],
                scope='Binary64 conversion and reused Xiph IMDCT only; no floor0/window/overlap/PCM.',
                target_executed=False,production_radio_integration=False,deferred_scopes_resumed=False,
                floor0_gain_executed=False,PCM_executed=False)
    def save():
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze_body(body,name,label):
        target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
        inputs[label]=dict(sha256=sha(body),snapshot=target.relative_to(out).as_posix());return body
    def freeze(path,name):
        return freeze_body(path.read_bytes(),name,str(path.resolve()))
    def run(name,argv):
        nonce=uuid.uuid4().hex
        request,receipt,stop=(out/(name+suffix) for suffix in ('.request.json','.receipt.json','.stop'))
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=60,
                                          receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command=(['wsl.exe','--exec','python3'] if sys.platform=='win32' else [sys.executable])+[linux(out/'supervisor.py'),linux(request)]
        row=dict(name=name,argv=command,child_argv=list(map(str,argv)),nonce=nonce,request_sha256=sha(request.read_bytes()))
        report['commands'].append(row);save();child,error,started=None,None,time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
                child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                row['transport_pid']=child.pid;child.wait(timeout=80)
        except BaseException as caught:
            error=caught;row['parent_error']=repr(caught)
        finally:
            if child is not None and child.poll() is None:
                stop.write_text(nonce,encoding='ascii')
                try:child.wait(timeout=15)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5);row['forced_transport_stop']=True
            observed=json.loads(receipt.read_text()) if receipt.exists() else {}
            row.update(elapsed_seconds=time.monotonic()-started,supervisor=observed,transport_exit=None if child is None else child.poll())
            for stream in ('stdout','stderr'):
                path=out/(name+'.'+stream+'.log');row[stream+'_sha256']=sha(path.read_bytes()) if path.exists() else None
            save()
        need(error is None and row['transport_exit']==0 and not row.get('forced_transport_stop'),'owned transport terminal: '+name)
        need(observed.get('nonce')==nonce and observed.get('request_sha256')==row['request_sha256'] and
             observed.get('state')=='terminal' and observed.get('final') is True and observed.get('child_reaped') is True and
             observed.get('group_gone') is True and observed.get('new_session') is True and
             observed.get('child_pid')==observed.get('owned_pgid') and observed.get('child_returncode')==0,'owned command terminal: '+name)
        return (out/(name+'.stdout.log')).read_text('utf-8',errors='replace')
    save()
    try:
        freeze(Path(__file__),'runner.py')
        for component in COMPONENTS:
            folder=ROOT/'idf/components'/component
            for path in sorted(folder.rglob('*')):
                if path.is_file():freeze(path,'components/'+component+'/'+path.relative_to(folder).as_posix())
        freeze(ROOT/'tests/native/vorbis_transform_host.c','native/vorbis_transform_host.c')
        generator=freeze(ROOT/'tools/generate-vorbis-imdct64.py','generate-vorbis-imdct64.py')
        upstream=freeze(ROOT/'idf/components/native_vorbis_xiph/upstream/libvorbis/lib/mdct.c','upstream/mdct.c')
        freeze(ROOT/'idf/components/native_vorbis_xiph/upstream/libvorbis/lib/mdct.h','upstream/mdct.h')
        generate=load(out/'sources/generate-vorbis-imdct64.py','frozen_transform_generator')
        need(generate.generated_body(upstream)==(out/'sources/components/native_vorbis_transform/xiph_backward.inc').read_bytes(),
             'all reused inverse-transform bodies unchanged')
        for name in ('test-vorbis-setup.py','test-vorbis-floor-packet.py','test-vorbis-residue.py',
                     'vorbis_packet_frame_model.py','test-vorbis-floor1-frame.py'):
            freeze(ROOT/'tests'/name,name)
        setup=load(out/'sources/test-vorbis-setup.py','transform_setup')
        floor=load(out/'sources/test-vorbis-floor-packet.py','transform_floor')
        residue=load(out/'sources/test-vorbis-residue.py','transform_residue')
        subject=load(out/'sources/vorbis_packet_frame_model.py','transform_model')
        frame=load(out/'sources/test-vorbis-floor1-frame.py','transform_product')
        prior=(ROOT/'tests/results/vorbis-floor1-product-20261026/captures.zip').read_bytes()
        need(sha(prior)==PRIOR_SHA,'pinned previous packet evidence')
        with zipfile.ZipFile(io.BytesIO(prior)) as archive:
            original=freeze_body(archive.read('frame03/sources/original31.json'),'original31.json','archive:prior/frame03/sources/original31.json')
            table=freeze_body(archive.read('frame03/sources/xiph-floor1.c'),'xiph-floor1.c','archive:prior/frame03/sources/xiph-floor1.c')
        model=subject.cases(setup,floor,residue,original)
        need(len(model['cases'])==1311,'complete previous1311 packet rows')
        model['cases'].extend(frame.extra_cases(subject,setup,floor,residue))
        packet_expected=frame.build_expected(model,subject,setup,floor,residue,frame.table_factors(table))
        rows=synthetic_cases()+packet_cases(model,packet_expected)
        anchors=oracle_anchors();expected=build_expected(rows)
        (out/'cases.json').write_text(json.dumps(rows,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
        (out/'expected.json').write_text(json.dumps(expected,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
        (out/'oracle-anchors.json').write_text(json.dumps(anchors,indent=2)+'\n',encoding='utf-8',newline='\n')
        (out/'input.bin').write_bytes(encode_input(rows))
        report.update(prepared=True,cases=len(rows),reference_archive_sha256=PRIOR_SHA,
            original_packet_models=sum(case['id'].startswith('original31-') for case in model['cases']),
            model_sha256=sha((out/'cases.json').read_bytes()),expected_sha256=sha((out/'expected.json').read_bytes()),
            input_sha256=sha((out/'input.bin').read_bytes()),oracle_anchors_sha256=sha((out/'oracle-anchors.json').read_bytes()),
            generator_sha256=sha(generator));save()
        if args.prepare_only:
            print(json.dumps(dict(prepared=True,cases=len(rows),anchors=anchors)));return 0
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py')
        supervisors=[ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node,ast.Assign) and
                     any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(supervisors)==1,'one owned process supervisor')
        (out/'supervisor.py').write_text(supervisors[0],encoding='utf-8',newline='\n');report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes())
        report['compiler_version']=run('compiler-version',['gcc','--version'])
        report['compiler_machine']=run('compiler-machine',['gcc','-dumpmachine'])
        components=out/'sources/components'
        common=['gcc','-std=c11','-O1','-g','-UNDEBUG','-D_GNU_SOURCE=1','-fno-fast-math','-ffp-contract=off',
                '-fno-pie','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer',
                '-ffunction-sections','-fdata-sections','-MMD','-Wall','-Wextra','-Werror',
                *['-I'+linux(components/name/'include') for name in COMPONENTS]]
        units=[components/'native_vorbis_transform/spectrum.c',components/'native_vorbis_transform/transform.c',out/'sources/native/vorbis_transform_host.c']
        objects=[]
        for index,source in enumerate(units):
            obj=out/'objects'/f'{index:02}.o';objects.append(obj)
            run(f'compile-{index:02}',[*common,'-c',linux(source),'-o',linux(obj)])
        binary=out/'transform'
        run('link',['gcc','-fsanitize=address,undefined','-fno-sanitize-recover=all','-no-pie','-Wl,--gc-sections',
                    *[linux(path) for path in objects],'-lm','-o',linux(binary)])
        text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1:allocator_may_return_null=1',
                           'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',linux(binary),linux(out/'input.bin'),linux(out/'capture.bin')])
        match=re.fullmatch(r'TRANSFORM_CAPTURE cases=(\d+) refusals=(\d+) checks=(\d+) live=0 bytes=0\s*',text)
        need(match is not None and not (out/'execute.stderr.log').read_bytes(),'complete guarded transform capture')
        observed,plans,controls=decode_output((out/'capture.bin').read_bytes(),rows)
        need(tuple(map(int,match.groups()))==(len(rows),controls['refusals'],controls['checks']),'actual assertion/refusal counts')
        measured=compare(rows,expected,observed,plans)
        (out/'measurement.json').write_text(json.dumps(measured,indent=2)+'\n',encoding='utf-8',newline='\n')
        report.update(measurement_completed=True,measurement_sha256=sha((out/'measurement.json').read_bytes()),
                      capture_sha256=sha((out/'capture.bin').read_bytes()),controls=controls);save()
        for label,pin in inputs.items():
            need(sha((out/pin['snapshot']).read_bytes())==pin['sha256'],'all frozen source bytes unchanged')
            if not label.startswith('archive:'):
                need(sha(Path(label).read_bytes())==pin['sha256'],'all original source bytes unchanged')
        for name,key in (('cases.json','model_sha256'),('expected.json','expected_sha256'),('input.bin','input_sha256'),('oracle-anchors.json','oracle_anchors_sha256')):
            need(sha((out/name).read_bytes())==report[key],'predeclared model/reference unchanged')
        report.update(completed=True,passed=True,binary_sha256=sha(binary.read_bytes()),units=len(units),measurements=measured);save()
        print(json.dumps({key:report[key] for key in ('completed','passed','cases','original_packet_models','controls','measurements')}));return 0
    except BaseException as error:
        report.update(error=repr(error));save();raise


if __name__=='__main__':
    raise SystemExit(main())
