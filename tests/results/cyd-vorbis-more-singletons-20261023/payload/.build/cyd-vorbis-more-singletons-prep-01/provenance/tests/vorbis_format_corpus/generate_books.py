#!/usr/bin/env python3
"""Finite public Vorbis codebook construction; no codec or target execution."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_SHA = "8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1"
BASE_PATH = ROOT / "tests/vorbis_block_matrix/generate_minimal.py"
if hashlib.sha256(BASE_PATH.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError("Pinned canonical minimal helper changed")
_spec = importlib.util.spec_from_file_location("vorbis_format_books_minimal", BASE_PATH)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)  # Definitions only; its guarded main is not called.
RATE, SHORT, LONG, CHANNELS = 192000, 256, 2048, 2
MODES = base.MODES
SPEC = "https://xiph.org/vorbis/doc/Vorbis_I_spec.html"
XIPH = "https://github.com/xiph/vorbis/blob/v1.3.7/lib/sharedbook.c"


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def words(lengths):
    """Entry-order lowest free MSb word, then integer reversal for LSb packing."""
    used, result = [], []
    for length in lengths:
        if not length:
            result.append(None)
            continue
        need(1 <= length <= 8, "finite corpus codeword length")
        candidates = (f"{i:0{length}b}" for i in range(1 << length))
        word = next((w for w in candidates if not any(
            w.startswith(u) or u.startswith(w) for u in used)), None)
        need(word is not None, "overpopulated codeword tree")
        used.append(word)
        result.append(word)
    need(sum((Fraction(1, 1 << n) for n in lengths if n), Fraction()) == 1,
         "finite corpus requires a complete codeword tree")
    return result


def reverse(word):
    return int(word[::-1], 2)


def configurations():
    ordered, unordered, sparse = [1, 3, 3, 3, 3], [3, 1, 3, 3, 3], [1, 0, 2, 3, 0, 3]
    lattice = [0, 2]
    explicit2 = [0, 0, 2, 0, 0, 2, 2, 2, 0, 0]
    explicit4 = [0, 0, 0, 0, 0, 2, 2, 0, 2, 0, 2, 0,
                 0, 2, 0, 2, 2, 0, 0, 2, 2, 2, 2, 2]
    specs = [
        ("ordered_lattice_d2_seq0", ordered, True, 1, 2, 0, lattice),
        ("unordered_lattice_d2_seq0", unordered, False, 1, 2, 0, lattice),
        ("sparse_lattice_d2_seq0", sparse, False, 1, 2, 0, lattice),
        ("ordered_lattice_d2_seq1", ordered, True, 1, 2, 1, lattice),
        ("ordered_explicit_d2_seq0", ordered, True, 2, 2, 0, explicit2),
        ("unordered_explicit_d2_seq1", unordered, False, 2, 2, 1, explicit2),
        ("sparse_explicit_d4_seq0", sparse, False, 2, 4, 0, explicit4),
        ("sparse_explicit_d4_seq1", sparse, False, 2, 4, 1, explicit4),
    ]
    return [dict(id=name, lengths=list(lengths), ordered=ordered_flag,
                 lookup_type=lookup, dimensions=dim, sequence_p=seq,
                 multiplicands=list(values), entries=len(lengths),
                 minimum=-1, delta=1, value_bits=2)
            for name, lengths, ordered_flag, lookup, dim, seq, values in specs]


def quantvals(entries, dim):
    value = 1
    while (value + 1) ** dim <= entries:
        value += 1
    return value


def vectors(book):
    if not book["lookup_type"]:
        return None
    dim, entries, values = book["dimensions"], book["entries"], book["multiplicands"]
    count = quantvals(entries, dim) if book["lookup_type"] == 1 else entries * dim
    need(len(values) == count, "lookup multiplicand count includes sparse holes")
    result = []
    for entry in range(entries):
        last, vector = 0, []
        for coordinate in range(dim):
            offset = ((entry // (count ** coordinate)) % count
                      if book["lookup_type"] == 1 else entry * dim + coordinate)
            value = values[offset] * book["delta"] + book["minimum"] + last
            vector.append(value)
            last = value if book["sequence_p"] else 0
        result.append(vector)
    return result


def write_book(b, number, book):
    p, lengths = f"book[{number}]", book["lengths"]
    b.put(p + ".sync", 24, 0x564342)
    b.put(p + ".dimensions", 16, book["dimensions"])
    b.put(p + ".entries", 24, len(lengths))
    b.put(p + ".ordered", 1, int(book["ordered"]))
    if book["ordered"]:
        need(all(lengths) and lengths == sorted(lengths), "ordered lengths")
        current, position = lengths[0], 0
        b.put(p + ".initial_length_minus_1", 5, current - 1)
        while position < len(lengths):
            count = lengths.count(current)
            b.put(p + f".length_{current}_count", (len(lengths) - position).bit_length(), count)
            position += count
            current += 1
    else:
        sparse = 0 in lengths
        b.put(p + ".sparse", 1, int(sparse))
        for entry, length in enumerate(lengths):
            if sparse:
                b.put(p + f".entry[{entry}].used", 1, int(length != 0))
            if length:
                b.put(p + f".entry[{entry}].length_minus_1", 5, length - 1)
    b.put(p + ".lookup_type", 4, book["lookup_type"])
    if book["lookup_type"]:
        for field in ("minimum", "delta"):
            b.put(p + "." + field, 32, base.packed_float(book[field]))
        b.put(p + ".value_bits_minus_1", 4, book["value_bits"] - 1)
        b.put(p + ".sequence_p", 1, book["sequence_p"])
        for i, value in enumerate(book["multiplicands"]):
            b.put(p + f".multiplicand[{i}]", book["value_bits"], value)


def scalar_book(ordered):
    return dict(entries=2, dimensions=1, lengths=[1, 1], ordered=ordered, lookup_type=0)


def setup(book):
    b = base.Bits()
    base.prefix(b, 5)
    b.put("codebooks_minus_1", 8, 1)
    write_book(b, 0, scalar_book(book["ordered"]))
    write_book(b, 1, book)
    # Identical public floor1/mapping/modes to base, two dense scalar classes.
    for name, width, value in [
        ("time_count_minus_1", 6, 0), ("time[0].type", 16, 0),
        ("floor_count_minus_1", 6, 0), ("floor[0].type", 16, 1),
        ("floor[0].partitions", 5, 0), ("floor[0].multiplier_minus_1", 2, 0),
        ("floor[0].rangebits", 4, 4), ("residue_count_minus_1", 6, 0),
        ("residue[0].type", 16, 1), ("residue[0].begin", 24, 0),
        ("residue[0].end", 24, 16), ("residue[0].partition_size_minus_1", 24, 15),
        ("residue[0].classifications_minus_1", 6, 1), ("residue[0].classbook", 8, 0),
    ]:
        b.put(name, width, value)
    for classification in range(2):
        b.put(f"residue[0].cascade[{classification}].low", 3, 1)
        b.put(f"residue[0].cascade[{classification}].high_present", 1, 0)
    for classification in range(2):
        b.put(f"residue[0].stagebook[{classification}][0]", 8, 1)
    for name, width, value in [
        ("mapping_count_minus_1", 6, 0), ("mapping[0].type", 16, 0),
        ("mapping[0].multiple_submaps", 1, 0), ("mapping[0].coupling", 1, 0),
        ("mapping[0].reserved", 2, 0), ("mapping[0].time", 8, 0),
        ("mapping[0].floor", 8, 0), ("mapping[0].residue", 8, 0),
        ("modes_minus_1", 6, 1),
    ]:
        b.put(name, width, value)
    for mode in range(2):
        for field, width, value in [("blockflag", 1, mode), ("windowtype", 16, 0),
                                    ("transformtype", 16, 0), ("mapping", 8, 0)]:
            b.put(f"mode[{mode}]." + field, width, value)
    b.put("framing", 1, 1)
    return b


def selected_entries(book, packet, channel):
    active = [i for i, length in enumerate(book["lengths"]) if length]
    return [active[(packet * 3 + channel + i) % len(active)]
            for i in range(16 // book["dimensions"])]


def audio(book, packet):
    b, codes = base.Bits(), words(book["lengths"])
    mode = MODES[packet]
    b.put("audio_packet_type", 1, 0)
    b.put("mode", 1, mode)
    if mode:
        b.put("previous_window_flag", 1, MODES[packet - 1] if packet else 0)
        b.put("next_window_flag", 1, MODES[packet + 1] if packet + 1 < len(MODES) else 0)
    for channel in range(CHANNELS):
        b.put(f"floor[{channel}].present", 1, 1)
        b.put(f"floor[{channel}].y0", 8, 255)
        b.put(f"floor[{channel}].y1", 8, 255)
    for channel in range(CHANNELS):
        b.put(f"classword[{channel}]", 1, (packet + channel) % 2)
    for channel in range(CHANNELS):
        for vector, entry in enumerate(selected_entries(book, packet, channel)):
            b.put(f"residue[{channel}].entry[{vector}]={entry}", len(codes[entry]), reverse(codes[entry]))
    return b


class Reader:
    def __init__(self, data):
        self.data, self.position = data, 0

    def take(self, width):
        need(self.position + width <= len(self.data) * 8, "truncated construction")
        value = (int.from_bytes(self.data, "little") >> self.position) & ((1 << width) - 1)
        self.position += width
        return value

    def symbol(self, codes):
        value = ""
        for _ in range(max(map(len, filter(None, codes)))):
            value += str(self.take(1))
            if value in codes:
                return codes.index(value)
        raise ValueError("invalid constructed Huffman token")


def read_book(r):
    need(r.take(24) == 0x564342, "book sync")
    dim, entries, ordered = r.take(16), r.take(24), bool(r.take(1))
    lengths = []
    if ordered:
        length = r.take(5) + 1
        while len(lengths) < entries:
            count = r.take((entries - len(lengths)).bit_length())
            need(count <= entries - len(lengths) and length <= 32, "ordered count")
            lengths.extend([length] * count)
            length += 1
    else:
        sparse = r.take(1)
        lengths = [r.take(5) + 1 if not sparse or r.take(1) else 0 for _ in range(entries)]
    lookup = r.take(4)
    result = dict(entries=entries, dimensions=dim, ordered=ordered, lengths=lengths, lookup_type=lookup)
    if lookup:
        result["minimum"], result["delta"] = int(base.unpack_float(r.take(32))), int(base.unpack_float(r.take(32)))
        result["value_bits"], result["sequence_p"] = r.take(4) + 1, r.take(1)
        count = quantvals(entries, dim) if lookup == 1 else entries * dim
        result["multiplicands"] = [r.take(result["value_bits"]) for _ in range(count)]
    return result


def inspect_audio(data, book, packet):
    r, codes = Reader(data), words(book["lengths"])
    need(r.take(1) == 0 and r.take(1) == MODES[packet], "audio mode")
    if MODES[packet]:
        previous = MODES[packet - 1] if packet else 0
        following = MODES[packet + 1] if packet + 1 < len(MODES) else 0
        need((r.take(1), r.take(1)) == (previous, following), "window neighbors")
    for _ in range(CHANNELS):
        need((r.take(1), r.take(8), r.take(8)) == (1, 255, 255), "floor fields")
    classes = [r.symbol(["0", "1"]) for _ in range(CHANNELS)]
    need(classes == [(packet + channel) % 2 for channel in range(CHANNELS)], "scalar classwords")
    entries = [[r.symbol(codes) for _ in range(16 // book["dimensions"])] for _ in range(CHANNELS)]
    need(entries == [selected_entries(book, packet, channel) for channel in range(CHANNELS)], "actual entry tokens")
    need(len(data) * 8 - r.position < 8 and r.take(len(data) * 8 - r.position) == 0, "audio zero padding")
    table = vectors(book)
    residue = [[value for entry in channel for value in table[entry]] for channel in entries]
    need(all(len(channel) == 16 and any(channel) for channel in residue), "nonzero spectral vectors")
    return dict(classwords=classes, vector_entry_ids=entries, residue_vectors=residue)


def construction_controls():
    example = words([2, 4, 4, 4, 4, 2, 3, 3])
    need(example == ["00", "0100", "0101", "0110", "0111", "10", "110", "111"], "spec Huffman example")
    need(words([1, 3, 3, 3, 3]) == ["0", "100", "101", "110", "111"], "ordered explicit codewords")
    need(words([3, 1, 3, 3, 3]) == ["000", "1", "001", "010", "011"], "entry-order unordered codewords")
    need(words([1, 0, 2, 3, 0, 3]) == ["0", None, "10", "110", None, "111"], "sparse explicit codewords")
    rejected = 0
    for invalid in ([1, 1, 1], [2, 2]):
        try:
            words(invalid)
        except ValueError:
            rejected += 1
    need(rejected == 2, "over/underpopulated construction controls")
    need(base.unpack_float(base.packed_float(-1)) == -1
         and base.unpack_float(base.packed_float(1)) == 1, "exact packed floats")


def generate(output):
    need(sha(Path(base.__file__).read_bytes()) == BASE_SHA, "frozen base helper changed")
    output = output.resolve()
    build_root = ROOT / ".build"
    need(output != build_root and output.is_relative_to(build_root) and not output.exists(),
         "fresh output beneath this checkout's .build required")
    construction_controls()
    payloads, cases, syntax, spectra = {}, [], {}, {}
    sizes = [LONG if mode else SHORT for mode in MODES]
    frames = [0] + [(sizes[i - 1] + sizes[i]) // 4 for i in range(1, len(MODES))]
    cumulative, total = [], 0
    for count in frames:
        total += count
        cumulative.append(total)
    transition_counts = Counter("SL"[MODES[i - 1]] + "SL"[MODES[i]] for i in range(1, len(MODES)))
    need(set(transition_counts) == {"SS", "SL", "LS", "LL"}, "four transitions")
    for case_index, book in enumerate(configurations()):
        name = book["id"]
        raw_book = {k: v for k, v in book.items() if k != "id"}
        sb, ib, cb = setup(book), base.identification(8, 11, RATE), base.comment()
        r = Reader(sb.data())
        need(r.take(8) == 5 and bytes(r.take(8) for _ in range(6)) == b"vorbis" and r.take(8) == 1, "setup prefix/count")
        need(read_book(r) == scalar_book(book["ordered"]), "actual scalar book fields")
        need(read_book(r) == raw_book, "actual vector book fields")
        packets = [audio(book, i) for i in range(len(MODES))]
        observed = [inspect_audio(p.data(), book, i) for i, p in enumerate(packets)]
        usage = Counter(entry for p in observed for channel in p["vector_entry_ids"] for entry in channel)
        active = [i for i, length in enumerate(book["lengths"]) if length]
        need(set(usage) == set(active) and all(usage[i] > 1 for i in active), "all active entries actually selected")
        need(set(x for p in observed for x in p["classwords"]) == {0, 1}, "both scalar entries used")
        table = vectors(book)
        need(len({tuple(table[i]) for i in active}) >= 4, "multiple distinct nonzero VQ values")
        spectra[name] = [p["residue_vectors"] for p in observed]
        offsets = [0]
        for p in packets:
            offsets.append(offsets[-1] + len(p.data()))
        directory = f"cases/{name}"
        paths = {key: f"{directory}/{filename}" for key, filename in (
            ("identification", "identification.bin"), ("setup", "setup.bin"),
            ("comment", "comment.bin"), ("audio", "audio.bin"), ("ogg", "reference.ogg"))}
        data = {"identification": ib.data(), "setup": sb.data(), "comment": cb.data(),
                "audio": b"".join(p.data() for p in packets)}
        full_packets = [data["identification"], data["comment"], data["setup"]] + [p.data() for p in packets]
        granules = [0, 0, 0] + cumulative
        carrier = b"".join(base.page(p, 0x424b0000 + case_index + 1, i, granules[i],
            2 if i == 0 else 4 if i == len(full_packets) - 1 else 0) for i, p in enumerate(full_packets))
        pages = base.read_pages(carrier)
        need([p["packet"] for p in pages] == full_packets and [p["granule"] for p in pages] == granules,
             "actual carrier packet/granule accounting")
        need([p["flags"] for p in pages] == [2] + [0] * (len(full_packets) - 2) + [4], "actual carrier BOS/EOS")
        data["ogg"] = carrier
        payloads.update({paths[key]: value for key, value in data.items()})
        codes = words(book["lengths"])
        audit = dict(**book, codewords_msb_first=codes,
            codewords_lsb_values=[None if code is None else reverse(code) for code in codes],
            vectors_by_original_entry=table, unused_entry_ids=[i for i, n in enumerate(book["lengths"]) if not n],
            actual_entry_usage={str(k): v for k, v in sorted(usage.items())})
        if book["ordered"]:
            audit["ordered_groups"] = [dict(length=n, count=book["lengths"].count(n))
                                        for n in range(min(book["lengths"]), max(book["lengths"]) + 1)]
        cases.append(dict(id=name, **paths, rate=RATE, channels=CHANNELS, short=SHORT, long=LONG,
            bits_per_sample=16, offsets=offsets, packet_count=len(MODES), mode_flags=list(MODES),
            expected_raw_samples=total, expected_s16le_bytes=total * CHANNELS * 2,
            expected_packet_samples=frames, expected_packet_pcm_bytes=[n * CHANNELS * 2 for n in frames],
            packet_granules=cumulative, transitions=dict(sorted(transition_counts.items())),
            features=["floor1", "residue1", "lookup0_scalar_classes0and1", "lookup" + str(book["lookup_type"]),
                      "ordered_zero_count_gap" if book["ordered"] else "sparse_vector_holes" if 0 in book["lengths"] else "unordered_nondecreasing_false",
                      f"vector_dimension{book['dimensions']}", f"sequence_p{book['sequence_p']}"],
            vector_book=audit, packet_syntax=observed,
            files={key: dict(bytes=len(value), sha256=sha(value)) for key, value in data.items()}))
        syntax[name] = dict(identification=ib.report(), setup=sb.report(), comment=cb.report(),
                            audio=[p.report() for p in packets])
    equivalent = [["ordered_lattice_d2_seq0", "unordered_lattice_d2_seq0", "ordered_explicit_d2_seq0"],
                  ["ordered_lattice_d2_seq1", "unordered_explicit_d2_seq1"]]
    different = [["ordered_lattice_d2_seq0", "ordered_lattice_d2_seq1"],
                 ["sparse_explicit_d4_seq0", "sparse_explicit_d4_seq1"]]
    for group in equivalent:
        need(all(spectra[name] == spectra[group[0]] for name in group), "equivalent complete spectral vectors")
    for first, second in different:
        need(spectra[first] != spectra[second], "sequence_p changes actual spectral vectors")
    damaged = bytearray(payloads[cases[0]["ogg"]])
    damaged[-1] ^= 1
    try:
        base.read_pages(damaged)
    except ValueError as exc:
        need(str(exc) == "CRC mismatch", "CRC rejection reason")
    else:
        raise ValueError("damaged carrier accepted")
    matrix = dict(schema="vorbis-public-codebooks-v1", status="INDEPENDENT_DECODE_PENDING",
        cases=cases, case_count=len(cases), raw_packet_count=len(cases) * len(MODES),
        expected_same_decoder_pcm_equal_groups=equivalent, expected_same_decoder_pcm_different_pairs=different,
        pure_spectral_equal_and_different_checks=True, independent_pcm_checks_executed=False,
        target_qualification_executed=False)
    checks = dict(schema="vorbis-books-construction-v1", status="CONSTRUCTION_CHECKED_ONLY",
        fields_roundtrip=True, actual_book_parse_and_token_scan=True, actual_original_entry_ids_preserved=True,
        complete_prefix_trees=True, spec_eight_entry_huffman_example=True, ordered_zero_count_length_group=True,
        all_active_vector_entries_used=True, both_dense_scalar_entries_used=True,
        no_single_entry_tree=True, crc_and_packet_and_granule_roundtrip=True, crc_corruption_rejected=True,
        spectral_vectors_nonzero=True, independent_decode_run=False, nonzero_pcm_observed=False,
        sdk_compiler_qemu_run=False, cases=len(cases), raw_packets=len(cases) * len(MODES),
        raw_samples_per_case=total, pcm_bytes_per_case=total * CHANNELS * 2)
    for filename, document in [("matrix.json", matrix), ("construction-checks.json", checks), ("bitfields.json", syntax)]:
        payloads[filename] = (json.dumps(document, indent=2) + "\n").encode()
    manifest = dict(schema="vorbis-books-manifest-v1", generator_sha256=sha(Path(__file__).read_bytes()),
        base_helper_sha256=BASE_SHA, references=[SPEC, XIPH], independent_decode_pending=True,
        files=[dict(path=name, bytes=len(data), sha256=sha(data)) for name, data in sorted(payloads.items())])
    payloads["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    for name, data in payloads.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
    print(json.dumps(dict(output=str(output), cases=len(cases), raw_packets=len(cases) * len(MODES),
        raw_samples_per_case=total, pcm_bytes_per_case=total * CHANNELS * 2,
        manifest_sha256=sha(payloads["manifest.json"]), independent_decode_pending=True)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".build/vorbis-books-corpus-01")
    generate(parser.parse_args().output)
