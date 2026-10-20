"""Read and byte-copy existing raw inputs; never run a corpus generator/decoder."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREVIOUS = ROOT / ".build/cyd-vorbis-format-corpus-checked-prep-02"
MATRICES = [
    ("books8", ".build/cyd-vorbis-books-prep-01/generated01/matrix.json", "38e38f1f5ada7cd84a6ea91c5b46e0680ee62a7f511c9a72bfa7b6d7eb64cd2e"),
    ("newbooks8", ".build/cyd-vorbis-map2-regression-prep-01/generated02/matrix.json", "7ec364dea889ead32407d90914b7f6fb91d515d03dfa82dd6a1f7affdac139b8"),
    ("floor9", ".build/cyd-vorbis-floor0-prep-01/generated01/matrix.json", "aa1231b8813ac193767c85a2ef339a2da36af52f2af157a16cda9f3d2d438f07")]
PINS = {
    "protocol.py": "547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e",
    "run-cyd-vorbis-format-corpus-checked-qemu.py": "3aa167fe4b231d2c15b91b1b5c78b24da3410d18eaacc0709d6afe0c33ea902d",
    "target/cyd_vorbis_format_corpus_checked_qemu/main/main.c": "37eaeb25a272ceadaafe36d6309449d31895b7019523333ed0e4c48226d0d065",
    "target/cyd_vorbis_format_corpus_checked_qemu/main/corpus_case.h": "91a040d89f3bc2b7740fa2f175f36d64cebcd92653cd4c2014149bbb11219be3"}


def sha(raw): return hashlib.sha256(raw).hexdigest()


def fact(path):
    raw = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(raw), sha256=sha(raw))


def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream: stream.write(raw)


def document(path, value): put(path, (json.dumps(value, indent=2) + "\n").encode())


def main():
    sources = [PREVIOUS / name for name in PINS]
    for name, expected in PINS.items():
        if sha((PREVIOUS / name).read_bytes()) != expected: raise ValueError("prior source pin " + name)
    for name in ("protocol.py", "windows_compile_command.py"):
        put(HERE / name, (PREVIOUS / name).read_bytes()); sources.append(PREVIOUS / name)
    project = PREVIOUS / "target/cyd_vorbis_format_corpus_checked_qemu"
    for path in sorted(project.rglob("*")):
        if path.is_file():
            sources.append(path)
            put(HERE / "target/cyd_vorbis_format_expanded25_qemu" / path.relative_to(project), path.read_bytes())
    mapping, merged, original_matrices = [], [], []
    for group, relative, expected in MATRICES:
        path = ROOT / relative; raw = path.read_bytes()
        if sha(raw) != expected: raise ValueError("matrix pin " + group)
        matrix = json.loads(raw); sources.append(path); original_matrices.append(fact(path))
        if len(matrix["cases"]) != (9 if group == "floor9" else 8): raise ValueError("matrix shape")
        for local, case in enumerate(matrix["cases"]):
            files = {}
            for kind in ("identification", "setup", "comment", "audio", "ogg"):
                origin = (path.parent / case[kind]).resolve()
                if not origin.is_relative_to(path.parent.resolve()): raise ValueError("case path escaped")
                sources.append(origin)
                destination = origin if group == "floor9" else HERE / "inputs/books16" / case[kind]
                if group != "floor9": put(destination, origin.read_bytes())
                if destination.read_bytes() != origin.read_bytes(): raise ValueError("raw byte copy")
                files[kind] = dict(original=fact(origin), selected=fact(destination))
            mapping.append(dict(case=len(mapping), id=case["id"], original_group=group,
                original_case=local, original_matrix=fact(path), original_reference_source_index=1 if group == "floor9" else 0,
                original_case_fields=case, selected_case_fields=case, fields_changed=[], files=files))
            if group != "floor9": merged.append(case)
    if len(mapping) != 25 or len({m["id"] for m in mapping}) != 25: raise ValueError("all25 unique cases")
    document(HERE / "inputs/books16/matrix.json", dict(schema="explicit-merged-public-books16-v1",
        status="BYTE_COPY_SOURCE_SELECTION_NOT_NEW_REFERENCE_EXECUTION", cases=merged,
        original_matrices=original_matrices[:2], fields_changed=[], case_order="oldbooks8,newbooks8"))
    document(HERE / "source-map.json", dict(schema="expanded25-original-source-map-v1", cases=mapping,
        order="books8,newbooks8,floor9", original_matrices=original_matrices, original_cases_rewritten=False,
        new_reference_commands_executed=False, expanded_target_executed=False))
    spec = importlib.util.spec_from_file_location("expanded25_checked_protocol", HERE / "protocol.py")
    protocol = importlib.util.module_from_spec(spec); spec.loader.exec_module(protocol)
    manifests = [dict(path=str((HERE / "inputs/books16/matrix.json").resolve()), sha256=sha((HERE / "inputs/books16/matrix.json").read_bytes())),
                 dict(path=str((ROOT / MATRICES[2][1]).resolve()), sha256=MATRICES[2][2])]
    contract = protocol.load_contract(manifests)
    model = contract["model"]
    if (len(model["cases"]), model["total_packets"], model["total_pcm"], model["case_mask"]) != (25, 350, 623360, 33554431): raise ValueError("expanded25 totals")
    if [c["id"] for c in model["cases"]] != [c["id"] for c in mapping]: raise ValueError("expanded25 order")
    document(HERE / "contract.json", contract)
    facts = [fact(path) for path in sorted(set(sources))]
    document(HERE / "input-selection.json", dict(schema="expanded25-input-selection-v1", completed=True,
        scope="existing raw input copy and public descriptor accounting only", counts=dict(cases=25, packets=350, pcm=623360, protocol_events=778, mask=33554431),
        contract=fact(HERE / "contract.json"), source_map=fact(HERE / "source-map.json"), original_inputs=facts,
        exact_source_relations={"protocol": "byte-identical checked-prep02", "caller": "byte-identical checked-prep02", "descriptor_header": "unchanged91a040..."},
        fixture_generators_or_codecs_or_SDK_compilers_QEMU_reference_Git_executed=False))
    print(json.dumps(dict(contract=fact(HERE / "contract.json"), model_sha256=contract["contract_sha256"], source_map=fact(HERE / "source-map.json"), counts=dict(cases=25, packets=350, pcm=623360))))


if __name__ == "__main__": main()
