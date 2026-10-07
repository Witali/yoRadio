"""Reject damaged ownership captures instead of attributing guessed allocations."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from heap_fragment import analyze

class HeapFragmentLog(unittest.TestCase):
    def rows(self):
        return [dict(at=0,line='PERF HEAP_WATCH: seq=1 first=0x1000 last=0x2000 live=1 peak=2 lost=0 alloc_events=3 free_events=2 rows=2 dropped=0 unknown=0 walk_us=200'),
                dict(at=0,line='PERF HEAP_OWNER: seq=1 row=0 address=0x1000 bytes=32 id=3 requested=32 task=tiT'),
                dict(at=0,line='PERF HEAP_OWNER: seq=1 row=1 address=0x1024 bytes=4060 id=0 requested=0 task=free')]

    def test_owner_and_free(self):
        result=analyze(self.rows())
        self.assertTrue(result['complete'])
        self.assertEqual(result['snapshots'][0]['largest_raw_free'],4060)
        self.assertEqual(result['snapshots'][0]['blocks'][0]['task'],'tiT')

    def test_missing_duplicate_overflow_unknown_and_corruption(self):
        rows=self.rows()
        invalid=[rows[:-1],rows+[rows[-1]],rows[1:]]
        for old,new in [('lost=0','lost=1'),('unknown=0','unknown=1'),('rows=2','rows=3'),('live=1','live=2')]:
            invalid.append([dict(r,line=r['line'].replace(old,new)) for r in rows])
        invalid.append([dict(r,line=r['line'].replace('requested=32','requested=x')) for r in rows])
        invalid.append(rows+[dict(r,line=r['line'].replace('seq=1','seq=3')) for r in rows])
        invalid.append([dict(r,line=r['line'].replace('address=0x1024','address=0x1010')) for r in rows])
        invalid.append(rows+[dict(r,line=r['line'].replace('seq=1','seq=2').replace('task=tiT','task=httpd')) for r in rows])
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):analyze(value)

if __name__=='__main__':unittest.main()
