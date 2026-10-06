"""Statistical regression checks: sample weighting, CPU windows and pair identity."""
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
sys.path.insert(0,str(ROOT/'tools/esp32c3_tests'))
from analyze_radio_flac import summarize_trace, instrument
from summarize_radio_flac import cpu_intervals, cpu_summary, decode_summary
from radio_flac_study import paired_order


def cpu(at, tick, busy, decode=20):
    return dict(at=at, line=f'I ({tick}) cpu_profile: PERF CPU: busy={busy}% idle={100-busy}% '
                f'stream=5.0% decode={decode}% output=3.0% wifi=10.0% tcpip=0.0% web=2.0% heap=100000 largest=50000 tasks=17')


class RadioStudy(unittest.TestCase):
    def test_lpc_uses_channel_samples_not_subframe_count(self):
        trace = ('RADIO_FRAME ch=0 block=1024 type=63 depth=24\n'
                 'RADIO_LPC ch=0 block=1024 order=32 nonzero=30 rolling=1\n'
                 'RADIO_FRAME ch=0 block=4608 type=43 depth=24\n'
                 'RADIO_LPC ch=0 block=4608 order=12 nonzero=12 rolling=0\n'
                 'RADIO_FRAME ch=0 block=4608 type=12 depth=24\n')
        stats = summarize_trace(trace)
        self.assertEqual(stats['lpc32_percent_all'],10)
        self.assertAlmostEqual(stats['lpc32_percent_lpc'],100*1024/5632)
        self.assertAlmostEqual(stats['mean_order_all_channel_samples'],(32*1024+12*4608+4*4608)/10240)
        self.assertEqual(stats['max_order'],32)
        with self.assertRaises(ValueError):
            summarize_trace(trace.replace('RADIO_LPC ch=0 block=4608 order=12 nonzero=12 rolling=0\n',''))

    def test_whole_cpu_intervals_and_time_weighted_saturation(self):
        rows = [cpu(100,1000,5),cpu(105,6000,50),cpu(111,12000,99.9),cpu(116,17000,99.8)]
        windows, malformed, gaps = cpu_intervals(rows,104,116)
        self.assertEqual([w['seconds'] for w in windows],[6,5])
        self.assertFalse(malformed or gaps)
        stats = cpu_summary(windows)
        self.assertAlmostEqual(stats['busy_mean_percent'],(6*99.9+5*99.8)/11)
        self.assertAlmostEqual(stats['at_least_99.9_percent']['observed_time_percent'],100*6/11)
        self.assertEqual(stats['decode_mean_percent'],20)

    def test_malformed_cpu_is_missing_evidence_not_zero_load(self):
        broken = cpu(110,11000,100)
        broken['line'] = broken['line'].replace('decode=20%','decode=')
        rows = [cpu(100,1000,5),cpu(105,6000,50),broken,cpu(115,16000,80)]
        windows, malformed, gaps = cpu_intervals(rows,100,115)
        self.assertEqual(len(malformed),1)
        self.assertEqual(len(windows),2)
        self.assertEqual(cpu_summary(windows)['busy_mean_percent'],65)
        self.assertNotIn('busy_mean_percent',cpu_summary([]))

    def test_log_gap_is_preserved(self):
        windows, malformed, gaps = cpu_intervals([cpu(100,1000,5),cpu(115,16000,100)],100,115)
        self.assertEqual(len(gaps),1)
        self.assertEqual(gaps[0]['seconds'],15)
        self.assertFalse(windows)
        self.assertNotIn('busy_mean_percent',cpu_summary(windows))

    def test_invalid_percentages_are_not_usable_measurements(self):
        broken=cpu(105,6000,120)
        windows, malformed, gaps=cpu_intervals([cpu(100,1000,5),broken],100,110)
        self.assertEqual(len(malformed),1)
        self.assertFalse(windows)

    def test_decode_cost_is_per_audio_time(self):
        rows = [dict(at=105,line='PERF FLAC: window 5000 ms, audio 1000 ms, decode 800 ms'),
                dict(at=110,line='PERF FLAC: window 5000 ms, audio 5000 ms, decode 1000 ms')]
        stats = decode_summary(rows,100,110)
        self.assertEqual(stats['audio_wall_ratio'],.6)
        self.assertEqual(stats['elapsed_decode_ms_per_audio_second'],300)
        self.assertEqual(stats['audio_shortfall_percent'],40)
        self.assertEqual(decode_summary(rows,106,110)['elapsed_decode_ms_per_audio_second'],None)

    def test_pairs_require_identical_pcm_and_alternate_order(self):
        entries = [dict(station=s,name=f'{s}-{order}',max_lpc_order=order,
                        pcm24_sha256=s,pcm24_bytes=100,pcm_sha256=s,rate=44100,channels=2,bits=24,seconds=120)
                   for s in ('a','b') for order in (32,12)]
        self.assertEqual(paired_order(entries),['a-32','a-12','b-12','b-32'])
        entries[1]['pcm24_sha256']='different'
        with self.assertRaises(AssertionError):
            paired_order(entries)

    def test_instrumentation_anchors_are_unique(self):
        source=(ROOT/'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp').read_text()
        observed=instrument(source)
        self.assertEqual(observed.count('RADIO_FRAME '),1)
        self.assertEqual(observed.count('RADIO_LPC '),1)
        with self.assertRaises(ValueError):
            instrument(source.replace('    sampleDepth -= shift;',''))


if __name__ == '__main__':
    unittest.main()
