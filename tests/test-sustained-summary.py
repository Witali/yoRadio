"""Check that sustained-window summaries preserve bad/missing telemetry."""
import sys
from pathlib import Path
import unittest
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from summarize_sustained import window


def rows():
    result=[]
    for at in range(5,61,5):
        result += [dict(at=at,line='PERF CPU: busy=70.0% idle=30.0% heap=50000 largest=30000'),
            dict(at=at,line='PERF AAC: window 5000 ms, audio 5000 ms, decode 2000 ms')]
    return result


class SustainedSummary(unittest.TestCase):
    def test_all_samples(self):
        result=window(rows(),0,60)
        self.assertEqual(result['strict']['result'],'PASS')
        self.assertEqual(result['cpu_samples'],12)
        self.assertEqual(result['diagnostic']['audio_wall_ratio'],1)

    def test_malformed_stays_failed(self):
        data=rows();data[4]['line']='PERF CPU: busy=70.0% idle=30.0% heapw=0 bound=0'
        result=window(data,0,60)
        self.assertEqual(result['strict']['result'],'FAIL')
        self.assertEqual(len(result['malformed']),1)

    def test_missing_window_stays_failed(self):
        result=window([r for r in rows() if not 10<=r['at']<=25],0,60)
        self.assertEqual(result['strict']['result'],'FAIL')
        self.assertIn('gap',result['strict']['reason'])

    def test_no_cross_station_samples(self):
        data=rows()+[dict(at=65,line='PERF CPU: busy=99.0% idle=1.0% heap=1 largest=1')]
        self.assertEqual(window(data,0,60)['strict']['result'],'PASS')


if __name__=='__main__':unittest.main()
