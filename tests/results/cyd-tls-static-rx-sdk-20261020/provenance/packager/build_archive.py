"""Default PLAN ONLY after terminal closure; separate reviewed fresh archive write.

Filesystem and stdlib only. Never import campaign/qualifier/test recipes, invoke
SDK/Git/tools, inspect a partial campaign, collect whole trees or overwrite output.
"""
import argparse
from pathlib import Path
import sys

from archive_core import Collector, encode, hashfile, ident, identity_references, load, require, sha, write_new
import evidence_rules as rules

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ORIGINAL = ROOT / '.build/cyd-tls-static-rx-production-prep-01'
REPAIR = ROOT / '.build/cyd-clang-config-repair-prep-01'
SDK = Path('C:/Work/yoRadio/.idf/v6.0.2')
DEST = ROOT / 'tests/results/cyd-tls-static-rx-sdk-20261020'
PLAN = HERE / 'plan02.json'
TOOLS = ('archive_core.py', 'build_archive.py', 'evidence_rules.py', 'verify.py',
         'check-prep.py', 'SPEC.md', 'README.template.md')
SCHEMA = 'cyd-static-rx-sdk-archive-plan-v1'
WARNING_REVIEW = ROOT / '.build/cyd-static-rx-warning-review-01'
WARNING_PINS = {'comparison.json': '92d5b58198522f537055b0925d6e701b0d4207ad33fd536c4f85830ec0b4a2e1',
                'REVIEW.md': '38cda2056bb4fb5112301c7a8a78e89c221fc903298f19d6e96e0d8db06cb2af'}


def root_receipt(summary_sha, receipt_path, receipt_sha):
    # This is the FIRST operation that reads campaign output in a real plan.
    # No output is created until the independent root receipt and full summary
    # satisfy the exact terminal/matrix rules.
    require(isinstance(summary_sha, str) and isinstance(receipt_sha, str), 'Explicit root SHA pins required')
    note = Path(receipt_path).resolve()
    require(note.is_relative_to(ROOT / '.build') and not note.is_relative_to(ORIGINAL)
            and not note.is_relative_to(REPAIR) and not note.is_relative_to(HERE),
            'Separate root-authored closure receipt required')
    require(hashfile(note) == receipt_sha, 'Root terminal receipt raw SHA mismatch')
    closed_path = REPAIR / 'summary.json'
    require(hashfile(closed_path) == summary_sha, 'Root successor summary raw SHA mismatch')
    closed, receipt = load(closed_path), load(note)
    rules.terminal(closed, receipt, summary_sha, str(closed_path), str(REPAIR / 'repair.py'))
    return closed_path, note, closed


class Selection:
    def __init__(self):
        self.collector = Collector(ROOT)
        self.pending, self.parsed = [], set()
        self.linked_manifests = {}
        self.historical_seeds = {}

    def add(self, path, role, expected=None, preferred=None, follow=True, manifest=False):
        path = Path(path).resolve()
        prior = ROOT / 'tests/results'
        external = None
        if path.is_relative_to(prior) and not path.is_relative_to(DEST) and not manifest:
            relative = path.relative_to(prior)
            require(len(relative.parts) >= 2, 'Existing evidence reference must name a bundle member')
            bundle = prior / relative.parts[0]
            manifest_path = bundle / 'manifest.json'
            if str(bundle) not in self.linked_manifests:
                linked = self.add(manifest_path, 'existing committed evidence manifest; bundle payload not copied',
                                  preferred='links/' + relative.parts[0] + '-manifest.json', follow=False, manifest=True)
                self.linked_manifests[str(bundle)] = linked['id']
            external = path.relative_to(ROOT).as_posix()
        row = self.collector.add(path, role, expected, preferred, external)
        if external is not None:
            row['linked_manifest_id'] = self.linked_manifests[str(bundle)]
        elif follow and row['disposition'] == 'stored' and path.suffix.lower() == '.json':
            self.pending.append(row)
        return row

    def document(self, path, role, expected=None, preferred=None):
        row = self.add(path, role, expected, preferred)
        require(row['disposition'] == 'stored', 'Required qualification JSON must be retained')
        return row, load(path)

    def drain(self):
        while self.pending:
            container = self.pending.pop(0)
            if container['id'] in self.parsed:
                continue
            self.parsed.add(container['id'])
            document = load(container['original_path'])
            for tokens, identity in identity_references(document):
                if tokens == ('seed_before_build',):
                    # Recorded BEFORE SDK normalization. The working config
                    # legitimately changed; recover its exact earlier bytes
                    # through the immutable original seed, not its later path.
                    require(document['kind'] in ('export', 'clang') and document['row'] in self.historical_seeds,
                            'Known execution initial seed phase required')
                    row = self.historical_seeds[document['row']]
                    config_path = row['config'] if document['kind'] == 'export' else row['clang_config']
                    require(rules.normalize(identity['path']) == rules.normalize(config_path)
                            and identity['bytes'] == row['seed']['bytes']
                            and identity['sha256'] == row['seed']['sha256'], 'Exact historical seed relationship required')
                    target = self.add(row['seed']['path'], 'immutable original full sdkconfig seed', row['seed'])
                    self.collector.bind(container, tokens, target, 'historical_seed')
                    continue
                target = self.add(identity['path'], 'exact JSON identity referenced by retained evidence', identity)
                self.collector.bind(container, tokens, target)


