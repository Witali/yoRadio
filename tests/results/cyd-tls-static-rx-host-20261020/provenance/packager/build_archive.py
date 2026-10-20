"""PREPARED packager for canonical host/config/service evidence; default PLAN ONLY.

No SDK/compiler/WSL/Git/network/device commands. Root review and explicit archive
write authorization are separate from evidence integrity. Source-only target
recipes in preparation snapshots are never promoted to executed target results.
"""
import argparse
from pathlib import Path
import re
import subprocess
import sys

from archive_core import Collector, encode, hashfile, load, require, sha
import evidence_rules as rules

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEST = ROOT / 'tests/results/cyd-tls-static-rx-host-20261020'
PREP = ROOT / '.build/cyd-tls-reserve-registry-target-prep-01'
COHORTS = {'unit': (ROOT / '.build/rxu01', rules.UNIT_SHA),
           'config': (ROOT / '.build/rxc01', rules.CONFIG_SHA),
           'service': (ROOT / '.build/rxs01', rules.SERVICE_SHA)}
ROOT_AUDIT = ROOT / '.build/cyd-static-rx-host-root-audit-01.json'
ROOT_AUDIT_SHA = '5b92b83114dcdca222ca32b023e951d2239f6a8bee839889cd7acffd93e41492'
TOOLS = ('archive_core.py', 'build_archive.py', 'evidence_rules.py', 'verify.py', 'check-prep.py', 'SPEC.md', 'README.template.md', 'HOST.template.md')


def local_relative(base, relative):
    path = (base / relative).resolve()
    require(path.is_relative_to(base.resolve()), 'Evidence relative path escapes cohort')
    return path


def terminal_pins(args):
    require(args.unit_report_sha256 == rules.UNIT_SHA and args.config_report_sha256 == rules.CONFIG_SHA and args.service_report_sha256 == rules.SERVICE_SHA,
            'All three exact root-authoritative terminal report pins are mandatory')
    require(not DEST.exists(), 'Fresh additive archive destination required')
    for name, (base, expected) in COHORTS.items():
        require(hashfile(base / 'report.json') == expected, 'Final report changed: ' + name)
    require(hashfile(PREP / 'manifest.json') == rules.PREP_SHA and hashfile(ROOT_AUDIT) == ROOT_AUDIT_SHA, 'Exact source-only prep and authoritative root readback')


def bind_report(c, container, report, base, mapping):
    for original, row in report['inputs'].items():
        target = c.entries[mapping[row['snapshot']]]
        require(target['sha256'] == row['sha256'], 'Input snapshot/report identity')
        c.bind(container, ['inputs', original, 'sha256'], target)
        c.add(original, 'Current byte-identical original input readback; no source Git-clean assertion', row['sha256'])
    for index, command in enumerate(report.get('commands', [])):
        target = c.entries[mapping[command['label'] + '.log']]
        require(target['sha256'] == command['log_sha256'], 'Raw command log identity')
        c.bind(container, ['commands', index, 'log_sha256'], target)
    for relative, digest in report.get('generated', {}).items():
        target = c.entries[mapping[relative]]
        require(target['sha256'] == digest, 'Generated artifact identity')
        c.bind(container, ['generated', relative], target)
    for key in ('tools_before', 'tools_after'):
        for original, digest in report.get(key, {}).items():
            c.bind(container, [key, original], c.reported_tool(original, digest))
    for key in ('tools', 'native_python'):
        for original, digest in report.get(key, {}).items():
            c.bind(container, [key, original], c.add(original, 'Original native tool identity; executable bytes omitted', digest))
    if 'cases' in report:
        for name, row in report['cases'].items():
            c.bind(container, ['cases', name, 'log_sha256'], c.entries[mapping[name + '/configure.log']])
            if 'overlay_sha256' in row:
                c.bind(container, ['cases', name, 'overlay_sha256'], c.entries[mapping[name + '/build/native-tls-static-rx/ssl_tls.c']])


