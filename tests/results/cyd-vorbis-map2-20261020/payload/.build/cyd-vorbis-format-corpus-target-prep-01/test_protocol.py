"""Synthetic protocol/source-data checks only. No target/compiler/codec process."""
import argparse
import copy
import json
from pathlib import Path
import unittest

import protocol as P

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = [dict(path=str(ROOT / ".build/cyd-vorbis-books-prep-01/generated01/matrix.json"),
             sha256="38e38f1f5ada7cd84a6ea91c5b46e0680ee62a7f511c9a72bfa7b6d7eb64cd2e"),
        dict(path=str(ROOT / ".build/cyd-vorbis-floor0-prep-01/generated01/matrix.json"),
             sha256="aa1231b8813ac193767c85a2ef339a2da36af52f2af157a16cda9f3d2d438f07")]
ATTEMPT = None
CONTROLS = []


def event(name, **fields):
    return P.PREFIX + name + " " + " ".join(f"{k}={v}" for k, v in fields.items())


def synthetic(contract):
    lines = [event("BEGIN", contract=contract["contract_sha256"], cases=17, packets=238, coordinator=0),
             event("WORKER", core=1, priority=3, configured_stack=16384)]
    for index, case in enumerate(contract["model"]["cases"]):
        lines.append(event("OPEN", case=index, id=case["id"], vendor_rc=0, checked_rc=0,
                           vendor_handle=1, checked_handle=1, distinct=1, core=1))
        nz = 0
        for packet in range(14):
            size, pcm, frames = case["sizes"][packet], case["pcm"][packet], case["frames"][packet]
            lines.append(event("PAIR", case=index, packet=packet, size=size, vendor_rc=0, checked_rc=0,
                vendor_consumed=size, checked_consumed=size, expected_pcm=pcm, vendor_pcm=pcm, checked_pcm=pcm,
                vendor_rate=case["rate"], checked_rate=case["rate"], vendor_channels=2, checked_channels=2,
                vendor_bits=16, checked_bits=16, equal=1, vendor_canary=1, checked_canary=1,
                vendor_first=1, transition=case["transitions"][packet], nz_l=frames, nz_r=frames, core=1))
            data = bytes([index + 1, 0, index + 2, 0]) * frames
            lines.append(event("PCM_HEX", case=index, packet=packet, bytes=pcm, core=1, hex=data.hex()))
            nz += frames
        lines += [event("CLOSE", case=index, vendor_rc=0, checked_rc=0, core=1),
                  event("CASE", case=index, id=case["id"], packets=14, pcm=case["total_pcm"],
                        nz_l=nz, nz_r=nz, transitions_mask=15, core=1)]
    lines.append(event("COMPLETE", cases=17, packets=238, pcm=contract["model"]["total_pcm"], cases_mask=131071, core=1))
    return "\n".join(lines) + "\n"


def change(log, name, field, value, *, packet=None):
    lines = log.splitlines()
    for i, line in enumerate(lines):
        if not line.startswith(P.PREFIX + name + " ") or (packet is not None and f" packet={packet} " not in line):
            continue
        parts = line.split(" ")
        found = False
        for j, token in enumerate(parts[1:], 1):
            if token.startswith(field + "="):
                parts[j] = field + "=" + str(value); found = True; break
        if not found:
            raise AssertionError((name, field))
        lines[i] = " ".join(parts)
        return "\n".join(lines) + "\n"
    raise AssertionError(name)


class ProtocolChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = P.load_contract(PINS)
        cls.log = synthetic(cls.contract)

    def validate(self, log=None, contract=None, **facts):
        values = dict(returncode=0, timed_out=False, interrupted=False,
                      manifest_hashes=self.contract["model"]["manifest_sha256"])
        values.update(facts)
        return P.validate_log(self.log if log is None else log, contract or self.contract, **values)

    def rejected(self, name, log=None, contract=None, **facts):
        CONTROLS.append(name)
        with self.subTest(control=name):
            with self.assertRaises((RuntimeError, ValueError, KeyError)):
                self.validate(log, contract, **facts)

    def test_complete_synthetic_and_actual_capture(self):
        result = self.validate()
        self.assertEqual(result["protocol_lines"], 530)
        self.assertEqual(result["paired_packets"], 238)
        self.assertEqual(result["pcm"], 398080)
        self.assertEqual(result["case_mask"], 131071)
        self.assertFalse(result["independent_reference_compared"])
        self.assertEqual(len(result["case_pcm"]), 17)
        self.assertEqual(sum(len(c["pcm"]) for c in result["case_pcm"]), 398080)
        for output, case in zip(result["case_pcm"], self.contract["model"]["cases"]):
            self.assertEqual(output["sha256"], P.sha(output["pcm"]))
            self.assertEqual(output["packet_offsets"][0:2], [0, 0])
            self.assertEqual(output["packet_offsets"][-1], case["total_pcm"])

    def test_pcm_is_returned_not_replaced_or_numerically_qualified(self):
        original = self.validate()["case_pcm"][0]
        lines = self.log.splitlines()
        for i, line in enumerate(lines):
            if line.startswith(P.PREFIX + "PCM_HEX case=0 packet=1 "):
                prefix, value = line.split("hex=")
                lines[i] = prefix + "hex=7f" + value[2:]
                break
        output = self.validate("\n".join(lines) + "\n")["case_pcm"][0]
        self.assertNotEqual(original["sha256"], output["sha256"])
        self.assertEqual(output["pcm"][0], 127)
        self.assertNotEqual(original["pcm"], output["pcm"])

    def test_real_process_fact_requirements(self):
        for key, values in (("returncode", [1, -1, None, True]),
                            ("timed_out", [True, None, 0]), ("interrupted", [True, None, 0])):
            for value in values:
                self.rejected(f"process-{key}-{value!r}", **{key: value})
        self.rejected("wrong-manifest-fact", manifest_hashes=["0" * 64] * 2)
        self.rejected("missing-manifest-facts", manifest_hashes=None)

    def test_contract_identity_and_source_hash(self):
        pins = copy.deepcopy(PINS); pins[0]["sha256"] = "0" * 64
        with self.assertRaises(RuntimeError): P.load_contract(pins)
        for key in ("contract_sha256", "source_facts", "model"):
            changed = copy.deepcopy(self.contract)
            if key == "model": changed[key]["total_pcm"] -= 4
            elif key == "source_facts": changed[key][0]["sha256"] = "0" * 64
            else: changed[key] = "0" * 64
            self.rejected("tampered-contract-" + key, contract=changed)
        self.rejected("wrong-begin-hash", change(self.log, "BEGIN", "contract", "0" * 64))

    def test_order_count_prefix_and_panic(self):
        lines = self.log.splitlines()
        self.rejected("missing-pair", "\n".join(lines[:3] + lines[4:]))
        self.rejected("duplicate-complete", self.log + lines[-1] + "\n")
        self.rejected("early-complete", "\n".join(lines[:2] + [lines[-1]] + lines[2:-1]))
        self.rejected("foreign-prefix", self.log.replace("CYD_VORBIS_CORPUS_BEGIN", "C3_VORBIS_CORPUS_BEGIN", 1))
        self.rejected("malformed-prefix", "noise " + self.log)
        self.rejected("panic-after-complete", self.log + "Guru Meditation Error\n")
        self.rejected("generic-36pair-mask", change(self.log, "COMPLETE", "cases_mask", (1 << 36) - 1))
        self.rejected("missing-named-case", change(self.log, "COMPLETE", "cases", 16))
        self.rejected("missing-paired-packet-count", change(self.log, "BEGIN", "packets", 237))
        self.rejected("worker-priority", change(self.log, "WORKER", "priority", 4))
        self.rejected("worker-stack", change(self.log, "WORKER", "configured_stack", 6144))

    def test_actual_pair_close_fields(self):
        controls = [("vendor_rc", -1), ("checked_rc", -1), ("vendor_consumed", 0),
                    ("checked_consumed", 0), ("expected_pcm", 0), ("vendor_pcm", 0),
                    ("checked_pcm", 0), ("vendor_rate", 48000), ("checked_rate", 48000),
                    ("vendor_channels", 1), ("checked_channels", 1), ("vendor_bits", 8),
                    ("checked_bits", 8), ("equal", 0), ("vendor_canary", 0),
                    ("checked_canary", 0), ("vendor_first", 0), ("transition", 9),
                    ("core", 0), ("nz_l", 0), ("nz_r", 0), ("nz_l", 999999)]
        for field, value in controls:
            self.rejected(f"pair-{field}-{value}", change(self.log, "PAIR", field, value, packet=1))
        self.rejected("primer-nonzero", change(self.log, "PAIR", "nz_l", 1, packet=0))
        self.rejected("primer-metadata-reset", change(self.log, "PAIR", "checked_rate", 0, packet=0))
        self.rejected("close-vendor-nonzero", change(self.log, "CLOSE", "vendor_rc", -1))
        self.rejected("close-checked-nonzero", change(self.log, "CLOSE", "checked_rc", -1))
        self.rejected("close-wrong-core", change(self.log, "CLOSE", "core", 0))
        self.rejected("case-nonzero-total", change(self.log, "CASE", "nz_l", 1))
        self.rejected("case-byte-total", change(self.log, "CASE", "pcm", 0))
        self.rejected("open-alias", change(self.log, "OPEN", "distinct", 0))
        self.rejected("duplicate-field", self.log.replace("PAIR case=0 packet=0", "PAIR case=0 case=0 packet=0", 1))

    def test_hex_alphabet_length_order_and_counts(self):
        size = self.contract["model"]["cases"][0]["pcm"][1]
        for name, value in (("odd", "1" + "00" * (size - 1)), ("invalid", "gg" * size),
                            ("uppercase", "AB" * size), ("short", "00" * (size - 1)), ("empty", "")):
            self.rejected("hex-" + name, change(self.log, "PCM_HEX", "hex", value, packet=1))
        for field, value in (("case", 1), ("packet", 2), ("bytes", 0), ("core", 0)):
            self.rejected("hex-" + field, change(self.log, "PCM_HEX", field, value, packet=1))
        self.rejected("nonempty-primer", change(self.log, "PCM_HEX", "hex", "00", packet=0))
        self.rejected("hex-versus-nonzero-count", change(self.log, "PCM_HEX", "hex", "00" * size, packet=1))
        lines = self.log.splitlines(); lines[3], lines[4] = lines[4], lines[3]
        self.rejected("hex-before-pair", "\n".join(lines))

    def test_descriptor_malformed_raw_copies(self):
        matrix_path = Path(PINS[0]["path"])
        source = json.loads(matrix_path.read_text())["cases"][0]
        for name in ("id-prefix", "id-length", "setup-prefix", "mode", "offsets", "total", "raw-path"):
            directory = ATTEMPT / name; directory.mkdir()
            case = copy.deepcopy(source)
            for kind in ("identification", "setup", "audio"):
                data = (matrix_path.parent / case[kind]).read_bytes()
                case[kind] = kind + ".bin"
                if name == "id-prefix" and kind == "identification": data = b"\0" + data[1:]
                if name == "id-length" and kind == "identification": data = data[:-1]
                if name == "setup-prefix" and kind == "setup": data = b"\0" + data[1:]
                if name == "mode" and kind == "audio": data = bytes([data[0] | 1]) + data[1:]
                (directory / case[kind]).write_bytes(data)
            if name == "offsets": case["offsets"][1] = 0
            if name == "total": case["expected_s16le_bytes"] -= 4
            if name == "raw-path": case["audio"] = "../escape.bin"
            CONTROLS.append("descriptor-" + name)
            with self.subTest(control=name), self.assertRaises(RuntimeError):
                P.inspect_case(case, directory, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    ATTEMPT = args.output.resolve()
    if ATTEMPT.parent != HERE or ATTEMPT.exists():
        raise RuntimeError("Fresh direct-child test output required")
    ATTEMPT.mkdir()
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProtocolChecks))
    report = dict(schema="vorbis-corpus-synthetic-protocol-checks-v1", synthetic_only=True,
                  tests_run=result.testsRun, rejected_controls=CONTROLS, passed=result.wasSuccessful(),
                  failures=[text for test, text in result.failures], errors=[text for test, text in result.errors],
                  target_compiler_sdk_codec_executed=False)
    (ATTEMPT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if result.wasSuccessful() else 1)
