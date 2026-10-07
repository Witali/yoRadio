import hashlib
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_aac_reserve import parse_log
EVIDENCE=ROOT/'tests/results/esp32c3-aac-scratch-20261001'

class ScratchEvidenceTests(unittest.TestCase):
    def test_qemu_and_reference_identity(self):
        report=json.loads((EVIDENCE/'qemu/result.json').read_text())
        log=(EVIDENCE/'qemu/qemu.log').read_text()
        for key,value in parse_log(log).items():self.assertEqual(report[key],value)
        for name in ('qemu.log','sdkconfig'):
            self.assertEqual(hashlib.sha256((EVIDENCE/'qemu'/name).read_bytes()).hexdigest(),
                             report['provenance'][name.replace('.','_')+'_sha256'])
        original=json.loads((ROOT/'tests/results/esp32c3-aac-radio-ram-20261001/qemu-reserve/result.json').read_text())
        for key in ('frames','channels','rate','sample_width','pcm_sha256'):
            self.assertEqual(report['pcm'][key],original['pcm'][key])
        self.assertEqual(report['pcm']['max_pcm_error_lsb'],0)

    def test_sources_and_physical_image(self):
        report=json.loads((EVIDENCE/'implementation.json').read_text())
        for path,digest in report['files'].items():
            snapshot=report.get('snapshots',{}).get(path)
            self.assertEqual(hashlib.sha256((EVIDENCE/snapshot if snapshot else ROOT/path).read_bytes()).hexdigest(),digest,path)
        folder=ROOT/'firmware/development/esp32c3-aac-scratch-radio'
        manifest=json.loads((folder/'manifest.json').read_text())
        for name,info in manifest['files'].items():
            data=(folder/name).read_bytes()
            self.assertEqual(len(data),info['bytes'])
            self.assertEqual(hashlib.sha256(data).hexdigest(),info['sha256'])
        config=(folder/'sdkconfig').read_text()
        self.assertIn('CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE=y',config)
        self.assertNotIn('CONFIG_YORADIO_QEMU=y',config)
        self.assertNotIn('CONFIG_YORADIO_DEEP_SLEEP_CLOCK=y',config)

if __name__=='__main__':unittest.main()
