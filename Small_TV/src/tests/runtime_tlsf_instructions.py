"""Explain allocator counters using exact ROM/linked walkers and metadata only."""
from collections import Counter

from runtime_instruction_image import InstructionImage
from runtime_memory import RAM


class TlsfInstructionWalker:
    """Replay real walker instructions with strictly bounded, read-only guest input."""
    REQUIRED = ('tlsf_size', 'tlsf_get_pool', 'tlsf_pool_overhead',
                'tlsf_alloc_overhead', 'tlsf_walk_pool')

    def __init__(self, rom, app=None):
        """Qualify the actual ROM and optional SDK patch, including save/restore code."""
        from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
        self.image = InstructionImage(rom)
        if app:
            self.image.add_walk_patch(app)
        functions = self.image.functions
        if any(name not in functions for name in self.REQUIRED):
            raise ValueError('Missing qualified TLSF instructions')
        names = set(self.REQUIRED) | {n for n in functions if n.startswith(('__riscv_save_', '__riscv_restore_'))}
        if app:
            names.add('linked_tlsf_walk_pool')
        self.code = [(functions[n]['address'], functions[n]['address'] + functions[n]['size']) for n in names]
        if any(not lo < hi or hi - lo > 4096 for lo, hi in self.code):
            raise ValueError('Unbounded TLSF instruction symbol')
        self.active = False
        self.image.cpu.hook_add(UC_HOOK_CODE, self._code)
        self.image.cpu.hook_add(UC_HOOK_MEM_READ, self._read)
        self.image.cpu.hook_add(UC_HOOK_MEM_WRITE, self._write)

    def _code(self, cpu, address, size, _):
        """Capture callback scalars; reject unexpected branches before executing them."""
        if not self.active:
            return
        if address == self.image.CALLBACK:
            if self.stage != 'walk':
                raise ValueError('Unexpected TLSF callback')
            rv = self.image.rv
            pointer, capacity, used, token = [cpu.reg_read(rv.UC_RISCV_REG_A0 + i) for i in range(4)]
            if (token != 0x5A17 or used not in (0, 1) or not capacity or capacity % 4 or pointer % 4 or
                    not self.control <= pointer < pointer + capacity <= self.end or
                    pointer - self.overhead != self.current_header):
                raise ValueError('Invalid block callback geometry')
            if self.blocks:
                previous = self.blocks[-1]
                if pointer != previous[0] + previous[1] + self.overhead:
                    raise ValueError('Noncontiguous or cyclic TLSF block chain')
                if previous[2] == used == 0:
                    raise ValueError('Adjacent uncoalesced free blocks')
            if len(self.blocks) >= 16384:
                raise ValueError('Too many TLSF blocks')
            self.blocks.append((pointer, capacity, used))
            self.next_header = pointer + capacity
        elif self.image.CALLBACK < address < self.image.CALLBACK + 8:
            return
        elif not any(lo <= address < hi for lo, hi in self.code):
            raise ValueError('Unexpected TLSF instruction control flow')

    def _read(self, cpu, _, address, size, value, user):
        """Forward only real header-word reads, never an allocated payload read."""
        if not self.active or self.image.STACK <= address < address + size <= self.image.STACK + 4096:
            return
        if size != 4 or address % 4 or not self.control <= address < address + size <= self.end:
            raise ValueError('TLSF requested non-header memory')
        if self.stage == 'walk':
            if address not in (self.current_header, self.next_header):
                raise ValueError('TLSF attempted to inspect allocator payload')
            self.current_header = address
        else:
            raise ValueError('Unexpected memory read by qualified constant getter')
        if address not in self.words:
            data = self.reader(address, size)
            if len(data) != size:
                raise ValueError('Short TLSF metadata read')
            self.words[address] = int.from_bytes(data, 'little')
        cpu.mem_write(address, self.words[address].to_bytes(4, 'little'))

    def _write(self, cpu, _, address, size, value, user):
        """Permit local stack saves only; a replay cannot write the observed heap."""
        if self.active and not self.image.STACK <= address < address + size <= self.image.STACK + 4096:
            raise ValueError('Read-only TLSF replay attempted a heap write')

    def inspect(self, read, control, pool_size, free_counter, extent, linked=True):
        """Return exact block accounting plus a payload-free replay transcript."""
        if (type(control) is not int or control % 4 or type(pool_size) is not int or pool_size % 4 or
                not 0 < pool_size <= 0x40000 or type(free_counter) is not int or
                not 0 <= free_counter <= pool_size or len(extent) != 2 or
                not any(lo <= extent[0] < extent[1] <= hi for lo, hi in RAM) or
                not extent[0] <= control < control + pool_size <= extent[1]):
            raise ValueError('Invalid bounded heap extent')
        name = 'linked_tlsf_walk_pool' if linked else 'tlsf_walk_pool'
        if name not in self.image.functions:
            raise ValueError('Requested TLSF walker is unavailable')
        self.control, self.end = control, control + pool_size
        self.reader, self.words, self.blocks, self.stage = read, {}, [], 'constants'
        self.active = True
        try:
            control_size = self.image.call('tlsf_size')
            pool = self.image.call('tlsf_get_pool', control)
            self.overhead = self.image.call('tlsf_alloc_overhead')
            pool_overhead = self.image.call('tlsf_pool_overhead')
            if (pool != control + control_size or self.overhead != 4 or pool_overhead != 8 or
                    not control_size < pool_size - pool_overhead):
                raise ValueError('Qualified ROM heap layout differs')
            self.stage = 'walk'; self.current_header = self.next_header = pool
            self.image.call(name, pool, self.image.CALLBACK, 0x5A17)
            if not self.blocks or self.current_header != self.blocks[-1][0] + self.blocks[-1][1]:
                raise ValueError('TLSF walk did not read its terminal sentinel')
            allocated = [row for row in self.blocks if row[2]]
            free = [row for row in self.blocks if not row[2]]
            used_bytes = sum(row[1] for row in allocated)
            available = pool_size - control_size
            if used_bytes + len(allocated) * self.overhead + free_counter != available:
                raise ValueError('Block inventory disagrees with actual free counter')
            if sum(row[1] for row in self.blocks) + (len(self.blocks) - 1) * self.overhead + pool_overhead != available:
                raise ValueError('TLSF physical pool bytes do not balance')
            histogram = lambda rows: [list(item) for item in sorted(Counter(row[1] for row in rows).items())]
            return {'rom_sha256': self.image.rom_sha256, 'app_elf_sha256': self.image.app_sha256,
                    'walker': name, 'control_bytes': control_size, 'pool_overhead_bytes': pool_overhead,
                    'allocation_header_bytes': self.overhead,
                    'allocated_blocks': len(allocated), 'allocated_capacity_bytes': used_bytes,
                    'allocated_header_bytes': len(allocated) * self.overhead,
                    'free_blocks': len(free), 'free_capacity_bytes': sum(row[1] for row in free),
                    'largest_free_capacity_bytes': max((row[1] for row in free), default=0),
                    'allocated_capacity_histogram': histogram(allocated), 'free_capacity_histogram': histogram(free),
                    'record': {'control': control, 'pool_size': pool_size, 'free_counter': free_counter,
                               'extent': list(extent), 'linked': linked,
                               'metadata_words': [[address - control, word] for address, word in sorted(self.words.items())]}}
        finally:
            self.active = False; self.reader = None

    def replay(self, record):
        """Re-execute metadata transcripts; reject duplicate, unused or payload words."""
        entries = record['metadata_words']
        if (len(entries) > 16385 or any(len(row) != 2 or type(row[0]) is not int or
                type(row[1]) is not int or row[0] < 0 or row[0] % 4 or not 0 <= row[1] < 2**32 for row in entries)):
            raise ValueError('Invalid TLSF metadata transcript')
        words = {record['control'] + offset: value for offset, value in entries}
        if len(words) != len(entries):
            raise ValueError('Duplicate TLSF metadata word')
        def read(address, size):
            """Serve only archived scalar headers; no zero-filled payload fallback."""
            if size != 4 or address not in words:
                raise ValueError('Missing TLSF metadata word')
            return words[address].to_bytes(4, 'little')
        result = self.inspect(read, record['control'], record['pool_size'], record['free_counter'],
                              record['extent'], record['linked'])
        if result['record'] != record:
            raise ValueError('Noncanonical or unused TLSF metadata words')
        return result
