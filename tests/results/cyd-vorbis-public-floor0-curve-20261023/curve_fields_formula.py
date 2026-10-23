"""Own finite floor0 formula diagnostic, never a decoder or PCM implementation."""
import argparse
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
DB_EXP_COEFFICIENT = 0.11512925
EXPECTED_IDS = (
    'floor0-even6-r0-s64-l256', 'floor0-even6-r0-s256-l2048', 'floor0-even6-r0-s64-l2048',
    'floor0-odd5-r0-s64-l256', 'floor0-odd5-r0-s256-l2048', 'floor0-odd5-r0-s64-l2048')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class Bits:
    """Bounded LSB-first reader for the frozen construction field layouts."""
    def __init__(self, data):
        self.data, self.position = data, 0

    def take(self, width):
        need(type(width) is int and 0 <= width <= 32 and self.position + width <= len(self.data) * 8,
             'Bounded field width/span required')
        value = 0
        for shift in range(width):
            bit = self.position + shift
            value |= ((self.data[bit // 8] >> (bit % 8)) & 1) << shift
        self.position += width
        return value


def read_layout(data, declaration):
    need(len(data) == declaration['bytes'], 'Original field-layout byte count')
    reader, out = Bits(data), {}
    for item in declaration['fields']:
        name, width = item['name'], item['width']
        need(name not in out and item['offset'] == reader.position, 'Complete sequential original field layout')
        value = reader.take(width)
        need(value == item['value'], 'Actual raw bit field differs: ' + name)
        out[name] = dict(value=value, width=width, offset=item['offset'])
    need(reader.position == declaration['used_bits'] and len(data) * 8 - reader.position == declaration['padding_bits'],
         'All original fields and final byte padding accounted')
    need(reader.take(declaration['padding_bits']) == 0, 'Original zero padding')
    return out


def field(fields, name, width):
    item = fields[name]
    need(item['width'] == width, 'Public field width: ' + name)
    return item['value']


def unpack_fraction(value):
    negative = bool(value & (1 << 31))
    significand = value & ((1 << 21) - 1)
    exponent = ((value >> 21) & 1023) - 788
    return (-1 if negative else 1) * significand * (Fraction(2) ** exponent)


def book(fields, number, *, dimensions, entries, length, maptype):
    prefix = f'book[{number}].'
    expected = dict(sync=(24, 0x564342), dimensions=(16, dimensions), entries=(24, entries),
                    ordered=(1, 0), sparse=(1, 0), maptype=(4, maptype), sequence_p=(1, 0))
    for key,(width,value) in expected.items():
        need(field(fields,prefix+key,width) == value, 'Exact finite fixture book representation')
    for index in range(entries):
        need(field(fields,prefix+f'length_minus_1[{index}]',5) + 1 == length, 'Exact finite fixture code lengths')
    minimum = unpack_fraction(field(fields,prefix+'minimum',32))
    delta = unpack_fraction(field(fields,prefix+'delta',32))
    width = field(fields,prefix+'value_bits_minus_1',4) + 1
    count = entries * dimensions if maptype == 2 else 2
    values = [field(fields,prefix+f'multiplicand[{i}]',width) for i in range(count)]
    return dict(number=number, dimensions=dimensions, entries=entries, minimum=minimum,
                delta=delta, values=values, value_bits=width, maptype=maptype)


def configuration(fields):
    need(field(fields,'packet_type',8) == 5
         and bytes(field(fields,f'signature[{i}]',8) for i in range(6)) == b'vorbis', 'Actual setup header')
    order = field(fields,'floor0.order',8)
    rate = field(fields,'floor0.rate',16)
    bark = field(fields,'floor0.barkmap',16)
    amplitude_bits = field(fields,'floor0.amplitude_bits',6)
    offset = field(fields,'floor0.amplitude_offset',8)
    books_count = field(fields,'floor0.books_minus_1',4) + 1
    need((order,rate,bark,amplitude_bits,offset,books_count) in
         ((6,48000,64,6,60,1),(5,48000,128,8,60,2)), 'All original parity/configuration families')
    for name,width,value in (('floor.type',16,0),('residue.type',16,0),('residue.begin',24,0),
        ('residue.end',24,16),('residue.partition_size_minus_1',24,15),('residue.classbook',8,0),
        ('residue.classifications_minus_1',6,0),('residue.cascade_low',3,1),('residue.cascade_high_present',1,0),
        ('residue.stagebook',8,1),('mapping.submaps_flag',1,0),('mapping.coupling_flag',1,0),
        ('mapping.floor',8,0),('mapping.residue',8,0),('modes_minus_1',6,1)):
        need(field(fields,name,width) == value, 'Exact original floor/residue/mapping topology')
    floor_books = []
    for i in range(books_count):
        number = field(fields,f'floor0.book[{i}]',8)
        need(number == i + 2, 'Original explicit floor book list')
        b = book(fields,number,dimensions=3,entries=2,length=1,maptype=2)
        need(b['minimum'] == 0 and b['delta'] == Fraction(1,16) and b['value_bits'] == 5,
             'Original exact zero-minimum/delta1/16 floor books')
        floor_books.append(b)
    residue_book = book(fields,1,dimensions=2,entries=4,length=2,maptype=1)
    need(residue_book['minimum'] == -1 and residue_book['delta'] == 2 and residue_book['values'] == [0,1],
         'Original lookup1 residue values')
    return dict(order=order,rate=rate,bark=bark,amplitude_bits=amplitude_bits,offset=offset,
                floor_books=floor_books,residue_book=residue_book)


def floor_and_residue(fields, config, channel, packet_metadata):
    prefix = f'floor[{channel}].'
    raw_amplitude = field(fields,prefix+'amplitude',config['amplitude_bits'])
    need(raw_amplitude > 0, 'Every original fixture channel has nonzero floor amplitude')
    selector = field(fields,prefix+'book_selector',len(config['floor_books']).bit_length())
    need(selector < len(config['floor_books']), 'Actual finite floor book selector')
    selected = config['floor_books'][selector]
    # These exact dense two-entry, length1 books have wire0/1 = entry0/1.
    # This is a construction witness, not a general entropy decoder.
    words = [field(fields,prefix+f'vq_word[{i}]',1) for i in range(2)]
    coefficients, last = [], Fraction(0)
    for word in words:
        first = word * selected['dimensions']
        vector = [selected['minimum'] + selected['delta'] * selected['values'][first+i] + last
                  for i in range(selected['dimensions'])]
        coefficients.extend(vector)
        last = vector[-1]
    used, unused = coefficients[:config['order']], coefficients[config['order']:]
    floor_expected = packet_metadata['floors'][channel]
    need(raw_amplitude == floor_expected['amplitude_raw'] and selector == floor_expected['book_selector']
         and words == floor_expected['vq_words'] and used == [Fraction(x,16) for x in floor_expected['lsp_used_units_1_16']]
         and unused == [Fraction(x,16) for x in floor_expected['lsp_ignored_units_1_16']], 'Actual floor values agree with independent original witness')
    need(all(Fraction(0) < x < Fraction(3) for x in used) and all(a < b for a,b in zip(used,used[1:])),
         'Original finite increasing LSP angles in radians')
    need(field(fields,f'classword[{channel}]',1) == 0, 'Original scalar classification word')
    residue, residue_words = [None] * 16, []
    b = config['residue_book']
    for index in range(8):
        wire = field(fields,f'residue[{channel}].vq_word[{index}]',2)
        residue_words.append(wire)
        # The recorded dense length2 canonical codes have their two bits
        # reversed on the LSB-first wire. Residue0 places dimensions8 apart.
        entry = ((wire & 1) << 1) | ((wire >> 1) & 1)
        low, high = entry % 2, entry // 2
        residue[index] = b['minimum'] + b['delta'] * b['values'][low]
        residue[index+8] = b['minimum'] + b['delta'] * b['values'][high]
    need(residue == packet_metadata['residue_first16'][channel] and all(value != 0 for value in residue),
         'All actual first16 residue-active bins independently witnessed')
    denominator = (1 << config['amplitude_bits']) - 1
    amplitude = Fraction(raw_amplitude * config['offset'],denominator)
    q4 = (raw_amplitude * config['offset'] * 16) // denominator
    return dict(raw_amplitude=raw_amplitude,amplitude_denominator=denominator,amplitude=amplitude,
        public_Tremor_amplitude_Q4=q4,selector=selector,words=words,coefficients=used,unused=unused,
        residue=residue,residue_words=residue_words)


def bark(hz):
    # Corrected Vorbis I Bark equation, including the term outside arctan.
    return 13.1 * math.atan(0.00074 * hz) + 2.24 * math.atan(1.85e-8 * hz * hz) + 0.0001 * hz


def frequency_point(bin_index, spectral_bins, rate, bark_size):
    frequency = rate * bin_index / (2.0 * spectral_bins)
    bark_hz, bark_nyquist = bark(frequency), bark(rate / 2.0)
    scaled = bark_hz * bark_size / bark_nyquist
    map_index = min(bark_size-1,math.floor(scaled))
    need(0 <= map_index < bark_size, 'Finite original Bark map domain')
    return dict(bin=bin_index,linear_frequency_hz=frequency,normalized_to_nyquist=bin_index/spectral_bins,
        normalized_cycles_per_sample=bin_index/(2.0*spectral_bins),bark_frequency=bark_hz,
        bark_nyquist=bark_nyquist,bark_scaled_bin=scaled,bark_map=map_index,
        distance_to_nearest_bark_boundary=abs(scaled-round(scaled)),
        mapped_angle_radians=math.pi*map_index/bark_size)


def products(coefficients, angle):
    """Own direct squared-product formulation of the public parity equations."""
    cosine = math.cos(angle)
    even_product, odd_product = 1.0, 1.0
    for index,value in enumerate(coefficients):
        factor = 4.0 * (math.cos(value) - cosine) ** 2
        if index % 2:
            odd_product *= factor
        else:
            even_product *= factor
    if len(coefficients) % 2:
        p = (1.0 - cosine*cosine) * odd_product
        q = even_product / 4.0
    else:
        p = (1.0 - cosine) * odd_product / 2.0
        q = (1.0 + cosine) * even_product / 2.0
    total = math.fsum((p,q))
    need(math.isfinite(total) and total > 0, 'Finite strictly positive public floor denominator')
    return dict(p=p,q=q,p_plus_q=total,denominator_sqrt=math.sqrt(total),cosine_omega=cosine)


def linear_gain(db):
    exponent = DB_EXP_COEFFICIENT * db
    if exponent > math.log(sys.float_info.max):
        return dict(log_gain=exponent,gain=None,representation='exp(log_gain) exceeds binary64 range')
    value = math.exp(exponent)
    return dict(log_gain=exponent,gain=value,representation='finite' if value else 'binary64 underflow to zero')


def requested_curve(coefficients, amplitude, offset, angle):
    terms = products(coefficients,angle)
    db = float(amplitude) / terms['denominator_sqrt'] - offset
    need(math.isfinite(db), 'Finite requested public dB')
    gain = linear_gain(db)
    return dict(**terms,requested_db=db,requested_gain=gain,
        positive_db_unity_overlay=dict(applies=db>0,gain_if_applied_to_same_ideal_db=1.0 if db>0 else gain['gain'],
            excess_over_unity_db=max(0.0,db),
            interpretation='Conditional positive-dB clamp on the same ideal formula input; no integer Tremor/backend prediction'))


def sanity_controls():
    # These are proposed formula controls. They run only if root explicitly
    # executes this diagnostic, never while assembling/checking this source.
    need(bark(0.0) == 0.0 and bark(100.0) < bark(1000.0) < bark(24000.0), 'Bark zero/monotonic sanity')
    for order,values,angle in ((1,[math.pi/2],0.0),(1,[math.pi/2],math.pi/2),
                               (2,[math.pi/3,2*math.pi/3],math.pi/2)):
        result = products(values,angle)
        need(len(values)==order and math.isclose(result['p_plus_q'],1.0,rel_tol=1e-12,abs_tol=1e-12),
             'Closed-form parity normalization control')
    # Independent doubled-cosine normalization, algebraically distinct from
    # the direct squared-product path used for the original observations.
    for values in ([0.31,0.77,1.21,1.83,2.44],[0.31,0.77,1.21,1.83,2.44,2.81]):
        for angle in (0.0,0.1,1.2,math.pi-0.1):
            w = 2.0*math.cos(angle)
            left, right = 0.5, 0.5
            for index,value in enumerate(values):
                if index%2: left *= w-2.0*math.cos(value)
                else: right *= w-2.0*math.cos(value)
            expected = (left*left*(4.0-w*w)+right*right if len(values)%2
                        else left*left*(2.0-w)+right*right*(2.0+w))
            need(math.isclose(products(values,angle)['p_plus_q'],expected,rel_tol=1e-12,abs_tol=1e-12),
                 'Independent doubled-cosine parity equality')
    need(linear_gain(0.0)['gain']==1.0 and math.isclose(linear_gain(20.0)['gain'],10.0,rel_tol=2e-6)
         and math.isclose(linear_gain(-20.0)['gain'],0.1,rel_tol=2e-6), 'Declared dB exponential coefficient sanity')
    positive = requested_curve([math.pi/2],61.0,60,0.0)
    need(positive['requested_db']>0 and positive['requested_gain']['gain']>1
         and positive['positive_db_unity_overlay']['gain_if_applied_to_same_ideal_db']==1.0,
         'Explicit positive-unity overlay boundary control')
    return dict(result='OWN_FORMULA_SANITY_CONTROLS_PASSED',groups=5,
                scope='Own analytic formulas only; never decoder/PCM/numeric conformance')


def diagnostic(pins):
    before = {}
    for item in pins['inputs']:
        path = (HERE/item['snapshot']).resolve()
        need(path.is_relative_to(HERE), 'Scoped immutable source snapshot')
        data = path.read_bytes()
        need(len(data)==item['bytes'] and sha(data)==item['sha256'], 'Original frozen source identity: '+item['snapshot'])
        before[path] = item['sha256']
    corpus = HERE/pins['fixture_root']
    matrix = json.loads((corpus/'matrix.json').read_bytes())
    construction = json.loads((corpus/'construction-fields.json').read_bytes())
    selected = [c for c in matrix['cases'] if c['id'].startswith('floor0-')]
    need(len(matrix['cases'])==9 and tuple(c['id'] for c in selected)==EXPECTED_IDS
         and pins['case_ids']==list(EXPECTED_IDS), 'All six unchanged original floor0 cases, no substituted controls')
    controls = sanity_controls()
    cases, bin_count, positive_count = [], 0, 0
    for case in selected:
        declaration = construction['variants'][case['variant']]
        setup = read_layout((corpus/case['setup']).read_bytes(),declaration['setup'])
        config = configuration(setup)
        identity = (corpus/case['identification']).read_bytes()
        need(len(identity)==30 and identity[:7]==b'\x01vorbis' and identity[11]==2
             and int.from_bytes(identity[12:16],'little')==config['rate'], 'Actual original identification rate/channels')
        short,long = 1 << (identity[28]&15), 1 << (identity[28]>>4)
        need((short,long)==(case['short'],case['long']) and case['channels']==2, 'Actual original short/long sizes')
        metadata = json.loads((corpus/case['packet_metadata']).read_bytes())
        audio = (corpus/case['audio']).read_bytes()
        need(len(metadata)==len(declaration['audio'])==case['packet_count']==14, 'Every original packet including primer')
        packets = []
        for index,(packet,layout) in enumerate(zip(metadata,declaration['audio'])):
            start,end = case['offsets'][index:index+2]
            need(start==packet['offset'] and end-start==packet['bytes'], 'Exact original packet spans')
            fields = read_layout(audio[start:end],layout)
            mode = field(fields,'audio.mode',1)
            need(field(fields,'audio.type',1)==0 and mode==packet['mode']==case['mode_flags'][index], 'Actual packet type/mode')
            if mode:
                need(field(fields,'audio.previous_window',1)==case['mode_flags'][index-1]
                     and field(fields,'audio.next_window',1)==case['mode_flags'][index+1], 'Actual long-neighbor flags')
            block = long if mode else short
            channels = []
            for channel in range(2):
                decoded = floor_and_residue(fields,config,channel,packet)
                lsp = list(map(float,decoded['coefficients']))
                observations = []
                for i in range(16):
                    frequency = frequency_point(i,block//2,config['rate'],config['bark'])
                    curve = requested_curve(lsp,decoded['amplitude'],config['offset'],frequency['mapped_angle_radians'])
                    observations.append(dict(**frequency,residue_value=int(decoded['residue'][i]),**curve))
                    bin_count += 1
                    positive_count += int(curve['requested_db']>0)
                channels.append(dict(channel=channel,raw_amplitude=decoded['raw_amplitude'],amplitude_bits=config['amplitude_bits'],
                    amplitude_denominator=decoded['amplitude_denominator'],amplitude_offset_db=config['offset'],
                    normalized_amplitude_db=str(decoded['amplitude']),normalized_amplitude_db_binary64=float(decoded['amplitude']),
                    public_Tremor_amplitude_Q4=decoded['public_Tremor_amplitude_Q4'],
                    public_Tremor_amplitude_db_from_Q4=decoded['public_Tremor_amplitude_Q4']/16,
                    selected_book=decoded['selector'],floor_wire_words=decoded['words'],
                    lsp_radians_exact=[str(x) for x in decoded['coefficients']],lsp_radians_binary64=lsp,
                    unused_final_vector_values=[str(x) for x in decoded['unused']],
                    residue_wire_words=decoded['residue_words'],bins=observations))
            packets.append(dict(packet=index,primer=index==0,mode=mode,block_samples=block,spectral_bins=block//2,
                transition='primer' if index==0 else ('L' if case['mode_flags'][index-1] else 'S')+('L' if mode else 'S'),channels=channels))
        cases.append(dict(id=case['id'],order=config['order'],parity='odd' if config['order']%2 else 'even',
            rate_hz=config['rate'],bark_map_size=config['bark'],short_samples=short,long_samples=long,packets=packets))
    need(bin_count==2688 and len(cases)==6 and all(sha(p.read_bytes())==h for p,h in before.items()),
         'All6/84/168/2688 formula observations and immutable source identity')
    return dict(result='OWN_PUBLIC_FLOOR0_FORMULA_DIAGNOSTIC_COMPLETED',formula='Vorbis I6.2.3/Xiph mathematical equations in binary64',
        diagnostic_source_sha256=sha(Path(__file__).read_bytes()),source_pins_sha256=sha((HERE/'source-pins.json').read_bytes()),
        DB_exp_coefficient=DB_EXP_COEFFICIENT,case_count=6,packets=84,channel_packets=168,active_bin_observations=bin_count,
        positive_db_observations=positive_count,controls=controls,cases=cases,math_computed=True,
        actual_decoder_or_reference_executed=False,PCM_computed=False,public_Tremor_integer_path_evaluated=False,
        vendor_behavior_attributed=False,overflow_inferred_from_PCM=False,numeric_qualified=False,
        full_G6_qualified=False,production_qualified=False,physical_qualified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    repo = next(p for p in HERE.parents if (p/'idf/esp32-cyd2usb-native/main').is_dir())
    output = args.output.resolve()
    protected = (HERE,repo/'.build/cyd-vorbis-floor0-prep-01',repo/'.build/cyd-vorbis-floor0-diagnosis-prep-01')
    need(output.is_relative_to(repo/'.build') and not output.exists()
         and not any(output.is_relative_to(p) or p.is_relative_to(output) for p in protected), 'Fresh independent .build result file')
    result = diagnostic(json.loads((HERE/'source-pins.json').read_bytes()))
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(dict(result=result['result'],cases=result['case_count'],active_bins=result['active_bin_observations'],
        positive_db_observations=result['positive_db_observations'],numeric_qualified=False,full_G6_qualified=False)))


if __name__=='__main__':
    main()
