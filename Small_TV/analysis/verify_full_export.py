"""Independently bind a complete Ghidra export's instructions and function index to the factory ELF."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/tools'))
from elftools.elf.elffile import ELFFile
from audit_factory_xrefs import sha

FACTORY = '8c9fd166a6536bc1bc236fc98018eb0daba9aad01ce8356511ad68eba03de882'
INSTRUCTION = re.compile(r'^(?:ram:)?([0-9a-fA-F]{8}): ([0-9a-fA-F]+) (.+)$')
HEADER = re.compile(r'^/\* ENTRY (?:ram:)?([0-9a-fA-F]{8}) (\S+) BODY_BYTES (\d+) COMPLETED (true|false) \*/\r?$', re.M)


def verify(elf, directory, expected_sha256=FACTORY):
    """Check every exported instruction byte without trusting Ghidra's aggregate counters."""
    required = ('report.json', 'instructions.asm', 'functions.jsonl', 'all-functions.c',
                'code-gaps.jsonl', 'computed-flows.jsonl')
    if any(not (directory / name).is_file() for name in required):
        raise ValueError('Incomplete full export')
    if sha(elf) != expected_sha256:
        raise ValueError('Unexpected factory ELF')
    report = json.loads((directory / 'report.json').read_text())
    if report['program_sha256'] != expected_sha256:
        raise ValueError('Export belongs to another firmware')
    image = ELFFile(io.BytesIO(elf))
    if image.elfclass != 32 or not image.little_endian or image['e_machine'] != 'EM_RISCV':
        raise ValueError('Expected a little-endian RV32 ELF')
    sections = [dict(start=s['sh_addr'], data=s.data(), covered=bytearray(s['sh_size']))
                for s in image.iter_sections() if s['sh_flags'] & 6 == 6 and s['sh_type'] != 'SHT_NOBITS']
    instructions = 0
    for line in (directory / 'instructions.asm').read_text().splitlines():
        match = INSTRUCTION.fullmatch(line)
        if match is None:
            raise ValueError('Malformed instruction record')
        address = int(match[1], 16)
        code = bytes.fromhex(match[2])
        matches = [s for s in sections if s['start'] <= address < address + len(code) <= s['start'] + len(s['data'])]
        if len(matches) != 1 or len(code) not in (2, 4):
            raise ValueError('Instruction outside the actual executable segments')
        section = matches[0]
        offset = address - section['start']
        if code != section['data'][offset:offset + len(code)]:
            raise ValueError('Exported instruction bytes differ from the factory ELF')
        if any(section['covered'][offset:offset + len(code)]):
            raise ValueError('Overlapping exported instructions')
        section['covered'][offset:offset + len(code)] = b'\1' * len(code)
        instructions += 1
    decoded = sum(sum(s['covered']) for s in sections)
    executable = sum(len(s['data']) for s in sections)
    if (instructions, decoded, executable) != (report['instruction_count'], report['decoded_instruction_bytes'], report['executable_bytes']):
        raise ValueError('Instruction coverage counters are inconsistent')
    gaps = [json.loads(line) for line in (directory / 'code-gaps.jsonl').read_text().splitlines()]
    gap_counts = {'undecoded-executable': 0, 'instructions-without-function': 0}
    seen_ranges = []
    for gap in gaps:
        start, end = (int(gap[k].split(':')[-1], 16) for k in ('start', 'end'))
        size = end - start + 1
        matches = [s for s in sections if s['start'] <= start <= end < s['start'] + len(s['data'])]
        if len(matches) != 1 or size != gap['bytes'] or gap['kind'] not in gap_counts:
            raise ValueError('Invalid executable gap extent')
        if any(lo <= end and start <= hi for lo, hi in seen_ranges):
            raise ValueError('Overlapping executable gaps')
        seen_ranges.append((start, end))
        section = matches[0]
        offset = start - section['start']
        actual = sum(section['covered'][offset:offset + size])
        if actual != (0 if gap['kind'] == 'undecoded-executable' else size):
            raise ValueError('Gap disagrees with the literal instruction coverage')
        gap_counts[gap['kind']] += size
    if (gap_counts['undecoded-executable'], gap_counts['instructions-without-function']) != (
            executable - decoded, report['instruction_bytes_without_function']):
        raise ValueError('Executable gap counters are inconsistent')
    flows = [json.loads(line) for line in (directory / 'computed-flows.jsonl').read_text().splitlines()]
    if len(flows) != report['computed_flow_sites']:
        raise ValueError('Missing computed-flow records')
    index = [json.loads(line) for line in (directory / 'functions.jsonl').read_text().splitlines()]
    with (directory / 'all-functions.c').open(encoding='utf-8', newline='') as stream:
        code = stream.read()
    headers = list(HEADER.finditer(code))
    if len(index) != len(headers) or len(index) != report['functions_attempted']:
        raise ValueError('Missing or extra function in the pseudocode export')
    entries = set()
    for number, (row, header) in enumerate(zip(index, headers)):
        address = int(row['address'].split(':')[-1], 16)
        if address in entries:
            raise ValueError('Duplicate function entry')
        entries.add(address)
        if (address, row['name'], row['body_bytes'], row['completed']) != (
                int(header[1], 16), header[2], int(header[3]), header[4] == 'true'):
            raise ValueError('Function index differs from its pseudocode block')
        if row['completed']:
            end = headers[number + 1].start() if number + 1 < len(headers) else len(code)
            text = code[header.end() + 1:end].rstrip('\r\n')
            # PrintWriter adds a separator around each block. Preserve the
            # decompiler's own possible final newline when comparing its hash.
            hashes = {sha((text + newline * n).encode()) for newline in ('\n', '\r\n') for n in range(4)}
            if row['pseudocode_sha256'] not in hashes:
                raise ValueError('Pseudocode text differs from its indexed digest')
    completed = sum(row['completed'] for row in index)
    if completed != report['completed'] or len(index) - completed != report['failed']:
        raise ValueError('Function completion counters are inconsistent')
    files = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes())) for p in sorted(directory.iterdir()) if p.is_file()}
    return dict(schema='small-tv-full-export-verification-v1', passed=True,
        factory_elf_sha256=sha(elf), instructions_verified=instructions,
        instruction_bytes_verified=decoded, executable_bytes=executable,
        decoded_executable_percent=decoded * 100 / executable,
        functions_verified=len(index), completed=completed, files=files,
        pseudocode_digests_verified=True, all_function_boundaries_independently_proved=False,
        semantic_equivalence_proved=False, whole_image_completeness_proved=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--export', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expected-elf-sha256', default=FACTORY)
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve().is_relative_to(args.export.resolve()):
        raise ValueError('Preserve the original export and existing reports')
    result = verify(args.elf.read_bytes(), args.export, args.expected_elf_sha256)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('passed', 'functions_verified', 'instructions_verified', 'decoded_executable_percent')}))


if __name__ == '__main__':
    main()
