"""Fail closed on unknown clock drivers and corrupt readback; verify divider math."""
import hashlib
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'tools/esp32c3_tests')]
from patch_i2s_pdm_clock import patch, SOURCE_SHA256, OVERRIDE, DECLARATIONS, GUARD, SNAPSHOT, REPORT
from pdm_clock import parse


def record(**overrides):
    fields = dict(sclk=160000000, source=2, integer=2, x=1, y=1, z=0,
                  yn1=0, bdiv=13, osr=2, fp=960, fs=480)
    fields.update(overrides)
    return 'I (100) i2s_pdm: PERF PDM_CLOCK: '+' '.join(f'{k}={v}' for k,v in fields.items())


class ClockTests(unittest.TestCase):
    def test_integer_and_exact_fractional_readback(self):
        integer = parse(record())
        self.assertEqual(integer['nominal_pcm_hz_fraction'], '625000/13')
        self.assertAlmostEqual(integer['error_ppm'], 1602.5641025641)
        self.assertFalse(integer['exact_nominal_48khz'])
        precise = parse(record(x=311, y=0, z=1))
        self.assertEqual(precise['divider'], '625/312')
        self.assertEqual(precise['nominal_pcm_hz_fraction'], '48000')
        self.assertTrue(precise['exact_nominal_48khz'])

    def test_bad_or_unscoped_registers_are_not_measurements(self):
        for fields in [dict(integer=0), dict(z=512), dict(source=0), dict(osr=0),
                       dict(fp=625, fs=312), dict(x=311, y=1, z=1), dict(yn1=1), dict(bdiv=0)]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                parse(record(**fields))
        for line in [record().replace(' x=1',''), record()+' PERF CPU:',
                     record().replace('PDM_CLOCK:', 'PDM_CLOCK'), record().replace('z=0','z=-1')]:
            with self.subTest(line=line), self.assertRaises(ValueError): parse(line)
        self.assertIsNone(parse('unrelated diagnostic'))

    def test_audited_source_and_only_explicit_insertions(self):
        source = (ROOT/'tests/results/esp32c3-heap-pacing-20261009/clock-sources/driver.c').read_bytes()
        normalized = source.decode().replace('\r\n','\n')
        self.assertEqual(hashlib.sha256(normalized.encode()).hexdigest(), SOURCE_SHA256)
        updated = patch(source).decode()
        self.assertEqual(patch(normalized.encode()), updated.encode())
        # Undo the defined insertions and recover the exact SDK source. This
        # catches accidental RX, locking, error-path and cached-clock edits.
        restored = updated
        for addition in (DECLARATIONS, GUARD, SNAPSHOT, REPORT):
            self.assertEqual(restored.count(addition), 1)
            restored = restored.replace(addition, '')
        restored = restored.replace('#ifndef CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK\n'+OVERRIDE+'\n#endif', OVERRIDE)
        self.assertEqual(restored, normalized)
        tx = updated[updated.index('static esp_err_t i2s_pdm_tx_set_clock('):]
        self.assertLess(tx.index(SNAPSHOT), tx.index('portEXIT_CRITICAL'))
        self.assertGreater(tx.index(REPORT), tx.index('portEXIT_CRITICAL'))
        self.assertLess(tx.index(GUARD), tx.index('esp_clk_tree_enable_src'))

    def test_unknown_and_double_patched_sdk_rejected(self):
        source = (ROOT/'tests/results/esp32c3-heap-pacing-20261009/clock-sources/driver.c').read_bytes()
        for value in (source+b'\n', source.replace(b'clk_info.mclk_div', b'other_divider'), patch(source)):
            with self.assertRaisesRegex(ValueError, 'Unaudited'): patch(value)

    def test_integer_compensation_keeps_noise_workaround_and_guard(self):
        source = (ROOT/'tests/results/esp32c3-heap-pacing-20261009/clock-sources/driver.c').read_bytes()
        updated = patch(source).decode()
        # Only fractional mode may remove the integer write. Compensation
        # must also validate the hardcoded 625000/13 ratio before use.
        self.assertIn('#ifndef CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK\n'+OVERRIDE+'\n#endif', updated)
        self.assertIn('defined(CONFIG_YORADIO_PDM_INTEGER_RATE_COMPENSATION)', GUARD)
        self.assertIn('clk_info.mclk_div == 2U', GUARD)
        self.assertIn('clk_info.sclk == YORADIO_PDM_SOURCE_HZ', GUARD)


if __name__ == '__main__':
    unittest.main()
