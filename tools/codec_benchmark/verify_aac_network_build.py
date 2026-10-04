"""Verify the compiled physical PC19/late-SBR candidate before a board test.

Checks configuration, actual ELF types, linked calls and pinned patch provenance.
This is a build gate, not a claim of hardware or full-format qualification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from elftools.elf.elffile import ELFFile
from compact_sbr_tables import PIN

FEATURES = ('AAC_PLUS', 'AAC_COMPACT_SBR', 'AAC_HIGH_HISTORY',
            'AAC_HIGH_HISTORY_PC19', 'AAC_SMOOTHING_HISTORY',
            'AAC_LOW_WORKSPACE', 'AAC_ASYMMETRIC_OWNER', 'AAC_LATE_SBR')
SIZES = {'native_aac_decoder': 204, 'aac_high_owner_t': 32744,
         'aac_high_runtime_t': 160}
CALLS = {
    'compact5_PVMP4AudioDecodeFrame': ('aac_late_sbr_select', '__wrap_get_sbr_bitstream', '__wrap_getfill'),
    '__wrap_get_sbr_bitstream': ('aac_fill_sbr', 'aac_late_sbr_after_fill'),
    'aac_late_sbr_select': ('aac_late_sbr_retain',),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(build, objdump):
    config = (build/'sdkconfig').read_text()
    for key in FEATURES:
        if not re.search(r'^CONFIG_YORADIO_'+key+r'=y$', config, re.M):
            raise ValueError('Missing candidate feature: '+key)
    if re.search(r'^CONFIG_YORADIO_(?:QEMU\w*|DEEP_SLEEP_CLOCK)=y$', config, re.M):
        raise ValueError('Physical candidate contains emulator or sleep configuration')
    if 'CONFIG_SPI_FLASH_AUTO_SUSPEND=y' in config:
        raise ValueError('Keep Auto Suspend off for this qualification')
    app = build/'yoradio_esp32c3_oled_native.bin'
    elf_path = app.with_suffix('.elf')
    if app.read_bytes()[176:208].hex() != sha(elf_path):
        raise ValueError('Application and ELF do not match')
    layout = build/'esp-idf/main/compact5'
    audit = json.loads((layout/'audit.json').read_text())
    branch = json.loads((layout/'late-sbr-audit.json').read_text())
    if (audit['codec_sha256'] != PIN or branch['changed_native_bytes'] != 4 or
            branch['structure_offsets_changed'] or
            branch['input_sha256'] != audit['functions']['PVMP4AudioDecodeFrame']['output_sha256'] or
            branch['output_sha256'] != sha(layout/'pvmp4audiodecoderframe.c.obj')):
        raise ValueError('Native patch provenance mismatch')
    found = {name: set() for name in SIZES}
    with elf_path.open('rb') as file:
        elf = ELFFile(file)
        table = elf.get_section_by_name('.symtab')
        names = {s.name for s in table.iter_symbols() if s['st_shndx'] != 'SHN_UNDEF'}
        if any(n.startswith(('qemu_aac', 'native_aac_decoder_test_', 'aac_pointer_audit_')) for n in names):
            raise ValueError('Test hooks linked in physical image')
        for cu in elf.get_dwarf_info().iter_CUs():
            source = cu.get_top_DIE().attributes.get('DW_AT_name')
            if not source or not source.value.endswith((b'native_aac_decoder.c', b'aac_compact_owner.c')):
                continue
            for die in cu.iter_DIEs():
                name = die.attributes.get('DW_AT_name')
                if not name or name.value.decode(errors='replace') not in found:
                    continue
                typ = die
                while 'DW_AT_byte_size' not in typ.attributes and 'DW_AT_type' in typ.attributes:
                    typ = typ.get_DIE_from_attribute('DW_AT_type')
                size = typ.attributes.get('DW_AT_byte_size')
                if size:
                    found[name.value.decode()].add(size.value)
    if found != {name: {size} for name, size in SIZES.items()}:
        raise ValueError('Missing or inconsistent compiled layout: '+repr(found))
    linked = {}
    for caller, callees in CALLS.items():
        code = subprocess.run([str(objdump), '-d', '--disassemble='+caller, str(elf_path)],
                              check=True, capture_output=True, text=True).stdout
        for callee in callees:
            if not re.search(r'\b(?:j|jal|jalr)\s+[^\n]*<'+re.escape(callee)+r'>', code):
                raise ValueError('Missing linked call: '+caller+' -> '+callee)
        linked[caller] = list(callees)
    commands = json.loads((build/'compile_commands.json').read_text())
    owner = [r['command'] for r in commands if r['file'].endswith('aac_compact_owner.c')]
    if len(owner) != 1 or any(flag not in owner[0] for flag in (
            '-fno-strict-aliasing', '-DAAC_HIGH_HISTORY_PC19=1', '-DAAC_HIGH_HISTORY_PC19_SIDECAR=1')):
        raise ValueError('Owner aliasing or PC19 compile flags missing')
    return dict(app_sha256=sha(app), elf_sha256=sha(elf_path),
                sdkconfig_sha256=sha(build/'sdkconfig'), app_bytes=app.stat().st_size,
                types=SIZES, linked_calls=linked, features=list(FEATURES),
                codec_sha256=PIN, layout_sha256=sha(layout/'layout.o'),
                branch_patch=branch, hardware_tested=False, production_qualified=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--objdump', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--artifact', type=Path, help='Unreleased firmware/development destination')
    args = parser.parse_args()
    result = verify(args.build, args.objdump)
    encoded = json.dumps(result, indent=2)+'\n'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(encoded, encoding='utf-8')
    if args.artifact:
        root = Path(__file__).resolve().parents[2]/'firmware/development'
        if not args.artifact.resolve().is_relative_to(root.resolve()):
            raise ValueError('Artifact destination must be under firmware/development')
        args.artifact.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.build/'yoradio_esp32c3_oled_native.bin', args.artifact/'app.bin')
        shutil.copyfile(args.build/'sdkconfig', args.artifact/'sdkconfig')
        (args.artifact/'manifest.json').write_text(encoded, encoding='utf-8')
    print(encoded)


if __name__ == '__main__':
    main()
