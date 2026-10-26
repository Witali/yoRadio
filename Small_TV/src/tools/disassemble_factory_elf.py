"""Export all original executable regions through an explicit RV32 ISA view."""
import argparse
import hashlib
import json
from pathlib import Path

from audit_factory_xrefs import Image, sha
from reverse.rv32_disassembly import Disassembler


def main():
    """Keep the original ELF immutable and omit DROM, RAM data and ELF metadata payloads."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('elf','objdump','output'):parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();data=args.elf.read_bytes();image=Image(data)
    regions=[(row['name'],row['start'],row['data']) for row in image.sections if row['execute']]
    if {name for name,_,_ in regions}!={'.flash.text','.iram.text','.iram.vectors'}:
        raise ValueError('Requalify original executable sections')
    args.output.mkdir(parents=True,exist_ok=False)
    with Disassembler(args.objdump,regions,args.output) as decoder:
        text=decoder.text(canonical=True)
    path=args.output/'factory-rv32.asm';path.write_text(text,encoding='utf8',newline='\n')
    if sha(args.elf.read_bytes())!=sha(data):raise ValueError('Original ELF changed during export')
    report=dict(schema='factory-rv32-disassembly-v1',factory_elf_sha256=sha(data),
        disassembler=decoder.metadata,assembly=path.name,assembly_sha256=sha(path.read_bytes()),
        regions=[dict(name=name,start=address,bytes=len(code),sha256=sha(code)) for name,address,code in regions],
        drom_or_settings_exported=False,whole_image_completeness_proved=False,semantic_equivalence_proved=False)
    (args.output/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(passed=True,regions=len(regions),code_bytes=sum(len(code) for _,_,code in regions),output=str(path))))


if __name__=='__main__':main()