def selected_artifacts(selection, report_path, report, kind):
    folder = report_path.parent
    if kind == 'clang':
        names = ['actual-module-sdk-commands.json', 'tls-sdk-frontend.d', 'tls-sdk-frontend.log']
    else:
        names = ['actual-module-sdk-commands.json', 'header-closure.json', 'nm.log',
                 'mbedtls_ssl_setup.log', 'mbedtls_ssl_free.log', 'mbedtls_ssl_config_init.log',
                 'mbedtls_ssl_config_free.log', 'app-main.log', 'early-mpi.log', 'commands.log']
        names += ['dependencies-' + str(index) + '.log' for index in range(len(report['actual_header_closure']))]
        if 'static_rx' in report:
            names += ['sdk-rx-size-probe.c', 'sdk-rx-size-probe.log', 'sdk-rx-size-probe-nm.log']
    return {name: selection.add(folder / name,
            'selected original qualification text; observed at archive stage, not a newly rerun tool')['id']
            for name in names}


def packager_sources(selection, source_root=HERE):
    packager = {}
    for name in TOOLS:
        preferred = name if name in ('verify.py', 'evidence_rules.py') else 'provenance/packager/' + name
        packager[name] = selection.add(Path(source_root) / name,
            'reviewed bounded archive tool/source', preferred=preferred)['id']
    return packager


def canonical_packager_paths(selection, packager):
    for name in TOOLS:
        expected = name if name in ('verify.py', 'evidence_rules.py') else 'provenance/packager/' + name
        row = selection.collector.entries[packager[name]]
        require(row['disposition'] == 'stored' and row['stored_path'] == expected,
                'Canonical standalone packager retention path missing: ' + name)


