"""Match the complete NVS record-repair call closure to Item/HashList/Page source objects."""
import io

from elftools.elf.elffile import ELFFile
from audit_factory_xrefs import Image, sha, startup_gp
from reverse.elf_archive import members
from reverse.factory_nvs import TABLE, native_address
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import model, match

FACTORY_PARTS = {'nvs_page.cpp': '9ed443fea642655cdfe641e74bce4a26fd69bdefe151c40dee96919888731d0f',
                 'nvs_types.cpp': '5607b50be0ed6098094372d077525be146c5c5f2afc6e46becaa987f59d0448e',
                 'nvs_item_hash_list.cpp': 'b1c56c25ca76298f6a0ab39ec1652d083fcfc6d56ff3d8591c2589a7384df02c'}
EXTERNAL = {'malloc', 'free', 'strncmp', 'strncpy', 'memset', 'esp_rom_crc32_le'}


def archive_objects(archive):
    """Read exactly the three source members without extracting archive-controlled paths."""
    result = {}
    for name, raw in members(archive):
        key = name.removesuffix('.obj')
        if key not in FACTORY_PARTS: continue
        if key in result: raise ValueError('Duplicate NVS record object')
        result[key] = raw
    if set(result) != set(FACTORY_PARTS): raise ValueError('Missing NVS record source object')
    return result


def definitions(parts):
    """Keep duplicate inline definitions as candidates, not as proof of their original TU."""
    result = {}
    for member, raw in parts.items():
        elf = ELFFile(io.BytesIO(raw))
        if elf.elfclass != 32 or not elf.little_endian or elf['e_machine'] != 'EM_RISCV' or elf['e_type'] != 'ET_REL':
            raise ValueError('Expected a complete RV32 source object')
        for symbol in elf.get_section_by_name('.symtab').iter_symbols():
            if symbol['st_info']['type'] == 'STT_FUNC' and symbol['st_size'] and isinstance(symbol['st_shndx'], int):
                result.setdefault(symbol.name, []).append(member)
    return result


def qualify(factory, parts, native, app, current_parts, replacements=None):
    """Traverse every named direct call from the full loader; reject missing algorithms."""
    if set(parts) != set(FACTORY_PARTS) or any(sha(raw) != FACTORY_PARTS[name] for name, raw in parts.items()):
        raise ValueError('Requalify factory record source objects')
    image = Image(factory); linked = LinkedRuntime(native, app); variants = {}
    for variant, objects, reader, gp in (('factory', parts, image.read, startup_gp(image)),
                                       ('native', current_parts, linked.read, linked.symbol('__global_pointer$')['st_value'])):
        defined = definitions(objects); seen = {}; external = {}; queue = [(TABLE, 0x42040a8c if variant == 'factory' else linked.symbol(TABLE)['st_value'])]
        while queue:
            name, start = queue.pop(0)
            if name in seen:
                if int(seen[name]['start'], 0) != start: raise ValueError('Conflicting record call binding')
                continue
            if name not in defined:
                if name not in EXTERNAL: raise ValueError('Unqualified record algorithm: '+name)
                if name in external and external[name] != start: raise ValueError('Conflicting external primitive')
                external[name] = start; continue
            accepted = []
            for member in defined[name]:
                spec = model(objects[member], name)
                size = len(spec['code'])+96 if variant == 'factory' else linked.symbol(name)['st_size']
                data = reader(start, size, True)
                if replacements and (variant, name) in replacements: data = replacements[variant, name]
                try: row = match(spec, data, start, gp)
                except ValueError: continue
                if variant == 'native' and (row['linked_bytes'] != size or linked.symbol(name)['st_value'] != start):
                    raise ValueError('Incomplete/incorrectly bound native record body')
                row.update(member=member, object_sha256=sha(objects[member]), code_sha256=sha(data[:row['linked_bytes']]))
                accepted.append(row)
            if not accepted: raise ValueError('No complete source match for '+name)
            if len({(r['linked_bytes'], r['code_sha256']) for r in accepted}) != 1:
                raise ValueError('Ambiguous record body extent')
            row = accepted[0]; row['matching_members'] = sorted(r['member'] for r in accepted)
            seen[name] = row
            for edge in row['symbol_bindings']:
                if edge['kind'] != 'call': continue
                if variant == 'native' and edge['address'] != native_address(linked, edge['name']):
                    raise ValueError('Incorrect native record callee')
                queue.append((edge['name'], edge['address']))
        if external.get('esp_rom_crc32_le') != 0x400007fc: raise ValueError('Record CRC primitive changed')
        variants[variant] = dict(functions=list(seen.values()), externals=external, allocator_veneer=None)
    return dict(passed=True, factory_elf_sha256=sha(factory), native_elf_sha256=sha(native), app_sha256=sha(app),
                factory_objects={k: sha(v) for k, v in parts.items()}, native_objects={k: sha(v) for k, v in current_parts.items()},
                variants=variants, complete_direct_record_call_closure=True, whole_image_completeness_proved=False,
                physical_hardware_tested=False)
