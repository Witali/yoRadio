"""Qualify the five compact-call gaps using complete SDK/runtime bodies and named bindings."""
import io
from pathlib import Path

from elftools.elf.elffile import ELFFile

from audit_factory_xrefs import Image, sha, startup_gp
from reverse.elf_archive import members
from reverse.rv32_link_match import branch_target, link_register, match, model

NATIVE_SHA = '9e4ec88d6e85ae58fa3e164362f1b10491f9edef0feaa4af8c52c9fa88446e24'
LIBRARY_SHA = '27a8ced3a7c5d209bc60d9882a6c6b497eb4fec59317b0183d6c94e9d1350b83'
OBJECTS = {
    'vectors.S.obj': '81b8c24f89286153a23413aa1d22dba1531e6f1ecdea16dc5554946c042a8b26',
    'cxx_exception_stubs.cpp.obj': 'f3cdfcddf38a31f05ed3d83f0c2b2cb5183af83a443f2baf72daf34c7b533911',
    'eh_catch.o': 'bbd91038b966ab6591e21cebfe3dfb926f318e2cf07dcd76d34f0e40b3a8710d',
    'eh_globals.o': '36d0f99c04603c8ffbdbe67c940f00d6406b1cd000e2a81445e268ed0efb7379',
    'new_op.o': '88d98e175b46ad5b40b045bd03fedc236efa2367295845979d185d0a320c8dcc',
    'new_opv.o': 'b0fbaf6051fe531127eff6d97a99abe10e6b4e4c83b5c7aa6e0a508af22bf7f1',
    'new_opvnt.o': 'c9c2f4ac4f06a182e1e2eb421f8678453e94292c784f3dccdb43067609c50578',
}
# Addresses are independently checked against relocation names and shared callees.
CASES = (
    ('_panic_handler', 'vectors.S.obj', 0x40380102),
    ('_Znwj', 'new_op.o', 0x420a3f4c),
    ('_Znaj', 'new_opv.o', 0x420a3f4a),
    ('_ZnajRKSt9nothrow_t', 'new_opvnt.o', 0x420a3a0a),
    ('_ZL15eh_globals_dtorPv', 'eh_globals.o', 0x420a3e0a),
    ('__cxa_end_catch', 'eh_catch.o', 0x420a3da2),
    ('__wrap__Unwind_DeleteException', 'cxx_exception_stubs.cpp.obj', 0x420a3fd4),
    ('__wrap__Unwind_Resume', 'cxx_exception_stubs.cpp.obj', 0x420a3fc8),
    ('__wrap___cxa_allocate_exception', 'cxx_exception_stubs.cpp.obj', 0x420a3fe8),
    ('__wrap___cxa_throw', 'cxx_exception_stubs.cpp.obj', 0x420a3ff4),
)
NATIVE_ABSENT = ('__wrap__Unwind_Resume',)


class Linked:
    """Read only initialized linked sections and unambiguous nonzero symbols."""
    def __init__(self, data):
        """Pin the exact native image before using any SDK symbol or address."""
        if sha(data) != NATIVE_SHA:
            raise ValueError('Requalify the native runtime ELF')
        self.elf = ELFFile(io.BytesIO(data))
        self.symbols = list(self.elf.get_section_by_name('.symtab').iter_symbols())

    def symbol(self, name):
        """Permit linker --wrap names only when the original symbol is absent."""
        rows = [s for s in self.symbols if s.name == name and s['st_value']]
        if not rows and not name.startswith('__wrap_'):
            rows = [s for s in self.symbols if s.name == '__wrap_' + name and s['st_value']]
        if len(rows) != 1:
            raise ValueError('Missing/ambiguous runtime symbol: ' + name)
        return rows[0]

    def read(self, address, length, execute=False):
        """Refuse zero-fill, unmapped, cross-section and non-executable code reads."""
        rows = [s for s in self.elf.iter_sections() if s['sh_type'] != 'SHT_NOBITS'
                and s['sh_flags'] & 2 and (not execute or s['sh_flags'] & 4)
                and s['sh_addr'] <= address < address + length <= s['sh_addr'] + s['sh_size']]
        if len(rows) != 1:
            raise ValueError('Runtime read is outside one initialized section')
        section = rows[0]; offset = address - section['sh_addr']
        return section.data()[offset:offset + length]


