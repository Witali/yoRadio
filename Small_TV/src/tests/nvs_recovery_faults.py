"""Inject real Partition API failures into compiled NVS record recovery and reopen retained bytes."""
import struct

from nvs_records_cpu import RecordCpu, RecordPartition, FIND_ITEM
from nvs_record_vectors import WRITTEN, ERASED, vectors
from reverse.factory_nvs import TABLE
from audit_factory_xrefs import sha
from runtime_call_instructions import HEAP


def attempt(variant, definition, reader, crc, partition, wanted, state=0xfffffffe):
    """Discard volatile Page/cache state between attempts while retaining the sector itself."""
    cpu = RecordCpu(variant, definition, reader, crc); page = HEAP+128
    initial = bytearray(b'\xa5'*84)
    for offset, value in ((8, 8192), (12, state), (16, 0), (56, 0xffffffff),
                          (60, 0xffffffff), (80, HEAP+512)):
        struct.pack_into('<I', initial, offset, value)
    initial[20] = 254; initial[64:80] = b'\0'*16
    cpu.cpu.mem_write(page, bytes(initial)); partition.attach(cpu); cpu.reg(10, page)
    status = cpu.invoke(TABLE)
    fields = dict(state=cpu.word(page+12), used=int.from_bytes(cpu.cpu.mem_read(page+64, 2), 'little'),
                  erased=int.from_bytes(cpu.cpu.mem_read(page+66, 2), 'little'))
    operations = list(partition.operations)
    lookup = []
    if status == 0:
        for expected in wanted:
            namespace, key, chunk, value = expected[:4]
            datatype = expected[4] if len(expected) > 4 else 255
            index, out, key_at = HEAP+1024, HEAP+1088, HEAP+1152
            cpu.word(index, 0); cpu.cpu.mem_write(out, b'\xa5'*32)
            cpu.cpu.mem_write(key_at, key.ljust(16, b'\0'))
            for register, argument in enumerate((page, namespace, datatype, key_at, index, out, chunk, 255), 10):
                cpu.reg(register, argument)
            found = cpu.invoke(FIND_ITEM)
            observed = int.from_bytes(cpu.cpu.mem_read(out+24, 8), 'little') if found == 0 else None
            lookup.append(dict(key=key.decode(), chunk=chunk, status=found, value=observed,
                               expected_value=value))
    bitmap = [(partition.bytes[32+i//4] >> (i % 4*2)) & 3 for i in range(126)]
    return dict(status=status, fields=fields, bitmap=bitmap,
                counters_correct=(fields['used'], fields['erased']) == (bitmap.count(WRITTEN), bitmap.count(ERASED)),
                keys_correct=all(r['status'] == 0 and r['value'] == r['expected_value'] for r in lookup),
                lookups=lookup, operations=operations, media_sha256=sha(partition.bytes))


def media_check(partition, operations):
    """Reconstruct only actually transferred program bytes independently of fixture mutation."""
    expected = bytearray(partition.initial)
    for operation in operations:
        if operation['kind'] != 'write_raw':
            continue
        raw = bytes.fromhex(operation['data']); offset = operation['offset']
        for i in range(operation['transferred']):
            expected[offset+i] &= raw[i]
    assert partition.bytes == expected, 'Failed writes lost their physical prefix'


def run(variant, definition, reader, crc, require_errors=False, require_retention=False):
    """Fail each observed recovery I/O ordinal, then retry with a fresh real Page instance."""
    selected = {'duplicate-value', 'different-type-replacement', 'illegal-slot', 'bad-header-crc',
                'variable-erased-child', 'variable-illegal-child', 'variable-partial-empty-child',
                'hash24-collision', 'published-index-before-new-generation'}
    results = []; hidden = []
    for case in (row for row in vectors() if row['name'] in selected):
        baseline_partition = RecordPartition(case)
        baseline = attempt(variant, definition, reader, crc, baseline_partition, case['wanted'])
        assert baseline['status'] == 0
        for ordinal in range(1, len(baseline['operations'])+1):
            for partial in (False, True):
                partition = RecordPartition(case); partition.fail_at = ordinal; partition.partial = partial
                failed = attempt(variant, definition, reader, crc, partition, ())
                assert any(op['failed'] for op in failed['operations'])
                media_check(partition, failed['operations'])
                surfaced = failed['status'] == 0x104 and failed['fields']['state'] == 0
                if not surfaced:
                    hidden.append(dict(name=case['name'], ordinal=ordinal, partial=partial,
                                       status=failed['status'], state=failed['fields']['state'],
                                       operation=failed['operations'][ordinal-1]['kind']))
                if require_errors:
                    assert surfaced, (variant, case['name'], ordinal, partial, failed)
                    assert len(failed['operations']) == ordinal, 'Recovery continued after an I/O error'
                retained = bytes(partition.bytes)
                partition.fail_at = 0; partition.operations = []
                reopened = attempt(variant, definition, reader, crc, partition, case['wanted'])
                assert reopened['status'] == 0 and reopened['fields']['state'] == 0xfffffffe
                if require_retention:
                    assert reopened['counters_correct'] and reopened['keys_correct'], (case['name'], reopened)
                # A second clean open must be stable, even after a torn program.
                after_retry = bytes(partition.bytes); partition.operations = []
                stable = attempt(variant, definition, reader, crc, partition, case['wanted'])
                assert stable['status'] == 0 and bytes(partition.bytes) == after_retry
                assert not any(op['kind'] == 'write_raw' for op in stable['operations'])
                results.append(dict(name=case['name'], ordinal=ordinal, partial=partial, failed=failed,
                                    retained_before_retry_sha256=sha(retained), reopened=reopened, stable=stable))
    return dict(passed=True, variant=variant, cases=len(results), hidden_errors=hidden,
                error_contract_passed=not hidden, results=results, physical_hardware_tested=False,
                full_vm_power_fault_proved=False)
