"""Reconstruct archived raw NOR bytes and replay cold-publication checks offline."""
import argparse
import gzip
import json
from pathlib import Path

from photo_publication_contract import validate, rejection_checks
from photo_publication_qemu import CASES, sha, ELFFile
from verify_photo_format_matrix_evidence import source_hashes


def verify(path, root, source_revision=None):
    """Check every payload, complete image, producer identity and cut-state oracle."""
    proof = json.loads(path.read_text())
    assert proof['schema_version'] == 2 and proof['passed']
    assert not any(proof[key] for key in ('all_functionality_verified', 'network_acceptance',
        'lcd_acceptance', 'physical_hardware_tested', 'physical_power_cut_tested'))
    payloads = {}
    for row in proof['blobs']:
        file = (path.parent/row['file']).resolve()
        assert file.is_relative_to(path.parent.resolve())
        compressed = file.read_bytes(); assert sha(compressed) == row['gzip_sha256']
        data = gzip.decompress(compressed)
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
        assert row['sha256'] not in payloads; payloads[row['sha256']] = data
    files = {}
    for row in proof['raw']:
        assert row['source'] not in files; files[row['source']] = payloads[row['sha256']]
    base = payloads[proof['flash_base_sha256']]; assert len(base) == 0x400000
    resolved = {proof['flash_base_sha256']: base}
    for row in proof['images']:
        assert row['base_sha256'] in resolved
        data = bytearray(resolved[row['base_sha256']]); previous = -4096
        for sector in row['sectors']:
            offset = sector['offset']; value = payloads[sector['sha256']]
            assert len(value) == 4096 and offset % 4096 == 0 and previous < offset <= len(data)-4096
            data[offset:offset+4096] = value; previous = offset
        assert sha(data) == row['sha256'] and row['source'] not in files
        resolved[row['sha256']] = files[row['source']] = bytes(data)
    plan = json.loads(files[proof['plan_source']])
    seed = files[proof['seed_source']]
    elf_path = root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf'
    assert sha(elf_path.read_bytes()) == proof['elf_sha256']
    with elf_path.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
        segments = [(segment['p_vaddr'], segment.data()) for segment in elf.iter_segments()
                    if segment['p_type'] == 'PT_LOAD' and segment['p_filesz']]
    bundle = root/'Small_TV/src/tests/fixtures/jpeg_extended/lossless6-manifest.json'
    covered = []; results = []
    for run in proof['runs']:
        prefix = run['prefix']; report = json.loads(files[prefix+'/report.json'])
        for key in ('app_sha256', 'elf_sha256', 'source_sha256'): assert report[key] == proof[key]
        assert report['frozen_inputs'] == proof['frozen_inputs']
        instructions = {}
        for name, address in report['entries'].items():
            assert {symbol['st_value'] for symbol in symbols if symbol.name == name and symbol['st_value']} == {address}
            matches = [data[address-start:address-start+2] for start, data in segments
                       if start <= address <= start+len(data)-2]
            assert matches and all(code == matches[0] for code in matches)
            instructions[name] = sha(matches[0])
        for row in report['cases']:
            for event in row.get('trace', {}).get('completed_callbacks', []):
                assert event['instruction_sha256'] == instructions[event['function']]
        read = lambda name: files[prefix+'/'+name]
        for row in report['cases']: assert read(row['name']+'/warm/initial.bin') == seed
        result = validate(report, plan, bundle, read)
        assert rejection_checks(report, plan, bundle, read) == run['rejected_controls']
        covered += [row['name'] for row in report['cases']]; results.append(result)
    assert len(covered) == len(set(covered)) == len(CASES) and set(covered) == set(CASES)
    observed = source_hashes(root, proof['source_pins'], source_revision)
    for name, digest in proof['source_pins'].items(): assert observed[name] == digest, name
    manifest = json.loads((root/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text())
    assert manifest['source_sha256'] == proof['source_sha256'] and manifest['elf_sha256'] == proof['elf_sha256']
    return dict(passed=True, cases=len(covered), actual_cold_boots=len(covered),
        successful_recoveries=len(covered), physical_images=len(proof['images']), runs=results,
        physical_power_cut_tested=False)


def main():
    """Replay committed evidence without launching or contacting a guest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof', type=Path, required=True)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--source-revision', help='Read exact historical producer pins without resetting files')
    args = parser.parse_args(); print(json.dumps(verify(args.proof, args.root, args.source_revision)))


if __name__ == '__main__': main()
