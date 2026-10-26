"""Pure S16 comparator units using invented numbers, never decoder evidence.

Synthetic rows deliberately have the wrong whole31 sample total and a unit-only
policy. They cannot qualify the original corpus or substitute for SDK captures.
"""
import hashlib
import importlib.util
from pathlib import Path
import struct
import unittest
PATH=Path(__file__).with_name('test-vorbis-xiph-port-pcm.py')
PIN='3e311ba2c6ca4e93d0fea8df52468aedef82cd394dc67a01f849beaa6a203243'
if hashlib.sha256(PATH.read_bytes()).hexdigest()!=PIN:raise RuntimeError('Frozen pure comparator source changed')
spec=importlib.util.spec_from_file_location('xiph_pcm_unit_subject',PATH)
subject=importlib.util.module_from_spec(spec);spec.loader.exec_module(subject)


def invented_rows():
    cases=[];rows=[];references={};frames=[0]+[1]*13;modes=[0,0,1,1,1,0,1,0,0,0,1,1,0,0]
    for i in range(31):
        value=10 if i==1 else 10+i;name='unit-'+str(i);pcm=struct.pack('<hh',value,-value)*13;references[name]=pcm
        case=dict(case=i,id=name,rate=48000,channels=2,short_block=64,long_block=256,frames=list(frames),modes=list(modes),granules=list(range(14)),pcm_bytes=len(pcm),reference_pcm_sha256=hashlib.sha256(pcm).hexdigest());cases.append(case)
        packets=[dict(packet=p,granule=p,eos=p==13,synthesis_status=0,blockin_status=0,read_status=0 if p else-99,frames=frames[p],pcm_hex=''if p==0 else struct.pack('<hh',value,-value).hex())for p in range(14)]
        rows.append(dict(case=i,id=name,guards=1,unchanged=1,header_statuses=[0,0,0],synthesis_init_status=0,block_init_status=0,api_ok=True,info=dict(rate=48000,channels=2,short_block=64,long_block=256),packets=packets,pcm_hex=pcm.hex(),pcm_bytes=len(pcm),frames=13))
    model=dict(policy={'scope':'invented pure unit numbers; not decoder qualification'},cases=cases,relations=[dict(kind='equal',cases=['unit-0','unit-1']),dict(kind='different',cases=['unit-0','unit-2'])])
    return model,rows,references

def change_packet(row,packet,delta):
    values=subject.samples(bytes.fromhex(row['packets'][packet]['pcm_hex']));row['packets'][packet]['pcm_hex']=struct.pack('<hh',*(x+delta for x in values)).hex();row['pcm_hex']=''.join(p['pcm_hex']for p in row['packets'])


