"""Reject silent resets and lost UART history independently of a soak's success flag."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'tools/runtime_run_guard.py'
SPEC = importlib.util.spec_from_file_location('runtime_guard', PATH)
GUARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARD)
BOOT = b'ESP-ROM:esp32c2-eco4-20240515\r\nBuild:May 15 2024\r\n'


class UptimeGuardTests(unittest.TestCase):
    def test_one_real_boot_and_normal_warnings(self):
        self.assertTrue(GUARD.inspect_uart(BOOT + b'W (25) wifi: test warning\n')['passed'])

    def test_a_silent_second_boot_is_not_leak_free(self):
        result = GUARD.inspect_uart(BOOT + b'running\n' + BOOT)
        self.assertFalse(result['passed'])
        self.assertEqual(result['rom_boots'], 2)
        self.assertIn('unexpected_rom_boot_count', result['errors'])

    def test_missing_startup_is_not_a_complete_capture(self):
        self.assertFalse(GUARD.inspect_uart(b'only application messages\n')['passed'])

    def test_embedded_text_is_not_a_boot_banner(self):
        self.assertTrue(GUARD.inspect_uart(BOOT + b'field: ESP-ROM:esp32c2 is text\n')['passed'])

    def test_reset_can_interrupt_an_unfinished_uart_line(self):
        result = GUARD.inspect_uart(BOOT + b'W (15) unfinished application message ' + BOOT)
        self.assertEqual(result['rom_boots'], 2)
        self.assertFalse(result['passed'])

    def test_each_panic_category_rejects(self):
        for token in GUARD.PANICS:
            with self.subTest(token=token):
                self.assertIn('panic_or_watchdog', GUARD.inspect_uart(BOOT + token)['errors'])

    def test_truncated_uart_cannot_erase_a_restart(self):
        result = GUARD.inspect_uart(BOOT, len(BOOT) * 2)
        self.assertFalse(result['passed'])
        self.assertIn('uart_history_truncated', result['errors'])


if __name__ == '__main__':
    unittest.main()
