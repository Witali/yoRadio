"""Synthetic finite raw-open OOM protocol tests; no SDK or codec execution."""
import copy
import hashlib
import unittest
from vorbis_open_oom_protocol import MAX_CALLS, MAX_REQUEST, validate_log
from vorbis_registered_protocol import validate_log as registered_log


def model():
    blocks = [256 if v == 'S' else 2048 for v in 'SSLLLSLSSSLLSS']
    sizes = [0] + [a + b for a, b in zip(blocks, blocks[1:])]
    return dict(cases=[dict(id=f'case-{i}', expected_valid=i < 8,
        expected_packet_bytes=sizes[:], offsets=[p * 11 for p in range(15)]) for i in range(14)])


def allocations(case):
    return [48, 80, 192, 512] + [64 + 4 * n for n in range(2 + case % 3)]


def pcm(case, packet):
    size = model()['cases'][case]['expected_packet_bytes'][packet]
    pattern = bytes((n + case * 7 + packet * 13) % 256 for n in range(256))
    return (pattern * ((size + 255) // 256))[:size]


def protocol(target='esp32', control=None):
    core, machine = (1, 94) if target == 'esp32' else (0, 243)
    rows = [f'FLOOR1_START coordinator=0 decoder={core}',
        f'VORBIS_REGISTRY_BEGIN cases=14 packets=112 retries=312 core={core}',
        f'VORBIS_REGISTRY_INITIAL empty=1 unsupported=1 core={core}',
        f'VORBIS_OPEN_OOM_BEGIN target={target} machine={machine} core={core}']

    def stop(case, reason):
        rows.extend([f'FLOOR1_FAILURE case={case} reason={reason}',
            f'VORBIS_REGISTRY_CLEANUP case={case} closed=0 empty=1 unsupported=1 core={core}',
            'FLOOR1_CONTROLLED_STOP'])
        return '\n'.join(rows)

    def result_fields(result, handle, calls, injected):
        return f'result={result} handle={handle} calls={calls} injected={injected} live=0 guards=1'

    for case, c in enumerate(model()['cases']):
        rows.extend([f'VORBIS_REGISTRY_REGISTER case={case} result=0 ops=1 supported=1 core={core}',
            f'VORBIS_REGISTRY_BIND_OPEN case={case} match=1 core={core}',
            f'VORBIS_REGISTRY_BIND_DECODE case={case} match=1 core={core}',
            f'VORBIS_REGISTRY_BIND_OTHER case={case} reset=1 close=1 core={core}'])
        if not c['expected_valid']:
            rows.extend([f'FLOOR1_OPEN case={case} result=-1 handle=0',
                f'FLOOR1_REJECT case={case} name={c["id"]} result=-1 handle=0 core={core}',
                f'VORBIS_OPEN_OOM_MALFORMED case={case} calls={case - 1} injected=0 result=-1 handle=0 live=0 guards=1 core={core}',
                f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}'])
            continue
        rows.append(f'FLOOR1_OPEN case={case} result=0 handle=1')
        for packet, size in enumerate(c['expected_packet_bytes']):
            if size:
                rows.extend(f'VORBIS_REGISTRY_RETRY case={case} packet={packet} attempt={a} result=-8 consumed=0 '
                    f'decoded=0 needed={size} untouched=1 canaries=1 core={core}' for a in range(3))
            fields = 'result=0 sample_rate=48000 channel=2 bits=16' if size else 'result=-9 sample_rate=0 channel=0 bits=0'
            rows.extend([f'VORBIS_REGISTRY_META case={case} packet={packet} {fields} core={core}',
                f'FLOOR1_PCM case={case} packet={packet} consumed=11 bytes={size} hex={pcm(case, packet).hex()}'])
        sizes = allocations(case)
        rows.extend([f'VORBIS_REGISTRY_CLOSE case={case} called=1 core={core}',
            f'VORBIS_OPEN_OOM_DISCOVER case={case} calls={len(sizes)} live=0 guards=1 core={core}'])
        rows.extend(f'VORBIS_OPEN_OOM_ALLOC case={case} call={n} bytes={size}' for n, size in enumerate(sizes, 1))
        for mode in ('once', 'persistent'):
            for nth in range(1, len(sizes) + 1):
                # One continued positive request after a failed paired allocation.
                calls = nth + 1 if nth == 5 else nth
                injected = calls - nth + 1 if mode == 'persistent' else 1
                legacy = control == 'oom-legacy' and case == 0 and mode == 'once' and nth == 4
                rows.append(f'VORBIS_OPEN_OOM_FAULT case={case} mode={mode} nth={nth} calls={calls} injected={injected} '
                    f'result={-1 if legacy else -2} handle=0 live=0 guards=1 core={core}')
                if legacy: return stop(0, 'oom_memory_error')
                rows.append(f'VORBIS_OPEN_OOM_RECOVER case={case} mode={mode} nth={nth} packets=14 pcm=28160 baseline_exact=1 live=0 guards=1 core={core}')
        rows.extend([f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}',
            f'FLOOR1_ACCEPT case={case} name={c["id"]} packets=14 pcm=28160 renderer_repair=1 core={core}'])
    n0, m8 = len(allocations(0)), 7
    nested = [((-2, 0, 4, 1), (-1, 0, m8, 0)), ((-1, 0, m8, 0), (-2, 0, 4, 1)),
              ((0, 1, n0, 0), (-2, 0, 4, 1)), ((-2, 0, 1, 1), (-1, 0, m8, 0))]
    for pair, (inner, outer) in enumerate(nested):
        rows.extend([f'VORBIS_OPEN_OOM_NEST_ENTER pair={pair} outer_call=1 core={core}',
            f'VORBIS_OPEN_OOM_NEST_INNER pair={pair} {result_fields(*inner)} core={core}',
            f'VORBIS_OPEN_OOM_NEST_OUTER pair={pair} {result_fields(*outer)} nested=1 core={core}'])
    for scenario in range(2):
        rows.extend([f'VORBIS_OPEN_OOM_TASK_WAIT scenario={scenario} role=A call=1 core=0',
            f'VORBIS_OPEN_OOM_TASK_WAIT scenario={scenario} role=B call=1 core={core}',
            f'VORBIS_OPEN_OOM_TASK_RELEASE scenario={scenario} role=A',
            f'VORBIS_OPEN_OOM_TASK_RESULT scenario={scenario} role=A {result_fields(-2, 0, 1, 1)} core=0',
            f'VORBIS_OPEN_OOM_TASK_RELEASE scenario={scenario} role=B',
            f'VORBIS_OPEN_OOM_TASK_FIRST scenario={scenario} role=B call=1 success=1 core={core}'])
        wrong = control == 'oom-global' and scenario == 1
        b = (-2, 0, 4, 1) if scenario == 0 else (-2 if wrong else -1, 0, m8, 0)
        rows.append(f'VORBIS_OPEN_OOM_TASK_RESULT scenario={scenario} role=B {result_fields(*b)} core={core}')
        if wrong: return stop(14, 'oom_task_error_isolation')
        rows.append(f'VORBIS_OPEN_OOM_TASK_DONE scenario={scenario} isolated=1')
    s = sum(len(allocations(c)) for c in range(8))
    rows.extend([f'VORBIS_OPEN_OOM_COMPLETE valid=8 malformed=6 discoveries=8 faults={2*s} recoveries={2*s} recovery_packets={28*s} recovery_pcm={56320*s} nested=4 task_scenarios=2 live=0 guards=1 core={core}',
        f'VORBIS_REGISTRY_COMPLETE registrations=14 bindings=14 closes=8 unregistrations=14 metadata=112 retries=312 core={core}',
        f'FLOOR1_COMPLETE accepted=8 rejected=6 packets=112 pcm=225280 core={core}', 'FLOOR1_CONTROLLED_STOP'])
    return '\n'.join(rows)


class OpenOOMProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.positive = protocol()
        cls.legacy = protocol(control='oom-legacy')
        cls.global_log = protocol(control='oom-global')

    def check_log(self, log=None, target='esp32', control=None, **facts):
        return validate_log(self.positive if log is None else log, model(), target, control,
            **dict(dict(returncode=0, timed_out=False, interrupted=False), **facts))

    def rejects(self, *logs, control=None):
        for n, log in enumerate(logs):
            with self.subTest(mutation=n), self.assertRaises(ValueError): self.check_log(log, control=control)

    def test_complete_both_architectures_crlf_and_original_registry_protocol(self):
        for target in ('esp32', 'esp32c3'):
            log = protocol(target).replace('\n', '\r\n')
            r = self.check_log(log, target)
            registered = registered_log(log, model(), target, returncode=0, timed_out=False, interrupted=False)
            self.assertEqual(r['baseline_pcm_sha256'], registered['pcm_sha256'])
            self.assertTrue(r['raw_open_oom_qualified'] and r['target_capture_completed'])
            self.assertEqual((r['baseline_packets'], r['baseline_pcm_bytes'], r['baseline_retries']), (112, 225280, 312))
            self.assertEqual(r['allocation_request_bytes'], {str(c): allocations(c) for c in range(8)})
            s = sum(len(allocations(c)) for c in range(8))
            self.assertEqual((r['faults'], r['recoveries'], r['recovery_packets'], r['recovery_pcm_bytes']), (2*s, 2*s, 28*s, 56320*s))
            self.assertFalse(any(r[k] for k in ('independent_reference_compared', 'vendor_comparison_available',
                'full_G1_qualified', 'full_G4_qualified', 'full_G6_qualified', 'radio_qualified', 'recovery_pcm_is_separately_captured')))

    def test_baseline_hash_includes_every_high_bit_and_final_sample(self):
        r = self.check_log()
        for case in range(8):
            data = b''.join(pcm(case, packet) for packet in range(14))
            self.assertEqual(r['baseline_pcm_sha256'][str(case)], hashlib.sha256(data).hexdigest())
        rows = self.positive.splitlines()
        at = next(i for i, row in enumerate(rows) if row.startswith('FLOOR1_PCM case=7 packet=13 '))
        head, hexdump = rows[at].split('hex='); data = bytearray.fromhex(hexdump); data[-1] ^= 0x80
        rows[at] = head + 'hex=' + data.hex()
        changed = self.check_log('\n'.join(rows))
        self.assertNotEqual(r['baseline_pcm_sha256']['7'], changed['baseline_pcm_sha256']['7'])

    def test_named_controls_both_cores_are_diagnostic_only(self):
        for target in ('esp32', 'esp32c3'):
            for control in ('oom-legacy', 'oom-global'):
                r = self.check_log(protocol(target, control), target, control)
                self.assertTrue(r['control_effective'])
                self.assertFalse(r['raw_open_oom_qualified'] or r['target_capture_completed'])
                if control == 'oom-legacy':
                    self.assertEqual((r['faults'], r['recoveries'], r['baseline_packets']), (4, 3, 14))
                    self.assertEqual(r['exact_failure'], 'oom_memory_error')
                else:
                    self.assertEqual(len(r['nested_pairs']), 4)
                    self.assertTrue(r['task_scenarios'][0]['isolated'])
                    self.assertFalse(r['task_scenarios'][1]['isolated'])
                    self.assertEqual(r['task_scenarios'][1]['B']['injected'], 0)

    def test_actual_terminal_facts_and_controls_are_required(self):
        with self.assertRaises(TypeError): validate_log(self.positive, model(), 'esp32')
        for facts in (dict(returncode=1), dict(returncode=False), dict(returncode=None), dict(returncode=-9),
                      dict(timed_out=True), dict(timed_out=None), dict(interrupted=True), dict(interrupted=None)):
            with self.subTest(facts=facts), self.assertRaises(ValueError): self.check_log(**facts)
        with self.assertRaises(ValueError): self.check_log(control='oom-unknown')
        self.rejects(self.positive, control='oom-legacy')
        self.rejects(self.positive, control='oom-global')
        self.rejects(self.legacy, self.global_log)

    def test_each_event_family_is_required_unique_and_ordered(self):
        rows = self.positive.splitlines()
        for family in ('BEGIN', 'DISCOVER', 'ALLOC', 'FAULT', 'RECOVER', 'MALFORMED', 'NEST_ENTER', 'NEST_INNER',
                       'NEST_OUTER', 'TASK_WAIT', 'TASK_RELEASE', 'TASK_FIRST', 'TASK_RESULT', 'TASK_DONE', 'COMPLETE'):
            at = next(i for i, row in enumerate(rows) if row.startswith('VORBIS_OPEN_OOM_' + family + ' '))
            swapped = rows[:]; swapped[at], swapped[at+1] = swapped[at+1], swapped[at]
            self.rejects('\n'.join(rows[:at] + rows[at+1:]), '\n'.join(rows[:at] + [rows[at]] + rows[at:]), '\n'.join(swapped))

    def test_latest_and_middle_fault_recoveries_cannot_be_omitted(self):
        rows = self.positive.splitlines()
        for nth in (2, len(allocations(7))):
            remove = ('VORBIS_OPEN_OOM_FAULT case=7 mode=persistent nth=' + str(nth) + ' ',
                      'VORBIS_OPEN_OOM_RECOVER case=7 mode=persistent nth=' + str(nth) + ' ')
            self.rejects('\n'.join(row for row in rows if not row.startswith(remove)))

    def test_discovery_requires_all_positive_requests_and_finite_capacity(self):
        for before, after in (('case=0 calls=6 live=0', 'case=0 calls=3 live=0'), ('call=1 bytes=48', 'call=1 bytes=0'),
                ('call=1 bytes=48', f'call=1 bytes={MAX_REQUEST+1}'), ('call=2 bytes=80', 'call=1 bytes=80'),
                ('case=0 calls=6 live=0', f'case=0 calls={MAX_CALLS+1} live=0')):
            self.assertIn(before, self.positive); self.rejects(self.positive.replace(before, after, 1))

    def test_actual_once_and_persistent_injection_counts_not_just_configured_nth(self):
        for before, after in (('nth=1 calls=1 injected=1', 'nth=1 calls=1 injected=0'),
                ('nth=1 calls=1 injected=1', 'nth=1 calls=2 injected=1'),
                ('nth=5 calls=6 injected=1', 'nth=5 calls=4 injected=1'),
                ('nth=5 calls=6 injected=1', 'nth=5 calls=7 injected=1'),
                ('mode=persistent nth=5 calls=6 injected=2', 'mode=persistent nth=5 calls=6 injected=1')):
            self.assertIn(before, self.positive); self.rejects(self.positive.replace(before, after, 1))

    def test_fault_error_null_publication_cleanup_and_guard_facts(self):
        for before, after in (('result=-2 handle=0 live=0 guards=1', 'result=-1 handle=0 live=0 guards=1'),
                ('result=-2 handle=0 live=0 guards=1', 'result=-5 handle=0 live=0 guards=1'),
                ('result=-2 handle=0 live=0 guards=1', 'result=0 handle=1 live=0 guards=1'),
                ('result=-2 handle=0 live=0 guards=1', 'result=-2 handle=0 live=1 guards=1'),
                ('result=-2 handle=0 live=0 guards=1', 'result=-2 handle=0 live=0 guards=0')):
            self.rejects(self.positive.replace(before, after, 1))

    def test_recovery_requires_full_target_asserted_packet_and_byte_counts(self):
        for before, after in (('packets=14 pcm=28160 baseline_exact=1', 'packets=13 pcm=28160 baseline_exact=1'),
                ('packets=14 pcm=28160 baseline_exact=1', 'packets=14 pcm=28156 baseline_exact=1'),
                ('baseline_exact=1 live=0 guards=1', 'baseline_exact=0 live=0 guards=1'),
                ('baseline_exact=1 live=0 guards=1', 'baseline_exact=1 live=1 guards=1')):
            self.rejects(self.positive.replace(before, after, 1))

    def test_oom_events_cannot_move_across_registry_close_or_case_boundary(self):
        rows = self.positive.splitlines()
        at = next(i for i, row in enumerate(rows) if row.startswith('VORBIS_OPEN_OOM_DISCOVER case=0 '))
        moved = rows[at]; rest = rows[:at] + rows[at+1:]
        for prefix in ('VORBIS_REGISTRY_CLOSE case=0 ', 'VORBIS_REGISTRY_UNREGISTER case=0 ', 'FLOOR1_OPEN case=1 '):
            n = next(i for i, row in enumerate(rest) if row.startswith(prefix))
            self.rejects('\n'.join(rest[:n] + [moved] + rest[n:]))

    def test_malformed_headers_are_not_memory_failures_without_injected_null(self):
        for before, after in (('calls=7 injected=0 result=-1', 'calls=7 injected=1 result=-1'),
                ('calls=7 injected=0 result=-1', 'calls=7 injected=0 result=-2'),
                ('case=8 result=-1 handle=0', 'case=8 result=-2 handle=0')):
            self.rejects(self.positive.replace(before, after, 1))

    def test_nested_scope_restoration_success_and_both_error_directions(self):
        rows = self.positive.splitlines()
        for prefix in ('VORBIS_OPEN_OOM_NEST_INNER pair=0 ', 'VORBIS_OPEN_OOM_NEST_OUTER pair=0 ',
                       'VORBIS_OPEN_OOM_NEST_OUTER pair=1 ', 'VORBIS_OPEN_OOM_NEST_INNER pair=2 ',
                       'VORBIS_OPEN_OOM_NEST_INNER pair=3 '):
            n = next(i for i, row in enumerate(rows) if row.startswith(prefix))
            changed = rows[:]; changed[n] = changed[n].replace('result=-2', 'result=-1').replace('result=0', 'result=-2') if 'result=-2' in changed[n] or 'result=0' in changed[n] else changed[n].replace('result=-1', 'result=-2')
            self.rejects('\n'.join(changed))
        self.rejects(self.positive.replace('handle=1 calls=6 injected=0 live=0', 'handle=1 calls=6 injected=0 live=1', 1))

    def test_task_handoff_order_actual_first_success_and_no_fault_companion(self):
        for before, after in (('role=B call=1 success=1', 'role=B call=1 success=0'),
                ('role=A result=-2 handle=0 calls=1', 'role=A result=-1 handle=0 calls=1'),
                ('role=B result=-1 handle=0 calls=7 injected=0', 'role=B result=-2 handle=0 calls=7 injected=0'),
                ('role=B result=-1 handle=0 calls=7 injected=0', 'role=B result=-1 handle=0 calls=7 injected=1')):
            self.rejects(self.positive.replace(before, after, 1))
        self.rejects(self.positive.replace('TASK_RELEASE scenario=0 role=A', 'TASK_RELEASE scenario=0 role=B', 1))

    def test_legacy_control_requires_exact_first_three_recoveries_and_once_four(self):
        for before, after in (('nth=4 calls=4 injected=1 result=-1', 'nth=4 calls=4 injected=1 result=-2'),
                ('mode=once nth=4', 'mode=persistent nth=4'), ('reason=oom_memory_error', 'reason=other_error'),
                ('FLOOR1_FAILURE case=0', 'FLOOR1_FAILURE case=1'), ('closed=0 empty=1', 'closed=1 empty=1')):
            self.rejects(self.legacy.replace(before, after, 1), control='oom-legacy')
        self.rejects('\n'.join(row for row in self.legacy.splitlines() if not row.startswith('VORBIS_OPEN_OOM_RECOVER case=0 mode=once nth=3 ')), control='oom-legacy')

    def test_global_control_requires_all_prefixes_and_exact_semantic_contamination(self):
        for before, after in (('role=B result=-2 handle=0 calls=7 injected=0', 'role=B result=-1 handle=0 calls=7 injected=0'),
                ('role=B result=-2 handle=0 calls=7 injected=0', 'role=B result=-2 handle=0 calls=7 injected=1'),
                ('reason=oom_task_error_isolation', 'reason=oom_memory_error'), ('FLOOR1_FAILURE case=14', 'FLOOR1_FAILURE case=0')):
            self.rejects(self.global_log.replace(before, after, 1), control='oom-global')
        self.rejects('\n'.join(row for row in self.global_log.splitlines() if not row.startswith('VORBIS_OPEN_OOM_TASK_DONE scenario=0 ')), control='oom-global')

    def test_architecture_core_completion_unknown_and_panic_are_strict(self):
        for before, after in (('target=esp32 machine=94', 'target=esp32 machine=243'), ('target=esp32 machine=94', 'target=esp32c3 machine=94'),
                ('TASK_WAIT scenario=0 role=A call=1 core=0', 'TASK_WAIT scenario=0 role=A call=1 core=1'),
                ('TASK_WAIT scenario=0 role=B call=1 core=1', 'TASK_WAIT scenario=0 role=B call=1 core=0'),
                ('nested=4 task_scenarios=2', 'nested=3 task_scenarios=2'), ('discoveries=8', 'discoveries=7')):
            self.rejects(self.positive.replace(before, after, 1))
        self.rejects(self.positive + '\nVORBIS_OPEN_OOM_UNKNOWN value=1', self.positive + '\nFLOOR1_CONTROLLED_STOP', self.positive + '\nGuru Meditation Error')
        with self.assertRaises(ValueError): self.check_log(target='esp32c3')

    def test_matrix_baseline_metadata_and_geometry_cannot_shrink(self):
        for kind in ('count', 'duplicate', 'validity', 'size', 'offset'):
            m = copy.deepcopy(model())
            if kind == 'count': m['cases'].pop()
            if kind == 'duplicate': m['cases'][1]['id'] = m['cases'][0]['id']
            if kind == 'validity': m['cases'][8]['expected_valid'] = True
            if kind == 'size': m['cases'][0]['expected_packet_bytes'][1] += 4
            if kind == 'offset': m['cases'][0]['offsets'][1] = 0
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                validate_log(self.positive, m, 'esp32', returncode=0, timed_out=False, interrupted=False)
        self.rejects(self.positive.replace('sample_rate=48000', 'sample_rate=0', 1),
            self.positive.replace('channel=2 bits=16', 'channel=1 bits=16', 1),
            self.positive.replace('consumed=11 bytes=512', 'consumed=10 bytes=512', 1))


if __name__ == '__main__': unittest.main()
