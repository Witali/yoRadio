"""Qualify the full-range keep-alive redirect, all SDK callers and timer backends."""
import argparse
import io
import json
from pathlib import Path

from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
from audit_factory_xrefs import sha
from reverse.elf_archive import members
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import model,match
from reverse.timer_event11_match import adapter_table,unique

REPLACEMENT='small_tv_wifi_enable_keep_alive_timer'
SDK_NAME='pm_enable_keep_alive_timer'
TIMER_SOURCE_SHA='cdde10900900c338463fbc7610b4b4f0804253b80598678f4961cd1a3d43e454'
LIBRARIES={'libpp.a':'c7797847c9229cc14b27194b5b7ccd63c20e2c909815d72e189973dd9f2a1aa2',
           'libnet80211.a':'c2df6fcca4c1c19c9c6b8171f16461e52a636da90dd7f7be3b67bed4fbe71cca'}
CALLERS={('libnet80211.a','wl_cnx.o','cnx_sta_pm.part.0'),
         ('libpp.a','pm.o','pm_tx_data_done_process'),
         ('libpp.a','pm.o','pm_tx_null_data_done_process'),
         ('libpp.a','pm.o','pm_keep_alive_timeout_process')}


def definitions(data):
    """Read only complete defined function names from a saved source object."""
    elf=ELFFile(io.BytesIO(data));table=elf.get_section_by_name('.symtab')
    return [s.name for s in table.iter_symbols() if s['st_info']['type']=='STT_FUNC'
            and isinstance(s['st_shndx'],int) and s['st_size']]


def complete(linked,source,name,locals_):
    """Match every instruction and enforce real linked callee/data identities."""
    symbol,code=linked.body(name)
    row=match(model(source,name),code,symbol['st_value'],unique(linked.symbols,'__global_pointer$')['st_value'])
    if row['linked_bytes']!=symbol['st_size']:raise ValueError('Incomplete keep-alive function: '+name)
    for b in row['symbol_bindings']:
        if b['kind']=='call' or b['binding']!='STB_LOCAL':
            wrapped=[s for s in linked.symbols if s.name=='__wrap_'+b['name'] and s['st_value']]
            expected=wrapped[0]['st_value'] if len(wrapped)==1 else unique(linked.symbols,b['name'])['st_value']
            if b['address']!=expected:raise ValueError('Wrong keep-alive linked target: '+b['name'])
        if b['binding']=='STB_LOCAL':
            key=(sha(source),b['name'],b['section'])
            if key in locals_ and locals_[key]!=b['address']:raise ValueError('Inconsistent keep-alive local anchor')
            locals_[key]=b['address']
    row['linked_code_sha256']=sha(code)
    return row


