"""Execute real partial-entry table repair and distinguish bitmap programming from data purge."""
import argparse
import json
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from unicorn import riscv_const as rv
from audit_factory_xrefs import Image, sha
from reverse.factory_nvs import TABLE
from reverse.nothrow_linkage import LinkedRuntime
from reverse.runtime_call_gaps import binding
from reverse.nvs_repair_linkage import RANGE
from runtime_call_instructions import Fixture, HEAP, END, PRESERVED
from nvs_partition_fixture import Partition


def execute(variant, definition, reader, partition, state=0xfffffffe):
    """Create fresh volatile Page fields while retaining the supplied physical partition bytes."""
    f = Fixture('nvs-repair-'+variant, definition, reader); page = HEAP+128
    blob = bytearray(b'\xa5'*84)
    for offset, value in ((8, 8192), (12, state), (16, 0), (56, 0xffffffff), (60, 0xffffffff), (80, HEAP+512)):
        struct.pack_into('<I', blob, offset, value)
    blob[20] = 254; blob[64:68] = b'\0'*4; f.cpu.mem_write(page, bytes(blob)); f.reg(10, page)
    partition.attach(f)
    if variant == 'native':
        row = next(r for r in definition['functions'] if r['name'] == RANGE)
        def clear(args):
            """Model only the purge buffer's ROM memset, keeping every repair/writer instruction real."""
            destination, value, size = args[:3]; assert value == 0 and size == 32
            f.cpu.mem_write(destination, b'\0'*size); return destination
        f.boundary('memset', binding(row, 'memset'), clear)
    try:
        f.cpu.emu_start(int(f.rows[TABLE]['start'], 0), END, count=131072)
    except Exception as error:
        raise AssertionError(f'{variant} repair stopped at {f.cpu.reg_read(rv.UC_RISCV_REG_PC):#x}; '
                             f'events={f.events}; operations={partition.operations}') from error
    assert f.stopped is None and f.cpu.reg_read(rv.UC_RISCV_REG_PC) == END
    for register in PRESERVED: assert f.reg(register) == f.initial[register]
    fields = dict(state=f.word(page+12), next_free=f.word(page+56), first_used=f.word(page+60),
                  used=int.from_bytes(f.cpu.mem_read(page+64, 2), 'little'),
                  erased=int.from_bytes(f.cpu.mem_read(page+66, 2), 'little'))
    actual = bytes(f.cpu.mem_read(page, 84)); protected = bytearray(actual)
    protected[12:16] = blob[12:16]; protected[24:68] = blob[24:68]
    assert protected == blob, 'Repair changed unrelated Page fields'
    return dict(result=f.reg(10), fields=fields, page_hex=actual.hex(),
                operations=partition.operations.copy(), physical_sha256=sha(bytes(partition.bytes))), f.visited


