"""Exact binary64 window products and views; no overlap or PCM execution.

Retain all saved window-product underflow witnesses as data-only operands.
The independent oracle uses integer ratios and unbounded multiplication.
"""
import argparse,ast,hashlib,importlib.util,io,json,math,os,re,struct,subprocess,sys,time,uuid,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COMPONENTS=('native_vorbis_numeric','native_vorbis_packet_frame','native_vorbis_floor1_product',
    'native_vorbis_transform','native_vorbis_window','native_vorbis_window_exact')
WINDOW_SHA='c2fbcc21f1236b2c4b95d7e4f77a5498d4eb427fb2ec5ec5777c0447b0ed69d9'
PRIOR_SHA='685778be3a8650fd9e1740e2e99b1540b1f2cde7ec33046f96d3e3bde6fd2d23'
PRIOR_MANIFEST_SHA='cba1bd703fb6467828b56db3becd796eaf270f4ecdebf78025f5d3b577c54700'
SIZES=tuple(64<<i for i in range(8))
EXPONENTS=(-(1<<63),(1<<63)-1,(1<<63)-1,(1<<63)-1,1074,1074,-788,512)
SCALES=(-(1<<63),(1<<63)-1,0,-788,512,1074,-1074)
BOUND=2e-15


def need(test,message):
    if not test:raise ValueError(message)
def sha(body):return hashlib.sha256(body).hexdigest()
def bits(value):return struct.unpack('<Q',struct.pack('<d',value))[0]
def value(word):return struct.unpack('<d',struct.pack('<Q',word))[0]
def linux(path):
    result=Path(path).resolve().as_posix()
    return '/mnt/'+result[0].lower()+result[2:] if sys.platform=='win32' else result
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


class Reader:
    def __init__(self,body):self.body=body;self.at=0
    def take(self,fmt):
        count=struct.calcsize('<'+fmt);need(self.at+count<=len(self.body),'complete capture field')
        result=struct.unpack_from('<'+fmt,self.body,self.at);self.at+=count
        return result[0] if len(result)==1 else result
    def doubles(self,count):return tuple(self.take('d') for _ in range(count))


def original_data():
    folder=ROOT/'tests/results/vorbis-overlap-20261028'
    body=(folder/'captures.zip').read_bytes();manifest=(folder/'manifest.json').read_bytes()
    need(sha(body)==PRIOR_SHA and sha(manifest)==PRIOR_MANIFEST_SHA,'pinned saved DATA archive/manifest')
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        capture=z.read('host03/capture.bin');report=z.read('host03/report.json')
    saved=json.loads(report)
    need(saved['passed'] and sha(capture)==saved['capture_sha256'] and
        saved['measurements']['nonzero_operands_rounded_to_zero']==17962 and
        saved['measurements']['underflow_terms_with_exponent_at_least1074']==13767,'original witness provenance')
    return capture,report


def sample(i):
    fixed=(sys.float_info.max,-sys.float_info.max,math.ulp(0.0),-math.ulp(0.0),
        0.0,-0.0,float.fromhex('0x1p-1000'),-float.fromhex('0x1p800'),1.0,-1.0)
    return fixed[i%12] if i%12<10 else (i%1021-510)*.03125


