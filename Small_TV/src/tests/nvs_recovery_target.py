"""Verify corrected linked C2 NVS recovery against key retention, counters and physical bytes."""
from nvs_recovery_faults import attempt
from nvs_recovery_vectors import vectors_extra
from nvs_records_cpu import RecordPartition


def run(definition, reader, crc):
    """Check all record cases and stable reopens; test distinct FULL/FREEING repair branches."""
    results = []; state_cases = []
    for case in vectors_extra():
        partition = RecordPartition(case)
        row = attempt('native', definition, reader, crc, partition, case['wanted'])
        assert row['status'] == 0 and row['fields']['state'] == 0xfffffffe
        assert row['counters_correct'] and row['keys_correct'], (case['name'], row)
        after = bytes(partition.bytes); partition.operations = []
        reopened = attempt('native', definition, reader, crc, partition, case['wanted'])
        assert reopened['status'] == 0 and reopened['counters_correct'] and reopened['keys_correct']
        assert bytes(partition.bytes) == after and not any(op['kind'] == 'write_raw' for op in reopened['operations'])
        results.append(dict(name=case['name'], loaded=row, reopened=reopened))
        if case['name'] in ('single', 'variable-erased-child', 'variable-illegal-child',
                            'bad-header-crc', 'published-index-before-new-generation', 'hash24-collision'):
            for state in (0xfffffffc, 0xfffffff8):
                partition = RecordPartition(case)
                row = attempt('native', definition, reader, crc, partition, case['wanted'], state)
                assert row['status'] == 0 and row['fields']['state'] == state
                assert row['counters_correct'] and row['keys_correct'], (case['name'], state, row)
                state_cases.append(dict(name=case['name'], page_state=state, loaded=row))
    return dict(passed=True, record_cases=len(results), reopen_cases=len(results),
                full_freeing_cases=len(state_cases), results=results, states=state_cases,
                physical_hardware_tested=False, whole_image_completeness_proved=False)
