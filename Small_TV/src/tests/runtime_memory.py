"""Decode ESP32-C2 heap/task counters through bounded read-only memory access.

The ABI comes from the tested ELF's DWARF, not offsets from an earlier build.
Only aggregate counters and stack fill lengths leave the decoder; stack bytes
and allocator payloads are never returned or stored in reports.
"""
import hashlib
from pathlib import Path

RAM = ((0x3FCA0000, 0x3FCE0000), (0x4037C000, 0x403C0000))
STRUCTURES = {
    'heap_t_': ('caps', 'start', 'end', 'heap', 'next'),
    'multi_heap_info': ('free_bytes', 'minimum_free_bytes', 'pool_size'),
    'tskTaskControlBlock': ('pxStack', 'pxEndOfStack', 'pcTaskName'),
    'xLIST': ('uxNumberOfItems', 'xListEnd'),
    'xLIST_ITEM': ('pxNext', 'pxPrevious', 'pvOwner', 'pxContainer'),
}
LISTS = ('pxReadyTasksLists', 'xDelayedTaskList1', 'xDelayedTaskList2',
         'xSuspendedTaskList', 'xTasksWaitingTermination')


def size_of(die):
    """Resolve scalar/array/qualified DWARF sizes without evaluating expressions."""
    for _ in range(16):
        if 'DW_AT_byte_size' in die.attributes:
            return die.attributes['DW_AT_byte_size'].value
        if die.tag == 'DW_TAG_array_type':
            element = size_of(die.get_DIE_from_attribute('DW_AT_type'))
            dimensions = [row for row in die.iter_children() if row.tag == 'DW_TAG_subrange_type']
            if len(dimensions) != 1:
                raise ValueError('Expected a one-dimensional observed array')
            bound = dimensions[0].attributes
            return element * (bound['DW_AT_count'].value if 'DW_AT_count' in bound
                              else bound['DW_AT_upper_bound'].value + 1)
        die = die.get_DIE_from_attribute('DW_AT_type')
    raise ValueError('Unresolved observed DWARF size')


def native_layout(path):
    """Extract required linked symbols and complete structure fields from one ELF."""
    from elftools.elf.elffile import ELFFile
    path = Path(path)
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        if elf.elfclass != 32 or not elf.little_endian or elf['e_machine'] != 'EM_RISCV':
            raise ValueError('Expected a little-endian RV32 ELF')
        wanted = set(LISTS) | {'registered_heaps', 'uxCurrentNumberOfTasks', 'pxCurrentTCBs',
                              'vTaskDelay', 'heap_caps_get_free_size', 'connected'}
        symbols = {row.name: {'address': row['st_value'], 'size': row['st_size']}
                   for row in elf.get_section_by_name('.symtab').iter_symbols()
                   if row.name in wanted and row['st_value']}
        if set(symbols) != wanted:
            raise ValueError('Missing runtime symbols: ' + str(wanted - set(symbols)))
        structures, stack_unit = {}, None
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                name = die.attributes.get('DW_AT_name')
                name = name.value.decode('ascii', errors='replace') if name else ''
                if name == 'StackType_t' and die.tag == 'DW_TAG_typedef':
                    stack_unit = size_of(die)
                if (name not in STRUCTURES or name in structures or
                        die.tag != 'DW_TAG_structure_type' or 'DW_AT_byte_size' not in die.attributes):
                    continue
                fields = {}
                for field in die.iter_children():
                    if field.tag == 'DW_TAG_member':
                        key = field.attributes['DW_AT_name'].value.decode('ascii')
                        offset = field.attributes['DW_AT_data_member_location'].value
                        if not isinstance(offset, int):
                            raise ValueError('Nonconstant observed field offset')
                        fields[key] = {'offset': offset,
                                       'size': size_of(field.get_DIE_from_attribute('DW_AT_type'))}
                if not set(STRUCTURES[name]).issubset(fields):
                    raise ValueError('Missing observed fields in ' + name)
                structures[name] = {'size': size_of(die), 'fields': fields}
            if len(structures) == len(STRUCTURES) and stack_unit is not None:
                break
    if len(structures) != len(STRUCTURES) or stack_unit != 1:
        raise ValueError('Expected complete IDF C2 layouts and byte-sized StackType_t')
    return {'elf_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'symbols': symbols, 'structures': structures, 'stack_unit_bytes': stack_unit,
            'stack_growth': -1, 'stack_fill_byte': 0xA5}


