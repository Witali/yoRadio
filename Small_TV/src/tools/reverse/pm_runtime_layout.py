"""Qualify typed runtime reads for the real PM timer and ROM state binding."""
import io

from elftools.elf.elffile import ELFFile

from audit_factory_xrefs import Image,sha
from reverse.rv32_link_match import branch_target,link_register
from reverse.timer_event11_match import unique
from reverse.timer_pm_lifecycle import qualify as lifecycle


def field(die,name):
    """Require one named DWARF member with a constant offset and scalar size."""
    rows=[f for f in die.iter_children() if f.tag=='DW_TAG_member'
          and f.attributes.get('DW_AT_name') and f.attributes['DW_AT_name'].value==name.encode()]
    if len(rows)!=1:raise ValueError('Missing/ambiguous timer DWARF field')
    row=rows[0];offset=row.attributes.get('DW_AT_data_member_location')
    if not offset or not isinstance(offset.value,int):raise ValueError('Nonconstant timer field')
    target=row.get_DIE_from_attribute('DW_AT_type')
    for _ in range(16):
        if 'DW_AT_byte_size' in target.attributes:return dict(offset=offset.value,size=target.attributes['DW_AT_byte_size'].value)
        target=target.get_DIE_from_attribute('DW_AT_type')
    raise ValueError('Unresolved timer field type')


def native_types(elf):
    """Derive layouts from the actual linked C2 compilation units, not a guessed SDK ABI."""
    found={}
    for cu in elf.get_dwarf_info().iter_CUs():
        name=cu.get_top_DIE().attributes.get('DW_AT_name')
        name=name.value.decode(errors='strict').replace('\\','/') if name else ''
        if name.rsplit('/',1)[-1] not in ('esp_timer.c','ets_timer_legacy.c'):continue
        for die in cu.iter_DIEs():
            label=die.attributes.get('DW_AT_name')
            label=label.value.decode() if label else ''
            if die.tag!='DW_TAG_structure_type' or label not in ('esp_timer','_ETSTIMER_') or 'DW_AT_byte_size' not in die.attributes:continue
            selected=('alarm',) if label=='esp_timer' else ('timer_expire','timer_arg')
            value=dict(size=die.attributes['DW_AT_byte_size'].value,fields={n:field(die,n) for n in selected})
            if label in found and found[label]!=value:raise ValueError('Inconsistent timer DWARF definitions')
            found[label]=value
    expected={'esp_timer':dict(size=32,fields={'alarm':dict(offset=0,size=8)}),
              '_ETSTIMER_':dict(size=20,fields={'timer_expire':dict(offset=4,size=4),'timer_arg':dict(offset=16,size=4)})}
    if found!=expected:raise ValueError('Requalify linked native timer layouts')
    return found


def qualify(factory,native,old_pp,new_pp,rom):
    """Bind factory layout to actual reads/predicates and native layout to its DWARF."""
    previous=lifecycle(factory,native,old_pp,new_pp,rom)
    image=Image(factory);elf=ELFFile(io.BytesIO(native))
    symbols=list(elf.get_section_by_name('.symtab').iter_symbols())
    predicate=image.read(0x40384076,14,True)
    if predicate!=bytes.fromhex('1c41584133e5e7003335a0008280'):raise ValueError('Changed factory alarm predicate')
    call=image.read(0x40384600,4,True)
    if link_register(call)!=1 or branch_target(call,0x40384600)!=0x40384076:
        raise ValueError('Factory stop does not use the qualified alarm predicate')
    marker=image.read(0x40384632,18,True)
    # The initialized marker helper is independently exercised by the host test.
    if marker!=bytes.fromhex('4841b7f7eded9387e7de3e95133515008280'):
        raise ValueError('Changed factory initialized-marker predicate')
    read_handle=image.read(0x403847b0,6,True)
    if read_handle[:2]!=bytes.fromhex('0848') or branch_target(read_handle[2:],0x403847b2)!=0x403845dc:
        raise ValueError('Factory legacy disarm uses a different backend handle')
    native_abi=native_types(elf)
    cancel=unique(symbols,'pm_disable_keep_alive_timer')
    if (cancel['st_value'],cancel['st_size'])!=(0x4207a0e6,22):
        raise ValueError('Requalify native keep-alive cancellation entry')
    cancel_code=next(s.data()[cancel['st_value']-s['sh_addr']:cancel['st_value']-s['sh_addr']+22]
                     for s in elf.iter_sections() if s['sh_flags']&4 and
                     s['sh_addr']<=cancel['st_value']<cancel['st_value']+22<=s['sh_addr']+s['sh_size'])
    if cancel_code!=bytes.fromhex('b707ce3f83a787dd3765cb3f1305c5b683a7470e8287'):
        raise ValueError('Changed native keep-alive cancellation body')
    connected=unique(symbols,'connected')
    if connected['st_size']!=1:raise ValueError('Unexpected connected flag width')
    layouts={}
    for variant,layout in previous['layouts'].items():
        base=layout['prior']['prior']
        stop=next(f for f in layout['prior']['functions'] if f['name']=='pm_stop')
        stop_exit=int(stop['end'],0)-12
        code=(image.read(stop_exit,12,True) if variant=='factory' else
              next(s.data()[stop_exit-s['sh_addr']:stop_exit-s['sh_addr']+12] for s in elf.iter_sections()
                   if s['sh_flags']&4 and s['sh_addr']<=stop_exit<stop_exit+12<=s['sh_addr']+s['sh_size']))
        if code!=bytes.fromhex('f2406244d244424905618280'):raise ValueError('Unknown PM stop epilogue')
        layouts[variant]=dict(pm=base['g_pm'],pm_bytes=base['g_pm_bytes'],config=base['g_pm_cfg'],
            osi_pointer=base['osi_pointer'],osi_table=base['osi_table']['address'],rom_pm_pointer=layout['rom']['pointer'],
            connected=0x3fcc3a74 if variant=='factory' else connected['st_value'],
            connected_value=2 if variant=='factory' else 1,connected_max=5 if variant=='factory' else 1,stop_exit=stop_exit,
            backend_min_bytes=8 if variant=='factory' else native_abi['esp_timer']['size'],
            legacy_timer_offset=492,legacy_size=20,marker_offset=4,handle_offset=16,alarm_offset=0,alarm_bytes=8)
        if variant=='native':layouts[variant]['cancel_entry']=cancel['st_value']
    return dict(schema='pm-runtime-layout-v1',layouts=layouts,native_dwarf=native_abi,
        native_cancel_body=dict(start=cancel['st_value'],bytes_hex=cancel_code.hex(),sha256=sha(cancel_code)),
        factory_predicates=[dict(name='alarm_nonzero',start=0x40384076,bytes_hex=predicate.hex(),sha256=sha(predicate)),
                            dict(name='legacy_initialized',start=0x40384632,bytes_hex=marker.hex(),sha256=sha(marker))],
        factory_elf_sha256=sha(factory),native_elf_sha256=sha(native),rom_sha256=sha(rom),
        physical_hardware_tested=False,whole_image_completeness_proved=False)
