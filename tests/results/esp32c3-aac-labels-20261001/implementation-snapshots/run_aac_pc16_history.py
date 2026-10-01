#!/usr/bin/env python3
"""Compare PC16 block/scalar histories to the unmodified C3 decoder in QEMU."""
import sys
import run_aac_packed_history as legacy

VARIANTS = {1: "block8_sbr", 2: "block8_ps", 3: "block8_both",
            4: "scalar_sbr", 5: "scalar_ps", 6: "scalar_both",
            7: "lossless_history_traversal", 0: "wrapper_bypass"}


def parse_log(log):
    if "PCX14_" in log or "PCX16_ARITHMETIC_PASS" not in log:
        raise ValueError("Not a PC16 experiment")
    # Same pinned history layout/matrix and log fields; reuse its strict audit.
    normalized = log.replace("PCX16_", "PCX14_")
    result = legacy.parse_log(normalized)
    result["experiment"] = "complex_history_16_16_side_exponent4"
    result["theoretical_history_payload_saving_bytes_hev2"] = 4188
    blocks = legacy.records(normalized, "BLOCKS")
    expected = {legacy.row_key(r) for r in result["runs"]}
    if len(blocks) != len(expected) or {legacy.row_key(r) for r in blocks} != expected:
        raise ValueError("Missing/duplicate block-path coverage")
    history = {legacy.row_key(r): r for r in result["history"]}
    for b in blocks:
        v = b["variant"]
        pairs = history[legacy.row_key(b)]["pairs"]
        if min(b["blocks8"], b["tail_pairs"], b["scalar_pairs"]) < 0:
            raise ValueError("Invalid block counter")
        if v in (0, 7):
            if b["blocks8"] or b["tail_pairs"] or b["scalar_pairs"]:
                raise ValueError("Control packed history")
        elif v <= 3:
            if 8 * b["blocks8"] + b["tail_pairs"] != pairs or b["scalar_pairs"] or (pairs and not b["blocks8"]):
                raise ValueError("Block path missing or wrong history coverage")
        elif b["scalar_pairs"] != pairs or b["blocks8"] or b["tail_pairs"]:
            raise ValueError("Scalar path coverage mismatch")
    by_key = {legacy.row_key(r): r for r in result["runs"]}
    fields = ("samples", "frames", "different", "over_one", "over_two", "over_limit", "max_l", "max_r", "changed_qmf", "max_shift")
    for (case, variant, run), row in by_key.items():
        if not 1 <= variant <= 3 or case.startswith("lc"):
            continue
        scalar = by_key[(case, variant + 3, run)]
        if any(row[k] != scalar[k] for k in fields):
            raise ValueError("Block/scalar PCM or history differs")
    for s in result["summaries"]:
        s["name"] = VARIANTS[s["variant"]]
    for r in result["runs"]:
        if not 0 <= r["max_shift"] <= 16:
            raise ValueError("PC16 shift outside selected range")
    channel_stats = {(s["variant"], s["run"], s["channel"]): s for s in result.get("error_statistics", [])}
    for (variant, run, channel), s in channel_stats.items():
        if 1 <= variant <= 3:
            scalar = channel_stats[(variant + 3, run, channel)]
            if any(s[k] != scalar[k] for k in s if k != "variant"):
                raise ValueError("Block/scalar per-channel statistics differ")
    result["block_coverage"] = blocks
    return result


if __name__ == "__main__":
    args = legacy.common.make_parser(__doc__, "pc16-history").parse_args()
    sys.exit(legacy.common.run(args, log_parser=parse_log,
                              config_key="YORADIO_QEMU_AAC_PC16_HISTORY_TEST", axis="variant"))
