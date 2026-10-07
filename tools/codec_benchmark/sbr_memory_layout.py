"""Measure pinned PacketVideo reference types with the C3 compiler, not host sizes.

Downloads reference headers into the requested output directory. These are a
layout reference, not the source of Espressif's modified binary decoder.
Requires pyelftools (included in the ESP-IDF Python environment).
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
from urllib.request import urlopen

from elftools.elf.elffile import ELFFile

REVISION = '437ced8a14944bf5450df50c5e7e7a6dfe20ea40'
SOURCE = f'https://android.googlesource.com/platform/frameworks/av/+/{REVISION}/media/libstagefright/codecs/aacdec/'
TYPES = ('SBRDECODER_DATA', 'SBR_FRAME_DATA', 'SBR_CHANNEL', 'SBR_DEC',
         'STRUCT_PS_DEC', 'tDec_Int_File')
PROBE = '''#define AAC_PLUS
#define HQ_SBR
#define PARAMETRICSTEREO
#include "s_tdec_int_file.h"
SBRDECODER_DATA survey_sbr;
SBR_DEC survey_tables;
tDec_Int_File survey_core;
'''


def layouts(path):
    def name(die):
        return die.attributes['DW_AT_name'].value.decode() if 'DW_AT_name' in die.attributes else ''

    def size(die):
        if 'DW_AT_byte_size' in die.attributes:
            return die.attributes['DW_AT_byte_size'].value
        if die.tag == 'DW_TAG_array_type':
            count = 1
            for child in die.iter_children():
                if child.tag == 'DW_TAG_subrange_type':
                    count *= child.attributes['DW_AT_upper_bound'].value + 1
            return count * size(die.get_DIE_from_attribute('DW_AT_type'))
        return size(die.get_DIE_from_attribute('DW_AT_type'))

    result = {}
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        if elf.elfclass != 32 or elf.header.e_machine != 'EM_RISCV':
            raise ValueError('Use the ESP32-C3 RISC-V compiler, not the host compiler')
        for unit in elf.get_dwarf_info().iter_CUs():
            for die in unit.iter_DIEs():
                if die.tag != 'DW_TAG_typedef' or name(die) not in TYPES:
                    continue
                struct = die.get_DIE_from_attribute('DW_AT_type')
                fields = [dict(name=name(member),
                    offset=member.attributes['DW_AT_data_member_location'].value,
                    size=size(member.get_DIE_from_attribute('DW_AT_type')))
                    for member in struct.iter_children() if member.tag == 'DW_TAG_member']
                result[name(die)] = dict(bytes=size(struct), fields=fields)
    if set(result) != set(TYPES):
        raise ValueError('Missing reference structures in compiler output')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', type=Path, required=True, help='riscv32-esp-elf-g++ executable')
    parser.add_argument('--output', type=Path, required=True, help='Use an ignored .build directory')
    args = parser.parse_args()
    output = args.output.resolve()
    headers = output/'upstream'
    headers.mkdir(parents=True, exist_ok=True)
    index = json.loads(urlopen(SOURCE+'?format=JSON', timeout=30).read()[4:])
    allowed = {entry['name'] for entry in index['entries'] if entry['name'].endswith('.h')}
    pending, done, hashes = {'s_tdec_int_file.h'}, set(), {}
    while pending:
        filename = pending.pop()
        if filename in done:
            continue
        if filename not in allowed or Path(filename).name != filename:
            raise ValueError('Unexpected upstream include: '+filename)
        data = base64.b64decode(urlopen(SOURCE+filename+'?format=TEXT', timeout=30).read())
        (headers/filename).write_bytes(data)
        hashes[filename] = hashlib.sha256(data).hexdigest()
        done.add(filename)
        for dependency in re.findall(rb'#\s*include\s*[<"]([^>"]+)', data):
            dependency = dependency.decode()
            if dependency != 'stdint.h' and dependency not in done:
                pending.add(dependency)
    probe, elf = headers/'layout.cpp', output/'layout.elf'
    probe.write_text(PROBE)
    compiler = str(args.compiler.resolve())
    command = [compiler, '-g', '-nostdlib', '-Wl,-e,0', '-o', str(elf), str(probe)]
    subprocess.run(command, check=True)
    result = dict(source=SOURCE, revision=REVISION,
        scope='32-bit upstream reference; compare offsets with the actual Espressif ELF separately',
        compiler=subprocess.check_output([compiler, '--version'], text=True).splitlines()[0],
        flags=command[1:4], headers_sha256=hashes, structures=layouts(elf))
    (output/'layout.json').write_text(json.dumps(result, indent=2)+'\n')
    for name, struct in result['structures'].items():
        print(f'{name}: {struct["bytes"]} bytes')


if __name__ == '__main__':
    main()
