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
STRIDE = 0x64c0 - 4 * (64 - 5) * 4
SIZE = 2 * STRIDE + 8 + 3536
PREFIX = 'compact5_'

# (section offset, original instruction, new immediate, meaning).
# C.LUI immediates below are in 4096-byte units; I/S immediates are bytes.
PATCHES = {
 'init_sbr_dec': [
  (0x58, '1117a023', 20, 'table 1 stride'),
  (0x5c, '3107a023', 60, 'table 3 stride'),
  (0x60, '2067a023', 40, 'table 2 stride')],
 'sbr_open': [
  (0x0a, '64b5', 12, 'two-channel end high'),
  (0x14, '98048493', 0x220, 'two-channel end low'),
  (0x40, '4c098993', 0x110, 'channel stride'),
  (0x4c, '4c060613', 0x110, 'channel memset length')],
 'sbr_read_data': [
  (0x8a, '58870713', 0x1d8, 'right header'),
  (0xbe, '67b5', 12, 'channel loop end high'),
  (0xc0, '98878793', 0x228, 'channel loop end low'),
  (0xe6, '4c078793', 0x110, 'channel stride'),
  (0xfe, '4c858593', 0x118, 'right frame'),
  (0x15c, '67b5', 12, 'PS pointer high'),
  (0x160, '9847a603', 0x224, 'PS pointer low')],
 'sbr_applied': [
  (0x3c, '67b5', 12, 'PS pointer high'),
  (0x40, '9847a503', 0x224, 'PS pointer low'),
  (0x54, '9847a803', 0x224, 'PS pointer reload'),
  (0x62, '78070713', 0x3d0, 'right synthesis V'),
  (0x100, '4c47a683', 0x114, 'right status'),
  (0x10a, '4c860613', 0x118, 'right frame'),
  (0x10e, '2fc7ae23', -180, 'right high real pointer'),
  (0x112, 'e667ac23', -1336, 'right high imaginary pointer'),
  (0x1a8, '6635', 12, 'PS control high'),
  (0x1ac, '98062583', 0x220, 'PS initialization flag'),
  (0x1b2, '98062023', 0x220, 'PS initialization flag store'),
  (0x1b6, '98462603', 0x224, 'PS pointer low'),
  (0x1fc, '4c850513', 0x118, 'right frame'),
  (0x222, '6406a683', 0x290, 'right coupling'),
  (0x26e, '4c46a683', 0x114, 'right status'),
  (0x286, '4c868693', 0x118, 'right frame')],
 'ps_allocate_decoder': [
  (0x08, '67b5', 12, 'PS pointer high'),
  (0x10, '9847a983', 0x224, 'PS pointer low'),
  (0x32, '67860613', 0x2c8, 'right PS workspace 0'),
  (0x38, '6c868693', 0x318, 'right PS workspace 1'),
  (0x3c, '71870713', 0x368, 'right PS workspace 2'),
  (0x40, '76878793', 0x3b8, 'right hybrid workspace'),
  (0x92, '0c0a8a93', -752, 'allpass QMF workspace'),
  (0x7c, '6a25', 8, 'allpass sub-QMF workspace high'),
  (0x96, '8a0a0a13', 0x4f0, 'allpass sub-QMF workspace low'),
  (0x9a, 'cc048493', -1776, 'main QMF real history'),
  (0x9e, 'dc090913', -1520, 'main QMF imaginary history'),
  (0xa2, 'fc0b8b93', -1008, 'real delay pointer table'),
  (0xa6, '2c0b0b13', -240, 'imaginary delay pointer table'),
  (0x102, 'fc078793', -1008, 'real delay table initialization cursor')],
 'sbr_dec': [
  (0x1fa, '3b850513', 0xf4, 'smoothing pointer table 3'),
  (0x1fe, '2b868693', 0xe0, 'smoothing pointer table 2'),
  (0x202, '1b870713', 0xcc, 'smoothing pointer table 1')],
 'PVMP4AudioDecodeFrame': [
  (0x800, '67b5', 12, 'PS embedded address high'),
  (0x80a, '66b5', 12, 'PS pointer high'),
  (0x80c, '98878793', 0x228, 'PS embedded address low'),
  (0x816, '98f6a223', 0x224, 'PS pointer store'),
  (0x98c, '66b5', 12, 'PS flag high'),
  (0x996, '98d7a023', 0x220, 'PS flag store')],
}
MEMBERS = {s: (s if s != 'PVMP4AudioDecodeFrame' else 'pvmp4audiodecoderframe') + '.c.obj' for s in PATCHES}


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


def transform(data, symbol):
    elf = ELFFile(io.BytesIO(data))
    section = elf.get_section_by_name('.text.' + symbol)
    if section is None:
        raise ValueError('Missing function section ' + symbol)
    patched = bytearray(data)
    changes = []
    for offset, old, value, meaning in PATCHES[symbol]:
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
                if any(off <= rel['r_offset'] < off + len(old)//2 for off, old, _, _ in PATCHES[symbol]):
                    raise ValueError('Patch overlaps a relocation')
    return bytes(patched), changes


def build(archive, output, ar, objcopy):
    if hashlib.sha256(archive.read_bytes()).hexdigest() != PIN:
        raise ValueError('AAC archive SHA differs; refusing ABI patch')
    output.mkdir(parents=True, exist_ok=True)
    mapping = output / 'symbols.txt'
    mapping.write_text(''.join(f'{s} {PREFIX}{s}\n' for s in
                              (*PATCHES, 'defaultHeader', 'aRevLinkDelaySer')), newline='\n')
    evidence = dict(codec_sha256=PIN, original_channel=25792, compact_channel=STRIDE,
                    original_owner=55128, compact_owner=SIZE, requested_saving=55128-SIZE,
                    scope='QEMU experiment only; original reset API is not supported', functions={})
    for symbol, member in MEMBERS.items():
        # Windows binutils may translate stdout LF bytes in `ar p`; extract to
        # a file so ELF contents cannot pass through text-mode stdout.
        subprocess.run([str(ar.resolve()), 'x', str(archive.resolve()), member], cwd=output, check=True)
        path = output / member
        original = path.read_bytes()
        modified, changes = transform(original, symbol)
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
    a = p.parse_args()
    result = build(a.archive, a.output, a.ar, a.objcopy)
    print(f"Compact SBR owner: {result['compact_owner']} bytes; savings {result['requested_saving']} bytes")
