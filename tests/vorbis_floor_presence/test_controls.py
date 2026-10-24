"""Root-only host controls: synthetic PCM/logs never establish codec validity."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import struct
import unittest

import pcm_witness
import protocol as p

MATRIX = None
MATRIX_SHA = None


def event(kind, **fields):
    return p.PREFIX + kind + ' ' + ' '.join(str(k) + '=' + str(v) for k, v in fields.items())


def synthetic_packet(case, packet):
    witness = case['presence_witnesses'][packet]; result = []
    for frame in range(witness['frames']):
        for channel in range(case['channels']):
            silent = any(first <= frame < stop for first, stop in witness['channel_zero_spans'][channel])
            result.append(0 if silent else (-1 if channel else 1))
    return b''.join(struct.pack('<h', value) for value in result)


def transcript(contract):
    model = contract['model']; lines = [event('BEGIN', contract=contract['contract_sha256'],
        cases=39, packets=546, coordinator=0), event('WORKER', core=1, priority=3, configured_stack=16384)]
    for index, case in enumerate(model['cases']):
        lines.append(event('OPEN', case=index, id=case['id'], checked_rc=0, checked_handle=1, core=1))
        sums = dict(nz_l=0, nz_r=0)
        for packet in range(14):
            raw = synthetic_packet(case, packet); nz = p.channel_nonzero(raw, case['channels'])
            lines.append(event('PACKET', case=index, packet=packet, size=case['sizes'][packet], checked_rc=0,
                checked_consumed=case['sizes'][packet], expected_pcm=len(raw), checked_pcm=len(raw),
                checked_rate=case['rate'], checked_channels=case['channels'], checked_bits=16,
                checked_canary=1, transition=case['transitions'][packet], core=1, **nz))
            lines.append(event('PCM_HEX', case=index, packet=packet, bytes=len(raw), core=1, hex=raw.hex()))
            for key in sums: sums[key] += nz[key]
        lines.append(event('CLOSE', case=index, checked_rc=0, core=1))
        lines.append(event('CASE', case=index, id=case['id'], packets=14, pcm=case['total_pcm'],
            transitions_mask=15, core=1, **sums))
    lines.append(event('COMPLETE', cases=39, packets=546, pcm=971520, cases_mask=549755813887, core=1))
    return '\n'.join(lines) + '\n'


class PresenceControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(MATRIX.read_bytes())
        cls.contract = p.load_contract([dict(path=str(MATRIX), sha256=MATRIX_SHA)])
        cls.log = transcript(cls.contract)

    def validate(self, log):
        return p.validate_log(log, self.contract, returncode=0, timed_out=False, interrupted=False,
                              manifest_hashes=[MATRIX_SHA])

    def test_full39_scope_and_uint64_mask(self):
        result = self.validate(self.log)
        self.assertEqual((result['cases'], result['decoded_packets'], result['pcm'], result['protocol_lines'], result['case_mask']),
            (39, 546, 971520, 1212, 549755813887))
        self.assertGreater(result['case_mask'], 0xffffffff)

    def test_separate_constant_all_absent_cases(self):
        rows = [c for c in self.source['cases'] if c['constant_all_absent_silence_witness']]
        self.assertEqual(len(rows), 9)
        for case in rows:
            witnesses = pcm_witness.derive(case)
            self.assertTrue(all(all(spans == [[0, row['frames']]] for spans in row['channel_zero_spans'])
                for row in witnesses[1:]))
            self.assertEqual(pcm_witness.stream(bytes(case['expected_s16le_bytes']), case)['always_absent_channels'],
                             [True] * case['channels'])

    def test_separate_constant_mixed_channel_witnesses(self):
        rows = [c for c in self.source['cases'] if c['channels'] == 2 and c['schedule_kind'] == 'constant' and c['schedule'][0] in (1, 2)]
        self.assertEqual(len(rows), 12)
        self.assertTrue(all(sum(c['always_absent_channel_silence_witness']) == 1 for c in rows))

    def test_reject_always_absent_channel_leak(self):
        case = self.contract['model']['cases'][7]  # r0 uncoupled mask01.
        raw = bytearray(synthetic_packet(case, 1)); raw[2] = 1
        with self.assertRaisesRegex(RuntimeError, 'guaranteed_silent_frame_span_channel:1'):
            pcm_witness.packet(raw, 2, case['presence_witnesses'][1])

    def test_reject_all_absent_leak(self):
        case = self.contract['model']['cases'][0]; raw = bytearray(synthetic_packet(case, 1)); raw[-1] = 1
        with self.assertRaisesRegex(RuntimeError, 'guaranteed_silent_frame_span_channel:0'):
            pcm_witness.packet(raw, 1, case['presence_witnesses'][1])

    def test_reject_present_channel_silenced(self):
        case = self.contract['model']['cases'][1]; raw = bytes(case['pcm'][1])
        with self.assertRaisesRegex(RuntimeError, 'predeclared_packet_channel_zero_nonzero:0'):
            pcm_witness.packet(raw, 1, case['presence_witnesses'][1])

    def test_exact_short_long_tail_and_long_short_prefix(self):
        tails, prefixes = [], []
        for case in self.contract['model']['cases']:
            for packet, row in enumerate(case['presence_witnesses']):
                for channel, spans in enumerate(row['channel_zero_spans']):
                    if spans == [[128, 576]]: tails.append((case, packet, channel))
                    if spans == [[0, 448]]: prefixes.append((case, packet, channel))
        self.assertTrue(tails and prefixes)
        for rows in (tails, prefixes):
            case, packet, channel = rows[0]; raw = bytearray(synthetic_packet(case, packet))
            first = case['presence_witnesses'][packet]['channel_zero_spans'][channel][0][0]
            raw[(first * case['channels'] + channel) * 2] = 1
            with self.assertRaisesRegex(RuntimeError, 'guaranteed_silent_frame_span_channel:'):
                pcm_witness.packet(raw, case['channels'], case['presence_witnesses'][packet])

    def test_current_absence_still_requires_overlap_nonzero(self):
        pairs = [(c, packet) for c in self.contract['model']['cases'] for packet in range(1, 14)
            if not c['floor_masks'][packet] and c['floor_masks'][packet - 1]]
        self.assertTrue(pairs)
        case, packet = pairs[0]
        with self.assertRaisesRegex(RuntimeError, 'predeclared_packet_channel_zero_nonzero:'):
            pcm_witness.packet(bytes(case['pcm'][packet]), case['channels'], case['presence_witnesses'][packet])

    def test_reject_witness_metadata_tampering(self):
        case = copy.deepcopy(self.source['cases'][0]); case['packet_PCM_witnesses'][1]['channel_zero_spans'][0] = []
        with self.assertRaisesRegex(RuntimeError, 'serialized_PCM_witnesses_match_independent_geometry'):
            pcm_witness.derive(case)

    def test_reject_schedule_metadata_tampering(self):
        case = copy.deepcopy(self.source['cases'][0]); case['schedule'][1] = 1
        with self.assertRaisesRegex(RuntimeError, 'serialized_PCM_witnesses_match_independent_geometry'):
            pcm_witness.derive(case)

    def test_reject_partial_PCM16_frame(self):
        case = self.contract['model']['cases'][1]
        with self.assertRaisesRegex(RuntimeError, 'witness_full_PCM16_channel_frames'):
            pcm_witness.packet(b'\0', 1, case['presence_witnesses'][1])

    def test_reject_32bit_case_mask(self):
        with self.assertRaisesRegex(RuntimeError, 'COMPLETE cases_mask'):
            self.validate(self.log.replace('cases_mask=549755813887', 'cases_mask=4294967295'))

    def test_reject_missing_high_case_bit(self):
        with self.assertRaisesRegex(RuntimeError, 'COMPLETE cases_mask'):
            self.validate(self.log.replace('cases_mask=549755813887', 'cases_mask=274877906943'))

    def test_reject_missing_complete(self):
        with self.assertRaisesRegex(RuntimeError, 'missing protocol event'):
            self.validate('\n'.join(self.log.splitlines()[:-1]) + '\n')

    def test_reject_worker_core_change(self):
        with self.assertRaisesRegex(RuntimeError, 'WORKER core'):
            self.validate(self.log.replace('WORKER core=1', 'WORKER core=0', 1))

    def test_reject_phantom_mono_right(self):
        with self.assertRaisesRegex(RuntimeError, 'nonzero observations disagree'):
            self.validate(self.log.replace('core=1 nz_l=0 nz_r=0', 'core=1 nz_l=0 nz_r=1', 1))

    def test_reject_nonterminal_process_fact(self):
        with self.assertRaisesRegex(RuntimeError, 'process incomplete'):
            p.validate_log(self.log, self.contract, returncode=1, timed_out=False, interrupted=False,
                           manifest_hashes=[MATRIX_SHA])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--matrix', type=Path, required=True); parser.add_argument('--matrix-sha256', required=True)
    args, remaining = parser.parse_known_args(); MATRIX = args.matrix.resolve(); MATRIX_SHA = args.matrix_sha256
    if hashlib.sha256(MATRIX.read_bytes()).hexdigest() != MATRIX_SHA: raise RuntimeError('reviewed_actual_matrix_SHA')
    unittest.main(argv=[__file__, *remaining])
