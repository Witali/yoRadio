"""Create-only floor1 presence supplement39; no decoder or SDK invocation.

The original mono21 generator/helper are pinned ordinary imports. New cases are
separate, with fixed masks/schedules and zero/nonzero witnesses declared before
reference or target execution. This generator performs construction accounting,
not independent decode or standard conformance qualification.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MONO = ROOT / "tests/vorbis_format_corpus/generate_mono_mapping.py"
MONO_SHA = "c7c494f8b03266a4589a8b141e4b12b008e545f8081a09cf57c9b0965cd14a27"
BASE = ROOT / "tests/vorbis_block_matrix/generate_minimal.py"
BASE_SHA = "8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1"
SHORT, LONG, RATE, PACKETS = 256, 2048, 48000, 14
MONO_SCHEDULE = (0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1)
STEREO_SCHEDULE = (0, 0, 1, 2, 3, 0, 2, 1, 0, 0, 3, 3, 0, 1)
REFERENCES = ["https://xiph.org/vorbis/doc/Vorbis_I_spec.html",
    "https://xiph.org/ogg/doc/framing.html",
    "https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/mapping0.c",
    "https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/res0.c",
    "https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor1.c",
    "https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/block.c"]


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(data): return hashlib.sha256(data).hexdigest()


def load(name, path, digest):
    need(sha(path.read_bytes()) == digest, "ordinary_import_source_pin:" + name)
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


mono = load("presence39_original_mono21", MONO, MONO_SHA)
base = mono.base  # Exactly the already-pinned ordinary helper dependency.
MODES = mono.MODES


def requests():
    rows = []
    for residue in range(3):
        for mask in range(2):
            rows.append(dict(id=f"floor1-r{residue}-mono-mask{mask}", residue=residue,
                channels=1, coupled=False, schedule=[mask] * PACKETS, schedule_kind="constant"))
    for residue in range(3):
        for coupled in (False, True):
            for mask in range(4):
                rows.append(dict(id=f"floor1-r{residue}-{'coupled' if coupled else 'uncoupled'}-mask{mask:02b}",
                    residue=residue, channels=2, coupled=coupled,
                    schedule=[mask] * PACKETS, schedule_kind="constant"))
    for residue in range(3):
        rows.append(dict(id=f"floor1-r{residue}-mono-schedule", residue=residue,
            channels=1, coupled=False, schedule=list(MONO_SCHEDULE), schedule_kind="packet_changes"))
    for residue in range(3):
        for coupled in (False, True):
            rows.append(dict(id=f"floor1-r{residue}-{'coupled' if coupled else 'uncoupled'}-schedule",
                residue=residue, channels=2, coupled=coupled,
                schedule=list(STEREO_SCHEDULE), schedule_kind="packet_changes"))
    need(len(rows) == len({r["id"] for r in rows}) == 39, "full39_distinct_requests")
    return rows


def layout(request, packet):
    channels, mask = request["channels"], request["schedule"][packet]
    floor = [bool(mask & (1 << channel)) for channel in range(channels)]
    nonzero = [True] * channels if request["coupled"] and any(floor) else floor[:]
    # Vorbis8.6.5 type2 ignores individual do_not_decode if ANY channel is active.
    residue = ([any(nonzero)] * channels if request["residue"] == 2 else nonzero[:])
    return dict(floor_present=floor, nonzero_after_coupling=nonzero,
                residue_channels=residue, do_not_decode=[not x for x in nonzero])


def setup(request):
    channels, coupled, kind = (request[k] for k in ("channels", "coupled", "residue"))
    span = 16 * channels if kind == 2 else 16
    b = base.Bits(); base.prefix(b, 5)
    b.put("codebooks_minus_1", 8, 1)
    base.book(b, 0, 1, False)
    if coupled: mono.coupling_book(b)
    else: base.book(b, 1, 2, True)
    fields = (("time_count_minus_1", 6, 0), ("time[0].type", 16, 0),
        ("floor_count_minus_1", 6, 0), ("floor[0].type", 16, 1),
        ("floor[0].partitions", 5, 0), ("floor[0].multiplier_minus_1", 2, 0),
        ("floor[0].rangebits", 4, 10), ("residue_count_minus_1", 6, 0),
        ("residue[0].type", 16, kind), ("residue[0].begin", 24, 0),
        ("residue[0].end", 24, span), ("residue[0].partition_size_minus_1", 24, span - 1),
        ("residue[0].classifications_minus_1", 6, 0), ("residue[0].classbook", 8, 0),
        ("residue[0].cascade_low", 3, 1), ("residue[0].cascade_high_present", 1, 0),
        ("residue[0].stagebook[0][0]", 8, 1), ("mapping_count_minus_1", 6, 0),
        ("mapping[0].type", 16, 0), ("mapping[0].multiple_submaps", 1, 0),
        ("mapping[0].coupling", 1, int(coupled)))
    for name, width, value in fields: b.put(name, width, value)
    if coupled:
        b.put("mapping[0].coupling_steps_minus_1", 8, 0)
        b.put("mapping[0].magnitude[0]", 1, 0)
        b.put("mapping[0].angle[0]", 1, 1)
    b.put("mapping[0].reserved", 2, 0)
    for name in ("time", "floor", "residue"): b.put("mapping[0]." + name, 8, 0)
    b.put("modes_minus_1", 6, 1)
    for mode in range(2):
        for name, width, value in (("blockflag", 1, mode), ("windowtype", 16, 0),
            ("transformtype", 16, 0), ("mapping", 8, 0)):
            b.put(f"mode[{mode}]." + name, width, value)
    b.put("framing", 1, 1)
    return b


def audio(request, packet):
    state = layout(request, packet)
    channels, coupled, kind = (request[k] for k in ("channels", "coupled", "residue"))
    b = base.Bits(); mode = MODES[packet]
    b.put("audio_packet_type", 1, 0); b.put("mode", 1, mode)
    if mode:
        b.put("previous_window_flag", 1, MODES[packet - 1])
        b.put("next_window_flag", 1, MODES[packet + 1])
    for channel, present in enumerate(state["floor_present"]):
        b.put(f"floor[{channel}].present", 1, int(present))
        if present:
            b.put(f"floor[{channel}].y0", 8, 255)
            b.put(f"floor[{channel}].y1", 8, 255)
    active = [c for c, yes in enumerate(state["residue_channels"]) if yes]
    if active:
        for index in range(1 if kind == 2 else len(active)):
            b.put(f"residue.classword[{index}]", 1, 0)
        positions = [(i % channels, i // channels) for i in range(16 * channels)] if kind == 2 else [
            (channel, scalar) for channel in active for scalar in range(16)]
        for channel, scalar in positions:
            index = mono.symbol(packet, channel, scalar, coupled)
            b.put(f"residue[{channel}][{scalar}]", 2 if coupled else 1,
                  mono.wire_symbol(index, coupled))
    return b


def inspect_setup(data, request):
    """Actual-byte grammar with no call to this supplement's setup writer."""
    r = mono.Reader(data); coupled = request["coupled"]; channels = request["channels"]
    r.exact(56, int.from_bytes(b"\x05vorbis", "little"), "setup_prefix")
    r.exact(8, 1, "two_books")
    for index in range(2):
        entries = 1 if index == 0 else 4 if coupled else 2
        for width, value in ((24, 0x564342), (16, 1), (24, entries), (1, 0), (1, 0)):
            r.exact(width, value, "scalar_complete_book")
        for _ in range(entries): r.exact(5, int(index == 1 and coupled), "book_length")
        r.exact(4, int(index == 1), "book_lookup")
        if index:
            minimum, delta = (-2, 1) if coupled else (-1, 2)
            need(base.unpack_float(r.take(32)) == minimum and base.unpack_float(r.take(32)) == delta,
                 "book_quantization")
            width = r.take(4) + 1; need(width == (3 if coupled else 1), "quant_width")
            r.exact(1, 0, "book_sequence")
            values = [minimum + delta * r.take(width) for _ in range(entries)]
            need(values == ([-2, -1, 1, 2] if coupled else [-1, 1]), "exact_bounded_VQ_values")
    kind = request["residue"]; span = 16 * channels if kind == 2 else 16
    for width, value in ((6, 0), (16, 0), (6, 0), (16, 1), (5, 0), (2, 0), (4, 10),
        (6, 0), (16, kind), (24, 0), (24, span), (24, span - 1), (6, 0), (8, 0),
        (3, 1), (1, 0), (8, 1), (6, 0), (16, 0), (1, 0), (1, int(coupled))):
        r.exact(width, value, "setup_shape")
    if coupled:
        for width, value in ((8, 0), (1, 0), (1, 1)): r.exact(width, value, "coupling_pair")
    for width, value in ((2, 0), (8, 0), (8, 0), (8, 0), (6, 1)):
        r.exact(width, value, "one_submap_two_modes")
    for mode in range(2):
        for width, value in ((1, mode), (16, 0), (16, 0), (8, 0)):
            r.exact(width, value, "mode")
    r.exact(1, 1, "framing"); r.finish()
    return dict(used_bits=r.offset, bytes=len(data), vector_dimension=1,
        residue_span=span, floor1_endpoint=1024, complete_huffman_trees=True)


