"""Exercise offline CLI rejection and preservation of authoritative run data."""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import analyze_tcp_runtime as cli


class CliTests(unittest.TestCase):
    """Use disposable files only; no VM, TCP connection or firmware acceptance."""
    def setUp(self):
        """Keep each run's protected data separate from new analysis artifacts."""
        self.temporary = tempfile.TemporaryDirectory(prefix='tcp-cli-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.run = self.root / 'run'
        self.run.mkdir()
        self.supervisor = self.root / 'run-supervisor'
        self.supervisor.mkdir()

    def command(self, output, diagnostic=False):
        """Invoke the real entry point with intentionally missing journal evidence."""
        args = [sys.executable, '-B', '-X', 'utf8', cli.__file__, '--run', str(self.run),
                '--repository-root', str(self.root), '--output', str(output)]
        return subprocess.run(args + (['--diagnostic'] if diagnostic else []),
                              capture_output=True, text=True, timeout=30)

    def test_existing_run_report_is_never_overwritten(self):
        target = self.run / 'report.json'
        target.write_bytes(b'original workload record\n')
        result = self.command(target)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(target.read_bytes(), b'original workload record\n')

    def test_new_output_inside_run_is_rejected(self):
        target = self.run / 'new' / 'analysis.json'
        self.assertNotEqual(self.command(target).returncode, 0)
        self.assertFalse(target.parent.exists())

    def test_existing_supervisor_record_is_never_overwritten(self):
        target = self.supervisor / 'supervisor.json'
        target.write_bytes(b'original supervisor record\n')
        self.assertNotEqual(self.command(target).returncode, 0)
        self.assertEqual(target.read_bytes(), b'original supervisor record\n')

    def test_new_output_inside_supervisor_is_rejected(self):
        target = self.supervisor / 'new' / 'analysis.json'
        self.assertNotEqual(self.command(target).returncode, 0)
        self.assertFalse(target.parent.exists())

    def test_existing_external_analysis_is_never_overwritten(self):
        target = self.root / 'analysis.json'
        target.write_bytes(b'previous analysis\n')
        self.assertNotEqual(self.command(target).returncode, 0)
        self.assertEqual(target.read_bytes(), b'previous analysis\n')

    def test_missing_evidence_fails_closed_in_both_modes(self):
        for diagnostic in (False, True):
            with self.subTest(diagnostic=diagnostic):
                target = self.root / ('diagnostic.json' if diagnostic else 'strict.json')
                result = self.command(target, diagnostic)
                self.assertEqual(result.returncode, 1)
                row = json.loads(target.read_text(encoding='utf-8'))
                self.assertEqual(row['status'], 'evidence_rejected')
                self.assertFalse(row['evidence_verified'])
                self.assertFalse(row['h10_checks_passed'])
                self.assertFalse(row['all_functionality_verified'])
                self.assertTrue(row['error'])

    def test_unrelated_sibling_directory_can_hold_rejection_artifact(self):
        target = self.root / 'run-analysis' / 'result.json'
        self.assertEqual(self.command(target).returncode, 1)
        self.assertEqual(json.loads(target.read_text())['status'], 'evidence_rejected')

    def test_file_created_during_analysis_is_preserved(self):
        target = self.root / 'race.json'

        def concurrent_writer(*args):
            """Model a second host writer, not a successful evidence audit."""
            target.write_bytes(b'concurrent writer owns this file\n')
            return {'status': 'not-evidence', 'evidence_verified': False}

        argv = ['analyze_tcp_runtime.py', '--run', str(self.run),
                '--repository-root', str(self.root), '--output', str(target)]
        with patch.object(sys, 'argv', argv), patch.object(cli, 'analyze', concurrent_writer), \
                contextlib.redirect_stdout(io.StringIO()), self.assertRaises(FileExistsError):
            cli.main()
        self.assertEqual(target.read_bytes(), b'concurrent writer owns this file\n')


def main():
    """Record host-only CLI checks and exact source identities separately from VM tests."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    files = [Path(__file__), *map(Path, cli.analysis_sources())]
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    pins = {str(path): sha(path) for path in files}
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(CliTests))
    unchanged = pins == {str(path): sha(path) for path in files}
    report = dict(passed=result.wasSuccessful() and unchanged, tests=result.testsRun,
                  inputs_sha256=pins, inputs_unchanged=unchanged, no_vm_or_hardware_access=True,
                  all_functionality_verified=False, h10_checks_passed=False,
                  scope='Host CLI data protection and rejection; no successful VM audit is mocked.',
                  failures=[str(case) for case, _ in result.failures], errors=[str(case) for case, _ in result.errors])
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
