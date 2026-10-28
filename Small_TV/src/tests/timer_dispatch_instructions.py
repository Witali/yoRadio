"""Execute exact dispatcher instructions against synthetic host-only messages."""
from unicorn import Uc, UC_ARCH_RISCV, UC_MODE_RISCV32, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn import riscv_const as rv


class DispatcherProbe:
    """Stub only transitive log/free/callback calls, never the dispatcher being checked."""
    STACK, OSI, FREE, MESSAGE, RETURN = 0x10000, 0x30000, 0x40000, 0x50000, 0x60000

    def __init__(self, layout, read):
        """Copy only qualified code, numeric table data and disposable fixture state."""
        self.layout = layout
        self.function = next(row for row in layout['functions'] if row['name'] == 'pp_timer_do_process')
        self.start, self.end = (int(self.function[key], 0) for key in ('start', 'end'))
        self.table = int(layout['table']['address'], 0)
        self.table_bytes = bytes.fromhex(layout['table']['bytes_hex'])
        bindings = {row['name']: row['address'] for row in self.function['symbol_bindings']}
        self.log, self.osi_global = bindings['wifi_log'], bindings['g_osi_funcs_p']
        self.callbacks = {int(row['target'], 0): row['id'] for row in layout['table']['entries']}
        self.cpu = Uc(UC_ARCH_RISCV, UC_MODE_RISCV32)
        self.pages, self.trace = set(), None
        for start, size in ((self.STACK, 4096), (self.OSI, 4096), (self.FREE, 4096),
                            (self.MESSAGE, 4096), (self.RETURN, 4096),
                            (self.table, 256 * 8), (self.osi_global, 4), (self.start, self.end-self.start)):
            self.map(start, size)
        self.cpu.mem_write(self.start, read(self.start, self.end-self.start))
        for address in (*self.callbacks, self.log, self.FREE):
            assert not self.start <= address < self.end
            self.map(address, 2)
            # These are declared external-call stubs in a private host CPU.
            self.cpu.mem_write(address, bytes.fromhex('8280'))
        self.cpu.mem_write(self.osi_global, self.OSI.to_bytes(4, 'little'))
        self.cpu.mem_write(self.OSI + 176, self.FREE.to_bytes(4, 'little'))
        self.cpu.hook_add(UC_HOOK_CODE, self.execute)
        self.cpu.hook_add(UC_HOOK_MEM_READ, self.read)
        self.cpu.hook_add(UC_HOOK_MEM_WRITE, self.write)

    def map(self, start, size):
        """Map each disposable page once; no firmware VM is contacted."""
        for page in range(start & ~4095, (start + size + 4095) & ~4095, 4096):
            if page not in self.pages:
                self.cpu.mem_map(page, 4096)
                self.pages.add(page)

    def execute(self, cpu, address, size, _):
        """Allow the exact selected body and record explicitly stubbed external calls."""
        if self.start <= address < self.end:
            self.trace['instructions'] += 1
            return
        argument = cpu.reg_read(rv.UC_RISCV_REG_A0)
        if address in self.callbacks:
            self.trace['callbacks'].append({'id': self.callbacks[address], 'message': argument})
            value = self.callback_result
        elif address == self.FREE:
            self.trace['frees'].append(argument)
            value = 0
        elif address == self.log:
            self.trace['logs'] += 1
            value = 0
        else:
            raise ValueError('Dispatcher left the qualified body/stub set: ' + hex(address))
        cpu.reg_write(rv.UC_RISCV_REG_A0, value)
        cpu.reg_write(rv.UC_RISCV_REG_PC, cpu.reg_read(rv.UC_RISCV_REG_RA))

    def read(self, cpu, access, address, size, value, _):
        """Record pre-bound table reads separately from allowed synthetic message/stack reads."""
        if self.table <= address < self.table + 256 * 8:
            row = {'address': hex(address), 'size': size, 'pc': hex(cpu.reg_read(rv.UC_RISCV_REG_PC))}
            self.trace['table_reads'].append(row)
            if address + size > self.table + len(self.table_bytes):
                self.trace['out_of_table_reads'].append(row)
            return
        if any(lo <= address < address + size <= hi for lo, hi in (
                (self.STACK, self.STACK + 4096), (self.MESSAGE, self.MESSAGE + 8),
                (self.osi_global, self.osi_global + 4), (self.OSI + 176, self.OSI + 180))):
            return
        raise ValueError('Unexpected dispatcher data read: ' + hex(address))

    def write(self, cpu, access, address, size, value, _):
        """The dispatcher itself may write only to its private call stack."""
        if not self.STACK <= address < address + size <= self.STACK + 4096:
            raise ValueError('Unexpected dispatcher write: ' + hex(address))

    def call(self, event=0, null=False, table=None, callback_result=1, poison_prefetch=False):
        """Measure literal instruction behavior; external callbacks are not being qualified."""
        assert type(event) is int and 0 <= event <= 255
        self.trace = {'instructions': 0, 'callbacks': [], 'frees': [], 'logs': 0,
                      'table_reads': [], 'out_of_table_reads': []}
        self.callback_result = callback_result
        raw = self.table_bytes if table is None else bytes(table)
        assert len(raw) == len(self.table_bytes)
        self.cpu.mem_write(self.table, bytes(256 * 8))
        self.cpu.mem_write(self.table, raw)
        if poison_prefetch and event >= 15:
            self.cpu.mem_write(self.table + event * 8, bytes([event]))
        message = bytes([event, 0, 0, 0]) + bytes.fromhex('78563412')
        self.cpu.mem_write(self.MESSAGE, message)
        for index in range(1, 32):
            self.cpu.reg_write(rv.UC_RISCV_REG_X0 + index, 0)
        self.cpu.reg_write(rv.UC_RISCV_REG_SP, self.STACK + 2048)
        self.cpu.reg_write(rv.UC_RISCV_REG_RA, self.RETURN)
        self.cpu.reg_write(rv.UC_RISCV_REG_GP, int(self.layout['gp'], 0))
        self.cpu.reg_write(rv.UC_RISCV_REG_A0, 0 if null else self.MESSAGE)
        self.cpu.emu_start(self.start, self.RETURN, count=2000)
        assert self.cpu.reg_read(rv.UC_RISCV_REG_PC) == self.RETURN
        assert self.cpu.reg_read(rv.UC_RISCV_REG_SP) == self.STACK + 2048
        assert bytes(self.cpu.mem_read(self.table, len(raw))) == raw
        assert bytes(self.cpu.mem_read(self.MESSAGE, len(message))) == message
        self.trace['return'] = self.cpu.reg_read(rv.UC_RISCV_REG_A0)
        return self.trace