def verify(elf,app,libraries,object_data,timer_object,timer_source):
    """Reject a missing/bypassed replacement and bind real ms/us/disarm implementations."""
    linked=LinkedRuntime(elf,app);symbols=linked.symbols
    replacement=linked.symbol(REPLACEMENT);alias=unique(symbols,SDK_NAME)
    if alias['st_value']!=replacement['st_value']:raise ValueError('Keep-alive redirect is not active')
    for name,size in (('g_pm',584),('g_pm_cfg',76)):
        if unique(symbols,name)['st_size']!=size:raise ValueError('Requalify private PM geometry')
    if unique(symbols,'g_osi_funcs_p')['st_value']!=0x3fcdfdd8:raise ValueError('Requalify C2 OSI pointer')
    own=definitions(object_data)
    if REPLACEMENT not in own or not 1<=len(own)<=4:raise ValueError('Requalify replacement translation unit')
    locals_={};own_rows=[complete(linked,object_data,name,locals_) for name in own]
    references=[];objects={};archive_hashes={}
    for archive in sorted(libraries.glob('*.a')):
        raw=archive.read_bytes();archive_hashes[archive.name]=sha(raw)
        if archive.name in LIBRARIES and sha(raw)!=LIBRARIES[archive.name]:raise ValueError('Changed keep-alive SDK library')
        for member,data in members(raw):
            if data[:4]!=b'\x7fELF':continue
            obj=ELFFile(io.BytesIO(data));table=obj.get_section_by_name('.symtab')
            if table is None:continue
            funcs=[s for s in table.iter_symbols() if s['st_info']['type']=='STT_FUNC' and isinstance(s['st_shndx'],int)]
            for section in obj.iter_sections():
                if not isinstance(section,RelocationSection) or not obj.get_section(section['sh_info'])['sh_flags']&2:continue
                names=obj.get_section(section['sh_link'])
                for r in section.iter_relocations():
                    if names.get_symbol(r['r_info_sym']).name!=SDK_NAME:continue
                    owners=[s.name for s in funcs if s['st_shndx']==section['sh_info'] and s['st_value']<=r['r_offset']<s['st_value']+s['st_size']]
                    if len(owners)!=1 or (archive.name,member,owners[0]) not in CALLERS:
                        raise ValueError('Unqualified additional keep-alive reference')
                    references.append(dict(archive=archive.name,member=member,owner=owners[0],offset=r['r_offset'],type=r['r_info_type']))
                    objects[archive.name,member]=data
    if not LIBRARIES.keys()<=archive_hashes.keys():raise ValueError('Missing keep-alive libraries')
    if len(references)!=4 or {(r['archive'],r['member'],r['owner']) for r in references}!=CALLERS:
        raise ValueError('Keep-alive caller inventory changed')
    callers=[]
    for archive,member,name in sorted(CALLERS):
        row=complete(linked,objects[archive,member],name,locals_)
        targets=[b for b in row['symbol_bindings'] if b['name']==SDK_NAME]
        if len(targets)!=1 or targets[0]['address']!=replacement['st_value']:
            raise ValueError('A keep-alive caller bypasses the replacement')
        callers.append(row)
    pm=objects['libpp.a','pm.o']
    disable=complete(linked,pm,'pm_disable_keep_alive_timer',locals_)
    backend_names=('ets_timer_arm','ets_timer_arm_us','ets_timer_disarm')
    backends=[complete(linked,timer_object,name,locals_) for name in backend_names]
    # The selected SDK source explicitly promotes ms before multiplying. The
    # compiled object is separately bound above; runtime tests exercise its ABI.
    if sha(timer_source)!=TIMER_SOURCE_SHA or b'uint64_t time_us = 1000LL * (uint64_t) time_ms;' not in timer_source:
        raise ValueError('Timer millisecond conversion source changed')
    table=adapter_table(linked.read,'native',symbols)
    return dict(schema='small-tv-wifi-keep-alive-linkage-v1',passed=True,elf_sha256=sha(elf),app_sha256=sha(app),
        replacement_object_sha256=sha(object_data),timer_object_sha256=sha(timer_object),timer_source_sha256=sha(timer_source),
        sdk_archives_sha256=archive_hashes,sdk_objects_sha256={a+':'+m:sha(data) for (a,m),data in objects.items()},
        replacement=dict(name=REPLACEMENT,address=replacement['st_value'],bytes=replacement['st_size']),
        sdk_alias=dict(name=SDK_NAME,address=alias['st_value'],section=alias['st_shndx']),
        g_pm=unique(symbols,'g_pm')['st_value'],g_pm_cfg=unique(symbols,'g_pm_cfg')['st_value'],
        osi_pointer=unique(symbols,'g_osi_funcs_p')['st_value'],osi_table=table,
        functions=own_rows,callers=callers,disable=disable,backends=backends,sdk_references=references,
        full_runtime_lifecycle_proved=False,whole_image_completeness_proved=False,physical_hardware_tested=False)


def main():
    """Verify saved local build artifacts before allowing the archive step."""
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('elf','app','sdk-libraries','object','timer-object','timer-source','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve existing keep-alive guard report')
    files=[args.elf,args.app,args.object,args.timer_object,args.timer_source,*sorted(args.sdk_libraries.glob('*.a'))]
    if args.output.resolve() in [p.resolve() for p in files]:raise ValueError('Keep-alive report aliases input')
    pins={str(path.resolve()):sha(path.read_bytes()) for path in files}
    result=verify(args.elf.read_bytes(),args.app.read_bytes(),args.sdk_libraries,args.object.read_bytes(),
                  args.timer_object.read_bytes(),args.timer_source.read_bytes())
    if not all(sha(Path(p).read_bytes())==digest for p,digest in pins.items()):raise ValueError('Keep-alive inputs changed')
    result.update(inputs_sha256=pins,inputs_unchanged=True)
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,caller_count=len(result['callers']),backend_count=len(result['backends']))))


if __name__=='__main__':main()
