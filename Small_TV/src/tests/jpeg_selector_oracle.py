"""Execute actual factory/native RV32 JPEG selectors and check the entire panel."""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]


def main():
    """Require literal neutral pixels for valid selectors and early invalid rejection."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dependency-root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(args.dependency_root / '.build/small-tv-parity/oracle-deps'))
    from control_oracle import verify_inputs
    from jpeg_oracle import JpegMachine, patterned_panel
    from jpeg_selector_fixtures import cases
    original = (ROOT / 'Small_TV/full-flash.bin').read_bytes()
    app = verify_inputs(ROOT, args.dependency_root)
    factory = JpegMachine('factory', original, dependency_root=args.dependency_root)
    native = JpegMachine('native', original, dependency_root=args.dependency_root)
    archive = ROOT / 'firmware/development/small-tv-esp32c2-reconstructed'
    paths = [Path(__file__), *[Path(__file__).with_name(name) for name in
        ('jpeg_selector_fixtures.py', 'jpeg_header_fixtures.py', 'jpeg_oracle.py', 'machine_oracle.py',
         'classic_oracle.py', 'control_oracle.py')], ROOT / 'Small_TV/full-flash.bin',
         ROOT / '.build/small-tv-esp32c2/small_tv_reconstructed.elf',
         args.dependency_root / '.build/small-tv-reverse/factory-analysis.elf',
         *[archive / name for name in ('app.bin', 'assets.bin', 'manifest.json', 'source-manifest.json')]]
    pins = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}
    report = dict(passed=False, all_functionality_verified=False, app_sha256=app,
        source_sha256=json.loads((archive / 'manifest.json').read_text())['source_sha256'],
        native_elf_sha256=native.source_sha, factory_elf_sha256=factory.source_sha,
        inputs_sha256=pins, cases=[], scope=__doc__ +
        ' Synthetic bytes enter only through SDK flash reads. Instructions and complete ELF files remain unchanged. '
        'Expected pixels are literal neutral RGB565, independently of either decoder. No network/display device acceptance.')
    for name, valid, data in cases():
        asset = dict(width=8, height=8, source_length=len(data), flash_offset='0x200000', native_offset=0x200000)
        factory.dump = original[:0x200000] + data + b'\xff' * 512 + original[0x200000 + len(data) + 512:]
        native.native_assets = data + b'\xff' * 512 + native.native_assets[len(data) + 512:]
        row = dict(name=name, expected_valid=valid, fixture_sha256=hashlib.sha256(data).hexdigest())
        for label, machine in (('factory', factory), ('native', native)):
            machine.panel = patterned_panel()
            initial = machine.panel.pixels[:]
            expected = initial[:]
            for y in range(8):
                expected[y * 240:y * 240 + 8] = array('H', [0x8410]) * 8
            result = machine.draw(asset, length=len(data))
            row[label] = dict(result=result, decoder_started=machine.decompression_started,
                changed_pixels=sum(a != b for a, b in zip(initial, machine.panel.pixels)),
                pixel_differences=sum(a != b for a, b in zip(expected, machine.panel.pixels)))
        native.panel = patterned_panel()
        initial = native.panel.pixels[:]
        result = native.validate(asset, 8, 8, length=len(data))
        row['validation'] = dict(result=result, decoder_started=native.decompression_started,
            changed_pixels=sum(a != b for a, b in zip(initial, native.panel.pixels)))
        draw = row['native']
        row['passed'] = (draw['result'] == result == 0 and draw['decoder_started'] and
            row['validation']['decoder_started'] and draw['pixel_differences'] == 0 and not row['validation']['changed_pixels']) if valid else (
            draw['result'] == result == 0x102 and not draw['decoder_started'] and
            not row['validation']['decoder_started'] and not draw['changed_pixels'] and not row['validation']['changed_pixels'])
        report['cases'].append(row)
        print(name, 'passed:', row['passed'], flush=True)
    report['inputs_unchanged'] = all(hashlib.sha256(Path(path).read_bytes()).hexdigest() == value for path, value in pins.items())
    report['passed'] = report['inputs_unchanged'] and len(report['cases']) == 168 and all(row['passed'] for row in report['cases'])
    args.output.write_text(json.dumps(report, indent=2) + '\n', newline='\n')
    print('Selector cases:', len(report['cases']), 'passed:', sum(row['passed'] for row in report['cases']))
    return not report['passed']


if __name__ == '__main__':
    raise SystemExit(main())