def factor_at(n,previous,following,index,coefficients):
    if not 0<=index<n:return 0.0
    p,q=min(n,previous),min(n,following)
    left=n//4-p//4;right=3*n//4-q//4
    if index<left or index>=right+q//2:return 0.0
    if index<left+p//2:return coefficients[p][index-left]
    if index>=right:return coefficients[q][right+q//2-index-1]
    return 1.0


def saved_witnesses(body):
    r=Reader(body);need(r.take('8s')==b'VOVERL01' and r.take('I')==8,'saved data header')
    coefficients={}
    for n in SIZES:
        need(r.take('I')==n,'all saved coefficient sizes');coefficients[n]=r.doubles(n//2)
        need(all(math.isfinite(v) and 0<v<=1 for v in coefficients[n]),'finite saved factors')
    need(r.take('I')==864,'all saved row identities');rows=[];records=terms=large=0
    for small in range(8):
        for large_index in range(small,8):
            s,l=SIZES[small],SIZES[large_index]
            for pattern in range(3):
                previous=None;previous_exponent=0
                for step,long in enumerate((0,0,1,1,0,1,0,0)):
                    if step==4:previous=None;previous_exponent=0
                    n=l if long else s;a=len(previous) if previous is not None else 0
                    count=(a+n)//4 if a else 0
                    need(r.take('7I')==(s,l,pattern,step,a,n,count),'every original saved configuration/row')
                    ep,ec=r.take('qq');need((ep,ec)==(previous_exponent,EXPONENTS[step]),'saved symbolic scales')
                    source=r.doubles(n);previous_at=r.at;old_previous=r.doubles(count)
                    current_at=r.at;old_current=r.doubles(count);history=r.doubles(n//2)
                    for i,v in enumerate(source):
                        if pattern==1:
                            wanted=coefficients[n][i-n//2] if step==2 and i>=n//2 else (
                                -coefficients[n][n//2-i-1] if step==3 and i<n//2 else ((i*37+step*19)%257-128)/128)
                        elif pattern==2:wanted=0.0 if step&1 else ((i*37+step*19)%257-128)/128
                        else:wanted=sample(i+step*17)
                        need(bits(v)==bits(wanted),'every retained original source bit')
                    need(tuple(map(bits,history))==tuple(map(bits,source[n//2:])),'unwindowed saved history identity')
                    if a:
                        for t in range(count):
                            for side,block,index,e,actual,at,p,q in (
                                ('previous',previous,a//2+t,ep,old_previous[t],previous_at+8*t,a,n),
                                ('current',source,t+(n-a)//4,ec,old_current[t],current_at+8*t,a,n)):
                                size=len(block);factor=factor_at(size,p,q,index,coefficients)
                                operand=block[index] if 0<=index<size else 0.0
                                if operand and factor and actual==0:
                                    need(operand*factor==0,'recorded zero is actual binary64 product underflow')
                                    identity=[s,l,pattern,step,side,t,index,at]
                                    rows.append(dict(id='saved-'+str(len(rows)),sample=bits(operand),factor=bits(factor),
                                        exponent=e,status=0,controls=False,witness=identity,old_output=bits(actual)))
                                    large+=e>=1074
                                terms+=1
                    previous=source;previous_exponent=ec;records+=1
    need(r.at==len(body) and len(rows)==17962 and large==13767,'all original underflow witnesses, without deduplication')
    identities=[row['witness'] for row in rows]
    need(len({tuple(v) for v in identities})==17962,'distinct original witness identities')
    return rows,dict(records=records,terms=terms,witnesses=len(rows),exponents_at_least1074=large,
        identity_sha256=sha(json.dumps(identities,separators=(',',':')).encode()))


def cases(witnesses):
    rows=[]
    def add(label,a,b,controls=False):
        x,y=value(a),value(b);valid=math.isfinite(x) and math.isfinite(y) and 0<=y<=1
        rows.append(dict(id=label,sample=a,factor=b,exponent=SCALES[len(rows)%len(SCALES)],
            status=0 if valid else -2,controls=controls))
    for field in range(2047):
        for fraction in (0,1,(1<<52)-1):
            for sign in (0,1):
                word=(sign<<63)|(field<<52)|fraction
                for factor in (1,0x3fefffffffffffff,0x3ff0000000000000):
                    add(f'sample-field-{field}-{fraction}-{sign}-{factor}',word,factor,field in (0,1,1023,2046))
    for field in range(1024):
        for fraction in ((0,) if field==1023 else (0,1,(1<<52)-1)):
            for word in (1,0x7fefffffffffffff,0xbff0000000000000):
                add(f'factor-field-{field}-{fraction}-{word}',word,(field<<52)|fraction)
    for width in range(1,54):
        for significand in sorted({(1<<(width-1))|1,(1<<width)-1}):
            fraction=(significand<<(53-width))&((1<<52)-1)
            for field in (0,1,1023,2046):
                for sign in (0,1):
                    add(f'width-{width}-{significand}-{field}-{sign}',(sign<<63)|(field<<52)|fraction,
                        (1022<<52)|fraction,True)
    for a in (0,1,0x8000000000000000,0x7fefffffffffffff,0xffefffffffffffff,0x7ff0000000000000,
        0xfff0000000000000,0x7ff8000000000001,0x7ff0000000000001):
        for b in (0,0x8000000000000000,1,0x3ff0000000000000,0x3ff0000000000001,0xbff0000000000000,
            0x8000000000000001,0x7ff0000000000000,0xfff0000000000000,0x7ff8000000000001):
            add(f'domain-{a}-{b}',a,b,True)
    return rows+witnesses


def encode(rows):
    body=bytearray(b'VWXIN001'+struct.pack('<I',len(rows)))
    for row in rows:body.extend(struct.pack('<QQqiI',row['sample'],row['factor'],row['exponent'],row['status'],row['controls']))
    return bytes(body)


def exact(sample_word,factor_word,exponent):
    a,b=value(sample_word).as_integer_ratio();c,d=value(factor_word).as_integer_ratio()
    numerator=a*c
    if not numerator:return (0,0,0,0,0)
    magnitude=abs(numerator);trailing=(magnitude&-magnitude).bit_length()-1
    shift=trailing-(b*d).bit_length()+1;magnitude>>=trailing
    need(magnitude&1 and magnitude.bit_length()<=106 and -2148<=shift<=1023,'independent exact dyadic domain')
    return magnitude&((1<<64)-1),magnitude>>64,exponent,shift,int(numerator<0)


def compare(body,rows,oracle):
    r=Reader(body);need(r.take('8s')==b'VWXOUT01' and r.take('I')==len(rows),'complete scalar capture header')
    nonzero=invalid=witnesses=large=0;maximum_bits=0;shifts=set();sample_fields=set();factor_fields=set();widths=set();factor_widths=set()
    for index,row in enumerate(rows):
        need(r.take('IQQqi')==(index,row['sample'],row['factor'],row['exponent'],row['status']),'all scalar operand and scale identities')
        actual=r.take('QQqiI')
        if row['status']:
            need(actual==(0xa5a5a5a5a5a5a5a5,)*2+(-6510615555426900571,-1515870811,0xa5a5a5a5),'failed scalar sentinel');invalid+=1;continue
        wanted=exact(row['sample'],row['factor'],row['exponent']);need(actual==wanted,'every exact integer-ratio product')
        magnitude=wanted[0]+(wanted[1]<<64)
        if magnitude:
            nonzero+=1;maximum_bits=max(maximum_bits,magnitude.bit_length());shifts.add(wanted[3])
            n,d=value(row['sample']).as_integer_ratio();n=abs(n);widths.add((n//(n&-n)).bit_length())
            n,d=value(row['factor']).as_integer_ratio();factor_widths.add((n//(n&-n)).bit_length())
        sample_fields.add((row['sample']>>52)&2047);factor_fields.add((row['factor']>>52)&2047)
        if 'witness' in row:
            need(magnitude and bits(value(row['old_output'])) in (0,1<<63),'every saved rounded-zero product survives exactly')
            witnesses+=1;large+=row['exponent']>=1074
    need(sample_fields==set(range(2047)) and factor_fields==set(range(1024)) and widths==factor_widths==set(range(1,54)) and
        maximum_bits==106 and min(shifts)==-2148 and max(shifts)==1023,'complete declared scalar range and precision coverage')
    need(witnesses==17962 and large==13767,'all saved underflow witnesses remain nonzero')
    need(r.take('I')==8,'all prepared lookup sizes');coefficients={};max_error=0.0
    for n in SIZES:
        need(r.take('I')==n,'ordered prepared lookup');coefficients[n]=r.doubles(n//2)
        for actual,wanted in zip(coefficients[n],oracle.coefficients(n)):
            need(math.isfinite(actual) and 0<actual<=1 and abs(actual-wanted)<=BOUND,'unchanged high-precision sine bound')
            max_error=max(max_error,abs(actual-wanted))
    need(r.take('I')==288,'complete exact view shape corpus');view_values=zeros=plateau=0
    for small in range(8):
        for large_index in range(small,8):
            s,l=SIZES[small],SIZES[large_index]
            for flags in range(8):
                need(r.take('III')==(s,l,flags),'every configuration and flags')
                w,previous,following=flags&1,(flags>>1)&1,(flags>>2)&1
                n=l if w else s;p=l if w and previous else s;q=l if w and following else s
                shape=(n,p,q,n//4-p//4,n//4+p//4,3*n//4-q//4,3*n//4+q//4)
                need(r.take('7I')==shape,'independent exact view geometry')
                exponent=r.take('q');need(exponent==(-(1<<63) if flags&2 else (1<<63)-1),'view retains full symbolic scale')
                source=r.doubles(n)
                for i,operand in enumerate(source):
                    need(bits(operand)==bits(sample(i+flags)),'all original view input bits')
                    factor=factor_at(n,p,q,i,coefficients);actual=r.take('QQqiI')
                    need(actual==exact(bits(operand),bits(factor),exponent),'every exact view sample/factor product')
                    zeros+=not factor;plateau+=factor==1;view_values+=1
    need(r.at==len(body),'no missing or trailing exact capture bytes')
    return dict(passed=True,scalar_rows=len(rows),nonzero_scalar_products=nonzero,invalid_scalar_rows=invalid,
        maximum_product_bits=maximum_bits,minimum_shift=min(shifts),maximum_shift=max(shifts),
        finite_sample_exponent_fields=len(sample_fields),factor_exponent_fields=len(factor_fields),significand_widths=len(widths),
        factor_significand_widths=len(factor_widths),
        saved_underflow_witnesses=witnesses,saved_witnesses_at_least1074=large,
        shapes=288,configurations=36,coefficients=8160,maximum_coefficient_error=max_error,coefficient_bound=BOUND,
        exact_view_values=view_values,outside_support_values=zeros,plateau_values=plateau,
        overlap_executed=False,PCM_executed=False,full_synthesis_qualified=False)


def corruption_controls(body,rows,oracle):
    # Scalar rows have explicit fixed-width input/status/product fields.
    wide=next(i for i,row in enumerate(rows) if not row['status'] and
        exact(row['sample'],row['factor'],row['exponent'])[1])
    scalar_end=12+64*len(rows);first_view=scalar_end+8+sum(4+4*n for n in SIZES)
    first_view_product=first_view+48+64*8
    high_at=12+wide*64+40;changed=bytearray(body[high_at:high_at+8]);changed[0]^=1
    edits=[('magic',0,b'X'),('scalar-index',12,struct.pack('<I',999)),
        ('sample',16,struct.pack('<Q',1)),('factor',24,struct.pack('<Q',0)),
        ('base-exponent',32,struct.pack('<q',0)),('status',40,struct.pack('<i',-2)),
        ('canonical-zero',44,struct.pack('<Q',1)),('high-product',high_at,bytes(changed)),
        ('coefficient',scalar_end+8,struct.pack('<d',math.nan)),
        ('geometry',first_view+12,struct.pack('<I',63)),
        ('view-product',first_view_product,bytes(8))]
    damaged=[(name,body[:at]+replacement+body[at+len(replacement):]) for name,at,replacement in edits]
    damaged.extend([('truncated',body[:-1]),('trailing',body+b'X')])
    for name,bad in damaged:
        try:compare(bad,rows,oracle)
        except (ValueError,struct.error):continue
        raise ValueError('corrupted exact capture accepted: '+name)
    return [name for name,_ in damaged]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh task-local output');out.mkdir(parents=True)
    report=dict(completed=False,passed=False,commands=[],sources={},sanitizers=['address','undefined'],
        native_executed=False,production_selected=False,overlap_executed=False,PCM_executed=False,deferred_scopes_resumed=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,label):
        body=path.read_bytes();target=out/'sources'/label;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
        report['sources'][label]=sha(body);return body
    def run(name,argv):
        nonce=uuid.uuid4().hex;request,receipt,stop=(out/(name+s) for s in ('.request.json','.receipt.json','.stop'))
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=60,receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command=(['wsl.exe','--exec','python3'] if os.name=='nt' else [sys.executable])+[linux(out/'supervisor.py'),linux(request)]
        row=dict(name=name,argv=command,child_argv=list(map(str,argv)),nonce=nonce,request_sha256=sha(request.read_bytes()))
        report['commands'].append(row);save();child=None;started=time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as so,(out/(name+'.stderr.log')).open('xb') as se:
                child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=so,stderr=se,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
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
            receipt_body.get('child_pid')==receipt_body.get('owned_pgid') and receipt_body.get('child_returncode')==0,'owned child terminal: '+name)
        return (out/(name+'.stdout.log')).read_text('utf-8')
    save()
    try:
        freeze(Path(__file__),'runner.py')
        for component in COMPONENTS:
            folder=ROOT/'idf/components'/component
            for path in sorted(folder.rglob('*')):
                if path.is_file():freeze(path,'components/'+component+'/'+path.relative_to(folder).as_posix())
        for name in ('vorbis_window_host.c','vorbis_window_exact_host.c'):freeze(ROOT/'tests/native'/name,'native/'+name)
        helper=freeze(ROOT/'tests/test-vorbis-window.py','window-oracle.py');need(sha(helper)==WINDOW_SHA,'pinned local sine oracle')
        oracle=load(out/'sources/window-oracle.py','frozen_exact_window_oracle')
        saved,saved_report=original_data();(out/'sources/recorded-overlap.bin').write_bytes(saved)
        (out/'sources/recorded-overlap-report.json').write_bytes(saved_report)
        report['sources']['recorded-overlap.bin']=sha(saved);report['sources']['recorded-overlap-report.json']=sha(saved_report)
        witnesses,witness_metrics=saved_witnesses(saved);rows=cases(witnesses)
        (out/'model.json').write_text(json.dumps(rows,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
        (out/'input.bin').write_bytes(encode(rows));report.update(saved_DATA_archive_sha256=PRIOR_SHA,
            saved_DATA_manifest_sha256=PRIOR_MANIFEST_SHA,witnesses=witness_metrics,
            model_sha256=sha((out/'model.json').read_bytes()),input_sha256=sha((out/'input.bin').read_bytes()))
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py')
        definitions=[ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node,ast.Assign) and
            any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(definitions)==1,'one owned process supervisor');(out/'supervisor.py').write_text(definitions[0],encoding='utf-8',newline='\n')
        report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes());save()
        report['compiler_version']=run('compiler-version',['gcc','--version'])
        common=['gcc','-std=c11','-O1','-g','-UNDEBUG','-fno-fast-math','-ffp-contract=off','-fno-pie','-no-pie',
            '-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-ffunction-sections','-fdata-sections',
            '-Wall','-Wextra','-Werror',*['-I'+linux(out/'sources/components'/name/'include') for name in COMPONENTS]]
        units=[out/'sources/components/native_vorbis_window/window.c',
            out/'sources/components/native_vorbis_window_exact/product.c',out/'sources/components/native_vorbis_window_exact/view.c',
            out/'sources/native/vorbis_window_exact_host.c']
        run('compile',[*common,*map(linux,units),'-Wl,--gc-sections','-lm','-o',linux(out/'window-exact')])
        text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',
            linux(out/'window-exact'),linux(out/'input.bin'),linux(out/'capture.bin')])
        match=re.fullmatch(r'WINDOW_EXACT rows=(\d+) shapes=288 refusals=(\d+) checks=(\d+)\s*',text)
        need(match is not None and int(match[1])==len(rows) and not (out/'execute.stderr.log').read_bytes(),'guarded exact products without diagnostics')
        measured=compare((out/'capture.bin').read_bytes(),rows,oracle)
        report['corruption_controls']=corruption_controls((out/'capture.bin').read_bytes(),rows,oracle)
        for name,digest in report['sources'].items():need(sha((out/'sources'/name).read_bytes())==digest,'frozen source/data identities unchanged')
        report.update(completed=True,passed=True,measurements=measured,controls=dict(rows=int(match[1]),refusals=int(match[2]),checks=int(match[3])),
            capture_sha256=sha((out/'capture.bin').read_bytes()),binary_sha256=sha((out/'window-exact').read_bytes()))
        save();print(json.dumps(dict(passed=True,controls=report['controls'],measurements=measured)));return 0
    except BaseException as error:report['error']=repr(error);save();raise


if __name__=='__main__':raise SystemExit(main())
