"""Prepare checked RV32 types for a separate, readable Ghidra AAC export.

The original binary/raw export stays unchanged. This is analysis metadata, not
a build of the vendor decoder. Requires pyelftools and the C3 cross compiler.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / 'idf/esp32c3-oled-native/main/aac_sbr_abi.h'
REGIONS = Path(__file__).with_name('aac_analysis_regions.h')
ELF_SHA256 = '2f7535c3d8e7e7a1cad05fa865a13c0f59ad64d48411b0276dc9fceefa5c254f'

# Zero-based ABI argument positions. Only verified pointer roles are overridden;
# unlisted parameters/return values keep Ghidra's inferred types. Sources are
# the raw function bodies/callers in the pinned complete audit and the runtime
# wrappers tested against that same binary (not an upstream struct assumption).
PARAMETERS = {}
def roles(names, *entries):
    for name in names.split():
        PARAMETERS[name] = {str(index): dict(type=kind, name=label)
                            for index, kind, label in entries}

roles('PVMP4AudioDecodeFrame PVMP4AudioDecoderInitLibrary',
      (1, 'aac_core_abi_t *', 'core'))
roles('PVMP4AudioDecoderResetBuffer', (0, 'aac_core_abi_t *', 'core'))
roles('sbr_open', (1, 'aac_sbr_control_abi_t *', 'control'), (2, 'aac_sbr_owner_abi_t *', 'owner'))
roles('init_sbr_dec', (2, 'aac_sbr_control_abi_t *', 'control'), (3, 'aac_sbr_frame_abi_t *', 'frame'))
roles('sbr_read_data', (0, 'aac_sbr_owner_abi_t *', 'owner'), (1, 'aac_sbr_control_abi_t *', 'control'))
# Espressif's sbr_applied has TEN arguments (reference PacketVideo has eight).
# Native caller/callee put control in argument 8 and core in argument 9.
roles('sbr_applied', (0, 'aac_sbr_owner_abi_t *', 'owner'), (7, 'aac_sbr_control_abi_t *', 'control'),
      (8, 'aac_core_abi_t *', 'core'))
roles('sbr_dec', (2, 'aac_sbr_frame_abi_t *', 'frame'), (4, 'aac_sbr_control_abi_t *', 'control'),
      (6, 'aac_ps_abi_t *', 'ps'), (7, 'aac_core_abi_t *', 'core'))
roles('sbr_reset_dec', (0, 'aac_sbr_frame_abi_t *', 'frame'), (1, 'aac_sbr_control_abi_t *', 'control'))
roles('sbr_get_header_data', (0, 'aac_sbr_header_abi_t *', 'header'))
roles('sbr_get_cpe', (0, 'aac_sbr_frame_abi_t *', 'left'), (1, 'aac_sbr_frame_abi_t *', 'right'))
roles('sbr_get_sce', (0, 'aac_sbr_frame_abi_t *', 'frame'), (2, 'aac_ps_abi_t *', 'ps'))
roles('calc_sbr_envelope', (0, 'aac_sbr_frame_abi_t *', 'frame'))
roles('sbr_decode_envelope decode_noise_floorlevels sbr_get_dir_control_data sbr_get_envelope '
      'sbr_get_noise_floor_data sbr_get_additional_data sbr_requantize_envelope_data',
      (0, 'aac_sbr_frame_abi_t *', 'frame'))
roles('sbr_envelope_unmapping', (0, 'aac_sbr_frame_abi_t *', 'left'), (1, 'aac_sbr_frame_abi_t *', 'right'))
roles('extractFrameInfo', (1, 'aac_sbr_frame_abi_t *', 'frame'))
roles('sbr_extract_extended_data', (1, 'aac_ps_abi_t *', 'ps'))
roles('ps_allocate_decoder', (0, 'aac_sbr_owner_abi_t *', 'owner'))
roles('ps_applied ps_bstr_decoding ps_read_data ps_decorrelate ps_pwr_transient_detection '
      'ps_init_stereo_mixing ps_stereo_processing', (0, 'aac_ps_abi_t *', 'ps'))
roles('ps_hybrid_analysis', (4, 'aac_hybrid_abi_t *', 'hybrid'))
roles('ps_hybrid_filter_bank_allocation', (0, 'aac_hybrid_abi_t **', 'hybrid'))


def dwarf_layouts(path):
    def name(die):
        return die.attributes['DW_AT_name'].value.decode() if 'DW_AT_name' in die.attributes else ''
    def size(die):
        if 'DW_AT_byte_size' in die.attributes: return die.attributes['DW_AT_byte_size'].value
        target = die.get_DIE_from_attribute('DW_AT_type')
        if die.tag != 'DW_TAG_array_type': return size(target)
        n = 1
        for child in die.iter_children():
            if child.tag == 'DW_TAG_subrange_type': n *= child.attributes['DW_AT_upper_bound'].value + 1
        return n * size(target)
    result, nodes, roots = {}, {}, {}
    def node(die):
        key = str(die.offset)
        if key in nodes: return key
        value = dict(kind=die.tag.removeprefix('DW_TAG_'), name=name(die))
        nodes[key] = value
        if 'DW_AT_type' in die.attributes: value['type'] = node(die.get_DIE_from_attribute('DW_AT_type'))
        if die.tag == 'DW_TAG_pointer_type': value['bytes'] = 4
        else: value['bytes'] = size(die)
        if die.tag == 'DW_TAG_base_type': value['encoding'] = die.attributes['DW_AT_encoding'].value
        if die.tag == 'DW_TAG_array_type':
            value['dimensions'] = [c.attributes['DW_AT_upper_bound'].value + 1 for c in die.iter_children()
                                   if c.tag == 'DW_TAG_subrange_type']
        if die.tag in ('DW_TAG_structure_type', 'DW_TAG_union_type'):
            value['members'] = [dict(name=name(m), type=node(m.get_DIE_from_attribute('DW_AT_type')),
                offset=m.attributes['DW_AT_data_member_location'].value if 'DW_AT_data_member_location' in m.attributes else 0)
                for m in die.iter_children() if m.tag == 'DW_TAG_member']
        return key
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        if elf.elfclass != 32 or elf.header.e_machine != 'EM_RISCV' or not elf.little_endian:
            raise ValueError('RV32 little-endian object required')
        for unit in elf.get_dwarf_info().iter_CUs():
            for die in unit.iter_DIEs():
                if die.tag != 'DW_TAG_typedef' or not name(die).startswith('aac_'): continue
                roots[name(die)] = node(die)
                target = die.get_DIE_from_attribute('DW_AT_type')
                fields = []
                for member in target.iter_children():
                    if member.tag != 'DW_TAG_member': continue
                    fields.append(dict(name=name(member), offset=member.attributes.get('DW_AT_data_member_location').value
                        if 'DW_AT_data_member_location' in member.attributes else 0,
                        bytes=size(member.get_DIE_from_attribute('DW_AT_type'))))
                result[name(die)] = dict(bytes=size(target), fields=fields)
    if not result: raise ValueError('No ABI types in debug information')
    for label, key in roots.items():
        target = nodes[nodes[key]['type']]
        if not target['name']: target['name'] = label + '_fields'
    return dict(types=result, nodes=nodes, roots=roots)


def apply_regions(meta):
    """Specialize analysis types without changing any byte boundary."""
    nodes, roots = meta['nodes'], meta['roots']
    def fields(type_name): return nodes[nodes[roots[type_name]]['type']]['members']
    def member(type_name, label): return next(m for m in fields(type_name) if m['name'] == label)
    changes = []
    def replace(type_name, label, target):
        m = member(type_name, label)
        if nodes[m['type']]['bytes'] != nodes[target]['bytes']: raise ValueError('Region size changed')
        changes.append(dict(type=type_name, member=label, offset=m['offset'], original=m['type'], replacement=target))
        m['type'] = target
    for owner, label, region in (
        ('aac_ps_abi_t','parameters','aac_analysis_ps_parameters_t'),
        ('aac_sbr_frame_abi_t','frame_control','aac_analysis_frame_control_t'),
        ('aac_sbr_frame_abi_t','domain_and_inverse_filter','aac_analysis_inverse_filter_t'),
        ('aac_sbr_frame_abi_t','harmonics_and_envelopes','aac_analysis_harmonics_t'),
        ('aac_sbr_frame_abi_t','envelope_and_noise','aac_analysis_envelope_t'),
        ('aac_sbr_control_abi_t','remaining','aac_analysis_frequency_control_t')):
        replace(owner, label, roots[region])
    replace('aac_sbr_owner_abi_t','channel',member('aac_analysis_bindings_t','channel')['type'])
    replace('aac_core_abi_t','sbr',member('aac_analysis_bindings_t','owner')['type'])
    meta['analysis_regions'] = changes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=True)
    probe = output/'types.c'; obj = output/'types.elf'
    probe.write_text('#include "aac_analysis_regions.h"\n', encoding='utf-8')
    common = [str(args.compiler.resolve()), '-std=c11', '-march=rv32imc', '-mabi=ilp32',
              '-I', str(HEADER.parent), '-I', str(REGIONS.parent)]
    subprocess.run(common + ['-g', '-fno-eliminate-unused-debug-types', '-nostdlib', '-Wl,-e,0',
                             str(probe), '-o', str(obj)], check=True)
    # Import compiler debug types directly: C parsers can silently misread
    # multiple pointer declarators or pointers to arrays. Preserve both.
    meta = dict(elf_sha256=ELF_SHA256, header_sha256=hashlib.sha256(HEADER.read_bytes()).hexdigest(),
                regions_sha256=hashlib.sha256(REGIONS.read_bytes()).hexdigest(),
                **dwarf_layouts(obj), parameters=PARAMETERS)
    apply_regions(meta)
    (output/'types.json').write_text(json.dumps(meta, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(f'Prepared {len(meta["types"])} checked types and {len(PARAMETERS)} function parameter maps')


if __name__ == '__main__': main()
