"""Strict finite public raw reset transcript, including all registry events.

PCM is compared as bytes, including every high bit; only counts and hashes are
returned. Numerical/reference, full G1/G3/G6 and radio qualification are separate.
"""
import hashlib
import re


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def validate_log(log, matrix, target, control=None, *, returncode, timed_out, interrupted):
    need(type(returncode) is int and returncode == 0 and timed_out is False and interrupted is False,
         'actual terminal process facts required')
    need(target in ('esp32', 'esp32c3') and control in (None, 'reset-skip'), 'target/control')
    core = 1 if target == 'esp32' else 0
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
             if line.startswith(('FLOOR1_', 'VORBIS_REGISTRY_', 'VORBIS_RESET_'))]
    at = 0

    def take(expected):
        nonlocal at
        need(at < len(lines) and lines[at] == expected, f'event {at}: expected {expected}')
        at += 1

    def match(pattern):
        nonlocal at
        found = re.fullmatch(pattern, lines[at]) if at < len(lines) else None
        need(found is not None, f'event {at}: malformed PCM/metadata')
        at += 1
        return found.groups()

    def info(result, rate, channels, bits, empty):
        need((result, rate, channels, bits) == (0, 48000, 2, 16) or
             (empty and result == -9 and 0 <= rate <= 0xffffffff and 0 <= channels <= 255 and 0 <= bits <= 255),
             'public metadata')

    baseline_hashes, replay_hashes, prefix_hashes, case_counts = {}, {}, {}, {}
    counts = dict(baseline_packets=0, baseline_pcm_bytes=0, baseline_retries=0, baseline_metadata=0,
                  reset_calls=0, reset_call_events=0, skipped_calls=0, replay_packets=0,
                  prefix_packets=0, reset_retries=0, replay_pcm_bytes=0, prefix_pcm_bytes=0,
                  reset_metadata=0, rounds_completed=0, reset_cases_completed=0)
    probe = None

    def call(case, round_id, purpose, attempt=0, skip=False):
        take(f'VORBIS_RESET_CALL case={case} round={round_id} purpose={purpose} attempt={attempt} '
             f'called={0 if skip else 1} result={"SKIPPED" if skip else "0"} core={core}')
        counts['reset_call_events'] += 1
        counts['skipped_calls' if skip else 'reset_calls'] += 1

    def reset_packet(case, c, round_id, phase, packet, baseline, failing_primer=False):
        consumed, size, result, rate, channels, bits, hexdump = match(
            rf'VORBIS_RESET_PCM case={case} round={round_id} phase={phase} packet={packet} '
            r'consumed=(\d+) bytes=(\d+) info_result=(-?\d+) sample_rate=(\d+) channel=(\d+) bits=(\d+) hex=([0-9a-f]*)')
        consumed, size, result, rate, channels, bits = map(int, (consumed, size, result, rate, channels, bits))
        data = bytes.fromhex(hexdump)
        need(consumed == c['offsets'][packet + 1] - c['offsets'][packet] and size == len(data) and
             size <= 4096 and size % 2 == 0, 'reset packet consumption/output bound')
        info(result, rate, channels, bits, size == 0)
        counts['reset_metadata'] += 1
        if failing_primer:
            need(packet == 0 and size > 0, 'reset-skip must expose actual nonempty primer')
            return dict(bytes=size, sha256=hashlib.sha256(data).hexdigest(), packet=0, consumed=consumed)
        need(data == baseline[packet], 'every reset packet equals its complete baseline slice')
        counts[phase + '_packets' if phase == 'prefix' else 'replay_packets'] += 1
        counts['prefix_pcm_bytes' if phase == 'prefix' else 'replay_pcm_bytes'] += size
        return data

    take(f'FLOOR1_START coordinator=0 decoder={core}')
    take(f'VORBIS_REGISTRY_BEGIN cases=14 packets=112 retries=312 core={core}')
    take(f'VORBIS_REGISTRY_INITIAL empty=1 unsupported=1 core={core}')
    for case, c in enumerate(cases):
        key = str(case)
        take(f'VORBIS_REGISTRY_REGISTER case={case} result=0 ops=1 supported=1 core={core}')
        take(f'VORBIS_REGISTRY_BIND_OPEN case={case} match=1 core={core}')
        take(f'VORBIS_REGISTRY_BIND_DECODE case={case} match=1 core={core}')
        take(f'VORBIS_REGISTRY_BIND_OTHER case={case} reset=1 close=1 core={core}')
        if not c['expected_valid']:
            take(f'FLOOR1_OPEN case={case} result=-1 handle=0')
            take(f'FLOOR1_REJECT case={case} name={c["id"]} result=-1 handle=0 core={core}')
            take(f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}')
            continue
        take(f'FLOOR1_OPEN case={case} result=0 handle=1')
        call(case, 'initial', 'initial')
        baseline = []
        for packet, size in enumerate(c['expected_packet_bytes']):
            if size:
                for attempt in range(3):
                    take(f'VORBIS_REGISTRY_RETRY case={case} packet={packet} attempt={attempt} result=-8 consumed=0 '
                         f'decoded=0 needed={size} untouched=1 canaries=1 core={core}')
                    counts['baseline_retries'] += 1
            fields = match(rf'VORBIS_REGISTRY_META case={case} packet={packet} result=(-?\d+) sample_rate=(\d+) channel=(\d+) bits=(\d+) core={core}')
            info(*map(int, fields), size == 0)
            counts['baseline_metadata'] += 1
            consumed, actual, hexdump = match(rf'FLOOR1_PCM case={case} packet={packet} consumed=(\d+) bytes=(\d+) hex=([0-9a-f]*)')
            data = bytes.fromhex(hexdump)
            need(int(consumed) == c['offsets'][packet + 1] - c['offsets'][packet] and
                 int(actual) == len(data) == size, 'baseline complete consumption/PCM')
            baseline.append(data)
            counts['baseline_packets'] += 1
            counts['baseline_pcm_bytes'] += size
        base_pcm = b''.join(baseline)
        need(len(base_pcm) == 28160 and any(base_pcm), 'complete nonzero baseline')
        baseline_hashes[key] = hashlib.sha256(base_pcm).hexdigest()
        replay_hashes[key], prefix_hashes[key] = {}, {}
        take(f'VORBIS_RESET_BEGIN case={case} rounds=4 core={core}')
        for round_id in range(4):
            if round_id in (1, 2):
                call(case, round_id, 'prepare')
                limit = 7 if round_id == 1 else 5
                prefix = b''.join(reset_packet(case, c, round_id, 'prefix', p, baseline) for p in range(limit))
                prefix_hashes[key][str(round_id)] = hashlib.sha256(prefix).hexdigest()
                if round_id == 2:
                    for attempt in range(3):
                        take(f'VORBIS_RESET_RETRY case={case} round=2 packet=5 attempt={attempt} result=-8 '
                             f'consumed=0 decoded=0 needed={c["expected_packet_bytes"][5]} untouched=1 canaries=1 core={core}')
                        counts['reset_retries'] += 1
            skip = control == 'reset-skip' and case == 0 and round_id == 1
            for attempt in range(3 if round_id == 3 else 1):
                call(case, round_id, 'restart', attempt, skip)
            if skip:
                probe = reset_packet(case, c, round_id, 'full', 0, baseline, failing_primer=True)
                break
            replay = b''.join(reset_packet(case, c, round_id, 'full', p, baseline) for p in range(14))
            need(replay == base_pcm, 'full replay equals baseline')
            replay_hashes[key][str(round_id)] = hashlib.sha256(replay).hexdigest()
            take(f'VORBIS_RESET_ROUND case={case} round={round_id} packets=14 pcm=28160 baseline_exact=1 core={core}')
            counts['rounds_completed'] += 1
        if probe is not None:
            break
        prefix_bytes = sum(c['expected_packet_bytes'][:7]) + sum(c['expected_packet_bytes'][:5])
        take(f'VORBIS_RESET_DONE case={case} calls=9 replay_packets=56 prefix_packets=12 retries=3 '
             f'replay_pcm=112640 prefix_pcm={prefix_bytes} core={core}')
        case_counts[key] = dict(calls=9, replay_packets=56, prefix_packets=12, retries=3,
                                replay_pcm_bytes=112640, prefix_pcm_bytes=prefix_bytes)
        counts['reset_cases_completed'] += 1
        take(f'VORBIS_REGISTRY_CLOSE case={case} called=1 core={core}')
        take(f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}')
        take(f'FLOOR1_ACCEPT case={case} name={c["id"]} packets=14 pcm=28160 renderer_repair=1 core={core}')
    if control:
        need(probe is not None and counts['reset_calls'] == 3 and counts['skipped_calls'] == 1 and
             counts['rounds_completed'] == 1 and counts['baseline_packets'] == 14 and
             counts['replay_packets'] == 14 and counts['prefix_packets'] == 7, 'exact control prerequisites')
        take('FLOOR1_FAILURE case=0 reason=reset_primer_empty')
        take(f'VORBIS_REGISTRY_CLEANUP case=0 closed=1 empty=1 unsupported=1 core={core}')
    else:
        prefix_bytes = sum(sum(c['expected_packet_bytes'][:7]) + sum(c['expected_packet_bytes'][:5]) for c in cases[:8])
        take(f'VORBIS_RESET_COMPLETE cases=8 calls=72 replay_packets=448 prefix_packets=96 retries=24 '
             f'replay_pcm=901120 prefix_pcm={prefix_bytes} core={core}')
        take(f'VORBIS_REGISTRY_COMPLETE registrations=14 bindings=14 closes=8 unregistrations=14 metadata=112 retries=312 core={core}')
        take(f'FLOOR1_COMPLETE accepted=8 rejected=6 packets=112 pcm=225280 core={core}')
        need(counts == dict(baseline_packets=112, baseline_pcm_bytes=225280, baseline_retries=312,
             baseline_metadata=112, reset_calls=72, reset_call_events=72, skipped_calls=0, replay_packets=448,
             prefix_packets=96, reset_retries=24, replay_pcm_bytes=901120, prefix_pcm_bytes=prefix_bytes,
             reset_metadata=544, rounds_completed=32, reset_cases_completed=8), 'complete counted reset matrix')
    take('FLOOR1_CONTROLLED_STOP')
    need(at == len(lines), 'extra protocol events')
    return dict(counts, baseline_pcm_sha256=baseline_hashes, replay_pcm_sha256=replay_hashes,
        prefix_pcm_sha256=prefix_hashes, case_counts=case_counts, control_primer=probe,
        core=core, control_effective=bool(control), exact_failure='reset_primer_empty' if control else None,
        reset_cycles_qualified=not control, registered_callbacks_qualified=not control,
        target_capture_completed=not control, registrations=1 if control else 14,
        bindings=1 if control else 14, closes=0 if control else 8, unregistrations=1 if control else 14,
        vendor_comparison_available=False, independent_reference_compared=False,
        full_G1_qualified=False, full_G3_qualified=False, full_G6_qualified=False, radio_qualified=False)
