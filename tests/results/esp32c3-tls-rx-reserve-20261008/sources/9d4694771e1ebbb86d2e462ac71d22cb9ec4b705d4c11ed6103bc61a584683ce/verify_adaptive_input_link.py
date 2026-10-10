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
    adaptive = 'CONFIG_YORADIO_ADAPTIVE_INPUT_BUFFER=y' in config.splitlines()
    reserved = 'CONFIG_YORADIO_TLS_LARGE_BLOCK_RESERVE=y' in config.splitlines()
    assert adaptive or reserved, 'No experimental TLS allocator enabled'
    for setting in ('CONFIG_MBEDTLS_INTERNAL_MEM_ALLOC=y',
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
        def verify_pointer(name, target_name):
            pointer, target = symbol(name), symbol(target_name)
            assert pointer['st_size'] == 4
            section = elf.get_section(pointer['st_shndx'])
            offset = pointer['st_value'] - section['sh_addr']
            address = int.from_bytes(section.data()[offset:offset + 4], 'little')
            assert address == target['st_value'], name + ' is not hooked'
            return hex(address)
        allocation_target = verify_pointer('mbedtls_calloc_func', '__wrap_esp_mbedtls_mem_calloc')
        free_target = None
        storage = None
        if reserved:
            free_target = verify_pointer('mbedtls_free_func', '__wrap_esp_mbedtls_mem_free')
            block = symbol('s_tls_large_storage')
            section = elf.get_section(block['st_shndx'])
            # This reviewed capacity is also the host-test sizing fixture.
            assert block['st_size'] == 17058, 'Review changed SDK buffer sizing'
            assert block['st_value'] % 16 == 0 and section['sh_type'] == 'SHT_NOBITS'
            assert section.name == '.dram0.bss', 'Reserve must reside in static DRAM'
            storage = dict(bytes=block['st_size'], address=hex(block['st_value']), section=section.name)
    disassembly = subprocess.check_output([args.objdump, '-d', str(args.elf)], text=True)
    functions = dict(re.findall(r'^[0-9a-f]+ <([^>]+)>:\n(.*?)(?=^[0-9a-f]+ <|\Z)',
                                disassembly, flags=re.M | re.S))
    def reachable(entry):
        found, pending = set(), [entry]
        # Follow only our allocator helpers, never traverse the entire SDK.
        while pending:
            name = pending.pop()
            calls = set(re.findall(r'<([^>+]+)(?:\+[^>]*)?>', functions.get(name, '')))
            found.update(calls)
            pending.extend(c for c in calls if c.startswith('allocate') and c not in seen)
            seen.update(calls)
        return found
    seen = set()
    calls = reachable('__wrap_esp_mbedtls_mem_calloc')
    assert 'esp_mbedtls_mem_calloc' in calls
    if adaptive:
        assert 'adaptive_input_release_one' in calls and 'heap_caps_get_largest_free_block' in calls
    if reserved:
        assert 'tls_large_reserve_calloc' in calls
        frees = functions['__wrap_esp_mbedtls_mem_free']
        assert '<tls_large_reserve_free>' in frees and '<esp_mbedtls_mem_free>' in frees
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(dict(
        passed=True, allocator_pointer=allocation_target, free_pointer=free_target,
        adaptive_input=adaptive, reserved_storage=storage,
        elf_sha256=hashlib.sha256(args.elf.read_bytes()).hexdigest(),
        sdkconfig_sha256=hashlib.sha256(args.sdkconfig.read_bytes()).hexdigest(),
        scope='Linked allocator function pointer and required call targets; not playback qualification.'
    ), indent=2) + '\n')
    selected = ['__wrap_esp_mbedtls_mem_calloc', '__wrap_esp_mbedtls_mem_free',
                'tls_large_reserve_calloc', 'tls_large_reserve_free']
    args.output.with_suffix('.disassembly.txt').write_text('\n'.join(
        name+':\n'+functions[name] for name in selected if name in functions))
    print('PASS linked adaptive input allocator')


if __name__ == '__main__':
    main()