def prepare_selection(closed_path, receipt_path, closed):
    selection = Selection()
    c = selection.collector
    # Register canonical paths BEFORE any proof/report reference can register
    # identical source bytes under raw/. Collector dedup keeps the first path.
    packager = packager_sources(selection)
    summary_entry, _ = selection.document(closed_path, 'authoritative successor closure', preferred='reports/summary.json')
    receipt_entry, _ = selection.document(receipt_path, 'separate root authoritative terminal0 receipt', preferred='reports/root-terminal.json')
    old_marker_entry, old_marker = selection.document(ORIGINAL / 'plan02/marker.json', 'original immutable campaign marker',
                                                     preferred='reports/original-marker.json')
    repair_marker_entry, repair_marker = selection.document(REPAIR / 'marker.json', 'immutable successor qualification marker',
                                                           preferred='reports/repair-marker.json')
    require(old_marker_entry['sha256'] == rules.ORIGINAL_MARKER
            and repair_marker_entry['sha256'] == rules.REPAIR_MARKER, 'Exact frozen marker pair required')
    require(old_marker['source_snapshot'] == closed['source_snapshot'] == repair_marker['source_snapshot'],
            'Marker/summary frozen source identity mismatch')
    plan_entry, plan = selection.document(ORIGINAL / 'plan02/plan.json', 'original baseline/seed/invocation metadata',
                                          preferred='reports/original-plan.json')
    selection.historical_seeds = {row['name']: row for row in plan['rows']}
    require(hashfile(ORIGINAL / 'campaign.py') == rules.ORIGINAL_SCRIPT, 'Original helper source changed')
    failed_entry, failed = selection.document(ORIGINAL / 'plan02/qualifications/clang-pdm/report.json',
        'historical rejected original PDM qualifier; remains nonpass', preferred='history/clang-pdm-nonpass.json')
    rules.historical_failure(failed, failed_entry['sha256'])
    controls_entry, controls = selection.document(REPAIR / 'policy-check01/report.json',
        '81 pure policy controls and fixture identities; not runtime qualification', preferred='reports/policy-controls.json')
    rules.control_report(controls)
    prep_entry, prep_proof = selection.document(HERE / 'prep-check03/report.json',
        'synthetic archive-tool prep controls only, not actual archive qualification')
    require(prep_proof['passed'] is True and prep_proof['sources_unchanged'] is True
            and prep_proof['actual_plan_collect_write_sdk_compiler_git_device_invocations'] == 0,
            'Reviewed pure archive preparation controls required')
    warning_review = {}
    for name in ['comparison.json', 'REVIEW.md', 'pending-history.json', 'review.ps1']:
        path = WARNING_REVIEW / name
        observed = ident(path)
        if name in WARNING_PINS:
            require(observed['sha256'] == WARNING_PINS[name], 'Root-accepted warning review changed')
        warning_review[name] = selection.add(path,
            'separate accepted warning comparison/review; no lint rerun', observed, follow=False)['id']
    # Hash actual supporting source text named by the original marker. Do not
    # infer a capacity/ABI from the archive tool's own guessed constants.
    for relative, digest in old_marker['guards'].items():
        path = SDK / relative
        observed = ident(path)
        require(observed['sha256'] == digest, 'Pinned SDK supporting source changed')
        target = selection.add(path, 'actual marker-guarded SDK supporting source', observed)
        c.bind(old_marker_entry, ['guards', relative], target, 'sha256')
    for baseline in plan['baselines'].values():
        for value in baseline['files'].values():
            if 'snapshot' in value:
                observed = ident(value['snapshot'])
                require(observed['bytes'] == value['bytes'] and observed['sha256'] == value['sha256'],
                        'Exact baseline metadata snapshot changed')
                selection.add(value['snapshot'], 'frozen original baseline metadata copy', observed)
    # Link the two already committed canonical archives by manifest only.
    for name in ['cyd-tls-static-rx-host-20261020', 'cyd-tls-static-rx-qemu-20261020']:
        path = ROOT / 'tests/results' / name / 'manifest.json'
        linked = selection.add(path, 'existing committed canonical host/QEMU manifest only',
                               preferred='links/' + name + '-manifest.json', follow=False, manifest=True)
        selection.linked_manifests[str(path.parent)] = linked['id']
    reports = {}
    for item in closed['reports']:
        identity = item['report']
        entry, value = selection.document(identity['path'], 'qualified ' + item['origin'] + ' ' + item['kind'], identity)
        require(value['passed'] is True and value['kind'] == item['kind']
                and value['source_snapshot'] == closed['source_snapshot'], 'Exact successful qualification required')
        reports[(value['kind'], value['row'])] = (entry, value)
    profiles = []
    for row in plan['rows']:
        name = row['name']
        require(name in rules.SPECS, 'Unexpected profile in frozen plan')
        baseline = plan['baselines'][row['baseline']]
        before_entry, before = selection.document(baseline['files']['sdkconfig.json']['snapshot'], 'baseline normalized config')
        seed = selection.add(row['seed']['path'], 'immutable original full sdkconfig seed', row['seed'])
        profile = {key: row[key] for key in ('name', 'backend', 'custom_flac', 'enabled')}
        profile.update(baseline_config_id=before_entry['id'], seed_id=seed['id'])
        for kind in ['export'] + (['clang'] if row['enabled'] else []):
            report_entry, report = reports[(kind, name)]
            build = Path(row['build'] if kind == 'export' else row['clang_build'])
            config_entry, config = selection.document(build / 'config/sdkconfig.json', 'qualified ' + kind + ' normalized config')
            rules.config_scope(before, config, name, kind)
            execution_entry, execution = selection.document(report['run_record']['path'], 'original successful terminal run', report['run_record'])
            require(execution['status'] == 'TERMINAL_SUCCESS' and execution['kind'] == kind
                    and execution['row'] == name and execution['marker_sha256'] == rules.ORIGINAL_MARKER
                    and execution['source_snapshot_before'] == execution['source_snapshot_after'] == closed['source_snapshot'],
                    'Actual execution record identity/terminal mismatch')
            require(all(command['status'] == 'TERMINAL' and type(command['returncode']) is int
                        and command['returncode'] == 0 for command in execution['commands']),
                    'Every actual command must have authoritative terminal0')
            record = {'qualification_id': report_entry['id'], 'config_id': config_entry['id'],
                      'execution_id': execution_entry['id'],
                      'selected_text': selected_artifacts(selection, Path(report_entry['original_path']), report, kind)}
            # No recursive build-tree scan: select only generated command/config
            # and toolchain descriptions useful for interpreting original rows.
            record['compile_database_id'] = selection.add(build / 'compile_commands.json',
                'actual generated compiler database observed at archive stage')['id']
            compiler_descriptions = []
            for filename in ['CMakeCCompiler.cmake', 'CMakeCXXCompiler.cmake']:
                matches = list((build / 'CMakeFiles').glob('*/' + filename))
                require(len(matches) == 1, 'One actual generated compiler description required')
                compiler_descriptions.append(selection.add(matches[0], 'actual generated compiler description')['id'])
            record['compiler_description_ids'] = compiler_descriptions
            if kind == 'export':
                receipt, _value = selection.document(Path(row['output']) / 'manifest.json', 'saved GCC production artifact receipt')
                record['receipt_id'] = receipt['id']
                record['firmware_link'] = (Path(row['output']) / 'app.bin').relative_to(ROOT).as_posix()
            else:
                lint_entry, lint = selection.document(report['lint_report']['path'], 'complete original full-project lint report', report['lint_report'])
                record['lint_report_id'] = lint_entry['id']
                record['tu_source_ids'] = {}
                for result in lint['results']:
                    path = (ROOT / result['file']).resolve()
                    require(path.is_relative_to(ROOT), 'Project TU path escape')
                    observed = ident(path)
                    require(observed['sha256'] == result['source_sha256'], 'Actual lint TU source changed')
                    record['tu_source_ids'][result['file']] = selection.add(path, 'full-project lint TU source', observed)['id']
                record['lint_artifact_ids'] = [selection.add(value['path'], 'complete original lint output/log/YAML', value)['id']
                                                for value in report['lint_artifacts']]
            profile[kind] = record
        profiles.append(profile)
    # Original markers/reports recursively name exact source/header/tool/log
    # identities. Follow those identities only, never a directory tree.
    selection.drain()
    canonical_packager_paths(selection, packager)
    c.stable()
    index = {
        'schema': 'cyd-static-rx-sdk-archive-index-v1', 'source_snapshot': closed['source_snapshot'],
        'summary_id': summary_entry['id'], 'root_terminal_id': receipt_entry['id'],
        'original_marker_id': old_marker_entry['id'], 'repair_marker_id': repair_marker_entry['id'],
        'original_plan_id': plan_entry['id'], 'original_failed_pdm_id': failed_entry['id'],
        'pure_policy_controls_id': controls_entry['id'], 'profiles': profiles, 'packager_ids': packager,
        'pure_archive_preparation_id': prep_entry['id'],
        'warning_review_ids': warning_review,
        'linked_manifests': selection.linked_manifests,
        'limits': {'physical_qualified': False, 'heap_saving_claimed': False,
                   'clang_is_experimental_frontend_profile': True, 'production_compiler_is_gcc': True,
                   'omitted_binaries_reconstructed': False, 'original_failed_qualifier_remains_nonpass': True},
        'archival_observation_scope': 'Explicit selected text lacking a prior raw hash is labelled archive-stage observation; original qualification assertions are not rerun or independently reconstructed from omitted ELF.',
    }
    return selection, index


