"""Test literal factory dispatch/teardown and the retained native reconnect callback."""
import argparse
import json
from pathlib import Path
import sys

from unicorn import Uc, UC_ARCH_RISCV, UC_MODE_RISCV32, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn import riscv_const as rv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import Image, sha
from reverse.event_delivery_layout import qualify
from reverse.rv32_link_match import size_at
from event_delivery_metadata import decode
from machine_oracle import Machine, SCRATCH

SOURCES = ('tools/reverse/event_delivery_layout.py', 'tests/event_delivery_metadata.py',
           'tests/event_lifetime_test.py', 'tests/machine_oracle.py', 'tools/audit_factory_xrefs.py',
           'tools/reverse/rv32_link_match.py', 'tools/reverse/timer_event11_match.py', 'tools/reverse/elf_archive.py')


def registers(cpu, values):
    """Initialize explicit private RV32 registers without modifying any real guest."""
    for index in range(1, 32): cpu.reg_write(rv.UC_RISCV_REG_X0+index, 0x12340000+index)
    for index, value in values.items(): cpu.reg_write(rv.UC_RISCV_REG_X0+index, value)


def dispatch(layout):
    """Execute the entire 50-byte handler helper; substitute only its external callback."""
    spec = layout['code']['handler_execute']; start = spec['start']; code = bytes.fromhex(spec['bytes_hex'])
    cpu = Uc(UC_ARCH_RISCV, UC_MODE_RISCV32)
    for address, size in ((0x420ae000, 4096), (0x30000, 4096), (0x60000, 8192), (0x70000, 8192)):
        cpu.mem_map(address, size)
    cpu.mem_write(start, code); cpu.mem_write(0x60000, bytes.fromhex('8280'))
    observed = []; visited = set()
    def execute(machine, pc, size, _):
        """Record exact callback arguments, leaving helper decisions as original instructions."""
        if start <= pc < start+len(code): visited.add(pc)
        elif pc == 0x60000:
            observed.append([machine.reg_read(rv.UC_RISCV_REG_A0+i) for i in range(4)])
            ret = machine.reg_read(rv.UC_RISCV_REG_RA)
            for index in (5, 6, 7, *range(10, 18), 28, 29, 30, 31):
                machine.reg_write(rv.UC_RISCV_REG_X0+index, 0x98760000+index)
            machine.reg_write(rv.UC_RISCV_REG_PC, ret)
        else: raise ValueError('Unexpected handler instruction')
    def read(machine, access, address, size, value, _):
        """Reject payload reads; only context, post header and the private RA save are valid."""
        if not any(lo <= address < address+size <= hi for lo, hi in
                   ((0x30000,0x30004), (0x30020,0x30028), (0x30080,0x30090), (0x70ff0,0x71000))):
            raise ValueError('Handler read outside qualified metadata')
    def write(machine, access, address, size, value, _):
        """Only the helper's private stack save may be written during literal execution."""
        if not 0x70ff0 <= address < address+size <= 0x71000: raise ValueError('Unexpected handler write')
    cpu.hook_add(UC_HOOK_CODE, execute); cpu.hook_add(UC_HOOK_MEM_READ, read); cpu.hook_add(UC_HOOK_MEM_WRITE, write)
    rows = []
    for allocated in (0, 1):
        for present in (0, 1):
            for base in (layout['factory']['wifi_base'], layout['factory']['ip_base']):
                for event in (0, 5, 0xffffffff):
                    cpu.mem_write(0x30000, (0x30020).to_bytes(4,'little'))
                    cpu.mem_write(0x30020, (0x60000).to_bytes(4,'little')+(0x30500).to_bytes(4,'little'))
                    post = bytes((allocated,present,0,0))+base.to_bytes(4,'little')+event.to_bytes(4,'little')+(0x30600).to_bytes(4,'little')
                    cpu.mem_write(0x30080, post); observed.clear()
                    registers(cpu, {1:0x61000, 2:0x71000, 10:0x300c0, 11:0x30000, 12:0x30080})
                    saved = {i:cpu.reg_read(rv.UC_RISCV_REG_X0+i) for i in (2,3,4,8,9,*range(18,28))}
                    cpu.emu_start(start, 0x61000, count=64)
                    expected = [0x30500, base, event, 0 if not present else 0x30600 if allocated else 0x3008c]
                    assert observed == [expected] and cpu.reg_read(rv.UC_RISCV_REG_PC) == 0x61000
                    assert all(cpu.reg_read(rv.UC_RISCV_REG_X0+i)==v for i,v in saved.items())
                    rows.append(dict(allocated=allocated,present=present,base=base,event=event,arguments=expected))
    expected_starts = set(); offset = 0
    while offset < len(code): expected_starts.add(start+offset); offset += size_at(code,offset)
    assert visited == expected_starts
    return dict(cases=rows, visited_instruction_starts=sorted(visited), complete_body_bytes=50)


