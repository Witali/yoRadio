"""Verify the EOF heap checkpoint does not implicitly issue Stop."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure, check_recovery_heap
from run import Suite
from summarize_terminal_memory import summarize


class TerminalMemory(unittest.TestCase):
    def test_checkpoint_without_stop_and_default_stop(self):
        class Board:
            stops=0
            def stop(self): self.stops+=1
        class Capture:
            port=True
            def since(self, started):
                return [dict(at=started+i,line='PERF CPU: heap=94000 largest=59000 tasks=17') for i in (1,6)]
        board=Board()
        with tempfile.TemporaryDirectory() as folder:
            suite=Suite(board,'unused',{},Capture(),Path(folder))
            suite.observe=lambda seconds,name: None
            observed=suite.idle_heap(stop=False)
            self.assertEqual(board.stops,0)
            self.assertEqual(len(observed),2)
            suite.idle_heap()
            self.assertEqual(board.stops,1)
            with self.assertRaisesRegex(Failure,'Persistent heap loss'):
                check_recovery_heap([dict(heap=148000,largest=110000,tasks=17)]*2,observed)

    def test_summary_rejects_stop_masking(self):
        def report(stop):
            cases=[dict(name='flac:auto:'+name,result='PASS',evidence=dict(explicit_stop=flag,
                samples=[dict(heap=148000,largest=110000,tasks=17)]*2))
                for name,flag in [('idle-before',True),('idle-without-stop',stop),('idle-after-stop',True)]]
            cases += [dict(name='flac:auto:'+name,result='PASS')
                      for name in ('eof-recovery','stop-recovery','play-to-eof')]
            return dict(board=dict(app_elf_sha256='test'),cases=cases)
        self.assertEqual(summarize(report(False))['streams']['flac:auto']['eof_heap_loss'],0)
        with self.assertRaisesRegex(ValueError,'masked'): summarize(report(True))


if __name__=='__main__':unittest.main()
