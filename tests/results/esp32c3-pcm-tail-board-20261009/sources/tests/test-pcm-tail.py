"""Acceptance-parser tests: incomplete or wrong PCM tails must fail."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure
from pcm_tail import terminal_records,check_submission


def rows(frames=127,generation=8,written=4096):
    return [dict(at=1,line=f'I (100) audio_output: PERF PCM_FLUSH: frames={frames} result=0'),
        dict(at=1,line=f'I (101) audio_output: PERF STAGED_DMA: q_overruns=9 writes=2 '
                      f'written_bytes={written} write_us=100 max_write_us=50 errors=0'),
        dict(at=1,line=f'I (102) audio: PERF PCM_END: generation={generation} completion=1 result=0')]


class TailTests(unittest.TestCase):
    def setUp(self):
        self.previous=terminal_records(rows(0,6,2048))[0]

    def test_exact_submission(self):
        result=check_submission(self.previous,terminal_records(rows())[0],127,48000)
        self.assertEqual(result['submitted_bytes'],2048)

    def test_shapes(self):
        for rate in (8000,44100,48000):
            for frames in (1,127,511,512,513):
                expected=1+(frames-1)*48000//rate
                byte_count=((expected+511)//512)*2048
                end=terminal_records(rows(expected%512,8,2048+byte_count))[0]
                check_submission(self.previous,end,frames,rate)

    def test_missing_tail_rejected(self):
        with self.assertRaises(Failure):
            check_submission(self.previous,terminal_records(rows(written=2048))[0],127,48000)

    def test_wrong_padding_rejected(self):
        with self.assertRaises(Failure):
            check_submission(self.previous,terminal_records(rows(written=2048+127*4))[0],127,48000)

    def test_stale_end_rejected(self):
        with self.assertRaises(Failure):
            check_submission(self.previous,terminal_records(rows(generation=6))[0],127,48000)

    def test_missing_or_out_of_order_evidence(self):
        original=rows()
        for malformed in ([original[2]],[original[1],original[2]],
                          [original[1],original[0],original[2]]):
            with self.assertRaises(Failure): terminal_records(malformed)

    def test_merged_records_rejected(self):
        bad=rows();bad[1]['line']+=' PERF CPU: busy=1%'
        with self.assertRaises(ValueError): terminal_records(bad)
        bad=rows();bad[0]['line']+=' PERF PCM_FLUSH: frames=1 result=0'
        with self.assertRaises(Failure): terminal_records(bad)

    def test_failed_write_or_non_eof_rejected(self):
        for key,value in [('completion',2),('result',-1)]:
            current=terminal_records(rows())[0];current[key]=value
            with self.assertRaises(Failure): check_submission(self.previous,current,127,48000)
        current=terminal_records(rows())[0];current['flush']['result']=-1
        with self.assertRaises(Failure): check_submission(self.previous,current,127,48000)

    def test_tail_size_and_counter_error(self):
        with self.assertRaises(Failure): terminal_records(rows(frames=512))
        current=terminal_records(rows())[0];current['dma']['errors']=1
        with self.assertRaises(Failure): check_submission(self.previous,current,127,48000)

    def test_terminal_cannot_reuse_prior_flush(self):
        current=rows()
        with self.assertRaises(Failure): terminal_records(current+[current[-1]])


if __name__=='__main__': unittest.main()
