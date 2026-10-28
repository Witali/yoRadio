"""Exact106-bit pair and exact-window slice PCM tests; no legacy C execution."""
import argparse,ast,hashlib,importlib.util,io,json,math,os,random,re,struct,subprocess,sys,time,uuid,zipfile
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COMPONENTS=('native_vorbis_numeric','native_vorbis_packet_frame','native_vorbis_floor1_product',
    'native_vorbis_transform','native_vorbis_window','native_vorbis_window_exact','native_vorbis_pcm_exact')
PCM_ARCHIVE='d96b5cbe53cee88ca78d5f4fb4e43dd72b5fc8676f64b55d92c2d575d413e648'
PCM_MANIFEST='1cab066613634e0cd0240389c45c783c536df6e620e86d6cc4da83f4a6bbedd0'
PINS={'legacy-reader.py':('test-vorbis-pcm-pair.py','f53ec0429b06abf2576e5c052df4ea95fc60dae59f63f42687a25e6ba7e60aa9'),
    'window-reader.py':('test-vorbis-window-exact.py','06268abe3c9fe4836bf17ca91b1fcb73ce82137ea872282e21bad61fa4494e41'),
    'sine-oracle.py':('test-vorbis-window.py','c2fbcc21f1236b2c4b95d7e4f77a5498d4eb427fb2ec5ec5777c0447b0ed69d9')}
MIN,MAX=-(1<<63),(1<<63)-1
ZERO=(0,0,0,0,0)


def need(test,message):
    if not test:raise ValueError(message)
def sha(body):return hashlib.sha256(body).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def helpers(base):
    for label,(_,digest) in PINS.items():need(sha((base/label).read_bytes())==digest,'pinned local pure reader')
    return {label:load(base/label,'pcm_exact_'+label.replace('-','_')) for label in PINS}
def linux(path):
    p=Path(path).resolve().as_posix();return '/mnt/'+p[0].lower()+p[2:] if sys.platform=='win32' else p
def clamp(n):return max(-32768,min(32767,n))
def canonical(integer,shift=0,exponent=0):
    if not integer:return ZERO
    m=abs(integer);z=(m&-m).bit_length()-1;m>>=z
    return m&((1<<64)-1),m>>64,exponent,shift+z,int(integer<0)
def valid(p):
    lo,hi,e,s,negative=p;m=lo+(hi<<64)
    return p==ZERO if not m else bool(m&1 and hi<1<<42 and -2148<=s<=1023 and negative in (0,1))
def rounded(n,q):
    if not n:return 0
    sign=-1 if n<0 else 1;m=abs(n);top=m.bit_length()-1+q
    if top>16:return 32767 if sign>0 else -32768
    if top< -1:return 0
    if q>=0:return clamp(n<<q)
    d=1<<-q;whole,remainder=divmod(m,d)
    whole+=2*remainder>d or (2*remainder==d and whole&1)
    return clamp(sign*whole)
def reference(a,b):
    need(valid(a) and valid(b),'canonical oracle inputs')
    ma=a[0]+(a[1]<<64);mb=b[0]+(b[1]<<64)
    na=-ma if a[4] else ma;nb=-mb if b[4] else mb
    qa=a[2]+a[3]+15;qb=b[2]+b[3]+15
    if not na:return rounded(nb,qb)
    if not nb:return rounded(na,qa)
    if abs(qa-qb)<=8192:
        q=min(qa,qb);return rounded((na<<(qa-q))+(nb<<(qb-q)),q)
    # With <=106-bit integer magnitudes, a gap>8192 leaves the tiny term
    # smaller than every nonzero grid distance of the dominant term. Only
    # an exact half tie can change rounding; retain the tiny term's sign.
    n,q,tiny=(na,qa,nb) if qa>qb else (nb,qb,na)
    top=abs(n).bit_length()-1+q
    if top>16:return 32767 if n>0 else -32768
    if top< -1:return 0
    if q>=0:return rounded(n,q)
    d=1<<-q;floor,remainder=divmod(n,d)
    return clamp(floor+(tiny>0)) if 2*remainder==d else rounded(n,q)
