"""Do not let stable playback/EOF hide a retained decoder failure."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from audit_stream_probe import check_decoder_faults
from common import Failure


class DecoderFaultAuditTests(unittest.TestCase):
    def case(self):
        row = {'decoder_failure': {'sequence': 0}}
        return dict(name='fixture', before=copy.deepcopy(row), after=copy.deepcopy(row),
                    active_before=copy.deepcopy(row), active_after=copy.deepcopy(row),
                    failure_health=copy.deepcopy(row), transition_health=[copy.deepcopy(row)])

    def test_all_sample_locations_are_checked(self):
        self.assertEqual(check_decoder_faults(self.case(), required=True),
                         dict(checked=6, missing=0))
        for key in self.case():
            if key == 'name':
                continue
            with self.subTest(key=key):
                case = self.case()
                row = case[key][0] if key == 'transition_health' else case[key]
                row['decoder_failure']['sequence'] = 1
                with self.assertRaises(Failure):
                    check_decoder_faults(case)

    def test_legacy_missing_evidence_is_explicit(self):
        case = dict(name='old', before={}, after={})
        self.assertEqual(check_decoder_faults(case), dict(checked=0, missing=2))
        with self.assertRaises(Failure):
            check_decoder_faults(case, required=True)

    def test_partial_coverage_is_not_strict_pass(self):
        case = self.case()
        del case['after']['decoder_failure']
        with self.assertRaises(Failure):
            check_decoder_faults(case, required=True)

    def test_malformed_counters_and_empty_evidence_fail(self):
        for counter in ({}, {'sequence': False}, {'sequence': '0'}, {'sequence': -1}, []):
            with self.subTest(counter=counter), self.assertRaises(Failure):
                check_decoder_faults(dict(name='bad', before={'decoder_failure': counter}))
        with self.assertRaises(Failure):
            check_decoder_faults(dict(name='empty'))


if __name__ == '__main__':
    unittest.main()
