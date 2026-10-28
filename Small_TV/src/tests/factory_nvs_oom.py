"""Follow the actual factory NVS allocation to abort and current NVS to ESP_ERR_NO_MEM."""
from unicorn import riscv_const as rv

from audit_factory_xrefs import Image
from reverse.factory_nvs import PAGE
from reverse.nothrow_linkage import LinkedRuntime
from reverse.runtime_call_gaps import binding
from runtime_call_instructions import Fixture, END, PRESERVED
from factory_nvs_target import setup


def run(factory, native, app, nvs, old_runtime, new_runtime):
    """Retain actual allocator/helper/stub instructions; model only malloc, handler and SDK I/O."""
    linked = LinkedRuntime(native, app); results = {}
    assert old_runtime['factory_elf_sha256'] == nvs['factory_elf_sha256']
    assert new_runtime['elf_sha256'] == nvs['native_elf_sha256']
    for variant, reader in (('factory', Image(factory).read), ('native', linked.read)):
        private = nvs['variants'][variant]
        allocator = old_runtime['variants']['factory']['functions'] if variant == 'factory' else new_runtime['functions']
        definition = dict(functions=[r for r in private['functions'] if r['name'] != '_ZN3nvs4Page15mLoadEntryTableEv']+allocator,
                          allocator_veneer=None)
        f = Fixture(variant+'-nvs-oom', definition, reader)
        page, _, _, _, _, _, _, _, _ = setup(f, private, dict(name='actual-runtime-oom'), variant)
        # The normal caller matrix deliberately injects an allocator result. Remove only that
        # hook here: the already mapped allocator bytes now run, including the factory throw stubs.
        del f.callbacks[private['allocation_boundary']]
        scalar = next(r for r in allocator if r['name'] == '_Znwj') if variant == 'factory' else None
        malloc = binding(scalar, 'malloc') if scalar else linked.symbol('malloc')['st_value']
        handler = binding(scalar, '_ZSt15get_new_handlerv') if scalar else linked.symbol('_ZSt15get_new_handlerv')['st_value']
        def allocation_failure(args):
            """Force one genuine 512-byte allocation failure before the allocator's own decisions."""
            assert args[0] == 512; return 0
        f.boundary('malloc', malloc, allocation_failure)
        f.boundary('get_new_handler', handler, lambda args: 0)
        if variant == 'factory':
            f.boundary('abort', old_runtime['variants']['factory']['abort_boundary'], lambda args: f.stop('abort'))
        f.cpu.emu_start(int(f.rows[PAGE]['start'], 0), END, count=4096)
        if variant == 'factory':
            assert f.stopped == 'abort' and 0x42040f80 not in f.visited
            assert [n for n, a in f.events] == ['read_raw', 'malloc', 'get_new_handler', 'abort']
            outcome = 'abort'
        else:
            assert f.stopped is None and f.cpu.reg_read(rv.UC_RISCV_REG_PC) == END and f.reg(10) == 0x101
            for register in PRESERVED: assert f.reg(register) == f.initial[register]
            assert [n for n, a in f.events] == ['memset', 'read_raw', 'malloc', 'get_new_handler']
            outcome = 'ESP_ERR_NO_MEM'
        assert f.word(page+12) == 0xffffffff and f.word(page+8) == 8192
        results[variant] = dict(outcome=outcome, events=[n for n, a in f.events], visited=sorted(f.visited))
    return dict(passed=True, results=results, factory_nothrow_contract_passed=False,
                native_nothrow_contract_passed=True, full_vm_fault_injection_proved=False, physical_hardware_tested=False)
