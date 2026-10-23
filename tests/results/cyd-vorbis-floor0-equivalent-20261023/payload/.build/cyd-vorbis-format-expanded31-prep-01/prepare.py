"""Root-owned31 source selection/materialization/sealing; never run a codec/SDK."""
import argparse
import ast
import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / ".build/cyd-vorbis-format-expanded25-prep-02"
PROJECT = "target/cyd_vorbis_format_expanded31_qemu"


def need(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def fact(path):
    data = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(data), sha256=sha(data))


def put(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def document(path, value):
    put(path, (json.dumps(value, indent=2) + "\n").encode())


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def prepare(output):
    output = output.resolve()
    need(output != ROOT / ".build" and output.is_relative_to(ROOT / ".build") and not output.exists() and
         not output.is_relative_to(HERE) and not output.is_relative_to(BASE), "fresh_independent_runtime_directory")
    readiness = json.loads((HERE / "readiness.json").read_bytes())
    for row in readiness["files"]:
        path = HERE / row["path"]
        need(path.stat().st_size == row["bytes"] and sha(path.read_bytes()) == row["sha256"], "prep_source_pin:" + row["path"])
    pins = json.loads((HERE / "source-pins.json").read_bytes())
    before = []
    for row in pins["inputs"]:
        observed = fact(ROOT / row["path"])
        need(observed["bytes"] == row["bytes"] and observed["sha256"] == row["sha256"], "source_input_pin:" + row["path"])
        before.append(observed)
    output.mkdir()
    for name in ("protocol.py", "windows_compile_command.py", "materialize.py", "reference_binding.py", "source-pins.json"):
        put(output / name, (HERE / name).read_bytes())
    for path in sorted((HERE / PROJECT).rglob("*")):
        if path.is_file():
            put(output / PROJECT / path.relative_to(HERE / PROJECT), path.read_bytes())
    old_contract = json.loads((BASE / "contract.json").read_bytes())
    mapping = copy.deepcopy(json.loads((BASE / "source-map.json").read_bytes()))
    old_model = old_contract["model"]
    need(len(old_model["cases"]) == len(mapping["cases"]) == 25, "unchanged25_selection")
    floor_path = ROOT / pins["original_floor_matrix"]["path"]
    extra_path = ROOT / pins["additional_floor_matrix"]["path"]
    reference_path = ROOT / pins["new12_proofs"]["comparison_matrix"]["path"]
    floor = json.loads(floor_path.read_bytes())["cases"]
    additions = json.loads(extra_path.read_bytes())["cases"]
    need(len(floor) == 9 and len(additions) == 6, "original9_plus_additional6")
    merged = []
    for group, matrix_path, cases in (("floor9", floor_path, floor), ("newfloor6", extra_path, additions)):
        for local, case in enumerate(cases):
            copied = copy.deepcopy(case)
            files = {}
            for kind in ("identification", "setup", "comment", "audio", "ogg", "packet_metadata"):
                if kind not in case:
                    continue
                source = (matrix_path.parent / case[kind]).resolve()
                need(source.is_relative_to(matrix_path.parent), "original_raw_boundary")
                destination = (output / "inputs/floor15" / case[kind]).resolve()
                need(destination.is_relative_to(output / "inputs/floor15"), "selected_raw_boundary")
                put(destination, source.read_bytes())
                need(destination.read_bytes() == source.read_bytes(), "byte_exact_raw_selection")
                files[kind] = dict(original=fact(source), selected=fact(destination))
            merged.append(copied)
            if group == "floor9":
                origin = mapping["cases"][16 + local]
                need(origin["id"] == case["id"] and origin["original_case_fields"] == case and origin["fields_changed"] == [],
                     "all_nine_original_floor_fields_unchanged")
                # Retain the original five-kind mapping structure for old cases.
                for kind in origin["files"]:
                    origin["files"][kind]["selected"] = files[kind]["selected"]
            else:
                mapping["cases"].append(dict(case=len(mapping["cases"]), id=case["id"], original_group=group,
                    original_case=local, original_matrix=fact(matrix_path), reference_matrix=fact(reference_path),
                    original_reference_source_index=0, original_case_fields=case, selected_case_fields=copied,
                    fields_changed=[], files=files))
    merged_path = output / "inputs/floor15/matrix.json"
    document(merged_path, dict(schema="explicit-merged-original9-plus-equivalent6-v1", cases=merged,
        original_matrices=[fact(floor_path), fact(extra_path)], original_cases_rewritten=False,
        new_reference_commands_executed=False, case_order="original_floor9,additional_equivalent_floor6"))
    mapping.update(schema="expanded31-original-source-map-v1", order="books8,newbooks8,floor9,newfloor6",
        original_cases_rewritten=False, new_reference_commands_executed=False, expanded_target_executed=False)
    document(output / "source-map.json", mapping)
    first_path = Path(old_contract["manifest_inputs"][0]["path"])
    manifest_inputs = [dict(path=str(first_path.resolve()), sha256=sha(first_path.read_bytes())),
                       dict(path=str(merged_path.resolve()), sha256=sha(merged_path.read_bytes()))]
    protocol = module("expanded31_unchanged_protocol", output / "protocol.py")
    contract = protocol.load_contract(manifest_inputs)
    model = contract["model"]
    need(model["cases"][:25] == old_model["cases"] and len(model["cases"]) == 31 and
         [case["id"] for case in model["cases"]] == pins["expected_case_ids"] and
         model["total_packets"] == sum(len(case["sizes"]) for case in model["cases"]) and
         model["total_pcm"] == sum(case["total_pcm"] for case in model["cases"]) and
         model["case_mask"] == (1 << len(model["cases"])) - 1 <= 0x7fffffff,
         "complete31_original25_prefix_and_derived_counts")
    document(output / "contract.json", contract)
    raw_cases = []
    for manifest in manifest_inputs:
        path = Path(manifest["path"])
        for case in json.loads(path.read_bytes())["cases"]:
            raw_cases.append({kind: (path.parent / case[kind]).read_bytes() for kind in ("identification", "setup", "audio")})
    formatter = module("expanded31_pure_materializer", output / "materialize.py")
    materialized = formatter.materialize(output / "contract.json", raw_cases, output / "materialized01")
    binding_helper = module("expanded31_source_reference_binding", output / "reference_binding.py")
    binding = binding_helper.derive(contract, mapping)
    document(output / "reference-binding31.json", binding)
    replacements = {
        "__FIRST_MATRIX_PATH__": first_path.relative_to(ROOT).as_posix(), "__FIRST_MATRIX_SHA__": manifest_inputs[0]["sha256"],
        "__SECOND_MATRIX_PATH__": merged_path.relative_to(ROOT).as_posix(), "__SECOND_MATRIX_SHA__": manifest_inputs[1]["sha256"],
        "__CONTRACT_ID__": contract["contract_sha256"], "__CONTRACT_FILE_SHA__": sha((output / "contract.json").read_bytes()),
        "__DATA_HEADER_SHA__": materialized["header"]["sha256"], "__SOURCE_MAP_SHA__": sha((output / "source-map.json").read_bytes()),
        "__REFERENCE_BINDING_SHA__": sha((output / "reference-binding31.json").read_bytes()),
        "__REFERENCE_HELPER_SHA__": sha((output / "reference_binding.py").read_bytes()),
        "__SOURCE_PINS_SHA__": sha((output / "source-pins.json").read_bytes()),
        "__CASE_COUNT__": str(len(model["cases"])), "__TOTAL_PACKETS__": str(model["total_packets"]),
        "__TOTAL_PCM__": str(model["total_pcm"]), "__CASE_MASK__": str(model["case_mask"]),
        "__PROTOCOL_EVENTS__": str(3 + len(model["cases"]) * (2 * protocol.PACKETS + 3)),
    }
    template = (HERE / "controller.template.py").read_text(encoding="utf-8")
    for marker, value in replacements.items():
        need(marker in template, "controller_marker_missing:" + marker)
        template = template.replace(marker, value)
    need(not any(marker in template for marker in replacements), "unsealed_controller_marker")
    tree = ast.parse(template)
    old_text = (BASE / "run-cyd-vorbis-format-expanded25-qemu02.py").read_text(encoding="utf-8")
    old_tree = ast.parse(old_text)
    for name in ("save", "freeze", "current", "execute"):
        before_nodes = [node for node in ast.walk(old_tree) if isinstance(node, ast.FunctionDef) and node.name == name]
        after_nodes = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name]
        need(len(before_nodes) == len(after_nodes) == 1 and ast.dump(before_nodes[0], include_attributes=False) ==
             ast.dump(after_nodes[0], include_attributes=False), "unchanged_runtime_helper_AST:" + name)
    controller = output / "run-cyd-vorbis-format-expanded31-qemu.py"
    put(controller, template.encode())
    put(output / "controller-from25.diff", "".join(difflib.unified_diff(old_text.splitlines(True), template.splitlines(True),
        fromfile=str(BASE / "run-cyd-vorbis-format-expanded25-qemu02.py"), tofile=controller.name)).encode())
    need(all(fact(Path(row["path"])) == row for row in before), "all_original_inputs_stable")
    need(all(fact(Path(row["path"])) == row for row in contract["source_facts"]), "all_model_raw_sources_stable")
    need(all(fact(Path(row["path"])) == row for row in binding["proof_facts"]), "all_reference_facts_stable")
    counts = dict(cases=len(model["cases"]), packets=model["total_packets"], expected_pcm_bytes=model["total_pcm"],
        protocol_events=3 + len(model["cases"]) * (2 * protocol.PACKETS + 3), case_mask=model["case_mask"],
        descriptor_capacity=len(model["cases"]), arrays=len(model["cases"]) * 5, full_raw_arrays=len(model["cases"]) * 3)
    document(output / "preparation.json", dict(schema="expanded31-root-owned-materialization-v1", completed=True,
        counts=counts, contract=fact(output / "contract.json"), header=fact(output / "materialized01/data.h"),
        controller=fact(controller), reference_binding=fact(output / "reference-binding31.json"), original_inputs=before,
        original25_model_prefix_unchanged=True, new_reference_commands_executed=False,
        codec_SDK_compiler_QEMU_Git_executed=False, target_executed=False, full_G6_qualified=False))
    document(output / "runtime-readiness.json", dict(schema="expanded31-runtime-source-readiness-v1", files=[
        dict(path=path.relative_to(output).as_posix(), bytes=path.stat().st_size, sha256=sha(path.read_bytes()))
        for path in sorted(output.rglob("*")) if path.is_file()], target_executed=False))
    print(json.dumps(dict(output=str(output), counts=counts, contract=fact(output / "contract.json"),
        header=fact(output / "materialized01/data.h"), controller=fact(controller), target_executed=False)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    prepare(parser.parse_args().output)
