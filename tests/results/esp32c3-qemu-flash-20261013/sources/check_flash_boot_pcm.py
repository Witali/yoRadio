"""Boot a preserved PCM fixture image and compare it with a known-good capture.

Run with Linux Python (also under WSL); all paths are native Linux paths.
This tests application startup/Flash reads/decoded PCM, not Flash timing.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

from run_pipeline_pcm import compare, parse_capture


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qemu', type=Path, required=True)
    parser.add_argument('--bios', type=Path, required=True)
    parser.add_argument('--flash', type=Path, required=True)
    parser.add_argument('--reference-log', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    reference = args.reference_log.read_bytes()
    if args.reference_log.suffix == '.gz':
        reference = gzip.decompress(reference)
    expected = parse_capture(reference.decode())
    report = dict(qemu_sha256=digest(args.qemu), flash_sha256=digest(args.flash),
                  reference_sha256=digest(args.reference_log),
                  controller_sha256=digest(Path(__file__)), cases=[])
    try:
        for model in ('gd25q', 'w25q'):
            command = [str(args.qemu), '-M', f'esp32c3,flash-model={model},flash-size=4M',
                       '-nographic', '-no-reboot', '-snapshot',
                       '-icount', 'shift=0,align=off,sleep=off',
                       '-L', str(args.bios), '-drive',
                       f'file={args.flash},if=mtd,format=raw']
            log = args.output / (model + '.log')
            with log.open('wb') as stream:
                result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT,
                                        stdin=subprocess.DEVNULL, timeout=240)
            if result.returncode:
                raise ValueError(f'{model}: QEMU exited {result.returncode}')
            text = log.read_text()
            if 'spi_flash: flash io: qio' not in text:
                raise ValueError(f'{model}: application did not configure QIO')
            compared = compare(expected, parse_capture(text))
            report['cases'].append(dict(model=model, command=command, **compared))
            print(model, compared, flush=True)
        report['passed'] = True
    except Exception as error:
        report.update(passed=False, error=str(error))
        raise
    finally:
        (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
