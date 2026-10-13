from pathlib import Path
import sys
import unittest
import struct
import zlib

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from rx_ownership import analyze, fields, OWNER_FIELDS, OWNER3_FIELDS, BLOCK_FIELDS


class OwnerChecks(unittest.TestCase):
    def rows(self):
        return [dict(at=1,line='PERF RX_OWNER: seq=1 live=2 peak=2 allocs=5 frees=3 lost=0 unmatched=0 payload=1724 metadata=64 missing=0 walk_us=100'),
                dict(at=1,line='PERF RX_BLOCK: seq=1 id=4 payload=0x1000 payload_bytes=1724 metadata=0x2000 metadata_bytes=32'),
                dict(at=1,line='PERF RX_BLOCK: seq=1 id=5 payload=0x1000 payload_bytes=1724 metadata=0x2100 metadata_bytes=32')]
    def test_shared_payload_counted_once(self):
        result=analyze(self.rows())
        self.assertEqual(result['maximum_allocated_payload_bytes'],1788)
        self.assertEqual(result['snapshots'][0]['unique_blocks'],3)
    def compact_rows(self):
        result = []
        for row in self.rows():
            owner = 'RX_OWNER:' in row['line']
            marker = 'PERF RX_OWNER:' if owner else 'PERF RX_BLOCK:'
            keys = OWNER_FIELDS if owner else BLOCK_FIELDS
            values = fields(row['line'], marker)
            crc = zlib.crc32(struct.pack('<'+'I'*len(keys), *(values[k] for k in keys)))
            tokens = [f'{values[k]:08x}' if not owner and k in ('payload','metadata')
                      else str(values[k]) for k in keys]
            result.append(dict(row, line=marker.replace(':','2:')+' '+','.join(tokens)+f',{crc:08x}'))
        return result
    def test_checksummed_format_matches_legacy_and_reduces_burst(self):
        compact = self.compact_rows()
        self.assertEqual(analyze(compact), analyze(self.rows()))
        self.assertLess(sum(len(r['line']) for r in compact), .6*sum(len(r['line']) for r in self.rows()))
    def paired_rows(self, free=100000, largest=64000):
        rows=self.compact_rows()
        values=fields(rows[0]['line'],'PERF RX_OWNER2:')
        values.update(heap_free=free,heap_largest=largest)
        words=[values[k] for k in OWNER3_FIELDS]
        crc=zlib.crc32(struct.pack('<'+'I'*len(words),*words))
        rows[0]['line']='PERF RX_OWNER3: '+','.join(map(str,words))+f',{crc:08x}'
        return rows
    def test_paired_heap_preserves_owner_accounting(self):
        result=analyze(self.paired_rows())
        self.assertEqual(result['maximum_allocated_payload_bytes'],1788)
        snapshot=result['snapshots'][0]
        self.assertEqual((snapshot['heap_free'],snapshot['heap_largest']),(100000,64000))
    def test_paired_heap_corruption_and_inconsistency_rejected(self):
        for rows in (self.paired_rows(free=100,largest=101),
                     self.paired_rows()):
            if '100000' in rows[0]['line']:
                rows[0]['line']=rows[0]['line'].replace('100000','100001')
            with self.assertRaises(ValueError):analyze(rows)
    def test_changed_missing_reordered_values_and_crc_rejected(self):
        original = self.compact_rows()
        for before, after in [('1,2,2,5', '1,2,2,6'), ('00001000', '00001001'),
                              ('1724,00002000', '172,00002000'),
                              ('1,2,2,5,3', '1,2,5,2,3'),
                              ('1,2,2,5', '4294967296,2,2,5')]:
            modified = [dict(r, line=r['line'].replace(before, after)) for r in original]
            with self.subTest(before=before), self.assertRaises(ValueError):
                analyze(modified)
        for index in range(len(original)):
            modified = [dict(r) for r in original]
            modified[index]['line'] = modified[index]['line'][:-1]
            with self.subTest(index=index), self.assertRaises(ValueError):
                analyze(modified)
    def test_negative_controls(self):
        for before,after in [('lost=0','lost=1'),('missing=0','missing=1'),('frees=3','frees=2'),
                             ('live=2','live=3'),('peak=2','peak=1'),('payload=1724','payload=3448')]:
            rows=self.rows();rows[0]['line']=rows[0]['line'].replace(before,after)
            with self.assertRaises(ValueError):analyze(rows)
        rows=self.rows();rows[-1]['line']=rows[-1]['line'].replace('id=5','id=6')
        with self.assertRaises(ValueError):analyze(rows)
        rows=self.rows()+[dict(at=2,line=self.rows()[0]['line'].replace('seq=1','seq=3'))]
        with self.assertRaises(ValueError):analyze(rows)
        with self.assertRaises(ValueError):analyze(self.rows()+[dict(at=2,line='serial capture interrupted')])
        for rows in [[],self.rows()[:-1],self.rows()+[self.rows()[-1]],self.rows()[1:],self.rows()*2,
                     [dict(at=1,line=self.rows()[0]['line'].split(' missing=')[0])],
                     [dict(at=1,line=self.rows()[0]['line']+self.rows()[1]['line'])]]:
            with self.assertRaises(ValueError):analyze(rows)


if __name__=='__main__':unittest.main()
