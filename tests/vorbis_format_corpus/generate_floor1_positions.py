"""Construct 14 floor1 position setups; no decoder, SDK or target execution."""
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
_spec = importlib.util.spec_from_file_location("floor1_positions_minimal", BASE)
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)
SHORT, LONG, RATE, CHANNELS = 256, 2048, 48000, 2
REFERENCES = ["https://xiph.org/vorbis/doc/Vorbis_I_spec.html",
              "https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor1.c",
              "https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/backends.h"]


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def requests():
    rows = [
        ("no-extra-range0", 0, [], True, None),
        ("one-x1-range1", 1, [1], True, None),
        ("unsorted-5-1-3", 3, [5, 1, 3], True, None),
        ("62-ascending", 7, list(range(1, 63)), True, None),
        ("63-ascending", 7, list(range(1, 64)), True, None),
        ("63-reversed", 7, list(range(63, 0, -1)), True, None),
        ("63-odds-evens", 7, list(range(1, 64, 2)) + list(range(2, 64, 2)), True, None),
        ("63-wide", 15, [1 + i * 503 for i in range(63)], True, None),
        ("duplicate-implicit-zero", 1, [0], False, "duplicate_x"),
        ("duplicate-interior", 3, [2, 2], False, "duplicate_x"),
        ("duplicate-separated", 3, [5, 1, 5], False, "duplicate_x"),
        ("duplicate-range0", 0, [0], False, "duplicate_x"),
        ("66-total", 7, list(range(1, 65)), False, "too_many_x"),
        ("250-total", 8, list(range(1, 249)), False, "too_many_x"),
    ]
    return [dict(id=name, rangebits=bits, interior=xs, expected_valid=valid,
                 expected_rejection=reason) for name, bits, xs, valid, reason in rows]