def plan(args):
    require(not PLAN.exists(), 'Never overwrite archive selection plan')
    closed_path, note, closed = root_receipt(args.summary_sha256, args.terminal_receipt, args.terminal_receipt_sha256)
    selection, index = prepare_selection(closed_path, note, closed)
    c = selection.collector
    result = {'schema': SCHEMA, 'mode': 'PLAN_ONLY', 'archive_written': False,
              'destination': str(DEST), 'summary_sha256': args.summary_sha256,
              'terminal_receipt': ident(note), 'entries': c.entries, 'bindings': c.bindings,
              'index': index, 'observed': list(c.observed.values()),
              'selected_entries': len(c.entries), 'unique_text_bytes': c.unique_text_bytes,
              'unique_stored_payloads': len(c.payloads),
              'next': 'Root reviews exact plan SHA, then separately authorizes fresh write'}
    c.stable()
    write_new(PLAN, encode(result))
    print(encode({'plan': ident(PLAN), 'archive_written': False}).decode())


def write(args):
    require(args.write_reviewed_archive, 'Separate explicit --write-reviewed-archive required')
    require(hashfile(PLAN) == args.plan_sha256, 'Exact root-reviewed plan SHA required')
    chosen = load(PLAN)
    require(chosen['schema'] == SCHEMA and chosen['mode'] == 'PLAN_ONLY'
            and chosen['destination'] == str(DEST) and not DEST.exists(), 'Fresh fixed archive destination required')
    root_receipt(chosen['summary_sha256'], chosen['terminal_receipt']['path'], chosen['terminal_receipt']['sha256'])
    require(all(ident(item['path']) == item for item in chosen['observed']), 'Reviewed selection changed before write')
    # No collection/reselection occurs during write. Every selected original
    # byte and the exact tools are pinned by the reviewed plan.
    files = {}
    for row in chosen['entries']:
        if row['disposition'] != 'stored':
            continue
        if row['stored_path'] in files:
            continue
        raw = Path(row['original_path']).read_bytes()
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'Selected text changed')
        import gzip
        data = gzip.compress(raw, compresslevel=9, mtime=0) if row['encoding'] == 'gzip' else raw
        require(len(data) == row['stored_bytes'] and sha(data) == row['stored_sha256'], 'Selected encoding changed')
        files[row['stored_path']] = data
    files.update({'index.json': encode(chosen['index']), 'path-map.json': encode({'entries': chosen['entries']}),
                  'bindings.json': encode({'bindings': chosen['bindings']}),
                  'retention.json': encode({'schema': SCHEMA, 'plan_sha256': args.plan_sha256,
                    'selected_entries': chosen['selected_entries'],
                    'unique_text_bytes': chosen['unique_text_bytes'],
                    'binary_bytes_duplicated': 0, 'whole_trees_copied': False,
                    'references_scope': 'Binary omissions and linked evidence identities are not reconstructed by this archive.',
                    'archive_stage_observation': chosen['index']['archival_observation_scope']}),
                  'README.md': (HERE / 'README.template.md').read_bytes(), '.gitattributes': b'* -text\n'})
    manifest = {'schema': 'cyd-static-rx-sdk-archive-manifest-v1',
                'files': [{'path': name, 'bytes': len(raw), 'sha256': sha(raw)} for name, raw in sorted(files.items())]}
    require(all(ident(item['path']) == item for item in chosen['observed']), 'Selected bytes changed during encoding')
    DEST.mkdir()
    for name, raw in sorted(files.items()):
        destination = (DEST / name).resolve()
        require(destination.is_relative_to(DEST.resolve()), 'Reviewed archive member path escape')
        write_new(destination, raw)
    write_new(DEST / 'manifest.json', encode(manifest))
    print(encode({'archive_written': True, 'manifest': ident(DEST / 'manifest.json'),
                  'offline_verification_pending': True}).decode())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', nargs='?', default='plan', choices=['plan', 'write'])
    parser.add_argument('--summary-sha256')
    parser.add_argument('--terminal-receipt', type=Path)
    parser.add_argument('--terminal-receipt-sha256')
    parser.add_argument('--plan-sha256')
    parser.add_argument('--write-reviewed-archive', action='store_true')
    args = parser.parse_args()
    if args.phase == 'plan':
        require(args.summary_sha256 and args.terminal_receipt and args.terminal_receipt_sha256,
                'Root terminal closure receipt and exact SHA pins required before any real plan')
        plan(args)
    else:
        require(args.plan_sha256, 'Explicit reviewed plan SHA required')
        write(args)


if __name__ == '__main__':
    main()
