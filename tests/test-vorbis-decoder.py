"""Persistent public raw-packet owner: complete PCM and transactional lifetime."""
import argparse,ast,copy,hashlib,importlib.util,json,os,re,struct,subprocess,sys,time,uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PINS={
    'test-vorbis-synthesis.py':'f42ab5b669b5a39e0619449a798c00f682bf2f1468664d5376eb63bdda429765',
    'test-vorbis-timing.py':'f990067645a196972767639c100506be757b9adb8a2d0f8bbd8fe3857f0be33a',
    'test-vorbis-floor0-frame.py':'e92e1470f9806fe9fa2fe3c6903bd8f4015ab735ede11d54b6be5dc9c95c5357',
    'test-vorbis-setup.py':'ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff',
    'test-vorbis-floor-packet.py':'8ab01db0169af95e75f7aa6cc1e7c28df48371f94f445aaa03c08882c17776d7',
    'test-vorbis-residue.py':'1191a648a9070a995b1e256519ce71891f70779d924db651db16c490c856f31d',
    'vorbis_packet_frame_model.py':'5ed0ad7b589fc16de2d99f5aca77e179808aa0553fd22d9907b59369abcd77a9'}
DECODER_SHA='5656842a0d3a78a072cc56b7f382a0100b6757473056322acb57cc3081d43f2b'
PCM_SHA='b9df479b6cb6ac07b2aff2049f05bb8ba98ef9ce4fdc72acf40a333f47e01d75'
SUPERVISOR_ORIGIN_SHA='df9f6c4496836f8e166209d92114e88b20568aac143081d0c4cc3096b6828cb2'

def need(test,message):
    if not test:raise ValueError(message)
def sha(body):return hashlib.sha256(body).hexdigest()
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def linux(path):
    p=Path(path).resolve().as_posix();return '/mnt/'+p[0].lower()+p[2:] if sys.platform=='win32' else p
def readers():
    for name,pin in PINS.items():need(sha((ROOT/'tests'/name).read_bytes())==pin,'pinned live pure reader: '+name)
    return {name:load(ROOT/'tests'/name,'decoder_'+name.replace('-','_').replace('.','_')) for name in PINS}
class Reader:
    def __init__(self,body):self.body=body;self.at=0
    def raw(self,count):
        need(0<=count<=len(self.body)-self.at,'complete persistent-owner capture field');part=self.body[self.at:self.at+count];self.at+=count;return part
    def take(self,fmt):
        values=struct.unpack('<'+fmt,self.raw(struct.calcsize('<'+fmt)));return values[0] if len(values)==1 else values

def supplementary(modules):
    setup=modules['test-vorbis-setup.py'];floor=modules['test-vorbis-floor-packet.py'];residue=modules['test-vorbis-residue.py'];frame=modules['vorbis_packet_frame_model.py'];old=modules['test-vorbis-floor0-frame.py']
    rows=old.supplement(modules);need(len(rows)==13,'all retained typed floor0 packet vectors');out=[]
    for row in rows:
        ctx=frame._context(row,setup);ident=ctx['layout']['identification'];need(len(ctx['modes'])==1 and ctx['modes'][0]['blockflag']==0,'retained short-only packet prefix')
        mapping=residue.mapping_info(ctx,0);floor_index=mapping['submaps'][mapping['mux'][0]][1]
        fi=floor.floor_info(ctx,floor_index);need(fi['type']==0,'retained floor0 route')
        writer=setup.Writer();writer.put(0,1)
        for _ in range(ident['channels']):writer.put(0,fi['bits'])
        prime=dict(row,packet_hex=writer.octets(),packet_bits=len(writer.bits),start_bit=0)
        expected=frame.expected_case(prime,setup,floor,residue);need(expected['decode_status']==0,'valid independently parsed absent-floor prime')
        route=old.EXTRA_ROUTES[row['id']];need(route[0]==route[1],'retained shared route identity')
        out.append(dict(row,index=len(out),prime_hex=prime['packet_hex'],prime_bits=prime['packet_bits'],
            expected_status=0 if route[0]==0 else -(route[0]+5),extreme=False,rate=ident['sample_rate'],channels=ident['channels'],
            short_block=ident['blocksize_0'],long_block=ident['blocksize_1']))
    spec=floor.floor1_spec();spec['identification'].update(channels=255,small=13,large=13);spec['mappings'][0]['mux']=[0]*255;spec['mappings'][0]['pairs']=[]
    row=frame._packet('decoder-resource-255x8192',spec,setup,floor,residue,[0]*255)
    expected=frame.expected_case(row,setup,floor,residue);need(expected['decode_status']==0 and expected['frame']['prefix']['blocksize']==8192,'valid full-domain absent-floor resource packet')
    out.append(dict(row,index=13,prime_hex=row['packet_hex'],prime_bits=row['packet_bits'],expected_status=0,extreme=True,
        rate=spec['identification']['rate'],channels=255,short_block=8192,long_block=8192))
    return out

