"""Regenerate deterministic, nonpersonal JPEG variations; not required to run the tests."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageFile, __version__ as PILLOW_VERSION, features

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Encode a fixed arithmetic pattern and bind each checked-in fixture to its exact bytes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'tests/fixtures/jpeg')
    args = parser.parse_args()
    if PILLOW_VERSION != '12.3.0':
        raise ValueError('Reproduction requires the recorded Pillow 12.3.0 encoder')
    ImageFile.MAXBLOCK = 1024 * 1024
    args.output.mkdir(parents=True, exist_ok=True)
    cases = []
    for name, size, mode, options in [
        ('rgb-444', (240, 240), 'RGB', {'subsampling': 0}),
        ('rgb-422', (240, 240), 'RGB', {'subsampling': 1}),
        ('rgb-420', (240, 240), 'RGB', {'subsampling': 2}),
        ('rgb-444-restart', (240, 240), 'RGB', {'subsampling': 0, 'restart_marker_blocks': 3}),
        ('rgb-420-restart', (240, 240), 'RGB', {'subsampling': 2, 'restart_marker_blocks': 1}),
        ('grayscale', (240, 240), 'L', {}),
        ('odd-rgb', (123, 117), 'RGB', {'subsampling': 2}),
        ('odd-grayscale', (23, 29), 'L', {}),
    ]:
        image = Image.new(mode, size)
        image.putdata([((x * 17 + y * 31) % 256 if mode == 'L' else
                        ((x * 17 + y * 31) % 256, (x * x + 29 * y) % 256, (y * y + 7 * x) % 256))
                       for y in range(size[1]) for x in range(size[0])])
        path = args.output / (name + '.jpg')
        image.save(path, quality=83, optimize=True, **options)
        cases.append({'name': name, 'file': path.name, 'width': size[0], 'height': size[1],
                      'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size,
                      'mode': mode, 'options': options})
    manifest = {'encoder': {'pillow': PILLOW_VERSION, 'libjpeg': features.version_codec('jpg'),
                            'libjpeg_turbo': features.version('libjpeg_turbo'),
                            'quality': 83, 'optimize': True, 'max_block_bytes': ImageFile.MAXBLOCK},
                'cases': cases, 'scope': __doc__}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n',
                                              encoding='utf-8', newline='\n')
    print('Generated', len(cases), 'synthetic JPEG variations')


if __name__ == '__main__':
    main()
