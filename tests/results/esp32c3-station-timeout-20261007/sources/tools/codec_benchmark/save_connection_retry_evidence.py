"""Freeze old/new connection tests, expected failures and the final board state."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)

    def save(name, data):
        dest = args.output/name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.read_bytes() != data:
            raise ValueError('Evidence collision: '+str(name))
        dest.write_bytes(data)

    def source(name, digest):
        data = (ROOT/name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            data = (args.work/'runner-sources'/digest/Path(name).name).read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError('Measured source changed: '+name)
        save(Path('runner-sources')/digest/Path(name).name, data)

    save('.gitattributes', b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
    for folder in ('baseline', 'ota', 'ota-timeout', 'board-timeout', 'board-final-tests'):
        report = json.loads((args.work/folder/'report.json').read_text())
        if folder in ('ota', 'ota-timeout', 'board-final-tests') and (not report['cases'] or
                any(c['result'] != 'PASS' for c in report['cases'])):
            raise ValueError('Final verification not successful: '+folder)
        for path in sorted((args.work/folder).glob('*.json')):
            save(Path(folder)/path.name, path.read_bytes())
        for name, digest in report['test_sources_sha256'].items():
            source(name, digest)
    for folder in ('verify', 'verify-timeout', 'host', 'host-timeout', 'host-configurable', 'host-final'):
        for path in sorted((args.work/folder).rglob('*')):
            if path.is_file() and path.name != 'test':  # Native host executable is rebuildable.
                save(path.relative_to(args.work), path.read_bytes())
    for name in ('board-final.json', 'web-tests.log', 'web-tests-current.log',
                 'web-tests-final.log', 'eof-final.log'):
        save(name, (args.work/name).read_bytes())
    for variant in ('esp32c3-connect-retry', 'esp32c3-station-timeout'):
        folder = ROOT/'firmware/development'/variant
        manifest = json.loads((folder/'manifest.json').read_text())
        assert hashlib.sha256((folder/'app.bin').read_bytes()).hexdigest() == manifest['app_sha256']
        for name in ('manifest.json', 'sdkconfig'):
            save(Path('firmware')/variant/name, (folder/name).read_bytes())
    for name in ('tests/test-station-timeout-evidence.py', 'tests/test-connection-retry-runtime.py',
                 'tests/test-audio-server-recovery.py', 'tests/webui-station-timeout.test.js',
                 'tests/esp32c3-native-idf.test.js', 'tests/native/esp32c3_eof_test.c',
                 'tests/run-esp32c3-eof.py', 'tools/codec_benchmark/save_connection_retry_evidence.py'):
        save(Path('sources')/name, (ROOT/name).read_bytes())
    manifest = {p.relative_to(args.output).as_posix(): dict(bytes=p.stat().st_size,
        sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(args.output.rglob('*')) if p.is_file()}
    save('manifest.json', (json.dumps(manifest, indent=2)+'\n').encode())
    print('Retained', len(manifest), 'files; original failed checks unchanged')


if __name__ == '__main__':
    main()
