"""Check event-11 registration through actual instructions and disposable state."""
import argparse
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_factory_xrefs import Image, sha
from reverse.timer_event11_registration import qualify
from reverse.rv32_link_match import size_at
from timer_event11_semantics import reader
from timer_registration_instructions import RegistrationProbe


def attach_writes(cfg):
    """Independent model of direct pm_attach stores; helper bodies stay external."""
    word = lambda at: int.from_bytes(cfg[at:at + 4], 'little')
    return [[36,4,1], [44,4,word(8)], [48,4,word(16)], [11,1,1], [60,4,word(20)],
            [52,4,0x19000], [34,2,1], [56,4,word(32)], [64,4,word(36)],
            [388,4,0x30000], [452,4,word(68)], [12,1,1], [26,2,1], [15,1,1],
            [72,4,0], [23,1,0], [385,1,0], [386,2,0], [468,1,0],
            [424,4,0], [289,1,0], [428,4,0], [398,2,0], [457,1,1], [0,1,1]]


def exercise(layout, read):
    """Check first registration, failure propagation, repeated calls and saved callback use."""
    probe = RegistrationProbe(layout, read)
    version = layout['prior']['osi_table']['version']
    rows, registrations = [], []
    for existing, null, supplied_version, magic, gateway in product(
            (0, 0x76543000), (False, True), (version, 8 if version == 9 else 9, 0xffffffff),
            (0xdeadbeaf, 0), (False, True)):
        probe.reset(existing, supplied_version, magic)
        valid = not null and supplied_version == version and magic == 0xdeadbeaf
        accepted = bool(existing) or valid
        if gateway:
            trace = probe.invoke('esp_wifi_init_internal', 0 if null else probe.CONFIG)
            # Force a known API-lock failure only after the real registration
            # returns. Later Wi-Fi initialization effects are not being simulated.
            result = probe.lock_return if not null and accepted else 258
            expected_pointer = existing or (probe.table if not null and valid else 0)
            assert sum(c[0] == 'lock' for c in trace['calls']) == int(not null and accepted)
        else:
            trace = probe.invoke('wifi_osi_funcs_register', 0 if null else probe.table)
            result = 0 if accepted else 258
            expected_pointer = existing or (probe.table if valid else 0)
            assert not any(c[0] == 'lock' for c in trace['calls'])
        assert trace['return_value'] == result
        assert probe.word(probe.osi_global) == expected_pointer
        expected_stores = [[probe.osi_global, probe.table]] if not existing and not null and valid else []
        assert trace['globals'] == expected_stores
        assert not trace['writes']
        # The SDK deliberately ignores a replacement table once registered;
        # gateway still rejects a null configuration before calling registration.
        printed = sum(c[0] in ('puts', 'printf') for c in trace['calls'])
        assert printed == int((gateway and null) or (not existing and not valid))
        rows.append(dict(existing=existing, null=null, version=supplied_version, magic=magic,
                         gateway=gateway, trace=trace, pointer=expected_pointer))
    for initial_fill in (0, 0xa5):
        probe.reset()
        trace = probe.invoke('wifi_osi_funcs_register', probe.table)
        assert trace['return_value'] == 0 and probe.word(probe.osi_global) == probe.table
        probe.cpu.mem_write(probe.pm, bytes([initial_fill]) * probe.layout['g_pm_bytes'])
        cfg = bytes(probe.cpu.mem_read(probe.cfg, probe.layout['g_pm_cfg_bytes']))
        trace = probe.invoke('pm_attach')
        assert trace['writes'] == attach_writes(cfg), (trace['writes'], attach_writes(cfg))
        expected_pm = bytearray(probe.layout['g_pm_bytes'])
        for offset, size, value in attach_writes(cfg):
            expected_pm[offset:offset + size] = value.to_bytes(size, 'little')
        assert bytes(probe.cpu.mem_read(probe.pm, len(expected_pm))) == expected_pm
        assert bytes(probe.cpu.mem_read(probe.cfg, len(cfg))) == cfg
        bindings = {b['name']: b['address'] for b in layout['functions'][2]['symbol_bindings']}
        timeout = layout['timer_timeout_name']
        callbacks = ((180,'pm_dream_timeout'), (200,'pm_active_timeout'), (260,'pm_sleep_delay_timeout'),
                     (240,'pm_coex_slice_wifi_timeout'), (296,'pm_disconnected_sleep_delay_timeout'),
                     (316,'pm_connectionless_wake_interval_timeout'), (336,'pm_connectionless_wake_window_timeout'),
                     (364,'pm_beacon_monitor_timeout'), (492,timeout), (512,'pm_coex_restart_timeout'))
        expected = {probe.pm + offset: (bindings[name], probe.pm if offset == 364 else 0)
                    for offset, name in callbacks}
        assert probe.timer_bindings == expected
        calls = [c for c in trace['calls'] if c[0] == 'setfn']
        assert calls == [['setfn', address, *values] for address, values in expected.items()]
        assert trace['calls'][0] == ['memset', probe.pm, 0, len(expected_pm)]
        assert [c for c in trace['calls'] if c[0] == 'set-state'] == [['set-state', 0]]
        registrations.append(dict(initial_fill=initial_fill, trace=trace, timer_bindings=expected))
        callback, argument = probe.timer_bindings[probe.pm + 492]
        assert callback == probe.entries[timeout] and argument == 0
        no_post = probe.invoke(callback, argument)
        assert no_post['return_value'] == 0xffffffff and not no_post['calls']
        register = probe.invoke('pp_timer_register_post_cb', probe.POST)
        assert register['return_value'] == 0 and probe.word(probe.post_slot) == probe.POST
        for result in (0, 1, 0xfffffffb):
            probe.post_return = result
            posted = probe.invoke(callback, argument)
            assert posted['return_value'] == result
            assert posted['calls'] == [['post', 8, 11, 0]] and not posted['globals'] and not posted['writes']
            registrations.append(dict(post_result=result, trace=posted))
        remove = probe.invoke('pp_timer_register_post_cb', 0)
        assert remove['return_value'] == 0 and probe.word(probe.post_slot) == 0
        assert probe.invoke(callback, argument)['return_value'] == 0xffffffff
    coverage = []
    for row in (*layout['functions'], layout['timer_setfn']):
        start = int(row['start'], 0); raw = read(start, row['linked_bytes'])
        addresses, offset = set(), 0
        while offset < len(raw):
            addresses.add(start + offset); offset += size_at(raw, offset)
        missing = addresses - probe.visited
        # The gateway intentionally exits at API lock: initialization after that
        # point is neither stubbed wholesale nor claimed as covered.
        if row['name'] != 'esp_wifi_init_internal':
            assert not missing, (row['name'], sorted(map(hex, missing)))
        coverage.append(dict(name=row['name'], instruction_starts=len(addresses),
                             visited=len(addresses & probe.visited), missing=sorted(map(hex, missing))))
    return dict(passed=True, registration_cases=len(rows), cases=rows,
                timer_initialization_and_posts=registrations, coverage=coverage,
                complete_wifi_initialization_executed=False, backend_timer_effects_stubbed=True,
                actual_guest_runtime_observed=False, physical_hardware_tested=False)


