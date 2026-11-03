"""Compare original and guarded BSS processing using their actual RV32 instructions."""
import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_factory_xrefs import Image, sha
from reverse.bss_assoc import qualify
from reverse.nothrow_linkage import LinkedRuntime
from reverse.rv32_link_match import size_at
from verify_wifi_bss import verify, SDK_NAME
from bss_assoc_instructions import AssocProbe


def run(factory, before, before_app, elf, app, old_net, libraries, own):
    """Require failing old inputs, safe short-IE handling and unchanged valid values."""
    baseline = qualify(factory, before, before_app, old_net, libraries / 'libnet80211.a')
    guarded = verify(elf, app, libraries, own)
    images = dict(factory=Image(factory), before=LinkedRuntime(before, before_app),
                  guarded=LinkedRuntime(elf, app))
    layouts = dict(factory=baseline['layouts']['factory'], before=baseline['layouts']['native'],
                   guarded=guarded['layout'])
    probes = {name: AssocProbe(name, layouts[name], image.read) for name, image in images.items()}
    counts, samples = Counter(), {}
    digest = hashlib.sha256()

    def record(name, family, result):
        """Retain a deterministic digest and a small readable set of regression witnesses."""
        counts[name + ':' + family] += 1
        digest.update(json.dumps([name, family, result], sort_keys=True, separators=(',', ':')).encode())

    for length, enabled, tail, route in product(range(256), (0, 256), (False, True),
                                               ('direct', 'association', 'reassociation')):
        payload = bytes((length + 37 * i) & 255 for i in range(length))
        ies = bytes([90, length]) + payload + (b'\xf0\x03ABC' if tail else b'')
        short = enabled and length < 3
        values = {}
        for name, probe in probes.items():
            stop = 'input-overread' if short and name != 'guarded' else 'bss-join'
            try:
                result = probe.call(ies, feature_word=enabled, management=route != 'direct',
                                    subtype=48 if route == 'reassociation' else 16, expected_stop=stop)
            except AssertionError as error:
                raise AssertionError((name, length, enabled, tail, route)) from error
            if short and name != 'guarded':
                assert result['overreads'] and result['overreads'][0]['element_oob']
                if not tail:
                    assert result['overreads'][0]['packet_oob']
            else:
                assert not result['overreads']
                expected = ((payload[0] | payload[1] << 8, payload[2] & 1)
                            if enabled and length >= 3 else (probe.INITIAL_PERIOD, probe.INITIAL_OPTIONS))
                assert (result['period'], result['options']) == expected
                assert result['bss_logs'] == ([dict(period=expected[0], option='TRUE' if expected[1] else 'FALSE')]
                                             if enabled and length >= 3 else [])
                values[name] = (result['period'], result['options'], result['bss_logs'])
            record(name, 'all-lengths-ingress', result)
            if enabled and length < 4 and not tail and route == 'association':
                samples[name + ':length-' + str(length)] = result
        if not short:
            assert values['factory'] == values['before'] == values['guarded']

    for period, option in product((0, 1, 255, 256, 4196, 4197, 32772, 65535), range(256)):
        ies = bytes([90, 3, period & 255, period >> 8, option])
        for name, probe in probes.items():
            result = probe.call(ies)
            assert not result['overreads']
            assert (result['period'], result['options']) == (period, option & 1)
            assert result['bss_logs'] == [dict(period=period, option='TRUE' if option & 1 else 'FALSE')]
            record(name, 'periods-options', result)

    for name, probe in probes.items():
        result = probe.call(b'', setter_only=True, expected_stop=None)
        assert not result['overreads'] and not result['writes'] and not result['bss_logs']
        assert (result['period'], result['options']) == (probe.INITIAL_PERIOD, probe.INITIAL_OPTIONS)
        record(name, 'null-setter', result)
        for route, ies in product(('direct', 'association', 'reassociation'),
                                  (b'', b'\xf0\x03ABC', b'\x5a\x03\x12\x34\x01\x5a\x03\x56\x78\x00')):
            result = probe.call(ies, management=route != 'direct', subtype=48 if route == 'reassociation' else 16)
            assert not result['overreads']
            # The real parser selects the last complete BSS IE, matching the
            # original duplicate-element behavior rather than a new parser.
            expected = (0x7856, 0) if ies.startswith(b'\x5a') else (probe.INITIAL_PERIOD, probe.INITIAL_OPTIONS)
            assert (result['period'], result['options']) == expected
            record(name, 'absent-duplicate', result)
        for subtype, length in product((16, 48), range(6)):
            result = probe.call(b'', management=True, subtype=subtype, truncate_body=length, expected_stop=None)
            assert not result['association_ingress'] and not result['overreads']
            record(name, 'truncated-fixed-header', result)
        for ies in (b'\x5a', b'\x5a\x04\x01\x02\x03', b'\x5a\xff\x01\x02\x03'):
            result = probe.call(ies, management=True,
                                expected_stop='bss-join' if len(ies) == 1 else 'management-return')
            assert not result['overreads'] and not result['setter_ingress']
            assert (result['period'], result['options']) == (probe.INITIAL_PERIOD, probe.INITIAL_OPTIONS)
            record(name, 'truncated-ie', result)

    coverage = []
    for name, probe in probes.items():
        row = probe.rows_by_name[SDK_NAME]
        start = int(row['start'], 0)
        code = images[name].read(start, row['linked_bytes'], True)
        starts, offset = set(), 0
        while offset < len(code):
            starts.add(start + offset)
            offset += size_at(code, offset)
        assert starts <= probe.visited, (name, sorted(starts - probe.visited))
        coverage.append(dict(variant=name, bytes=len(code), instruction_starts=len(starts), visited=len(starts)))

    # A stale binary, mismatched descriptor or altered compiled implementation
    # must not receive a passing production linkage report.
    changed = bytearray(own)
    from elftools.elf.elffile import ELFFile
    import io
    obj = ELFFile(io.BytesIO(own))
    symbols = obj.get_section_by_name('.symtab')
    symbol = next(s for s in symbols.iter_symbols() if s.name == 'small_tv_wifi_set_bss_max_idle_period')
    position = obj.get_section(symbol['st_shndx'])['sh_offset'] + symbol['st_value']
    changed[position] ^= 1
    controls = {
        'old-build-has-no-guard': lambda: verify(before, before_app, libraries, own),
        'mismatched-app-descriptor': lambda: verify(elf, before_app, libraries, own),
        'changed-guard-opcode': lambda: verify(elf, app, libraries, bytes(changed)),
    }
    rejected = []
    for name, action in controls.items():
        try:
            action()
        except (AssertionError, ValueError):
            rejected.append(name)
        else:
            raise AssertionError('Invalid BSS guard accepted: ' + name)
    return dict(passed=True, baseline=baseline, guarded=guarded, counts=dict(counts),
        executions=sum(counts.values()), trace_sha256=digest.hexdigest(), samples=samples,
        setter_coverage=coverage, rejected_controls=rejected, all_256_ie_lengths_executed=True,
        all_256_option_bytes_executed=True, full_association_lifecycle_proved=False,
        external_rx_reachability_proved=False, whole_image_completeness_proved=False,
        physical_hardware_tested=False)


