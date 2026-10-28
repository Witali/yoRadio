"""Integer-only granule/EOS qualification, unlimited model and pinned Xiph slice.

Only metadata is executed. No decoder, overlap, PCM, deferred controller,
SDK/QEMU or production radio is invoked. Original31 means saved434 metadata
events and frame counts, not a new PCM qualification.
"""
import argparse,ast,hashlib,io,json,os,random,re,struct,subprocess,sys,time,uuid,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAX=(1<<63)-1
CAP=MAX+4096
BLOCK_SHA='7f65c7031c2b94405d2c1b5f0a73cc19efe9506e95736ba0b38d86bd42170a7e'
ORIGINAL_SHA='32ba4c7e401fcfd05238f929fa6874c3048237792d78f36b05a8fade5b861e24'
PRIOR_SHA='0e3682f21e327d13308e2c771ae6cb286c224d49ed779ce93ef2a55622d4ea87'
FIELDS=('short','long','previous','known','eos','total','prediction')


def need(test,message):
    if not test:raise ValueError(message)


def sha(body):return hashlib.sha256(body).hexdigest()
def linux(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def initial(s,l):return dict(zip(FIELDS,(s,l,0,0,0,0,0)))
def bounded(state):
    return tuple(state[k] if k not in ('total','prediction') else min(state[k],CAP) for k in FIELDS)


def apply(state,event):
    # Unlimited integers; capping happens only in the capture projection above.
    n,g,eos,gap=event
    available=(state['previous']+n)//4 if state['previous'] else 0
    total=0 if not state['previous'] or gap else state['total']+available
    predicted=None if not state['known'] or gap or not state['previous'] else state['prediction']+available
    head=tail=0
    if predicted is None:
        if g>=0:
            excess=min(available,max(total-g,0))
            if eos:tail=excess
            else:head=excess
            predicted=g
    elif g>=0:
        if eos:tail=min(available,max(predicted-g,0))
        predicted=g
    following=dict(state,previous=n,total=total,known=int(predicted is not None),
                   prediction=0 if predicted is None else predicted,eos=state['eos']|eos)
    kind=0 if predicted is None else 2 if predicted>MAX else 1
    result=(available,head,tail,available-head-tail,kind,predicted if kind==1 else 0)
    return following,result


def reference_safe(state,event):
    n,g,eos,gap=event
    available=(state['previous']+n)//4 if state['previous'] else 0
    return (state['total']<=MAX and state['prediction']<=MAX and
        (gap or not state['previous'] or state['total']+available<=MAX) and
        (gap or not state['known'] or state['prediction']+available<=MAX))


def corpus(original):
    commands=[];current=None
    def init(s,l,label):
        nonlocal current
        commands.append(dict(action=0,label=label,seed=initial(s,l),event=(0,0,0,0),reference=False))
        current=initial(s,l)
    def push(n,g=-1,eos=0,gap=0,label='',seed=None,original=None):
        nonlocal current
        if seed is not None:current=seed.copy()
        event=(n,g,eos,gap)
        row=dict(action=3 if seed is not None else 1,label=label,
                 seed=seed,event=event,reference=reference_safe(current,event))
        if original is not None:row['original']=original
        commands.append(row);current,_=apply(current,event)
    def reset(label):
        nonlocal current
        commands.append(dict(action=2,label=label,seed=None,event=(0,0,0,0),reference=False))
        current=initial(current['short'],current['long'])
    for short_index in range(8):
        for long_index in range(short_index,8):
            s,l=64<<short_index,64<<long_index
            for a in (s,l):
                for b in (s,l):
                    span=(a+b)//4
                    for eos in (0,1):
                        init(s,l,f'first-{a}-{b}-{eos}')
                        push(a,label='prime-unknown')
                        push(b,max(0,span-1),eos,label='first-known-end' if eos else 'first-known-start')
                        push(a,label='unknown-after-anchor')
                        push(b,0,1,label='backdated-eos-clamps-current')
                        push(a,MAX,0,label='forward-nonEOS')
                        push(b,MAX,1,label='MAX-after-increment-EOS')
                        push(a,-1,1,label='unknown-EOS')
                        push(b,17,0,label='nonEOS-backdate-resync')
                        push(a,-1,0,1,label='gap-retains-ready-span')
                        push(b,7,1,label='first-known-after-gap')
                        reset('hard-reset')
                        push(b,0,label='restart-prime-zero')
                        push(a,span+32,label='positive-inferred-start')
                    init(s,l,'late-first-anchor')
                    for n in (a,b,a,b,a,b):push(n,label='unset-run')
                    push(b,0,0,label='late-first-start-clamp')
            seeds=(MAX-4097,MAX-4096,MAX-1,MAX,MAX+1,CAP-1,CAP,CAP+1,CAP+4097,CAP+(1<<80))
            for exact in seeds:
                for known in (0,1):
                    seed=dict(initial(s,l),previous=l,known=known,total=exact,prediction=exact if known else 0)
                    push(s,label='seeded-unbounded-arithmetic',seed=seed)
                    push(l,MAX,1,label='future-MAX-anchor')
                    push(s,label='future-unknown-prediction')
                    push(l,0,0,label='future-nonEOS-anchor')
                    push(s,-1,0,1,label='future-gap')
                    push(l,1,1,label='future-gap-anchor')
    rng=random.Random(0x4752414e554c45)
    for stream in range(150):
        x,y=sorted((rng.randrange(8),rng.randrange(8)));s,l=64<<x,64<<y
        init(s,l,f'random-stream-{stream}')
        for packet in range(64):
            n=(s,l)[rng.randrange(2)];g=rng.choice((-1,-1,0,rng.randrange(100000),MAX,MAX-4096))
            push(n,g,rng.randrange(2),int(rng.randrange(17)==0),label=f'random-{stream}-{packet}')
            if packet in (20,41):reset('random-hard-reset')
    need(len(original['cases'])==31,'all original31 streams')
    for stream in original['cases']:
        init(stream['short_block'],stream['long_block'],'original31-'+stream['id'])
        need(len(stream['modes'])==len(stream['granules'])==len(stream['frames']),'original aligned metadata')
        for packet,(mode,g,frames) in enumerate(zip(stream['modes'],stream['granules'],stream['frames'])):
            push(stream['long_block'] if mode else stream['short_block'],g,
                 int(packet+1==len(stream['modes'])),label='original31-'+stream['id']+'-'+str(packet),
                 original=dict(id=stream['id'],packet=packet,frames=frames))
    need(sum('original' in row for row in commands)==434,'all original434 packet metadata')
    return commands


def encode(model):
    body=bytearray(b'VTIMIN01'+struct.pack('<I',len(model)))
    for row in model:
        seed=row['seed'] or initial(0,0)
        body.extend(struct.pack('<II5I2QIqII',row['action'],int(row['reference']),*bounded(seed),*row['event']))
    return bytes(body)


def inspect_capture(body,model):
    need(body[:12]==b'VTIMOUT1'+struct.pack('<I',len(model)),'complete ordered timing capture')
    offset=12;current=initial(0,0)
    references=packets=priming=resets=gaps=head_rows=tail_rows=seeded=exceeds=original_frames=0
    head_samples=tail_samples=available_samples=kept_samples=0;original_ids=set();transitions=set();caps=0
    for row in model:
        need(offset+160<=len(body),'complete fixed timing record')
        action,status,used=struct.unpack_from('<II I',body,offset);offset+=12
        before=struct.unpack_from('<5I2Q',body,offset);offset+=36
        event=struct.unpack_from('<IqII',body,offset);offset+=20
        after=struct.unpack_from('<5I2Q',body,offset);offset+=36
        result=struct.unpack_from('<5Iq',body,offset);offset+=28
        ref=struct.unpack_from('<5Iq',body,offset);offset+=28
        if row['seed'] is not None and action==3:current=row['seed'].copy();seeded+=1
        need((action,status,used)==(row['action'],0,int(row['reference'])),'ordered action/status/reference')
        need(before==bounded(current) and event==tuple(row['event']),'every state/event input field')
        if action==0:
            current=initial(row['seed']['short'],row['seed']['long']);wanted=(0,)*6
        elif action==2:
            current=initial(current['short'],current['long']);wanted=(0,)*6;resets+=1
        else:
            old_previous=current['previous'];current,wanted=apply(current,event);packets+=1
            gaps+=event[3];priming+=not old_previous;head_rows+=wanted[1]>0;tail_rows+=wanted[2]>0
            head_samples+=wanted[1];tail_samples+=wanted[2];available_samples+=wanted[0];kept_samples+=wanted[3]
            exceeds+=wanted[4]==2
            if old_previous:transitions.add((old_previous,event[0]))
            if 'original' in row:
                need(wanted[3]==row['original']['frames'],'retained original per-packet frame count')
                original_ids.add(row['original']['id']);original_frames+=wanted[3]
        need(after==bounded(current) and result==wanted,'unlimited timeline projection and every trim field')
        if used:
            need(ref==wanted,'unchanged Xiph metadata slice agrees on safe domain');references+=1
        else:need(ref==(0,)*6,'unexecuted reference is empty')
        caps+=current['total']>=CAP or current['prediction']>=CAP
    need(offset==len(body),'no trailing or missing timing capture bytes')
    need(len(original_ids)==31 and original_frames>0,'all original31 stream frame totals')
    need(head_rows and tail_rows and gaps and seeded and exceeds and caps,'all important transition families executed')
    return dict(passed=True,commands=len(model),packets=packets,references=references,priming_blocks=priming,
        hard_resets=resets,gaps=gaps,seeded_arithmetic_cases=seeded,capped_states=caps,
        out_of_wire_predictions=exceeds,start_trim_rows=head_rows,end_trim_rows=tail_rows,
        start_discarded=head_samples,end_discarded=tail_samples,available_frames=available_samples,kept_frames=kept_samples,
        size_transitions=len(transitions),original_streams=len(original_ids),original_packets=434,
        original_returned_frames=original_frames,counter_limit=CAP,unbounded_seed_max=CAP+(1<<80),
        decoder_executed=False,PCM_executed=False)


def corruption_controls(body,model):
    # First record is init, second is a real prime event; all changes are fixed
    # before execution and checked against the complete independently built model.
    modifications=[('magic',0,b'X'),('action',12,struct.pack('<I',9)),
        ('status',16,struct.pack('<I',1)),('before-state',24,struct.pack('<I',1)),
        ('event',12+160+48,struct.pack('<I',63)),('after-state',12+68,bytes(4)),
        ('trim',12+160+104,struct.pack('<I',1)),('reference',12+160+132,struct.pack('<I',1))]
    damaged=[(name,body[:offset]+value+body[offset+len(value):]) for name,offset,value in modifications]
    damaged += [('truncated',body[:-1]),('trailing',body+b'X')]
    for name,value in damaged:
        try:inspect_capture(value,model)
        except (ValueError,struct.error):continue
        raise ValueError('damaged capture accepted: '+name)
    return [name for name,_ in damaged]


def xiph_fragment(body):
    need(sha(body)==BLOCK_SHA,'pinned complete Xiph block.c')
    start=body.index(b'  if(b->sample_count==-1){',body.index(b'int vorbis_synthesis_blockin'))
    last=body.index(b'  if(vb->eofflag)v->eofflag=1;',start)
    end=body.index(b'\n',last)+1
    return body[start:end]


def original_body():
    archive=(ROOT/'tests/results/vorbis-transform-20261026/captures.zip').read_bytes()
    need(sha(archive)==PRIOR_SHA,'pinned committed original31 source archive')
    with zipfile.ZipFile(io.BytesIO(archive)) as z:body=z.read('host03/sources/original31.json')
    need(sha(body)==ORIGINAL_SHA,'exact original31 metadata')
    return body


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--verify-capture',type=Path);args=parser.parse_args()
    original=original_body();model=corpus(json.loads(original))
    if args.verify_capture:
        body=args.verify_capture.read_bytes();result=inspect_capture(body,model);result['corruption_controls']=corruption_controls(body,model)
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result));return 0
    out=args.output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh task-local output');out.mkdir(parents=True)
    report=dict(completed=False,passed=False,commands=[],sources={},sanitizers=['address','undefined'],
        metadata_only=True,decoder_executed=False,overlap_executed=False,PCM_executed=False,native_executed=False)
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
            with (out/(name+'.stdout.log')).open('xb') as so,(out/(name+'.stderr.log')).open('xb') as se:
                child=subprocess.Popen(command,stdout=so,stderr=se,stdin=subprocess.DEVNULL,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
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
        for component in ('native_vorbis_numeric','native_vorbis_timing'):
            folder=ROOT/'idf/components'/component
            for path in sorted(folder.rglob('*')):
                if path.is_file():freeze(path,'components/'+component+'/'+path.relative_to(folder).as_posix())
        freeze(ROOT/'tests/native/vorbis_timing_host.c','native/vorbis_timing_host.c')
        upstream=freeze(ROOT/'idf/components/native_vorbis_xiph/upstream/libvorbis/lib/block.c','upstream/block.c')
        freeze(ROOT/'idf/components/native_vorbis_xiph/upstream/libvorbis/COPYING','upstream/COPYING')
        provenance=freeze(ROOT/'tests/native/vorbis_xiph_host.c','upstream/original31-fixture.c')
        need(b'p+1==test->packet_count' in provenance,'original31 saved EOS policy: final packet')
        (out/'sources/original31.json').write_bytes(original);report['sources']['original31.json']=sha(original)
        fragment=xiph_fragment(upstream);(out/'sources/native/xiph-granule.inc').write_bytes(fragment)
        report['sources']['native/xiph-granule.inc']=sha(fragment)
        (out/'model.json').write_text(json.dumps(model,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
        (out/'input.bin').write_bytes(encode(model));report.update(input_sha256=sha((out/'input.bin').read_bytes()),
            model_sha256=sha((out/'model.json').read_bytes()),fragment_sha256=sha(fragment),model_commands=len(model))
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py')
        found=[ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node,ast.Assign) and
            any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(found)==1,'one owned supervisor');(out/'supervisor.py').write_text(found[0],encoding='utf-8',newline='\n')
        report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes());save()
        report['compiler_version']=run('compiler-version',['gcc','--version'])
        run('compile',['gcc','-std=c11','-O1','-g','-UNDEBUG','-fno-pie','-no-pie','-fsanitize=address,undefined',
            '-fno-sanitize-recover=all','-fno-omit-frame-pointer','-Wall','-Wextra','-Werror',
            '-I'+linux(out/'sources/components/native_vorbis_numeric/include'),'-I'+linux(out/'sources/components/native_vorbis_timing/include'),
            linux(out/'sources/components/native_vorbis_timing/timing.c'),linux(out/'sources/native/vorbis_timing_host.c'),'-o',linux(out/'timing')])
        text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',
            linux(out/'timing'),linux(out/'input.bin'),linux(out/'capture.bin')])
        match=re.fullmatch(r'TIMING_CAPTURE commands=(\d+) references=(\d+) refusals=(\d+) checks=(\d+)\s*',text)
        need(match is not None and not (out/'execute.stderr.log').read_bytes(),'complete guarded capture')
        controls=dict(zip(('commands','references','refusals','checks'),map(int,match.groups())))
        measured=inspect_capture((out/'capture.bin').read_bytes(),model)
        need(controls['commands']==measured['commands'] and controls['references']==measured['references'],'actual complete counts')
        damaged=corruption_controls((out/'capture.bin').read_bytes(),model)
        for name,digest in report['sources'].items():need(sha((out/'sources'/name).read_bytes())==digest,'unchanged frozen source')
        report.update(completed=True,passed=True,controls=controls,measurements=measured,corruption_controls=damaged,
            capture_sha256=sha((out/'capture.bin').read_bytes()),binary_sha256=sha((out/'timing').read_bytes()))
        save();print(json.dumps(dict(passed=True,controls=controls,measurements=measured)));return 0
    except BaseException as error:report['error']=repr(error);save();raise


if __name__=='__main__':raise SystemExit(main())
