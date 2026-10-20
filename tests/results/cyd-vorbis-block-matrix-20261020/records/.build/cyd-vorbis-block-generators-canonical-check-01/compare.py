"""Pure byte/metadata comparison; never import generators or invoke codecs."""
import copy
import hashlib
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANONICAL = ROOT / "tests/vorbis_block_matrix"
REPORT = HERE / "report.json"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def crc(data):
    value = 0
    for octet in data:
        value ^= octet << 24
        for _ in range(8):
            value = ((value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)) & 0xffffffff
    return value


def packets(data):
    result = []
    pending = bytearray()
    position = 0
    sequence = 0
    while position < len(data):
        assert data[position:position + 5] == b"OggS\0"
        count = data[position + 26]
        laces = data[position + 27:position + 27 + count]
        end = position + 27 + count + sum(laces)
        assert len(laces) == count and end <= len(data)
        page = bytearray(data[position:end])
        assert struct.unpack_from("<I", page, 18)[0] == sequence
        assert bool(page[5] & 1) == bool(pending)
        expected = struct.unpack_from("<I", page, 22)[0]
        page[22:26] = bytes(4)
        assert crc(page) == expected
        offset = 27 + count
        for size in laces:
            pending.extend(page[offset:offset + size])
            offset += size
            if size < 255:
                result.append(bytes(pending))
                pending.clear()
        position = end
        sequence += 1
    assert not pending and position == len(data)
    return result


def differences(before, after, prefix=""):
    if isinstance(before, dict) and isinstance(after, dict):
        assert set(before) == set(after), prefix
        result = []
        for key in before:
            result += differences(before[key], after[key], prefix + "/" + str(key))
        return result
    if isinstance(before, list) and isinstance(after, list):
        assert len(before) == len(after), prefix
        result = []
        for i, (left, right) in enumerate(zip(before, after)):
            result += differences(left, right, prefix + "/" + str(i))
        return result
    return [] if before == after else [dict(pointer=prefix, before=before, after=after)]


def row(old_path, new_path, kind):
    old, new = old_path.read_bytes(), new_path.read_bytes()
    return dict(historical=str(old_path), canonical_output=str(new_path), kind=kind,
                historical_bytes=len(old), canonical_bytes=len(new),
                historical_sha256=digest(old), canonical_sha256=digest(new),
                byte_equal=old == new)


def verify_inputs(rows):
    for source in rows:
        data = Path(source["path"]).read_bytes()
        assert len(data) == source["bytes"] and digest(data) == source["sha256"], source["path"]


