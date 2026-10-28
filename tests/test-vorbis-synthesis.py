"""Actual complete original31/raw434 public owned synthesis qualification."""
import argparse,ast,hashlib,importlib.util,io,json,os,re,struct,subprocess,sys,time,uuid,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COMPONENTS=('native_vorbis_numeric','native_vorbis_setup_owner','native_vorbis_packet_frame',
    'native_vorbis_floor1_product','native_vorbis_transform','native_vorbis_floor0_spectrum',
    'native_vorbis_window','native_vorbis_window_exact','native_vorbis_pcm_exact','native_vorbis_timing','native_vorbis_synthesis')
ORIGINAL_SHA='32ba4c7e401fcfd05238f929fa6874c3048237792d78f36b05a8fade5b861e24'
PRIOR_SHA='3b74cc7425b315997011040b6b6a8924b908cdff0404e0d0601cbb81a68a93ea'
XIPH_SHA='f31167f2a52e8e8a8f01e20cbadb3597d1394931bd2dfd2ac67a0381e2d6985b'
XIPH_MANIFEST='4ffcc25005b7dd3d51f6fd16df8282de3316532211a3020f17dedaa295d43b6a'
TIMING_SHA='f990067645a196972767639c100506be757b9adb8a2d0f8bbd8fe3857f0be33a'
WINDOW_SHA='06268abe3c9fe4836bf17ca91b1fcb73ce82137ea872282e21bad61fa4494e41'
PCM_SHA='ca145e73850ac1af5e16ebef5c1287f5a4c74d131752f6a71bee63ef5190cf01'
BOUND=2


def need(test,message):
    if not test:raise ValueError(message)
def sha(body):return hashlib.sha256(body).hexdigest()
def linux(path):
    p=Path(path).resolve().as_posix();return '/mnt/'+p[0].lower()+p[2:] if sys.platform=='win32' else p
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class Reader:
    def __init__(self,body):self.body=body;self.at=0
    def raw(self,count):
        need(0<=count<=len(self.body)-self.at,'complete synthesis capture field');out=self.body[self.at:self.at+count];self.at+=count;return out
    def take(self,fmt):
        values=struct.unpack('<'+fmt,self.raw(struct.calcsize('<'+fmt)));return values[0] if len(values)==1 else values


def original_data():
    body=(ROOT/'tests/results/vorbis-floor1-product-20261026/captures.zip').read_bytes();need(sha(body)==PRIOR_SHA,'pinned original31 provenance archive')
    with zipfile.ZipFile(io.BytesIO(body)) as z:original=z.read('frame03/sources/original31.json')
    need(sha(original)==ORIGINAL_SHA,'all original31 raw inputs/relations')
    model=json.loads(original);need(len(model['cases'])==31 and len(model['relations'])==14,'complete original31 contract')
    body=(ROOT/'tests/results/vorbis-xiph-packets-20261026/captures.zip').read_bytes();need(sha(body)==XIPH_SHA,'pinned saved Xiph/reference DATA archive')
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        need(sha(z.read('manifest.json'))==XIPH_MANIFEST,'pinned saved reference inventory')
        captured=z.read('host/pcm.bin');references={row['id']:z.read('host/sources/cases/'+row['reference_path']) for row in model['cases']}
    r=Reader(captured);need(r.take('8s')==b'XIPHRES1' and r.take('I')==31,'whole saved Xiph capture')
    xiph={};total=packets=0
    for index,row in enumerate(model['cases']):
        need(r.take('4I')==(index,row['rate'],row['channels'],len(row['frames'])),'saved actual format and packet counts');parts=[]
        for packet,count in enumerate(row['frames']):
            need(r.take('3I')==(packet,count,count*row['channels']*2),'saved per-packet reference span');parts.append(r.raw(count*row['channels']*2));packets+=1
        xiph[row['id']]=b''.join(parts);reference=references[row['id']]
        need(len(reference)==len(xiph[row['id']])==row['pcm_bytes'] and sha(reference)==row['reference_pcm_sha256'],'whole original reference bytes and digest');total+=len(reference)
    need(r.at==len(captured) and total==738560 and packets==434,'all saved reference PCM bytes')
    return original,model,references,xiph,captured
