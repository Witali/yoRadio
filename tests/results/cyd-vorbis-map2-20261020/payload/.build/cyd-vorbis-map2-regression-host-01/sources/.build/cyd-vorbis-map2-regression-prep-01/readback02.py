"""Pure saved-input verification for the varied single-bit map2 cohort."""
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "generated02"


def fact(path, relative=None):
    raw = path.read_bytes()
    return dict(path=path.relative_to(relative).as_posix() if relative else str(path),
                bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def main():
    spec = importlib.util.spec_from_file_location("map2_checked_source_revision02", HERE / "generate02.py")
    g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
    manifest = json.loads((OUT / "manifest.json").read_bytes())
    matrix = json.loads((OUT / "matrix.json").read_bytes())
    checks = json.loads((OUT / "pure-checks.json").read_bytes())
    for row in manifest["files"]: assert fact(OUT / row["path"], OUT) == row, row["path"]
    assert len(manifest["files"]) == 43
    assert checks["source_inputs_before"] == checks["source_inputs_after"]
    for row in checks["source_inputs_after"]: assert fact(Path(row["path"])) == row
    expected = g.configurations()
    assert len(matrix["cases"]) == 8 and [c["id"] for c in matrix["cases"]] == [b["id"] for b in expected]
    actual_spectra, actual_audio, rows = {}, {}, []
    all_single_bits = Counter()
    for case, book in zip(matrix["cases"], expected):
        data = {kind: (OUT / case[kind]).read_bytes() for kind in ("identification", "setup", "audio", "comment", "ogg")}
        assert {k: dict(bytes=len(v), sha256=hashlib.sha256(v).hexdigest()) for k, v in data.items()} == case["files"]
        info = data["identification"]
        assert len(info) == 30 and info[:7] == b"\x01vorbis" and info[11] == case["channels"] == 2
        assert int.from_bytes(info[12:16], "little") == case["rate"] == 192000
        short, long = 1 << (info[28] & 15), 1 << (info[28] >> 4)
        assert (short, long) == (case["short"], case["long"]) == (256, 2048)
        parsed = g.inspect_setup(data["setup"], book)
        assert len(parsed["multiplicands"]) == parsed["entries"] * parsed["dimensions"]
        offsets = case["offsets"]; assert len(offsets) == 15 and offsets[0] == 0 and offsets[-1] == len(data["audio"])
        assert all(a < b for a, b in zip(offsets, offsets[1:]))
        packets = [data["audio"][a:b] for a, b in zip(offsets, offsets[1:])]
        syntax = [g.inspect_audio(packet, book, p) for p, packet in enumerate(packets)]
        assert syntax == case["packet_syntax"]
        usage = Counter(e for p in syntax for channel in p["vector_entry_ids"] for e in channel)
        assert dict(sorted((str(k), v) for k, v in usage.items())) == case["vector_book"]["selected_original_id_counts"]
        if parsed["entries"] == 1:
            for packet in syntax:
                bits = [bit for channel in packet["single_entry_wire_bits"] for bit in channel]
                assert Counter(bits) == {0: 8, 1: 8} and packet["token_bits"] == packet["token_count"] == 16
                all_single_bits.update(bits)
        frames = [0] + [((long if a else short) + (long if b else short)) // 4 for a, b in zip(case["mode_flags"], case["mode_flags"][1:])]
        assert case["mode_flags"] == list(g.MODES)
        assert frames == case["expected_packet_frames"] == case["expected_packet_samples"] and sum(frames) == 7040
        pcm = [n * 4 for n in frames]
        assert pcm == case["expected_packet_pcm_bytes"] == case["expected_packet_s16le_bytes"] and sum(pcm) == 28160
        pages = g.base.read_pages(data["ogg"])
        assert [p["packet"] for p in pages] == [info, data["comment"], data["setup"]] + packets
        assert [p["granule"] for p in pages] == [0, 0, 0] + case["packet_granules"]
        assert [p["flags"] for p in pages] == [2] + [0] * 15 + [4]
        actual_spectra[case["id"]] = [p["residue_vectors"] for p in syntax]
        actual_audio[case["id"]] = data["audio"]
        rows.append(dict(id=case["id"], raw_sizes={k: len(v) for k, v in data.items()}, expected_pcm_bytes=28160,
                         active_entry_usage=dict(usage), all_original_multiplicands=len(parsed["multiplicands"])))
    groups = matrix["expected_same_decoder_pcm_equal_groups"]
    assert groups == [[expected[i]["id"], expected[i+1]["id"]] for i in (0, 2, 4, 6)]
    for first, second in groups:
        assert actual_spectra[first] == actual_spectra[second] and actual_audio[first] == actual_audio[second]
    assert all_single_bits == {0: 224, 1: 224}
    assert len(checks["exact_negative_controls"]) == 8 and all(c["rejected"] for c in checks["exact_negative_controls"])
    # The prior zero-only source/proof remains readable and byte-identical history.
    old_manifest = json.loads((HERE / "generated01/manifest.json").read_bytes())
    for row in old_manifest["files"]: assert fact(HERE / "generated01" / row["path"], HERE / "generated01") == row
    for row in old_manifest["source_inputs"]: assert fact(Path(row["path"])) == row
    for row in checks["source_inputs_after"]: assert fact(Path(row["path"])) == row
    result = dict(schema="map2-saved-input-readback-v1", completed=True, construction_only=True,
        cases=8, raw_packets=112, raw_files=32, carriers=8, manifest_files_checked=43,
        expected_pcm_bytes_per_case=28160, expected_total_pcm_bytes=225280,
        exact_negative_controls=checks["exact_negative_controls"], cases_observed=rows,
        expected_pair_groups=groups, actual_saved_audio_equal_for_all_four_pairs=True,
        actual_saved_integer_spectrum_equal_for_all_four_pairs=True,
        actual_PCM_equality_observed=False, single_consumed_bit_counts=dict(all_single_bits),
        previous_zero_only_manifest=fact(HERE / "generated01/manifest.json"),
        previous_zero_only_inputs_and_files_unchanged=True,
        inputs=checks["source_inputs_after"], source_or_campaign_mutations=False,
        actual_codec_SDK_compiler_QEMU_reference_Git_privatebinary_device_executed=False)
    with (HERE / "readback02.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2); stream.write("\n")
    print(json.dumps(dict(readback=fact(HERE / "readback02.json"), cases=8, packets=112,
                         single_bit_counts=dict(all_single_bits), source_only=True)))


if __name__ == "__main__":
    main()
