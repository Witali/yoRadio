"""Materialize the pinned 17-case public raw corpus; never execute a codec."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FROZEN = ROOT / ".build/cyd-vorbis-format-corpus-target-prep-01"
CONTRACT_FILE_SHA = "6c95b8d52a7bd5a3ca8e2d1b519f5d0ec3172e7e76e83ade8c1e78d364fdd391"
MODEL_SHA = "847022a7835de03c0f820b3f8e418e7e8b89b6125d2dba8bdf09712d33d3a65a"
PINS = {
    "contract.json": CONTRACT_FILE_SHA,
    "protocol.py": "7b9912db4d5317376c22d4ab1f65a206941f84f6773b07cf37a522a3bc7f35f8",
    "corpus_case.h": "91a040d89f3bc2b7740fa2f175f36d64cebcd92653cd4c2014149bbb11219be3",
    "main.c": "3ca8f85b8a2a9fad5c196143f4833da5fb9ce13b9b69351900b9eecc7e831f54",
}


def need(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(paths):
    result = []
    for path in sorted({p.resolve() for p in paths}):
        data = path.read_bytes()
        result.append(dict(path=str(path), bytes=len(data), sha256=sha(data)))
    return result


def load(contract_path):
    for name, expected in PINS.items():
        need(sha((FROZEN / name).read_bytes()) == expected, "frozen_source_pin:" + name)
    encoded = contract_path.read_bytes()
    need(sha(encoded) == CONTRACT_FILE_SHA, "contract_file_pin")
    contract = json.loads(encoded)
    need(contract["contract_sha256"] == MODEL_SHA, "model_identity")
    spec = importlib.util.spec_from_file_location("pinned_corpus_protocol", FROZEN / "protocol.py")
    protocol = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(protocol)  # Only pinned stdlib definitions; no target action.
    need(protocol.load_contract(contract["manifest_inputs"]) == contract, "current_contract_inputs")
    need(len(contract["model"]["cases"]) == 17 and contract["model"]["total_packets"] == 238
         and contract["model"]["total_pcm"] == 398080, "complete_17_case_model")
    items = []
    for source in contract["manifest_inputs"]:
        manifest = Path(source["path"])
        for case in json.loads(manifest.read_bytes())["cases"]:
            raw = {}
            for kind in ("identification", "setup", "audio"):
                path = (manifest.parent / case[kind]).resolve()
                need(path.is_relative_to(manifest.parent.resolve()), "raw_path_boundary")
                raw[kind] = path.read_bytes()
            items.append(raw)
    need(len(items) == 17, "raw_case_count")
    for case, raw in zip(contract["model"]["cases"], items):
        need({k: sha(v) for k, v in raw.items()} == case["raw_sha256"], "ordered_raw_payload_identity")
    return contract, items


def symbols(index):
    return {kind: f"corpus_{index:03d}_{kind}" for kind in ("identification", "setup", "audio", "offsets", "modes")}


def descriptor_fields(index, case):
    names = symbols(index)
    fields = {"id": json.dumps(case["id"])}
    for kind in ("identification", "setup", "audio"):
        fields[kind] = names[kind]
        fields[kind + "_size"] = f"sizeof({names[kind]})"
    for kind, count in (("offsets", "offset_count"), ("modes", "mode_count")):
        fields[kind] = names[kind]
        fields[count] = f"sizeof({names[kind]}) / sizeof({names[kind]}[0])"
    for field, value in (("rate", case["rate"]), ("channels", case["channels"]),
                         ("short_block", case["short"]), ("long_block", case["long"]),
                         ("expected_pcm_bytes", case["total_pcm"])):
        fields[field] = f"{value}U"
    return fields


def array(name, kind, values):
    tokens = [f"0x{x:02x}" if kind == "uint8_t" else f"{x}U" for x in values]
    lines = [f"static const {kind} {name}[{len(values)}] = {{"]
    for start in range(0, len(tokens), 12):
        lines.append("    " + ", ".join(tokens[start:start + 12]) + ",")
    return "\n".join(lines + ["};", ""])


def render(contract, items):
    text = ("// Generated complete raw inputs; source materialization only, not target qualification.\n"
            "#pragma once\n#include \"corpus_case.h\"\n\n"
            "#define CORPUS_CASE_COUNT 17U\n"
            f"#define CORPUS_CONTRACT_SHA256 \"{MODEL_SHA}\"\n"
            f"#define CORPUS_CONTRACT_FILE_SHA256 \"{CONTRACT_FILE_SHA}\"\n"
            "#define CORPUS_EXPECTED_PCM_BYTES 398080U\n\n")
    rows = []
    for index, (case, raw) in enumerate(zip(contract["model"]["cases"], items)):
        names = symbols(index)
        for kind in ("identification", "setup", "audio"):
            text += array(names[kind], "uint8_t", raw[kind])
        text += array(names["offsets"], "uint32_t", case["offsets"])
        text += array(names["modes"], "uint8_t", case["modes"])
        rows.append("    {\n" + "".join(f"        .{k} = {v},\n" for k, v in descriptor_fields(index, case).items()) + "    },\n")
    text += "static const corpus_case_t corpus_cases[CORPUS_CASE_COUNT] = {\n" + "".join(rows) + "};\n"
    return text, rows


def recover(text, contract, items):
    """Read the emitted restricted C grammar; no compiler, generator import or C evaluation."""
    for name, expected in (("CORPUS_CASE_COUNT", "17U"), ("CORPUS_EXPECTED_PCM_BYTES", "398080U"),
                           ("CORPUS_CONTRACT_SHA256", json.dumps(MODEL_SHA)),
                           ("CORPUS_CONTRACT_FILE_SHA256", json.dumps(CONTRACT_FILE_SHA))):
        found = re.findall(r"^#define " + name + r" (.+)$", text, re.M)
        need(found == [expected], "identity_macro:" + name)
    arrays = {}
    for match in re.finditer(r"static const (uint8_t|uint32_t) (corpus_[0-9]{3}_[a-z]+)\[([0-9]+)\] = \{\n(.*?)\n\};", text, re.S):
        kind, name, count, body = match.groups()
        need(name not in arrays, "duplicate_array")
        tokens = [token.strip() for token in body.split(",") if token.strip()]
        pattern = r"0x[0-9a-f]{2}" if kind == "uint8_t" else r"(?:0|[1-9][0-9]*)U"
        need(all(re.fullmatch(pattern, token) for token in tokens), "array_integer_grammar")
        values = [int(token.removesuffix("U"), 0) for token in tokens]
        need(len(values) == int(count), "array_declaration_count")
        arrays[name] = (kind, values)
    need(len(arrays) == 85, "all_85_arrays")
    table = re.findall(r"static const corpus_case_t corpus_cases\[CORPUS_CASE_COUNT\] = \{\n(.*?)\n\};", text, re.S)
    need(len(table) == 1, "one_descriptor_table")
    blocks = re.findall(r"    \{\n(.*?)    \},\n?", table[0], re.S)
    need(len(blocks) == 17, "all_17_descriptors")
    report, seen = [], set()
    for index, (case, raw, block) in enumerate(zip(contract["model"]["cases"], items, blocks)):
        names = symbols(index)
        expected_fields = descriptor_fields(index, case)
        fields = {}
        for line in block.splitlines():
            match = re.fullmatch(r"        \.([a-z_]+) = (.+),", line)
            need(match is not None, "descriptor_grammar")
            key, value = match.groups()
            need(key not in fields, "duplicate_descriptor_field")
            fields[key] = value
        need(list(fields.items()) == list(expected_fields.items()), "ordered_descriptor_fields")
        for kind in ("identification", "setup", "audio"):
            array_kind, values = arrays[names[kind]]; seen.add(names[kind])
            need(array_kind == "uint8_t" and bytes(values) == raw[kind], "raw_array_bytes:" + kind)
        offset_type, offsets = arrays[names["offsets"]]; seen.add(names["offsets"])
        mode_type, modes = arrays[names["modes"]]; seen.add(names["modes"])
        need(offset_type == "uint32_t" and offsets == case["offsets"], "offset_values")
        need(mode_type == "uint8_t" and modes == case["modes"], "mode_values")
        info = bytes(arrays[names["identification"]][1])
        setup, audio = (bytes(arrays[names[kind]][1]) for kind in ("setup", "audio"))
        need(len(info) == 30 and info[:7] == b"\x01vorbis" and setup[:7] == b"\x05vorbis", "full_header_recovery")
        rate, channels = int.from_bytes(info[12:16], "little"), info[11]
        short, long = 1 << (info[28] & 15), 1 << (info[28] >> 4)
        need((rate, channels, short, long) == (case["rate"], case["channels"], case["short"], case["long"]), "recovered_header_metadata")
        need(len(offsets) == 15 and len(modes) == 14 and offsets[0] == 0 and offsets[-1] == len(audio), "recovered_offset_shape")
        need(all(a < b <= len(audio) for a, b in zip(offsets, offsets[1:])), "recovered_offset_bounds")
        blocksizes = [long if flag else short for flag in modes]
        pcm = [0] + [(a + b) // 4 * channels * 2 for a, b in zip(blocksizes, blocksizes[1:])]
        need(pcm == case["pcm"] and sum(pcm) == case["total_pcm"], "recovered_pcm_accounting")
        report.append(dict(index=index, id=case["id"], symbols=names,
            payloads={kind: dict(bytes=len(raw[kind]), sha256=sha(raw[kind])) for kind in raw},
            offsets=offsets, modes=modes, rate=rate, channels=channels, short=short, long=long,
            expected_packet_pcm_bytes=pcm, expected_pcm_bytes=sum(pcm),
            stored_identification_bytes=30, public_info_payload_bytes=23,
            stored_prefixed_setup_bytes=len(setup), public_setup_payload_bytes=len(setup) - 7))
    need(set(arrays) == seen, "no_extra_or_missing_arrays")
    need(sum(row["expected_pcm_bytes"] for row in report) == 398080, "recovered_corpus_total")
    return report


def materialize(contract_path, output):
    contract_path, output = contract_path.resolve(), output.resolve()
    need(output.parent == HERE and not output.exists(), "fresh_direct_child_output")
    contract, items = load(contract_path)
    paths = [contract_path, Path(__file__), HERE / "README.md"] + [FROZEN / name for name in PINS]
    paths += [Path(row["path"]) for row in contract["source_facts"]]
    before = snapshot(paths)
    output.mkdir()
    report = dict(schema="public-vorbis-corpus-materialization-v1", completed=False, source_verified=False,
                  contract_file_sha256=CONTRACT_FILE_SHA, contract_model_sha256=MODEL_SHA,
                  codec_sdk_compiler_qemu_git_executed=False, target_qualification=False,
                  actual_PCM_synthesized=False, inputs_before=before, failures=[])
    try:
        text, rows = render(contract, items)
        header = output / "data.h"
        with header.open("xb") as stream:
            stream.write(text.encode("ascii"))
        report["header"] = dict(path="data.h", bytes=header.stat().st_size, sha256=sha(header.read_bytes()))
        report["cases"] = recover(header.read_text(encoding="ascii"), contract, items)
        controls = [
            ("raw_identification_byte", text.replace("0x01", "0x02", 1), "raw_array_bytes:identification"),
            ("first_offset", text.replace("    0U,", "    1U,", 1), "offset_values"),
            ("descriptor_rate", text.replace(".rate = 192000U", ".rate = 48000U", 1), "ordered_descriptor_fields"),
            ("descriptor_order", text.replace(rows[0] + rows[1], rows[1] + rows[0], 1), "ordered_descriptor_fields"),
            ("model_identity", text.replace(MODEL_SHA, "0" + MODEL_SHA[1:], 1), "identity_macro:CORPUS_CONTRACT_SHA256"),
        ]
        report["pure_recovery_controls"] = []
        for name, changed, reason in controls:
            need(changed != text, "control_was_not_applied:" + name)
            try:
                recover(changed, contract, items)
            except RuntimeError as error:
                need(str(error) == reason, "control_wrong_oracle:" + name + ":" + str(error))
                report["pure_recovery_controls"].append(dict(name=name, rejected=True, exact_reason=reason))
            else:
                raise RuntimeError("control_accepted:" + name)
        report["inputs_after"] = snapshot(paths)
        need(report["inputs_after"] == before, "source_identity_changed")
        report["counts"] = dict(cases=17, arrays=85, full_raw_payload_arrays=51, audio_packets=238,
                                 expected_pcm_bytes=398080, input_identities=len(before))
        report["source_verified"] = report["completed"] = True
    except BaseException as error:
        report["failures"].append(dict(type=type(error).__name__, message=str(error)))
        raise
    finally:
        with (output / "report.json").open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(report, stream, indent=2); stream.write("\n")
        print(json.dumps(dict(output=str(output), completed=report["completed"], source_verified=report["source_verified"],
            header=report.get("header"), report_sha256=sha((output / "report.json").read_bytes()), failures=report["failures"])))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=FROZEN / "contract.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    materialize(args.contract, args.output)
