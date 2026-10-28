"""Actual raw packet -> exact frame -> floor spectrum -> reused IMDCT handoff.

All original434 packets remain present. Floor0 uses a fixed2e-12 ordinary
relative spectrum bound; the joint rounding itself is bit exact. IMDCT retains
the original5e-12*L1 bound. No window, overlap, PCM or native execution occurs.
"""
import argparse,ast,copy,hashlib,importlib.util,io,json,math,os,re,struct,subprocess,sys,time,uuid,zipfile
from decimal import Context,Decimal,localcontext
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
COMPONENTS=('native_vorbis_numeric','native_vorbis_setup_owner','native_vorbis_packet_frame',
    'native_vorbis_floor1_product','native_vorbis_transform','native_vorbis_floor0_spectrum')
PRIOR_SHA='3b74cc7425b315997011040b6b6a8924b908cdff0404e0d0601cbb81a68a93ea'
ORIGINAL_SHA='32ba4c7e401fcfd05238f929fa6874c3048237792d78f36b05a8fade5b861e24'
SPECTRUM_BOUND=2e-12
TRANSFORM_BOUND=5e-12
EXTRA_ROUTES={
    'handoff-absent-coupled':(0,0),'handoff-absent-zero-domain':(0,0),
    'handoff-order0':(0,0),'handoff-unity':(0,0),'handoff-pole':(4,4),
    'handoff-indeterminate':(5,5),'handoff-pole-zero-residue':(4,4),
    'handoff-zero-rate':(3,3),'handoff-zero-map':(3,3),
    'handoff-finite-zero-tiny':(0,0),'handoff-precision-tiny':(2,2),'handoff-wide-span':(1,1),
    'handoff-near-unity-normalization':(0,0)}


def need(test,message):
    if not test:raise ValueError(message)


def sha(body):return hashlib.sha256(body).hexdigest()
def bits(value):return struct.pack('<d',value)
def linux(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:] if sys.platform=='win32' else value


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def original_inputs():
    body=(ROOT/'tests/results/vorbis-floor1-product-20261026/captures.zip').read_bytes()
    need(sha(body)==PRIOR_SHA,'pinned complete prior evidence')
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        original=z.read('frame03/sources/original31.json')
        model=json.loads(z.read('frame03/cases.json'))
        table=z.read('frame03/sources/xiph-floor1.c')
    need(sha(original)==ORIGINAL_SHA,'original31 identity')
    original_model=dict(model,cases=[row for row in model['cases'] if row['id'].startswith('original31-')])
    need(len(original_model['cases'])==434 and len(json.loads(original)['relations'])==14,'all434 packets/all14 relation identities')
    return original,original_model,table


def signed_values(frame,channel):
    layout=frame['spectrum_layout'];limbs=layout['limbs'];values=[]
    for i in range(layout['bins']):
        words=frame['spectrum'][(channel*layout['bins']+i)*limbs:(channel*layout['bins']+i+1)*limbs]
        value=sum(word<<(32*j) for j,word in enumerate(words))
        if words and words[-1]&0x80000000:value-=1<<(32*limbs)
        values.append(value)
    return values


def exact_power(value,exponent):
    return Fraction(value*(1<<exponent)) if exponent>=0 else Fraction(value,1<<-exponent)


def readers(base):
    names=('test-vorbis-setup.py','test-vorbis-floor-packet.py','test-vorbis-residue.py',
        'vorbis_packet_frame_model.py','test-vorbis-packet-frame.py','test-vorbis-floor1-frame.py',
        'test-vorbis-transform.py','test-vorbis-floor0-angles.py','test-vorbis-floor0-numeric.py')
    return {name:load(base/name,'handoff_'+name.replace('-','_').replace('.','_')) for name in names}


