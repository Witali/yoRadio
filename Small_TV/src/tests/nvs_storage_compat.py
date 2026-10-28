"""Preserve type replacement/legacy BLOB behavior and exercise repeated Storage initialization."""
from nvs_storage_fixture import Partition, execute, sector, ACTIVE, FULL, STORAGE_INIT
from nvs_record_vectors import item, crc
from runtime_call_instructions import HEAP


def run(definition, reader, crc_definition):
    """Check ordinary TYPE_MISMATCH search misses, legacy fallback and owned-object retries."""
    blank = b'\xff'*4096; results = []
    scenarios = [
        dict(name='cross-page-type-replacement', pages=[sector(FULL, 0, {0: item()}),
             sector(ACTIVE, 1, {0: item(datatype=2, value=257)}), blank],
             wanted=[(1, b'value', 2, b'\x01\x01')]),
        dict(name='cross-page-legacy-blob-replacement', pages=[
             sector(FULL, 0, {0: item(b'blob', datatype=0x41, span=2, size=1, data_crc=crc(b'A'))}, {1: b'A'}),
             sector(ACTIVE, 1, {0: item(b'blob', datatype=0x42, span=2, size=1, chunk=0, data_crc=crc(b'B')),
                                2: item(b'blob', datatype=0x48, value=1 | 1 << 32 | 0xffff << 48)}, {1: b'B'}), blank],
             wanted=[(1, b'blob', 0x41, b'B')]),
    ]
    for case in scenarios:
        media = Partition(case['pages'])
        row, _ = execute('native', definition, reader, crc_definition, media, wanted=case['wanted'])
        assert row['status'] == 0 and row['keys_correct']
        results.append(dict(name=case['name'], result=row))

    retries = []
    for failure in ('header-read', 'page-array-oom'):
        media = Partition([sector(ACTIVE, 0, {0: item(b'cfg', namespace=0, value=1), 1: item()}), blank, blank])
        first, cpu = execute('native', definition, reader, crc_definition, media, wanted=[(1, b'value', 1, b'\x07')])
        assert first['status'] == 0 and first['keys_correct']
        def initialize():
            """Reuse the same constructed C++ object, real destructors and live allocator ownership."""
            for register, value in enumerate((HEAP+128, 2, 3), 10): cpu.reg(register, value)
            return cpu.invoke(STORAGE_INIT)
        media.operations = []
        if failure == 'header-read': media.fail_at = 1
        else: cpu.fail_malloc = cpu.malloc_calls+1
        failed = initialize()
        assert failed == (0x104 if failure == 'header-read' else 0x101) and cpu.word(HEAP+128+100) == 0
        media.fail_at = 0; cpu.fail_malloc = 0; media.operations = []
        recovered = initialize()
        assert recovered == 0 and cpu.word(HEAP+128+100) == 1
        # The temporary index list is empty and the original namespace is replaced,
        # rather than retained as an unreachable allocation after another init.
        assert sum(size == 28 for size in cpu.allocations.values()) == 1
        assert not any(size == 40 for size in cpu.allocations.values())
        retries.append(dict(failure=failure, failed_status=failed, recovered_status=recovered,
                            live_sizes=sorted(cpu.allocations.values()), operations=media.operations))
    return dict(passed=True, replacement_cases=len(results), same_object_retries=len(retries),
                results=results, retries=retries, physical_hardware_tested=False)
