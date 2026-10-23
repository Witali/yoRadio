"""Eight complete raw map2 regression candidates; pure construction only."""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BOOKS = ROOT / "tests/vorbis_format_corpus/generate_books.py"
BOOKS_SHA = "de9b09de59a0825feda741c0343c6d60821ddad1258ce7df5ae342c68e268fc1"
MINIMAL = ROOT / "tests/vorbis_block_matrix/generate_minimal.py"
MINIMAL_SHA = "8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1"
RATE, CHANNELS, SHORT, LONG, FLOOR_RANGEBITS = 192000, 2, 256, 2048, 10
SPEC = "https://xiph.org/vorbis/doc/Vorbis_I_spec.html"
REFERENCES = [SPEC, "https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/sharedbook.c",
              "https://xiph.org/ogg/doc/framing.html"]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


need(sha(BOOKS.read_bytes()) == BOOKS_SHA, "canonical_book_helper_pin")
need(sha(MINIMAL.read_bytes()) == MINIMAL_SHA, "canonical_minimal_helper_pin")
spec = importlib.util.spec_from_file_location("pinned_map2_book_construction", BOOKS)
books = importlib.util.module_from_spec(spec)
spec.loader.exec_module(books)  # Guarded generator main is not called.
base = books.base
need(Path(base.__file__).resolve() == MINIMAL.resolve(), "actual_minimal_import_path")
MODES = base.MODES


def codewords(lengths):
    # Exact declared single-leaf exception, Vorbis Errata 20150226.
    # Keep the complete-tree helper unchanged; all other underpopulation rejects.
    if lengths == [1]:
        return ["0"]
    return books.words(lengths)


def configurations():
    rows = [[2, 0] * 8, [3, 0, 1, 2] * 4, [0, 2] * 8,
            [2, 2, 0, 0] * 4, [1, 3, 2, 0] * 4, [0, 0, 2, 2] * 4]
    need(len({tuple(r) for r in rows}) == 6, "distinct_original_rows_including_holes")
    active = [0, 2, 3, 5]
    result = []
    for seq in (0, 1):
        for kind, lengths, selected_rows, ordered in (
            ("sparse_explicit", [1, 0, 2, 3, 0, 3], rows, False),
            ("dense_active", [1, 2, 3, 3], [rows[i] for i in active], True)):
            result.append(dict(id=f"{kind}_d16_seq{seq}", lengths=lengths, ordered=ordered,
                lookup_type=2, dimensions=16, entries=len(lengths), minimum=-1, delta=1,
                value_bits=2, sequence_p=seq, multiplicands=[v for row in selected_rows for v in row]))
    for seq in (0, 1):
        for kind, count in (("single_explicit", 1), ("dense_twin", 2)):
            result.append(dict(id=f"{kind}_d2_seq{seq}", lengths=[1] * count, ordered=False,
                lookup_type=2, dimensions=2, entries=count, minimum=-1, delta=1,
                value_bits=2, sequence_p=seq, multiplicands=[2, 0] * count))
    return result


def raw_book(book):
    return {key: value for key, value in book.items() if key != "id"}


