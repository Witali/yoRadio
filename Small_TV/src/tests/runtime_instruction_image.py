"""Load exact C2 instructions into a private host CPU, never into a guest VM."""
import hashlib
from pathlib import Path


class InstructionImage:
    """Provide bounded ROM code and optional linked code for independent replay."""
    STACK = 0x10000
    CALLBACK = 0x20000
    RETURN = 0x20100
    ROM_SHA256 = '289ce00e79c024d9efeb29a7fbc2d21853a1cbc383a2b9c2ece85c54fa829dd9'

    def __init__(self, rom):
        """Include ROM initial data so host-only allocator fixtures use its real vtable."""
        from elftools.elf.elffile import ELFFile
        from unicorn import Uc, UC_ARCH_RISCV, UC_MODE_RISCV32, riscv_const
        self.cpu = Uc(UC_ARCH_RISCV, UC_MODE_RISCV32)
        self.rv, self.pages, self.functions = riscv_const, set(), {}
        self.rom_sha256 = hashlib.sha256(Path(rom).read_bytes()).hexdigest()
        if self.rom_sha256 != self.ROM_SHA256:
            raise ValueError('Unqualified C2 ROM identity')
        self._map(0x3FCA0000, 0x40000)
        self._map(0x4037C000, 0x44000)
        self._map(self.STACK, 4096)
        self._map(self.CALLBACK, 4096)
        # A genuine callback return in this private CPU; no guest code is patched.
        self.cpu.mem_write(self.CALLBACK, bytes.fromhex('1305100067800000'))
        with Path(rom).open('rb') as stream:
            elf = ELFFile(stream)
            self._check_elf(elf)
            for segment in elf.iter_segments():
                size, start = segment['p_filesz'], segment['p_vaddr']
                if segment['p_type'] != 'PT_LOAD' or not size:
                    continue
                if not any(lo <= start < start + size <= hi for lo, hi in (
                        (0x40000000, 0x40090000), (0x3FF00000, 0x3FF60000),
                        (0x3FCA0000, 0x3FCE0000))):
                    raise ValueError('ROM segment outside qualified C2 mappings')
                self._map(start, size)
                self.cpu.mem_write(start, segment.data())
            self.functions = {s.name: {'address': s['st_value'], 'size': s['st_size']}
                              for s in elf.get_section_by_name('.symtab').iter_symbols()
                              if s['st_value']}
        self.app_sha256 = None

    @staticmethod
    def _check_elf(elf):
        """Reject another architecture or endian before interpreting any address."""
        if elf.elfclass != 32 or not elf.little_endian or elf['e_machine'] != 'EM_RISCV':
            raise ValueError('Expected little-endian RV32 instructions')

    def _map(self, start, size):
        """Map each local Unicorn page once, including overlapping ELF segments."""
        if not 0 < size <= 0x100000 or not 0 < start < start + size <= 2**32:
            raise ValueError('Oversized instruction image mapping')
        for page in range(start & ~4095, (start + size + 4095) & ~4095, 4096):
            if page not in self.pages:
                self.cpu.mem_map(page, 4096)
                self.pages.add(page)

    def add_walk_patch(self, app):
        """Copy only the linked SDK walker; globals and allocator payloads stay absent."""
        from elftools.elf.elffile import ELFFile
        self.app_sha256 = hashlib.sha256(Path(app).read_bytes()).hexdigest()
        with Path(app).open('rb') as stream:
            elf = ELFFile(stream)
            self._check_elf(elf)
            symbols = [s for s in elf.get_section_by_name('.symtab').iter_symbols()
                       if s.name == 'tlsf_walk_pool_impl' and s['st_value']]
            if len(symbols) != 1 or not 0 < symbols[0]['st_size'] <= 1024:
                raise ValueError('Missing or ambiguous linked TLSF walker')
            start, size = symbols[0]['st_value'], symbols[0]['st_size']
            if not (0x42000000 <= start < start + size <= 0x42400000):
                raise ValueError('Linked walker outside C2 flash text')
            for segment in elf.iter_segments():
                offset = start - segment['p_vaddr']
                if segment['p_type'] == 'PT_LOAD' and 0 <= offset < offset + size <= segment['p_filesz']:
                    self._map(start, size)
                    self.cpu.mem_write(start, segment.data()[offset:offset + size])
                    self.functions['linked_tlsf_walk_pool'] = {'address': start, 'size': size}
                    return
        raise ValueError('Linked walker has no exact ELF bytes')

    def call(self, name, *args, limit=1000000):
        """Execute a bounded natural call/return exclusively inside this host image."""
        for register in range(1, 32):
            self.cpu.reg_write(self.rv.UC_RISCV_REG_X0 + register, 0)
        self.cpu.reg_write(self.rv.UC_RISCV_REG_SP, self.STACK + 2048)
        self.cpu.reg_write(self.rv.UC_RISCV_REG_RA, self.RETURN)
        for index, value in enumerate(args):
            if index >= 8 or not 0 <= value < 2**32:
                raise ValueError('Invalid RV32 call argument')
            self.cpu.reg_write(self.rv.UC_RISCV_REG_A0 + index, value)
        self.cpu.emu_start(self.functions[name]['address'], self.RETURN, count=limit)
        if (self.cpu.reg_read(self.rv.UC_RISCV_REG_PC) != self.RETURN or
                self.cpu.reg_read(self.rv.UC_RISCV_REG_SP) != self.STACK + 2048):
            raise ValueError('Instruction replay did not return within its bound')
        return self.cpu.reg_read(self.rv.UC_RISCV_REG_A0)
