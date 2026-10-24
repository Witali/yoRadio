"""Pure construction tests: no codec, SDK, emulator, FFmpeg or subprocess."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import struct
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests/vorbis_format_corpus/generate_floor1_slopes.py"
spec = importlib.util.spec_from_file_location("floor1_slopes_generator", SOURCE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
MODES = [int(c == "L") for c in "SSLLLSLSSSLLSS"]
RANGES = (256, 128, 86, 64)


class Reader:
    def __init__(self, data):
        self.raw, self.position = data, 0

    def take(self, width):
        if width < 0 or self.position + width > len(self.raw) * 8:
            raise ValueError("bounded bit reader")
        value = 0
        for shift in range(width):
            bit = self.position + shift
            value |= ((self.raw[bit // 8] >> (bit % 8)) & 1) << shift
        self.position += width
        return value

    def expect(self, width, value):
        if self.take(width) != value:
            raise ValueError("unexpected field")

    def end(self):
        remaining = len(self.raw) * 8 - self.position
        if remaining >= 8:
            raise ValueError("noncanonical suffix")
        self.expect(remaining, 0)


def inspect_setup(raw):
    """Parse full setup independently of generated field names/offsets."""
    if raw[:7] != b"\x05vorbis":
        raise ValueError("setup signature")
    r = Reader(raw); r.take(56); r.expect(8, 2)
    books = []
    for entries, lookup in ((1, 0), (2, 1), (2, 0)):
        start = r.position
        for width, value in ((24, 0x564342), (16, 1), (24, entries), (1, 0), (1, 0)):
            r.expect(width, value)
        for _ in range(entries):
            r.expect(5, 0)
        r.expect(4, lookup)
        if lookup:
            for width, value in ((32, 0xe2800001), (32, 0x62800002), (4, 0), (1, 0), (1, 0), (1, 1)):
                r.expect(width, value)
        books.append((start, r.position))
    for width, value in ((6, 0), (16, 0), (6, 0), (16, 1)):
        r.expect(width, value)
    floor_start = r.position
    partition_classes = [r.take(4) for _ in range(r.take(5))]
    classes = []
    for _ in range(max(partition_classes, default=-1) + 1):
        classes.append(r.take(3) + 1); r.expect(2, 0); r.expect(8, 3)
    multiplier, rangebits = r.take(2) + 1, r.take(4)
    count = sum(classes[c] for c in partition_classes)
    xs = [0, 1 << rangebits] + [r.take(rangebits) for _ in range(count)]
    floor_end = r.position
    for width, value in ((6, 0), (16, 1), (24, 0), (24, 16), (24, 15), (6, 0),
            (8, 0), (3, 1), (1, 0), (8, 1), (6, 0), (16, 0), (1, 0), (1, 0),
            (2, 0), (8, 0), (8, 0), (8, 0), (6, 1)):
        r.expect(width, value)
    for mode in (0, 1):
        for width, value in ((1, mode), (16, 0), (16, 0), (8, 0)):
            r.expect(width, value)
    r.expect(1, 1); used = r.position; r.end()
    return dict(x_list=xs, multiplier=multiplier, rangebits=rangebits,
                partition_classes=partition_classes, class_dimensions=classes,
                partition_dimensions=[classes[c] for c in partition_classes],
                floor_start=floor_start, floor_end=floor_end, used_bits=used, books=books)


def residue_sign(packet, channel, scalar):
    value = ((packet + 1) * 0x9e3779b9) ^ ((channel + 1) * 0x85ebca6b) ^ ((scalar + 1) * 0xc2b2ae35)
    value &= 0xffffffff
    value ^= value >> 16
    value = value * 0x7feb352d & 0xffffffff
    return (value ^ (value >> 15)) & 1


def inspect_audio(raw, setup, packet):
    r = Reader(raw); r.expect(1, 0); r.expect(1, MODES[packet])
    if MODES[packet]:
        r.expect(1, MODES[packet - 1] if packet else 0)
        r.expect(1, MODES[packet + 1] if packet < 13 else 0)
    value_range = RANGES[setup["multiplier"] - 1]
    width = (value_range - 1).bit_length()
    floors = []
    for channel in range(2):
        r.expect(1, 1)
        y0, y1 = r.take(width), r.take(width)
        if not (0 <= y0 < value_range and 0 <= y1 < value_range):
            raise ValueError("floor scalar bounds")
        codes = [r.take(1) for _ in setup["x_list"][2:]]
        floors.append((y0, y1, codes))
    for _ in range(2):
        r.expect(1, 0)
    for channel in range(2):
        for scalar in range(16):
            r.expect(1, residue_sign(packet, channel, scalar))
    used = r.position; r.end()
    return floors, used


def reconstruct_floor(xs, endpoints, codes, value_range):
    """Wide-integer spec prediction and activation, without renderer code."""
    ys, active = list(endpoints), [True, True] + [False] * len(codes)
    for i, code in enumerate(codes, 2):
        low = max((j for j in range(i) if xs[j] < xs[i]), key=lambda j: xs[j])
        high = min((j for j in range(i) if xs[j] > xs[i]), key=lambda j: xs[j])
        slope = ys[high] - ys[low]
        offset = abs(slope) * (xs[i] - xs[low]) // (xs[high] - xs[low])
        predicted = ys[low] + (offset if slope >= 0 else -offset)
        highroom, lowroom = value_range - predicted, predicted
        room = 2 * min(highroom, lowroom)
        if code:
            active[i] = active[low] = active[high] = True
            if code >= room:
                value = (code - lowroom + predicted if highroom > lowroom
                         else predicted - code + highroom - 1)
            else:
                value = predicted - (code + 1) // 2 if code & 1 else predicted + code // 2
        else:
            value = predicted
        if not 0 <= value < value_range:
            raise ValueError("reconstructed floor outside range")
        ys.append(value)
    return ys, active


def ogg_pages(raw):
    """Independent bounded Ogg page walk and polynomial CRC calculation."""
    pages, offset = [], 0
    while offset < len(raw):
        if len(raw) - offset < 27 or raw[offset:offset + 5] != b"OggS\0":
            raise ValueError("Ogg header")
        count = raw[offset + 26]
        laces = raw[offset + 27:offset + 27 + count]
        size = 27 + count + sum(laces)
        page = raw[offset:offset + size]
        if not count or len(laces) != count or laces[-1] == 255 or len(page) != size:
            raise ValueError("bounded one-packet Ogg page")
        checksum = int.from_bytes(page[22:26], "little")
        value = 0
        for octet in page[:22] + bytes(4) + page[26:]:
            value ^= octet << 24
            for _ in range(8):
                value = (value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)
                value &= 0xffffffff
        if value != checksum:
            raise ValueError("CRC mismatch")
        flags, granule, serial, sequence = struct.unpack_from("<BQII", page, 5)
        if sequence != len(pages):
            raise ValueError("Ogg sequence")
        pages.append(dict(flags=flags, granule=granule, serial=serial,
                          packet=page[27 + count:], crc=f"{checksum:08x}"))
        offset += size
    return pages


def c_array(header, name):
    found = re.search(r"\b" + re.escape(name) + r"\[[^]]+\]\s*=\s*\{([^}]+)\}", header)
    if not found:
        raise ValueError("missing C array " + name)
    return [int(x.strip(), 0) for x in found.group(1).split(",") if x.strip()]


class Floor1SlopesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = ROOT / ".build" / ("floor1-slopes-host-tests-" + uuid.uuid4().hex)
        cls.result = g.generate(cls.output)
        cls.matrix = json.loads((cls.output / "matrix.json").read_text())
        cls.fields = json.loads((cls.output / "bitfields.json").read_text())

    @classmethod
    def tearDownClass(cls):
        target, build = cls.output.resolve(), (ROOT / ".build").resolve()
        if target.parent != build or not target.name.startswith("floor1-slopes-host-tests-"):
            raise ValueError("owned test cleanup boundary")
        shutil.rmtree(target)

    def test_exact_matrix_geometry_scalar_ranges_and_rejections(self):
        expected = [(1, 0, [], 160, 255), (1, 15, [5, 1, 3], 255, 160),
            (2, 1, [], 80, 127), (2, 10, [300, 1, 1023], 127, 80),
            (3, 3, [5, 1, 3], 54, 85), (3, 7, [64, 1, 127], 85, 54),
            (4, 7, [64, 1, 127], 40, 63), (4, 10, [300, 1, 1023], 63, 40)]
        invalid = [(1, [0]), (3, [2, 2]), (3, [5, 1, 5]), (0, [0]),
                   (7, list(range(1, 65))), (8, list(range(1, 249)))]
        cases = self.matrix["cases"]
        self.assertEqual(len(cases), 14); self.assertEqual(len({c["id"] for c in cases}), 14)
        self.assertEqual([(c["multiplier"], c["rangebits"], c["interior"], c["y0"], c["y1"])
                          for c in cases[:8]], expected)
        self.assertEqual([(c["rangebits"], c["interior"]) for c in cases[8:]], invalid)
        for i, case in enumerate(cases):
            actual = inspect_setup((self.output / case["setup"]).read_bytes())
            self.assertEqual(actual["x_list"], [0, 1 << case["rangebits"]] + case["interior"])
            valid = len(actual["x_list"]) <= 65 and len(set(actual["x_list"])) == len(actual["x_list"])
            self.assertEqual(valid, i < 8); self.assertEqual(case["expected_valid"], valid)
            self.assertEqual(case["pcm_expectations_apply"], valid)
            if not valid:
                self.assertEqual((case["multiplier"], case["y0"], case["y1"]), (1, 160, 255))
            for key in ("multiplier", "rangebits", "partition_classes", "partition_dimensions", "class_dimensions"):
                self.assertEqual(actual[key], case[key])
        self.assertEqual(cases[12]["partition_dimensions"], [8] * 8)
        self.assertEqual(cases[13]["partition_dimensions"], [8] * 31)
        self.assertNotEqual(cases[1]["x_list"], sorted(cases[1]["x_list"]))

    def test_full_audio_floor_posts_predictions_and_residue_framing(self):
        activation = set()
        for case in self.matrix["cases"]:
            setup = inspect_setup((self.output / case["setup"]).read_bytes())
            raw = (self.output / case["audio"]).read_bytes(); offsets = case["offsets"]
            self.assertEqual((len(offsets), offsets[0], offsets[-1]), (15, 0, len(raw)))
            self.assertTrue(all(a < b for a, b in zip(offsets, offsets[1:])))
            for packet, (a, b) in enumerate(zip(offsets, offsets[1:])):
                floors, used = inspect_audio(raw[a:b], setup, packet)
                self.assertEqual(used, self.fields["audio"][case["id"]][packet]["used_bits"])
                for channel, (y0, y1, codes) in enumerate(floors):
                    self.assertEqual((y0, y1), (case["y0"], case["y1"]))
                    self.assertEqual(codes, [(packet + channel + i) % 2 for i in range(len(case["interior"]))])
                    if case["expected_valid"]:
                        ys, active = reconstruct_floor(setup["x_list"], (y0, y1), codes, case["value_range"])
                        self.assertEqual(len(ys), len(setup["x_list"]))
                        self.assertTrue(all(0 <= y * case["multiplier"] <= 255 for y in ys))
                        activation.update(active[2:])
        self.assertEqual(activation, {False, True})
        self.assertGreater(len({tuple(c["offsets"]) for c in self.matrix["cases"]}), 2)
        self.assertEqual(len({(self.output / c["audio"]).read_bytes() for c in self.matrix["cases"][:8]}), 8)

    def test_all_field_audits_complete_headers_and_scalar_negative_controls(self):
        info = (self.output / "identification.bin").read_bytes()
        self.assertEqual((info[:7], len(info), info[11], int.from_bytes(info[12:16], "little")),
                         (b"\x01vorbis", 30, 2, 48000))
        self.assertEqual((info[7:11], info[16:28]), (bytes(4), bytes(12)))
        self.assertEqual((self.output / "info.bin").read_bytes(), info[7:])
        self.assertEqual((info[28], info[29]), (0xb8, 1))
        comment = (self.output / "comment.bin").read_bytes()
        self.assertEqual(comment[:7], b"\x03vorbis")
        vendor = int.from_bytes(comment[7:11], "little")
        self.assertEqual(comment[11 + vendor:], bytes(4) + b"\x01")
        audits = [(info, self.fields["identification"]), (comment, self.fields["comment"])]
        for case in self.matrix["cases"]:
            full = (self.output / case["setup"]).read_bytes()
            self.assertEqual((self.output / case["setup_raw"]).read_bytes(), full[7:])
            actual = inspect_setup(full)
            audit = self.fields["setup"][case["id"]]
            self.assertEqual(actual["used_bits"], audit["used_bits"])
            self.assertEqual((next(f["offset"] for f in audit["fields"] if f["name"] == "floor[0].partitions"),
                              next(f["offset"] for f in audit["fields"] if f["name"] == "residue_count_minus_1")),
                             (actual["floor_start"], actual["floor_end"]))
            audits.append((full, audit))
            audio = (self.output / case["audio"]).read_bytes()
            for i, (a, b) in enumerate(zip(case["offsets"], case["offsets"][1:])):
                audits.append((audio[a:b], self.fields["audio"][case["id"]][i]))
        for raw, audit in audits:
            packed = int.from_bytes(raw, "little"); cursor = 0
            self.assertEqual(len(raw), audit["bytes"])
            for field in audit["fields"]:
                self.assertEqual(field["offset"], cursor)
                self.assertEqual((packed >> cursor) & ((1 << field["width"]) - 1), field["value"])
                cursor += field["width"]
            self.assertEqual(cursor, audit["used_bits"])
            self.assertEqual(packed >> cursor, 0)
        case = self.matrix["cases"][4]  # multiplier3 has unused 7-bit scalar codes.
        setup = inspect_setup((self.output / case["setup"]).read_bytes())
        raw = (self.output / case["audio"]).read_bytes()[:case["offsets"][1]]
        field = next(f for f in self.fields["audio"][case["id"]][0]["fields"] if f["name"] == "floor[0].y0")
        packed = int.from_bytes(raw, "little") | (127 << field["offset"])
        with self.assertRaisesRegex(ValueError, "scalar bounds"):
            inspect_audio(packed.to_bytes(len(raw), "little"), setup, 0)
        for bad in (full[:-1], full + b"\0", b"\0" + full[1:]):
            with self.assertRaises(ValueError):
                inspect_setup(bad)

    def test_ogg_crc_packets_and_genuine_overlap_granules(self):
        blocks = [2048 if mode else 256 for mode in MODES]
        frames = [0] + [(a + b) // 4 for a, b in zip(blocks, blocks[1:])]
        total, granules = 0, []
        for count in frames:
            total += count; granules.append(total)
        self.assertEqual((total, total * 4 * 8), (7040, 225280))
        for i, case in enumerate(self.matrix["cases"]):
            raw = (self.output / case["ogg"]).read_bytes(); pages = ogg_pages(raw)
            self.assertEqual(len(pages), 17)
            self.assertEqual([p["flags"] for p in pages], [2] + [0] * 15 + [4])
            self.assertEqual({p["serial"] for p in pages}, {0x46530001 + i})
            self.assertEqual([p["granule"] for p in pages], [0, 0, 0] + granules)
            self.assertEqual([p["crc"] for p in pages], case["page_crc32"])
            self.assertEqual([p["packet"] for p in pages[:3]], [(self.output / name).read_bytes()
                             for name in ("identification.bin", "comment.bin", case["setup"])])
            audio = (self.output / case["audio"]).read_bytes()
            self.assertEqual([p["packet"] for p in pages[3:]],
                             [audio[a:b] for a, b in zip(case["offsets"], case["offsets"][1:])])
            self.assertEqual(case["expected_packet_bytes"], [n * 4 for n in frames])
            self.assertEqual(case["expected_packet_samples"], frames)
            self.assertEqual(case["expected_s16le_bytes"], 28160)
            self.assertEqual(case["expected_raw_samples"], total)
            self.assertEqual(case["packet_granules"], granules)
            with self.assertRaisesRegex(ValueError, "CRC mismatch"):
                ogg_pages(raw[:-1] + bytes([raw[-1] ^ 1]))

    def test_c_interface_per_case_audio_and_raw_payloads(self):
        header = (self.output / "fixture.h").read_text()
        for text in ("#define FIXTURE_CASES 14", "#define FIXTURE_PACKETS 14",
                     "#define FIXTURE_PCM_BYTES 28160", "#define FLOOR1_PER_CASE_AUDIO 1",
                     "#define fixture_packets fixture_packets_0", "#define fixture_offsets fixture_offsets_0"):
            self.assertIn(text, header)
        self.assertIn("const uint8_t *packets; const uint32_t *offsets;", header)
        self.assertEqual(bytes(c_array(header, "fixture_info")), (self.output / "info.bin").read_bytes())
        self.assertEqual(c_array(header, "fixture_modes"), MODES)
        self.assertEqual(c_array(header, "fixture_expected_bytes"), self.matrix["cases"][0]["expected_packet_bytes"])
        rows = re.findall(r'\{"([^\"]+)", fixture_setup_(\d+), sizeof\(fixture_setup_(\d+)\), (true|false), fixture_packets_(\d+), fixture_offsets_(\d+)\}', header)
        self.assertEqual(rows, [(c["id"], str(i), str(i), str(c["expected_valid"]).lower(), str(i), str(i))
                                for i, c in enumerate(self.matrix["cases"])])
        for i, case in enumerate(self.matrix["cases"]):
            self.assertEqual(bytes(c_array(header, f"fixture_setup_{i}")), (self.output / case["setup_raw"]).read_bytes())
            self.assertEqual(bytes(c_array(header, f"fixture_packets_{i}")), (self.output / case["audio"]).read_bytes())
            self.assertEqual(c_array(header, f"fixture_offsets_{i}"), case["offsets"])
        self.assertEqual((self.output / self.matrix["audio"]).read_bytes(), (self.output / self.matrix["cases"][0]["audio"]).read_bytes())
        self.assertEqual(self.matrix["offsets"], self.matrix["cases"][0]["offsets"])

    def test_manifest_complete_pending_and_reproducible_create_only(self):
        manifest = json.loads((self.output / "manifest.json").read_text())
        actual = {str(p.relative_to(self.output)).replace("\\", "/") for p in self.output.rglob("*") if p.is_file()}
        self.assertEqual(len(actual), 64)
        self.assertEqual(actual, {r["path"] for r in manifest["files"]} | {"manifest.json"})
        for row in manifest["files"]:
            data = (self.output / row["path"]).read_bytes()
            self.assertEqual((len(data), hashlib.sha256(data).hexdigest()), (row["bytes"], row["sha256"]))
        self.assertEqual(manifest["generator_sha256"], hashlib.sha256(SOURCE.read_bytes()).hexdigest())
        self.assertEqual(manifest["helper"], dict(path="tests/vorbis_block_matrix/generate_minimal.py", sha256=g.BASE_SHA))
        for row, case in zip(manifest["cases"], self.matrix["cases"]):
            self.assertEqual(row, dict(case, setup_bitfields=self.fields["setup"][case["id"]],
                                      audio_bitfields=self.fields["audio"][case["id"]]))
        for key in ("decoder_execution", "independent_reference_qualification", "target_qualification"):
            self.assertIs(self.matrix[key], False)
        self.assertEqual(self.matrix["expected_valid_pcm_bytes"], 225280)
        self.assertEqual((self.matrix["valid_cases"], self.matrix["invalid_cases"],
                          self.matrix["valid_raw_packet_count"]), (8, 6, 112))
        self.assertIs(manifest["construction_only"], True)
        self.assertEqual(g.payloads(), {name: (self.output / name).read_bytes() for name in actual})
        before = {name: (self.output / name).read_bytes() for name in actual}
        with self.assertRaisesRegex(ValueError, "fresh beneath"):
            g.generate(self.output)
        self.assertEqual(before, {name: (self.output / name).read_bytes() for name in actual})

    def test_output_and_geometry_boundaries(self):
        for path in (ROOT / ".build", ROOT / "outside-floor1-slopes", ROOT / ".build/../outside-floor1-slopes"):
            with self.assertRaisesRegex(ValueError, "fresh beneath"):
                g.generate(path)
        for bits, xs, mult in ((0, [1], 1), (15, [32768], 1), (8, list(range(249)), 1), (3, [], 5)):
            with self.assertRaisesRegex(ValueError, "representable"):
                g.setup(dict(rangebits=bits, interior=xs, multiplier=mult))
        for y in (-1, 86, 127):
            with self.assertRaisesRegex(ValueError, "scalar bounds"):
                g.audio(dict(multiplier=3, y0=y, y1=85, interior=[]), 0)


if __name__ == "__main__":
    unittest.main()
