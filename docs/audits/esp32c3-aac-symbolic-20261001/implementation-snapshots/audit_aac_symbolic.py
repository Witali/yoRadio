"""Inventory all AAC exports and retain numeric-access review candidates.

This is deliberately a lexical review aid, not a proof that every constant is
an address. Array indices, strides and DSP constants must not be renamed as
structure fields just to make this list empty.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

NUMBER = r'(?:0x[0-9a-fA-F]+|\d+)'
ARITHMETIC = re.compile(r'[+-]\s*' + NUMBER + r'\b')
CAST = re.compile(r'\*\s*\([^;\n]*?\*\)\s*\(')
UNTYPED_INDEX = re.compile(r'\bparam_\d+\[' + NUMBER + r'\]')

def candidates(text):
    return [dict(line=n, text=line.strip()) for n, line in enumerate(text.splitlines(), 1)
            if (CAST.search(line) and ARITHMETIC.search(line)) or UNTYPED_INDEX.search(line)]

def audit(raw, symbolic):
    original = json.loads((raw/'manifest.json').read_text())
    current = json.loads((symbolic/'manifest.json').read_text())
    before = {f['name']: f for f in original['functions']}
    after = {f['name']: f for f in current['functions']}
    if original['sha256'] != current['sha256'] or before.keys() != after.keys():
        raise ValueError('Different binaries or incomplete function inventory')
    rows = []
    for name in sorted(before):
        a, b = before[name], after[name]
        if not b['completed'] or a['address'] != b['address'] or a['body_bytes'] != b['body_bytes']:
            raise ValueError('Changed/missing machine function: ' + name)
        old, new = raw/a['file'], symbolic/b['file']
        old_text, new_text = old.read_text(), new.read_text()
        rows.append(dict(function=name, address=b['address'], changed=old_text != new_text,
            raw_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),
            symbolic_sha256=hashlib.sha256(new.read_bytes()).hexdigest(),
            before_candidates=len(candidates(old_text)), remaining_candidates=candidates(new_text),
            contains_warning=b['pseudocode_contains_warning']))
    return dict(elf_sha256=current['sha256'], functions=len(rows),
        changed_functions=sum(r['changed'] for r in rows),
        before_candidates=sum(r['before_candidates'] for r in rows),
        remaining_candidates=sum(len(r['remaining_candidates']) for r in rows),
        scope='All inventory functions scanned; lexical candidates require semantic review and include valid array indexing. '
              'This does not claim a fully reconstructed or compilable decoder.', rows=rows)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw', type=Path, required=True)
    parser.add_argument('--symbolic', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.raw, args.symbolic)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'rows'}))
