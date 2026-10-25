"""Compare both qualified event-11 bodies with independent algorithm models."""
from collections import Counter
from dataclasses import asdict, replace
import hashlib
import io
from itertools import product
import json

from elftools.elf.elffile import ELFFile

from reverse.rv32_link_match import size_at
from timer_event11_instructions import Event11Probe
from timer_event11_model import State, expected, configured


def reader(data):
    """Expose only initialized ELF sections to the disposable instruction probe."""
    elf = ELFFile(io.BytesIO(data))
    sections = [(s['sh_addr'], s.data()) for s in elf.iter_sections()
                if s['sh_flags'] & 2 and s['sh_type'] != 'SHT_NOBITS' and s['sh_size']]
    def read(address, size):
        found = [raw[address - base:address - base + size] for base, raw in sections
                 if base <= address < address + size <= base + len(raw)]
        if len(found) != 1:
            raise ValueError('Unknown/ambiguous initialized ELF address')
        return found[0]
    return read


def states():
    """Cover boolean branches, disabled/fallback timers and 32-bit wrap edges."""
    for flags, word, enabled, period, fallback, adjustment in product(
            product((0, 1), repeat=5), (0, 0x12345678), (0, 1), (0, 1, 10, 65535),
            (0, 1, 60000000), (0, 1024000, 0xffffffff)):
        yield State(*flags, word, enabled, period, fallback, adjustment)
    # Noncanonical nonzero bytes and values around the multiplication wrap.
    for field in ('byte1', 'byte14', 'byte15', 'byte16', 'byte488', 'enabled52'):
        for value in (2, 255):
            yield replace(State(word36=1), **{field: value})
    for period, adjustment in product((4193, 4194, 4195), (0, 1, 1024000, 0xffffffff)):
        yield State(period72=period, adjustment56=adjustment)


def run(qualification, factory, native):
    """Execute identical inputs on each image, preserving every unexplained delta."""
    reads = {'factory': reader(factory), 'native': reader(native)}
    probes = {v: Event11Probe(qualification['layouts'][v], read) for v, read in reads.items()}
    digest, counts, totals = hashlib.sha256(), Counter(), Counter()
    samples = {}
    for index, state in enumerate(states()):
        observed = {}
        for variant, probe in probes.items():
            result = probe.call(state)
            assert result == expected(variant, state), (variant, asdict(state), result, expected(variant, state))
            observed[variant] = result
            totals[variant] += probe.instructions
        record = dict(index=index, input=asdict(state), observed=observed)
        digest.update((json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n').encode())
        if observed['factory'] != observed['native']:
            counts['different_traces'] += 1
        else:
            counts['equal_traces'] += 1
        categories = {
            'rearm-while-context-nonzero': state.enabled52 and state.word36,
            'fallback-when-disabled': not state.enabled52 and state.fallback28,
            'pending-action-suppressed': state.byte14 and state.byte15 and not state.byte16 and state.byte488,
            'byte15-zero-new-state-writes': not state.byte15,
            'different-rearm-formula': state.enabled52 and not state.word36,
        }
        for name, condition in categories.items():
            if condition:
                counts[name] += 1
                samples.setdefault(name, record)
        counts['states'] += 1
    setter_cases, normalized_samples = 0, []
    periods = (*range(17), 127, 128, 255, 256, 1023, 4096, 4193, 4194, 4195,
               32767, 32768, 32771, 32772, 65534, 65535)
    for period, word36, fallback28 in product(periods, (0, 1), (0, 60000000)):
        initial = State(word36=word36, fallback28=fallback28, enabled52=255,
                        period72=12345, adjustment56=0xffffffff)
        observations = {}
        for variant, probe in probes.items():
            after, setter_model = configured(variant, initial, period)
            setter = probe.call(initial, period)
            assert setter == setter_model, (variant, period, setter, setter_model)
            totals[variant] += probe.instructions
            # All configuration writes were compared above. Recreate that exact
            # state for an event call, without inventing helper side effects.
            event = probe.call(after)
            assert event == expected(variant, after), (variant, period, event)
            totals[variant] += probe.instructions
            observations[variant] = dict(state=asdict(after), setter=setter, event=event)
        record = dict(period=period, word36=word36, fallback28=fallback28, observed=observations)
        digest.update((json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n').encode())
        if not word36 and not fallback28 and period in (0, 1, 3, 4, 5, 8, 10, 65535):
            normalized_samples.append(record)
        setter_cases += 1
    coverage = {}
    for variant, probe in probes.items():
        coverage[variant] = []
        for function in (*qualification['layouts'][variant]['functions'],
                         qualification['layouts'][variant]['configuration_function']):
            start, end = int(function['start'], 0), int(function['end'], 0)
            raw = reads[variant](start, end - start)
            addresses, offset = set(), 0
            while offset < len(raw):
                addresses.add(start + offset)
                offset += size_at(raw, offset)
            missing = addresses - probe.visited
            assert not missing, (variant, function['name'], sorted(map(hex, missing)))
            coverage[variant].append(dict(name=function['name'], instruction_starts=len(addresses),
                                           visited=len(addresses & probe.visited), missing=[]))
    return dict(passed=True, cases_per_image=counts['states'], configuration_cases_per_image=setter_cases,
                total_executions=counts['states'] * 2 + setter_cases * 4,
                trace_sha256=digest.hexdigest(), counts=dict(counts), body_instructions=dict(totals),
                coverage=coverage, representative_differences=samples,
                configured_period_samples=normalized_samples,
                external_helpers_stubbed=True, runtime_state_reachability_proved=False,
                timer_elapsed_time_proved=False, rf_semantics_proved=False,
                semantic_equivalence_proved=False, whole_image_completeness_proved=False,
                physical_hardware_tested=False)