def run(factory, native, app, linkage):
    """Sweep every slot, then inject each observed partition error without rolling back media."""
    readers = {'factory': Image(factory).read, 'native': LinkedRuntime(native, app).read}
    results = {}; coverage = {}; fault_results = {}; baselines = {}
    for variant, definition in linkage['variants'].items():
        rows = []; visited = set()
        for slot in range(126):
            states = [0]*slot+[3]*(126-slot); partition = Partition(states, {slot})
            result, seen = execute(variant, definition, readers[variant], partition); visited.update(seen)
            assert result['result'] == 0 and result['fields'] == dict(state=0xfffffffe, next_free=slot+1,
                                                                    first_used=0xffffffff, used=0, erased=slot+1)
            expected = bytearray(partition.initial); expected[32+slot//4] &= ~(3 << ((slot % 4)*2))
            if variant == 'native': expected[64+32*slot:96+32*slot] = b'\0'*32
            assert partition.bytes == expected, (variant, slot)
            writes = [r for r in result['operations'] if r['kind'] == 'write_raw']
            assert [(r['offset'], r['bytes']) for r in writes] == [(32+4*(slot//16), 4)]+(
                [(64+32*slot, 32)] if variant == 'native' else [])
            assert all(not r['failed'] for r in result['operations'])
            partition.operations = []
            reopened, seen = execute(variant, definition, readers[variant], partition); visited.update(seen)
            assert reopened['result'] == 0 and reopened['fields']['next_free'] == (slot+1 if slot < 125 else 0xffffffff)
            assert reopened['fields']['used'] == 0 and reopened['fields']['erased'] == slot+1
            assert not any(r['kind'] == 'write_raw' for r in partition.operations) and partition.bytes == expected
            rows.append(dict(slot=slot, **result, reopened=reopened))
        results[variant] = rows; coverage[variant] = sorted(visited)
        checks = []
        for state in (0xfffffffe, 0xfffffffc, 0xfffffff8):
            for entry in (0, 3):
                partition = Partition([entry]*126, set())
                result, seen = execute(variant, definition, readers[variant], partition, state); visited.update(seen)
                assert result['result'] == 0 and result['fields']['state'] == state
                assert result['fields']['used'] == 0 and result['fields']['erased'] == (126 if entry == 0 else 0)
                assert result['fields']['next_free'] == (0 if state == 0xfffffffe and entry == 3 else 0xffffffff)
                assert result['fields']['first_used'] == 0xffffffff
                assert not any(r['kind'] == 'write_raw' for r in partition.operations)
                assert bytes(partition.bytes) == partition.initial
                checks.append(dict(state=state, entry=entry, **result))
        baselines[variant] = checks
        faults = []
        for slot in (0, 15, 16, 125):
            baseline = rows[slot]
            for ordinal in range(1, len(baseline['operations'])+1):
                for partial in (False, True):
                    partition = Partition([0]*slot+[3]*(126-slot), {slot}, ordinal, partial)
                    result, seen = execute(variant, definition, readers[variant], partition); visited.update(seen)
                    assert result['result'] == 0x104 and result['fields']['state'] == 0
                    assert len(partition.operations) == ordinal and partition.operations[-1]['failed']
                    failed_operation = partition.operations[-1]
                    completed = failed_operation['kind'] == 'read_raw' and failed_operation['offset'] == 64+32*(slot+1)
                    assert result['fields']['used'] == 0 and result['fields']['first_used'] == 0xffffffff
                    assert result['fields']['erased'] == (0 if ordinal == 1 else slot+int(completed))
                    assert result['fields']['next_free'] == (0xffffffff if ordinal == 1 else slot+int(completed))
                    # Reconstruct bytes from the initial sector and issued physical prefixes,
                    # independently of both the NVS state machine and fixture program method.
                    expected = bytearray(partition.initial)
                    for operation in partition.operations:
                        if operation['kind'] != 'write_raw': continue
                        data = bytes.fromhex(operation['data']); at = operation['offset']
                        for i in range(operation['transferred']): expected[at+i] &= data[i]
                    assert partition.bytes == expected
                    no_empty_before_retry = all(((partition.bytes[32+i//4] >> ((i % 4)*2)) & 3) != 3 for i in range(126))
                    partition.fail_at = 0; partition.operations = []
                    recovered, seen = execute(variant, definition, readers[variant], partition); visited.update(seen)
                    assert recovered['result'] == 0 and recovered['fields']['state'] == 0xfffffffe
                    assert recovered['fields']['used'] == 0 and recovered['fields']['erased'] == slot+1
                    # A fresh scan with no EMPTY entry retains INVALID_ENTRY; the original
                    # successful in-flight scan instead increments the last slot to126.
                    # Both describe exhausted capacity, but their actual RAM values differ.
                    expected_free = 0xffffffff if no_empty_before_retry else slot+1
                    assert recovered['fields']['next_free'] == expected_free, (variant, slot, ordinal, partial, recovered['fields'])
                    retained = sum(value != 0 for value in partition.bytes[64+32*slot:96+32*slot])
                    faults.append(dict(slot=slot, ordinal=ordinal, partial=partial, failed=result, recovered=recovered,
                                       retained_nonzero_payload_bytes_after_retry=retained))
        fault_results[variant] = faults; coverage[variant] = sorted(visited)
    return dict(passed=True, slots_per_variant=126, successful_cases=252, reopened_cases=252, baseline_cases=12,
                fault_cases=sum(len(r) for r in fault_results.values()), results=results, faults=fault_results,
                recovery_cases=sum(len(r) for r in fault_results.values()), baselines=baselines,
                visited=coverage, native_extra_program_bytes_per_repaired_slot=32, erase_operations=0,
                backend='private Partition API byte fixture; SPI timing/WIP not modeled',
                actual_slot_repair_instructions_executed=True, whole_entry_table_algorithm_proved=False,
                physical_hardware_tested=False, full_vm_power_fault_proved=False)


def main():
    """Capture bounded partial-record repair without modifying either flash image."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('factory', 'native', 'app', 'linkage', 'output'): parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('Preserve existing repair report')
    report = run(args.factory.read_bytes(), args.native.read_bytes(), args.app.read_bytes(), json.loads(args.linkage.read_bytes()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('results', 'faults', 'visited', 'baselines')}))


if __name__ == '__main__': main()
