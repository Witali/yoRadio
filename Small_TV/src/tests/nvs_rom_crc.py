"""Qualify and execute the C2 ROM CRC32 implementation and its immutable polynomial table."""
import binascii
import io

from elftools.elf.elffile import ELFFile
from unicorn import UC_MEM_READ, UC_HOOK_MEM_READ
from unicorn import riscv_const as rv
from audit_factory_xrefs import sha
from reverse.rv32_link_match import branch_target
from reverse.runtime_metadata import instructions
from runtime_call_instructions import Fixture, HEAP, END, PRESERVED

ROM_SHA = '289ce00e79c024d9efeb29a7fbc2d21853a1cbc383a2b9c2ece85c54fa829dd9'


def qualify(data):
    """Pin the official ROM image before accepting symbol extents or a lookup table."""
    if sha(data) != ROM_SHA: raise ValueError('Requalify ROM CRC image')
    elf = ELFFile(io.BytesIO(data)); symbols = list(elf.get_section_by_name('.symtab').iter_symbols())
    def symbol(name):
        """Reject absent or ambiguous ROM function/data symbols."""
        rows = [s for s in symbols if s.name == name]
        if len(rows) != 1: raise ValueError('Missing/ambiguous ROM CRC symbol')
        return rows[0]
    def read(address, size):
        """Read only one initialized ELF section, never synthesized BSS."""
        rows = [s for s in elf.iter_sections() if s['sh_type'] != 'SHT_NOBITS' and
                s['sh_addr'] <= address < address+size <= s['sh_addr']+s['sh_size']]
        if len(rows) != 1: raise ValueError('CRC range outside initialized ROM section')
        section = rows[0]; offset = address-section['sh_addr']; return section.data()[offset:offset+size]
    body = symbol('crc32_le'); stub = symbol('__call_crc32_le'); table = symbol('crc32_le_table')
    if (body['st_value'], body['st_size'], stub['st_value'], table['st_value'], table['st_size']) != \
            (0x4005d188, 156, 0x400007fc, 0x3ff47a34, 1024): raise ValueError('ROM CRC layout changed')
    jump = read(stub['st_value'], 4)
    if branch_target(jump, stub['st_value']) != body['st_value']: raise ValueError('ROM CRC stub target changed')
    expected = bytearray()
    for index in range(256):
        value = index
        for _ in range(8): value = (value >> 1) ^ (0xedb88320 if value & 1 else 0)
        expected.extend(value.to_bytes(4, 'little'))
    actual = read(table['st_value'], 1024)
    if actual != expected: raise ValueError('ROM CRC table does not implement reflected CRC32')
    functions = [dict(name='crc32_entry', start=hex(stub['st_value']), linked_bytes=4, code_sha256=sha(jump), bytes=jump.hex()),
                 dict(name='crc32_le', start=hex(body['st_value']), linked_bytes=156,
                      code_sha256=sha(read(body['st_value'], 156)), bytes=read(body['st_value'], 156).hex())]
    return dict(passed=True, rom_sha256=sha(data), functions=functions,
                table=dict(address=table['st_value'], bytes=actual.hex(), sha256=sha(actual)))


class CrcFixture(Fixture):
    """Extend the existing private CPU fixture with exactly one read-only ROM lookup table."""
    def __init__(self, variant, report, reader, crc):
        """Map exact ROM code and data; none of the CRC algorithm is replaced by a callback."""
        self.crc = crc; self.crc_table_indices = set()
        combined = dict(functions=report['functions']+crc['functions'], allocator_veneer=report.get('allocator_veneer'))
        rom = {int(r['start'], 0): bytes.fromhex(r['bytes']) for r in crc['functions']}
        def code(address, length, execute=False):
            """Route only qualified ROM function extents to archived code bytes."""
            if address in rom:
                if len(rom[address]) != length: raise ValueError('Incomplete CRC code extent')
                return rom[address]
            return reader(address, length, execute)
        super().__init__(variant, combined, code)
        table = crc['table']; raw = bytes.fromhex(table['bytes']); assert sha(raw) == table['sha256']
        self.map(table['address'], len(raw)); self.cpu.mem_write(table['address'], raw)

    def memory(self, cpu, access, address, size, value, data):
        """Permit table reads only; all other accesses retain the original stack/heap guard."""
        first = self.crc['table']['address']
        if first <= address < address+size <= first+1024:
            assert access == UC_MEM_READ and size == 4 and (address-first) % 4 == 0, 'Invalid access to ROM CRC table'
            self.crc_table_indices.add((address-first)//4); return
        super().memory(cpu, access, address, size, value, data)


def vectors(crc):
    """Cross-check real ROM arithmetic against standard CRC32 at each alignment and loop boundary."""
    results = []; visited = set(); table_indices = set()
    for seed in (0, 0xffffffff, 0x12345678):
        for alignment in range(4):
            for size in (0, 1, 2, 3, 4, 7, 8, 9, 15, 16, 31, 32, 127, 128, 256, 511):
                data = bytes((index*73+size*11) & 255 for index in range(size)); pointer = HEAP+1536+alignment
                f = CrcFixture('rom-crc', dict(functions=[], allocator_veneer=None), None, crc)
                f.cpu.mem_write(pointer, data); f.reg(10, seed); f.reg(11, pointer); f.reg(12, size)
                def read(cpu, access, address, length, value, context):
                    """Check that optimized ROM loads never read outside the requested input bytes."""
                    if HEAP <= address < HEAP+4096: assert pointer <= address < address+length <= pointer+size
                f.cpu.hook_add(UC_HOOK_MEM_READ, read)
                f.cpu.emu_start(0x400007fc, END, count=32768)
                assert f.cpu.reg_read(rv.UC_RISCV_REG_PC) == END
                for register in PRESERVED: assert f.reg(register) == f.initial[register]
                expected = binascii.crc32(data, seed) & 0xffffffff; assert f.reg(10) == expected
                results.append(dict(seed=seed, alignment=alignment, size=size, value=f.reg(10)))
                visited.update(f.visited); table_indices.update(f.crc_table_indices)
    starts = {int(row['pc'], 0) for function in crc['functions']
              for row in instructions(bytes.fromhex(function['bytes']), int(function['start'], 0))}
    assert starts <= visited, [hex(pc) for pc in sorted(starts-visited)]
    assert table_indices == set(range(256))
    return dict(passed=True, cases=len(results), results=results, instruction_starts=len(starts), visited=sorted(starts & visited),
                table_indices=sorted(table_indices), bounded_input_reads=True)
