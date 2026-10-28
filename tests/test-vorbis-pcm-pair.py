"""Exact paired-scale PCM qualification with integer/Fraction reference math.

The oracle constructs full integer sums for bounded spans, and retains an
infinitesimal's sign at an exact half tie for enormous scale gaps. No codec,
deferred target, native SDK/QEMU, production task or physical board is used.
"""
import argparse, ast, hashlib, json, math, os, random, re, struct, subprocess, sys, time, uuid
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENTS = ('native_vorbis_numeric','native_vorbis_packet_frame','native_vorbis_floor1_product',
              'native_vorbis_transform','native_vorbis_pcm')
MIN, MAX = -(1 << 63), (1 << 63)-1


def need(test, message):
    if not test: raise ValueError(message)


def sha(body): return hashlib.sha256(body).hexdigest()
def bits(value): return struct.unpack('<Q',struct.pack('<d',value))[0]
def floating(word): return struct.unpack('<d',struct.pack('<Q',word))[0]
def clamp(value): return max(-32768,min(32767,value))
def linux(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def rounded(integer, exponent):
    if not integer: return 0
    sign=-1 if integer < 0 else 1; magnitude=abs(integer)
    top=magnitude.bit_length()-1+exponent
    if top > 16: return 32767 if sign > 0 else -32768
    if top < -1: return 0
    if exponent >= 0: return clamp(integer << exponent)
    denominator=1 << -exponent
    quotient,remainder=divmod(magnitude,denominator)
    quotient += 2*remainder > denominator or (2*remainder == denominator and quotient&1)
    return clamp(sign*quotient)


def reference(a,ea,b,eb):
    na,da=a.as_integer_ratio(); nb,db=b.as_integer_ratio()
    qa=ea+15-(da.bit_length()-1); qb=eb+15-(db.bit_length()-1)
    if not na: return rounded(nb,qb)
    if not nb: return rounded(na,qa)
    if abs(qa-qb) <= 8192:
        q=min(qa,qb)
        return rounded((na << (qa-q))+(nb << (qb-q)),q)
    # Nonzero finite binary64 coefficients have <=53 significant bits. Across
    # a gap>8192, a tiny term can change nearest rounding only at an exact half
    # tie of the dominant term; keeping that sign is sufficient and exact.
    n,q,tiny=(na,qa,nb) if qa > qb else (nb,qb,na)
    top=abs(n).bit_length()-1+q
    if top > 16: return 32767 if n > 0 else -32768
    if top < -1: return 0
    if q >= 0: return rounded(n,q)
    denominator=1 << -q
    floor,remainder=divmod(n,denominator)
    if 2*remainder == denominator: return clamp(floor+(tiny > 0))
    return rounded(n,q)


def rows():
    result=[]
    def add(name,ea,eb,a,b,controls=False):
        need(len(a)==len(b),'matching model lengths')
        result.append(dict(id=name,ea=ea,eb=eb,a=a,b=b,controls=controls))
    add('empty-endpoints',MIN,MAX,[],[],True)
    halves=[k+.5 for k in range(-32769,32769)]
    for sign in (-1,0,1):
        add('all-half-ties-extreme-tiny-'+str(sign),-15,MIN,halves,[float(sign)]*len(halves))
    for sign in (-1,1):
        add('all-half-ties-subnormal-'+str(sign),-15,0,halves,[sign*math.ulp(0.0)]*len(halves))
    integers=list(map(float,range(-32770,32770)))
    add('all-integers-and-clips',-15,0,integers,[0.0]*len(integers))
    for width in range(1,54):
        patterns=sorted({1 << (width-1),(1 << width)-1,((1 << (width-1))|1),
            ((1 << width)-1)&~1})
        patterns=[value for value in patterns if value]
        for distance in (-2,-1,0,1,2):
            aa=[];bb=[]
            for x in patterns:
                for y in patterns:
                    for sa,sb in ((-1,-1),(-1,1),(1,-1),(1,1)):
                        aa.append(float(sa*x));bb.append(float(sb*y))
            add(f'width-{width}-distance-{distance}',-width,-width+distance,aa,bb,width in (1,32,53) and distance==0)
    fraction_words=(0,1,2,(1 << 51)-1,1 << 51,(1 << 52)-2,(1 << 52)-1)
    for field in range(2047):
        aa=[];bb=[]
        for index,fraction in enumerate(fraction_words):
            word=(field << 52)|fraction
            aa.extend([floating(word),floating(word|(1 << 63))])
            other=(field << 52)|fraction_words[-1-index]
            bb.extend([floating(other|(1 << 63)),floating(other)])
        # Scale the entire exponent field back near ordinary S16 values.
        # Every field including subnormals interacts with a rounding threshold.
        add(f'all-binary64-fields-{field}',1023-field-15,1023-field-15,aa,bb,field in (0,1,1023,2046))
    scales=(MIN,MIN+1,MIN+2048,-3000,-15,0,3000,MAX-2048,MAX-1,MAX)
    words=(0,1,0x000fffffffffffff,0x0010000000000000,0x3fe0000000000000,
        0x3ff0000000000000,0x3ff0000000000001,0x4000000000000000,0x7fefffffffffffff)
    for ea in scales:
        for eb in scales:
            aa=[];bb=[]
            for wa in words:
                for wb in words:
                    for sa,sb in ((0,0),(0,1),(1,0),(1,1)):
                        aa.append(floating(wa|(sa << 63)));bb.append(floating(wb|(sb << 63)))
            add(f'endpoint-matrix-{ea}-{eb}',ea,eb,aa,bb,ea==MIN and eb==MAX)
    rng=random.Random(0x50434d50414952)
    for index in range(60):
        ea=rng.randint(-3000,3000);eb=rng.randint(-3000,3000)
        aa=[];bb=[]
        for _ in range(128):
            for values in (aa,bb):
                word=(rng.getrandbits(1) << 63)|(rng.randrange(2047) << 52)|rng.getrandbits(52)
                values.append(floating(word))
        add(f'random-finite-{index}',ea,eb,aa,bb,index==0)
    return result


def fraction_anchors():
    rng=random.Random(0x4652414354494f4e);checks=0
    for _ in range(2000):
        a=rng.randint(-(1 << 53),(1 << 53))*2.0**rng.randint(-55,5)
        b=rng.randint(-(1 << 53),(1 << 53))*2.0**rng.randint(-55,5)
        ea,eb=rng.randint(-150,150),rng.randint(-150,150)
        value=(Fraction.from_float(a)*Fraction(2)**ea+Fraction.from_float(b)*Fraction(2)**eb)*32768
        need(reference(a,ea,b,eb)==clamp(round(value)),'independent Fraction rounding anchor');checks+=1
    for k in (-32769,-32768,-3,-2,-1,0,1,2,32766,32767,32768):
        need(reference(k+.5,-15,-1.0,MIN)==clamp(k),'symbolic negative infinitesimal')
        need(reference(k+.5,-15,1.0,MIN)==clamp(k+1),'symbolic positive infinitesimal')
        need(reference(k+.5,-15,0.0,MIN)==clamp(round(Fraction(2*k+1,2))),'symbolic exact half');checks+=3
    return checks


def encode(model):
    data=bytearray(b'VPCMPR01'+struct.pack('<I',len(model)))
    for row in model:
        n=len(row['a']);data.extend(struct.pack('<IIqq',n,int(row['controls']),row['ea'],row['eb']))
        for values in (row['a'],row['b']): data.extend(struct.pack('<'+str(n)+'d',*values))
    return bytes(data)


def compare(body,model):
    need(body[:12]==b'VPCMPR01'+struct.pack('<I',len(model)),'complete ordered capture header');offset=12
    values=0;positive=negative=zero=0;expected_body=bytearray()
    for row in model:
        n=len(row['a']);need(offset+20+n*18 <= len(body),'complete capture row')
        got=struct.unpack_from('<Iqq',body,offset);offset+=20
        need(got==(n,row['ea'],row['eb']),'ordered row identity and full exponents')
        for source in (row['a'],row['b']):
            wanted=struct.pack('<'+str(n)+'d',*source)
            need(body[offset:offset+n*8]==wanted,'every immutable source bit');offset+=n*8
        got=struct.unpack_from('<'+str(n)+'h',body,offset);offset+=n*2
        wanted=[reference(a,row['ea'],b,row['eb']) for a,b in zip(row['a'],row['b'])]
        need(tuple(wanted)==got,'every exact PCM value: '+row['id'])
        expected_body.extend(struct.pack('<'+str(n)+'h',*wanted))
        values+=n;positive+=sum(x==32767 for x in got);negative+=sum(x==-32768 for x in got);zero+=sum(x==0 for x in got)
    need(offset==len(body),'no missing or trailing capture data')
    return dict(passed=True,rows=len(model),pcm_values=values,positive_endpoint=positive,
        negative_endpoint=negative,zero_values=zero,expected_pcm_sha256=sha(expected_body),
        binary64_exponent_fields=2047,coefficient_widths=53,full_signed64_exponents=True)


def corruption_controls(body,model):
    # The first row is empty; the second starts at32 and has the full half grid.
    need(not model[0]['a'] and len(model[1]['a'])==65538,'stable protocol anchors')
    first_source=52; first_output=52+16*len(model[1]['a'])
    replacements=[('magic',0,b'X'),('count',12,struct.pack('<I',1)),
        ('exponent',16,bytes(8)),('source',first_source,bytes(8)),
        ('PCM',first_output,bytes(2))]
    damaged=[(name,body[:offset]+replacement+body[offset+len(replacement):])
        for name,offset,replacement in replacements]
    damaged += [('truncated',body[:-1]),('trailing',body+b'X')]
    for name,corrupt in damaged:
        try:compare(corrupt,model)
        except (ValueError,struct.error):continue
        raise ValueError('damaged capture accepted: '+name)
    return [name for name,_ in damaged]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh task-local output');out.mkdir(parents=True)
    report=dict(completed=False,passed=False,commands=[],inputs={},sanitizers=['address','undefined'],
        native_executed=False,production_selected=False,deferred_scopes_resumed=False)
    def save(): (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,name):
        target=out/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);body=path.read_bytes();target.write_bytes(body)
        report['inputs'][path.relative_to(ROOT).as_posix()]=dict(snapshot=target.relative_to(out).as_posix(),sha256=sha(body));return body
    def run(name,argv):
        nonce=uuid.uuid4().hex;request,receipt,stop=(out/(name+s) for s in ('.request.json','.receipt.json','.stop'))
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=60,receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command=(['wsl.exe','--exec','python3'] if os.name=='nt' else [sys.executable])+[linux(out/'supervisor.py'),linux(request)]
        row=dict(name=name,argv=command,child_argv=list(map(str,argv)),nonce=nonce,request_sha256=sha(request.read_bytes()))
        report['commands'].append(row);save();child=error=None;started=time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as stdout,(out/(name+'.stderr.log')).open('xb') as stderr:
                child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                row['transport_pid']=child.pid;child.wait(timeout=80)
        except BaseException as caught: error=caught;row['parent_error_type']=type(caught).__name__
        finally:
            if child is not None and child.poll() is None:
                stop.write_text(nonce,encoding='ascii')
                try:child.wait(timeout=15)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5);row['forced_transport_stop']=True
            observed=json.loads(receipt.read_bytes()) if receipt.exists() else {}
            row.update(supervisor=observed,elapsed_seconds=time.monotonic()-started,transport_exit=None if child is None else child.poll())
            for stream in ('stdout','stderr'):
                path=out/(name+'.'+stream+'.log');row[stream+'_sha256']=sha(path.read_bytes()) if path.exists() else None
            save()
        need(error is None and row['transport_exit']==0 and not row.get('forced_transport_stop'),'owned transport terminal: '+name)
        need(observed.get('nonce')==nonce and observed.get('request_sha256')==row['request_sha256'] and
            observed.get('state')=='terminal' and observed.get('final') is True and observed.get('new_session') is True and
            observed.get('child_reaped') is True and observed.get('group_gone') is True and
            observed.get('child_pid')==observed.get('owned_pgid') and observed.get('child_returncode')==0,'owned command terminal: '+name)
        return (out/(name+'.stdout.log')).read_text('utf-8',errors='replace')
    save()
    try:
        freeze(Path(__file__),'runner.py')
        for name in COMPONENTS:
            folder=ROOT/'idf/components'/name
            for path in sorted(folder.rglob('*')):
                if path.is_file():freeze(path,'components/'+name+'/'+path.relative_to(folder).as_posix())
        freeze(ROOT/'tests/native/vorbis_pcm_pair_host.c','native/vorbis_pcm_pair_host.c')
        model=rows();report['fraction_anchors']=fraction_anchors()
        (out/'input.bin').write_bytes(encode(model));report['input_sha256']=sha((out/'input.bin').read_bytes())
        report['model_summary']=[dict(id=r['id'],ea=r['ea'],eb=r['eb'],count=len(r['a']),controls=r['controls']) for r in model];save()
        if args.prepare_only: print(json.dumps(dict(prepared=True,rows=len(model),values=sum(len(r['a']) for r in model))));return 0
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py')
        supervisors=[ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node,ast.Assign) and
            any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(supervisors)==1,'one owned supervisor');(out/'supervisor.py').write_text(supervisors[0],encoding='utf-8',newline='\n')
        report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes())
        report['compiler_version']=run('compiler-version',['gcc','--version'])
        common=['gcc','-std=c11','-O1','-g','-UNDEBUG','-fno-fast-math','-ffp-contract=off','-fno-pie','-no-pie',
            '-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-Wall','-Wextra','-Werror',
            *['-I'+linux(out/'sources/components'/name/'include') for name in COMPONENTS]]
        run('compile',[*common,linux(out/'sources/components/native_vorbis_pcm/pcm.c'),
            linux(out/'sources/native/vorbis_pcm_pair_host.c'),'-o',linux(out/'pcm-pair')])
        text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1',
            'UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',linux(out/'pcm-pair'),linux(out/'input.bin'),linux(out/'capture.bin')])
        match=re.fullmatch(r'PCM_PAIR_CAPTURE rows=(\d+) refusals=(\d+) checks=(\d+)\s*',text)
        need(match is not None and not (out/'execute.stderr.log').read_bytes(),'complete guarded capture')
        measurement=compare((out/'capture.bin').read_bytes(),model)
        report['corruption_controls']=corruption_controls((out/'capture.bin').read_bytes(),model)
        need(int(match[1])==len(model),'same complete row count')
        for name,pin in report['inputs'].items():
            need(sha((ROOT/name).read_bytes())==pin['sha256']==sha((out/pin['snapshot']).read_bytes()),'all executed source bytes unchanged')
        report.update(completed=True,passed=True,measurement=measurement,
            controls=dict(refusals=int(match[2]),checks=int(match[3])),capture_sha256=sha((out/'capture.bin').read_bytes()),
            binary_sha256=sha((out/'pcm-pair').read_bytes()));save()
        print(json.dumps(dict(passed=True,controls=report['controls'],measurement=measurement)));return 0
    except BaseException as error:report['error_type']=type(error).__name__;report['error_message']=str(error);save();raise


if __name__=='__main__':raise SystemExit(main())
