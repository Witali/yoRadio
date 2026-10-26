"""Run real Page/Item/HashList recovery and key lookup with real ROM CRC arithmetic."""
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from unicorn import riscv_const as rv
from audit_factory_xrefs import Image, sha
from reverse.factory_nvs import TABLE
from reverse.nothrow_linkage import LinkedRuntime
from runtime_call_instructions import HEAP, END, PRESERVED
from nvs_partition_fixture import Partition
from nvs_record_vectors import EMPTY, WRITTEN, ERASED, vectors, hash24
from nvs_rom_crc import CrcFixture

FIND_ITEM = '_ZN3nvs4Page8findItemEhNS_8ItemTypeEPKcRjRNS_4ItemEhNS_9VerOffsetE'
HEADER_CHECK = '_ZNK3nvs4Item22checkHeaderConsistencyEh'
HASH = '_ZNK3nvs4Item26calculateCrc32WithoutValueEv'


class RecordPartition(Partition):
    """Extend only the synthetic Partition API adapter with written/illegal wire records."""
    def __init__(self, case):
        """Retain exact synthetic bytes instead of substituting parsed Item objects."""
        super().__init__([EMPTY]*126, set())
        for index, state in enumerate(case['states']):
            at = 32+index//4; shift = index % 4*2
            self.bytes[at] = (self.bytes[at] & ~(3 << shift)) | state << shift
        for index, raw in case['payloads'].items(): self.bytes[64+index*32:96+index*32] = raw
        for index, raw in case['data_payloads'].items(): self.bytes[64+index*32:96+index*32] = raw
        self.initial = bytes(self.bytes)

    def attach(self, f):
        """Expose unencrypted Item reads distinctly from raw bitmap and purge operations."""
        super().attach(f); f.word(HEAP+768+16, END+1056)
        def read(args):
            """Use the same bytes for unencrypted data while retaining the real virtual method identity."""
            result = self.operation(f, 'read_raw', args); self.operations[-1]['kind'] = 'read'; return result
        f.boundary('read', END+1056, read)


class RecordCpu(CrcFixture):
    """Track the128-byte cache allocations and reject CPU access to freed cache blocks."""
    def __init__(self, variant, definition, reader, crc, fail_malloc=0):
        """Keep all NVS algorithms and replace only explicit C-library/allocator primitives."""
        self.live = set(); self.malloc_calls = 0; self.free_calls = 0; self.fail_malloc = fail_malloc
        super().__init__(variant, definition, reader, crc)
        for name, address in definition['externals'].items():
            if name == 'esp_rom_crc32_le': continue
            self.boundary(name, address, getattr(self, 'primitive_'+name))

    def memory(self, cpu, access, address, size, value, data):
        """Preserve stack/ROM guards and enforce actual cache ownership in the allocation arena."""
        if HEAP+2048 <= address < HEAP+4096:
            assert any(pointer <= address < address+size <= pointer+128 for pointer in self.live), 'Cache use after free/out of range'
        super().memory(cpu, access, address, size, value, data)

    def primitive_malloc(self, args):
        """Allocate only the observed fixed-size NVS cache block, with optional exact-call OOM."""
        assert args[0] == 128; self.malloc_calls += 1
        if self.malloc_calls == self.fail_malloc: return 0
        pointer = next(p for p in range(HEAP+2048, HEAP+4096, 128) if p not in self.live)
        self.live.add(pointer); self.cpu.mem_write(pointer, b'\xa5'*128); return pointer

    def primitive_free(self, args):
        """Require ownership of the exact block before releasing it."""
        pointer = args[0]; assert pointer in self.live
        self.live.remove(pointer); self.free_calls += 1; return 0

    def primitive_memset(self, args):
        """Apply standard byte-fill semantics within guarded private memory."""
        destination, value, size = args[:3]; assert size <= 128
        self.cpu.mem_write(destination, bytes([value & 255])*size); return destination

    def primitive_strncpy(self, args):
        """Implement only the standard bounded constructor key copy, including zero padding."""
        destination, source, size = args[:3]; assert size == 15
        raw = bytes(self.cpu.mem_read(source, size)).split(b'\0', 1)[0]
        self.cpu.mem_write(destination, raw.ljust(size, b'\0')); return destination

    def primitive_strncmp(self, args):
        """Compare bounded unsigned bytes until NUL; never replace NVS key/type decisions."""
        left, right, size = args[:3]; assert size <= 16
        a = bytes(self.cpu.mem_read(left, size)); b = bytes(self.cpu.mem_read(right, size))
        for x, y in zip(a, b):
            if x != y: return x-y
            if x == 0: return 0
        return 0

    def invoke(self, name):
        """Give CRC-heavy full-page scans a finite budget and require natural ABI return."""
        self.reg(1, END)
        try: self.cpu.emu_start(int(self.rows[name]['start'], 0), END, count=2000000)
        except Exception as error:
            raise AssertionError(f'{self.variant}: {name} at {self.cpu.reg_read(rv.UC_RISCV_REG_PC):#x}') from error
        assert self.cpu.reg_read(rv.UC_RISCV_REG_PC) == END and self.stopped is None
        for register in PRESERVED: assert self.reg(register) == self.initial[register]
        return self.reg(10)


