"""Describe linked native SDK counterparts without inferring equivalence from names."""
import hashlib
import io

from elftools.elf.elffile import ELFFile
from reverse.rv32_link_match import branch_target,link_register


def describe(data):
    """Bind three symbols and the coexistence tail wrapper to actual native ELF bytes."""
    elf=ELFFile(io.BytesIO(data));symbols=list(elf.get_section_by_name('.symtab').iter_symbols())
    def function(name):
        """Reject aliases/undefined symbols and read the complete executable extent."""
        rows=[s for s in symbols if s.name==name and s['st_value'] and s['st_info']['type']=='STT_FUNC']
        assert len(rows)==1
        row=rows[0];section=elf.get_section(row['st_shndx']);assert section['sh_flags']&4
        offset=row['st_value']-section['sh_addr'];code=section.data()[offset:offset+row['st_size']]
        assert len(code)==row['st_size']>0
        return dict(name=name,address=hex(row['st_value']),bytes=row['st_size'],
            code_sha256=hashlib.sha256(code).hexdigest()),code
    names=('ieee80211_tx_mgt_cb','wifi_connect_process','pm_coex_slice_timeout_process')
    rows={};codes={}
    for name in names:rows[name],codes[name]=function(name)
    wrapper=codes['pm_coex_slice_timeout_process'];pc=int(rows['pm_coex_slice_timeout_process']['address'],0)
    assert len(wrapper)==6 and wrapper[:2]==bytes.fromhex('0545') and link_register(wrapper[2:])==0
    target=branch_target(wrapper[2:],pc+2);implementation,code=function('pm_coex_go_to_sleep')
    assert target==int(implementation['address'],0)
    return dict(native_elf_sha256=hashlib.sha256(data).hexdigest(),functions=list(rows.values()),
        coexistence_wrapper=dict(bytes_hex=wrapper.hex(),argument0=1,tail_target=implementation),
        semantic_equivalence_proved=False)
