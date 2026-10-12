"""Compare linked C3 IRAM and the start of the aliased DRAM heap.

Run with ESP-IDF's Python (pyelftools and esp_idf_size are required).
Arguments are LABEL=BUILD_DIRECTORY; the first build is the baseline.
No firmware is installed and no device is contacted.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from elftools.elf.elffile import ELFFile


BOUNDARIES = ('_iram_start', '_iram_end', '_data_start', '_data_end',
              '_bss_start', '_bss_end', '_heap_start')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(label, directory):
    elf_path = directory / 'yoradio_esp32c3_oled_native.elf'
    map_path = elf_path.with_suffix('.map')
    config = directory / 'sdkconfig'
    archives = json.loads(subprocess.check_output([
        sys.executable, '-m', 'esp_idf_size', '--format', 'json2',
        '--archives', str(map_path)], text=True, encoding='utf-8'))
    ranked = []
    for archive in archives.values():
        sections = {name: item['size']
                    for memory in archive['memory_types'].values()
                    for name, item in memory['sections'].items()
                    if name.startswith('.iram') and item['size']}
        if sections:
            ranked.append(dict(archive=archive['abbrev_name'],
                               bytes=sum(sections.values()), sections=sections))
    with elf_path.open('rb') as stream:
        elf = ELFFile(stream)
        sections = list(elf.iter_sections())
        boundaries, iram_symbols, functions = {}, [], {}
        for symbol in elf.get_section_by_name('.symtab').iter_symbols():
            if symbol.name in BOUNDARIES:
                boundaries[symbol.name] = symbol['st_value']
            index = symbol['st_shndx']
            if not isinstance(index, int) or not symbol['st_size']:
                continue
            section = sections[index].name
            row = dict(name=symbol.name, address=symbol['st_value'],
                       bytes=symbol['st_size'], section=section)
            if section.startswith('.iram'):
                iram_symbols.append(row)
            if symbol['st_info']['type'] == 'STT_FUNC':
                # Static symbols can share names; do not silently overwrite them.
                functions.setdefault(symbol.name, []).append(row)
        iram_sections = [dict(name=s.name, address=s['sh_addr'], bytes=s['sh_size'])
                         for s in sections if s.name.startswith('.iram')]
    if set(boundaries) != set(BOUNDARIES):
        raise ValueError('Missing C3 linker boundaries')
    # C3 IRAM and DRAM alias the same SRAM; never add the aliases twice.
    if boundaries['_iram_end'] - boundaries['_data_start'] != 0x700000:
        raise ValueError('Unexpected C3 IRAM/DRAM layout')
    return dict(label=label, fingerprints={p.name: digest(p) for p in
                (elf_path, map_path, config)}, boundaries=boundaries,
                iram_reserved=boundaries['_iram_end']-boundaries['_iram_start'],
                dram_data=boundaries['_data_end']-boundaries['_data_start'],
                dram_bss=boundaries['_bss_end']-boundaries['_bss_start'],
                iram_sections=iram_sections,
                iram_archives=sorted(ranked, key=lambda r: r['bytes'], reverse=True),
                iram_symbols=sorted(iram_symbols, key=lambda r: r['bytes'], reverse=True),
                functions=functions)


def compare(builds):
    baseline = builds[0]
    for build in builds:
        build['iram_released_vs_baseline'] = baseline['iram_reserved']-build['iram_reserved']
        build['heap_start_released_vs_baseline'] = (
            baseline['boundaries']['_heap_start']-build['boundaries']['_heap_start'])
        moved = []
        if build is not baseline:
            for name, entries in baseline['functions'].items():
                if len(entries) != 1 or not entries[0]['section'].startswith('.iram'):
                    continue
                targets = build['functions'].get(name, [])
                if len(targets) == 1 and targets[0]['section'] == '.flash.text':
                    moved.append(dict(name=name, baseline_iram_bytes=entries[0]['bytes'],
                                      flash_bytes=targets[0]['bytes']))
        build['functions_moved_to_flash'] = sorted(
            moved, key=lambda r: r['baseline_iram_bytes'], reverse=True)
    for build in builds:
        del build['functions']
    return dict(schema=1, note='Linker capacity, not measured runtime free heap. '
                'IRAM includes alignment. Missing symbols are not assumed relocated.', builds=builds)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='append', required=True, metavar='LABEL=DIRECTORY')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    builds = []
    for value in args.build:
        label, directory = value.split('=', 1)
        builds.append(inspect(label, Path(directory)))
    result = compare(builds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    for build in builds:
        print(f"{build['label']}: IRAM={build['iram_reserved']} "
              f"DRAM data={build['dram_data']} bss={build['dram_bss']} "
              f"heap capacity gain={build['heap_start_released_vs_baseline']}")


if __name__ == '__main__':
    main()
