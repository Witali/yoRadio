"""Read actual task stack, SDK heap counters and decoder diagnostics passively."""
import hashlib
from pathlib import Path
import re

from elftools.elf.elffile import ELFFile
from photo_target_state import shape

BASE=0x3fca0000
RAM_BYTES=0x40000


def describe(elf_path, state_layout, dependency_root=Path('C:/Work/yoRadio')):
    """Resolve SDK types and globals from this exact ELF, rejecting ambiguity."""
    names={'registered_heaps','pxCurrentTCBs'};types={}
    with elf_path.open('rb') as stream:
        elf=ELFFile(stream)
        locations={name:[s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
            if s.name==name and s['st_value']] for name in names}
        assert all(len(v)==1 for v in locations.values()),locations
        for cu in elf.get_dwarf_info().iter_CUs():
            for die in cu.iter_DIEs():
                if die.tag not in ('DW_TAG_structure_type','DW_TAG_typedef'):continue
                name=die.attributes.get('DW_AT_name')
                if not name:continue
                name=name.value.decode(errors='replace')
                if name not in ('heap_t_','multi_heap_info','jpeg_decode_diagnostic_t'):continue
                value=shape(die)
                if not value.get('fields'):continue
                assert name not in types or types[name]==value,'Conflicting DWARF '+name
                types[name]=value
    assert set(types)=={'heap_t_','multi_heap_info','jpeg_decode_diagnostic_t'}
    types['task']=state_layout['types']['tskTaskControlBlock']
    sdk=dependency_root/'.idf/v6.1-9a97f6c54ec6'
    paths=[sdk/'components/freertos/FreeRTOS-Kernel/tasks.c',
        sdk/'components/freertos/FreeRTOS-Kernel/portable/riscv/include/freertos/portmacro.h',
        sdk/'components/heap/heap_private.h',sdk/'components/heap/multi_heap.c',sdk/'components/heap/include/esp_heap_caps.h']
    tasks,port,_,_,caps=(p.read_text() for p in paths)
    assert re.search(r'#define\s+tskSTACK_FILL_BYTE\s+\(\s*0xa5U\s*\)',tasks)
    assert re.search(r'#define\s+portSTACK_GROWTH\s+\(-1\)',port)
    assert re.search(r'#define\s+portSTACK_TYPE\s+uint8_t',port)
    assert re.search(r'#define\s+MALLOC_CAP_8BIT\s+\(1<<2\)',caps)
    return dict(elf_sha256=hashlib.sha256(elf_path.read_bytes()).hexdigest(),types=types,
        globals={name:value[0] for name,value in locations.items()},ram_base=BASE,ram_bytes=RAM_BYTES,
        stack_fill=0xa5,stack_growth=-1,cap_8bit=4,worker_stack_bytes=8192,
        sdk_sources={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        interpretation='SDK stack-fill high-water; sum of individual heap minima is a conservative lower bound, not a simultaneous aggregate minimum')


def inspect(layout, ram, worker=None, diagnostic=None):
    """Derive values from one stopped RAM image, without invoking guest functions."""
    assert len(ram)==RAM_BYTES and layout['ram_base']==BASE

    def bytes_at(address,size):
        assert size>0 and BASE<=address<=BASE+len(ram)-size,(hex(address),size)
        return ram[address-BASE:address-BASE+size]

    def integer(address,size=4):
        return int.from_bytes(bytes_at(address,size),'little')

    def fields(address,kind):
        result={}
        for name,field in kind['fields'].items():
            if field.get('fields'):continue
            if field['kind']=='DW_TAG_array_type':continue
            if field['bytes'] in (1,2,4,8):result[name]=integer(address+field['offset'],field['bytes'])
        return result

    def stack(address):
        kind=layout['types']['task'];values=fields(address,kind)
        name=bytes_at(address+kind['fields']['pcTaskName']['offset'],16).split(b'\0',1)[0].decode('ascii')
        # The recorded top is aligned down, so adding sizeof(pointer) to it
        # would invent the allocation boundary. Use the pinned xTaskCreate
        # size for this specific task; check the recorded top lies inside it.
        assert name=='tv-photo','Metrics captured outside the decoder owner'
        start=values['pxStack'];end=start+layout['worker_stack_bytes']
        assert end-16<=values['pxEndOfStack']<end
        data=bytes_at(start,end-start);free=0
        for value in data:
            if value!=0xa5:break
            free+=1
        assert free<len(data),'Uninitialized task stack'
        return dict(tcb_address=address,name=name,start=start,end=end,stack_bytes=len(data),
            untouched_prefix_bytes=free,observed_used_bytes=len(data)-free,
            recorded_end=values['pxEndOfStack'],saved_top=values['pxTopOfStack'])

    current=integer(layout['globals']['pxCurrentTCBs'])
    worker=current if worker is None else worker
    result=dict(current_task=stack(current),worker=stack(worker),heaps=[])
    assert result['worker']['name']=='tv-photo' and result['worker']['stack_bytes']==8192
    address=integer(layout['globals']['registered_heaps']);seen=set()
    kind=layout['types']['heap_t_']
    while address:
        assert address not in seen and len(seen)<16;seen.add(address)
        values=fields(address,kind)
        caps=bytes_at(address+kind['fields']['caps']['offset'],kind['fields']['caps']['bytes'])
        all_caps=0
        for at in range(0,len(caps),4):all_caps|=int.from_bytes(caps[at:at+4],'little')
        if values['heap'] and all_caps&layout['cap_8bit']:
            counters=fields(values['heap'],layout['types']['multi_heap_info'])
            assert 0<=counters['minimum_free_bytes']<=counters['free_bytes']<=counters['pool_size']
            result['heaps'].append(dict(descriptor=address,handle=values['heap'],capabilities=all_caps,
                free_bytes=counters['free_bytes'],minimum_free_bytes=counters['minimum_free_bytes'],pool_bytes=counters['pool_size']))
        address=integer(address+kind['fields']['next']['offset'])
    assert result['heaps']
    result['free_8bit_bytes']=sum(h['free_bytes'] for h in result['heaps'])
    result['sum_individual_heap_minima']=sum(h['minimum_free_bytes'] for h in result['heaps'])
    if diagnostic is not None:result['decode_diagnostic']=fields(diagnostic,layout['types']['jpeg_decode_diagnostic_t'])
    return result


def snapshot(qmp, folder, label, layout, worker=None, diagnostic=None):
    """Save a coherent paused RAM image and retain the exact bytes behind metrics."""
    path=Path(folder)/(label+'-ram.bin')
    qmp.execute('pmemsave',val=BASE,size=RAM_BYTES,filename=str(path.resolve()))
    ram=path.read_bytes();result=inspect(layout,ram,worker,diagnostic)
    result.update(ram_file=path.name,ram_sha256=hashlib.sha256(ram).hexdigest())
    return result