def execute(variant, definition, reader, crc, case, fail_malloc=0):
    """Check real recovery, then call real findItem for every expected application key."""
    f = RecordCpu(variant, definition, reader, crc, fail_malloc); partition = RecordPartition(case)
    page = HEAP+128; blob = bytearray(b'\xa5'*84)
    for offset, value in ((8, 8192), (12, 0xfffffffe), (16, 0), (56, 0xffffffff), (60, 0xffffffff), (80, HEAP+512)):
        struct.pack_into('<I', blob, offset, value)
    blob[20] = 254; blob[64:80] = b'\0'*16; f.cpu.mem_write(page, bytes(blob)); partition.attach(f)
    inputs = []
    for index, raw in case['payloads'].items():
        f.cpu.mem_write(HEAP+1280, raw); f.reg(10, HEAP+1280); f.reg(11, index)
        valid = f.invoke(HEADER_CHECK); assert bool(valid) == (index not in case['invalid_headers'])
        f.reg(10, HEAP+1280); observed_hash = f.invoke(HASH) & 0xffffff
        expected_hash = hash24(raw[8:24].split(b'\0', 1)[0], raw[0], raw[3]); assert observed_hash == expected_hash
        inputs.append(dict(index=index, header_valid=bool(valid), hash24=observed_hash))
    f.reg(10, page)
    result = f.invoke(TABLE); after = bytes(f.cpu.mem_read(page, 84))
    counts = dict(used=int.from_bytes(after[64:66], 'little'), erased=int.from_bytes(after[66:68], 'little'))
    states = [(partition.bytes[32+i//4] >> ((i % 4)*2)) & 3 for i in range(126)]
    bitmap_counts = dict(used=states.count(WRITTEN), erased=states.count(ERASED))
    lookups = []
    if result == 0:
        for wanted in case['wanted']:
            namespace, key, chunk, value = wanted[:4]; datatype = wanted[4] if len(wanted) > 4 else 255
            index, out, key_at = HEAP+1024, HEAP+1088, HEAP+1152
            f.word(index, 0); f.cpu.mem_write(out, b'\xa5'*32); f.cpu.mem_write(key_at, key.ljust(16, b'\0'))
            for register, argument in enumerate((page, namespace, datatype, key_at, index, out, chunk, 255), 10): f.reg(register, argument)
            status = f.invoke(FIND_ITEM)
            observed = int.from_bytes(f.cpu.mem_read(out+24, 8), 'little') if status == 0 else None
            lookups.append(dict(namespace=namespace, key=key.decode(), status=status, value=observed,
                                expected_value=value, index=f.word(index)))
    return dict(name=case['name'], inputs=inputs, result=result, state=f.word(page+12), counts=counts, bitmap_counts=bitmap_counts,
                counters_correct=counts == bitmap_counts, lookups=lookups,
                keys_correct=all(r['status'] == 0 and r['value'] == r['expected_value'] for r in lookups),
                bitmap=states, physical_sha256=sha(bytes(partition.bytes)), operations=partition.operations,
                malloc_calls=f.malloc_calls, free_calls=f.free_calls, live_allocations=sorted(f.live), visited=sorted(f.visited))


def run(factory, native, app, linkage, crc, native_fixes=()):
    """Retain observed before defects instead of reporting them as desired contract passes."""
    readers = {'factory': Image(factory).read, 'native': LinkedRuntime(native, app).read}; results = {}; failures = {}
    for variant, definition in linkage['variants'].items():
        rows = []
        for case in vectors():
            row = execute(variant, definition, readers[variant], crc, case)
            assert row['result'] == 0, (variant, case['name'], row['result'])
            counter_fixed = variant == 'native' and 'counts' in native_fixes
            identity_fixed = variant == 'native' and 'key_identity' in native_fixes
            assert row['counters_correct'] == (counter_fixed or not case['counter_bug']), (variant, case['name'], row['counts'], row['bitmap_counts'])
            assert row['keys_correct'] == (identity_fixed or not (case['collision_bug'] or case['chunk_bug'])), (variant, case['name'], row['lookups'])
            rows.append(row)
        results[variant] = rows
        oom = []
        for case in (c for c in vectors() if c['name'] in ('single', 'cache-blocks-30', 'cache-blocks-60', 'cache-blocks-126')):
            for ordinal in range(1, (len(case['payloads'])+28)//29+1):
                row = execute(variant, definition, readers[variant], crc, case, fail_malloc=ordinal)
                assert row['result'] == 0x101 and row['state'] == 0
                assert row['malloc_calls'] == ordinal and len(row['live_allocations']) == ordinal-1 and row['free_calls'] == 0
                assert not any(op['kind'] == 'write_raw' for op in row['operations'])
                assert row['counts'] == row['bitmap_counts'] == dict(used=len(case['payloads']), erased=0)
                oom.append(dict(failed_allocation=ordinal, **row))
        failures[variant] = oom
    return dict(passed=True, results=results, oom=failures, native_fixes=sorted(native_fixes),
                native_counter_contract_passed=all(r['counters_correct'] for r in results['native']),
                native_key_contract_passed=all(r['keys_correct'] for r in results['native']),
                factory_defects_reproduced=True, physical_hardware_tested=False)
