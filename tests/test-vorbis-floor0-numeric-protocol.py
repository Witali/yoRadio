"""Pure literal-readback/event tests. No arithmetic oracle, compiler or QEMU runs."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('floor0_numeric_capture', ROOT/'tests/run-vorbis-floor0-numeric-qemu.py')
subject = importlib.util.module_from_spec(spec); spec.loader.exec_module(subject)
DOCUMENT = dict(schema='native-vorbis-floor0-numeric-cases-v1', cases=[
    dict(id='big-raw', operation='curve', raw_amplitude='9007199254740993', amplitude_bits=63,
         amplitude_offset=60, coefficients_hex=['0000000000000000', '3ff0000000000000'],
         w_hex='0000000000000000', denominator_mantissa_hex='0000000000000000', denominator_exponent=0),
    dict(id='direct', operation='gain', raw_amplitude='1', amplitude_bits=1, amplitude_offset=1,
         coefficients_hex=[], w_hex='0000000000000000', denominator_mantissa_hex='3fe0000000000000', denominator_exponent=1)])
HEADER = '''#define FLOOR0_NUMERIC_CASE_COUNT 2
static const uint64_t floor0_coefficients_0[] = {UINT64_C(0x0000000000000000),UINT64_C(0x3ff0000000000000)};
static const floor0_numeric_case_t floor0_numeric_cases[FLOOR0_NUMERIC_CASE_COUNT] = {
 {"big-raw",1,UINT64_C(9007199254740993),63,60,2,UINT64_C(0x0000000000000000),floor0_coefficients_0,UINT64_C(0x0000000000000000),INT32_C(0)},
 {"direct",2,UINT64_C(1),1,1,0,UINT64_C(0x0000000000000000),NULL,UINT64_C(0x3fe0000000000000),INT32_C(1)},
};
'''
API = ('prepare_valid', 'prepare_in_place', 'prepare_invalid', 'denominator_invalid',
       'gain_invalid', 'gain_absent', 'gain_pole', 'gain_indeterminate', 'gain_unity',
       'gain_at_cosine_absent', 'bark_valid', 'bark_invalid', 'bin_cardinals',
       'bin_invalid', 'gain_at_bin_valid', 'gain_at_bin_invalid')
DATA = 'a'*64


def log_for(target):
    core = 1 if target == 'esp32' else 0
    lines = [f'FLOOR0_NUMERIC_BEGIN cases=2 coordinator=0 worker={core} data={DATA}',
             f'FLOOR0_NUMERIC_WORKER core={core} priority=3 stack=16384']
    lines += [f'FLOOR0_NUMERIC_API index={i} name={name} ok=1 core={core}' for i, name in enumerate(API)]
    lines += [f'FLOOR0_NUMERIC_CASE case=0 id=big-raw operation=1 order=2 ds=0 denominator_bits=3fe0000000000000 denominator_exponent=0 gs=0 kind=0 log2_bits=3fe8000000000000 log2_exponent=1 guards=1 unchanged=1 core={core}',
              f'FLOOR0_NUMERIC_CASE case=1 id=direct operation=2 order=0 ds=-99 denominator_bits=3fe0000000000000 denominator_exponent=1 gs=0 kind=0 log2_bits=0000000000000000 log2_exponent=0 guards=1 unchanged=1 core={core}',
              f'FLOOR0_NUMERIC_COMPLETE cases=2 api=16 core={core}', 'FLOOR0_NUMERIC_STOP status=CAPTURED']
    return '\n'.join(lines)+'\n'


class LiteralReadback(unittest.TestCase):
    def test_all_exact_bits_and_wide_amplitude_are_recovered(self):
        self.assertEqual(subject.validate_cases(copy.deepcopy(DOCUMENT), HEADER), DOCUMENT['cases'])
        self.assertNotEqual(int(DOCUMENT['cases'][0]['raw_amplitude']), int(float(DOCUMENT['cases'][0]['raw_amplitude'])))

    def test_plain_and_macro_exponents_are_equivalent_literal_syntax(self):
        self.assertEqual(subject.validate_cases(DOCUMENT, HEADER.replace('INT32_C(0)', '0').replace('INT32_C(1)', '1')), DOCUMENT['cases'])

    def test_missing_coeff_or_descriptor_commas_are_rejected(self):
        for header in (HEADER.replace('0000000000000000),UINT64_C', '0000000000000000)UINT64_C'),
                       HEADER.replace('INT32_C(0)},\n', 'INT32_C(0)}\n')):
            with self.subTest(header=header), self.assertRaises(ValueError): subject.validate_cases(DOCUMENT, header)

    def test_changed_bits_wide_raw_pointer_or_capacity_are_rejected(self):
        for header in (HEADER.replace('0x3ff0000000000000', '0x3ff0000000000001'),
                       HEADER.replace('9007199254740993', '9007199254740992'),
                       HEADER.replace('),floor0_coefficients_0,', '),floor0_coefficients_1,'),
                       HEADER.replace('CASE_COUNT 2', 'CASE_COUNT 3')):
            with self.subTest(header=header), self.assertRaises(ValueError): subject.validate_cases(DOCUMENT, header)

    def test_duplicate_arrays_counts_or_nonliteral_syntax_are_rejected(self):
        declaration = HEADER.splitlines()[1]
        for header in (declaration+'\n'+HEADER, '#define FLOOR0_NUMERIC_CASE_COUNT 2\n'+HEADER,
                       HEADER.replace('UINT64_C(9007199254740993)', 'UINT64_C(9007199254740992)+1'),
                       HEADER.replace('INT32_C(0)', 'INT32_C(0')):
            with self.subTest(header=header), self.assertRaises(ValueError): subject.validate_cases(DOCUMENT, header)

    def test_invalid_schema_shape_fields_ids_or_domains_are_rejected(self):
        variants = []
        for key, value in (('raw_amplitude', 1), ('amplitude_bits', True), ('amplitude_bits', 64),
                           ('amplitude_offset', 256), ('raw_amplitude', '9223372036854775808'),
                           ('w_hex', '7ff8000000000000'), ('w_hex', '4008000000000000'), ('id', 'bad id')):
            data = copy.deepcopy(DOCUMENT); data['cases'][0][key] = value; variants.append(data)
        data = copy.deepcopy(DOCUMENT); data['cases'][1]['id'] = data['cases'][0]['id']; variants.append(data)
        data = copy.deepcopy(DOCUMENT); data['cases'][1]['denominator_exponent'] = 2147483648; variants.append(data)
        data = copy.deepcopy(DOCUMENT); data['cases'][0]['unused'] = 0; variants.append(data)
        for data in variants:
            with self.subTest(data=data), self.assertRaises(ValueError): subject.validate_cases(data, HEADER)


class EventCapture(unittest.TestCase):
    def test_both_native_worker_core_profiles_and_all_api_groups(self):
        for target in ('esp32', 'esp32c3'):
            result = subject.validate_log('I normal startup\n'+log_for(target), DOCUMENT['cases'], target, DATA)
            self.assertEqual(result['cases'], 2); self.assertEqual(result['protocol_lines'], 22)
            self.assertEqual(result['api_groups'], 16)
            self.assertEqual([r['operation'] for r in result['rows']], ['curve', 'gain'])
            self.assertEqual(result['rows'][1]['ds'], -99)

    def test_normalized_math_is_captured_for_separate_oracle_not_fitted(self):
        changed = log_for('esp32').replace('log2_bits=3fe8000000000000 log2_exponent=1', 'log2_bits=3fe4000000000000 log2_exponent=63')
        result = subject.validate_log(changed, DOCUMENT['cases'], 'esp32', DATA)
        self.assertEqual(result['rows'][0]['log2_bits'], '3fe4000000000000')
        self.assertEqual(result['rows'][0]['log2_exponent'], 63)

    def test_missing_reordered_duplicate_extra_or_truncated_events_fail(self):
        lines = log_for('esp32').splitlines()
        for changed in (lines[:2]+lines[3:], lines[:3]+[lines[2]]+lines[3:],
                        lines[:2]+[lines[3],lines[2]]+lines[4:], lines+['FLOOR0_NUMERIC_OTHER value=1'],
                        ['I noise: '+lines[0]]+lines[1:]):
            with self.subTest(changed=changed), self.assertRaises(ValueError): subject.validate_log('\n'.join(changed), DOCUMENT['cases'], 'esp32', DATA)

    def test_changed_core_data_input_identity_status_or_guards_fail(self):
        log = log_for('esp32')
        for changed in (log.replace('worker=1', 'worker=0'), log.replace('priority=3', 'priority=2'),
                        log.replace(DATA, 'b'*64), log.replace('id=big-raw', 'id=other'),
                        log.replace('ds=-99', 'ds=0'), log.replace('gs=0', 'gs=-1'),
                        log.replace('guards=1', 'guards=0'), log.replace('unchanged=1', 'unchanged=0')):
            with self.subTest(changed=changed), self.assertRaises(ValueError): subject.validate_log(changed, DOCUMENT['cases'], 'esp32', DATA)

    def test_nonfinite_nonnormalized_bad_exponent_or_nonzero_absent_fail(self):
        log = log_for('esp32')
        for changed in (log.replace('log2_bits=3fe8000000000000', 'log2_bits=7ff0000000000000'),
                        log.replace('log2_bits=3fe8000000000000', 'log2_bits=4000000000000000'),
                        log.replace('log2_exponent=1', 'log2_exponent=2147483648'),
                        log.replace('kind=0 log2_bits=3fe8000000000000', 'kind=1 log2_bits=3fe8000000000000'),
                        log.replace('denominator_bits=3fe0000000000000', 'denominator_bits=bfe0000000000000')):
            with self.subTest(changed=changed), self.assertRaises(ValueError): subject.validate_log(changed, DOCUMENT['cases'], 'esp32', DATA)

    def test_direct_denominator_echo_and_controlled_capture_stop_are_required(self):
        log = log_for('esp32')
        for changed in (log.replace('ds=-99 denominator_bits=3fe0000000000000', 'ds=-99 denominator_bits=3fe8000000000000'),
                        log.replace('status=CAPTURED', 'status=PASS'), log.replace('FLOOR0_NUMERIC_STOP status=CAPTURED\n', '')):
            with self.subTest(changed=changed), self.assertRaises(ValueError): subject.validate_log(changed, DOCUMENT['cases'], 'esp32', DATA)

    def test_duplicate_or_missing_case_fields_and_panic_fail(self):
        log = log_for('esp32')
        for changed in (log.replace('gs=0 kind=', 'gs=0 gs=0 kind='), log.replace('gs=0 ', ''),
                        log.replace('case=0', 'case=00'), log+'Guru Meditation\n'):
            with self.subTest(changed=changed), self.assertRaises(ValueError): subject.validate_log(changed, DOCUMENT['cases'], 'esp32', DATA)


if __name__ == '__main__': unittest.main(verbosity=2)