def geometry(case):
    count = len(case["interior"])
    dims = [8] * (count // 8) + ([count % 8] if count % 8 else [])
    classes = list(dict.fromkeys(dims))
    return dims, classes, [classes.index(dim) for dim in dims]


def setup(case):
    """Complete setup with the two unchanged minimal books and residue1."""
    xs, bits = case["interior"], case["rangebits"]
    dims, classes, partitions = geometry(case)
    need(0 <= bits <= 15 and len(dims) <= 31, "representable floor1 geometry")
    need(all(0 <= x < 1 << bits for x in xs), "representable floor1 coordinate")
    b = base.Bits(); base.prefix(b, 5)
    b.put("codebooks_minus_1", 8, 1)
    base.book(b, 0, 1, False)
    base.book(b, 1, 2, True)
    for name, width, value in (("time_count_minus_1", 6, 0), ("time[0].type", 16, 0),
            ("floor_count_minus_1", 6, 0), ("floor[0].type", 16, 1)):
        b.put(name, width, value)
    b.put("floor[0].partitions", 5, len(dims))
    for i, cls in enumerate(partitions):
        b.put(f"floor[0].partition_class[{i}]", 4, cls)
    for i, dim in enumerate(classes):
        b.put(f"floor[0].class[{i}].dimension_minus_1", 3, dim - 1)
        b.put(f"floor[0].class[{i}].subclass_bits", 2, 0)
        b.put(f"floor[0].class[{i}].subbook_plus_1[0]", 8, 0)
    b.put("floor[0].multiplier_minus_1", 2, 0)
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


def pcm_geometry():
    blocks = [LONG if mode else SHORT for mode in base.MODES]
    frames = [0] + [(a + b) // 4 for a, b in zip(blocks, blocks[1:])]
    return frames, [n * CHANNELS * 2 for n in frames]


def payloads():
    """Construct bytes in memory; qualification remains explicitly pending."""
    info, comment = base.identification(8, 11, RATE), base.comment()
    packets = [base.audio(i) for i in range(len(base.MODES))]
    offsets = [0]
    for packet in packets:
        offsets.append(offsets[-1] + len(packet.data()))
    audio = b"".join(p.data() for p in packets)
    frames, sizes = pcm_geometry()
    need(len(packets) == 14 and sum(sizes) == 28160, "fixed packet/PCM geometry")
    granules, total = [], 0
    for count in frames:
        total += count; granules.append(total)
    files = {"identification.bin": info.data(), "info.bin": info.data()[7:],
             "comment.bin": comment.data(), "audio.bin": audio}
    fields = dict(identification=info.report(), comment=comment.report(),
                  audio=[p.report() for p in packets], setup={})
    header = ("// Generated construction only; decoder/reference qualification pending.\n"
              "#pragma once\n#include <stdbool.h>\n#include <stdint.h>\n"
              "#define FIXTURE_CASES 14\n#define FIXTURE_PACKETS 14\n"
              f"#define FIXTURE_PCM_BYTES {sum(sizes)}\n")
    header += base.c_bytes("fixture_info", info.data()[7:])
    header += base.c_bytes("fixture_packets", audio)
    for name, ctype, values in (("fixture_offsets", "uint32_t", offsets),
            ("fixture_modes", "uint8_t", base.MODES),
            ("fixture_expected_samples", "uint32_t", frames),
            ("fixture_expected_bytes", "uint32_t", sizes)):
        header += f"static const {ctype} {name}[{len(values)}] = {{" + ", ".join(map(str, values)) + "};\n"
    header += "#define fixture_long_mode fixture_modes\n"
    cases = []
    for index, request in enumerate(requests()):
        b = setup(request); data = b.data(); name = request["id"]
        xs = [0, 1 << request["rangebits"]] + request["interior"]
        need((len(xs) <= 65 and len(set(xs)) == len(xs)) == request["expected_valid"],
             "declared floor1 validity")
        dims, classes, partitions = geometry(request)
        paths = dict(setup=f"cases/{name}/setup.bin", setup_raw=f"cases/{name}/setup.raw.bin",
                     ogg=f"cases/{name}/reference.ogg")
        files[paths["setup"]], files[paths["setup_raw"]] = data, data[7:]
        stream_packets = [info.data(), comment.data(), data] + [p.data() for p in packets]
        page_granules = [0, 0, 0] + granules
        flags = [2] + [0] * (len(stream_packets) - 2) + [4]
        serial = 0x46510001 + index
        stream = b"".join(base.page(p, serial, i, page_granules[i], flags[i])
                          for i, p in enumerate(stream_packets))
        pages = base.read_pages(stream)
        need([p["packet"] for p in pages] == stream_packets, "carrier packets")
        need([p["granule"] for p in pages] == page_granules, "carrier granules")
        need([p["flags"] for p in pages] == flags and all(p["serial"] == serial for p in pages),
             "carrier flags/serial")
        files[paths["ogg"]] = stream
        fields["setup"][name] = b.report()
        cases.append(dict(request, **paths, identification="identification.bin", info="info.bin",
            audio="audio.bin", offsets=offsets, rate=RATE, channels=CHANNELS, short=SHORT, long=LONG,
            partition_dimensions=dims, class_dimensions=classes, partition_classes=partitions,
            x_list=xs, total_positions=len(xs), multiplier=1, subclass_bits=0, subbook=-1,
            mode_flags=list(base.MODES), expected_packet_samples=frames, expected_packet_bytes=sizes,
            expected_raw_samples=total, expected_s16le_bytes=sum(sizes), packet_granules=granules,
            pcm_expectations_apply=request["expected_valid"], page_crc32=[p["crc"] for p in pages]))
        header += base.c_bytes(f"fixture_setup_{index}", data[7:])
    need(len(cases) == 14 and sum(c["expected_valid"] for c in cases) == 8, "fixed14/eight valid")
    header += ("typedef struct { const char *name; const uint8_t *setup; uint32_t setup_size; bool valid; } floor1_case_t;\n"
               "static const floor1_case_t cases[FIXTURE_CASES] = {\n")
    for i, case in enumerate(cases):
        header += f'    {{"{case["id"]}", fixture_setup_{i}, sizeof(fixture_setup_{i}), {str(case["expected_valid"]).lower()}}},\n'
    header += "};\n"
    files["fixture.h"] = header.encode()
    matrix = dict(schema="vorbis-floor1-positions-v1", status="CONSTRUCTION_ONLY",
        case_count=14, valid_cases=8, invalid_cases=6, packet_count=14,
        valid_raw_packet_count=112, expected_valid_pcm_bytes=sum(sizes) * 8,
        decoder_execution=False, independent_reference_qualification=False, target_qualification=False,
        pcm_policy_note="PCM sizes are overlap arithmetic for valid cases, not observed output or a standard error tolerance.",
        invalid_note="Invalid setups are rejection controls; their carriers do not establish decodability.",
        identification="identification.bin", info="info.bin", comment="comment.bin", audio="audio.bin",
        offsets=offsets, cases=cases)
    for name, obj in (("matrix.json", matrix), ("bitfields.json", fields)):
        files[name] = (json.dumps(obj, indent=2) + "\n").encode()
    manifest = dict(schema="vorbis-floor1-positions-manifest-v1", generator_sha256=sha(Path(__file__).read_bytes()),
        helper=dict(path="tests/vorbis_block_matrix/generate_minimal.py", sha256=BASE_SHA),
        references=REFERENCES, construction_only=True,
        cases=[dict(case, setup_bitfields=fields["setup"][case["id"]]) for case in cases],
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
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
    return dict(output=str(output), files=len(files), cases=14, valid_cases=8, invalid_cases=6,
                manifest_sha256=sha(files["manifest.json"]), construction_only=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / ".build/vorbis-floor1-positions-corpus-01")
    print(json.dumps(generate(parser.parse_args().output)))
