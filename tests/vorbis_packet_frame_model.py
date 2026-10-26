"""Independent exact front-half Vorbis frame oracle and finite packet corpus.

All helper modules and original packet bytes are supplied by the caller. This
module imports no archived code, starts no processes and writes no files.
The result stops before floor multiplication, transform, overlap and PCM.
"""
import copy
import hashlib
import json

ORIGINAL_SHA = '32ba4c7e401fcfd05238f929fa6874c3048237792d78f36b05a8fade5b861e24'
PREFIX = ('mode', 'blockflag', 'previous_window', 'next_window', 'mapping', 'blocksize')
ROW_KEYS = {'id', 'identification_hex', 'identification_bits', 'setup_hex', 'setup_bits',
            'packet_hex', 'packet_bits', 'start_bit', 'initial_eop'}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def _bind(setup, floor, residue):
    # These are the caller's private helper instances, never repository globals.
    for helper in (floor, residue):
        if helper.REFERENCE is not setup:
            helper.context.cache_clear()
            helper.REFERENCE = setup


def _context(row, setup):
    identity = setup.identification(bytes.fromhex(row['identification_hex']), row['identification_bits'])
    return setup.parse_setup(bytes.fromhex(row['setup_hex']), row['setup_bits'], identity)


def _initial_floor(index, info):
    return dict(floor_index=index, type=info['type'], present=0, value_count=0,
                selected_book=0xffffffff,
                amplitude=dict(raw_amplitude=0, amplitude_bits=info['bits'] if info['type'] == 0 else 0,
                               amplitude_offset=info['offset'] if info['type'] == 0 else 0),
                value_offset=0)


def _floor_values(ctx, info, reader, state, setup, floor):
    """Read one floor using the independent entropy and affine primitives."""
    coefficients, raw = [], []
    if info['type'] == 0:
        amplitude = reader.take(info['bits'])
        state['amplitude']['raw_amplitude'] = amplitude
        if not amplitude:
            return coefficients, raw
        selector = reader.take(len(info['books']).bit_length())
        need(selector < len(info['books']), 'floor0 selector is within configured list')
        state['selected_book'] = info['books'][selector]
        book = ctx['books'][state['selected_book']]
        dimension = book['layout']['quantization']['dimensions']
        carry_minimum = carry_delta = 0
        # The specification consumes one vector even for order0.
        while True:
            entry = floor.decode_word(book, reader)
            used = min(dimension, info['order'] - len(coefficients))
            current = floor.vector(book, entry, used)
            for value in current:
                value['minimum_multiplier'] += carry_minimum
                value['delta_multiplier'] += carry_delta
            coefficients.extend(current)
            if current:
                carry_minimum = current[-1]['minimum_multiplier']
                carry_delta = current[-1]['delta_multiplier']
            if len(coefficients) >= info['order']:
                break
    else:
        if not reader.take(1):
            return coefficients, raw
        limit = (256, 128, 86, 64)[info['multiplier'] - 1]
        width = (limit - 1).bit_length()
        raw = [reader.take(width), reader.take(width)]
        for class_id in info['partitions']:
            cls = info['classes'][class_id]
            subclass = cls['subclass_bits']
            selection = floor.decode_word(ctx['books'][cls['masterbook']], reader) if subclass else 0
            mask = (1 << subclass) - 1
            for _ in range(cls['dimensions']):
                book_id = cls['books'][selection & mask]
                selection >>= subclass
                raw.append(0 if book_id == 0xffffffff else floor.decode_word(ctx['books'][book_id], reader))
    state['present'] = 1
    state['value_count'] = len(coefficients) if info['type'] == 0 else len(raw)
    return coefficients, raw


def _zero_frame(prefix, states, floor_eop):
    channels = len(states)
    for state in states:
        state['present'] = 0
        state['value_count'] = 0
        state['value_offset'] = 0
    bins = prefix['blocksize'] // 2
    layout = dict(mapping=prefix['mapping'], bins=bins, channels=channels, limbs=0,
                  magnitude_bits=0, exponent=0, sample_count=channels * bins,
                  limb_count=0, classification_count=0)
    return dict(prefix=prefix, floor_count=channels, floor0_count=0, floor1_count=0,
                implicit_zero=True, floor_eop=floor_eop, spectrum_layout=layout,
                residue=dict(classwords=0, vectors=0, values=0, stopped_on_eop=0),
                floors=states, floor0=[], floor1=[], spectrum=[])


