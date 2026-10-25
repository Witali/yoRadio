"""Pure case-readback/protocol tests; no SDK, QEMU or decoder is executed."""
import copy
import importlib.util
from pathlib import Path
import unittest

SUBJECT = Path(__file__).with_name('run-vorbis-quantvals-qemu.py')
spec = importlib.util.spec_from_file_location('quantvals_protocol_subject', SUBJECT)
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)  # Definitions only; main() is guarded.
ROWS = [dict(entries=2, dimensions=32, expected=1),
        dict(entries=64, dimensions=3, expected=4)]
DOCUMENT = dict(schema='vorbis-quantvals-cases-v1', cases=ROWS)
HEADER = """#define QUANTVALS_CASE_COUNT 2
static const quantvals_case_t quantvals_cases[QUANTVALS_CASE_COUNT] = {
    {2, 32, 1},
    {64, 3, 4},
};
"""
DATA = 'a'*64


def log_for(target):
    core = 1 if target == 'esp32' else 0
    return '\n'.join([
        f'QUANTVALS_BEGIN cases=2 coordinator=0 worker={core} data={DATA}',
        f'QUANTVALS_WORKER core={core} priority=3 stack=16384',
        f'QUANTVALS_CASE index=0 entries=2 dimensions=32 expected=1 actual=1 core={core}',
        f'QUANTVALS_CASE index=1 entries=64 dimensions=3 expected=4 actual=4 core={core}',
        f'QUANTVALS_COMPLETE cases=2 core={core}', 'QUANTVALS_STOP status=PASS'])+'\n'


class Cases(unittest.TestCase):
    def test_valid_exact_integer_roots_and_literal_headers(self):
        for header in (HEADER, HEADER.replace('64, 3, 4', '64U, 3u, UINT32_C(4)')):
            self.assertEqual(subject.validate_cases(DOCUMENT, header), ROWS)

    def test_wrong_json_result_is_rejected_even_with_matching_header(self):
        data = copy.deepcopy(DOCUMENT)
        data['cases'][1]['expected'] = 3
        with self.assertRaises(ValueError):
            subject.validate_cases(data, HEADER.replace('64, 3, 4', '64, 3, 3'))

    def test_noninteger_and_invalid_fields_are_rejected(self):
        for field, value in (('entries', True), ('dimensions', 3.0), ('expected', '1'),
                             ('entries', 0), ('entries', 2147483648),
                             ('dimensions', 0), ('dimensions', 65536)):
            with self.subTest(field=field, value=value):
                data = copy.deepcopy(DOCUMENT)
                data['cases'][0][field] = value
                with self.assertRaises(ValueError):
                    subject.validate_cases(data, HEADER)

    def test_case_shape_and_schema_are_rejected(self):
        variants = [dict(schema='other', cases=ROWS), dict(schema=DOCUMENT['schema'], cases=[])]
        missing, extra = copy.deepcopy(DOCUMENT), copy.deepcopy(DOCUMENT)
        del missing['cases'][0]['dimensions']
        extra['cases'][0]['unused'] = 1
        for data in variants+[missing, extra]:
            with self.subTest(data=data), self.assertRaises(ValueError):
                subject.validate_cases(data, HEADER)

    def test_changed_missing_extra_rows_or_count_are_rejected(self):
        variants = [HEADER.replace('{64, 3, 4}', '{64, 3, 3}'),
                    HEADER.replace('    {64, 3, 4},\n', ''),
                    HEADER.replace('};', '    {1, 1, 1},\n};'),
                    HEADER.replace('COUNT 2', 'COUNT 3'),
                    HEADER.replace('COUNT 2', 'COUNT 2\n#define QUANTVALS_CASE_COUNT 2')]
        for header in variants:
            with self.subTest(header=header), self.assertRaises(ValueError):
                subject.validate_cases(DOCUMENT, header)

    def test_nonliteral_separators_are_rejected(self):
        for separator in (';', ' + ', ' /* hidden */ '):
            with self.subTest(separator=separator), self.assertRaises(ValueError):
                subject.validate_cases(DOCUMENT, HEADER.replace('},\n    {', '}'+separator+'{'))

    def test_missing_row_comma_is_rejected(self):
        with self.assertRaises(ValueError):
            subject.validate_cases(DOCUMENT, HEADER.replace('},\n    {', '}\n    {'))


class Protocol(unittest.TestCase):
    def test_complete_ordered_events_on_both_architectures(self):
        for target, core in (('esp32', 1), ('esp32c3', 0)):
            with self.subTest(target=target):
                result = subject.validate_log('I boot: normal startup\n'+log_for(target), ROWS, target, DATA)
                self.assertEqual((result['cases'], result['protocol_lines'], result['worker_core']),
                                 (2, 6, core))
                self.assertTrue(result['every_root_exact'])

    def test_missing_duplicated_extra_and_reordered_events_are_rejected(self):
        lines = log_for('esp32').splitlines()
        variants = [lines[:2]+lines[3:], lines[:3]+[lines[2]]+lines[3:],
                    lines+['QUANTVALS_UNKNOWN value=1'], lines[:2]+[lines[3], lines[2]]+lines[4:]]
        for values in variants:
            with self.subTest(values=values), self.assertRaises(ValueError):
                subject.validate_log('\n'.join(values), ROWS, 'esp32', DATA)

    def test_changed_case_core_data_or_worker_are_rejected(self):
        log = log_for('esp32')
        variants = [log.replace('entries=64', 'entries=63'), log.replace('actual=4', 'actual=3'),
                    log.replace('index=1', 'index=2'), log.replace('core=1', 'core=0'),
                    log.replace(DATA, 'b'*64), log.replace('priority=3', 'priority=2'),
                    log.replace('stack=16384', 'stack=8192'), log.replace('cases=2', 'cases=1')]
        for value in variants:
            with self.subTest(value=value), self.assertRaises(ValueError):
                subject.validate_log(value, ROWS, 'esp32', DATA)

    def test_missing_or_failed_stop_is_rejected(self):
        log = log_for('esp32c3')
        for value in (log.replace('QUANTVALS_STOP status=PASS\n', ''),
                      log.replace('status=PASS', 'status=FAIL')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                subject.validate_log(value, ROWS, 'esp32c3', DATA)

    def test_panic_or_timeout_never_qualifies_a_complete_prefix(self):
        for failure in ('Guru Meditation', 'abort()', 'Backtrace:', 'assert failed',
                        'CORRUPT HEAP', 'watchdog', 'stack overflow', 'timed out'):
            with self.subTest(failure=failure), self.assertRaises(ValueError):
                subject.validate_log(log_for('esp32')+failure, ROWS, 'esp32', DATA)


if __name__ == '__main__':
    unittest.main(verbosity=2)
