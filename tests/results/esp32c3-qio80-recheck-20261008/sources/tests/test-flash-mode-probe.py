import sys
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/esp32c3_tests'))
from flash_mode import validate


class ProbeTests(unittest.TestCase):
    image = bytes(range(256)) * 80

    def log(self, mode='qio'):
        ctrl = 0x012c2008 if mode == 'qio' else 0x00ac2008
        env = (f'FLASH_PROBE_ENV expected={mode} ctrl=0x{ctrl:08x} '
               'clock=0x80000000 source_mhz=80 divider=1 actual_mhz=80 '
               'cpu_hz=160000000 jedec=0x464016 physical_bytes=4194304\n')
        reads = ''.join(f'FLASH_PROBE_READ pass={i} offset=0x00010000 '
                        f'bytes={len(self.image)} crc32=0x{zlib.crc32(self.image):08x}\n'
                        for i in range(1, 5))
        return env + reads + 'FLASH_PROBE_PASS normal_app_follows=1\n'

    def test_valid_modes(self):
        for mode in ('dio', 'qio'):
            self.assertEqual(validate(self.log(mode), self.image, mode)['result'], 'PASS')

    def test_faults_rejected(self):
        good = self.log()
        mutations = [
            good.replace('ctrl=0x012c2008', 'ctrl=0x00ac2008'),
            good.replace('ctrl=0x012c2008', 'ctrl=0x01ac2008'),
            good.replace('actual_mhz=80', 'actual_mhz=40'),
            good.replace('clock=0x80000000', 'clock=0x00010001'),
            good.replace('cpu_hz=160000000', 'cpu_hz=80000000'),
            good.replace('jedec=0x464016', 'jedec=0x000000'),
            good.replace('FLASH_PROBE_PASS', 'FLASH_PROBE_FAIL'),
            '\n'.join(good.splitlines()[:-1]),
            '\n'.join(line for line in good.splitlines() if 'pass=2 ' not in line),
            good.replace('pass=2 ', 'pass=1 '),
            good.replace('offset=0x00010000', 'offset=0x00009000'),
            good.replace(f'bytes={len(self.image)}', 'bytes=1234'),
            good + good,
        ]
        for i, log in enumerate(mutations):
            with self.subTest(mutation=i), self.assertRaises(ValueError):
                validate(log, self.image, 'qio')
        with self.assertRaises(ValueError):
            validate(good, b'X' + self.image[1:], 'qio')


if __name__ == '__main__':
    unittest.main()
