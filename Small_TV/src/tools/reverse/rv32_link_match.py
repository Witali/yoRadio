"""Match complete RV32 function bodies while accounting for declared ELF relaxations.

Only the relocation forms needed by the pinned Wi-Fi objects are accepted.
Unrelocated bits, local control-flow destinations and repeated symbol bindings
must agree. This is a static identity check, not whole-firmware equivalence.
"""
from functools import lru_cache
import io

from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection


def signed(value,bits):
    """Interpret an encoded immediate in its specified two's-complement width."""
    return (value^(1<<(bits-1)))-(1<<(bits-1))


def size_at(data,offset):
    """Accept complete 16/32-bit RV32 instructions, rejecting longer encodings."""
    half=int.from_bytes(data[offset:offset+2],'little')
    size=2 if half&3!=3 else 4
    if offset+size>len(data) or size==4 and half&31==31:raise ValueError('Unsupported instruction length')
    return size


def model(data,name):
    """Read one defined function and every relocation affecting its bytes."""
    elf=ELFFile(io.BytesIO(data));symbols=elf.get_section_by_name('.symtab')
    rows=[s for s in symbols.iter_symbols() if s.name==name and s['st_info']['type']=='STT_FUNC'
          and isinstance(s['st_shndx'],int)]
    if len(rows)!=1:raise ValueError('Expected one defined SDK function')
    symbol=rows[0];section=elf.get_section(symbol['st_shndx']);start=symbol['st_value'];length=symbol['st_size']
    code=section.data()[start:start+length]
    if not 0<length<=4096 or len(code)!=length:raise ValueError('Function extent is not bounded')
    relocs={}
    for entry in elf.iter_sections():
        if not isinstance(entry,RelocationSection) or entry['sh_info']!=symbol['st_shndx']:continue
        table=elf.get_section(entry['sh_link'])
        for relocation in entry.iter_relocations():
            offset=relocation['r_offset']-start
            if not 0<=offset<length:continue
            target=table.get_symbol(relocation['r_info_sym'])
            row=dict(type=relocation['r_info_type'],name=target.name,addend=relocation['r_addend'],
                section=target['st_shndx'],value=target['st_value'],binding=target['st_info']['bind'])
            relocs.setdefault(offset,[]).append(row)
    instructions={};at=0
    while at<len(code):
        length=size_at(code,at);instructions[at]=code[at:at+length];at+=length
    return dict(name=name,code=code,section=symbol['st_shndx'],section_start=start,
        relocs=relocs,instructions=instructions)


def meaningful(rows):
    """Keep relaxation permissions separate from the relocation defining a value."""
    return [r for r in rows if r['type']!=51]


def mask_for(rows):
    """Mask only fields which the corresponding RISC-V relocation actually rewrites."""
    masks={16:0xfe000f80,17:0xfffff000,26:0xfffff000,27:0xfff00000,
           28:0xfe000f80,44:0x1c7c,45:0x1ffc}
    result=0
    for row in meaningful(rows):
        if row['type'] not in masks:raise ValueError('Unsupported relocation '+str(row['type']))
        result|=masks[row['type']]
    return result


def branch_target(data,pc):
    """Decode RV32 JAL/branches and compressed jump/branch destinations."""
    word=int.from_bytes(data,'little')
    if len(data)==4 and word&127==99:
        value=((word>>31)<<12)|(((word>>7)&1)<<11)|(((word>>25)&63)<<5)|(((word>>8)&15)<<1)
        offset=signed(value,13)
    elif len(data)==4 and word&127==111:
        value=((word>>31)<<20)|(((word>>12)&255)<<12)|(((word>>20)&1)<<11)|(((word>>21)&1023)<<1)
        offset=signed(value,21)
    elif len(data)==2 and word&3==1 and word>>13 in (1,5):
        value=(((word>>12)&1)<<11)|(((word>>11)&1)<<4)|(((word>>9)&3)<<8)|(((word>>8)&1)<<10)
        value|=(((word>>7)&1)<<6)|(((word>>6)&1)<<7)|(((word>>3)&7)<<1)|(((word>>2)&1)<<5)
        offset=signed(value,12)
    elif len(data)==2 and word&3==1 and word>>13 in (6,7):
        value=(((word>>12)&1)<<8)|(((word>>10)&3)<<3)|(((word>>5)&3)<<6)|(((word>>3)&3)<<1)|(((word>>2)&1)<<5)
        offset=signed(value,9)
    else:raise ValueError('Expected a direct control-flow instruction')
    return (pc+offset)&0xffffffff


def link_register(data):
    """Recognize direct compressed/standard jumps without confusing an indirect call."""
    word=int.from_bytes(data,'little')
    if len(data)==4 and word&127==111:return (word>>7)&31
    if len(data)==2 and word&3==1 and word>>13 in (1,5):return 1 if word>>13==1 else 0
    return None


def symbol_key(row):
    """Distinguish a function-local anchor from a shared global symbol."""
    return (row['name'],row['section'],row['value'],row['addend'])


