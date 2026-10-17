"""Verify build logging can switch modes without losing unrelated SDK settings."""
import argparse
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CMAKE = None


class LoggingConfiguration(unittest.TestCase):
    def test_reused_build_and_windows_config_preserve_other_settings(self):
        """A DEBUG build can return to release without a clean build directory."""
        folder = ROOT.parents[1] / '.build' / 'debug-config-test'
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=folder) as temporary:
            config = Path(temporary) / 'sdkconfig'
            unrelated = 'CONFIG_TEST_VALUE="first;second"\nCONFIG_XTAL_FREQ_26=y\n'
            config.write_bytes((unrelated + 'CONFIG_LOG_DEFAULT_LEVEL_VERBOSE=y\n'
                                'CONFIG_LOG_MAXIMUM_LEVEL_VERBOSE=y\n'
                                'CONFIG_BOOTLOADER_LOG_LEVEL_VERBOSE=y\n'
                                'CONFIG_LOG_BOOTLOADER_LEVEL_VERBOSE=y\n').replace('\n', '\r\n').encode())
            for mode, level in [('OFF', 'WARN'), ('ON', 'DEBUG'), ('OFF', 'WARN')]:
                command = [CMAKE, '-DDEBUG=' + mode, '-DSDKCONFIG=' + str(config),
                           '-P', str(ROOT / 'cmake/debug_logging.cmake')]
                subprocess.run(command, check=True, capture_output=True)
                text = config.read_text()
                self.assertIn(unrelated, text)
                for prefix in ('LOG_DEFAULT_LEVEL', 'BOOTLOADER_LOG_LEVEL'):
                    selected = [line for line in text.splitlines()
                                if line.startswith('CONFIG_' + prefix + '_') and line.endswith('=y')]
                    self.assertEqual(selected, [f'CONFIG_{prefix}_{level}=y'])
                self.assertNotIn('CONFIG_LOG_BOOTLOADER_LEVEL_VERBOSE=y', text)
                self.assertIn('CONFIG_LOG_MAXIMUM_EQUALS_DEFAULT=y', text)
                self.assertNotIn('CONFIG_LOG_MAXIMUM_LEVEL_VERBOSE=y', text)
                before = config.stat().st_mtime_ns
                subprocess.run(command, check=True, capture_output=True)
                self.assertEqual(config.stat().st_mtime_ns, before)
            # ESP-IDF may expand the selected choice and use Windows newlines.
            config.write_bytes((config.read_text() + 'CONFIG_LOG_DEFAULT_LEVEL=2\n').replace('\n', '\r\n').encode())
            before = config.stat().st_mtime_ns
            subprocess.run(command, check=True, capture_output=True)
            self.assertEqual(config.stat().st_mtime_ns, before)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cmake', required=True)
    options = parser.parse_args()
    CMAKE = options.cmake
    unittest.main(argv=[__file__])