def teardown(layout, image):
    """Execute the original startup tail with declared unregister/delete/fatal API boundaries."""
    start, end = 0x4200cd90, 0x4200ce20
    rows = []
    for first in (0, 0x101, 0x107):
        for second in (0, 0x102, 0x107):
            cpu = Uc(UC_ARCH_RISCV, UC_MODE_RISCV32)
            for address in (0x4200c000, 0x420ae000, 0x40387000, 0x40388000, 0x3fcc3000, 0x70000):
                cpu.mem_map(address, 4096)
            cpu.mem_write(start, image.read(start, end-start, True))
            for address in (0x420aeae0,0x40388f00,0x4038726a,0x4200cc5c):
                cpu.mem_write(address,bytes.fromhex('8280'))
            cpu.mem_write(0x3fcc3a7c, (0x31000).to_bytes(4,'little'))
            cpu.mem_write(0x3fcc39ea, b'\x7f'); calls = []; fatal = []
            registers(cpu, {2:0x71000, 8:layout['factory']['wifi_base'], 9:layout['factory']['ip_base']})
            def execute(machine, pc, size, _):
                """SDK results are explicit inputs; no real event registry is being simulated."""
                if pc == 0x420aeae0:
                    calls.append(['unregister',*[machine.reg_read(rv.UC_RISCV_REG_A0+i) for i in range(3)]])
                    result = first if len(calls)==1 else second
                    machine.reg_write(rv.UC_RISCV_REG_A0, result)
                    machine.reg_write(rv.UC_RISCV_REG_PC, machine.reg_read(rv.UC_RISCV_REG_RA))
                elif pc == 0x40388f00:
                    calls.append(['delete-startup-group', machine.reg_read(rv.UC_RISCV_REG_A0)])
                    machine.reg_write(rv.UC_RISCV_REG_PC, machine.reg_read(rv.UC_RISCV_REG_RA))
                elif pc == 0x4038726a:
                    fatal.append(machine.reg_read(rv.UC_RISCV_REG_A0)); machine.emu_stop()
                elif pc == 0x4200cc5c: machine.emu_stop()
                elif not start <= pc < end: raise ValueError('Unexpected teardown boundary')
            cpu.hook_add(UC_HOOK_CODE, execute); cpu.emu_start(start, 0, count=128)
            expected = [['unregister',layout['factory']['ip_base'],0,0x4200c602]]
            if not first: expected.append(['unregister',layout['factory']['wifi_base'],0xffffffff,0x4200c602])
            error = first or second
            if not error: expected.append(['delete-startup-group',0x31000])
            assert calls == expected and fatal == ([error] if error else [])
            assert bytes(cpu.mem_read(0x3fcc3a74,1)) == b'\x02' and bytes(cpu.mem_read(0x3fcc39ea,1)) == b'\0'
            rows.append(dict(first_result=first,second_result=second,calls=calls,fatal=fatal))
    return rows


def metadata(layout):
    """Test queue geometry and bounded pointer rejection using synthetic numeric fields only."""
    l = layout['factory']; loop, queue, task, mutex = 0x3fcb8000, 0x3fcb8100, 0x3fcb8200, 0x3fcb8300
    values = {l['default_loop']:loop, l['current_task']:task, loop+4:queue, loop+8:task,
              loop+12:task, loop+16:mutex, queue+56:0, queue+60:32, queue+64:16}
    positive = []
    for count in (0,1,32):
        for running in (0,task):
            values[queue+56], values[loop+12] = count, running
            positive.append(decode(lambda address,size:values[address].to_bytes(size,'little'), l))
    rejected = []
    faults = {'null-loop':(l['default_loop'],0), 'unaligned-loop':(l['default_loop'],loop+1),
        'outside-loop':(l['default_loop'],0x60000000), 'crossing-loop':(l['default_loop'],0x3fcdfff0),
        'null-queue':(loop+4,0), 'unaligned-queue':(loop+4,queue+1), 'crossing-queue':(loop+4,0x3fcdfff0),
        'count':(queue+56,33), 'capacity':(queue+60,257), 'item-size':(queue+64,8),
        'null-task':(loop+8,0), 'current-task':(l['current_task'],task+1), 'mutex':(loop+16,0x60000000),
        'running-task':(loop+12,1)}
    values[queue+56] = 0
    for name, (address,value) in faults.items():
        changed = dict(values); changed[address] = value
        try: decode(lambda address,size:changed[address].to_bytes(size,'little'), l)
        except ValueError: rejected.append(name)
        else: raise AssertionError('Bad event metadata accepted: '+name)
    try: decode(lambda address,size:b'\0', l)
    except ValueError: rejected.append('short-read')
    else: raise AssertionError('Short event metadata accepted')
    return dict(cases=positive,rejected_controls=rejected)


