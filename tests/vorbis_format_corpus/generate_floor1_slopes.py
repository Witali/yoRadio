"""Construct complete floor1 slope/post packets; no decoder or target execution."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "tests/vorbis_block_matrix/generate_minimal.py"
BASE_SHA = "8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1"
if hashlib.sha256(BASE.read_bytes()).hexdigest() != BASE_SHA:
    raise ValueError("Pinned canonical minimal helper changed")
_spec = importlib.util.spec_from_file_location("floor1_slopes_minimal", BASE)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
SHORT, LONG, RATE, CHANNELS = 256, 2048, 48000, 2
RANGES = (256, 128, 86, 64)
REFERENCES = ["https://xiph.org/vorbis/doc/Vorbis_I_spec.html",
              "https://xiph.org/ogg/doc/framing.html",
              "https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor1.c"]


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def requests():
    valid = [
        ("m1-range0-up", 1, 0, [], 160, 255),
        ("m1-range15-down-5-1-3", 1, 15, [5, 1, 3], 255, 160),
        ("m2-range1-up", 2, 1, [], 80, 127),
        ("m2-range10-down-wide", 2, 10, [300, 1, 1023], 127, 80),
        ("m3-range3-up-5-1-3", 3, 3, [5, 1, 3], 54, 85),
        ("m3-range7-down-64-1-127", 3, 7, [64, 1, 127], 85, 54),
        ("m4-range7-up-64-1-127", 4, 7, [64, 1, 127], 40, 63),
        ("m4-range10-down-wide", 4, 10, [300, 1, 1023], 63, 40),
    ]
    invalid = [
        ("duplicate-implicit-zero", 1, [0], "duplicate_x"),
        ("duplicate-interior", 3, [2, 2], "duplicate_x"),
        ("duplicate-separated", 3, [5, 1, 5], "duplicate_x"),
        ("duplicate-range0", 0, [0], "duplicate_x"),
        ("66-total", 7, list(range(1, 65)), "too_many_x"),
        ("250-total", 8, list(range(1, 249)), "too_many_x"),
    ]
    return ([dict(id=name, multiplier=mult, rangebits=bits, interior=xs, y0=y0, y1=y1,
                  expected_valid=True, expected_rejection=None)
             for name, mult, bits, xs, y0, y1 in valid] +
            [dict(id=name, multiplier=1, rangebits=bits, interior=xs, y0=160, y1=255,
                  expected_valid=False, expected_rejection=reason)
             for name, bits, xs, reason in invalid])


def geometry(case):
    count = len(case["interior"])
    dims = [8] * (count // 8) + ([count % 8] if count % 8 else [])
    classes = list(dict.fromkeys(dims))
    return dims, classes, [classes.index(dim) for dim in dims]


def setup(case):
    """Book0 classword, book1 mapped residue, book2 two-entry scalar floor book."""
    xs, bits, mult = case["interior"], case["rangebits"], case["multiplier"]
    dims, classes, partitions = geometry(case)
    need(0 <= bits <= 15 and len(dims) <= 31 and 1 <= mult <= 4, "representable floor1 geometry")
    need(all(0 <= x < 1 << bits for x in xs), "representable floor1 coordinate")
    b = base.Bits(); base.prefix(b, 5)
    b.put("codebooks_minus_1", 8, 2)
    base.book(b, 0, 1, False)
    base.book(b, 1, 2, True)
    base.book(b, 2, 2, False)
    for name, width, value in (("time_count_minus_1", 6, 0), ("time[0].type", 16, 0),
            ("floor_count_minus_1", 6, 0), ("floor[0].type", 16, 1)):
        b.put(name, width, value)
    b.put("floor[0].partitions", 5, len(dims))
    for i, cls in enumerate(partitions):
        b.put(f"floor[0].partition_class[{i}]", 4, cls)
    for i, dim in enumerate(classes):
        b.put(f"floor[0].class[{i}].dimension_minus_1", 3, dim - 1)
        b.put(f"floor[0].class[{i}].subclass_bits", 2, 0)
        b.put(f"floor[0].class[{i}].subbook_plus_1[0]", 8, 3)
    b.put("floor[0].multiplier_minus_1", 2, mult - 1)
    b.put("floor[0].rangebits", 4, bits)
    for i, value in enumerate(xs):
        b.put(f"floor[0].x[{i + 2}]", bits, value)
    for name, width, value in (("residue_count_minus_1", 6, 0), ("residue[0].type", 16, 1),
            ("residue[0].begin", 24, 0), ("residue[0].end", 24, 16),
            ("residue[0].partition_size_minus_1", 24, 15),
            ("residue[0].classifications_minus_1", 6, 0), ("residue[0].classbook", 8, 0),
            ("residue[0].cascade_low", 3, 1), ("residue[0].cascade_high_present", 1, 0),
            ("residue[0].stagebook[0][0]", 8, 1), ("mapping_count_minus_1", 6, 0),
            ("mapping[0].type", 16, 0), ("mapping[0].multiple_submaps", 1, 0),
            ("mapping[0].coupling", 1, 0), ("mapping[0].reserved", 2, 0)):
        b.put(name, width, value)
    for field in ("time", "floor", "residue"):
        b.put("mapping[0]." + field, 8, 0)
    b.put("modes_minus_1", 6, 1)
    for mode in range(2):
        for field, width, value in (("blockflag", 1, mode), ("windowtype", 16, 0),
                                   ("transformtype", 16, 0), ("mapping", 8, 0)):
            b.put(f"mode[{mode}]." + field, width, value)
    b.put("framing", 1, 1)
    return b


def audio(case, packet):
    b = base.Bits(); mode = base.MODES[packet]
    value_range = RANGES[case["multiplier"] - 1]
    width = (value_range - 1).bit_length()
    need(0 <= case["y0"] < value_range and 0 <= case["y1"] < value_range, "floor scalar bounds")
    b.put("audio_packet_type", 1, 0); b.put("mode", 1, mode)
    if mode:
        b.put("previous_window_flag", 1, base.MODES[packet - 1] if packet else 0)
        b.put("next_window_flag", 1, base.MODES[packet + 1] if packet + 1 < len(base.MODES) else 0)
    for channel in range(CHANNELS):
        b.put(f"floor[{channel}].present", 1, 1)
        b.put(f"floor[{channel}].y0", width, case["y0"])
        b.put(f"floor[{channel}].y1", width, case["y1"])
        for index in range(len(case["interior"])):
            b.put(f"floor[{channel}].post[{index + 2}].code", 1, (packet + channel + index) & 1)
    for channel in range(CHANNELS):
        b.put(f"classword[{channel}]", 1, 0)
    for channel in range(CHANNELS):
        for scalar in range(16):
            b.put(f"residue[{channel}][{scalar}]", 1, base.sign_code(packet, channel, scalar))
    return b


def pcm_geometry():
    blocks = [LONG if mode else SHORT for mode in base.MODES]
    frames = [0] + [(a + b) // 4 for a, b in zip(blocks, blocks[1:])]
    return frames, [n * CHANNELS * 2 for n in frames]


def payloads():
    info, comment = base.identification(8, 11, RATE), base.comment()
    frames, sizes = pcm_geometry()
    need(len(base.MODES) == 14 and sum(sizes) == 28160, "fixed packet/PCM geometry")
    granules, total = [], 0
    for count in frames:
        total += count; granules.append(total)
    files = {"identification.bin": info.data(), "info.bin": info.data()[7:], "comment.bin": comment.data()}
    fields = dict(identification=info.report(), comment=comment.report(), setup={}, audio={})
    header = ("// Construction only; reference/target qualification remains pending.\n"
              "#pragma once\n#include <stdbool.h>\n#include <stdint.h>\n"
              "#define FIXTURE_CASES 14\n#define FIXTURE_PACKETS 14\n"
              "#define FLOOR1_PER_CASE_AUDIO 1\n#define FIXTURE_PCM_BYTES 28160\n")
    header += base.c_bytes("fixture_info", info.data()[7:])
    for name, ctype, values in (("fixture_modes", "uint8_t", base.MODES),
            ("fixture_expected_samples", "uint32_t", frames), ("fixture_expected_bytes", "uint32_t", sizes)):
        header += f"static const {ctype} {name}[{len(values)}] = {{" + ", ".join(map(str, values)) + "};\n"
    header += "#define fixture_long_mode fixture_modes\n"
    cases = []
    for index, request in enumerate(requests()):
        b = setup(request); data = b.data(); name = request["id"]
        xs = [0, 1 << request["rangebits"]] + request["interior"]
        need((len(xs) <= 65 and len(set(xs)) == len(xs)) == request["expected_valid"], "declared validity")
        dims, classes, partitions = geometry(request)
        packets = [audio(request, i) for i in range(14)]
        offsets = [0]
        for packet in packets:
            offsets.append(offsets[-1] + len(packet.data()))
        raw_audio = b"".join(p.data() for p in packets)
        paths = dict(setup=f"cases/{name}/setup.bin", setup_raw=f"cases/{name}/setup.raw.bin",
                     audio=f"cases/{name}/audio.bin", ogg=f"cases/{name}/reference.ogg")
        files[paths["setup"]], files[paths["setup_raw"]], files[paths["audio"]] = data, data[7:], raw_audio
        stream_packets = [info.data(), comment.data(), data] + [p.data() for p in packets]
        page_granules = [0, 0, 0] + granules
        flags = [2] + [0] * (len(stream_packets) - 2) + [4]
        serial = 0x46530001 + index
        stream = b"".join(base.page(p, serial, i, page_granules[i], flags[i])
                          for i, p in enumerate(stream_packets))
        pages = base.read_pages(stream)
        need([p["packet"] for p in pages] == stream_packets, "carrier packets")
        need([p["granule"] for p in pages] == page_granules, "carrier granules")
        need([p["flags"] for p in pages] == flags and all(p["serial"] == serial for p in pages), "carrier metadata")
        files[paths["ogg"]] = stream
        fields["setup"][name], fields["audio"][name] = b.report(), [p.report() for p in packets]
        cases.append(dict(request, **paths, identification="identification.bin", info="info.bin",
            offsets=offsets, audio_sha256=sha(raw_audio), rate=RATE, channels=CHANNELS, short=SHORT, long=LONG,
            partition_dimensions=dims, class_dimensions=classes, partition_classes=partitions,
            x_list=xs, total_positions=len(xs), value_range=RANGES[request["multiplier"] - 1],
            subclass_bits=0, subbook=2, floor_codebook=2, mode_flags=list(base.MODES),
            expected_packet_samples=frames, expected_packet_bytes=sizes,
            expected_raw_samples=total, expected_s16le_bytes=sum(sizes), packet_granules=granules,
            pcm_expectations_apply=request["expected_valid"], page_crc32=[p["crc"] for p in pages]))
        header += base.c_bytes(f"fixture_setup_{index}", data[7:])
        header += base.c_bytes(f"fixture_packets_{index}", raw_audio)
        header += f"static const uint32_t fixture_offsets_{index}[15] = {{" + ", ".join(map(str, offsets)) + "};\n"
    need(len(cases) == 14 and sum(c["expected_valid"] for c in cases) == 8, "fixed14/eight valid")
    header += ("#define fixture_packets fixture_packets_0\n#define fixture_offsets fixture_offsets_0\n"
               "typedef struct { const char *name; const uint8_t *setup; uint32_t setup_size; bool valid; const uint8_t *packets; const uint32_t *offsets; } floor1_case_t;\n"
               "static const floor1_case_t cases[FIXTURE_CASES] = {\n")
    for i, case in enumerate(cases):
        header += f'    {{"{case["id"]}", fixture_setup_{i}, sizeof(fixture_setup_{i}), {str(case["expected_valid"]).lower()}, fixture_packets_{i}, fixture_offsets_{i}}},\n'
    header += "};\n"
    files["fixture.h"] = header.encode()
    files["audio.bin"] = files[cases[0]["audio"]]
    matrix = dict(schema="vorbis-floor1-slopes-v1", status="CONSTRUCTION_ONLY", case_count=14,
        valid_cases=8, invalid_cases=6, packet_count=14, valid_raw_packet_count=112,
        expected_valid_pcm_bytes=sum(sizes) * 8, decoder_execution=False,
        independent_reference_qualification=False, target_qualification=False,
        pcm_policy_note="Overlap sizes are arithmetic expectations, not observed output or an error tolerance.",
        invalid_note="Malformed setup rejection controls; carrier construction does not establish decodability.",
        identification="identification.bin", info="info.bin", comment="comment.bin", audio="audio.bin",
        offsets=cases[0]["offsets"], shared_audio_note="Top-level audio/offsets alias case0 only; use each case's audio/offsets.",
        cases=cases)
    for name, obj in (("matrix.json", matrix), ("bitfields.json", fields)):
        files[name] = (json.dumps(obj, indent=2) + "\n").encode()
    manifest = dict(schema="vorbis-floor1-slopes-manifest-v1", generator_sha256=sha(Path(__file__).read_bytes()),
        helper=dict(path="tests/vorbis_block_matrix/generate_minimal.py", sha256=BASE_SHA),
        references=REFERENCES, construction_only=True,
        cases=[dict(case, setup_bitfields=fields["setup"][case["id"]],
                    audio_bitfields=fields["audio"][case["id"]]) for case in cases],
        files=[dict(path=name, bytes=len(data), sha256=sha(data)) for name, data in sorted(files.items())])
    files["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    return files


def generate(output):
    output = Path(output).resolve()
    build = (ROOT / ".build").resolve()
    need(build.parent == ROOT and output != build and output.is_relative_to(build) and not output.exists(),
         "output must be fresh beneath this checkout's .build")
    files = payloads()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    for name, data in files.items():
        path = output / name; path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
    return dict(output=str(output), files=len(files), cases=14, valid_cases=8, invalid_cases=6,
                manifest_sha256=sha(files["manifest.json"]), construction_only=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".build/vorbis-floor1-slopes-corpus-01")
    print(json.dumps(generate(parser.parse_args().output)))
