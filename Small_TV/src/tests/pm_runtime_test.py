"""Check factory timer predicates and bounded typed PM metadata independently."""
import argparse
import json
from pathlib import Path
import sys

from unicorn import Uc,UC_ARCH_RISCV,UC_MODE_RISCV32,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn import riscv_const as rv

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_factory_xrefs import sha
from reverse.pm_runtime_layout import qualify
from pm_runtime_metadata import decode

SOURCES=('tools/reverse/pm_runtime_layout.py','tools/reverse/timer_pm_lifecycle.py',
         'tools/reverse/timer_keep_alive.py','tools/reverse/timer_event11_match.py',
         'tools/reverse/rv32_link_match.py','tools/reverse/elf_archive.py','tools/audit_factory_xrefs.py',
         'tests/pm_runtime_test.py','tests/pm_runtime_metadata.py')


def predicates(layout):
    """Execute both complete factory leaf bodies with only disposable scalar data."""
    cpu=Uc(UC_ARCH_RISCV,UC_MODE_RISCV32);cpu.mem_map(0x40384000,4096)
    cpu.mem_map(0x30000,4096);cpu.mem_map(0x60000,4096)
    reads=[]
    def read(machine,access,address,size,value,_):
        """Require precisely the metadata word reads encoded by the leaf functions."""
        if not 0x30000<=address<address+size<=0x30014:raise ValueError('Unexpected predicate read')
        reads.append([address-0x30000,size])
    def write(machine,access,address,size,value,_):
        """Neither predicate may write state or use a call stack."""
        raise ValueError('Factory predicate unexpectedly writes memory')
    cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write)
    cases=[]
    for row in layout['factory_predicates']:
        code=bytes.fromhex(row['bytes_hex']);cpu.mem_write(row['start'],code)
        values=(0,1,0xffffffff,1<<32,(1<<64)-1) if row['name']=='alarm_nonzero' else (0,0x12121212,0xffffffff)
        for value in values:
            raw=bytearray(20)
            if row['name']=='alarm_nonzero':raw[:8]=value.to_bytes(8,'little');expected=int(bool(value));expected_reads=[[0,4],[4,4]]
            else:raw[4:8]=value.to_bytes(4,'little');expected=int(value==0x12121212);expected_reads=[[4,4]]
            cpu.mem_write(0x30000,bytes(raw));reads.clear()
            for index in range(1,32):cpu.reg_write(rv.UC_RISCV_REG_X0+index,0x12340000+index)
            cpu.reg_write(rv.UC_RISCV_REG_A0,0x30000);cpu.reg_write(rv.UC_RISCV_REG_RA,0x60000)
            saved={i:cpu.reg_read(rv.UC_RISCV_REG_X0+i) for i in (2,3,4,8,9,*range(18,28))}
            cpu.emu_start(row['start'],0x60000,count=32)
            assert cpu.reg_read(rv.UC_RISCV_REG_PC)==0x60000 and cpu.reg_read(rv.UC_RISCV_REG_A0)==expected
            assert reads==expected_reads
            assert all(cpu.reg_read(rv.UC_RISCV_REG_X0+i)==v for i,v in saved.items())
            cases.append(dict(name=row['name'],value=value,return_value=expected,reads=list(reads)))
    return cases


def metadata(layout):
    """Test armed/unarmed state and pointer/length rejection without reading live RAM."""
    cases=[];rejected=[];uninitialized=[]
    for variant,l in layout['layouts'].items():
        for alarm in (0,1,1<<32,(1<<64)-1):
            pm,cfg=l['pm'],l['config'];handle=0x3fcb8000
            values={(l['connected'],1):l['connected_value'],(0x6004d000,4):123456,
                (l['rom_pm_pointer'],4):pm,(l['osi_pointer'],4):l['osi_table'],(pm+14,1):1,
                (pm+488,1):0,(pm+36,4):1,(cfg+52,1):0,(cfg+28,4):10000000,
                (pm+480,8):0xfffffff0,(pm+496,4):0x12121212,(pm+508,4):handle,(handle,8):alarm}
            def memory(address,size):
                """Expose exactly the known synthetic fields, with no fallback reader."""
                return values[address,size].to_bytes(size,'little')
            result=decode(memory,l);assert result['timer_armed']==bool(alarm) and result['backend_alarm_us']==alarm
            cases.append(dict(variant=variant,alarm=alarm,result=result))
            if alarm:continue
            for fault in ('unaligned','outside-ram','cross-boundary','bad-station-state','short-read'):
                changed=dict(values);bad=handle
                if fault=='unaligned':bad=handle+1
                elif fault=='outside-ram':bad=0x60000000
                elif fault=='cross-boundary':bad=0x3fcdfffc
                elif fault=='bad-station-state':changed[l['connected'],1]=l['connected_max']+1
                changed[pm+508,4]=bad
                def broken(address,size):
                    """Fail if an invalid pointer is followed instead of being rejected first."""
                    if fault=='short-read' and size==4:return b'\0'
                    return changed[address,size].to_bytes(size,'little')
                try:decode(broken,l)
                except ValueError:rejected.append(variant+':'+fault)
                else:raise AssertionError('Invalid PM metadata accepted')
            values[pm+496,4]=0;values[pm+508,4]=0xdeadbeef
            result=decode(memory,l);assert result['timer_armed'] is None and result['backend_alarm_us'] is None
            uninitialized.append(dict(variant=variant,kind='uninitialized',result=result))
            values[pm+496,4]=0x12121212;values[l['rom_pm_pointer'],4]=0
            result=decode(memory,l);assert result['timer_armed'] is None and not result['timer_owner_bound']
            uninitialized.append(dict(variant=variant,kind='rom-unbound',result=result))
    return dict(cases=cases,rejected_controls=rejected,uninitialized=uninitialized)


def run(factory,native,old_pp,new_pp,rom):
    """Bind immutable layouts before interpreting even a synthetic backend handle."""
    layout=qualify(factory,native,old_pp,new_pp,rom)
    return dict(passed=True,layout=layout,predicates=predicates(layout),metadata=metadata(layout),
                physical_hardware_tested=False,full_runtime_lifecycle_proved=False)


def main():
    """Save a fresh host-only qualification and negative-control report."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('factory','native','old-pp','new-pp','rom','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing PM runtime layout results')
    root=Path(__file__).resolve().parents[1]
    files=[args.factory,args.native,args.old_pp,args.new_pp,args.rom]+[root/name for name in SOURCES]
    pins={str(p.resolve()):sha(p.read_bytes()) for p in files}
    result=run(args.factory.read_bytes(),args.native.read_bytes(),args.old_pp,args.new_pp,args.rom.read_bytes())
    assert all(sha(Path(p).read_bytes())==digest for p,digest in pins.items())
    result.update(inputs_unchanged=True,inputs_sha256=pins)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,predicate_cases=len(result['predicates']),metadata_cases=len(result['metadata']['cases']),
                          rejected_controls=result['metadata']['rejected_controls'])))


if __name__=='__main__':main()
