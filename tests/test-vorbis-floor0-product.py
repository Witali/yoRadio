"""Exact joint floor0 product/rounding primitives; no gain or decoder execution.

Expected integers use Python unbounded multiplication. Expected binary64 values
use direct Fraction conversion, never a preliminary float(integer) conversion.
The frame-channel application and real packet/IMDCT handoff are separate tests.
"""
import argparse,ast,hashlib,json,os,random,re,struct,subprocess,sys,time,uuid
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COMPONENTS=('native_vorbis_numeric','native_vorbis_packet_frame','native_vorbis_floor1_product',
            'native_vorbis_transform','native_vorbis_floor0_spectrum')
SELECTED={1,31,32,33,52,53,54,63,64,65,1079,1087}


def need(test,message):
    if not test:raise ValueError(message)


def sha(body):return hashlib.sha256(body).hexdigest()
def bits(value):return struct.unpack('<Q',struct.pack('<d',value))[0]
def linux(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def cases():
    rows=[]
    def add(label,width,value,factor,top,controls=False):
        rows.append(dict(id=label,width=width,value=value,factor=factor,top=top,controls=controls))
    factors=(0,1,(1<<32)-1,1<<32,1<<52,(1<<53)-1)
    for width in range(1,1088):
        maximum=(1<<width)-1
        values=sorted({0,1,-1,maximum,-maximum,1<<(width-1),-(1<<(width-1))})
        for fi,factor in enumerate(factors):
            for vi,value in enumerate(values):
                top=(-1022,-1,0,637,638)[(width+fi+vi)%5]
                add(f'width-{width}-{fi}-{vi}',width,value,factor,top,
                    width in SELECTED and fi==0 and vi==0)
        for sign in (-1,1):
            add(f'excluded-endpoint-{width}-{sign}',width,sign*(1<<width),1,0)
    for width in sorted(SELECTED):
        for factor_bits in range(1,54):
            for factor in sorted({1<<(factor_bits-1),(1<<factor_bits)-1}):
                for sign in (-1,1):
                    add(f'factor-bits-{width}-{factor_bits}-{factor}-{sign}',width,
                        sign*((1<<width)-1),factor,(-1022,638)[factor_bits&1])
    # The entire target exponent grid meets even, odd and carry midpoint
    # significands, with a guard-bit neighbor on either side, at both signs.
    for top in range(-1022,639):
        for significand in ((1<<52)+2,(1<<52)+1,(1<<53)-1):
            for delta in (-1,0,1):
                value=(significand<<11)+(1<<10)+delta
                for sign in (-1,1):
                    add(f'round-grid-{top}-{significand}-{delta}-{sign}',64,sign*value,1,top)
    for highest in (53,54,55,63,64,65,127,511,1086):
        shift=highest-52
        for significand in ((1<<52)+2,(1<<52)+1,(1<<53)-1):
            for delta in (-1,0,1):
                for sign in (-1,1):
                    value=(significand<<shift)+(1<<(shift-1))+delta
                    # At shift1 the upper carry neighbor is the next power of
                    # two; give that exact value its required strict width.
                    width=max(highest+1,value.bit_length())
                    add(f'deep-round-{highest}-{significand}-{delta}-{sign}',width,sign*value,1,638)
    rng=random.Random(0x463050524f445543)
    for index in range(1000):
        width=rng.randint(1,1087);factor_bits=rng.randint(1,53)
        value=rng.randrange(1<<width)*(-1 if index&1 else 1)
        factor=rng.randrange(1<<factor_bits)
        add(f'random-{index}',width,value,factor,rng.randint(-1022,638))
    return rows


def encode(rows):
    body=bytearray(b'F0PRODIN'+struct.pack('<I',len(rows)))
    for row in rows:
        limbs=(row['width']+32)//32
        body.extend(struct.pack('<IIIQi',row['width'],limbs,int(row['controls']),row['factor'],row['top']))
        body.extend((row['value']&((1<<(limbs*32))-1)).to_bytes(limbs*4,'little'))
    return bytes(body)


def inspect_capture(body,rows):
    need(body[:12]==b'F0PRODOU'+struct.pack('<I',len(rows)),'complete product capture header')
    offset=12;valid_count=invalid=rounded_count=zero_products=ties=rounding_carries=0
    widths=set();factor_widths=set();tops=set();maximum_bits=0;words_count=0
    for row in rows:
        limbs=(row['width']+32)//32
        need(offset+44+limbs*4+144<=len(body),'complete product row')
        width,got_limbs,factor,top,valid,zero,highest,negative,rounded=struct.unpack_from('<IIQiIIiIQ',body,offset);offset+=44
        need((width,got_limbs,factor,top)==(row['width'],limbs,row['factor'],row['top']),'ordered product identity')
        source=body[offset:offset+limbs*4];offset+=limbs*4
        raw=row['value']&((1<<(limbs*32))-1)
        need(source==raw.to_bytes(limbs*4,'little'),'every immutable source word')
        signed=raw-(1<<(limbs*32)) if raw>>(limbs*32-1) else raw
        wanted_valid=abs(signed)<(1<<width)
        need(valid==int(wanted_valid) and zero==int(signed==0),'strict source domain and zero predicate')
        actual_words=struct.unpack_from('<36I',body,offset);offset+=144
        if not wanted_valid:
            need(highest==-2 and negative==rounded==0 and actual_words==(0xa5a5a5a5,)*36,
                 'rejected source leaves magnitude untouched')
            invalid+=1;continue
        product=abs(signed)*factor;wanted_top=product.bit_length()-1
        expected_words=tuple((product>>(32*i))&0xffffffff for i in range(36))
        need(actual_words==expected_words and highest==wanted_top and negative==int(signed<0),
             'all exact joint product words/top/sign')
        words_count+=36;valid_count+=1;widths.add(width)
        if factor:factor_widths.add(factor.bit_length())
        if not product:
            need(rounded==0,'zero product is not passed to nonzero rounding primitive');zero_products+=1;continue
        shift=top-wanted_top
        exact=Fraction(product<<shift) if shift>=0 else Fraction(product,1<<-shift)
        if signed<0:exact=-exact
        need(rounded==bits(float(exact)),'direct correctly-rounded Fraction boundary')
        need(1<=((rounded>>52)&2047)<=1662,'normal finite grid within2^639')
        rounded_count+=1;tops.add(top);maximum_bits=max(maximum_bits,product.bit_length())
        if wanted_top>52:
            discarded=wanted_top-52;_,remainder=divmod(product,1<<discarded)
            ties+=2*remainder==(1<<discarded)
            rounding_carries+=((rounded>>52)&2047)==top+1024
    need(offset==len(body),'no missing/trailing capture bytes')
    need(widths==set(range(1,1088)) and factor_widths==set(range(1,54)) and tops==set(range(-1022,639)),
         'all declared widths/factor bits/target exponents')
    need(invalid==2174 and maximum_bits==1140 and ties and rounding_carries,'endpoint and rounding witness families')
    return dict(passed=True,rows=len(rows),valid_products=valid_count,invalid_source_rows=invalid,
        rounded_values=rounded_count,zero_products=zero_products,exact_product_words=words_count,
        source_magnitude_widths=1087,nonzero_factor_widths=53,working_top_values=1661,
        maximum_product_bits=maximum_bits,midpoint_ties=ties,rounding_carries=rounding_carries,
        decoder_executed=False,gain_executed=False,IMDCT_executed=False,PCM_executed=False)


def corruption_controls(body,rows):
    # First row is a valid negative source multiplied byzero.
    changes=[('magic',0,b'X'),('factor',20,struct.pack('<Q',1)),('valid',32,bytes(4)),
        ('highest',40,struct.pack('<i',0)),('rounded',48,struct.pack('<Q',1)),
        ('source',56,bytes(4)),('magnitude',60,struct.pack('<I',1))]
    damaged=[(name,body[:at]+replacement+body[at+len(replacement):]) for name,at,replacement in changes]
    damaged.extend([('truncated',body[:-1]),('trailing',body+b'X')])
    for name,bad in damaged:
        try:inspect_capture(bad,rows)
        except (ValueError,struct.error):continue
        raise ValueError('corruption accepted: '+name)
    return [name for name,_ in damaged]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--verify-capture',type=Path);args=parser.parse_args();rows=cases()
    if args.verify_capture:
        body=args.verify_capture.read_bytes();result=inspect_capture(body,rows)
        result['corruption_controls']=corruption_controls(body,rows)
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result));return 0
    out=args.output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh task-local output');out.mkdir(parents=True)
    report=dict(completed=False,passed=False,commands=[],sources={},sanitizers=['address','undefined'],
        scope='Exact joint integer product and one binary64 rounding only',decoder_executed=False,
        gain_executed=False,IMDCT_executed=False,PCM_executed=False,native_executed=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,label):
        body=path.read_bytes();target=out/'sources'/label;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
        report['sources'][label]=sha(body);return body
    def run(name,argv):
        nonce=uuid.uuid4().hex;request,receipt,stop=(out/(name+x) for x in ('.request.json','.receipt.json','.stop'))
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=60,
            receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command=(['wsl.exe','--exec','python3'] if os.name=='nt' else [sys.executable])+[linux(out/'supervisor.py'),linux(request)]
        row=dict(name=name,nonce=nonce,argv=command,child_argv=list(map(str,argv)),request_sha256=sha(request.read_bytes()))
        report['commands'].append(row);save();child=None;started=time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as so,(out/(name+'.stderr.log')).open('xb') as se:
                child=subprocess.Popen(command,stdout=so,stderr=se,stdin=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                row['transport_pid']=child.pid;child.wait(timeout=80)
        finally:
            if child is not None and child.poll() is None:
                stop.write_text(nonce,encoding='ascii')
                try:child.wait(timeout=15)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5);row['forced_transport_stop']=True
            s=json.loads(receipt.read_bytes()) if receipt.exists() else {}
            row.update(elapsed_seconds=time.monotonic()-started,supervisor=s,transport_exit=None if child is None else child.poll());save()
        need(row['transport_exit']==0 and not row.get('forced_transport_stop'),'owned transport terminal: '+name)
        need(s.get('nonce')==nonce and s.get('request_sha256')==row['request_sha256'] and s.get('state')=='terminal' and
            s.get('final') and s.get('new_session') and s.get('child_reaped') and s.get('group_gone') and
            s.get('child_pid')==s.get('owned_pgid') and s.get('child_returncode')==0,'owned command terminal: '+name)
        return (out/(name+'.stdout.log')).read_text('utf-8')
    save()
    try:
        freeze(Path(__file__),'runner.py')
        for name in COMPONENTS:
            folder=ROOT/'idf/components'/name
            for path in sorted(folder.rglob('*.h')):freeze(path,'components/'+name+'/'+path.relative_to(folder).as_posix())
        freeze(ROOT/'idf/components/native_vorbis_floor0_spectrum/product.c','components/native_vorbis_floor0_spectrum/product.c')
        freeze(ROOT/'tests/native/vorbis_floor0_product_host.c','native/vorbis_floor0_product_host.c')
        (out/'input.bin').write_bytes(encode(rows));report.update(model_rows=len(rows),input_sha256=sha((out/'input.bin').read_bytes()))
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py')
        values=[ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node,ast.Assign) and
            any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(values)==1,'one owned process supervisor');(out/'supervisor.py').write_text(values[0],encoding='utf-8',newline='\n')
        report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes());save()
        report['compiler_version']=run('compiler-version',['gcc','--version'])
        include=['-I'+linux(out/'sources/components'/name/'include') for name in COMPONENTS]
        include.append('-I'+linux(out/'sources/components/native_vorbis_floor0_spectrum'))
        common=['gcc','-std=c11','-O1','-g','-UNDEBUG','-fno-fast-math','-ffp-contract=off','-fno-pie','-no-pie',
            '-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-Wall','-Wextra','-Werror',*include]
        run('compile',[*common,linux(out/'sources/components/native_vorbis_floor0_spectrum/product.c'),
            linux(out/'sources/native/vorbis_floor0_product_host.c'),'-o',linux(out/'product')])
        text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',
            linux(out/'product'),linux(out/'input.bin'),linux(out/'capture.bin')])
        match=re.fullmatch(r'FLOOR0_PRODUCT_CAPTURE rows=(\d+) invalid=(\d+) controls=(\d+) checks=(\d+)\s*',text)
        need(match is not None and not (out/'execute.stderr.log').read_bytes(),'complete guarded capture')
        measured=inspect_capture((out/'capture.bin').read_bytes(),rows)
        need(int(match[1])==len(rows) and int(match[2])==measured['invalid_source_rows'],'actual corpus/assertion counters')
        damaged=corruption_controls((out/'capture.bin').read_bytes(),rows)
        for name,digest in report['sources'].items():need(sha((out/'sources'/name).read_bytes())==digest,'unchanged frozen source')
        report.update(completed=True,passed=True,measurements=measured,corruption_controls=damaged,
            controls=dict(rows=int(match[1]),invalid=int(match[2]),controls=int(match[3]),checks=int(match[4])),
            capture_sha256=sha((out/'capture.bin').read_bytes()),binary_sha256=sha((out/'product').read_bytes()))
        save();print(json.dumps(dict(passed=True,controls=report['controls'],measurements=measured)));return 0
    except BaseException as error:report['error']=repr(error);save();raise


if __name__=='__main__':raise SystemExit(main())
