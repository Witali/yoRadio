"""Stage an OpenETH build with the normal web assets and a one-station SPIFFS fixture."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--spiffsgen', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build = args.build.resolve(strict=True)
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / '.build') or output == ROOT / '.build':
        raise ValueError('Use a fresh fixture directory under the project .build')
    output.mkdir(parents=True)
    assets = output / 'assets'
    files = subprocess.check_output(['git', '-c', 'core.longpaths=true', 'ls-files', '-z', '--', 'yoRadio/data/www'], cwd=ROOT)
    for name in files.split(b'\0'):
        if name:
            path = Path(name.decode('utf-8'))
            target = assets / path.relative_to('yoRadio/data')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
    data = assets / 'data'
    data.mkdir()
    (data / 'playlist.csv').write_bytes(b'OpenETH fixture\thttps://10.0.2.100:18080/file/station\t0\n')
    (data / 'index.dat').write_bytes(struct.pack('<I', 0))

    flasher = build / 'flasher_args.json'
    spec = json.loads(flasher.read_bytes())
    if spec['flash_files']['0x370000'] != 'spiffs.bin':
        raise ValueError('Unexpected production SPIFFS path')
    for name in spec['flash_files'].values():
        if name == 'spiffs.bin':
            continue
        source = (build / name).resolve(strict=True)
        if not source.is_relative_to(build):
            raise ValueError('Flash component is outside the diagnostic build')
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    (output / 'config').mkdir()
    shutil.copyfile(build / 'config/sdkconfig.json', output / 'config/sdkconfig.json')
    shutil.copyfile(flasher, output / flasher.name)
    subprocess.run([sys.executable, '-B', args.spiffsgen.resolve(strict=True), '0x90000', assets,
                    output / 'spiffs.bin', '--page-size=256', '--obj-name-len=32', '--meta-len=0',
                    '--use-magic', '--use-magic-len'], check=True)
    inventory = {p.relative_to(assets).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(assets.rglob('*')) if p.is_file()}
    (output / 'fixture.json').write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')
    print('Staged', len(inventory), 'SPIFFS fixture files with the unchanged bootloader, partitions and application.')


if __name__ == '__main__':
    main()
