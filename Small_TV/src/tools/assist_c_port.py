"""Report RISC-V blocks, loops, stack hints and C branch conditions for review.

The decoded objdump text and exact address range remain the source evidence.
Indirect transfers, gaps and outgoing branches are explicit review warnings.
The report helps recover algorithms; it does not certify C equivalence or emit
an executable implementation of instructions or external calls.
"""
import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import sys

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
        args=self.args()
        source=self.note if self.op in ('jalr','jr') else (args[-1] if args else '')
        match=re.match(r'(?:0x)?([0-9a-fA-F]+)(?=\s|<|$)',source)
        return int(match[1],16) if match else None

    def kind(self):
        """Classify transfers conservatively; indirect jumps remain unresolved."""
        args=self.args()
        if self.op in BRANCHES:
            return 'branch'
        if self.op=='ret' or (self.op=='jr' and args in (['ra'],['x1'])):
            return 'return'
        if self.op in ('j','tail'):
            return 'jump'
        if self.op in ('call','jal'):
            return 'jump' if len(args)>1 and args[0] in ('zero','x0') else 'call'
        if self.op=='jalr':
            if args and args[0] in ('zero','x0'):
                canonical=len(args)==2 and args[1] in ('0(ra)','(ra)','0(x1)','(x1)')
                return 'return' if canonical else 'indirect'
            return 'call'
        if self.op=='jr':
            return 'indirect'
        if self.op in ('ecall','ebreak','unimp') or self.op.startswith('.'):
            return 'trap'
        if self.op in ('mret','sret','uret'):
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
            name=fallback if header[2].startswith('.') else header[2]
            continue
        match=re.match(r'^\s*([0-9a-fA-F]+):\s+([0-9a-fA-F]{4,8})\s+(\S+)\s*(.*)$',line)
        if not match:
            continue
        if len(match[2]) not in (4,8):
            raise ValueError(f'Expected a 16/32-bit instruction at 0x{int(match[1],16):x}')
        operands,_,note=match[4].partition('#')
        instructions.append(Instruction(int(match[1],16),len(match[2])//2,match[2],
                                        match[3].removeprefix('c.'),operands.strip(),note.strip()))
    if instructions:
        functions.append((name,instructions))
    for _,items in functions:
        previous=None
        for item in items:
            if previous is not None and item.address<previous.next:
                raise ValueError(f'Overlapping or out-of-order instruction at 0x{item.address:x}')
            previous=item
    return functions


