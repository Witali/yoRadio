"""Execute the SDK table writer and actual ROM event-8 ingress in private RAM."""
from unicorn import Uc, UC_ARCH_RISCV, UC_MODE_RISCV32, UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_HOOK_MEM_INVALID
from unicorn import riscv_const as rv

WDEV_TABLE = 0x90000


def initialized_wdev(layout, read, initialized_data, beacon_pointer):
    """Run the real successful-allocation block for all preceding feature-bit choices."""
    rom = layout['rom_ingress']
    function = next(row for row in layout['linked_callers'] if row['name'] == 'wdev_funcs_init')
    start, end = (int(function[key], 0) for key in ('start', 'end'))
    first, stop = int(rom['init_begin'], 0), 0x60000
    guard, global_ = int(layout['guard']['start'], 0), int(rom['wdev_global'], 0)
    results, tables = [], []
    for flags in (0, 4, 8, 12):
        cpu = Uc(UC_ARCH_RISCV, UC_MODE_RISCV32)
        cpu.mem_map(start & ~4095, ((end + 4095) & ~4095) - (start & ~4095))
        cpu.mem_write(start, read(start, end-start))
        for address, size in ((0x3fca0000, 0x40000), (0x10000,4096), (0x30000,4096), (0x60000,4096), (0xb0000,4096), (WDEV_TABLE,4096)):
            cpu.mem_map(address, size)
        pages = set(range(0x3fca0000,0x3fce0000,4096))
        for address, data in initialized_data:
            for page in range(address & ~4095, (address+len(data)+4095) & ~4095,4096):
                if page not in pages:
                    cpu.mem_map(page,4096)
                    pages.add(page)
            cpu.mem_write(address,data)
        cpu.mem_write(0x3fcdfdd8, (0x30000).to_bytes(4, 'little'))
        # wdev_data_init precedes this slice and supplies a beacon callback
        # table. Its unrelated callbacks are opaque data stubs here: this
        # suffix copies their values, and may not execute them in the fixture.
        cpu.mem_write(beacon_pointer, (0xb0000).to_bytes(4,'little'))
        cpu.mem_write(0xb0000, (0x70000).to_bytes(4,'little') * 16)
        writes = []
        def instruction(machine, address, size, _):
            """A newly introduced external call must fail qualification instead of being guessed."""
            if not start <= address < end:
                raise ValueError('Unexpected call during wdev timer-slot initialization')
        def write(machine, access, address, size, value, _):
            """Retain the actual global and timer-slot writes made by SDK instructions."""
            if address in (global_, WDEV_TABLE + rom['wdev_timer_slot_offset']):
                writes.append({'address': hex(address), 'size': size, 'value': hex(value),
                               'pc': hex(machine.reg_read(rv.UC_RISCV_REG_PC))})
        cpu.hook_add(UC_HOOK_CODE, instruction)
        cpu.hook_add(UC_HOOK_MEM_WRITE, write)
        faults = []
        def invalid(machine, access, address, size, value, _):
            """An incomplete fixture must fail with its exact PC/address, never invent a read."""
            faults.append({'pc':hex(machine.reg_read(rv.UC_RISCV_REG_PC)),'address':hex(address),'access':access})
            return False
        cpu.hook_add(UC_HOOK_MEM_INVALID, invalid)
        cpu.reg_write(rv.UC_RISCV_REG_SP, 0x10800)
        # Resume after calloc, with the real function's saved return frame.
        cpu.mem_write(0x1080c, stop.to_bytes(4,'little'))
        cpu.reg_write(rv.UC_RISCV_REG_A0, WDEV_TABLE)
        cpu.reg_write(rv.UC_RISCV_REG_S0, flags)
        cpu.reg_write(rv.UC_RISCV_REG_GP, int(layout['gp'],0))
        try:
            cpu.emu_start(first, stop, count=3000)
        except Exception as error:
            raise ValueError('wdev fixture execution failed: ' + repr(faults) + ' PC=' + hex(cpu.reg_read(rv.UC_RISCV_REG_PC))) from error
        assert cpu.reg_read(rv.UC_RISCV_REG_PC) == stop
        assert cpu.reg_read(rv.UC_RISCV_REG_SP) == 0x10810
        assert cpu.reg_read(rv.UC_RISCV_REG_A0) == 0
        assert int.from_bytes(cpu.mem_read(global_,4),'little') == WDEV_TABLE
        assert int.from_bytes(cpu.mem_read(WDEV_TABLE + 356,4),'little') == guard
        assert len(writes) == 2 and writes[-1]['value'] == hex(guard)
        results.append({'feature_flags': flags, 'writes': writes, 'returned_successfully':True,
                        'beacon_callback_data_stubbed':True})
        tables.append(bytes(cpu.mem_read(WDEV_TABLE,1280)))
    return results, tables[0]


