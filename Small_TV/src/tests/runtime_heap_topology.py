"""Observe and replay allocator metadata without reading block payloads."""
from pathlib import Path

from runtime_memory import MemorySnapshot, native_layout, size_of
from runtime_heap_rom import RomHeapCounters
from runtime_tlsf_instructions import TlsfInstructionWalker


def topology_layout(app):
    """Resolve the native heap vtable ABI from DWARF, not SDK-version guesses."""
    from elftools.elf.elffile import ELFFile
    with Path(app).open('rb') as stream:
        elf = ELFFile(stream)
        wanted = {'heap_tlsf_table_ptr', 'heap_tlsf_patch_table_ptr', 'tlsf_check_pool_impl'}
        symbols = {s.name: {'address': s['st_value'], 'size': s['st_size']}
                   for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name in wanted}
        fields, structure_size = None, None
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                name = die.attributes.get('DW_AT_name')
                if (not name or name.value != b'heap_tlsf_stub_table_t' or
                        die.tag != 'DW_TAG_structure_type' or 'DW_AT_byte_size' not in die.attributes):
                    continue
                structure_size = size_of(die)
                fields = {}
                for member in die.iter_children():
                    if member.tag != 'DW_TAG_member':
                        continue
                    name = member.attributes['DW_AT_name'].value.decode('ascii')
                    offset = member.attributes['DW_AT_data_member_location'].value
                    if type(offset) is not int or size_of(member.get_DIE_from_attribute('DW_AT_type')) != 4:
                        raise ValueError('Unexpected TLSF dispatch member ABI')
                    fields[name] = offset
                break
            if fields is not None:
                break
    required = set(TlsfInstructionWalker.REQUIRED)
    if (set(symbols) != wanted or fields is None or not required <= fields.keys() or
            not 0 < structure_size <= 256 or symbols['heap_tlsf_patch_table_ptr']['size'] != structure_size or
            any(offset < 0 or offset % 4 or offset + 4 > structure_size for offset in fields.values()) or
            len(set(fields.values())) != len(fields)):
        raise ValueError('Missing or inconsistent native TLSF dispatch ABI')
    return {'symbols': symbols, 'fields': fields, 'size': structure_size}


class HeapTopology:
    """Bind live metadata and its replay to the same ELF, ROM and scalar counters."""
    def __init__(self, rom, app, layout=None):
        self.layout = layout or native_layout(app)
        self.dispatch_layout = topology_layout(app)
        self.walker = TlsfInstructionWalker(rom, app)
        self.counters = RomHeapCounters(rom)
        if self.layout['elf_sha256'] != self.walker.image.app_sha256:
            raise ValueError('Topology and counter ELF identities differ')
        default = self.walker.image.functions['rom_default_heap_tlsf_table']
        if default['size'] != self.dispatch_layout['size']:
            raise ValueError('ROM table and linked table sizes differ')
        expected = bytearray(self.walker.image.cpu.mem_read(default['address'], default['size']))
        for field, target in (
                ('tlsf_walk_pool', self.walker.image.functions['linked_tlsf_walk_pool']['address']),
                ('tlsf_check_pool', self.dispatch_layout['symbols']['tlsf_check_pool_impl']['address'])):
            offset = self.dispatch_layout['fields'][field]
            expected[offset:offset + 4] = target.to_bytes(4, 'little')
        # C2's size/alignment slots are reserved zero entries. Its direct ROM
        # size getter is executed independently; never call a reserved slot.
        self.expected_dispatch = bytes(expected)

    def check_dispatch(self, pointer, table):
        """Require the live patch and unchanged ROM geometry helpers before walking."""
        layout = self.dispatch_layout
        if pointer != layout['symbols']['heap_tlsf_patch_table_ptr']['address'] or len(table) != layout['size']:
            raise ValueError('Unsupported TLSF dispatch table')
        for name, offset in layout['fields'].items():
            target = int.from_bytes(self.expected_dispatch[offset:offset + 4], 'little')
            actual = int.from_bytes(table[offset:offset + 4], 'little')
            if actual != target:
                raise ValueError(f'Unqualified TLSF dispatch target: {name} ({actual:#x}, expected {target:#x})')

    def sample(self, reader, aggregate):
        """Read only typed heap/vtable headers while the controller holds its stop."""
        location = self.dispatch_layout['symbols']['heap_tlsf_table_ptr']['address']
        pointer = int.from_bytes(reader.memory(location, 4), 'little')
        table = reader.memory(pointer, self.dispatch_layout['size'])
        self.check_dispatch(pointer, table)
        descriptors = reader.heap_descriptors(aggregate['caps'], crosscheck=False)
        if [row['summary'] for row in descriptors] != aggregate['heaps']:
            raise ValueError('Heap metadata changed while observing the stopped guest')
        rows = []
        for descriptor in descriptors:
            control = reader.number('multi_heap_info', descriptor['header'], 'heap_data')
            summary = descriptor['summary']
            inventory = self.walker.inspect(reader.memory, control, summary['pool_size'],
                                            summary['free_bytes'], (descriptor['start'], descriptor['end']))
            rows.append({'heap_address': descriptor['address'], 'header_hex': descriptor['header'].hex(),
                         'summary': summary, 'inventory': inventory})
        return {'elf_sha256': self.layout['elf_sha256'], 'rom_sha256': self.walker.image.rom_sha256,
                'dispatch_pointer': pointer, 'dispatch_hex': table.hex(), 'heaps': rows}

    def validate(self, row):
        """Replay every saved header read and balance all allocated capacity/header bytes."""
        data, aggregate = row['heap_topology'], row['heap']
        if (data['elf_sha256'] != self.layout['elf_sha256'] or
                data['rom_sha256'] != self.walker.image.rom_sha256 or
                not 0 < len(data['heaps']) <= 32 or
                [part['summary'] for part in data['heaps']] != aggregate['heaps'] or
                sum(part['summary']['free_bytes'] for part in data['heaps']) != aggregate['free_bytes'] or
                sum(part['summary']['minimum_free_bytes'] for part in data['heaps']) != aggregate['minimum_free_bytes']):
            raise ValueError('Topology identity or heap summaries differ')
        self.check_dispatch(data['dispatch_pointer'], bytes.fromhex(data['dispatch_hex']))
        decoder = MemorySnapshot(lambda address, size: b'', self.layout)
        expected_size = self.layout['structures']['multi_heap_info']['size']
        seen = set()
        for part in data['heaps']:
            address = part['heap_address']
            if type(address) is not int or address in seen or address % 4:
                raise ValueError('Invalid topology heap owner')
            seen.add(address)
            header = bytes.fromhex(part['header_hex'])
            if len(header) != expected_size:
                raise ValueError('Wrong saved heap header size')
            summary, inventory = part['summary'], part['inventory']
            for name in ('free_bytes', 'minimum_free_bytes', 'pool_size'):
                if decoder.number('multi_heap_info', header, name) != summary[name]:
                    raise ValueError('Saved header differs from scalar counters')
            self.counters.validate(header, summary['free_bytes'], summary['minimum_free_bytes'])
            record = inventory['record']
            if (record['linked'] is not True or inventory['walker'] != 'linked_tlsf_walk_pool' or
                    decoder.number('multi_heap_info', header, 'heap_data') != record['control'] or
                    record['pool_size'] != summary['pool_size'] or record['free_counter'] != summary['free_bytes'] or
                    not record['extent'][0] <= address < address + expected_size <= record['control']):
                raise ValueError('Saved TLSF geometry differs from heap owner')
            if self.walker.replay(record) != inventory:
                raise ValueError('Saved topology differs from instruction replay')
