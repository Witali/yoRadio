"""Run the real JPEG object through partial NOR I/O failures and same-object recovery."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

HERE = Path(__file__).resolve().parent
PROBE = HERE.parent / 'jpeg_library_probe'


def sha(path):
    """Identify exact inputs and decoded pixel bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, environment=None):
    """A crash or timeout is a failure, never a handled flash error."""
    return subprocess.run([str(p) for p in command], env=environment, capture_output=True, timeout=30)


def points(count, exhaustive):
    """Sweep every small-image physical callback; sample full-size boundaries and passes."""
    if exhaustive:
        return range(1, count + 1)
    return sorted(set(range(1, min(count, 32) + 1)) | set(range(max(1, count - 3), count + 1)) |
                  {n for center in (count * i // 8 for i in range(1, 8))
                   for n in range(center - 1, center + 2) if 1 <= n <= count})


def main():
    """REQUESTED_CHANGE: preserve physical bytes after a failed callback and abort.

    Mode1 performs real partial read/program/erase and returns an I/O error.
    Mode2 silent corrupt reads are not claimed detectable by an unhashed scratch
    stream; silent write/erase verification is covered in the separate NOR tests.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-build', type=Path, required=True)
    parser.add_argument('--candidate-build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    builds = [json.loads((p / 'build.json').read_text()) for p in (args.reference_build, args.candidate_build)]
    assert builds[0]['backing_backend'] == 'stdio' and builds[1]['backing_backend'] == 'shared-nor-model'
    inputs = {str(Path(__file__).resolve()): sha(Path(__file__))}
    for build in builds:
        assert build['upstream_commit'] == 'c85e6b905bf237038faa936dab160ebfc5da0344'
        for name, digest in build['probe_inputs'].items():
            p = (PROBE / name).resolve()
            assert sha(p) == digest, p
            inputs[str(p)] = digest
        for name, digest in build['backing_fixture_inputs'].items():
            assert sha(Path(name)) == digest, name
            inputs[name] = digest
        assert sha(Path(build['executable'])) == build['executable_sha256']
        inputs[build['executable']] = build['executable_sha256']
    reference, candidate = [b['executable'] for b in builds]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    fixtures = output / 'fixtures'
    fixtures.mkdir()
    bad, good, expected = [output / p for p in ('first.raw', 'recovery.raw', 'expected.raw')]
    clean_env = {k: v for k, v in os.environ.items() if not k.startswith('SMALL_TV_NOR_')}
    report = dict(passed=False, hardware_tested=False, production_integration=False,
                  runner_sha256=sha(Path(__file__)), builds=builds, cases=[], inputs_sha256=inputs)
    started = time.perf_counter()
    try:
        for mode, bits, size in [('cmyk-progressive', 8, (31, 17)),
                                 ('ycck-progressive', 12, (31, 17)),
                                 ('arith-progressive', 8, (31, 17)),
                                 ('progressive420', 12, (240, 240)),
                                 ('ycck-progressive', 12, (240, 240)),
                                 ('cmyk-progressive', 8, (240, 240)),
                                 ('cmyk-progressive', 12, (240, 240))]:
            width, height = size
            name = f'{mode}-{bits}-{width}x{height}'
            image = fixtures / (name + '.jpg')
            generated = run([reference, 'generate', image, 'rich-' + mode + '-q83', bits, width, height, 1, 0, 0])
            assert generated.returncode == 0, generated.stderr
            decoded = run([reference, 'decode', image, expected, 0, 0])
            assert decoded.returncode == 0, decoded.stderr
            expected_sha = sha(expected)

            def exercise(ordinal):
                """One process retains both the JPEG object and partial physical temp data."""
                env = dict(clean_env, SMALL_TV_NOR_FAIL_AT=str(ordinal), SMALL_TV_NOR_FAULT_MODE='1')
                result = run([candidate, 'reuse', image, bad, good, 65536, 1, 'none', 0, 0], env)
                assert result.returncode == 0, (name, ordinal, result.returncode, result.stdout, result.stderr)
                record = json.loads(result.stdout)
                first, recovery = record['first'], record['recovery']
                assert recovery['passed'] and recovery['reused_object'] and sha(good) == expected_sha, record
                assert record['library_pool_final'] == 0 and record['stores_opened'] == record['stores_closed'], record
                for phase in (first, recovery):
                    assert phase['stores_opened'] == phase['stores_closed'] and phase['library_pool_peak'] <= 65536, record
                if ordinal:
                    assert not first['passed'] and first['error'] and first['scratch_error'] == 6, record
                    assert first['nor_fault_hits'] == recovery['nor_fault_hits'] == 1, record
                    assert first['nor_calls'] == ordinal, record
                else:
                    assert first['passed'] and sha(bad) == expected_sha, record
                    assert first['nor_fault_hits'] == recovery['nor_fault_hits'] == 0, record
                return dict(ordinal=ordinal, result=record, recovery_sha256=sha(good))

            control = exercise(0)
            count = control['result']['first']['nor_calls']
            assert count > 0, name
            row = dict(name=name, fixture_sha256=sha(image), expected_sha256=expected_sha,
                       exhaustive_physical_calls=width < 240, control=control, faults=[])
            report['cases'].append(row)
            for n in points(count, width < 240):
                row['faults'].append(exercise(n))
                if n % 300 == 0:
                    print(name, 'physical callback', n, 'of', count, flush=True)
            print(name, len(row['faults']), 'physical failures and same-object recoveries passed', flush=True)
        report['passed'] = True
    finally:
        report['inputs_unchanged'] = all(sha(Path(p)) == h for p, h in inputs.items())
        report['passed'] &= report['inputs_unchanged']
        report['fault_cases'] = sum(len(c['faults']) for c in report['cases'])
        report['host_seconds'] = time.perf_counter() - started
        report['scope'] = ('Actual shared scratch/NOR with host physical callbacks; partial I/O errors, no silent-read '
                           'integrity claim. Every small-image callback, sampled full-size callbacks. No target codec '
                           'execution, whole-app RAM/stack, timing budget, HTTP, LCD or hardware acceptance.')
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
