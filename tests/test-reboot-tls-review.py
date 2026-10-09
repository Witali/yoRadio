"""Reboot controls must not hide TLS errors, wrong reset causes or failed Stop."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/esp32c3_tests'))
from common import Failure
from reboot_tls import review_trial, stopped


class Tests(unittest.TestCase):
    def setUp(self):
        self.trial=dict(started_at=1, stop_started_at=4, reboot_started_at=8, ended_at=10)
        self.reset=dict(at=9,line='rst:0xc (RTC_SW_CPU_RST),boot:0xc (SPI_FAST_FLASH_BOOT)')

    def test_tls_is_kept_on_both_sides_of_stop_and_reboot(self):
        rows=[dict(at=t,line='TLS failure: component=esp-tls-mbedtls operation=read mbedtls_return=-76')
              for t in (3,5,8.9)] + [self.reset]
        result=review_trial(self.trial,rows)
        self.assertEqual(result['result'],'PASS')
        self.assertEqual(result['runtime_review'],'REVIEW_REQUIRED')
        self.assertEqual([r['phase'] for r in result['tls']],['playback','stop-and-settle','reboot'])
        self.assertAlmostEqual(result['tls'][-1]['seconds_before_reset'],.1)

    def test_missing_duplicate_early_and_watchdog_resets_fail(self):
        for rows in ([],[self.reset,self.reset],[dict(self.reset,at=6)],
                     [dict(at=9,line='rst:0x8 (TG1WDT_SYS_RESET),boot:0xc')]):
            self.assertEqual(review_trial(self.trial,rows)['result'],'FAIL')

    def test_faults_during_reboot_are_not_excused(self):
        for line in ('PANIC registers: MEPC=0x42000000','serial capture interrupted',
                     'allocation failed','Runtime watchdog timeout: task_watchdog=true'):
            rows=[self.reset,dict(at=8.5,line=line)]
            self.assertEqual(review_trial(self.trial,rows)['result'],'FAIL')

    def test_stop_requires_cleared_pcm_and_three_observations(self):
        idle=dict(audio=False,pcm_sample_rate=0,pcm_channels=0)
        stopped([idle]*3)
        for samples in ([idle]*2,[idle,idle,dict(idle,pcm_sample_rate=44100)],
                        [idle,idle,dict(idle,audio=True)]):
            with self.assertRaises(Failure): stopped(samples)


if __name__ == '__main__': unittest.main()
