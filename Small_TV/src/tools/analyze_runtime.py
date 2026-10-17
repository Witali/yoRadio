"""Audit a native runtime journal and compare free heap in equal workload phases.

This reads files only and never connects to or pauses the guest. A diagnostic
prefix of an active workload is explicitly pending, never a completed H10 pass.
"""
import argparse
import json
import math
from pathlib import Path
import sys

from runtime_evidence import audit_run, finite, require
from runtime_trend import analyze_trend


def analyze(folder, repository_root, start_record=None, diagnostic=False, extra_roots=()):
    """Keep journal validity, completed scope, and memory trend conclusions separate."""
    audit = audit_run(folder, repository_root, start_record, diagnostic, extra_roots)
    report, evidence = audit['report'], audit['evidence']
    start = finite(report['workload_start_guest_seconds'], 'workload start')
    end = (report['workload_end_guest_seconds'] if audit['terminal'] else
           evidence['series'][-1]['guest_seconds'])
    # Include outage cadence: the recovery cycle and the following cycles must
    # be compared with the same position in the network workload as well.
    phase_period = math.lcm(20, report['outage_every_cycles'] or 1)
    trend = analyze_trend(evidence['series'], start, end, phase_period=phase_period)
    summary = evidence['summary']
    weather = evidence['weather']
    weather_current = (audit['weather_evidence_verified'] and weather['distinct_valid_generations'] >= 2 and
                       weather['first_fresh_guest_seconds'] <= start + 3600 and
                       weather['last_fresh_guest_seconds'] >= end - 3600 and
                       weather['maximum_fresh_gap_guest_seconds'] <= 3600)
    checks = {
        'workload_complete': audit['terminal'],
        'duration_request_at_least_24h': (report['duration_requested_guest_seconds'] or 0) >= 86400,
        'observed_at_least_24h': end - start >= 86400,
        'start_record_matches': audit['start_record_verified'],
        'independent_terminal_guard_matches': audit['terminal_guard_verified'],
        'periodic_guest_disconnect_reconnect': summary['outages'] >= 2,
        'all_steady_windows_cover_all_workload_phases': trend['status'] != 'insufficient_steady_state_data',
        'no_retained_loss_flagged': not trend['flags'],
        'weather_refreshed_throughout_workload': weather_current,
    }
    passed = all(checks.values())
    return {'schema_version': 1, 'status': ('h10_checks_passed' if passed else
             'pending' if not audit['terminal'] else 'completed_scope_requires_review'),
            'h10_checks_passed': passed, 'all_functionality_verified': False,
            'scope': __doc__, 'run_directory': str(Path(folder).resolve()),
            'app_sha256': report['app_sha256'], 'native_elf_sha256': report['native_elf_sha256'],
            'qemu_sha256': report['qemu_sha256'], 'inputs_verified': audit['inputs_verified'],
            'journal_observed_sha256': evidence['sha256'],
            'journal_prefix_only': not audit['terminal'],
            'trailing_partial_bytes': evidence['trailing_partial_bytes'],
            'pending_events': evidence['pending_events'], 'complete_cycles_audited': evidence['cycles'],
            'elapsed_guest_seconds_observed': end - start,
            'checks': checks, 'uart': audit['uart'], 'summary': summary, 'trend': trend,
            'weather': weather, 'weather_freshness_bound_guest_seconds': 3600,
            'limitations': ['This audits native QEMU runtime only; it does not establish physical-board acceptance.',
                'The workload uses a fixed NTP epoch; this is not a continuous calendar/DST test.',
                'Task stack fill and sampled free heap cannot prove every interrupt or transient allocation peak.',
                'Retained memory loss is a finding to investigate, not automatically an allowed SDK cache.']}


def main():
    """Write a separate analysis artifact and fail closed on incomplete acceptance."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--repository-root', type=Path, required=True)
    parser.add_argument('--start-record', type=Path)
    parser.add_argument('--allow-root', type=Path, action='append', default=[])
    parser.add_argument('--diagnostic', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Keep both the workload's inputs and its own authoritative outputs intact.
    require(not args.output.resolve().is_relative_to(args.run.resolve()),
            'Analysis output must be outside the observed run directory')
    require(not args.output.exists(), 'Analysis output already exists')
    try:
        result = analyze(args.run, args.repository_root, args.start_record, args.diagnostic, args.allow_root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        result = {'schema_version': 1, 'status': 'evidence_rejected', 'h10_checks_passed': False,
                  'all_functionality_verified': False, 'error': str(error)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({key: result[key] for key in ('status', 'h10_checks_passed')}, ensure_ascii=False))
    return 0 if result['h10_checks_passed'] or (args.diagnostic and result['status'] != 'evidence_rejected') else 1


if __name__ == '__main__':
    sys.exit(main())