def encode(model,supplements,synthesis):
    body=bytearray(synthesis.encode(model));body.extend(b'VDECSUP1'+struct.pack('<I',len(supplements)))
    for row in supplements:
        values=[bytes.fromhex(row[key]) for key in ('identification_hex','setup_hex','packet_hex','prime_hex')]
        body.extend(struct.pack('<4IiI4IQQ',row['rate'],row['channels'],row['short_block'],row['long_block'],row['expected_status'],int(row['extreme']),
            *map(len,values),row['packet_bits'],row['prime_bits']))
        for part in values:body.extend(part)
    return bytes(body)

def primary_parts(body,model):
    r=Reader(body);need(r.take('8s')==b'VSYNOUT1' and r.take('I')==31,'whole persistent-owner PCM capture');parts=[];allocations=[]
    for index,row in enumerate(model['cases']):
        need(r.take('6I')==(index,row['rate'],row['channels'],row['short_block'],row['long_block'],14),'all primary stream identities')
        records=Reader(r.raw(r.take('Q')));stream=[]
        for packet in range(14):
            fields=records.take('5IQI5IqQ');need(fields[0]==packet,'all primary packet identities');stream.append(records.raw(fields[-1]*2))
        need(records.at==len(records.body),'all primary record bytes');need(r.take('i3I')==(0,0xffffffff,0xffffffff,0xffffffff),'successful persistent-owner stream')
        totals=r.take('11Q');need(not r.take('I') and totals[5]==totals[6] and totals[7]==totals[8]==0,'persistent owner released completely');allocations.append(totals);parts.append(stream)
    need(r.at==len(body),'complete primary capture');return parts,allocations

def info_tuple(row,state,eos):
    return (row['channels'],row['rate'],row['short_block'],row['long_block'],state['short'],state['long'],state['previous'],state['known'],state['eos'],
        min(state['total'],(1<<64)-1),min(state['prediction'],(1<<64)-1),int(eos))
def states_for(row,timing):
    state=timing.initial(row['short_block'],row['long_block']);out=[state]
    for index,mode in enumerate(row['modes']):state,_=timing.apply(state,(row['long_block'] if mode else row['short_block'],row['granules'][index],int(index==13),0));out.append(state)
    return out
def fnv(body,value=14695981039346656037):
    for byte in body:value=((value^byte)*1099511628211)&((1<<64)-1)
    return value

