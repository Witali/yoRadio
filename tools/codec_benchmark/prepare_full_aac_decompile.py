#!/usr/bin/env python3
"""Link every pinned AAC decoder object into an analysis-only ELF, without GC.

The firmware ELF supplies external SDK symbol addresses, not executable code.
This analysis ELF must never be flashed or executed. Requires pyelftools.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile

PINNED = '311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(archive, firmware, prefix, output):
    archive, firmware, output = archive.resolve(), firmware.resolve(), output.resolve()
    if digest(archive) != PINNED:
        raise ValueError('Archive changed; audit the AAC member boundaries first')
    output.mkdir(parents=True, exist_ok=True)
    suffix = '.exe' if Path(prefix + 'ar.exe').exists() else ''
    ar, cc = prefix + 'ar' + suffix, prefix + 'gcc' + suffix
    members = subprocess.check_output([ar, 't', str(archive)], text=True).splitlines()
    first, last = members.index('analysis_sub_band.c.obj'), members.index('window_tables_fxp.c.obj')
    selected = ['esp_aac_dec.c.obj'] + members[first:last+1] + [
        'calc_sbr_anafilterbank_core.c.obj', 'calc_sbr_synfilterbank.c.obj',
        'synthesis_sub_band_lc_core.c.obj']
    if len(selected) != 144 or len(set(selected)) != 144:
        raise ValueError('Unexpected AAC object inventory')
    # ar p on Windows can translate binary stdout; extract directly to files.
    subprocess.run([ar, 'x', str(archive)] + selected, cwd=output, check=True)
    functions, objects = [], []
    defined, undefined = set(), set()
    for name in selected:
        path = output / name
        row = dict(member=name, sha256=digest(path), functions=[], data=[])
        with path.open('rb') as stream:
            elf = ELFFile(stream)
            symbols = elf.get_section_by_name('.symtab')
            for symbol in symbols.iter_symbols() if symbols else ():
                if symbol.name and symbol['st_info']['bind'] != 'STB_LOCAL':
                    (undefined if symbol['st_shndx'] == 'SHN_UNDEF' else defined).add(symbol.name)
                if symbol['st_shndx'] == 'SHN_UNDEF' or not symbol['st_size']:
                    continue
                record = dict(name=symbol.name, member=name, bytes=symbol['st_size'],
                              binding=symbol['st_info']['bind'])
                if symbol['st_info']['type'] == 'STT_FUNC':
                    functions.append(record)
                    row['functions'].append(symbol.name)
                elif symbol['st_info']['type'] == 'STT_OBJECT':
                    row['data'].append(record)
        objects.append(row)
    if len(functions) != 186 or len({f['name'] for f in functions}) != 186:
        raise ValueError('Unexpected or ambiguous function inventory')
    subset = output / 'aac-full.a'
    subprocess.run([ar, 'rcs', str(subset)] + [str(output/n) for n in selected], check=True)
    external = []
    with firmware.open('rb') as stream:
        table = ELFFile(stream).get_section_by_name('.symtab')
        for name in sorted(undefined - defined - {'__global_pointer$'}):
            matches = [s for s in table.get_symbol_by_name(name) or ()
                       if s['st_info']['bind'] != 'STB_LOCAL' and s['st_shndx'] != 'SHN_UNDEF']
            if len(matches) != 1:
                raise ValueError('Missing/ambiguous external symbol: '+name)
            s = matches[0]
            external.append(dict(name=name, address=s['st_value'], type=s['st_info']['type']))
    # Import only actual external dependencies. --just-symbols with the entire
    # firmware would override the AAC definitions with their old addresses.
    assembly = []
    for symbol in external:
        name = symbol['name']
        kind = 'function' if symbol['type'] == 'STT_FUNC' else 'object'
        assembly += [f'.globl {name}', f'.type {name}, @{kind}', f'.set {name}, {symbol["address"]}']
    source = output/'external-symbols.S'
    source.write_text('\n'.join(assembly)+'\n', newline='\n')
    subprocess.run([cc, '-c', str(source), '-o', str(output/'external-symbols.o')], check=True)
    linked = output / 'aac-full.elf'
    command = [cc, '-nostdlib', '-Wl,--no-relax', '-Wl,-Ttext=0x43000000',
               '-Wl,-Tdata=0x3ef00000', '-Wl,-e,esp_aac_dec_decode',
               str(output/'external-symbols.o'), '-Wl,--whole-archive', str(subset),
               '-Wl,--no-whole-archive', '-o', str(linked)]
    result = subprocess.run(command, capture_output=True, text=True)
    (output/'link.log').write_text(result.stdout+result.stderr, newline='\n')
    result.check_returncode()
    with linked.open('rb') as stream:
        elf = ELFFile(stream)
        table = elf.get_section_by_name('.symtab')
        for function in functions:
            matches = [s for s in table.get_symbol_by_name(function['name'])
                       if isinstance(s['st_shndx'], int) and s['st_info']['type'] == 'STT_FUNC']
            if len(matches) != 1:
                raise ValueError('Function missing/duplicated in analysis ELF: '+function['name'])
            function['address'] = f"{matches[0]['st_value']:08x}"
    (output/'functions.txt').write_text('\n'.join(f['name'] for f in functions)+'\n', newline='\n')
    manifest = dict(scope='All 144 AAC decoder members including optimized filter cores; excludes AAC encoder and other codecs',
                    archive_sha256=digest(archive), firmware_symbols_sha256=digest(firmware),
                    elf_sha256=digest(linked), analysis_only=True, command=command,
                    objects=objects, functions=functions, external_symbols=external)
    (output/'inventory.json').write_text(json.dumps(manifest, indent=2)+'\n', newline='\n')
    print(f'Linked {len(objects)} members / {len(functions)} functions; analysis only: {linked}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--firmware', type=Path, required=True)
    parser.add_argument('--tool-prefix', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.archive, args.firmware, args.tool_prefix, args.output)
