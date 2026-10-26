"""Check an explicit, bidirectional port inventory; never infer equivalence from names.

Only addresses/symbol names and hashes are emitted, never factory data literals.
The selected Ghidra export is not a complete disassembly of the manufacturer image.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'/\*[\s\S]*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
DEFINITION = re.compile(
    r'(?m)^(?:[A-Za-z_]\w*(?:\([^()\n]*\))?[ \t\r\n*]+)+'
    r'([A-Za-z_]\w*)\s*\([^;{}]*\)\s*(?:noexcept\s*)?\{')


def masked(source: str) -> str:
    """Keep offsets/line numbers while excluding comments and string contents."""
    return TOKEN.sub(lambda m: ''.join('\n' if c == '\n' else ' ' for c in m[0]), source)


def functions(path: Path, root: Path) -> list[dict]:
    """Index source definitions, not linked symbols or reachable execution paths."""
    source = path.read_text(encoding='utf-8')
    code = masked(source)
    result = []
    for match in DEFINITION.finditer(code):
        start, depth, pos = match.end()-1, 1, match.end()
        while depth and pos < len(code):
            depth += (code[pos] == '{') - (code[pos] == '}')
            pos += 1
        if depth:
            raise ValueError(f'Unbalanced function: {path}:{match[1]}')
        body = code[start:pos]
        result.append(dict(symbol=path.relative_to(root).as_posix()+'#'+match[1],
                           line=source.count('\n', 0, match.start())+1,
                           sha256=hashlib.sha256(source[match.start():pos].encode()).hexdigest(),
                           calls=sorted(set(re.findall(r'\b([A-Za-z_]\w*)\s*\(', body))-
                                        {'if', 'for', 'while', 'switch', 'sizeof', '_Alignof'})))
    return result


def inputs(root: Path) -> dict[str, str]:
    """Bind the audit to code, headers, disassembly, page and resource bytes."""
    paths = set()
    for folder in ('app', 'codec', 'storage', 'resources', 'third_party/tjpgd', 'third_party/cjson', 'third_party/libjpeg-turbo',
                   'third_party/spleen', 'reference/assembly'):
        paths.update(p for p in (root/folder).rglob('*') if p.is_file())
    paths.update((root/'reference').glob('*.c'))
    paths.update((root.parent/'local_site/pages').glob('*.html'))
    paths.update(root/name for name in ('symbol-map.json', 'CMakeLists.txt', 'build.ps1',
                 'sdkconfig.defaults', 'partitions.csv', 'tools/prepare_resources.py',
                 'tools/prepare_timezones.py', 'tools/build_jpeg_library.py', 'tools/jpeg_cache_layout.py',
                 'tools/jpeg_guard_layout.py', 'tools/jpeg_storage_layout.py',
                 'tools/audit_correspondence.py', 'tools/organize_decompilation.py', 'cmake/debug_logging.cmake'))
    return {p.relative_to(root.parent).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def reconstruction_targets(row: dict) -> dict:
    """Derive navigation from reviewed function links, never a category guess."""
    targets = list(row['native'])
    modules = sorted({target.split('#', 1)[0] for target in targets})
    return dict(native_module=' + '.join(modules) if modules else 'ESP-IDF / libc (not ported)',
                native_targets=targets)


def check_navigation(symbols: dict, manifest: dict) -> None:
    """Reject stale file summaries even when the function inventory is valid."""
    reviewed = {row['address']: row for row in manifest['factory']}
    for key in ('native_module', 'native_targets'):
        for symbol in symbols['functions']:
            expected = reconstruction_targets(reviewed[symbol['address']])
            if symbol.get(key) != expected[key]:
                raise ValueError('Stale reconstruction navigation: '+symbol['address']+' '+key)


def audit(root: Path, manifest: dict) -> dict:
    """Fail closed on missing/duplicate/stale rows in either direction."""
    symbols = json.loads((root/'symbol-map.json').read_text(encoding='utf-8'))
    exported = {row['address']: row for row in symbols['functions']}
    if len(exported) != len(symbols['functions']):
        raise ValueError('Duplicate exported address')
    original = manifest['factory']
    if len({row['address'] for row in original}) != len(original):
        raise ValueError('Duplicate correspondence address')
    if {row['address'] for row in original} != set(exported):
        raise ValueError('Factory inventory differs from symbol-map.json')
    reference_rows = {}
    for path in sorted((root/'reference').glob('*.c')):
        content = path.read_text(encoding='utf-8')
        labels = re.findall(r'// Audit label: [^;]+; entry: ram:([0-9a-f]+); name: (\w+)', content)
        definitions = functions(path, root)
        if len(labels) != len(definitions):
            raise ValueError('Unlabelled/missing reference definition: '+path.name)
        for address, name in labels:
            if '0x'+address in reference_rows:
                raise ValueError('Duplicate reference address')
            reference_rows['0x'+address] = (name, path.relative_to(root).as_posix())
    if set(reference_rows) != set(exported):
        raise ValueError('Reference definitions differ from symbol-map.json')
    files = sorted((root/'app').rglob('*.c'))
    files += sorted((root/'app').rglob('*.cpp'))
    files += sorted((root/'codec').glob('*.c')) + sorted((root/'storage').glob('*.c'))
    files += [root/'third_party/tjpgd/tjpgd.c', root/'third_party/cjson/cJSON.c']
    indexed = [row for path in files for row in functions(path, root)]
    by_symbol = {row['symbol']: row for row in indexed}
    if len(by_symbol) != len(indexed):
        raise ValueError('Duplicate native function')
    sources = inputs(root)
    if manifest['inputs'] != sources:
        changed = sorted(k for k in sources.keys() | manifest['inputs'].keys()
                         if sources.get(k) != manifest['inputs'].get(k))
        raise ValueError('Review inputs changed: '+', '.join(changed))
    links = {name: [] for name in by_symbol}
    for row in original:
        if (row['name'], row['reference']) != reference_rows[row['address']] or \
                row['name'] != exported[row['address']]['logical_name']:
            raise ValueError('Wrong reference name/module: '+row['address'])
        if not row.get('note') or row['status'] not in ('source_reviewed', 'sdk_boundary'):
            raise ValueError('Missing review disposition: '+row['address'])
        if row['status'] == 'source_reviewed' and not row['native']:
            raise ValueError('Application address has no native target: '+row['address'])
        for target in row['native']:
            if target not in by_symbol:
                raise ValueError('Unknown native target: '+target)
            links[target].append(row['address'])
    extras = manifest['native_support']
    if set(extras) - set(by_symbol):
        raise ValueError('Unknown support function')
    for row in indexed:
        name = row['symbol']
        if not links[name] and name not in extras:
            raise ValueError('Unaccounted native function: '+name)
        if name in extras and not extras[name].get('note'):
            raise ValueError('Support function without reason: '+name)
        row['factory'] = sorted(links[name])
        row['disposition'] = extras.get(name, {'kind': 'reconstruction', 'note': 'See linked factory rows.'})
    for name, row in manifest['assembly_only'].items():
        if not row.get('note') or not row.get('native'):
            raise ValueError('Missing assembly-only disposition: '+name)
        if any(target not in by_symbol for target in row['native']):
            raise ValueError('Unknown assembly-only target: '+name)
        evidence = root/row['evidence']
        if not evidence.is_relative_to(root/'reference/assembly') or \
                not re.search(r'(?m)^'+re.escape(name[2:])+':', evidence.read_text(encoding='utf-8')):
            raise ValueError('Missing addressed assembly: '+name)
    reference = '\n'.join(path.read_text(encoding='utf-8') for path in sorted((root/'reference').glob('*.c')))
    missing_calls = sorted(set('0x'+a for a in re.findall(r'\bFUN_ram_([0-9a-f]{8})\s*\(', reference))-
                           set(exported))
    check_navigation(symbols, manifest)
    return dict(schema=1, passed=True, semantic_equivalence_proved=False,
                factory_export_functions=len(original), factory_dispositions=dict(Counter(r['status'] for r in original)),
                native_source_functions=len(indexed), native_app_functions=sum(r['symbol'].startswith('app/') for r in indexed),
                inputs=sources, factory=original, native=indexed, assembly_only=manifest['assembly_only'],
                unexported_direct_callees=missing_calls,
                limitations=manifest['limitations'], findings=manifest['findings'])


def main() -> None:
    """Validate a manually reviewed manifest and optionally save the inventory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'reference/correspondence.json')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit(ROOT, json.loads(args.manifest.read_text(encoding='utf-8')))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(f"PASS: {result['factory_export_functions']} factory / {result['native_app_functions']} app / "
          f"{result['native_source_functions']} total source functions; this is an inventory, not an equivalence proof")


if __name__ == '__main__':
    main()
