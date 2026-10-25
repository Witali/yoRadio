"""Match complete old/new station-leave bodies without claiming SDK lifecycle equivalence."""
import io

from elftools.elf.elffile import ELFFile

from audit_factory_xrefs import Image, sha, startup_gp
from reverse.elf_archive import members
from reverse.rv32_link_match import model, match
from reverse.timer_event11_match import NATIVE_SHA, unique
from reverse.timer_pm_lifecycle import read_allocated

LIBRARIES = {
    'factory': '8f989ecd7104520083727442247aed08ad93ef2bc304ae727022f8573f4bc558',
    'native': 'c2df6fcca4c1c19c9c6b8171f16461e52a636da90dd7f7be3b67bed4fbe71cca',
}


def qualify(factory, native, old_net, new_net):
    """Require every relocated and unrelocated instruction of the exact wl_cnx.o functions."""
    if sha(native) != NATIVE_SHA: raise ValueError('Unexpected native station-leave ELF')
    image = Image(factory)
    elf = ELFFile(io.BytesIO(native)); symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
    result = {}
    for variant, library in (('factory', old_net), ('native', new_net)):
        raw = library.read_bytes()
        if sha(raw) != LIBRARIES[variant]: raise ValueError('Unexpected station-leave SDK library')
        source = [data for name, data in members(raw) if name == 'wl_cnx.o']
        if len(source) != 1: raise ValueError('Missing/ambiguous wl_cnx.o')
        spec = model(source[0], 'cnx_sta_leave')
        if variant == 'factory':
            address = 0x4206c1ae; gp = startup_gp(image)
            code = image.read(address, len(spec['code'])+64, True)
            expected, pm_stop = 662, 0x4207661c
        else:
            symbol = unique(symbols, 'cnx_sta_leave'); address = symbol['st_value']
            gp = unique(symbols, '__global_pointer$')['st_value']
            code = read_allocated(elf, address, symbol['st_size'], True)
            expected, pm_stop = 628, unique(symbols, 'pm_stop')['st_value']
        row = match(spec, code, address, gp)
        if row['linked_bytes'] != expected: raise ValueError('Changed station-leave function extent')
        stops = [b['address'] for b in row['symbol_bindings'] if b['name'] == 'pm_stop']
        if stops != [pm_stop]: raise ValueError('Station leave uses a different PM stop')
        row['linked_code_sha256'] = sha(code[:row['linked_bytes']]); result[variant] = row
    return dict(schema='station-leave-bodies-v1', functions=result,
                factory_elf_sha256=sha(factory), native_elf_sha256=sha(native),
                full_runtime_lifecycle_proved=False, whole_image_completeness_proved=False)
