"""Pure original-angle literal/event checks; no compiler, SDK, QEMU or oracle run."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('floor0_angles_capture', ROOT/'tests/run-vorbis-floor0-angles-qemu.py')
subject = importlib.util.module_from_spec(spec); spec.loader.exec_module(subject)
DOCUMENT = dict(schema='native-vorbis-floor0-angles-cases-v1', cases=[
    dict(id='full', angles_hex=['7fefffffffffffff', 'ffefffffffffffff', '0000000000000001',
                              '8000000000000001', '0000000000000000', '8000000000000000'],
         bin=1, map_size=3, raw_amplitude='9007199254740993', amplitude_bits=63, amplitude_offset=255),
    dict(id='zero', angles_hex=['0000000000000000'], bin=0, map_size=1,
         raw_amplitude='0', amplitude_bits=0, amplitude_offset=0)])
HEADER = '''#define FLOOR0_ANGLES_CASE_COUNT 2
static const uint64_t floor0_angles_0[] = {UINT64_C(0x7fefffffffffffff),UINT64_C(0xffefffffffffffff),UINT64_C(0x0000000000000001),UINT64_C(0x8000000000000001),UINT64_C(0x0000000000000000),UINT64_C(0x8000000000000000)};
static const uint64_t floor0_angles_1[] = {UINT64_C(0x0000000000000000)};
static const floor0_angles_case_t floor0_angles_cases[FLOOR0_ANGLES_CASE_COUNT] = {
 {"full",floor0_angles_0,6,1,3,UINT64_C(9007199254740993),63,255},
 {"zero",floor0_angles_1,1,0,1,UINT64_C(0),0,0},
};
'''
API = ('denominator_unit', 'gain_composition', 'tiny_angles_survive_rounding', 'full_finite_inputs',
       'denominator_invalid', 'gain_invalid', 'absent_pole_indeterminate', 'zero_offset_unity')
DATA = 'a'*64


def log_for(target):
    core = 1 if target == 'esp32' else 0
    lines = [f'FLOOR0_ANGLES_BEGIN cases=2 coordinator=0 worker={core} data={DATA}',
             f'FLOOR0_ANGLES_WORKER core={core} priority=3 stack=16384']
    lines += [f'FLOOR0_ANGLES_API index={i} name={name} ok=1 core={core}' for i, name in enumerate(API)]
    lines += [f'FLOOR0_ANGLES_CASE case=0 id=full order=6 bin=1 map_size=3 ds=0 denominator_bits=3fe0000000000000 denominator_exponent=123 gs=0 kind=0 log2_bits=bfe8000000000000 log2_exponent=1 guards=1 unchanged=1 core={core}',
              f'FLOOR0_ANGLES_CASE case=1 id=zero order=1 bin=0 map_size=1 ds=0 denominator_bits=0000000000000000 denominator_exponent=0 gs=0 kind=1 log2_bits=0000000000000000 log2_exponent=0 guards=1 unchanged=1 core={core}',
              f'FLOOR0_ANGLES_COMPLETE cases=2 api=8 core={core}', 'FLOOR0_ANGLES_STOP status=CAPTURED']
    return '\n'.join(lines)+'\n'


class LiteralReadback(unittest.TestCase):
    def test_full_finite_angle_domain_and_wide_raw_are_exact(self):
        self.assertEqual(subject.validate_cases(copy.deepcopy(DOCUMENT), HEADER), DOCUMENT['cases'])
        self.assertNotEqual(int(DOCUMENT['cases'][0]['raw_amplitude']), int(float(DOCUMENT['cases'][0]['raw_amplitude'])))

    def test_missing_angle_and_descriptor_commas_are_rejected(self):
        for header in (HEADER.replace('7fefffffffffffff),UINT64_C', '7fefffffffffffff)UINT64_C'),
                       HEADER.replace('63,255},\n', '63,255}\n')):
            with self.subTest(header=header), self.assertRaises(ValueError): subject.validate_cases(DOCUMENT, header)

    def test_changed_angle_raw_pointer_or_bin_metadata_are_rejected(self):
        for header in (HEADER.replace('0x0000000000000001', '0x0000000000000002'),
                       HEADER.replace('9007199254740993', '9007199254740992'),
                       HEADER.replace('"full",floor0_angles_0,', '"full",floor0_angles_1,'),
                       HEADER.replace('floor0_angles_0,6,1,3,', 'floor0_angles_0,6,1,4,')):
            with self.subTest(header=header), self.assertRaises(ValueError): subject.validate_cases(DOCUMENT, header)

    def test_duplicate_arrays_counts_and_nonliteral_tokens_fail(self):
        for header in (HEADER.splitlines()[1]+'\n'+HEADER, '#define FLOOR0_ANGLES_CASE_COUNT 2\n'+HEADER,
                       HEADER.replace('UINT64_C(9007199254740993)', 'UINT64_C(9007199254740992)+1'),
                       HEADER.replace('63,255}', '63,255+0}')):
            with self.subTest(header=header), self.assertRaises(ValueError): subject.validate_cases(DOCUMENT, header)

    def test_nonfinite_angles_empty_order_and_invalid_integer_domains_fail(self):
        variants = []
        for key, value in (('raw_amplitude', 1), ('raw_amplitude', '9223372036854775808'),
                           ('amplitude_bits', True), ('amplitude_bits', 64), ('amplitude_offset', 256),
                           ('map_size', 0), ('map_size', 65536), ('bin', 3), ('bin', True),
                           ('angles_hex', []), ('angles_hex', ['0000000000000000']*256),
                           ('angles_hex', ['7ff8000000000000']), ('angles_hex', ['7ff0000000000000'])):
            data = copy.deepcopy(DOCUMENT); data['cases'][0][key] = value; variants.append(data)
        for data in variants:
            with self.subTest(data=data), self.assertRaises(ValueError): subject.validate_cases(data, HEADER)

    def test_schema_fields_ids_capacity_missing_and_extra_rows_fail(self):
        variants = []
        data = copy.deepcopy(DOCUMENT); data['schema'] = 'other'; variants.append(data)
        data = copy.deepcopy(DOCUMENT); data['cases'][0]['unused'] = 0; variants.append(data)
        data = copy.deepcopy(DOCUMENT); data['cases'][0]['id'] = 'bad id'; variants.append(data)
        data = copy.deepcopy(DOCUMENT); data['cases'][1]['id'] = 'full'; variants.append(data)
        for data in variants:
            with self.subTest(data=data), self.assertRaises(ValueError): subject.validate_cases(data, HEADER)
        first = ' {"full",floor0_angles_0,6,1,3,UINT64_C(9007199254740993),63,255},\n'
        second = ' {"zero",floor0_angles_1,1,0,1,UINT64_C(0),0,0},\n'
        for header in (HEADER.replace('CASE_COUNT 2', 'CASE_COUNT 3'), HEADER.replace(second, ''),
                       HEADER.replace(second, second+second), HEADER.replace(first+second, second+first)):
            with self.subTest(header=header), self.assertRaises(ValueError): subject.validate_cases(DOCUMENT, header)


class EventCapture(unittest.TestCase):
    def test_both_core_profiles_and_all_api_groups(self):
        for target in ('esp32', 'esp32c3'):
            result = subject.validate_log('I normal startup\n'+log_for(target), DOCUMENT['cases'], target, DATA)
            self.assertEqual((result['cases'], result['protocol_lines'], result['api_groups']), (2, 14, 8))
            self.assertEqual(result['rows'][0]['bin'], 1); self.assertEqual(result['rows'][0]['map_size'], 3)

    def test_finite_numbers_are_retained_for_separate_oracle_without_fitting(self):
        changed = log_for('esp32').replace('log2_bits=bfe8000000000000 log2_exponent=1', 'log2_bits=3fe4000000000000 log2_exponent=63')
        result = subject.validate_log(changed, DOCUMENT['cases'], 'esp32', DATA)
        self.assertEqual((result['rows'][0]['log2_bits'], result['rows'][0]['log2_exponent']), ('3fe4000000000000', 63))

    def test_missing_reordered_duplicate_extra_and_truncated_events_fail(self):
        lines = log_for('esp32').splitlines()
        for changed in (lines[:2]+lines[3:], lines[:3]+[lines[2]]+lines[3:],
                        lines[:2]+[lines[3],lines[2]]+lines[4:], lines+['FLOOR0_ANGLES_OTHER value=1'],
                        ['I noise: '+lines[0]]+lines[1:]):
            with self.subTest(changed=changed), self.assertRaises(ValueError): subject.validate_log('\n'.join(changed), DOCUMENT['cases'], 'esp32', DATA)

    def test_changed_core_data_case_bin_map_status_or_guards_fail(self):
        log = log_for('esp32')
        for changed in (log.replace('worker=1', 'worker=0'), log.replace('priority=3', 'priority=2'),
                        log.replace(DATA, 'b'*64), log.replace('id=full', 'id=other'), log.replace('bin=1', 'bin=0'),
                        log.replace('map_size=3', 'map_size=4'), log.replace('ds=0', 'ds=-99'),
                        log.replace('gs=0', 'gs=-1'), log.replace('guards=1', 'guards=0'), log.replace('unchanged=1', 'unchanged=0')):
            with self.subTest(changed=changed), self.assertRaises(ValueError): subject.validate_log(changed, DOCUMENT['cases'], 'esp32', DATA)

    def test_nonfinite_nonnormalized_bad_exponent_or_nonzero_absent_fail(self):
        log = log_for('esp32')
        for changed in (log.replace('log2_bits=bfe8000000000000', 'log2_bits=7ff0000000000000'),
                        log.replace('log2_bits=bfe8000000000000', 'log2_bits=4000000000000000'),
                        log.replace('log2_exponent=1', 'log2_exponent=2147483648'),
                        log.replace('kind=0 log2_bits=bfe8000000000000', 'kind=1 log2_bits=bfe8000000000000'),
                        log.replace('denominator_bits=3fe0000000000000', 'denominator_bits=bfe0000000000000')):
            with self.subTest(changed=changed), self.assertRaises(ValueError): subject.validate_log(changed, DOCUMENT['cases'], 'esp32', DATA)

    def test_only_controlled_capture_stop_and_exact_fields_are_accepted(self):
        log = log_for('esp32')
        for changed in (log.replace('status=CAPTURED', 'status=PASS'),
                        log.replace('FLOOR0_ANGLES_STOP status=CAPTURED\n', ''),
                        log.replace('gs=0 kind=', 'gs=0 gs=0 kind='), log.replace('gs=0 ', ''),
                        log.replace('case=0', 'case=00'), log+'Guru Meditation\n'):
            with self.subTest(changed=changed), self.assertRaises(ValueError): subject.validate_log(changed, DOCUMENT['cases'], 'esp32', DATA)


if __name__ == '__main__': unittest.main(verbosity=2)
