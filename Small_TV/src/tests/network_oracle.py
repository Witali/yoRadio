"""Execute original and rebuilt RV32 station events and the original active loop.

Synthetic DHCP leases and Wi-Fi events enter the actual compiled handlers. SDK
connect/notification/HTTP lifecycle and IPv4 formatting are boundaries; field
selection, cache, counters and native address formatting remain machine code.
The bounded original main-loop slice records dispatch, without substituting its
branches. This is not a radio, whole FreeRTOS scheduler or live QEMU link test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[3]
# Worktrees can share an existing SDK/oracle installation without copying it.
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo-root',type=Path,default=ROOT)
parser.add_argument('--dependency-root',type=Path)
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args()
dependencies=args.dependency_root or args.repo_root
sys.path.insert(0,str(dependencies/'.build/small-tv-parity/oracle-deps'))
from control_oracle import verify_inputs
from machine_oracle import Machine, RETURN, SCRATCH, UC_HOOK_CODE, rv


def digest(path):
    """Bind each executed image and adapter to its actual bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


class EventMachine(Machine):
    """Adapt SDK boundaries while retaining actual event/address instructions."""
    def __init__(self,variant):
        self.connects=0
        super().__init__(variant,dependency_root=dependencies,
            native_elf=args.repo_root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf')
        if self.is_factory:
            self.symbols['__global_pointer$']=0x3fcb49c0
            self.ip_base=int.from_bytes(self.cpu.mem_read(0x3c0f1848,4),'little')
            self.wifi_base=int.from_bytes(self.cpu.mem_read(0x3c0f1eb8,4),'little')
            self.adapt(0x4204551e,'sdk-wifi-connect',self.connect)
            self.adapt(0x40388e2e,'sdk-task-notification',lambda:0)
            self.adapt(0x4200c5ec,'sdk-http-start',lambda:0)
            self.adapt(0x4200c578,'sdk-http-stop',lambda:0)
            self.adapt(0x420365f2,'sdk-ip4-to-string',self.ip_string)
            self.cpu.mem_write(0x3fcb7b84,b'0.0.0.0\0')
            self.cpu.mem_write(0x3fcc3a78,bytes(4))
        else:
            self.ip_base=int.from_bytes(self.cpu.mem_read(self.symbols['IP_EVENT'],4),'little')
            self.wifi_base=int.from_bytes(self.cpu.mem_read(self.symbols['WIFI_EVENT'],4),'little')
            self.adapt(self.symbols['esp_wifi_connect'],'sdk-wifi-connect',self.connect)
            self.adapt(self.symbols['esp_netif_get_ip_info'],'sdk-later-netif-snapshot',self.info)
            self.cpu.mem_write(self.symbols['station_configured'],b'\1')

    def connect(self):
        """Count SDK reconnect requests without operating a physical radio."""
        self.connects+=1
        return 0

    def ip_string(self):
        """Format the SDK-pointed IPv4 address into its bounded destination."""
        raw=self.cpu.mem_read(self.reg(10),4)
        encoded='.'.join(str(octet) for octet in raw).encode()+b'\0'
        if len(encoded)>self.reg(12):
            raise ValueError('IPv4 formatter destination is too small')
        self.cpu.mem_write(self.reg(11),encoded)
        return self.reg(11)

    def info(self):
        """Model a later netif query that differs from the newer event snapshot."""
        self.cpu.mem_write(self.reg(11),bytes([10,0,2,15])+bytes(8))
        return 0

    def event(self,kind,last=15):
        """Pass the actual RV32 event ABI: netif pointer, IP/netmask/gateway, flag."""
        packet=struct.pack('<I',SCRATCH+0x900)+bytes([10,0,2,last])+bytes(12)
        self.cpu.mem_write(SCRATCH,packet)
        base,number=(self.ip_base,0) if kind=='got-ip' else (self.wifi_base,5)
        self.call(0x4200c602 if self.is_factory else self.symbols['wifi_event'],
                  0,base,number,SCRATCH)

    def address(self):
        """Read the original display string or execute the rebuilt bounded getter."""
        if self.is_factory:
            return self.string(0x3fcb7b84).decode('ascii')
        self.call(self.symbols['network_address'],SCRATCH+0x400,20)
        return self.string(SCRATCH+0x400).decode('ascii')


def event_trace(variant,recover):
    """Check a lease change and retry exhaustion, optionally resetting retries first."""
    machine=EventMachine(variant)
    machine.event('got-ip',15)
    first=machine.address()
    if recover:
        for _ in range(3): machine.event('disconnected')
    machine.event('got-ip',21)
    updated=machine.address()
    rows=[]
    for _ in range(5):
        machine.event('disconnected')
        rows.append({'address':machine.address(),'connect_calls':machine.connects})
    expected=[{'address':'10.0.2.21','connect_calls':min(i+1,4)+(3 if recover else 0)}
              for i in range(5)]
    return {'case':'reconnect-resets-retries' if recover else 'new-dhcp-lease',
            'first_lease':first,'new_lease':updated,'disconnections':rows,
            'passed':first=='10.0.2.15' and updated=='10.0.2.21' and rows==expected,
            'elf_sha256':machine.source_sha,'adapters':machine.executed_adapters}


def factory_dispatch(theme,state):
    """Execute the bounded original active loop for one theme and station state."""
    machine=EventMachine('factory')
    calls=[]
    targets={0x4200b738:'classic',0x4200bd8c:'simple',0x4200bc36:'photo',
             0x4200a5b0:'dial',0x42010864:'weather',0x42010b70:'local-time',
             0x4200d06e:'setup-ui',0x42010c4e:'setup-services'}
    def record(name):
        """Record an output/service boundary without selecting a branch for the guest."""
        calls.append(name)
        return 0
    for address,name in targets.items():
        machine.adapt(address,name,lambda name=name:record(name))
    def finish(cpu,address,size,context):
        """End this explicit slice at the unchanged loop's common continuation."""
        cpu.reg_write(rv.UC_RISCV_REG_PC,RETURN)
    machine.cpu.hook_add(UC_HOOK_CODE,finish,begin=0x42008fb2,end=0x42008fb2)
    for address,value in [(0x3fcc39eb,0),(0x3fcc39ea,0),(0x3fcc39e9,1),
                          (0x3fcc3a74,state),(0x3fcc39d7,1),(0x3fcc39f3,0),
                          (0x3fcc39e0,0),(0x3fcc39f2,0),(0x3fcc39f1,0)]:
        machine.cpu.mem_write(address,bytes([value]))
    machine.cpu.mem_write(0x3fcb7b9c+360,struct.pack('<I',theme))
    machine.cpu.mem_write(0x3fcbffc8+8,b'\0')
    machine.call(0x42008fdc,instruction_limit=1000)
    expected=[['classic','simple','photo','dial'][theme],'local-time']
    return {'theme':theme,'station_state':state,'calls':calls,'passed':calls==expected}


def main():
    """Require executable identity and all event/dispatch checks before reporting success."""
    app=verify_inputs(args.repo_root,dependencies)
    paths={
        'native_elf':args.repo_root/'.build/small-tv-esp32c2/small_tv_reconstructed.elf',
        'factory_elf':dependencies/'.build/small-tv-reverse/factory-analysis.elf',
        'rom_elf':dependencies/'.idf/tools-v6.1/tools/esp-rom-elfs/20260528/esp32c2_rev200_rom.elf',
        'test':Path(__file__),
        'machine_adapter':Path(__file__).with_name('machine_oracle.py'),
        'input_verifier':Path(__file__).with_name('control_oracle.py')}
    hashes={name:digest(path) for name,path in paths.items()}
    cases={variant:[event_trace(variant,recover) for recover in (False,True)]
           for variant in ('factory','native')}
    dispatch=[factory_dispatch(theme,state) for theme in range(4) for state in (0,1,2,5)]
    if hashes!={name:digest(path) for name,path in paths.items()} or app!=verify_inputs(args.repo_root,dependencies):
        raise ValueError('An executable or observer changed during the run')
    manifest=json.loads((args.repo_root/'firmware/development/small-tv-esp32c2-reconstructed/manifest.json')
                        .read_text(encoding='utf-8-sig'))
    passed=all(row['passed'] for group in cases.values() for row in group) and all(row['passed'] for row in dispatch)
    report={'passed':passed,'app_sha256':app,'source_sha256':manifest['source_sha256'],
            'native_elf_sha256':hashes['native_elf'],'factory_elf_sha256':hashes['factory_elf'],
            'input_hashes':hashes,'event_cases':cases,'factory_dispatch':dispatch,'scope':__doc__}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Network RV32: 4 event traces, 16 factory dispatch states; passed=',passed)
    raise SystemExit(0 if passed else 1)


if __name__=='__main__':
    main()
