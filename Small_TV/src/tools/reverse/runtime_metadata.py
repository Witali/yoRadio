"""Check scoped Ghidra runtime recovery against complete object matches and raw RV32 bytes."""
from copy import deepcopy
import json

from audit_factory_xrefs import sha
from reverse.runtime_call_gaps import CASES
from reverse.rv32_link_match import branch_target, link_register

DETACHED = ((0x420a3e08, 0x420a3e0a), (0x420a3fe0, 0x420a3fe8))


def require(condition, message):
    """Keep evidence rejection active even if Python is invoked with optimization."""
    if not condition:
        raise ValueError(message)


def instructions(code, start):
    """Split only qualified RV32/RVC bytes, including disconnected landing pads."""
    result = []; offset = 0
    while offset < len(code):
        length = 4 if code[offset] & 3 == 3 else 2
        require(offset + length <= len(code), 'Truncated runtime instruction')
        result.append(dict(pc=f'0x{start+offset:08x}', bytes=code[offset:offset+length].hex()))
        offset += length
    return result


def specification(qualification):
    """Derive ten extents only from the independently recomputed full-object qualification."""
    require(qualification['passed'], 'Runtime qualification failed')
    rows = qualification['variants']['factory']['functions']
    require({(r['name'], int(r['start'], 0)) for r in rows} == {(n, a) for n, _, a in CASES},
            'Different runtime function selection')
    result = []
    for row in sorted(rows, key=lambda r: int(r['start'], 0)):
        code = b''.join(bytes.fromhex(t['linked_bytes']) for t in row['transformations'])
        decoded = instructions(code, int(row['start'], 0))
        require(sha(code) == row['code_sha256'] and len(code) == row['linked_bytes'] and
                len(decoded) == row['linked_instruction_starts'] and
                int(row['end'], 0) - int(row['start'], 0) == len(code), 'Incomplete runtime body')
        result.append({**{k: row[k] for k in ('name', 'start', 'end', 'code_sha256')}, 'instructions': decoded})
    return dict(schema='factory-runtime-metadata-manifest-v1',
                factory_elf_sha256=qualification['factory_elf_sha256'], functions=result)


def static_target(image, pc, raw):
    """Resolve direct control flow and an adjacent AUIPC/JALR pair without trusting Ghidra."""
    try:
        return branch_target(raw, pc)
    except ValueError:
        pass
    word = int.from_bytes(raw, 'little')
    if len(raw) == 4 and word & 127 == 0x67:
        before = int.from_bytes(image.read(pc-4, 4, True), 'little')
        if before & 127 == 0x17 and (before >> 7) & 31 == (word >> 15) & 31:
            immediate = word >> 20
            if immediate & 0x800: immediate -= 0x1000
            return ((pc-4 + (before & 0xfffff000) + immediate) & 0xffffffff) & ~1
    return None


def normalized(graph):
    """Ignore database reference iteration order, retaining every reference field and duplicate."""
    result = deepcopy(graph)
    for row in result['functions']:
        row['references'].sort(key=lambda r: json.dumps(r, sort_keys=True))
    return result


def compact_calls(image, graph):
    """Scan all executable bytes at real instruction boundaries, then check exact graph edges."""
    calls = []
    for section in image.sections:
        if not section['execute']: continue
        for row in instructions(section['data'], section['start']):
            raw = bytes.fromhex(row['bytes']); pc = int(row['pc'], 0)
            if len(raw) == 2 and int.from_bytes(raw, 'little') & 0xe003 == 0x2001:
                calls.append((pc, branch_target(raw, pc), row['bytes']))
    known = {int(f['entry'], 0): f for f in graph['functions']}
    missing = []; unknown = []
    for pc, target, raw in calls:
        if target not in known:
            unknown.append(f'0x{target:08x}'); missing.append(f'0x{pc:08x}'); continue
        matches = [r for r in known[target]['references'] if r['from_space'] == 'ram' and int(r['from'], 0) == pc
                   and r['bytes'] == raw and r['type'] == 'UNCONDITIONAL_CALL' and
                   int(r['to'], 0) == target and r['to_space'] == 'ram']
        if len(matches) != 1: missing.append(f'0x{pc:08x}')
    return dict(total=len(calls), missing_references=missing, unknown_targets=unknown)


