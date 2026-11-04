"""Synthetic public-capability parser controls; no SDK/QEMU access is claimed."""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
READER=ROOT/'tests/run-cyd-word-plane-caps-qemu.py'


def need(value,reason):
    if not value:raise ValueError(reason)


def vectors():
    rows=[]
    def add(tag,**row):rows.append(('CYD_WORD_'+tag,row))
    add('BOOT',sdk='v6.0.2',public_caps=1,physical_hardware=0,decoder=0,private_heap=0)
    add('LIMITS',iram_low=0x40080000,pure_iram_high=0x400a0000,iram_high=0x400aa000,diram_iram_low=0x400a0000,diram_iram_high=0x400c0000,
        diram_dram_low=0x3ffe0000,diram_dram_high=0x40000000,dram_low=0x3ffae000,dram_high=0x40000000,cap_internal=2048,cap32=2,cap8=4,cap_exec=1)
    baseline=dict(free8=200000,largest8=150000,free32=300000,largest32=150000,free_exec=200000,largest_exec=150000)
    def heap(kind,phase,slot):add('HEAP',kind=kind,phase=phase,slot=slot,**baseline,integrity=1)
    for kind,caps in (('WORDS32',2050),('EXEC32',2051)):
        heap(kind,'BEFORE',0)
        add('POINTER',kind='DRAM_CONTROL',slot=0,caps=2052,pointer=0x3ffb8000,bytes=23040,internal=1,byte_accessible=1,executable=0,
            in_dram=1,in_iram=0,diram_dram=0,diram_iram=0,pure_iram=0,alias_first_word=0,alias_last_word=0,alias_dereferenced=0)
        heap(kind,'SCRATCH',0);pointers=[]
        for slot in range(8):
            p=0x4008c000+slot*11520 if slot<7 else (0x3ffc0000 if kind=='WORDS32' else 0x400a4000)
            pure=slot<7;dram=kind=='WORDS32' and slot==7;alias=kind=='EXEC32' and slot==7;pointers.append(p)
            first_alias=0x3ffffffc-(p-0x400a0000) if alias else 0;last_alias=first_alias-11516 if alias else 0
            heap(kind,'ALLOC_BEFORE',slot);add('ALLOC',kind=kind,slot=slot,bytes=11520,caps=caps,pointer=p,success=1);heap(kind,'ALLOC_AFTER',slot)
            add('POINTER',kind=kind,slot=slot,caps=caps,pointer=p,bytes=11520,internal=1,byte_accessible=int(dram),executable=int(not dram),
                in_dram=int(dram),in_iram=1-int(dram),diram_dram=0,diram_iram=int(alias),pure_iram=int(pure),alias_first_word=first_alias,alias_last_word=last_alias,alias_dereferenced=0)
            add('ACCESS',kind=kind,slot=slot,samples=5760,clear=1,whole_pattern=1,odd_rmw=1,volatile32_only=1)
        heap(kind,'HELD',0)
        for slot,p in enumerate(pointers):add('FREE',kind=kind,slot=slot,pointer=p,real_returned=1)
        heap(kind,'CLEANUP',0)
        add('CASE',kind=kind,attempted=8,allocated=8,refused=0,bytes_per_plane=11520,byte_control=23040,exact_cleanup=1,extra_RAM_inferred=0,application_qualified=0)
    add('COMPLETE',cases=2,word_plane_bytes=11520,plane_slots=8,diagnostic_yield_between_planes=1,all_planes_byte_or_FP_access=0,hardware=0,application_memory_qualified=0,integrity=1)
    return rows


