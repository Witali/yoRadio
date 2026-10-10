"""Verify the experimental input allocator hook in a linked ESP32-C3 image."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

from elftools.elf.elffile import ELFFile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--sdkconfig', type=Path, required=True)
    parser.add_argument('--objdump', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    config = args.sdkconfig.read_text()
    for setting in ('CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=y',
                    'CONFIG_MBEDTLS_INTERNAL_MEM_ALLOC=y',
                    'CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN=16384',
                    'CONFIG_MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL=y'):
        assert setting in config.splitlines(), setting
    with args.elf.open('rb') as stream:
        elf = ELFFile(stream)
        symbols = elf.get_section_by_name('.symtab')
        def symbol(name):
            found = symbols.get_symbol_by_name(name)
            assert found and len(found) == 1, name
            return found[0]
        pointer = symbol('mbedtls_calloc_func')
        wrapper = symbol('__wrap_esp_mbedtls_mem_calloc')
        assert pointer['st_size'] == 4
        section = elf.get_section(pointer['st_shndx'])
        offset = pointer['st_value'] - section['sh_addr']
        target = int.from_bytes(section.data()[offset:offset + 4], 'little')
        assert target == wrapper['st_value'], 'mbedTLS allocator hook is not installed'
    disassembly = subprocess.check_output([
        args.objdump, '-d', '--disassemble=__wrap_esp_mbedtls_mem_calloc', str(args.elf)], text=True)
    for function in ('adaptive_input_release_one', 'esp_mbedtls_mem_calloc',
                     'heap_caps_get_largest_free_block'):
        assert re.search(r'<'+re.escape(function)+r'>', disassembly), function
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(
        passed=True, allocator_pointer=hex(target),
        elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),
        sdkconfig_sha256=hashlib.sha256(args.sdkconfig.read_bytes()).hexdigest(),
        scope='Linked allocator function pointer and required call targets; not playback qualification.'
    ), indent=2) + '\n')
    args.output.with_suffix('.disassembly.txt').write_text(disassembly)
    print('PASS linked adaptive input allocator')


if __name__ == '__main__':
    main()
