"""Construct 18 advertised mono/stereo rate cases plus three mapping supplements.

Only stdlib field/packet accounting is executed; no audio decoder is invoked.
"""
from collections import Counter
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / "tests/vorbis_block_matrix/generate_minimal.py"
BASE_SHA = "8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1"
SETUP_SOURCE = ROOT / "idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c"
SETUP_SHA = "d23fd5cb2ad7d8c3a87ebcda2197421245f571dea5724de3d328058264e491c2"
RATES = (8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000)
SHORT, LONG, RANGEBITS = 256, 2048, 10
SPEC = "https://xiph.org/vorbis/doc/Vorbis_I_spec.html"
REFERENCES = [SPEC, "https://xiph.org/ogg/doc/framing.html",
    "https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/mapping0.c",
    "https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/res0.c",
    "https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/sharedbook.c",
    "https://github.com/espressif/esp-adf-libs/blob/master/esp_audio_codec/README.md"]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


need(sha(BASE.read_bytes()) == BASE_SHA, "canonical_helper_pin")
spec = importlib.util.spec_from_file_location("pinned_minimal_construction", BASE)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
MODES = base.MODES


def plan(variant, channels):
    need(channels in (1, 2), "mono_or_stereo_only")
    need(variant in ("uncoupled", "coupled", "submaps", "residue2"), "variant")
    need(variant == "uncoupled" or channels == 2, "supplement_is_stereo")
    if variant == "submaps":
        return dict(residues=[(1, 16), (1, 32)], mux=[1, 0], coupling=False, values=[-1, 1])
    return dict(residues=[(2, 32) if variant == "residue2" else (1, 16)],
                mux=[0] * channels, coupling=variant == "coupled",
                values=[-2, -1, 1, 2] if variant == "coupled" else [-1, 1])


def identification(rate, channels):
    need(rate in RATES, "advertised_rate")
    need(channels in (1, 2), "mono_or_stereo_only")
    b = base.Bits(); base.prefix(b, 1)
    for name, width, value in (("version", 32, 0), ("channels", 8, channels),
        ("sample_rate", 32, rate), ("bitrate_maximum", 32, 0),
        ("bitrate_nominal", 32, 0), ("bitrate_minimum", 32, 0),
        ("short_exponent", 4, 8), ("long_exponent", 4, 11), ("framing", 1, 1)):
        b.put(name, width, value)
    return b


def coupling_book(b):
    # Complete four-leaf scalar tree; map1 vectors -2,-1,+1,+2.
    for name, width, value in (("sync", 24, 0x564342), ("dimensions", 16, 1),
        ("entries", 24, 4), ("ordered", 1, 0), ("sparse", 1, 0)):
        b.put("book[1]." + name, width, value)
    for i in range(4):
        b.put(f"book[1].length_minus_1[{i}]", 5, 1)
    for name, width, value in (("lookup_type", 4, 1), ("minimum", 32, base.packed_float(-2)),
        ("delta", 32, base.packed_float(1)), ("value_bits_minus_1", 4, 2), ("sequence_p", 1, 0)):
        b.put("book[1]." + name, width, value)
    for i, value in enumerate((0, 1, 3, 4)):
        b.put(f"book[1].multiplicand[{i}]", 3, value)


