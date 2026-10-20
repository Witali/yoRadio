"""Read bounded ESP-NETIF lists; derive native offsets from the matching ELF."""
import hashlib
from pathlib import Path

FACTORY_SHA = '5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4'
RAM = (0x3fca0000, 0x3fce0000)
DROM = (0x3c000000, 0x3c400000)
PUBLIC_KEYS = {b'WIFI_STA_DEF', b'WIFI_AP_DEF'}


def require(value, message):
    """Reject incomplete or corrupt evidence instead of guessing a guest layout."""
    if not value:
        raise ValueError(message)


def digest(path):
    """Identify the exact binary or source used by the read-only observer."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def factory_layout(path):
    """Bind fixed SDK addresses to the original dump and addressed assembly exports."""
    require(digest(path) == FACTORY_SHA, 'Unknown factory image for netif addresses')
    # lookup 0x42034e32 loads head 0x3fcc3c0c, node netif+0/next+4;
    # get_ifkey 0x42036f98 is lw a0,92(a0); ret. No guest calls are injected.
    return {'head': 0x3fcc3c0c, 'head_first': 0, 'node_size': 8,
            'node_netif': 0, 'node_next': 4, 'if_key': 92}


def native_layout(elf_path, app_path):
    """Read native list/structure/settings offsets from this application's DWARF."""
    from elftools.elf.elffile import ELFFile
    elf_sha = digest(elf_path)
    require(Path(app_path).read_bytes()[176:208] == bytes.fromhex(elf_sha),
            'Application does not embed this native ELF identity')
    names = {'slisthead', 'slist_netifs_s', 'esp_netif_obj', 'tv_settings_t'}
    types = {}
    with Path(elf_path).open('rb') as stream:
        elf = ELFFile(stream)
        require(elf.little_endian and elf.elfclass == 32, 'Expected a little-endian RV32 ELF')
        symbols = {name: [s for s in elf.get_section_by_name('.symtab').iter_symbols()
                          if s.name == name] for name in ('s_head', 'current_settings')}
        for name, matches in symbols.items():
            require(len(matches) == 1, 'Missing or ambiguous symbol: ' + name)
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                attr = die.attributes.get('DW_AT_name')
                if not attr or attr.value.decode() not in names:
                    continue
                name = attr.value.decode()
                if die.tag == 'DW_TAG_typedef':
                    die = die.get_DIE_from_attribute('DW_AT_type')
                if die.tag != 'DW_TAG_structure_type' or 'DW_AT_byte_size' not in die.attributes:
                    continue
                row = (die.attributes['DW_AT_byte_size'].value,
                       {child.attributes['DW_AT_name'].value.decode():
                        child.attributes['DW_AT_data_member_location'].value
                        for child in die.iter_children() if child.tag == 'DW_TAG_member'})
                require(name not in types or types[name] == row, 'Conflicting native type: ' + name)
                types[name] = row
        require(set(types) == names, 'Missing native netif/settings DWARF')
        head, node, netif, settings = (types[name] for name in
                                      ('slisthead', 'slist_netifs_s', 'esp_netif_obj', 'tv_settings_t'))
        require(symbols['s_head'][0]['st_size'] == head[0] == 4 and
                symbols['current_settings'][0]['st_size'] == settings[0], 'ELF symbol/type size differs')
        return {'head': symbols['s_head'][0]['st_value'], 'head_first': head[1]['slh_first'],
                'node_size': node[0], 'node_netif': node[1]['netif'], 'node_next': node[1]['next'],
                'if_key': netif[1]['if_key'], 'elf_sha256': elf_sha,
                'settings': {'address': symbols['current_settings'][0]['st_value'],
                             'fields': settings[1]}}


def read_netifs(read, layout):
    """Follow at most eight RAM nodes and accept only known NUL-terminated keys."""
    def pointer(address, size=4):
        require(address % 4 == 0 and RAM[0] <= address < address + size <= RAM[1],
                'Netif pointer outside aligned C2 RAM')
        return address

    def word(address):
        raw = read(pointer(address), 4)
        require(len(raw) == 4, 'Truncated netif pointer')
        return int.from_bytes(raw, 'little')

    node = word(layout['head'] + layout['head_first'])
    seen, rows = set(), []
    while node:
        pointer(node, layout['node_size'])
        require(node not in seen and len(seen) < 8, 'Cyclic or oversized netif list')
        seen.add(node)
        interface = pointer(word(node + layout['node_netif']), layout['if_key'] + 4)
        key_pointer = word(interface + layout['if_key'])
        require(any(start <= key_pointer < key_pointer + 16 <= end for start, end in (RAM, DROM)),
                'Netif key outside C2 RAM/DROM')
        raw = read(key_pointer, 16)
        require(len(raw) == 16 and b'\0' in raw, 'Missing netif key terminator')
        key = raw.split(b'\0', 1)[0]
        require(key in PUBLIC_KEYS, 'Unexpected netif key')
        rows.append({'key': key.decode('ascii'), 'object': hex(interface)})
        node = word(node + layout['node_next'])
    return rows


def require_role(rows, station):
    """Require exactly the selected TCP/IP interface, rejecting duplicate/idle roles."""
    require([row['key'] for row in rows] == ['WIFI_STA_DEF' if station else 'WIFI_AP_DEF'],
            'Unexpected interfaces for selected role: ' + str([row['key'] for row in rows]))


def driver_credentials(partition, parser):
    """Verify public SDK SSID blobs and their CRCs without exporting payloads."""
    parsed = parser.NVS_Partition('synthetic-driver-nvs', bytearray(partition))
    entries = [entry for page in parsed.pages for entry in page.entries if entry.state == 'Written']
    namespaces = {entry.data['value'] for entry in entries
                  if entry.metadata['namespace'] == 0 and entry.key == 'nvs.net80211'}
    require(len(namespaces) == 1, 'Missing driver namespace')
    found = []
    for entry in entries:
        if entry.metadata['namespace'] not in namespaces or entry.key not in ('sta.ssid', 'sta.apinfo'):
            continue
        if entry.metadata['type'] == 'blob_index':
            # NVS v2 stores a separate index alongside the payload chunks.
            # The index contains sizes/indices, not the SSID bytes themselves.
            crc = entry.metadata['crc']
            require(crc['original'] == crc['computed'], 'Driver SSID index CRC mismatch')
            continue
        require(entry.metadata['type'] in ('blob_data', 'blob') and entry.data is not None,
                'Unexpected driver SSID entry type')
        crc = entry.metadata['crc']
        require(crc['original'] == crc['computed'] and crc['data_original'] == crc['data_computed'],
                'Driver SSID entry CRC mismatch')
        payload = b''.join(bytes(child.raw) for child in entry.children)[:entry.data['size']]
        require(b'yoRadio-QEMU\0' in payload, 'Driver credentials are not the synthetic fixture')
        found.append({'namespace': 'nvs.net80211', 'key': entry.key,
                      'header_crc_matches': True, 'data_crc_matches': True,
                      'contains_expected_synthetic_ssid': True})
    require({row['key'] for row in found} == {'sta.ssid', 'sta.apinfo'}, 'Missing retained SSID blobs')
    return {'sha256': hashlib.sha256(partition).hexdigest(), 'entries': found}
