"""Independent Fraction qualification of the selected basic arithmetic owner."""
import argparse,ast,hashlib,json,math,os,re,subprocess,sys,time,uuid
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SUPERVISOR_ORIGIN_SHA='df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2'
COMPONENT_SHA='dc848de646f25ff5a8a4997cd422718e23ace867502b19e6062ca22887a4d93a'
HEADER_SHA='379726cc07f1fcbb2ecc1512c08ea077085fea12828cd96afd9fa0cca61013c1'
UPSTREAM_ARCHIVE_SHA='4b23394d67a4a3c3266a38b66831094523fffb5d01974a5c05a0327b36b0a340'
MANIFEST_SHA='edc6d65b51c205bfcc3c2fe1e58f0b012d265cb00337667417688baf0f097a77'
PORTABLE_SHA='158da48780e54571ae2ce56ef7049f9829f62817c005009c9018bdf74d92a378'
PATCH_SHA='cd15a88f0718bb2f18e2b8b269a57983315ef28617b2e836b3bba07391389a42'

def need(test,message):
    if not test:raise ValueError(message)
def sha(body):return hashlib.sha256(body).hexdigest()
def linux(path):
    p=Path(path).resolve().as_posix();return '/mnt/'+p[0].lower()+p[2:] if sys.platform=='win32' else p
def dyadic(sign,magnitude,exponent):
    value=Fraction(magnitude<<exponent) if exponent>=0 else Fraction(magnitude,1<<-exponent)
    return -value if sign else value
def canonical(sign,magnitude,exponent):
    if not magnitude:return (0,0,0)
    shift=(magnitude&-magnitude).bit_length()-1
    return (int(bool(sign)),magnitude>>shift,exponent+shift)
def top_bit(value):
    need(value>0,'positive rational top bit');n,d=value.numerator,value.denominator;top=n.bit_length()-d.bit_length()
    if (n<d<<top) if top>=0 else (n<<-top<d):top-=1
    return top
def rounded(value,precision,direction):
    need(precision>=1 and direction in (-1,1),'independent precision/direction domain')
    if not value:return (0,0,0)
    negative=value<0;value=abs(value);exponent=top_bit(value)+1-precision
    n,d=value.numerator,value.denominator
    if exponent>=0:d<<=exponent
    else:n<<=-exponent
    magnitude,remainder=divmod(n,d)
    if remainder and ((direction>0)^negative):magnitude+=1
    return canonical(negative,magnitude,exponent)
