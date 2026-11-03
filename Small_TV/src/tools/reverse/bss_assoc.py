"""Bind complete association/BSS bodies before exercising malformed IE inputs."""
from audit_factory_xrefs import Image,sha,startup_gp,signed12
from reverse.elf_archive import members
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import model,match,branch_target,link_register
from reverse.wifi_producers import NET_SHA,ROOTS

FACTORY_SHA='8c9fd166a6536bc1bc236fc98018eb0daba9aad01ce8356511ad68eba03de882'
FUNCTIONS=('sta_recv_assoc','ieee80211_set_bss_max_idle_period','sta_is_bss_max_idle_enabled')


def factory_reference_sites(image,target,materialized=False):
    """Find actual direct calls or adjacent LUI/ADDI references to one known body."""
    found=[]
    for section in image.sections:
        if not section['execute']:continue
        data=section['data'];base=section['start']
        for offset in range(0,len(data)-8,2):
            pc=base+offset
            if materialized:
                high=int.from_bytes(data[offset:offset+4],'little');low=int.from_bytes(data[offset+4:offset+8],'little')
                if high&127!=55 or low&0x707f!=19 or (high>>7)&31!=(low>>15)&31 or (high>>7)&31!=(low>>7)&31:continue
                if ((high&0xfffff000)+signed12(low>>20))&0xffffffff==target:found.append(pc)
            else:
                for length in (2,4):
                    code=data[offset:offset+length]
                    if link_register(code)==1 and branch_target(code,pc)==target:found.append(pc)
    return sorted(set(found))


def find_factory_owner(image,source,name,gp,target,materialized=False):
    """Locate a complete owner around an anchored reference and reject lookalikes."""
    spec=model(source,name);first=spec['instructions'][0];matches={}
    for site in factory_reference_sites(image,target,materialized):
        for start in range(site-len(spec['code'])-64,site+1,2):
            try:
                if image.read(start,len(first),True)!=first:continue
                row=match(spec,image.read(start,len(spec['code'])+64,True),start,gp)
            except (AssertionError,ValueError):continue
            bindings=[b for b in row['symbol_bindings'] if b['name']=='sta_recv_assoc' and b['address']==target]
            if len(bindings)!=1:continue
            row['linked_code_sha256']=sha(image.read(start,row['linked_bytes'],True));matches[start]=row
    if len(matches)!=1:raise ValueError('Ambiguous complete factory association owner: '+name)
    return next(iter(matches.values()))


def selected(rows,name):
    """Require a single exact named binding rather than choosing a same-shaped helper."""
    values=[row for row in rows if row['name']==name]
    if len(values)!=1:raise ValueError('Ambiguous association anchor: '+name)
    return values[0]


def complete_association(linked,source,name,locals_):
    """Resolve public symbols in the public namespace and preserve object-local anchors."""
    symbol,code=linked.body(name)
    row=match(model(source,name),code,symbol['st_value'],linked.symbol('__global_pointer$')['st_value'])
    if row['linked_bytes']!=symbol['st_size']:raise ValueError('Incomplete linked association body')
    for binding in row['symbol_bindings']:
        if binding['binding']!='STB_LOCAL':
            wrapped=[s for s in linked.symbols if s.name=='__wrap_'+binding['name'] and s['st_value']]
            candidates=wrapped or [s for s in linked.symbols if s.name==binding['name'] and s['st_value']
                                   and s['st_info']['bind']!='STB_LOCAL']
            if len(candidates)!=1 or candidates[0]['st_value']!=binding['address']:
                raise ValueError('Wrong association public target: '+binding['name'])
        else:
            key=(sha(source),binding['name'],binding['section'])
            if key in locals_ and locals_[key]!=binding['address']:raise ValueError('Inconsistent association local anchor')
            locals_[key]=binding['address']
            if binding['kind']=='call':
                candidates=[s for s in linked.symbols if s.name==binding['name'] and s['st_value']==binding['address']
                            and s['st_info']['bind']=='STB_LOCAL' and s['st_info']['type']=='STT_FUNC']
                if len(candidates)!=1:raise ValueError('Unbound association local callee')
                local=candidates[0];matched=match(model(source,binding['name']),linked.read(local['st_value'],local['st_size'],True),
                    local['st_value'],linked.symbol('__global_pointer$')['st_value'])
                if matched['linked_bytes']!=local['st_size']:raise ValueError('Incomplete association local callee')
    row['linked_code_sha256']=sha(code)
    return row


def return_sites(row,target):
    """Derive direct-call return PCs from the completely matched instruction stream."""
    found=[]
    for event in row['transformations']:
        code=bytes.fromhex(event['linked_bytes']);pc=int(event['pc'],0)
        if event['kind'].startswith('call') and link_register(code)==1 and branch_target(code,pc)==target:
            found.append(pc+len(code))
    if len(found)!=1:raise ValueError('Expected one direct BSS setter call')
    return found[0]


