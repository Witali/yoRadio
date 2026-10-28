"""Bind null-frame callbacks and the BSS Max Idle producer chain in both images."""
from audit_factory_xrefs import Image,sha
from reverse.elf_archive import members
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import model,match
from reverse.timer_event11_match import objects,unique
from reverse.tx_null import qualify as null_qualify

NET_SHA={'factory':'8f989ecd7104520083727442247aed08ad93ef2bc304ae727022f8573f4bc558',
         'native':'c2df6fcca4c1c19c9c6b8171f16461e52a636da90dd7f7be3b67bed4fbe71cca'}
ROOTS={
    'pm_send_sleep_null_cb':('pm.o',0x420760b2),
    'pm_send_wake_null_cb':('pm.o',0x420760be),
    'pm_go_to_wake':('pm.o',0x42075bce),
    'pm_attach':('pm.o',0x42076792),
    'ieee80211_pm_tx_null_process':('ieee80211_output.o',0x4205a63a),
    'wifi_hmac_init':('ieee80211_ioctl.o',0x42065f0c),
    'cnx_sta_pm.part.0':('wl_cnx.o',0x42069f1e),
    'sta_recv_assoc':('ieee80211_sta.o',0x4206ebde),
    'ieee80211_set_bss_max_idle_period':('ieee80211_sta.o',0x4206d90e),
    'sta_is_bss_max_idle_enabled':('ieee80211_sta.o',None),
}


def qualify(factory,reference,native,app,old_pp,new_pp,old_net,new_net,replacements=None):
    """Match full bodies, public/absolute symbols and object-scoped local anchors."""
    prior=null_qualify(factory,reference,native,app,old_pp,new_pp)
    image,linked=Image(factory),LinkedRuntime(native,app)
    layouts={}
    for variant,pp,net in (('factory',old_pp,old_net),('native',new_pp,new_net)):
        raw=net.read_bytes()
        if sha(raw)!=NET_SHA[variant]:raise ValueError('Unexpected producer net80211 library')
        parts=objects(pp,variant)
        required={member for member,_ in ROOTS.values()}-{'pm.o'}
        for member,data in members(raw):
            if member in required:
                if member in parts:raise ValueError('Duplicate producer object')
                parts[member]=data
        if not required<=parts.keys():raise ValueError('Missing producer objects')
        selected=prior['layouts'][variant];base=selected['prior']
        anchors={r['name']:int(r['start'],0) for r in (*base['functions'],base['configuration_function'],*selected['functions'])}
        anchors.update({name:address for name,(_,address) in ROOTS.items() if address is not None}
                       if variant=='factory' else {name:unique(linked.symbols,name)['st_value'] for name in ROOTS})
        globals_,locals_,rows={},{},[]
        # Seed PM anchors from the already qualified parent/helper closure.
        for row in (*base['functions'][1:],base['configuration_function'],*selected['functions']):
            for b in row['symbol_bindings']:
                if b['binding']=='STB_LOCAL':locals_[('pm.o',b['name'],b['section'])]=b['address']
                else:globals_[b['name']]=b['address']
        for name,(member,address) in ROOTS.items():
            spec=model(parts[member],name)
            if variant=='factory':
                if address is None:
                    address=next(b['address'] for r in rows for b in r['symbol_bindings'] if b['name']==name)
                start=address;code=image.read(start,len(spec['code'])+64,True)
            else:symbol,code=linked.body(name);start=symbol['st_value']
            if replacements and (variant,name) in replacements:code=replacements[variant,name]
            row=match(spec,code,start,base['gp'])
            if variant=='native' and row['linked_bytes']!=symbol['st_size']:raise ValueError('Incomplete producer body')
            for b in row['symbol_bindings']:
                key=(member,b['name'],b['section'])
                if b['binding']=='STB_LOCAL':
                    if key in locals_ and locals_[key]!=b['address']:raise ValueError('Different producer local anchor')
                    locals_[key]=b['address']
                else:
                    if b['name'] in globals_ and globals_[b['name']]!=b['address']:raise ValueError('Different producer shared target')
                    globals_[b['name']]=b['address']
                if b['name'] in anchors and anchors[b['name']]!=b['address']:raise ValueError('Producer calls another selected function')
                if variant=='native' and (b['kind']=='call' or b['binding']!='STB_LOCAL'):
                    if unique(linked.symbols,b['name'])['st_value']!=b['address']:raise ValueError('Wrong producer native symbol')
            row['linked_code_sha256']=sha(code[:row['linked_bytes']]);row['source_object']=member;rows.append(row)
            anchors[name]=start
        getter=next(row for row in rows if row['name']=='sta_is_bss_max_idle_enabled')
        cfg=[b['address'] for b in getter['symbol_bindings'] if b['kind']=='data']
        if len(cfg)!=1:raise ValueError('Ambiguous menuconfig anchor')
        layouts[variant]=dict(prior=selected,functions=rows,g_ic=globals_['g_ic'],menuconfig=cfg[0],
            sdk_objects_sha256={name:sha(data) for name,data in parts.items()},net_library_sha256=sha(raw))
    return dict(schema='wifi-producer-linkage-v1',layouts=layouts,factory_elf_sha256=sha(factory),
        reference_elf_sha256=sha(reference),native_elf_sha256=sha(native),native_app_sha256=sha(app),
        runtime_registration_proved=False,station_pointer_lifetime_proved=False,
        whole_image_completeness_proved=False,physical_hardware_tested=False)
