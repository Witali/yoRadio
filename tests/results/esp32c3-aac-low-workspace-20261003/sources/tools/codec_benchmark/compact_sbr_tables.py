#!/usr/bin/env python3
"""Build QEMU-only copies of the pinned RV32 decoder with five-entry SBR tables.

Only audited address/stride immediates change; DSP instructions and relocations
are retained. The SDK archive is never modified. See the accompanying audit.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile

PIN = '311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909'
PREFIX = 'compact5_'

# (instruction offset, original word, compiler-layout expression, meaning).
# Instruction locations/words describe the pinned archive, not RAM addresses.
# C.LUI immediates below are in 4096-byte units; I/S immediates are bytes.
PATCH_SPECS = {
 'init_sbr_dec': [
  (0x58, '1117a023', 'scale:table_size:1', 'table 1 stride'),
  (0x5c, '3107a023', 'scale:table_size:3', 'table 3 stride'),
  (0x60, '2067a023', 'scale:table_size:2', 'table 2 stride')],
 'sbr_open': [
  (0xa, '64b5', 'hi:ps_flag', 'two-channel end high'),
  (0x14, '98048493', 'lo:ps_flag', 'two-channel end low'),
  (0x40, '4c098993', 'lo:channel_size', 'channel stride'),
  (0x4c, '4c060613', 'lo:channel_size', 'channel memset length')],
 'sbr_read_data': [
  (0x8a, '58870713', 'lo:right_header', 'right header'),
  (0xbe, '67b5', 'hi:ps_data', 'channel loop end high'),
  (0xc0, '98878793', 'lo:ps_data', 'channel loop end low'),
  (0xe6, '4c078793', 'lo:channel_size', 'channel stride'),
  (0xfe, '4c858593', 'lo:right_frame', 'right frame'),
  (0x15c, '67b5', 'hi:ps_pointer', 'PS pointer high'),
  (0x160, '9847a603', 'lo:ps_pointer', 'PS pointer low')],
 'sbr_applied': [
  (0x3c, '67b5', 'hi:ps_pointer', 'PS pointer high'),
  (0x40, '9847a503', 'lo:ps_pointer', 'PS pointer low'),
  (0x54, '9847a803', 'lo:ps_pointer', 'PS pointer reload'),
  (0x62, '78070713', 'lo:right_synthesis', 'right synthesis V'),
  (0x100, '4c47a683', 'lo:right_status', 'right status'),
  (0x10a, '4c860613', 'lo:right_frame', 'right frame'),
  (0x10e, '2fc7ae23', 'lo:right_high_real', 'right high real pointer'),
  (0x112, 'e667ac23', 'lo:right_high_imag', 'right high imaginary pointer'),
  (0x1a8, '6635', 'hi:ps_flag', 'PS control high'),
  (0x1ac, '98062583', 'lo:ps_flag', 'PS initialization flag'),
  (0x1b2, '98062023', 'lo:ps_flag', 'PS initialization flag store'),
  (0x1b6, '98462603', 'lo:ps_pointer', 'PS pointer low'),
  (0x1fc, '4c850513', 'lo:right_frame', 'right frame'),
  (0x222, '6406a683', 'lo:right_coupling', 'right coupling'),
  (0x26e, '4c46a683', 'lo:right_status', 'right status'),
  (0x286, '4c868693', 'lo:right_frame', 'right frame')],
 'ps_allocate_decoder': [
  (0x8, '67b5', 'hi:ps_pointer', 'PS pointer high'),
  (0x10, '9847a983', 'lo:ps_pointer', 'PS pointer low'),
  (0x32, '67860613', 'lo:ps_peak', 'right PS workspace 0'),
  (0x38, '6c868693', 'lo:ps_energy', 'right PS workspace 1'),
  (0x3c, '71870713', 'lo:ps_difference', 'right PS workspace 2'),
  (0x40, '76878793', 'lo:ps_hybrid', 'right hybrid workspace'),
  (0x92, '0c0a8a93', 'lo:ps_allpass_qmf', 'allpass QMF workspace'),
  (0x7c, '6a25', 'hi:ps_allpass_sub', 'allpass sub-QMF workspace high'),
  (0x96, '8a0a0a13', 'lo:ps_allpass_sub', 'allpass sub-QMF workspace low'),
  (0x9a, 'cc048493', 'lo:ps_delay_real', 'main QMF real history'),
  (0x9e, 'dc090913', 'lo:ps_delay_imag', 'main QMF imaginary history'),
  (0xa2, 'fc0b8b93', 'lo:ps_real_pointers', 'real delay pointer table'),
  (0xa6, '2c0b0b13', 'lo:ps_imag_pointers', 'imaginary delay pointer table'),
  (0x102, 'fc078793', 'lo:ps_real_pointers', 'real delay table initialization cursor')],
 'sbr_dec': [
  (0x1fa, '3b850513', 'lo:frame_table_3', 'smoothing pointer table 3'),
  (0x1fe, '2b868693', 'lo:frame_table_2', 'smoothing pointer table 2'),
  (0x202, '1b870713', 'lo:frame_table_1', 'smoothing pointer table 1')],
 'PVMP4AudioDecodeFrame': [
  (0x800, '67b5', 'hi:ps_data', 'PS embedded address high'),
  (0x80a, '66b5', 'hi:ps_pointer', 'PS pointer high'),
  (0x80c, '98878793', 'lo:ps_data', 'PS embedded address low'),
  (0x816, '98f6a223', 'lo:ps_pointer', 'PS pointer store'),
  (0x98c, '66b5', 'hi:ps_flag', 'PS flag high'),
  (0x996, '98d7a023', 'lo:ps_flag', 'PS flag store')],
}
MEMBERS = {s: (s if s != 'PVMP4AudioDecodeFrame' else 'pvmp4audiodecoderframe') + '.c.obj' for s in PATCH_SPECS}



def read_layout(data):
    elf = ELFFile(io.BytesIO(data))
    if elf.elfclass != 32 or not elf.little_endian or elf['e_machine'] != 'EM_RISCV':
        raise ValueError('ABI layout must be a little-endian RV32 compiler object')
    result = {}
    for symbol in elf.get_section_by_name('.symtab').iter_symbols():
        if symbol['st_info']['type'] != 'STT_OBJECT' or not symbol.name.startswith('aac_abi_'):
            continue
        if symbol['st_size'] != 8:
            raise ValueError('Expected an original/compact layout pair')
        section = elf.get_section(symbol['st_shndx'])
        offset = symbol['st_value'] - section['sh_addr']
        values = section.data()[offset:offset+8]
        name = symbol.name.removeprefix('aac_abi_')
        if name in result or len(values) != 8:
            raise ValueError('Duplicate/truncated ABI descriptor')
        result[name] = [int.from_bytes(values[n:n+4], 'little') for n in (0,4)]
    needed = {expr.split(':')[1] for rows in PATCH_SPECS.values() for _,_,expr,_ in rows}
    needed.add('owner_size')
    if set(result) != needed:
        raise ValueError('Missing/extra compiler ABI fields')
    return result


def resolve_patches(layout):
    def value(expression):
        operation, field, *factor = expression.split(':')
        address = layout[field][1]
        high = (address + 0x800) >> 12
        if operation == 'hi': return high
        if operation == 'lo': return address - (high << 12)
        if operation == 'scale': return address * int(factor[0])
        raise ValueError('Unknown ABI expression')
    return {name: [(offset, word, value(expr), meaning) for offset,word,expr,meaning in rows]
            for name,rows in PATCH_SPECS.items()}


def immediate(word, width, value):
    if width == 2:
        if word & 0xe003 != 0x6001 or not 0 < value < 32:
            raise ValueError('Expected positive C.LUI')
        return (word & ~0x107c) | ((value & 31) << 2) | ((value & 32) << 7)
    if not -2048 <= value <= 2047:
        raise ValueError('Immediate out of range')
    value &= 0xfff
    if word & 0x7f in (0x03, 0x13):
        return (word & 0xfffff) | (value << 20)
    if word & 0x7f == 0x23:
        return (word & ~0xfe000f80) | ((value >> 5) << 25) | ((value & 31) << 7)
    raise ValueError('Unexpected instruction opcode')


def transform(data, symbol, patches):
    elf = ELFFile(io.BytesIO(data))
    section = elf.get_section_by_name('.text.' + symbol)
    if section is None:
        raise ValueError('Missing function section ' + symbol)
    patched = bytearray(data)
    changes = []
    for offset, old, value, meaning in patches[symbol]:
        width = len(old) // 2
        position = section['sh_offset'] + offset
        expected = int(old, 16)
        if int.from_bytes(data[position:position+width], 'little') != expected:
            raise ValueError(f'Instruction mismatch: {symbol}+{offset:#x}')
        new = immediate(expected, width, value)
        patched[position:position+width] = new.to_bytes(width, 'little')
        changes.append(dict(offset=hex(offset), original=old, replacement=f'{new:0{width*2}x}', meaning=meaning))
    # No relocation may overwrite a patched immediate or straddle it.
    for sec in elf.iter_sections():
        if sec.name == '.rela.text.' + symbol:
            for rel in sec.iter_relocations():
                if any(off <= rel['r_offset'] < off + len(old)//2 for off, old, _, _ in patches[symbol]):
                    raise ValueError('Patch overlaps a relocation')
    return bytes(patched), changes


def build(archive, output, ar, objcopy, layout_object=None):
    if hashlib.sha256(archive.read_bytes()).hexdigest() != PIN:
        raise ValueError('AAC archive SHA differs; refusing ABI patch')
    if layout_object is None:
        raise ValueError('Compiler-generated ABI layout is required')
    layout = read_layout(layout_object.read_bytes())
    patches = resolve_patches(layout)
    output.mkdir(parents=True, exist_ok=True)
    mapping = output / 'symbols.txt'
    mapping.write_text(''.join(f'{s} {PREFIX}{s}\n' for s in
                              (*PATCH_SPECS, 'defaultHeader', 'aRevLinkDelaySer')), newline='\n')
    evidence = dict(codec_sha256=PIN, original_channel=layout['channel_size'][0], compact_channel=layout['channel_size'][1],
                    original_owner=layout['owner_size'][0], compact_owner=layout['owner_size'][1],
                    requested_saving=layout['owner_size'][0]-layout['owner_size'][1],
                    compiler_layout=layout, layout_sha256=hashlib.sha256(layout_object.read_bytes()).hexdigest(),
                    scope='QEMU experiment only; original reset API is not supported', functions={})
    for symbol, member in MEMBERS.items():
        # Windows binutils may translate stdout LF bytes in `ar p`; extract to
        # a file so ELF contents cannot pass through text-mode stdout.
        subprocess.run([str(ar.resolve()), 'x', str(archive.resolve()), member], cwd=output, check=True)
        path = output / member
        original = path.read_bytes()
        modified, changes = transform(original, symbol, patches)
        path.write_bytes(modified)
        subprocess.run([str(objcopy), '--redefine-syms=' + str(mapping), str(path)], check=True)
        evidence['functions'][symbol] = dict(input_sha256=hashlib.sha256(original).hexdigest(),
            output_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), patches=changes)
    (output / 'audit.json').write_text(json.dumps(evidence, indent=2) + '\n', newline='\n')
    return evidence


if __name__ == '__main__':
    p = argparse.ArgumentParser(__doc__)
    p.add_argument('--archive', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--ar', required=True, type=Path)
    p.add_argument('--objcopy', required=True, type=Path)
    p.add_argument('--layout-object', required=True, type=Path)
    a = p.parse_args()
    result = build(a.archive, a.output, a.ar, a.objcopy, a.layout_object)
    print(f"Compact SBR owner: {result['compact_owner']} bytes; savings {result['requested_saving']} bytes")