def setup(variant, channels):
    p = plan(variant, channels); b = base.Bits(); base.prefix(b, 5)
    b.put("codebooks_minus_1", 8, 1)
    base.book(b, 0, 1, False)
    if p["coupling"]:
        coupling_book(b)
    else:
        base.book(b, 1, 2, True)
    for name, width, value in (("time_count_minus_1", 6, 0), ("time[0].type", 16, 0),
        ("floor_count_minus_1", 6, 0), ("floor[0].type", 16, 1),
        ("floor[0].partitions", 5, 0), ("floor[0].multiplier_minus_1", 2, 0),
        ("floor[0].rangebits", 4, RANGEBITS), ("residue_count_minus_1", 6, len(p["residues"]) - 1)):
        b.put(name, width, value)
    for index, (kind, span) in enumerate(p["residues"]):
        for name, width, value in (("type", 16, kind), ("begin", 24, 0), ("end", 24, span),
            ("partition_size_minus_1", 24, span - 1), ("classifications_minus_1", 6, 0),
            ("classbook", 8, 0), ("cascade_low", 3, 1), ("cascade_high_present", 1, 0),
            ("stagebook[0][0]", 8, 1)):
            b.put(f"residue[{index}]." + name, width, value)
    b.put("mapping_count_minus_1", 6, 0); b.put("mapping[0].type", 16, 0)
    b.put("mapping[0].multiple_submaps", 1, int(len(p["residues"]) > 1))
    if len(p["residues"]) > 1:
        b.put("mapping[0].submaps_minus_1", 4, len(p["residues"]) - 1)
    b.put("mapping[0].coupling", 1, int(p["coupling"]))
    if p["coupling"]:
        b.put("mapping[0].coupling_steps_minus_1", 8, 0)
        b.put("mapping[0].magnitude[0]", (channels - 1).bit_length(), 0)
        b.put("mapping[0].angle[0]", (channels - 1).bit_length(), 1)
    b.put("mapping[0].reserved", 2, 0)
    if len(p["residues"]) > 1:
        for channel, mux in enumerate(p["mux"]):
            b.put(f"mapping[0].mux[{channel}]", 4, mux)
    for submap in range(len(p["residues"])):
        for name, value in (("time", 0), ("floor", 0), ("residue", submap)):
            b.put(f"mapping[0].submap[{submap}]." + name, 8, value)
    b.put("modes_minus_1", 6, 1)
    for mode in range(2):
        for name, width, value in (("blockflag", 1, mode), ("windowtype", 16, 0),
            ("transformtype", 16, 0), ("mapping", 8, 0)):
            b.put(f"mode[{mode}]." + name, width, value)
    b.put("framing", 1, 1)
    return b


def symbol(packet, channel, scalar, coupled):
    bit = ((scalar >> (1 - channel)) & 1) if coupled and scalar < 4 else base.sign_code(packet, channel, scalar)
    return (0 if not bit else 3) if coupled and channel == 0 else (1 if not bit else 2) if coupled else bit


def wire_symbol(index, coupled):
    return ((index & 1) << 1) | (index >> 1) if coupled else index


