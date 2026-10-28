"""Qualify complete factory NVS bodies and their current production counterparts."""
import re
from audit_factory_xrefs import Image, sha, startup_gp
from reverse.elf_archive import members
from reverse.nothrow_linkage import LinkedRuntime
from reverse.runtime_call_gaps import binding
from reverse.rv32_link_match import match, model

PAGE = '_ZN3nvs4Page4loadEPNS_9PartitionEm'
CRC = '_ZN3nvs4Page6Header14calculateCrc32Ev'
TABLE = '_ZN3nvs4Page15mLoadEntryTableEv'
HEADER = '_ZN3nvs4Page6HeaderC1Ev'
FIND = '_ZSt9__find_ifIPmN9__gnu_cxx5__ops10_Iter_predIZN3nvs4Page4loadEPNS4_9PartitionEmEUlmE_EEET_SA_SA_T0_St26random_access_iterator_tag'
FACTORY_OBJECT = '9ed443fea642655cdfe641e74bce4a26fd69bdefe151c40dee96919888731d0f'
NATIVE_OBJECT = '66a953b7997555a48a062026dd0200b285a30c7aeebc57c90e3fa5ba608a8022'
NATIVE_ELF = 'eb20fb1309d1a5f28229d2ca846924cd18b311da229d34a1319a324d621ee2e6'
FACTORY_ENTRIES = {PAGE: 0x42040e56, CRC: 0x4203fd12, FIND: 0x4203fbea, TABLE: 0x42040a8c}


def source_correspondence(old_cpp, current_cpp, current_header):
    """Keep caller identity separate from a real SDK6.1 repair/erasure policy difference."""
    if sha(old_cpp) != '632fb3f9c8667e3b17f8bc823d5c056dc5aee4d7e2d08a4778478bc0732c91a4' or \
            sha(current_cpp) != 'b6c1dd565c41479e9ad7d7b5caf296c4621b1b93e6b6eb048e0cd562c5a559c7':
        raise ValueError('Requalify NVS source revisions')
    texts = [value.decode().replace('\r\n', '\n') for value in (old_cpp, current_cpp)]
    result = {}
    for key, signature in (('load', 'esp_err_t Page::load('), ('crc', 'uint32_t Page::Header::calculateCrc32('),
                           ('entry_table', 'esp_err_t Page::mLoadEntryTable(')):
        bodies = []
        for text in texts:
            start = text.index(signature)
            # These pinned member definitions close at column zero; nested blocks are indented.
            last = re.search(r'(?m)^}', text[start:])
            if last is None: raise ValueError('Missing NVS source body')
            bodies.append(text[start:start+last.end()].encode())
        result[key] = dict(identical=bodies[0] == bodies[1], factory_sha256=sha(bodies[0]), native_sha256=sha(bodies[1]))
    if not result['load']['identical'] or not result['crc']['identical'] or result['entry_table']['identical']:
        raise ValueError('NVS source correspondence changed')
    if not re.search(rb'\bDEFAULT_PURGE_AFTER_ERASE\s*=\s*true\s*;', current_header):
        raise ValueError('NVS repair policy changed')
    return dict(passed=True, cpp_sha256={'factory': sha(old_cpp), 'native': sha(current_cpp)},
                native_header_sha256=sha(current_header), functions=result, native_default_purge_after_erase=True,
                inherited_repair_policy_equivalence_proved=False)


def native_address(linked, name):
    """Permit a named ROM absolute symbol without weakening the linked-image reader."""
    if name == '_ZnajRKSt9nothrow_t': name = '__wrap__ZnajRKSt9nothrow_t'
    rows = [s['st_value'] for s in linked.symbols if s.name == name and s['st_value']]
    if len(rows) != 1: raise ValueError('Missing/ambiguous NVS binding: '+name)
    return rows[0]


def qualify(factory, factory_object, native, app, native_object, replacements=None):
    """Match every instruction and local branch, checking shared callees and allocator ingress."""
    if sha(factory_object) != FACTORY_OBJECT or sha(native_object) != NATIVE_OBJECT or sha(native) != NATIVE_ELF:
        raise ValueError('Requalify NVS source objects or the current production ELF')
    image = Image(factory); linked = LinkedRuntime(native, app); variants = {}
    for variant, obj, reader, gp, names in (
            ('factory', factory_object, image.read, startup_gp(image), tuple(FACTORY_ENTRIES)),
            ('native', native_object, linked.read, linked.symbol('__global_pointer$')['st_value'], (PAGE, CRC, TABLE, HEADER))):
        rows = []
        for name in names:
            spec = model(obj, name)
            start = FACTORY_ENTRIES[name] if variant == 'factory' else linked.symbol(name)['st_value']
            size = len(spec['code']) + 96 if variant == 'factory' else linked.symbol(name)['st_size']
            data = reader(start, size, True)
            if replacements and (variant, name) in replacements: data = replacements[variant, name]
            row = match(spec, data, start, gp)
            if variant == 'native':
                if row['linked_bytes'] != size: raise ValueError('Incomplete current NVS body')
                for callee in row['symbol_bindings']:
                    if callee['kind'] == 'call' or callee['binding'] != 'STB_LOCAL':
                        if native_address(linked, callee['name']) != callee['address']:
                            raise ValueError('Wrong current NVS callee')
            row['code_sha256'] = sha(data[:row['linked_bytes']]); rows.append(row)
        by_name = {r['name']: r for r in rows}; page = by_name[PAGE]
        for name in (CRC, TABLE):
            if binding(page, name) != int(by_name[name]['start'], 0):
                raise ValueError('Wrong NVS helper selected by Page::load')
        if variant == 'factory':
            if (binding(page, FIND), binding(page, '_ZnajRKSt9nothrow_t'), binding(page, '_ZdaPv'),
                    binding(by_name[CRC], 'esp_rom_crc32_le')) != (0x4203fbea, 0x420a3a0a, 0x420a390e, 0x400007fc):
                raise ValueError('Factory NVS runtime anchors changed')
            if (page['linked_bytes'], page['end']) != (312, '0x42040f8e'):
                raise ValueError('Factory NVS body extent differs')
        else:
            if binding(page, HEADER) != int(by_name[HEADER]['start'], 0): raise ValueError('Wrong NVS Header constructor')
        variants[variant] = dict(functions=rows, allocation_boundary=binding(page, '_ZnajRKSt9nothrow_t'),
                                 delete_boundary=binding(page, '_ZdaPv'),
                                 crc_boundary=binding(by_name[CRC], 'esp_rom_crc32_le'),
                                 entry_table_boundary=binding(page, TABLE),
                                 memset_boundary=native_address(linked, 'memset') if variant == 'native' else None)
    return dict(schema='factory-nvs-qualification-v1', passed=True, factory_elf_sha256=sha(factory),
                factory_object_sha256=sha(factory_object), native_elf_sha256=sha(native), app_sha256=sha(app),
                native_object_sha256=sha(native_object), variants=variants,
                factory_compiler_version_identified=False, factory_config_identified=False,
                whole_image_completeness_proved=False, physical_hardware_tested=False)


def native_object(archive):
    """Extract one known NVS member as bytes without trusting archive-controlled paths."""
    rows = [raw for name, raw in members(archive) if name == 'nvs_page.cpp.obj']
    if len(rows) != 1: raise ValueError('Missing/duplicate current NVS object')
    return rows[0]
