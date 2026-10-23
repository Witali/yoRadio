"""Exact restricted40-array reader functions; no formatter/generator startup."""
import hashlib
import json
import re

def need(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def digest(data):
    return hashlib.sha256(data).hexdigest()


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
