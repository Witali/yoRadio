"""Check the factory's complete std::find_if helper at unroll and remainder boundaries."""
from unicorn import UC_HOOK_MEM_READ

from audit_factory_xrefs import Image
from reverse.factory_nvs import FIND
from reverse.runtime_metadata import instructions
from runtime_call_instructions import Fixture, HEAP


def run(factory, qualified):
    """Execute every possible dirty position for small arrays and lengths127/128/129."""
    image = Image(factory); row = next(r for r in qualified['variants']['factory']['functions'] if r['name'] == FIND)
    definition = dict(functions=[row], allocator_veneer=None); block = HEAP+1536
    results = []; visited = set()
    for length in (*range(10), 127, 128, 129):
        for dirty in (None, *range(length)):
            f = Fixture('factory-find-if', definition, image.read)
            f.cpu.mem_write(block, b'\xff'*(length*4))
            if dirty is not None: f.word(block+dirty*4, 0xfffffffe)
            f.reg(10, block); f.reg(11, block+length*4); f.reg(12, 0); f.reg(13, 0)
            reads = []
            def read(cpu, access, address, size, value, data):
                """Forbid every array read past either end, including the zero-length case."""
                if HEAP <= address < HEAP+4096:
                    assert block <= address < address+size <= block+length*4
                    reads.append((address-block, size))
            f.cpu.hook_add(UC_HOOK_MEM_READ, read); f.run(FIND)
            result = length if dirty is None else dirty
            assert f.reg(10) == block+result*4
            results.append(dict(length=length, dirty=dirty, result_index=result, reads=len(reads)))
            visited.update(f.visited)
    start = int(row['start'], 0)
    starts = {int(i['pc'], 0) for i in instructions(image.read(start, row['linked_bytes'], True), start)}
    assert starts <= visited, [hex(pc) for pc in sorted(starts-visited)]
    return dict(passed=True, cases=len(results), results=results, helper_instruction_starts=len(starts), visited=sorted(starts & visited))
