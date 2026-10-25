"""Annotate phase-aware heap warnings using verified same-stop TCP metadata.

This reads saved files only. It never connects to QMP/RSP or changes a guest.
Running prefixes and eight-hour controls are not promoted to H10 acceptance.
"""
import argparse
import json
import math
from pathlib import Path

from runtime_evidence import audit_run, finite, require, sha
from runtime_tcp_trend import attribute_trend


def analysis_sources():
    """Bind offline calculations and every replay decoder to their exact source bytes."""
    src = Path(__file__).resolve().parents[1]
    tools = ('analyze_tcp_runtime.py', 'runtime_tcp_trend.py', 'runtime_trend.py',
             'runtime_evidence.py', 'runtime_run_guard.py')
    tests = ('runtime_tcp_journal.py', 'runtime_tcp_snapshot.py', 'runtime_tcp_allocations.py',
             'runtime_tcp_layout.py', 'runtime_tcp_gate.py', 'runtime_heap_topology.py',
             'runtime_tlsf_instructions.py', 'runtime_instruction_image.py', 'runtime_memory.py', 'runtime_heap_rom.py')
    files = [src / 'tools' / name for name in tools] + [src / 'tests' / name for name in tests]
    return {str(path): sha(path) for path in files}


def analyze(folder, repository_root, start_record=None, diagnostic=False, extra_roots=()):
    """Keep original trend verdicts and annotate their exact paired observations."""
    sources = analysis_sources()
    audit = audit_run(folder, repository_root, start_record, diagnostic, extra_roots)
    report, evidence = audit['report'], audit['evidence']
    require(report['schema_version'] == 7 and audit.get('tcp_topology_verified') is True,
            'A fully replayed schema7 TCP journal is required')
    require(audit['tcp_coverage']['snapshots'] == len(evidence['series']) == evidence['verified_snapshots'],
            'TCP replay does not cover every saved snapshot')
    start = finite(report['workload_start_guest_seconds'], 'workload start')
    end = (report['workload_end_guest_seconds'] if audit['terminal'] else evidence['series'][-1]['guest_seconds'])
    # Exactly the same defaults and LCM as analyze_runtime.py; this CLI provides
    # no override that could remove a flagged phase or shorten its warmup.
    attribution = attribute_trend(evidence['series'], audit['tcp_series'], start, end,
                                  phase_period=math.lcm(20, report['outage_every_cycles'] or 1))
    require(sources == analysis_sources(), 'Analysis or replay source changed while reading the evidence')
    return {'schema_version': 1, 'status': 'diagnostic_complete' if audit['terminal'] else 'pending_prefix',
            'evidence_verified': True, 'all_functionality_verified': False,
            'h10_checks_evaluated': False, 'h10_checks_passed': False,
            'run_directory': str(Path(folder).resolve()),
            'app_sha256': report['app_sha256'], 'native_elf_sha256': report['native_elf_sha256'],
            'qemu_sha256': report['qemu_sha256'],
            'inputs_verified': audit['inputs_verified'], 'analysis_inputs_sha256': sources,
            'analysis_inputs_unchanged': True,
            'journal_observed_sha256': evidence['sha256'], 'journal_prefix_only': not audit['terminal'],
            'trailing_partial_bytes': evidence['trailing_partial_bytes'], 'pending_events': evidence['pending_events'],
            'complete_cycles_audited': evidence['cycles'], 'elapsed_guest_seconds_observed': end - start,
            'terminal_workload_verified': audit['terminal'], 'terminal_guard_verified': audit['terminal_guard_verified'],
            'start_record_verified': audit['start_record_verified'], 'uart': audit['uart'],
            'tcp_coverage': audit['tcp_coverage'], 'attribution': attribution,
            'limitations': ['No VM is queried or paused; observations are replayed from saved numeric metadata.',
                'A running prefix can change after this read and is not a completed workload.',
                'Original retained-loss flags remain findings requiring investigation; ownership is not a waiver.',
                'This diagnostic does not evaluate all H10, firmware, calendar/DST or physical-board requirements.']}


def validate_output(output, folder):
    """Protect both authoritative workload data and its sibling supervisor directory."""
    output, folder = Path(output).resolve(), Path(folder).resolve()
    require(not output.is_relative_to(folder) and not output.is_relative_to(Path(str(folder) + '-supervisor')),
            'Analysis output must be outside workload and supervisor directories')
    require(not output.exists(), 'Analysis output already exists')
    return output


def main():
    """Create one new analysis artifact, including explicit rejection on invalid evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--repository-root', type=Path, required=True)
    parser.add_argument('--start-record', type=Path)
    parser.add_argument('--allow-root', type=Path, action='append', default=[])
    parser.add_argument('--diagnostic', action='store_true', help='Permit a pending prefix; never grants H10 acceptance')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = validate_output(args.output, args.run)
    try:
        result = analyze(args.run, args.repository_root, args.start_record, args.diagnostic, args.allow_root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = {'schema_version': 1, 'status': 'evidence_rejected', 'evidence_verified': False,
                  'h10_checks_passed': False, 'all_functionality_verified': False, 'error': str(error)}
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also protects a file that appeared after validation.
    with output.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    print(json.dumps({key: result.get(key) for key in ('status', 'evidence_verified', 'h10_checks_passed')}))
    return 0 if result.get('evidence_verified') else 1


if __name__ == '__main__':
    raise SystemExit(main())
