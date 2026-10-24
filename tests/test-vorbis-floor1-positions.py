"""Host construction checks only; no decoder, SDK, emulator or subprocess."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import unittest
import uuid

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tests/vorbis_format_corpus/generate_floor1_positions.py"
spec = importlib.util.spec_from_file_location("floor1_positions_generator", SOURCE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class Reader:
    def __init__(self, data):
        self.data, self.position = data, 0

    def take(self, width):
        if width < 0 or self.position + width > len(self.data) * 8:
            raise ValueError("bounded setup reader")
        value = (int.from_bytes(self.data, "little") >> self.position) & ((1 << width) - 1)
        self.position += width
        return value

    def expect(self, width, value):
        if self.take(width) != value:
            raise ValueError("unexpected complete setup field")


def inspect_setup(data):
    """Walk actual complete bytes, not construction field-offset metadata."""
    if data[:7] != b"\x05vorbis":
        raise ValueError("setup prefix")
    r = Reader(data); r.take(56); r.expect(8, 1)
    for number, entries in enumerate((1, 2)):
        for width, value in ((24, 0x564342), (16, 1), (24, entries), (1, 0), (1, 0)):
            r.expect(width, value)
        for _ in range(entries):
            r.expect(5, 0)
        r.expect(4, number)
        if number:
            for width, value in ((32, 0xe2800001), (32, 0x62800002), (4, 0), (1, 0), (1, 0), (1, 1)):
                r.expect(width, value)
    for width, value in ((6, 0), (16, 0), (6, 0), (16, 1)):
        r.expect(width, value)
    start = r.position
    partitions = r.take(5)
    partition_classes = [r.take(4) for _ in range(partitions)]
    classes = []
    for _ in range(max(partition_classes, default=-1) + 1):
        dim = r.take(3) + 1; r.expect(2, 0); r.expect(8, 0)
        classes.append(dim)
    multiplier, bits = r.take(2) + 1, r.take(4)
    count = sum(classes[cls] for cls in partition_classes)
    coordinate_start = r.position
    xs = [0, 1 << bits] + [r.take(bits) for _ in range(count)]
    end = r.position
    # Residue1, one submap/no coupling, two standard modes and framing.
    for width, value in ((6, 0), (16, 1), (24, 0), (24, 16), (24, 15), (6, 0),
            (8, 0), (3, 1), (1, 0), (8, 1), (6, 0), (16, 0), (1, 0), (1, 0),
            (2, 0), (8, 0), (8, 0), (8, 0), (6, 1)):
        r.expect(width, value)
    for mode in (0, 1):
        for width, value in ((1, mode), (16, 0), (16, 0), (8, 0)):
            r.expect(width, value)
    r.expect(1, 1)
    used = r.position
    if len(data) * 8 - used >= 8:
        raise ValueError("noncanonical setup suffix")
    r.expect(len(data) * 8 - used, 0)
    return dict(x_list=xs, rangebits=bits, multiplier=multiplier,
                partition_dimensions=[classes[c] for c in partition_classes],
                class_dimensions=classes, partition_classes=partition_classes,
                floor_start=start, floor_end=end, coordinate_start=coordinate_start, used_bits=used)


def c_array(header, name):
    body = re.search(r"\b" + re.escape(name) + r"\[[^]]+\]\s*=\s*\{([^}]+)\}", header).group(1)
    return [int(token.strip(), 0) for token in body.split(",") if token.strip()]


class Floor1PositionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output = ROOT / ".build" / ("floor1-positions-host-tests-" + uuid.uuid4().hex)
        cls.result = g.generate(cls.output)
        cls.matrix = json.loads((cls.output / "matrix.json").read_text())
        cls.fields = json.loads((cls.output / "bitfields.json").read_text())

    @classmethod
    def tearDownClass(cls):
        target = cls.output.resolve()
        build = (ROOT / ".build").resolve()
        if target.parent != build or not target.name.startswith("floor1-positions-host-tests-"):
            raise ValueError("owned test cleanup boundary")
        shutil.rmtree(target)

    def test_exact_requested_matrix_and_validity(self):
        cases = self.matrix["cases"]
        expected = [([], 0), ([1], 1), ([5, 1, 3], 3), (list(range(1, 63)), 7),
            (list(range(1, 64)), 7), (list(range(63, 0, -1)), 7),
            (list(range(1, 64, 2)) + list(range(2, 64, 2)), 7),
            ([1 + 503 * i for i in range(63)], 15), ([0], 1), ([2, 2], 3),
            ([5, 1, 5], 3), ([0], 0), (list(range(1, 65)), 7), (list(range(1, 249)), 8)]
        self.assertEqual(len(cases), 14)
        self.assertEqual(len({c["id"] for c in cases}), 14)
        self.assertEqual([(c["interior"], c["rangebits"]) for c in cases], expected)
        for index, case in enumerate(cases):
            actual = inspect_setup((self.output / case["setup"]).read_bytes())
            self.assertEqual(actual["x_list"], [0, 1 << expected[index][1]] + expected[index][0])
            valid = len(actual["x_list"]) <= 65 and len(set(actual["x_list"])) == len(actual["x_list"])
            self.assertEqual(valid, index < 8)
            self.assertEqual(case["expected_valid"], valid)
            self.assertEqual(case["pcm_expectations_apply"], valid)

    def test_raw_bitspans_class_dimensions_and_complete_framing(self):
        for case in self.matrix["cases"]:
            full = (self.output / case["setup"]).read_bytes()
            actual = inspect_setup(full)
            self.assertEqual((self.output / case["setup_raw"]).read_bytes(), full[7:])
            for key in ("x_list", "partition_dimensions", "class_dimensions", "partition_classes", "multiplier"):
                self.assertEqual(actual[key], case[key])
            self.assertLessEqual(len(actual["partition_dimensions"]), 31)
            self.assertEqual(sum(actual["partition_dimensions"]), len(case["interior"]))
            self.assertEqual(actual["used_bits"], self.fields["setup"][case["id"]]["used_bits"])
            fields = self.fields["setup"][case["id"]]["fields"]
            first = next(f for f in fields if f["name"] == "floor[0].partitions")
            following = next(f for f in fields if f["name"] == "residue_count_minus_1")
            self.assertEqual((first["offset"], following["offset"]), (actual["floor_start"], actual["floor_end"]))
        self.assertEqual(self.matrix["cases"][4]["partition_dimensions"], [8] * 7 + [7])
        self.assertEqual(self.matrix["cases"][12]["partition_dimensions"], [8] * 8)
        self.assertEqual(self.matrix["cases"][13]["partition_dimensions"], [8] * 31)

    def test_distinct_count_and_uniqueness_controls(self):
        actual = [inspect_setup((self.output / c["setup"]).read_bytes())["x_list"]
                  for c in self.matrix["cases"]]
        # Removing either normative predicate admits its specific malformed cases.
        self.assertEqual([i for i, xs in enumerate(actual) if len(set(xs)) == len(xs)], list(range(8)) + [12, 13])
        self.assertEqual([i for i, xs in enumerate(actual) if len(xs) <= 65], list(range(12)))
        self.assertNotEqual(actual[2], sorted(actual[2]))
        self.assertEqual(actual[11], [0, 1, 0])  # rangebits0 still represents x=0.
        self.assertEqual(actual[7][-1], 31187)

    def test_unchanged_audio_and_independent_overlap_arithmetic(self):
        audio = (self.output / "audio.bin").read_bytes()
        expected_packets = [g.base.audio(i).data() for i in range(14)]
        self.assertEqual(audio, b"".join(expected_packets))
        blocks = [256 if c == "S" else 2048 for c in "SSLLLSLSSSLLSS"]
        samples = [0] + [(blocks[i-1] + blocks[i]) // 4 for i in range(1, 14)]
        self.assertEqual(sum(samples), 7040)
        for case in self.matrix["cases"]:
            self.assertEqual(case["expected_packet_samples"], samples)
            self.assertEqual(case["expected_packet_bytes"], [n * 4 for n in samples])
            self.assertEqual(case["expected_s16le_bytes"], 28160)
            self.assertEqual([audio[a:b] for a, b in zip(case["offsets"], case["offsets"][1:])], expected_packets)

    def test_carrier_bytes_granules_flags_serial_and_crc(self):
        info = (self.output / "identification.bin").read_bytes()
        self.assertEqual(info[:7], b"\x01vorbis")
        self.assertEqual((len(info), (self.output / "info.bin").read_bytes()), (30, info[7:]))
        for index, case in enumerate(self.matrix["cases"]):
            stream = (self.output / case["ogg"]).read_bytes()
            pages = g.base.read_pages(stream)
            self.assertEqual(len(pages), 17)
            self.assertEqual([p["flags"] for p in pages], [2] + [0] * 15 + [4])
            self.assertEqual({p["serial"] for p in pages}, {0x46510001 + index})
            self.assertEqual([p["granule"] for p in pages], [0, 0, 0] + case["packet_granules"])
            self.assertEqual([p["packet"] for p in pages[:3]],
                [info, (self.output / "comment.bin").read_bytes(), (self.output / case["setup"]).read_bytes()])
            self.assertEqual([p["packet"] for p in pages[3:]], [g.base.audio(i).data() for i in range(14)])
            damaged = stream[:-1] + bytes([stream[-1] ^ 1])
            with self.assertRaisesRegex(ValueError, "CRC mismatch"):
                g.base.read_pages(damaged)

    def test_c_harness_arrays_match_raw_files_and_pcm_formula(self):
        h = (self.output / "fixture.h").read_text()
        self.assertIn("#define FIXTURE_CASES 14", h)
        self.assertIn("#define FIXTURE_PACKETS 14", h)
        self.assertIn("#define FIXTURE_PCM_BYTES 28160", h)
        self.assertEqual(bytes(c_array(h, "fixture_info")), (self.output / "info.bin").read_bytes())
        self.assertEqual(bytes(c_array(h, "fixture_packets")), (self.output / "audio.bin").read_bytes())
        self.assertEqual(c_array(h, "fixture_offsets"), self.matrix["offsets"])
        self.assertEqual(c_array(h, "fixture_modes"), [0 if c == "S" else 1 for c in "SSLLLSLSSSLLSS"])
        self.assertEqual(c_array(h, "fixture_expected_bytes"), self.matrix["cases"][0]["expected_packet_bytes"])
        rows = re.findall(r'\{"([^\"]+)", fixture_setup_(\d+), sizeof\(fixture_setup_\d+\), (true|false)\}', h)
        self.assertEqual([(name, int(index), valid == "true") for name, index, valid in rows],
                         [(c["id"], i, c["expected_valid"]) for i, c in enumerate(self.matrix["cases"])])
        for i, case in enumerate(self.matrix["cases"]):
            self.assertEqual(bytes(c_array(h, f"fixture_setup_{i}")), (self.output / case["setup_raw"]).read_bytes())

    def test_manifest_closure_pending_claims_and_determinism(self):
        manifest = json.loads((self.output / "manifest.json").read_text())
        actual = {str(p.relative_to(self.output)).replace("\\", "/") for p in self.output.rglob("*") if p.is_file()}
        self.assertEqual(actual, {r["path"] for r in manifest["files"]} | {"manifest.json"})
        for row in manifest["files"]:
            data = (self.output / row["path"]).read_bytes()
            self.assertEqual((len(data), hashlib.sha256(data).hexdigest()), (row["bytes"], row["sha256"]))
        self.assertEqual(manifest["cases"], [dict(case, setup_bitfields=self.fields["setup"][case["id"]])
                                            for case in self.matrix["cases"]])
        for key in ("decoder_execution", "independent_reference_qualification", "target_qualification"):
            self.assertIs(self.matrix[key], False)
        self.assertEqual(g.payloads(), {name: (self.output / name).read_bytes() for name in actual})

    def test_output_and_unrepresentable_geometry_guards(self):
        for path in (self.output, ROOT / ".build", ROOT / "outside-floor1-corpus",
                     ROOT / ".build" / ".." / "outside-floor1-corpus"):
            with self.assertRaisesRegex(ValueError, "fresh beneath"):
                g.generate(path)
        for case in (dict(interior=[1], rangebits=0), dict(interior=[32768], rangebits=15),
                     dict(interior=list(range(249)), rangebits=8)):
            with self.assertRaisesRegex(ValueError, "representable"):
                g.setup(case)
        raw = (self.output / self.matrix["cases"][0]["setup"]).read_bytes()
        for bad in (raw[:-1], raw + b"\0", b"\0" + raw[1:]):
            with self.assertRaises(ValueError):
                inspect_setup(bad)


if __name__ == "__main__":
    unittest.main()