def setup(book):
    b = base.Bits(); base.prefix(b, 5); b.put("codebooks_minus_1", 8, 1)
    books.write_book(b, 0, books.scalar_book(False))
    books.write_book(b, 1, book)
    for name, width, value in (
        ("time_count_minus_1", 6, 0), ("time[0].type", 16, 0),
        ("floor_count_minus_1", 6, 0), ("floor[0].type", 16, 1),
        ("floor[0].partitions", 5, 0), ("floor[0].multiplier_minus_1", 2, 0),
        ("floor[0].rangebits", 4, FLOOR_RANGEBITS), ("residue_count_minus_1", 6, 0),
        ("residue[0].type", 16, 1), ("residue[0].begin", 24, 0),
        ("residue[0].end", 24, 16), ("residue[0].partition_size_minus_1", 24, 15),
        ("residue[0].classifications_minus_1", 6, 1), ("residue[0].classbook", 8, 0)):
        b.put(name, width, value)
    for classification in range(2):
        b.put(f"residue[0].cascade[{classification}].low", 3, 1)
        b.put(f"residue[0].cascade[{classification}].high_present", 1, 0)
    for classification in range(2): b.put(f"residue[0].stagebook[{classification}][0]", 8, 1)
    for name, width, value in (
        ("mapping_count_minus_1", 6, 0), ("mapping[0].type", 16, 0),
        ("mapping[0].multiple_submaps", 1, 0), ("mapping[0].coupling", 1, 0),
        ("mapping[0].reserved", 2, 0), ("mapping[0].time", 8, 0),
        ("mapping[0].floor", 8, 0), ("mapping[0].residue", 8, 0), ("modes_minus_1", 6, 1)):
        b.put(name, width, value)
    for mode in range(2):
        for field, width, value in (("blockflag", 1, mode), ("windowtype", 16, 0),
                                    ("transformtype", 16, 0), ("mapping", 8, 0)):
            b.put(f"mode[{mode}]." + field, width, value)
    b.put("framing", 1, 1)
    return b


def inspect_setup(data, expected):
    r = books.Reader(data)
    need(r.take(56) == int.from_bytes(b"\x05vorbis", "little") and r.take(8) == 1, "setup_prefix_and_book_count")
    need(books.read_book(r) == books.scalar_book(False), "scalar_book_fields")
    observed = books.read_book(r)
    need(observed == raw_book(expected), "vector_book_fields")
    codewords(observed["lengths"])
    suffix = ((6, 0), (16, 0), (6, 0), (16, 1), (5, 0), (2, 0), (4, 10),
        (6, 0), (16, 1), (24, 0), (24, 16), (24, 15), (6, 1), (8, 0),
        (3, 1), (1, 0), (3, 1), (1, 0), (8, 1), (8, 1),
        (6, 0), (16, 0), (1, 0), (1, 0), (2, 0), (8, 0), (8, 0), (8, 0), (6, 1),
        (1, 0), (16, 0), (16, 0), (8, 0), (1, 1), (16, 0), (16, 0), (8, 0), (1, 1))
    for width, value in suffix: need(r.take(width) == value, "complete_setup_suffix")
    finish(r, "setup")
    return observed


def finish(r, kind):
    remaining = len(r.data) * 8 - r.position
    need(0 <= remaining < 8 and r.take(remaining) == 0, kind + "_exact_bytes_and_padding")


def audio(book, packet):
    b = base.Bits(); codes = codewords(book["lengths"]); mode = MODES[packet]
    b.put("audio_packet_type", 1, 0); b.put("mode", 1, mode)
    if mode:
        b.put("previous_window_flag", 1, MODES[packet - 1])
        b.put("next_window_flag", 1, MODES[packet + 1])
    for channel in range(CHANNELS):
        b.put(f"floor[{channel}].present", 1, 1)
        b.put(f"floor[{channel}].y0", 8, 255); b.put(f"floor[{channel}].y1", 8, 255)
    for channel in range(CHANNELS): b.put(f"classword[{channel}]", 1, (packet + channel) % 2)
    for channel in range(CHANNELS):
        for vector, entry in enumerate(books.selected_entries(book, packet, channel)):
            # Errata20150226 permits either consumed bit for the sole used value.
            # Match the dense twin's entry0/1 parity while single still returns0.
            wire = (packet + channel + vector) % 2 if book["entries"] == 1 else books.reverse(codes[entry])
            b.put(f"residue[{channel}].entry[{vector}]={entry}", len(codes[entry]), wire)
    return b


