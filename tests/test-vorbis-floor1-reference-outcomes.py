"""Reference refusals must be decoder errors, never process or output failures."""
import importlib.util
from pathlib import Path
import struct
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('floor1_reference_checker', ROOT / 'tests/check-vorbis-floor1-render.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class ReferenceOutcomes(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='floor1-reference-outcomes-', dir=ROOT / '.build')
        self.out = Path(self.directory.name).resolve()
        self.assertTrue(self.out.is_relative_to((ROOT / '.build').resolve()))
        self.addCleanup(self.directory.cleanup)
        self.check = checker.Checker(self.out)
        self.wav = self.out / 'case.wav'
        self.command = dict(state='terminal', reaped=True, returncode=3199971767)
        self.codec_error = ('[libvorbis @ 000002962835ef00] 3. vorbis header damaged\n'
            '[aist#0:0/vorbis @ 0000029628364140] [dec:libvorbis @ 0000029628366700] '
            'Error while opening decoder: Invalid data found when processing input\n')
        self.stderr = (self.codec_error + 'Error opening output file ' + str(self.wav) + '.\n'
            'Error opening output files: Invalid data found when processing input\n')

    def outcome(self, command=None, stderr=None, valid=False):
        return self.check.reference_outcome(self.command if command is None else command,
            self.stderr if stderr is None else stderr, self.wav, dict(expected_valid=valid))

    def write_wav(self, channels=2, rate=48000, frames=7040):
        with wave.open(str(self.wav), 'wb') as stream:
            stream.setparams((channels, 2, rate, 0, 'NONE', 'not compressed'))
            stream.writeframes(struct.pack('<h', 317) * channels * frames)

    def test_actual_decoder_refusal_and_secondary_path_diagnostic(self):
        for code in (1, -1094995529, 3199971767):
            with self.subTest(code=code):
                pcm, fact = self.outcome(dict(self.command, returncode=code))
                self.assertEqual(pcm, b'')
                self.assertTrue(fact['codec_rejection'])
                self.assertIsNone(fact['wav_sha256'])

    def test_process_failures_never_count_as_codec_refusals(self):
        for change in (dict(returncode=0), dict(returncode=-11), dict(returncode=3221225477),
                       dict(state='tool_or_timeout_nonpass'), dict(reaped=False), dict(forced_stop=True)):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.outcome(dict(self.command, **change))

    def test_environment_errors_remain_nonpassing_after_codec_diagnostic(self):
        for error in ('Permission denied', 'No such file or directory', 'Unknown decoder', 'Error writing trailer'):
            with self.subTest(error=error), self.assertRaises(ValueError):
                self.outcome(stderr=self.stderr + error + '\n')

    def test_output_error_requires_the_bound_path_and_decoder_reason(self):
        wrong = self.stderr.replace(str(self.wav), str(self.out / 'other.wav'))
        reversed_order = self.stderr[len(self.codec_error):] + self.codec_error
        for text in (wrong, reversed_order, self.stderr.replace('output files: Invalid data found when processing input',
                     'output files: Invalid argument'), self.stderr.replace(self.codec_error, '')):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.outcome(stderr=text)

    def test_refused_header_cannot_publish_pcm(self):
        self.write_wav()
        with self.assertRaises(ValueError):
            self.outcome()

    def test_valid_reference_has_complete_original_stereo_pcm(self):
        self.write_wav()
        pcm, fact = self.outcome(dict(self.command, returncode=0), stderr='', valid=True)
        self.assertEqual(len(pcm), 28160)
        self.assertEqual(fact['metadata']['frames'], 7040)
        self.assertFalse(fact['codec_rejection'])

    def test_valid_reference_cannot_change_channels_rate_or_length(self):
        for values in (dict(channels=1), dict(rate=44100), dict(frames=7039)):
            with self.subTest(values=values):
                self.write_wav(**values)
                with self.assertRaises(ValueError):
                    self.outcome(dict(self.command, returncode=0), stderr='', valid=True)

    def test_pcm_errors_use_signed_samples_and_include_both_channels(self):
        left = struct.pack('<4h', -32768, 23, 7, -11)
        right = struct.pack('<4h', 32767, 25, 4, -11)
        result = checker.metrics(left, right)
        self.assertEqual(result, dict(samples=4, max_abs_error=65535, over_bound=2, allowed=2))
        with self.assertRaises(ValueError):
            checker.metrics(left, right[:-2])


if __name__ == '__main__':
    unittest.main()
