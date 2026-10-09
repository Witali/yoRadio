"""OTA playback gates must reject AAC-core fallback and transient format matches."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
import ota
from common import Failure

SPEC=dict(rate=44100,channels=2,bits=16,label='HE-AACv2 ')
FULL=dict(audio=True,pcm_sample_rate=44100,pcm_channels=2,bits_per_sample=16,
          format='HE-AACv2 44.1 kHz stereo',channels_are_core=False)


class Clock:
    def __init__(self): self.now=0
    def monotonic(self): return self.now
    def sleep(self,seconds): self.now+=seconds


class Board:
    def __init__(self,rows): self.rows=rows;self.calls=0
    def status(self):
        row=self.rows[min(self.calls,len(self.rows)-1)];self.calls+=1
        return row


class Tests(unittest.TestCase):
    def run_gate(self,rows,spec=SPEC):
        board=Board(rows)
        with patch.object(ota,'time',Clock()):
            result=ota.wait_playback(board,spec,timeout=2)
        return result,board.calls

    def test_full_format_needs_consecutive_observations(self):
        state,calls=self.run_gate([dict(audio=False),FULL,FULL,dict(audio=False),FULL,FULL,FULL])
        self.assertEqual(state,FULL);self.assertEqual(calls,7)

    def test_rejects_core_rate_channels_and_profile(self):
        for change in (dict(pcm_sample_rate=22050),dict(pcm_channels=1),
                       dict(format='AAC PCM 44.1 kHz stereo'),dict(channels_are_core=True)):
            with self.subTest(change=change),self.assertRaises(Failure):
                self.run_gate([dict(FULL,**change)])

    def test_one_transient_match_is_insufficient(self):
        with self.assertRaises(Failure): self.run_gate([FULL,dict(audio=False)])

    def test_generic_cli_preserves_flag_check(self):
        self.assertEqual(self.run_gate([dict(audio=True)],None),(dict(audio=True),1))

    def test_transport_error_is_not_retried(self):
        class Broken:
            def status(self): raise OSError('transport failure')
        with patch.object(ota,'time',Clock()),self.assertRaises(OSError): ota.wait_playback(Broken(),SPEC)


if __name__=='__main__': unittest.main()
