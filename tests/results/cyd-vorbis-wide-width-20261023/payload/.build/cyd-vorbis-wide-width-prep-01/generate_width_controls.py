"""Construct additive valid qbits9/16 encodings of four frozen public raw books."""
import argparse
from collections import Counter
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WIDTHS = (9, 16)
SOURCE_PINS_SHA = '75cb073a50c88b93086ebddf18a83108cdda69b46a96f3f7c1a29dadad97db96'
HELPERS = {
    'tests/vorbis_format_corpus/generate_map2_regression.py': '49015a8a849682ad886c970ea3b1a3bc06f02f21a4f01785b7d52695e23d3caa',
    'tests/vorbis_format_corpus/generate_books.py': 'de9b09de59a0825feda741c0343c6d60821ddad1258ce7df5ae342c68e268fc1',
    'tests/vorbis_block_matrix/generate_minimal.py': '8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1',
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(data), sha256=sha(data))


def canonical():
    for name, expected in HELPERS.items():
        need(sha((ROOT / name).read_bytes()) == expected, 'canonical_helper_pin:' + name)
    path = ROOT / 'tests/vorbis_format_corpus/generate_map2_regression.py'
    spec = importlib.util.spec_from_file_location('pinned_public_map2_width_construction', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Ordinary pinned import; guarded main is not called.
    need(Path(module.__file__).resolve() == path.resolve(), 'actual_map2_import_path')
    need(Path(module.books.__file__).resolve() == (ROOT / 'tests/vorbis_format_corpus/generate_books.py').resolve(), 'actual_books_import_path')
    need(Path(module.base.__file__).resolve() == (ROOT / 'tests/vorbis_block_matrix/generate_minimal.py').resolve(), 'actual_minimal_import_path')
    return module


def generate(output):
    output = output.resolve()
    need(output.is_relative_to(ROOT / '.build') and output != ROOT / '.build' and not output.exists() and
         not output.is_relative_to(HERE) and not HERE.is_relative_to(output), 'fresh_independent_build_output')
    pins_path = HERE / 'source-pins.json'
    need(sha(pins_path.read_bytes()) == SOURCE_PINS_SHA, 'frozen_source_pins_identity')
    pins = json.loads(pins_path.read_bytes())
    need(pins['canonical_helpers'] and pins['original_matrix_sha256'] ==
         '7ec364dea889ead32407d90914b7f6fb91d515d03dfa82dd6a1f7affdac139b8', 'selected_original_matrix_pin')
    sources = [Path(__file__).resolve(), HERE / 'README.md', pins_path, *[ROOT / name for name in HELPERS],
               *[HERE / name for name in pins['files']]]
    before = [fact(path) for path in sources]
    for name, row in pins['files'].items():
        value = (HERE / name).read_bytes()
        need(len(value) == row['bytes'] and sha(value) == row['sha256'], 'frozen_original_pin')
    original_matrix = json.loads((HERE / 'originals/matrix.json').read_bytes())
    originals = pins['selected_original_cases']
    need(originals == original_matrix['cases'][:4] and len(originals) == 4, 'exact_original_four')
    helper = canonical()
    configs = helper.configurations()[:4]
    need([row['id'] for row in configs] == pins['original_case_ids'], 'original_configuration_order')
    payloads, syntax, original_values, new_values = {}, {}, [], []
    for case, book in zip(originals, configs):
        value = {kind: (HERE / f"originals/{case['id']}/{Path(case[kind]).name}").read_bytes()
                 for kind in ('identification', 'comment', 'setup', 'audio', 'ogg')}
        need(helper.inspect_setup(value['setup'], book) == helper.raw_book(book), 'original_complete_setup')
        need(value['identification'] == helper.base.identification(8, 11, helper.RATE).data() and
             value['comment'] == helper.base.comment().data(), 'original_ID_and_comment')
        packets = [value['audio'][a:b] for a, b in zip(case['offsets'], case['offsets'][1:])]
        need(len(packets) == len(helper.MODES) == case['packet_count'] and
             all(packet == helper.audio(book, i).data() for i, packet in enumerate(packets)), 'original_audio_wire')
        pages = helper.base.read_pages(value['ogg'])
        need([row['packet'] for row in pages] == [value['identification'], value['comment'], value['setup']] + packets and
             [row['granule'] for row in pages] == [0, 0, 0] + case['packet_granules'], 'original_carrier')
        original_values.append((case, book, value, packets, pages))
    for width in WIDTHS:
        for case, original_book, value, packets, pages in original_values:
            book = copy.deepcopy(original_book)
            book.update(id=case['id'] + f'_qbits{width}', value_bits=width)
            need({k: v for k, v in book.items() if k not in ('id', 'value_bits')} ==
                 {k: v for k, v in original_book.items() if k not in ('id', 'value_bits')}, 'sole_book_field_width')
            setup_bits = helper.setup(book)
            need(helper.inspect_setup(setup_bits.data(), book) == helper.raw_book(book), 'new_complete_setup')
            need(helper.books.vectors(book) == helper.books.vectors(original_book), 'exact_integer_vectors')
            observations = [helper.inspect_audio(packet, book, i) for i, packet in enumerate(packets)]
            need(all(packet == helper.audio(book, i).data() for i, packet in enumerate(packets)), 'new_audio_wire_unchanged')
            new = dict(value, setup=setup_bits.data())
            carrier_packets = [new['identification'], new['comment'], new['setup']] + packets
            new['ogg'] = b''.join(helper.base.page(packet, page['serial'], index, page['granule'], page['flags'])
                for index, (packet, page) in enumerate(zip(carrier_packets, pages)))
            recovered = helper.base.read_pages(new['ogg'])
            need([row['packet'] for row in recovered] == carrier_packets and
                 [(row['serial'], row['flags'], row['granule']) for row in recovered] ==
                 [(row['serial'], row['flags'], row['granule']) for row in pages], 'new_carrier_valid')
            result = copy.deepcopy(case)
            result['id'] = book['id']
            result['vector_book'].update(value_bits=width, quantized_bits_per_vector=width * book['dimensions'])
            result['vector_book']['expected_public_setup_storage_path'] = 'wide_map2_dec_type3'
            result['packet_syntax'] = observations
            result['features'] += [f'quant_width{width}', 'equivalent_width_control']
            result['width_control'] = dict(original_id=case['id'], original_value_bits=2, value_bits=width,
                changed_book_fields=['value_bits'], unsigned_multiplicands_unchanged=True,
                minimum=-1, delta=1, dimensions=16, canonical_helpers_rebound=False)
            result['raw_sha256'] = {kind: sha(data) for kind, data in new.items() if kind != 'ogg'}
            result['files'] = {kind: dict(bytes=len(data), sha256=sha(data)) for kind, data in new.items()}
            syntax[book['id']] = setup_bits.report()
            new_values.append((result, new))
    need(len(new_values) == len(originals) * len(WIDTHS) == 8, 'exact_eight_additions')
    groups = [[case['id'], case['id'] + '_qbits9', case['id'] + '_qbits16'] for case in originals]
    def matrix(name, values, equal_groups):
        cases = []
        for original, data in values:
            case = copy.deepcopy(original)
            for kind, value in data.items():
                suffix = '.ogg' if kind == 'ogg' else '.bin'
                case[kind] = f"cases/{case['id']}/{kind}{suffix}"
                payloads[name + '/' + case[kind]] = value
            cases.append(case)
        modes = cases[0]['mode_flags']
        transitions = Counter('SL'[a] + 'SL'[b] for a, b in zip(modes, modes[1:]))
        need(set(transitions) == {'SS', 'SL', 'LS', 'LL'}, 'all_four_transitions')
        result = dict(schema='vorbis-wide-quant-width-candidates-v1', status='CONSTRUCTION_CHECKED_REFERENCE_PENDING',
            supplement_not_replacement=True, cases=cases, case_count=len(cases),
            raw_packet_count=sum(case['packet_count'] for case in cases),
            expected_total_s16le_bytes=sum(case['expected_s16le_bytes'] for case in cases),
            expected_same_decoder_pcm_equal_groups=equal_groups,
            unchanged_original_case_ids=pins['original_case_ids'], comparison_three_width_groups=groups,
            transitions=dict(transitions), actual_PCM_equality_verified=False, independent_reference_run=False,
            target_run=False, format_conformance_qualified=False, full_G6_qualified=False)
        payloads[name + '/matrix.json'] = (json.dumps(result, indent=2) + '\n').encode()
        return result
    added = matrix('additions8', new_values, [row[1:] for row in groups])
    compared = matrix('comparison12', [(case, value) for case, _, value, _, _ in original_values] + new_values, groups)
    need(compared['case_count'] == 12 and added['case_count'] == 8, 'explicit_12_and_8_scopes')
    payloads['bitfields.json'] = (json.dumps(syntax, indent=2) + '\n').encode()
    need([fact(path) for path in sources] == before, 'source_inputs_unchanged')
    manifest = dict(schema='wide-width-construction-manifest-v1', source_inputs=before,
        source_pins_sha256=sha(pins_path.read_bytes()), original_matrix_sha256=pins['original_matrix_sha256'],
        canonical_helpers=HELPERS, no_monkeypatch_or_helper_copy=True,
        codec_SDK_compiler_QEMU_reference_Git_device_executed=False,
        files=[dict(path=name, bytes=len(data), sha256=sha(data)) for name, data in sorted(payloads.items())])
    payloads['manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    for name, data in payloads.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(data)
    print(json.dumps(dict(output=str(output), additions=added['case_count'], comparison=compared['case_count'],
        addition_packets=added['raw_packet_count'], comparison_packets=compared['raw_packet_count'],
        addition_expected_pcm=added['expected_total_s16le_bytes'], comparison_expected_pcm=compared['expected_total_s16le_bytes'],
        manifest_sha256=sha(payloads['manifest.json']), reference_pending=True)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    generate(parser.parse_args().output)