def inspect_audio(data, book, packet):
    r = books.Reader(data); codes = codewords(book["lengths"])
    need(r.take(1) == 0 and r.take(1) == MODES[packet], "audio_packet_mode")
    if MODES[packet]: need((r.take(1), r.take(1)) == (MODES[packet - 1], MODES[packet + 1]), "window_flags")
    for _ in range(CHANNELS): need((r.take(1), r.take(8), r.take(8)) == (1, 255, 255), "channel_floor_order")
    classes = [r.symbol(["0", "1"]) for _ in range(CHANNELS)]
    need(classes == [(packet + c) % 2 for c in range(CHANNELS)], "classword_order")
    token_start = r.position
    entries, single_wire_bits = [], []
    for channel in range(CHANNELS):
        values, wire = [], []
        for _ in range(16 // book["dimensions"]):
            if book["entries"] == 1:
                wire.append(r.take(1)); values.append(0)
            else:
                values.append(r.symbol(codes))
        entries.append(values)
        if book["entries"] == 1: single_wire_bits.append(wire)
    need(entries == [books.selected_entries(book, packet, c) for c in range(CHANNELS)], "actual_selected_entries")
    if book["entries"] == 1:
        need(single_wire_bits == [[(packet + channel + vector) % 2 for vector in range(8)] for channel in range(2)], "single_entry_varied_wire_bits")
    used_bits = r.position
    finish(r, "audio")
    vectors = books.vectors(book)
    residue = [[value for entry in channel for value in vectors[entry]] for channel in entries]
    need(all(len(v) == 16 and any(v) and max(map(abs, v)) <= 2 for v in residue), "bounded_nonzero_integer_spectrum")
    return dict(classwords=classes, vector_entry_ids=entries, residue_vectors=residue,
                one_bit_per_single_entry=book["entries"] == 1, used_bits=used_bits,
                token_bits=used_bits-token_start, token_count=sum(map(len, entries)),
                padding_bits=len(data)*8-used_bits, single_entry_wire_bits=single_wire_bits)


def spectra(book):
    return [inspect_audio(audio(book, p).data(), book, p)["residue_vectors"] for p in range(14)]


def pair_equal(first, second):
    need(spectra(first) == spectra(second), "expected_spectral_equality")


def negative_controls(configs):
    result = []
    def reject(name, action, reason):
        try: action()
        except ValueError as error:
            need(str(error) == reason, "wrong_control_oracle:" + name + ":" + str(error))
        else: raise ValueError("accepted_negative_control:" + name)
        result.append(dict(name=name, rejected=True, exact_reason=reason))
    sparse, dense, single, twin = configs[0], configs[1], configs[4], configs[5]
    compacted = dict(sparse, multiplicands=dense["multiplicands"])
    reject("map2_unused_original_rows_omitted", lambda: inspect_setup(setup(compacted).data(), sparse), "vector_book_fields")
    prefix = dict(dense, multiplicands=sparse["multiplicands"][:64])
    reject("map2_used_count_reads_original_prefix", lambda: pair_equal(sparse, prefix), "expected_spectral_equality")
    reject("single_entry_length2_rejected", lambda: codewords([2]), "finite corpus requires a complete codeword tree")
    reject("other_underpopulated_tree_rejected", lambda: codewords([2, 2]), "finite corpus requires a complete codeword tree")
    b = audio(single, 0); missing = base.Bits(); missing.bits = b.bits[:-16]
    reject("single_entry_zero_bit_consumption", lambda: inspect_audio(missing.data(), single, 0), "truncated construction")
    wrong_twin = dict(twin, multiplicands=[2, 0, 3, 0])
    reject("twin_rows_must_be_vector_identical", lambda: pair_equal(single, wrong_twin), "expected_spectral_equality")
    changed = bytearray(audio(sparse, 0).data()); changed[4] ^= 1 << 6
    reject("audio_selected_entry_changed", lambda: inspect_audio(bytes(changed), sparse, 0), "actual_selected_entries")
    carrier = bytearray(base.page(audio(single, 0).data(), 1, 0, 0, 2)); carrier[-1] ^= 1
    reject("carrier_crc_changed", lambda: base.read_pages(carrier), "CRC mismatch")
    return result


def fact(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), sha256=sha(raw))