def compare_controls(body,model,supplements,primary,timing):
    r=Reader(body);need(r.take('8s')==b'VDECCTL1' and r.take('I')==31,'owner-control header');inventory=[];expected_events=[]
    for index,row in enumerate(model['cases']):
        need(r.take('I')==index,'allocation baseline identity');opening=r.take('Q');need(0<opening<10000,'finite actual opening allocation count');requests=tuple(r.take('Q') for _ in range(opening));need(all(requests),'no zero-sized allocation request')
        need(r.take('I')==14,'all packet allocation baselines');packets=[]
        for _ in range(14):
            count=r.take('Q');need(count<100,'finite packet growth allocation count');packet=tuple(r.take('Q') for _ in range(count));need(all(packet),'positive packet request sizes');packets.append(packet)
        inventory.append(dict(open=requests,packets=packets))
        expected_events.append((3,index,0,0,0))
        expected_events.extend((0,index,0,j+1,size) for j,size in enumerate(requests));expected_events.extend((1,index,3,j+1,size) for j,size in enumerate(requests))
        for packet,sequence in enumerate(packets):expected_events.extend((2,index,packet,j+1,size) for j,size in enumerate(sequence))
    expected_events.extend(((4,0,3,0,0),(5,0,20,0,0),(6,0,20,0,0),(7,0,13,0,0)))
    need(r.take('Q')==len(expected_events),'every actual allocation ordinal and lifecycle event retained')
    before_states=[states_for(row,timing) for row in model['cases']];null=(0,)*12;totals=[0]*8;recovery_spans=recovery_bytes=0;event_rows=[]
    def read_info():return r.take('9I2QI')
    for expected in expected_events:
        kind,stream,packet,ordinal,size=r.take('3I2Q');need((kind,stream,packet,ordinal,size)==expected,'ordered complete refusal/recovery identity');totals[kind]+=1
        before,after=read_info(),read_info();count=r.take('I');row=model['cases'][stream];states=before_states[stream]
        if kind==0:need(before==after==null,'failed new-open has no committed handle');wanted=[(stream,0),(stream,1)]
        elif kind==1:need(before==after==info_tuple(row,states[3],False),'failed replacement preserves old committed timeline');wanted=[(stream,3),(stream,0),(stream,1)]
        elif kind==2:need(before==after==info_tuple(row,states[packet],False),'failed scratch growth preserves committed timeline');wanted=[(stream,packet)]+([(stream,packet+1)] if packet<13 else [])
        elif kind==3:need(before==info_tuple(row,states[14],True) and after==info_tuple(row,states[0],False),'hard reset clears EOS/timing and retains setup');wanted=[(stream,i) for i in range(14)]
        elif kind==4:
            n=row['long_block'] if row['modes'][3] else row['short_block'];state,_=timing.apply(states[3],(n,-1,0,1))
            need(before==info_tuple(row,states[3],False) and after==info_tuple(row,state,False),'discontinuity retains history and reanchors timing');wanted=[(stream,3),(stream,4)]
        elif kind==5:need(before==after==null,'independent-handle event');wanted=[item for i in range(14) for item in ((stream,i),(packet,i))]
        elif kind==6:
            new=model['cases'][packet];need(before==info_tuple(row,states[3],False) and after==info_tuple(new,before_states[packet][0],False),'cross-stream replace restarts committed stream');wanted=[(packet,0),(packet,1)]
        else:need(before==after==info_tuple(row,states[13],False),'HTTP EOF does not set packet EOS or consume history');wanted=[(stream,13)]*2
        need(count==len(wanted),'all actual recovery spans retained');pieces=[]
        for identity in wanted:
            actual_stream,actual_packet,length=r.take('3I');need((actual_stream,actual_packet)==identity,'recovery PCM packet identity');actual=r.raw(length);pieces.append(actual);recovery_spans+=1;recovery_bytes+=length
            if kind!=7:need(actual==primary[actual_stream][actual_packet],'every retry/reset/replacement PCM byte equals full independently qualified baseline')
        if kind==7:
            need(pieces[0]==pieces[1] and len(pieces[0])==((row['long_block'] if row['modes'][12] else row['short_block'])+(row['long_block'] if row['modes'][13] else row['short_block']))//4*row['channels']*2,
                'HTTP EOF refused call leaves actual next PCM identical to untouched independent handle')
        hash_value,live,allocations,releases=r.take('4Q');need(hash_value==fnv(b''.join(pieces)) and live==0 and allocations==releases and allocations>0,'supplemental hash and exact allocation cleanup')
        event_rows.append(dict(kind=kind,stream=stream,packet=packet,ordinal=ordinal,requested_bytes=size,spans=count,pcm_bytes=sum(map(len,pieces))))
    need(r.take('I')==13,'all retained numeric-route packet cases');routes=[]
    for index,row in enumerate(supplements[:13]):
        need(r.take('Ii')==(index,row['expected_status']),'explicit original supplemental route status');before,after=read_info(),read_info()
        state=timing.initial(row['short_block'],row['long_block']);state,_=timing.apply(state,(row['short_block'],-1,0,0));need(before==info_tuple(row,state,False),'actual absent-floor primer committed')
        if row['expected_status']:need(before==after,'two numeric failures preserve history and do not commit requested EOS')
        else:
            state,_=timing.apply(state,(row['short_block'],-1,1,0));need(after==info_tuple(row,state,True),'successful candidate commits EOS')
        count=r.take('Q');need(count==row['short_block']//2*row['channels'],'full numeric recovery span');pcm=r.raw(count*2)
        if row['expected_status']:need(pcm==bytes(len(pcm)),'typed refusal followed by real absent-floor silence preserves history')
        alloc,release,live=r.take('3Q');need(alloc==release and not live,'numeric route cleanup');routes.append(dict(id=row['id'],status=row['expected_status'],samples=count,pcm_sha256=sha(pcm)))
    need(r.take('I')==1 and r.take('Ii')==(13,-4),'legal-extreme allocator refusal');budget,requested,alloc,release,live=r.take('5Q')
    need(budget==1<<20 and requested==255*4096*8 and alloc==release and not live,'exact full-domain history request refused with complete cleanup without a format cap')
    count=r.take('Q');need(count==4096*255 and r.raw(count*2)==bytes(count*2),'all full-domain actual interleaved zero PCM bytes')
    large_alloc,large_release,large_live,peak=r.take('4Q');need(large_alloc==large_release and not large_live and 1<<20<peak<=64<<20,'larger supplied host allocator supports legal dimensions')
    checks,undersized,measures,opening,replacing,processing,other=r.take('7Q');need(r.at==len(body),'all owner controls and terminal summary')
    need((opening,replacing,processing)==tuple(totals[:3]) and checks>0 and measures>=2*434,'all actual refusal ordinal totals')
    wanted_undersized=sum(len({0,len(part)//4,len(part)//2-1}) for stream in primary for part in stream if part)+3
    need(undersized==wanted_undersized,'bounded distinct capacity controls on every original emitted packet and extreme packet')
    return dict(passed=True,allocation_baselines=inventory,events=event_rows,event_counts=totals,recovery_spans=recovery_spans,recovery_pcm_bytes=recovery_bytes,
        checks=checks,undersized=undersized,measures=measures,open_refusals=opening,replace_refusals=replacing,process_refusals=processing,other_refusals=other,
        numeric_routes=routes,extreme=dict(channels=255,short=8192,long=8192,bounded_budget=budget,bounded_status=-4,large_peak_payload=peak,samples=count),
        no_zero_sized_callback=True,no_null_release=True,full_recovery_PCM_compared=True)

def corruption_controls(capture,controls,model,supplements,synthesis,references,xiph,timing):
    def reject(name,body,control):
        try:
            primary,_=primary_parts(body,model);need(synthesis.compare(body,model,references,xiph,timing)['passed'],'complete PCM contract');need(sha(b''.join(p for stream in primary for p in stream))==PCM_SHA,'prior full pipeline PCM identity');compare_controls(control,model,supplements,primary,timing)
        except (ValueError,struct.error,IndexError,OverflowError):return dict(name=name,rejected=True)
        raise ValueError('accepted corrupted owner evidence: '+name)
    cases=[]
    cases.append(reject('truncated-primary',capture[:-1],controls));cases.append(reject('trailing-primary',capture+b'\0',controls))
    bad=bytearray(capture);bad[12]^=1;cases.append(reject('stream-identity',bytes(bad),controls))
    r=Reader(capture);r.raw(12);r.raw(24);record_length=r.take('Q');records_start=r.at;r.raw(68);r.raw(68);need(record_length>136,'emitted original PCM exists');bad=bytearray(capture);bad[records_start+136]^=1;cases.append(reject('actual-PCM',bytes(bad),controls))
    cases.append(reject('truncated-controls',capture,controls[:-1]));cases.append(reject('trailing-controls',capture,controls+b'\0'))
    bad=bytearray(controls);bad[24]^=1;cases.append(reject('allocation-request',capture,bytes(bad)))
    bad=bytearray(controls);bad[-32]^=1;cases.append(reject('refusal-total',capture,bytes(bad)))
    return cases

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);parser.add_argument('--preflight',action='store_true');args=parser.parse_args()
    out=args.output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh task-local output');out.mkdir(parents=True)
    report=dict(completed=False,passed=False,commands=[],sources={},sanitizers=['address','undefined'],production_selected=False,private_decoder_executed=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,label):
        body=path.read_bytes();p=out/'sources'/label;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body);report['sources'][label]=sha(body);return body
    def data(body,label):
        p=out/'sources'/label;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body);report['sources'][label]=sha(body)
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
        need(row['transport_exit']==0 and not row.get('forced_transport_stop'),'owned transport terminal: '+name)
        need(s.get('nonce')==nonce and s.get('request_sha256')==row['request_sha256'] and s.get('state')=='terminal' and s.get('final') and s.get('new_session') and
            s.get('child_pid')==s.get('owned_pgid') and s.get('child_reaped') and s.get('group_gone') and s.get('child_returncode')==0,'owned child terminal: '+name)
        return (out/(name+'.stdout.log')).read_text('utf-8')
    save()
    try:
        freeze(Path(__file__),'runner.py');modules=readers();synthesis=modules['test-vorbis-synthesis.py'];timing=modules['test-vorbis-timing.py'];components=(*synthesis.COMPONENTS,'native_vorbis_decoder')
        for name in components:
            for path in sorted((ROOT/'idf/components'/name).rglob('*')):
                if path.is_file():freeze(path,'components/'+name+'/'+path.relative_to(ROOT/'idf/components'/name).as_posix())
        need(report['sources']['components/native_vorbis_decoder/decoder.c']==DECODER_SHA,'reviewed production source freeze');freeze(ROOT/'tests/native/vorbis_decoder_host.c','native/vorbis_decoder_host.c')
        for name,pin in PINS.items():need(sha(freeze(ROOT/'tests'/name,'readers/'+name))==pin,'frozen pure reader')
        original,model,references,xiph,saved=synthesis.original_data();data(original,'original31.json');data(saved,'saved-Xiph-PCM.bin')
        for index,row in enumerate(model['cases']):data(references[row['id']],f'reference/{index:02}.s16le')
        supplements=supplementary(modules);data((json.dumps(supplements,indent=2)+'\n').encode(),'supplements.json');input_body=encode(model,supplements,synthesis);(out/'input.bin').write_bytes(input_body)
        report.update(input_sha256=sha(input_body),original31_sha256=synthesis.ORIGINAL_SHA,previous_PCM_sha256=PCM_SHA,
            raw_API_input_bytes=sum(len(bytes.fromhex(row[key])) for row in model['cases'] for key in ('identification_hex','setup_hex','audio_hex')),
            retained_comment_bytes=sum(len(bytes.fromhex(row['comment_hex'])) for row in model['cases']),supplement_count=len(supplements))
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py');need(sha(origin)==SUPERVISOR_ORIGIN_SHA,'pinned owned supervisor origin before derivation')
        templates=[ast.literal_eval(n.value) for n in ast.parse(origin).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SUPERVISOR' for t in n.targets)]
        need(len(templates)==1 and templates[0].count('assert 0<timeout<=60')==1,'documented timeout-only supervisor derivation')
        (out/'supervisor.py').write_text(templates[0].replace('assert 0<timeout<=60','assert 0<timeout<=180'),encoding='utf-8',newline='\n');report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes());save()
        if args.preflight:report['preflight_only']=True;save();print(json.dumps(dict(preflight=True,input_bytes=len(input_body),supplements=len(supplements))));return 0
        report['compiler_version']=run('compiler-version',['gcc','--version']);units=[path for name in components for path in sorted((out/'sources/components'/name).glob('*.c'))]+[out/'sources/native/vorbis_decoder_host.c']
        flags=['gcc','-std=c11','-O1','-g','-UNDEBUG','-fno-fast-math','-ffp-contract=off','-fno-pie','-no-pie','-fsanitize=address,undefined','-fno-sanitize-recover=all',
            '-fno-omit-frame-pointer','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror',*['-I'+linux(out/'sources/components'/name/'include') for name in components]]
        run('compile',[*flags,*map(linux,units),'-Wl,--gc-sections','-lm','-o',linux(out/'decoder')])
        text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',linux(out/'decoder'),linux(out/'input.bin'),linux(out/'capture.bin'),linux(out/'controls.bin')])
        match=re.fullmatch(r'DECODER_CAPTURE cases=31 packets=434 pcm_bytes=738560 open=(\d+) replace=(\d+) process=(\d+) undersized=(\d+) measures=(\d+) other=(\d+) checks=(\d+) live=0 bytes=0\s*',text)
        need(match is not None and not (out/'execute.stderr.log').read_bytes(),'complete guarded owner execution without sanitizer diagnostics')
        capture=(out/'capture.bin').read_bytes();controls=(out/'controls.bin').read_bytes();measurements=synthesis.compare(capture,model,references,xiph,timing);need(measurements['passed'] and measurements['pcm_sha256']==PCM_SHA,'all31/434/738560/both references/bound2/14 relations and previous full PCM identity')
        primary,allocation_totals=primary_parts(capture,model);qualified=compare_controls(controls,model,supplements,primary,timing);corrupt=corruption_controls(capture,controls,model,supplements,synthesis,references,xiph,timing)
        values=dict(zip(('open','replace','process','undersized','measures','other','checks'),map(int,match.groups())))
        need(tuple(values[k] for k in ('open','replace','process','undersized','measures','other'))==tuple(qualified[k] for k in ('open_refusals','replace_refusals','process_refusals','undersized','measures','other_refusals')),'terminal summary equals binary controls')
        # The binary snapshots checks before seven put64 calls (14 put32 checks)
        # and the final fclose assertion. Both observed counters stay preserved.
        need(values['checks']==qualified['checks']+15,'exact fifteen final serialization/close assertions after binary check snapshot')
        for label,pin in report['sources'].items():need(sha((out/'sources'/label).read_bytes())==pin,'frozen source/data unchanged')
        report.update(completed=True,passed=True,measurements=measurements,owner_controls=qualified,terminal_summary=values,corruption_controls=corrupt,
            capture_sha256=sha(capture),controls_sha256=sha(controls),binary_sha256=sha((out/'decoder').read_bytes()),allocation_totals=allocation_totals);save();print(json.dumps(dict(passed=True,terminal_summary=values,measurements=measurements)));return 0
    except BaseException as error:report['error']=repr(error);save();raise

if __name__=='__main__':raise SystemExit(main())
