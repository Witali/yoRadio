"""Execute complete factory/current NVS callers with explicit private partition/CRC boundaries."""
import argparse
import io
import json
from pathlib import Path
import struct
import sys
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from elftools.elf.elffile import ELFFile
from unicorn import riscv_const as rv
from audit_factory_xrefs import Image
from reverse.factory_nvs import PAGE, CRC, TABLE, FIND, HEADER
from reverse.nothrow_linkage import LinkedRuntime
from reverse.runtime_call_gaps import binding
from reverse.runtime_metadata import instructions
from nothrow_target import page_layout
from runtime_call_instructions import Fixture, HEAP, END, PRESERVED

INVALID = 0; UNINITIALIZED = 0xffffffff; CORRUPT = 0xfffffff0
STATES = (0xfffffffe, 0xfffffffc, 0xfffffff8, CORRUPT, INVALID, 0x12345678)


def layout(elf):
    """Read private offsets from resolved DWARF, independently in both compiled profiles."""
    linked = SimpleNamespace(elf=ELFFile(io.BytesIO(elf))); result = page_layout(linked)
    found = {}
    for cu in linked.elf.get_dwarf_info().iter_CUs():
        for die in cu.iter_DIEs():
            name = die.attributes.get('DW_AT_name'); size = die.attributes.get('DW_AT_byte_size')
            if die.tag != 'DW_TAG_class_type' or not name or name.value != b'Page' or not size: continue
            for child in die.iter_children():
                member = child.attributes.get('DW_AT_name')
                if child.tag == 'DW_TAG_member' and member and member.value in (b'mSeqNumber', b'mVersion'):
                    found[member.value.decode()] = child.attributes['DW_AT_data_member_location'].value
    assert found == {'mSeqNumber': 16, 'mVersion': 20}
    result['members'].update(found)
    assert result == dict(page_bytes=84, members=dict(mBaseAddress=8, mState=12, mUsedEntryCount=64,
                         mErasedEntryCount=66, mPartition=80, mSeqNumber=16, mVersion=20), read_raw_slot=12)
    return result


def cases():
    """Cover every caller branch, each erased-page block and all positions in its first block."""
    result = [dict(name='empty'), dict(name='null-partition', null_partition=True),
              dict(name='header-read-error', header_error=0x104), dict(name='allocator-returns-null', allocation_null=True)]
    for block in range(8): result.append(dict(name=f'block-read-error-{block}', read_error=block))
    positions = {(0, word) for word in range(128)} | {(block, word) for block in range(8) for word in (0, 63, 127)}
    for block, word in sorted(positions): result.append(dict(name=f'dirty-{block}-{word}', dirty=(block, word)))
    for state in STATES:
        for version in (0, 253, 254, 255):
            result.append(dict(name=f'header-{state:08x}-v{version}', state=state, version=version))
        result.append(dict(name=f'bad-crc-{state:08x}', state=state, bad_crc=True))
    for state in STATES[:3]: result.append(dict(name=f'entry-table-error-{state:08x}', state=state, table_error=0x107))
    for sector in (0, 0x100000, 0xffffffff): result.append(dict(name=f'sector-arithmetic-{sector:x}', sector=sector))
    return result


def setup(f, private, case, variant):
    """Construct private ABI inputs and boundary callbacks; never read a live flash or VM."""
    page, partition, vtable, block = HEAP+128, HEAP+512, HEAP+768, HEAP+1536
    initial = bytearray(b'\xa5'*84)
    def word(offset, value):
        """Set one declared constructor field without initializing unrelated private members."""
        struct.pack_into('<I', initial, offset, value)
    word(8, 0); word(12, INVALID); word(16, 0xffffffff); initial[20] = 254
    initial[64:68] = b'\0'*4; word(80, 0)
    f.cpu.mem_write(page, bytes(initial)); f.word(partition, vtable); f.word(vtable+12, END+1024)
    sector = case.get('sector', 2); base = (sector << 12) & 0xffffffff
    f.reg(10, page); f.reg(11, 0 if case.get('null_partition') else partition); f.reg(12, sector)
    state = case.get('state', UNINITIALIZED); version = case.get('version', 254)
    header = struct.pack('<IIB19sI', state, 0x89abcdef, version, b'\xff'*19, 0x13572468)
    reads = []; frees = []; allocations = []; table = []
    def read_raw(args):
        """Model actual partition reads and prove constructor initialization before the header read."""
        owner, offset, destination, size = args[:4]
        assert owner == partition and offset == base+(0 if not reads else (len(reads)-1)*512)
        assert size == (32 if not reads else 512)
        index = len(reads)-1; reads.append([offset, size])
        if size == 32:
            assert bytes(f.cpu.mem_read(destination+9, 19)) == b'\xff'*19
            if case.get('header_error'): return case['header_error']
            f.cpu.mem_write(destination, header)
        else:
            assert destination == block
            if case.get('read_error') == index: return 0x104
            f.cpu.mem_write(block, b'\xff'*512)
            if case.get('dirty', (-1, -1))[0] == index: f.word(block+case['dirty'][1]*4, 0xfffffffe)
        return 0
    def allocate(args):
        """Exercise the caller's standard nullable allocation contract, explicitly as a boundary."""
        assert args[0] == 512; allocations.append(512)
        return 0 if case.get('allocation_null') else block
    def release(args):
        """Require exactly one delete for the same successfully allocated buffer."""
        assert args[0] == block; frees.append(block); return 0
    def checksum(args):
        """Exercise the real CRC wrapper's seed/offset/length; ROM CRC arithmetic is an external boundary."""
        seed, pointer, length = args[:3]
        assert seed == 0xffffffff and length == 24 and bytes(f.cpu.mem_read(pointer, length)) == header[4:28]
        return 0x13572469 if case.get('bad_crc') else 0x13572468
    def load_table(args):
        """Observe delegation only; entry scanning and repair flash writes need their own tests."""
        assert args[0] == page; table.append(page); return case.get('table_error', 0)
    f.boundary('read_raw', END+1024, read_raw)
    f.boundary('array_new', private['allocation_boundary'], allocate)
    f.boundary('array_delete', private['delete_boundary'], release)
    f.boundary('crc_rom', private['crc_boundary'], checksum)
    f.boundary('entry_table', private['entry_table_boundary'], load_table)
    if variant == 'native':
        def fill(args):
            """Model only the constructor's existing ROM memset call."""
            destination, value, size = args[:3]; assert value == 255 and size == 19
            f.cpu.mem_write(destination, b'\xff'*size); return destination
        f.boundary('memset', private['memset_boundary'], fill)
    return page, initial, base, state, version, reads, frees, allocations, table


