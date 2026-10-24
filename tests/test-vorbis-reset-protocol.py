"""Synthetic public raw reset transcripts; no codecs, SDK, compiler or target."""
import copy
import hashlib
import unittest
from vorbis_registered_protocol import validate_log as registered_log
from vorbis_reset_protocol import validate_log


def model():
    blocks = [256 if mode == 'S' else 2048 for mode in 'SSLLLSLSSSLLSS']
    sizes = [0] + [a + b for a, b in zip(blocks, blocks[1:])]
    return dict(cases=[dict(id=f'case-{i}', expected_valid=i < 8,
        expected_packet_bytes=sizes[:], offsets=[p * 11 for p in range(15)]) for i in range(14)])


def pcm(case, packet):
    size = model()['cases'][case]['expected_packet_bytes'][packet]
    # Retain varying byte pairs with high bits through the final PCM16 sample.
    pattern = bytes((n + case * 7 + packet * 13) % 256 for n in range(256))
    return (pattern * ((size + 255) // 256))[:size]


def protocol(target='esp32', control=None, ready=False):
    core = 1 if target == 'esp32' else 0
    rows = [f'FLOOR1_START coordinator=0 decoder={core}',
        f'VORBIS_REGISTRY_BEGIN cases=14 packets=112 retries=312 core={core}',
        f'VORBIS_REGISTRY_INITIAL empty=1 unsupported=1 core={core}']

    def call(case, round_id, purpose, attempt=0, skipped=False):
        rows.append(f'VORBIS_RESET_CALL case={case} round={round_id} purpose={purpose} attempt={attempt} '
            f'called={0 if skipped else 1} result={"SKIPPED" if skipped else "0"} core={core}')

    def packet(case, round_id, phase, number, probe=False):
        data = b'\x80\xff' * 1152 if probe else pcm(case, number)
        fields = 'info_result=-9 sample_rate=0 channel=0 bits=0' if not data and not ready else 'info_result=0 sample_rate=48000 channel=2 bits=16'
        rows.append(f'VORBIS_RESET_PCM case={case} round={round_id} phase={phase} packet={number} '
            f'consumed=11 bytes={len(data)} {fields} hex={data.hex()}')

    for case, c in enumerate(model()['cases']):
        rows += [f'VORBIS_REGISTRY_REGISTER case={case} result=0 ops=1 supported=1 core={core}',
            f'VORBIS_REGISTRY_BIND_OPEN case={case} match=1 core={core}',
            f'VORBIS_REGISTRY_BIND_DECODE case={case} match=1 core={core}',
            f'VORBIS_REGISTRY_BIND_OTHER case={case} reset=1 close=1 core={core}']
        if not c['expected_valid']:
            rows += [f'FLOOR1_OPEN case={case} result=-1 handle=0',
                f'FLOOR1_REJECT case={case} name={c["id"]} result=-1 handle=0 core={core}',
                f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}']
            continue
        rows.append(f'FLOOR1_OPEN case={case} result=0 handle=1')
        call(case, 'initial', 'initial')
        for p, size in enumerate(c['expected_packet_bytes']):
            if size:
                rows += [f'VORBIS_REGISTRY_RETRY case={case} packet={p} attempt={a} result=-8 consumed=0 '
                    f'decoded=0 needed={size} untouched=1 canaries=1 core={core}' for a in range(3)]
            fields = 'result=-9 sample_rate=0 channel=0 bits=0' if not size and not ready else 'result=0 sample_rate=48000 channel=2 bits=16'
            rows += [f'VORBIS_REGISTRY_META case={case} packet={p} {fields} core={core}',
                f'FLOOR1_PCM case={case} packet={p} consumed=11 bytes={size} hex={pcm(case, p).hex()}']
        rows.append(f'VORBIS_RESET_BEGIN case={case} rounds=4 core={core}')
        for r in range(4):
            if r in (1, 2):
                call(case, r, 'prepare')
                for p in range(7 if r == 1 else 5): packet(case, r, 'prefix', p)
                if r == 2:
                    rows += [f'VORBIS_RESET_RETRY case={case} round=2 packet=5 attempt={a} result=-8 consumed=0 '
                        f'decoded=0 needed={c["expected_packet_bytes"][5]} untouched=1 canaries=1 core={core}' for a in range(3)]
            skip = control == 'reset-skip' and case == 0 and r == 1
            for a in range(3 if r == 3 else 1): call(case, r, 'restart', a, skip)
            if skip:
                packet(case, r, 'full', 0, probe=True)
                rows += ['FLOOR1_FAILURE case=0 reason=reset_primer_empty',
                    f'VORBIS_REGISTRY_CLEANUP case=0 closed=1 empty=1 unsupported=1 core={core}',
                    'FLOOR1_CONTROLLED_STOP']
                return '\n'.join(rows)
            for p in range(14): packet(case, r, 'full', p)
            rows.append(f'VORBIS_RESET_ROUND case={case} round={r} packets=14 pcm=28160 baseline_exact=1 core={core}')
        prefix_bytes = sum(c['expected_packet_bytes'][:7]) + sum(c['expected_packet_bytes'][:5])
        rows += [f'VORBIS_RESET_DONE case={case} calls=9 replay_packets=56 prefix_packets=12 retries=3 replay_pcm=112640 prefix_pcm={prefix_bytes} core={core}',
            f'VORBIS_REGISTRY_CLOSE case={case} called=1 core={core}',
            f'VORBIS_REGISTRY_UNREGISTER case={case} empty=1 unsupported=1 core={core}',
            f'FLOOR1_ACCEPT case={case} name={c["id"]} packets=14 pcm=28160 renderer_repair=1 core={core}']
    rows += [f'VORBIS_RESET_COMPLETE cases=8 calls=72 replay_packets=448 prefix_packets=96 retries=24 replay_pcm=901120 prefix_pcm=212992 core={core}',
        f'VORBIS_REGISTRY_COMPLETE registrations=14 bindings=14 closes=8 unregistrations=14 metadata=112 retries=312 core={core}',
        f'FLOOR1_COMPLETE accepted=8 rejected=6 packets=112 pcm=225280 core={core}', 'FLOOR1_CONTROLLED_STOP']
    return '\n'.join(rows)


class ResetProtocol(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.positive = protocol()
        cls.control_log = protocol(control='reset-skip')

    def check_log(self, log=None, target='esp32', control=None, **facts):
        return validate_log(self.positive if log is None else log, model(), target, control,
            **dict(dict(returncode=0, timed_out=False, interrupted=False), **facts))

    def rejects(self, *logs, control=None):
        for n, log in enumerate(logs):
            with self.subTest(mutation=n), self.assertRaises(ValueError):
                self.check_log(log, control=control)

    def test_complete_both_cores_crlf_and_registered_baseline_compatibility(self):
        for target in ('esp32', 'esp32c3'):
            log = protocol(target).replace('\n', '\r\n')
            result = self.check_log(log, target)
            old = registered_log(log, model(), target, returncode=0, timed_out=False, interrupted=False)
            self.assertEqual(result['baseline_pcm_sha256'], old['pcm_sha256'])
            self.assertTrue(result['reset_cycles_qualified'] and result['target_capture_completed'])
            for field, expected in dict(reset_calls=72, replay_packets=448, prefix_packets=96, reset_retries=24,
                    replay_pcm_bytes=901120, prefix_pcm_bytes=212992, baseline_packets=112,
                    baseline_pcm_bytes=225280, rounds_completed=32, reset_cases_completed=8).items():
                self.assertEqual(result[field], expected)
            self.assertFalse(any(result[k] for k in ('independent_reference_compared', 'vendor_comparison_available',
                'full_G1_qualified', 'full_G3_qualified', 'full_G6_qualified', 'radio_qualified')))

    def test_every_full_and_prefix_hash_is_actual_complete_pcm(self):
        result = self.check_log()
        for case in range(8):
            key = str(case)
            expected = hashlib.sha256(b''.join(pcm(case, p) for p in range(14))).hexdigest()
            self.assertEqual(result['baseline_pcm_sha256'][key], expected)
            self.assertEqual(result['replay_pcm_sha256'][key], {str(r): expected for r in range(4)})
            for r, n in ((1, 7), (2, 5)):
                self.assertEqual(result['prefix_pcm_sha256'][key][str(r)],
                    hashlib.sha256(b''.join(pcm(case, p) for p in range(n))).hexdigest())

    def test_ready_primers_and_finite_control_both_cores(self):
        self.assertTrue(self.check_log(protocol(ready=True))['reset_cycles_qualified'])
        for target in ('esp32', 'esp32c3'):
            r = self.check_log(protocol(target, 'reset-skip'), target, 'reset-skip')
            self.assertTrue(r['control_effective'])
            self.assertFalse(r['reset_cycles_qualified'] or r['target_capture_completed'])
            self.assertEqual((r['reset_calls'], r['skipped_calls'], r['reset_call_events']), (3, 1, 4))
            self.assertEqual((r['baseline_packets'], r['replay_packets'], r['prefix_packets'], r['closes']), (14, 14, 7, 0))
            self.assertEqual(r['control_primer']['bytes'], 2304)

    def test_actual_process_facts_are_required(self):
        with self.assertRaises(TypeError): validate_log(self.positive, model(), 'esp32')
        for facts in (dict(returncode=1), dict(returncode=False), dict(returncode=None), dict(returncode=-9),
                      dict(timed_out=True), dict(timed_out=None), dict(interrupted=True), dict(interrupted=None)):
            with self.subTest(facts=facts), self.assertRaises(ValueError): self.check_log(**facts)

    def test_every_event_family_is_required_once_in_order(self):
        rows = self.positive.splitlines()
        for family in ('CALL', 'BEGIN', 'PCM', 'RETRY', 'ROUND', 'DONE', 'COMPLETE'):
            at = next(i for i, row in enumerate(rows) if row.startswith('VORBIS_RESET_' + family + ' '))
            swapped = rows[:]; swapped[at], swapped[at + 1] = swapped[at + 1], swapped[at]
            self.rejects('\n'.join(rows[:at] + rows[at + 1:]),
                '\n'.join(rows[:at] + [rows[at]] + rows[at:]), '\n'.join(swapped))

    def test_reset_data_cannot_move_across_open_close_or_cases(self):
        rows = self.positive.splitlines()
        at = next(i for i, row in enumerate(rows) if row.startswith('VORBIS_RESET_BEGIN case=0'))
        line = rows[at]; reduced = rows[:at] + rows[at + 1:]
        for prefix in ('FLOOR1_OPEN case=0', 'VORBIS_REGISTRY_CLOSE case=0', 'FLOOR1_OPEN case=1'):
            n = next(i for i, row in enumerate(reduced) if row.startswith(prefix))
            self.rejects('\n'.join(reduced[:n] + [line] + reduced[n:]))
        self.rejects('\n'.join(row for row in rows if not row.startswith('VORBIS_RESET_')))

    def test_reset_calls_are_exact_successful_ordered_public_calls(self):
        for before, after in (('purpose=initial', 'purpose=restart'), ('round=0 purpose=restart attempt=0', 'round=0 purpose=restart attempt=1'),
                ('called=1 result=0', 'called=1 result=-1'), ('called=1 result=0', 'called=0 result=SKIPPED'),
                ('round=3 purpose=restart attempt=2', 'round=3 purpose=restart attempt=1')):
            self.assertIn(before, self.positive)
            self.rejects(self.positive.replace(before, after, 1))

    def test_metadata_is_checked_for_all_replays_and_prefixes(self):
        for before, after in (('info_result=0 sample_rate=48000', 'info_result=0 sample_rate=0'),
                ('info_result=0 sample_rate=48000 channel=2', 'info_result=0 sample_rate=48000 channel=1'),
                ('bits=16 hex=', 'bits=24 hex='), ('info_result=-9 sample_rate=0', 'info_result=0 sample_rate=0'),
                ('info_result=-9 sample_rate=0', 'info_result=-1 sample_rate=0')):
            self.rejects(self.positive.replace(before, after, 1))

    def test_entire_pcm_including_final_high_bit_sample_must_equal(self):
        rows = self.positive.splitlines()
        for phase in ('full', 'prefix'):
            at = next(i for i, row in enumerate(rows) if row.startswith('VORBIS_RESET_PCM case=0 round=') and
                ('phase=' + phase + ' ') in row and 'packet=1 ' in row)
            # Flip only the final high bit; no signed conversion, trim or tolerance.
            left, hexdump = rows[at].split('hex=')
            data = bytearray.fromhex(hexdump); data[-1] ^= 0x80
            changed = rows[:]; changed[at] = left + 'hex=' + data.hex()
            self.rejects('\n'.join(changed))
        self.rejects(self.positive.replace('phase=full packet=1 consumed=11 bytes=512',
            'phase=full packet=1 consumed=10 bytes=512', 1),
            self.positive.replace('phase=full packet=1 consumed=11 bytes=512',
            'phase=full packet=1 consumed=11 bytes=510', 1))

    def test_reset_tiny_retries_are_exact_and_guarded(self):
        for before, after in (('result=-8', 'result=-1'), ('consumed=0', 'consumed=1'), ('decoded=0', 'decoded=1'),
                ('needed=2304', 'needed=2305'), ('untouched=1', 'untouched=0'), ('canaries=1', 'canaries=0')):
            rows = self.positive.splitlines()
            at = next(i for i, row in enumerate(rows) if row.startswith('VORBIS_RESET_RETRY '))
            self.assertIn(before, rows[at]); rows[at] = rows[at].replace(before, after, 1)
            self.rejects('\n'.join(rows))

    def test_reset_skip_requires_all_exact_prior_obligations(self):
        log = self.control_log
        self.rejects(self.positive, control='reset-skip')
        self.rejects(log)
        for before, after in (('round=1 purpose=restart', 'round=2 purpose=restart'),
                ('called=0 result=SKIPPED', 'called=1 result=0'), ('case=0 reason=reset_primer_empty', 'case=1 reason=reset_primer_empty'),
                ('reason=reset_primer_empty', 'reason=reset_baseline_exact'), ('closed=1 empty=1', 'closed=0 empty=1'),
                ('closed=1 empty=1', 'closed=1 empty=0')):
            self.rejects(log.replace(before, after, 1), control='reset-skip')
        self.rejects(log + '\nVORBIS_REGISTRY_CLOSE case=0 called=1 core=1', control='reset-skip')

    def test_control_probe_must_be_actual_nonempty_bounded_pcm_and_ready_metadata(self):
        rows = self.control_log.splitlines()
        at = next(i for i, row in enumerate(rows) if row.startswith('VORBIS_RESET_PCM case=0 round=1 phase=full packet=0 '))
        for replacement in (rows[at].replace('bytes=2304', 'bytes=0').split('hex=')[0] + 'hex=',
                rows[at].replace('info_result=0 sample_rate=48000 channel=2 bits=16', 'info_result=-9 sample_rate=0 channel=0 bits=0'),
                rows[at].replace('consumed=11', 'consumed=10'),
                rows[at].replace('bytes=2304', 'bytes=2303')[:-2],
                rows[at].split('bytes=')[0] + 'bytes=4098 info_result=0 sample_rate=48000 channel=2 bits=16 hex=' + '80ff' * 2049):
            changed = rows[:]; changed[at] = replacement
            self.rejects('\n'.join(changed), control='reset-skip')

    def test_completion_counts_invalid_cases_core_and_unknown_events(self):
        for before, after in (('calls=9 replay_packets=56', 'calls=8 replay_packets=56'),
                ('calls=72 replay_packets=448', 'calls=71 replay_packets=448'),
                ('prefix_pcm=212992', 'prefix_pcm=212990'), ('baseline_exact=1', 'baseline_exact=0'),
                ('case=8 result=-1 handle=0', 'case=8 result=-2 handle=0'), ('core=1', 'core=0')):
            self.rejects(self.positive.replace(before, after, 1))
        for suffix in ('VORBIS_RESET_UNKNOWN value=1', 'FLOOR1_CONTROLLED_STOP', 'Guru Meditation Error'):
            self.rejects(self.positive + '\n' + suffix)

    def test_matrix_and_control_selection_cannot_shrink_qualification(self):
        for kind in ('count', 'validity', 'size', 'offset', 'duplicate'):
            m = copy.deepcopy(model())
            if kind == 'count': m['cases'].pop()
            if kind == 'validity': m['cases'][8]['expected_valid'] = True
            if kind == 'size': m['cases'][0]['expected_packet_bytes'][1] += 4
            if kind == 'offset': m['cases'][0]['offsets'][1] = 0
            if kind == 'duplicate': m['cases'][1]['id'] = m['cases'][0]['id']
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                validate_log(self.positive, m, 'esp32', returncode=0, timed_out=False, interrupted=False)
        with self.assertRaises(ValueError): self.check_log(control='register-open')
        with self.assertRaises(ValueError): self.check_log(target='esp32c3')


if __name__ == '__main__': unittest.main()
