"""Read public word-allocation telemetry as data, never execute a capture.

This proves the observed pointer/counter trace, not codec correctness, a real
OOM injection, private replacement transactions or full application headroom.
The separate heap getters are not an atomic snapshot of other tasks' heaps.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
LIMITS=dict(iram_low=0x40080000,pure_iram_high=0x400a0000,iram_high=0x400aa000,
    diram_iram_low=0x400a0000,diram_iram_high=0x400c0000,
    diram_dram_low=0x3ffe0000,diram_dram_high=0x40000000,
    dram_low=0x3ffae000,dram_high=0x40000000,cap_internal=2048,cap32=2,cap8=4,
    owner_core=1,owner_priority=5,owner_published=1)
COUNT_KEYS=('attempts','successes','live_planes','peak_planes','live_bytes','peak_bytes','frees','refusals')
POINTER_KEYS=('internal','byte_accessible','executable','in_dram','in_iram','diram_dram','diram_iram',
              'pure_iram','alias_first_word','alias_last_word','alias_dereferenced')
HEAP_KEYS={'fixture','operation','stage','allocation','generation','bytes','caps','pointer','real_returned',
    *COUNT_KEYS,'inflight','live_decoders','free8','largest8','free32','largest32',
    'heap_snapshot_atomic',*POINTER_KEYS,'time_us','core','priority'}
COMPLETE_KEYS={*COUNT_KEYS,'inflight','owner_only_table','atomic_counters','final_maintenance',
    'diagnostic_delays','private_heap','application_memory_qualified','hardware'}

def need(value,reason):
    if not value:raise ValueError(reason)

def record(line):
    parts=line.split();need(parts,'nonempty record');tag=parts[0];row={}
    for part in parts[1:]:
        need(part.count('=')==1,'one complete field assignment')
        key,value=part.split('=');need(key not in row,'no duplicate fields')
        if key in ('fixture','operation','stage'):
            need(re.fullmatch('[A-Za-z0-9_]+',value),'bounded observation label');row[key]=value
        else:
            need(re.fullmatch('[0-9]+',value),'unsigned decimal public field')
            row[key]=int(value);need(row[key]<2**64,'bounded public integer')
    return tag,row

def pointer_class(pointer,bytes):
    empty={key:0 for key in POINTER_KEYS}
    if not pointer:return empty,None
    need(pointer<2**32 and not pointer%4 and pointer+bytes<=2**32,'aligned classic ESP32 pointer extent')
    last=pointer+bytes-4
    pure=LIMITS['iram_low']<=pointer and pointer+bytes<=LIMITS['pure_iram_high']
    dram=LIMITS['dram_low']<=pointer<LIMITS['dram_high']
    iram=LIMITS['iram_low']<=pointer<LIMITS['iram_high']
    diram_i=LIMITS['diram_iram_low']<=pointer and pointer+bytes<=LIMITS['diram_iram_high']
    diram_d=LIMITS['diram_dram_low']<=pointer and pointer+bytes<=LIMITS['diram_dram_high']
    need(pure or (dram and pointer+bytes<=LIMITS['dram_high']) or diram_i,'one complete permitted internal RAM range')
    if diram_i:
        first_alias=LIMITS['diram_dram_high']-(pointer-LIMITS['diram_iram_low'])-4
        last_alias=LIMITS['diram_dram_high']-(last-LIMITS['diram_iram_low'])-4
        canonical=min(first_alias,last_alias)
    elif diram_d:
        first_alias=LIMITS['diram_iram_low']+LIMITS['diram_dram_high']-pointer-4
        last_alias=LIMITS['diram_iram_low']+LIMITS['diram_dram_high']-last-4
        canonical=pointer
    else:first_alias=last_alias=0;canonical=pointer
    # The pinned public executable predicate stops at SOC_IRAM_HIGH, even
    # though a legal shared D/IRAM allocator alias can extend farther.
    expected=dict(internal=1,byte_accessible=int(dram),executable=int(iram),in_dram=int(dram),
        in_iram=int(iram),diram_dram=int(diram_d),diram_iram=int(diram_i),pure_iram=int(pure),
        alias_first_word=first_alias,alias_last_word=last_alias,alias_dereferenced=0)
    return expected,(canonical,canonical+bytes)

def parse_word_allocation_log(log,require_terminal=True):
    records=[]
    for line in log.replace('\r\n','\n').splitlines():
        if 'CYD_F1_WORD_' not in line:continue
        need(line.startswith('CYD_F1_WORD_'),'interleaved word record is not complete evidence')
        records.append(record(line))
    need(records and records[0]==('CYD_F1_WORD_LIMITS',LIMITS),'one exact pinned public memory/owner definition')
    state={key:0 for key in COUNT_KEYS};owned={};pending=None;terminal=None;clock=0
    paired=0;observations=[];peak_pure=peak_shared=0
    for tag,row in records[1:]:
        need(terminal is None,'no records after the terminal census')
        if tag=='CYD_F1_WORD_COMPLETE':
            need(set(row)==COMPLETE_KEYS and pending is None,'complete terminal fields and all real returns paired')
            need(all(row[key]==state[key] for key in COUNT_KEYS),'terminal counters equal every observed allocation/free')
            need(state['attempts']>0 and state['successes']>0 and not owned and state['live_planes']==state['live_bytes']==0 and
                 state['successes']==state['frees'] and row['inflight']==0,'terminal zero live planes/bytes and real frees')
            need({key:row[key] for key in ('owner_only_table','atomic_counters','final_maintenance','diagnostic_delays','private_heap','application_memory_qualified','hardware')}==
                 dict(owner_only_table=1,atomic_counters=1,final_maintenance=1,diagnostic_delays=0,private_heap=0,application_memory_qualified=0,hardware=0),
                 'owner synchronization and narrow diagnostic scope')
            terminal=row;continue
        need(tag=='CYD_F1_WORD_HEAP' and set(row)==HEAP_KEYS,'only complete declared word heap records')
        need(row['operation'] in ('ALLOC','FREE') and row['stage'] in ('BEFORE','AFTER'),'public operation and stage')
        need(row['core']==1 and row['priority']==5 and row['generation']>0 and row['allocation']>0,'actual published decoder owner and source generation')
        need(4<=row['bytes']<=11520 and not row['bytes']%4 and row['caps']==2050,'unchanged rounded INTERNAL|32BIT plane request')
        need(row['heap_snapshot_atomic']==0 and all(row[key]<2**32 for key in ('free8','largest8','free32','largest32')),
             'separate public heap observations; no exclusive delta inference')
        need(0<=row['live_decoders']<=8 and row['time_us']>=clock,'bounded public handles and monotonic owner records');clock=row['time_us']
        classification,interval=pointer_class(row['pointer'],row['bytes'])
        need(all(row[key]==classification[key] for key in POINTER_KEYS),'public pointer flags and same-memory aliases match pinned SDK')
        if row['stage']=='BEFORE':
            need(pending is None and row['real_returned']==0 and row['inflight']==1,'one owner operation before the real public call')
            if row['operation']=='ALLOC':
                state['attempts']+=1
                need(row['allocation']==state['attempts'] and row['pointer']==0,'every sequential real allocation request starts without a result')
            else:
                need(row['allocation'] in owned,'free refers to a still-live successful allocation')
                original=owned[row['allocation']]['row']
                need(all(row[key]==original[key] for key in ('fixture','allocation','generation','bytes','caps','pointer')),'free exact original pointer, request and source')
            pending=row
        else:
            need(pending is not None and row['real_returned']==1 and row['inflight']==0,'actual public call returned before its AFTER record')
            need(all(row[key]==pending[key] for key in ('fixture','operation','allocation','generation','bytes','caps')),'matching real public-call pair')
            if row['operation']=='ALLOC':
                if row['pointer']:
                    need(all(interval[1]<=old['interval'][0] or interval[0]>=old['interval'][1] for old in owned.values()),
                         'no simultaneous pointers overlap through either physical D/IRAM alias')
                    owned[row['allocation']]=dict(row=row,interval=interval)
                    state['successes']+=1;state['live_planes']+=1;state['live_bytes']+=row['bytes']
                    state['peak_planes']=max(state['peak_planes'],state['live_planes'])
                    state['peak_bytes']=max(state['peak_bytes'],state['live_bytes'])
                    peak_pure=max(peak_pure,sum(x['row']['bytes'] for x in owned.values() if x['row']['pure_iram']))
                    peak_shared=max(peak_shared,sum(x['row']['bytes'] for x in owned.values() if x['row']['diram_dram'] or x['row']['diram_iram']))
                else:state['refusals']+=1
            else:
                need(row['pointer']==pending['pointer'],'exact original pointer passed through the real free')
                del owned[row['allocation']];state['frees']+=1;state['live_planes']-=1;state['live_bytes']-=row['bytes']
            pending=None;paired+=1
        need(all(row[key]==state[key] for key in COUNT_KEYS),'all cumulative/live/peak counters equal the observed operations')
        need(state['live_planes']<=16 and state['live_bytes']<=16*11520 and state['attempts']==state['successes']+state['refusals']+(1 if pending and pending['operation']=='ALLOC' else 0),
             'bounded old-plus-candidate ownership and honest refusals')
        observations.append(row)
    need(not require_terminal or terminal is not None,'complete terminal word census is required')
    return dict(completed=terminal is not None,counts=state,paired_public_calls=paired,
        records=observations,terminal=terminal,unpaired_public_call=pending,
        peak_requested_pure_IRAM_bytes=peak_pure,peak_requested_shared_D_IRAM_bytes=peak_shared,
        private_heap_inspected=False,extra_physical_RAM_inferred=False,application_memory_qualified=False,
        separate_heap_getters_are_not_atomic=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--allow-partial',action='store_true')
    args=parser.parse_args();out=args.output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh local data-only report')
    body=args.input.read_bytes();result=parse_word_allocation_log(body.decode('utf-8'),not args.allow_partial)
    result['input']=dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(completed=result['completed'],counts=result['counts'],application_memory_qualified=False)))

if __name__=='__main__':main()