def verify_rom_path(layout, read, guarded_probe_class, initialized_data, beacon_pointer):
    """Feed all byte IDs through the exact ROM dispatch block and SDK-initialized pointer."""
    initializers, table_bytes = initialized_wdev(layout, read, initialized_data, beacon_pointer)
    rom = layout['rom_ingress']

    class RomProbe(guarded_probe_class):
        """Extend the same guard/vendor fixture with the real 12-byte ROM caller."""
        def __init__(self):
            """Use the table actually written by the SDK block, not a fabricated guard pointer."""
            super().__init__(layout, read)
            self.rom_start, self.rom_end = int(rom['block_start'],0), int(rom['block_end'],0)
            self.wdev_global = int(rom['wdev_global'],0)
            self.map(self.rom_start, self.rom_end-self.rom_start)
            self.cpu.mem_write(self.rom_start, bytes.fromhex(rom['block_bytes']))
            self.map(WDEV_TABLE, len(table_bytes))
            self.cpu.mem_write(WDEV_TABLE, table_bytes)
            self.cpu.mem_write(self.wdev_global, WDEV_TABLE.to_bytes(4,'little'))

        def execute(self, cpu, address, size, context):
            """Allow the exact ROM caller in addition to the guard, vendor and declared stubs."""
            if self.rom_start <= address < self.rom_end:
                self.trace['instructions'] += 1
                return
            super().execute(cpu,address,size,context)

        def read(self, cpu, access, address, size, value, context):
            """Allow only the two ROM table reads beyond the base fixture's allowlist."""
            if (address,size) in ((self.wdev_global,4),(WDEV_TABLE + 356,4)):
                return
            super().read(cpu,access,address,size,value,context)

        def call_rom(self, event):
            """Model the parent event-8 stack context and let the actual ROM load its argument."""
            self.trace = {'instructions':0,'callbacks':[],'frees':[],'logs':0,'table_reads':[],'out_of_table_reads':[]}
            self.callback_result = 1
            self.cpu.mem_write(self.table, self.table_bytes)
            message = bytes([event,0,0,0]) + bytes.fromhex('78563412')
            self.cpu.mem_write(self.MESSAGE,message)
            for index in range(1,32):
                self.cpu.reg_write(rv.UC_RISCV_REG_X0 + index,0)
            stack = self.STACK + 2048
            self.cpu.reg_write(rv.UC_RISCV_REG_SP,stack)
            self.cpu.reg_write(rv.UC_RISCV_REG_S0,0x3fce0000)
            self.cpu.reg_write(rv.UC_RISCV_REG_GP,int(layout['gp'],0))
            self.cpu.mem_write(stack+8,(8).to_bytes(4,'little') + self.MESSAGE.to_bytes(4,'little'))
            self.cpu.emu_start(self.rom_start,self.rom_end,count=2000)
            assert self.cpu.reg_read(rv.UC_RISCV_REG_PC) == self.rom_end
            assert self.cpu.reg_read(rv.UC_RISCV_REG_SP) == stack
            assert bytes(self.cpu.mem_read(self.MESSAGE,8)) == message
            self.trace['return'] = self.cpu.reg_read(rv.UC_RISCV_REG_A0)
            return self.trace

    probe, examples = RomProbe(), {}
    for event in range(256):
        row = probe.call_rom(event)
        valid = event < 14
        assert row['return'] == int(valid) and row['frees'] == [probe.MESSAGE]
        assert row.get('vendor_entries',0) == int(valid) and not row['out_of_table_reads']
        assert row['callbacks'] == ([{'id':event,'message':probe.MESSAGE}] if valid else [])
        if not valid:
            assert not row['table_reads']
        if event in (0,13,14,15,255):
            examples[str(event)] = row
    return {'passed':True,'sdk_initializer_feature_cases':initializers,'rom_event_byte_cases':256,
            'actual_sdk_slot_write_verified':True,'actual_rom_indirect_entry_verified':True,
            'guarded_out_of_table_reads':0,'examples':examples,
            'limitations':['Initialization is executed from a successful calloc return through the real function return; earlier external calls are excluded.',
                'The preceding beacon callback table is declared opaque stub data; its values are copied but its functions are never executed.',
                'The scheduler/queue/interrupt setup and transitive handler effects are not simulated by this fixture.']}
