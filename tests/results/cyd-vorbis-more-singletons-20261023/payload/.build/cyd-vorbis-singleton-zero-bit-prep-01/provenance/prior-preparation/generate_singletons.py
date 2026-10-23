"""Eight additive complete singleton candidates; construction only, never decoding."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tests/vorbis_format_corpus/generate_books.py').is_file())
BOOKS = ROOT / 'tests/vorbis_format_corpus/generate_books.py'
MINIMAL = ROOT / 'tests/vorbis_block_matrix/generate_minimal.py'
BOOKS_SHA = 'de9b09de59a0825feda741c0343c6d60821ddad1258ce7df5ae342c68e268fc1'
MINIMAL_SHA = '8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1'
RATE, CHANNELS, SHORT, LONG = 192000, 2, 256, 2048
SPEC = 'https://xiph.org/vorbis/doc/Vorbis_I_spec.html'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


need(sha(BOOKS.read_bytes()) == BOOKS_SHA, 'canonical_book_helper_pin')
need(sha(MINIMAL.read_bytes()) == MINIMAL_SHA, 'canonical_minimal_helper_pin')
_spec = importlib.util.spec_from_file_location('pinned_more_singletons_books', BOOKS)
books = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(books)  # Ordinary exact helper import; guarded main is not called.
base = books.base
need(Path(base.__file__).resolve() == MINIMAL.resolve(), 'actual_minimal_import_path')
MODES = base.MODES


def configurations():
    result = []
    for dim in (4, 16):
        for seq in (0, 1):
            active = [2, 0, 2, 0] if dim == 4 else [2] * 16
            rows = [[0] * dim, [1] * dim, active, [3] * dim]
            result.append(dict(id=f'map2_sparse_single_d{dim}_seq{seq}', lengths=[0, 0, 1, 0],
                ordered=False, lookup_type=2, dimensions=dim, entries=4, minimum=-1, delta=1,
                value_bits=2, sequence_p=seq, multiplicands=[x for row in rows for x in row]))
    for kind, lengths in (('dense', [1]), ('sparse', [0, 0, 0, 0, 1, 0])):
        for seq in (0, 1):
            result.append(dict(id=f'map1_{kind}_single_d16_seq{seq}', lengths=list(lengths),
                ordered=False, lookup_type=1, dimensions=16, entries=len(lengths),
                minimum=-1, delta=1, value_bits=2, sequence_p=seq, multiplicands=[2]))
    return result


def active_id(book):
    active = [i for i, length in enumerate(book['lengths']) if length]
    need(len(active) == 1 and book['lengths'][active[0]] == 1, 'exact_single_active_length1')
    return active[0]


def raw_book(book):
    return {k: v for k, v in book.items() if k != 'id'}


def setup(book):
    active_id(book)
    expected_count = (books.quantvals(book['entries'], book['dimensions']) if book['lookup_type'] == 1
                      else book['entries'] * book['dimensions'])
    need(len(book['multiplicands']) == expected_count, 'all_declared_lookup_multiplicands_required')
    b = base.Bits(); base.prefix(b, 5); b.put('codebooks_minus_1', 8, 1)
    books.write_book(b, 0, books.scalar_book(False))
    books.write_book(b, 1, book)
    for name, width, value in (
        ('time_count_minus_1', 6, 0), ('time[0].type', 16, 0),
        ('floor_count_minus_1', 6, 0), ('floor[0].type', 16, 1), ('floor[0].partitions', 5, 0),
        ('floor[0].multiplier_minus_1', 2, 0), ('floor[0].rangebits', 4, 10),
        ('residue_count_minus_1', 6, 0), ('residue[0].type', 16, 0), ('residue[0].begin', 24, 0),
        ('residue[0].end', 24, 16), ('residue[0].partition_size_minus_1', 24, 15),
        ('residue[0].classifications_minus_1', 6, 1), ('residue[0].classbook', 8, 0)):
        b.put(name, width, value)
    for c in range(2):
        b.put(f'residue[0].cascade[{c}].low', 3, 1)
        b.put(f'residue[0].cascade[{c}].high_present', 1, 0)
    for c in range(2):
        b.put(f'residue[0].stagebook[{c}][0]', 8, 1)
    for name, width, value in (
        ('mapping_count_minus_1', 6, 0), ('mapping[0].type', 16, 0),
        ('mapping[0].multiple_submaps', 1, 0), ('mapping[0].coupling', 1, 0),
        ('mapping[0].reserved', 2, 0), ('mapping[0].time', 8, 0),
        ('mapping[0].floor', 8, 0), ('mapping[0].residue', 8, 0), ('modes_minus_1', 6, 1)):
        b.put(name, width, value)
    for mode in range(2):
        for field, width, value in (('blockflag', 1, mode), ('windowtype', 16, 0),
                                    ('transformtype', 16, 0), ('mapping', 8, 0)):
            b.put(f'mode[{mode}].' + field, width, value)
    b.put('framing', 1, 1)
    return b


def audio(book, packet):
    entry = active_id(book)
    b = base.Bits(); mode = MODES[packet]
    b.put('audio_packet_type', 1, 0); b.put('mode', 1, mode)
    if mode:
        b.put('previous_window_flag', 1, MODES[packet - 1])
        b.put('next_window_flag', 1, MODES[packet + 1])
    for channel in range(CHANNELS):
        b.put(f'floor[{channel}].present', 1, 1)
        b.put(f'floor[{channel}].y0', 8, 255); b.put(f'floor[{channel}].y1', 8, 255)
    for channel in range(CHANNELS):
        b.put(f'classword[{channel}]', 1, (packet + channel) % 2)
    for channel in range(CHANNELS):
        for vector in range(16 // book['dimensions']):
            # Errata20150226: consume one bit for the sole original value.
            # Both branches deliberately exercised; bit1 tests decoder tolerance.
            b.put(f'residue[{channel}].entry[{vector}]={entry}', 1, (packet + channel + vector) % 2)
    return b


def packet_intention(book, packet):
    dim, entry = book['dimensions'], active_id(book)
    table = books.vectors(book); steps = 16 // dim
    spectra = [[0] * 16 for _ in range(CHANNELS)]
    for channel in range(CHANNELS):
        for i in range(steps):
            for j in range(dim):
                spectra[channel][i + j * steps] += table[entry][j]
    need(all(any(v) and max(map(abs, v)) <= 16 for v in spectra), 'bounded_nonzero_spectral_intention')
    mode = MODES[packet]
    used = 38 + 2 * mode + CHANNELS * steps
    return dict(classwords=[(packet + c) % 2 for c in range(CHANNELS)],
        vector_entry_ids=[[entry] * steps for _ in range(CHANNELS)], residue_vectors=spectra,
        one_bit_per_single_entry=True, used_bits=used, token_bits=CHANNELS * steps,
        token_count=CHANNELS * steps, padding_bits=(-used) % 8,
        single_entry_wire_bits=[[(packet + c + i) % 2 for i in range(steps)] for c in range(CHANNELS)])


def relations(configs):
    by_id = {b['id']: b for b in configs}
    groups = [[f'map2_sparse_single_d16_seq{s}', f'map1_dense_single_d16_seq{s}',
               f'map1_sparse_single_d16_seq{s}'] for s in (0, 1)]
    pairs = [[b['id'], b['id'][:-1] + '1'] for b in configs if b['sequence_p'] == 0]
    for group in groups:
        first = [packet_intention(by_id[group[0]], p)['residue_vectors'] for p in range(14)]
        for name in group[1:]:
            need(first == [packet_intention(by_id[name], p)['residue_vectors'] for p in range(14)], 'equal_spectral_intention')
    for a, b in pairs:
        need(packet_intention(by_id[a], 0)['residue_vectors'] != packet_intention(by_id[b], 0)['residue_vectors'],
             'sequence_changes_spectral_intention')
    return groups, pairs


def fact(path):
    raw = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(raw), sha256=sha(raw))


def check_sources(expected):
    manifest = HERE / 'readiness.json'
    need(sha(manifest.read_bytes()) == expected, 'reviewed_preparation_readiness_pin')
    data = json.loads(manifest.read_bytes())
    need(data['schema'] == 'more-singletons-source-only-readiness-v1' and data['runtime_executed'] is False,
         'source_only_preparation_required')
    files = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}
    need(files == set(data['files']) | {'readiness.json'}, 'preparation_exact_file_set')
    for name, item in data['files'].items():
        p = (HERE / name).resolve()
        need(p.is_relative_to(HERE) and p.stat().st_size == item['bytes'] and sha(p.read_bytes()) == item['sha256'],
             'preparation_file_changed:' + name)
    pins = json.loads((HERE / 'source-pins.json').read_bytes())
    for item in pins['inputs']:
        need(fact(Path(item['source']))['sha256'] == item['sha256'], 'canonical_origin_changed')
    return [fact(HERE / n) for n in sorted(files)] + [fact(Path(x['source'])) for x in pins['inputs']]


def generate(output, readiness_sha):
    before = check_sources(readiness_sha)
    output = output.resolve(); build = ROOT / '.build'
    need(output != build and output.is_relative_to(build) and not output.exists()
         and not output.is_relative_to(HERE) and not HERE.is_relative_to(output), 'fresh_separate_build_output')
    configs = configurations(); need(len(configs) == 8, 'exact_eight_singleton_cases')
    equal_groups, different_pairs = relations(configs)
    frames = [0] + [((LONG if a else SHORT) + (LONG if b else SHORT)) // 4 for a, b in zip(MODES, MODES[1:])]
    pcm = [n * CHANNELS * 2 for n in frames]; granules = []; total = 0
    for n in frames:
        total += n; granules.append(total)
    transitions = Counter('SL'[a] + 'SL'[b] for a, b in zip(MODES, MODES[1:]))
    neighbors = Counter((MODES[i - 1], MODES[i + 1]) for i in range(1, 13) if MODES[i])
    need(set(transitions) == {'SS', 'SL', 'LS', 'LL'} and len(neighbors) == 4, 'all_transition_and_neighbor_states')
    payloads, cases, syntax = {}, [], {}
    for index, book in enumerate(configs):
        ib, cb, sb = base.identification(8, 11, RATE), base.comment(), setup(book)
        packets = [audio(book, p) for p in range(14)]
        intentions = [packet_intention(book, p) for p in range(14)]
        offsets = [0]
        for p in packets:
            offsets.append(offsets[-1] + len(p.data()))
        folder = f"cases/{book['id']}/"
        paths = {kind: folder + kind + '.bin' for kind in ('identification', 'comment', 'setup', 'audio')}
        paths['ogg'] = folder + 'reference.ogg'
        data = dict(identification=ib.data(), comment=cb.data(), setup=sb.data(), audio=b''.join(p.data() for p in packets))
        all_packets = [data['identification'], data['comment'], data['setup']] + [p.data() for p in packets]
        carrier = b''.join(base.page(p, 0x53470000 + index + 1, i, ([0, 0, 0] + granules)[i],
            2 if i == 0 else 4 if i == 16 else 0) for i, p in enumerate(all_packets))
        pages = base.read_pages(carrier)
        need([p['packet'] for p in pages] == all_packets and [p['granule'] for p in pages] == [0, 0, 0] + granules
             and [p['flags'] for p in pages] == [2] + [0] * 15 + [4], 'carrier_construction_roundtrip')
        data['ogg'] = carrier
        payloads.update({paths[k]: v for k, v in data.items()})
        active = active_id(book); usage = 14 * CHANNELS * (16 // book['dimensions'])
        audit = dict(**raw_book(book), active_original_ids=[active],
            inactive_original_ids=[i for i, n in enumerate(book['lengths']) if not n],
            vectors_by_original_entry=books.vectors(book),
            selected_original_id_counts={str(active): usage},
            codewords_msb=[None if not n else '0' for n in book['lengths']],
            declared_multiplicand_count=len(book['multiplicands']), all_declared_lookup_values_retained=True,
            intended_public_setup_path=('map1_dec_type2' if book['lookup_type'] == 1 else
                                        'map2_dec_type3' if book['dimensions'] == 16 else 'map2_dec_type1'),
            intended_setup_path_only_not_observed=True)
        cases.append(dict(id=book['id'], **paths, rate=RATE, channels=CHANNELS, bits_per_sample=16,
            short=SHORT, long=LONG, offsets=offsets, mode_flags=list(MODES), packet_count=14,
            expected_raw_samples=total, expected_s16le_bytes=sum(pcm), expected_packet_samples=frames,
            expected_packet_frames=frames, expected_packet_pcm_bytes=pcm, expected_packet_s16le_bytes=pcm,
            packet_granules=granules,
            long_window_flags=[None if not mode else dict(previous=MODES[i - 1], next=MODES[i + 1]) for i, mode in enumerate(MODES)],
            features=['floor1', 'residue0', 'singleton_errata20150226', 'both_singleton_wire_bits',
                      'map' + str(book['lookup_type']), 'dimension' + str(book['dimensions']),
                      'sequence_p' + str(book['sequence_p']), 'active_original_index' + str(active)],
            vector_book=audit, packet_syntax=intentions,
            files={k: dict(bytes=len(v), sha256=sha(v)) for k, v in data.items()},
            raw_sha256={k: sha(v) for k, v in data.items() if k != 'ogg'}))
        syntax[book['id']] = dict(identification=ib.report(), comment=cb.report(), setup=sb.report(),
                                 audio=[p.report() for p in packets])
    for group in equal_groups:
        need(all(payloads[next(c['audio'] for c in cases if c['id'] == name)] ==
                 payloads[next(c['audio'] for c in cases if c['id'] == group[0])] for name in group), 'equal_group_raw_audio')
    after = check_sources(readiness_sha); need(after == before, 'all_sources_unchanged_before_after')
    matrix = dict(schema='vorbis-more-singletons-candidates-v1', status='CONSTRUCTED_INDEPENDENT_WITNESS_AND_REFERENCE_PENDING',
        cases=cases, case_count=8, raw_packet_count=112, expected_total_s16le_bytes=sum(pcm) * 8,
        expected_same_decoder_pcm_equal_groups=equal_groups, expected_same_decoder_pcm_different_pairs=different_pairs,
        expected_audio_wire_equal_groups=equal_groups, pure_spectral_relations_checked=True,
        independent_witness_executed=False, independent_reference_run=False, actual_PCM_equality_verified=False,
        actual_nonzero_PCM_observed=False, target_run=False, readiness_sha256=readiness_sha,
        transitions=dict(transitions), long_neighbor_states={str(k): v for k, v in sorted(neighbors.items())})
    checks = dict(schema='more-singletons-construction-checks-v1', cases=8, packets=112,
        source_inputs_before=before, source_inputs_after=after, normal_pinned_helpers_no_rebinding=True,
        complete_headers_floor1_residue0_and_14_packets=True, bitfield_byte_roundtrips=True,
        singleton_one_bit_both_branches_intended=True, bounded_nonzero_spectrum_is_intention_only=True,
        decoder_reference_unit_SDK_compiler_QEMU_Git_or_device_executed=False)
    for name, value in (('matrix.json', matrix), ('bitfields.json', syntax), ('pure-checks.json', checks)):
        payloads[name] = (json.dumps(value, indent=2) + '\n').encode()
    manifest = dict(schema='more-singletons-generated-manifest-v1', source_inputs=before,
        files=[dict(path=n, bytes=len(v), sha256=sha(v)) for n, v in sorted(payloads.items())])
    payloads['manifest.json'] = (json.dumps(manifest, indent=2) + '\n').encode()
    output.mkdir(parents=True, exist_ok=False)
    for name, raw in payloads.items():
        p = output / name; p.parent.mkdir(parents=True, exist_ok=True)
        with p.open('xb') as stream:
            stream.write(raw)
    print(json.dumps(dict(output=str(output), cases=8, raw_packets=112, manifest_sha256=sha(payloads['manifest.json']),
                         independent_witness_and_reference_pending=True)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--readiness-sha256', required=True)
    args = parser.parse_args()
    generate(args.output, args.readiness_sha256)
