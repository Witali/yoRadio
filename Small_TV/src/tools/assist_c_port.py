"""Expose RISC-V control flow and emit a C draft for manual algorithm recovery.

This is a review aid, not an automatic high-level decompiler. It consumes objdump
text, retains instruction addresses and stops on unsupported instructions. Calls
and memory access need explicit bindings in the generated runtime interface.
"""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re

REGISTERS = ('zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 '
             's2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6').split()
REG_INDEX = {name:index for index,name in enumerate(REGISTERS)}
REG_INDEX.update({f'x{index}':index for index in range(32)})
REG_INDEX['fp']=8
BRANCHES={'beq':'==','bne':'!=','blt':'<','bge':'>=','bltu':'<','bgeu':'>=',
          'beqz':'==','bnez':'!=','bltz':'<','bgez':'>=','bgtz':'>','blez':'<=',
          'bgt':'>','ble':'<=','bgtu':'>','bleu':'<='}


@dataclass
class Instruction:
    """Keep one decoded instruction and its exact byte length/address."""
    address:int
    size:int
    encoding:str
    op:str
    operands:str
    note:str=''

    @property
    def next(self):
        """Return the sequential successor, including compressed instructions."""
        return self.address+self.size

    def args(self):
        """Split register/immediate operands without consuming objdump annotations."""
        return [part.strip() for part in self.operands.split(',') if part.strip()]

    def target(self):
        """Resolve direct branch targets and annotated AUIPC/JALR call destinations."""
        source=self.note if self.op in ('jalr','jr') else self.operands
        matches=re.findall(r'(?:0x)?([0-9a-fA-F]{6,16})(?:\s|\b)',source)
        return int(matches[-1],16) if matches else None

    def kind(self):
        """Classify transfers conservatively; indirect jumps remain unresolved."""
        args=self.args()
        if self.op in BRANCHES:
            return 'branch'
        if self.op=='ret' or (self.op=='jr' and args==['ra']):
            return 'return'
        if self.op in ('j','tail'):
            return 'jump'
        if self.op in ('call','jal'):
            return 'jump' if len(args)>1 and args[0] in ('zero','x0') else 'call'
        if self.op=='jalr':
            if args and args[0] in ('zero','x0'):
                return 'return' if any('ra' in part or 'x1)' in part for part in args[1:]) else 'indirect'
            return 'call'
        if self.op=='jr':
            return 'indirect'
        return 'ordinary'


def parse(text, fallback='function'):
    """Read objdump function headers and decoded RV32/RVC instruction lines."""
    functions=[]; name=fallback; instructions=[]
    for line in text.splitlines():
        header=re.match(r'^\s*([0-9a-fA-F]+)\s+<([^>]+)>:\s*$',line)
        if header:
            if instructions:
                functions.append((name,instructions)); instructions=[]
            name=fallback if header[2].startswith('.data') else header[2]
            continue
        match=re.match(r'^\s*([0-9a-fA-F]+):\s+([0-9a-fA-F]{4,8})\s+(\S+)\s*(.*)$',line)
        if not match:
            continue
        operands,_,note=match[4].partition('#')
        instructions.append(Instruction(int(match[1],16),len(match[2])//2,match[2],
                                        match[3].removeprefix('c.'),operands.strip(),note.strip()))
    if instructions:
        functions.append((name,instructions))
    return functions


