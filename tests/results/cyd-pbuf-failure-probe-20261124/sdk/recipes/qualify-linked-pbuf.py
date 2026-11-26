"""Fail-closed static proof of the four pinned SDK tcp_out wrap references.

Reads an immutable linked ELF and frozen SDK reference objects tied to its CU.
No build, guest, network, source/index mutation, or runtime-coverage claim.
"""
import argparse
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

from elftools.elf.elffile import ELFFile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
FUNCTIONS = ('tcp_output_alloc_header_common$constprop$0', 'tcp_write',
             'tcp_split_unsent_seg', 'tcp_enqueue_flags')
TCP_SOURCE_SHA = 'f31f0eef0c9aba4402ebff73b6d99a560b1d7ec219b4e0e5791996c41a832308'
# Debug compilation directories differ by backend; preserve exact coupled pins.
OBJECT_PINS = {
    'legacy': ('29a98e26478c7b71a0e30b2668739718806813690219b3049754e9f491860244',
               '956e10c6b180b7ee8b285b759abab18b82de066e9fe6f66e72f3619cb083c862'),
    'pdm': ('4b83cc23b14e7a18ec4b2ef5c4c0c3196218ee2607f1a1a9b4ab06decb4e264e',
            '19d152fdb4a34dbe3b02da75c6307454b75fdbb04f28d1e95805a2614c61b3e8'),
    'continuous': ('161446cedf0d4205c872194cbaf7a2184602cf9262d87846cf60e93517674bc4',
                   'e92a77552bc9b7534f490bb8dc75e86c3dfbf2afddc713600f3d331341433bf2'),
}
LINE = re.compile(r'^\s*([0-9a-fA-F]+):\s+([0-9a-fA-F]+)\s+(\S+)(?:\s+(.*?))?\s*$')
REGISTER = re.compile(r'^a([0-9]|1[0-5])$')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def pin(path):
    path = Path(path)
    before = path.stat()
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for body in iter(lambda:stream.read(1024*1024),b''):
            h.update(body)
    after = path.stat()
    require((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),
            'Input changed while being read: '+str(path))
    return dict(bytes=after.st_size,sha256=h.hexdigest())


def number(text):
    token = text.strip().split()[0]
    return int(token,16) if not token.startswith(('0x','-0x')) else int(token,0)


class Image:
    def __init__(self, path):
        self.path = path
        self.stream = path.open('rb')
        self.elf = ELFFile(self.stream)
        require(self.elf.elfclass==32 and self.elf.little_endian and
                self.elf['e_machine']=='EM_XTENSA' and self.elf['e_type']=='ET_EXEC',
                'Expected a linked little-endian Xtensa32 executable')
        self.table = self.elf.get_section_by_name('.symtab')
        require(self.table is not None,'Missing full symbol table')
        self.symbols = list(self.table.iter_symbols())
        self.sections = list(self.elf.iter_sections())
        self.dwarf = self.elf.get_dwarf_info()
        self.aranges = self.dwarf.get_aranges()
        require(self.aranges is not None,'Missing DWARF address ranges for source provenance')

    def close(self):
        self.stream.close()

    def section_at(self, address, size):
        matches = [s for s in self.sections if s['sh_flags']&2 and
                   s['sh_addr']<=address and address+size<=s['sh_addr']+s['sh_size']]
        require(len(matches)==1,'Address not mapped uniquely in allocated ELF sections: '+hex(address))
        return matches[0]

    def read(self, address, size, readonly=False):
        section = self.section_at(address,size)
        require(section['sh_type']!='SHT_NOBITS','Cannot read ELF-initialized bytes from BSS')
        require(not readonly or not section['sh_flags']&1,'Indirect target depends on mutable ELF storage')
        at = address-section['sh_addr']
        return section.data()[at:at+size]

    def word(self, address):
        require(address%4==0,'Unaligned literal pointer')
        return struct.unpack('<I',self.read(address,4,readonly=True))[0]

    def function(self, name, binding='STB_GLOBAL'):
        symbols = [s for s in self.table.get_symbol_by_name(name) or []
                   if s['st_info']['type']=='STT_FUNC' and s['st_info']['bind']==binding and
                   isinstance(s['st_shndx'],int) and s['st_size']>0]
        require(len(symbols)==1,'Missing/ambiguous true function binding: '+name)
        symbol = symbols[0]
        section = self.sections[symbol['st_shndx']]
        require(section['sh_flags']&2 and section['sh_flags']&4,'Function is not allocated executable code: '+name)
        return dict(name=name,address=symbol['st_value'],bytes=symbol['st_size'],
                    binding=binding,section=section.name)

    def target(self, address):
        functions = [s for s in self.symbols if s['st_value']==address and
                     s['st_info']['type']=='STT_FUNC' and isinstance(s['st_shndx'],int) and s['st_size']>0]
        if functions:
            return dict(address=address,names=sorted(set(s.name for s in functions)),kind='ELF_function')
        rom = [s for s in self.symbols if s['st_value']==address and s['st_shndx']=='SHN_ABS' and
               s['st_info']['bind']=='STB_GLOBAL' and s.name and 0x40000000<=address<0x400a0000]
        require(rom,'Resolved call has no true ELF function/defined ROM entry: '+hex(address))
        return dict(address=address,names=sorted(set(s.name for s in rom)),kind='SDK_ROM_absolute')

    def cu(self, address):
        offset = self.aranges.cu_offset_at_addr(address)
        require(offset is not None,'No source CU for required function at '+hex(address))
        attributes = self.dwarf.get_CU_at(offset).get_top_DIE().attributes
        text = lambda key:attributes[key].value.decode(errors='strict')
        return dict(offset=offset,source=text('DW_AT_name'),directory=text('DW_AT_comp_dir'))


