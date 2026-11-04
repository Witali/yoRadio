"""Owned data-only reference-subphase and future normalizer gate readers."""
import hashlib
import json
from pathlib import Path
import re


def need(value, reason):
    if not value:
        raise ValueError(reason)


def fields(line):
    tokens = line.split(); result = {}
    for token in tokens[1:]:
        key, separator, value = token.partition('=')
        need(separator and key not in result, 'unique complete observation fields')
        result[key] = int(value) if re.fullmatch('-?[0-9]+', value) and key not in ('sha256', 'hex') else value
    return tokens[0], result


def reference_subphase(capture):
    """Authenticate a finite completed reference phase, never a whole-run PASS."""
    capture = Path(capture)
    report_data = (capture / 'report.json').read_bytes()
    report = json.loads(report_data)
    log_path = capture / 'qemu.stdout.log'
    log_data = log_path.read_bytes()
    command = next(x for x in report['commands'] if x['name'] == 'qemu')
    need(command['state'] in ('complete', 'forced_stop_nonpass') and 'exit_status' in command, 'authoritatively terminal original QEMU receipt')
    need(command['stdout_sha256'] == hashlib.sha256(log_data).hexdigest(), 'complete unchanged original UART receipt')
    text = log_data.decode('utf-8', errors='strict').replace('\r\n', '\n')
    lines = text.splitlines(); terminal = [i for i, line in enumerate(lines) if line.startswith('CYD_F1_REFERENCE_COMPLETE ')]
    need(len(terminal) == 1, 'one completed independent reference phase')
    prefix = lines[:terminal[0] + 1]
    need(not re.search(r'FAILURE|Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered', '\n'.join(prefix), re.I), 'reference subphase itself has no runtime failure')
    need(not any(x.startswith('CYD_F1_TASK_PROFILE ') for x in prefix), 'public reference phase precedes production tasks')
    rows = [fields(x) for x in prefix if x.startswith('CYD_F1_REFERENCE_')]
    complete = [r for t, r in rows if t == 'CYD_F1_REFERENCE_COMPLETE']
    need(complete == [dict(cases=13, live=0, private_helpers=0, production_tasks=0, heap_integrity=1)], 'complete independent reference census')
    cases = [r for t, r in rows if t == 'CYD_F1_REFERENCE_CASE']
    need([r['index'] for r in cases] == list(range(13)), 'all reference summaries in original order')
    pcm = bytearray()
    for tag, row in rows:
        if tag == 'CYD_F1_REFERENCE_PCM' and row['index'] == 12:
            need(isinstance(row['hex'], str) and re.fullmatch('(?:[0-9a-f]{2})+', row['hex']), 'exact local PCM byte text')
            body = bytes.fromhex(row['hex'])
            need(row['offset'] == len(pcm) and row['bytes'] == len(body) <= 256, 'complete ordered C8 byte coverage')
            pcm.extend(body)
    case = cases[12]
    need(case['complete'] == 1 and case['driver'] == case['live'] == case['private_helpers'] == 0 and
         case['channels'] == 8 and case['frames'] == 9600 and case['pcm_bytes'] == len(pcm) == 153600 and
         case['sha256'] == hashlib.sha256(pcm).hexdigest() and case['opens'] == case['closes'] == 5 and
         case['core'] == 1 and case['priority'] == 3 and 0 < case['stack_free'] <= 16384, 'whole F12 independent public reference geometry')
    opens = [r for t, r in rows if t == 'CYD_F1_REFERENCE_OPEN' and r['index'] == 12]
    closes = [r for t, r in rows if t == 'CYD_F1_REFERENCE_CLOSE' and r['index'] == 12]
    calls = [r for t, r in rows if t == 'CYD_F1_REFERENCE_CALL' and r['index'] == 12]
    need(len(opens) == len(closes) == 5 and all(r['result'] == 0 and r['handle'] == 1 for r in opens) and
         all(r['result'] == 0 for r in closes) and closes[-1]['live'] == 0, 'every F12 public open/close')
    need(len(calls) == case['calls'] and [r['call'] for r in calls] == list(range(1, len(calls) + 1)) and
         all(0 <= r['consumed'] <= r['input'] and 0 <= r['decoded'] <= r['capacity'] and r['result'] in (0, -8) for r in calls), 'all real F12 public decode calls')
    # Recorded compiler closure, not an execution of any archived script.
    closure = json.loads((capture / 'actual-compiler-closure.json').read_bytes())
    bundle_data = (capture / 'execution-bundle.json').read_bytes()
    bundle = json.loads(bundle_data)
    manifest = json.loads((capture / 'source-manifest.json').read_bytes())
    for name in ('actual-compiler-closure.json', 'source-manifest.json'):
        need(bundle['artifacts'].get(name) == hashlib.sha256((capture / name).read_bytes()).hexdigest(), 'frozen execution-bundle metadata binding')
    need(bundle['sources'] == manifest, 'original complete frozen source inventory')
    entry = next(r for r in report['pcm_reference']['entries'] if r['id'] == 12)
    need(entry['channels'] == 8 and entry['pre_skip'] == 312 and entry['logical_frames'] == 9600 and
         entry['original_source_sha256'] == 'c6a06d1bf954c9119f844167d43b3f080bdbe4e7c2a305318109e524cf3b6757', 'exact creator F12 source identity')
    forbidden = {'opus_family1_playback.h', 'opus_family1_decoder.h', 'opus_family1_mapping.h', 'opus_multistream_framing.h', 'opus_pcm_trim.h', 'ogg_page_input.h', 'pcm_speaker_mix.h'}
    units = [r for r in closure['translation_units'] if Path(r['file']).name in ('direct_reference.c', 'reference_control.c')]
    need(len(units) == 2 and all(not forbidden & {Path(x).name for x in r['actual_dependency_paths']} for r in units), 'actual reference TUs exclude production mapping/trim/mix helpers')
    for unit in units:
        for dependency in unit['actual_dependency_paths']:
            row = closure['dependencies'][dependency]
            source = manifest[row['manifest_original']]
            body = (capture / source['snapshot']).read_bytes()
            need(hashlib.sha256(body).hexdigest() == row['sha256'] == source['sha256'] and len(body) == source['bytes'], 'complete retained reference compiler dependency identity')
    return bytes(pcm), dict(original_capture=capture.name, whole_capture_passed=report['passed'], whole_capture_completed=report['completed'],
        whole_capture_status_is_not_relabelled=True, original_report_sha256=hashlib.sha256(report_data).hexdigest(),
        original_uart_sha256=hashlib.sha256(log_data).hexdigest(), reference_prefix_lines=len(prefix),
        reference_only_passed=True, native_gate_passed=False, source_pcm_sha256=case['sha256'],
        execution_bundle_sha256=hashlib.sha256(bundle_data).hexdigest(),
        sdk_commit=bundle['sdk_commit'], vendor_commit=bundle['vendor_commit'],
        vendor_archives={Path(p).name: r['sha256'] for p, r in manifest.items() if Path(p).name in ('libesp_audio_codec.a', 'libesp_audio_simple_dec.a')},
        compiler_closure_sha256=hashlib.sha256((capture / 'actual-compiler-closure.json').read_bytes()).hexdigest())