def encode(model):
    body=bytearray(b'VSYNIN01'+struct.pack('<I',len(model['cases'])))
    for index,row in enumerate(model['cases']):
        raw=[bytes.fromhex(row[key]) for key in ('identification_hex','setup_hex','audio_hex')]
        body.extend(struct.pack('<9I',index,row['rate'],row['channels'],row['short_block'],row['long_block'],len(row['modes']),*map(len,raw)))
        for part in raw:body.extend(part)
        body.extend(struct.pack('<'+str(len(row['offsets']))+'I',*row['offsets']))
        body.extend(struct.pack('<'+str(len(row['granules']))+'q',*row['granules']))
    return bytes(body)


def compare(body,model,references,xiph,timing):
    r=Reader(body);need(r.take('8s')==b'VSYNOUT1' and r.take('I')==31,'whole actual synthesis capture')
    cases=[];targets={};packets=pcm_bytes=floor0=floor1=0;maximum=maximum_xiph=0;failures=[];peak=0
    for index,row in enumerate(model['cases']):
        need(r.take('6I')==(index,row['rate'],row['channels'],row['short_block'],row['long_block'],len(row['modes'])),'actual complete stream identity')
        records=Reader(r.raw(r.take('Q')));status,failed_packet,failed_channel,failed_route=r.take('i3I');totals=r.take('11Q');stage=r.raw(r.take('I')).decode('ascii')
        observed_packets=frames=samples=f0=f1=0;parts=[];state=timing.initial(row['short_block'],row['long_block'])
        while records.at<len(records.body):
            fields=records.take('5IQI5IqQ');packet,n,channels,a,b,cursor,eop,*tail=fields
            available,head,end,count,kind,position,pcm_samples=tail
            need(packet==observed_packets and packet<len(row['modes']) and channels==row['channels'] and a+b==channels and
                n==(row['long_block'] if row['modes'][packet] else row['short_block']) and eop in (0,1) and
                cursor<=8*(row['offsets'][packet+1]-row['offsets'][packet]),'every actual decoded packet/route/cursor')
            state,wanted=timing.apply(state,(n,row['granules'][packet],int(packet+1==len(row['modes'])),0))
            need((available,head,end,count,kind,position)==wanted and count==row['frames'][packet] and
                pcm_samples==count*channels,'every actual shared timing and interleaved PCM span')
            parts.append(records.raw(pcm_samples*2));observed_packets+=1;frames+=count;samples+=pcm_samples;f0+=a;f1+=b
        need(totals[:5]==(observed_packets,frames,samples,f0,f1) and totals[5]==totals[6] and totals[7]==totals[8]==0,
            'actual stage totals and complete allocation cleanup')
        actual=b''.join(parts);targets[row['id']]=actual;reference=references[row['id']];saved=xiph[row['id']]
        complete=status==0 and observed_packets==len(row['modes']) and len(actual)==len(reference)==row['pcm_bytes']
        if status:failures.append(dict(id=row['id'],status=status,packet=failed_packet,channel=failed_channel,route=failed_route,stage=stage))
        else:need(not stage and (failed_packet,failed_channel,failed_route)==(0xffffffff,)*3,'successful helper has no failure metadata')
        actual_values=struct.unpack('<'+str(len(actual)//2)+'h',actual)
        refs=struct.unpack('<'+str(len(reference)//2)+'h',reference);saved_values=struct.unpack('<'+str(len(saved)//2)+'h',saved)
        error=max((abs(a-b) for a,b in zip(actual_values,refs)),default=0)
        xiph_error=max((abs(a-b) for a,b in zip(actual_values,saved_values)),default=0)
        cases.append(dict(id=row['id'],complete=complete,packets=observed_packets,pcm_bytes=len(actual),max_abs_error=error,
            max_xiph_abs_error=xiph_error,sha256=sha(actual),peak_payload_bytes=totals[10]))
        maximum=max(maximum,error);maximum_xiph=max(maximum_xiph,xiph_error);peak=max(peak,totals[10])
        packets+=observed_packets;pcm_bytes+=len(actual);floor0+=f0;floor1+=f1
    need(r.at==len(body),'no unread or missing synthesis capture data')
    relations=[]
    for relation in model['relations']:
        names=relation['cases'];equal=all(targets[name]==targets[names[0]] for name in names[1:])
        relations.append(dict(kind=relation['kind'],cases=names,passed=equal==(relation['kind']=='equal')))
    passed=(not failures and all(row['complete'] for row in cases) and packets==434 and pcm_bytes==738560 and
        maximum<=BOUND and maximum_xiph<=BOUND and all(row['passed'] for row in relations))
    return dict(passed=passed,cases=cases,failures=failures,streams=31,packets=packets,pcm_bytes=pcm_bytes,
        max_abs_error=maximum,max_xiph_abs_error=maximum_xiph,fixed_S16_bound=BOUND,relations=relations,
        floor0_channels=floor0,floor1_channels=floor1,peak_payload_bytes=peak,
        pcm_sha256=sha(b''.join(targets[row['id']] for row in model['cases'])),actual_full_pipeline_executed=True,
        saved_transform_or_gain_inputs_used=False,private_decoder_executed=False,production_selected=False)


def owner_data(model,timing,window):
    folder=ROOT/'tests/results/vorbis-overlap-20261028';body=(folder/'captures.zip').read_bytes()
    need(sha(body)==window.PRIOR_SHA and sha((folder/'manifest.json').read_bytes())==window.PRIOR_MANIFEST_SHA,'pinned overlap DATA')
    with zipfile.ZipFile(io.BytesIO(body)) as z:saved=z.read('host03/capture.bin')
    witnesses,witness_metrics=window.saved_witnesses(saved);r=Reader(saved);need(r.take('8s')==b'VOVERL01' and r.take('I')==8,'saved overlap data header')
    coefficients={}
    for n in window.SIZES:
        need(r.take('I')==n,'saved lookup order');coefficients[n]=r.take(str(n//2)+'d')
    need(r.take('I')==864,'all saved owner overlap rows');rows=[]
    for _ in range(864):
        identity=r.take('7I');ea,eb=r.take('qq');n,count=identity[5:7];source=r.take(str(n)+'d');r.raw(count*16+n//2*8)
        rows.append(dict(identity=identity,ea=ea,eb=eb,source=source))
    need(r.at==len(saved),'complete original overlap DATA')
    actions=timing.corpus(model);need(len(actions)==20019,'all existing timing actions')
    return dict(overlap=rows,actions=actions,coefficients=coefficients,witnesses=witnesses,witness_metrics=witness_metrics,saved_capture=saved)
def encode_owner(data,timing):
    body=bytearray(b'VSYNOWNI'+struct.pack('<I',864))
    for row in data['overlap']:
        body.extend(struct.pack('<7Iqq',*row['identity'],row['ea'],row['eb']));body.extend(struct.pack('<'+str(len(row['source']))+'d',*row['source']))
    body.extend(timing.encode(data['actions']));return bytes(body)
def channel_event(channels,step):
    n=128 if step==1 else 64
    g=(40 if channels%3==0 else -1) if step==1 else ((50 if channels%3==0 else 10 if channels%5==0 else -1) if step==2 else -1)
    return n,g,int(step==2),int(step==1 and channels%7==0)
def span_products(previous,current,ea,eb,head,count,coefficients,window):
    a,b=len(previous),len(current)
    for i in range(count):
        t=head+i;products=[]
        for source,index,e,p,q in ((previous,a//2+t,ea,a,b),(current,t+(b-a)//4,eb,a,b)):
            n=len(source);operand=source[index] if 0<=index<n else 0.0;factor=window.factor_at(n,p,q,index,coefficients)
            products.append(window.exact(window.bits(operand),window.bits(factor),e))
        yield products
def compare_owner(body,data,timing,window,pcm):
    r=Reader(body);need(r.take('8s')==b'VSYNOWNO' and r.take('I')==8,'owner capture header');coefficients={}
    for n in window.SIZES:
        need(r.take('I')==n,'actual owner lookups');coefficients[n]=r.take(str(n//2)+'d')
        need(tuple(map(window.bits,coefficients[n]))==tuple(map(window.bits,data['coefficients'][n])),'qualified actual binary64 lookup identity')
    need(r.take('I')==864,'complete owner overlap corpus');previous=[];state=None;history=[];exponents=[];overlap_values=0
    for row in data['overlap']:
        s,l,pattern,step,a,n,count=row['identity'];need(r.take('7Iqq')==(*row['identity'],row['ea'],row['eb']),'all actual owner overlap record identities')
        if step==0:state=timing.initial(s,l);previous=[];history=[0x7ff8000000000042]*(l//2+2);exponents=[0xa5a5a5a5a5a5a5a5]*3
        if step==4:state=timing.initial(s,l);previous=[]
        state,wanted=timing.apply(state,(n,-1,0,0));actual=r.take('5Iq');channels,samples=r.take('IQ');after=r.take('5I2Q')
        need(actual==wanted and channels==1 and samples==count and after==timing.bounded(state),'every owner timing field, reset and unknown-GP span')
        source=r.take(str(n)+'d');need(tuple(map(window.bits,source))==tuple(map(window.bits,row['source'])),'all source DATA bits')
        history[:n//2]=list(map(window.bits,source[n//2:]));exponents[0]=row['eb']&((1<<64)-1)
        need(r.take(str(l//2+2)+'Q')==tuple(history) and r.take('3Q')==tuple(exponents),'complete active/unused history and exponent storage')
        got=r.take(str(samples)+'h') if samples else ();expected=tuple(pcm.reference(*pair) for pair in span_products(previous,source,row['ea'],row['eb'],0,count,coefficients,window))
        need(got==expected,'all exact stateful owner overlap PCM values');overlap_values+=samples;previous=source
    need(r.take('I')==20019,'complete timing-action campaign');current=timing.initial(0,0);timing_values=0
    for row in data['actions']:
        action=r.take('I');before=r.take('5I2Q');event=r.take('IqII');after=r.take('5I2Q');actual=r.take('5Iq');samples,hash_value=r.take('QQ')
        if row['action']==3:current=row['seed'].copy()
        need(action==row['action'] and before==timing.bounded(current) and event==tuple(row['event']),'all seeded/current timing-action metadata')
        if action==0:current=timing.initial(row['seed']['short'],row['seed']['long']);wanted=(0,)*6
        elif action==2:current=timing.initial(current['short'],current['long']);wanted=(0,)*6
        else:current,wanted=timing.apply(current,event)
        need(after==timing.bounded(current) and actual==wanted and samples==wanted[3] and
            hash_value==(14695981039346656037*pow(1099511628211,2*samples,1<<64))% (1<<64),
            'all owner timing transitions and losslessly encoded zero PCM outputs')
        timing_values+=samples
    need(r.take('I')==255,'all legal channel counts');channel_values=0;head_rows=tail_rows=0
    for channels in range(1,256):
        need(r.take('I')==channels,'complete legal channel domain');current=timing.initial(64,128)
        previous=[[] for _ in range(channels)];previous_e=[0]*channels;history=[0x7ff8000000000042]*(channels*64+2);exponents=[0xa5a5a5a5a5a5a5a5]*(channels+2)
        for step in range(3):
            event=channel_event(channels,step);n=event[0];need(r.take('I')==step,'channel event order');actual=r.take('5Iq');samples=r.take('Q')
            current,wanted=timing.apply(current,event);need(actual==wanted and samples==wanted[3]*channels,'channel-shared timeline/trim/interleave shape')
            source=[tuple(window.sample(i*37+ch*17+step*11) for i in range(n)) for ch in range(channels)]
            e=[(1<<63)-1 if (ch+step)&1 else -(1<<63) for ch in range(channels)]
            for ch in range(channels):history[ch*64:ch*64+n//2]=map(window.bits,source[ch][n//2:]);exponents[ch]=e[ch]&((1<<64)-1)
            need(r.take(str(channels*64+2)+'Q')==tuple(history) and r.take(str(channels+2)+'Q')==tuple(exponents),'every channel cache, stride and untouched tail')
            got=r.take(str(samples)+'h') if samples else ();expected=[0]*samples
            for ch in range(channels):
                for i,pair in enumerate(span_products(previous[ch],source[ch],previous_e[ch],e[ch],wanted[1],wanted[3],coefficients,window)):
                    expected[i*channels+ch]=pcm.reference(*pair)
            need(tuple(expected)==got,'all channel-domain exact PCM values including signed64 endpoint scales and trimming')
            channel_values+=samples;head_rows+=wanted[1]>0;tail_rows+=wanted[2]>0;previous=source;previous_e=e
        need(r.take('5I2Q')==timing.bounded(timing.initial(64,128)),'hard reset primes again after unread-history test')
    need(r.at==len(body),'no missing or trailing owner capture bytes')
    return dict(passed=True,overlap_rows=864,overlap_pcm_values=overlap_values,timing_actions=20019,timing_pcm_zero_values=timing_values,
        channel_counts=255,channel_pushes=765,channel_pcm_values=channel_values,channel_start_trim_rows=head_rows,channel_end_trim_rows=tail_rows,
        saved_underflow_witnesses=17962,saved_witnesses_at_least1074=13767,witness_identity_sha256=data['witness_metrics']['identity_sha256'],
        zero_PCM_encoding='exact zero run length and FNV64, with every actual S16 asserted zero',old_overlap_API_executed=False,old_PCM_API_executed=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    out=args.output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh task-local output');out.mkdir(parents=True)
    report=dict(completed=False,passed=False,commands=[],sources={},sanitizers=['address','undefined'],native_executed=False,
        production_selected=False,private_decoder_executed=False,saved_transform_or_gain_inputs_used=False)
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
        freeze(Path(__file__),'runner.py')
        for name in COMPONENTS:
            for path in sorted((ROOT/'idf/components'/name).rglob('*')):
                if path.is_file():freeze(path,'components/'+name+'/'+path.relative_to(ROOT/'idf/components'/name).as_posix())
        for name in ('vorbis_synthesis_host.c','vorbis_synthesis_pipeline.c','vorbis_synthesis_pipeline.h'):freeze(ROOT/'tests/native'/name,'native/'+name)
        original,model,references,xiph,saved=original_data();data(original,'original31.json');data(saved,'saved-Xiph-PCM.bin')
        for index,row in enumerate(model['cases']):data(references[row['id']],f'reference/{index:02}.s16le')
        need(sha(freeze(ROOT/'tests/test-vorbis-timing.py','timing-oracle.py'))==TIMING_SHA,'pinned local unlimited timing oracle')
        timing=load(out/'sources/timing-oracle.py','frozen_synthesis_timing')
        need(sha(freeze(ROOT/'tests/test-vorbis-window-exact.py','window-oracle.py'))==WINDOW_SHA,'pinned exact-window pure reader')
        need(sha(freeze(ROOT/'tests/test-vorbis-pcm-exact.py','pcm-oracle.py'))==PCM_SHA,'pinned exact-pair pure reader')
        window=load(out/'sources/window-oracle.py','frozen_synthesis_window');pcm=load(out/'sources/pcm-oracle.py','frozen_synthesis_pcm')
        owner=owner_data(model,timing,window);data(owner['saved_capture'],'saved-overlap-DATA.bin')
        (out/'owner-input.bin').write_bytes(encode_owner(owner,timing));report['owner_input_sha256']=sha((out/'owner-input.bin').read_bytes())
        report['owner_recipe']=dict(overlap_rows=864,timing_actions=20019,channels=list(range(1,256)),waveform='owner_wave/sample(i*37+channel*17+step*11)',
            signed64_exponents='INT64_MIN/MAX selected by (channel+step)&1',witnesses=owner['witness_metrics'])
        (out/'input.bin').write_bytes(encode(model));report.update(input_sha256=sha((out/'input.bin').read_bytes()),original31_sha256=ORIGINAL_SHA,
            raw_API_input_bytes=sum(len(bytes.fromhex(row[key])) for row in model['cases'] for key in ('identification_hex','setup_hex','audio_hex')),
            retained_comment_bytes=sum(len(bytes.fromhex(row['comment_hex'])) for row in model['cases']))
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py');templates=[ast.literal_eval(n.value) for n in ast.parse(origin).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SUPERVISOR' for t in n.targets)]
        need(len(templates)==1 and templates[0].count('assert 0<timeout<=60')==1,'documented timeout-only supervisor derivation')
        (out/'supervisor.py').write_text(templates[0].replace('assert 0<timeout<=60','assert 0<timeout<=180'),encoding='utf-8',newline='\n');report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes());save()
        report['compiler_version']=run('compiler-version',['gcc','--version'])
        units=[path for name in COMPONENTS for path in sorted((out/'sources/components'/name).glob('*.c'))]
        units.extend(out/'sources/native'/name for name in ('vorbis_synthesis_pipeline.c','vorbis_synthesis_host.c'))
        flags=['gcc','-std=c11','-O1','-g','-UNDEBUG','-fno-fast-math','-ffp-contract=off','-fno-pie','-no-pie','-fsanitize=address,undefined',
            '-fno-sanitize-recover=all','-fno-omit-frame-pointer','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror',
            *['-I'+linux(out/'sources/components'/name/'include') for name in COMPONENTS]]
        run('compile',[*flags,*map(linux,units),'-Wl,--gc-sections','-lm','-o',linux(out/'synthesis')])
        text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',linux(out/'synthesis'),linux(out/'input.bin'),linux(out/'capture.bin')])
        match=re.fullmatch(r'SYNTHESIS_CAPTURE cases=31 packets=(\d+) pcm_bytes=(\d+) failed=(\d+) checks=(\d+) live=0 bytes=0\s*',text)
        need(match is not None and not (out/'execute.stderr.log').read_bytes(),'whole raw capture without sanitizer diagnostics')
        measured=compare((out/'capture.bin').read_bytes(),model,references,xiph,timing);report.update(completed=True,measurements=measured,
            controls=dict(zip(('packets','pcm_bytes','failed','checks'),map(int,match.groups()))),capture_sha256=sha((out/'capture.bin').read_bytes()),binary_sha256=sha((out/'synthesis').read_bytes()))
        save();need(measured['passed'],'complete31/434/738560 PCM and14 relations at unchanged2 bound')
        owner_text=run('execute-owner',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',
            linux(out/'synthesis'),'--owner',linux(out/'owner-input.bin'),linux(out/'owner-capture.bin')])
        owner_match=re.fullmatch(r'SYNTHESIS_OWNER overlap=864 timing=20019 channels=255 pushes=(\d+) values=(\d+) refusals=(\d+) checks=(\d+)\s*',owner_text)
        need(owner_match is not None and not (out/'execute-owner.stderr.log').read_bytes(),'complete guarded owner campaign without diagnostics')
        report['owner_measurements']=compare_owner((out/'owner-capture.bin').read_bytes(),owner,timing,window,pcm)
        report['owner_controls']=dict(zip(('pushes','values','refusals','checks'),map(int,owner_match.groups())))
        report['owner_capture_sha256']=sha((out/'owner-capture.bin').read_bytes());save()
        for label,pin in report['sources'].items():need(sha((out/'sources'/label).read_bytes())==pin,'frozen source/data unchanged')
        report['passed']=True;save();print(json.dumps(dict(passed=True,controls=report['controls'],measurements=measured)));return 0
    except BaseException as error:report['error']=repr(error);save();raise


if __name__=='__main__':raise SystemExit(main())
