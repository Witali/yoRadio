"""Identify omitted factory Wi-Fi functions by complete relocated SDK byte sequences."""
from collections import Counter
import hashlib
import io
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from audit_factory_xrefs import Image,sha,startup_gp
from reverse.elf_archive import members
from reverse.rv32_link_match import model,match

COMMIT='b87cce81803b85c3639fb14bac6c24cff6d0fbad'
CASES=(('ieee80211_tx_mgt_cb',0x420581b6,0x42058280,0x4206fd6a),
       ('wifi_connect_process',0x420662da,0x420662da,0x42068f1e),
       ('pm_coex_slice_timeout_process',0x420756f0,0x420757d2,0x4207b120))
LIBRARIES={'libnet80211.a':'8f989ecd7104520083727442247aed08ad93ef2bc304ae727022f8573f4bc558',
    'libpp.a':'b460bb305a8d3c5e93489a03710108a06435d58bf12410e080c0c6805a74bade',
    'libcore.a':'85394ad591b3964c19d57fa8403b61a9ac5906c3f89a5d3a09d3493abf1e8353'}


def load_models(directory):
    """Require pinned public library bytes and unique defined SDK symbols."""
    wanted={row[0] for row in CASES};result={};inputs={}
    for name,digest in LIBRARIES.items():
        path=directory/name;data=path.read_bytes();assert sha(data)==digest,'Changed SDK library'
        inputs[name]=dict(sha256=digest,git_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest())
        for member,payload in members(data):
            if payload[:4]!=b'\x7fELF':continue
            elf=ELFFile(io.BytesIO(payload));table=elf.get_section_by_name('.symtab')
            if table is None:continue
            for symbol in table.iter_symbols():
                if symbol.name not in wanted or symbol['st_info']['type']!='STT_FUNC' or not isinstance(symbol['st_shndx'],int):continue
                assert symbol.name not in result,'Ambiguous SDK symbol'
                parsed=model(payload,symbol.name)
                result[symbol.name]=dict(spec=parsed,library=name,member=member,
                    object_sha256=sha(payload),function_sha256=sha(parsed['code']))
    assert set(result)==wanted
    return result,inputs


def classify(image_bytes,directory,replacements=None):
    """Match every function byte, local edge and shared symbol binding across the three cases."""
    image=Image(image_bytes);gp=startup_gp(image);models,inputs=load_models(directory)
    shared={};results=[]
    for name,start,site,caller in CASES:
        item=models[name];spec=item['spec'];data=image.read(start,len(spec['code'])+64,True)
        if replacements and name in replacements:data=replacements[name]
        row=match(spec,data,start,gp);assert start<=site<int(row['end'],0)
        for binding in row['symbol_bindings']:
            if binding['binding']!='STB_LOCAL':
                symbol=binding['name'];address=binding['address']
                assert symbol not in shared or shared[symbol]==address,'Shared SDK symbol resolves differently'
                shared[symbol]=address
        row.update(site=hex(site),caller_site=hex(caller),library=item['library'],member=item['member'],
            object_sha256=item['object_sha256'],source_function_sha256=item['function_sha256'],
            factory_function_sha256=sha(data[:row['linked_bytes']]),
            transformation_counts=dict(Counter(t['kind'] for t in row['transformations'])))
        results.append(row)
    return dict(schema_version=1,passed=True,semantic_equivalence_proved=False,
        whole_image_completeness_proved=False,physical_hardware_tested=False,
        factory_elf_sha256=sha(image_bytes),sdk_wifi_commit=COMMIT,libraries=inputs,gp=hex(gp),functions=results,
        shared_symbols={name:hex(address) for name,address in sorted(shared.items())})


def main():
    """Save new evidence and bounded ranges for transient Ghidra reconstruction."""
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf',type=Path,required=True)
    parser.add_argument('--sdk-libraries',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists()
    result=classify(args.elf.read_bytes(),args.sdk_libraries)
    result['inputs_sha256']={str(p.resolve()):sha(p.read_bytes()) for p in
        (Path(__file__),Path(__file__).parent/'reverse/rv32_link_match.py',Path(__file__).parent/'reverse/elf_archive.py')}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=True,functions=[{k:r[k] for k in ('name','start','end','source_bytes','linked_bytes','local_branches_checked')} for r in result['functions']])))


if __name__=='__main__':main()
