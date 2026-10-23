"""Root-owned pure8 materialization; imports pinned corrected25 formatting helpers."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / ".build/cyd-vorbis-format-expanded25-prep-02/materialize.py"
BASE_SHA = "740be8723dea9938bb834e7eec098916476807fdf82eb056b7b5f63ac763acf5"


def need(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def base_module():
    need(digest(BASE_PATH.read_bytes()) == BASE_SHA, "corrected25_materializer_pin")
    spec = importlib.util.spec_from_file_location("more_singletons8_corrected25_materializer", BASE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # Definitions only; original guarded main never runs.
    return module


def render(contract, raw_cases, contract_file_sha):
    base = base_module()
    model = contract["model"]
    count = len(model["cases"])
    need(count == len(raw_cases) == 8 and model["case_mask"] == (1 << count) - 1 and count <= 31,
         "complete8_bounded_model")
    text = ("// Complete public raw8 data; materialization is not target qualification.\n"
        "#pragma once\n#include \"corpus_case.h\"\n\n"
        f"#define CORPUS_CASE_COUNT {count}U\n"
        f"#define CORPUS_CONTRACT_SHA256 \"{contract['contract_sha256']}\"\n"
        f"#define CORPUS_CONTRACT_FILE_SHA256 \"{contract_file_sha}\"\n"
        f"#define CORPUS_EXPECTED_PCM_BYTES {model['total_pcm']}U\n\n")
    descriptors = []
    for index, (case, raw) in enumerate(zip(model["cases"], raw_cases)):
        names = base.symbols(index)
        for kind in ("identification", "setup", "audio"):
            need(digest(raw[kind]) == case["raw_sha256"][kind], "model_raw_identity")
            text += base.array(names[kind], "uint8_t", raw[kind])
        text += base.array(names["offsets"], "uint32_t", case["offsets"])
        text += base.array(names["modes"], "uint8_t", case["modes"])
        descriptors.append("    {\n" + "".join(f"        .{key} = {value},\n"
            for key, value in base.descriptor_fields(index, case).items()) + "    },\n")
    text += "static const corpus_case_t corpus_cases[CORPUS_CASE_COUNT] = {\n" + "".join(descriptors) + "};\n"
    return text, descriptors


def recover(text, contract, raw_cases, contract_file_sha):
    """Independent restricted C parser: no compiler, formatter or generator calls."""
    model, cases = contract["model"], contract["model"]["cases"]
    count = len(cases)
    need(count == len(raw_cases) == 8 and count <= 31, "recovery_complete8")
    for name, expected in (("CORPUS_CASE_COUNT", f"{count}U"),
        ("CORPUS_EXPECTED_PCM_BYTES", f"{model['total_pcm']}U"),
        ("CORPUS_CONTRACT_SHA256", json.dumps(contract["contract_sha256"])),
        ("CORPUS_CONTRACT_FILE_SHA256", json.dumps(contract_file_sha))):
        need(re.findall(r"^#define " + name + r" (.+)$", text, re.M) == [expected], "identity_macro:" + name)
    arrays = {}
    for match in re.finditer(r"static const (uint8_t|uint32_t) (corpus_[0-9]{3}_[a-z]+)\[([0-9]+)\] = \{\n(.*?)\n\};", text, re.S):
        kind, name, capacity, body = match.groups()
        need(name not in arrays, "duplicate_array")
        tokens = [token.strip() for token in body.split(",") if token.strip()]
        grammar = r"0x[0-9a-f]{2}" if kind == "uint8_t" else r"(?:0|[1-9][0-9]*)U"
        need(all(re.fullmatch(grammar, token) for token in tokens), "bounded_integer_grammar")
        values = [int(token.removesuffix("U"), 0) for token in tokens]
        need(len(values) == int(capacity) and all(0 <= value <= (255 if kind == "uint8_t" else 0xffffffff)
             for value in values), "array_capacity_or_integer_range")
        arrays[name] = (kind, values)
    need(len(arrays) == count * 5, "complete_array_set")
    tables = re.findall(r"static const corpus_case_t corpus_cases\[CORPUS_CASE_COUNT\] = \{\n(.*?)\n\};", text, re.S)
    need(len(tables) == 1, "one_bounded_descriptor_table")
    blocks = re.findall(r"    \{\n(.*?)    \},\n?", tables[0], re.S)
    declared = int(re.findall(r"^#define CORPUS_CASE_COUNT ([0-9]+)U$", text, re.M)[0])
    need(declared == len(blocks) == count == len(raw_cases), "declared_capacity_descriptor_model_raw_count")
    rows, used = [], set()
    for index, (case, raw, block) in enumerate(zip(cases, raw_cases, blocks)):
        names = {kind: f"corpus_{index:03d}_{kind}" for kind in ("identification", "setup", "audio", "offsets", "modes")}
        expected = {"id": json.dumps(case["id"])}
        for kind in ("identification", "setup", "audio"):
            expected[kind], expected[kind + "_size"] = names[kind], f"sizeof({names[kind]})"
            actual_kind, values = arrays[names[kind]]
            need(actual_kind == "uint8_t" and bytes(values) == raw[kind] and digest(bytes(values)) == case["raw_sha256"][kind],
                 "raw_array_bytes:" + kind)
        for kind, count_field, c_type in (("offsets", "offset_count", "uint32_t"), ("modes", "mode_count", "uint8_t")):
            expected[kind] = names[kind]
            expected[count_field] = f"sizeof({names[kind]}) / sizeof({names[kind]}[0])"
            need(arrays[names[kind]] == (c_type, case[kind]), "model_array_values:" + kind)
        for field, value in (("rate", case["rate"]), ("channels", case["channels"]), ("short_block", case["short"]),
            ("long_block", case["long"]), ("expected_pcm_bytes", case["total_pcm"])):
            expected[field] = f"{value}U"
        fields = {}
        for line in block.splitlines():
            match = re.fullmatch(r"        \.([a-z_]+) = (.+),", line)
            need(match is not None, "descriptor_grammar")
            key, value = match.groups()
            need(key not in fields, "duplicate_descriptor_field")
            fields[key] = value
        need(fields == expected, "ordered_descriptor_fields")
        used.update(names.values())
        rows.append(dict(case=index, id=case["id"], raw_sha256=case["raw_sha256"], descriptor_fields=fields))
    need(used == set(arrays), "no_unused_or_missing_arrays")
    remaining = re.sub(r"static const (uint8_t|uint32_t) (corpus_[0-9]{3}_[a-z]+)\[([0-9]+)\] = \{\n(.*?)\n\};", "", text, flags=re.S)
    remaining = re.sub(r"static const corpus_case_t corpus_cases\[CORPUS_CASE_COUNT\] = \{\n(.*?)\n\};", "", remaining, flags=re.S)
    remaining = re.sub(r"^//[^\n]*$", "", remaining, flags=re.M)
    remaining = re.sub(r'^#pragma once$|^#include "corpus_case.h"$|^#define (?:CORPUS_CASE_COUNT|CORPUS_EXPECTED_PCM_BYTES|CORPUS_CONTRACT_SHA256|CORPUS_CONTRACT_FILE_SHA256) .+$',
                       "", remaining, flags=re.M)
    need(not remaining.strip(), "unsupported_C_outside_bounded_grammar")
    return rows


def materialize(contract_path, raw_cases, output):
    need(not output.exists(), "fresh_materialization_output")
    contract_data = contract_path.read_bytes()
    contract, file_sha = json.loads(contract_data), digest(contract_data)
    text, descriptors = render(contract, raw_cases, file_sha)
    output.mkdir()
    header = output / "data.h"
    with header.open("xb") as stream:
        stream.write(text.encode("ascii"))
    recovered = recover(header.read_text(encoding="ascii"), contract, raw_cases, file_sha)
    cases, pcm = len(contract["model"]["cases"]), contract["model"]["total_pcm"]
    controls = [
        ("old25_capacity", text.replace(f"#define CORPUS_CASE_COUNT {cases}U", "#define CORPUS_CASE_COUNT 25U", 1), "identity_macro:CORPUS_CASE_COUNT"),
        ("old25_PCM", text.replace(f"#define CORPUS_EXPECTED_PCM_BYTES {pcm}U", "#define CORPUS_EXPECTED_PCM_BYTES 623360U", 1), "identity_macro:CORPUS_EXPECTED_PCM_BYTES"),
        ("raw_identification", text.replace("0x01", "0x02", 1), "raw_array_bytes:identification"),
        ("first_offset", text.replace("    0U,", "    1U,", 1), "model_array_values:offsets"),
        ("descriptor_order", text.replace(descriptors[0] + descriptors[1], descriptors[1] + descriptors[0], 1), "ordered_descriptor_fields"),
    ]
    observed = []
    for name, damaged, reason in controls:
        need(damaged != text, "control_not_applied:" + name)
        try:
            recover(damaged, contract, raw_cases, file_sha)
        except RuntimeError as error:
            need(str(error) == reason, "control_wrong_rejection:" + name + ":" + str(error))
            observed.append(dict(name=name, rejected=True, exact_reason=reason))
        else:
            raise RuntimeError("control_accepted:" + name)
    report = dict(schema="more_singletons8-pure-materialization-v1", completed=True, source_verified=True,
        counts=dict(cases=cases, arrays=cases * 5, full_raw_payload_arrays=cases * 3,
            packets=contract["model"]["total_packets"], expected_pcm_bytes=pcm,
            descriptor_capacity=cases, case_mask=contract["model"]["case_mask"]),
        header=dict(path=str(header.resolve()), bytes=header.stat().st_size, sha256=digest(header.read_bytes())),
        cases=recovered, controls=observed, contract_file_sha256=file_sha,
        contract_sha256=contract["contract_sha256"], codec_compiler_SDK_QEMU_reference_Git_executed=False,
        target_qualified=False, actual_PCM_synthesized=False)
    with (output / "report.json").open("xb") as stream:
        stream.write((json.dumps(report, indent=2) + "\n").encode())
    return report
