"""The quiet-idle runner must make no board requests during its quiet window."""
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
import heap_idle


class HeapIdleTest(unittest.TestCase):
    def test_quiet_window_and_capture_cleanup(self):
        now=[0]
        calls=[]
        closed=[]
        def request(kind):
            calls.append((kind,now[0]))
            if 0<now[0]<130: raise AssertionError('HTTP request during quiet interval')
        class Board:
            def __init__(self,*_):pass
            def info(self):request('info');return dict(app_elf_sha256='test')
            def status(self):request('status');return dict(audio=False)
        class Capture:
            def __init__(self,*_):self.rows=[dict(at=10,line='PERF HEAP_WATCH: test')]
            def close(self):closed.append(True)
        class Suite:
            def __init__(self,board,*_):self.board=board
            def observe(self,seconds,*_):
                now[0]+=seconds
                return [self.board.status()]
        def sleep(seconds):
            self.assertGreaterEqual(seconds,0)
            self.assertLessEqual(seconds,10)
            now[0]+=seconds
        with tempfile.TemporaryDirectory() as folder:
            argv=['heap_idle','--board','http://test','--serial-port','fake','--output',folder]
            with patch.object(sys,'argv',argv),patch.object(heap_idle,'Board',Board),\
                 patch.object(heap_idle,'DiagnosticCapture',Capture),patch.object(heap_idle,'Suite',Suite),\
                 patch.object(heap_idle,'time',SimpleNamespace(monotonic=lambda:now[0],sleep=sleep)):
                self.assertEqual(heap_idle.main(),0)
            result=json.loads((Path(folder)/'report.json').read_text())
            self.assertEqual(result['quiet_window'],dict(started_at=0,ended_at=130,http_polls=0))
        self.assertEqual(closed,[True])
        self.assertEqual(calls,[('info',0),('status',0),('status',142),('info',142)])


if __name__=='__main__':unittest.main()