def structure(name, instructions):
    """Build intraprocedural blocks, dominators and proven natural-loop back edges."""
    if not instructions:
        raise ValueError('No instructions in selected function')
    addresses={item.address for item in instructions}; leaders={instructions[0].address}
    warnings=[]
    for previous,item in zip(instructions,instructions[1:]):
        if previous.next!=item.address:
            leaders.add(item.address)
            warnings.append({'kind':'gap','after':hex(previous.address),'next':hex(item.address)})
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
    for item in blocks[0][:12]:
        args=item.args()
        if item.op=='addi' and len(args)==3 and args[:2]==['sp','sp'] and int(args[2],0)<0:
            prologue.append({'address':hex(item.address),'stack_bytes':-int(args[2],0)})
        elif item.op in ('sw','sd') and args and (args[0]=='ra' or re.fullmatch(r's\d+',args[0])) and '(sp)' in item.operands:
            prologue.append({'address':hex(item.address),'saved_register':args[0],'slot':args[-1]})
    returns=[hex(item.address) for item in instructions if item.kind()=='return']
    epilogues=[]
    for block in blocks:
        last=block[-1]
        if last.kind()=='return':
            frame=0; restored=[]
            for item in block[-13:-1]:
                args=item.args()
                if item.op=='addi' and len(args)==3 and args[:2]==['sp','sp'] and int(args[2],0)>0:
                    frame+=int(args[2],0)
                if item.op in ('lw','ld') and args and (args[0]=='ra' or re.fullmatch(r's\d+',args[0])) and '(sp)' in item.operands:
                    restored.append(args[0])
            epilogues.append({'return_address':hex(last.address),'stack_bytes':frame,'restored_registers':restored})
        if last.kind() in ('indirect','trap'):
            warnings.append({'kind':last.kind(),'address':hex(last.address),'instruction':last.op+' '+last.operands})
        if last.kind()=='call' and last.target() in addresses:
            warnings.append({'kind':'call_inside_range','address':hex(last.address),'target':hex(last.target())})
        if last.kind() in ('branch','jump') and last.target() not in addresses:
            warnings.append({'kind':'external_branch','address':hex(last.address),
                             'target':hex(last.target()) if last.target() is not None else None})
        if last.kind() in ('ordinary','call','branch') and last.next not in addresses:
            warnings.append({'kind':'fallthrough_outside_input','address':hex(last.address),'next':hex(last.next)})
    return {'name':name,'entry':hex(entry),'instructions':len(instructions),
            'blocks':[{'address':hex(block[0].address),'end':hex(block[-1].address),
                       'successors':[hex(value) for value in sorted(successors[block[0].address])],
                       'reachable':block[0].address in reachable} for block in blocks],
            'natural_loops':loops,'back_edge_candidates':candidates,'prologue':prologue,
            'return_sites':returns,'epilogues':epilogues,'warnings':warnings,
            'branch_conditions':[{'address':hex(item.address),'condition':branch_condition(item),
                'target':hex(item.target()) if item.target() is not None else None}
                for item in instructions if item.op in BRANCHES],
            'calls':[{'address':hex(item.address),
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


def analyze(text, fallback, start=None, stop=None, name=None, symbols=None):
    """Analyze a bounded decoded range and attach exact-address logical names."""
    functions=parse(text,fallback)
    all_items=[item for _,items in functions for item in items]
    if start is not None and start not in {item.address for item in all_items}:
        raise ValueError('Start must be the address of a decoded instruction')
    if start is not None and stop is not None and stop<=start:
        raise ValueError('Stop must be greater than start')
    if stop is not None and any(item.address<stop<item.next for item in all_items):
        raise ValueError('Stop splits a decoded instruction')
    selected=[(label,[item for item in items if (start is None or item.address>=start) and
                     (stop is None or item.address<stop)]) for label,items in functions]
    selected=[(label,items) for label,items in selected if items]
    if not selected:
        raise ValueError('No decoded instructions in the selected input/range')
    if name and len(selected)!=1:
        raise ValueError('--name requires exactly one selected function')
    bindings={}
    for row in (symbols or {}).get('functions',[]):
        address=int(row['address'],0)
        if address in bindings:
            raise ValueError(f'Ambiguous function name at 0x{address:x}')
        bindings[address]=row
    output=[]
    for label,items in selected:
        binding=bindings.get(items[0].address,{})
        result=structure(name or binding.get('logical_name') or label,items)
        result['end_exclusive']=hex(items[-1].next)
        result['native_module']=binding.get('native_module')
        result['listing']=[{'address':hex(item.address),'encoding':item.encoding,
                            'assembly':item.op+(' '+item.operands if item.operands else ''),
                            'annotation':item.note} for item in items]
        for call in result['calls']:
            if call['target']!='indirect':
                call['logical_name']=bindings.get(int(call['target'],0),{}).get('logical_name')
        output.append(result)
    return output


def markdown_report(report):
    """Render reviewable assembly blocks alongside inferred C branch conditions."""
    lines=['# RISC-V algorithm transfer review','',
           'Source SHA-256: `'+report['source_sha256']+'`','',
           'This report describes decoded control flow. Calls may not return; indirect transfers, '
           'missing instructions and data-dependent targets require manual review. '
           'C conditions use a conceptual `uint32_t r[32]` register file. '
           'The instruction bodies and external-call semantics still need implementation and comparison.','']
    for function in report['functions']:
        lines += ['## '+function['name'],'',
                  f"Range: `{function['entry']}` .. `{function['end_exclusive']}` (exclusive); "
                  f"{function['instructions']} instructions, {len(function['blocks'])} blocks.",'']
        if function['native_module']:
            lines += ['C module: `'+function['native_module']+'`.','']
        for hint in function['prologue']:
            lines.append('Prologue hint: `'+json.dumps(hint,sort_keys=True)+'`.')
        for hint in function['epilogues']:
            lines.append('Epilogue hint: `'+json.dumps(hint,sort_keys=True)+'`.')
        lines.append('')
        for loop in function['natural_loops']:
            lines.append(f"Natural loop: header `{loop['header']}`, latch `{loop['latch']}`, "
                         'blocks '+', '.join('`'+block+'`' for block in loop['blocks'])+'.')
        for edge in function['back_edge_candidates']:
            lines.append(f"Backward edge `{edge['source']}` → `{edge['target']}` needs review; "
                         'dominance does not establish a natural loop.')
        for call in function['calls']:
            lines.append(f"Call at `{call['address']}` → `{call['target']}`"+
                         (' ('+call['logical_name']+')' if call.get('logical_name') else '')+'.')
        for warning in function['warnings']:
            lines.append('Review warning: `'+json.dumps(warning,sort_keys=True)+'`.')
        conditions={row['address']:row for row in function['branch_conditions']}
        for block in function['blocks']:
            lines += ['',"### Block `"+block['address']+'`'+(' (unreachable in decoded CFG)' if not block['reachable'] else ''),'',
                      'Successors: '+(', '.join('`'+edge+'`' for edge in block['successors']) or 'none in selected input')+'.','',
                      '```asm']
            for item in function['listing']:
                if int(block['address'],0)<=int(item['address'],0)<=int(block['end'],0):
                    lines.append(item['address']+': '+item['encoding']+'  '+item['assembly']+
                                 (' # '+item['annotation'] if item['annotation'] else ''))
            lines += ['```','']
            condition=conditions.get(block['end'])
            if condition:
                lines += ['C branch condition:','', '```c',
                          'if ('+condition['condition']+') /* target '+str(condition['target'])+' */;',
                          '```','']
    return '\n'.join(lines)+'\n'


def main(argv=None):
    """Write JSON/Markdown review reports without altering disassembly or bindings."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path,help='Decoded RISC-V objdump text')
    parser.add_argument('--json',type=Path,dest='json_output',help='JSON report; default is stdout')
    parser.add_argument('--markdown',type=Path,help='Assembly and branch-condition review report')
    parser.add_argument('--start',type=lambda value:int(value,0),help='Inclusive instruction address')
    parser.add_argument('--stop',type=lambda value:int(value,0),help='Exclusive end address')
    parser.add_argument('--name',help='Logical name for a single selected function')
    parser.add_argument('--symbols',type=Path,help='Optional repository symbol-map.json name bindings')
    parser.add_argument('--force',action='store_true',help='Replace existing report files')
    args=parser.parse_args(argv)
    try:
        raw=args.input.read_bytes()
        symbols_raw=args.symbols.read_bytes() if args.symbols else None
        functions=analyze(raw.decode('utf-8-sig'),args.input.stem,args.start,args.stop,args.name,
                          json.loads(symbols_raw.decode('utf-8-sig')) if symbols_raw else None)
        report={'schema_version':1,'analysis_only':True,'source_file':args.input.name,
                'source_sha256':hashlib.sha256(raw).hexdigest(),
                'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'symbols_sha256':hashlib.sha256(symbols_raw).hexdigest() if symbols_raw else None,
                'functions':functions}
        outputs=[path for path in (args.json_output,args.markdown) if path is not None]
        protected={args.input.resolve(),Path(__file__).resolve()}
        if args.symbols:
            protected.add(args.symbols.resolve())
        if len({path.resolve() for path in outputs})!=len(outputs):
            raise ValueError('Choose different JSON and Markdown output files')
        for path in outputs:
            if path.resolve() in protected:
                raise ValueError('A report must not overwrite its input, symbol map or tool')
            if path.exists() and not args.force:
                raise ValueError('Report already exists; use --force to replace it: '+str(path))
        serialized=json.dumps(report,indent=2,ensure_ascii=False)+'\n'
        for path in outputs:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(serialized if path==args.json_output else markdown_report(report),
                            encoding='utf-8',newline='\n')
        if not outputs:
            print(serialized,end='')
        return 0
    except (OSError,UnicodeError,ValueError,KeyError) as error:
        parser.error(str(error))


if __name__=='__main__':
    sys.exit(main())
