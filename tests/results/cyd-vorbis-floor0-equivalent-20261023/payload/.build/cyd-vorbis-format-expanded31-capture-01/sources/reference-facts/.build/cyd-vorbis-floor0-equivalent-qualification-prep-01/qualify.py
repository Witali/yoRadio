"""Read-only qualification of recorded floor0 controls; no process or decoder.

The original host outer exit1 and all native lookup2 refusals remain NONPASS.
An exit0 here means only that the distinct recorded Xiph reference evidence and
the six exact representation-equality relations have been independently checked.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import wave

HERE = Path(__file__).resolve().parent
NATIVE_REFUSAL = 3199971767
MODES = [0 if character == "S" else 1 for character in "SSLLLSLSSSLLSS"]
RAW_KINDS = ("identification", "comment", "setup", "audio", "ogg")


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def relative(value):
    need(isinstance(value, str) and value and "\\" not in value and ":" not in value,
         "relative_path_syntax")
    path = Path(value)
    need(not path.is_absolute() and ".." not in path.parts, "relative_path_bounds")
    return path


class Inputs:
    def __init__(self):
        self.rows = {}

    def read(self, path, digest=None, size=None):
        path = Path(path).resolve()
        data = path.read_bytes()
        row = dict(bytes=len(data), sha256=sha(data))
        need(digest is None or row["sha256"] == digest, "input_sha:" + str(path))
        need(size is None or row["bytes"] == size, "input_size:" + str(path))
        need(str(path) not in self.rows or self.rows[str(path)] == row, "input_changed:" + str(path))
        self.rows[str(path)] = row
        return data

    def json(self, path, digest=None, size=None):
        return json.loads(self.read(path, digest, size))

    def stable(self):
        for path, row in self.rows.items():
            data = Path(path).read_bytes()
            need(len(data) == row["bytes"] and sha(data) == row["sha256"], "input_changed_at_end:" + path)


def terminal(receipt, code, timeout):
    need(receipt.get("status") == "TERMINAL" and type(receipt.get("returncode")) is int and
         receipt["returncode"] == code and type(receipt.get("owned_pid")) is int and receipt["owned_pid"] > 0 and
         receipt.get("timeout_seconds") == timeout and receipt.get("elapsed_seconds", -1) >= 0 and
         receipt.get("timed_out", False) is False and receipt.get("interrupted", False) is False and
         not receipt.get("error_type") and "returncode_after_stop" not in receipt, "actual_terminal_facts")


def logs(inputs, receipt, receipt_path):
    need(len(receipt["logs"]) == 2, "both_owned_streams")
    stem = receipt_path.stem
    result = {}
    for stream in ("stdout", "stderr"):
        expected = receipt_path.with_name(stem + "." + stream + ".log").resolve()
        matches = [row for path, row in receipt["logs"].items() if Path(path).resolve() == expected]
        need(len(matches) == 1, "owned_stream_path:" + stream)
        result[stream] = inputs.read(expected, matches[0]["sha256"], matches[0]["bytes"])
    return result


def crc(data):
    result = 0
    for octet in data:
        result ^= octet << 24
        for _ in range(8):
            result = ((result << 1) ^ (0x04c11db7 if result & 0x80000000 else 0)) & 0xffffffff
    return result


def carrier(data):
    offset, pages, serial = 0, [], None
    while offset < len(data):
        need(len(data) - offset >= 27 and data[offset:offset + 5] == b"OggS\0", "carrier_header")
        count = data[offset + 26]
        laces = data[offset + 27:offset + 27 + count]
        size = 27 + count + sum(laces)
        raw = data[offset:offset + size]
        need(count > 0 and len(laces) == count and laces[-1] != 255 and len(raw) == size,
             "complete_one_packet_page")
        flags, granule, current_serial, sequence = struct.unpack_from("<BQII", raw, 5)
        checksum = int.from_bytes(raw[22:26], "little")
        need(checksum == crc(raw[:22] + bytes(4) + raw[26:]) and sequence == len(pages), "carrier_CRC_sequence")
        if serial is None:
            serial = current_serial
        need(current_serial == serial and flags == (2 if sequence == 0 else 4 if sequence == 16 else 0),
             "carrier_serial_BOS_EOS_flags")
        pages.append(dict(data=raw[27 + count:], granule=granule))
        offset += size
    need(offset == len(data) and len(pages) == 17, "exact_17_pages")
    return pages


def frozen(inputs, repository, campaign, report):
    result = {}
    for origin, row in report["inputs"].items():
        source = Path(origin).resolve()
        need(source.is_relative_to(repository), "recorded_source_outside_repository")
        snapshot = (campaign / relative(row["snapshot"])).resolve()
        need(snapshot.is_relative_to(campaign / "sources"), "snapshot_path_bounds")
        original = inputs.read(source, row["sha256"], row["bytes"])
        need(inputs.read(snapshot, row["sha256"], row["bytes"]) == original, "source_snapshot_equality")
        key = str(source).casefold()
        need(key not in result, "ambiguous_recorded_input")
        result[key] = original
    return result


def recorded_source(index, path):
    key = str(Path(path).resolve()).casefold()
    need(key in index, "unbound_recorded_source:" + str(path))
    return index[key]


def raw_case(case, matrix_path, source_index):
    parts = {kind: recorded_source(source_index, matrix_path.parent / relative(case[kind])) for kind in RAW_KINDS}
    info = parts["identification"]
    need(len(info) == 30 and info[:7] == b"\x01vorbis" and info[7:11] == bytes(4) and info[16:28] == bytes(12) and info[29] == 1 and
         parts["setup"][:7] == b"\x05vorbis" and parts["comment"][:7] == b"\x03vorbis", "full_public_headers")
    rate, channels = int.from_bytes(info[12:16], "little"), info[11]
    short, long = 1 << (info[28] & 15), 1 << (info[28] >> 4)
    need((rate, channels, short, long) == (case["rate"], case["channels"], case["short"], case["long"]) and
         rate == 48000 and channels == 2 and (short, long) in ((64, 256), (256, 2048), (64, 2048)) and
         case["bits"] == 16, "actual_identification_metadata")
    offsets = case["offsets"]
    need(case["mode_flags"] == MODES and case["packet_count"] == 14 and len(offsets) == 15 and
         offsets[0] == 0 and offsets[-1] == len(parts["audio"]) and
         all(type(value) is int for value in offsets) and all(a < b for a, b in zip(offsets, offsets[1:])),
         "complete_audio_offsets_modes")
    frames = [0] + [((long if a else short) + (long if b else short)) // 4 for a, b in zip(MODES, MODES[1:])]
    need(frames == case["expected_packet_frames"] and sum(frames) == case["expected_raw_samples"] and
         [n * 4 for n in frames] == case["expected_packet_s16le_bytes"] and
         sum(frames) * 4 == case["expected_s16le_bytes"], "independent_overlap_frames")
    pages = carrier(parts["ogg"])
    packets = [parts[kind] for kind in ("identification", "comment", "setup")] + [
        parts["audio"][a:b] for a, b in zip(offsets, offsets[1:])]
    need([page["data"] for page in pages] == packets and [page["granule"] for page in pages[:3]] == [0, 0, 0],
         "carrier_raw_header_packet_binding")
    total = 0
    granules = []
    for index, packet in enumerate(packets[3:]):
        total += frames[index]
        granules.append(total)
        need(packet[0] & 3 == MODES[index] << 1 and pages[index + 3]["granule"] == total, "mode_granule")
        if MODES[index]:
            need(0 < index < 13 and (packet[0] >> 2) & 1 == MODES[index - 1] and
                 (packet[0] >> 3) & 1 == MODES[index + 1], "long_window_neighbor_flags")
    need(granules == case["packet_granules"], "declared_granules")
    return parts, frames


def pcm_evidence(wav_data, md5_data, frames):
    need(wav_data[:4] == b"RIFF" and wav_data[8:12] == b"WAVE" and
         int.from_bytes(wav_data[4:8], "little") + 8 == len(wav_data), "complete_RIFF_WAV_bytes")
    with wave.open(io.BytesIO(wav_data), "rb") as stream:
        need((stream.getcomptype(), stream.getframerate(), stream.getnchannels(), stream.getsampwidth(), stream.getnframes()) ==
             ("NONE", 48000, 2, 2, sum(frames)), "actual_WAV_metadata")
        pcm = stream.readframes(sum(frames) + 1)
    need(len(pcm) == sum(frames) * 4, "complete_PCM_length")
    text = md5_data.decode("utf-8").replace("\r\n", "\n")
    for pattern in (r"^#format: frame checksums$", r"^#version: 2$", r"^#hash: MD5$",
                    r"^#tb 0: 1/48000$", r"^#codec_id 0: pcm_s16le$", r"^#sample_rate 0: 48000$"):
        need(re.search(pattern, text, re.M), "framemd5_header:" + pattern)
    rows = [line for line in text.splitlines() if line.strip() and not line.startswith("#")]
    need(len(rows) == 13 and len(frames) == 14 and frames[0] == 0, "all_nonprimer_MD5_packets")
    position = timestamp = 0
    transition_bytes, transition_channels = {}, {}
    for index, (line, count) in enumerate(zip(rows, frames[1:]), 1):
        columns = [column.strip() for column in line.split(",")]
        size = count * 4
        need(len(columns) == 6 and [int(value) for value in columns[:5]] == [0, timestamp, timestamp, count, size],
             "actual_packet_PTS_duration_size")
        chunk = pcm[position:position + size]
        need(len(chunk) == size and hashlib.md5(chunk).hexdigest() == columns[5], "packet_MD5_matches_WAV_PCM")
        transition = "SL"[MODES[index - 1]] + "SL"[MODES[index]]
        transition_bytes[transition] = transition_bytes.get(transition, 0) + sum(value != 0 for value in chunk)
        channels = transition_channels.setdefault(transition, [0, 0])
        for channel in range(2):
            channels[channel] += sum(chunk[pos:pos + 2] != b"\0\0" for pos in range(channel * 2, size, 4))
        position += size
        timestamp += count
    need(position == len(pcm) and set(transition_bytes) == {"SS", "SL", "LS", "LL"} and
         all(transition_bytes.values()) and all(all(counts) for counts in transition_channels.values()),
         "each_channel_nonzero_all_transitions")
    return pcm, dict(rate=48000, channels=2, bits=16, frames=frames[1:], pcm_bytes=len(pcm),
        nonzero_bytes=sum(value != 0 for value in pcm), transition_nonzero_bytes=transition_bytes,
        transition_nonzero_frames_per_channel=transition_channels,
        wav_sha256=sha(wav_data), pcm_sha256=sha(pcm))


def expected_argv(ffmpeg, folder, decoder):
    return [ffmpeg, "-nostdin", "-n", "-hide_banner", "-loglevel", "error", "-xerror", "-err_detect", "explode",
        "-c:a", decoder, "-i", str(folder / "input.ogg"), "-map", "0:a:0", "-map_metadata", "-1", "-fflags", "+bitexact",
        "-flags:a", "+bitexact", "-c:a", "pcm_s16le", "-f", "wav", str(folder / (decoder + ".wav")),
        "-map", "0:a:0", "-map_metadata", "-1", "-flags:a", "+bitexact", "-c:a", "pcm_s16le", "-f", "framemd5", "-"]


def child(inputs, repository, campaign, report, case, decoder, frames, command_index, pins, historical=False):
    name = "cases/" + case["id"] + "/decode-" + decoder
    command = command_index[name]
    need(command["receipt"] == name + ".json", "child_receipt_role")
    path = campaign / relative(command["receipt"])
    receipt = inputs.json(path, command["sha256"])
    terminal(receipt, NATIVE_REFUSAL if decoder == "vorbis" else 0, 30)
    ffmpeg = next(path for path in report["tools"] if Path(path).name == "ffmpeg.exe")
    need(receipt["argv"] == expected_argv(ffmpeg, path.parent, decoder) and Path(receipt["cwd"]).resolve() == repository and
         receipt["runner_sha256"] == pins["capture_sha256"] and receipt["executable_sha256"] == pins["tools"]["ffmpeg.exe"],
         "exact_actual_child_argv_tool_cwd")
    streams = logs(inputs, receipt, path)
    if decoder == "vorbis":
        need(not streams["stdout"] and b"Codebook lookup type not supported." in streams["stderr"] and
             b"Setup header corrupt." in streams["stderr"] and "vorbis" not in case["decoded"], "documented_native_lookup2_refusal")
        return None, dict(returncode=NATIVE_REFUSAL, owned_pid=receipt["owned_pid"],
            diagnosis="Codebook lookup type not supported.", PCM_accepted=False)
    need(not streams["stderr"] and set(case["decoded"]) == {"libvorbis"}, "strict_Xiph_only_decode")
    recorded = case["decoded"]["libvorbis"]
    wav_data = inputs.read(path.parent / "libvorbis.wav", recorded["wav_sha256"])
    pcm, evidence = pcm_evidence(wav_data, streams["stdout"], frames)
    expected = {key: evidence[key] for key in recorded}
    need(expected == recorded and (historical or evidence == recorded), "recomputed_reference_report_evidence")
    return pcm, evidence


def outer(inputs, repository, path, pins, role):
    receipt = inputs.json(path, pins["artifacts"][role]["sha256"])
    spec = pins["outer_facts"][role]
    need(spec["returncode"] == (1 if role in ("outer", "historical-outer") else 0), "original_outer_returncode_policy")
    terminal(receipt, spec["returncode"], spec["timeout_seconds"])
    need(receipt["argv"] == spec["argv"] and Path(receipt["cwd"]).resolve() == repository and
         receipt["runner_sha256"] == pins["capture_sha256"] and receipt["executable_sha256"] == pins["tools"]["python.exe"],
         "actual_outer_argv_tool_cwd:" + role)
    return receipt, logs(inputs, receipt, path)


def report_scope(report, pins, driver):
    need(report["schema"] == "public-vorbis-format-corpus-host-v1" and report["completed"] is True and
         report["xiph_reference_qualified"] is True and report["dual_reference_qualified"] is False and
         report["target_executed"] is False and report["production_changed"] is False and
         report["driver_sha256"] == driver and report["parser_source_sha256"] == pins["parser_sha256"] and
         report["capture_sha256"] == pins["capture_sha256"] and report["cross_reference_pcm16_max_error_allowed"] == 2,
         "preserved_report_scope_and_NONPASS")
    need(len(report["tools"]) == 2 and {Path(path).name: digest for path, digest in report["tools"].items()} == pins["tools"],
         "actual_reference_tool_identities")


def qualify(args, result, save):
    inputs = Inputs()
    result["validated_inputs"] = inputs.rows
    pins = inputs.json(HERE / "pins.json")
    inputs.read(__file__, pins["qualifier_sha256"])
    repository = args.repository.resolve()
    for role, row in pins["artifacts"].items():
        inputs.read(repository / relative(row["path"]), row["sha256"], row["bytes"])
    for path, digest in pins["tool_paths"].items():
        inputs.read(path, digest)
    campaign = args.campaign.resolve()
    need(campaign == repository / pins["campaign"] and args.outer.resolve() == repository / pins["artifacts"]["outer"]["path"],
         "exact_campaign_profile")
    receipt, streams = outer(inputs, repository, args.outer.resolve(), pins, "outer")
    need(not streams["stderr"], "host_outer_stderr")
    report = inputs.json(campaign / "report.json", pins["artifacts"]["report"]["sha256"])
    report_scope(report, pins, pins["driver_sha256"])
    source_index = frozen(inputs, repository, campaign, report)
    generated = repository / pins["generated"]
    manifest = inputs.json(generated / "manifest.json", pins["artifacts"]["manifest"]["sha256"])
    need(manifest["codec_execution"] is False and manifest["validity_qualified"] is False and
         manifest["generator_sha256"] == pins["artifacts"]["generator"]["sha256"] and
         manifest["source_pins_sha256"] == pins["artifacts"]["source-pins"]["sha256"], "manifest_source_binding")
    generated_paths = []
    for row in manifest["files"]:
        path = relative(row["path"])
        need(path.as_posix() not in generated_paths, "duplicate_manifest_path")
        generated_paths.append(path.as_posix())
        inputs.read(generated / path, row["sha256"], row["bytes"])
    need(len(generated_paths) == 77 and set(generated_paths) | {"manifest.json"} == {
        path.relative_to(generated).as_posix() for path in generated.rglob("*") if path.is_file()}, "complete_78_file_manifest")
    source_pins = inputs.json(repository / pins["artifacts"]["source-pins"]["path"])
    for row in source_pins["local_inputs"]:
        inputs.read(repository / relative(row["path"]), row["sha256"], row["bytes"])
    for role in ("generation-outer", "witness-outer"):
        _, command_streams = outer(inputs, repository, repository / pins["artifacts"][role]["path"], pins, role)
        need(not command_streams["stderr"], "source_command_stderr")
        observed = json.loads(command_streams["stdout"])
        if role == "generation-outer":
            need(observed["additions"] == 6 and observed["comparison_cases"] == 12 and observed["files"] == 78 and
                 observed["manifest_sha256"] == pins["artifacts"]["manifest"]["sha256"], "actual_generation_result")
        else:
            need(observed == dict(result="CONSTRUCTION_EQUIVALENCE_WITNESSED", pairs=6, controls=3,
                 actual_PCM_equality_observed=False), "actual_witness_result")
    witness = inputs.json(repository / pins["artifacts"]["witness-report"]["path"])
    need(witness["result"] == "CONSTRUCTION_EQUIVALENCE_WITNESSED" and witness["generated_manifest_sha256"] ==
         pins["artifacts"]["manifest"]["sha256"] and witness["generated_matrix_sha256"] == pins["artifacts"]["additions-matrix"]["sha256"] and
         witness["source_pins_sha256"] == pins["artifacts"]["source-pins"]["sha256"] and witness["witness_sha256"] ==
         pins["artifacts"]["witness-source"]["sha256"] and len(witness["pairs"]) == 6 and
         witness["negative_controls"] == [dict(name=name, result="EXPECTED_REJECTION", exact_error=error)
            for name, error in (("wrong-minimum", "equivalent_minimum"), ("wrong-delta", "equivalent_delta"),
                                ("wrong-multiplicand", "multiplicand_shift"))], "actual_source_witness_binding")
    need(all(witness[key] is False for key in ("actual_decoder_or_reference_run", "actual_PCM_equality_observed",
        "floor_curve_residue_synthesis_computed", "numeric_qualified", "full_G6_qualified", "original_campaigns_reclassified")),
         "source_witness_scope")
    need(all(len(pair["packets"]) == 14 and [packet["packet"] for packet in pair["packets"]] == list(range(14))
             for pair in witness["pairs"]), "actual_source_witness_all84_packets")
    matrix_path = generated / "comparison-matrix.json"
    matrix = json.loads(recorded_source(source_index, matrix_path))
    need(sha(recorded_source(source_index, matrix_path)) == pins["artifacts"]["comparison-matrix"]["sha256"] and
         len(matrix["cases"]) == len(report["cases"]) == 12 and [case["id"] for case in matrix["cases"]] == pins["case_ids"],
         "exact_twelve_case_order")
    groups = matrix["expected_same_decoder_pcm_equal_groups"]
    need(groups == [[row["original_id"], row["equivalent_id"]] for row in witness["pairs"]] and len(groups) == 6,
         "six_actual_witness_pair_identities")
    commands = {command["name"]: command for command in report["commands"]}
    expected_names = ["cases/0-" + case["id"] + "/decode-" + decoder for case in matrix["cases"] for decoder in ("vorbis", "libvorbis")]
    need(len(commands) == 24 and [command["name"] for command in report["commands"]] == expected_names, "all24_actual_child_commands")
    pcms, raw_originals, failures = {}, {}, []
    for case, recorded in zip(matrix["cases"], report["cases"]):
        case_id = "0-" + case["id"]
        need(recorded["id"] == case_id and recorded["input"] == case and Path(recorded["source_matrix"]).resolve() == matrix_path and
             recorded["source_matrix_sha256"] == pins["artifacts"]["comparison-matrix"]["sha256"], "case_source_identity")
        parts, frames = raw_case(case, matrix_path, source_index)
        need(inputs.read(campaign / "cases" / case_id / "input.ogg", recorded["ogg_sha256"]) == parts["ogg"], "actual_decoded_input")
        _, refusal = child(inputs, repository, campaign, report, recorded, "vorbis", frames, commands, pins)
        pcm, evidence = child(inputs, repository, campaign, report, recorded, "libvorbis", frames, commands, pins)
        expected_failure = dict(stage="vorbis", error="RuntimeError('Nonpassing reference command cases/" + case_id + "/decode-vorbis')")
        need(recorded["failures"] == [expected_failure], "only_documented_native_failure")
        failures.append(dict(case=case_id, **expected_failure))
        pcms[case["id"]] = pcm
        raw_originals[case["id"]] = parts
        result["cases"].append(dict(id=case_id, xiph_reference_revalidated=True, native=refusal, **evidence))
        save()
    need(failures == report["failures"], "all12_original_failures_preserved")
    expected_relations = [dict(decoder=decoder, kind="equal", cases=group,
        passed=decoder == "libvorbis" and pcms[group[0]] == pcms[group[1]])
        for decoder in ("vorbis", "libvorbis") for group in groups]
    need(all(row["passed"] for row in expected_relations if row["decoder"] == "libvorbis") and
         expected_relations == report["metamorphic_checks"], "six_exact_complete_Xiph_PCM_pairs")
    printed = [json.loads(line) for line in streams["stdout"].decode().splitlines() if line.strip()]
    need(len(printed) == 13 and [row["case"] for row in printed[:-1]] == [case["id"] for case in report["cases"]] and
         all(row["decoded"] == ["libvorbis"] and row["failures"] == 1 and row["max_error"] is None for row in printed[:-1]) and
         printed[-1] == dict(completed=True, xiph_reference_qualified=True, dual_reference_qualified=False), "actual_host_outer_result")
    historical = repository / pins["historical_campaign"]
    old_report = inputs.json(historical / "report.json", pins["artifacts"]["historical-report"]["sha256"])
    old_receipt, old_streams = outer(inputs, repository, repository / pins["artifacts"]["historical-outer"]["path"], pins, "historical-outer")
    old_printed = [line for line in old_streams["stdout"].decode().splitlines() if line.strip()]
    need(not old_streams["stderr"] and old_printed and json.loads(old_printed[-1]) ==
         dict(completed=True, xiph_reference_qualified=True, dual_reference_qualified=False), "historical_outer_NONPASS")
    report_scope(old_report, pins, pins["historical_driver_sha256"])
    need(len(old_report["cases"]) == 17 and len(old_report["commands"]) == 34, "original_full17_unchanged")
    old_index = frozen(inputs, repository, historical, old_report)
    old_commands = {command["name"]: command for command in old_report["commands"]}
    need(len(old_commands) == 34, "original_command_roles_unique")
    historical_rows = []
    for old_id, equivalent_id in groups:
        candidates = [case for case in old_report["cases"] if case["id"] == "1-" + old_id and case["input"]["id"] == old_id]
        need(len(candidates) == 1, "unique_historical_original")
        recorded = candidates[0]
        path = Path(recorded["source_matrix"]).resolve()
        need(recorded["source_matrix_sha256"] == pins["original_matrix_sha256"] and
             sha(recorded_source(old_index, path)) == pins["original_matrix_sha256"], "historical_original_matrix_binding")
        parts, frames = raw_case(recorded["input"], path, old_index)
        need(parts == raw_originals[old_id] and inputs.read(historical / "cases" / recorded["id"] / "input.ogg",
             recorded["ogg_sha256"]) == parts["ogg"], "historical_original_raw_equality")
        pcm, evidence = child(inputs, repository, historical, old_report, recorded, "libvorbis", frames, old_commands, pins, historical=True)
        need(pcm == pcms[old_id] == pcms[equivalent_id], "historical_Xiph_complete_PCM_equality")
        historical_rows.append(dict(original_id=old_id, historical_id=recorded["id"], equivalent_id=equivalent_id,
            historical_pcm_sha256=sha(pcm), historical_pcm_bytes=len(pcm), exact_complete_PCM_equal=True))
    inputs.stable()
    result.update(result="XIPH_EQUIVALENCE_QUALIFIED_DUAL_NONPASS", completed=True, xiph_reference_qualified=True,
        xiph_cases=12, native_lookup2_refusals=12, actual_child_commands_checked=24, xiph_PCM_equal_pairs=6,
        historical_six_Xiph_commands_checked=6, historical_Xiph_PCM_equalities=historical_rows,
        original_report_sha256=pins["artifacts"]["report"]["sha256"], original_outer_returncode=1,
        original_dual_reference_qualified=False, dual_reference_qualified=False,
        original_metamorphic_checks=expected_relations, original_failures=report["failures"],
        raw_packets_checked=168, xiph_PCM_bytes=sum(len(pcm) for pcm in pcms.values()),
        project_numeric_policy=2, numeric_policy_changed=False,
        scope="Recorded Xiph references and exact representation relations only; no decoder/target/conformance qualification")
    save()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("repository", "campaign", "outer", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    repository, output = args.repository.resolve(), args.output.resolve()
    protected = (HERE, args.campaign.resolve(), repository / ".build/cyd-vorbis-floor0-equivalent-generated-01",
                 repository / ".build/cyd-vorbis-floor0-equivalent-prep-01", repository / ".build/cyd-vorbis-format-corpus-host-01")
    need(output != repository / ".build" and output.is_relative_to(repository / ".build") and not output.exists() and
         all(not output.is_relative_to(path) and not path.is_relative_to(output) for path in protected), "fresh_independent_output")
    output.mkdir(parents=True, exist_ok=False)
    result = dict(schema="floor0-equivalent-recorded-reference-qualification-v1", result="INCOMPLETE", completed=False,
        xiph_reference_qualified=False, dual_reference_qualified=False, target_executed=False, production_changed=False,
        numeric_reference_qualified=False, standard_conformance_qualified=False, full_G6_qualified=False,
        physical_device=False, original_campaigns_reclassified=False, cases=[])
    def save():
        path = output / "qualification.json.tmp"
        path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        path.replace(output / "qualification.json")
    save()
    try:
        qualify(args, result, save)
    except BaseException as error:
        result.update(result="INTERRUPTED" if isinstance(error, KeyboardInterrupt) else "REJECTED", completed=False,
            xiph_reference_qualified=False, dual_reference_qualified=False, error_type=type(error).__name__, error=str(error))
        save()
        return 130 if isinstance(error, KeyboardInterrupt) else 1
    print(json.dumps({key: result[key] for key in ("result", "xiph_reference_qualified", "dual_reference_qualified",
        "xiph_cases", "native_lookup2_refusals", "actual_child_commands_checked", "xiph_PCM_equal_pairs", "xiph_PCM_bytes")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