def validate_trace(spec,linked,base,trace,gp):
    """Verify every relaxed address pair, local branch and repeated symbol value."""
    mapping={i:base+j for _,i,_,j,_ in trace};mapping[len(spec['code'])]=base+sum(r[4] for r in trace)
    events={i:(kind,j,n) for kind,i,_,j,n in trace};bindings={};branches=0;highs=[]
    def bind(row,value,kind):
        """Repeated references to a symbol must resolve to the same base address."""
        key=(row['name'],row['section'],row['value'],row['binding'])
        value=(value-row['addend'])&0xffffffff
        if key in bindings and bindings[key]['address']!=value:raise ValueError('Inconsistent symbol binding')
        bindings[key]=dict(name=row['name'],section=row['section'],binding=row['binding'],
            address=value,kind=kind)
    for kind,i,count,j,length in trace:
        data=spec['code'][i:i+count];actual=linked[j:j+length];rows=meaningful(spec['relocs'].get(i,[]))
        if not rows:continue
        if len(rows)!=1:raise ValueError('Overlapping value relocations')
        row=rows[0];rtype=row['type'];word=int.from_bytes(data[:4],'little')
        if rtype in (18,19):
            if kind=='call-relaxed':target=branch_target(actual,base+j)
            else:
                upper=int.from_bytes(actual[:4],'little');lower=int.from_bytes(actual[4:],'little')
                target=(base+j+(upper&0xfffff000)+signed(lower>>20,12))&0xfffffffe
            bind(row,target,'call')
        elif rtype==26:highs.append((i,(word>>7)&31,row,kind,actual))
        elif rtype in (27,28):
            register=(word>>15)&31
            candidates=[h for h in highs if h[1]==register and symbol_key(h[2])==symbol_key(row)]
            if not candidates:raise ValueError('Low relocation has no corresponding high part')
            _,_,_,high_kind,high_data=candidates[-1];value=int.from_bytes(actual,'little')
            immediate=(value>>20) if rtype==27 else ((value>>25)<<5)|((value>>7)&31)
            if kind=='gp-low':
                if high_kind!='gp-high-removed':raise ValueError('GP use without declared high elision')
                target=gp+signed(immediate,12)
            else:
                if high_kind=='gp-high-removed':raise ValueError('Removed high register still used')
                target=(int.from_bytes(high_data,'little')&0xfffff000)+signed(immediate,12)
            bind(row,target,'data')
        elif rtype in (16,17,44,45):
            target=branch_target(actual,base+j)
            if row['section']==spec['section']:
                offset=row['value']+row['addend']-spec['section_start']
                if offset not in mapping or mapping[offset]!=target:raise ValueError('Local control flow differs')
                branches+=1
            else:bind(row,target,'branch')
        else:raise ValueError('Unsupported trace relocation')
    for i,register,row,kind,_ in highs:
        if kind=='gp-high-removed' and not any(k=='gp-low' and n>i and
            any(symbol_key(r)==symbol_key(row) for r in meaningful(spec['relocs'].get(n,[])))
            for k,n,_,_,_ in trace):raise ValueError('Unconsumed high elision')
    return dict(local_branches_checked=branches,symbol_bindings=list(bindings.values()),
        mapping=mapping)


def match(spec,linked,base,gp):
    """Find a unique full-body match with only ELF-authorized linker transformations."""
    code=spec['code'];instructions=spec['instructions'];relocs=spec['relocs'];furthest=[0,0]
    @lru_cache(maxsize=None)
    def walk(i,j):
        """Bound the search to instruction boundaries and reject ambiguous expansions."""
        if i>furthest[0]:furthest[:]=[i,j]
        if i==len(code):return ((),)
        if j>=len(linked):return ()
        n=len(instructions[i]);m=size_at(linked,j);left=int.from_bytes(code[i:i+n],'little')
        right=int.from_bytes(linked[j:j+m],'little');rows=relocs.get(i,[]);values=meaningful(rows)
        permitted=any(r['type']==51 for r in rows);options=[]
        call=next((r for r in values if r['type'] in (18,19)),None)
        if call:
            low=int.from_bytes(code[i+4:i+8],'little')
            if n!=4 or left&127!=23 or low&127!=103 or (low>>12)&7 or (left>>7)&31!=(low>>15)&31:
                raise ValueError('Invalid AUIPC/JALR call pair')
            if j+8<=len(linked) and m==4 and size_at(linked,j+4)==4:
                actual_low=int.from_bytes(linked[j+4:j+8],'little')
                if (left^right)&~0xfffff000==0 and (low^actual_low)&~0xfff00000==0:
                    options.append(('call',8,8))
            if permitted and link_register(linked[j:j+m])==(low>>7)&31:
                options.append(('call-relaxed',8,m))
        else:
            mask=mask_for(rows)
            if n==m and (left^right)&~mask==0:options.append(('relocated' if values else 'same',n,m))
            if permitted and any(r['type']==26 for r in values) and left&127==55:
                options.append(('gp-high-removed',n,0))
            if permitted and any(r['type'] in (27,28) for r in values) and n==m==4:
                if (right>>15)&31==3 and (left>>15)&31!=3 and (left^right)&~(mask|0xf8000)==0:
                    options.append(('gp-low',n,m))
        result=[]
        for kind,old_size,new_size in options:
            for tail in walk(i+old_size,j+new_size):
                result.append(((kind,i,old_size,j,new_size),)+tail)
                if len(result)>4:raise ValueError('Ambiguous instruction alignment')
        return tuple(result)
    traces=walk(0,0);accepted=[]
    for trace in traces:
        try:verified=validate_trace(spec,linked,base,trace,gp)
        except ValueError:continue
        accepted.append((trace,verified))
    if len(accepted)!=1:raise ValueError('Expected one complete match; furthest offsets '+str(furthest))
    trace,verified=accepted[0];length=sum(row[4] for row in trace)
    return dict(name=spec['name'],start=hex(base),end=hex(base+length),source_bytes=len(code),linked_bytes=length,
        source_instructions=len(instructions),linked_instruction_starts=sum(2 if kind=='call' else bool(n)
            for kind,_,_,_,n in trace),
        transformations=[dict(kind=kind,object_offset=i,object_bytes=code[i:i+n].hex(),
            pc=hex(base+j),linked_bytes=linked[j:j+m].hex()) for kind,i,n,j,m in trace],
        local_branches_checked=verified['local_branches_checked'],symbol_bindings=verified['symbol_bindings'])