def caller_case(f, private, case, variant):
    """Check complete page bytes, return value, ownership and ABI after the real caller returns."""
    page, initial, base, state, version, reads, frees, allocations, table = setup(f, private, case, variant)
    f.cpu.emu_start(int(f.rows[PAGE]['start'], 0), END, count=32768)
    assert f.stopped is None and f.cpu.reg_read(rv.UC_RISCV_REG_PC) == END
    for register in PRESERVED: assert f.reg(register) == f.initial[register]
    expected = bytearray(initial); rc = 0
    def word(offset, value):
        """Apply the expected caller-only state transition to the complete private object."""
        struct.pack_into('<I', expected, offset, value)
    if case.get('null_partition'): rc = 0x102; assert not reads
    else:
        word(8, base); word(80, HEAP+512); expected[64:68] = b'\0'*4
        if case.get('header_error'): rc = case['header_error']; word(12, INVALID)
        elif state == UNINITIALIZED:
            word(12, UNINITIALIZED)
            if case.get('allocation_null'): rc = 0x101
            elif 'read_error' in case: rc = 0x104; word(12, INVALID)
            elif 'dirty' in case: word(12, CORRUPT)
            assert allocations == [512] and len(frees) == (0 if case.get('allocation_null') else 1)
            expected_blocks = (0 if case.get('allocation_null') else case.get('read_error', case.get('dirty', (7,))[0])+1)
            assert len(reads) == 1+expected_blocks
        elif case.get('bad_crc'): word(12, CORRUPT)
        else:
            word(12, state); word(16, 0x89abcdef)
            if version < 254: rc = 0x1110
            else:
                expected[20] = version
                if state in STATES[:3]: assert table == [page]; rc = case.get('table_error', 0)
                else: word(12, CORRUPT)
    assert bytes(f.cpu.mem_read(page, 84)) == bytes(expected), case
    assert f.reg(10) == rc, (case, hex(f.reg(10)), hex(rc))
    if state != UNINITIALIZED or case.get('null_partition') or case.get('header_error'): assert not allocations and not frees
    if not (state in STATES[:3] and not case.get('bad_crc') and version >= 254): assert not table
    events = [name for name, _ in f.events if name != 'memset']
    return dict(name=case['name'], result=rc, page_hex=bytes(expected).hex(), reads=reads,
                events=events, allocation_count=len(allocations), delete_count=len(frees), table_calls=len(table))


def run(factory, native, app, qualification, layout_elf):
    """Compare every selected caller case in both images, including explicit synthetic NULL allocation."""
    linked = LinkedRuntime(native, app); layouts = {'factory': layout(layout_elf), 'native': layout(native)}
    assert layouts['factory'] == layouts['native']
    readers = {'factory': Image(factory).read, 'native': linked.read}
    results = {}; coverage = {}
    for variant, private in qualification['variants'].items():
        definition = dict(functions=[r for r in private['functions'] if r['name'] != TABLE], allocator_veneer=None)
        rows = []; visited = set()
        for case in cases():
            f = Fixture(variant, definition, readers[variant]); rows.append(caller_case(f, private, case, variant)); visited.update(f.visited)
        page = next(r for r in private['functions'] if r['name'] == PAGE)
        starts = {int(i['pc'], 0) for i in instructions(readers[variant](int(page['start'], 0), page['linked_bytes'], True), int(page['start'], 0))}
        assert starts <= visited, (variant, [hex(pc) for pc in sorted(starts-visited)])
        results[variant] = rows; coverage[variant] = dict(caller_instruction_starts=len(starts), visited=sorted(starts & visited))
    assert results['factory'] == results['native']
    return dict(passed=True, cases_per_variant=len(cases()), total_cases=len(cases())*2, layout=layouts['factory'],
                results=results, coverage=coverage, allocator_return_null_is_synthetic_for_factory=True,
                allocator_runtime_executed=False, entry_table_algorithm_executed=False, crc_rom_executed=False,
                full_vm_fault_injection_proved=False, physical_hardware_tested=False)


def main():
    """Capture a new bounded CPU report from explicit immutable image and qualification paths."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('factory', 'native', 'app', 'qualification', 'layout', 'output'): parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('Preserve existing NVS target evidence')
    report = run(args.factory.read_bytes(), args.native.read_bytes(), args.app.read_bytes(),
                 json.loads(args.qualification.read_bytes()), args.layout.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf8', newline='\n')
    print(json.dumps({k: v for k, v in report.items() if k not in ('results', 'coverage', 'layout')}))


if __name__ == '__main__': main()