def qualify(factory,native,app,old_net,new_net,replacements=None):
    """Match both full callers, real getter/setter and every original callee/data binding."""
    if sha(factory)!=FACTORY_SHA:raise ValueError('Unexpected factory association image')
    image,linked=Image(factory),LinkedRuntime(native,app);layouts={}
    for variant,path in (('factory',old_net),('native',new_net)):
        raw=path.read_bytes()
        if sha(raw)!=NET_SHA[variant]:raise ValueError('Unexpected association SDK archive')
        parts=dict(members(raw));source=parts['ieee80211_sta.o']
        gp=startup_gp(image) if variant=='factory' else linked.symbol('__global_pointer$')['st_value']
        read=image.read if variant=='factory' else linked.read
        anchors={name:ROOTS[name][1] for name in FUNCTIONS if ROOTS[name][1] is not None}
        if variant=='native':anchors={name:linked.symbol(name)['st_value'] for name in FUNCTIONS}
        foundations=[];locals_={}
        for name in FUNCTIONS:
            spec=model(source,name)
            if variant=='factory':
                if name not in anchors:
                    anchors[name]=selected(foundations[0]['symbol_bindings'],name)['address']
                start=anchors[name];code=read(start,len(spec['code'])+64,True)
                row=match(spec,code,start,gp)
            else:row=complete_association(linked,source,name,locals_)
            row['linked_code_sha256']=sha(read(int(row['start'],0),row['linked_bytes'],True))
            foundations.append(row)
        rows=[]
        for name,foundation in zip(FUNCTIONS,foundations):
            start=int(foundation['start'],0)
            code=read(start,foundation['linked_bytes'],True)
            if replacements and (variant,name) in replacements:code=replacements[variant,name]
            row=match(model(source,name),code,start,gp)
            if row['linked_bytes']!=foundation['linked_bytes']:raise ValueError('Incomplete association body')
            if row['symbol_bindings']!=foundation['symbol_bindings']:raise ValueError('Changed association call/data target')
            row['linked_code_sha256']=sha(code[:row['linked_bytes']]);rows.append(row)
        association,setter,getter=rows
        for name in FUNCTIONS[1:]:
            if selected(association['symbol_bindings'],name)['address']!=anchors[name]:
                raise ValueError('Association does not use the selected BSS function')
        menu=[b for b in getter['symbol_bindings'] if b['kind']=='data']
        if len(menu)!=1:raise ValueError('Ambiguous BSS feature object')
        owners=[]
        for name,member,materialized in (('sta_recv_mgmt','ieee80211_sta.o',False),
                                         ('net80211_funcs_init','ieee80211_api.o',True)):
            if variant=='factory':row=find_factory_owner(image,parts[member],name,gp,int(association['start'],0),materialized)
            else:row=complete_association(linked,parts[member],name,locals_)
            row['linked_code_sha256']=sha(read(int(row['start'],0),row['linked_bytes'],True));owners.append(row)
        management,registration=owners
        for row in owners:
            if selected(row['symbol_bindings'],'sta_recv_assoc')['address']!=int(association['start'],0):
                raise ValueError('Association ingress points at another body')
        osi_pointer=selected(management['symbol_bindings'],'g_osi_funcs_p')['address']
        table=0x3fcb459c if variant=='factory' else linked.symbol('g_wifi_osi_funcs')['st_value']
        assert int.from_bytes(read(table,4),'little')==(8 if variant=='factory' else 9)
        noop=int.from_bytes(read(table+412,4),'little');noop_code=read(noop,4,True)
        if noop_code!=bytes.fromhex('01458280'):raise ValueError('Requalify OSI slot 412 backend')
        if variant=='native' and linked.symbol('coex_wifi_release_wrapper')['st_value']!=noop:
            raise ValueError('Wrong native coexistence release target')
        osi_body=dict(name='osi-412-noop',start=hex(noop),end=hex(noop+4),linked_bytes=4,linked_code_sha256=sha(noop_code))
        layouts[variant]=dict(functions=[*rows,*owners,osi_body],gp=gp,menuconfig=menu[0]['address'],
            g_ic=selected(association['symbol_bindings'],'g_ic')['address'],
            after_bss=return_sites(association,int(setter['start'],0)),
            management_entry=int(management['start'],0),after_assoc=return_sites(management,int(association['start'],0)),
            hmac_counter=selected(management['symbol_bindings'],'g_hmac_cnt')['address'],
            osi_pointer=osi_pointer,osi_table=table,osi_412_target=noop,
            sdk_library_sha256=sha(raw),sdk_object_sha256=sha(source))
    return dict(schema='bss-association-linkage-v1',layouts=layouts,
        factory_elf_sha256=sha(factory),native_elf_sha256=sha(native),native_app_sha256=sha(app),
        entire_association_executed=False,external_rx_reachability_proved=False,
        physical_hardware_tested=False,whole_image_completeness_proved=False)
