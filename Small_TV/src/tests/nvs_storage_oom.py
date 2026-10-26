"""Detect leaked temporary BLOB index nodes on actual exceptionless allocation failures."""
from nvs_storage_fixture import Partition, execute, sector, ACTIVE
from nvs_record_vectors import item, crc


def run(definitions, readers, crc_definition, require_native_cleanup=False):
    """Fail each of two40-byte temporary nodes while preserving persistent Page/namespace ownership."""
    headers = {0: item(b'cfg', namespace=0, value=1)}; data = {}
    for head, key, value in ((1, b'a', b'A'), (4, b'b', b'B')):
        headers[head] = item(key, datatype=0x42, span=2, size=1, chunk=0, data_crc=crc(value))
        data[head+1] = value
        headers[head+2] = item(key, datatype=0x48, value=1 | 1 << 32 | 0xffff << 48)
    pages = [sector(ACTIVE, 0, headers, data), b'\xff'*4096, b'\xff'*4096]; results = {}
    for variant, definition in definitions.items():
        baseline_partition = Partition(pages)
        baseline, _ = execute(variant, definition, readers[variant], crc_definition, baseline_partition)
        assert baseline['status'] == 0
        assert not any(size == 40 for size in baseline['retained_allocations'].values())
        ordinals = [i for i, row in enumerate(baseline['allocations'], 1) if row['size'] == 40]
        assert ordinals == [6, 7]; rows = []
        for position, ordinal in enumerate(ordinals):
            partition = Partition(pages)
            failed, cpu = execute(variant, definition, readers[variant], crc_definition, partition, fail_malloc=ordinal)
            assert failed['status'] == 0x101 and failed['storage_state'] == 0
            assert cpu.allocation_log[-1] == dict(size=40, pointer=0)
            retained = sum(size == 40 for size in cpu.allocations.values())
            expected = 0 if variant == 'native' and require_native_cleanup else position
            assert retained == expected, (variant, ordinal, retained)
            assert not any(op['kind'] in ('write', 'write_raw', 'erase') for op in failed['operations'])
            assert bytes(partition.bytes) == partition.initial
            rows.append(dict(failed_ordinal=ordinal, failed=failed, leaked_temporary_bytes=40*retained))
        results[variant] = dict(baseline=baseline, failures=rows)
    return dict(passed=True, cases=4, results=results,
                native_temporary_cleanup_passed=not any(r['leaked_temporary_bytes'] for r in results['native']['failures']),
                standard_array_oom_executed=False, physical_hardware_tested=False)
