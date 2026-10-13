"""Repeated cases must retain payload identity and never hide an inter-case reboot."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/esp32c3_tests'))
from common import Failure
from stream_probe_cases import repeat_specs, validate_schedule
import audit_stream_probe


class RepeatTests(unittest.TestCase):
    def report(self):
        original = {'a': dict(bytes=10, sha256='abc', mime=None),
                    'b': dict(bytes=20, sha256='def', mime=None)}
        expanded = repeat_specs(original, 3)
        return dict(fixtures=expanded, repetitions=3,
                    cases=[dict(name=name) for name in expanded])

    def test_order_and_distinct_request_names(self):
        report = self.report()
        self.assertEqual(list(validate_schedule(report, 6)),
                         ['a','b','a--repeat-2','b--repeat-2','a--repeat-3','b--repeat-3'])

    def test_payload_memory_is_reused(self):
        data = bytes(1000)
        specs = repeat_specs({'x':dict(data=data)}, 2)
        self.assertIs(specs['x']['data'], specs['x--repeat-2']['data'])

    def test_invalid_counts_and_collisions(self):
        for value in (0, 21, True, 1.5, '2'):
            with self.assertRaises(Failure): repeat_specs({'x':{}}, value)
        with self.assertRaises(Failure): repeat_specs({'x':{},'x--repeat-2':{}}, 2)

    def test_missing_duplicate_reordered_or_changed_payload_fails(self):
        for mode in range(6):
            report = self.report()
            if mode == 0: report['cases'].pop()
            if mode == 1: report['cases'][1] = report['cases'][0]
            if mode == 2: report['cases'].reverse()
            if mode == 3: report['fixtures']['a--repeat-2']['sha256'] = 'changed'
            if mode == 4: report['fixtures']['a--repeat-2']['source_name'] = 'b'
            if mode == 5: report['fixtures']['a--repeat-2']['iteration'] = 3
            with self.subTest(mode=mode), self.assertRaises(Failure): validate_schedule(report, 6)

    def test_older_single_pass_reports(self):
        report = dict(fixtures={'a':dict(bytes=10,sha256='abc',mime=None)},cases=[dict(name='a')])
        self.assertEqual(validate_schedule(report,1), {'a':'a'})

    def test_actual_audit_rejects_reboot_between_otherwise_valid_cases(self):
        evidence = ROOT/'tests/results/esp32c3-stream-probe-20261013/startup-fault-01'
        report = json.loads((evidence/'https/results.json').read_text())
        controller = evidence/'sources/tools/esp32c3_tests/stream_probe.py'
        folder = ROOT/'.build'; folder.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=folder) as temp:
            src = Path(temp)/'results.json'; out = Path(temp)/'audit.json'
            argv = ['audit', '--results',str(src),'--controller',str(controller),
                    '--expected-cases','20','--output',str(out)]
            src.write_text(json.dumps(report))
            with patch.object(sys,'argv',argv): audit_stream_probe.main()
            self.assertTrue(json.loads(out.read_text())['passed'])
            changed = copy.deepcopy(report)
            case = changed['cases'][1]
            for key in ('before','after','active_before','active_after'):
                case[key]['boot_id'] = '1234567890abcdef'
            src.write_text(json.dumps(changed))
            with patch.object(sys,'argv',argv), self.assertRaisesRegex(Failure,'restart between cases'):
                audit_stream_probe.main()


if __name__ == '__main__': unittest.main()
