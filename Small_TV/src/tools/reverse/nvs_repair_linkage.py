"""Qualify the actual table-repair helpers without modifying earlier NVS evidence pins."""
from audit_factory_xrefs import Image, sha, startup_gp
from reverse.factory_nvs import TABLE, native_address
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import model, match

ALTER = '_ZN3nvs4Page15alterEntryStateEjNS0_10EntryStateE'
SET = '_ZN19CompressedEnumTableIN3nvs4Page10EntryStateELj2ELj126EE3setEjS2_'
GET = '_ZNK19CompressedEnumTableIN3nvs4Page10EntryStateELj2ELj126EE3getEjPS2_'
PURGE = '_ZN3nvs4Page10purgeEntryEj'
RANGE = '_ZN3nvs4Page15purgeEntryRangeEjj'


def qualify(factory, obj, native, app, current_obj, nvs, replacements=None):
    """Use qualified caller bindings to identify full helper bodies and all native destinations."""
    if sha(factory) != nvs['factory_elf_sha256'] or sha(native) != nvs['native_elf_sha256'] or \
            sha(obj) != nvs['factory_object_sha256'] or sha(current_obj) != nvs['native_object_sha256']:
        raise ValueError('Repair input differs from complete NVS qualification')
    image = Image(factory); linked = LinkedRuntime(native, app); result = {}
    for variant, data, reader, gp in (('factory', obj, image.read, startup_gp(image)),
                                    ('native', current_obj, linked.read, linked.symbol('__global_pointer$')['st_value'])):
        root = next(r for r in nvs['variants'][variant]['functions'] if r['name'] == TABLE)
        rows = {TABLE: root}; pending = [root]
        wanted = {ALTER, SET} if variant == 'factory' else {ALTER, SET, PURGE, RANGE, GET}
        while pending:
            caller = pending.pop(0)
            for edge in caller['symbol_bindings']:
                name = edge['name']
                if edge['kind'] != 'call' or name not in wanted or name in rows: continue
                spec = model(data, name); start = edge['address']
                size = len(spec['code'])+96 if variant == 'factory' else linked.symbol(name)['st_size']
                code = reader(start, size, True)
                if replacements and (variant, name) in replacements: code = replacements[variant, name]
                row = match(spec, code, start, gp)
                if variant == 'native':
                    if row['linked_bytes'] != size or start != linked.symbol(name)['st_value']:
                        raise ValueError('Incomplete or incorrectly bound native repair helper')
                    for callee in row['symbol_bindings']:
                        if callee['kind'] == 'call' and native_address(linked, callee['name']) != callee['address']:
                            raise ValueError('Native repair callee differs')
                row['code_sha256'] = sha(code[:row['linked_bytes']]); rows[name] = row; pending.append(row)
        if set(rows) != wanted | {TABLE}: raise ValueError('Missing repair helper closure')
        for caller in rows.values():
            for edge in caller['symbol_bindings']:
                if edge['kind'] == 'call' and edge['name'] in rows and int(rows[edge['name']]['start'], 0) != edge['address']:
                    raise ValueError('Repair call binding disagrees with qualified body')
        result[variant] = dict(functions=list(rows.values()), allocator_veneer=None)
    return dict(passed=True, variants=result, whole_entry_table_algorithm_proved=False,
                physical_hardware_tested=False)
