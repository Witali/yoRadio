"""Compare identical JPEGs and NOR/cache geometry with raw versus packed coefficients."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
PROBE = HERE.parent / 'jpeg_library_probe'


def sha(path):
    """Identify actual source, fixture and output bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, env):
    """Retain child errors and reject unexpected crashes/timeouts."""
    result = subprocess.run([str(p) for p in command], env=env, capture_output=True, timeout=30)
    assert result.returncode == 0, (command, result.returncode, result.stdout, result.stderr)
    return result


def main():
    """REQUESTED_CHANGE: prove savings without reducing capacity, formats or pixels."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-build', type=Path, required=True)
    parser.add_argument('--candidate-build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    builds = [json.loads((p / 'build.json').read_text()) for p in (args.reference_build, args.candidate_build)]
    assert builds[0]['backing_backend'] == 'stdio' and builds[1]['backing_backend'] == 'shared-nor-model'
    for build in builds:
        assert sha(Path(build['executable'])) == build['executable_sha256']
        assert all(sha(PROBE / name) == digest for name, digest in build['probe_inputs'].items())
        assert all(sha(Path(p)) == digest for p, digest in build['backing_fixture_inputs'].items())
    reference, candidate = [b['executable'] for b in builds]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    fixtures = output / 'fixtures'
    fixtures.mkdir()
    environment = {k: v for k, v in os.environ.items()
                   if not k.startswith('SMALL_TV_NOR_') and k != 'SMALL_TV_COEFF_PACKING'}
    report = dict(passed=False, all_functionality_verified=False, builds=builds,
                  runner_sha256=sha(Path(__file__)), cases=[])
    matrix = [('rich', mode, bits) for bits in (8, 12) for mode in
              ('baseline', 'progressive420', 'progressive444', 'gray-progressive',
               'cmyk-progressive', 'ycck-progressive')]
    matrix += [('rich', 'arith-progressive', 8), ('rich', 'lossless-rgb', 16)]
    # Flat controls expose the initial-erasure tradeoff rather than hiding it.
    matrix += [('flat', mode, bits) for mode, bits in
               [('gray-progressive', 8), ('cmyk-progressive', 8),
                ('cmyk-progressive', 12), ('ycck-progressive', 12)]]
    try:
        for pattern, mode, bits in matrix:
            name = f'{pattern}-{mode}-{bits}'
            image = fixtures / (name + '.jpg')
            generated_mode = ('rich-' if pattern == 'rich' else '') + mode + '-q83'
            run([reference, 'generate', image, generated_mode, bits, 240, 240, 1, 0, 0], environment)
            expected = output / 'expected.raw'
            run([reference, 'decode', image, expected, 0, 0], environment)
            row = dict(name=name, fixture_sha256=sha(image), fixture_bytes=image.stat().st_size,
                       expected_sha256=sha(expected))
            for variant, enabled in [('raw', '0'), ('packed', '1')]:
                first, recovery = output / 'first.raw', output / 'recovery.raw'
                env = dict(environment, SMALL_TV_COEFF_PACKING=enabled)
                result = run([candidate, 'reuse', image, first, recovery, 65536, 1, 'none', 0, 0], env)
                record = json.loads(result.stdout)
                assert record['library_pool_final'] == 0 and record['stores_opened'] == record['stores_closed'], record
                assert sha(first) == sha(recovery) == row['expected_sha256'], (name, variant)
                assert record['first']['passed'] and record['recovery']['passed'] and record['recovery']['reused_object'], record
                assert record['first']['library_pool_peak'] <= 65536 and record['recovery']['library_pool_peak'] <= 65536, record
                row[variant] = record
            before, after = row['raw']['first'], row['packed']['first']
            assert before['scratch_peak_bytes'] == after['scratch_peak_bytes'], row
            assert before['library_pool_peak'] == after['library_pool_peak'], row
            if 'progressive' in mode:
                if pattern == 'rich':
                    assert after['nor_program_bytes'] < before['nor_program_bytes'], row
                    assert after['nor_erases'] < before['nor_erases'], row
                row['program_reduction_fraction'] = (1 - after['nor_program_bytes'] / before['nor_program_bytes']) if before['nor_program_bytes'] else None
                row['erase_reduction_fraction'] = (1 - after['nor_erases'] / before['nor_erases']) if before['nor_erases'] else None
            else:
                assert before['nor_program_bytes'] == after['nor_program_bytes'] == 0, row
            report['cases'].append(row)
            print(name, 'program', before['nor_program_bytes'], '->', after['nor_program_bytes'],
                  'erase', before['nor_erases'], '->', after['nor_erases'], flush=True)
        report['passed'] = True
    finally:
        report['inputs_unchanged'] = all(sha(PROBE / n) == h for b in builds for n, h in b['probe_inputs'].items())
        report['passed'] &= report['inputs_unchanged']
        report['scope'] = ('Identical host JPEG object, hard65536-byte library pool limit, one4KiB NOR cache, '
                           'same backing capacity, retained physical bytes across two decodes. Packing uses256-byte '
                           'conversion buffer on stack. Not whole-app RAM, hardware SPI timing/endurance or UI integration.')
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
