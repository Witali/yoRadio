"""Exercise full compiled Storage initialization, data reads and retained multi-sector faults."""
from nvs_storage_fixture import Partition, execute
from nvs_storage_vectors import cases


def physical(partition, operations):
    """Reconstruct transferred NOR programs/erases independently of the adapter implementation."""
    expected = bytearray(partition.initial)
    for op in operations:
        at, count = op['offset'], op['transferred']
        if op['kind'] == 'erase':
            expected[at:at+count] = b'\xff'*count
        elif op['kind'] in ('write', 'write_raw'):
            data = bytes.fromhex(op['data'])
            for i in range(count): expected[at+i] &= data[i]
    assert partition.bytes == expected, 'Storage fault lost physical side effects'


def run(definitions, readers, crc, require_native_errors=False):
    """Keep successful baseline behavior separate from newly discovered failure contracts."""
    results = {}; failures = {}; faults_for = {'cross-page-duplicate', 'freeing-copy',
                                              'published-blob-next-page', 'unpublished-blob-next-page'}
    for variant, definition in definitions.items():
        rows = []; faults = []
        for case in cases():
            partition = Partition(case['sectors'])
            row, _ = execute(variant, definition, readers[variant], crc, partition, wanted=case['wanted'])
            assert row['status'] == 0 and row['storage_state'] == 1
            known_loss = variant == 'factory' and case.get('factory_key_loss', False)
            assert row['keys_correct'] != known_loss, (variant, case['name'], row['lookups'])
            if 'order' in case: assert [p['sequence'] for p in row['pages']] == case['order']
            if 'erases' in case: assert sum(op['kind'] == 'erase' for op in row['init_operations']) == case['erases']
            physical(partition, row['operations'])
            retained = bytes(partition.bytes); partition.operations = []
            reopened, _ = execute(variant, definition, readers[variant], crc, partition, wanted=case['wanted'])
            assert reopened['status'] == 0 and reopened['storage_state'] == 1
            assert reopened['keys_correct'] != known_loss
            assert bytes(partition.bytes) == retained and not any(op['kind'] in ('write', 'write_raw', 'erase') for op in reopened['operations'])
            rows.append(dict(name=case['name'], loaded=row, reopened=reopened))
            if case['name'] not in faults_for: continue
            for ordinal, operation in enumerate(row['init_operations'], 1):
                # The old isolated Page caller suite already exhausts all eight blank
                # sector scans. Keep every other observed I/O on these four new paths.
                if operation['kind'] == 'read_raw' and operation['bytes'] == 512: continue
                for partial in (False, True):
                    media = Partition(case['sectors'], fail_at=ordinal, partial=partial)
                    failed, _ = execute(variant, definition, readers[variant], crc, media)
                    assert any(op['failed'] for op in failed['operations'])
                    physical(media, failed['operations'])
                    surfaced = failed['status'] == 0x104 and failed['storage_state'] == 0
                    if variant == 'native' and require_native_errors:
                        assert surfaced and len(failed['operations']) == ordinal, (case['name'], ordinal, partial, failed)
                    media.operations = []; media.fail_at = 0
                    recovered, _ = execute(variant, definition, readers[variant], crc, media, wanted=case['wanted'])
                    faults.append(dict(name=case['name'], ordinal=ordinal, partial=partial, failed=failed,
                                       error_surfaced=surfaced, recovered=recovered,
                                       key_preservation_passed=recovered['status'] == 0 and recovered['keys_correct']))
        results[variant] = rows; failures[variant] = faults
        print(__import__('json').dumps(dict(variant=variant,baseline_cases=len(rows),fault_cases=len(faults),
              hidden_errors=sum(not r['error_surfaced'] for r in faults),
              key_loss_after_retry=sum(not r['key_preservation_passed'] for r in faults))),flush=True)
    return dict(passed=True, baselines=results, faults=failures, physical_hardware_tested=False,
                native_error_contract_passed=all(r['error_surfaced'] for r in failures['native']),
                native_key_preservation_passed=all(r['key_preservation_passed'] for r in failures['native']),
                full_vm_power_fault_proved=False)