class MemorySnapshot:
    """Read a stopped guest, rejecting invalid pointers, counts and list cycles."""
    def __init__(self, read, layout, validate_counters=None):
        self.read, self.layout = read, layout
        self.validate_counters = validate_counters

    def memory(self, address, size):
        """Restrict every read to a small mapped C2 SRAM interval."""
        if not 0 < size <= 4096 or not any(lo <= address and address + size <= hi for lo, hi in RAM):
            raise ValueError('Observed memory outside bounded C2 RAM')
        data = self.read(address, size)
        if len(data) != size:
            raise ValueError('Short observed memory read')
        return data

    def symbol(self, name):
        """Read a scalar pointer/count at the linked symbol's actual address."""
        row = self.layout['symbols'][name]
        if row['size'] != 4:
            raise ValueError('Unexpected scalar symbol size: ' + name)
        return int.from_bytes(self.memory(row['address'], 4), 'little')

    def structure(self, name, address):
        """Read exactly one complete compiled structure, with no payload walk."""
        return self.memory(address, self.layout['structures'][name]['size'])

    def field(self, name, data, key):
        """Extract one compiled member while checking its extent."""
        row = self.layout['structures'][name]['fields'][key]
        start, size = row['offset'], row['size']
        if start < 0 or size <= 0 or start + size > len(data):
            raise ValueError('Observed field outside its structure')
        return data[start:start + size]

    def number(self, name, data, key):
        """Decode only the RV32 unsigned integer/pointer members used here."""
        raw = self.field(name, data, key)
        if len(raw) != 4:
            raise ValueError('Expected a 32-bit observed field')
        return int.from_bytes(raw, 'little')

    def heaps(self, caps=4):
        """Match IDF heap_caps_get_free/minimum_size, without calling guest code."""
        pointer, seen, rows = self.symbol('registered_heaps'), set(), []
        while pointer:
            if pointer in seen or len(seen) >= 32:
                raise ValueError('Cyclic or oversized registered heap list')
            seen.add(pointer)
            heap = self.structure('heap_t_', pointer)
            raw_caps = self.field('heap_t_', heap, 'caps')
            if len(raw_caps) % 4:
                raise ValueError('Invalid heap capability array')
            all_caps = 0
            for offset in range(0, len(raw_caps), 4):
                all_caps |= int.from_bytes(raw_caps[offset:offset + 4], 'little')
            pool = self.number('heap_t_', heap, 'heap')
            if pool and all_caps & caps == caps:
                info = self.structure('multi_heap_info', pool)
                free = self.number('multi_heap_info', info, 'free_bytes')
                minimum = self.number('multi_heap_info', info, 'minimum_free_bytes')
                size = self.number('multi_heap_info', info, 'pool_size')
                if self.validate_counters:
                    self.validate_counters(info, free, minimum)
                start = self.number('heap_t_', heap, 'start')
                end = self.number('heap_t_', heap, 'end')
                if not 0 <= minimum <= free <= size <= end - start or not start <= pool < end:
                    raise ValueError('Inconsistent heap counters or pool extent')
                rows.append({'free_bytes': free, 'minimum_free_bytes': minimum,
                             'pool_size': size, 'caps': all_caps})
            pointer = self.number('heap_t_', heap, 'next')
        if not rows:
            raise ValueError('No initialized heap matching requested capabilities')
        return {'caps': caps, 'free_bytes': sum(row['free_bytes'] for row in rows),
                'minimum_free_bytes': sum(row['minimum_free_bytes'] for row in rows), 'heaps': rows}

    def task_list(self, address):
        """Walk one FreeRTOS state list, validating sentinel and both link directions."""
        data = self.structure('xLIST', address)
        count = self.number('xLIST', data, 'uxNumberOfItems')
        sentinel_offset = self.layout['structures']['xLIST']['fields']['xListEnd']['offset']
        sentinel = address + sentinel_offset
        next_offset = self.layout['structures']['xLIST_ITEM']['fields']['pxNext']['offset']
        previous_offset = self.layout['structures']['xLIST_ITEM']['fields']['pxPrevious']['offset']
        # Both sentinel links are already inside the complete xLIST read. Avoid
        # two extra debugger round trips for every empty priority/state list.
        offsets = (sentinel_offset + next_offset, sentinel_offset + previous_offset)
        if any(offset < 0 or offset + 4 > len(data) for offset in offsets):
            raise ValueError('Sentinel links outside the observed list structure')
        pointer = int.from_bytes(data[offsets[0]:offsets[0] + 4], 'little')
        tail = int.from_bytes(data[offsets[1]:offsets[1] + 4], 'little')
        if count > 64:
            raise ValueError('Oversized FreeRTOS state list')
        seen, owners, previous = set(), [], sentinel
        for _ in range(count):
            if pointer == sentinel or pointer in seen:
                raise ValueError('Cyclic or short FreeRTOS state list')
            seen.add(pointer)
            item = self.structure('xLIST_ITEM', pointer)
            if (self.number('xLIST_ITEM', item, 'pxPrevious') != previous or
                    self.number('xLIST_ITEM', item, 'pxContainer') != address):
                raise ValueError('Inconsistent FreeRTOS list links')
            owners.append(self.number('xLIST_ITEM', item, 'pvOwner'))
            previous, pointer = pointer, self.number('xLIST_ITEM', item, 'pxNext')
        if pointer != sentinel or tail != previous:
            raise ValueError('FreeRTOS list count/tail does not match its chain')
        return owners

    def stack_free(self, start, end):
        """Count untouched 0xA5 bytes exactly as the downward-growing SDK stack scan."""
        if not 0 < end - start + 1 <= 65536:
            raise ValueError('Invalid recorded task stack extent')
        free = 0
        while start + free <= end:
            # The RSP hex reply doubles the raw bytes. Stay below QEMU's packet
            # limit while avoiding the many 256-byte reads used by the preflight.
            data = self.memory(start + free, min(1024, end - start - free + 1))
            used = next((index for index, byte in enumerate(data) if byte != 0xA5), len(data))
            free += used
            if used < len(data):
                return free
        raise ValueError('No saved context or used bytes in recorded task stack')

    def tasks(self):
        """Account for every linked task and return only names and stack fill counts."""
        pointers = []
        size = self.layout['structures']['xLIST']['size']
        for name in LISTS:
            symbol = self.layout['symbols'][name]
            if symbol['size'] % size:
                raise ValueError('Unexpected FreeRTOS list array size')
            for offset in range(0, symbol['size'], size):
                pointers.extend(self.task_list(symbol['address'] + offset))
        if (len(set(pointers)) != len(pointers) or len(pointers) != self.symbol('uxCurrentNumberOfTasks')
                or self.symbol('pxCurrentTCBs') not in pointers):
            raise ValueError('Task count, current task or state-list membership disagrees')
        rows = []
        for pointer in pointers:
            task = self.structure('tskTaskControlBlock', pointer)
            start = self.number('tskTaskControlBlock', task, 'pxStack')
            end = self.number('tskTaskControlBlock', task, 'pxEndOfStack')
            rows.append({'name': self.field('tskTaskControlBlock', task, 'pcTaskName').split(b'\0')[0].decode('utf-8', errors='replace'),
                         'recorded_stack_span_bytes': end - start + 1,
                         'stack_high_water_free_bytes': self.stack_free(start, end)})
        return sorted(rows, key=lambda row: row['name'])
