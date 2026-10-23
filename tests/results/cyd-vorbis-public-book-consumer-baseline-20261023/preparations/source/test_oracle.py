"""Root-owned independent oracle construction controls; no C/compiler/decoder calls."""
import json
from fractions import Fraction
from pathlib import Path
import unittest

from oracle import Bits, describe, fixed_fields, number, patch_zero_fields, select, words
from materialize import host_table

HERE=Path(__file__).resolve().parent
ONE=(788<<21)|1


class OracleControls(unittest.TestCase):
    def rows(self): return json.loads((HERE/'fixture-inputs.json').read_bytes())['cases']
    def raw(self,row): return (HERE/row['setup']).read_bytes()

    def test_exact_packed_float_known_answers(self):
        self.assertEqual(number(ONE),1);self.assertEqual(number(ONE|0x80000000),-1)
        self.assertEqual(number((784<<21)|1),Fraction(1,16))

    def test_zero_is_exact_and_normalized_sentinel_is_explicit(self):
        for packed in (0,0x80000000,0x7fe00000):
            self.assertEqual(number(packed),0);self.assertEqual(fixed_fields(packed),(0,-9999))

    def test_q_bits_2_9_16_canonical_delta_scaling_identity(self):
        value,point=fixed_fields(ONE)
        for width in (2,9,16):
            self.assertEqual(Fraction(value>>width)*Fraction(2)**(point+width),1)
        self.assertEqual([(value>>n,point+n) for n in (2,9,16)],[(268435456,-28),(2097152,-21),(16384,-14)])

    def test_lsb_bitreader_cross_byte_and_width32(self):
        reader=Bits(bytes.fromhex('a55a12345678'));self.assertEqual(reader.read(4),5);self.assertEqual(reader.read(4),10)
        self.assertEqual(reader.read(32),0x5634125a)

    def test_reader_rejects_out_of_bounds_without_partial_consume(self):
        reader=Bits(b'\x01');reader.read(1)
        with self.assertRaises(ValueError):reader.read(8)
        self.assertEqual(reader.position,1)

    def test_prefix_intervals_allow_decreasing_lengths(self):
        self.assertEqual(words([2,2,1]),{0:'00',1:'01',2:'1'})
        self.assertEqual(words([1,0,2,3,0,3]),{0:'0',2:'10',3:'110',5:'111'})

    def test_singleton_rule_preserves_original_index(self):
        self.assertEqual(words([0,0,0,0,1,0]),{4:'0'})
        with self.assertRaises(ValueError):words([0,2,0])

    def test_overfull_or_incomplete_tree_rejected(self):
        for lengths in ([1,1,1],[2,2],[0,0]):
            with self.assertRaises(ValueError):words(lengths)

    def test_first16_vectors_fields_and_sizes_match_recorded_construction(self):
        old=json.loads((HERE/'fixtures/prior16-contract.json').read_bytes())['model']['cases']
        for row,expected in zip(self.rows()[:16],old):
            actual=describe(self.raw(row),row['book_index'])
            for field,key in (('dim','dim'),('entries','entries'),('used_entries','used_entries'),('dec_type','dec_type'),
                              ('dec_nodeb','node_bytes'),('dec_leafw','leaf_words'),('q_pack','q_pack'),('q_minp','q_minp'),('q_delp','q_delp'),('table_bytes','table_bytes')):
                self.assertEqual(actual[field],expected[key],(row['id'],field))
            self.assertEqual([(p['wire'],p['bits'],p['expected_by_point']['0']) for p in actual['probes']],
                             [(p['wire'],p['bits'],p['expected']) for p in expected['probes']])

    def test_map1_d16_singletons_have_q_pack0_and_distinct_both_bit_controls(self):
        rows=[r for r in self.rows() if r['id'].startswith('map1_')]
        self.assertEqual(len(rows),4)
        for row in rows:
            d=describe(self.raw(row),row['book_index']);self.assertEqual((d['dec_type'],d['q_pack'],d['dim']),(2,0,16))
            self.assertEqual([(p['wire'],p['bits']) for p in d['probes']],[(0,1),(1,1)])
            self.assertEqual([p['wire_scope'] for p in d['probes']],['preferred_zero','nonpreferred_one_tolerance_control'])
            for p in d['probes']:
                expected=list(range(1,17)) if d['q_seq'] else [1]*16
                for point in (0,-8,-24):self.assertEqual(p['expected_by_point'][str(point)],[n*(1<<-point) for n in expected])

    def test_all_sparse_wide_unused_rows_remain_in_raw_book(self):
        row=next(r for r in self.rows() if r['id']=='sparse_explicit_d16_seq0_qbits16')
        d=describe(self.raw(row),1);self.assertEqual(len(d['raw_book']['multiplicands']),6*16)
        self.assertEqual(len(bytes.fromhex(d['qval_hex'])),4*16*2)

    def test_qwidth_equivalent_full_vectors_and_scaled_fields(self):
        rows=self.rows();base=next(r for r in rows if r['id']=='sparse_explicit_d16_seq1')
        expected=describe(self.raw(base),1)
        for width in (9,16):
            row=next(r for r in rows if r['id']==base['id']+'_qbits'+str(width));actual=describe(self.raw(row),1)
            self.assertEqual(actual['q_bits'],width)
            self.assertEqual([p['expected_by_point'] for p in actual['probes']],[p['expected_by_point'] for p in expected['probes']])

    def test_floor0_dyadic_vectors_use_representable_public_positions(self):
        rows=[r for r in self.rows() if r['id'].startswith('floor0-')];self.assertEqual(len(rows),2)
        vectors=[]
        for row in rows:
            raw=self.raw(row);d=describe(raw,2,(-8,-24));vectors.append([p['expected_by_point'] for p in d['probes']])
            with self.assertRaisesRegex(ValueError,'exact signed32 point oracle'):describe(raw,2,(0,))
        self.assertEqual(vectors[0],vectors[1])

    def test_zero_delta_unit_variants_change_only_declared_fields(self):
        for row in self.rows()[-2:]:
            original=self.raw(row);changed,edits=patch_zero_fields(original,row['book_index'],row['overrides'])
            before=select(original,1);after=select(changed,1)
            self.assertEqual(before['multiplicands'],after['multiplicands']);self.assertEqual(before['lengths'],after['lengths'])
            self.assertEqual(after['delta_packed'],0);self.assertTrue(edits)
            d=describe(changed,1);self.assertEqual((d['q_del'],d['q_delp']),(0,-9997))
            for p in d['probes']:
                self.assertEqual(p['expected_by_point']['0'],[0 if 'minimum' in row['overrides'] else -1]*2)

    def test_nonzero_or_unknown_field_override_rejected(self):
        row=self.rows()[0]
        for changes in ({'delta':1},{'q_bits':0},{'minimum':False}):
            with self.assertRaises(ValueError):patch_zero_fields(self.raw(row),1,changes)

    def test_all36_host_array_formats_and_predeclared_counts(self):
        probes=calls=0;rows=self.rows();self.assertEqual(len(rows),36)
        for row in rows:
            raw,_=patch_zero_fields(self.raw(row),row['book_index'],row['overrides'])
            points=(-8,-24) if row['id'].startswith('floor0-') else (0,-8,-24)
            d=describe(raw,row['book_index'],points);self.assertEqual(len(host_table(d)),d['table_bytes'])
            probes+=len(d['probes']);calls+=len(d['probes'])*len(points)
        self.assertEqual((probes,calls),(123,365))


if __name__=='__main__':unittest.main()