class Decoder:
    def __init__(self, image, objdump, directory):
        self.image,self.objdump,self.directory = image,objdump,directory
        self.outputs = []

    def dump(self, start, end, label):
        command = [str(self.objdump),'-d','--start-address='+hex(start),'--stop-address='+hex(end),str(self.image.path)]
        child = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
        prefix = self.directory/(str(len(self.outputs)).zfill(3)+'-'+re.sub(r'[^A-Za-z0-9_-]','_',label))
        stdout,stderr = prefix.with_suffix('.txt'),prefix.with_suffix('.stderr.txt')
        stdout.write_bytes(child.stdout); stderr.write_bytes(child.stderr)
        self.outputs.append(dict(file=stdout.name,**pin(stdout),stderr=dict(file=stderr.name,**pin(stderr)),command=command))
        require(child.returncode==0,'Objdump failed; raw output retained')
        result = {}
        for line in child.stdout.decode(errors='strict').splitlines():
            match = LINE.match(line)
            if not match:
                continue
            address,encoding,mnemonic,arguments = match.groups()
            address = int(address,16)
            if not start<=address<end:
                continue
            size = len(encoding)//2
            if len(encoding)%2 or not 1<=size<=8:
                continue
            raw = int(encoding,16).to_bytes(size,'little')
            require(raw==self.image.read(address,size),'Disassembly bytes differ from actual ELF')
            result[address] = dict(address=address,size=size,encoding=encoding.lower(),
                                   mnemonic=mnemonic,arguments=arguments or '')
        require(start in result,'Objdump did not decode the requested instruction boundary')
        return result


