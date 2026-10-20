"""Pure expanded25 source/binding/byte closure; no controller or decoder runs."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def fact(path):
    raw = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def main():
    spec = importlib.util.spec_from_file_location("expanded25_selected_binding02", HERE / "reference_binding02.py")
    b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
    contract = json.loads((HERE / "contract.json").read_bytes())
    mapping = json.loads((HERE / "source-map.json").read_bytes())
    binding = json.loads((HERE / "reference-binding02.json").read_bytes())
    b.verify(contract, mapping, binding)
    controls = []
    for name, reason in (("subset", "all25 source cases"), ("reorder", "strict selected source order"),
        ("raw_sha", "model raw SHA binding"), ("changed_case_fields", "original case fields changed")):
        c, m = copy.deepcopy(contract), copy.deepcopy(mapping)
        if name == "subset": c["model"]["cases"].pop()
        elif name == "reorder": c["model"]["cases"][0], c["model"]["cases"][1] = c["model"]["cases"][1], c["model"]["cases"][0]
        elif name == "raw_sha": c["model"]["cases"][8]["raw_sha256"]["audio"] = "0" * 64
        else: m["cases"][8]["fields_changed"] = ["mode_flags"]
        try: b.derive(c, m)
        except RuntimeError as error:
            assert str(error) == reason, (name, str(error))
            controls.append(dict(name=name, rejected=True, exact_reason=reason))
        else: raise RuntimeError("source control accepted " + name)
    old = ROOT / ".build/cyd-vorbis-format-corpus-checked-prep-02"
    oldsrc = (old / "run-cyd-vorbis-format-corpus-checked-qemu.py").read_bytes().decode()
    newsrc = (HERE / "run-cyd-vorbis-format-expanded25-qemu02.py").read_bytes().decode()
    oa, na = ast.parse(oldsrc), ast.parse(newsrc)
    helpers = []
    for name in ("save", "freeze", "current", "execute"):
        before = next(n for n in ast.walk(oa) if isinstance(n, ast.FunctionDef) and n.name == name)
        after = next(n for n in ast.walk(na) if isinstance(n, ast.FunctionDef) and n.name == name)
        assert ast.get_source_segment(oldsrc, before).encode() == ast.get_source_segment(newsrc, after).encode()
        helpers.append(name)
    for relative in ("protocol.py", "windows_compile_command.py"):
        assert (old / relative).read_bytes() == (HERE / relative).read_bytes()
    project = old / "target/cyd_vorbis_format_corpus_checked_qemu"
    selected = HERE / "target/cyd_vorbis_format_expanded25_qemu"
    projectrows = []
    for path in sorted(project.rglob("*")):
        if path.is_file():
            target = selected / path.relative_to(project)
            assert path.read_bytes() == target.read_bytes()
            projectrows.append(dict(relative=path.relative_to(project).as_posix(), old=fact(path), selected=fact(target)))
    report = json.loads((HERE / "materialized01/report.json").read_bytes())
    assert report["completed"] is True and report["source_verified"] is True
    assert (report["counts"]["cases"], report["counts"]["arrays"], report["counts"]["full_raw_payload_arrays"]) == (25, 125, 75)
    assert report["inputs_before"] == report["inputs_after"]
    for item in report["inputs_after"]: assert fact(Path(item["path"])) == item
    selection = json.loads((HERE / "input-selection.json").read_bytes())
    for item in selection["original_inputs"]: assert fact(Path(item["path"])) == item
    for path in HERE.rglob("*.py"): ast.parse(path.read_bytes())
    result = dict(schema="expanded25-source-static-closure-v2", completed=True,
        scope="source/raw bytes, restricted C reader and Python AST only", source_binding_cases=25,
        existing_reference_scopes=["old17", "new8"], new_reference_commands_executed=False,
        exact_source_binding_controls=controls, byte_identical_runtime_helpers=helpers,
        byte_identical_protocol_and_compile_helper=True, byte_identical_project_files=projectrows,
        materialized_counts=report["counts"], materialized_report=fact(HERE / "materialized01/report.json"),
        superseded_nonpass=fact(HERE / "source-static-closure01.failure.json"),
        target_executed=False, numeric_target_comparison=False, SDK_compiler_QEMU_Git_device_executed=False)
    with (HERE / "source-static-closure02.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2); stream.write("\n")
    print(json.dumps(dict(closure=fact(HERE / "source-static-closure02.json"), source_validation_controls=4,
                         materialized=report["counts"], project_files=len(projectrows))))


if __name__ == "__main__": main()