def load_objects(build, library):
    """Load seven pinned objects without extracting archive-controlled paths."""
    paths = {
        'vectors.S.obj': Path(build) / 'esp-idf/riscv/CMakeFiles/__idf_riscv.dir/vectors.S.obj',
        'cxx_exception_stubs.cpp.obj': Path(build) / 'esp-idf/cxx/CMakeFiles/__idf_cxx.dir/cxx_exception_stubs.cpp.obj',
    }
    result = {name: path.read_bytes() for name, path in paths.items()}
    raw = Path(library).read_bytes()
    if sha(raw) != LIBRARY_SHA:
        raise ValueError('Requalify the selected compiler runtime archive')
    for name, data in members(raw):
        if name not in OBJECTS or name in paths:
            continue
        if name in result:
            raise ValueError('Duplicate runtime archive member')
        result[name] = data
    validate_objects(result)
    return result


def validate_objects(parts):
    """Require exact object identities, including those used by offline evidence replay."""
    if set(parts) != set(OBJECTS) or any(sha(parts[name]) != digest for name, digest in OBJECTS.items()):
        raise ValueError('Runtime object set or identity changed')


def binding(row, name):
    """Do not infer a function name from a coincidentally matching tiny body alone."""
    rows = [b['address'] for b in row['symbol_bindings'] if b['name'] == name]
    if len(rows) != 1:
        raise ValueError('Missing/ambiguous qualified binding: ' + name)
    return rows[0]


