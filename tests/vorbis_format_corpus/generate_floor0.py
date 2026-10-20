"""Construct complete floor0/residue0 packets; no codec or synthesis execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SUPPORT_SHA = "8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1"
support_path = ROOT / "tests/vorbis_block_matrix/generate_minimal.py"
if hashlib.sha256(support_path.read_bytes()).hexdigest() != SUPPORT_SHA:
    raise ValueError("Pinned canonical minimal helper changed")
spec = importlib.util.spec_from_file_location("vorbis_format_floor0_minimal", support_path)
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)  # Definitions only; its guarded main is not called.
RATE, CHANNELS = 48000, 2
PAIRS = ((64, 256), (256, 2048), (64, 2048))
VARIANTS = {
    "floor1-r0": dict(floor=1, order=0, ampbits=0, barkmap=0, books=[]),
    "floor0-even6-r0": dict(floor=0, order=6, ampbits=6, barkmap=64,
                           books=[[[7, 14, 21], [8, 15, 22]]]),
    "floor0-odd5-r0": dict(floor=0, order=5, ampbits=8, barkmap=128,
                          books=[[[8, 16, 24], [9, 17, 25]],
                                 [[7, 15, 23], [8, 16, 24]]]),
}


def put_book(b, number, dim, entries, length, maptype, minimum=0, delta=0, values=()):
    p = f"book[{number}]"
    for key, width, value in (("sync", 24, 0x564342), ("dimensions", 16, dim),
                              ("entries", 24, entries), ("ordered", 1, 0), ("sparse", 1, 0)):
        b.put(p + "." + key, width, value)
    for i in range(entries):
        b.put(p + f".length_minus_1[{i}]", 5, length - 1)
    b.put(p + ".maptype", 4, maptype)
    if maptype:
        b.put(p + ".minimum", 32, minimum)
        b.put(p + ".delta", 32, delta)
        value_bits = max(values).bit_length() or 1
        b.put(p + ".value_bits_minus_1", 4, value_bits - 1)
        b.put(p + ".sequence_p", 1, 0)
        for i, value in enumerate(values):
            b.put(p + f".multiplicand[{i}]", value_bits, value)


def setup(v):
    b = S.Bits()
    S.prefix(b, 5)
    b.put("books_minus_1", 8, 1 + len(v["books"]))
    put_book(b, 0, 1, 1, 1, 0)  # Scalar classification; one zero bit.
    put_book(b, 1, 2, 4, 2, 1, S.packed_float(-1), S.packed_float(2), (0, 1))
    for i, vectors in enumerate(v["books"], 2):
        put_book(b, i, 3, 2, 1, 2, 0, (784 << 21) | 1,
                 [value for vector in vectors for value in vector])
    for key, width, value in (("times_minus_1", 6, 0), ("time.type", 16, 0),
                              ("floors_minus_1", 6, 0), ("floor.type", 16, v["floor"])):
        b.put(key, width, value)
    if v["floor"] == 0:
        for key, width, value in (("order", 8, v["order"]), ("rate", 16, RATE),
                ("barkmap", 16, v["barkmap"]), ("amplitude_bits", 6, v["ampbits"]),
                ("amplitude_offset", 8, 60), ("books_minus_1", 4, len(v["books"]) - 1)):
            b.put("floor0." + key, width, value)
        for i in range(len(v["books"])):
            b.put(f"floor0.book[{i}]", 8, i + 2)
    else:
        b.put("floor1.partitions", 5, 0)
        b.put("floor1.multiplier_minus_1", 2, 0)
        b.put("floor1.rangebits", 4, 4)
    for key, width, value in (("residues_minus_1", 6, 0), ("residue.type", 16, 0),
            ("residue.begin", 24, 0), ("residue.end", 24, 16),
            ("residue.partition_size_minus_1", 24, 15), ("residue.classifications_minus_1", 6, 0),
            ("residue.classbook", 8, 0), ("residue.cascade_low", 3, 1),
            ("residue.cascade_high_present", 1, 0), ("residue.stagebook", 8, 1),
            ("mappings_minus_1", 6, 0), ("mapping.type", 16, 0),
            ("mapping.submaps_flag", 1, 0), ("mapping.coupling_flag", 1, 0),
            ("mapping.reserved", 2, 0), ("mapping.time", 8, 0),
            ("mapping.floor", 8, 0), ("mapping.residue", 8, 0), ("modes_minus_1", 6, 1)):
        b.put(key, width, value)
    for mode in range(2):
        b.put(f"mode[{mode}].blockflag", 1, mode)
        b.put(f"mode[{mode}].windowtype", 16, 0)
        b.put(f"mode[{mode}].transformtype", 16, 0)
        b.put(f"mode[{mode}].mapping", 8, 0)
    b.put("framing", 1, 1)
    return b


def lsp_values(v, selected, words):
    result, last = [], 0
    for word in words:
        vector = [x + last for x in v["books"][selected][word]]
        result.extend(vector)
        last = vector[-1]
    used = result[:v["order"]]
    assert all(x > 0 for x in used) and used[-1] < 3 * 16
    assert min(b - a for a, b in zip(used, used[1:])) >= 7
    return used, result[v["order"]:]


def reverse2(value):
    return ((value & 1) << 1) | (value >> 1)


def audio(v, packet):
    b = S.Bits()
    mode = S.MODES[packet]
    b.put("audio.type", 1, 0)
    b.put("audio.mode", 1, mode)
    if mode:
        b.put("audio.previous_window", 1, S.MODES[packet - 1])
        b.put("audio.next_window", 1, S.MODES[packet + 1])
    floors = []
    for channel in range(CHANNELS):
        if v["floor"] == 1:
            b.put(f"floor[{channel}].present", 1, 1)
            b.put(f"floor[{channel}].y0", 8, 255)
            b.put(f"floor[{channel}].y1", 8, 255)
            floors.append(dict(y0=255, y1=255))
        else:
            amplitude = (44 + (packet * 3 + channel * 5) % 12) if v["ampbits"] == 6 else (176 + (packet * 3 + channel * 5) % 32)
            selected = (packet // 2 + channel) % len(v["books"])
            words = [((packet >> i) ^ channel) & 1 for i in range(2)]
            b.put(f"floor[{channel}].amplitude", v["ampbits"], amplitude)
            # ilog(numbooks), not ilog(numbooks - 1), per spec and Xiph.
            b.put(f"floor[{channel}].book_selector", len(v["books"]).bit_length(), selected)
            for i, word in enumerate(words):
                b.put(f"floor[{channel}].vq_word[{i}]", 1, word)
            used, ignored = lsp_values(v, selected, words)
            floors.append(dict(amplitude_raw=amplitude, book_selector=selected, vq_words=words,
                               lsp_used_units_1_16=used, lsp_ignored_units_1_16=ignored))
    for channel in range(CHANNELS):
        b.put(f"classword[{channel}]", 1, 0)
    residue = []
    for channel in range(CHANNELS):
        vector = [2 * S.sign_code(packet, channel, i) - 1 for i in range(16)]
        assert -1 in vector and 1 in vector
        for i in range(8):
            entry = ((vector[i] + 1) // 2) | (((vector[i + 8] + 1) // 2) << 1)
            # Canonical Huffman words are MSB-first; Bits.put writes LSB-first.
            b.put(f"residue[{channel}].vq_word[{i}]", 2, reverse2(entry))
        residue.append(vector)
    return b, dict(floors=floors, residue_first16=residue)


def syntax_roundtrip(v, b, expected):
    data, position = int.from_bytes(b.data(), "little"), 0
    def get(width):
        nonlocal position
        assert position + width <= len(b.bits)
        result = (data >> position) & ((1 << width) - 1)
        position += width
        return result
    assert get(1) == 0
    mode = get(1)
    if mode:
        get(1); get(1)
    floors = []
    for channel in range(CHANNELS):
        if v["floor"] == 1:
            assert get(1) == 1
            floors.append(dict(y0=get(8), y1=get(8)))
        else:
            amplitude, selected = get(v["ampbits"]), get(len(v["books"]).bit_length())
            assert amplitude > 0 and selected < len(v["books"])
            words = [get(1), get(1)]
            used, ignored = lsp_values(v, selected, words)
            floors.append(dict(amplitude_raw=amplitude, book_selector=selected, vq_words=words,
                               lsp_used_units_1_16=used, lsp_ignored_units_1_16=ignored))
    assert get(1) == get(1) == 0
    residue = []
    for channel in range(CHANNELS):
        vector = [0] * 16
        for i in range(8):
            entry = reverse2(get(2))
            vector[i], vector[i + 8] = 2 * (entry & 1) - 1, 2 * (entry >> 1) - 1
        residue.append(vector)
    assert dict(floors=floors, residue_first16=residue) == expected
    assert position == len(b.bits) and data >> position == 0


def generate(output):
    output = output.resolve()
    build_root = ROOT / ".build"
    if output == build_root or not output.is_relative_to(build_root) or output.exists():
        raise ValueError("Fresh output beneath this checkout's .build required")
    assert S.unpack_float((784 << 21) | 1) == S.Fraction(1, 16)
    comment = S.comment()
    payloads, cases, fields = {}, [], dict(comment=comment.report(), variants={}, identifications={})
    for name, v in VARIANTS.items():
        sb = setup(v)
        audio_packets = [audio(v, i) for i in range(len(S.MODES))]
        offsets = [0]
        for b, expected in audio_packets:
            offsets.append(offsets[-1] + len(b.data()))
        fields["variants"][name] = dict(configuration=v, setup=sb.report(),
                audio=[b.report() for b, expected in audio_packets])
        for short, long in PAIRS:
            case_id = f"{name}-s{short}-l{long}"
            directory = f"cases/{case_id}"
            ib = S.identification(short.bit_length() - 1, long.bit_length() - 1, RATE)
            fields["identifications"][f"s{short}-l{long}"] = ib.report()
            blocks = [long if mode else short for mode in S.MODES]
            frames = [0] + [(a + b) // 4 for a, b in zip(blocks, blocks[1:])]
            granules, total = [], 0
            for size in frames:
                total += size
                granules.append(total)
            raw = [ib.data(), comment.data(), sb.data()] + [b.data() for b, expected in audio_packets]
            gp = [0, 0, 0] + granules
            serial = 0x46300000 + len(cases) + 1
            ogg = b"".join(S.page(p, serial, i, gp[i], 2 if i == 0 else 4 if i == len(raw) - 1 else 0)
                           for i, p in enumerate(raw))
            pages = S.read_pages(ogg)
            assert [p["packet"] for p in pages] == raw and [p["granule"] for p in pages] == gp
            data = {"identification.bin": ib.data(), "comment.bin": comment.data(),
                    "setup.bin": sb.data(), "audio.bin": b"".join(raw[3:]), "reference.ogg": ogg}
            packet_info = []
            for i, (b, expected) in enumerate(audio_packets):
                syntax_roundtrip(v, b, expected)
                packet_info.append(dict(index=i, offset=offsets[i], bytes=len(b.data()),
                    used_bits=len(b.bits), mode=S.MODES[i], expected_frames=frames[i],
                    expected_s16le_bytes=frames[i] * 4, **expected))
            data["packets.json"] = (json.dumps(packet_info, indent=2) + "\n").encode()
            for filename, content in data.items():
                payloads[f"{directory}/{filename}"] = content
            features = ["complete-packets", "stereo", "residue0", "residue0-dim2-step8",
                        "short-long-transitions", "all-long-neighbor-flags", "nonzero-amplitude"]
            features += ["floor1-control"] if v["floor"] else [f"floor0-order{v['order']}",
                        "lsp-increasing-dyadic", "lsp-multivector-accumulation",
                        "single-floor-book" if len(v["books"]) == 1 else "two-floor-books-selector2bits"]
            if v["order"] == 5:
                features.append("extra-final-lsp-scalar-ignored")
            cases.append(dict(id=case_id, variant=name, features=features, short=short, long=long,
                rate=RATE, channels=2, bits=16, mode_flags=list(S.MODES), offsets=offsets,
                identification=f"{directory}/identification.bin", setup=f"{directory}/setup.bin",
                comment=f"{directory}/comment.bin", audio=f"{directory}/audio.bin", ogg=f"{directory}/reference.ogg",
                packet_metadata=f"{directory}/packets.json", expected_packet_frames=frames,
                expected_packet_s16le_bytes=[n * 4 for n in frames], expected_raw_samples=total,
                expected_s16le_bytes=total * 4, packet_granules=granules, packet_count=len(S.MODES),
                public_decode_output_capacity=16384, independent_decode_status="PENDING"))
    assert len(cases) == 9
    damaged = bytearray(payloads[cases[0]["ogg"]]); damaged[-1] ^= 1
    try:
        S.read_pages(damaged)
    except ValueError as error:
        assert str(error) == "CRC mismatch"
    else:
        raise AssertionError("Corrupted CRC control accepted")
    checks = dict(scope="Pure construction/bit-syntax roundtrip only; no curve, IMDCT or PCM synthesis",
        cases=9, packets_per_case=14, syntax_roundtrip_packets=126,
        residue_type=0, residue_partition=16, residue_vq_dimension=2, residue_interleave_step=8,
        residue_vectors=[[-1, -1], [1, -1], [-1, 1], [1, 1]],
        lsp_delta=dict(packed_hex="62000001", exact="1/16"), lsp_minimum_gap="7/16 radians",
        used_lsp_range="0 < LSP < 3 < pi", actual_nonzero_pcm_observed=False,
        independent_decode_run=False, crc_tamper_rejected=True)
    for name, value in (("matrix.json", dict(schema="vorbis-floor0-residue0-candidates-v1", cases=cases,
                validity_qualified=False, actual_nonzero_pcm_observed=False)),
                ("construction-fields.json", fields), ("pure-checks.json", checks)):
        payloads[name] = (json.dumps(value, indent=2) + "\n").encode()
    manifest = dict(schema="vorbis-floor0-construction-manifest-v1", generator_sha256=S.sha(Path(__file__).read_bytes()),
        support_sha256=SUPPORT_SHA, source_references_sha256=S.sha((HERE / "source_references.json").read_bytes()),
        codec_execution=False, validity_qualified=False,
        files=[dict(path=p, bytes=len(d), sha256=S.sha(d)) for p, d in sorted(payloads.items())])
    payloads["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    for name, content in payloads.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(content)
    print(json.dumps(dict(output=str(output), cases=9, files=len(payloads),
                          manifest_sha256=S.sha(payloads["manifest.json"]), independent_decode_pending=True)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".build/vorbis-floor0-corpus-01")
    generate(parser.parse_args().output)