def generate(output):
    output = output.resolve(); need(output.parent == HERE and not output.exists(), "fresh_direct_child_output")
    inputs = [Path(__file__).resolve(), HERE / "README02.md", BOOKS, MINIMAL]
    before = [fact(p) for p in inputs]
    configs = configurations(); need(len(configs) == 8, "exact_8_cases")
    equal_groups = [[configs[i]["id"], configs[i + 1]["id"]] for i in (0, 2, 4, 6)]
    for i in (0, 2, 4, 6): pair_equal(configs[i], configs[i + 1])
    controls = negative_controls(configs)
    frames = [0] + [((LONG if a else SHORT) + (LONG if b else SHORT)) // 4 for a, b in zip(MODES, MODES[1:])]
    pcm = [n * CHANNELS * 2 for n in frames]; granules = []; total = 0
    for count in frames: total += count; granules.append(total)
    transitions = Counter("SL"[a] + "SL"[b] for a, b in zip(MODES, MODES[1:]))
    neighbors = Counter((MODES[i - 1], MODES[i + 1]) for i in range(1, 13) if MODES[i])
    need(set(transitions) == {"SS", "SL", "LS", "LL"} and len(neighbors) == 4, "all_transitions_and_neighbors")
    payloads, cases, syntax = {}, [], {}
    for index, book in enumerate(configs):
        ib, sb, cb = base.identification(8, 11, RATE), setup(book), base.comment()
        observed_book = inspect_setup(sb.data(), book)
        packets = [audio(book, p) for p in range(14)]
        observed = [inspect_audio(packet.data(), book, p) for p, packet in enumerate(packets)]
        usage = Counter(e for p in observed for channel in p["vector_entry_ids"] for e in channel)
        active = [i for i, n in enumerate(book["lengths"]) if n]
        need(set(usage) == set(active) and all(usage[i] > 1 for i in active), "every_active_entry_selected")
        offsets = [0]
        for packet in packets: offsets.append(offsets[-1] + len(packet.data()))
        folder = f"cases/{book['id']}/"
        paths = {kind: folder + kind + ".bin" for kind in ("identification", "setup", "comment", "audio")}
        paths["ogg"] = folder + "reference.ogg"
        data = dict(identification=ib.data(), setup=sb.data(), comment=cb.data(), audio=b"".join(p.data() for p in packets))
        all_packets = [data["identification"], data["comment"], data["setup"]] + [p.data() for p in packets]
        carrier = b"".join(base.page(p, 0x4d320000 + index + 1, i, ([0, 0, 0] + granules)[i],
            2 if i == 0 else 4 if i == 16 else 0) for i, p in enumerate(all_packets))
        pages = base.read_pages(carrier)
        need([p["packet"] for p in pages] == all_packets and [p["granule"] for p in pages] == [0, 0, 0] + granules and
             [p["flags"] for p in pages] == [2] + [0] * 15 + [4], "carrier_packet_crc_granule_flags")
        data["ogg"] = carrier
        for kind, value in data.items(): payloads[paths[kind]] = value
        audit = dict(**raw_book(book), vectors_by_original_entry=books.vectors(observed_book),
            codewords_msb=codewords(book["lengths"]), active_original_ids=active,
            inactive_original_ids=[i for i, n in enumerate(book["lengths"]) if not n],
            all_original_multiplicands_retained=True, original_multiplicand_count=book["entries"] * book["dimensions"],
            selected_original_id_counts={str(k): v for k, v in sorted(usage.items())},
            quantized_bits_per_vector=book["value_bits"] * book["dimensions"],
            expected_public_setup_storage_path="wide_map2_dec_type3" if book["dimensions"] == 16 else "single_or_twin_packed_map2")
        cases.append(dict(id=book["id"], **paths, rate=RATE, channels=CHANNELS, bits_per_sample=16, short=SHORT, long=LONG,
            offsets=offsets, mode_flags=list(MODES), packet_count=14, expected_raw_samples=total,
            expected_s16le_bytes=sum(pcm), expected_packet_samples=frames, expected_packet_frames=frames,
            expected_packet_pcm_bytes=pcm, expected_packet_s16le_bytes=pcm, packet_granules=granules,
            long_window_flags=[None if not mode else dict(previous=MODES[i - 1], next=MODES[i + 1]) for i, mode in enumerate(MODES)],
            features=["map2_complete_rows", f"dimension{book['dimensions']}", f"sequence_p{book['sequence_p']}",
                      "single_entry_errata20150226" if book["entries"] == 1 else "sparse_rows" if 0 in book["lengths"] else "dense_control"],
            vector_book=audit, packet_syntax=observed, raw_sha256={k: sha(v) for k, v in data.items() if k != "ogg"},
            files={k: dict(bytes=len(v), sha256=sha(v)) for k, v in data.items()}))
        syntax[book["id"]] = dict(identification=ib.report(), setup=sb.report(), comment=cb.report(), audio=[p.report() for p in packets])
    # Active-row remapping and single/twin bit tolerance preserve actual wires.
    for i in (0, 2, 4, 6):
        need(payloads[cases[i]["audio"]] == payloads[cases[i + 1]["audio"]], "metamorphic_audio_wire_equivalence")
    need([fact(p) for p in inputs] == before, "unchanged_source_inputs")
    matrix = dict(schema="vorbis-map2-regression-candidates-v1", status="CONSTRUCTION_CHECKED_REFERENCE_PENDING", cases=cases,
        case_count=8, raw_packet_count=112, expected_total_s16le_bytes=sum(c["expected_s16le_bytes"] for c in cases),
        expected_same_decoder_pcm_equal_groups=equal_groups, pure_integer_spectral_equal_groups_verified=True,
        actual_PCM_equality_verified=False, actual_nonzero_PCM_observed=False, independent_reference_run=False, target_run=False,
        transitions=dict(transitions), long_neighbor_states={str(k): v for k, v in sorted(neighbors.items())}, references=REFERENCES)
    checks = dict(schema="map2-pure-construction-checks-v1", completed=True, cases=8, packets=112,
        expected_pcm_bytes_per_case=sum(pcm), expected_total_pcm_bytes=sum(pcm) * 8, source_inputs_before=before,
        source_inputs_after=[fact(p) for p in inputs], full_setup_and_packet_field_scan=True,
        single_entry_exact_length1_both_bits_consumed=True, other_underpopulation_rejected=True,
        all_active_original_entries_selected=True, all_original_map2_rows_retained=True,
        all_four_expected_spectral_pair_equalities=True, exact_negative_controls=controls,
        no_helper_copies_or_global_function_rebinding=True, actual_codec_SDK_compiler_QEMU_reference_Git_device_executed=False)
    for name, value in (("matrix.json", matrix), ("bitfields.json", syntax), ("pure-checks.json", checks)):
        payloads[name] = (json.dumps(value, indent=2) + "\n").encode()
    manifest = dict(schema="map2-regression-source-manifest-v1", source_inputs=before, references=REFERENCES,
        files=[dict(path=p, bytes=len(v), sha256=sha(v)) for p, v in sorted(payloads.items())])
    payloads["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    output.mkdir()
    for name, data in payloads.items():
        path = output / name; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream: stream.write(data)
    print(json.dumps(dict(output=str(output), cases=8, raw_packets=112, expected_pcm_bytes_per_case=sum(pcm),
        expected_total_pcm_bytes=sum(pcm) * 8, manifest_sha256=sha(payloads["manifest.json"]), reference_pending=True)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    generate(parser.parse_args().output)
