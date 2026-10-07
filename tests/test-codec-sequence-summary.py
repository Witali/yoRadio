"""A fragmented later baseline cannot hide loss against the first idle heap."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from summarize_codec_sequence import summarize


class SequenceSummary(unittest.TestCase):
    def test_global_baseline_detects_persistent_fragmentation(self):
        names=('mp3','vorbis','opus')
        report=dict(board=dict(app_elf_sha256='test'),cases=[dict(name='cpu-under-http-load:'+n,result='FAIL') for n in names])
        status=[];rows=[]
        for i in range(6):
            start=i*200
            status.append(dict(case='settled-idle',started_at=start,ended_at=start+12,samples=[]))
            largest=114688 if i<3 else 59392
            for at in (start+2,start+7):
                rows.append(dict(at=at,line=f'PERF CPU: busy=10 idle=90 heap=148000 largest={largest} tasks=17'))
        for i,name in enumerate(names):
            status.append(dict(case='load:'+name,started_at=i*400+20,ended_at=i*400+200,
                               samples=[dict(request_ms=100,rssi=-60)]))
        result=summarize(report,status,rows)['cases']
        self.assertEqual(result['vorbis']['recovery_from_first']['result'],'FAIL')
        self.assertEqual(result['opus']['recovery_from_previous']['result'],'PASS')
        self.assertEqual(result['opus']['recovery_from_first']['result'],'FAIL')
        self.assertEqual(result['opus']['original_acceptance']['result'],'FAIL')


if __name__=='__main__':unittest.main()
