#!/usr/bin/env python3
"""Route one verified native branch through a QEMU-only SBR retention predicate.

No DSP instructions, input syntax or structure offsets are changed. Native
continuations come from the pinned object's local symbol and branch relocation.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess
from elftools.elf.elffile import ELFFile
from compact_sbr_tables import PIN

SECTION = '.text.PVMP4AudioDecodeFrame'
BRANCH_LABEL = '.L140'
ACTIVE_LABEL = '.L245'
ELEMENT_LOAD = bytes.fromhex('03270a00')  # lw a4,0(s4)
BRANCH_WORD = 0x5a071b63                 # bnez a4,.L245 in the pinned object
DISABLE_PREFIX = bytes.fromhex('230404002320040c232e040a')
R_RISCV_BRANCH, R_RISCV_JAL = 16, 17


def digest(data):
    return hashlib.sha256(data).hexdigest()


def locate(data):
    elf = ELFFile(io.BytesIO(data))
    if elf.elfclass != 32 or not elf.little_endian or elf['e_machine'] != 'EM_RISCV':
        raise ValueError('Expected little-endian RV32 native object')
    code = elf.get_section_by_name(SECTION)
    symtab = elf.get_section_by_name('.symtab')
    rels = elf.get_section_by_name('.rela'+SECTION)
    if code is None or symtab is None or rels is None:
        raise ValueError('Missing native code, symbols or relocations')
    labels = {}
    for name in (BRANCH_LABEL, ACTIVE_LABEL):
        symbols = symtab.get_symbol_by_name(name)
        if not symbols or len(symbols) != 1 or elf.get_section(symbols[0]['st_shndx']).name != SECTION:
            raise ValueError('Missing or ambiguous native continuation: '+name)
        labels[name] = symbols[0]['st_value']
    load = labels[BRANCH_LABEL]
    branch = load + len(ELEMENT_LOAD)
    disable = branch + 4
    if (code.data()[load:branch] != ELEMENT_LOAD or
            struct.unpack_from('<I', code.data(), branch)[0] != BRANCH_WORD or
            code.data()[disable:disable+len(DISABLE_PREFIX)] != DISABLE_PREFIX):
        raise ValueError('Native branch/register/disable instructions changed')
    matches = [(i,r) for i,r in enumerate(rels.iter_relocations()) if branch <= r['r_offset'] < disable]
    if len(matches) != 1:
        raise ValueError('Expected one branch relocation')
    index, rel = matches[0]
    if (rel['r_offset'] != branch or rel['r_info_type'] != R_RISCV_BRANCH or
            symtab.get_symbol(rel['r_info_sym']).name != ACTIVE_LABEL or rel['r_addend']):
        raise ValueError('Native branch relocation changed')
    return elf, code, symtab, rels, index, branch, disable, labels[ACTIVE_LABEL]


def build(native, bridge, cc, linker, objcopy):
    original = native.read_bytes()
    previous = json.loads((native.parent/'audit.json').read_text())
    if (previous['codec_sha256'] != PIN or
            previous['functions']['PVMP4AudioDecodeFrame']['output_sha256'] != digest(original)):
        raise ValueError('Native input does not match the pinned compact-layout audit')
    _, _, _, _, _, branch, disable, active = locate(original)
    directory = native.parent
    (directory/'late-sbr-input.o').write_bytes(original)
    named = directory/'late-sbr-native.o'
    bridge_object = directory/'late-sbr-bridge.o'
    merged = directory/'late-sbr-merged.o'
    subprocess.run([str(objcopy), '--add-symbol', f'aac_late_sbr_native_active={SECTION}:{active},global,function',
                    '--add-symbol', f'aac_late_sbr_native_disable={SECTION}:{disable},global,function',
                    str(native), str(named)], check=True)
    subprocess.run([str(cc), '-march=rv32imc', '-mabi=ilp32', '-c', str(bridge), '-o', str(bridge_object)], check=True)
    subprocess.run([str(linker), '-r', str(named), str(bridge_object), '-o', str(merged)], check=True)
    data = merged.read_bytes()
    elf, code, symbols, rels, index, found, _, _ = locate(data)
    if found != branch:
        raise ValueError('Relocatable link moved the branch')
    targets = [i for i,s in enumerate(symbols.iter_symbols()) if s.name=='aac_late_sbr_select']
    if len(targets) != 1 or symbols.get_symbol(targets[0])['st_shndx']=='SHN_UNDEF':
        raise ValueError('Missing bridge definition')
    result = bytearray(data)
    struct.pack_into('<I', result, code['sh_offset']+branch, 0x0000006f) # JAL x0, bridge
    # ELF32 Rela: offset, symbol/type, addend. Keep the instruction position.
    reloc = rels['sh_offset'] + index*rels['sh_entsize']
    struct.pack_into('<IIi', result, reloc, branch, (targets[0]<<8)|R_RISCV_JAL, 0)
    native.write_bytes(result)
    audit = dict(experiment='qemu_missing_sbr_retention', input_sha256=digest(original),
                 bridge_source_sha256=digest(bridge.read_bytes()), output_sha256=digest(result),
                 section=SECTION, branch_offset=branch, original=f'{BRANCH_WORD:08x}', replacement='0000006f',
                 active_label=ACTIVE_LABEL, active_offset=active, disable_offset=disable,
                 branch_target='aac_late_sbr_select', changed_native_bytes=4,
                 bridge_stack_bytes=64, structure_offsets_changed=False)
    (directory/'late-sbr-audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8',newline='\n')
    return audit


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('native','bridge','cc','linker','objcopy'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(build(args.native,args.bridge,args.cc,args.linker,args.objcopy)))