def fraction_anchors():
    rng=random.Random(0x31303650434d);count=0
    for _ in range(2000):
        products=[];total=Fraction(0)
        for _ in range(2):
            width=rng.randint(1,106);m=rng.randrange(1<<(width-1),1<<width)|1
            if rng.getrandbits(1):m=-m
            shift=rng.randint(-80,80);e=rng.randint(-150,150);p=canonical(m,shift,e)
            products.append(p);total+=Fraction(m)*Fraction(2)**(shift+e)
        need(reference(*products)==clamp(round(total*32768)),'independent Fraction106 anchor');count+=1
    for k in (-32769,-32768,-3,-2,-1,0,1,2,32766,32767,32768):
        for sign in (-1,0,1):
            need(reference(canonical(2*k+1,-16),canonical(sign,-2148,MIN))==
                (clamp(k+(sign>0)) if sign else clamp(round(Fraction(2*k+1,2)))),'symbolic106 infinitesimal anchor');count+=1
    return count


def scalar_cases(window):
    rows=[]
    def add(name,a,b,controls=False,operands=None,nulls=0,matrix=False):
        rows.append(dict(id=name,a=a,b=b,status=0 if valid(a) and valid(b) and not nulls else -1,
            controls=controls,operands=operands,nulls=nulls,matrix=matrix))
    for k in range(-32769,32769):
        for sign in (-1,0,1):add(f'half-{k}-{sign}',canonical(2*k+1,-16),canonical(sign,-2148,MIN))
    for width in range(1,107):
        for m in sorted({(1<<(width-1))|1,(1<<width)-1}):
            for shift in (-2148,0,1023):
                for exponent in (MIN,MAX,-shift-width-15):
                    for sign in (-1,1):
                        a=canonical(sign*m,shift,exponent)
                        for other in (ZERO,canonical(-sign*m,shift,exponent),canonical(-sign,shift,exponent)):
                            add(f'width-{width}-{m}-{shift}-{exponent}-{sign}-{other[0]}',a,other,width in (1,53,64,106))
    for width in (64,65,105,106):
        magnitudes=sorted({(1<<width)-1,(1<<(width-1))|((1<<min(64,width))-1)})
        for first in magnitudes:
            for second in (first,first-2):
                for distance in (0,1,2):
                    for exponent in (-15,-width-14,-width):
                        for sa,sb in ((-1,-1),(-1,1),(1,-1),(1,1)):
                            add(f'wide-merge-{width}-{first}-{second}-{distance}-{exponent}-{sa}-{sb}',
                                canonical(sa*first,0,exponent),canonical(sb*second,0,exponent+distance),
                                True,matrix=True)
    genuine=(window.bits(1+2**-52),window.bits(1-2**-53))
    for sign in (-1,1):
        aword=genuine[0]^((1<<63) if sign<0 else 0)
        for exponent,other,name in ((-16,ZERO,'midpoint-tail'),(38,canonical(-sign,0,38),'cancellation-tail')):
            a=window.exact(aword,genuine[1],exponent)
            operands=[aword,genuine[1],exponent,window.bits(float(-sign)) if other!=ZERO else 0,window.bits(1.0),38 if other!=ZERO else 0]
            add(name+'-'+str(sign),a,other,True,operands)
            need(reference(a,other)==sign,'genuine106-bit midpoint/cancellation tail witness')
    bad=[(0,0,1,0,0),(0,0,0,1,0),(0,0,0,0,1),(2,0,0,0,0),(0,1,0,0,0),
        (1,1<<42,0,0,0),(1,0,0,-2149,0),(1,0,0,1024,0)]
    for index,p in enumerate(bad):
        add('invalid-a-'+str(index),p,ZERO,True);add('invalid-b-'+str(index),ZERO,p,True)
    for nulls in (1,2,4,3,7):add('null-'+str(nulls),ZERO,ZERO,True,nulls=nulls)
    return rows


def saved_pcm():
    folder=ROOT/'tests/results/vorbis-pcm-pair-20261028';body=(folder/'captures.zip').read_bytes()
    need(sha(body)==PCM_ARCHIVE and sha((folder/'manifest.json').read_bytes())==PCM_MANIFEST,'pinned original PCM DATA')
    with zipfile.ZipFile(io.BytesIO(body)) as z:return z.read('host04/input.bin'),z.read('host04/capture.bin'),z.read('host04/report.json')
