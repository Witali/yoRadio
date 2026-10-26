"""Reject missing Storage algorithms, altered call targets and actual private ABI mutations."""
import io
from elftools.elf.elffile import ELFFile

from audit_factory_xrefs import Image
from reverse.nvs_storage_linkage import qualify, ROOTS
from reverse.nvs_storage_layout import layout
from reverse.nothrow_linkage import LinkedRuntime


def controls(factory, parts, native, app, current_parts, report, carrier):
    """Exercise the real full-body/ABI guard, not only a forged success field."""
    rejected = []
    def reject(name, operation):
        """Require every effective mutation to fail the production checker."""
        try: operation()
        except (ValueError, AssertionError): rejected.append(name)
        else: raise AssertionError('Altered Storage input accepted: '+name)
    reject('missing-factory-manager', lambda: qualify(factory,
        {k: v for k, v in parts.items() if k != 'nvs_pagemanager.cpp'}, native, app, current_parts))
    reject('missing-current-storage', lambda: qualify(factory, parts, native, app,
        {k: v for k, v in current_parts.items() if k != 'nvs_storage.cpp'}))
    images = {'factory': Image(factory).read, 'native': LinkedRuntime(native, app).read}
    name = next(iter(ROOTS))
    for variant in ('factory', 'native'):
        row = next(r for r in report['variants'][variant]['functions'] if r['name'] == name)
        start = int(row['start'], 0)
        for is_call in (False, True):
            code = bytearray(images[variant](start, row['linked_bytes'], True))
            if is_call:
                edge = next(r for r in row['transformations'] if 'call' in r['kind'])
                offset = int(edge['pc'], 0)-start; size = len(bytes.fromhex(edge['linked_bytes']))
                if size == 8: offset += 4; size = 4
                mask = 1 << 21 if size == 4 else 8
            else:
                offset = 0; size = 4 if code[0] & 3 == 3 else 2; mask = 16
            code[offset:offset+size] = (int.from_bytes(code[offset:offset+size], 'little') ^ mask).to_bytes(size, 'little')
            reject(variant+('-call-target' if is_call else '-frame'),
                   lambda: qualify(factory, parts, native, app, current_parts, {(variant, name): bytes(code)}))
    for variant, raw in (('factory', carrier), ('native', native)):
        elf = ELFFile(io.BytesIO(raw)); dwarf = elf.get_dwarf_info(); attributes = []
        for cu in dwarf.iter_CUs():
            for die in cu.iter_DIEs():
                a = die.attributes
                if a.get('DW_AT_name') and a['DW_AT_name'].value == b'Storage' and 'DW_AT_byte_size' in a:
                    for child in die.iter_children():
                        c = child.attributes
                        if child.tag == 'DW_TAG_member' and c['DW_AT_name'].value == b'mPageManager':
                            attributes.append(c['DW_AT_data_member_location'])
        assert attributes
        changed = bytearray(raw); section = elf.get_section_by_name('.debug_info')
        # Mutate every repeated complete DIE consistently, then reject the wrong ABI.
        for attr in attributes:
            assert attr.form == 'DW_FORM_data1' and attr.value == 16
            offset = section['sh_offset']+attr.offset; assert raw[offset] == 16
            changed[offset] = 17
        reject(variant+'-storage-member-offset', lambda: layout(bytes(changed)))
    return dict(passed=True, rejected=rejected)
