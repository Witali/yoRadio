from pathlib import Path
import json
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools/esp8266_audio_profile"))
import measure_rcpdm_6144_legacy as legacy
import measure_rcpdm_6144 as modern


class LegacyTest(unittest.TestCase):
    def test_original_algorithm_not_only_two_disabled_flags(self):
        self.assertEqual(len(legacy.CONFIGS),7)
        for name,cfg in modern.CONFIGS.items():self.assertEqual(legacy.CONFIGS[name],cfg)
        for name in legacy.LEGACY:
            cfg=legacy.CONFIGS[name]
            self.assertEqual(cfg["bits"],128);self.assertEqual(cfg["bit_rate_hz"],6144000)
            self.assertEqual(cfg["state_bytes"],4);self.assertEqual(cfg["shift"],6)
            self.assertEqual(cfg["alpha"],1/64);self.assertEqual(cfg["dither"],0)
            self.assertFalse(cfg["interpolate"]);self.assertFalse(cfg["feedback_enabled"])
            self.assertEqual(cfg["fixed_delay_seconds"],0)

    def test_capture_rejects_wrong_rate_or_incomplete_reference_check(self):
        proof=dict(samples=100,variants=3,bits_per_sample=128,rc_shift=6,reference_word_state_checks=1200)
        with patch.object(legacy.subprocess,"check_output",return_value=json.dumps(proof)) as run:
            paths,got=legacy.legacy_capture(Path("exe"),Path("pcm"),Path("prefix"))
            self.assertEqual(set(paths),{"pdm128","rc128-legacy","simple128-legacy"})
            self.assertEqual(got,proof)
            self.assertEqual(run.call_args.args[0][-1],"--matched-6144")
        for field,value in (("variants",5),("bits_per_sample",32),("rc_shift",4),("reference_word_state_checks",1199)):
            with patch.object(legacy.subprocess,"check_output",return_value=json.dumps({**proof,field:value})):
                with self.assertRaises(ValueError):legacy.legacy_capture(Path("exe"),Path("pcm"),Path("prefix"))


if __name__=="__main__":unittest.main()