def native_callback(layout, dependencies, native):
    """Run the actual native callback across losses, new leases and retry exhaustion."""
    machine = Machine('native', dependency_root=dependencies, native_elf=native)
    symbols = machine.symbols; calls = []; rows = []
    def read(name, size=1):
        """Inspect one qualified native callback state scalar in the private CPU."""
        return int.from_bytes(machine.cpu.mem_read(symbols[name],size),'little')
    def connect():
        """Record connectivity at the real SDK boundary, before any synthetic success."""
        calls.append(dict(connected=read('connected'), retries=read('station_retries',4))); return 0
    machine.adapt(symbols['esp_wifi_connect'], 'sdk-connect', connect)
    for name, value in (('station_configured',1),('connected',1),('scanning',0),('station_failed',0)):
        machine.cpu.mem_write(symbols[name],bytes([value]))
    machine.cpu.mem_write(symbols['station_retries'],bytes(4))
    wifi = int.from_bytes(machine.cpu.mem_read(symbols['WIFI_EVENT'],4),'little')
    ip = int.from_bytes(machine.cpu.mem_read(symbols['IP_EVENT'],4),'little')
    for label, base, event in [('loss',wifi,5),('lease',ip,0), *[('loss',wifi,5)]*5,('lease',ip,0),('loss',wifi,5)]:
        machine.cpu.mem_write(SCRATCH,bytes(4)+bytes((10,0,2,21))+bytes(12))
        machine.call(symbols['wifi_event'],0,base,event,SCRATCH,instruction_limit=1024)
        rows.append(dict(event=label, connected=read('connected'), retries=read('station_retries',4), failed=read('station_failed')))
    assert [r['connected'] for r in rows] == [0,1,0,0,0,0,0,1,0]
    assert [r['retries'] for r in rows] == [1,0,1,2,3,4,4,0,1]
    assert [r['failed'] for r in rows] == [0,0,0,0,0,0,1,0,0]
    assert len(calls)==6 and all(call['connected']==0 for call in calls)
    return dict(events=rows,connect_boundaries=calls,native_elf_sha256=machine.source_sha,
                sdk_event_registration_tested=False)


def run(factory, native, dependencies):
    """Keep callback algorithm tests distinct from real event registration and delivery."""
    layout = qualify(factory.read_bytes(), native.read_bytes())
    return dict(passed=True,layout=layout,dispatch=dispatch(layout),teardown=teardown(layout,Image(factory.read_bytes())),
                metadata=metadata(layout),native_callback=native_callback(layout,dependencies,native),
                full_startup_function_proved=False,whole_image_completeness_proved=False,physical_hardware_tested=False)


def main():
    """Write a new host-only instruction report with exact source/binary identities."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('factory','native','dependency-root','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists()
    root=Path(__file__).resolve().parents[1]
    files=[args.factory,args.native,args.dependency_root/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf']+[root/name for name in SOURCES]
    pins={str(p.resolve()):sha(p.read_bytes()) for p in files}
    report=run(args.factory,args.native,args.dependency_root)
    report.update(inputs_sha256=pins,inputs_unchanged=all(sha(Path(p).read_bytes())==v for p,v in pins.items()))
    assert report['inputs_unchanged'];args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(passed=True,dispatch_cases=len(report['dispatch']['cases']),teardown_cases=len(report['teardown']),
                         metadata_controls=len(report['metadata']['rejected_controls']),native_events=len(report['native_callback']['events']))))


if __name__=='__main__':main()
