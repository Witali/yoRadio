"""Execute factory time/cache/retry instructions and compiled native sync validity.

Calendar conversion and both notification handlers are actual RV32 code.
Only factory time(), SNTP restart and logging SDK boundaries are adapted.
This gate does not substitute for the separate real UDP/SNTP QEMU test.
"""
import argparse
import datetime as dt
import json
from pathlib import Path
import struct
from machine_oracle import ROOT, SCRATCH, REGS
from control_oracle import verify_inputs
from timezone_oracle import TimeMachine


class FactoryTimeState(TimeMachine):
    """Run the literal update/cache logic with synthetic, controlled wall-clock time."""
    def __init__(self):
        super().__init__('factory')
        self.epoch=0
        self.enabled=True
        self.restart_attempts=0
        self.adapt(0x420aa7e2,'sdk-time',self.read_time)
        self.adapt(0x42017ea0,'sdk-sntp-restart',self.restart)
        self.adapt(0x4038d3b4,'sdk-log-timestamp',lambda:0)
        self.adapt(0x4038d2a2,'sdk-log-write',lambda:0)
        self.set_zone('CST-8')
        self.cpu.mem_write(0x3fcc3ab9,b'\1')
        self.cpu.mem_write(0x3fcc3ab8,b'\0')
        self.cpu.mem_write(0x3fcc3ab4,bytes(4))
        self.cpu.mem_write(0x3fcbffc8,struct.pack('<I6B',2025,9,19,17,4,40,5))

    def read_time(self):
        """Supply the SDK's time_t through both the pointer and real RV32 return pair."""
        if self.reg(10):
            self.cpu.mem_write(self.reg(10),struct.pack('<q',self.epoch))
        self.cpu.reg_write(REGS[11],(self.epoch>>32)&0xffffffff)
        return self.epoch&0xffffffff

    def restart(self):
        """Report whether the SDK could restart its active client, recording each request."""
        self.restart_attempts+=1
        return int(self.enabled)

    def state(self):
        """Read only the identified synthetic cache/flags/counter, never owner settings."""
        return {'cached_date':list(struct.unpack('<I6B',self.cpu.mem_read(0x3fcbffc8,10))),
                'retry_counter':int.from_bytes(self.cpu.mem_read(0x3fcc3ab4,4),'little'),
                'initialized':self.cpu.mem_read(0x3fcc3ab9,1)[0],
                'sync_notification':self.cpu.mem_read(0x3fcc3ab8,1)[0],
                'restart_attempts':self.restart_attempts}


def native_time(machine,epoch):
    """Execute actual validity, country conversion and Newlib with a sentinel output."""
    pointer=SCRATCH+0x3100
    sentinel=struct.pack('<9i',*range(9))
    machine.cpu.mem_write(pointer,sentinel)
    machine.cpu.mem_write(SCRATCH+0x3200,b'CN\0')
    result=machine.call(machine.symbols['services_local_time'],SCRATCH+0x3200,
                        epoch&0xffffffff,(epoch>>32)&0xffffffff,pointer)
    data=bytes(machine.cpu.mem_read(pointer,36))
    return result,list(struct.unpack('<9i',data)),data==sentinel


def main():
    """Retain literal factory errors and require corrected native semantics explicitly."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    app=verify_inputs()
    factory,native=FactoryTimeState(),TimeMachine('native')
    literal=[]
    cases=[('initial-2025',1735726447,1,0,True),('same-second-year-jump',1767262447,1,0,True),
           ('synced-2024-below-year-threshold',1704104047,20,20,True),
           ('retry-after-21-updates',1704104047,1,0,True),
           ('stopped-client-retry-clears-initialized',1704104047,21,0,False)]
    for name,epoch,calls,counter,enabled in cases:
        factory.epoch,factory.enabled=epoch,enabled
        if name=='synced-2024-below-year-threshold':
            factory.call(0x420109de,SCRATCH+0x3000)
        for _ in range(calls):factory.call(0x42010b70)
        state=factory.state()
        passed=state['cached_date']==[2025,1,1,18,14,7,3] and state['retry_counter']==counter
        passed &= state['initialized']==int(enabled)
        passed &= state['sync_notification']==int(len(literal)>=2)
        passed &= state['restart_attempts']==[0,0,0,1,2][len(literal)]
        literal.append({'case':name,'epoch':epoch,'calls':calls,**state,'passed':bool(passed)})
    corrected=[]
    for epoch in (1704104047,1893456000):
        result,calendar,unchanged=native_time(native,epoch)
        corrected.append({'case':'before-notification','epoch':epoch,'passed':result==0 and unchanged})
    native.cpu.mem_write(SCRATCH+0x3000,struct.pack('<qi',1704104047,0))
    native.call(native.symbols['time_sync_notify'],SCRATCH+0x3000)
    for epoch in (1704104047,1735726447,1767262447,1704104047,0,2147483648):
        result,calendar,_=native_time(native,epoch)
        local=dt.datetime(1970,1,1,tzinfo=dt.timezone.utc)+dt.timedelta(seconds=epoch+8*3600)
        expected=[local.second,local.minute,local.hour,local.day,local.month-1,local.year-1900,
                  (local.weekday()+1)%7,local.timetuple().tm_yday-1,0]
        corrected.append({'case':'after-notification','epoch':epoch,'calendar':calendar,
                          'passed':result==1 and calendar==expected})
    manifest=json.loads((ROOT/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json').read_text(encoding='utf-8-sig'))
    report={'passed':all(r['passed'] for r in literal+corrected),'factory_cases':literal,
            'native_cases':corrected,'app_sha256':app,'source_sha256':manifest['source_sha256'],
            'factory_elf_sha256':factory.source_sha,'native_elf_sha256':native.source_sha,
            'adapters':{'factory':factory.executed_adapters,'native':native.executed_adapters},
            'approved_fixes':['validity-after-actual-sntp-notification','accept-pre-2025-synchronized-time',
                              'update-complete-calendar-at-unchanged-seconds'], 'scope':__doc__}
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Time state RV32:',len(literal),'literal factory;',len(corrected),'native checks; passed=',report['passed'])
    raise SystemExit(0 if report['passed'] else 1)


if __name__=='__main__':main()
