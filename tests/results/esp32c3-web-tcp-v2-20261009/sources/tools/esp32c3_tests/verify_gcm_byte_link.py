"""Verify the optional GHASH dispatch/table/wipe in the actual linked RISC-V ELF."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf',type=Path,required=True)
    p.add_argument('--objdump',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    table=subprocess.check_output([str(a.objdump),'-t',str(a.elf)]).decode()
    rows=[line for line in table.splitlines() if re.search(r'\byoradio_gcm_reduction8$',line)]
    assert len(rows)==1 and '.flash.rodata' in rows[0] and int(rows[0].split()[-2],16)==1024,rows
    names=('esp_gcm_ghash','yoradio_gcm_ghash_large','yoradio_gcm_mult_byte')
    bodies={name:subprocess.check_output([str(a.objdump),'-d','--disassemble='+name,str(a.elf)]).decode() for name in names}
    assert '<yoradio_gcm_ghash_large>' in bodies['esp_gcm_ghash']
    assert '<esp_gcm_ghash.part.0>' in bodies['esp_gcm_ghash']
    assert '<yoradio_gcm_mult_byte>' in bodies['yoradio_gcm_ghash_large']
    assert '<mbedtls_platform_zeroize>' in bodies['yoradio_gcm_ghash_large']
    assert not re.search(r'<[^>]*(?:alloc|free|mutex|yield|delay)[^>]*>',bodies['yoradio_gcm_ghash_large'],re.I)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    for name,body in bodies.items():
        a.output.with_name(name+'.disassembly.txt').write_text(body)
    result=dict(result='PASS',elf_sha256=hashlib.sha256(a.elf.read_bytes()).hexdigest(),
        reduction_table=rows[0],body_sha256={n:hashlib.sha256(b.encode()).hexdigest() for n,b in bodies.items()},
        scope='Linked dispatch, flash table and explicit scratch wipe; not crypto or hardware performance qualification')
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
