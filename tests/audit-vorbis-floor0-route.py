"""Read saved packet captures/models; independent Decimal floor0 data audit."""
import argparse,hashlib,importlib.util,json,math,struct,zipfile
from collections import Counter
from decimal import Context,Decimal,ROUND_FLOOR,localcontext
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
R=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args();OUT=args.output.resolve()
if not OUT.is_relative_to(R) or OUT==R or OUT.exists():raise ValueError('Fresh task-local output directory required')
PINS={'tests/test-vorbis-setup.py': 'ce69b4136ac1b1a4b71e185e6c600330e46cfb8b2b14c3d4a1e54c044afb02ff', 'tests/test-vorbis-floor-packet.py': '8ab01db0169af95e75f7aa6cc1e7c28df48371f94f445aaa03c08882c17776d7', 'tests/test-vorbis-residue.py': '1191a648a9070a995b1e256519ce71891f70779d924db651db16c490c856f31d', 'tests/vorbis_packet_frame_model.py': '5ed0ad7b589fc16de2d99f5aca77e179808aa0553fd22d9907b59369abcd77a9', 'tests/test-vorbis-floor1-frame.py': '570f1cc80a4eea6611bb2ef8a051ce11d1a9e60d6aff96afbc764f247ffccdad', 'tests/test-vorbis-packet-frame.py': '7c449b4b190500b0ab5931205f06e51e9f691112ebea80ac1affb7b200cb22d0', 'tests/test-vorbis-floor0-angles.py': '1965f554980254900e5df6fb92ebfa2e1dd5ffa159ff9383561df33782e4a742', 'tests/test-vorbis-floor0-numeric.py': '0d3f49022a2c6c13cf8ab820b4b3aab97913fd46eb58bc70562230a14de5d088'}
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(body):return hashlib.sha256(body).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
sources={}
def load(name):
    path=R/'tests'/name;sources['tests/'+name]=sha(path.read_bytes())
    need(sources['tests/'+name]==PINS['tests/'+name],'Pinned independent pure reader/oracle')
    spec=importlib.util.spec_from_file_location('audit_'+name.replace('-','_').replace('.','_'),path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
archive_path=R/'tests/results/vorbis-floor1-product-20261026/captures.zip'
archive_body=archive_path.read_bytes()
need(sha(archive_body)=='3b74cc7425b315997011040b6b6a8924b908cdff0404e0d0601cbb81a68a93ea','pinned saved evidence')
with zipfile.ZipFile(archive_path) as archive:
    bodies={n:archive.read('frame03/'+n) for n in ['sources/original31.json','cases.json','expected.json','capture.bin']}
    archived_helpers={name:archive.read('frame03/sources/'+name) for name in
        ['test-vorbis-setup.py','test-vorbis-floor-packet.py','test-vorbis-residue.py','vorbis_packet_frame_model.py']}
setup=load('test-vorbis-setup.py');floor=load('test-vorbis-floor-packet.py')
residue=load('test-vorbis-residue.py');model=load('vorbis_packet_frame_model.py')
frame_reader=load('test-vorbis-floor1-frame.py');capture_reader=load('test-vorbis-packet-frame.py')
angle=load('test-vorbis-floor0-angles.py');numeric=load('test-vorbis-floor0-numeric.py')
for name,body in archived_helpers.items():need(body==(R/'tests'/name).read_bytes(),'unchanged pure source helper')
original=json.loads(bodies['sources/original31.json']);cases=json.loads(bodies['cases.json'])
expected=json.loads(bodies['expected.json'])
actual,controls=frame_reader.decode_output(bodies['capture.bin'],cases,capture_reader)
comparison=frame_reader.compare(cases,actual,expected)
need(comparison['passed'] and comparison['original_packets']==434,'full captured front end matches expected')
need(len(original['cases'])==31 and len(original['relations'])==14,'all original identities/relations')
floor.REFERENCE=setup;residue.REFERENCE=setup
identities=[];stream_results=[];all_log=[];support_log=[];all_d=[];all_lsp=[];all_res=[]
field_sets={name:set() for name in ['order','rate','map_size','amplitude_bits','amplitude_offset','raw_amplitude','residue_exponent','residue_magnitude_bits','residue_limbs']}
domain_counts=Counter();floor0_packets=floor0_channels=coefficient_values=total_floor_bins=total_support_bins=0
packet_cursor=0;equivalence={};gain_cache={};map_cache={};bark_boundary_distance=[];spans=[]
def exact_affine(value):
    return residue.unpack(value['minimum_bits'])*value['minimum_multiplier']+residue.unpack(value['delta_bits'])*value['delta_multiplier']
def format_number(value):
    with localcontext(Context(prec=45,Emin=-1000000,Emax=1000000)):return str(+value)
def range_summary(values):
    return None if not values else dict(min=format_number(min(values)),max=format_number(max(values)))
def integer_range(values):return None if not values else dict(min=min(values),max=max(values),distinct=len(set(values)))
def exact_string(value):return str(value.numerator) if value.denominator==1 else f'{value.numerator}/{value.denominator}'
def maps(rate,bins,size):
    key=(rate,bins,size)
    if key in map_cache:return map_cache[key]
    results=[]
    for precision in (120,240):
        numeric.DECIMAL_CONTEXT=Context(prec=precision,Emin=-1000000,Emax=1000000)
        numeric.bark_map.cache_clear()
        results.append(numeric.bark_map(rate,bins,size))
    need(results[0]==results[1],'Bark integer map stable at120/240 digits')
    with localcontext(numeric.DECIMAL_CONTEXT):
        nyquist=numeric.bark(Decimal(rate)/2)
        for i in range(1,bins):
            value=numeric.bark(Decimal(rate)*i/(2*bins))*size/nyquist
            low=value.to_integral_value(rounding=ROUND_FLOOR)
            bark_boundary_distance.append(min(value-low,low+1-value))
    map_cache[key]=results[1];return results[1]
@lru_cache(maxsize=None)
def denominator(angles,bin_index,size):
    bits=[]
    for value in angles:
        converted=float(value)
        need(Fraction.from_float(converted)==value,'each original affine LSP is exactly binary64 representable')
        bits.append(struct.pack('>d',converted).hex())
    return angle.denominator(tuple(bits),bin_index,size)
def logarithm(angles,bin_index,size,raw,bits,offset):
    key=(angles,bin_index,size,raw,bits,offset)
    if key not in gain_cache:
        d=denominator(angles,bin_index,size)
        need(d>0,'observed finite positive floor denominator')
        with localcontext(angle.context(800)):
            value=(Decimal(raw)*offset/((1<<bits)-1)/d.sqrt()-offset)*angle.db_coefficient(800)
        gain_cache[key]=(d,value)
    return gain_cache[key]
for stream in original['cases']:
    stream_logs=[];stream_support=[];stream_ds=[];stream_lsp=[];stream_res=[];stream_fields=Counter()
    stream_channels=stream_packets=stream_bins=stream_nonzero=0;canonical_stream=[];stream_configuration=None
    identity=setup.identification(bytes.fromhex(stream['identification_hex']),len(stream['identification_hex'])*4)
    context=setup.parse_setup(bytes.fromhex(stream['setup_hex']),len(stream['setup_hex'])*4,identity)
    audio=bytes.fromhex(stream['audio_hex']);offsets=stream['offsets']
    need(len(offsets)==15 and offsets[0]==0 and offsets[-1]==len(audio),'all14 original packets')
    for ordinal,(begin,end) in enumerate(zip(offsets,offsets[1:])):
        row=cases['cases'][packet_cursor];decoded=actual[packet_cursor];packet=audio[begin:end]
        need(row['id']=='original31-'+stream['id']+'-p'+str(ordinal),'ordered original packet identity')
        need(row['identification_hex']==stream['identification_hex'] and row['setup_hex']==stream['setup_hex'] and
             row['packet_hex']==packet.hex() and row['packet_bits']==len(packet)*8 and row['start_bit']==0 and
             row['initial_eop'] is False,'unchanged original packet/header bytes')
        independently=model.expected_case(row,setup,floor,residue)
        need(decoded['decode_status']==0 and decoded['frame']==independently['frame'],'independent exact front-end for every original packet')
        frame=decoded['frame'];layout=frame['spectrum_layout'];types=[f['type'] for f in frame['floors']]
        identities.append(dict(id=row['id'],packet_sha256=sha(packet),frame_sha256=sha(canonical(frame)),floor_types=types))
        own_packet=[];has_floor0=False
        for channel,state in enumerate(frame['floors']):
            if state['type']!=0:continue
            has_floor0=True;floor0_channels+=1;stream_channels+=1
            info=floor.floor_info(context,state['floor_index']);amp=state['amplitude']
            configuration=dict(order=info['order'],rate=info['rate'],map_size=info['bark'],
                amplitude_bits=info['bits'],amplitude_offset=info['offset'])
            if stream_configuration is None:stream_configuration=configuration
            else:need(stream_configuration==configuration,'one retained floor0 configuration in each original stream')
            for name,value in [('order',info['order']),('rate',info['rate']),('map_size',info['bark']),
                ('amplitude_bits',info['bits']),('amplitude_offset',info['offset']),('raw_amplitude',amp['raw_amplitude']),
                ('residue_exponent',layout['exponent']),('residue_magnitude_bits',layout['magnitude_bits']),('residue_limbs',layout['limbs'])]:
                field_sets[name].add(value)
            domain_counts['present' if state['present'] else 'absent']+=1
            domain_counts['zero_order']+=info['order']==0;domain_counts['zero_rate']+=info['rate']==0
            domain_counts['zero_map']+=info['bark']==0;domain_counts['zero_offset']+=info['offset']==0
            domain_counts['zero_raw_amplitude']+=amp['raw_amplitude']==0
            domain_counts['implicit_zero_residue_grid']+=frame['implicit_zero']
            need(state['present'] and info['rate'] and info['bark'] and info['order'] and amp['raw_amplitude'],'observed original active domain')
            count=state['value_count'];start=state['value_offset']
            need(count==info['order'],'complete actual LSP extent')
            angles=tuple(exact_affine(x) for x in frame['floor0'][start:start+count])
            all_lsp.extend(angles);stream_lsp.extend(angles);coefficient_values+=len(angles)
            # Rational nonzero LSPs in(0,3), with pi>3, cannot equal a rational
            # multiple of pi; cos(phi)-cos(theta) is therefore never zero here.
            need(all(0<value<3 for value in angles),'exact rational positive/nonpole LSP proof domain')
            domain_counts['strictly_increasing_LSP_channels']+=all(a<b for a,b in zip(angles,angles[1:]))
            values=[]
            for bin_index in range(layout['bins']):
                words=frame['spectrum'][(channel*layout['bins']+bin_index)*layout['limbs']:(channel*layout['bins']+bin_index+1)*layout['limbs']]
                integer=sum(w<<(32*i) for i,w in enumerate(words))
                if words and words[-1]&0x80000000:integer-=1<<(32*layout['limbs'])
                value=Fraction(integer)*(Fraction(2)**layout['exponent']);values.append(value)
            all_res.extend(values);stream_res.extend(values)
            mapped=maps(info['rate'],layout['bins'],info['bark'])
            logs={}
            for mapped_bin in set(mapped):
                d,value=logarithm(angles,mapped_bin,info['bark'],amp['raw_amplitude'],info['bits'],info['offset'])
                logs[mapped_bin]=value;all_d.append(d);stream_ds.append(d)
            ownlogs=[logs[m] for m in mapped];nonzero=[v for v,x in zip(ownlogs,values) if x]
            with localcontext(angle.context(800)):
                spans.append(dict(id=row['id'],channel=channel,all_bins=max(ownlogs)-min(ownlogs),
                    nonzero_residue_bins=max(nonzero)-min(nonzero)))
            all_log.extend(ownlogs);stream_logs.extend(ownlogs);support_log.extend(nonzero);stream_support.extend(nonzero)
            total_floor_bins+=len(mapped);stream_bins+=len(mapped);total_support_bins+=len(nonzero);stream_nonzero+=len(nonzero)
            own_packet.append(dict(channel=channel,angles=list(map(exact_string,angles)),
                raw_amplitude=amp['raw_amplitude'],amplitude_bits=info['bits'],amplitude_offset=info['offset'],
                rate=info['rate'],map_size=info['bark'],spectrum=list(map(exact_string,values))))
        if has_floor0:floor0_packets+=1;stream_packets+=1;canonical_stream.append(own_packet)
        packet_cursor+=1
    if stream_packets:
        key=stream['id'].replace('-minp1','');digest=sha(canonical(canonical_stream))
        if key in equivalence:need(equivalence[key]==digest,'original/equivalent exact floor0 input/residue identity')
        else:equivalence[key]=digest
        stream_results.append(dict(id=stream['id'],packets=stream_packets,channels=stream_channels,
            configuration=stream_configuration,identification_rate=identity['sample_rate'],
            short_block=stream['short_block'],long_block=stream['long_block'],
            floor_bins=stream_bins,nonzero_residue_bins=stream_nonzero,
            exact_LSP_range=dict(min=exact_string(min(stream_lsp)),max=exact_string(max(stream_lsp))),
            exact_residue_range=dict(min=exact_string(min(stream_res)),max=exact_string(max(stream_res))),
            denominator_range=range_summary(stream_ds),log2_gain_range=range_summary(stream_logs),
            nonzero_residue_log2_gain_range=range_summary(stream_support),
            canonical_floor0_inputs_sha256=digest,reference_pcm_sha256=stream['reference_pcm_sha256']))
need(packet_cursor==434 and floor0_packets==168 and floor0_channels==336 and len(stream_results)==12,'complete actual floor0 subset')
need(len(equivalence)==6,'all six floor0 original/equivalent pairs')
@lru_cache(maxsize=None)
def denominator_crosscheck(angles,bin_index,size):
    # A second existing Decimal model uses Machin pi/direct cosine rather than
    # the800-digit Chudnovsky model. No production phase/sine code is executed.
    with localcontext(Context(prec=150,Emin=-1000000,Emax=1000000)):
        w=2*numeric.decimal_cos(numeric.decimal_pi(180)*bin_index/size)
        products=[Decimal(1),Decimal(1)]
        for index,value in enumerate(angles):
            phi=Decimal(value.numerator)/value.denominator
            products[index%2]*=w-2*numeric.decimal_cos(phi)
        even,odd=products
        if len(angles)%2:return +(even*even+(4-w*w)*odd*odd)/4
        return +((2+w)*even*even+(2-w)*odd*odd)/4
max_d_relative=max_log_absolute=Decimal(0)
for (angles,bin_index,size,raw,bits,offset),(d800,log800) in gain_cache.items():
    with localcontext(Context(prec=150,Emin=-1000000,Emax=1000000)):
        d150=denominator_crosscheck(angles,bin_index,size)
        log150=(Decimal(raw)*offset/((1<<bits)-1)/d150.sqrt()-offset)*Decimal('0.11512925')/Decimal(2).ln()
        d_error=abs(d150-d800)/d800;log_error=abs(log150-log800)
        need(d_error<Decimal('1e-100') and log_error<Decimal('1e-100'),'ordinary-corpus independent precision convergence')
        max_d_relative=max(max_d_relative,d_error);max_log_absolute=max(max_log_absolute,log_error)
result=dict(schema='vorbis-floor0-original-route-audit-v1',
    scope='Saved original31 packet/front-end data and independent floor0 Decimal math only; no new decoder/linear spectrum/PCM execution',
    input_archive=dict(path=archive_path.relative_to(R).as_posix(),sha256=sha(archive_body),
        members={name:dict(sha256=sha(body),bytes=len(body)) for name,body in bodies.items()}),
    local_pure_sources_sha256=sources,analysis_source_sha256=sha(Path(__file__).read_bytes()),
    original=dict(streams=31,packets=434,ordered_identity_sha256=sha(canonical(identities)),identities=identities,
        relations=14,relations_sha256=sha(canonical(original['relations'])),retained_host_C_capture_rows_compared=comparison['cases']),
    floor0=dict(streams=12,packets=168,channels=336,coefficient_values=coefficient_values,
        field_values={name:sorted(values) for name,values in field_sets.items()},domain_counts=dict(domain_counts),
        all_mapped_bins=total_floor_bins,nonzero_residue_bins=total_support_bins,
        exact_LSP_range=dict(min=exact_string(min(all_lsp)),max=exact_string(max(all_lsp)),distinct=len(set(all_lsp))),
        exact_residue_values=sorted(map(exact_string,set(all_res))),
        denominator_range=range_summary(all_d),log2_gain_range=range_summary(all_log),
        nonzero_residue_log2_gain_range=range_summary(support_log),
        maximum_per_channel_log2_gain_span=format_number(max(s['all_bins'] for s in spans)),
        maximum_per_channel_nonzero_residue_log2_gain_span=format_number(max(s['nonzero_residue_bins'] for s in spans)),
        distinct_gain_evaluations=len(gain_cache),distinct_bark_maps=len(map_cache),
        minimum_nonzero_Bark_integer_boundary_distance=format_number(min(bark_boundary_distance)),
        all_LSPs_exactly_binary64=True,finite_nonpole_proof='All LSPs are nonzero rational numbers in(0,3); theta is a rational multiple of irrational pi in[0,pi), so no cos(phi)=cos(theta); at least one weighted squared product is positive.',
        original_equivalent_pairs_exact=6,streams_detail=stream_results),
    numerical_observation=dict(denominator_and_log2_decimal_digits=800,Bark_map_context_digits=[120,240],
        Bark_pi_digits=160,all_Bark_floor_results_equal=True,
        independent_crosscheck_decimal_digits=150,independent_crosscheck_gain_values=len(gain_cache),
        independent_crosscheck_denominators=denominator_crosscheck.cache_info().currsize,
        maximum_crosscheck_denominator_relative_difference=format_number(max_d_relative),
        maximum_crosscheck_log2_gain_absolute_difference=format_number(max_log_absolute),
        convergence_threshold='1e-100; engineering crosscheck for this ordinary corpus, not a universal certified error bound',
        independent_models='Direct Decimal cosine P/Q with Chudnovsky pi; Decimal Bark atan/Machin pi; exact Fraction affine/residue arithmetic',
        formal_error_certificate=False,linear_gain_materialized=False,spectrum_materialized=False,
        int64_fit_used_as_precision_evidence=False),
    uncovered_original_domains=['absent/zero amplitude','order0/1/255','zero rate/map/offset',
        'amplitude widths0..5/7/9..63','odd floor rate','map65535','pole/indeterminate',
        'extreme affine phase/gain spans','full-width nontrivial residue','mixed floor0/floor1 channel mapping'],
    complete_floor0_or_PCM_qualified=False,native_executed=False,archived_code_executed=False,
    deferred_scopes_resumed=False)
OUT.mkdir(exist_ok=False)
(OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(dict(passed=True,output=(OUT/'audit.json').relative_to(R).as_posix(),
    bytes=(OUT/'audit.json').stat().st_size,sha256=sha((OUT/'audit.json').read_bytes()),
    original_packets=434,floor0_packets=168,floor0_channels=336,fields=result['floor0']['field_values'],
    domain_counts=result['floor0']['domain_counts'],floor_bins=total_floor_bins,nonzero_residue_bins=total_support_bins,
    exact_LSP_range=result['floor0']['exact_LSP_range'],exact_residue_values=result['floor0']['exact_residue_values'],
    log2_gain_range=result['floor0']['log2_gain_range'],nonzero_residue_log2_gain_range=result['floor0']['nonzero_residue_log2_gain_range'],
    denominator_range=result['floor0']['denominator_range'],distinct_gain_evaluations=len(gain_cache))))
