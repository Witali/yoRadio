from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from rx_ownership import analyze


class OwnerChecks(unittest.TestCase):
    def rows(self):
        return [dict(at=1,line='PERF RX_OWNER: seq=1 live=2 peak=2 allocs=5 frees=3 lost=0 unmatched=0 payload=1724 metadata=64 missing=0 walk_us=100'),
                dict(at=1,line='PERF RX_BLOCK: seq=1 id=4 payload=0x1000 payload_bytes=1724 metadata=0x2000 metadata_bytes=32'),
                dict(at=1,line='PERF RX_BLOCK: seq=1 id=5 payload=0x1000 payload_bytes=1724 metadata=0x2100 metadata_bytes=32')]
    def test_shared_payload_counted_once(self):
        result=analyze(self.rows())
        self.assertEqual(result['maximum_allocated_payload_bytes'],1788)
        self.assertEqual(result['snapshots'][0]['unique_blocks'],3)
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
