"""Synthetic transcript controls only; not observed codec/target executions."""
import copy
import unittest

from protocol import validate_sdk
from run_host import sanitizer_clean_scope


def fixture():
    b=dict(dim=2,dec_type=1,dec_nodeb=4,dec_leafw=1,q_bits=2,q_pack=0,q_min=-1073741824,q_minp=-30,
        q_del=268435456,q_delp=-28,table_bytes=12,qval_hex='',points=[0],
        probes=[dict(bits=1,wire_scope='preferred_zero',expected_by_point={'0':[1,-1]})])
    contract=dict(contract_sha256='a'*64,model=dict(case_count=1,vector_calls=1,cases=[dict(book=b)]))
    lines=[f'PUBLIC_BOOK_CONSUMER_BEGIN contract={"a"*64} cases=1 calls=1 core=0',
        'PUBLIC_BOOK_CONSUMER_FIELDS case=0 type=1 node=4 leaf=1 qbits=2 qpack=0 qmin=-1073741824 minp=-30 qdel=268435456 delp=-28 table=000000800000008000000000 qval=- core=0',
        'PUBLIC_BOOK_CONSUMER_VECTOR case=0 probe=0 point=0 bits=1 consumed=1 equal=1 core=0 values=1,-1',
        'PUBLIC_BOOK_CONSUMER_CASE case=0 probes=1 live=0 core=0',
        'PUBLIC_BOOK_CONSUMER_COMPLETE cases=1 calls=1 unequal=0 live=0 core=0']
    return contract,lines


class TranscriptControls(unittest.TestCase):
    def test_honest_mismatch_does_not_fabricate_a_sanitizer_finding(self):
        row=dict(terminal=True,timed_out=False,interrupted=False,returncode=1)
        self.assertTrue(sanitizer_clean_scope(row,b'',dict(equal=False)))
        row['returncode']=0;self.assertTrue(sanitizer_clean_scope(row,b'',dict(equal=True)))

    def test_sanitizer_diagnostic_missing_vector_or_bad_exit_remains_nonclean(self):
        row=dict(terminal=True,timed_out=False,interrupted=False,returncode=1)
        self.assertFalse(sanitizer_clean_scope(row,b'runtime error: shift exponent',None))
        self.assertFalse(sanitizer_clean_scope(row,b'',dict(equal=True)))
        row['returncode']=0;self.assertFalse(sanitizer_clean_scope(row,b'ERROR: AddressSanitizer',dict(equal=True)))

    def test_complete_synthetic_publication_comparison_scopes_stay_separate(self):
        contract,lines=fixture();r=validate_sdk('\n'.join(lines),contract)
        self.assertTrue(r['actual_canonical_SDK_publication_completed']);self.assertTrue(r['complete_Fraction_comparison'])
        self.assertTrue(r['all_Fraction_vectors_equal']);self.assertFalse(r['host_sanitizers_qualified'])
        self.assertFalse(r['public_arithmetic_portability_qualified']);self.assertFalse(r['full_standard_qualified'])

    def test_missing_vector_rejected(self):
        c,lines=fixture();del lines[2]
        with self.assertRaises(ValueError):validate_sdk('\n'.join(lines),c)

    def test_last_component_tamper_with_false_pass_flag_rejected(self):
        c,lines=fixture();lines[2]=lines[2].replace('values=1,-1','values=1,-2')
        with self.assertRaises(ValueError):validate_sdk('\n'.join(lines),c)

    def test_honestly_recorded_mismatch_is_complete_numerical_nonpass(self):
        c,lines=fixture();lines[2]=lines[2].replace('equal=1','equal=0').replace('values=1,-1','values=1,-2');lines[-1]=lines[-1].replace('unequal=0','unequal=1')
        r=validate_sdk('\n'.join(lines),c);self.assertTrue(r['complete_Fraction_comparison'])
        self.assertFalse(r['all_Fraction_vectors_equal']);self.assertEqual(r['unequal_calls'],1)

    def test_wrong_point_consumption_and_core_rejected(self):
        for before,after in (('point=0','point=-8'),('consumed=1','consumed=0'),('core=0','core=1')):
            c,lines=fixture();lines[2]=lines[2].replace(before,after)
            with self.assertRaises(ValueError):validate_sdk('\n'.join(lines),c)

    def test_scaled_qdel_field_mismatch_rejected(self):
        c,lines=fixture();lines[1]=lines[1].replace('qdel=268435456','qdel=1073741824')
        with self.assertRaises(ValueError):validate_sdk('\n'.join(lines),c)

    def test_full_owned_array_bytecount_required(self):
        c,lines=fixture();lines[1]=lines[1].replace('table=000000800000008000000000','table=00000080')
        with self.assertRaises(ValueError):validate_sdk('\n'.join(lines),c)

    def test_extra_protocol_record_or_panic_rejected(self):
        for text in ('\nPUBLIC_BOOK_CONSUMER_UNKNOWN x=1','\npanic: synthetic'):
            c,lines=fixture()
            with self.assertRaises(ValueError):validate_sdk('\n'.join(lines)+text,c)


if __name__=='__main__':unittest.main()
