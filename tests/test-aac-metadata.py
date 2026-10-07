"""Retained real-library evidence and rejection of misleading AAC profile results."""
import hashlib
import gzip
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/codec_benchmark'))
from run_aac_metadata import parse_log

DATA=ROOT/'tests/results/esp32c3-aac-metadata-20261004'


class MetadataTests(unittest.TestCase):
    def test_retained_metadata_runs(self):
        for variant,frames,resets in (('plain',93,0),('reference',104,1),('pc19',104,1)):
            saved=json.loads((DATA/variant/'result.json').read_text())
            actual=parse_log((DATA/variant/'diagnostics.log').read_text())
            for key,value in actual.items():self.assertEqual(value,saved[key],(variant,key))
            self.assertEqual(actual['frames'],frames)
            self.assertEqual(actual['resets'],resets)
            self.assertFalse(actual['precision_qualified'])

    def test_mono_upmix_cannot_be_labeled_ps(self):
        log=(DATA/'plain/diagnostics.log').read_text()
        with self.assertRaisesRegex(ValueError,'Wrong native metadata'):
            parse_log(log.replace('case=he_mono_metadata label=HE-AAC ',
                                  'case=he_mono_metadata label=HE-AACv2 '))
        with self.assertRaisesRegex(ValueError,'Wrong native metadata'):
            parse_log(log.replace('source_channels=1 pcm_channels=2','source_channels=2 pcm_channels=2'))

    def test_partial_or_failed_run_is_rejected(self):
        log=(DATA/'pc19/diagnostics.log').read_text()
        for invalid in (log.replace('QEMU_AAC_FORMAT_PASS','incomplete'),
                        log.replace('AAC_METADATA_RESET_PASS','missing'),
                        log+'\nassert failed: regression\n',
                        log.replace('AAC_METADATA_PASS frames=104','AAC_METADATA_PASS frames=103')):
            with self.assertRaises(ValueError):parse_log(invalid)

    def test_exact_pcm_and_unchanged_adapter_memory(self):
        result=json.loads((DATA/'comparison.json').read_text())
        for row in result['pcm']:
            self.assertGreater(row['channel_samples'],0)
            self.assertEqual(row['max_error_lsb'],0)
            self.assertEqual(row['different'],0)
            self.assertEqual(row['reference_pcm_sha256'],row['candidate_pcm_sha256'])
        self.assertEqual({r['case'] for r in result['pcm']},
                         {'pc19-gaps','reference-gaps','pc19-late','reference-late','pc19-groovesalad16'})
        for row in result['pcm']:
            if 'baseline' not in row:continue
            variant,kind=row['case'].split('-')
            current=gzip.decompress((DATA/variant/(kind+'.pcm.gz')).read_bytes())
            baseline=gzip.decompress((ROOT/row['baseline']).read_bytes())
            self.assertEqual(current,baseline)
            self.assertEqual(hashlib.sha256(current).hexdigest(),row['candidate_pcm_sha256'])
        sizes=result['adapter_bytes']
        self.assertEqual(sizes['gap-pc19-side'],sizes['metadata-pc19'])
        self.assertEqual(sizes['late-reference'],sizes['metadata-reference'])
        self.assertEqual(sizes['metadata-plain'],28)
        self.assertEqual(result['recording_format'],dict(label='HE-AAC',source_channels=1,
                         pcm_channels=2,rate=32000,pcm_only=False))

    def test_evidence_fingerprints(self):
        manifest=json.loads((DATA/'manifest.json').read_text())
        for name,digest in manifest['files'].items():
            self.assertEqual(hashlib.sha256((DATA/name).read_bytes()).hexdigest(),digest,name)


if __name__=='__main__':unittest.main()
