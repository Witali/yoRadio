"""Check the actual six-sector NVS geometry and the no-free-page/read-only distinction."""
from nvs_storage_fixture import Partition, execute, sector, FULL
from nvs_record_vectors import item


def run(definitions, readers, crc):
    """Use complete init/read code for five live pages plus reserve, and six occupied pages."""
    results = {}
    for variant, definition in definitions.items():
        rows = []
        for occupied, readonly in ((5, False), (6, False), (6, True)):
            pages = [sector(FULL, n, {0: item(f'key{n}'.encode(), value=n+1)}) for n in range(occupied)]
            pages += [b'\xff'*4096]*(6-occupied)
            wanted = [(1, f'key{n}'.encode(), 1, bytes([n+1])) for n in range(occupied)]
            partition = Partition(pages, readonly=readonly)
            row, _ = execute(variant, definition, readers[variant], crc, partition, wanted=wanted)
            expected = 0x110d if occupied == 6 and not readonly else 0
            assert row['status'] == expected and row['storage_state'] == int(expected == 0)
            assert [p['sequence'] for p in row['pages']] == list(range(occupied))
            assert row['keys_correct'] and len(row['free_pages']) == 6-occupied
            assert not any(op['kind'] in ('write', 'write_raw', 'erase') for op in row['operations'])
            assert bytes(partition.bytes) == partition.initial
            rows.append(dict(occupied=occupied, readonly=readonly, **row))
        results[variant] = rows
    return dict(passed=True, cases=6, sectors=6, bytes=24576, results=results,
                physical_hardware_tested=False)