def run(factory, native, old_pp, new_pp, old_net, new_net):
    """Qualify exact code before using any private instruction fixture."""
    result = qualify(factory, native, old_pp, new_pp, old_net, new_net)
    observed = {variant: exercise(result['layouts'][variant], reader(data))
                for variant, data in (('factory', factory), ('native', native))}
    image = Image(factory)
    attach = result['layouts']['factory']['functions'][2]
    raw = image.read(int(attach['start'], 0), attach['linked_bytes'], True)
    timeout = result['layouts']['factory']['functions'][3]
    timeout_raw = image.read(int(timeout['start'], 0), timeout['linked_bytes'], True)
    assert timeout_raw[2:4] == bytes.fromhex('2d45')
    controls = {
        'wrong-net-sdk': lambda: qualify(factory, native, old_pp, new_pp, new_net, old_net),
        'truncated-attach': lambda: qualify(factory, native, old_pp, new_pp, old_net, new_net,
                                             {('factory', 'pm_attach'): raw[:-2]}),
        'neighboring-attach': lambda: qualify(factory, native, old_pp, new_pp, old_net, new_net,
                                               {('factory', 'pm_attach'): image.read(int(attach['end'], 0), len(raw), True)}),
        'wrong-posted-event': lambda: qualify(factory, native, old_pp, new_pp, old_net, new_net,
                                               {('factory', 'pm_max_idle_timeout'): timeout_raw[:2] + bytes.fromhex('3145') + timeout_raw[4:]}),
    }
    rejected = []
    for name, action in controls.items():
        try: action()
        except (AssertionError, ValueError): rejected.append(name)
        else: raise AssertionError('Invalid registration accepted: ' + name)
    return dict(passed=True, qualification=result, instructions=observed, rejected_controls=rejected,
                full_runtime_lifecycle_proved=False, whole_image_completeness_proved=False,
                physical_hardware_tested=False)


def main():
    """Save a fresh host-only registration checkpoint; inputs remain unchanged."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('factory', 'native', 'old-pp', 'new-pp', 'old-net', 'new-net', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists(): raise ValueError('Preserve previous registration evidence')
    inputs = [args.factory, args.native, args.old_pp, args.new_pp, args.old_net, args.new_net]
    root = Path(__file__).resolve().parents[1]
    inputs += [root / name for name in (
        'tools/reverse/timer_event11_registration.py', 'tests/timer_registration_test.py',
        'tests/timer_registration_instructions.py', 'tests/timer_event11_instructions.py',
        'tests/timer_event11_semantics.py', 'tests/timer_event11_model.py',
        'tools/reverse/timer_event11_match.py', 'tools/audit_factory_xrefs.py',
        'tools/reverse/rv32_link_match.py', 'tools/reverse/elf_archive.py')]
    pins = {str(path.resolve()): sha(path.read_bytes()) for path in inputs}
    result = run(args.factory.read_bytes(), args.native.read_bytes(), args.old_pp, args.new_pp, args.old_net, args.new_net)
    assert all(sha(Path(path).read_bytes()) == digest for path, digest in pins.items())
    result.update(inputs_unchanged=True, inputs_sha256=pins)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(passed=True, controls=result['rejected_controls'],
                          coverage={v:r['coverage'] for v,r in result['instructions'].items()})))


if __name__ == '__main__': main()