def audio(packet, variant, channels):
    p = plan(variant, channels); b = base.Bits(); mode = MODES[packet]
    b.put("audio_packet_type", 1, 0); b.put("mode", 1, mode)
    if mode:
        b.put("previous_window_flag", 1, MODES[packet - 1] if packet else 0)
        b.put("next_window_flag", 1, MODES[packet + 1] if packet + 1 < len(MODES) else 0)
    # Floors are ALWAYS in channel order, all before residues.
    for channel in range(channels):
        for name, width, value in (("present", 1, 1), ("y0", 8, 255), ("y1", 8, 255)):
            b.put(f"floor[{channel}]." + name, width, value)
    # Residues are in submap order; each r1 bundle's classwords precede vectors.
    for submap, (kind, span) in enumerate(p["residues"]):
        bundle = [c for c in range(channels) if p["mux"][c] == submap]
        for local in range(1 if kind == 2 else len(bundle)):
            b.put(f"submap[{submap}].classword[{local}]", 1, 0)
        positions = [(bundle[i % len(bundle)], i // len(bundle)) for i in range(span)] if kind == 2 else [
            (channel, scalar) for channel in bundle for scalar in range(span)]
        for channel, scalar in positions:
            index = symbol(packet, channel, scalar, p["coupling"])
            b.put(f"submap[{submap}].residue[{channel}][{scalar}]", 2 if p["coupling"] else 1,
                  wire_symbol(index, p["coupling"]))
    return b


class Reader:
    def __init__(self, data):
        self.data, self.offset = data, 0

    def take(self, width):
        need(self.offset + width <= len(self.data) * 8, "complete_packet_fields")
        value = (int.from_bytes(self.data, "little") >> self.offset) & ((1 << width) - 1)
        self.offset += width
        return value

    def exact(self, width, value, reason):
        need(self.take(width) == value, reason)

    def finish(self):
        need(len(self.data) == (self.offset + 7) // 8, "exact_packet_byte_count")
        need(int.from_bytes(self.data, "little") >> self.offset == 0, "zero_padding")


def inspect_setup(data, variant, channels):
    # Independent actual-byte extraction for this deliberately small grammar.
    r = Reader(data); p = plan(variant, channels)
    r.exact(56, int.from_bytes(b"\x05vorbis", "little"), "setup_prefix"); r.exact(8, 1, "book_count")
    for index in range(2):
        r.exact(24, 0x564342, "book_sync"); r.exact(16, 1, "book_dimension")
        entries = 1 if index == 0 else 4 if p["coupling"] else 2
        r.exact(24, entries, "book_entries"); r.exact(1, 0, "book_ordered"); r.exact(1, 0, "book_sparse")
        for _ in range(entries):
            r.exact(5, int(index == 1 and p["coupling"]), "book_length")
        r.exact(4, int(index == 1), "book_map")
        if index == 1:
            minimum, delta = (-2, 1) if p["coupling"] else (-1, 2)
            need(base.unpack_float(r.take(32)) == minimum and base.unpack_float(r.take(32)) == delta, "book_quantization")
            width = r.take(4) + 1; need(width == (3 if p["coupling"] else 1), "book_quant_bits")
            r.exact(1, 0, "book_sequence")
            values = [minimum + delta * r.take(width) for _ in range(entries)]
            need(values == p["values"], "book_values")
    for width, value, reason in ((6, 0, "time_count"), (16, 0, "time_type"), (6, 0, "floor_count"),
        (16, 1, "floor_type"), (5, 0, "floor_partitions"), (2, 0, "floor_multiplier"),
        (4, 10, "floor_endpoint"), (6, len(p["residues"]) - 1, "residue_count")):
        r.exact(width, value, reason)
    for kind, span in p["residues"]:
        for width, value in ((16, kind), (24, 0), (24, span), (24, span - 1), (6, 0), (8, 0), (3, 1), (1, 0), (8, 1)):
            r.exact(width, value, "residue_setup")
    r.exact(6, 0, "map_count"); r.exact(16, 0, "map_type")
    multi = r.take(1); need(multi == int(len(p["residues"]) > 1), "submap_flag")
    if multi: r.exact(4, 1, "submap_count")
    r.exact(1, int(p["coupling"]), "coupling_flag")
    if p["coupling"]:
        r.exact(8, 0, "coupling_steps"); r.exact(1, 0, "magnitude_channel"); r.exact(1, 1, "angle_channel")
    r.exact(2, 0, "reserved_mapping")
    if multi:
        for mux in p["mux"]: r.exact(4, mux, "channel_mux")
    for submap in range(len(p["residues"])):
        r.exact(8, 0, "submap_time"); r.exact(8, 0, "submap_floor"); r.exact(8, submap, "submap_residue")
    r.exact(6, 1, "mode_count")
    for mode in range(2):
        r.exact(1, mode, "block_flag"); r.exact(16, 0, "window"); r.exact(16, 0, "transform"); r.exact(8, 0, "mode_map")
    r.exact(1, 1, "setup_framing"); r.finish()


def inspect_packet(data, packet, variant, channels):
    r = Reader(data); p = plan(variant, channels); mode = MODES[packet]
    r.exact(1, 0, "packet_type"); r.exact(1, mode, "packet_mode")
    if mode:
        r.exact(1, MODES[packet - 1], "previous_window"); r.exact(1, MODES[packet + 1], "next_window")
    for _ in range(channels):
        r.exact(1, 1, "floor_present"); r.exact(8, 255, "floor_endpoint_y"); r.exact(8, 255, "floor_endpoint_y")
    vectors = [[0] * 32 for _ in range(channels)]
    for submap, (kind, span) in enumerate(p["residues"]):
        bundle = [c for c in range(channels) if p["mux"][c] == submap]
        for _ in range(1 if kind == 2 else len(bundle)): r.exact(1, 0, "classword")
        for local in range(span * (1 if kind == 2 else len(bundle))):
            if kind == 2:
                channel, scalar = bundle[local % len(bundle)], local // len(bundle)
            else:
                channel, scalar = bundle[local // span], local % span
            code = r.take(2 if p["coupling"] else 1)
            index = ((code & 1) << 1) | (code >> 1) if p["coupling"] else code
            need(index == symbol(packet, channel, scalar, p["coupling"]), "spectral_values")
            vectors[channel][scalar] = p["values"][index]
    r.finish()
    if p["coupling"]:
        quadrants = set()
        for scalar, (mag, angle) in enumerate(zip(*vectors)):
            if scalar < 16:
                quadrants.add((mag > 0, angle > 0))
            if mag > 0:
                left, right = (mag, mag - angle) if angle > 0 else (mag + angle, mag)
            else:
                left, right = (mag, mag + angle) if angle > 0 else (mag - angle, mag)
            vectors[0][scalar], vectors[1][scalar] = left, right
        need(len(quadrants) == 4, "all_coupling_quadrants")
    need(all(any(v) and min(v) < 0 < max(v) and max(map(abs, v)) <= 2 for v in vectors), "bounded_mixed_nonzero_spectra")
    need(channels == 1 or vectors[0] != vectors[1], "distinct_channel_spectra")
    return dict(used_bits=r.offset, byte_count=len(data), spectrum_integer_model=vectors,
                spectrum_nonzero_bins=[sum(x != 0 for x in v) for v in vectors], actual_PCM_observed=False)


def negatives():
    result = []
    def reject(name, action, reason):
        try: action()
        except ValueError as error:
            need(str(error) == reason, "wrong_control_oracle:" + name + ":" + str(error))
        else: raise ValueError("accepted_control:" + name)
        result.append(dict(name=name, exact_reason=reason, rejected=True))
    reject("stereo_audio_cannot_be_relabelled_mono", lambda: inspect_packet(audio(0, "uncoupled", 2).data(), 0, "uncoupled", 1), "classword")
    reject("mono_audio_cannot_be_relabelled_stereo", lambda: inspect_packet(audio(0, "uncoupled", 1).data(), 0, "uncoupled", 2), "floor_present")
    b = audio(0, "submaps", 2); start = 2 + 17 * 2
    changed = base.Bits(); changed.bits = b.bits[:start] + b.bits[start + 17:] + b.bits[start:start + 17]
    reject("residue_channel_order_instead_of_submap_order", lambda: inspect_packet(changed.data(), 0, "submaps", 2), "spectral_values")
    b = audio(0, "residue2", 2); changed = base.Bits(); changed.bits = b.bits[:start + 1] + [0] + b.bits[start + 1:]
    reject("residue2_per_channel_extra_classword", lambda: inspect_packet(changed.data(), 0, "residue2", 2), "spectral_values")
    b = audio(0, "coupled", 2); changed = bytearray(b.data()); changed[5] ^= 1
    reject("coupled_vq_code_corruption", lambda: inspect_packet(bytes(changed), 0, "coupled", 2), "spectral_values")
    damaged = bytearray(base.page(b.data(), 1, 0, 0, 2)); damaged[-1] ^= 1
    reject("ogg_crc_corruption", lambda: base.read_pages(damaged), "CRC mismatch")
    return result


def fact(path):
    raw = path.read_bytes()
    return dict(path=str(path), bytes=len(raw), sha256=sha(raw))


def generate(output):
    output = output.resolve()
    need(output.parent == HERE and not output.exists(), "fresh_direct_child_output")
    need(sha(SETUP_SOURCE.read_bytes()) == SETUP_SHA, "audited_setup_source_pin")
    inputs = [Path(__file__).resolve(), BASE, SETUP_SOURCE, HERE / "README.md"]
    before = [fact(path) for path in inputs]
    need(base.CHANNELS == 2 and base.unpack_float(base.packed_float(-2)) == -2, "helper_unmodified_contract")
    transitions = Counter(zip(MODES, MODES[1:])); neighbors = Counter((MODES[i - 1], MODES[i + 1]) for i in range(1, 13) if MODES[i])
    need(set(transitions) == set(neighbors) == {(0, 0), (0, 1), (1, 0), (1, 1)}, "transition_neighbor_matrix")
    frames = [0] + [((LONG if a else SHORT) + (LONG if b else SHORT)) // 4 for a, b in zip(MODES, MODES[1:])]
    cumulative = []; total = 0
    for count in frames: total += count; cumulative.append(total)
    construction = dict(scope="pure field/symbol accounting; not a codec/reference", shapes={}, identification={})
    payloads, cases = {}, []
    requests = [("uncoupled", c, rate) for rate in RATES for c in (1, 2)] + [(v, 2, 48000) for v in ("coupled", "submaps", "residue2")]
    for variant, channels, rate in requests:
        caseid = f"{variant}-c{channels}-r{rate}"; folder = f"cases/{caseid}/"
        ib, sb, cb = identification(rate, channels), setup(variant, channels), base.comment()
        packets = [audio(i, variant, channels) for i in range(14)]
        inspect_setup(sb.data(), variant, channels)
        need(len(ib.data()) == 30 and ib.data()[11] == channels and int.from_bytes(ib.data()[12:16], "little") == rate and ib.data()[28] == 0xb8, "identification_actual_bytes")
        shape = f"{variant}-c{channels}"
        if shape not in construction["shapes"]:
            construction["shapes"][shape] = dict(setup=sb.report(), audio=[dict(bitfields=b.report(), **inspect_packet(b.data(), i, variant, channels)) for i, b in enumerate(packets)])
        else:
            for i, packet in enumerate(packets): inspect_packet(packet.data(), i, variant, channels)
        construction["identification"][caseid] = ib.report()
        offsets = [0]
        for packet in packets: offsets.append(offsets[-1] + len(packet.data()))
        raw = dict(identification=ib.data(), setup=sb.data(), comment=cb.data(), audio=b"".join(p.data() for p in packets))
        serial = 0x4d4d0000 + len(cases) + 1
        all_packets = [raw["identification"], raw["comment"], raw["setup"]] + [p.data() for p in packets]
        granules = [0, 0, 0] + cumulative; flags = [2] + [0] * 15 + [4]
        carrier = b"".join(base.page(p, serial, i, granules[i], flags[i]) for i, p in enumerate(all_packets))
        pages = base.read_pages(carrier)
        need([p["packet"] for p in pages] == all_packets and [p["granule"] for p in pages] == granules and [p["flags"] for p in pages] == flags, "carrier_roundtrip")
        for kind, value in raw.items(): payloads[folder + kind + ".bin"] = value
        payloads[folder + "reference.ogg"] = carrier
        pcm = [count * channels * 2 for count in frames]
        p = plan(variant, channels)
        cases.append(dict(id=caseid, identification=folder + "identification.bin", setup=folder + "setup.bin", audio=folder + "audio.bin", comment=folder + "comment.bin", ogg=folder + "reference.ogg",
            rate=rate, channels=channels, short=SHORT, long=LONG, mode_flags=list(MODES), offsets=offsets,
            packet_count=14, expected_packet_frames=frames, expected_packet_samples=frames,
            expected_packet_s16le_bytes=pcm, expected_raw_samples=total, expected_s16le_bytes=sum(pcm),
            packet_granules=cumulative, long_window_flags=[None if not mode else dict(previous=MODES[i - 1], next=MODES[i + 1]) for i, mode in enumerate(MODES)],
            features=["floor1_rangebits10", "mono" if channels == 1 else "stereo", variant],
            construction_shape=shape, residue_type_spans=p["residues"], mux=p["mux"], coupling=p["coupling"],
            raw_sha256={k: sha(v) for k, v in raw.items()}, ogg_sha256=sha(carrier),
            page_crc32=[p["crc"] for p in pages], independent_decode_pending=True))
    controls = negatives()
    need(len(cases) == 21 and [(c["rate"], c["channels"]) for c in cases[:18]] == [(r, c) for r in RATES for c in (1, 2)], "exact_18_plus_3_cases")
    need([fact(path) for path in inputs] == before, "unchanged_input_identities")
    matrix = dict(schema="vorbis-mono-mapping-matrix-v1", status="CONSTRUCTION_CHECKED_REFERENCE_PENDING", base_cases=18, mapping_supplements=3,
        packet_count=14, total_packets=294, expected_total_s16le_bytes=sum(c["expected_s16le_bytes"] for c in cases), cases=cases,
        references=REFERENCES, transitions={str(k): v for k, v in sorted(transitions.items())}, long_neighbors={str(k): v for k, v in sorted(neighbors.items())},
        independent_reference_run=False, nonzero_PCM_observed=False, target_run=False, physical_audio_run=False)
    checks = dict(schema="vorbis-mono-mapping-pure-checks-v1", completed=True, cases=21, base_cases=18, supplements=3, packets=294,
        actual_byte_field_roundtrip=True, setup_and_audio_bounded_grammar_checked=True, spectra_are_integer_symbol_models_not_PCM=True,
        all_channels_mixed_nonzero_distinct_bounded_in_symbol_model=True, all_ogg_crc_packet_granule_flags_roundtrip=True,
        exact_rejection_controls=controls, inputs_before=before, inputs_after=[fact(path) for path in inputs],
        helper_copied_or_globals_monkeypatched=False, decoder_SDK_compiler_QEMU_Git_device_executed=False)
    for name, value in (("matrix.json", matrix), ("construction.json", construction), ("pure-checks.json", checks)):
        payloads[name] = (json.dumps(value, indent=2) + "\n").encode()
    manifest = dict(schema="vorbis-mono-mapping-manifest-v1", source_inputs=before, references=REFERENCES,
        files=[dict(path=name, bytes=len(data), sha256=sha(data)) for name, data in sorted(payloads.items())])
    payloads["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    output.mkdir()
    for name, data in payloads.items():
        path = output / name; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream: stream.write(data)
    print(json.dumps(dict(output=str(output), cases=21, packets=294, expected_pcm_bytes=matrix["expected_total_s16le_bytes"],
        manifest_sha256=sha(payloads["manifest.json"]), pure_checks_sha256=sha(payloads["pure-checks.json"]), reference_pending=True)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    generate(parser.parse_args().output)
