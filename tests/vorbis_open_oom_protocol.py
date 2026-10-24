"""Finite checked raw-open allocation protocol; no private decoder inspection.

Baseline PCM hashes come from captured bytes. Recovery equality is a target
assertion witnessed by the complete recovery marker, not separately logged PCM.
Neither this parser nor allocation fault injection establishes physical margins.
"""
import hashlib
import re

MAX_CALLS = 256
MAX_REQUEST = 0xffffffff - 47


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def validate_log(log, matrix, target, control=None, *, returncode, timed_out, interrupted):
    need(type(returncode) is int and returncode == 0 and timed_out is False and interrupted is False,
         'actual terminal process facts required')
    need(target in ('esp32', 'esp32c3') and control in (None, 'oom-legacy', 'oom-global'), 'target/control')
    core, machine = (1, 94) if target == 'esp32' else (0, 243)
    cases = matrix['cases']
    need(len(cases) == 14 and len({c['id'] for c in cases}) == 14 and
         all(type(c['expected_valid']) is bool for c in cases) and
         [c['expected_valid'] for c in cases] == [True] * 8 + [False] * 6, 'fourteen-case matrix')
    for c in cases:
        sizes, offsets = c['expected_packet_bytes'], c['offsets']
        need(re.fullmatch(r'\S+', c['id']) and len(sizes) == 14 and type(sizes[0]) is int and sizes[0] == 0 and
             all(type(n) is int and 1 < n <= 4096 and n % 4 == 0 for n in sizes[1:]) and sum(sizes) == 28160 and
             len(offsets) == 15 and all(type(n) is int for n in offsets) and offsets[0] == 0 and
             all(a < b for a, b in zip(offsets, offsets[1:])), 'packet geometry')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP', log), 'panic')
    lines = [line for line in log.replace('\r\n', '\n').splitlines()
             if line.startswith(('FLOOR1_', 'VORBIS_REGISTRY_', 'VORBIS_OPEN_OOM_'))]
    at = 0

    def take(expected):
        nonlocal at
        need(at < len(lines) and lines[at] == expected, f'event {at}: expected {expected}')
        at += 1

    def match(pattern):
        nonlocal at
        found = re.fullmatch(pattern, lines[at]) if at < len(lines) else None
        need(found is not None, f'event {at}: malformed event')
        at += 1
        return found.groups()

    stats_pattern = r'result=(-?\d+) handle=(\d+) calls=(\d+) injected=(\d+) live=(\d+) guards=(\d+)'

    def stats(pattern):
        values = tuple(map(int, match(pattern)))
        result, handle, calls, injected, live, guards = values
        need(1 <= calls <= MAX_CALLS and 0 <= injected <= calls and handle in (0, 1) and
             live == 0 and guards == 1, 'actual allocation counts, ownership and guards')
        return dict(zip(('result', 'handle', 'calls', 'injected', 'live', 'guards'), values))

    hashes, requests, malformed, faults, nested, tasks = {}, {}, {}, [], [], []
    counts = dict(baseline_packets=0, baseline_pcm_bytes=0, baseline_metadata=0, baseline_retries=0,
                  discoveries=0, faults=0, recoveries=0, recovery_packets=0, recovery_pcm_bytes=0)

    def finish(failure=None, failure_case=None):
        if failure:
            take(f'FLOOR1_FAILURE case={failure_case} reason={failure}')
            take(f'VORBIS_REGISTRY_CLEANUP case={failure_case} closed=0 empty=1 unsupported=1 core={core}')
        take('FLOOR1_CONTROLLED_STOP')
        need(at == len(lines), 'unknown, duplicated or extra protocol events')
        return dict(counts, baseline_pcm_sha256=hashes, allocation_request_bytes=requests,
            malformed_open=malformed, fault_records=faults, nested_pairs=nested, task_scenarios=tasks,
            observed_allocation_positions=sum(map(len, requests.values())),
            recovery_target_byte_exact=counts['recoveries'] > 0,
            recovery_pcm_is_separately_captured=False,
            target_capture_completed=not control, raw_open_oom_qualified=not control,
            control_effective=bool(control), exact_failure=failure, core=core, machine=machine,
            independent_reference_compared=False, vendor_comparison_available=False,
            full_G1_qualified=False, full_G4_qualified=False, full_G6_qualified=False,
            radio_qualified=False, allocation_scope='checked raw open only')

    take(f'FLOOR1_START coordinator=0 decoder={core}')
    take(f'VORBIS_REGISTRY_BEGIN cases=14 packets=112 retries=312 core={core}')
    take(f'VORBIS_REGISTRY_INITIAL empty=1 unsupported=1 core={core}')
    take(f'VORBIS_OPEN_OOM_BEGIN target={target} machine={machine} core={core}')
    for case, c in enumerate(cases):
        key = str(case)
        take(f'VORBIS_REGISTRY_REGISTER case={case} result=0 ops=1 supported=1 core={core}')
        take(f'VORBIS_REGISTRY_BIND_OPEN case={case} match=1 core={core}')
        take(f'VORBIS_REGISTRY_BIND_DECODE case={case} match=1 core={core}')
        take(f'VORBIS_REGISTRY_BIND_OTHER case={case} reset=1 close=1 core={core}')
        if not c['expected_valid']:
            take(f'FLOOR1_OPEN case={case} result=-1 handle=0')
            take(f'FLOOR1_REJECT case={case} name={c["id"]} result=-1 handle=0 core={core}')
            calls, = map(int, match(rf'VORBIS_OPEN_OOM_MALFORMED case={case} calls=(\d+) injected=0 result=-1 handle=0 live=0 guards=1 core={core}'))
            need(4 <= calls <= MAX_CALLS, 'malformed open actual checked-header allocations')
            malformed[key] = dict(calls=calls, injected=0, result=-1, handle=0, live=0, guards=1)
            take(f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}')
            continue
        take(f'FLOOR1_OPEN case={case} result=0 handle=1')
        pcm = bytearray()
        for packet, size in enumerate(c['expected_packet_bytes']):
            if size:
                for attempt in range(3):
                    take(f'VORBIS_REGISTRY_RETRY case={case} packet={packet} attempt={attempt} result=-8 consumed=0 '
                         f'decoded=0 needed={size} untouched=1 canaries=1 core={core}')
                    counts['baseline_retries'] += 1
            values = tuple(map(int, match(rf'VORBIS_REGISTRY_META case={case} packet={packet} result=(-?\d+) sample_rate=(\d+) channel=(\d+) bits=(\d+) core={core}')))
            result, rate, channel, bits = values
            need(values == (0, 48000, 2, 16) or
                 (not size and result == -9 and 0 <= rate <= 0xffffffff and 0 <= channel <= 255 and 0 <= bits <= 255), 'public metadata')
            counts['baseline_metadata'] += 1
            consumed, actual, hexdump = match(rf'FLOOR1_PCM case={case} packet={packet} consumed=(\d+) bytes=(\d+) hex=([0-9a-f]*)')
            data = bytes.fromhex(hexdump)
            need(int(consumed) == c['offsets'][packet + 1] - c['offsets'][packet] and
                 int(actual) == len(data) == size, 'baseline complete consumption/PCM')
            pcm.extend(data)
            counts['baseline_packets'] += 1
            counts['baseline_pcm_bytes'] += size
        need(len(pcm) == 28160 and any(pcm), 'complete nonzero baseline PCM')
        hashes[key] = hashlib.sha256(pcm).hexdigest()
        take(f'VORBIS_REGISTRY_CLOSE case={case} called=1 core={core}')
        total, = map(int, match(rf'VORBIS_OPEN_OOM_DISCOVER case={case} calls=(\d+) live=0 guards=1 core={core}'))
        need(4 <= total <= MAX_CALLS, 'bounded complete allocation discovery')
        sizes = []
        for call in range(1, total + 1):
            size, = map(int, match(rf'VORBIS_OPEN_OOM_ALLOC case={case} call={call} bytes=(\d+)'))
            need(0 < size <= MAX_REQUEST, 'actual positive allocation request')
            sizes.append(size)
        requests[key] = sizes
        counts['discoveries'] += 1
        for mode in ('once', 'persistent'):
            for nth in range(1, total + 1):
                calls, injected, result, handle, live, guards = map(int, match(
                    rf'VORBIS_OPEN_OOM_FAULT case={case} mode={mode} nth={nth} calls=(\d+) injected=(\d+) '
                    rf'result=(-?\d+) handle=(\d+) live=(\d+) guards=(\d+) core={core}'))
                need(nth <= calls <= total and injected == (1 if mode == 'once' else calls - nth + 1) and
                     handle == 0 and live == 0 and guards == 1, 'actual nth/persistent failure and complete cleanup')
                need(nth > 4 or calls == nth, 'wrapper/info/setup/book-array failure returns immediately')
                record = dict(case=case, mode=mode, nth=nth, calls=calls, injected=injected,
                              result=result, handle=handle, live=live, guards=guards)
                faults.append(record)
                counts['faults'] += 1
                if control == 'oom-legacy' and case == 0 and mode == 'once' and nth == 4:
                    need(result == -1 and calls == 4 and counts['recoveries'] == 3,
                         'legacy control must expose the exact header-memory misclassification')
                    return finish('oom_memory_error', 0)
                need(result == -2, 'real allocation failure must report MEM_LACK')
                take(f'VORBIS_OPEN_OOM_RECOVER case={case} mode={mode} nth={nth} packets=14 pcm=28160 '
                     f'baseline_exact=1 live=0 guards=1 core={core}')
                counts['recoveries'] += 1
                counts['recovery_packets'] += 14
                counts['recovery_pcm_bytes'] += 28160
        take(f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}')
        take(f'FLOOR1_ACCEPT case={case} name={c["id"]} packets=14 pcm=28160 renderer_repair=1 core={core}')

    n0, m8 = len(requests['0']), malformed['8']['calls']
    expected_nested = [((-2, 0, 4, 1), (-1, 0, m8, 0)),
                       ((-1, 0, m8, 0), (-2, 0, 4, 1)),
                       ((0, 1, n0, 0), (-2, 0, 4, 1)),
                       ((-2, 0, 1, 1), (-1, 0, m8, 0))]
    for pair, (inner_expected, outer_expected) in enumerate(expected_nested):
        take(f'VORBIS_OPEN_OOM_NEST_ENTER pair={pair} outer_call=1 core={core}')
        inner = stats(rf'VORBIS_OPEN_OOM_NEST_INNER pair={pair} {stats_pattern} core={core}')
        need(tuple(inner[k] for k in ('result', 'handle', 'calls', 'injected')) == inner_expected, 'nested inner scope classification')
        outer = stats(rf'VORBIS_OPEN_OOM_NEST_OUTER pair={pair} {stats_pattern} nested=1 core={core}')
        need(tuple(outer[k] for k in ('result', 'handle', 'calls', 'injected')) == outer_expected, 'nested outer scope restoration/isolation')
        nested.append(dict(pair=pair, inner=inner, outer=outer))
    for scenario in range(2):
        take(f'VORBIS_OPEN_OOM_TASK_WAIT scenario={scenario} role=A call=1 core=0')
        take(f'VORBIS_OPEN_OOM_TASK_WAIT scenario={scenario} role=B call=1 core={core}')
        take(f'VORBIS_OPEN_OOM_TASK_RELEASE scenario={scenario} role=A')
        a = stats(rf'VORBIS_OPEN_OOM_TASK_RESULT scenario={scenario} role=A {stats_pattern} core=0')
        need(tuple(a[k] for k in ('result', 'handle', 'calls', 'injected')) == (-2, 0, 1, 1), 'task A first allocation failure')
        take(f'VORBIS_OPEN_OOM_TASK_RELEASE scenario={scenario} role=B')
        take(f'VORBIS_OPEN_OOM_TASK_FIRST scenario={scenario} role=B call=1 success=1 core={core}')
        b = stats(rf'VORBIS_OPEN_OOM_TASK_RESULT scenario={scenario} role=B {stats_pattern} core={core}')
        if control == 'oom-global' and scenario == 1:
            need(tuple(b[k] for k in ('result', 'handle', 'calls', 'injected')) == (-2, 0, m8, 0),
                 'global control must expose exact semantic-error cross-task contamination')
            tasks.append(dict(scenario=scenario, A=a, B=b, isolated=False))
            return finish('oom_task_error_isolation', 14)
        need(tuple(b[k] for k in ('result', 'handle', 'calls', 'injected')) ==
             ((-2, 0, 4, 1) if scenario == 0 else (-1, 0, m8, 0)), 'task B independent error classification')
        take(f'VORBIS_OPEN_OOM_TASK_DONE scenario={scenario} isolated=1')
        tasks.append(dict(scenario=scenario, A=a, B=b, isolated=True))
    positions = sum(map(len, requests.values()))
    take(f'VORBIS_OPEN_OOM_COMPLETE valid=8 malformed=6 discoveries=8 faults={2 * positions} recoveries={2 * positions} '
         f'recovery_packets={28 * positions} recovery_pcm={56320 * positions} nested=4 task_scenarios=2 live=0 guards=1 core={core}')
    take(f'VORBIS_REGISTRY_COMPLETE registrations=14 bindings=14 closes=8 unregistrations=14 metadata=112 retries=312 core={core}')
    take(f'FLOOR1_COMPLETE accepted=8 rejected=6 packets=112 pcm=225280 core={core}')
    need(counts == dict(baseline_packets=112, baseline_pcm_bytes=225280, baseline_metadata=112, baseline_retries=312,
         discoveries=8, faults=2 * positions, recoveries=2 * positions, recovery_packets=28 * positions,
         recovery_pcm_bytes=56320 * positions), 'complete counted finite matrix')
    return finish()
