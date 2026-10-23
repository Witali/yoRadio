"""Independent raw-bit/Fraction/Q24 witness; never decode or synthesize PCM.

No generator/helper module is imported. Field offsets are independently obtained
by reading the actual setup syntax, rather than trusting construction reports.
The public lookup2 equation and floor0 accumulation are evaluated with exact
rational arithmetic only; this is not a floor curve, residue or audio decoder.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
PACKED_SIXTEENTH = 0x62000001
VARIANTS = ("floor0-even6-r0", "floor0-odd5-r0")
PAIRS = ((64, 256), (256, 2048), (64, 2048))
IDS = tuple(f"{variant}-s{s}-l{l}" for variant in VARIANTS for s, l in PAIRS)
MODES = [0 if item == "S" else 1 for item in "SSLLLSLSSSLLSS"]
INVARIANTS = ("short", "long", "rate", "channels", "bits", "mode_flags", "offsets",
    "expected_packet_frames", "expected_packet_s16le_bytes", "expected_raw_samples",
    "expected_s16le_bytes", "packet_granules", "packet_count", "public_decode_output_capacity")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fraction_float(word):
    mantissa = word & 0x1fffff
    if word & 0x80000000:
        mantissa = -mantissa
    exponent = ((word >> 21) & 0x3ff) - 788
    return Fraction(mantissa) * Fraction(2) ** exponent


class Reader:
    def __init__(self, data):
        self.data, self.position, self.fields = data, 0, {}

    def take(self, name, width):
        need(name not in self.fields and 0 <= width <= 64 and
             self.position + width <= len(self.data) * 8, "bit_read_bounds_or_name")
        start, result = self.position, 0
        for index in range(width):
            position = self.position + index
            result |= ((self.data[position // 8] >> (position % 8)) & 1) << index
        self.position += width
        self.fields[name] = dict(offset=start, width=width, value=result)
        return result

    def expected(self, name, width, value):
        result = self.take(name, width)
        need(result == value, "field_expectation:" + name)
        return result

    def finish(self):
        need(0 <= len(self.data) * 8 - self.position < 8, "unexpected_trailing_fields")
        need(all(((self.data[p // 8] >> (p % 8)) & 1) == 0
             for p in range(self.position, len(self.data) * 8)), "nonzero_padding")


def prefix(reader, packet_type):
    reader.expected("packet_type", 8, packet_type)
    for index, value in enumerate(b"vorbis"):
        reader.expected(f"signature[{index}]", 8, value)


def parse_setup(data):
    r = Reader(data)
    prefix(r, 5)
    count = r.take("books_minus_1", 8) + 1
    need(count in (3, 4), "three_or_four_total_books")
    books = []
    for number in range(count):
        p = f"book[{number}]."
        r.expected(p + "sync", 24, 0x564342)
        dimensions, entries = r.take(p + "dimensions", 16), r.take(p + "entries", 24)
        need((dimensions, entries) == ((1, 1) if number == 0 else (2, 4) if number == 1 else (3, 2)),
             "bounded_original_book_shape")
        r.expected(p + "ordered", 1, 0)
        r.expected(p + "sparse", 1, 0)
        lengths = [r.take(p + f"length_minus_1[{i}]", 5) + 1 for i in range(entries)]
        need(lengths == ([2] * 4 if number == 1 else [1] * entries), "original_huffman_lengths")
        lookup = r.take(p + "maptype", 4)
        need(lookup == (0 if number == 0 else 1 if number == 1 else 2), "original_lookup_type")
        book = dict(number=number, dimensions=dimensions, entries=entries, lengths=lengths, lookup=lookup)
        if lookup:
            minimum, delta = r.take(p + "minimum", 32), r.take(p + "delta", 32)
            bits, sequence = r.take(p + "value_bits_minus_1", 4) + 1, r.take(p + "sequence_p", 1)
            need(bits == (1 if number == 1 else 5) and sequence == 0, "original_quant_width_sequence")
            values = [r.take(p + f"multiplicand[{i}]", bits) for i in range(2 if lookup == 1 else entries * dimensions)]
            book.update(minimum=minimum, delta=delta, bits=bits, sequence=sequence, multiplicands=values)
            if number == 1:
                need(fraction_float(minimum) == -1 and fraction_float(delta) == 2 and values == [0, 1],
                     "unchanged_residue_lookup")
            else:
                lo, step = fraction_float(minimum), fraction_float(delta)
                book["vectors"] = [[lo + value * step for value in values[i:i + dimensions]]
                                   for i in range(0, len(values), dimensions)]
        books.append(book)
    r.expected("times_minus_1", 6, 0)
    r.expected("time.type", 16, 0)
    r.expected("floors_minus_1", 6, 0)
    r.expected("floor.type", 16, 0)
    order, rate, bark = r.take("floor0.order", 8), r.take("floor0.rate", 16), r.take("floor0.barkmap", 16)
    ampbits, ampdB = r.take("floor0.amplitude_bits", 6), r.take("floor0.amplitude_offset", 8)
    floor_book_count = r.take("floor0.books_minus_1", 4) + 1
    floor_books = [r.take(f"floor0.book[{i}]", 8) for i in range(floor_book_count)]
    need((order, rate, bark, ampbits, ampdB, floor_books) in
         ((6, 48000, 64, 6, 60, [2]), (5, 48000, 128, 8, 60, [2, 3])), "original_floor_configuration")
    need(floor_book_count == count - 2, "floor_book_count_matches_setup")
    for name, width, value in (("residues_minus_1", 6, 0), ("residue.type", 16, 0),
        ("residue.begin", 24, 0), ("residue.end", 24, 16), ("residue.partition_size_minus_1", 24, 15),
        ("residue.classifications_minus_1", 6, 0), ("residue.classbook", 8, 0),
        ("residue.cascade_low", 3, 1), ("residue.cascade_high_present", 1, 0),
        ("residue.stagebook", 8, 1), ("mappings_minus_1", 6, 0), ("mapping.type", 16, 0),
        ("mapping.submaps_flag", 1, 0), ("mapping.coupling_flag", 1, 0), ("mapping.reserved", 2, 0),
        ("mapping.time", 8, 0), ("mapping.floor", 8, 0), ("mapping.residue", 8, 0), ("modes_minus_1", 6, 1)):
        r.expected(name, width, value)
    for mode in range(2):
        r.expected(f"mode[{mode}].blockflag", 1, mode)
        r.expected(f"mode[{mode}].windowtype", 16, 0)
        r.expected(f"mode[{mode}].transformtype", 16, 0)
        r.expected(f"mode[{mode}].mapping", 8, 0)
    r.expected("framing", 1, 1)
    r.finish()
    return dict(fields=r.fields, books=books, order=order, ampbits=ampbits,
                floor_books=floor_books, used_bits=r.position, padding_bits=len(data) * 8 - r.position)


def setup_pair(original, equivalent):
    old, new = parse_setup(original), parse_setup(equivalent)
    need(len(original) == len(equivalent) and old["fields"].keys() == new["fields"].keys(), "setup_layout")
    allowed, changed, rows = set(), [], []
    for ob, nb in zip(old["books"][2:], new["books"][2:]):
        number = ob["number"]
        need(ob["minimum"] == 0 and nb["minimum"] == PACKED_SIXTEENTH, "equivalent_minimum")
        need(ob["delta"] == nb["delta"] == PACKED_SIXTEENTH, "equivalent_delta")
        need(nb["multiplicands"] == [value - 1 for value in ob["multiplicands"]], "multiplicand_shift")
        need(ob["vectors"] == nb["vectors"], "exact_lookup2_vector_equality")
        allowed.add(f"book[{number}].minimum")
        allowed.update(f"book[{number}].multiplicand[{i}]" for i in range(6))
        q24 = []
        for vector in ob["vectors"]:
            row = []
            for value in vector:
                exact = value * (1 << 24)
                need(exact.denominator == 1 and 0 < exact < (1 << 31), "exact_signed32_Q24")
                row.append(int(exact))
            q24.append(row)
        rows.append(dict(book=number, original_multiplicands=ob["multiplicands"],
            equivalent_multiplicands=nb["multiplicands"], decoded_vectors_exact=[
                [str(value) for value in vector] for vector in ob["vectors"]], exact_Q24_vectors=q24))
    mask = 0
    for name, before in old["fields"].items():
        after = new["fields"][name]
        need((before["offset"], before["width"]) == (after["offset"], after["width"]), "field_layout")
        if name in allowed:
            need(before["value"] != after["value"], "each_target_field_changes")
            mask |= ((1 << before["width"]) - 1) << before["offset"]
            changed.append(dict(name=name, offset=before["offset"], width=before["width"],
                original=before["value"], equivalent=after["value"]))
        else:
            need(before == after, "non_target_setup_field_changed:" + name)
    xor = int.from_bytes(original, "little") ^ int.from_bytes(equivalent, "little")
    need(xor != 0 and not xor & ~mask and len(changed) == 7 * len(old["floor_books"]), "allowed_setup_bit_changes")
    return old, new, dict(changed_fields=changed, books=rows)


def packet_fields(data, setup, index):
    r = Reader(data)
    r.expected("type", 1, 0)
    r.expected("mode", 1, MODES[index])
    if MODES[index]:
        r.expected("previous_window", 1, MODES[index - 1])
        r.expected("next_window", 1, MODES[index + 1])
    floors = []
    for channel in range(2):
        p = f"floor[{channel}]."
        amplitude = r.take(p + "amplitude", setup["ampbits"])
        selector = r.take(p + "selector", len(setup["floor_books"]).bit_length())
        need(amplitude > 0 and selector < len(setup["floor_books"]), "positive_amplitude_valid_selector")
        words = [r.take(p + f"word[{i}]", 1) for i in range(2)]
        book = setup["books"][setup["floor_books"][selector]]
        last, coefficients = Fraction(0), []
        for word in words:
            vector = [value + last for value in book["vectors"][word]]
            coefficients.extend(vector)
            last = vector[-1]
        used, ignored = coefficients[:setup["order"]], coefficients[setup["order"]:]
        need(all(0 < value < 3 for value in used) and all(a < b for a, b in zip(used, used[1:])),
             "increasing_original_LSP_angles")
        need(all((value * 16).denominator == (value * (1 << 24)).denominator == 1
             for value in coefficients), "dyadic_Q24_coefficients")
        floors.append(dict(amplitude_raw=amplitude, book_selector=selector, vq_words=words,
            lsp_used_units_1_16=[int(value * 16) for value in used],
            lsp_ignored_units_1_16=[int(value * 16) for value in ignored],
            exact_Q24_used=[int(value * (1 << 24)) for value in used],
            exact_Q24_ignored=[int(value * (1 << 24)) for value in ignored]))
    for channel in range(2):
        r.expected(f"classword[{channel}]", 1, 0)
    residue = []
    for channel in range(2):
        values = [0] * 16
        for i in range(8):
            bits = r.take(f"residue[{channel}].word[{i}]", 2)
            word = ((bits & 1) << 1) | (bits >> 1)
            values[i], values[i + 8] = 2 * (word & 1) - 1, 2 * (word >> 1) - 1
        residue.append(values)
    r.finish()
    return dict(floors=floors, residue_first16=residue, used_bits=r.position)


def crc(data):
    value = 0
    for octet in data:
        value ^= octet << 24
        for _ in range(8):
            value = ((value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)) & 0xffffffff
    return value


def pages(data):
    offset, result = 0, []
    while offset < len(data):
        need(data[offset:offset + 5] == b"OggS\0" and len(data) - offset >= 27, "carrier_header")
        count = data[offset + 26]
        laces = data[offset + 27:offset + 27 + count]
        length = 27 + count + sum(laces)
        body = data[offset:offset + length]
        need(len(laces) == count and count > 0 and laces[-1] != 255 and len(body) == length,
             "complete_carrier_packet")
        actual_crc = int.from_bytes(body[22:26], "little")
        need(actual_crc == crc(body[:22] + bytes(4) + body[26:]), "carrier_CRC")
        flags, granule, serial, sequence = struct.unpack_from("<BQII", body, 5)
        need(sequence == len(result), "carrier_sequence")
        result.append(dict(offset=offset, bytes=length, page=body, header=body[:27 + count],
            packet=body[27 + count:], flags=flags, granule=granule, serial=serial))
        offset += length
    need(offset == len(data) and len(result) == 17, "complete_17_page_carrier")
    return result


def patch_field(data, field, value):
    need(0 <= value < 1 << field["width"], "control_patch_value")
    packed = int.from_bytes(data, "little")
    mask = ((1 << field["width"]) - 1) << field["offset"]
    packed = (packed & ~mask) | (value << field["offset"])
    return packed.to_bytes(len(data), "little")


def require_rejected(name, original, equivalent, field, replacement, expected):
    damaged = patch_field(equivalent, field, replacement)
    try:
        setup_pair(original, damaged)
    except ValueError as error:
        need(str(error) == expected, "wrong_control_failure:" + name + ":" + str(error))
        return dict(name=name, result="EXPECTED_REJECTION", exact_error=str(error))
    raise ValueError("control_unexpectedly_accepted:" + name)


def witness(repository, generated):
    pins = json.loads((HERE / "source-pins.json").read_bytes())
    for row in pins["local_inputs"]:
        data = (repository / row["path"]).read_bytes()
        need(len(data) == row["bytes"] and sha(data) == row["sha256"], "source_pin:" + row["path"])
    original_root = repository / pins["fixture_root"]
    original_matrix = json.loads((original_root / "matrix.json").read_bytes())
    additions = json.loads((generated / "matrix.json").read_bytes())
    comparison = json.loads((generated / "comparison-matrix.json").read_bytes())
    relations = json.loads((generated / "relations.json").read_bytes())
    manifest = json.loads((generated / "manifest.json").read_bytes())
    need(manifest["source_pins_sha256"] == sha((HERE / "source-pins.json").read_bytes()) and
         manifest["generator_sha256"] == sha((HERE / "generate.py").read_bytes()), "generator_manifest_binding")
    names = []
    for row in manifest["files"]:
        path = (generated / row["path"]).resolve()
        need(path.is_relative_to(generated) and row["path"] not in names, "manifest_path")
        names.append(row["path"])
        data = path.read_bytes()
        need(len(data) == row["bytes"] and sha(data) == row["sha256"], "output_manifest:" + row["path"])
    need(set(names) | {"manifest.json"} == {p.relative_to(generated).as_posix()
         for p in generated.rglob("*") if p.is_file()}, "complete_output_inventory")
    selected = [case for case in original_matrix["cases"] if case["id"] in IDS]
    need(tuple(case["id"] for case in selected) == IDS and len(original_matrix["cases"]) == 9,
         "all_originals_retained")
    need(len(additions["cases"]) == len(relations["pairs"]) == 6 and len(comparison["cases"]) == 12,
         "six_additions_twelve_comparison_cases")
    need(comparison["cases"][6:] == additions["cases"], "comparison_addition_accounting")
    expected_groups = [[old["id"], new["id"]] for old, new in zip(selected, additions["cases"])]
    need(comparison["expected_same_decoder_pcm_equal_groups"] == expected_groups, "six_exact_PCM_expectations")
    rows, controls = [], []
    for original, new, copied, relation in zip(selected, additions["cases"], comparison["cases"][:6], relations["pairs"]):
        need(all(new[key] == original[key] == copied[key] for key in INVARIANTS), "invariant_case_accounting")
        need(new["id"] == original["id"].replace("-s", "-minp1-s") and copied["id"] == original["id"] and
             relation["original_id"] == original["id"] and relation["equivalent_id"] == new["id"], "pair_identity")
        oldraw, newraw = {}, {}
        for key in ("identification", "comment", "setup", "audio", "ogg", "packet_metadata"):
            oldraw[key], newraw[key] = (original_root / original[key]).read_bytes(), (generated / new[key]).read_bytes()
            need((generated / copied[key]).read_bytes() == oldraw[key], "original_copy_unchanged:" + key)
            if key not in ("setup", "ogg"):
                need(oldraw[key] == newraw[key], "unchanged_raw:" + key)
        expected_raw_relations = [dict(kind=key, original_path=original[key],
            original_sha256=sha(oldraw[key]), equivalent_path=new[key], equivalent_sha256=sha(newraw[key]),
            expected_equal=key not in ("setup", "ogg"))
            for key in ("identification", "comment", "setup", "audio", "ogg", "packet_metadata")]
        need(relation["raw_file_relations"] == expected_raw_relations and
             relation["invariant_case_keys"] == list(INVARIANTS) and
             relation["original_matrix"] == (original_root / "matrix.json").relative_to(repository).as_posix() and
             relation["original_matrix_sha256"] == sha((original_root / "matrix.json").read_bytes()),
             "six_exact_relations_bound_to_actual_bytes")
        old_setup, new_setup, detail = setup_pair(oldraw["setup"], newraw["setup"])
        need(detail["changed_fields"] == relation["setup_field_changes"], "independent_field_change_witness")
        header = oldraw["identification"]
        need(len(header) == 30 and header[:7] == b"\x01vorbis" and header[7:11] == bytes(4) and header[11] == 2 and
             int.from_bytes(header[12:16], "little") == original["rate"] == 48000 and
             (1 << (header[28] & 15), 1 << (header[28] >> 4)) == (original["short"], original["long"]),
             "actual_identification")
        need(original["mode_flags"] == MODES and original["packet_count"] == 14, "all_fourteen_modes")
        frames = [0] + [((original["long"] if x else original["short"]) +
            (original["long"] if y else original["short"])) // 4 for x, y in zip(MODES, MODES[1:])]
        need(frames == original["expected_packet_frames"] and sum(frames) == original["expected_raw_samples"] and
             [4 * value for value in frames] == original["expected_packet_s16le_bytes"] and
             sum(frames) * 4 == original["expected_s16le_bytes"], "actual_overlap_accounting")
        offsets = original["offsets"]
        metadata = json.loads(oldraw["packet_metadata"])
        need(len(offsets) == 15 and offsets[0] == 0 and offsets[-1] == len(oldraw["audio"]) and
             all(a < b for a, b in zip(offsets, offsets[1:])) and len(metadata) == 14, "complete_audio_offsets")
        packet_rows = []
        for index, (start, end) in enumerate(zip(offsets, offsets[1:])):
            data = oldraw["audio"][start:end]
            left, right = packet_fields(data, old_setup, index), packet_fields(data, new_setup, index)
            need(left == right, "exact_packet_LSP_Q24_equality")
            declared = metadata[index]
            need((declared["index"], declared["offset"], declared["bytes"], declared["used_bits"], declared["mode"],
                 declared["expected_frames"], declared["expected_s16le_bytes"]) ==
                 (index, start, end - start, left["used_bits"], MODES[index], frames[index], frames[index] * 4),
                 "independent_packet_metadata")
            for actual, expected in zip(left["floors"], declared["floors"]):
                need({key: actual[key] for key in expected} == expected, "independent_original_LSP_metadata")
            need(left["residue_first16"] == declared["residue_first16"], "independent_residue_wire_metadata")
            packet_rows.append(dict(packet=index, channels=left["floors"], actual_used_bits=left["used_bits"]))
        old_pages, new_pages = pages(oldraw["ogg"]), pages(newraw["ogg"])
        raw_packets = [oldraw[k] for k in ("identification", "comment", "setup")] + [
            oldraw["audio"][a:b] for a, b in zip(offsets, offsets[1:])]
        need([p["packet"] for p in old_pages] == raw_packets, "original_carrier_raw_binding")
        total = 0
        for index, (left, right) in enumerate(zip(old_pages, new_pages)):
            need((left["offset"], left["bytes"], left["flags"], left["granule"], left["serial"]) ==
                 (right["offset"], right["bytes"], right["flags"], right["granule"], right["serial"]),
                 "all_carrier_metadata_unchanged")
            need(left["flags"] == (2 if index == 0 else 4 if index == 16 else 0), "carrier_BOS_EOS")
            if index >= 3:
                total += frames[index - 3]
            need(left["granule"] == total, "carrier_granule")
            if index == 2:
                need(right["packet"] == newraw["setup"] and left["header"][:22] + left["header"][26:] ==
                     right["header"][:22] + right["header"][26:], "only_setup_payload_CRC_changes")
            else:
                need(left["page"] == right["page"], "non_setup_page_unchanged")
        if not controls:
            field = new_setup["fields"]["book[2].minimum"]
            controls.append(require_rejected("wrong-minimum", oldraw["setup"], newraw["setup"], field, 0,
                                             "equivalent_minimum"))
            field = new_setup["fields"]["book[2].delta"]
            controls.append(require_rejected("wrong-delta", oldraw["setup"], newraw["setup"], field, 0x62200001,
                                             "equivalent_delta"))
            field = new_setup["fields"]["book[2].multiplicand[0]"]
            controls.append(require_rejected("wrong-multiplicand", oldraw["setup"], newraw["setup"], field,
                                             field["value"] + 1, "multiplicand_shift"))
        rows.append(dict(original_id=original["id"], equivalent_id=new["id"], setup=detail,
            packets=packet_rows, unchanged_audio_sha256=sha(oldraw["audio"]),
            exact_headers_audio_packet_metadata=True, only_setup_payload_CRC_changed=True))
    for row in pins["local_inputs"]:
        need(sha((repository / row["path"]).read_bytes()) == row["sha256"], "source_changed_during_witness")
    return dict(schema="floor0-equivalent-raw-Q24-witness-v1", result="CONSTRUCTION_EQUIVALENCE_WITNESSED",
        generated_matrix_sha256=sha((generated / "matrix.json").read_bytes()),
        generated_manifest_sha256=sha((generated / "manifest.json").read_bytes()),
        source_pins_sha256=sha((HERE / "source-pins.json").read_bytes()),
        witness_sha256=sha(Path(__file__).read_bytes()), pairs=rows, negative_controls=controls,
        actual_decoder_or_reference_run=False, actual_PCM_equality_observed=False,
        floor_curve_residue_synthesis_computed=False, numeric_qualified=False, full_G6_qualified=False,
        original_campaigns_reclassified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--generated", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    repository, generated, output = args.repository.resolve(), args.generated.resolve(), args.output.resolve()
    need(generated.is_relative_to(repository / ".build") and generated.is_dir(), "generated_root")
    need(output.is_relative_to(repository / ".build") and not output.exists() and
         not output.is_relative_to(HERE) and not output.is_relative_to(generated), "fresh_independent_witness_output")
    result = witness(repository, generated)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write((json.dumps(result, indent=2) + "\n").encode())
    print(json.dumps(dict(result=result["result"], pairs=len(result["pairs"]),
        controls=len(result["negative_controls"]), actual_PCM_equality_observed=False)))


if __name__ == "__main__":
    main()
