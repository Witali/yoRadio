"""Summarize saved Rice A/B evidence; importing this module performs no IO."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys

REPOSITORY = next(path for path in Path(__file__).resolve().parents
                  if (path / 'tools/esp32c3_tests/common.py').is_file())
sys.path.insert(0, str(Path(__file__).resolve().parent / 'test-sources/tools/esp32c3_tests'))
from public_streams import no_runtime_faults
from staged_dma import MAX_SAMPLE_GAP_SECONDS, summarize as dma_summary
from summarize_radio_flac import CPU_FIELDS, cpu_intervals, cpu_summary

MINIMUM_INTERVALS = 3
WARMUP_SECONDS = 10
MODES = ('control', 'bytewise')
EXPECTED_FOLDERS = {'radio-bossa-lpc32-http', 'radio-groovesalad-lpc12-http',
                    'stress-flac-48000-2ch-16bit-610s-https', 'aac-alternate-90'}
DECODER_MARKER = re.compile(r'\bPERF (?:AAC|FLAC)\b')
DECODER_VALUES = re.compile(
    r'PERF (?:AAC|FLAC): window (\d+) ms, audio (\d+) ms, decode (\d+) ms')


def interval_coverage(intervals, start, end):
    """Check selected full intervals and uncovered gaps, including both edges."""
    measurement = max(0, end - start)
    observed = sum(row['seconds'] for row in intervals)
    gaps, invalid = [], []
    cursor, previous_end = start, None
    for row in intervals:
        interval_end = row['at']
        interval_start = interval_end - row['seconds']
        if (not math.isfinite(interval_end) or not math.isfinite(row['seconds']) or
                row['seconds'] <= 0 or interval_start < start or interval_end > end):
            invalid.append(dict(interval=row, reason='Invalid or partial interval'))
            continue
        if previous_end is not None and interval_end <= previous_end:
            invalid.append(dict(interval=row, reason='Duplicate or unordered interval'))
        # Host arrival jitter can make board-duration intervals overlap slightly.
        # The raw board duration and host placement remain separately visible.
        if interval_start > cursor:
            gaps.append(dict(start=cursor, end=interval_start, seconds=interval_start-cursor))
        cursor = max(cursor, interval_end)
        previous_end = interval_end
    if cursor < end:
        gaps.append(dict(start=cursor, end=end, seconds=end-cursor))
    maximum_gap = max((gap['seconds'] for gap in gaps), default=0)
    return dict(measurement_seconds=measurement, observed_seconds=observed,
                coverage_percent=100 * observed / measurement if measurement else 0,
                full_intervals=len(intervals), gaps=gaps, invalid_intervals=invalid,
                maximum_gap_seconds=maximum_gap,
                coverage_complete=(measurement > 0 and len(intervals) >= MINIMUM_INTERVALS
                    and not invalid and maximum_gap <= MAX_SAMPLE_GAP_SECONDS))


def malformed_cpu_rows(rows):
    malformed = []
    for row in rows:
        line = row['line']
        if 'PERF CPU' not in line:
            continue
        fields = re.findall(r'(\w+)=([\d.]+)%', line)
        try:
            values = {key: float(value) for key, value in fields}
            valid = (line.count('PERF ') == 1 and 'PERF CPU:' in line and
                re.search(r'\((\d+)\).*PERF CPU:', line) is not None and
                math.isfinite(float(row['at'])) and
                all(sum(key == required for key, _ in fields) == 1 for required in CPU_FIELDS) and
                all(required in values and 0 <= values[required] <= 100 for required in CPU_FIELDS) and
                abs(values.get('busy', 0) + values.get('idle', 0) - 100) < .3)
        except (ValueError, TypeError):
            valid = False
        if not valid:
            malformed.append(row)
    return malformed


def decoder_intervals(rows, start, end):
    intervals, malformed = [], []
    for row in rows:
        if not DECODER_MARKER.search(row['line']):
            continue
        match = DECODER_VALUES.search(row['line'])
        if not match or row['line'].count('PERF ') != 1:
            malformed.append(row)
            continue
        wall, audio, decode = map(int, match.groups())
        try:
            at = float(row['at'])
        except (ValueError, TypeError):
            malformed.append(row)
            continue
        if wall <= 0 or not math.isfinite(at):
            malformed.append(row)
            continue
        if start <= at - wall / 1000 and at <= end:
            intervals.append(dict(at=at, seconds=wall / 1000,
                                  wall_ms=wall, audio_ms=audio, decode_ms=decode))
    return intervals, malformed


def runtime_acceptance(rows, interrupted):
    failures = []
    try:
        no_runtime_faults(rows)
    except AssertionError as error:
        failures.append(str(error))
    if interrupted:
        failures.append('Status observation interrupted: ' + str(interrupted))
    # Apply the canonical gate to individual rows to retain fault evidence,
    # instead of maintaining a narrower local watchdog/error expression.
    fault_rows = []
    for row in rows:
        try:
            no_runtime_faults([row])
        except AssertionError:
            fault_rows.append(row)
    return dict(result='FAIL' if failures else 'PASS', failures=failures), fault_rows


def summarize_batch(mode, folder, batch, data, hashes):
    started, end = batch['started_at'], batch['ended_at']
    start = started + WARMUP_SECONDS
    rows = data['performance']
    malformed = malformed_cpu_rows(rows)
    try:
        cpu, selected_malformed, excluded_gaps = cpu_intervals(rows, start, end)
    except (ValueError, TypeError) as error:
        cpu, selected_malformed, excluded_gaps = [], [], []
        cpu_parse_error = str(error)
    else:
        cpu_parse_error = None
    for row in selected_malformed:
        if row not in malformed:
            malformed.append(row)
    cpu_coverage = interval_coverage(cpu, start, end)
    cpu_result = dict(cpu_summary(cpu), **{
        key: value for key, value in cpu_coverage.items() if key != 'observed_seconds'})
    cpu_result['excluded_gap_seconds'] = sum(gap['seconds'] for gap in excluded_gaps)
    decoder, malformed_decoder = decoder_intervals(rows, start, end)
    decoder_coverage = interval_coverage(decoder, start, end)
    heap, malformed_heap = [], []
    for row in rows:
        if start <= row['at'] <= end and 'PERF CPU:' in row['line']:
            fields = re.findall(r'\b(heap|largest)=(\d+)', row['line'])
            if len(fields) == 2 and {key for key, _ in fields} == {'heap', 'largest'}:
                heap.append({key: int(value) for key, value in fields})
            else:
                malformed_heap.append(row)
    interrupted = batch.get('interrupted', False)
    runtime, faults = runtime_acceptance(rows, interrupted)
    original = data['report'].get('cases', [])
    original_passed = bool(original) and all(case['result'] == 'PASS' for case in original)
    samples = batch.get('samples', [])
    item = dict(mode=mode, case=folder.name, observation=batch['case'],
                board=data['report']['board'], original_acceptance=original,
                original_gates_passed=original_passed, runtime_acceptance=runtime,
                acceptance_passed=original_passed and runtime['result'] == 'PASS',
                seconds=end-started, measured_start=start, measured_end=end,
                interrupted=interrupted, cpu=cpu_result, cpu_intervals=cpu,
                malformed_cpu=malformed, cpu_parse_error=cpu_parse_error,
                cpu_gaps=excluded_gaps, decoder_intervals=decoder,
                decoder_coverage=decoder_coverage, malformed_decoder=malformed_decoder,
                malformed_heap=malformed_heap, fault_rows=faults,
                minimum_rssi=min((sample['rssi'] for sample in samples), default=None),
                median_rssi=statistics.median(sample['rssi'] for sample in samples) if samples else None,
                maximum_http_ms=max((sample['request_ms'] for sample in samples), default=None),
                input_sha256=hashes)
    wall = sum(row['wall_ms'] for row in decoder)
    audio = sum(row['audio_ms'] for row in decoder)
    decode = sum(row['decode_ms'] for row in decoder)
    item.update(decoder_totals=dict(wall_ms=wall, audio_ms=audio, decode_ms=decode),
                decoded_audio_wall_ratio=audio/wall if wall else None,
                elapsed_decode_ms_per_audio_second=1000*decode/audio if audio else None)
    if heap:
        item['heap'] = {key: dict(min=min(row[key] for row in heap),
                first_median=statistics.median(row[key] for row in heap[:3]),
                last_median=statistics.median(row[key] for row in heap[-3:]))
                for key in ('heap', 'largest')}
    try:
        dma = dma_summary(rows, start, end)
        dma['overruns_per_second'] = dma['delta']['q_overruns']/dma['observed_seconds']
        # native_audio_output.c fixes PDM output at 48 kHz stereo s16. These
        # bytes are counted in pdm_write_block after source-rate resampling.
        dma['written_audio_wall_ratio'] = dma['delta']['written_bytes'] / (
            48000 * 2 * 2 * dma['observed_seconds'])
        item['dma'] = dma
    except ValueError as error:
        item['dma_unavailable'] = str(error)
    item['telemetry_complete'] = (not interrupted and not malformed and
        not malformed_decoder and not malformed_heap and cpu_parse_error is None and
        not excluded_gaps and cpu_coverage['coverage_complete'] and
        decoder_coverage['coverage_complete'] and len(heap) >= MINIMUM_INTERVALS and
        item.get('dma', {}).get('coverage_complete', False))
    item['complete'] = item['telemetry_complete']
    item['acceptance_passed'] = item['acceptance_passed'] and item['telemetry_complete']
    return item


def summarize(root):
    root = Path(root)
    cases, original_reports, missing = [], [], []
    seen = set()
    for mode in MODES:
        mode_folder = root / 'physical' / mode
        folders = sorted(path for path in mode_folder.iterdir() if path.is_dir()) if mode_folder.exists() else []
        for folder in folders:
            seen.add((mode, folder.name))
            paths = {name: folder/(name+'.json') for name in ('report', 'status', 'performance')}
            absent = [name for name, path in paths.items() if not path.exists()]
            if paths['report'].exists():
                original_reports.append(dict(mode=mode, case=folder.name,
                    report=json.loads(paths['report'].read_text())))
            if absent:
                missing.append(dict(mode=mode, case=folder.name, reason='Missing suite files', files=absent))
                continue
            data = {name: json.loads(path.read_text()) for name, path in paths.items()}
            hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
            batches = [batch for batch in data['status'] if batch['case'].startswith(('load:', 'tls-record:'))]
            if len(batches) != 1:
                missing.append(dict(mode=mode, case=folder.name,
                    reason='Expected exactly one sustained observation', observations=len(batches)))
            cases.extend(summarize_batch(mode, folder, batch, data, hashes) for batch in batches)
    expected = {(mode, name) for mode in MODES for name in EXPECTED_FOLDERS}
    for mode, name in sorted(expected - seen):
        missing.append(dict(mode=mode, case=name, reason='Missing case folder'))
    for mode, name in sorted(seen - expected):
        missing.append(dict(mode=mode, case=name, reason='Unexpected case folder'))
    phases_path = root / 'physical/phases.json'
    phases = json.loads(phases_path.read_text()) if phases_path.exists() else []
    phase_failures = [phase for phase in phases if phase['code'] != 0]
    expected_phases = {mode+'/'+name for mode, name in expected} | {
        mode+'/install' for mode in MODES} | {'restore'}
    phases_complete = (len(phases) == len(expected_phases) and
                       {phase['name'] for phase in phases} == expected_phases)
    final_path = root / 'physical/final-board.json'
    final = json.loads(final_path.read_text()) if final_path.exists() else None
    all_present = not missing and len(cases) == len(expected)
    telemetry_complete = all_present and all(case['telemetry_complete'] for case in cases)
    original_passed = all_present and all(case['original_gates_passed'] for case in cases)
    runtime_passed = all_present and all(case['runtime_acceptance']['result'] == 'PASS' for case in cases)
    return dict(complete=telemetry_complete, telemetry_complete=telemetry_complete,
                original_gates_passed=original_passed, runtime_gates_passed=runtime_passed,
                acceptance_passed=(telemetry_complete and original_passed and runtime_passed
                    and phases_complete and not phase_failures and final is not None
                    and final['result'] == 'PASS'),
                cases=cases, missing_or_unexpected=missing, original_reports=original_reports,
                phases=phases, phases_complete=phases_complete, phase_failures=phase_failures,
                restored=final['result'] if final else 'UNKNOWN', final_board=final,
                note='Matched awake builds. Original reports and failures retained. CPU is informational. '
                'CPU and decoder totals use complete intervals after 10 s; observed coverage is reported. '
                'Host serial arrival times locate board-duration intervals, with UART timing uncertainty. '
                'DMA covers its first through last selected samples. Overruns are diagnostic and are not '
                'an acoustic gap count. No acoustic qualification or repeated crossover experiment.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    result = summarize(args.root)
    output = args.output or args.root/'summary.json'
    output.write_text(json.dumps(result, indent=2)+'\n')
    for case in result['cases']:
        print(case['mode'], case['case'], 'telemetry complete', case['telemetry_complete'],
              'original gates', case['original_gates_passed'],
              'runtime', case['runtime_acceptance']['result'],
              'CPU', case['cpu'].get('busy_mean_percent'),
              'decode ms/audio s', case['elapsed_decode_ms_per_audio_second'], flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