def validate_gate(log, expected):
    """Strict finite native gate checks; synthetic tests cannot establish target execution."""
    need(isinstance(expected, dict), 'expected golden metadata object')
    plans = expected.get('cases')
    need(isinstance(plans, list) and len(plans) == 2 and
         all(isinstance(p, dict) for p in plans) and [p.get('case') for p in plans] == [1, 2], 'exactly two ordered golden case IDs before comparison')
    need(expected.get('profile') == dict(enabled=True, gain_db=20, target_dbfs=-20, time_ms=100,
         rate=48000, channels=8, volume=127, balance=0, header_gain_q8=1536), 'fixed independently prepared golden profile')
    need(expected.get('decimal_precisions') == [100, 160] and expected.get('new_tolerance') is False, 'exact golden precision policy')
    def pcm_geometry(pin, size, frames=None):
        return (isinstance(pin, dict) and pin.get('bytes') == size and
                (frames is None or pin.get('frames') == frames) and
                isinstance(pin.get('sha256'), str) and re.fullmatch('[0-9a-f]{64}', pin['sha256']))
    need(pcm_geometry(expected.get('source_pcm'), 153600), 'complete independent C8 source golden geometry')
    for index, plan in enumerate(plans):
        need(plan.get('reset_frames') == ([5448] if index == 0 else []) and
             pcm_geometry(plan.get('normalized'), 153600) and pcm_geometry(plan.get('final_pcm'), 19200, 9600), 'complete fixed per-case golden/reset geometry')
    need(not re.search(r'FAILURE|Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered', log, re.I), 'no actual runtime failure')
    lines = log.replace('\r\n', '\n').splitlines()
    need(not any('CYD_NORM_' in line and not line.startswith('CYD_NORM_') for line in lines), 'all normalizer observations intact at column zero')
    rows = [fields(x) for x in lines if x.startswith('CYD_NORM_')]
    known = {'CYD_NORM_BOOT', 'CYD_NORM_BEGIN', 'CYD_NORM_CONFIG', 'CYD_NORM_RESET', 'CYD_NORM_REQUEST', 'CYD_NORM_CASE', 'CYD_NORM_COMPLETE'}
    need(rows and all(t in known for t, r in rows), 'only complete declared normalizer observations')
    need([t for t, r in rows] == ['CYD_NORM_BOOT', 'CYD_NORM_BEGIN', 'CYD_NORM_CONFIG', 'CYD_NORM_RESET',
         'CYD_NORM_REQUEST', 'CYD_NORM_RESET', 'CYD_NORM_RESET', 'CYD_NORM_CASE', 'CYD_NORM_BEGIN',
         'CYD_NORM_RESET', 'CYD_NORM_RESET', 'CYD_NORM_CASE', 'CYD_NORM_COMPLETE'], 'strict request-before-reset and complete case ordering')
    def select(t): return [r for tag, r in rows if tag == t]
    need(select('CYD_NORM_BOOT') == [dict(cases=2, enabled=1, hardware=0, release='UNRELEASED')], 'truthful prepared gate scope')
    need(select('CYD_NORM_BEGIN') == [dict(case=i, enabled=1, gain_db=20, target_dbfs=-20, time_ms=100, rate=48000, channels=8, volume=127, balance=0, schedule=i, page_style=i - 1) for i in (1, 2)], 'fixed case settings and original transport plans')
    need(select('CYD_NORM_CONFIG') == [dict(case=1, enabled=1, gain_db=20, target_dbfs=-20, time_ms=100, rate=48000, frames=0, core=1, priority=6)], 'one real cached output-owner configuration')
    need(select('CYD_NORM_REQUEST') == [dict(case=1, frames=5448, requests=2, immediate_resets=0, config_unchanged=1, geometry_unchanged=1)], 'deferred requests after established enabled format')
    resets = select('CYD_NORM_RESET')
    need(resets == [dict(case=1, frames=0, phase=2, core=1, priority=6), dict(case=1, frames=5448, phase=2, core=1, priority=6), dict(case=1, frames=9600, phase=3, core=1, priority=6), dict(case=2, frames=0, phase=2, core=1, priority=6), dict(case=2, frames=9600, phase=3, core=1, priority=6)], 'initial format/request/EOF resets in exact phase order')
    cases = select('CYD_NORM_CASE')
    need([r['case'] for r in cases] == [1, 2], 'two original completed enabled cases')
    for row, plan in zip(cases, plans):
        need(row['frames'] == 9600 and row['mono_bytes'] == 19200 and row['wire_bytes'] == 19456 and row['padding_bytes'] == 256 and row['sha256'] == plan['final_pcm']['sha256'] and row['normalizer_frames'] == 9600 and row['wrong_api_calls'] == 0, 'full expected normalized/rendered PCM and padding')
    need(select('CYD_NORM_COMPLETE') == [dict(cases=2, opens=10, closes=10, http_cleanup=2, flushes=2, heap_integrity=1, hardware=0)], 'complete exact public lifecycle census')
    need(rows[-1][0] == 'CYD_NORM_COMPLETE', 'terminal census last')
    return dict(passed=True, cases=2, enabled=True, hardware=False, exact_final_pcm=True)