def rounded_sqrt(value,precision,direction):
    need(value>=0 and precision>=1 and direction in (-1,1),'independent square-root domain')
    if not value:return (0,0,0)
    exponent=top_bit(value)//2+1-precision;n,d=value.numerator,value.denominator
    if exponent>=0:d<<=2*exponent
    else:n<<=-2*exponent
    magnitude=math.isqrt(n//d)
    if direction>0 and magnitude*magnitude*d!=n:magnitude+=1
    return canonical(0,magnitude,exponent)
def dense(width,seed):
    need(width>0,'positive dense input width');value=0;state=seed
    for at in range(0,width,64):
        state=(6364136223846793005*state+1442695040888963407)&((1<<64)-1);value|=state<<at
    return (value&((1<<width)-1))|(1<<(width-1))|1

def corpus(ntt_width):
    rows=[]
    def add(operation,precision,direction,a,b=(0,0,0),sweep=False,label=''):
        rows.append(dict(id=len(rows),operation=operation,precision=precision,direction=direction,a=a,b=b,sweep=bool(sweep),label=label))
    # Preserve unsigned magnitudes on import, including the signed64 endpoint.
    for magnitude in (0,1,2,3,(1<<31)-1,1<<31,(1<<32)-1,1<<32,(1<<63)-1,1<<63,(1<<64)-1):
        for sign in (0,1):
            for exponent in (-1074,-65,-1,0,31,1023):add('add',128,-1,(sign,magnitude,exponent),label='unsigned-import')
    widths=(1,2,3,7,31,32,33,53,63,64,65,106,127,128,129,257)
    precisions=(2,2,3,7,24,31,32,33,53,63,64,65,106,113,128,257)
    for i,(width,precision) in enumerate(zip(widths,precisions)):
        m=dense(width,0xb16bf+i);n=dense(max(1,width-1),0xcafe+i)
        for sign in (0,1):
            a=(sign,m,-width//2);b=(1-sign,n,-width//2-3)
            for direction in (-1,1):
                for operation in ('add','sub','mul','div'):add(operation,precision,direction,a,b,label='width-precision-sign-matrix')
                add('sqrt',precision,direction,(0,m,-width//2),label='sqrt-significand-matrix')
                add('add',precision,direction,a,(1-sign,m,a[2]),label='exact-cancellation')
    for precision in (2,3,24,53,64,65,113,257):
        for direction in (-1,1):
            for delta in (-1,0,1):
                m=(1<<(precision+4))+delta
                add('add',precision,direction,(0,m,-precision-4),(0,1,-4*precision-17),label='positive-round-boundary')
                add('sub',precision,direction,(1,m,-precision-4),(0,1,-4*precision-17),label='negative-round-boundary')
                square=((1<<(precision+3))+1)**2+delta
                add('sqrt',precision,direction,(0,square,-2*precision-6),label='perfect-square-neighbors')
    for sign,m,e in ((1,1,-1),(1,3,-1),(1,(1<<64)-1,-64),(0,(1<<64)-1,-64),(1,1<<63,0),(0,(1<<64)-1,0),
                     (1,dense(257,7),-129),(0,dense(257,8),-129)):
        add('floor',2,-1,(sign,m,e),sweep=True,label='integer-floor-not-truncation')
    for operation,a,b in (('div',(0,1,0),(0,0,0)),('div',(0,0,0),(0,0,0)),('sqrt',(1,1,-1),(0,0,0))):
        add(operation,53,-1,a,b,sweep=True,label='invalid-domain')
    for operation in ('add','sub','mul','div','sqrt'):
        for direction in (-1,1):add(operation,113,direction,(0,dense(257,0x4321),-127),(0,dense(193,0x9876),-91),sweep=True,label='allocation-refusal-recovery')
    # Dense long operands and retained precision, not a large precision request
    # applied to small operands. The selected source threshold fixes this width.
    for direction in (-1,1):
        a=(0,dense(ntt_width,0x123456),-ntt_width//2);b=(1,dense(ntt_width,0xabcdef),-ntt_width//2-1)
        add('mul',8192,direction,a,b,sweep=True,label='NTT-dense-product')
        add('div',8192,direction,a,b,sweep=True,label='high-precision-division')
        add('sqrt',8192,direction,a,sweep=True,label='high-precision-sqrt')
    for value in (0,1,1<<63,(1<<64)-1):add('u64',64,-1,(0,value,0),sweep=True,label='direct-unsigned-import')
    for operation in ('copy','round','import'):
        for direction in (-1,1):add(operation,53,direction,(1,dense(257,123),-131),sweep=True,label='owned-copy-round-import')
    add('add',1048576,-1,(0,1,0),label='maximum-valid-precision-small-operands')
    add('round',8193,1,(0,13,-3),label='above-old-conservative-ceiling-valid')
    need(len(rows)==699,'retain the complete original699 arithmetic rows before targeted supplement')
    # Earlier NTT results already export wider integer floors. These two rows
    # specifically distinguish all-ones positive floor from negative carry.
    for sign in (0,1):add('floor',2,-1,(sign,(1<<4096)-1,-2524),sweep=True,label='1572-bit-all-ones-fractional-carry')
    return rows

def expected(row):
    a=dyadic(*row['a']);b=dyadic(*row['b']);op=row['operation']
    if op=='div' and not b or op=='sqrt' and a<0:return dict(status=-4)
    if op=='sqrt':value=rounded_sqrt(a,row['precision'],row['direction'])
    elif op in ('floor','copy','u64','import'):value=canonical(*row['a'])
    elif op=='round':value=rounded(a,row['precision'],row['direction'])
    else:
        value={'add':lambda:a+b,'sub':lambda:a-b,'mul':lambda:a*b,'div':lambda:a/b}[op]()
        value=rounded(value,row['precision'],row['direction'])
    result=dyadic(*value)
    return dict(status=0,value=value,floor=result.numerator//result.denominator)

def encode(rows):
    lines=['VBFCASE1 '+str(len(rows))]
    for row in rows:
        a,b=row['a'],row['b'];lines.append(' '.join(map(str,(row['id'],row['operation'],row['precision'],row['direction'],int(row['sweep']),
            a[0],a[2],format(a[1],'x'),b[0],b[2],format(b[1],'x')))))
    return ('\n'.join(lines)+'\n').encode('ascii')

def compare(body,rows,limb_bits):
    text=body.decode('ascii');lines=text.splitlines();at=0
    def line(tag,count):
        nonlocal at
        need(at<len(lines),'complete arithmetic record');parts=lines[at].split(' ');at+=1
        need(len(parts)==count and parts[0]==tag and all(parts),'strict arithmetic record: '+tag);return parts
    need(line('BFBEGIN',4)==['BFBEGIN','1',str(limb_bits),str(len(rows))],'limb model and complete input row count')
    def value(parts,start):
        negative,exponent,magnitude,floor_negative,floor_magnitude=parts[start:start+5]
        need(negative in ('0','1') and floor_negative in ('0','1') and re.fullmatch(r'0|[1-9a-f][0-9a-f]*',magnitude) and
            re.fullmatch(r'0|[1-9a-f][0-9a-f]*',floor_magnitude),'canonical exact ASCII signs/magnitudes')
        n,e,m,fn,fm=int(negative),int(exponent),int(magnitude,16),int(floor_negative),int(floor_magnitude,16)
        need((m&1 if m else not n and not e) and (fm or not fn),'odd dyadic and canonical integer zero')
        return (n,m,e),-fm if fn else fm
    def wanted(row):
        expected_value=expected(row)
        if expected_value['status']:return expected_value['status'],(0,13,-3),1
        return 0,expected_value['value'],expected_value['floor']
    measured=[];oom=[];refusals=aliases=capacity=0;ntt_entries=[]
    for row in rows:
        parts=line('BFROW',12);need(int(parts[1])==row['id'],'all ordered original arithmetic rows');status,d,f=wanted(row)
        need(int(parts[2])==status and value(parts,3)==(d,f),'exact independently directed Fraction/isqrt result and negative integer floor')
        attempts,ntt_before,ntt_after,peak=map(int,parts[8:12]);need(attempts>=0 and ntt_before==0 and ntt_after in (0,1) and peak>0,'fresh independent engine context and real allocator statistics')
        if row['label']=='NTT-dense-product':need(ntt_after==1,'actual NTT state initialized by dense8192-bit multiply');ntt_entries.append(row['id'])
        if row['label']=='maximum-valid-precision-small-operands':need(ntt_after==0,'large precision alone is not NTT execution')
        magnitude_words=(d[1].bit_length()+31)//32;floor_words=(abs(f).bit_length()+31)//32
        capacity+=sum(len({0,count-1}) for count in (magnitude_words,floor_words) if count)
        if not status and row['operation'] not in ('import','u64'):aliases+=1+int(row['operation'] in ('add','sub','mul','div'))
        count=attempts if row['sweep'] else 0
        for ordinal in range(1,count+1):
            record=line('BFOOM',17);need(tuple(map(int,record[1:3]))==(row['id'],ordinal) and int(record[3])>0,'every actual allocation ordinal refused')
            need(value(record,4)==((0,13,-3),1) and value(record,9)==(d,f),'every refused destination unchanged and every recovered exact dyadic/floor rechecked')
            allocated,released,live=map(int,record[14:17]);need(allocated==released and allocated>0 and live==0,'every allocation refusal and recovery cleans up completely')
            oom.append(dict(row=row['id'],ordinal=ordinal,requested_bytes=int(record[3]),allocations=allocated));refusals+=1
        measured.append(dict(id=row['id'],status=status,attempts=attempts,ntt=bool(ntt_after),peak_bytes=peak))
    need(line('BFGUARD',2)==['BFGUARD','18'],'all explicit precision/domain/context/extent/lifecycle preflight controls')
    terminal=list(map(int,line('BFEND',10)[1:]));cases,failed,exports,capacity_checks,alias_checks,checks,peak,live,remaining=terminal
    need(at==len(lines) and cases==len(rows) and failed==refusals and alias_checks==aliases and capacity_checks==capacity+2 and
        exports==len(rows)+aliases+2*refusals+2 and checks>0 and peak>=max(r['peak_bytes'] for r in measured) and live==remaining==0,
        'complete arithmetic transcript, actual refusal/export/capacity/alias totals and terminal cleanup')
    need(len(ntt_entries)==2,'both directed dense-product NTT cases retained')
    return dict(passed=True,limb_bits=limb_bits,cases=cases,allocation_refusals=refusals,guards=18,exports=exports,
        capacity_refusals=capacity_checks,alias_checks=aliases,checks=checks,peak_allocator_bytes=peak,ntt_rows=ntt_entries,rows=measured,refusals=oom,
        oracle='Python Fraction with exact integer quotient/remainder and integer-isqrt; no production limb algorithm',
        transcendental_gain_certified=False,production_selected=False)

def corruption_controls(body,rows,limb_bits):
    lines=body.decode('ascii').splitlines();controls=[]
    def reject(name,changed):
        candidate=('\n'.join(changed)+'\n').encode('ascii')
        try:compare(candidate,rows,limb_bits)
        except (ValueError,IndexError,OverflowError):controls.append(dict(name=name,rejected=True));return
        raise ValueError('accepted corrupted arithmetic evidence: '+name)
    reject('missing-summary',lines[:-1]);reject('extra-record',lines+['BFEND 0'])
    changed=lines.copy();p=changed[0].split();p[2]='16';changed[0]=' '.join(p);reject('wrong-limb-model',changed)
    index=next(i for i,line in enumerate(lines) if line.startswith('BFROW ') and line.split()[5]!='0')
    changed=lines.copy();p=changed[index].split();p[5]=format(int(p[5],16)+2,'x');changed[index]=' '.join(p);reject('directed-result',changed)
    changed=lines.copy();p=changed[index].split();p[7]=format(int(p[7],16)+1,'x');changed[index]=' '.join(p);reject('integer-floor',changed)
    index=next(i for i,line in enumerate(lines) if line.startswith('BFOOM '))
    changed=lines.copy();p=changed[index].split();p[2]='0';changed[index]=' '.join(p);reject('refusal-ordinal',changed)
    changed=lines.copy();p=changed[index].split();p[6]='f';changed[index]=' '.join(p);reject('refused-destination',changed)
    index=next(i for i,line in enumerate(lines) if line.startswith('BFROW ') and int(line.split()[1]) in {r['id'] for r in rows if r['label']=='NTT-dense-product'})
    changed=lines.copy();p=changed[index].split();p[10]='0';changed[index]=' '.join(p);reject('actual-NTT-branch',changed)
    changed=lines.copy();changed[-2]='BFGUARD 17';reject('preflight-count',changed)
    changed=lines.copy();p=changed[-1].split();p[2]=str(int(p[2])+1);changed[-1]=' '.join(p);reject('terminal-refusal-total',changed)
    return controls

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    out=args.output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh task-local arithmetic output');out.mkdir(parents=True)
    report=dict(completed=False,passed=False,commands=[],sources={},sanitizers=['address','undefined'],production_selected=False,transcendental_gain_certified=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,label):
        body=path.read_bytes();destination=out/'sources'/label;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(body);report['sources'][label]=sha(body);return body
    def run(name,argv):
        nonce=uuid.uuid4().hex;request,receipt,stop=(out/(name+s) for s in ('.request.json','.receipt.json','.stop'));timeout=180 if name.startswith('execute') else 60
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=timeout,receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command=(['wsl.exe','--exec','python3'] if os.name=='nt' else [sys.executable])+[linux(out/'supervisor.py'),linux(request)]
        row=dict(name=name,argv=command,child_argv=list(map(str,argv)),nonce=nonce,request_sha256=sha(request.read_bytes()));report['commands'].append(row);save();child=None;start=time.monotonic()
        try:
            with (out/(name+'.stdout.log')).open('xb') as so,(out/(name+'.stderr.log')).open('xb') as se:
                child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=so,stderr=se,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0);row['transport_pid']=child.pid;child.wait(timeout=220 if name.startswith('execute') else 80)
        finally:
            if child is not None and child.poll() is None:
                stop.write_text(nonce,encoding='ascii')
                try:child.wait(timeout=15)
                except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5);row['forced_transport_stop']=True
            s=json.loads(receipt.read_bytes()) if receipt.exists() else {};row.update(elapsed_seconds=time.monotonic()-start,supervisor=s,transport_exit=None if child is None else child.poll());save()
        need(row['transport_exit']==0 and not row.get('forced_transport_stop'),'owned arithmetic transport terminal: '+name)
        need(s.get('nonce')==nonce and s.get('request_sha256')==row['request_sha256'] and s.get('state')=='terminal' and s.get('final') and s.get('new_session') and
            s.get('child_pid')==s.get('owned_pgid') and s.get('child_reaped') and s.get('group_gone') and s.get('child_returncode')==0,'owned arithmetic child terminal: '+name)
        return (out/(name+'.stdout.log')).read_bytes()
    save()
    try:
        freeze(Path(__file__),'runner.py');component=ROOT/'idf/components/native_vorbis_bigfloat'
        for path in sorted(component.rglob('*')):
            if path.is_file():freeze(path,'component/'+path.relative_to(component).as_posix())
        need(report['sources']['component/bigfloat.c']==COMPONENT_SHA and report['sources']['component/include/native_vorbis_bigfloat.h']==HEADER_SHA,'reviewed selected arithmetic source/header')
        manifest_body=(out/'sources/component/upstream-manifest.json').read_bytes();need(sha(manifest_body)==MANIFEST_SHA,'pinned creator/portability inventory');manifest=json.loads(manifest_body)
        need(manifest['archive_sha256']==UPSTREAM_ARCHIVE_SHA and len(manifest['modifications'])==2,'two explicit portability adaptations, original creator source retained')
        for entry in manifest['files']:
            body=(out/'sources/component'/entry['path']).read_bytes();need(len(body)==entry['bytes'] and sha(body)==entry['sha256'],'unchanged upstream bytes: '+entry['path'])
        original=(out/'sources/component/upstream/libbf.c').read_bytes();portable=(out/'sources/component/portable/libbf.c').read_bytes();patch=(out/'sources/component/portability.patch').read_bytes()
        old=b'    return bf_get_int32(pres, a, flags);';new=b'    int value;\n    int status = bf_get_int32(&value, a, flags);\n    *pres = value;\n    return status;'
        copy_old=b'    memcpy(r->tab, a->tab, a->len * sizeof(limb_t));';copy_new=b'    if (a->len != 0)\n        memcpy(r->tab, a->tab, a->len * sizeof(limb_t));'
        need(original.count(old)==1 and original.count(copy_old)==1 and portable==original.replace(old,new).replace(copy_old,copy_new) and sha(portable)==PORTABLE_SHA and sha(patch)==PATCH_SHA,
            'exact native pointer adaptation and zero-length-copy guard, each once, without upstream byte changes')
        freeze(ROOT/'tests/native/vorbis_bigfloat_host.c','native/vorbis_bigfloat_host.c')
        rows=corpus(8192);(out/'cases.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8',newline='\n');(out/'input.txt').write_bytes(encode(rows));report.update(input_sha256=sha((out/'input.txt').read_bytes()),cases_sha256=sha((out/'cases.json').read_bytes()),case_count=len(rows),NTT_operand_bits=8192)
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py');need(sha(origin)==SUPERVISOR_ORIGIN_SHA,'pinned owned process supervisor')
        templates=[ast.literal_eval(n.value) for n in ast.parse(origin).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SUPERVISOR' for t in n.targets)]
        need(len(templates)==1 and templates[0].count('assert 0<timeout<=60')==1,'one documented timeout-only supervisor replacement')
        (out/'supervisor.py').write_text(templates[0].replace('assert 0<timeout<=60','assert 0<timeout<=180'),encoding='utf-8',newline='\n');report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes());save()
        compiler=run('compiler-version',['gcc','--version']).decode('ascii');need(compiler.splitlines()[0]=='gcc (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0','pinned installed WSL GCC version');report['compiler_version']=compiler
        units=[*sorted((out/'sources/component').glob('*.c')),out/'sources/component/portable/libbf.c',out/'sources/component/upstream/cutils.c',out/'sources/native/vorbis_bigfloat_host.c']
        need(any(path.name=='bigfloat.c' for path in units),'selected checked arithmetic source present')
        base=['gcc','-std=c11','-O1','-g','-UNDEBUG','-fno-fast-math','-ffp-contract=off','-fno-pie','-no-pie','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer',
            '-ffunction-sections','-fdata-sections','-Wall','-Wextra','-I'+linux(out/'sources/component/include'),'-I'+linux(out/'sources/component/upstream')]
        measurements={};corruptions={}
        for limb_bits in (64,32):
            selection=[] if limb_bits==64 else ['-U__SIZEOF_INT128__'];name='limb'+str(limb_bits);binary=out/name
            objects=[]
            for unit in units:
                obj=out/(name+'-'+unit.stem+'.o');objects.append(obj);owned=unit.name in ('bigfloat.c','vorbis_bigfloat_host.c')
                run('compile-'+name+'-'+unit.stem,[*base,*selection,*(['-Werror'] if owned else []),'-c',linux(unit),'-o',linux(obj)])
            run('link-'+name,[*base,*selection,*map(linux,objects),'-Wl,--gc-sections','-lm','-o',linux(binary)])
            body=run('execute-'+name,['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',linux(binary),linux(out/'input.txt')])
            need(not (out/('execute-'+name+'.stderr.log')).read_bytes(),'no arithmetic sanitizer or runtime diagnostics')
            measured=compare(body,rows,limb_bits);measurements[name]=measured;corruptions[name]=corruption_controls(body,rows,limb_bits);report.update(measurements=measurements,corruption_controls=corruptions);save()
        for label,pin in report['sources'].items():need(sha((out/'sources'/label).read_bytes())==pin,'frozen arithmetic source immutability')
        need([(r['id'],r['status']) for r in measurements['limb64']['rows']]==[(r['id'],r['status']) for r in measurements['limb32']['rows']],'same complete corpus and domain outcomes on both limb models')
        report.update(completed=True,passed=True);save();print(json.dumps(dict(passed=True,cases=len(rows),models={k:{n:v[n] for n in ('limb_bits','allocation_refusals','guards','capacity_refusals','alias_checks','checks','peak_allocator_bytes','ntt_rows')} for k,v in measurements.items()})));return 0
    except BaseException as error:report['error']=repr(error);save();raise

if __name__=='__main__':raise SystemExit(main())
