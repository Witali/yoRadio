"""Validate retained reproductions, sanitizer passes and source guard behavior."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
from patch_lwip_timewait import patch, patch_api
RESULTS = ROOT/'tests/results/esp32c3-lwip-half-close-20261001'
CASES = ['reap', 'reap-unread', 'expire', 'expire-unread', 'lastack', 'full']


class HalfCloseEvidence(unittest.TestCase):
    def test_real_stack_before_and_after_both_allocators(self):
        for allocator in ('pool', 'heap'):
            for variant in ('original', 'fixed'):
                report = json.loads((RESULTS/f'host-{allocator}-{variant}.json').read_text())
                self.assertEqual(report['lwip_commit'], 'fd432e4ee2cfb7f7f1c7eb7227e0173412e7b84e')
                self.assertEqual(report['allocator'], allocator)
                self.assertEqual(report['patched'], variant == 'fixed')
                self.assertEqual([c['name'] for c in report['cases']], CASES)
                for case in report['cases']:
                    passes = variant == 'fixed' or case['name'] == 'full'
                    self.assertEqual(case['result'], 'PASS' if passes else 'FAIL')
                    if passes:
                        self.assertEqual(case['returncode'], 0)
                        self.assertEqual(case['stderr'], '')
                        self.assertIn('response/data/EOF/ownership', case['stdout'])
                    elif allocator == 'heap':
                        self.assertIn('AddressSanitizer: heap-use-after-free', case['stderr'])
                    else:
                        self.assertIn('owned[i]->callback_arg', case['stderr'])

    def test_unaudited_sources_are_rejected(self):
        for function in (patch, patch_api):
            with self.assertRaisesRegex(ValueError, 'Unaudited lwIP'):
                function('/* changed SDK revision */')


if __name__ == '__main__':
    unittest.main()
