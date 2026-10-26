"""Execute the production RV32 wrappers and the real NVS Page::load error branch."""
import argparse
import io
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from elftools.dwarf.dwarf_expr import DWARFExprParser
from audit_factory_xrefs import sha
from reverse.nothrow_linkage import LinkedRuntime, WRAPPERS
from runtime_call_instructions import Fixture, HEAP, END, PRESERVED
from unicorn import riscv_const as rv


def page_layout(linked):
    """Derive private NVS fields and virtual read_raw slot from the exact linked DWARF."""
    dwarf=linked.elf.get_dwarf_info();units=[]
    for cu in dwarf.iter_CUs():
        name=cu.get_top_DIE().attributes.get('DW_AT_name')
        if name and name.value.decode().replace('\\','/').endswith('/nvs_page.cpp'):units.append(cu)
    if len(units)!=1:raise ValueError('Requalify the NVS source compilation unit')
    found={}
    for die in units[0].iter_DIEs():
        name=die.attributes.get('DW_AT_name');size=die.attributes.get('DW_AT_byte_size')
        if die.tag=='DW_TAG_class_type' and name and size and name.value in (b'Page',b'Partition'):
            if name.value in found:raise ValueError('Ambiguous NVS private class')
            found[name.value]=die
    page=found[b'Page'];members={}
    for child in page.iter_children():
        name=child.attributes.get('DW_AT_name')
        if child.tag=='DW_TAG_member' and name and name.value.decode() in (
            'mBaseAddress','mState','mPartition','mUsedEntryCount','mErasedEntryCount'):
            location=child.attributes['DW_AT_data_member_location'].value
            if type(location)!=int:raise ValueError('Nonconstant NVS field location')
            members[name.value.decode()]=location
    if len(members)!=5:raise ValueError('Incomplete NVS page fields')
    slots=[]
    for child in found[b'Partition'].iter_children():
        name=child.attributes.get('DW_AT_name')
        if child.tag=='DW_TAG_subprogram' and name and name.value==b'read_raw':
            expression=child.attributes['DW_AT_vtable_elem_location'].value
            decoded=DWARFExprParser(dwarf.structs).parse_expr(expression)
            if len(decoded)!=1 or decoded[0].op_name!='DW_OP_constu':raise ValueError('Requalify NVS read_raw vtable expression')
            slots.append(decoded[0].args[0]*4)
    if len(slots)!=1:raise ValueError('Missing/ambiguous NVS read_raw slot')
    return dict(page_bytes=page.attributes['DW_AT_byte_size'].value,members=members,read_raw_slot=slots[0])


