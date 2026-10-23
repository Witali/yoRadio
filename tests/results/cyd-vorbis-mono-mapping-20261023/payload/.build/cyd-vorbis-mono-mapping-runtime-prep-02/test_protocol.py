"""Host-only protocol construction controls; synthetic log bytes are not decoded PCM."""
import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest

import protocol as p

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MATRIX = ROOT / '.build/vorbis-mono-mapping-canonical-check-01/matrix.json'
MATRIX_SHA = '30fad94ec85727030a415f33c544041ed225aae97397b09584a534f7c2636d37'


def event(kind, **fields):
    return p.PREFIX + kind + ' ' + ' '.join(str(key) + '=' + str(value) for key, value in fields.items())


def synthetic_transcript(contract):
    """Independent fixed sample patterns, direct per-channel counts and complete ordering."""
    model = contract['model']
    lines = [event('BEGIN', contract=contract['contract_sha256'], cases=len(model['cases']),
        packets=model['total_packets'], coordinator=0), event('WORKER', core=1, priority=3, configured_stack=16384)]
    for index, c in enumerate(model['cases']):
        lines.append(event('OPEN', case=index, id=c['id'], checked_rc=0, checked_handle=1, core=1))
        left = right = 0
        for packet in range(14):
            count = c['frames'][packet]
            # Every left sample is +1. Stereo right samples are alternating 0/-2.
            samples = []
            for frame in range(count):
                samples.append(1)
                if c['channels'] == 2:
                    samples.append(-2 if frame % 2 else 0)
            pcm = b''.join(struct.pack('<h', value) for value in samples)
            nl, nr = count, count // 2 if c['channels'] == 2 else 0
            lines.append(event('PACKET', case=index, packet=packet, size=c['sizes'][packet], checked_rc=0,
                checked_consumed=c['sizes'][packet], expected_pcm=len(pcm), checked_pcm=len(pcm),
                checked_rate=c['rate'], checked_channels=c['channels'], checked_bits=16,
                checked_canary=1, transition=c['transitions'][packet], core=1, nz_l=nl, nz_r=nr))
            lines.append(event('PCM_HEX', case=index, packet=packet, bytes=len(pcm), core=1, hex=pcm.hex()))
            left += nl; right += nr
        lines.append(event('CLOSE', case=index, checked_rc=0, core=1))
        lines.append(event('CASE', case=index, id=c['id'], packets=14, pcm=c['total_pcm'],
            nz_l=left, nz_r=right, transitions_mask=15, core=1))
    lines.append(event('COMPLETE', cases=len(model['cases']), packets=model['total_packets'], pcm=model['total_pcm'],
        cases_mask=model['case_mask'], core=1))
    return '\n'.join(lines) + '\n'


class MonoProtocolControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = p.load_contract([dict(path=str(MATRIX), sha256=MATRIX_SHA)])
        cls.matrix = json.loads(MATRIX.read_bytes())
        cls.log = synthetic_transcript(cls.contract)

    def validate(self, text):
        return p.validate_log(text, self.contract, returncode=0, timed_out=False, interrupted=False,
                              manifest_hashes=[MATRIX_SHA])

    def change(self, text, kind, case, packet, old, new):
        lines = text.splitlines()
        matches = [i for i, row in enumerate(lines) if row.startswith(p.PREFIX + kind + ' ') and
                   ('case=' + str(case)) in row.split() and
                   (packet is None or ('packet=' + str(packet)) in row.split())]
        self.assertEqual(len(matches), 1)
        index = matches[0]
        self.assertIn(old, lines[index].split())
        lines[index] = ' '.join(new if token == old else token for token in lines[index].split(' '))
        return '\n'.join(lines) + '\n'

    def rejected(self, text, reason):
        with self.assertRaisesRegex(RuntimeError, reason):
            self.validate(text)

    def test_complete21_mixed_channel_model(self):
        model = self.contract['model']
        self.assertEqual((len(model['cases']), model['total_packets'], model['total_pcm'], model['case_mask']),
                         (21, 294, 464640, 2097151))
        self.assertEqual([c['channels'] for c in model['cases']], [1, 2] * 9 + [2, 2, 2])
        self.assertEqual({c['rate'] for c in model['cases']}, {8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000})
        self.assertEqual([c['id'] for c in model['cases'][-3:]],
                         ['coupled-c2-r48000', 'submaps-c2-r48000', 'residue2-c2-r48000'])
        self.assertTrue(all(set(c['transitions'][1:]) == {0, 1, 2, 3} for c in model['cases']))
        observed = self.validate(self.log)
        self.assertEqual((observed['protocol_lines'], observed['cases'], observed['decoded_packets'], observed['pcm']),
                         (654, 21, 294, 464640))
        self.assertEqual([len(c['pcm']) for c in observed['case_pcm']], [14080, 28160] * 9 + [28160] * 3)

    def test_mono_odd_frame_count_no_second_channel(self):
        self.assertEqual(p.channel_nonzero(struct.pack('<hhh', 1, 0, -1), 1), dict(nz_l=2, nz_r=0))

    def test_stereo_interleaving_independent_channel_counts(self):
        self.assertEqual(p.channel_nonzero(struct.pack('<hhhh', 1, 0, 0, -2), 2), dict(nz_l=1, nz_r=1))

    def test_primer_has_no_output_channels(self):
        self.assertEqual(p.channel_nonzero(b'', 1), dict(nz_l=0, nz_r=0))
        self.assertEqual(p.channel_nonzero(b'', 2), dict(nz_l=0, nz_r=0))

    def test_reject_partial_frames(self):
        for raw, channels in ((b'x', 1), (b'xx', 2), (b'xxx', 2)):
            with self.subTest(channels=channels, length=len(raw)):
                with self.assertRaisesRegex(RuntimeError, 'complete mono/stereo PCM16 frames'):
                    p.channel_nonzero(raw, channels)

    def test_reject_unsupported_or_boolean_channels(self):
        for channels in (0, 3, True):
            with self.subTest(channels=channels):
                with self.assertRaisesRegex(RuntimeError, 'complete mono/stereo PCM16 frames'):
                    p.channel_nonzero(b'', channels)

    def test_reject_mono_relabelled_stereo(self):
        self.rejected(self.change(self.log, 'PACKET', 0, 1, 'checked_channels=1', 'checked_channels=2'), 'checked_channels')

    def test_reject_stereo_relabelled_mono(self):
        self.rejected(self.change(self.log, 'PACKET', 1, 1, 'checked_channels=2', 'checked_channels=1'), 'checked_channels')

    def test_reject_fabricated_mono_right_channel(self):
        self.rejected(self.change(self.log, 'PACKET', 0, 1, 'nz_r=0', 'nz_r=1'), 'absent mono right channel')

    def test_reject_old_stride4_count_for_mono(self):
        self.rejected(self.change(self.log, 'PACKET', 0, 1, 'nz_l=128', 'nz_l=64'), 'nonzero observations disagree')

    def test_reject_silent_stereo_right_channel(self):
        self.rejected(self.change(self.log, 'PACKET', 1, 1, 'nz_r=64', 'nz_r=0'), 'nonzero each actual channel')

    def test_reject_silent_mono_actual_channel(self):
        self.rejected(self.change(self.log, 'PACKET', 0, 1, 'nz_l=128', 'nz_l=0'), 'nonzero each actual channel')

    def test_reject_silent_stereo_left_channel(self):
        self.rejected(self.change(self.log, 'PACKET', 1, 1, 'nz_l=128', 'nz_l=0'), 'nonzero each actual channel')

    def test_reject_primer_nonzero(self):
        self.rejected(self.change(self.log, 'PACKET', 0, 0, 'nz_l=0', 'nz_l=1'), 'nonzero each actual channel')

    def test_reject_partial_input_consumption(self):
        self.rejected(self.change(self.log, 'PACKET', 0, 1, 'checked_consumed=5', 'checked_consumed=4'), 'checked_consumed')

    def test_reject_wrong_actual_rate(self):
        self.rejected(self.change(self.log, 'PACKET', 0, 1, 'checked_rate=8000', 'checked_rate=48000'), 'checked_rate')

    def test_reject_canary_damage(self):
        self.rejected(self.change(self.log, 'PACKET', 0, 1, 'checked_canary=1', 'checked_canary=0'), 'checked_canary')

    def test_reject_worker_core_migration(self):
        self.rejected(self.change(self.log, 'PACKET', 0, 1, 'core=1', 'core=0'), 'core')

    def test_reject_stereo_sized_mono_output(self):
        self.rejected(self.change(self.log, 'PACKET', 0, 1, 'checked_pcm=256', 'checked_pcm=512'), 'checked_pcm')

    def test_reject_truncated_pcm(self):
        lines = self.log.splitlines()
        index = next(i for i, row in enumerate(lines) if row.startswith(p.PREFIX + 'PCM_HEX case=0 packet=1 '))
        lines[index] = lines[index][:-2]
        self.rejected('\n'.join(lines) + '\n', 'PCM hex length/alphabet')

    def test_reject_missing_complete(self):
        self.rejected('\n'.join(self.log.splitlines()[:-1]) + '\n', 'missing protocol event')

    def test_reject_duplicate_pcm_event(self):
        lines = self.log.splitlines()
        lines.insert(6, lines[5])
        self.rejected('\n'.join(lines) + '\n', 'event syntax/order')

    def test_reject_case_total_count_corruption(self):
        self.rejected(self.change(self.log, 'CASE', 0, None, 'nz_r=0', 'nz_r=1'), 'CASE nz_r')

    def test_reject_missing_transition(self):
        self.rejected(self.change(self.log, 'CASE', 0, None, 'transitions_mask=15', 'transitions_mask=7'), 'transitions_mask')

    def test_reject_metadata_only_channel_change(self):
        case = copy.deepcopy(self.matrix['cases'][0])
        case['channels'] = 2
        with self.assertRaisesRegex(RuntimeError, 'identification fields'):
            p.inspect_case(case, MATRIX.parent, 0)

    def test_reject_declared_pcm_counts_from_stereo(self):
        case = copy.deepcopy(self.matrix['cases'][0])
        case['expected_packet_s16le_bytes'] = [2 * value for value in case['expected_packet_s16le_bytes']]
        with self.assertRaisesRegex(RuntimeError, 'declared frame/PCM counts'):
            p.inspect_case(case, MATRIX.parent, 0)

    def test_reject_disagreeing_declared_frame_fields(self):
        case = copy.deepcopy(self.matrix['cases'][0])
        case['expected_packet_frames'][1] += 1
        with self.assertRaisesRegex(RuntimeError, 'declared frame/PCM counts'):
            p.inspect_case(case, MATRIX.parent, 0)

    def test_reject_wrong_matrix_sha(self):
        with self.assertRaisesRegex(RuntimeError, 'source manifest SHA'):
            p.load_contract([dict(path=str(MATRIX), sha256='0' * 64)])

    def test_reject_two_matrix_partial_selection(self):
        with self.assertRaisesRegex(RuntimeError, 'one complete mono21 source matrix required'):
            p.load_contract([dict(path=str(MATRIX), sha256=MATRIX_SHA)] * 2)

    def test_reject_complete20_subset_before_raw_reads(self):
        subset = copy.deepcopy(self.matrix)
        subset['cases'] = subset['cases'][:-1]
        raw = (json.dumps(subset) + '\n').encode()
        with tempfile.TemporaryDirectory(prefix='mono21-protocol-controls-', dir=ROOT / '.build') as directory:
            path = Path(directory) / 'matrix.json'
            path.write_bytes(raw)
            with self.assertRaisesRegex(RuntimeError, 'complete21 source cases required'):
                p.load_contract([dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest())])


if __name__ == '__main__':
    unittest.main()