def supplement(modules):
    setup=modules['test-vorbis-setup.py'];floor=modules['test-vorbis-floor-packet.py']
    residue=modules['test-vorbis-residue.py'];subject=modules['vorbis_packet_frame_model.py']
    floor.REFERENCE=setup;residue.REFERENCE=setup
    rows=[]
    for name in EXTRA_ROUTES:
        spec=residue.base_spec(1,channels=2,bins=6)
        spec['books'][1].update(lengths=[2,1,2],lookup=2,minimum_bits=residue.ONE,delta_bits=residue.ONE,value_bits=4)
        spec['books'].append(residue.book(dim=1,minimum=residue.ONE,delta=0,sequence=0,width=4))
        spec['floors']=[dict(type=0,order=1,rate=48000,bark=64,amplitude_bits=8,amplitude_offset=60,books=[2])]
        flags=[1,1]
        if name=='handoff-absent-coupled':spec['mappings'][0]['pairs']=[(0,1)];flags=[1,0]
        elif name=='handoff-absent-zero-domain':spec['floors'][0].update(rate=0,bark=0);flags=[0,0]
        elif name=='handoff-order0':spec['floors'][0]['order']=0
        elif name=='handoff-unity':spec['floors'][0]['amplitude_offset']=0
        elif name in ('handoff-pole','handoff-indeterminate','handoff-pole-zero-residue'):
            spec['books'][2]['minimum_bits']=0
            if name=='handoff-indeterminate':spec['floors'][0]['amplitude_offset']=0
            if name=='handoff-pole-zero-residue':spec['books'][1].update(minimum_bits=0,delta_bits=0)
        elif name=='handoff-zero-rate':spec['floors'][0]['rate']=0
        elif name=='handoff-zero-map':spec['floors'][0]['bark']=0
        elif name in ('handoff-finite-zero-tiny','handoff-precision-tiny'):
            spec['books'][2]['minimum_bits']=1
            if name=='handoff-finite-zero-tiny':spec['books'][1].update(minimum_bits=0,delta_bits=0)
        elif name=='handoff-wide-span':spec['books'][2]['minimum_bits']=(782<<21)|1
        elif name=='handoff-near-unity-normalization':
            spec['floors'][0].update(order=0,amplitude_bits=63,amplitude_offset=1)
            header,_,_,_=setup.make_case(name,spec);writer=setup.Writer()
            need(len(spec['modes'])==1 and not spec['modes'][0]['blockflag'],'fixed order0 raw packet prefix')
            writer.put(0,1)
            for _ in flags:
                writer.put((1<<63)-2,63);writer.put(0,1)
                book=spec['books'][2]
                floor.put_word(writer,book['lengths'],setup.greedy_words(book['lengths'])[0]['entry'])
            bins=1<<(spec['identification']['small']-1)
            residual=residue.build_case(name,spec,bins=bins,flags=flags,mapping=0,seed=1)
            subject._append_bits(writer,bytes.fromhex(residual['packet_hex']),residual['packet_bits'])
            rows.append(subject._row(name,header,writer,0));continue
        rows.append(subject._packet(name,spec,setup,floor,residue,flags))
    return rows