def run(elf, app, qualification):
    """Keep real wrapper/NVS instructions; replace only malloc/handler/free/partition I/O."""
    linked=LinkedRuntime(elf,app);layout=page_layout(linked)
    functions=list(qualification['functions']);functions.append(qualification['nvs_page_load'])
    for name in ('_ZN3nvs4Page6HeaderC1Ev','_ZdaPv','_ZdlPv'):
        s,code=linked.body(name)
        functions.append(dict(name=name,start=hex(s['st_value']),linked_bytes=len(code),code_sha256=sha(code)))
    definition=dict(functions=functions,allocator_veneer=None)
    cases=[]
    def new():
        """Every case uses independent private memory and ABI register state."""
        return Fixture('new-nothrow',definition,linked.read)
    def record(name,f):
        """Report actual callbacks and visited instruction PCs, never a desired pass alone."""
        cases.append(dict(name=name,events=[dict(name=n,args=list(a[:4])) for n,a in f.events],
                          result=f.reg(10),visited=sorted(f.visited)))
    for wrapper in WRAPPERS:
        for size in (0,1,512,0xffffffff):
            for succeed in (False,True):
                f=new();f.reg(10,size)
                f.boundary('malloc',linked.symbol('malloc')['st_value'],lambda a:(HEAP+1536) if succeed else 0)
                f.boundary('handler',linked.symbol('_ZSt15get_new_handlerv')['st_value'],lambda a:0)
                f.run(wrapper)
                assert f.reg(10)==(HEAP+1536 if succeed else 0)
                assert f.events[0][1][0]==max(size,1)
                assert [n for n,a in f.events]==(['malloc'] if succeed else ['malloc','handler'])
                record(wrapper+f'/{size}/{succeed}',f)
        for kind in ('retry','remove'):
            f=new();f.reg(10,512);attempt=[]
            f.boundary('malloc',linked.symbol('malloc')['st_value'],lambda a:attempt.append(a[0]) or
                       ((HEAP+1536) if len(attempt)==2 and kind=='retry' else 0))
            f.boundary('handler',linked.symbol('_ZSt15get_new_handlerv')['st_value'],
                       lambda a:END+512 if len(attempt)==1 else 0)
            f.boundary('callback',END+512,lambda a:0);f.run(wrapper)
            assert attempt==[512,512] and f.reg(10)==(HEAP+1536 if kind=='retry' else 0)
            assert [n for n,a in f.events]==(['malloc','handler','callback','malloc']+
                                          ([] if kind=='retry' else ['handler']))
            record(wrapper+'/'+kind,f)
        f=new();f.reg(10,512)
        f.boundary('malloc',linked.symbol('malloc')['st_value'],lambda a:0)
        f.boundary('handler',linked.symbol('_ZSt15get_new_handlerv')['st_value'],lambda a:END+512)
        f.boundary('callback',END+512,lambda a:f.stop('nonreturning-handler'))
        f.run(wrapper,expected_stop='nonreturning-handler')
        assert [n for n,a in f.events]==['malloc','handler','callback']
        record(wrapper+'/nonreturning-handler',f)
    for mode in ('oom','success','read-error','null-partition'):
        f=new();page=HEAP+128;partition=HEAP+512;vtable=HEAP+768;block=HEAP+1536
        assert 0<layout['page_bytes']<=256
        f.word(partition,vtable);f.word(vtable+layout['read_raw_slot'],END+1024)
        f.reg(10,page);f.reg(11,0 if mode=='null-partition' else partition);f.reg(12,2)
        reads=[]
        def read_raw(args):
            """Present a real erased-page header/body, or an explicit partition read error."""
            owner,offset,destination,length=args[:4];assert owner==partition
            assert (length==32 and not reads) or (length==512 and len(reads)>=1)
            assert offset==8192+(0 if length==32 else (len(reads)-1)*512)
            reads.append((offset,length))
            if mode=='read-error':return 0x104
            f.cpu.mem_write(destination,b'\xff'*length);return 0
        f.boundary('read_raw',END+1024,read_raw)
        memset=[s['st_value'] for s in linked.symbols if s.name=='memset' and s['st_value']]
        assert len(memset)==1
        def fill(args):
            """Model only Header's explicit ROM memset boundary, not its caller instructions."""
            destination,value,length=args[:3];assert value==255 and length==19
            f.cpu.mem_write(destination,bytes([value])*length);return destination
        f.boundary('memset',memset[0],fill)
        f.boundary('malloc',linked.symbol('malloc')['st_value'],lambda a:block if mode=='success' else 0)
        f.boundary('handler',linked.symbol('_ZSt15get_new_handlerv')['st_value'],lambda a:0)
        f.boundary('free',linked.symbol('free')['st_value'],lambda a:0)
        # The real eight-block erased-page scan exceeds the small fixture's
        # 4096-instruction default. It still has a strict finite CPU budget.
        f.cpu.emu_start(int(qualification['nvs_page_load']['start'],0),END,count=32768)
        assert f.stopped is None and f.cpu.reg_read(rv.UC_RISCV_REG_PC)==END
        for register in PRESERVED:assert f.reg(register)==f.initial[register]
        assert f.reg(10)=={'oom':0x101,'success':0,'read-error':0x104,'null-partition':0x102}[mode]
        names=[n for n,a in f.events]
        if mode=='oom':assert names==['memset','read_raw','malloc','handler']
        if mode=='success':
            assert names==['memset','read_raw','malloc']+['read_raw']*8+['free']
            assert f.events[-1][1][0]==block
        if mode=='read-error':assert names==['memset','read_raw']
        if mode=='null-partition':assert not names
        if mode in ('oom','success'):
            assert f.word(page+layout['members']['mBaseAddress'])==8192
            assert f.word(page+layout['members']['mState'])==0xffffffff
            assert f.word(page+layout['members']['mPartition'])==partition
        record('nvs-page/'+mode,f)
    return dict(passed=True,cases=len(cases),layout=layout,results=cases,
                nvs_instruction_oom_proved=True,full_vm_fault_injection_proved=False,physical_hardware_tested=False)


def main():
    """Require an explicit fresh production image/report and new output path."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('elf','app','qualification','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing target cases')
    report=run(args.elf.read_bytes(),args.app.read_bytes(),json.loads(args.qualification.read_bytes()))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('results','layout')}))


if __name__=='__main__':main()
