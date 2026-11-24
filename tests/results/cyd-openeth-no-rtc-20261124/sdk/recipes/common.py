import hashlib
import json
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
DEP=Path('C:/Work/yoRadio/.idf')
SOURCE='7595a79958b8a2ef56babb24c43259fcf536b6dd'
def load(p): return json.loads(Path(p).read_bytes())
def pin(p):
    b=Path(p).read_bytes(); return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
def write(p,data):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
def git(*args): return subprocess.check_output(['git','-c','core.longpaths=true',*args],cwd=ROOT)
def same(item):
    assert pin(ROOT/item['path'])==dict(bytes=item['bytes'],sha256=item['sha256']),item['path']+' changed'
def alloc_signature(path):
    result={}
    with Path(path).open('rb') as stream:
        elf=ELFFile(stream)
        for section in elf.iter_sections():
            allocated=bool(section['sh_flags']&2)
            relocation=section['sh_type'] in ('SHT_REL','SHT_RELA') and bool(elf.get_section(section['sh_info'])['sh_flags']&2)
            if allocated or relocation:
                result[section.name]=dict(type=section['sh_type'],flags=section['sh_flags'],bytes=section['sh_size'],
                    sha256=None if section['sh_type']=='SHT_NOBITS' else hashlib.sha256(section.data()).hexdigest())
                if relocation:
                    symbols=elf.get_section(section['sh_link']); references=[]
                    for record in section.iter_relocations():
                        symbol=symbols.get_symbol(record['r_info_sym']); index=symbol['st_shndx']
                        storage=elf.get_section(index).name if isinstance(index,int) else index
                        references.append((record['r_offset'],record['r_info_type'],record.entry.get('r_addend'),
                            symbol.name,symbol['st_value'],symbol['st_size'],symbol['st_info']['type'],symbol['st_info']['bind'],storage))
                    result[section.name]['symbol_references_sha256']=hashlib.sha256(json.dumps(references).encode()).hexdigest()
    return result
def guard(prep,row):
    assert git('rev-parse','HEAD').decode().strip()==SOURCE
    assert not git('diff','--name-only','HEAD') and not git('diff','--cached','--name-only')
    for item in prep['protected']+prep['sources']: same(item)
    for unit in row['project_units']:
        assert pin(ROOT/unit['file'])==dict(bytes=unit['bytes'],sha256=unit['sha256'])
    for folder,commit in prep['sdk_repositories'].items():
        assert subprocess.check_output(['git','-C',str(DEP/folder),'rev-parse','HEAD'],text=True).strip()==commit
        assert not subprocess.check_output(['git','-c','core.longpaths=true','-C',str(DEP/folder),'status','--porcelain','--untracked-files=no'])
