"""Execute literal panic, allocation and cleanup paths with explicit private SDK boundaries."""
from collections import Counter
import struct

from unicorn import Uc, UcError, UC_ARCH_RISCV, UC_MODE_RISCV32, UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn import riscv_const as rv

from audit_factory_xrefs import Image, sha
from reverse.runtime_call_gaps import Linked, binding

END = 0x10000
STACK = 0x3ff01000
HEAP = 0x3fe00000
REGISTERS = [getattr(rv,'UC_RISCV_REG_X'+str(i)) for i in range(32)]
CALLER = (1,5,6,7,*range(10,18),*range(28,32))
PRESERVED = (2,3,4,8,9,*range(18,28))


class Fixture:
    """Map only qualified code, synthetic stack/heap and named external boundaries."""
    def __init__(self, variant, report, reader):
        """Never connect this fixture to QEMU, a flash backing or a physical device."""
        self.cpu = Uc(UC_ARCH_RISCV,UC_MODE_RISCV32); self.pages = set()
        self.variant = variant; self.report = report; self.reader = reader
        self.rows = {r['name']:r for r in report['functions']}
        self.allowed = []; self.callbacks = {}; self.events = []; self.visited = set()
        self.stopped = None
        for row in self.rows.values():
            address = int(row['start'],0); code = reader(address,row['linked_bytes'],True)
            assert sha(code) == row['code_sha256']; self.code(address,code)
        if report['allocator_veneer']:
            row = report['allocator_veneer']; self.code(row['address'],bytes.fromhex(row['bytes_hex']))
        self.map(END,4096); self.cpu.mem_write(END,b'\x13\x00\x00\x00')
        self.map(STACK-4096,8192); self.cpu.mem_write(STACK-4096,b'\xa5'*8192)
        self.map(HEAP,4096)
        self.initial = {i:(i*0x1020304)&0xffffffff for i in range(1,32)}
        self.initial.update({1:END,2:STACK})
        for i,value in self.initial.items():self.reg(i,value)
        self.cpu.hook_add(UC_HOOK_CODE,self.step)
        self.cpu.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,self.memory)

    def map(self, address, length):
        """Avoid overlapping mappings when separate qualified bodies share a code page."""
        for page in range(address&~4095,(address+length+4095)&~4095,4096):
            if page not in self.pages:self.cpu.mem_map(page,4096);self.pages.add(page)

    def code(self, address, code):
        """Retain exact byte ranges; mapped alignment is not executable permission in the oracle."""
        self.map(address,len(code)); self.cpu.mem_write(address,code)
        self.allowed.append((address,address+len(code)))

    def reg(self, number, value=None):
        """Read/write a numeric guest register without relying on ABI aliases."""
        if value is not None:self.cpu.reg_write(REGISTERS[number],value)
        return self.cpu.reg_read(REGISTERS[number])

    def word(self, address, value=None):
        """Use only synthetic private words, never a live dump of application memory."""
        if value is not None:self.cpu.mem_write(address,struct.pack('<I',value))
        return int.from_bytes(self.cpu.mem_read(address,4),'little')

    def boundary(self, name, address, callback):
        """Register one explicit external call target; it may stop instead of returning."""
        assert address not in self.callbacks
        self.map(address,4)
        if not any(lo<=address<address+2<=hi for lo,hi in self.allowed):
            # Unicorn translates an instruction before delivering a code hook.
            # Keep unimplemented boundary entries valid; the hook owns semantics.
            self.cpu.mem_write(address,b'\x67\x80\x00\x00')
        self.callbacks[address]=(name,callback)

    def memory(self, cpu, access, address, size, value, data):
        """Reject all CPU data access outside the synthetic stack and heap."""
        assert (STACK-4096<=address<address+size<=STACK+4096 or HEAP<=address<address+size<=HEAP+4096),hex(address)

    def step(self, cpu, pc, size, data):
        """Check every executed PC and poison caller-saved registers after boundary returns."""
        if pc in self.callbacks:
            name,callback = self.callbacks[pc];args=tuple(self.reg(i) for i in range(10,18))
            self.events.append((name,args)); resume=self.reg(1); result=callback(args)
            if self.stopped is not None:cpu.emu_stop();return
            for i in CALLER:self.reg(i,0xa7000000+i)
            self.reg(10,result or 0);cpu.reg_write(rv.UC_RISCV_REG_PC,resume);return
        assert any(lo<=pc<pc+size<=hi for lo,hi in self.allowed),hex(pc)
        self.visited.add(pc)

    def stop(self, reason):
        """Observe a nonreturning boundary without inventing a successful return."""
        self.stopped=reason

    def run(self, name=None, pc=None, expected_stop=None):
        """Require bounded execution, exact termination and preserved ABI on ordinary return."""
        start=pc if pc is not None else int(self.rows[name]['start'],0)
        try:self.cpu.emu_start(start,END,count=4096)
        except UcError as error:
            raise AssertionError(f'Private runtime CPU failed at {self.cpu.reg_read(rv.UC_RISCV_REG_PC):#x}') from error
        assert self.stopped==expected_stop
        if expected_stop is None:
            assert self.cpu.reg_read(rv.UC_RISCV_REG_PC)==END
            for i in PRESERVED:assert self.reg(i)==self.initial[i],(i,self.reg(i),self.initial[i])