def qualify(factory, native, parts, replacements=None):
    """Match both images to complete objects, then check the actual five call chains."""
    validate_objects(parts); original = Image(factory); linked = Linked(native)
    result = {}
    for variant, reader, gp in (('factory', original.read, startup_gp(original)),
                               ('native', linked.read, linked.symbol('__global_pointer$')['st_value'])):
        rows = []
        for name, member, address in CASES:
            if variant == 'native' and name in NATIVE_ABSENT:
                if any(s.name == name and s['st_value'] for s in linked.symbols):
                    raise ValueError('Requalify previously absent native runtime symbol')
                continue
            spec = model(parts[member], name)
            if variant == 'native':
                symbol = linked.symbol(name)
                address = symbol['st_value']; length = symbol['st_size']
            else:
                length = len(spec['code']) + 64
            data = reader(address, length, True)
            if replacements and (variant, name) in replacements:
                data = replacements[variant, name]
            row = match(spec, data, address, gp)
            if variant == 'native':
                if row['linked_bytes'] != symbol['st_size']:
                    raise ValueError('Incomplete native runtime body')
                for callee in row['symbol_bindings']:
                    if callee['binding'] != 'STB_LOCAL' and linked.symbol(callee['name'])['st_value'] != callee['address']:
                        raise ValueError('Native runtime callee binding differs')
            row.update(member=member,object_sha256=sha(parts[member]),code_sha256=sha(data[:row['linked_bytes']]))
            rows.append(row)
        by_name = {r['name']: r for r in rows}
        panic, allocator, destructor, end_catch, delete = [by_name[name] for name in
            ('_panic_handler','_Znwj','_ZL15eh_globals_dtorPv','__cxa_end_catch','__wrap__Unwind_DeleteException')]
        delete_at = int(delete['start'], 0)
        if binding(destructor, '_Unwind_DeleteException') != delete_at or binding(end_catch, '_Unwind_DeleteException') != delete_at:
            raise ValueError('Exception cleanup does not select the qualified abort stub')
        for name, member, _ in CASES:
            if member == 'cxx_exception_stubs.cpp.obj' and name in by_name:
                if binding(by_name[name], 'abort') != binding(delete, 'abort'):
                    raise ValueError('Identical-looking abort stubs have different callees')
        for callee in ('__cxa_allocate_exception','__cxa_throw'):
            if binding(allocator,callee) != int(by_name['__wrap_'+callee]['start'],0):
                raise ValueError('Allocator does not select a qualified exception stub')
        if variant == 'factory' and binding(destructor, 'free') != 0x4038e4da:
            raise ValueError('Factory runtime cleanup free binding differs')
        nothrow = by_name['_ZnajRKSt9nothrow_t']; array = by_name['_Znaj']
        if binding(nothrow, '__cxa_end_catch') != int(end_catch['start'], 0):
            raise ValueError('Nothrow landing pad selects a different end-catch body')
        if binding(nothrow, '_Znaj') != int(array['start'],0) or binding(array,'_Znwj') != int(allocator['start'],0):
            raise ValueError('Scalar and array allocation bindings differ')
        veneer = dict(address=int(array['start'],0),target=int(allocator['start'],0),
                      bytes_hex=reader(int(array['start'],0),array['linked_bytes'],True).hex())
        if variant == 'factory':
            resume = by_name['__wrap__Unwind_Resume']
            if binding(delete, 'abort') != binding(resume, 'abort'):
                raise ValueError('Identical-looking abort stubs have different callees')
            if (binding(panic, 'xt_unhandled_exception'), binding(panic, 'panicHandler'),
                binding(nothrow, '__cxa_begin_catch'), binding(delete, 'abort')) != (
                    0x40380584, 0x40380566, 0x420a3d32, 0x4038e23e):
                raise ValueError('Factory runtime target anchors changed')
        result[variant] = dict(functions=rows,allocator_veneer=veneer,
                               abort_boundary=binding(delete, 'abort'),
                               begin_catch_boundary=binding(nothrow, '__cxa_begin_catch'),
                               absent_linked_symbols=list(NATIVE_ABSENT) if variant == 'native' else [])
    gaps = []
    factory_rows = {r['name']:r for r in result['factory']['functions']}
    for pc, owner, callee in ((0x40380180,'_panic_handler','xt_unhandled_exception'),
                              (0x4038018e,'_panic_handler','panicHandler'),
                              (0x420a3a12,'_ZnajRKSt9nothrow_t','__cxa_begin_catch'),
                              (0x420a3a14,'_ZnajRKSt9nothrow_t','__cxa_end_catch'),
                              (0x420a3e32,'_ZL15eh_globals_dtorPv','_Unwind_DeleteException')):
        row = factory_rows[owner]; items = [t for t in row['transformations'] if int(t['pc'],0) == pc]
        if len(items) != 1:
            raise ValueError('Missing compact runtime call')
        item = items[0]; code = bytes.fromhex(item['linked_bytes'])
        spec = model(parts[row['member']],owner)
        names = [r['name'] for r in spec['relocs'].get(item['object_offset'],[]) if r['type'] in (18,19)]
        target = binding(row,callee)
        if names != [callee] or len(code) != 2 or link_register(code) != 1 or branch_target(code,pc) != target:
            raise ValueError('Runtime call site/relocation identity differs')
        gaps.append(dict(pc=pc,owner=owner,callee=callee,target=target,bytes_hex=code.hex()))
    caller = original.read(0x42040efc,4,True)
    if (link_register(caller) != 1 or branch_target(caller,0x42040efc) != 0x420a3a0a or
        original.read(0x42040ef8,4,True) != bytes.fromhex('13050020') or
        original.read(0x42040f00,4,True) != bytes.fromhex('2a8a3dcd') or
        branch_target(original.read(0x42040f02,2,True),0x42040f02) != 0x42040f80):
        raise ValueError('Factory 512-byte allocation caller/null branch changed')
    return dict(schema='factory-runtime-call-gaps-v1',passed=True,gaps=gaps,
                selected_nothrow_caller=dict(pc=0x42040efc,target=0x420a3a0a,requested_bytes=512,
                                            return_null_branch_pc=0x42040f02,return_null_target=0x42040f80),
                factory_elf_sha256=sha(factory),native_elf_sha256=sha(native),objects=OBJECTS,
                variants=result,whole_image_completeness_proved=False,
                natural_exception_reachability_proved=False,physical_hardware_tested=False,
                factory_compiler_version_identified=False)
