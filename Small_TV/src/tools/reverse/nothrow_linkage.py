"""Check the new RV32 wrappers and actual NVS ingress without weakening old ELF pins."""
import io

from elftools.elf.elffile import ELFFile
from audit_factory_xrefs import sha
from reverse.elf_archive import members
from reverse.rv32_link_match import model, match

WRAPPERS = ('__wrap__ZnwjRKSt9nothrow_t','__wrap__ZnajRKSt9nothrow_t')


class LinkedRuntime:
    """Bind a fresh linked RV32 image to its ESP app descriptor and initialized code."""
    def __init__(self, data, app):
        """Accept a new ELF only with a matching app, not an old proof's relaxed identity."""
        self.elf=ELFFile(io.BytesIO(data));self.digest=sha(data)
        if (self.elf.elfclass!=32 or not self.elf.little_endian or self.elf['e_machine']!='EM_RISCV'
            or len(app)<208 or app[0]!=0xe9 or app[176:208].hex()!=self.digest):
            raise ValueError('Nothrow build is not a matching RV32 ESP app/ELF pair')
        self.symbols=list(self.elf.get_section_by_name('.symtab').iter_symbols())

    def symbol(self, name):
        """Reject missing/ambiguous definitions even when an alias has the same address."""
        rows=[s for s in self.symbols if s.name==name and s['st_value'] and isinstance(s['st_shndx'],int)]
        if len(rows)!=1:raise ValueError('Missing/ambiguous nothrow symbol: '+name)
        return rows[0]

    def read(self, address, length, execute=False):
        """Never read zero-fill, a cross-section extent or data as an executable body."""
        rows=[s for s in self.elf.iter_sections() if s['sh_type']!='SHT_NOBITS' and s['sh_flags']&2
              and (not execute or s['sh_flags']&4)
              and s['sh_addr']<=address<address+length<=s['sh_addr']+s['sh_size']]
        if len(rows)!=1:raise ValueError('Invalid nothrow linked extent')
        section=rows[0];offset=address-section['sh_addr']
        return section.data()[offset:offset+length]

    def body(self, name):
        """Read only the symbol's entire nonempty executable extent."""
        s=self.symbol(name)
        if s['st_info']['type']!='STT_FUNC' or not 0<s['st_size']<=4096:
            raise ValueError('Invalid nothrow function bounds')
        return s,self.read(s['st_value'],s['st_size'],True)


def complete(linked, obj, name):
    """Match every instruction and verify global/local direct-call symbol bindings."""
    symbol,code=linked.body(name);spec=model(obj,name)
    row=match(spec,code,symbol['st_value'],linked.symbol('__global_pointer$')['st_value'])
    if row['linked_bytes']!=symbol['st_size']:raise ValueError('Incomplete nothrow body match')
    for entry in row['symbol_bindings']:
        # The wrappers call a file-local helper in another section. A CALL
        # relocation permits rewriting its immediate, but its final target
        # must still be that helper, just like the global malloc/handler calls.
        if entry['kind']=='call' or entry['binding']!='STB_LOCAL':
            if linked.symbol(entry['name'])['st_value']!=entry['address']:
                raise ValueError('Wrong linked nothrow callee')
    row['code_sha256']=sha(code)
    return row


def verify(elf, app, wrapper_object, nvs_archive):
    """Prove NVS selects the wrapper, and reject surviving unsupported nothrow overloads."""
    linked=LinkedRuntime(elf,app)
    obj=ELFFile(io.BytesIO(wrapper_object))
    functions=[s.name for s in obj.get_section_by_name('.symtab').iter_symbols()
               if s['st_info']['type']=='STT_FUNC' and isinstance(s['st_shndx'],int) and s['st_size']]
    if not set(WRAPPERS)<=set(functions) or not 2<=len(functions)<=3:
        raise ValueError('Requalify the nothrow translation unit')
    forbidden=[s.name for s in linked.symbols if s['st_value'] and s.name.startswith(('_Znwj','_Znaj'))
               and 'nothrow' in s.name]
    if forbidden:raise ValueError('Unwrapped nothrow overload remains linked: '+', '.join(forbidden))
    wrappers=[complete(linked,wrapper_object,name) for name in functions]
    names=set(functions)
    for row in wrappers:
        for entry in row['symbol_bindings']:
            if entry['kind']=='call' and entry['name'] not in names|{'malloc','_ZSt15get_new_handlerv'}:
                raise ValueError('Nothrow wrapper can enter an unexpected runtime function')
    objects=[raw for name,raw in members(nvs_archive) if name=='nvs_page.cpp.obj']
    if len(objects)!=1:raise ValueError('Missing/duplicate NVS page object')
    page=ELFFile(io.BytesIO(objects[0]));table=page.get_section_by_name('.symtab')
    loads=[s.name for s in table.iter_symbols() if s['st_info']['type']=='STT_FUNC'
           and isinstance(s['st_shndx'],int) and s.name.startswith('_ZN3nvs4Page4loadE')]
    if len(loads)!=1:raise ValueError('Requalify NVS Page::load')
    # Do not require an unwrapped symbol to exist while matching this caller.
    symbol,code=linked.body(loads[0]);spec=model(objects[0],loads[0])
    row=match(spec,code,symbol['st_value'],linked.symbol('__global_pointer$')['st_value'])
    if row['linked_bytes']!=symbol['st_size']:raise ValueError('Incomplete NVS page match')
    calls=[b for b in row['symbol_bindings'] if b['name']=='_ZnajRKSt9nothrow_t']
    if len(calls)!=1 or calls[0]['address']!=linked.symbol(WRAPPERS[1])['st_value']:
        raise ValueError('NVS page allocation bypasses the nothrow wrapper')
    row['code_sha256']=sha(code)
    return dict(schema='small-tv-nothrow-linkage-v1',passed=True,elf_sha256=sha(elf),app_sha256=sha(app),
                wrapper_object_sha256=sha(wrapper_object),nvs_archive_sha256=sha(nvs_archive),
                nvs_object_sha256=sha(objects[0]),functions=wrappers,nvs_page_load=row,
                wrappers={name:linked.symbol(name)['st_value'] for name in WRAPPERS},
                nvs_runtime_oom_tested=False,physical_hardware_tested=False)