def saved_overlap(window):
    folder=ROOT/'tests/results/vorbis-overlap-20261028';body=(folder/'captures.zip').read_bytes()
    need(sha(body)==window.PRIOR_SHA and sha((folder/'manifest.json').read_bytes())==window.PRIOR_MANIFEST_SHA,
        'pinned overlap DATA at explicit repository location')
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        capture=z.read('host03/capture.bin');report=z.read('host03/report.json')
    need(sha(capture)==json.loads(report)['capture_sha256'],'saved overlap capture identity')
    return capture,report
def model(legacy,window,legacy_input,legacy_capture,overlap_capture):
    batches=legacy.rows();need(len(batches)==2479 and sum(len(r['a']) for r in batches)==478388,'all original PCM batches/values')
    need(legacy.encode(batches)==legacy_input,'every original PCM input byte')
    measured=legacy.compare(legacy_capture,batches);need(measured['pcm_values']==478388,'complete live pure old PCM reference')
    witnesses,witness_metrics=window.saved_witnesses(overlap_capture)
    r=window.Reader(overlap_capture);need(r.take('8s')==b'VOVERL01' and r.take('I')==8,'saved overlap DATA header')
    coefficients={}
    for n in window.SIZES:
        need(r.take('I')==n,'saved lookup order');coefficients[n]=r.doubles(n//2)
    need(r.take('I')==864,'all saved overlap DATA rows');adapters=[]
    for small in range(8):
        for large in range(small,8):
            for pattern in range(3):
                previous=[]
                for step in range(8):
                    if step==4:previous=[]
                    identity=r.take('7I');s,l,p,st,a,n,count=identity;ea,eb=r.take('qq');current=r.doubles(n)
                    pa=r.at;r.doubles(count);pb=r.at;r.doubles(count);r.doubles(n//2)
                    need((s,l,p,st,a,count)==(64<<small,64<<large,pattern,step,len(previous),(len(previous)+n)//4 if previous else 0),'all adapter source/record identities')
                    adapters.append(dict(identity=identity,ea=ea,eb=eb,a=previous,b=current,pa=pa,pb=pb))
                    previous=current
    need(r.at==len(overlap_capture),'complete saved DATA consumption')
    return dict(legacy=batches,legacy_input=legacy_input,legacy_capture=legacy_capture,legacy_measurements=measured,
        scalars=scalar_cases(window),adapters=adapters,coefficients=coefficients,witnesses=witnesses,witness_metrics=witness_metrics)
def encode(m):
    body=bytearray(b'VPCMEX01'+m['legacy_input']+struct.pack('<I',len(m['scalars'])))
    for row in m['scalars']:
        body.extend(struct.pack('<3I',row['controls'],bool(row['operands']),row['nulls']))
        for p in (row['a'],row['b']):body.extend(struct.pack('<QQqiI',*p))
        if row['operands']:body.extend(struct.pack('<QQqQQq',*row['operands']))
    body.extend(struct.pack('<I',len(m['adapters'])))
    for row in m['adapters']:
        body.extend(struct.pack('<7Iqq',*row['identity'],row['ea'],row['eb']))
        for values in (row['a'],row['b']):body.extend(struct.pack('<'+str(len(values))+'d',*values))
    return bytes(body)


def compare(body,m,window,sine):
    r=window.Reader(body);need(r.take('8s')==b'VPCMEX01' and r.take('I')==2479,'new capture and complete old batch count')
    for row in m['legacy']:
        n=len(row['a']);need(r.take('Iqq')==(n,row['ea'],row['eb']),'old batch scale identities')
        r.at+=n*18;need(r.at<=len(body),'complete old PCM batch')
    need(b'VPCMPR01'+body[8:r.at]==m['legacy_capture'],'every original source bit and all478388 exact PCM outputs preserved')
    need(r.take('I')==len(m['scalars']),'all new scalar rows');widths=set();invalid=genuine=matrix=0
    for index,row in enumerate(m['scalars']):
        need(r.take('I')==index,'scalar row identity');a=r.take('QQqiI');b=r.take('QQqiI');status,got=r.take('ih')
        need(a==tuple(row['a']) and b==tuple(row['b']) and status==row['status'],'all actual canonical products and statuses')
        if status:need(got==-23131,'failure preserves scalar output bytes');invalid+=1;continue
        need(got==reference(a,b),'exact106-bit pair nearest-even/clamp')
        for p in (a,b):
            magnitude=p[0]+(p[1]<<64)
            if magnitude:widths.add(magnitude.bit_length())
        if row['operands']:need(abs(got)==1,'real multiply handoff preserves midpoint/cancellation tail');genuine+=1
        matrix+=row['matrix']
    need(widths==set(range(1,107)) and genuine==4 and matrix==432,'all106 widths, wide merge matrix and four real multiply tail witnesses')
    need(r.take('I')==8,'all actual lookup sizes');coefficients={};max_error=0.0
    for n in window.SIZES:
        need(r.take('I')==n,'ordered current lookup');coefficients[n]=r.doubles(n//2)
        need(tuple(map(window.bits,coefficients[n]))==tuple(map(window.bits,m['coefficients'][n])),'saved/current actual binary64 coefficient identities')
        for a,b in zip(coefficients[n],sine.coefficients(n)):
            need(abs(a-b)<=2e-15,'unchanged sine coefficient bound');max_error=max(max_error,abs(a-b))
    need(r.take('I')==864,'all actual adapter rows')
    witness_lookup={tuple(row['witness']):row for row in m['witnesses']};seen=set();outputs=terms=ready=negative_current=0
    for row in m['adapters']:
        s,l,pattern,step,a,n,count=row['identity']
        need(r.take('7Iqq')==(*row['identity'],row['ea'],row['eb']),'every saved adapter identity and scale')
        ab,bb=r.take('ii');need((ab,bb)==(a//2,(n-a)//4 if a else 0),'actual-neighbor signed slice origins')
        for expected in (row['a'],row['b']):
            need(tuple(map(window.bits,r.doubles(len(expected))))==tuple(map(window.bits,expected)),'every full unwindowed source bit')
        if count:ready+=1;negative_current+=bb<0
        for t in range(count):
            products=[]
            for side,source,index,e,at,p,q in (
                ('previous',row['a'],ab+t,row['ea'],row['pa']+8*t,a,n),
                ('current',row['b'],bb+t,row['eb'],row['pb']+8*t,a,n)):
                size=len(source);operand=source[index] if 0<=index<size else 0.0
                factor=window.factor_at(size,p,q,index,coefficients)
                wanted=window.exact(window.bits(operand),window.bits(factor),e);actual=r.take('QQqiI')
                need(actual==wanted,'every actual adapter exact window term');products.append(actual);terms+=1
                identity=(s,l,pattern,step,side,t,index,at)
                if identity in witness_lookup:need(actual!=ZERO,'saved underflow term remains nonzero before sum');seen.add(identity)
            need(r.take('h')==reference(*products),'every adapter exact sum rounded and clipped only after addition');outputs+=1
    need(r.at==len(body) and len(seen)==17962 and terms==1197984 and ready==648,'complete adapter DATA/witness coverage')
    return dict(passed=True,legacy_batches=2479,legacy_pcm_values=478388,scalar_rows=len(m['scalars']),
        scalar_widths=len(widths),invalid_scalar_rows=invalid,genuine106_tail_witnesses=genuine,wide_merge_matrix_rows=matrix,
        half_boundaries=65538,half_perturbation_variants=3,adapter_rows=864,ready_rows=ready,adapter_pcm_values=outputs,
        exact_window_terms=terms,preserved_underflow_witnesses=len(seen),preserved_witnesses_at_least1074=13767,
        negative_current_origin_rows=negative_current,coefficients=8160,maximum_coefficient_error=max_error,coefficient_bound=2e-15,
        old_overlap_API_executed=False,old_PCM_API_executed=False,deferred_scopes_resumed=False,full_decoder_qualified=False)


def corruption_controls(body,m,window,sine):
    legacy_end=12+sum(20+18*len(row['a']) for row in m['legacy'])
    scalar_start=legacy_end+4;coefficients=scalar_start+74*len(m['scalars'])
    adapter_start=coefficients+8+sum(4+4*n for n in window.SIZES)
    ready=adapter_start+52+64*8;ready_product=ready+52+128*8
    genuine=next(i for i,row in enumerate(m['scalars']) if row['operands'])
    changed_pcm=bytearray(body[ready_product+64:ready_product+66]);changed_pcm[0]^=1
    edits=[('magic',0,b'X'),('legacy-source',52,bytes(8)),
        ('legacy-PCM',52+16*65538,bytes(2)),('scalar-index',scalar_start,struct.pack('<I',99)),
        ('scalar-product',scalar_start+4,bytes(8)),('scalar-base',scalar_start+20,struct.pack('<q',1)),
        ('genuine-tail-PCM',scalar_start+genuine*74+72,bytes(2)),
        ('coefficient',coefficients+8,struct.pack('<d',math.nan)),
        ('signed-origin',adapter_start+48,struct.pack('<i',-1)),
        ('unwindowed-source',adapter_start+52,bytes(8)),('window-product',ready_product,bytes(8)),
        ('adapter-PCM',ready_product+64,bytes(changed_pcm))]
    damaged=[(name,body[:at]+replacement+body[at+len(replacement):]) for name,at,replacement in edits]
    damaged.extend([('truncated',body[:-1]),('trailing',body+b'X')])
    need(all(bad!=body for _,bad in damaged),'every declared corruption changes actual capture bytes')
    for name,bad in damaged:
        try:compare(bad,m,window,sine)
        except (ValueError,struct.error):continue
        raise ValueError('corrupted exact PCM capture accepted: '+name)
    return [name for name,_ in damaged]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh task-local output');out.mkdir(parents=True)
    report=dict(completed=False,passed=False,commands=[],sources={},sanitizers=['address','undefined'],native_executed=False,
        production_selected=False,old_overlap_API_executed=False,old_PCM_API_executed=False,deferred_scopes_resumed=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,label):
        b=path.read_bytes();p=out/'sources'/label;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);report['sources'][label]=sha(b);return b
    def data(b,label):
        p=out/'sources'/label;p.write_bytes(b);report['sources'][label]=sha(b)
    def run(name,argv):
        timeout=180 if name=='execute' else 60;nonce=uuid.uuid4().hex
        request,receipt,stop=(out/(name+s) for s in ('.request.json','.receipt.json','.stop'))
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=timeout,receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command=(['wsl.exe','--exec','python3'] if os.name=='nt' else [sys.executable])+[linux(out/'supervisor.py'),linux(request)]
        row=dict(name=name,argv=command,child_argv=list(map(str,argv)),nonce=nonce,request_sha256=sha(request.read_bytes()))
        report['commands'].append(row);save();child=None;started=time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as so,(out/(name+'.stderr.log')).open('xb') as se:
                child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=so,stderr=se,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                row['transport_pid']=child.pid;child.wait(timeout=220 if name=='execute' else 80)
        finally:
            if child is not None and child.poll() is None:
                stop.write_text(nonce,encoding='ascii')
                try:child.wait(timeout=15)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5);row['forced_transport_stop']=True
            receipt_body=json.loads(receipt.read_bytes()) if receipt.exists() else {}
            row.update(elapsed_seconds=time.monotonic()-started,supervisor=receipt_body,transport_exit=None if child is None else child.poll());save()
        need(row['transport_exit']==0 and not row.get('forced_transport_stop'),'owned transport terminal: '+name)
        need(receipt_body.get('nonce')==nonce and receipt_body.get('request_sha256')==row['request_sha256'] and receipt_body.get('state')=='terminal' and
            receipt_body.get('final') and receipt_body.get('new_session') and receipt_body.get('child_pid')==receipt_body.get('owned_pgid') and
            receipt_body.get('child_reaped') and receipt_body.get('group_gone') and receipt_body.get('child_returncode')==0,'owned child terminal: '+name)
        return (out/(name+'.stdout.log')).read_text('utf-8')
    save()
    try:
        freeze(Path(__file__),'runner.py')
        for name in COMPONENTS:
            for path in sorted((ROOT/'idf/components'/name).rglob('*')):
                if path.is_file():freeze(path,'components/'+name+'/'+path.relative_to(ROOT/'idf/components'/name).as_posix())
        for name in ('vorbis_window_host.c','vorbis_pcm_exact_host.c'):freeze(ROOT/'tests/native'/name,'native/'+name)
        for label,(name,pin) in PINS.items():need(sha(freeze(ROOT/'tests'/name,label))==pin,'frozen local pure reader')
        modules=helpers(out/'sources');legacy=modules['legacy-reader.py'];window=modules['window-reader.py'];sine=modules['sine-oracle.py']
        old_input,old_capture,old_report=saved_pcm();overlap,overlap_report=saved_overlap(window)
        for b,label in ((old_input,'saved-pcm-input.bin'),(old_capture,'saved-pcm-capture.bin'),(old_report,'saved-pcm-report.json'),
            (overlap,'saved-overlap-capture.bin'),(overlap_report,'saved-overlap-report.json')):data(b,label)
        m=model(legacy,window,old_input,old_capture,overlap);report['fraction_anchors']=fraction_anchors()
        report['legacy_fraction_anchors']=legacy.fraction_anchors();report['witnesses']=m['witness_metrics']
        scalar_digest=sha((json.dumps(m['scalars'],separators=(',',':'))+'\n').encode())
        recipe=dict(schema='owned-exact-PCM-scalar-recipe-v1',rows=len(m['scalars']),half_boundaries=65538,
            half_perturbation_variants=3,widths=list(range(1,107)),shifts=[-2148,0,1023],
            genuine_tail_rows=4,wide_merge_matrix_rows=432,wide_merge_widths=[64,65,105,106],
            normalized_exponent_distances=[0,1,2],model_sha256=scalar_digest)
        (out/'scalar-recipe.json').write_text(json.dumps(recipe,indent=2)+'\n',encoding='utf-8',newline='\n')
        (out/'input.bin').write_bytes(encode(m));report.update(input_sha256=sha((out/'input.bin').read_bytes()),scalar_model_sha256=scalar_digest)
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py')
        templates=[ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SUPERVISOR' for t in node.targets)]
        need(len(templates)==1 and templates[0].count('assert 0<timeout<=60')==1,'single documented watchdog limit adjustment')
        (out/'supervisor.py').write_text(templates[0].replace('assert 0<timeout<=60','assert 0<timeout<=180'),encoding='utf-8',newline='\n')
        report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes());save();report['compiler_version']=run('compiler-version',['gcc','--version'])
        units=[out/'sources/components'/name/file for name,file in (
            ('native_vorbis_window','window.c'),('native_vorbis_window_exact','product.c'),('native_vorbis_window_exact','view.c'),
            ('native_vorbis_pcm_exact','pcm.c'),('native_vorbis_pcm_exact','windows.c'))]+[out/'sources/native/vorbis_pcm_exact_host.c']
        flags=['gcc','-std=c11','-O1','-g','-UNDEBUG','-fno-fast-math','-ffp-contract=off','-fno-pie','-no-pie',
            '-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-ffunction-sections','-fdata-sections',
            '-Wall','-Wextra','-Werror',*['-I'+linux(out/'sources/components'/name/'include') for name in COMPONENTS]]
        run('compile',[*flags,*map(linux,units),'-Wl,--gc-sections','-lm','-o',linux(out/'pcm-exact')])
        text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',linux(out/'pcm-exact'),linux(out/'input.bin'),linux(out/'capture.bin')])
        match=re.fullmatch(r'PCM_EXACT batches=2479 scalars=(\d+) adapters=864 refusals=(\d+) checks=(\d+)\s*',text)
        need(match is not None and int(match[1])==len(m['scalars']) and not (out/'execute.stderr.log').read_bytes(),'guarded complete capture')
        measured=compare((out/'capture.bin').read_bytes(),m,window,sine)
        report['corruption_controls']=corruption_controls((out/'capture.bin').read_bytes(),m,window,sine)
        for label,pin in report['sources'].items():need(sha((out/'sources'/label).read_bytes())==pin,'frozen sources/data unchanged')
        report.update(completed=True,passed=True,measurements=measured,controls=dict(scalars=int(match[1]),refusals=int(match[2]),checks=int(match[3])),
            capture_sha256=sha((out/'capture.bin').read_bytes()),binary_sha256=sha((out/'pcm-exact').read_bytes()))
        save();print(json.dumps(dict(passed=True,controls=report['controls'],measurements=measured)));return 0
    except BaseException as error:report['error']=repr(error);save();raise


if __name__=='__main__':raise SystemExit(main())