class Function:
    def __init__(self, image, decoder, symbol):
        self.image,self.decoder,self.symbol = image,decoder,symbol
        self.start,self.end = symbol['address'],symbol['address']+symbol['bytes']
        self.instructions = decoder.dump(self.start,self.end,symbol['name'])
        self.nodes,self.successors,self.predecessors,self.exits = {},{},defaultdict(set),[]
        self._build()

    def instruction(self, address):
        if address not in self.instructions:
            # Linear objdump can lose alignment in unreachable padding. Restart
            # at actual reachable branch targets instead of accepting fake calls.
            self.instructions.update(self.decoder.dump(address,self.end,self.symbol['name']+'-branch'))
        instruction = self.instructions[address]
        require(instruction['size'] in (2,3) and not instruction['mnemonic'].startswith('.'),
                'Unresolved reachable instruction at '+hex(address))
        return instruction

    def _build(self):
        queue = deque([self.start])
        loops = []
        while queue:
            address = queue.popleft()
            if address in self.nodes:
                continue
            require(self.start<=address<self.end,'Control flow escapes function bounds')
            instruction = self.instruction(address)
            self.nodes[address] = instruction
            mnemonic,args = instruction['mnemonic'],instruction['arguments']
            following = address+instruction['size']
            if mnemonic in ('retw','retw.n','ret','ret.n','ill','ill.n','break','break.n'):
                successors = []
                self.exits.append(address)
            elif mnemonic=='j':
                successors = [number(args)]
            elif mnemonic=='jx':
                raise ValueError('Unresolved reachable indirect jump')
            elif mnemonic.startswith('loop'):
                target = number(args.split(',')[-1])
                loops.append((target,following))
                successors = [following,target]
            elif mnemonic.startswith('b'):
                successors = [following,number(args.split(',')[-1])]
            else:
                successors = [following]
            require(all(self.start<=x<self.end for x in successors),'Unresolved outgoing function edge at '+hex(address))
            self.successors[address] = set(successors)
            queue.extend(successors)
        for end,body in loops:
            for address,instruction in self.nodes.items():
                if address+instruction['size']==end:
                    self.successors[address].add(body)
        for address,successors in self.successors.items():
            for successor in successors:
                self.predecessors[successor].add(address)
        require(self.nodes[self.start]['mnemonic']=='entry','Missing windowed-ABI entry')

    def constant(self, before, register, trail=frozenset()):
        token = (before,register)
        require(token not in trail and len(trail)<512,'Cyclic/unresolved indirect-call register provenance')
        trail = trail|{token}
        predecessors = self.predecessors[before]
        require(predecessors,'Indirect-call register originates outside proved definitions')
        values,proofs = [],[]
        for address in sorted(predecessors):
            instruction = self.nodes[address]
            mnemonic = instruction['mnemonic'].removesuffix('.n')
            operands = [x.strip().split()[0] for x in instruction['arguments'].split(',') if x.strip()]
            if mnemonic.startswith('call'):
                raise ValueError('Indirect-call provenance crosses a call-clobbered register')
            stores = ('s8i','s16i','s32i','s32e','ssi','ssiu','wsr','memw','isync','rsync')
            writes = bool(operands and operands[0]==register and mnemonic not in stores and
                          not mnemonic.startswith(('b','loop')) and mnemonic not in ('j','entry'))
            if writes and mnemonic=='l32r':
                literal = number(instruction['arguments'].split(',')[1])
                encoded = int(instruction['encoding'],16)
                expected = ((address+3)&~3)+((encoded>>8)<<2)-0x40000
                require(literal==expected,'L32R operand differs from encoded literal address')
                value = self.image.word(literal)
                proof = [dict(instruction=address,literal_address=literal,literal_word=value)]
            elif writes and mnemonic=='movi':
                value,proof = int(operands[1],0)&0xffffffff,[dict(instruction=address,immediate=operands[1])]
            elif writes and (mnemonic=='mov' or (mnemonic=='or' and operands[1]==operands[2])):
                value,proof = self.constant(address,operands[1],trail)
            elif writes:
                raise ValueError('Unresolved indirect-call register writer '+mnemonic+' at '+hex(address))
            else:
                value,proof = self.constant(address,register,trail)
            values.append(value); proofs.extend(proof)
        require(len(set(values))==1,'Conflicting incoming indirect-call targets')
        return values[0],proofs

    def calls(self):
        calls = []
        for address,instruction in sorted(self.nodes.items()):
            mnemonic,args = instruction['mnemonic'],instruction['arguments']
            if not mnemonic.startswith('call'):
                continue
            if mnemonic in ('call0','call4','call8','call12'):
                target = number(args)
                encoded = int(instruction['encoding'],16)
                immediate = encoded>>6
                if immediate&0x20000: immediate-=0x40000
                require(target==((address&~3)+4+(immediate<<2))&0xffffffff,'Call operand differs from encoded target')
                proof = [dict(instruction=address,encoding=instruction['encoding'])]
            elif mnemonic in ('callx0','callx4','callx8','callx12'):
                require(REGISTER.fullmatch(args.strip()),'Unrecognized indirect call register')
                target,proof = self.constant(address,args.strip())
            else:
                raise ValueError('Unresolved reachable call mnemonic '+mnemonic)
            calls.append(dict(site=address,offset=address-self.start,instruction=mnemonic,
                              target=self.image.target(target),provenance=proof,
                              normalized_return_pc_expected=address))
        return calls

    def dominates_returns_once(self, call):
        nodes = set(self.nodes)
        dominators = {n:({n} if n==self.start else set(nodes)) for n in nodes}
        changed = True
        while changed:
            changed = False
            for n in sorted(nodes-{self.start}):
                predecessors = self.predecessors[n]
                value = {n}|set.intersection(*(dominators[p] for p in predecessors))
                if value!=dominators[n]: dominators[n]=value;changed=True
        require(self.exits and all(call in dominators[n] for n in self.exits),
                'Original allocator call does not dominate all wrapper exits')
        seen,queue = set(),deque(self.successors[call])
        while queue:
            n=queue.popleft()
            require(n!=call,'Wrapper can loop back to its real allocator call')
            if n not in seen:
                seen.add(n);queue.extend(self.successors[n])


