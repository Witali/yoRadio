"""Synthetic host controls only; no fixture/capture/reference I/O or processes."""
import copy
from pathlib import Path
import struct
import unittest

from binding_identity import RELOCATED_HELPERS, verify_relocated_binding
from compare_capture8 import transition_counts
from pcm_metrics import compare
from policy8 import CASE_IDS, FRAMES, GROUPS, bounded_policy, relations
from reference_binding import qualification_gate

PACKETS = [n * 4 for n in FRAMES]
MODES = [0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0]
PCM = struct.pack('<hh', 100, -200) * 7040
COUNTS = {name: [n, n] for name, n in (('SS', 512), ('SL', 1728), ('LL', 3072), ('LS', 1728))}


def fixture():
    metric = compare(PCM, PCM, PACKETS)
    rows = []
    for i, name in enumerate(CASE_IDS):
        native = i >= 4
        rows.append(dict(case=i, id=name, rate=192000, channels=2, bits=16, frames=list(FRAMES),
            packet_bytes=PACKETS.copy(), pcm_bytes=28160, native_compared=native,
            native_packet_decode_failure=not native, native_lookup2_refusal=False,
            native_cause_diagnosed=False, native_actual_returncode=0 if native else 4294967295,
            references={decoder: dict(comparison=copy.deepcopy(metric), reference_transition_nonzero=copy.deepcopy(COUNTS),
                target_transition_nonzero=copy.deepcopy(COUNTS)) for decoder in (('libvorbis', 'vorbis') if native else ('libvorbis',))}))
    values = {name: PCM for name in CASE_IDS}
    return rows, dict(xiph=relations(values), target=relations(values))


def qualification():
    q = dict(schema='public-vorbis-new-format-reference-qualification-v1', profile='zero8',
        result='XIPH_QUALIFIED_DUAL_NONPASS', completed=True, reference_corpus_qualified=True,
        xiph_reference_qualified=True, dual_reference_qualified=False, original_dual_reference_passed=False,
        native_cause_diagnosed=False, target_executed=False, production_changed=False,
        standard_conformance_qualified=False, full_G6_qualified=False, physical_device=False,
        xiph_cases=8, native_compared=4, native_lookup2_refusals=0, native_packet_decode_failures=4,
        paired_raw_packets=112, expected_pcm_bytes=225280, cases=[])
    for i, name in enumerate(CASE_IDS):
        accepted = i >= 4
        q['cases'].append(dict(id='0-' + name, xiph_qualified=True, native_compared=accepted,
            native_lookup2_refusal=False, native_packet_decode_failure=not accepted,
            native_outcome_kind='accepted' if accepted else 'packet_decode_failure_no_PCM',
            native_actual_returncode=0 if accepted else 4294967295, native_cause_diagnosed=False,
            cross_reference_max_abs_error=1 if accepted else None))
    return q


class MixedPolicyControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.rows, cls.groups = fixture()

    def values(self): return copy.deepcopy(self.rows), copy.deepcopy(self.groups)

    def test_full_mixed12_pass_keeps_original_host_dual_nonpass(self):
        policy, passed = bounded_policy(*self.values())
        self.assertTrue(passed)
        self.assertEqual(policy['required_reference_comparisons'], 12)
        self.assertFalse(policy['full8_dual_reference_passed'])
        self.assertFalse(policy['prior_numeric_NONPASS_requalified'])
        self.assertEqual(policy['reference_scopes'], dict(libvorbis='all8', vorbis='new_zero4_only'))

    def test_exact_fixed2_accepted_and3_rejected(self):
        for error, expected in ((2, True), (3, False)):
            rows, groups = self.values()
            rows[7]['references']['vorbis']['comparison']['zero_lag_direct_LR']['max_abs_error'] = error
            self.assertEqual(bounded_policy(rows, groups)[1], expected)

    def test_original4_xiph_failure_is_not_hidden_by_new4(self):
        rows, groups = self.values()
        rows[0]['references']['libvorbis']['comparison']['zero_lag_direct_LR']['max_abs_error'] = 3
        policy, passed = bounded_policy(rows, groups)
        self.assertFalse(passed); self.assertFalse(policy['bounded_original4_Xiph'])
        self.assertTrue(policy['bounded_new_zero4_both_references'])

    def test_new_native_failure_is_not_hidden_by_xiph_pass(self):
        rows, groups = self.values()
        rows[4]['references']['vorbis']['comparison']['zero_lag_direct_LR']['max_abs_error'] = 3
        policy, passed = bounded_policy(rows, groups)
        self.assertFalse(passed); self.assertTrue(policy['bounded_by_reference']['libvorbis_all8'])
        self.assertFalse(policy['bounded_by_reference']['vorbis_zero4'])

    def test_missing_or_reordered_case_rejected(self):
        for selected in (self.rows[:4], self.rows[:-1], list(reversed(self.rows))):
            with self.subTest(size=len(selected)):
                with self.assertRaises(RuntimeError): bounded_policy(selected, self.groups)

    def test_invented_original_native_pcm_rejected(self):
        rows, groups = self.values()
        rows[0]['references']['vorbis'] = copy.deepcopy(rows[4]['references']['vorbis'])
        with self.assertRaises(RuntimeError): bounded_policy(rows, groups)

    def test_missing_new_native_pcm_rejected(self):
        rows, groups = self.values(); del rows[7]['references']['vorbis']
        with self.assertRaises(RuntimeError): bounded_policy(rows, groups)

    def test_refusal_classification_or_cause_claim_rejected(self):
        for field, value in (('native_compared', True), ('native_packet_decode_failure', False),
                             ('native_lookup2_refusal', True), ('native_actual_returncode', 0),
                             ('native_cause_diagnosed', True)):
            rows, groups = self.values(); rows[0][field] = value
            with self.subTest(field=field):
                with self.assertRaises(RuntimeError): bounded_policy(rows, groups)

    def test_true_stereo_geometry_required(self):
        for field, value in (('channels', 1), ('rate', 48000), ('bits', 24), ('pcm_bytes', 28156)):
            rows, groups = self.values(); rows[4][field] = value
            with self.subTest(field=field):
                with self.assertRaises(RuntimeError): bounded_policy(rows, groups)

    def test_last_packet_and_zero_primer_boundaries_required(self):
        for packet in (0, 13):
            rows, groups = self.values()
            rows[0]['references']['libvorbis']['comparison']['packets'][packet]['bytes'] += 4
            with self.subTest(packet=packet):
                with self.assertRaises(RuntimeError): bounded_policy(rows, groups)

    def test_missing_packet_or_channel_cannot_pass(self):
        for key in ('packets', 'channels'):
            rows, groups = self.values(); rows[6]['references']['vorbis']['comparison'][key].pop()
            with self.subTest(key=key):
                with self.assertRaises(RuntimeError): bounded_policy(rows, groups)

    def test_silent_channel_rejects_numeric_pass(self):
        rows, groups = self.values()
        rows[2]['references']['libvorbis']['comparison']['channels'][1]['target_nonzero_samples'] = 0
        self.assertFalse(bounded_policy(rows, groups)[1])

    def test_missing_transition_activity_rejects_numeric_pass(self):
        rows, groups = self.values(); rows[7]['references']['vorbis']['target_transition_nonzero']['LS'][1] = 0
        self.assertFalse(bounded_policy(rows, groups)[1])

    def test_each_declared_equality_is_required(self):
        for decoder in ('target', 'xiph'):
            rows, groups = self.values()
            groups[decoder][3].update(observed_byte_equal=False, expected_relation_observed=False)
            with self.subTest(decoder=decoder): self.assertFalse(bounded_policy(rows, groups)[1])

    def test_missing_or_invented_equality_group_rejected(self):
        for field in ('missing', 'wrongpair'):
            rows, groups = self.values()
            if field == 'missing': groups['target'].pop()
            else: groups['target'][0]['cases'] = [CASE_IDS[0], CASE_IDS[5]]
            with self.subTest(field=field):
                with self.assertRaises(RuntimeError): bounded_policy(rows, groups)

    def test_relations_use_complete_bytes_including_last_sample(self):
        values = {name: PCM for name in CASE_IDS}
        values[CASE_IDS[4]] = PCM[:-2] + b'\x01\x00'
        observed = relations(values)
        self.assertFalse(observed[0]['observed_byte_equal'])
        self.assertTrue(all(row['observed_byte_equal'] for row in observed[1:]))

    def test_relations_reject_subset_and_trim(self):
        for values in ({name: PCM for name in CASE_IDS[:-1]}, {name: PCM[:-4] for name in CASE_IDS}):
            with self.assertRaises(RuntimeError): relations(values)

    def test_changed_bound_or_boolean_bound_rejected(self):
        for bound in (1, 3, True):
            with self.subTest(bound=bound):
                with self.assertRaises(RuntimeError): bounded_policy(self.rows, self.groups, bound)


