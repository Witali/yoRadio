"""Compare current DWARF layouts with immutable exports that mislabeled the PS flag."""
from copy import deepcopy


def assert_archive_layout(test, current, archived):
    current = semantic_layout(current)
    archived = semantic_layout(archived, legacy_ps_name=True)
    # Added after these 2026-10-01 exports; its size/boundaries have independent
    # assertions in aac_sbr_abi.h. Every original type still compares in full.
    added = {'aac_sbr_compact_relocated_owner_abi_t'}
    for section in ('types', 'roots'):
        test.assertEqual(current[section].keys() - archived[section].keys(), added)
        for name in added:
            del current[section][name]
    test.assertEqual(current, archived)


def semantic_layout(meta, *, legacy_ps_name=False):
    meta = deepcopy(meta)
    nodes = meta['nodes']
    if legacy_ps_name:
        # Only this verified correction is permitted. All other types, offsets,
        # sizes, pointer depths and array dimensions must still compare exactly.
        core = meta['types']['aac_core_abi_t']['fields']
        configuration = next(f for f in core if f['name'] == 'configuration')
        ps = next(f for f in core if f['name'] == 'channels')
        assert configuration == dict(name='configuration', offset=9, bytes=183)
        assert ps == dict(name='channels', offset=0xc0, bytes=4)
        configuration['bytes'] = 0x8c-9
        index = core.index(configuration)+1
        core[index:index] = [dict(name='encoded_channels', offset=0x8c, bytes=4),
                            dict(name='extension_configuration', offset=0x90, bytes=0xbc-0x90)]
        ps['name'] = 'ps_present'
        core.insert(core.index(ps), dict(name='sbr_present', offset=0xbc, bytes=4))

        members = nodes[nodes[meta['roots']['aac_core_abi_t']]['type']]['members']
        configuration = next(f for f in members if f['name'] == 'configuration')
        ps = next(f for f in members if f['name'] == 'channels')
        # Clone the array type: a DWARF node can be shared with another field.
        array = deepcopy(nodes[configuration['type']])
        assert array['bytes'] == 183 and array['dimensions'] == [183]
        array.update(bytes=0x8c-9, dimensions=[0x8c-9])
        configuration['type'] = 'corrected_core_configuration'
        nodes[configuration['type']] = array
        extension_array = deepcopy(array)
        extension_array.update(bytes=0xbc-0x90, dimensions=[0xbc-0x90])
        nodes['corrected_extension_configuration'] = extension_array
        index = members.index(configuration)+1
        members[index:index] = [dict(name='encoded_channels', offset=0x8c, type=ps['type']),
                               dict(name='extension_configuration', offset=0x90,
                                    type='corrected_extension_configuration')]
        ps['name'] = 'ps_present'
        members.insert(members.index(ps), dict(name='sbr_present', offset=0xbc, type=ps['type']))

    def semantic_node(key):
        node = deepcopy(nodes[key])
        if 'type' in node:
            node['type'] = semantic_node(node['type'])
        if 'members' in node:
            for member in node['members']:
                member['type'] = semantic_node(member['type'])
        return node

    # Numeric DWARF IDs move when a field is renamed or added. Compare their
    # complete resolved types instead of those incidental debug-file positions.
    regions = []
    for region in meta['analysis_regions']:
        regions.append({**region, 'original': semantic_node(region['original']),
                        'replacement': semantic_node(region['replacement'])})
    return dict(types=meta['types'], parameters=meta['parameters'],
                roots={name: semantic_node(key) for name, key in meta['roots'].items()},
                analysis_regions=regions, data_symbols=meta.get('data_symbols', {}))
