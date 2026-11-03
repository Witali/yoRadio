"""Inspect recorded Xtensa probe disassembly as data, never execute objects."""
import re

def need(value,reason):
    if not value:raise ValueError(reason)

def functions(text):
    result={};active=None
    for line in text.splitlines():
        label=re.fullmatch(r'\s*[0-9a-f]+ <([A-Za-z_][A-Za-z_0-9]*)>:',line)
        if label:
            active=label.group(1);need(active not in result,'unique function');result[active]=[]
        elif active:
            instruction=re.match(r'\s*[0-9a-f]+:\s+[0-9a-f]+\s+([a-z0-9_.]+)\s*(.*)',line)
            if instruction:result[active].append(dict(mnemonic=instruction.group(1),operands=instruction.group(2),original=line))
            else:
                relocation=re.match(r'\s*[0-9a-f]+:\s+(R_XTENSA_[A-Z0-9_]+)\s+(\S+)',line)
                if relocation and result[active]:result[active][-1].setdefault('relocations',[]).append(relocation.groups())
    return result

def inspect(text,names,readonly_literals=None):
    need(not re.search(r'\b(?:memcpy|memset|memmove|bcopy|bzero)\b',text),'no hidden byte-library access')
    bodies=functions(text);measurements={}
    for name in names:
        need(name in bodies and bodies[name],'actual nonempty noinline probe: '+name)
        words=[];stack_words=[];literal_words=[]
        for row in bodies[name]:
            instruction=row['mnemonic']
            need(not instruction.startswith(('call','j.l')),'no helper/library call from probe')
            if instruction in ('l32i','l32i.n','s32i','s32i.n'):
                (stack_words if re.search(r'\ba1\b',row['operands']) else words).append(instruction)
            elif instruction=='l32r':
                targets=row.get('relocations',[])
                need(len(targets)==1 and targets[0][0]=='R_XTENSA_SLOT0_OP','one literal relocation for L32R')
                target=targets[0][1];literal=(readonly_literals or {}).get(target)
                need(literal and literal['readonly'] and literal['bytes']==4 and literal['alignment']>=4,
                     'authenticated readonly32-bit literal: '+target)
                literal_words.append(dict(mnemonic=instruction,target=target,metadata=literal))
            elif instruction.startswith('l'):
                need(instruction.startswith('loop'),'no narrow/FP/literal/unknown load: '+instruction)
            elif instruction.startswith('s'):
                need(instruction.startswith(('sll','srl','sra','ssr','ssl','ssa','sext','sub')),
                     'no narrow/FP/unknown store: '+instruction)
        need(words,'real word storage memory operand: '+name)
        measurements[name]=dict(instructions=len(bodies[name]),word_memory_operands=words,
             ordinary_stack_word_operands=stack_words,authenticated_literal_operands=literal_words,
             additionally_storage_only_operands=not stack_words and not literal_words)
    return measurements