def compare(body,front_body,model,table,modules):
    setup=modules['test-vorbis-setup.py'];floor=modules['test-vorbis-floor-packet.py'];residue=modules['test-vorbis-residue.py']
    subject=modules['vorbis_packet_frame_model.py'];front=modules['test-vorbis-packet-frame.py'];product=modules['test-vorbis-floor1-frame.py']
    transform=modules['test-vorbis-transform.py'];angle=modules['test-vorbis-floor0-angles.py'];numeric=modules['test-vorbis-floor0-numeric.py']
    expected=[subject.expected_case(row,setup,floor,residue) for row in model['cases']]
    observed,front_controls=front.decode_output(front_body,model)
    checked=front.compare(model,observed,expected);need(checked['passed'],'complete independently modeled actual C front end')
    products=product.build_expected(model,subject,setup,floor,residue,product.table_factors(table))
    numeric.DECIMAL_CONTEXT=Context(prec=240,Emin=-1000000,Emax=1000000);numeric.bark_map.cache_clear()
    r=front.Reader(body);need(r.take('8s')==b'VF0HAND1' and r.take('I')==len(model['cases']),'complete ordered handoff header')
    channels=zero_channels=sample_values=time_values=floor0_channels=floor1_channels=0
    routed_channels=synthetic_channels=absent_nonzero=0;routes={str(i):0 for i in range(6)}
    exact_joint=nonzero_gain=normalization_channels=0;max_gain_error=max_transform_error=0.0;minimum_fraction=53
    gain_cache={};contexts={}
    def doubles(count):return tuple(r.take('d') for _ in range(count))
    def gain(angles,bark,size,amplitude):
        key=(angles,bark,size,amplitude['raw_amplitude'],amplitude['amplitude_bits'],amplitude['amplitude_offset'])
        if key not in gain_cache:
            angle_words=[]
            for value in angles:
                converted=float(value);need(Fraction.from_float(converted)==value,'ordinary original LSP is exactly binary64')
                angle_words.append(struct.pack('>d',converted).hex())
            d=angle.denominator(tuple(angle_words),bark,size) if angles else Decimal(1)
            with localcontext(angle.context(800)):
                raw=Decimal(amplitude['raw_amplitude']);offset=Decimal(amplitude['amplitude_offset'])
                value=((raw*offset/((1<<amplitude['amplitude_bits'])-1)/d.sqrt()-offset)*Decimal('0.11512925')).exp()
                gain_cache[key]=+value
        return gain_cache[key]
    for index,(case,actual,prod_row) in enumerate(zip(model['cases'],observed,products)):
        frame=actual['frame'];need(frame is not None,'every selected packet actually decodes')
        need((r.take('I'),r.take('I'))==(index,frame['floor_count']),'packet and channel order')
        if case['setup_hex'] not in contexts:contexts[case['setup_hex']]=subject._context(case,setup)
        context=contexts[case['setup_hex']]
        for channel in range(frame['floor_count']):
            floor_state=frame['floors'][channel];kind=r.take('I');route=r.take('I');bins=r.take('I');exponent=r.take('q')
            zero,approximate=r.take('II');evaluations,fraction_bits,route_sample=r.take('III')
            mapped_count=r.take('I');mapped=[r.take('H') for _ in range(mapped_count)]
            factor_count=r.take('I');factors=[r.take('Qq') for _ in range(factor_count)];materialized=r.take('I')
            wanted_route=0 if index<434 else EXTRA_ROUTES[case['id']][channel]
            need(kind==floor_state['type'] and bins==frame['spectrum_layout']['bins'] and route==wanted_route and
                 materialized==int(route==0),'each original/supplement channel retains its explicit route')
            need(zero in (0,1) and approximate in (0,1),'boolean route fields')
            if index>=434:synthetic_channels+=1
            routes[str(route)]+=1
            if route:
                need(not mapped_count and not factor_count,'noncandidate retains provenance without a partial spectrum')
                routed_channels+=1;channels+=1
                continue
            count,source_exponent=r.take('Iq');source=doubles(count)
            time_count,time_exponent=r.take('Iq');times=doubles(time_count)
            need(count==bins and time_count==2*bins and source_exponent==exponent==time_exponent,'handoff shape and retained exponent')
            raw=signed_values(frame,channel)
            if kind==0:
                floor0_channels+=1
                if zero:
                    need(not mapped_count and not factor_count and not evaluations and exponent==0 and
                         all(bits(v)==bytes(8) for v in source),'absent/proven-finite zero bypasses gain math and scratch')
                    if not floor_state['present'] and any(raw):absent_nonzero+=1
                else:
                    need(mapped_count==factor_count==bins,'nonzero candidate has complete borrowed factors/map')
                if index<434:
                    need(not zero and approximate and evaluations>0 and fraction_bits>=50,
                         'original floor0 approximation and logarithm resolution are explicit')
                    minimum_fraction=min(minimum_fraction,fraction_bits)
                info=floor.floor_info(context,floor_state['floor_index'])
                if case['id']=='handoff-near-unity-normalization':
                    need(info['order']==0 and info['bits']==63 and info['offset']==1 and
                        floor_state['amplitude']['raw_amplitude']==(1<<63)-2 and approximate and evaluations>0 and
                        any(raw),'owned order0 tiny negative nonzero logarithm is actually evaluated')
                    need(all(mantissa==1<<52 and power==frame['spectrum_layout']['exponent']-52
                        for integer,(mantissa,power) in zip(raw,factors) if integer),
                        'fraction rounding to1 normalizes exp2(1) to unity, without doubling the gain')
                    normalization_channels+=1
                expected_map=numeric.bark_map(info['rate'],bins,info['bark']) if not zero else []
                need(tuple(mapped)==tuple(expected_map),'every independently computed Bark index')
                start=floor_state['value_offset'];affine=frame['floor0'][start:start+floor_state['value_count']]
                angles=tuple(residue.unpack(v['minimum_bits'])*v['minimum_multiplier']+
                    residue.unpack(v['delta_bits'])*v['delta_multiplier'] for v in affine)
                physical_tops=[]
                for i,(integer,(mantissa,power),working) in enumerate(zip(raw,factors,source)):
                    if integer:
                        need(1<<52<=mantissa<1<<53,'complete binary64 factor significand')
                        physical_tops.append(abs(integer*mantissa).bit_length()-1+power)
                    else:need(mantissa==0,'zero residue skips only a finite product')
                    wanted=float(exact_power(integer*mantissa,power-exponent))
                    need(bits(working)==bits(wanted),'every once-rounded exact joint product')
                    exact_joint+=1
                    if integer and index<434:
                        reference=gain(angles,mapped[i],info['bark'],floor_state['amplitude'])
                        with localcontext(angle.context(800)):
                            physical=Decimal.from_float(working)*(Decimal(2)**exponent)
                            expected_physical=Decimal(integer)*(Decimal(2)**frame['spectrum_layout']['exponent'])*reference
                            relative=float(abs((physical-expected_physical)/expected_physical))
                        need(relative<=SPECTRUM_BOUND,'fixed original ordinary floor0 spectrum bound')
                        max_gain_error=max(max_gain_error,relative);nonzero_gain+=1
                    elif not integer:need(bits(working)==bytes(8),'canonical zero residue output')
                if not zero:
                    need(physical_tops and exponent==max(physical_tops)-638 and max(physical_tops)-min(physical_tops)<=1660,
                         'selected common grid from actual joint products')
            else:
                floor1_channels+=1;need(not approximate and not mapped_count and not factor_count,'unchanged exact floor1 route')
                p=prod_row['products'][channel];shape=p['layout'];values=[]
                for i in range(bins):
                    words=p['samples'][i*shape['limbs']:(i+1)*shape['limbs']]
                    integer=sum(w<<(32*j) for j,w in enumerate(words))
                    if words and words[-1]&0x80000000:integer-=1<<(32*len(words))
                    values.append(float(Fraction(integer,1<<512)))
                need(tuple(map(bits,source))==tuple(map(bits,values)) and exponent==(shape['exponent']+512 if shape['limbs'] else 0),
                     'every original exact floor1 product/conversion bit')
            reference=transform.imdct_oracle(source);norm=math.fsum(abs(x) for x in source)
            for value,wanted in zip(times,reference):
                need(math.isfinite(value) and abs(value-wanted)<=TRANSFORM_BOUND*norm,'unchanged IMDCT normwise bound')
                if norm:max_transform_error=max(max_transform_error,abs(value-wanted)/norm)
                else:need(bits(value)==bytes(8),'canonical zero transformed block')
            channels+=1;zero_channels+=bool(zero);sample_values+=bins;time_values+=time_count
    need(r.at==len(body),'no unread or trailing handoff bytes')
    need(sum(row['id'].startswith('original31-') for row in model['cases'])==434 and
         floor0_channels-synthetic_channels+routed_channels==336 and floor1_channels==532,'all original packet/channel route identities')
    return dict(passed=True,packets=len(model['cases']),original_packets=434,channels=channels,
        original_floor0_packets=168,original_floor0_channels=336,materialized_floor0_channels=floor0_channels,
        floor1_channels=floor1_channels,spectrum_values=sample_values,time_values=time_values,
        exact_floor0_joint_values=exact_joint,nonzero_floor0_reference_values=nonzero_gain,
        distinct_decimal_gains=len(gain_cache),zero_channels=zero_channels,
        minimum_original_log_fraction_bits=minimum_fraction,maximum_floor0_relative_error=max_gain_error,
        floor0_relative_bound=SPECTRUM_BOUND,maximum_transform_normalized_error=max_transform_error,
        transform_normwise_bound=TRANSFORM_BOUND,front_end_original_packets=checked['original_packets'],
        synthetic_channels=synthetic_channels,routed_channels=routed_channels,route_counts=routes,
        absent_floor_with_nonzero_residue=absent_nonzero,near_unity_normalization_channels=normalization_channels,
        front_end_controls=front_controls,PCM_executed=False,full_codec_qualified=False)


