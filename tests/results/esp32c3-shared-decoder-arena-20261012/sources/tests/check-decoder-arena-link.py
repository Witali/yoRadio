"""Verify allocator call edges and configuration of the experimental ELF."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf', type=Path, required=True)
    p.add_argument('--objdump', required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--baseline-config', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    text = subprocess.check_output([a.objdump, '-d', str(a.elf)], text=True)
    functions = {}
    for block in re.split(r'(?=^[0-9a-f]+ <[^>]+>:\n)', text, flags=re.M):
        match = re.match(r'([0-9a-f]+) <([^>]+)>:', block)
        if match:
            functions[match[2]] = (int(match[1], 16), block)
    edges = {
        'media_lib_module_malloc': '__wrap_malloc',
        'media_lib_module_calloc': '__wrap_calloc',
        'media_lib_module_realloc': '__wrap_realloc',
        'media_lib_free': '__wrap_free',
        '_Znwj': '__wrap_malloc', '_ZdlPv': '__wrap_free',
        'decoder_task': 'decoder_arena_select',
        'audio_service_start': 'decoder_arena_init',
        'esp_mbedtls_mem_calloc': 'heap_caps_calloc',
    }
    for caller, callee in edges.items():
        assert caller in functions and '<' + callee + '>' in functions[caller][1], (caller, callee)
    for name in ('malloc', 'calloc', 'free', 'realloc'):
        address = functions['__wrap_' + name][0]
        assert 0x40380000 <= address < 0x403e0000, (name, address)
    def config(path):
        return dict(re.findall(r'^(CONFIG_\w+)=(.*)$', path.read_text(), re.M))
    candidate, baseline = config(a.config), config(a.baseline_config)
    changed = {k: [baseline.get(k), candidate.get(k)] for k in baseline.keys() | candidate.keys()
               if baseline.get(k) != candidate.get(k)}
    permitted = {'CONFIG_YORADIO_SHARED_DECODER_ARENA', 'CONFIG_YORADIO_SHARED_DECODER_ARENA_BYTES'}
    assert set(changed) <= permitted, changed
    report = dict(result='PASS', elf_sha256=hashlib.sha256(a.elf.read_bytes()).hexdigest(),
                  edges=edges, configuration_changes=changed,
                  limitation='Call edges and wrapper placement; no claim that all SDK allocations use libc.')
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))

if __name__ == '__main__':
    main()
