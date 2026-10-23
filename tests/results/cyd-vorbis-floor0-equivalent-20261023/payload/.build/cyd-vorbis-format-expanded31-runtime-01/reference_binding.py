"""Bind31 cases to existing old17/new8/new12 evidence; no new reference run."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = ROOT / ".build/cyd-vorbis-format-expanded25-prep-02"
BASE_SHA = "3961e32fc5abb5a883260b2932a570908367c46ad2058a210a123336db7638ce"


def need(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def fact(path):
    data = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def derive(contract, mapping):
    pins = json.loads((HERE / "source-pins.json").read_bytes())
    need(fact(BASE / "reference_binding02.py")["sha256"] == BASE_SHA, "corrected25_reference_helper_pin")
    spec = importlib.util.spec_from_file_location("expanded31_existing25_reference_binding", BASE / "reference_binding02.py")
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)  # Definitions only; original guarded main never runs.
    old_contract = json.loads((BASE / "contract.json").read_bytes())
    old_mapping = json.loads((BASE / "source-map.json").read_bytes())
    existing = helper.derive(old_contract, old_mapping)
    need(len(contract["model"]["cases"]) == len(mapping["cases"]) == 31 and
         contract["model"]["cases"][:25] == old_contract["model"]["cases"] and
         [row["id"] for row in mapping["cases"][:25]] == [row["id"] for row in old_mapping["cases"]],
         "all_previous25_model_and_order_unchanged")
    facts = {row["path"]: row for row in existing["proof_facts"]}
    external = []
    def observed(path, expected=None, size=None):
        row = fact(path)
        need(expected is None or row["sha256"] == expected, "reference_or_source_pin:" + str(path))
        need(size is None or row["bytes"] == size, "reference_or_source_size:" + str(path))
        if path.resolve().is_relative_to(ROOT):
            facts[row["path"]] = row
        else:
            external.append(row)
        return row
    for path in (BASE / "reference_binding02.py", BASE / "contract.json", BASE / "source-map.json", HERE / "source-pins.json"):
        observed(path)
    for row in pins["new12_proofs"].values():
        observed(ROOT / row["path"], row["sha256"], row["bytes"])
    qrow, hrow, rrow = (pins["new12_proofs"][key] for key in ("qualification", "host", "host_outer"))
    q = json.loads((ROOT / qrow["path"]).read_bytes())
    host = json.loads((ROOT / hrow["path"]).read_bytes())
    receipt = json.loads((ROOT / rrow["path"]).read_bytes())
    qreceipt = json.loads((ROOT / pins["new12_proofs"]["qualification_outer"]["path"]).read_bytes())
    need(q["completed"] is True and q["result"] == "XIPH_EQUIVALENCE_QUALIFIED_DUAL_NONPASS" and
         q["xiph_reference_qualified"] is True and q["dual_reference_qualified"] is False and
         (q["xiph_cases"], q["native_lookup2_refusals"], q["actual_child_commands_checked"], q["xiph_PCM_equal_pairs"]) == (12, 12, 24, 6) and
         q["original_report_sha256"] == hrow["sha256"] and q["original_outer_returncode"] == 1,
         "actual_full12_Xiph_qualification_scope")
    need(receipt["status"] == qreceipt["status"] == "TERMINAL" and receipt["returncode"] == 1 and qreceipt["returncode"] == 0 and
         type(receipt["owned_pid"]) is int and receipt["owned_pid"] > 0 and
         type(qreceipt["owned_pid"]) is int and qreceipt["owned_pid"] > 0,
         "actual_new12_host_NONPASS_and_qualifier_terminal")
    need(host["completed"] is True and host["xiph_reference_qualified"] is True and host["dual_reference_qualified"] is False and
         len(host["cases"]) == 12 and len(host["commands"]) == 24 and len(host["failures"]) == 12,
         "preserve_full12_original_report_scope")
    # Preserve all actual consumed files: all12 child receipts/logs/WAVs and the
    # original/copy/source witness, not merely the selected six additions.
    for path, row in q["validated_inputs"].items():
        observed(Path(path), row["sha256"], row["bytes"])
    for command in (receipt, qreceipt):
        for path, row in command["logs"].items():
            observed(Path(path), row["sha256"], row["bytes"])
    for origin in mapping["cases"]:
        need(origin["case"] < 31 and contract["model"]["cases"][origin["case"]]["id"] == origin["id"], "source_map_case_order")
        for kind, pair in origin["files"].items():
            for role in ("original", "selected"):
                observed(Path(pair[role]["path"]), pair[role]["sha256"], pair[role]["bytes"])
            need(pair["original"]["sha256"] == pair["selected"]["sha256"], "complete_selected_raw_byte_copy")
    relations = q["historical_Xiph_PCM_equalities"]
    need(len(relations) == 6 and all(row["exact_complete_PCM_equal"] is True for row in relations), "all_six_historical_equivalence_relations")
    rows = list(existing["cases"])
    for model, origin in zip(contract["model"]["cases"][25:], mapping["cases"][25:]):
        need(origin["original_group"] == "newfloor6" and origin["case"] == len(rows), "six_additions_last")
        source_matrix = origin["original_matrix"]
        reference_matrix = origin["reference_matrix"]
        observed(Path(source_matrix["path"]), source_matrix["sha256"], source_matrix["bytes"])
        observed(Path(reference_matrix["path"]), reference_matrix["sha256"], reference_matrix["bytes"])
        case = json.loads(Path(source_matrix["path"]).read_bytes())["cases"][origin["original_case"]]
        need(case == origin["original_case_fields"] == origin["selected_case_fields"] and origin["fields_changed"] == [], "addition_case_unchanged")
        rid = "0-" + model["id"]
        matching = [row for row in host["cases"] if row["id"] == rid]
        qualified = [row for row in q["cases"] if row["id"] == rid]
        need(len(matching) == len(qualified) == 1, "unique_actual_new12_reference_case")
        raw, accepted = matching[0], qualified[0]
        need(raw["input"] == case and raw["source_matrix_sha256"] == reference_matrix["sha256"] and
             Path(raw["source_matrix"]).resolve() == Path(reference_matrix["path"]).resolve(), "actual_new12_case_matrix_binding")
        decoded = raw["decoded"]["libvorbis"]
        need(accepted["xiph_reference_revalidated"] is True and accepted["frames"] == model["frames"][1:] and
             accepted["pcm_bytes"] == model["total_pcm"] == decoded["pcm_bytes"] and accepted["pcm_sha256"] == decoded["pcm_sha256"] and
             (accepted["rate"], accepted["channels"], accepted["bits"]) == (model["rate"], model["channels"], 16), "actual_new12_PCM_metadata_hash")
        relation = [row for row in relations if row["equivalent_id"] == model["id"]]
        need(len(relation) == 1 and relation[0]["historical_pcm_sha256"] == accepted["pcm_sha256"] and
             relation[0]["original_id"] in {case["id"] for case in contract["model"]["cases"][:25]}, "new_minimum_exact_old_original_PCM_relation")
        for kind in ("identification", "setup", "audio"):
            need(model["raw_sha256"][kind] == origin["files"][kind]["original"]["sha256"], "new_model_actual_raw_hash")
        rows.append(dict(case=origin["case"], id=model["id"], original_group="newfloor6", original_reference_id=rid,
            qualification_sha256=qrow["sha256"], original_host_report_sha256=hrow["sha256"], original_host_receipt_sha256=rrow["sha256"],
            original_host_returncode=1, original_matrix=source_matrix, reference_matrix=reference_matrix,
            raw_sha256=model["raw_sha256"], frames=model["frames"], pcm_bytes=model["total_pcm"], rate=model["rate"], channels=model["channels"],
            reference_pcm_sha256=accepted["pcm_sha256"], reference_wav_sha256=decoded["wav_sha256"], xiph_qualified_existing=True,
            native_compared=False, native_lookup2_refusal=True, exact_original_floor0_relation=relation[0]))
    need(len(rows) == 31 and sum(row["pcm_bytes"] for row in rows) == contract["model"]["total_pcm"], "complete31_reference_bindings")
    for row in facts.values():
        need(fact(Path(row["path"])) == row, "reference_fact_changed_during_binding")
    for row in external:
        need(fact(Path(row["path"])) == row, "external_reference_tool_changed_during_binding")
    return dict(schema="expanded31-existing-reference-source-binding-v1", completed=True,
        status="EXACT_SOURCE_BINDING_TO_EXISTING_17_PLUS_8_PLUS_12_XIPH_SCOPES", contract_sha256=contract["contract_sha256"], cases=rows,
        source_scopes=existing["source_scopes"] + [dict(name="new12", qualification_path=qrow["path"], qualification_sha256=qrow["sha256"],
            host_path=hrow["path"], host_sha256=hrow["sha256"], receipt_path=rrow["path"], receipt_sha256=rrow["sha256"], original_returncode=1,
            full_reference_cases=12, selected_cases=6, actual_child_commands=24, exact_equivalence_relations=relations)],
        proof_facts=sorted(facts.values(), key=lambda row: row["path"]), external_reference_tool_identities=external,
        new_reference_commands_executed=False, aggregate_reference_campaign_exists=False, dual_reference_passed=False,
        target_executed=False, target_numeric_comparison_performed=False, full_G6_qualified=False)


def verify(contract, mapping, binding):
    need(derive(contract, mapping) == binding, "expanded31_existing_reference_source_binding_changed")
    return binding
