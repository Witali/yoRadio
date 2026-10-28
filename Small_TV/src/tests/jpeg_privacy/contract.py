"""Check real codec-qualified JPEGs and metadata placed after entropy scans."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def sha(path):
    """Bind the actual executable, fixture and privacy source bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(executable, path):
    """A crash/timeout is a failure, not a successful privacy rejection."""
    result = subprocess.run([str(executable), str(path)], capture_output=True,
                            check=True, timeout=10)
    return json.loads(result.stdout)


def main():
    """Use previously decoded valid fixtures; inject only structurally placed APPs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--oracle', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    executable = args.build / 'jpeg_privacy_test.exe'
    project = Path(__file__).resolve().parents[2]
    paths = [executable, Path(__file__), project / 'codec/jpeg_privacy.c',
             project / 'codec/jpeg_privacy.h', args.oracle / 'report.json']
    report = dict(passed=False, scope='Metadata gate, not entropy decode or UI acceptance',
                  inputs_sha256={str(p.resolve()): sha(p) for p in paths}, positive=[], rejected=[])
    try:
        oracle = json.loads((args.oracle / 'report.json').read_text())
        assert oracle['passed']
        for row in oracle['positive']:
            path = args.oracle / 'fixtures' / row['name']
            assert sha(path) == row['fixture_sha256']
            result = inspect(executable, path)
            assert result['result'] == 'ok', (path, result)
            report['positive'].append(dict(name=path.name, sha256=sha(path), result=result))
        source = args.oracle / 'fixtures/full-cmyk12.jpg'
        data = source.read_bytes()
        assert data[-2:] == b'\xff\xd9'
        # Inserting a complete APP before EOI is structurally between scan and
        # EOI. A gate that returns after the first SOS would miss this metadata.
        for marker in (0xe1, 0xe2, 0xed, 0xfe):
            private = b'private GPS/date/camera serial'
            segment = bytes([255, marker]) + (len(private)+2).to_bytes(2, 'big') + private
            path = args.output / f'late-private-{marker:02x}.jpg'
            path.write_bytes(data[:-2] + segment + data[-2:])
            result = inspect(executable, path)
            assert result['result'] == 'private-metadata' and result['marker'] == marker, result
            report['rejected'].append(dict(name=path.name, sha256=sha(path), result=result))
        path = args.output / 'appended-data.jpg'
        path.write_bytes(data + b'private trailing GPS')
        result = inspect(executable, path)
        assert result['result'] == 'trailing-data', result
        report['rejected'].append(dict(name=path.name, sha256=sha(path), result=result))
        assert report['inputs_sha256'] == {str(p.resolve()): sha(p) for p in paths}
        report['passed'] = True
    finally:
        (args.output / 'report.json').write_text(json.dumps(report, indent=2)+'\n',
                                                encoding='utf-8', newline='\n')
    print('PASS real JPEG privacy:', len(report['positive']), 'valid,', len(report['rejected']), 'private/trailing refusals')


if __name__ == '__main__':
    main()
