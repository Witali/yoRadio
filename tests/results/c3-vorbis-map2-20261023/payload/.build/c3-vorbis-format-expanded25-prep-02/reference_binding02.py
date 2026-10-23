"""Bind25 exact raw cases to two existing completed reference qualifications.

Read-only stdlib facts. Does not execute a qualifier, decoder, SDK or target.
Historical source identity is checked through saved snapshots, not mutable originals.
"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PROOFS = [
    ("old17", ".build/cyd-vorbis-format-corpus-qualified-01/qualification.json", "d269d71ab02568fcb549c5abf39e4daf8ffcd082b1ede3c259351615768e02b0",
     ".build/cyd-vorbis-format-corpus-host-01/report.json", "eaf3d8033406d5c6844f5dd6e3f42b26195d6e03b3293c27ea03353d6ca0ae29",
     ".build/cyd-vorbis-format-corpus-host-01-command.json", "799bb892e5b12e0ccc13fc02607aefe49527f51568d0aecfe8a98ac88c492773", (17, 7, 10, 238, 398080)),
    ("new8", ".build/cyd-vorbis-map2-regression-qualified-01/qualification.json", "bb78d2478d6e2a191202098443f5d224cda37fe7c44b33052de005ce10662bc4",
     ".build/cyd-vorbis-map2-regression-host-01/report.json", "5701c50e49118123e059c2a48a152f1fdd2f9def3bffb84053759b51c9a8df88",
     ".build/cyd-vorbis-map2-regression-host-01-command.json", "829899ce49f473962c2abc838fb9a1c6a6be14cf1ec007e66c464f7cff09bc2f", (8, 0, 8, 112, 225280))]


def need(value, reason):
    if not value: raise RuntimeError(reason)


def fact(path):
    raw = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def derive(contract, mapping):
    facts, scopes = {}, {}
    def observed(path, expected=None):
        item = fact(path)
        need(path.resolve().is_relative_to(ROOT), "source/reference fact outside checkout")
        need(expected is None or item["sha256"] == expected, "pinned reference/source bytes differ " + str(path))
        facts[item["path"]] = item
        return item
    for name, qpath, qsha, hpath, hsha, rpath, rsha, totals in PROOFS:
        q, host, receipt = [json.loads((ROOT / p).read_bytes()) for p in (qpath, hpath, rpath)]
        for p, digest in ((qpath, qsha), (hpath, hsha), (rpath, rsha)): observed(ROOT / p, digest)
        need(q["completed"] is True and q["reference_corpus_qualified"] is True and q["original_dual_reference_passed"] is False, "completed scoped Xiph qualification required")
        need(tuple(q[k] for k in ("xiph_cases", "native_compared", "native_lookup2_refusals", "paired_raw_packets", "expected_pcm_bytes")) == totals, "exact existing proof scope")
        need(q["original_report_sha256"] == hsha and q["original_outer_receipt_sha256"] == rsha, "actual qualifier/report/receipt linkage")
        need(receipt["status"] == "TERMINAL" and type(receipt["returncode"]) is int and receipt["returncode"] == 1, "original dual-reference terminal NONPASS preserved")
        need(host["completed"] is True and host["xiph_reference_qualified"] is True and host["dual_reference_qualified"] is False and len(host["cases"]) == totals[0] and len(host["failures"]) == totals[2], "exact original host scope")
        # Current source may have advanced. Actual historical snapshots remain authoritative.
        for original, row in host["inputs"].items():
            snapshot = ((ROOT / hpath).parent / row["snapshot"]).resolve()
            need(snapshot.is_relative_to((ROOT / hpath).parent.resolve()), "snapshot boundary")
            item = observed(snapshot, row["sha256"])
            need("bytes" not in row or item["bytes"] == row["bytes"], "historical snapshot size")
        scopes[name] = dict(qualification_path=qpath, qualification_sha256=qsha, host_path=hpath, host_sha256=hsha,
            receipt_path=rpath, receipt_sha256=rsha, original_returncode=1, totals=list(totals),
            qualification=q, host=host)
    need(len(contract["model"]["cases"]) == len(mapping["cases"]) == 25, "all25 source cases")
    rows = []
    for model, origin in zip(contract["model"]["cases"], mapping["cases"]):
        need(model["id"] == origin["id"] and origin["case"] == len(rows), "strict selected source order")
        matrix_fact = origin["original_matrix"]; observed(Path(matrix_fact["path"]), matrix_fact["sha256"])
        matrix = json.loads(Path(matrix_fact["path"]).read_bytes())
        original_case = matrix["cases"][origin["original_case"]]
        need(original_case == origin["original_case_fields"] == origin["selected_case_fields"] and origin["fields_changed"] == [], "original case fields changed")
        scope = scopes["new8" if origin["original_group"] == "newbooks8" else "old17"]
        rid = f"{origin['original_reference_source_index']}-{model['id']}"
        raw = [c for c in scope["host"]["cases"] if c["id"] == rid]
        qualified = [c for c in scope["qualification"]["cases"] if c["id"] == rid]
        need(len(raw) == len(qualified) == 1, "one real scoped reference case")
        raw, qualified = raw[0], qualified[0]
        need(raw["input"] == original_case and raw["source_matrix_sha256"] == matrix_fact["sha256"] and Path(raw["source_matrix"]).resolve() == Path(matrix_fact["path"]).resolve(), "actual original case/matrix binding")
        need(qualified["xiph_qualified"] is True and qualified["frames"] == model["frames"][1:] and qualified["pcm_bytes"] == model["total_pcm"] and all(qualified["transition_nonzero_bytes"].values()), "existing Xiph frame/nonzero/PCM binding")
        decoded = raw["decoded"]["libvorbis"]
        need((decoded["rate"], decoded["channels"], decoded["bits"]) == (model["rate"], 2, 16) and decoded["pcm_sha256"] == qualified["pcm_sha256"] and decoded["pcm_bytes"] == model["total_pcm"], "actual host decoded metadata/hash binding")
        for kind, paths in origin["files"].items():
            for role in ("original", "selected"):
                item = observed(Path(paths[role]["path"]), paths[role]["sha256"])
                need(item["bytes"] == paths[role]["bytes"], "copied raw file size")
            need(paths["original"]["sha256"] == paths["selected"]["sha256"], "raw copy identity")
            if kind in ("identification", "setup", "audio"):
                need(model["raw_sha256"][kind] == paths["original"]["sha256"], "model raw SHA binding")
                need(scope["host"]["inputs"][paths["original"]["path"]]["sha256"] == model["raw_sha256"][kind], "real host raw SHA binding")
        rows.append(dict(case=origin["case"], id=model["id"], original_group=origin["original_group"], original_reference_id=rid,
            qualification_sha256=scope["qualification_sha256"], original_host_report_sha256=scope["host_sha256"], original_host_receipt_sha256=scope["receipt_sha256"], original_host_returncode=1,
            original_matrix=matrix_fact, raw_sha256=model["raw_sha256"], frames=model["frames"], pcm_bytes=model["total_pcm"],
            rate=model["rate"], channels=2, reference_pcm_sha256=qualified["pcm_sha256"], reference_wav_sha256=decoded["wav_sha256"],
            xiph_qualified_existing=True, native_compared=qualified["native_compared"], native_lookup2_refusal=qualified["native_lookup2_refusal"]))
    need(len(rows) == 25 and sum(c["pcm_bytes"] for c in rows) == 623360, "all25 complete reference-source bindings")
    for item in facts.values(): need(fact(Path(item["path"])) == item, "source/reference changed during binding")
    return dict(schema="expanded25-existing-reference-source-binding-v1", completed=True,
        status="EXACT_SOURCE_BINDING_TO_EXISTING_17_PLUS_8_XIPH_QUALIFICATIONS", contract_sha256=contract["contract_sha256"],
        cases=rows, source_scopes=[{k: v for k, v in scope.items() if k not in ("host", "qualification")} for scope in scopes.values()],
        proof_facts=sorted(facts.values(), key=lambda x: x["path"]), new_reference_commands_executed=False,
        aggregate_reference_campaign_exists=False, dual_reference_passed=False, target_executed=False,
        target_numeric_comparison_performed=False, full_G6_qualified=False)


def verify(contract, mapping, binding):
    need(derive(contract, mapping) == binding, "expanded25 source/reference binding differs")
    return binding


if __name__ == "__main__":
    value = derive(json.loads((HERE / "contract.json").read_bytes()), json.loads((HERE / "source-map.json").read_bytes()))
    with (HERE / "reference-binding02.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2); stream.write("\n")
    print(json.dumps(dict(binding=fact(HERE / "reference-binding02.json"), cases=len(value["cases"]), new_reference_commands=False)))