def text(rows):
    return 'I (1) heap_init: At 4008C000 len 00014000 (80 KiB): IRAM\n'+'\n'.join(tag+' '+' '.join(key+'='+str(value) for key,value in row.items()) for tag,row in rows)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    out=parser.parse_args().output.resolve();need(out.is_relative_to(ROOT/'.build') and not out.exists(),'fresh synthetic parser result')
    spec=importlib.util.spec_from_file_location('current_public_word_caps_reader',READER);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    original=vectors();reader.parse(text(original))
    # The pinned SDK allocator may return this high D/IRAM instruction alias.
    # Its public executable-address predicate stops at0x400aa000, so BOTH
    # executable=0 and in_iram=0 are the faithful observations at this address.
    high_alias=copy.deepcopy(original);address=0x400bcd14
    first_alias=0x3ffffffc-(address-0x400a0000)
    for tag,row in high_alias:
        if row.get('kind')!='EXEC32' or row.get('slot')!=7:continue
        if tag in ('CYD_WORD_ALLOC','CYD_WORD_POINTER','CYD_WORD_FREE'):row['pointer']=address
        if tag=='CYD_WORD_POINTER':row.update(executable=0,in_iram=0,alias_first_word=first_alias,alias_last_word=first_alias-11516)
    need(reader.parse(text(high_alias))['cases'][1]['pointers'][7]['executable']==0,
        'high D/IRAM alias keeps the actual public address-query result')
    refusal=copy.deepcopy(original)
    refusal=[(tag,row) for tag,row in refusal if not (row.get('kind')=='WORDS32' and row.get('slot')==7 and tag in ('CYD_WORD_POINTER','CYD_WORD_ACCESS','CYD_WORD_FREE'))]
    for tag,row in refusal:
        if row.get('kind')=='WORDS32' and row.get('slot')==7 and tag=='CYD_WORD_ALLOC':row.update(pointer=0,success=0)
        if row.get('kind')=='WORDS32' and tag=='CYD_WORD_CASE':row.update(allocated=7,refused=1)
    need(reader.parse(text(refusal))['cases'][0]['case']['refused']==1,'actual NULL outcome remains an explicit resource observation')
    controls=[
        ('alias_is_not_pure_IRAM','POINTER',{'kind':'EXEC32','slot':7},{'pure_iram':1}),
        ('missing_alias_identity','POINTER',{'kind':'EXEC32','slot':7},{'alias_first_word':0}),
        ('wrong_alias_direction','POINTER',{'kind':'EXEC32','slot':7},{'alias_last_word':0x400a4000}),
        ('alias_dereferenced','POINTER',{'kind':'EXEC32','slot':7},{'alias_dereferenced':1}),
        ('word_pointer_misaligned','POINTER',{'kind':'WORDS32','slot':0},{'pointer':0x4008c001}),
        ('IRAM_byte_access_claim','POINTER',{'kind':'WORDS32','slot':0},{'byte_accessible':1}),
        ('EXEC_not_real','POINTER',{'kind':'EXEC32','slot':0},{'executable':0}),
        ('wrong_public_caps','ALLOC',{'kind':'WORDS32','slot':0},{'caps':2052}),
        ('refusal_relabelled_success','ALLOC',{'kind':'WORDS32','slot':0},{'pointer':0}),
        ('uninitialized_word_RMW','ACCESS',{'kind':'WORDS32','slot':0},{'clear':0}),
        ('incomplete_plane_check','ACCESS',{'kind':'WORDS32','slot':0},{'samples':5759}),
        ('halfword_access_allowed','ACCESS',{'kind':'WORDS32','slot':0},{'volatile32_only':0}),
        ('odd_RMW_not_checked','ACCESS',{'kind':'WORDS32','slot':0},{'odd_rmw':0}),
        ('missing_real_free','FREE',{'kind':'WORDS32','slot':0},None),
        ('wrong_freed_pointer','FREE',{'kind':'WORDS32','slot':0},{'pointer':1}),
        ('free_not_forwarded','FREE',{'kind':'WORDS32','slot':0},{'real_returned':0}),
        ('cleanup_leak','HEAP',{'kind':'WORDS32','phase':'CLEANUP'},{'free32':299996}),
        ('impossible_resource','HEAP',{'kind':'WORDS32','phase':'HELD'},{'largest32':300001}),
        ('heap_integrity_failed','HEAP',{'kind':'WORDS32','phase':'HELD'},{'integrity':0}),
        ('EXEC_extraRAM_claim','CASE',{'kind':'EXEC32'},{'extra_RAM_inferred':1}),
        ('application_fit_claim','CASE',{'kind':'EXEC32'},{'application_qualified':1}),
        ('scratch_is_IRAM','POINTER',{'kind':'DRAM_CONTROL'},{'pointer':0x40080000}),
        ('private_heap_access','BOOT',{}, {'private_heap':1}),
        ('full_application_PASS_claim','COMPLETE',{}, {'application_memory_qualified':1}),
    ]
    rejected=[]
    for name,tag,match,changes in controls:
        altered=copy.deepcopy(original)
        for index,(found,row) in enumerate(altered):
            if found!='CYD_WORD_'+tag or not all(row.get(key)==value for key,value in match.items()):continue
            if changes is None:del altered[index]
            else:row.update(changes)
            break
        else:raise ValueError('missing synthetic mutation target')
        try:reader.parse(text(altered))
        except ValueError as error:rejected.append(dict(name=name,reason=str(error)))
        else:raise ValueError('contradictory public capability evidence accepted: '+name)
    for field in ('executable','in_iram'):
        altered=copy.deepcopy(high_alias)
        for tag,row in altered:
            if tag=='CYD_WORD_POINTER' and row.get('kind')=='EXEC32' and row.get('slot')==7:row[field]=1;break
        try:reader.parse(text(altered))
        except ValueError as error:rejected.append(dict(name='high_DIRAM_false_'+field+'_query_relabelled_true',reason=str(error)))
        else:raise ValueError('incorrect high D/IRAM public query accepted: '+field)
    out.mkdir(parents=True);(out/'reader.py').write_bytes(READER.read_bytes());(out/'controller.py').write_bytes(Path(__file__).read_bytes())
    report=dict(passed=True,synthetic_parser_vectors=True,honest_refusal_vector_preserved=True,high_DIRAM_query_vector_preserved=True,SDK_started=False,QEMU_started=False,native_word_access_qualified=False,rejected_controls=len(rejected),rejected=rejected,
        reader_sha256=hashlib.sha256(READER.read_bytes()).hexdigest())
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(dict(passed=True,rejected_controls=len(rejected),synthetic_parser_vectors=True)));return 0


if __name__=='__main__':raise SystemExit(main())
