"""Cross-check typed counters using exact ROM instructions in an isolated CPU.

Only a bounded allocator header is copied from a paused VM. Guest registers,
RAM and instructions are never modified; no allocator payload is inspected.
"""
import hashlib


class RomHeapCounters:
    """Execute the two real ROM getters, without replacing their memory accesses."""
    def __init__(self, path):
        from elftools.elf.elffile import ELFFile
        from unicorn import Uc, UC_ARCH_RISCV, UC_MODE_RISCV32
        from unicorn import riscv_const as rv
        self.cpu, self.rv, self.checks = Uc(UC_ARCH_RISCV, UC_MODE_RISCV32), rv, 0
        self.sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        self.functions = {}
        mapped = set()
        with path.open('rb') as stream:
            elf = ELFFile(stream)
            for symbol in elf.get_section_by_name('.symtab').iter_symbols():
                if symbol.name not in ('multi_heap_free_size_impl', 'multi_heap_minimum_free_size_impl'):
                    continue
                address, size = symbol['st_value'], symbol['st_size']
                if not 0 < size <= 64 or address // 4096 != (address + size - 1) // 4096:
                    raise ValueError('Unexpected bounded ROM heap getter')
                for segment in elf.iter_segments():
                    offset = address - segment['p_vaddr']
                    if segment['p_type'] == 'PT_LOAD' and 0 <= offset and offset + size <= segment['p_filesz']:
                        page = address & ~4095
                        if page not in mapped:
                            self.cpu.mem_map(page, 4096)
                            mapped.add(page)
                        self.cpu.mem_write(address, segment.data()[offset:offset + size])
                        self.functions[symbol.name] = address
                        break
        if len(self.functions) != 2:
            raise ValueError('Both ROM heap getters are required')
        self.cpu.mem_map(0x10000, 4096)
        self.cpu.mem_map(0x20000, 4096)
        self.cpu.reg_write(rv.UC_RISCV_REG_SP, 0x10800)

    def value(self, function, header, null=False):
        """Run one getter on a copied header; enforce its natural return and bound."""
        if not 0 < len(header) <= 256:
            raise ValueError('Expected only a bounded heap control header')
        self.cpu.mem_write(0x10000, header)
        self.cpu.reg_write(self.rv.UC_RISCV_REG_A0, 0 if null else 0x10000)
        self.cpu.reg_write(self.rv.UC_RISCV_REG_RA, 0x20000)
        self.cpu.emu_start(self.functions[function], 0x20000, count=32)
        if self.cpu.reg_read(self.rv.UC_RISCV_REG_PC) != 0x20000:
            raise ValueError('ROM getter did not return within its instruction bound')
        return self.cpu.reg_read(self.rv.UC_RISCV_REG_A0)

    def validate(self, header, free, minimum):
        """Compare both independently executed getters with the DWARF decoder."""
        if (self.value('multi_heap_free_size_impl', header) != free or
                self.value('multi_heap_minimum_free_size_impl', header) != minimum):
            raise ValueError('DWARF heap counters disagree with exact ROM getters')
        self.checks += 2
