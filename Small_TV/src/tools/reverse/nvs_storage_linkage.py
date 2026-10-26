"""Qualify all direct NVS algorithms reachable from complete Storage init/read bodies."""
from audit_factory_xrefs import Image, sha, startup_gp
from reverse.elf_archive import members
from reverse.factory_nvs import native_address
from reverse.nvs_record_linkage import FACTORY_PARTS, definitions
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import model, match

PARTS = dict(FACTORY_PARTS,
    **{'nvs_pagemanager.cpp': '5bcb562530f449ea4d63acd649693b474177728e612abafe10b033150b48342e',
       'nvs_storage.cpp': 'aed3fbcf5c3ef11ceaecc16a11249cc6b6d1dae7c4daeb8f3f2289df70a9827e'})
ROOTS = {'_ZN3nvs7Storage4initEmm': 0x42041d38,
         '_ZN3nvs7Storage8readItemEhNS_8ItemTypeEPKcPvj': 0x42041740}
EXTERNAL = {'malloc', 'free', 'memcpy', 'memset', 'strncmp', 'strncpy',
            '_ZnajRKSt9nothrow_t', '_ZdaPv', 'esp_rom_crc32_le'}


def archive_objects(raw):
    """Extract five named source objects without interpreting archive paths as files."""
    result = {}
    for name, data in members(raw):
        key = name.removesuffix('.obj')
        if key not in PARTS: continue
        if key in result: raise ValueError('Duplicate storage object')
        result[key] = data
    if set(result) != set(PARTS): raise ValueError('Missing storage object')
    return result


def qualify(factory, parts, native, app, current_parts, replacements=None):
    """Require full bodies, local control flow and every named call; allow only explicit C/runtime boundaries."""
    if set(parts) != set(PARTS) or any(sha(v) != PARTS[k] for k, v in parts.items()):
        raise ValueError('Requalify factory Storage sources')
    if set(current_parts) != set(PARTS): raise ValueError('Missing current Storage source objects')
    image = Image(factory); linked = LinkedRuntime(native, app); results = {}
    for variant, objects, reader, gp in (('factory', parts, image.read, startup_gp(image)),
                                       ('native', current_parts, linked.read, linked.symbol('__global_pointer$')['st_value'])):
        available = definitions(objects); seen = {}; external = {}
        queue = [(name, address if variant == 'factory' else linked.symbol(name)['st_value']) for name, address in ROOTS.items()]
        while queue:
            name, address = queue.pop(0)
            if name in seen:
                if int(seen[name]['start'], 0) != address: raise ValueError('Conflicting Storage function binding')
                continue
            if name not in available:
                if name not in EXTERNAL: raise ValueError('Unqualified Storage algorithm: '+name)
                if name in external and external[name] != address: raise ValueError('Conflicting Storage primitive')
                external[name] = address; continue
            accepted = []
            for member in available[name]:
                spec = model(objects[member], name)
                length = len(spec['code'])+96 if variant == 'factory' else linked.symbol(name)['st_size']
                code = reader(address, length, True)
                if replacements and (variant, name) in replacements: code = replacements[variant, name]
                try: row = match(spec, code, address, gp)
                except ValueError: continue
                if variant == 'native' and (row['linked_bytes'] != length or linked.symbol(name)['st_value'] != address):
                    raise ValueError('Incomplete native Storage body')
                row.update(member=member, object_sha256=sha(objects[member]), code_sha256=sha(code[:row['linked_bytes']]))
                accepted.append(row)
            if not accepted: raise ValueError('No full Storage source match: '+name)
            if len({(r['linked_bytes'], r['code_sha256']) for r in accepted}) != 1:
                raise ValueError('Ambiguous Storage extent')
            row = accepted[0]; row['matching_members'] = sorted(r['member'] for r in accepted)
            seen[name] = row
            for edge in row['symbol_bindings']:
                if edge['kind'] != 'call': continue
                if variant == 'native' and native_address(linked, edge['name']) != edge['address']:
                    raise ValueError('Wrong native Storage callee')
                queue.append((edge['name'], edge['address']))
        if external.get('esp_rom_crc32_le') != 0x400007fc: raise ValueError('Storage CRC entry changed')
        results[variant] = dict(functions=list(seen.values()), externals=external, allocator_veneer=None)
    return dict(passed=True, factory_elf_sha256=sha(factory), native_elf_sha256=sha(native), app_sha256=sha(app),
                factory_objects={k: sha(v) for k, v in parts.items()}, native_objects={k: sha(v) for k, v in current_parts.items()},
                variants=results, complete_direct_init_read_closure=True, factory_compiler_version_identified=False,
                whole_image_completeness_proved=False, physical_hardware_tested=False)
