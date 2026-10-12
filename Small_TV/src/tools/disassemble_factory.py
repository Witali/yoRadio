"""Disassemble selected original application functions from the verified dump.

The extraction is restricted to the mapped IROM segment; settings and credential
strings in DROM are never exported. Function boundaries use symbol-map.json.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

DUMP_SHA256='5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4'
IROM_BASE=0x42000020
IROM_OFFSET=0x50020
IROM_SIZE=0xb29b4


def main():
    """Verify input, extract executable bytes and save addressed disassembly."""
    root=Path(__file__).resolve().parents[1]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--objdump',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--addresses',nargs='*',default=[],type=lambda value:int(value,0))
    parser.add_argument('--ranges',nargs='*',default=[],help='Additional start:stop IROM ranges')
    args=parser.parse_args()
    dump=(root.parent/'full-flash.bin').read_bytes()
    if hashlib.sha256(dump).hexdigest()!=DUMP_SHA256:
        raise ValueError('The original flash dump differs from the analyzed capture')
    symbols=json.loads((root/'symbol-map.json').read_text())['functions']
    ordered=sorted(symbols,key=lambda item:int(item['address'],0))
    boundaries={int(item['address'],0):int(ordered[index+1]['address'],0)
                for index,item in enumerate(ordered[:-1])}
    names={int(item['address'],0):item['logical_name'] for item in ordered}
    args.output.mkdir(parents=True,exist_ok=True)
    binary=args.output/'factory-irom.bin'
    code=dump[IROM_OFFSET:IROM_OFFSET+IROM_SIZE]
    binary.write_bytes(code)
    records=[]
    try:
        requested=[(start,boundaries.get(start),names.get(start)) for start in args.addresses]
        for item in args.ranges:
            start,stop=(int(value,0) for value in item.split(':'))
            requested.append((start,stop,f'helper_at_{start:08x}'))
        for start,stop,name in requested:
            if stop is None or not IROM_BASE<=start<stop<=IROM_BASE+IROM_SIZE:
                raise ValueError(f'No bounded IROM function at {start:#x}')
            command=[str(args.objdump),'-D','-b','binary','-m','riscv:rv32',
                     f'--adjust-vma={IROM_BASE}',f'--start-address={start}',
                     f'--stop-address={stop}',str(binary)]
            assembly=subprocess.check_output(command,text=True)
            # Omit the temporary absolute path from the saved artifact.
            assembly=assembly.replace(str(binary),'factory-irom.bin')
            path=args.output/(name+'.asm')
            path.write_text(assembly,encoding='utf-8')
            records.append({'name':name,'start':hex(start),'stop':hex(stop),
                            'code_sha256':hashlib.sha256(code[start-IROM_BASE:stop-IROM_BASE]).hexdigest(),
                            'assembly':path.name})
    finally:
        binary.unlink()
    (args.output/'manifest.json').write_text(json.dumps({'dump_sha256':DUMP_SHA256,
        'irom_base':hex(IROM_BASE),'irom_flash_offset':hex(IROM_OFFSET),
        'note':'Bounds end at the next exported symbol; they can include alignment bytes.',
        'functions':records},indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    main()