def expected_case(row, setup_module, floor_module, residue_module):
    """Return exact expectations without calling any production C component."""
    setup, floor, residue = setup_module, floor_module, residue_module
    _bind(setup, floor, residue)
    need(set(row) == ROW_KEYS, 'complete finite frame row')
    body = bytes.fromhex(row['packet_hex'])
    need(type(row['initial_eop']) is bool and 0 <= row['start_bit'] <= row['packet_bits'] <= len(body) * 8,
         'literal packet extent and sticky state')
    ctx = _context(row, setup)
    reader = setup.Bits(body, row['packet_bits'], row['start_bit'])
    result = dict(measure_status=-99, requirements=None, decode_status=-99, frame=None,
                  position=row['start_bit'], end_of_packet=row['initial_eop'])
    try:
        if row['initial_eop']:
            raise setup.Truncated('sticky prefix EOP')
        need(reader.take(1) == 0, 'audio packet type0')
        mode = reader.take((ctx['layout']['mode_count'] - 1).bit_length())
        need(mode < ctx['layout']['mode_count'], 'audio mode range')
        mode_info = ctx['modes'][mode]
        block = mode_info['blockflag']
        previous, following = (reader.take(1), reader.take(1)) if block else (0, 0)
    except setup.Truncated:
        result.update(measure_status=-3, decode_status=-3, end_of_packet=True)
        return result
    except ValueError:
        result.update(measure_status=-1, decode_status=-1)
        return result
    identity = ctx['layout']['identification']
    prefix = dict(zip(PREFIX, (mode, block, previous, following, mode_info['mapping'],
                               identity['blocksize_1' if block else 'blocksize_0'])))
    mapping = residue.mapping_info(ctx, prefix['mapping'])
    bins, channels = prefix['blocksize'] // 2, mapping['channels']
    infos, states = [], []
    for channel in range(channels):
        index = mapping['submaps'][mapping['mux'][channel]][1]
        info = floor.floor_info(ctx, index)
        infos.append(info)
        states.append(_initial_floor(index, info))
    bound_case = dict(mapping=prefix['mapping'], bins=bins, floor_present=[1] * channels)
    requirements = dict(prefix=prefix, floor_count=channels,
                        floor0_values=sum(info['order'] for info in infos if info['type'] == 0),
                        floor1_values=sum(len(info['x']) for info in infos if info['type'] == 1),
                        residue_bound=residue.measure(bound_case, ctx))
    result.update(measure_status=0, requirements=requirements)
    coefficients, raw_values = [], []
    for state, info in zip(states, infos):
        state['value_offset'] = len(coefficients) if info['type'] == 0 else len(raw_values)
        try:
            own_coefficients, own_raw = _floor_values(ctx, info, reader, state, setup, floor)
        except setup.Truncated:
            result.update(decode_status=0, frame=_zero_frame(prefix, states, True),
                          position=reader.position, end_of_packet=True)
            return result
        except ValueError:
            result['decode_status'] = -1
            return result
        coefficients.extend(own_coefficients)
        raw_values.extend(own_raw)
    flags = [state['present'] for state in states]
    if not any(flags):
        result.update(decode_status=0, frame=_zero_frame(prefix, states, False), position=reader.position)
        return result
    residue_case = {key: row[key] for key in ('id', 'identification_hex', 'identification_bits', 'setup_hex',
                                             'setup_bits', 'packet_hex', 'packet_bits')}
    residue_case.update(start_bit=reader.position, initial_eop=False, mapping=prefix['mapping'],
                        bins=bins, floor_present=flags)
    decoded = residue.expected_case(residue_case)['exact']
    if decoded['packet_status'] != 0:
        result['decode_status'] = decoded['packet_status']
        return result
    frame = dict(prefix=prefix, floor_count=channels, floor0_count=len(coefficients),
                 floor1_count=len(raw_values), implicit_zero=decoded['layout']['limbs'] == 0,
                 floor_eop=False, spectrum_layout=decoded['layout'], residue=decoded['state'],
                 floors=states, floor0=coefficients, floor1=raw_values,
                 spectrum=decoded['coupled_limbs'])
    result.update(decode_status=0, frame=frame, position=decoded['position'],
                  end_of_packet=decoded['end_of_packet'])
    return result


