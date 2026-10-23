"""Construction-only witness; no codec, floor curve, reference or PCM computation."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def raw_fields(data, report):
    need(len(data) == report['bytes'], 'Construction byte count')
    value = int.from_bytes(data, 'little')
    position, values = 0, {}
    for field in report['fields']:
        name, width = field['name'], field['width']
        need(name not in values and field['offset'] == position and width >= 0, 'Field layout')
        actual = (value >> position) & ((1 << width) - 1)
        need(actual == field['value'], 'Raw field differs: ' + name)
        values[name] = actual
        position += width
    need(position == report['used_bits'] and value >> position == 0 and
         len(data) * 8 - position == report['padding_bits'], 'Final field/padding')
    return values


def float32_fraction(value):
    sign = -1 if value & 0x80000000 else 1
    mantissa = value & 0x1fffff
    exponent = ((value & 0x7fe00000) >> 21) - 788
    return sign * mantissa * (Fraction(2) ** exponent)


def witness(repo, pins):
    for row in pins['local_inputs']:
        data = (repo / row['path']).read_bytes()
        need(len(data) == row['bytes'] and sha(data) == row['sha256'], 'Input changed: ' + row['path'])
    corpus = repo / pins['fixture_root']
    matrix = json.loads((corpus / 'matrix.json').read_bytes())
    fields = json.loads((corpus / 'construction-fields.json').read_bytes())
    need(len(matrix['cases']) == 9, 'All nine original cases required')
    rows = []
    for case in matrix['cases']:
        declaration = fields['variants'][case['variant']]
        setup = raw_fields((corpus / case['setup']).read_bytes(), declaration['setup'])
        configuration = declaration['configuration']
        packets = json.loads((corpus / case['packet_metadata']).read_bytes())
        audio = (corpus / case['audio']).read_bytes()
        need(len(packets) == len(declaration['audio']) == case['packet_count'] == 14, 'All packets required')
        if configuration['floor'] == 0:
            order, bits, bark = configuration['order'], configuration['ampbits'], configuration['barkmap']
            need((order, bits, bark) in ((6, 6, 64), (5, 8, 128)), 'Exact original floor configurations')
            expected = {'order': (8, order), 'rate': (16, 48000), 'barkmap': (16, bark),
                'amplitude_bits': (6, bits), 'amplitude_offset': (8, 60),
                'books_minus_1': (4, len(configuration['books']) - 1)}
            for name, (width, value) in expected.items():
                actual = [f for f in declaration['setup']['fields'] if f['name'] == 'floor0.' + name]
                need(len(actual) == 1 and actual[0]['width'] == width and setup['floor0.' + name] == value,
                     'Independent floor header expectation: ' + name)
            for number, vectors in enumerate(configuration['books'], 2):
                prefix = f'book[{number}].'
                need([setup[prefix + key] for key in ('dimensions', 'entries', 'maptype', 'minimum', 'delta',
                    'value_bits_minus_1', 'sequence_p')] == [3, 2, 2, 0, 0x62000001, 4, 0], 'Original LSP book')
                need(float32_fraction(setup[prefix + 'delta']) == Fraction(1, 16), 'Exact dyadic delta')
                need([setup[prefix + f'multiplicand[{i}]'] for i in range(6)] == sum(vectors, []), 'LSP row order')
        packet_rows = []
        for index, (packet, record) in enumerate(zip(packets, declaration['audio'])):
            start, length = packet['offset'], packet['bytes']
            values = raw_fields(audio[start:start + length], record)
            if configuration['floor'] == 0:
                per_channel = []
                for channel, expected_floor in enumerate(packet['floors']):
                    prefix = f'floor[{channel}].'
                    selector = values[prefix + 'book_selector']
                    width = [f['width'] for f in record['fields'] if f['name'] == prefix + 'book_selector']
                    need(width == [len(configuration['books']).bit_length()] and selector < len(configuration['books']),
                         'Floor book selector width/value')
                    words = [values[prefix + f'vq_word[{i}]'] for i in range(2)]
                    coefficients, last = [], 0
                    for word in words:
                        vector = [x + last for x in configuration['books'][selector][word]]
                        coefficients.extend(vector)
                        last = vector[-1]
                    used, ignored = coefficients[:configuration['order']], coefficients[configuration['order']:]
                    need(expected_floor['amplitude_raw'] == values[prefix + 'amplitude'] and
                         expected_floor['book_selector'] == selector and expected_floor['vq_words'] == words and
                         used == expected_floor['lsp_used_units_1_16'] and ignored == expected_floor['lsp_ignored_units_1_16'],
                         'Independent vector accumulation differs')
                    need(all(0 < x < 48 for x in used) and all(a < b for a, b in zip(used, used[1:])), 'Used LSP angle domain')
                    need(all(x * (1 << 25) < (1 << 31) for vector in configuration['books'][selector] for x in vector),
                         'Public Q24 multiplicand product signed32 bound')
                    q24 = [x * (1 << 20) for x in used]
                    per_channel.append(dict(amplitude_raw=values[prefix + 'amplitude'], selector=selector,
                        used_units_1_16=used, ignored_units_1_16=ignored, exact_Q24_used=q24))
                packet_rows.append(dict(packet=index, channels=per_channel))
        rows.append(dict(id=case['id'], floor=configuration['floor'], fields_checked=True, floor_packets=packet_rows))
    return dict(result='CONSTRUCTION_FIELDS_WITNESSED', cases=rows, actual_codec_or_reference_executed=False,
        floor_curve_or_PCM_computed=False, numeric_qualified=False, full_G6_qualified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    repo, output = args.repository.resolve(), args.output.resolve()
    need(output.is_relative_to(repo / '.build') and not output.exists() and not output.is_relative_to(HERE),
         'Fresh independent .build result required')
    result = witness(repo, json.loads((HERE / 'source-pins.json').read_bytes()))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        stream.write((json.dumps(result, indent=2) + '\n').encode())
    print(json.dumps(dict(result=result['result'], cases=len(result['cases']), numeric_qualified=False)))


if __name__ == '__main__':
    main()