def inspect_audio(data, request, packet):
    """Parse actual floor flags, then independently derive nonzero/skip decisions."""
    r = mono.Reader(data); channels = request["channels"]; coupled = request["coupled"]
    r.exact(1, 0, "audio_type"); r.exact(1, MODES[packet], "mode")
    if MODES[packet]:
        r.exact(1, MODES[packet - 1], "previous_window")
        r.exact(1, MODES[packet + 1], "next_window")
    actual_floor = []
    for channel in range(channels):
        present = r.take(1)
        need(present == ((request["schedule"][packet] >> channel) & 1), "scheduled_floor_bit")
        actual_floor.append(bool(present))
        if present: r.exact(8, 255, "floor_y0"); r.exact(8, 255, "floor_y1")
    nz = actual_floor[:]
    if coupled and (nz[0] or nz[1]): nz[0] = nz[1] = True
    kind = request["residue"]
    residue_channels = (list(range(channels)) if any(nz) else []) if kind == 2 else [
        c for c in range(channels) if nz[c]]
    decoded = [[0] * 16 for _ in range(channels)]
    if residue_channels:
        for _ in range(1 if kind == 2 else len(residue_channels)):
            r.exact(1, 0, "classword")
        # All vector dimensions are1, so residue0/1 have identical scalar order.
        for local in range(16 * (channels if kind == 2 else len(residue_channels))):
            channel = local % channels if kind == 2 else residue_channels[local // 16]
            scalar = local // channels if kind == 2 else local % 16
            code = r.take(2 if coupled else 1)
            index = ((code & 1) << 1) | (code >> 1) if coupled else code
            need(index == mono.symbol(packet, channel, scalar, coupled), "residue_symbol")
            decoded[channel][scalar] = ([-2, -1, 1, 2] if coupled else [-1, 1])[index]
    r.finish()
    coupled_spectra = [v[:] for v in decoded]
    if coupled:
        for scalar in range(16):
            mag, angle = decoded[0][scalar], decoded[1][scalar]
            if mag > 0:
                left, right = (mag, mag - angle) if angle > 0 else (mag + angle, mag)
            else:
                left, right = (mag, mag + angle) if angle > 0 else (mag - angle, mag)
            coupled_spectra[0][scalar], coupled_spectra[1][scalar] = left, right
    postfloor = [v if present else [0] * 16 for v, present in zip(coupled_spectra, actual_floor)]
    need(all(bool(any(v)) == present for v, present in zip(postfloor, actual_floor)), "postfloor_zero_nonzero_model")
    need(all(max(map(abs, v)) <= 2 for v in postfloor), "bounded_spectral_integer_model")
    return dict(used_bits=r.offset, bytes=len(data), actual_floor_present=actual_floor,
        nonzero_after_coupling=nz, do_not_decode=[not x for x in nz],
        residue_channels_decoded=residue_channels, residue_scalar_model=decoded,
        uncoupled_scalar_model=coupled_spectra, postfloor_scalar_model=postfloor,
        scalar_model_is_not_PCM=True, actual_PCM_observed=False)


def packet_witness(request, packet):
    channels = request["channels"]
    if packet == 0:
        return dict(packet=0, frames=0, channel_zero_spans=[[] for _ in range(channels)],
            channel_requires_nonzero=[False] * channels, reason="primer_emits_no_frames")
    a, b = (LONG if MODES[i] else SHORT for i in (packet - 1, packet))
    frames = (a + b) // 4
    prior, current = request["schedule"][packet - 1:packet + 1]
    zero, required = [], []
    for channel in range(channels):
        previous_present = bool(prior & (1 << channel)); current_present = bool(current & (1 << channel))
        # Output timeline [previous_center,current_center), length(a+b)/4.
        # Previous window support ends at min(a/2,frames). Current window
        # support begins at max(0,frames-b/2). These are support envelopes;
        # no exact nonzero sample waveform is invented here.
        spans = []
        if not previous_present and not current_present: spans = [[0, frames]]
        elif not previous_present and a > b: spans = [[0, frames - b // 2]]
        elif not current_present and a < b: spans = [[a // 2, frames]]
        zero.append(spans); required.append(previous_present or current_present)
    return dict(packet=packet, frames=frames, channel_zero_spans=zero,
        channel_requires_nonzero=required, previous_floor_mask=prior, current_floor_mask=current,
        reason="postfloor_zero_blocks_and_Vorbis_window_support")


def generate(output):
    output = output.resolve(); build = ROOT / ".build"
    need(output.parent == build and not output.exists(), "fresh_direct_child_build_output")
    source_paths = [Path(__file__).resolve(), MONO, BASE]
    before = [{"path": str(p), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size} for p in source_paths]
    need(len(MODES) == PACKETS and MODES[0] == MODES[-1] == 0, "reviewed14_mode_sequence")
    frames = [0] + [((LONG if a else SHORT) + (LONG if b else SHORT)) // 4 for a, b in zip(MODES, MODES[1:])]
    granules = []; total = 0
    for count in frames: total += count; granules.append(total)
    payloads, cases, construction = {}, [], {}
    for index, request in enumerate(requests()):
        folder = "cases/" + request["id"] + "/"; channels = request["channels"]
        ib, sb, cb = mono.identification(RATE, channels), setup(request), base.comment()
        packets = [audio(request, packet) for packet in range(PACKETS)]
        setup_readback = inspect_setup(sb.data(), request)
        parsed = [inspect_audio(p.data(), request, packet) for packet, p in enumerate(packets)]
        offsets = [0]
        for p in packets: offsets.append(offsets[-1] + len(p.data()))
        raw = dict(identification=ib.data(), setup=sb.data(), comment=cb.data(), audio=b"".join(p.data() for p in packets))
        all_packets = [raw[k] for k in ("identification", "comment", "setup")] + [p.data() for p in packets]
        carrier = b"".join(base.page(p, 0x46500001 + index, sequence, granule, flag)
            for sequence, (p, granule, flag) in enumerate(zip(all_packets, [0, 0, 0] + granules, [2] + [0] * 15 + [4])))
        pages = base.read_pages(carrier)
        need([p["packet"] for p in pages] == all_packets and [p["granule"] for p in pages] == [0, 0, 0] + granules,
             "complete_Ogg_packet_CRC_granule_roundtrip")
        need(all(p["serial"] == 0x46500001 + index for p in pages), "complete_Ogg_serial_roundtrip")
        need([p["flags"] for p in pages] == [2] + [0] * 15 + [4], "complete_Ogg_flags_roundtrip")
        for kind, data in raw.items(): payloads[folder + kind + ".bin"] = data
        payloads[folder + "reference.ogg"] = carrier
        pcm = [count * channels * 2 for count in frames]
        witnesses = [packet_witness(request, packet) for packet in range(PACKETS)]
        constant = request["schedule_kind"] == "constant"
        always_absent = [not any(mask & (1 << c) for mask in request["schedule"]) for c in range(channels)]
        case = dict(**request, identification=folder + "identification.bin", comment=folder + "comment.bin",
            setup=folder + "setup.bin", audio=folder + "audio.bin", ogg=folder + "reference.ogg",
            rate=RATE, short=SHORT, long=LONG, mode_flags=list(MODES), offsets=offsets, packet_count=PACKETS,
            expected_packet_frames=frames, expected_packet_samples=frames, expected_packet_s16le_bytes=pcm,
            expected_raw_samples=total, expected_s16le_bytes=sum(pcm), packet_granules=granules,
            raw_sha256={k: sha(v) for k, v in raw.items()}, ogg_sha256=sha(carrier),
            features=["floor1_rangebits10", "residue" + str(request["residue"]), "floor_presence"],
            presence_mask_bit_order="bit0=channel0;bit1=channel1", packet_PCM_witnesses=witnesses,
            constant_all_absent_silence_witness=constant and request["schedule"][0] == 0,
            always_absent_channel_silence_witness=always_absent, independent_decode_pending=True)
        cases.append(case)
        construction[request["id"]] = dict(setup_writer=sb.report(), setup_readback=setup_readback,
            audio=[dict(writer=p.report(), readback=parsed[i]) for i, p in enumerate(packets)])
    need(len(cases) == 39 and sum(c["channels"] == 1 for c in cases) == 9, "exact39_and_channels")
    need(sum(c["constant_all_absent_silence_witness"] for c in cases) == 9, "nine_constant_all_absent_witnesses")
    matrix = dict(schema="vorbis-floor-presence39-matrix-v1", status="CONSTRUCTION_REFERENCE_PENDING",
        packet_count=PACKETS, total_packets=39 * PACKETS, cases=cases,
        expected_total_s16le_bytes=sum(c["expected_s16le_bytes"] for c in cases),
        case_mask=(1 << 39) - 1, case_mask_C_type="uint64_t",
        references=REFERENCES, supplement_not_replacement=True, original_mono21_changed=False,
        predeclared_max_abs_error=2, references_required=["libvorbis", "vorbis"],
        transitions={str(k): v for k, v in sorted(Counter(zip(MODES, MODES[1:])).items())},
        independent_reference_executed=False, target_executed=False, full_G6_qualified=False)
    for path, original in zip(source_paths, before):
        need(sha(path.read_bytes()) == original["sha256"], "source_changed_during_construction")
    for name, value in (("matrix.json", matrix), ("construction.json", construction)):
        payloads[name] = (json.dumps(value, indent=2, allow_nan=False) + "\n").encode()
    manifest = dict(schema="vorbis-floor-presence39-manifest-v1", source_inputs=before,
        files=[dict(path=p, bytes=len(d), sha256=sha(d)) for p, d in sorted(payloads.items())])
    payloads["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    output.mkdir()
    for name, data in payloads.items():
        path = output / name; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream: stream.write(data)
    print(json.dumps(dict(output=str(output), cases=39, packets=546,
        expected_pcm_bytes=matrix["expected_total_s16le_bytes"], manifest_sha256=sha(payloads["manifest.json"]),
        independent_reference_pending=True, target_executed=False)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    generate(parser.parse_args().output)