def sdk_provenance(image, functions):
    units = [image.cu(function.symbol['address']) for function in functions]
    require(len({x['offset'] for x in units})==1,'SDK callers do not share one source CU')
    unit = units[0]
    source = Path(unit['source'].replace('\\','/')).resolve(strict=True)
    require(source.name=='tcp_out.c' and pin(source)['sha256']==TCP_SOURCE_SHA,'SDK tcp_out source changed')
    directory = Path(unit['directory'].replace('\\','/')).resolve()
    snapshots = {name:json.loads((BASE/'sdk-baseline'/name/'snapshot.json').read_bytes())
                 for name in OBJECT_PINS}
    profiles = [name for name,snapshot in snapshots.items() if
                snapshot['backend']==name and (ROOT/snapshot['cache']).resolve()==directory]
    require(len(profiles)==1,'Source CU is not tied to one frozen SDK reference profile')
    profile = profiles[0]
    pair = OBJECT_PINS[profile]
    object_path = BASE/'sdk-baseline'/profile/'tcp_out.c.obj'
    pbuf_object = object_path.with_name('pbuf.c.obj')
    for filename,expected in zip(('tcp_out.c.obj','pbuf.c.obj'),pair):
        require(pin(BASE/'sdk-baseline'/profile/filename)['sha256']==expected,
                'Frozen baseline SDK object changed')
    references=[]
    with object_path.open('rb') as stream:
        elf = ELFFile(stream)
        for section in elf.iter_sections():
            if section['sh_type'] not in ('SHT_REL','SHT_RELA'): continue
            symbols=elf.get_section(section['sh_link']);target=elf.get_section(section['sh_info'])
            for relocation in section.iter_relocations():
                symbol=symbols.get_symbol(relocation['r_info_sym'])
                if symbol.name=='pbuf_alloc':
                    require(symbol['st_shndx']=='SHN_UNDEF','tcp_out allocation is not an eligible undefined reference')
                    references.append(dict(section=target.name,offset=relocation['r_offset'],type=relocation['r_info_type']))
    require(len(references)==8,'Unexpected number of literal/ASM_EXPAND allocation relocations')
    for name in FUNCTIONS:
        require(sum(x['section']=='.literal.'+name and x['type']==1 for x in references)==1 and
                sum(x['section']=='.text.'+name and x['type']==11 for x in references)==1,
                'Expected one original external allocator reference per SDK function')
    return dict(profile=profile,cu=unit,source=dict(path=str(source),**pin(source)),
                object_scope='Frozen pre-probe SDK reference objects. Current build-object identity is independently checked by SDK qualification; no live build output is read here.',
                tcp_object=dict(path=str(object_path),**pin(object_path)),
                pbuf_object=dict(path=str(pbuf_object),**pin(pbuf_object)),references=references)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--elf',type=Path,required=True)
    parser.add_argument('--objdump',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    output=args.report.resolve()
    require(output.is_relative_to(ROOT/'.build') and not output.exists(),'Use a fresh report under the worktree .build')
    output.parent.mkdir(parents=True,exist_ok=True)
    raw=output.with_name(output.stem+'-raw');raw.mkdir(exist_ok=False)
    elf,objdump=args.elf.resolve(strict=True),args.objdump.resolve(strict=True)
    report=dict(passed=False,runtime_verified=False,physical_tested=False,
        scope='Conservative reachable instruction CFG and literal-backed call targets; branch feasibility and dynamic execution are not proved. '
              'Only the four pinned undefined tcp_out references are covered; same-object allocator paths remain separate.',
        elf=dict(path=str(elf),**pin(elf)),objdump=dict(path=str(objdump),**pin(objdump)),verifier=pin(Path(__file__)),
        source_inputs={p.relative_to(ROOT).as_posix():pin(p) for p in
            (ROOT/'tests/target/cyd_full_app_openeth_qemu/pbuf_failure.c',
             ROOT/'tests/target/cyd_full_app_openeth_qemu/pbuf_failure_record.h')},
        source_binding_scope='Current source byte identities; build-release/dependency binding is independently owned by SDK qualification.')
    image=None;decoder=None
    try:
        image=Image(elf);decoder=Decoder(image,objdump,raw)
        wrapper_symbol=image.function('__wrap_pbuf_alloc');real=image.function('pbuf_alloc')
        require(wrapper_symbol['address']!=real['address'],'Wrapper aliases original allocator')
        functions=[Function(image,decoder,image.function(name,'STB_LOCAL' if '$' in name else 'STB_GLOBAL')) for name in FUNCTIONS]
        report['sdk_provenance']=sdk_provenance(image,functions)
        sites=[]
        for function in functions:
            calls=function.calls()
            allocations=[c for c in calls if c['target']['address'] in (real['address'],wrapper_symbol['address'])]
            require(len(allocations)==1,'Not exactly one resolved allocator call in '+function.symbol['name'])
            call=allocations[0]
            require(call['instruction'] in ('call8','callx8') and call['target']['address']==wrapper_symbol['address'],
                    'SDK external allocation bypasses wrapper in '+function.symbol['name'])
            sites.append(dict(function=function.symbol,call=call,reachable_instructions=len(function.nodes)))
        report['tcp_out_sites']=sites
        wrapper=Function(image,decoder,wrapper_symbol);calls=wrapper.calls()
        report['wrapper_calls']=calls
        require(not any(c['target']['address']==wrapper_symbol['address'] for c in calls),'Wrapper calls itself')
        original=[c for c in calls if c['target']['address']==real['address']]
        require(len(original)==1 and original[0]['instruction'] in ('call8','callx8'),'Wrapper does not call the original allocator exactly once')
        wrapper.dominates_returns_once(original[0]['site'])
        clone=Function(image,decoder,image.function('pbuf_clone'));clone_calls=clone.calls()
        negative=[c for c in clone_calls if c['target']['address']==real['address']]
        require(len(negative)==1 and not any(c['target']['address']==wrapper_symbol['address'] for c in clone_calls),
                'Expected same-object clone blind-spot witness changed')
        report.update(symbols=dict(wrapper=wrapper_symbol,original=real),
            wrapper_real_call_dominates_exits_without_cycle=True,
            same_object_clone_blind_spot=dict(function=clone.symbol,original_allocator_call=negative[0]),
            storage={})
        for name in ('s_pbuf_failures','s_pbuf_failure_lock'):
            symbols=[s for s in image.table.get_symbol_by_name(name) or [] if s['st_info']['type']=='STT_OBJECT']
            require(len(symbols)==1 and isinstance(symbols[0]['st_shndx'],int),'Ambiguous diagnostic storage owner')
            s=symbols[0];section=image.sections[s['st_shndx']]
            require(section.name in ('.dram0.bss','.dram0.data') and section['sh_flags']&3==3 and
                    0x3ffae000<=s['st_value']<s['st_value']+s['st_size']<=0x40000000,
                    'Diagnostic owner is not ordinary writable internal DRAM')
            report['storage'][name]=dict(address=s['st_value'],bytes=s['st_size'],section=section.name)
        require(report['storage']['s_pbuf_failures']['bytes']==128,'Diagnostic table ABI changed')
        require(pin(elf)=={k:report['elf'][k] for k in ('bytes','sha256')},'ELF changed during verification')
        for path,expected in report['source_inputs'].items():
            require(pin(ROOT/path)==expected,'Source changed during verification')
        report['passed']=True
    except (OSError,ValueError,KeyError,struct.error,subprocess.SubprocessError) as error:
        report['reason']=str(error)
    finally:
        if decoder: report['raw_disassembly']=decoder.outputs
        if image: image.close()
        output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(passed=report['passed'],reason=report.get('reason'),
                         tcp_out_sites=len(report.get('tcp_out_sites',[])),wrapper_calls=report.get('wrapper_calls'))))
    return 0 if report['passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
