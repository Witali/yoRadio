"""Compare additional JPEG inputs using actual factory/native RV32 decoder instructions."""
import argparse
from array import array
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--dependency-root', type=Path)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
dependencies = args.dependency_root or ROOT
sys.path.insert(0, str(dependencies / '.build/small-tv-parity/oracle-deps'))
from control_oracle import verify_inputs
from jpeg_oracle import JpegMachine, patterned_panel
from jpeg_test_fixtures import gray_huffman_fixture
from jpeg_dht_contract import rejection_checks

FIXTURES = Path(__file__).parent / 'fixtures/jpeg'
BASE = 0x200000


def digest(path):
    """Bind fixtures, executables and adapters to the exact tested bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def segments(data):
    """Locate bounded header segments in a known baseline fixture, stopping before entropy."""
    if data[:2] != b'\xff\xd8':
        raise ValueError('Fixture has no JPEG SOI')
    offset = 2
    while offset + 4 <= len(data):
        if data[offset] != 255:
            raise ValueError('Invalid fixture segment framing')
        marker = data[offset + 1]
        length = int.from_bytes(data[offset + 2:offset + 4], 'big')
        if length < 2 or offset + length + 2 > len(data):
            raise ValueError('Invalid fixture segment length')
        yield marker, offset, length
        if marker == 0xda:
            return
        offset += length + 2
    raise ValueError('Fixture has no SOS')


def mutations(baseline, restarted):
    """Make single-cause invalid tables, headers, scan length and restart sequences."""
    header = list(segments(baseline))
    position = lambda marker: next(offset for item, offset, _ in header if item == marker)
    cases = []
    for name, offset, value in (
        ('bad-huffman-table-id', position(0xc4) + 4, 4),
        ('bad-quantization-table-id', position(0xdb) + 4, 4),
        ('unsupported-sample-precision', position(0xc0) + 4, 12),
        ('invalid-sampling-factor', position(0xc0) + 11, 0),
    ):
        data = bytearray(baseline)
        data[offset] = value
        cases.append((name, bytes(data)))
    data = bytearray(baseline)
    counts = position(0xc4) + 5
    total = sum(data[counts:counts + 16])
    if total < 3:
        raise ValueError('Fixture needs at least three Huffman symbols')
    # Three codes of length one cannot be a binary prefix code. Keep the
    # declared symbol count and table byte length unchanged to isolate this.
    data[counts:counts + 16] = bytes([3, total - 3] + [0] * 14)
    cases.append(('oversubscribed-huffman-tree', bytes(data)))
    data = bytearray(baseline)
    scan = position(0xda)
    data[scan + 2:scan + 4] = b'\xff\xff'
    cases.append(('oversized-scan-header', bytes(data)))
    frame = position(0xc0)
    frame_length = int.from_bytes(baseline[frame + 2:frame + 4], 'big')
    for name, payload in (('short-frame-header', baseline[frame + 4:frame + 9]),
                          ('missing-frame-components', baseline[frame + 4:frame + 10]),
                          ('extra-frame-component-data', baseline[frame + 4:frame + 2 + frame_length] + b'\0')):
        data = (baseline[:frame + 2] + (len(payload) + 2).to_bytes(2, 'big') + payload +
                baseline[frame + frame_length + 2:])
        cases.append((name, data))
    data = bytearray(restarted)
    scan_end = next(offset + length + 2 for marker, offset, length in segments(data) if marker == 0xda)
    restart = next(index for index in range(scan_end, len(data) - 1)
                   if data[index] == 255 and 0xd0 <= data[index + 1] <= 0xd7)
    if data[restart + 1] != 0xd0:
        raise ValueError('Unexpected first restart marker')
    data[restart + 1] = 0xd7
    cases.append(('wrong-restart-sequence', bytes(data)))
    data = bytearray(restarted)
    data[restart + 1] = 0
    cases.append(('missing-restart-marker', bytes(data)))
    scan_end = next(offset + length + 2 for marker, offset, length in header if marker == 0xda)
    cases.append(('truncated-entropy', baseline[:scan_end + 64]))
    return cases


def huffman_cases(factory, native, original):
    """Exercise unused invalid branches at every depth and valid 1/16-bit boundaries."""
    one, long = [1] + [0] * 15, [0] * 15 + [1]
    valid, invalid = [], []
    for name, dc, ac in (('one-bit', one, one), ('long-dc', long, one),
                         ('long-ac', one, long), ('long-dc-and-ac', long, long)):
        data = gray_huffman_fixture(dc, [0], ac, [0])
        row = {'name': name, 'width': 240, 'height': 240, 'bytes': len(data),
               'sha256': hashlib.sha256(data).hexdigest()}
        result = valid_case(factory, native, original, row, data)
        valid.append(result)
        print('Huffman valid', name, 'passed:', result['passed'], flush=True)
    ac_symbols = [0] + [value for value in range(1, 256) if 1 <= value % 16 <= 10]
    inputs = [('dc-depth-1', gray_huffman_fixture([3] + [0] * 15, [0, 1, 2], one, [0]))]
    for depth in range(1, 17):
        counts = [1] * (depth - 1) + [3] + [0] * (16 - depth)
        # Each earlier level leaves one unused prefix; the next level has two
        # slots, so three codes oversubscribe it. Entropy uses only the first EOB.
        data = gray_huffman_fixture(one, [0], counts, ac_symbols[:sum(counts)])
        inputs.append(('ac-depth-' + str(depth), data))
    for name, data in inputs:
        result = invalid_case(native, original, name, data)
        result['passed'] = result['passed'] and not result['decoder_started']
        asset = supply(factory, original, {'width': 240, 'height': 240}, data)
        factory.panel = patterned_panel()
        literal = factory.draw(asset, length=len(data))
        result['literal_factory'] = {'result': literal, 'decoder_started': factory.decompression_started}
        invalid.append(result)
        print('Huffman invalid', name, 'passed:', result['passed'], flush=True)
    return {'passed': all(row['passed'] for row in valid + invalid), 'valid': valid, 'invalid': invalid}


def supply(machine, original, row, data):
    """Supply only synthetic JPEG bytes and erased padding at the SDK flash-read boundary."""
    if machine.is_factory:
        machine.dump = original[:BASE] + data + b'\xff' * 512 + original[BASE + len(data) + 512:]
    else:
        machine.native_assets = data + b'\xff' * 512 + machine.native_assets[len(data) + 512:]
    return {**row, 'flash_offset': hex(BASE), 'native_offset': BASE, 'source_length': len(data)}


def valid_case(factory, native, original, row, data):
    """Compare the entire panel and require discard validation to leave every pixel intact."""
    output = {**row, 'passed': False}
    for machine in (factory, native):
        asset = supply(machine, original, row, data)
        machine.panel = patterned_panel()
        result = machine.draw(asset, length=len(data))
        output['factory_result' if machine.is_factory else 'native_result'] = result
        output['factory_decoder_started' if machine.is_factory else 'native_decoder_started'] = machine.decompression_started
    different = sum(left != right for left, right in zip(factory.panel.pixels, native.panel.pixels))
    native.panel = patterned_panel()
    initial = native.panel.pixels[:]
    validation = native.validate(asset, row['width'], row['height'], length=len(data))
    output.update(different_pixels=different, validation_result=validation,
                  validation_pixel_changes=sum(left != right for left, right in zip(initial, native.panel.pixels)),
                  passed=not different and output['factory_result'] == 0 and output['native_result'] == 0 and
                         output['factory_decoder_started'] and output['native_decoder_started'] and
                         validation == 0 and native.panel.pixels == initial)
    return output


def invalid_case(native, original, name, data):
    """Require a bounded error, exact error erase and a drawing-free validation failure."""
    row = {'name': name, 'width': 240, 'height': 240, 'bytes': len(data),
           'sha256': hashlib.sha256(data).hexdigest()}
    asset = supply(native, original, row, data)
    native.panel = patterned_panel()
    initial = native.panel.pixels[:]
    result = native.draw(asset, length=len(data))
    started = native.decompression_started
    expected = array('H', [0]) * 57600 if started else initial
    differences = sum(left != right for left, right in zip(expected, native.panel.pixels))
    native.panel = patterned_panel()
    initial = native.panel.pixels[:]
    validation = native.validate(asset, 240, 240, length=len(data))
    return {**row, 'result': result, 'decoder_started': started, 'erase_pixel_differences': differences,
            'validation_result': validation, 'validation_pixel_changes':
                sum(left != right for left, right in zip(initial, native.panel.pixels)),
            'passed': result == 0x102 and validation == 0x102 and not differences and native.panel.pixels == initial}


def main():
    """Execute the additional valid/invalid inputs without modifying either firmware image."""
    app_sha = verify_inputs(ROOT, dependencies)
    original = (ROOT / 'Small_TV/full-flash.bin').read_bytes()
    manifest = json.loads((FIXTURES / 'manifest.json').read_text(encoding='utf-8'))
    paths = [Path(__file__), *[Path(__file__).with_name(name) for name in
                             ('jpeg_oracle.py', 'machine_oracle.py', 'control_oracle.py', 'classic_oracle.py', 'jpeg_test_fixtures.py',
                              'jpeg_dht_oracle.py', 'jpeg_dht_contract.py')],
             FIXTURES / 'manifest.json', *[FIXTURES / row['file'] for row in manifest['cases']]]
    inputs = [{'file': path.relative_to(ROOT).as_posix(), 'sha256': digest(path)} for path in paths]
    factory = JpegMachine('factory', original, dependency_root=dependencies)
    native = JpegMachine('native', original, dependency_root=dependencies)
    valid, invalid, errors = [], [], []
    for row in manifest['cases']:
        data = (FIXTURES / row['file']).read_bytes()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('JPEG fixture changed: ' + row['file'])
        result = valid_case(factory, native, original, row, data)
        valid.append(result)
        print(row['name'], 'different pixels:', result['different_pixels'], 'passed:', result['passed'], flush=True)
    for name, data in mutations((FIXTURES / 'rgb-444.jpg').read_bytes(),
                                (FIXTURES / 'rgb-444-restart.jpg').read_bytes()):
        try:
            result = invalid_case(native, original, name, data)
            if name in ('bad-quantization-table-id', 'unsupported-sample-precision', 'extra-frame-component-data'):
                asset = supply(factory, original, {'width': 240, 'height': 240}, data)
                factory.panel = patterned_panel()
                initial = factory.panel.pixels[:]
                literal = factory.draw(asset, length=len(data))
                result['literal_factory'] = {
                    'result': literal, 'decoder_started': factory.decompression_started,
                    'changed_pixels': sum(left != right for left, right in zip(initial, factory.panel.pixels))}
        except Exception as error:
            result = {'name': name, 'passed': False, 'error': str(error)}
            errors.append(str(error))
        invalid.append(result)
        print(name, 'passed:', result['passed'], flush=True)
    huffman = huffman_cases(factory, native, original)
    dht_output = args.output.with_name(args.output.stem + '-dht-' + uuid.uuid4().hex[:12] + '.json')
    completed = subprocess.run([sys.executable, str(Path(__file__).with_name('jpeg_dht_oracle.py')),
        '--dependency-root', str(dependencies), '--output', str(dht_output)], timeout=180)
    dht = json.loads(dht_output.read_text())
    dht_guards = []
    if completed.returncode == 0 and dht['passed']:
        dht_guards = rejection_checks(dht)
    unchanged = app_sha == verify_inputs(ROOT, dependencies) and all(
        digest(ROOT / row['file']) == row['sha256'] for row in inputs)
    archive = json.loads((ROOT / 'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text(encoding='utf-8-sig'))
    report = {'passed': all(row['passed'] for row in valid + invalid) and huffman['passed'] and unchanged and not errors and
                        completed.returncode == 0 and dht['passed'] and len(dht_guards) == 7 and all(row['passed'] for row in dht_guards),
              'app_sha256': app_sha, 'source_sha256': archive['source_sha256'],
              'native_elf_sha256': native.source_sha, 'factory_elf_sha256': factory.source_sha,
              'test_inputs': inputs, 'inputs_unchanged': unchanged, 'valid': valid, 'invalid': invalid,
              'huffman': huffman, 'dht': dht, 'dht_rejection_checks': dht_guards,
              'scope': __doc__ + ' Only the SDK flash-read boundary supplies generated test bytes. Full panel guards, discard validation and native error cleanup are checked. This is not an image-upload HTTP or physical/concurrency test.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    raise SystemExit(0 if report['passed'] else 1)


if __name__ == '__main__':
    main()
