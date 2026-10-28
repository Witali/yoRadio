"""Check selected native SDK bodies against the same relocated factory SDK models."""
import io

from elftools.elf.elffile import ELFFile
from audit_factory_xrefs import sha
from match_factory_timers import CASES, load_models
from reverse.rv32_link_match import match

NATIVE_SHA = '76b5ce3700d299b607774467a57bc95e07d3cd39f6385bc3a1befd0504c2dad8'


def describe(data, directory, replacements=None):
    """Check complete native function bounds, fixed bits, edges and actual symbol targets."""
    assert sha(data) == NATIVE_SHA, 'Unexpected native ELF'
    elf = ELFFile(io.BytesIO(data))
    symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
    models, rows, locals_ = load_models(directory), [], {}

    def symbol(name, function=False):
        """Never choose an arbitrary alias or undefined symbol as a relocation target."""
        found = [row for row in symbols if row.name == name and row['st_value'] and
                 (not function or row['st_info']['type'] == 'STT_FUNC')]
        assert len(found) == 1, 'Missing/ambiguous native symbol: ' + name
        return found[0]

    gp = symbol('__global_pointer$')['st_value']
    for name, member, _, _ in CASES:
        native = symbol(name, True)
        section = elf.get_section(native['st_shndx'])
        assert section['sh_flags'] & 4 and native['st_size'] > 0, 'Non-executable native body'
        offset = native['st_value'] - section['sh_addr']
        assert 0 <= offset and offset + native['st_size'] <= section['sh_size']
        code = section.data()[offset:offset + native['st_size']]
        if replacements and name in replacements:
            code = replacements[name]
        row = match(models[name]['spec'], code, native['st_value'], gp)
        assert int(row['end'], 0) == native['st_value'] + native['st_size'], 'Incomplete native function match'
        for binding in row['symbol_bindings']:
            if binding['binding'] == 'STB_LOCAL':
                # Object-local anchors only share identity within that object.
                key = (member, binding['name'], binding['section'])
                assert key not in locals_ or locals_[key] == binding['address'], 'Native state anchor differs'
                locals_[key] = binding['address']
            else:
                assert symbol(binding['name'])['st_value'] == binding['address'], 'Native callee/global anchor differs'
        row.update(native_code_sha256=sha(code), member=member)
        rows.append(row)
    return {'native_elf_sha256': sha(data), 'gp': hex(gp), 'functions': rows,
            'selected_instruction_correspondence_verified': True,
            'semantic_equivalence_proved': False, 'whole_image_completeness_proved': False,
            'limitations': ['Complete selected bodies match the same SDK model after permitted relocation/relaxation.',
                'Calls bind to real native symbols, but their transitive implementations can differ across SDK versions.',
                'No timer registration, RF behavior, firmware timing or whole-image acceptance is inferred.']}