def verify(image, qualification, manifest, recovery, before, after):
    """Rebuild the entire graph change, accepting only qualified bodies and their actual edges."""
    require(manifest == specification(qualification), 'Runtime recovery manifest differs')
    require(recovery['schema'] == 'factory-runtime-metadata-recovery-v1' and
            recovery['program_sha256'] == manifest['factory_elf_sha256'] == before['program_sha256'], 'Wrong recovery image')
    blocks = {b['name']: b['sha256'] for b in before['memory_blocks'] if b['initialized']}
    require(recovery['memory_before'] == recovery['memory_after'] == blocks and
            recovery['program_bytes_unchanged'] and not recovery['whole_image_completeness_proved'], 'Memory/coverage claim differs')
    specs = {r['start']: r for r in manifest['functions']}
    old = {f['entry']: f for f in before['functions']}
    require(len(recovery['functions']) == len(specs) == 10, 'Missing/duplicate recovered function')
    expected = deepcopy(before); funcs = {f['entry']: f for f in expected['functions']}
    all_instructions = []; starts = set(); created = 0
    for row, spec in zip(recovery['functions'], manifest['functions'], strict=True):
        start, end = int(spec['start'], 0), int(spec['end'], 0)
        require(sha(image.read(start, end-start, True)) == spec['code_sha256'], 'Factory code differs')
        description = dict(entry=spec['start'], name=spec['name'], body_bytes=end-start,
                           ranges=[[spec['start'], f'0x{end-1:08x}']])
        require(row['after'] == description, 'Recovered function ownership differs')
        existed = spec['start'] in old
        require(row['created_function'] == (not existed), 'Incorrect created-function claim')
        if existed:
            prior = row['before']; original = old[spec['start']]
            require({k: prior[k] for k in ('entry', 'name', 'body_bytes')} ==
                    {k: original[k] for k in ('entry', 'name', 'body_bytes')}, 'Original owner differs')
            addresses = set()
            for first, last in prior['ranges']:
                addresses.update(range(int(first, 0), int(last, 0)+1))
            require(len(addresses) == prior['body_bytes'], 'Invalid original ranges')
            if start in (0x420a3da2, 0x420a3fc8):
                original_end = 0x420a3e0a if start == 0x420a3da2 else 0x420a3fe8
                require(addresses == set(range(start, original_end)), 'Unexpected merged body')
            else:
                require(addresses <= set(range(start, end)), 'Unqualified bytes detached')
        else:
            require(row['before'] == {}, 'Invented original function'); created += 1
        require([{k: r[k] for k in ('pc', 'bytes')} for r in row['instructions']] == spec['instructions'],
                'Instruction byte boundaries differ')
        all_instructions.extend(row['instructions']); starts.update(int(r['pc'], 0) for r in row['instructions'])
        if not existed: funcs[spec['start']] = dict(entry=spec['start'], space='ram', references=[])
        funcs[spec['start']].update({k: description[k] for k in ('name', 'body_bytes')})
    require(created == 3, 'Unexpected function creation count')
    require(len(recovery['detached']) == len(DETACHED), 'Lost detached instructions')
    for row, (start, end) in zip(recovery['detached'], DETACHED, strict=True):
        require((row['start'], row['end'], row['owner']) == (f'0x{start:08x}', f'0x{end:08x}', {}),
                'Detached bytes acquired a guessed owner')
        require([{k: r[k] for k in ('pc', 'bytes')} for r in row['instructions']] ==
                instructions(image.read(start, end-start, True), start), 'Detached bytes changed')
        all_instructions.extend(row['instructions'])
    existing = [int(pc, 0) for pc in recovery['instruction_starts_before']]
    require(len(existing) == len(set(existing)) and set(existing) <= starts, 'Invalid original instruction starts')
    added = len(starts - set(existing))
    require(recovery['instruction_count_before'] == before['instruction_count'] and
            recovery['instruction_count_after'] == before['instruction_count'] + added, 'Unscoped instruction change')
    # This database's API count is five larger than its enumerated memory functions.
    # Keep both observations; do not turn that pre-existing discrepancy into coverage.
    require(recovery['function_count_before'] == len(before['functions']) + 5 and
            recovery['function_count_after'] == len(after['functions']) + 5 and
            recovery['function_count_after'] - recovery['function_count_before'] == created, 'Function API count differs')
    by_pc = {int(r['pc'], 0): r for r in all_instructions}
    require(len(by_pc) == len(all_instructions), 'Duplicate instruction evidence')
    # Keep every old reference outside these bodies; rebuild all in-scope references from instructions.
    for function in funcs.values():
        function['references'] = [r for r in function['references'] if r['from_space'] != 'ram' or int(r['from'], 0) not in by_pc]
    for pc, instruction in by_pc.items():
        owner = {}
        for spec in specs.values():
            if int(spec['start'], 0) <= pc < int(spec['end'], 0): owner = dict(entry=spec['start'], name=spec['name'])
        for ref in instruction['references']:
            target = f"0x{ref['offset']:08x}"
            if ref['space'] != 'ram' or target not in funcs: continue
            raw = bytes.fromhex(instruction['bytes'])
            target_from_code = static_target(image, pc, raw)
            if target_from_code is None:
                # Preserve the existing bad_alloc destructor argument only when its full-object
                # data relocation and original analysis edge agree; do not infer a new data alias.
                bindings = [b for r in qualification['variants']['factory']['functions']
                            if r['start'] == owner.get('entry') for b in r['symbol_bindings']
                            if b['kind'] == 'data' and b['address'] == ref['offset']]
                original = [r for r in old.get(target, {}).get('references', [])
                            if r['from_space'] == 'ram' and r['from'] == instruction['pc'] and r['type'] == ref['type']]
                require(len(bindings) == len(original) == 1 and ref['type'] == 'PARAM', 'Unqualified function data alias')
            else:
                require(target_from_code == ref['offset'], 'Reference target differs from RV32 code')
            lr = link_register(raw)
            if lr is not None:
                require(ref['type'] == ('UNCONDITIONAL_CALL' if lr == 1 else 'UNCONDITIONAL_JUMP'), 'Reference control-flow type differs')
            funcs[target]['references'].append(dict(
                **{'from': instruction['pc'], 'to': target, 'from_space': 'ram', 'to_space': 'ram'},
                type=ref['type'], source=ref['source'], operand=ref['operand'], owner=owner,
                mnemonic=instruction['mnemonic'], bytes=instruction['bytes']))
    expected['functions'] = sorted(funcs.values(), key=lambda r: int(r['entry'], 0))
    expected['instruction_count'] += added
    require(normalized(expected) == normalized(after), 'Unqualified graph alteration or missing reference')
    initial, final = compact_calls(image, before), compact_calls(image, after)
    require(initial['total'] == final['total'] == 453 and
            set(initial['missing_references']) == {f"0x{g['pc']:08x}" for g in qualification['gaps']} and
            initial['unknown_targets'] == ['0x420a3fd4'] and
            final['missing_references'] == final['unknown_targets'] == [], 'Compact-call coverage differs')
    return dict(passed=True,qualified_functions=10,qualified_bytes=508,created_functions=created,
                enumerated_before=len(before['functions']),enumerated_after=len(after['functions']),
                function_api_before=recovery['function_count_before'],function_api_after=recovery['function_count_after'],
                added_instructions=added,detached_unowned_bytes=10,before=initial,after=final,
                whole_image_completeness_proved=False,semantic_equivalence_proved=False,
                persistent_project_modified=False,physical_hardware_tested=False)