def execute(factory, native, qualified):
    """Compare literal bodies to explicit branch/frame/ownership expectations in both images."""
    images={'factory':Image(factory),'native':Linked(native)};cases=Counter();visited={}
    def fixture(variant):
        """Each case owns independent CPU/register/memory state."""
        return Fixture(variant,qualified['variants'][variant],images[variant].read)
    def record(family,f):
        """Retain coverage by actual instruction address, not by a successful case label."""
        cases[family]+=1;visited.setdefault(f.variant,set()).update(f.visited)
    for variant in images:
        # A returning panic boundary is synthetic: it exercises the assembly's
        # context-restore path and does not claim the SDK recovers from a panic.
        for cause in (*range(32),*(0x80000000|n for n in range(32)),0x7fffffff,0xffffffff):
            f=fixture(variant);c=f.cpu
            for register,value in ((rv.UC_RISCV_REG_MEPC,END),(rv.UC_RISCV_REG_MCAUSE,cause),
                                   (rv.UC_RISCV_REG_MSTATUS,0x1880),(rv.UC_RISCV_REG_MTVEC,0x40380000),
                                   (rv.UC_RISCV_REG_MTVAL,0x12345678)):
                c.reg_write(register,value)
            expected_csr={128:c.reg_read(rv.UC_RISCV_REG_MSTATUS),132:c.reg_read(rv.UC_RISCV_REG_MTVEC),
                          136:cause&31,140:c.reg_read(rv.UC_RISCV_REG_MTVAL),144:c.reg_read(rv.UC_RISCV_REG_MHARTID)}
            row=f.rows['_panic_handler'];selected='panicHandler' if cause&0x80000000 else 'xt_unhandled_exception'
            def panic(args):
                """Validate every saved GPR/CSR before deliberately allowing handler return."""
                assert args[:2]==(STACK-160,cause&31)
                assert f.word(STACK-160)==END
                for i in range(1,32):assert f.word(STACK-160+4*i)==f.initial[i]
                for offset,value in expected_csr.items():assert f.word(STACK-160+offset)==value
                return 0
            f.boundary(selected,binding(row,selected),panic);f.run('_panic_handler')
            for i in range(1,32):assert f.reg(i)==f.initial[i]
            assert [name for name,args in f.events]==[selected];record('panic-return',f)

        for size in (0,1,512,0xffffffff):
            f=fixture(variant);row=f.rows['_Znwj'];f.reg(10,size)
            def malloc(args):
                """C++ new requests at least one byte for a zero-sized allocation."""
                assert args[0]==max(size,1);return HEAP+128
            f.boundary('malloc',binding(row,'malloc'),malloc);f.run('_Znwj')
            assert f.reg(10)==HEAP+128;assert [n for n,a in f.events]==['malloc'];record('new-success',f)

        for size in (0,1,512,0xffffffff):
            f=fixture(variant);f.reg(10,size);row=f.rows['_Znwj']
            f.boundary('malloc',binding(row,'malloc'),lambda a:0)
            f.boundary('get_new_handler',binding(row,'_ZSt15get_new_handlerv'),lambda a:0)
            f.boundary('abort',f.report['abort_boundary'],lambda a:f.stop('abort'))
            f.run('_Znwj',expected_stop='abort')
            assert [n for n,a in f.events]==['malloc','get_new_handler','abort'];record('new-oom-aborts',f)

        f=fixture(variant);row=f.rows['_Znwj'];attempts=[];f.reg(10,7)
        f.boundary('malloc',binding(row,'malloc'),lambda a:attempts.append(a[0]) or (0 if len(attempts)==1 else HEAP+128))
        f.boundary('get_new_handler',binding(row,'_ZSt15get_new_handlerv'),lambda a:END+256)
        f.boundary('new_handler',END+256,lambda a:0)
        f.run('_Znwj');assert f.reg(10)==HEAP+128 and attempts==[7,7]
        assert [n for n,a in f.events]==['malloc','get_new_handler','new_handler','malloc'];record('new-handler-retry',f)

        for state in ('null','empty','one','two'):
            f=fixture(variant);row=f.rows['_ZL15eh_globals_dtorPv'];root=HEAP+32;node=HEAP+128
            f.reg(10,0 if state=='null' else root);f.word(root,0 if state=='empty' else node)
            f.word(node+16,node+128 if state=='two' else 0)
            f.boundary('free',binding(row,'free'),lambda a:0)
            deleted=[]
            # Observing this target must not replace its abort-only implementation.
            target=binding(row,'_Unwind_DeleteException')
            f.cpu.hook_add(UC_HOOK_CODE,lambda c,p,s,d: deleted.append(f.reg(10)) if p==target else None)
            f.boundary('abort',f.report['abort_boundary'],lambda a:f.stop('abort'))
            f.run('_ZL15eh_globals_dtorPv',expected_stop='abort' if state in ('one','two') else None)
            if state in ('one','two'):assert deleted==[node+48] and not any(n=='free' for n,a in f.events)
            elif state=='empty':assert len(f.events)==1 and f.events[0][0]=='free' and f.events[0][1][0]==root
            else:assert not f.events
            record('globals-'+state,f)

        for size in (0,1,512,0xffffffff):
            f=fixture(variant);row=f.rows['_ZnajRKSt9nothrow_t'];f.reg(10,size)
            f.boundary('operator_new_array',binding(row,'_Znaj'),lambda a:HEAP+128)
            f.run('_ZnajRKSt9nothrow_t');assert f.reg(10)==HEAP+128
            assert f.events[0][1][0]==size;record('nothrow-success',f)
        for size in (0,1,512,0xffffffff):
            f=fixture(variant);f.reg(10,size);row=f.rows['_Znwj']
            f.boundary('malloc',binding(row,'malloc'),lambda a:0)
            f.boundary('get_new_handler',binding(row,'_ZSt15get_new_handlerv'),lambda a:0)
            f.boundary('abort',f.report['abort_boundary'],lambda a:f.stop('abort'))
            f.run('_ZnajRKSt9nothrow_t',expected_stop='abort')
            assert [n for n,a in f.events]==['malloc','get_new_handler','abort']
            pad=int(f.rows['_ZnajRKSt9nothrow_t']['start'],0)+8
            assert not {pad,pad+2}&f.visited;record('nothrow-oom-aborts',f)
        f=fixture(variant);row=f.rows['_ZnajRKSt9nothrow_t']
        f.boundary('begin_catch',binding(row,'__cxa_begin_catch'),lambda a:HEAP+128)
        f.boundary('end_catch',binding(row,'__cxa_end_catch'),lambda a:0)
        f.reg(2,STACK-16);f.word(STACK-4,END)
        f.run(pc=int(row['start'],0)+8);assert f.reg(10)==0
        assert [n for n,a in f.events]==['begin_catch','end_catch'];record('nothrow-explicit-landing-pad',f)
    return dict(passed=True,cases=sum(cases.values()),families=dict(cases),
                visited={name:sorted(values) for name,values in visited.items()},
                desired_nothrow_oom_contract_passed=False,
                actual_panic_recovery_proved=False,natural_exception_reachability_proved=False,
                full_end_catch_semantics_proved=False,physical_hardware_tested=False)