def structure(name, instructions):
    """Build intraprocedural blocks, dominators and proven natural-loop back edges."""
    addresses={item.address for item in instructions}; leaders={instructions[0].address}
    for item in instructions:
        if item.kind()!='ordinary':
            if item.next in addresses:
                leaders.add(item.next)
            if item.kind() in ('branch','jump') and item.target() in addresses:
                leaders.add(item.target())
    blocks=[]; current=[]
    for item in instructions:
        if item.address in leaders and current:
            blocks.append(current); current=[]
        current.append(item)
    if current:
        blocks.append(current)
    by_address={item.address:block[0].address for block in blocks for item in block}
    successors={block[0].address:set() for block in blocks}
    for block in blocks:
        last=block[-1]; kind=last.kind(); edges=successors[block[0].address]
        if kind in ('branch','jump') and last.target() in by_address:
            edges.add(by_address[last.target()])
        if kind in ('ordinary','call','branch') and last.next in by_address:
            edges.add(by_address[last.next])
    entry=blocks[0][0].address; reachable={entry}; pending=[entry]
    while pending:
        for target in successors[pending.pop()]-reachable:
            reachable.add(target); pending.append(target)
    predecessors={address:set() for address in successors}
    for source,targets in successors.items():
        for target in targets:
            predecessors[target].add(source)
    dominators={address:({entry} if address==entry else set(reachable)) for address in reachable}
    changed=True
    while changed:
        changed=False
        for address in sorted(reachable-{entry}):
            parents=[dominators[p] for p in predecessors[address] if p in reachable]
            value={address}|set.intersection(*parents)
            if value!=dominators[address]:
                dominators[address]=value; changed=True
    loops=[]; candidates=[]
    for source,targets in successors.items():
        for target in targets:
            if source not in reachable or target not in dominators[source]:
                if target<=source:
                    candidates.append({'source':hex(source),'target':hex(target)})
                continue
            members={source,target}; pending=[] if source==target else [source]
            while pending:
                for parent in predecessors[pending.pop()]:
                    if parent not in members and parent in reachable:
                        members.add(parent); pending.append(parent)
            loops.append({'header':hex(target),'latch':hex(source),
                          'blocks':[hex(value) for value in sorted(members)]})
    prologue=[]
    for item in instructions[:12]:
        args=item.args()
        if item.op=='addi' and len(args)==3 and args[:2]==['sp','sp'] and int(args[2],0)<0:
            prologue.append({'address':hex(item.address),'stack_bytes':-int(args[2],0)})
        elif item.op in ('sw','sd') and args and (args[0]=='ra' or re.fullmatch(r's\d+',args[0])) and '(sp)' in item.operands:
            prologue.append({'address':hex(item.address),'saved_register':args[0],'slot':args[-1]})
    returns=[hex(item.address) for item in instructions if item.kind()=='return']
    return {'name':name,'entry':hex(entry),'instructions':len(instructions),
            'blocks':[{'address':hex(block[0].address),'end':hex(block[-1].address),
                       'successors':[hex(value) for value in sorted(successors[block[0].address])],
                       'reachable':block[0].address in reachable} for block in blocks],
            'natural_loops':loops,'back_edge_candidates':candidates,'prologue':prologue,
            'return_sites':returns,'calls':[{'address':hex(item.address),
                'target':hex(item.target()) if item.target() is not None else 'indirect'}
                for item in instructions if item.kind()=='call']}


def register(name):
    """Render ABI aliases as explicit register-file values; x0 is a constant."""
    index=REG_INDEX[name]
    return f'r[{index}]' if index else 'UINT32_C(0)'


def literal(value):
    """Express every immediate as an unambiguous 32-bit C bit pattern."""
    return f'UINT32_C(0x{value&0xffffffff:08x})'


def memory(operand):
    """Decode offset(base) addressing used by integer loads and stores."""
    match=re.fullmatch(r'(-?(?:0x[0-9a-fA-F]+|\d+))?\((\w+)\)',operand)
    if not match:
        raise ValueError('Unknown memory operand: '+operand)
    return f'({register(match[2])} + {literal(int(match[1] or "0",0))})'


def branch_condition(item):
    """Keep signed/unsigned comparisons explicit when lifting branch conditions."""
    args=item.args(); left=register(args[0]); right=register(args[1]) if len(args)>2 else 'UINT32_C(0)'
    signed=item.op not in ('beq','bne','beqz','bnez','bltu','bgeu','bgtu','bleu')
    if signed:
        left=f'(int32_t){left}'; right=f'(int32_t){right}'
    return f'{left} {BRANCHES[item.op]} {right}'
