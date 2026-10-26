"""Retain the failing NVS/OOM behavior in the frozen original native ELF."""
import argparse
import io
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from elftools.elf.elffile import ELFFile
from audit_factory_xrefs import sha
from reverse.elf_archive import members
from reverse.nothrow_linkage import LinkedRuntime, complete
from reverse.runtime_call_gaps import NATIVE_SHA
from runtime_call_instructions import Fixture, HEAP, END
from nothrow_target import page_layout
from verify_rv32_disassembly_evidence import payload


def run(elf,app,nvs_object,old_qualification):
    """Execute the same erased-page allocation path through the actual old abort stub."""
    assert sha(elf)==NATIVE_SHA and old_qualification['native_elf_sha256']==NATIVE_SHA
    linked=LinkedRuntime(elf,app);layout=page_layout(linked)
    obj=ELFFile(io.BytesIO(nvs_object))
    names=[s.name for s in obj.get_section_by_name('.symtab').iter_symbols()
           if s.name.startswith('_ZN3nvs4Page4loadE') and s['st_info']['type']=='STT_FUNC' and s['st_size']]
    assert len(names)==1
    page=complete(linked,nvs_object,names[0])
    functions=list(old_qualification['variants']['native']['functions'])+[page]
    for name in ('_ZN3nvs4Page6HeaderC1Ev','_ZdaPv','_ZdlPv'):
        symbol,code=linked.body(name)
        functions.append(dict(name=name,start=hex(symbol['st_value']),linked_bytes=len(code),code_sha256=sha(code)))
    f=Fixture('legacy-nothrow',dict(functions=functions,allocator_veneer=None),linked.read)
    pointer=HEAP+128;partition=HEAP+512;vtable=HEAP+768
    f.word(partition,vtable);f.word(vtable+layout['read_raw_slot'],END+1024)
    f.reg(10,pointer);f.reg(11,partition);f.reg(12,2)
    def read_raw(args):
        """Supply the same erased 32-byte header as the corrected-image fixture."""
        assert args[0]==partition and args[1]==8192 and args[3]==32
        f.cpu.mem_write(args[2],b'\xff'*32);return 0
    def fill(args):
        """Model only the constructor's explicit ROM memset boundary."""
        assert args[1:3]==(255,19)
        f.cpu.mem_write(args[0],b'\xff'*19);return args[0]
    f.boundary('read_raw',END+1024,read_raw)
    memset=[s['st_value'] for s in linked.symbols if s.name=='memset' and s['st_value']];assert len(memset)==1
    f.boundary('memset',memset[0],fill)
    f.boundary('malloc',linked.symbol('malloc')['st_value'],lambda a:0)
    f.boundary('handler',linked.symbol('_ZSt15get_new_handlerv')['st_value'],lambda a:0)
    f.boundary('abort',old_qualification['variants']['native']['abort_boundary'],lambda a:f.stop('abort'))
    f.run(names[0],expected_stop='abort')
    assert [n for n,a in f.events]==['memset','read_raw','malloc','handler','abort']
    assert next(a[0] for n,a in f.events if n=='malloc')==512
    return dict(passed=True,desired_contract_passed=False,elf_sha256=sha(elf),nvs_object_sha256=sha(nvs_object),
                nvs_page_load=page,layout=layout,events=[dict(name=n,args=list(a[:4])) for n,a in f.events],
                visited=sorted(f.visited),physical_hardware_tested=False)


def main():
    """Read a pinned historical report and capture a new bounded failing-before observation."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('elf','app','nvs','proof','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing failing-before capture')
    old=json.loads(args.proof.read_bytes())
    qualification=json.loads(payload(args.proof.parent,old['files']['qualification']))
    objects=[data for name,data in members(args.nvs.read_bytes()) if name=='nvs_page.cpp.obj'];assert len(objects)==1
    result=run(args.elf.read_bytes(),args.app.read_bytes(),objects[0],qualification)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(passed=True,desired_contract_passed=False,actual_nvs_abort_observed=True)))


if __name__=='__main__':main()