def corruption_controls(body,front_body,model,table,modules):
    capture=modules['test-vorbis-packet-frame.py'];r=capture.Reader(body)
    need(r.take('8s')==b'VF0HAND1','capture offset anchors');count=r.take('I')
    found={}
    for _ in range(count):
        r.take('I');channels=r.take('I')
        for _ in range(channels):
            kind=r.take('I');route_at=r.at;route=r.take('I');r.take('I');r.take('q');r.take('II');r.take('III')
            mapped=r.take('I')
            if mapped and 'map' not in found:found['map']=r.at
            for _ in range(mapped):r.take('H')
            factors=r.take('I')
            for _ in range(factors):
                at=r.at;mantissa=r.take('Q');r.take('q')
                if mantissa and 'factor' not in found:found['factor']=at
            materialized=r.take('I')
            found.setdefault('route',route_at)
            if not materialized:continue
            n=r.take('I');r.take('q');found.setdefault('source',r.at)
            for _ in range(n):r.take('d')
            n=r.take('I');r.take('q');found.setdefault('time',r.at)
            for _ in range(n):r.take('d')
    need(set(found)=={'map','factor','route','source','time'},'all declared corruption anchors')
    factor=bytearray(body[found['factor']:found['factor']+8]);factor[0]^=1
    edits=[('magic',0,b'X'),('packet',12,struct.pack('<I',999)),('route',found['route'],struct.pack('<I',9)),
        ('Bark',found['map'],struct.pack('<H',65535)),('factor',found['factor'],bytes(factor)),
        ('spectrum',found['source'],struct.pack('<d',math.nan)),('IMDCT',found['time'],struct.pack('<d',math.nan))]
    damaged=[(name,body[:at]+value+body[at+len(value):],front_body) for name,at,value in edits]
    damaged.extend([('truncated',body[:-1],front_body),('trailing',body+b'X',front_body),
        ('front-magic',body,b'X'+front_body[1:])])
    for name,bad,front_bad in damaged:
        try:compare(bad,front_bad,model,table,modules)
        except (ValueError,struct.error):continue
        raise ValueError('damaged capture was accepted: '+name)
    return [name for name,_,_ in damaged]


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();out=args.output.resolve()
    need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh task-local output');out.mkdir(parents=True)
    report=dict(completed=False,passed=False,commands=[],sources={},sanitizers=['address','undefined'],
        floor0_gain_executed=True,transform_executed=True,overlap_executed=False,PCM_executed=False,
        native_executed=False,production_selected=False,deferred_scopes_resumed=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    def freeze(path,label):
        data=path.read_bytes();target=out/'sources'/label;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        report['sources'][label]=sha(data);return data
    def run(name,argv):
        nonce=uuid.uuid4().hex;request,receipt,stop=(out/(name+s) for s in ('.request.json','.receipt.json','.stop'))
        request.write_text(json.dumps(dict(nonce=nonce,argv=list(map(str,argv)),timeout=60,receipt=linux(receipt),stop=linux(stop))),encoding='utf-8')
        command=(['wsl.exe','--exec','python3'] if os.name=='nt' else [sys.executable])+[linux(out/'supervisor.py'),linux(request)]
        row=dict(name=name,argv=command,child_argv=list(map(str,argv)),nonce=nonce,request_sha256=sha(request.read_bytes()))
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
        for component in COMPONENTS:
            folder=ROOT/'idf/components'/component
            for path in sorted(folder.rglob('*')):
                if path.is_file():freeze(path,'components/'+component+'/'+path.relative_to(folder).as_posix())
        for name in ('vorbis_packet_frame_host.c','vorbis_floor0_frame_host.c'):
            freeze(ROOT/'tests/native'/name,'native/'+name)
        for name in ('test-vorbis-setup.py','test-vorbis-floor-packet.py','test-vorbis-residue.py',
            'vorbis_packet_frame_model.py','test-vorbis-packet-frame.py','test-vorbis-floor1-frame.py',
            'test-vorbis-transform.py','test-vorbis-floor0-angles.py','test-vorbis-floor0-numeric.py'):
            freeze(ROOT/'tests'/name,name)
        original,model,table=original_inputs()
        (out/'sources/original31.json').write_bytes(original);(out/'sources/xiph-floor1.c').write_bytes(table)
        report['sources']['original31.json']=sha(original);report['sources']['xiph-floor1.c']=sha(table)
        modules=readers(out/'sources');model['cases'].extend(supplement(modules))
        report['transform_anchors']=modules['test-vorbis-transform.py'].oracle_anchors()
        report['relations_sha256']=sha(json.dumps(json.loads(original)['relations'],sort_keys=True).encode())
        report['original_relations']=14
        (out/'model.json').write_text(json.dumps(model,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
        (out/'input.bin').write_bytes(modules['test-vorbis-packet-frame.py'].encode_input(model))
        report.update(model_sha256=sha((out/'model.json').read_bytes()),input_sha256=sha((out/'input.bin').read_bytes()))
        origin=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-origin.py')
        scripts=[ast.literal_eval(node.value) for node in ast.parse(origin).body if isinstance(node,ast.Assign) and
            any(isinstance(target,ast.Name) and target.id=='SUPERVISOR' for target in node.targets)]
        need(len(scripts)==1,'one owned supervisor');(out/'supervisor.py').write_text(scripts[0],encoding='utf-8',newline='\n')
        report['supervisor_sha256']=sha((out/'supervisor.py').read_bytes());save()
        report['compiler_version']=run('compiler-version',['gcc','--version'])
        common=['gcc','-std=c11','-O1','-g','-UNDEBUG','-fno-fast-math','-ffp-contract=off','-fno-pie','-no-pie',
            '-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-ffunction-sections','-fdata-sections',
            '-Wall','-Wextra','-Werror',*['-I'+linux(out/'sources/components'/name/'include') for name in COMPONENTS]]
        units=[p for name in COMPONENTS for p in sorted((out/'sources/components'/name).glob('*.c'))]
        units.append(out/'sources/native/vorbis_floor0_frame_host.c')
        run('compile',[*common,*map(linux,units),'-Wl,--gc-sections','-lm','-o',linux(out/'handoff')])
        text=run('execute',['env','ASAN_OPTIONS=detect_leaks=1:abort_on_error=1','UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',
            linux(out/'handoff'),linux(out/'input.bin'),linux(out/'front.bin'),linux(out/'capture.bin')])
        match=re.fullmatch(r'FLOOR0_HANDOFF cases=(\d+) channels=(\d+) floor0=(\d+) floor1=(\d+) refusals=(\d+) checks=(\d+) live=0 bytes=0\s*',text)
        need(match is not None and not (out/'execute.stderr.log').read_bytes(),'complete guarded handoff without diagnostics')
        measured=compare((out/'capture.bin').read_bytes(),(out/'front.bin').read_bytes(),model,table,modules)
        report['corruption_controls']=corruption_controls((out/'capture.bin').read_bytes(),(out/'front.bin').read_bytes(),model,table,modules)
        report['controls']=dict(zip(('cases','channels','floor0','floor1','refusals','checks'),map(int,match.groups())))
        for name,digest in report['sources'].items():need(sha((out/'sources'/name).read_bytes())==digest,'frozen source unchanged')
        report.update(completed=True,passed=True,measurements=measured,units=len(units),
            capture_sha256=sha((out/'capture.bin').read_bytes()),front_sha256=sha((out/'front.bin').read_bytes()),binary_sha256=sha((out/'handoff').read_bytes()))
        save();print(json.dumps(dict(passed=True,controls=report['controls'],measurements=measured)));return 0
    except BaseException as error:report['error']=repr(error);save();raise


if __name__=='__main__':raise SystemExit(main())
