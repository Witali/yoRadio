"""Add six floor0 representation controls; no reference, decoder or PCM synthesis.

Original files are read-only. The extra comparison matrix contains byte-exact
copies of the six original controls plus six additions; its equality relations
are expectations requiring an independent decoder, not construction results.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ORIGINAL = ROOT / ".build/cyd-vorbis-floor0-prep-01/generated01"
FLOOR_GENERATOR = ROOT / "tests/vorbis_format_corpus/generate_floor0.py"
FLOOR_SHA = "7bd0f139e496edce90c1335e4dc4370ed9e99499e209e9f14324c68297971a07"
PACKED_SIXTEENTH = 0x62000001
ORIGINAL_IDS = tuple(f"{variant}-s{short}-l{long}"
    for variant in ("floor0-even6-r0", "floor0-odd5-r0")
    for short, long in ((64, 256), (256, 2048), (64, 2048)))
FILES = ("identification", "comment", "setup", "audio", "ogg", "packet_metadata")
INVARIANTS = ("short", "long", "rate", "channels", "bits", "mode_flags", "offsets",
    "expected_packet_frames", "expected_packet_s16le_bytes", "expected_raw_samples",
    "expected_s16le_bytes", "packet_granules", "packet_count", "public_decode_output_capacity")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def serialized(value):
    return (json.dumps(value, indent=2) + "\n").encode()


def load_inputs():
    pins = json.loads((HERE / "source-pins.json").read_bytes())
    for row in pins["local_inputs"]:
        data = (ROOT / row["path"]).read_bytes()
        need(len(data) == row["bytes"] and sha(data) == row["sha256"],
             "Pinned input changed: " + row["path"])
    need(sha(FLOOR_GENERATOR.read_bytes()) == FLOOR_SHA, "Canonical floor generator changed")
    spec = importlib.util.spec_from_file_location("floor0_equivalent_canonical", FLOOR_GENERATOR)
    floor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(floor)  # Definitions only; guarded generation is never called.
    return pins, floor


def equivalent_setup(floor, configuration, declaration, original):
    """Re-emit identical-width fields; only floor minimum/multiplicands differ."""
    baseline = floor.setup(configuration)
    need(baseline.data() == original and baseline.report() == declaration,
         "Canonical definitions must reproduce the complete frozen setup")
    result = floor.S.Bits()
    changes = []
    targets = {f"book[{number}].minimum": PACKED_SIXTEENTH
               for number in range(2, 2 + len(configuration["books"]))}
    for number, vectors in enumerate(configuration["books"], 2):
        for index, value in enumerate(sum(vectors, [])):
            need(1 <= value <= 31, "All decremented multiplicands must retain five bits")
            targets[f"book[{number}].multiplicand[{index}]"] = value - 1
    mask = 0
    for field in declaration["fields"]:
        name, width, value = field["name"], field["width"], field["value"]
        replacement = targets.get(name, value)
        if name in targets:
            need(width == (32 if name.endswith(".minimum") else 5), "Exact target field width")
            mask |= ((1 << width) - 1) << field["offset"]
            changes.append(dict(name=name, offset=field["offset"], width=width,
                                original=value, equivalent=replacement))
        need(field["offset"] == len(result.bits), "All field offsets remain unchanged")
        result.put(name, width, replacement)
    need(len(changes) == 7 * len(configuration["books"]), "Every floor minimum and scalar changed")
    changed = int.from_bytes(original, "little") ^ int.from_bytes(result.data(), "little")
    need(changed and not changed & ~mask and len(original) == len(result.data()),
         "Only declared floor representation bits may change")
    return result, changes


def replace_setup_page(floor, original, replacement, setup):
    """Retain serial, page boundaries, granules and every non-setup page byte."""
    pages = floor.S.read_pages(original)
    need(len(pages) == 17 and pages[2]["packet"] == setup, "Complete 3+14 packet carrier required")
    source_setup = pages[2]["packet"]
    output = b"".join(floor.S.page(replacement if index == 2 else page["packet"],
        page["serial"], index, page["granule"], page["flags"])
        for index, page in enumerate(pages))
    rebuilt_original = b"".join(floor.S.page(page["packet"], page["serial"], index,
        page["granule"], page["flags"]) for index, page in enumerate(pages))
    need(rebuilt_original == original and source_setup != replacement and len(output) == len(original),
         "Canonical original pages must roundtrip byte-exactly")
    actual = floor.S.read_pages(output)
    need(all(actual[i] == pages[i] for i in range(17) if i != 2), "Non-setup carrier page changed")
    need(actual[2]["packet"] == replacement and all(actual[2][key] == pages[2][key]
         for key in ("flags", "granule", "serial")), "Setup carrier metadata changed")
    return output


def generate(output):
    output = output.resolve()
    build = (ROOT / ".build").resolve()
    need(output != build and output.is_relative_to(build) and not output.exists()
         and not output.is_relative_to(HERE) and not output.is_relative_to(ORIGINAL),
         "Fresh independent output beneath this checkout's .build required")
    pins, floor = load_inputs()
    matrix = json.loads((ORIGINAL / "matrix.json").read_bytes())
    original_fields = json.loads((ORIGINAL / "construction-fields.json").read_bytes())
    need(len(matrix["cases"]) == 9, "All original nine cases must remain present")
    selected = [case for case in matrix["cases"] if case["id"] in ORIGINAL_IDS]
    need(tuple(case["id"] for case in selected) == ORIGINAL_IDS, "Exact original floor0 order required")
    payloads, cases, original_cases, relations = {}, [], [], []
    fields = dict(comment=copy.deepcopy(original_fields["comment"]), variants={},
                  identifications=copy.deepcopy(original_fields["identifications"]))
    for original_case in selected:
        old_id, old_variant = original_case["id"], original_case["variant"]
        variant = old_variant + "-minp1"
        new_id = f"{variant}-s{original_case['short']}-l{original_case['long']}"
        declaration = original_fields["variants"][old_variant]
        configuration = declaration["configuration"]
        need(configuration == floor.VARIANTS[old_variant] and configuration["floor"] == 0,
             "Exact original floor0 configuration required")
        raw = {key: (ORIGINAL / original_case[key]).read_bytes() for key in FILES}
        sb, changes = equivalent_setup(floor, configuration, declaration["setup"], raw["setup"])
        changed = dict(raw, setup=sb.data(), ogg=replace_setup_page(floor, raw["ogg"], sb.data(), raw["setup"]))
        if variant not in fields["variants"]:
            fields["variants"][variant] = dict(configuration=copy.deepcopy(configuration),
                setup=sb.report(), audio=copy.deepcopy(declaration["audio"]),
                representation=dict(lookup_type=2, sequence_p=0, minimum_packed=PACKED_SIXTEENTH,
                    delta_packed=PACKED_SIXTEENTH, multiplicands="original decoded units minus one",
                    configuration_books_mean="decoded LSP vector components in units 1/16"))
        new_case, copied_original = copy.deepcopy(original_case), copy.deepcopy(original_case)
        new_case.update(id=new_id, variant=variant,
            features=original_case["features"] + ["nonzero-minimum-equivalent-LSP-control"],
            equivalent_original_id=old_id, independent_decode_status="PENDING")
        for key in FILES:
            filename = Path(original_case[key]).name
            new_case[key] = f"cases/{new_id}/{filename}"
            copied_original[key] = f"original-cases/{old_id}/{filename}"
            payloads[new_case[key]] = changed[key]
            payloads[copied_original[key]] = raw[key]
        need(all(new_case[key] == original_case[key] for key in INVARIANTS), "Case accounting changed")
        need(all(changed[key] == raw[key] for key in ("identification", "comment", "audio", "packet_metadata")),
             "Headers, audio and packet metadata must be byte-identical")
        cases.append(new_case)
        original_cases.append(copied_original)
        relations.append(dict(original_id=old_id, equivalent_id=new_id,
            original_matrix=(ORIGINAL / "matrix.json").relative_to(ROOT).as_posix(),
            original_matrix_sha256=sha((ORIGINAL / "matrix.json").read_bytes()),
            equality_expected="same-decoder complete s16le PCM byte equality, not measured here",
            setup_field_changes=changes, invariant_case_keys=list(INVARIANTS),
            raw_file_relations=[dict(kind=key, original_path=original_case[key],
                original_sha256=sha(raw[key]), equivalent_path=new_case[key],
                equivalent_sha256=sha(changed[key]), expected_equal=key not in ("setup", "ogg"))
                for key in FILES]))
    need(len(cases) == len(relations) == 6, "Exactly six additions required")
    common = dict(validity_qualified=False, actual_nonzero_pcm_observed=False,
                  independent_decode_run=False, numeric_qualified=False, full_G6_qualified=False)
    payloads["matrix.json"] = serialized(dict(schema="vorbis-floor0-equivalent-additions-v1", cases=cases,
        original_cases_retained=True, original_campaigns_reclassified=False, **common))
    payloads["comparison-matrix.json"] = serialized(dict(schema="vorbis-floor0-equivalent-comparison-v1",
        cases=original_cases + cases, expected_same_decoder_pcm_equal_groups=[
            [r["original_id"], r["equivalent_id"]] for r in relations], **common))
    payloads["relations.json"] = serialized(dict(schema="floor0-equivalent-representation-relations-v1",
        pairs=relations, mathematical_basis="(x-1)*(1/16)+(1/16)=x/16; sequence flag zero",
        actual_PCM_equality_observed=False, **common))
    payloads["construction-fields.json"] = serialized(fields)
    payloads["pure-checks.json"] = serialized(dict(scope="Construction only; no decoding, floor curve or PCM",
        additional_cases=6, comparison_cases=12, packets_per_case=14,
        exact_audio_and_metadata_copied=True, only_floor_minimum_and_multiplicand_bits_changed=True,
        only_setup_carrier_payload_and_CRC_changed=True, **common))
    # Inputs are checked again before any output becomes visible.
    for row in pins["local_inputs"]:
        need(sha((ROOT / row["path"]).read_bytes()) == row["sha256"], "Input changed during construction")
    manifest = dict(schema="floor0-equivalent-construction-manifest-v1", generator_sha256=sha(Path(__file__).read_bytes()),
        source_pins_sha256=sha((HERE / "source-pins.json").read_bytes()),
        original_manifest_sha256=sha((ORIGINAL / "manifest.json").read_bytes()),
        codec_execution=False, validity_qualified=False,
        files=[dict(path=name, bytes=len(data), sha256=sha(data)) for name, data in sorted(payloads.items())])
    payloads["manifest.json"] = serialized(manifest)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    for name, data in payloads.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as stream:
            stream.write(data)
    print(json.dumps(dict(output=str(output), additions=6, comparison_cases=12,
        files=len(payloads), manifest_sha256=sha(payloads["manifest.json"]), independent_decode_pending=True)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    generate(parser.parse_args().output)
