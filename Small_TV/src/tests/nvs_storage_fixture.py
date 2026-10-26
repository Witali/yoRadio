"""Keep synthetic multi-sector Partition bytes while running the real Storage/PageManager code."""
from collections import deque
import struct

from unicorn import UC_HOOK_CODE
from nvs_records_cpu import RecordCpu
from nvs_rom_crc import CrcFixture
from nvs_record_vectors import crc, item
from runtime_call_instructions import HEAP, STACK, END

STORAGE_INIT = '_ZN3nvs7Storage4initEmm'
STORAGE_READ = '_ZN3nvs7Storage8readItemEhNS_8ItemTypeEPKcPvj'
ACTIVE, FULL, FREEING = 0xfffffffe, 0xfffffffc, 0xfffffff8


def sector(state=ACTIVE, sequence=0, records=None, data=None):
    """Encode an independent wire page header/bitmap, without calling any SDK parser."""
    raw = bytearray(b'\xff'*4096)
    struct.pack_into('<IIB', raw, 0, state, sequence, 254)
    struct.pack_into('<I', raw, 28, crc(raw[4:28]))
    for index, header in (records or {}).items():
        span = header[2]; assert 0 < span <= 126-index
        for child in range(index, index+span):
            raw[32+child//4] &= ~(1 << ((child % 4)*2))
        raw[64+32*index:96+32*index] = header
    for index, payload in (data or {}).items():
        assert len(payload) <= 32; raw[64+32*index:96+32*index] = payload.ljust(32, b'\xff')
    return bytes(raw)


class Partition:
    """Model only declared Partition virtual methods, with retained NOR bytes and fault prefixes."""
    def __init__(self, sectors, readonly=False, fail_at=0, partial=False):
        """Own only synthetic pages at sector2; no dump, live flash or personal settings."""
        self.bytes = bytearray(b''.join(sectors)); assert len(self.bytes) % 4096 == 0
        self.initial = bytes(self.bytes); self.base = 8192; self.readonly = readonly
        self.fail_at = fail_at; self.partial = partial; self.operations = []

    def attach(self, f):
        """Install each independently declared virtual slot, including read-only status."""
        f.word(HEAP+512, HEAP+768)
        for slot, kind in ((12, 'read_raw'), (16, 'read'), (20, 'write_raw'), (24, 'write'), (28, 'erase')):
            address = END+1024+slot*4
            f.word(HEAP+768+slot, address)
            f.boundary(kind, address, lambda args, kind=kind: self.operation(f, kind, args))
        f.word(HEAP+768+40, END+1408)
        f.boundary('get_readonly', END+1408, lambda args: int(self.readonly))

    def operation(self, f, kind, args):
        """Keep transfers explicit and reject forbidden programs instead of rolling them back."""
        owner, address = args[:2]; assert owner == HEAP+512
        pointer, size = (0, args[2]) if kind == 'erase' else args[2:4]
        offset = address-self.base; assert 0 <= offset < offset+size <= len(self.bytes)
        assert size in (4, 32, 512, 4096)
        assert address % (4096 if kind == 'erase' else 4) == 0
        failed = len(self.operations)+1 == self.fail_at
        count = size//2 if failed and self.partial else 0 if failed else size
        op = dict(kind=kind, offset=offset, bytes=size, failed=failed, transferred=count)
        if kind in ('read_raw', 'read'):
            f.check_memory(pointer, size); f.cpu.mem_write(pointer, bytes(self.bytes[offset:offset+count]))
        else:
            assert not self.readonly, 'Unexpected mutation of a read-only partition'
            if kind == 'erase':
                self.bytes[offset:offset+count] = b'\xff'*count
            else:
                f.check_memory(pointer, size); data = bytes(f.cpu.mem_read(pointer, size)); op['data'] = data.hex()
                assert all(self.bytes[offset+i] & value == value for i, value in enumerate(data)), 'NOR0->1 program'
                for i in range(count): self.bytes[offset+i] &= data[i]
        self.operations.append(op)
        return 0x104 if failed else 0


class Cpu(RecordCpu):
    """Use real NVS/ROM algorithms with bounded generic allocation and standard primitives."""
    def __init__(self, variant, definition, reader, crc_definition, fail_malloc=0):
        """Reserve the upper synthetic arena for individually tracked allocation extents."""
        self.allocations = {}; self.allocation_log = []
        super().__init__(variant, definition, reader, crc_definition, fail_malloc)

    def check_memory(self, address, size):
        """Enforce both private fixture bounds and dynamic ownership for primitive/API buffers."""
        assert size >= 0
        assert STACK-4096 <= address <= address+size <= STACK+4096 or HEAP <= address <= address+size <= HEAP+4096
        if HEAP+1536 <= address < HEAP+4096:
            assert any(p <= address <= address+size <= p+n for p, n in self.allocations.items()), 'Unowned allocation buffer'

    def memory(self, cpu, access, address, size, value, data):
        """Preserve ROM read guards while checking actual allocation sizes instead of cache-only128B."""
        if HEAP+1536 <= address < HEAP+4096:
            self.check_memory(address, size)
        CrcFixture.memory(self, cpu, access, address, size, value, data)

    def primitive_malloc(self, args):
        """Return finite aligned blocks and allow an exact allocation ordinal to fail."""
        size = args[0]; assert 0 < size <= 1024
        self.malloc_calls += 1
        if self.malloc_calls == self.fail_malloc:
            self.allocation_log.append(dict(size=size, pointer=0)); return 0
        pointer = HEAP+1536
        for start, length in sorted(self.allocations.items()):
            if pointer+size <= start: break
            pointer = max(pointer, (start+length+7)&~7)
        assert pointer+size <= HEAP+4096, 'Synthetic allocator capacity exhausted'
        self.allocations[pointer] = size; self.cpu.mem_write(pointer, b'\xa5'*size)
        self.allocation_log.append(dict(size=size, pointer=pointer)); return pointer

    def primitive_free(self, args):
        """Reject interior pointers and double frees; tolerate the standard free(NULL)."""
        pointer = args[0]
        if pointer:
            assert pointer in self.allocations; del self.allocations[pointer]
            self.free_calls += 1
        return 0

    def primitive__ZnajRKSt9nothrow_t(self, args):
        """Expose a nullable standard array allocation boundary, not the factory abort implementation."""
        return self.primitive_malloc(args)

    def primitive__ZdaPv(self, args):
        """Observe the already adjusted array allocation pointer after real destructors run."""
        return self.primitive_free(args)

    def primitive_memset(self, args):
        """Apply standard bounded byte filling, including real Page constructor initialization."""
        destination, value, size = args[:3]; self.check_memory(destination, size)
        self.cpu.mem_write(destination, bytes([value & 255])*size); return destination

    def primitive_memcpy(self, args):
        """Copy only validated private ranges, without interpreting NVS records."""
        destination, source, size = args[:3]; self.check_memory(destination, size); self.check_memory(source, size)
        self.cpu.mem_write(destination, bytes(self.cpu.mem_read(source, size))); return destination

    def primitive_strncpy(self, args):
        """Use bounded C string-copy semantics for keys and namespace names."""
        destination, source, size = args[:3]; assert 0 < size <= 16
        self.check_memory(destination, size); self.check_memory(source, size)
        raw = bytes(self.cpu.mem_read(source, size)).split(b'\0', 1)[0]
        self.cpu.mem_write(destination, raw.ljust(size, b'\0')); return destination


def execute(variant, definition, reader, crc_definition, partition, fail_malloc=0, wanted=()):
    """Construct a fresh DWARF-checked Storage and execute actual init with all its algorithms."""
    f = Cpu(variant, definition, reader, crc_definition, fail_malloc); storage = HEAP+128
    # Both resolved DWARF profiles: Storage104B, PageManager40B at16, Namespace list12B at56.
    f.cpu.mem_write(storage, b'\0'*104); f.word(storage+8, HEAP+512); partition.attach(f)
    f.reg(10, storage); f.reg(11, 2); f.reg(12, len(partition.bytes)//4096)
    recent = deque(maxlen=12)
    f.cpu.hook_add(UC_HOOK_CODE, lambda cpu, pc, size, data: recent.append((hex(pc), hex(f.reg(1)))))
    try:
        status = f.invoke(STORAGE_INIT)
    except Exception as error:
        raise AssertionError('Storage CPU stopped; last PCs='+str(list(recent))+
                             '; operations='+str(partition.operations[-5:])) from error
    manager = storage+16; init_operations = list(partition.operations); lookups = []
    if status == 0:
        for namespace, key, datatype, expected in wanted:
            key_at, destination = HEAP+1024, HEAP+1088
            f.cpu.mem_write(key_at, key.ljust(16, b'\0')); f.cpu.mem_write(destination, b'\xa5'*32)
            for register, value in enumerate((storage, namespace, datatype, key_at, destination, len(expected)), 10):
                f.reg(register, value)
            result = f.invoke(STORAGE_READ)
            observed = bytes(f.cpu.mem_read(destination, len(expected)))
            lookups.append(dict(namespace=namespace, key=key.decode(), datatype=datatype, status=result,
                                value_hex=observed.hex(), expected_hex=expected.hex(), correct=result == 0 and observed == expected))
    def pages(offset):
        """Walk the actual intrusive list with cycle/extent checks, never a reconstructed Python order."""
        node = f.word(manager+offset); count = f.word(manager+offset+8); result = []
        while node:
            assert len(result) < 6 and node not in [r['pointer'] for r in result]
            f.check_memory(node, 84)
            result.append(dict(pointer=node, base=f.word(node+8), state=f.word(node+12), sequence=f.word(node+16),
                               used=int.from_bytes(f.cpu.mem_read(node+64, 2), 'little'),
                               erased=int.from_bytes(f.cpu.mem_read(node+66, 2), 'little')))
            node = f.word(node+4)
        assert len(result) == count
        return result
    return dict(status=status, storage_state=f.word(storage+100), page_sequence=f.word(manager+36),
                pages=pages(0), free_pages=pages(12), allocations=f.allocation_log,
                retained_allocations={str(p): size for p, size in f.allocations.items()}, operations=list(partition.operations),
                init_operations=init_operations, lookups=lookups,
                keys_correct=all(row['correct'] for row in lookups),
                media_sha256=__import__('hashlib').sha256(partition.bytes).hexdigest()), f
