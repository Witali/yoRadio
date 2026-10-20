"""Execute JPEG DHT edge cases in literal factory/native RV32 machine code.

ITU-T T.81 Annex C reserves the all-one Huffman word at every code length;
F.1.2.2.1/Table F.2 restrict baseline AC symbols to sizes 1..10 plus EOB/ZRL.
Malformed unused branches must not escape the native validation boundary.
"""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
BASE = 0x200000


def digest(path):
    """Bind each observation to the executable, fixture generator and adapters."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cases():
    """Generate isolated invalid unused symbols and complete trees, with valid controls."""
    one = [1] + [0] * 15
    long = [0] * 15 + [1]
    legal = [value for value in range(256) if value in (0, 0xf0) or 1 <= value % 16 <= 10]
    assert len(legal) == 162
    controls = [
        ('minimal', one, [0], one, [0]),
        ('all-legal-symbols', [0, 0, 0, 12] + [0] * 12, list(range(12)),
         [0] * 7 + [162] + [0] * 8, legal),
        ('sparse-16-bit', long, [0], long, [0]),
        ('last-legal-16-bit-word', one, [0], [1] * 16, legal[:16]),
    ]
    for name, dc, dv, ac, av in controls:
        yield name, True, dc, dv, ac, av
    # Only the first (valid zero DC / EOB) symbol is consumed. Rejection must
    # happen in jd_prepare, rather than accidentally on later entropy data.
    for value in range(256):
        if value not in legal:
            yield 'reserved-ac-%02x' % value, False, one, [0], [1, 1] + [0] * 14, [0, value]
    for value in (12, 15, 255):
        yield 'reserved-dc-%02x' % value, False, [1, 1] + [0] * 14, [0, value], one, [0]
    for cls, maximum in [('dc', 11), ('ac', 16)]:
        for depth in range(1, maximum + 1):
            counts = [1] * (depth - 1) + [2] + [0] * (16 - depth)
            if cls == 'dc':
                yield 'all-one-dc-depth-%d' % depth, False, counts, list(range(depth + 1)), one, [0]
            else:
                yield 'all-one-ac-depth-%d' % depth, False, one, [0], counts, legal[:depth + 1]


def main():
    """Compare valid pixels and require malformed DHT rejection before decompression."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dependency-root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    sys.path.insert(0, str(args.dependency_root / '.build/small-tv-parity/oracle-deps'))
    from control_oracle import verify_inputs
    from jpeg_oracle import JpegMachine, patterned_panel
    from jpeg_test_fixtures import gray_huffman_fixture
    app_sha = verify_inputs(ROOT, args.dependency_root)
    original = (ROOT / 'Small_TV/full-flash.bin').read_bytes()
    factory = JpegMachine('factory', original, dependency_root=args.dependency_root)
    native = JpegMachine('native', original, dependency_root=args.dependency_root)
    archive = ROOT / 'firmware/development/small-tv-esp32c2-reconstructed'
    paths = [Path(__file__), *[Path(__file__).with_name(name) for name in
        ('jpeg_test_fixtures.py', 'jpeg_oracle.py', 'machine_oracle.py', 'classic_oracle.py', 'control_oracle.py')],
        ROOT / 'Small_TV/full-flash.bin', ROOT / '.build/small-tv-esp32c2/small_tv_reconstructed.elf',
        args.dependency_root / '.build/small-tv-reverse/factory-analysis.elf',
        args.dependency_root / '.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf',
        *[archive / name for name in ('app.bin', 'assets.bin', 'manifest.json', 'source-manifest.json')]]
    pins = {str(path.resolve()): digest(path) for path in paths}
    report = dict(passed=False, all_functionality_verified=False, app_sha256=app_sha,
        source_sha256=json.loads((archive / 'manifest.json').read_text())['source_sha256'],
        native_elf_sha256=native.source_sha, factory_elf_sha256=factory.source_sha,
        inputs_sha256=pins, cases=[], scope=__doc__ +
        ' Only SDK flash-read/allocation/mutex and LCD transport are adapted. No real HTTP, timing, RF or physical-board claim.')
    try:
        for name, valid, dc, dv, ac, av in cases():
            data = gray_huffman_fixture(dc, dv, ac, av, width=8, height=8)
            asset = dict(width=8, height=8, source_length=len(data), flash_offset=hex(BASE), native_offset=BASE)
            row = dict(name=name, expected_valid=valid, fixture_sha256=hashlib.sha256(data).hexdigest(),
                fixture_bytes=len(data), passed=False)
            report['cases'].append(row)
            # This replaces only bytes supplied at the adapted SDK read boundary;
            # immutable capture/ELF files and all CPU instructions stay unchanged.
            factory.dump = original[:BASE] + data + bytes([255]) * 512 + original[BASE+len(data)+512:]
            native.native_assets = data + bytes([255]) * 512 + native.native_assets[len(data)+512:]
            try:
                for tag, machine in [('factory', factory), ('native', native)]:
                    machine.panel = patterned_panel()
                    initial = machine.panel.pixels[:]
                    result = machine.draw(asset, length=len(data))
                    expected = initial[:]
                    for y in range(8):
                        expected[y*240:y*240+8] = array('H', [0x8410]) * 8
                    row[tag] = dict(result=result, decoder_started=machine.decompression_started,
                        expected_pixel_differences=sum(a != b for a, b in zip(expected, machine.panel.pixels)),
                        changed_pixels=sum(a != b for a, b in zip(initial, machine.panel.pixels)))
                differences = sum(a != b for a, b in zip(factory.panel.pixels, native.panel.pixels))
                native.panel = patterned_panel()
                initial = native.panel.pixels[:]
                validation = native.validate(asset, 8, 8, length=len(data))
                row.update(validation_result=validation, validation_decoder_started=native.decompression_started,
                    validation_pixel_changes=sum(a != b for a, b in zip(initial, native.panel.pixels)),
                    different_pixels=differences)
                if valid:
                    row['passed'] = (all(row[tag]['result'] == 0 and row[tag]['decoder_started'] and
                        row[tag]['expected_pixel_differences'] == 0 for tag in ('factory', 'native')) and
                        not differences and validation == 0)
                else:
                    row['passed'] = (row['native']['result'] == 0x102 and not row['native']['decoder_started'] and
                        row['native']['changed_pixels'] == 0 and validation == 0x102 and not row['validation_decoder_started'])
                row['passed'] &= row['validation_pixel_changes'] == 0
            except Exception as error:
                row['error'] = str(error)
            print(name, 'passed:', row['passed'], flush=True)
        report['inputs_unchanged'] = all(digest(Path(path)) == expected for path, expected in pins.items())
        report['passed'] = report['inputs_unchanged'] and all(row['passed'] for row in report['cases'])
    finally:
        args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