class MixedReferenceControls(unittest.TestCase):
    def test_exact_mixed_classification_accepted(self): qualification_gate(qualification())

    def test_full8_dual_or_native_pass_not_invented(self):
        for field in ('dual_reference_qualified', 'original_dual_reference_passed'):
            q = qualification(); q[field] = True
            with self.assertRaises(RuntimeError): qualification_gate(q)

    def test_packet_refusal_not_lookup2_or_os_cause(self):
        for field in ('native_lookup2_refusal', 'native_cause_diagnosed'):
            q = qualification(); q['cases'][0][field] = True
            with self.assertRaises(RuntimeError): qualification_gate(q)

    def test_native_original_output_or_wrong_returncode_rejected(self):
        for field, value in (('native_compared', True), ('native_actual_returncode', 1), ('cross_reference_max_abs_error', 0)):
            q = qualification(); q['cases'][0][field] = value
            with self.assertRaises(RuntimeError): qualification_gate(q)

    def test_new_reference_error3_rejected(self):
        q = qualification(); q['cases'][7]['cross_reference_max_abs_error'] = 3
        with self.assertRaises(RuntimeError): qualification_gate(q)

    def test_missing_case_or_wrong_total_rejected(self):
        q = qualification(); q['cases'].pop()
        with self.assertRaises(RuntimeError): qualification_gate(q)
        q = qualification(); q['native_compared'] = 8
        with self.assertRaises(RuntimeError): qualification_gate(q)


class BindingRelocationControls(unittest.TestCase):
    def fixture(self):
        runtime, here = Path('synthetic-runtime').resolve(), Path('synthetic-numeric').resolve()
        hashes = {name: str(i + 1) * 64 for i, name in enumerate(RELOCATED_HELPERS)}
        saved = dict(cases=[dict(native_compared=False)], external_reference_tool_identities=[dict(sha256='f' * 64)],
            proof_facts=[dict(path=str(runtime / name), bytes=100 + i, sha256=hashes[name])
                         for i, name in enumerate(RELOCATED_HELPERS)] +
                        [dict(path=str(Path('shared-proof.json').resolve()), bytes=123, sha256='a' * 64)])
        replay = copy.deepcopy(saved)
        for i, name in enumerate(RELOCATED_HELPERS): replay['proof_facts'][i]['path'] = str(here / name)
        return saved, replay, runtime, here, hashes

    def test_exact_three_samebyte_moves_accepted(self): self.assertTrue(verify_relocated_binding(*self.fixture()))

    def test_one_helper_content_change_rejected(self):
        args = self.fixture(); args[1]['proof_facts'][0]['sha256'] = '0' * 64
        with self.assertRaises(RuntimeError): verify_relocated_binding(*args)

    def test_undeclared_shared_fact_move_rejected(self):
        args = self.fixture(); args[1]['proof_facts'][3]['path'] = str(Path('different-proof.json').resolve())
        with self.assertRaises(RuntimeError): verify_relocated_binding(*args)

    def test_missing_or_duplicate_fact_rejected(self):
        for duplicate in (False, True):
            args = self.fixture()
            if duplicate: args[1]['proof_facts'].append(copy.deepcopy(args[1]['proof_facts'][0]))
            else: args[1]['proof_facts'].pop()
            with self.assertRaises(RuntimeError): verify_relocated_binding(*args)

    def test_missing_required_helper_rejected(self):
        args = self.fixture(); args[0]['proof_facts'].pop(0)
        with self.assertRaises(RuntimeError): verify_relocated_binding(*args)

    def test_semantic_or_external_identity_change_rejected(self):
        for field in ('cases', 'external_reference_tool_identities'):
            args = self.fixture(); args[1][field] = []
            with self.assertRaises(RuntimeError): verify_relocated_binding(*args)


class TransitionControls(unittest.TestCase):
    def offsets(self):
        out = [0]
        for size in PACKETS: out.append(out[-1] + size)
        return out

    def test_known_all_four_transition_frame_counts_per_channel(self):
        self.assertEqual(transition_counts(PCM, dict(channels=2, pcm=PACKETS, modes=MODES), self.offsets()), COUNTS)

    def test_channels_are_not_duplicated_or_summed(self):
        actual = transition_counts(struct.pack('<hh', 1, 0) * 7040,
            dict(channels=2, pcm=PACKETS, modes=MODES), self.offsets())
        self.assertEqual(actual, {name: [values[0], 0] for name, values in COUNTS.items()})

    def test_last_right_sample_belongs_to_last_ss_packet(self):
        actual = transition_counts(b'\0' * 28158 + b'\x01\x00',
            dict(channels=2, pcm=PACKETS, modes=MODES), self.offsets())
        self.assertEqual(actual, dict(SS=[0, 1], SL=[0, 0], LS=[0, 0], LL=[0, 0]))

    def test_mono_and_missing_end_offset_rejected(self):
        with self.assertRaises(RuntimeError): transition_counts(PCM, dict(channels=1, pcm=PACKETS, modes=MODES), self.offsets())
        offsets = self.offsets(); offsets[-1] -= 4
        with self.assertRaises(RuntimeError): transition_counts(PCM, dict(channels=2, pcm=PACKETS, modes=MODES), offsets)


if __name__ == '__main__': unittest.main()
