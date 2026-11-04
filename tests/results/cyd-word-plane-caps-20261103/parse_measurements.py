"""Reviewed pure UART parser; no captured module is imported or executed."""
import re

def need(value, reason):
    if not value:
        raise ValueError(reason)

def fields(line):
    tag,*parts=line.split();pairs=[part.split('=',1) for part in parts]
    need(pairs and all(len(part)==2 for part in pairs) and len({p[0] for p in pairs})==len(pairs),'complete unique public observation fields')
    words={'sdk','kind','phase'};row={}
    for key,value in pairs:
        if key in words:row[key]=value
        else:need(re.fullmatch('[0-9]+',value),'strict actual public integer field');row[key]=int(value)
    return tag,row

def parse(log):
    need(not re.search(r'CYD_WORD_FAILURE|Guru Meditation|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack (?:overflow|smashing)',log,re.I),'no real access/resource/runtime assertion failure')
    lines=[line for line in log.replace('\r\n','\n').splitlines() if line.startswith('CYD_WORD_')]
    rows=[fields(line) for line in lines]
    def select(tag):return [row for found,row in rows if found=='CYD_WORD_'+tag]
    known={'BOOT','LIMITS','HEAP','ALLOC','POINTER','ACCESS','FREE','CASE','COMPLETE'}
    need(all(tag.removeprefix('CYD_WORD_') in known for tag,_ in rows),'only declared complete public records')
    need(select('BOOT')==[dict(sdk='v6.0.2',public_caps=1,physical_hardware=0,decoder=0,private_heap=0)],'isolated actual pinned SDK boot')
    limits=select('LIMITS');need(len(limits)==1,'actual public SoC/capability definitions');limits=limits[0]
    need({k:limits[k] for k in ('iram_low','pure_iram_high','iram_high','diram_iram_low','diram_iram_high','diram_dram_low','diram_dram_high','dram_low','dram_high')}==dict(
        iram_low=0x40080000,pure_iram_high=0x400a0000,iram_high=0x400aa000,diram_iram_low=0x400a0000,diram_iram_high=0x400c0000,
        diram_dram_low=0x3ffe0000,diram_dram_high=0x40000000,dram_low=0x3ffae000,dram_high=0x40000000),'pinned classic ESP32 public regions')
    need({k:limits[k] for k in ('cap_internal','cap32','cap8','cap_exec')}==dict(cap_internal=2048,cap32=2,cap8=4,cap_exec=1),'actual public capability bits')
    boot=[]
    for match in re.finditer(r'heap_init: At ([0-9A-Fa-f]{8}) len ([0-9A-Fa-f]{8}) .*: (DRAM|D/IRAM|IRAM)\r?$',log,re.M):
        start=int(match[1],16);size=int(match[2],16);boot.append(dict(start=start,bytes=size,end=start+size,kind=match[3]))
    pure_extent=sum(max(0,min(row['end'],limits['pure_iram_high'])-max(row['start'],limits['iram_low'])) for row in boot if row['kind']=='IRAM')
    need(boot and pure_extent>0,'probe initial pure-IRAM boot extent is observed separately from native06 and current free')
    cases=select('CASE');need([row['kind'] for row in cases]==['WORDS32','EXEC32'],'both separately labelled capability cases')
    observations=[]
    for case in cases:
        kind=case['kind'];caps=limits['cap_internal']|limits['cap32']|(limits['cap_exec'] if kind=='EXEC32' else 0)
        allocated=case['allocated'];attempted=case['attempted'];refused=case['refused']
        need(0<allocated<=8 and refused in (0,1) and attempted==allocated+refused and (attempted==8 or refused==1) and
             case['bytes_per_plane']==11520 and case['byte_control']==23040 and case['exact_cleanup']==1 and
             case['extra_RAM_inferred']==case['application_qualified']==0,'honest allocation/access scope; no extra-memory/application inference')
        alloc=[row for row in select('ALLOC') if row['kind']==kind];access=[row for row in select('ACCESS') if row['kind']==kind];freed=[row for row in select('FREE') if row['kind']==kind]
        need(len(alloc)==attempted and [row['slot'] for row in alloc]==list(range(attempted)) and all(row['caps']==caps and row['bytes']==11520 for row in alloc),'every real public plane allocation request retained')
        need([row['success'] for row in alloc]==[1]*allocated+[0]*refused and all(bool(row['pointer'])==bool(row['success']) for row in alloc),'actual successful and refused allocation results')
        pointers=[row for row in select('POINTER') if row['kind']==kind]
        need(len(pointers)==len(access)==len(freed)==allocated,'every successful plane classified/accessed/freed once')
        physical=[]
        for index,(request,pointer,checked,closed) in enumerate(zip(alloc,pointers,access,freed)):
            p=pointer['pointer'];size=pointer['bytes'];last=p+size-4
            need(pointer['slot']==checked['slot']==closed['slot']==index and p==request['pointer']==closed['pointer'] and
                 pointer['caps']==caps and pointer['internal']==1 and not p%4 and size==11520 and pointer['alias_dereferenced']==0 and closed['real_returned']==1,'original aligned public word-plane ownership and no alias access')
            pure=limits['iram_low']<=p and p+size<=limits['pure_iram_high']
            diram_i=limits['diram_iram_low']<=p and p+size<=limits['diram_iram_high'];diram_d=limits['diram_dram_low']<=p and p+size<=limits['diram_dram_high']
            dram=limits['dram_low']<=p<limits['dram_high'];iram=limits['iram_low']<=p<limits['iram_high']
            need(pointer['pure_iram']==pure and pointer['diram_iram']==diram_i and pointer['diram_dram']==diram_d and pointer['in_dram']==dram and pointer['in_iram']==iram and pointer['byte_accessible']==dram,
                 'actual pointer classes match independent public address definitions')
            # SDK6.0.2's public address predicate stops at SOC_IRAM_HIGH.
            # EXEC-capable heap aliases can extend to SOC_DIRAM_IRAM_HIGH;
            # preserve the actual predicate result rather than infer it from
            # the allocation request. No instruction execution is tested.
            need(pointer['executable']==iram,'actual public executable-address query matches its pinned SDK windows')
            if diram_i:
                first_alias=limits['diram_dram_high']-(p-limits['diram_iram_low'])-4;last_alias=limits['diram_dram_high']-(last-limits['diram_iram_low'])-4
                canonical=min(first_alias,last_alias)
            elif diram_d:
                first_alias=limits['diram_iram_low']+limits['diram_dram_high']-p-4;last_alias=limits['diram_iram_low']+limits['diram_dram_high']-last-4;canonical=p
            else:first_alias=last_alias=0;canonical=p
            need((pure or dram or diram_i) and pointer['alias_first_word']==first_alias and pointer['alias_last_word']==last_alias,'D/IRAM aliases are independently identified, never counted as extra physical RAM')
            need(all(canonical+size<=left or canonical>=right for left,right in physical),'no two live planes overlap in physical address space');physical.append((canonical,canonical+size))
            need(checked==dict(kind=kind,slot=index,samples=5760,clear=1,whole_pattern=1,odd_rmw=1,volatile32_only=1),'complete actual word helper clear/store/load/RMW access')
        heaps=[row for row in select('HEAP') if row['kind']==kind]
        expected=[('BEFORE',0),('SCRATCH',0)]+[(phase,index) for index in range(attempted) for phase in ('ALLOC_BEFORE','ALLOC_AFTER')]+[('HELD',0),('CLEANUP',0)]
        need([(row['phase'],row['slot']) for row in heaps]==expected,'public resources measured around every actual allocation and complete cleanup')
        keys=('free8','largest8','free32','largest32','free_exec','largest_exec')
        need(all(row['integrity']==1 and 0<=row['largest8']<=row['free8'] and 0<=row['largest32']<=row['free32'] and 0<=row['largest_exec']<=row['free_exec'] for row in heaps),'actual public capability resources and heap integrity')
        need(all(heaps[0][key]==heaps[-1][key] for key in keys),'all original public free/largest values restored after real cleanup')
        observations.append(dict(case=case,pointers=pointers,heap=heaps,pure_iram_requested_bytes=sum(row['bytes'] for row in pointers if row['pure_iram']),
            diram_alias_requested_bytes=sum(row['bytes'] for row in pointers if row['diram_dram'] or row['diram_iram'])))
    controls=select('POINTER');controls=[row for row in controls if row['kind']=='DRAM_CONTROL']
    need(len(controls)==2 and all(row['bytes']==23040 and row['caps']==limits['cap_internal']|limits['cap8'] and
         row['in_dram']==row['byte_accessible']==row['internal']==1 and limits['dram_low']<=row['pointer'] and row['pointer']+row['bytes']<=limits['dram_high'] for row in controls),
         'separate control workspace remains byte-capable DRAM')
    need(select('COMPLETE')==[dict(cases=2,word_plane_bytes=11520,plane_slots=8,diagnostic_yield_between_planes=1,all_planes_byte_or_FP_access=0,hardware=0,application_memory_qualified=0,integrity=1)] and rows[-1][0]=='CYD_WORD_COMPLETE','one complete isolated public-capability access observation')
    return dict(cases=observations,limits=limits,DRAM_controls=controls,probe_initial_boot_regions=boot,probe_initial_pure_IRAM_extent=pure_extent,
        initial_extent_is_not_current_free=True,full_application_memory_qualified=False,extra_RAM_inferred=False)
