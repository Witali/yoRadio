"""Prepare immutable source/data copies only; never compile or execute a unit."""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def array(data):
    return ','.join(str(n) for n in data)


def prepare(repo):
    need(not (HERE / 'fixture-contract.json').exists(), 'Preserve frozen materialization')
    pins = []
    def copy(role, source, destination, expected=None):
        source = repo / source
        data = source.read_bytes()
        need(expected is None or sha(data) == expected, 'Source identity: ' + role)
        path = HERE / destination
        need(not path.exists(), 'Fresh source copy: ' + destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(data)
        pins.append(dict(role=role, original=source.relative_to(repo).as_posix(),
            snapshot=destination, bytes=len(data), sha256=sha(data)))
        return data
    source_sha = '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c'
    abi_sha = 'e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60'
    copy('production/setup', 'idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c',
        'project/main/pinned/production/vorbis_repair/setup.c', source_sha)
    copy('production/ABI', 'idf/esp32-cyd2usb-native/main/vorbis_repair_abi.h',
        'project/main/pinned/production/vorbis_repair_abi.h', abi_sha)
    copy('production/license', 'idf/esp32-cyd2usb-native/main/vorbis_repair/COPYING',
        'project/main/pinned/production/vorbis_repair/COPYING')
    public_base = '.build/cyd-vorbis-format-expanded25-capture-02/sources/codec/include/'
    for name in ('esp_audio_types.h', 'decoder/esp_audio_dec.h', 'decoder/esp_audio_dec_reg.h', 'decoder/impl/esp_vorbis_dec.h'):
        copy('public/' + name, public_base + name, 'project/main/pinned/codec/include/' + name)
    roots = ['.build/cyd-vorbis-books-prep-01/generated01', '.build/cyd-vorbis-map2-regression-prep-01/generated02']
    expected_matrices = ['38e38f1f5ada7cd84a6ea91c5b46e0680ee62a7f511c9a72bfa7b6d7eb64cd2e',
                         '7ec364dea889ead32407d90914b7f6fb91d515d03dfa82dd6a1f7affdac139b8']
    rows, setups, probes_total = [], [], 0
    for source_index, root in enumerate(roots):
        matrix = json.loads(copy(f'fixture{source_index}/matrix', root + '/matrix.json',
            f'fixtures/source{source_index}/matrix.json', expected_matrices[source_index]))
        fields = json.loads(copy(f'fixture{source_index}/fields', root + '/bitfields.json',
            f'fixtures/source{source_index}/bitfields.json'))
        copy(f'fixture{source_index}/manifest', root + '/manifest.json', f'fixtures/source{source_index}/manifest.json')
        need(len(matrix['cases']) == 8, 'All eight cases per source')
        for case in matrix['cases']:
            index = len(rows)
            book = case['vector_book']
            need(book['minimum'] == -1 and book['delta'] == 1 and book['value_bits'] == 2, 'Bounded exact quantization')
            dim, entries, lengths = book['dimensions'], book['entries'], book['lengths']
            active = [i for i, length in enumerate(lengths) if length]
            setup = copy(f'case{index}/setup', root + '/' + case['setup'], f'fixtures/setup/{index:02d}-{case["id"]}.bin')
            bits = [f for f in fields[case['id']]['setup']['fields'] if f['name'].startswith('book[1].')]
            need(bits[0]['name'] == 'book[1].sync', 'Actual vector book offset')
            position = first = bits[0]['offset']
            packed = int.from_bytes(setup, 'little')
            for field in bits:
                need(field['offset'] == position and
                    (packed >> position) & ((1 << field['width']) - 1) == field['value'], 'Actual bit-field binding')
                position += field['width']
            end = position
            need(any(f['offset'] == end and f['name'] == 'time_count_minus_1' for f in fields[case['id']]['setup']['fields']),
                 'Exact book end precedes time suffix')
            codes = book.get('codewords_msb_first', book.get('codewords_msb'))
            need(len(codes) == entries and len(lengths) == entries, 'All original codewords')
            wide = dim == 16
            need(dim in (2, 4, 16) and book['lookup_type'] in (1, 2), 'Exact fixture vector formats')
            # Explicit fixture-shape expectations, not production helper calls.
            nodeb, leafw = (4, 1) if len(active) == 1 else (1, 2) if dim == 4 else (1, 1)
            table_bytes = (len(active) * 2 + 1) * 4 if nodeb == 4 else len(active) * (leafw + 1) - 2
            qval = []
            if wide:
                need(book['lookup_type'] == 2 and len(active) == 4, 'Original wide source books')
                for entry in active:
                    qval.extend(book['multiplicands'][entry * dim:(entry + 1) * dim])
                need(len(qval) == 64, 'All compact wide source rows')
            vectors = book['vectors_by_original_entry']
            probes = []
            for compact, entry in enumerate(active):
                vector, last, quantized = vectors[entry], 0, []
                need(len(vector) == dim and all(type(n) is int for n in vector), 'Independent integer vector metadata')
                for component in vector:
                    value = component - last - book['minimum']
                    need(0 <= value < 4, 'Inverse expected quantization range')
                    quantized.append(value)
                    last = component if book['sequence_p'] else 0
                leaf = compact if wide else sum(value << (2 * i) for i, value in enumerate(quantized))
                code = codes[entry]
                need(code and len(code) == lengths[entry] and set(code) <= {'0', '1'}, 'Actual codeword metadata')
                wires = [code, '1'] if len(active) == 1 else [code]
                need(len(active) != 1 or code == '0', 'Single-entry normal codeword')
                for wire in wires:
                    probes.append(dict(original=entry, wire_msb=wire, wire=int(wire[::-1], 2), bits=len(wire),
                        leaf=leaf, expected=vector))
            need(len(probes) <= 6, 'Bounded probe descriptor')
            probes_total += len(probes)
            rows.append(dict(index=index, id=case['id'], source_index=source_index, setup_sha256=sha(setup),
                setup_bytes=len(setup), book_first_bit=first, book_end_bit=end, dim=dim, entries=entries,
                used_entries=len(active), max_length=max(lengths), node_bytes=nodeb, leaf_words=leafw,
                dec_type=3 if wide else 1, sequence=book['sequence_p'], q_bits=2, q_pack=16 if wide else 0,
                q_min=-(1 << 30), q_minp=-30, q_del=1 << 28, q_delp=-28,
                table_bytes=table_bytes, qval_bytes=len(qval), qval_hex=bytes(qval).hex(), probes=probes))
            setups.append(setup)
    need(len(rows) == 16 and probes_total == 61, 'Exact original16 and61 codeword probes')
    model = dict(schema='owned-book-unit-fixtures-v1', cases=rows, case_count=16, probe_count=61,
        wide_pairs=[[8, 9], [10, 11]], point=0, setup_sha256=source_sha, ABI_sha256=abi_sha)
    digest = sha(canonical(model))
    contract = dict(contract_sha256=digest, model=model)
    with (HERE / 'fixture-contract.json').open('xb') as stream:
        stream.write((json.dumps(contract, indent=2) + '\n').encode())
    lines = ['/* Generated raw source-fixture descriptors; no codec execution. */', '#pragma once',
        '#include <stdint.h>', '#define UNIT_CASE_COUNT 16U', '#define UNIT_PROBE_COUNT 61U',
        f'#define UNIT_CONTRACT_SHA256 "{digest}"',
        'typedef struct { unsigned original; uint32_t wire; unsigned bits; uint32_t leaf; int32_t expected[16]; } unit_probe_t;',
        'typedef struct { const char *id; const uint8_t *setup; unsigned setup_bytes,book_first_bit,book_end_bit;',
        ' int dim,entries,used_entries,max_length,node_bytes,leaf_words,dec_type,sequence,q_pack;',
        ' unsigned table_bytes,qval_bytes; const uint8_t *qval; const unit_probe_t *probes; unsigned probe_count; } unit_case_t;']
    for row, setup in zip(rows, setups):
        i = row['index']
        lines.append(f'static const uint8_t setup_{i}[] = {{{array(setup)}}};')
        if row['qval_bytes']:
            lines.append(f'static const uint8_t qval_{i}[] = {{{array(bytes.fromhex(row["qval_hex"]))}}};')
        lines.append(f'static const unit_probe_t probes_{i}[] = {{')
        for p in row['probes']:
            lines.append(' {' + f'{p["original"]},{p["wire"]}U,{p["bits"]},{p["leaf"]}U,{{{array(p["expected"])}}}' + '},')
        lines.append('};')
    lines.append('static const unit_case_t unit_cases[] = {')
    for row in rows:
        i = row['index']
        fields = ','.join('.' + key + '=' + str(row[key]) for key in ('setup_bytes', 'book_first_bit', 'book_end_bit',
            'dim', 'entries', 'used_entries', 'max_length', 'node_bytes', 'leaf_words', 'dec_type', 'sequence', 'q_pack',
            'table_bytes', 'qval_bytes'))
        qval = f'qval_{i}' if row['qval_bytes'] else 'NULL'
        lines.append(f' {{.id="{row["id"]}",.setup=setup_{i},{fields},.qval={qval},.probes=probes_{i},.probe_count={len(row["probes"])}' + '},')
    lines += ['};', '_Static_assert(sizeof(unit_cases)/sizeof(unit_cases[0]) == UNIT_CASE_COUNT, "Exact sixteen books");', '']
    with (HERE / 'project/main/unit_data.h').open('xb') as stream:
        stream.write('\n'.join(lines).encode())
    with (HERE / 'source-pins.json').open('xb') as stream:
        stream.write((json.dumps(dict(schema='owned-book-unit-source-pins-v1', inputs=pins,
            actual_production_parser_copied_byte_exact=True, vendor_archive_linked=False,
            source_preparation_only=True, unit_or_decoder_executed=False), indent=2) + '\n').encode())
    print(json.dumps(dict(result='SOURCE_FIXTURES_PREPARED', cases=16, probes=61, contract_sha256=digest,
        unit_or_decoder_executed=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, required=True)
    prepare(parser.parse_args().repository.resolve())
