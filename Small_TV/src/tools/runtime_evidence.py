"""Validate native runtime evidence without trusting its final success flag."""
from collections import deque
import hashlib
import json
import math
from pathlib import Path
import re

from runtime_run_guard import inspect_uart


def require(condition, message):
    """Keep evidence rejection active under python -O."""
    if not condition:
        raise ValueError(message)


def integer(value, label, minimum=0):
    """Reject booleans masquerading as numeric counters."""
    require(type(value) is int and value >= minimum, 'Invalid counter: ' + label)
    return value


def finite(value, label):
    """Allow only finite nonnegative measured times."""
    require(type(value) in (int, float) and math.isfinite(value) and value >= 0, 'Invalid time: ' + label)
    return value


def unique_object(pairs):
    """Do not silently replace repeated JSON evidence fields."""
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key: ' + key)
        result[key] = value
    return result


def decode(data):
    """Read JSON data only; reject nonstandard NaN/Infinity constants."""
    def constant(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(data, object_pairs_hook=unique_object, parse_constant=constant)


def sha(path):
    """Hash large executable/media inputs without loading them all into RAM."""
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def checked_path(path, roots):
    """Evidence may reference only explicitly allowed source directories."""
    resolved = Path(path).resolve()
    require(any(resolved.is_relative_to(root.resolve()) for root in roots), 'Input outside allowed source roots')
    require(resolved.is_file(), 'Missing evidence input: ' + resolved.name)
    return resolved


def validate_snapshot(row):
    """Check heap arithmetic and task headroom against the recorded scalar ABI."""
    finite(row['guest_seconds'], 'snapshot')
    require(type(row['label']) is str, 'Missing snapshot label')
    heap = row['heap']
    require(heap['caps'] == 4, 'Expected MALLOC_CAP_8BIT counters')
    free = integer(heap['free_bytes'], 'free heap', 1)
    minimum = integer(heap['minimum_free_bytes'], 'SDK minimum', 1)
    require(minimum <= free and len(heap['heaps']) > 0, 'Invalid aggregate heap counters')
    for part in heap['heaps']:
        integer(part['caps'], 'heap capabilities')
        require(part['caps'] & 4, 'Selected heap lacks the requested capability')
        require(0 <= integer(part['minimum_free_bytes'], 'heap minimum') <=
                integer(part['free_bytes'], 'heap free') <= integer(part['pool_size'], 'heap pool', 1),
                'Invalid per-heap counters')
    require(sum(part['free_bytes'] for part in heap['heaps']) == free and
            sum(part['minimum_free_bytes'] for part in heap['heaps']) == minimum, 'Heap totals do not match their parts')
    names = set()
    require(len(row['tasks']) > 0, 'Missing task stack observations')
    for task in row['tasks']:
        name = task['name']
        require(type(name) is str and name and name not in names, 'Missing or ambiguous task name')
        names.add(name)
        require(integer(task['stack_high_water_free_bytes'], 'stack fill', 1) <=
                integer(task['recorded_stack_span_bytes'], 'stack span', 1), 'Stack headroom exceeds its observed span')


def journal_evidence(path, chunks, outage_every, allow_partial=False, require_weather=False):
    """Stream complete events, recompute aggregates, and retain a lean time series."""
    summary = {'events': 0, 'snapshots': 0, 'http_requests': 0, 'outages': 0,
               'minimum_sampled_free_heap_bytes': None, 'minimum_sdk_sum_of_per_heap_minima_bytes': None,
               'minimum_task_stack_fill_bytes_by_name': {}, 'maximum_http_or_batch_guest_seconds': 0,
               'first_snapshot': None, 'snapshot_tail': []}
    tail, series, pending = deque(maxlen=32), [], []
    digest, rom_calls, cycle, partial = hashlib.sha256(), 0, 0, 0
    heap_shape, last_minimum, last_time, recovery = None, None, None, None
    weather = {'snapshots': 0, 'quiescent_samples': 0, 'valid_samples': 0, 'distinct_valid_generations': 0,
               'first_fresh_guest_seconds': None, 'last_fresh_guest_seconds': None,
               'maximum_fresh_gap_guest_seconds': 0}
    generations, last_generation = set(), None
    with path.open('rb') as stream:
        for number, line in enumerate(stream, 1):
            require(len(line) <= 262144, 'Oversized runtime event')
            digest.update(line)
            if not line.endswith(b'\n'):
                require(allow_partial, 'Truncated runtime journal')
                partial = len(line)
                break
            event = decode(line)
            require(set(event) == {'kind', 'data'}, 'Malformed runtime event envelope')
            row, kind = event['data'], event['kind']
            summary['events'] += 1
            if kind == 'snapshot':
                validate_snapshot(row)
                when = row['guest_seconds']
                require(not require_weather or 'weather' in row, 'Missing weather observation')
                if 'weather' in row:
                    observed = row['weather']
                    state = integer(observed['worker_state'], 'weather state')
                    require(state <= 3, 'Invalid weather worker state')
                    weather['snapshots'] += 1
                    if state:
                        require(set(observed) == {'worker_state'}, 'Cache read while weather worker was active')
                    else:
                        weather['quiescent_samples'] += 1
                        require(type(observed['valid']) is bool, 'Invalid weather valid flag')
                        generation = integer(observed['generation'], 'weather generation')
                        require(generation <= 0xffffffff and (last_generation is None or generation >= last_generation),
                                'Weather generation regressed or exceeded RV32')
                        last_generation = generation
                        keys = {'worker_state', 'valid', 'generation'}
                        if observed['valid']:
                            require(type(observed['humidity']) is int and observed['humidity'] == 67 and generation > 0,
                                    'Synthetic weather was not parsed correctly')
                            keys.add('humidity')
                            weather['valid_samples'] += 1
                            if generation not in generations:
                                generations.add(generation)
                                if weather['first_fresh_guest_seconds'] is None:
                                    weather['first_fresh_guest_seconds'] = when
                                if weather['last_fresh_guest_seconds'] is not None:
                                    weather['maximum_fresh_gap_guest_seconds'] = max(
                                        weather['maximum_fresh_gap_guest_seconds'], when - weather['last_fresh_guest_seconds'])
                                weather['last_fresh_guest_seconds'] = when
                        require(set(observed) == keys, 'Unexpected weather observation fields')
                require(last_time is None or when > last_time, 'Snapshot clock is not increasing')
                require(recovery is None or when >= recovery, 'Snapshot precedes outage recovery')
                if last_time is None:
                    require(row['label'] == 'ready' and not pending, 'Missing initial ready snapshot')
                    summary['first_snapshot'] = row
                else:
                    require(row['label'] == 'cycle-' + str(cycle), 'Missing or repeated workload cycle')
                    expected = ['/setclocktype', '/setgifvalue', '/updateCity',
                                ('/getsettings', '/get_checkbox_state')]
                    if cycle % 4 == 2:
                        expected += ['/start_upload'] + ['/upload_chunk'] * chunks + ['/finish_upload']
                    if outage_every and (cycle + 1) % outage_every == 0:
                        expected += ['outage']
                    require(pending == expected, 'Incomplete cycle HTTP/upload/outage sequence')
                    cycle += 1
                    pending = []
                heap = row['heap']
                shape = [(part['caps'], part['pool_size']) for part in heap['heaps']]
                require(heap_shape is None or shape == heap_shape, 'Heap topology changed; review required')
                require(last_minimum is None or heap['minimum_free_bytes'] <= last_minimum,
                        'SDK cumulative minimum increased; possible reset or invalid observation')
                heap_shape, last_minimum, last_time = shape, heap['minimum_free_bytes'], when
                rom_calls += 2 * len(heap['heaps'])
                summary['snapshots'] += 1
                for field, value in (('minimum_sampled_free_heap_bytes', heap['free_bytes']),
                                     ('minimum_sdk_sum_of_per_heap_minima_bytes', heap['minimum_free_bytes'])):
                    summary[field] = value if summary[field] is None else min(summary[field], value)
                for task in row['tasks']:
                    minima = summary['minimum_task_stack_fill_bytes_by_name']
                    minima[task['name']] = min(minima.get(task['name'], task['stack_high_water_free_bytes']),
                                             task['stack_high_water_free_bytes'])
                tail.append(row)
                series.append({'guest_seconds': when, 'cycle': cycle - 1,
                               'free_bytes': heap['free_bytes'], 'sdk_minimum_bytes': heap['minimum_free_bytes']})
            elif kind == 'http':
                require(last_time is not None, 'HTTP before the initial snapshot')
                elapsed = finite(row['guest_seconds'], 'HTTP duration')
                require(elapsed <= 6, 'HTTP exceeded the existing six-second bound')
                if 'paths' in row:
                    require(row['paths'] == ['/getsettings', '/get_checkbox_state'] and
                            integer(row['request_count'], 'batch requests', 1) == 2, 'Invalid concurrent batch')
                    pending.append(tuple(row['paths']))
                    count = 2
                else:
                    require(type(row['status']) is int and row['status'] == 200 and type(row['path']) is str,
                            'Failed HTTP request')
                    pending.append(row['path'])
                    count = 1
                summary['http_requests'] += count
                summary['maximum_http_or_batch_guest_seconds'] = max(summary['maximum_http_or_batch_guest_seconds'], elapsed)
            elif kind == 'outage':
                start = finite(row['offline_started_guest_seconds'], 'outage start')
                end = finite(row['recovered_guest_seconds'], 'outage recovery')
                duration = finite(row['requested_offline_guest_seconds'], 'outage duration')
                require(last_time is not None and start >= last_time and end >= start + duration and 0 < duration <= 5,
                        'Invalid measured outage interval')
                require(row['ap_online_after'] is True and row['guest_disconnected'] is True and
                        row['guest_reconnected'] is True, 'No real guest disconnect/reconnect')
                summary['outages'] += 1
                recovery = end
                pending.append('outage')
            else:
                raise ValueError('Unknown runtime event kind')
    require(summary['snapshots'] > 0, 'No complete snapshots')
    require(allow_partial or not pending, 'Unfinished workload cycle')
    summary['snapshot_tail'] = list(tail)
    weather['distinct_valid_generations'] = len(generations)
    return {'summary': summary, 'series': series, 'cycles': cycle, 'rom_calls': rom_calls,
            'sha256': digest.hexdigest(), 'trailing_partial_bytes': partial, 'pending_events': len(pending), 'weather': weather}


def audit_run(folder, repository_root, start_record=None, allow_progress=False, extra_roots=()):
    """Bind final journal, UART guard, source files, image/ELF and elapsed guest time."""
    folder, repository_root = Path(folder).resolve(), Path(repository_root).resolve()
    report = decode((folder / 'report.json').read_bytes())
    require(report['schema_version'] in (3, 4, 5), 'Unsupported runtime report schema')
    terminal = 'journal' in report and 'inputs_unchanged' in report
    require(terminal or allow_progress, 'Runtime workload has not finished')
    roots = (repository_root, *map(Path, extra_roots))
    inputs = report['inputs_sha256']
    require(type(inputs) is dict and len(inputs) > 0, 'Missing runtime source identities')
    paths = {}
    for filename, expected in inputs.items():
        require(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected), 'Invalid source digest')
        path = checked_path(filename, roots)
        require(sha(path) == expected, 'Changed runtime input: ' + path.name)
        paths[filename] = path
    def named(name):
        matches = [path for path in paths.values() if path.name == name]
        require(len(matches) == 1, 'Missing or ambiguous runtime input: ' + name)
        return matches[0]
    app, elf = named('app.bin'), named('small_tv_reconstructed.elf')
    require(sha(app) == report['app_sha256'] and sha(elf) == report['native_elf_sha256'] and
            app.read_bytes()[176:208] == bytes.fromhex(report['native_elf_sha256']), 'Application/ELF binding differs')
    # FIXED_TEST: bind the explicit candidate to the pinned inputs, not a basename.
    if report['schema_version'] >= 5:
        executable = checked_path(report['qemu_executable'], roots)
        require(executable in paths.values(), 'Emulator executable is not a pinned input')
    else:
        executable = named('qemu-system-riscv32.exe')
    require(sha(executable) == report['qemu_sha256'], 'Emulator identity differs')
    chunks = (named('rgb-420.jpg').stat().st_size + 4095) // 4096
    every = integer(report['outage_every_cycles'], 'outage cadence')
    weather_required = report['schema_version'] >= 4
    evidence = journal_evidence(folder / 'events.jsonl', chunks, every, allow_partial=not terminal,
                                require_weather=weather_required)
    result = {'terminal': terminal, 'inputs_verified': len(inputs), 'evidence': evidence, 'report': report,
              'uart': inspect_uart((folder / 'vm/uart.log').read_bytes()), 'weather_evidence_verified': False}
    require(result['uart']['passed'], 'UART contains a reset, panic or incomplete boot capture')
    if terminal:
        require(report['passed'] is True and report['inputs_unchanged'] is True and report['no_panic'] is True and
                not report.get('error') and not report.get('cleanup_error'), 'Workload did not finish successfully')
        require(report['journal']['file'] == 'events.jsonl' and report['journal']['sha256'] == evidence['sha256'],
                'Journal digest differs')
        require(report['summary'] == evidence['summary'], 'Reported aggregates differ from the complete journal')
        require(report['completed_cycles'] == evidence['cycles'], 'Completed cycle count differs')
        require(report['rom_counter_crosscheck']['checks'] == evidence['rom_calls'] and
                sha(named('esp32c2_rev200_rom.elf')) == report['rom_counter_crosscheck']['rom_elf_sha256'],
                'ROM heap counter crosscheck is incomplete')
        start, end = (finite(report[key], key) for key in ('workload_start_guest_seconds', 'workload_end_guest_seconds'))
        elapsed = finite(report['elapsed_guest_seconds'], 'elapsed duration')
        require(end >= start and abs((end - start) - elapsed) < 1e-6, 'Guest duration arithmetic differs')
        series = evidence['series']
        require(start <= series[0]['guest_seconds'] <= start + 1 and
                end - 1 <= series[-1]['guest_seconds'] <= end, 'Snapshots do not cover the measured workload')
        wraps = round(end * 1e6) // 2**32 - round(series[0]['guest_seconds'] * 1e6) // 2**32
        require(report['radio_clock_wraps'] == wraps, 'Radio clock wrap count differs')
        requested = report['duration_requested_guest_seconds']
        if requested is not None:
            require(elapsed >= integer(requested, 'requested duration', 1), 'Requested duration was not reached')
        require(evidence['summary']['outages'] == (evidence['cycles'] // every if every else 0), 'Outage count differs')
        if weather_required:
            named('runtime_weather.py')
            require(report['weather_layout']['elf_sha256'] == report['native_elf_sha256'], 'Weather layout ELF differs')
            require(report['weather_coverage_passed'] is True and report['weather_observation'] == evidence['weather'] and
                    evidence['weather']['valid_samples'] > 0, 'Weather observation aggregates differ or no parsed weather')
            fixture = report['weather_fixture']
            require(1 <= integer(fixture['responses_ok'], 'weather responses', 1) <=
                    integer(fixture['requests'], 'weather requests', 1) and
                    fixture['all_synthetic_locations'] is True and fixture['all_synthetic_keys'] is True,
                    'Missing successful synthetic weather exchange')
            result['weather_evidence_verified'] = True
    # Earlier short preflights have a complete UART capture but predate the
    # independent running guard. Audit them without promoting them to H10.
    guard_path = folder / 'uptime-guard.json'
    result['terminal_guard_verified'] = False
    if guard_path.exists():
        guard = decode(guard_path.read_bytes())
        session = decode((folder / 'vm/session.json').read_bytes())
        require(guard['vm_name'] == session['name'], 'Uptime guard watches a different VM')
        require(guard['status'] != 'failed' and guard['last_observation']['passed'] is True,
                'Independent uptime guard failed')
        if terminal:
            require(guard['status'] == 'complete' and guard['passed'] is True and guard['workload_passed'] is True and
                    guard['last_observation'] == result['uart'], 'Missing matching terminal uptime guard')
            result['terminal_guard_verified'] = True
        result['guard'] = guard
    if start_record:
        record = decode(Path(start_record).read_bytes())
        require(all(record[key] == report[key] for key in ('app_sha256', 'native_elf_sha256', 'qemu_sha256')) and
                record['inputs_sha256'] == inputs, 'Run differs from the captured start identities')
        if 'duration_requested_guest_seconds' in record:
            require(record['duration_requested_guest_seconds'] == report['duration_requested_guest_seconds'],
                    'Requested duration differs from the captured start')
        metadata = record['guard']
        source = checked_path(repository_root / metadata['source_file'], roots)
        require(sha(source) == metadata['source_sha256'], 'Uptime guard source changed')
    result['start_record_verified'] = start_record is not None
    return result
