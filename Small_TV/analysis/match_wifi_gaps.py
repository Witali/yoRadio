"""Find complete, relocation-qualified SDK function candidates in Ghidra's code gaps."""
import argparse
from collections import Counter
import io
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/tools'))
from elftools.elf.elffile import ELFFile
from audit_factory_xrefs import Image, sha, startup_gp
from match_factory_sdk import LIBRARIES
from reverse.elf_archive import members
from reverse.rv32_link_match import model, match, meaningful

FACTORY = '8c9fd166a6536bc1bc236fc98018eb0daba9aad01ce8356511ad68eba03de882'


def run(elf, sdk, gaps):
    """Accept only unique full bodies; leave identical shapes and unsupported relocations explicit."""
    if sha(elf) != FACTORY:
        raise ValueError('Unexpected factory application')
    image = Image(elf)
    gp = startup_gp(image)
    ranges = [(int(r['start'].split(':')[-1], 16), int(r['end'].split(':')[-1], 16) + 1) for r in gaps]
    sections = [s for s in image.sections if s['execute']]
    counts = Counter()
    candidates, archives = [], {}
    for library in ('libnet80211.a', 'libpp.a'):
        raw = (sdk / library).read_bytes()
        if sha(raw) != LIBRARIES[library]:
            raise ValueError('Changed original Wi-Fi SDK archive')
        archives[library] = sha(raw)
        for member, data in members(raw):
            if data[:4] != b'\x7fELF':
                continue
            obj = ELFFile(io.BytesIO(data))
            table = obj.get_section_by_name('.symtab')
            if table is None:
                continue
            symbols = [s for s in table.iter_symbols() if s['st_info']['type'] == 'STT_FUNC'
                       and isinstance(s['st_shndx'], int) and 4 <= s['st_size'] <= 4096]
            for symbol in symbols:
                counts['models_considered'] += 1
                try:
                    spec = model(data, symbol.name)
                    length = 0
                    for offset, instruction in spec['instructions'].items():
                        if meaningful(spec['relocs'].get(offset, [])):
                            break
                        length += len(instruction)
                        if length >= 12:
                            break
                    if length < 4:
                        counts['no_fixed_entry_prefix'] += 1
                        continue
                    prefix = spec['code'][:length]
                    matches = []
                    for section in sections:
                        code = section['data']
                        offset = code.find(prefix)
                        while offset >= 0:
                            start = section['start'] + offset
                            if start % 2 == 0 and any(lo <= start < hi for lo, hi in ranges):
                                try:
                                    row = match(spec, code[offset:offset + len(spec['code']) + 64], start, gp)
                                    row.update(library=library, member=member, object_sha256=sha(data),
                                        code_sha256=sha(code[offset:offset + row['linked_bytes']]))
                                    matches.append(row)
                                except (ValueError, AssertionError, RecursionError):
                                    pass
                            offset = code.find(prefix, offset + 2)
                    if len(matches) == 1:
                        candidates.append(matches[0])
                        counts['unique_full_matches'] += 1
                    elif matches:
                        counts['ambiguous_full_matches'] += 1
                except (ValueError, AssertionError, RecursionError):
                    counts['unsupported_models'] += 1
            print(json.dumps(dict(member=member, considered=counts['models_considered'],
                                  candidates=len(candidates))), flush=True)
    by_address = {}
    for row in candidates:
        by_address.setdefault(row['start'], []).append(row)
    accepted, ambiguous = [], []
    for rows in by_address.values():
        if len(rows) != 1:
            ambiguous.extend(rows)
        else:
            accepted.append(rows[0])
    return dict(schema='small-tv-wifi-gap-matches-v1', factory_elf_sha256=sha(elf), sdk_archives=archives,
        counts=dict(counts), functions=sorted(accepted, key=lambda r: int(r['start'], 0)),
        ambiguous_same_entry=ambiguous, complete_relocated_bodies_matched=True,
        all_global_bindings_independently_proved=False, whole_image_completeness_proved=False,
        semantic_equivalence_proved=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('elf', 'sdk', 'gaps', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Preserve existing match evidence')
    files = [args.elf, args.gaps, args.sdk / 'libnet80211.a', args.sdk / 'libpp.a', Path(__file__)]
    if args.output.resolve() in [p.resolve() for p in files]:
        raise ValueError('Report aliases an input')
    pins = {str(p.resolve()): sha(p.read_bytes()) for p in files}
    gaps = [json.loads(line) for line in args.gaps.read_text().splitlines()]
    result = run(args.elf.read_bytes(), args.sdk, gaps)
    if any(sha(Path(p).read_bytes()) != digest for p, digest in pins.items()):
        raise ValueError('Gap matching inputs changed')
    result.update(inputs_sha256=pins, inputs_unchanged=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, matched_functions=len(result['functions']), counts=result['counts'])))


if __name__ == '__main__':
    main()
