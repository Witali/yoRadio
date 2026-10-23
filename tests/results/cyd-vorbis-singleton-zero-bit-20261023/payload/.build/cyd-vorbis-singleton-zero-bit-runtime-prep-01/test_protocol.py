"""Host-only finite protocol/reference/sealing controls; synthetic logs are not decoder output."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import protocol as p
from prepare_runtime import seal_controller
from reference_binding import qualification_gate

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / '.build/cyd-vorbis-singleton-zero-bit-generated-01'
MATRIX_SHA = '1f57c45bec6fa558b2948fb094276b7f936eb20f394d760c1fd501973bb8b1ad'


def event(kind, **fields):
    return p.PREFIX + kind + ' ' + ' '.join(str(k) + '=' + str(v) for k, v in fields.items())


def synthetic_transcript(contract):
    model = contract['model']
    lines = [event('BEGIN', contract=contract['contract_sha256'], cases=8, packets=112, coordinator=0),
             event('WORKER', core=1, priority=3, configured_stack=16384)]
    for index, case in enumerate(model['cases']):
        lines.append(event('OPEN', case=index, id=case['id'], checked_rc=0, checked_handle=1, core=1))
        total = 0
        for packet in range(14):
            frames = case['frames'][packet]
            raw = b'\x01\x00\xfe\xff' * frames  # Independent explicit left+1/right-2 samples.
            size = case['sizes'][packet]
            lines.append(event('PACKET', case=index, packet=packet, size=size, checked_rc=0, checked_consumed=size,
                expected_pcm=len(raw), checked_pcm=len(raw), checked_rate=case['rate'], checked_channels=2,
                checked_bits=16, checked_canary=1, transition=case['transitions'][packet], nz_l=frames, nz_r=frames, core=1))
            lines.append(event('PCM_HEX', case=index, packet=packet, bytes=len(raw), core=1, hex=raw.hex()))
            total += frames
        lines.append(event('CLOSE', case=index, checked_rc=0, core=1))
        lines.append(event('CASE', case=index, id=case['id'], packets=14, pcm=case['total_pcm'],
                           nz_l=total, nz_r=total, transitions_mask=15, core=1))
    lines.append(event('COMPLETE', cases=8, packets=112, pcm=225280, cases_mask=255, core=1))
    return '\n'.join(lines) + '\n'


class FullEightProtocolControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = (SOURCE / 'matrix.json').read_bytes()
        p.need(hashlib.sha256(raw).hexdigest() == MATRIX_SHA, 'immutable_full8_test_source')
        cls.matrix = json.loads(raw)
        cls.temporary = tempfile.TemporaryDirectory(prefix='zero8-protocol-controls-', dir=ROOT / '.build')
        base = Path(cls.temporary.name).resolve()
        p.need(base.parent == ROOT / '.build', 'bounded_control_temporary_directory')
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.manifests = []
        for group, cases in (('original4', cls.matrix['cases'][:4]), ('zero4', cls.matrix['cases'][4:])):
            root = base / group
            for case in cases:
                for kind in ('identification', 'setup', 'audio'):
                    destination = root / case[kind]
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes((SOURCE / case[kind]).read_bytes())
            path = root / 'matrix.json'
            path.write_text(json.dumps(dict(cases=cases)) + '\n', encoding='utf-8')
            cls.manifests.append(dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        cls.contract = p.load_contract(cls.manifests)
        cls.log = synthetic_transcript(cls.contract)

    def validate(self, text):
        return p.validate_log(text, self.contract, returncode=0, timed_out=False, interrupted=False,
                              manifest_hashes=[r['sha256'] for r in self.manifests])

    def change(self, kind, case, packet, old, new):
        lines = self.log.splitlines()
        choices = [i for i, line in enumerate(lines) if line.startswith(p.PREFIX + kind + ' ') and
                   'case=' + str(case) in line.split() and (packet is None or 'packet=' + str(packet) in line.split())]
        self.assertEqual(len(choices), 1)
        index = choices[0]
        self.assertIn(old, lines[index].split())
        lines[index] = ' '.join(new if item == old else item for item in lines[index].split(' '))
        return '\n'.join(lines) + '\n'

    def rejected(self, text, reason):
        with self.assertRaisesRegex(RuntimeError, reason): self.validate(text)

    def test_complete8_original_then_zero_full_accounting(self):
        model = self.contract['model']
        self.assertEqual(tuple(c['id'] for c in model['cases']), p.CASE_IDS)
        self.assertEqual([c['source_index'] for c in model['cases']], [0] * 4 + [1] * 4)
        self.assertTrue(all(c['channels'] == 2 and c['rate'] == 192000 for c in model['cases']))
        self.assertTrue(all(set(c['transitions'][1:]) == {0, 1, 2, 3} for c in model['cases']))
        observed = self.validate(self.log)
        self.assertEqual((observed['cases'], observed['decoded_packets'], observed['pcm'],
                          observed['protocol_lines'], observed['case_mask']), (8, 112, 225280, 251, 255))
        self.assertEqual([len(row['pcm']) for row in observed['case_pcm']], [28160] * 8)

    def test_reject_reversed_original_and_zero_groups(self):
        with self.assertRaisesRegex(RuntimeError, 'exact complete8 original4 then zero4'):
            p.load_contract(self.manifests[::-1])

    def test_reject_single_partial_matrix(self):
        with self.assertRaisesRegex(RuntimeError, 'two source matrices required'):
            p.load_contract(self.manifests[:1])

    def test_reject_three_case_subset_before_raw_reads(self):
        path = Path(self.temporary.name) / 'subset.json'
        raw = json.dumps(dict(cases=self.matrix['cases'][:3])).encode()
        path.write_bytes(raw)
        with self.assertRaisesRegex(RuntimeError, 'four unchanged cases'):
            p.load_contract([dict(path=str(path), sha256=hashlib.sha256(raw).hexdigest()), self.manifests[1]])

    def test_reject_wrong_source_SHA(self):
        with self.assertRaisesRegex(RuntimeError, 'source manifest SHA'):
            p.load_contract([dict(path=self.manifests[0]['path'], sha256='0' * 64), self.manifests[1]])

    def test_reject_partial_input_consumption(self):
        size = self.contract['model']['cases'][0]['sizes'][1]
        self.rejected(self.change('PACKET', 0, 1, f'checked_consumed={size}', f'checked_consumed={size - 1}'), 'checked_consumed')

    def test_reject_wrong_public_channels(self):
        self.rejected(self.change('PACKET', 0, 1, 'checked_channels=2', 'checked_channels=1'), 'checked_channels')

    def test_reject_wrong_public_rate(self):
        self.rejected(self.change('PACKET', 0, 1, 'checked_rate=192000', 'checked_rate=48000'), 'checked_rate')

    def test_reject_wrong_public_bits(self):
        self.rejected(self.change('PACKET', 0, 1, 'checked_bits=16', 'checked_bits=32'), 'checked_bits')

    def test_reject_canary_damage(self):
        self.rejected(self.change('PACKET', 0, 1, 'checked_canary=1', 'checked_canary=0'), 'checked_canary')

    def test_reject_worker_core_change(self):
        self.rejected(self.change('PACKET', 0, 1, 'core=1', 'core=0'), 'core')

    def test_reject_zero_or_wrong_channel_count(self):
        self.rejected(self.change('PACKET', 0, 1, 'nz_r=128', 'nz_r=0'), 'nonzero each output channel')
        self.rejected(self.change('PACKET', 0, 1, 'nz_l=128', 'nz_l=64'), 'nonzero observations disagree')

    def test_reject_nonzero_primer(self):
        self.rejected(self.change('PACKET', 0, 0, 'nz_l=0', 'nz_l=1'), 'nonzero each output channel')

    def test_reject_wrong_PCM_size(self):
        self.rejected(self.change('PACKET', 0, 1, 'checked_pcm=512', 'checked_pcm=508'), 'checked_pcm')

    def test_reject_missing_transition(self):
        self.rejected(self.change('CASE', 0, None, 'transitions_mask=15', 'transitions_mask=7'), 'transitions_mask')

    def test_reject_truncated_PCM_hex(self):
        lines = self.log.splitlines()
        index = next(i for i, line in enumerate(lines) if line.startswith(p.PREFIX + 'PCM_HEX case=0 packet=1 '))
        lines[index] = lines[index][:-2]
        self.rejected('\n'.join(lines) + '\n', 'PCM hex length/alphabet')

    def test_reject_missing_complete(self):
        self.rejected('\n'.join(self.log.splitlines()[:-1]) + '\n', 'missing protocol event')

    def test_reject_extra_protocol_event(self):
        self.rejected(self.log + self.log.splitlines()[-1] + '\n', 'extra/missing/duplicate protocol')

    def test_reject_declared_packet_PCM_metadata_change(self):
        case = copy.deepcopy(self.matrix['cases'][0])
        case['expected_packet_s16le_bytes'][1] += 4
        with self.assertRaisesRegex(RuntimeError, 'declared frame/PCM counts'):
            p.inspect_case(case, SOURCE, 0)


def mixed_qualification():
    q = dict(schema='public-vorbis-new-format-reference-qualification-v1', profile='zero8',
        result='XIPH_QUALIFIED_DUAL_NONPASS', completed=True, reference_corpus_qualified=True,
        xiph_reference_qualified=True, dual_reference_qualified=False, original_dual_reference_passed=False,
        native_cause_diagnosed=False, target_executed=False, production_changed=False,
        standard_conformance_qualified=False, full_G6_qualified=False, physical_device=False,
        xiph_cases=8, native_compared=4, native_lookup2_refusals=0, native_packet_decode_failures=4,
        paired_raw_packets=112, expected_pcm_bytes=225280, cases=[])
    for index, name in enumerate(p.CASE_IDS):
        accepted = index >= 4
        q['cases'].append(dict(id='0-' + name, xiph_qualified=True, native_compared=accepted,
            native_lookup2_refusal=False, native_packet_decode_failure=not accepted,
            native_outcome_kind='accepted' if accepted else 'packet_decode_failure_no_PCM',
            native_actual_returncode=0 if accepted else 4294967295, native_cause_diagnosed=False,
            cross_reference_max_abs_error=1 if accepted else None))
    return q


class MixedReferenceControls(unittest.TestCase):
    def test_accept_exact_original4_refused_zero4_accepted(self):
        qualification_gate(mixed_qualification())

    def test_reject_invented_full8_dual_pass(self):
        q = mixed_qualification(); q['dual_reference_qualified'] = True
        with self.assertRaisesRegex(RuntimeError, 'full8 dual pass prohibited'): qualification_gate(q)

    def test_reject_fake_eight_native_comparisons(self):
        q = mixed_qualification(); q['native_compared'] = 8
        with self.assertRaisesRegex(RuntimeError, 'mixed reference classification'): qualification_gate(q)

    def test_reject_relabelling_packet_failure_lookup2_refusal(self):
        q = mixed_qualification(); q['cases'][0]['native_lookup2_refusal'] = True
        with self.assertRaisesRegex(RuntimeError, 'Original4 packet refusals'): qualification_gate(q)

    def test_reject_invented_native_PCM_for_original(self):
        q = mixed_qualification(); q['cases'][0]['cross_reference_max_abs_error'] = 1
        with self.assertRaisesRegex(RuntimeError, 'Original4 packet refusals'): qualification_gate(q)

    def test_reject_zero_native_acceptance_rewritten_as_failure(self):
        q = mixed_qualification(); q['cases'][4]['native_actual_returncode'] = 4294967295
        with self.assertRaisesRegex(RuntimeError, 'Original4 packet refusals'): qualification_gate(q)

    def test_reject_backend_or_OS_cause_attribution(self):
        q = mixed_qualification(); q['cases'][0]['native_cause_diagnosed'] = True
        with self.assertRaisesRegex(RuntimeError, 'Original4 packet refusals'): qualification_gate(q)


class ControllerSealingControls(unittest.TestCase):
    def test_legitimate_doc_file_name_and_wrap_dunders_survive(self):
        text = '"""doc"""\nx="__VALUE__"\ny=__doc__\nz=__file__\nw=__name__\nu="__main__"\nv="__wrap_esp_vorbis_dec_open"\n'
        sealed = seal_controller(text, {'__VALUE__': 'actual'})
        self.assertIn('x="actual"', sealed)
        self.assertIn('y=__doc__', sealed)

    def test_reject_unknown_unsealed_marker(self):
        with self.assertRaisesRegex(RuntimeError, 'unsealed_controller_placeholder'):
            seal_controller('x="__VALUE__"\ny="__UNKNOWN__"\n', {'__VALUE__': 'actual'})

    def test_reject_missing_required_marker(self):
        with self.assertRaisesRegex(RuntimeError, 'controller_marker_missing'):
            seal_controller('x=1\n', {'__VALUE__': 'actual'})

    def test_reject_nonmarker_dunder_replacement(self):
        with self.assertRaisesRegex(RuntimeError, 'invalid_controller_marker'):
            seal_controller('x=__doc__\n', {'__doc__': 'actual'})


if __name__ == '__main__': unittest.main()