def collect(args):
    terminal_pins(args)
    c, index = Collector(), {'cohorts': {}, 'canonical_files': {}, 'source_only_preparation': {}}
    summaries = {}
    for name, (base, expected) in COHORTS.items():
        report = load(base / 'report.json')
        read = lambda relative: local_relative(base, relative).read_bytes()
        if name == 'service':
            summaries[name] = rules.service(report, read, lambda relative: hashfile(local_relative(base, relative)))
        else:
            summaries[name] = getattr(rules, name)(report, read)
        mapping = {}
        for path in sorted(base.rglob('*')):
            if path.is_file():
                relative = path.relative_to(base).as_posix()
                entry = c.add(path, 'Raw completed canonical ' + name + ' cohort source/config/log/artifact',
                              expected if relative == 'report.json' else None,
                              preferred='reports/' + name + '.json' if relative == 'report.json' else None)
                mapping[relative] = entry['id']
        primary = c.entries[mapping['report.json']]
        bind_report(c, primary, report, base, mapping)
        index['cohorts'][name] = {'original_directory': str(base), 'report_id': primary['id'], 'report_sha256': expected,
                                 'files': mapping, 'root_reported_outer_session': {'unit': 86428, 'config': 21895, 'service': 79183}[name],
                                 'root_reported_outer_terminal_exit': 0,
                                 'terminal_attribution': 'Root authoritative message; report and original child command logs retained. No invented wrapper terminal log.'}
    manifest = load(PREP / 'manifest.json')
    require(manifest['proposed_file_count'] == 34 and manifest['file_count'] == len(manifest['files']) == 554, 'Exact source-only preparation cohort')
    manifest_entry = c.add(PREP / 'manifest.json', 'Source-only preparation manifest, not target execution', rules.PREP_SHA, preferred='provenance/preparation-manifest.json')
    prep_map = {}
    for relative, row in manifest['files'].items():
        entry = c.add(local_relative(PREP, relative), 'Immutable source-only preparation payload; any recipes are unrun provenance', row['sha256'])
        require(entry['bytes'] == row['bytes'], 'Source-only prep size')
        c.bind(manifest_entry, ['files', relative, 'sha256'], entry)
        prep_map[relative] = entry['id']
        if relative.startswith('repository/'):
            canonical = relative.removeprefix('repository/')
            current = c.add(ROOT / canonical, 'Canonical applied file byte-equal source-only final preparation; not Git execution provenance', row['sha256'])
            index['canonical_files'][canonical] = {'raw_sha256': row['sha256'], 'bytes': row['bytes'], 'current_id': current['id'], 'preparation_id': entry['id']}
    require(len(index['canonical_files']) == 34, 'All canonical34 files')
    index['source_only_preparation'] = {'manifest_id': manifest_entry['id'], 'manifest_sha256': rules.PREP_SHA, 'files': prep_map,
                                        'executed_target_qualification': False, 'canonical_file_count': 34}
    root_audit = c.add(ROOT_AUDIT, 'Separate root filesystem-only completed host cohort readback', ROOT_AUDIT_SHA, preferred='reports/root-readback.json')
    root_script = c.add(ROOT / '.build/audit-cyd-static-rx-host-01.py', 'Root filesystem-only readback recipe; not new test execution',
                        'ec3a6002395970e6526acd1254c34f1fcdeedc439a863d5aa122fc13b716f1f5')
    require(load(ROOT_AUDIT)['passed'] is True, 'Root independent raw readback')
    for name in TOOLS:
        c.add(HERE / name, 'Self-contained archive tooling/template provenance', preferred='provenance/packager/' + name)
    for directory in sorted(HERE.glob('prep-check-*')):
        c.tree(directory, 'Pure packaging synthetic guard checks and original tool snapshots; no gate rerun')
    c.stable()
    index.update(format_version=1, module_normalized_lf_sha256=rules.MODULE, guard_manifest_sha256=rules.GUARDS,
                 root_readback_id=root_audit['id'], root_readback_script_id=root_script['id'], summaries=summaries,
                 status={'canonical_host_unit_passed': True, 'canonical_source_only_configure_passed': True,
                         'canonical_host_service_passed': True, 'production_files_applied': True,
                         'source_git_clean_or_committed_at_test_execution_claimed': False,
                         'actual_sdk_compile_qualified': False, 'qemu_qualified': False, 'actual_isr_smp_qualified': False,
                         'real_heap_oom_qualified': False, 'protocol_conformance_qualified': False,
                         'physical_or_runtime_savings_claimed': False, 'static_record_size_changed': False,
                         'deferred_codec_scope_included': False},
                 closure_scope='All files from three completed host cohorts and exact554-entry source-only prep. Binary artifacts/tools are identity-only omissions. No ignored historical runtime import is needed by canonical runners or offline verifier.')
    c.files.update({'index.json': encode(index), 'path-map.json': encode({'entries': c.entries}), 'bindings.json': encode({'bindings': c.bindings}),
                    'current-verification.json': encode({'selected_inputs_unchanged_after': True, 'selected_inputs': c.observed}),
                    '.gitattributes': b'* -text\n** -text\n', 'verify.py': (HERE / 'verify.py').read_bytes(),
                    'evidence_rules.py': (HERE / 'evidence_rules.py').read_bytes()})
    for source, dest in [('README.template.md', 'README.md'), ('HOST.template.md', 'HOST.md')]:
        raw = (HERE / source).read_bytes()
        for key, value in [('UNIT', rules.UNIT_SHA), ('CONFIG', rules.CONFIG_SHA), ('SERVICE', rules.SERVICE_SHA), ('PREP', rules.PREP_SHA)]:
            raw = raw.replace(('@@' + key + '_SHA@@').encode(), value.encode())
        require(b'@@' not in raw, 'No unresolved template')
        c.files[dest] = raw
    return c


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--unit-report-sha256', required=True)
    p.add_argument('--config-report-sha256', required=True)
    p.add_argument('--service-report-sha256', required=True)
    p.add_argument('--attempt', default='attempt-01')
    p.add_argument('--write-reviewed-archive', action='store_true')
    args = p.parse_args()
    require(re.fullmatch('attempt-[0-9]{2}', args.attempt), 'Exact fresh attempt name')
    for value in (args.unit_report_sha256, args.config_report_sha256, args.service_report_sha256):
        require(re.fullmatch('[0-9a-f]{64}', value), 'Explicit terminal SHA256')
    attempt = HERE / args.attempt
    require(not attempt.exists(), 'Prior packaging attempts are immutable')
    attempt.mkdir()
    result = {'passed': False, 'archive_written': False, 'sdk_compiler_wsl_git_network_device_invoked': False,
              'mode': 'write_reviewed_archive' if args.write_reviewed_archive else 'plan_only'}
    try:
        c = collect(args)
        manifest = encode({'files': [{'path': name, 'bytes': len(raw), 'sha256': sha(raw)} for name, raw in sorted(c.files.items())]})
        result.update(manifest_sha256=sha(manifest), readme_sha256=sha(c.files['README.md']),
                      payload_file_count=len(c.files) + 1, payload_total_bytes=sum(len(v) for v in c.files.values()) + len(manifest),
                      mapped_versions=len(c.entries), stored_versions=sum(r['disposition'] == 'stored' for r in c.entries),
                      explicit_omissions=sum(r['disposition'] == 'omitted' for r in c.entries),
                      selected_inputs=len(c.observed), json_hash_bindings=len(c.bindings))
        (attempt / 'planned-files.json').write_bytes(manifest)
        (attempt / 'planned-index.json').write_bytes(c.files['index.json'])
        (attempt / 'planned-path-map.json').write_bytes(c.files['path-map.json'])
        if args.write_reviewed_archive:
            require(not DEST.exists() and DEST.resolve() == DEST, 'New exact destination only')
            DEST.mkdir(parents=True)
            for name, raw in sorted(c.files.items()):
                path = local_relative(DEST, name)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            (DEST / 'manifest.json').write_bytes(manifest)
            execution = subprocess.run([sys.executable, '-B', str(DEST / 'verify.py')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
            (attempt / 'offline-verifier.log').write_bytes(execution.stdout)
            require(execution.returncode == 0, 'Offline verifier rejected archive; preserve failure')
            c.stable()
            result.update(archive_written=True, archive=str(DEST))
        result['passed'] = True
    except BaseException as error:
        result['error'] = type(error).__name__ + ': ' + str(error)
        if isinstance(error, subprocess.TimeoutExpired):
            (attempt / 'timeout.log').write_bytes(error.output or b'')
        (attempt / 'report.json').write_bytes(encode(result))
        raise
    (attempt / 'report.json').write_bytes(encode(result))
    print(encode(result).decode())


if __name__ == '__main__':
    main()