def main():
    """Save fresh evidence and verify its local input files remained unchanged."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('factory', 'before', 'before-app', 'elf', 'app', 'old-net', 'sdk-libraries', 'object', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    files = [args.factory, args.before, args.before_app, args.elf, args.app, args.old_net, args.object,
             *sorted(args.sdk_libraries.glob('*.a'))]
    root = Path(__file__).resolve().parents[1]
    files += [root / name for name in ('app/network/wifi_bss.c', 'tools/verify_wifi_bss.py',
        'tools/reverse/bss_assoc.py', 'tests/bss_assoc_instructions.py', 'tests/bss_assoc_test.py',
        'tools/reverse/rv32_link_match.py', 'tools/reverse/nothrow_linkage.py',
        'tools/reverse/wifi_producers.py', 'tools/reverse/elf_archive.py',
        'tools/audit_factory_xrefs.py', 'tests/runtime_call_instructions.py',
        'tools/reverse/runtime_call_gaps.py')]
    if args.output.exists() or args.output.resolve() in [p.resolve() for p in files]:
        raise ValueError('Preserve inputs and existing BSS evidence')
    pins = {str(p.resolve()): sha(p.read_bytes()) for p in files}
    result = run(args.factory.read_bytes(), args.before.read_bytes(), args.before_app.read_bytes(),
        args.elf.read_bytes(), args.app.read_bytes(), args.old_net, args.sdk_libraries, args.object.read_bytes())
    if any(sha(Path(p).read_bytes()) != digest for p, digest in pins.items()):
        raise ValueError('BSS inputs changed during execution')
    result.update(inputs_sha256=pins, inputs_unchanged=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(passed=True, executions=result['executions'], coverage=result['setter_coverage'],
                          rejected_controls=result['rejected_controls'])))


if __name__ == '__main__':
    main()