def main():
    assert not REPORT.exists(), "Comparison report already exists"
    report = dict(schema="vorbis-canonical-generator-byte-reproduction-v1", completed=False,
                  comparison_passed=False, scope="Pure stdlib generation/byte comparison only",
                  codec_sdk_compiler_qemu_git_executed=False, codec_qualification_claimed=False,
                  verifier_sha256=digest(Path(__file__).read_bytes()), commands=[],
                  files=[], raw_packet_comparisons=[], metadata_deltas=[], failures=[])
    try:
        before, after = load(HERE / "inputs-before.json"), load(HERE / "inputs-after.json")
        assert before == after
        verify_inputs(before)
        report["frozen_input_count"] = len(before)
        report["frozen_inputs_stable_before_comparison"] = True
        for name in ("minimal-48000", "minimal-192000", "encoder-72"):
            path = HERE / (name + ".command.json")
            command = load(path)
            assert command["returncode"] == 0 and not command["codec_tools_executed"]
            for stream in ("stdout", "stderr"):
                saved = command[stream]
                raw = Path(saved["path"]).read_bytes()
                assert len(raw) == saved["bytes"] and digest(raw) == saved["sha256"]
            assert command["stderr"]["bytes"] == 0
            report["commands"].append(dict(path=str(path), sha256=digest(path.read_bytes()),
                                            argv=command["argv"], returncode=0))
        for name, historical in (("minimal-48000", ".build/cyd-vorbis-minimal-block-prep-01/generated01"),
                                 ("minimal-192000", ".build/cyd-vorbis-minimal-block-rate-prep-01/generated01")):
            old_dir, new_dir = ROOT / historical, HERE / name
            old_files = {p.relative_to(old_dir).as_posix() for p in old_dir.rglob("*") if p.is_file()}
            new_files = {p.relative_to(new_dir).as_posix() for p in new_dir.rglob("*") if p.is_file()}
            assert old_files == new_files and len(old_files) == 80
            for relative in sorted(old_files):
                record = row(old_dir / relative, new_dir / relative,
                             "minimal manifest identity" if relative == "manifest.json" else "exact payload")
                report["files"].append(record)
                if relative == "manifest.json":
                    left, right = load(old_dir / relative), load(new_dir / relative)
                    delta = differences(left, right)
                    assert len(delta) == 1 and delta[0]["pointer"] == "/generator_sha256"
                    assert right["generator_sha256"] == digest((CANONICAL / "generate_minimal.py").read_bytes())
                    report["metadata_deltas"].append(dict(file=name + "/manifest.json", differences=delta))
                else:
                    assert record["byte_equal"], record
            matrix = load(new_dir / "matrix.json")
            assert len(matrix["cases"]) == 36
            for case in matrix["cases"]:
                left = packets((old_dir / case["ogg"]).read_bytes())
                right = packets((new_dir / case["ogg"]).read_bytes())
                assert left == right and len(right) == 17
                assert right[0] == (new_dir / "cases" / case["id"] / "identification.bin").read_bytes()
                assert right[1] == (new_dir / "comment.bin").read_bytes()
                assert right[2] == (new_dir / "setup.bin").read_bytes()
                assert b"".join(right[3:]) == (new_dir / "audio.bin").read_bytes()
                report["raw_packet_comparisons"].append(dict(corpus=name, id=case["id"],
                    header_packets=3, audio_packets=14, all_packets_byte_equal=True,
                    audio_sha256=digest(b"".join(right[3:]))))
        old_dir, new_dir = ROOT / ".build/cyd-vorbis-block-candidates-01", HERE / "encoder-72"
        old_json, new_json = old_dir / "candidates.json", new_dir / "candidates.json"
        left, right = load(old_json), load(new_json)
        assert len(left["cases"]) == len(right["cases"]) == 72
        assert left["tools"] == right["tools"]
        expected = copy.deepcopy(left)
        assert Path(left["source"]) == ROOT / ".build/cyd-vorbis-format-prep-01/reference/encoder-192000.ogg"
        expected["source"] = str(CANONICAL / "encoder-192000.ogg")
        expected_names = {"candidates.json"}
        for old_case, new_case, expected_case in zip(left["cases"], right["cases"], expected["cases"]):
            assert old_case["id"] == new_case["id"]
            relative = old_case["ogg"]
            expected_names.add(relative)
            old_path, new_path = old_dir / relative, new_dir / relative
            assert old_case["path"] == str(old_path)
            expected_case["path"] = str(new_path)
            assert [c["name"] for c in old_case["commands"]] == ["packet-frame-probe", "decode-vorbis", "decode-libvorbis"]
            for i, (old_command, expected_command) in enumerate(zip(old_case["commands"], expected_case["commands"])):
                if i == 0:
                    assert old_command["argv"][-1] == str(old_path)
                    expected_command["argv"][-1] = str(new_path)
                    assert "wav" not in old_command
                else:
                    argv = old_command["argv"]
                    assert argv.count("-i") == 1
                    index = argv.index("-i") + 1
                    assert argv[index] == str(old_path)
                    old_wav = old_dir / "pcm" / (old_path.stem + ("-vorbis.wav" if i == 1 else "-libvorbis.wav"))
                    new_wav = new_dir / "pcm" / old_wav.name
                    assert old_command["wav"] == argv[-1] == str(old_wav)
                    expected_command["argv"][index] = str(new_path)
                    expected_command["argv"][-1] = str(new_wav)
                    expected_command["wav"] = str(new_wav)
            record = row(old_path, new_path, "exact encoded Ogg")
            report["files"].append(record)
            assert record["byte_equal"] and record["canonical_sha256"] == old_case["sha256"] == new_case["sha256"]
            old_packets, new_packets = packets(old_path.read_bytes()), packets(new_path.read_bytes())
            assert old_packets == new_packets and len(new_packets) == old_case["packet_count"] + 3
            report["raw_packet_comparisons"].append(dict(corpus="encoder-72", id=old_case["id"],
                header_packets=3, audio_packets=len(new_packets) - 3, all_packets_byte_equal=True,
                audio_sha256=digest(b"".join(new_packets[3:]))))
        assert expected == right, differences(expected, right)
        assert {p.relative_to(new_dir).as_posix() for p in new_dir.rglob("*") if p.is_file()} == expected_names
        delta = differences(left, right)
        assert len(delta) == 577
        report["metadata_deltas"].append(dict(file="encoder-72/candidates.json", differences=delta))
        report["files"].append(row(old_json, new_json, "encoder path metadata only"))
        assert len(report["files"]) == 233
        assert sum(f["byte_equal"] for f in report["files"]) == 230
        assert len(report["raw_packet_comparisons"]) == 144
        verify_inputs(before)
        report["frozen_inputs_stable_after_comparison"] = True
        report["counts"] = dict(cases=144, minimal_cases=72, encoder_cases=72,
            output_files=233, byte_equal_files=230, metadata_only_files=3,
            metadata_value_deltas=sum(len(r["differences"]) for r in report["metadata_deltas"]),
            byte_equal_ogg_files=144,
            raw_header_packets=sum(r["header_packets"] for r in report["raw_packet_comparisons"]),
            raw_audio_packets=sum(r["audio_packets"] for r in report["raw_packet_comparisons"]))
        report["comparison_passed"] = True
        report["completed"] = True
        report["limits"] = "Reproduction only; independent decode results belong to the historical corpus. No new codec, target, full G6 or physical claim."
    except BaseException as error:
        report["failures"].append(dict(type=type(error).__name__, message=str(error)))
        raise
    finally:
        with REPORT.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, indent=2)
            stream.write("\n")
        print(json.dumps(dict(report=str(REPORT), report_sha256=digest(REPORT.read_bytes()),
                             completed=report["completed"], comparison_passed=report["comparison_passed"],
                             counts=report.get("counts"), failures=report["failures"])))


if __name__ == "__main__":
    main()
