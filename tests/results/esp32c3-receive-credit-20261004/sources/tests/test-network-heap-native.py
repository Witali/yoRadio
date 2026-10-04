"""Compile the actual network sampler with sanitizers (GCC, or GCC in WSL)."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NativeNetworkHeapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if shutil.which('gcc'):
            cls.prefix = []
        elif os.name == 'nt' and shutil.which('wsl.exe'):
            cls.prefix = ['wsl.exe', '--exec']
        else:
            raise unittest.SkipTest('GCC or WSL GCC is required')
        subprocess.run(cls.prefix+['gcc', '--version'], check=True, capture_output=True)

    def path(self, value):
        path = str(Path(value).resolve()).replace('\\', '/')
        return '/mnt/'+path[0].lower()+path[2:] if self.prefix else path

    def compile_run(self, source, include, definitions=()):
        (ROOT/'.build').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='network-heap-native-', dir=ROOT/'.build') as directory:
            output = Path(directory)/'test'
            if isinstance(source, str):
                source_path = Path(directory)/'test.c'
                source_path.write_text(source, encoding='utf-8')
            else:
                source_path = source
            command = self.prefix+['gcc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                '-fsanitize=address,undefined', *definitions, '-I', self.path(include),
                self.path(source_path), '-o', self.path(output)]
            subprocess.run(command, check=True, capture_output=True, text=True)
            return subprocess.run(self.prefix+[self.path(output)], check=True, capture_output=True, text=True).stdout

    def test_callback_lifetime_queues_failures_and_context(self):
        result = self.compile_run(ROOT/'tests/native/network_heap_profile_test.c',
                                  ROOT/'tests/native/network_heap_profile_stubs',
                                  ['-DCONFIG_YORADIO_NETWORK_HEAP_PROFILE=1'])
        self.assertIn('callback lifecycle: PASS', result)

    def test_disabled_header_links_without_lwip_or_freertos(self):
        # Only sdkconfig.h is supplied. The disabled path must have no other SDK
        # dependency and must link without the sampler or any lwIP functions.
        with tempfile.TemporaryDirectory(prefix='network-heap-off-', dir=ROOT/'.build') as directory:
            Path(directory, 'sdkconfig.h').write_text('/* disabled */\n')
            header = self.path(ROOT/'idf/esp32c3-oled-native/main/network_heap_profile.h')
            code = f'#include "{header}"\nint main(void) {{ network_heap_profile_poll(); return 0; }}\n'
            self.compile_run(code, directory)


if __name__ == '__main__':
    unittest.main()