def _append_bits(writer, body, extent):
    for position in range(extent):
        writer.put((body[position // 8] >> (position % 8)) & 1, 1)


def _row(identifier, setup_header, packet, start=0, sticky=False):
    return dict(id=identifier, identification_hex=setup_header['identification_hex'],
                identification_bits=setup_header['identification_bits'],
                setup_hex=setup_header['setup_hex'], setup_bits=setup_header['setup_bits'],
                packet_hex=packet.octets(), packet_bits=len(packet.bits),
                start_bit=start, initial_eop=sticky)


def _packet(identifier, spec, setup, floor, residue, flags, mode=0, start=0,
            invalid_selector=None, seed=1):
    """Encode floors and independent residue construction in separate walks."""
    header, _, _, _ = setup.make_case(identifier, spec)
    writer = setup.Writer()
    writer.put((1 << start) - 1, start)
    writer.put(0, 1)
    writer.put(mode, (len(spec['modes']) - 1).bit_length())
    mode_info = spec['modes'][mode]
    if mode_info['blockflag']:
        writer.put(1, 1)
        writer.put(0, 1)
    mapping = spec['mappings'][mode_info['mapping']]
    for channel, present in enumerate(flags):
        info = spec['floors'][mapping['submaps'][mapping['mux'][channel]][1]]
        if info['type'] == 0:
            amplitude = 127 if present else 0
            writer.put(amplitude, info['amplitude_bits'])
            if not amplitude:
                continue
            if channel == invalid_selector:
                writer.put(len(info['books']), len(info['books']).bit_length())
                return _row(identifier, header, writer, start)
            writer.put(0, len(info['books']).bit_length())
            book = spec['books'][info['books'][0]]
            count = max(1, (info['order'] + book['dimensions'] - 1) // book['dimensions'])
            choices = setup.greedy_words(book['lengths'])
            for index in range(count):
                if not choices:
                    writer.put(0, 1)
                    break
                floor.put_word(writer, book['lengths'], choices[index % len(choices)]['entry'])
        else:
            writer.put(int(present), 1)
            if not present:
                continue
            width = ((256, 128, 86, 64)[info['multiplier'] - 1] - 1).bit_length()
            writer.put(19 + channel, width)
            writer.put(40 + channel, width)
            for class_id in info['partitions']:
                cls = info['classes'][class_id]
                selection = 0
                if cls['subclass_bits']:
                    choices = setup.greedy_words(spec['books'][cls['masterbook']]['lengths'])
                    if not choices:
                        writer.put(0, 1)
                        return _row(identifier, header, writer, start)
                    selection = choices[0]['entry']
                    floor.put_word(writer, spec['books'][cls['masterbook']]['lengths'], selection)
                mask = (1 << cls['subclass_bits']) - 1
                for _ in range(cls['dimensions']):
                    selected = cls['books'][selection & mask]
                    selection >>= cls['subclass_bits']
                    if selected >= 0:
                        choices = setup.greedy_words(spec['books'][selected]['lengths'])
                        if not choices:
                            writer.put(0, 1)
                            return _row(identifier, header, writer, start)
                        floor.put_word(writer, spec['books'][selected]['lengths'], choices[-1]['entry'])
    bins = 1 << (spec['identification']['large' if mode_info['blockflag'] else 'small'] - 1)
    residual = residue.build_case(identifier, spec, bins=bins, flags=flags,
                                  mapping=mode_info['mapping'], seed=seed)
    _append_bits(writer, bytes.fromhex(residual['packet_hex']), residual['packet_bits'])
    return _row(identifier, header, writer, start)


def cases(setup_module, floor_module, residue_module, original31_model_bytes):
    """All original434 packets plus explicitly selected integration controls."""
    setup, floor, residue = setup_module, floor_module, residue_module
    _bind(setup, floor, residue)
    need(hashlib.sha256(original31_model_bytes).hexdigest() == ORIGINAL_SHA, 'unchanged original31 model')
    original = json.loads(original31_model_bytes)
    need(len(original['cases']) == 31, 'all original31 streams')
    rows = []
    for stream in original['cases']:
        audio = bytes.fromhex(stream['audio_hex'])
        offsets = stream['offsets']
        need(len(offsets) == 15 and offsets[0] == 0 and offsets[-1] == len(audio), 'all14 complete original packets')
        for ordinal, (begin, end) in enumerate(zip(offsets, offsets[1:])):
            packet = audio[begin:end]
            need(packet and begin < end, 'nonempty original packet')
            rows.append(dict(id='original31-' + stream['id'] + '-p' + str(ordinal),
                             identification_hex=stream['identification_hex'],
                             identification_bits=4 * len(stream['identification_hex']),
                             setup_hex=stream['setup_hex'], setup_bits=4 * len(stream['setup_hex']),
                             packet_hex=packet.hex(), packet_bits=len(packet) * 8,
                             start_bit=0, initial_eop=False))
    need(len(rows) == 434, 'all original434 packets')
    synthetic, exhaustive_cuts = [], []

    def build(identifier, spec, flags=None, cut=False, **options):
        row = _packet(identifier, spec, setup, floor, residue,
                      [1] * spec['identification']['channels'] if flags is None else flags, **options)
        synthetic.append(row)
        if cut:
            exhaustive_cuts.append(row)
        return row

    def with_floor(kind, floor_kind, channels=2, classes=1):
        spec = residue.base_spec(kind, channels=channels, bins=6, classes=classes)
        spec['books'][1].update(lengths=[2, 1, 2], lookup=2, minimum_bits=residue.ONE,
                                delta_bits=residue.ONE, value_bits=4)
        if floor_kind == 0:
            spec['books'].append(residue.book(dim=2, minimum=residue.ONE, delta=residue.ONE,
                                               sequence=1, width=4))
            spec['floors'] = [dict(type=0, order=3, rate=44100, bark=512,
                                   amplitude_bits=8, amplitude_offset=60, books=[2])]
        return spec

    for kind in range(3):
        for floor_kind in (0, 1):
            spec = with_floor(kind, floor_kind)
            build(f'grammar-f{floor_kind}-r{kind}', spec, cut=True, start=3)
            build(f'all-unused-f{floor_kind}-r{kind}', spec, flags=[0, 0])
        spec = with_floor(kind, 1, channels=3, classes=2)
        spec['mappings'][0]['pairs'] = [(1, 2), (0, 1)]
        for flags in ([1, 0, 0], [0, 0, 1], [1, 0, 1]):
            build('coupling-r' + str(kind) + '-' + ''.join(map(str, flags)), spec, flags=flags)
        spec = with_floor(kind, 1)
        spec['books'][1].update(minimum_bits=0x80000000, delta_bits=0)
        build('zero-grid-r' + str(kind), spec, cut=kind == 0)
        spec = with_floor(kind, 1)
        spec['residues'][0].update(cascades=[0], books=[])
        build('zero-cascades-r' + str(kind), spec)
        for target in ('phrase', 'stage'):
            spec = with_floor(kind, 1)
            spec['books'][0 if target == 'phrase' else 1]['lengths'] = [0]
            build('empty-' + target + '-r' + str(kind), spec)
    # Mixed floor grammar and submap order intentionally disagree with channels.
    for kind in range(3):
        spec = with_floor(kind, 0, channels=3, classes=2)
        spec['floors'].append(dict(type=1, partitions=[], classes=[], multiplier=2, range_bits=0, x=[]))
        spec['residues'].append(copy.deepcopy(spec['residues'][0]))
        spec['residues'][1]['books'] = [1] * len(spec['residues'][1]['books'])
        spec['mappings'][0] = dict(pairs=[(1, 2), (0, 1)], mux=[1, 0, 1],
                                   submaps=[(255, 1, 0), (7, 0, 1), (128, 1, 0)])
        for flags in ([1, 1, 1], [1, 0, 0], [0, 1, 0]):
            build('mixed-submaps-r' + str(kind) + '-' + ''.join(map(str, flags)), spec,
                  flags=flags, cut=kind == 0 and flags == [1, 1, 1])
    spec = with_floor(1, 0)
    spec['floors'][0]['order'] = 0
    build('floor0-order0-word-consumed', spec, cut=True)
    spec = with_floor(1, 0)
    spec['books'][2]['lengths'] = [0]
    build('floor0-active-empty-book', spec)
    spec = with_floor(1, 0)
    spec['floors'][0]['books'] = [2, 2, 2]
    build('floor0-invalid-selector', spec, invalid_selector=0)
    spec = with_floor(1, 1)
    spec['floors'][0].update(partitions=[0], classes=[dict(dimensions=1, subclass_bits=1,
        masterbook=0, books=[0, -1])], range_bits=4, x=[3])
    build('floor1-master-subbook', spec, cut=True)
    spec['books'][0]['lengths'] = [0]
    build('floor1-active-empty-master', spec)
    spec = with_floor(2, 1, channels=3)
    spec['residues'][0].update(begin=1, end=17, partition_size=3)
    build('type2-unaligned-flat-interval', spec, flags=[0, 1, 0], cut=True)
    spec = with_floor(0, 1)
    spec['books'][1]['dimensions'] = 2
    spec['residues'][0]['partition_size'] = 6
    build('residue0-complete-word-before-eop', spec, cut=True)
    spec = with_floor(1, 1)
    spec['identification']['large'] = 7
    spec['modes'] = [dict(blockflag=0, mapping=0), dict(blockflag=1, mapping=0), dict(blockflag=0, mapping=0)]
    long_row = build('three-modes-long-window', spec, mode=1, cut=True)
    bad_mode = dict(long_row, id='invalid-mode-three')
    bad_body = bytearray.fromhex(bad_mode['packet_hex'])
    bad_body[0] |= 6
    bad_mode['packet_hex'] = bad_body.hex()
    synthetic.append(bad_mode)
    for sign in (0, 0x80000000):
        spec = with_floor(1, 1)
        spec['books'][1].update(minimum_bits=1 | sign, delta_bits=(1023 << 21) | 0x100000,
                                value_bits=1)
        spec['mappings'][0]['pairs'] = [(0, 1)]
        build('wide-dyadic-coupling-' + str(sign >> 31), spec)
    # Prefix/type/sticky controls use complete immutable packet bytes.
    base = synthetic[0]
    sticky = dict(base, id='sticky-prefix-eop', initial_eop=True)
    synthetic.append(sticky)
    nonaudio = dict(base, id='non-audio-packet')
    body = bytearray.fromhex(nonaudio['packet_hex'])
    body[nonaudio['start_bit'] // 8] |= 1 << (nonaudio['start_bit'] % 8)
    nonaudio['packet_hex'] = body.hex()
    synthetic.append(nonaudio)
    padded = dict(base, id='transport-padding-and-ignored-tail')
    body = bytes.fromhex(padded['packet_hex']) + b'\xff'
    padded.update(packet_hex=body.hex(), packet_bits=len(body) * 8)
    synthetic.append(padded)
    rows.extend(synthetic)
    for row in exhaustive_cuts:
        expected = expected_case(row, setup, floor, residue)
        need(expected['decode_status'] == 0 and not expected['end_of_packet'], 'complete baseline for all-bit cuts')
        for extent in range(row['start_bit'], expected['position']):
            rows.append(dict(row, id=row['id'] + '-cut-' + str(extent), packet_bits=extent))
    names = set()
    for row in rows:
        need(set(row) == ROW_KEYS and row['id'] not in names, 'exact unique corpus rows')
        names.add(row['id'])
    return dict(schema='vorbis-packet-frame-cases-v1', cases=rows)