class PCMUnits(unittest.TestCase):
    def test_native_receipt_basename(self):
        for name in('native','esp32','esp32-retry','native_02'):
            self.assertEqual(subject.receipt_basename(name),name)
        for name in('', '.', '..', '../esp32', '/esp32', 'C:esp32', 'esp32.json', 'two names', 'x'*64, None, True):
            with self.subTest(name=name),self.assertRaises(ValueError):subject.receipt_basename(name)

    def test_explicit_unique_outer_options(self):
        self.assertEqual(subject.unique_option(['--output','.build/fresh','--target','esp32'],'output'),'.build/fresh')
        for argv in([],['--output'],['--output','--target','esp32'],['--output','one','--output','two']):
            with self.subTest(argv=argv),self.assertRaises(ValueError):subject.unique_option(argv,'output')

    def test_exact_original_arithmetic_ast(self):
        self.assertTrue(subject.unchanged_math(subject.BASE_COMPARATOR.read_bytes(),PATH.read_bytes()))

    def test_changed_arithmetic_policy_is_rejected(self):
        body=PATH.read_text();changed=body.replace("if whole['max_abs_error']>2:","if whole['max_abs_error']>3:")
        self.assertNotEqual(changed,body)
        with self.assertRaisesRegex(ValueError,'unchanged original numerical policy compare_rows'):
            subject.unchanged_math(subject.BASE_COMPARATOR.read_bytes(),changed)

    def test_hand_computed_errors(self):
        result=subject.errors((-32768,0,32767),(-32767,-2,32765))
        self.assertEqual({k:result[k]for k in('samples','different_samples','max_abs_error','min_signed_error','max_signed_error','sum_signed_error','sum_squared_error')},dict(samples=3,different_samples=3,max_abs_error=2,min_signed_error=-2,max_signed_error=1,sum_signed_error=-3,sum_squared_error=9))
        self.assertEqual(result['signed_error_histogram'],{'-2':2,'1':1});self.assertAlmostEqual(result['rms_error'],3**.5)
        self.assertEqual(result['first_mismatch'],dict(sample=0,frame=0,channel=0,reference=-32768,target=-32767,signed_error=1))

    def test_interleaved_first_mismatch(self):
        result=subject.errors((0,0,0,0,0,1),(0,0,0,0,0,3))
        self.assertEqual({k:result['first_mismatch'][k]for k in('sample','frame','channel')},dict(sample=5,frame=2,channel=1))

    def test_channel_first_mismatch(self):
        result=subject.errors((1,2,3,4,5),(1,2,3,6,5),channel=1)
        self.assertEqual({k:result['first_mismatch'][k]for k in('sample','frame','channel')},dict(sample=3,frame=3,channel=1))

    def test_raw_s16_values_and_byte_alignment(self):
        self.assertEqual(subject.samples(struct.pack('<4h',-32768,32767,0,-1)),(-32768,32767,0,-1))
        for n in(1,2,3,5,6):
            with self.subTest(bytes=n),self.assertRaises(ValueError):subject.samples(b'\0'*n)
        with self.assertRaises(ValueError):subject.errors((1,2),(1,))

    def test_exact_bound_two_and_out_of_bound_three(self):
        model,rows,reference=invented_rows();change_packet(rows[0],1,2);within=subject.compare_rows(model,rows,reference)
        self.assertEqual(within['cases'][0]['zero_lag_direct_LR']['max_abs_error'],2)
        self.assertNotIn('fixed2-S16 error bound',within['cases'][0]['failure_reasons'])
        model,rows,reference=invented_rows();change_packet(rows[0],1,3);outside=subject.compare_rows(model,rows,reference)
        self.assertEqual(outside['cases'][0]['zero_lag_direct_LR']['max_abs_error'],3)
        self.assertIn('fixed2-S16 error bound',outside['cases'][0]['failure_reasons'])
        self.assertFalse(within['passed']);self.assertFalse(outside['passed']);self.assertFalse(within['measurement_completed'])

    def test_missing_case_or_field_is_not_accepted(self):
        model,rows,reference=invented_rows()
        with self.assertRaises(ValueError):subject.compare_rows(model,rows[:-1],reference)
        del rows[0]['id'];result=subject.compare_rows(model,rows,reference)
        self.assertIn('nonmeasurement_error',result['cases'][0]);self.assertFalse(result['passed'])

    def test_invalid_hex_retains_case_failure(self):
        model,rows,reference=invented_rows();rows[0]['pcm_hex']='0';result=subject.compare_rows(model,rows,reference)
        self.assertIn('nonmeasurement_error',result['cases'][0]);self.assertEqual(len(result['cases']),31);self.assertFalse(result['passed'])

    def test_equality_and_difference_relations_are_distinct(self):
        model,rows,reference=invented_rows();result=subject.compare_rows(model,rows,reference)
        self.assertEqual([r['passed']for r in result['relations']['reference']],[True,True])
        self.assertEqual([r['passed']for r in result['relations']['target']],[True,True])
        change_packet(rows[1],1,1);changed=subject.compare_rows(model,rows,reference)
        self.assertEqual([r['passed']for r in changed['relations']['target']],[False,True])
        self.assertFalse(result['passed']);self.assertFalse(changed['passed'])

if __name__=='__main__':unittest.main()
