"""Standalone filesystem-only archive verifier. No original paths/tools are opened."""
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import evidence_rules as rules


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    root = Path(__file__).resolve().parent
    def local(relative):
        path = root / relative
        require(path.resolve().is_relative_to(root) and not path.is_symlink(), 'Archive path escape/symlink')
        return path
    def json_file(relative):
        return json.loads(local(relative).read_bytes())
    manifest = json_file('manifest.json')
    paths = [row['path'] for row in manifest['files']]
    require(len(paths) == len(set(paths)), 'Unique manifest paths')
    require(set(paths) == {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix() != 'manifest.json'}, 'Exact manifest payload file set')
    for row in manifest['files']:
        raw = local(row['path']).read_bytes()
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'Manifest raw file identity: ' + row['path'])
    require(local('.gitattributes').read_bytes() == b'* -text\n** -text\n', 'Raw archive byte attributes')
    index, mapping = json_file('index.json'), json_file('path-map.json')['entries']
    cache = {}
    def raw(entry_id):
        require(isinstance(entry_id, int) and 0 <= entry_id < len(mapping), 'Valid mapped identity')
        row = mapping[entry_id]
        require(row['id'] == entry_id and row['disposition'] == 'stored', 'Omitted artifact has identity only, not archived bytes')
        if entry_id not in cache:
            encoded = local(row['stored_path']).read_bytes()
            require(sha(encoded) == row['stored_sha256'] and len(encoded) == row['stored_bytes'], 'Stored representation identity')
            require(row['encoding'] in ('raw', 'gzip'), 'Explicit content representation')
            value = gzip.decompress(encoded) if row['encoding'] == 'gzip' else encoded
            require(sha(value) == row['sha256'] and len(value) == row['bytes'], 'Original decompressed/raw bytes')
            require(not value.startswith((b'\x7fELF', b'MZ', b'!<arch>\n')), 'Executables/archives deliberately excluded')
            if row['encoding'] == 'gzip':
                require(gzip.compress(value, compresslevel=9, mtime=0) == encoded, 'Deterministic gzip bytes')
            cache[entry_id] = value
        return cache[entry_id]
    for number, row in enumerate(mapping):
        require(row['id'] == number and len(row['sha256']) == 64 and row['roles'], 'Complete path-map metadata')
        if row['disposition'] == 'stored':
            require(row['observed_bytes'] is True, 'Stored bytes were actually observed')
            raw(number)
        else:
            require(row['disposition'] == 'omitted' and row['reason'] and 'stored_path' not in row, 'Explicit binary/tool omission metadata')
            require(row['bytes'] is None if row['observed_bytes'] is False else isinstance(row['bytes'], int), 'Known/unknown omitted size is explicit')
    for row in json_file('bindings.json')['bindings']:
        value = json.loads(raw(row['container_id']))
        for token in row['hash_tokens']:
            value = value[token]
        require(value == mapping[row['target_id']]['sha256'], 'Original JSON hash reference binding')
    require(index['module_normalized_lf_sha256'] == rules.MODULE and index['guard_manifest_sha256'] == rules.GUARDS, 'Canonical module/guards')
    expected_reports = {'unit': rules.UNIT_SHA, 'config': rules.CONFIG_SHA, 'service': rules.SERVICE_SHA}
    summaries = {}
    for name, cohort in index['cohorts'].items():
        require(name in expected_reports and sha(raw(cohort['report_id'])) == expected_reports[name] == cohort['report_sha256'], 'Exact terminal report hash')
        require(cohort['root_reported_outer_terminal_exit'] == 0 and cohort['root_reported_outer_session'] == {'unit': 86428, 'config': 21895, 'service': 79183}[name], 'Root-attributed outer terminal status')
        files = cohort['files']
        report = json.loads(raw(cohort['report_id']))
        read = lambda relative: raw(files[relative])
        identity = lambda relative: mapping[files[relative]]['sha256']
        summaries[name] = rules.service(report, read, identity) if name == 'service' else getattr(rules, name)(report, read)
    require(set(index['cohorts']) == set(expected_reports) and summaries == index['summaries'], 'All three complete host cohorts')
    prep = index['source_only_preparation']
    require(sha(raw(prep['manifest_id'])) == rules.PREP_SHA == prep['manifest_sha256'] and prep['executed_target_qualification'] is False, 'Source-only prep provenance remains source-only')
    prep_report = json.loads(raw(prep['manifest_id']))
    require(len(prep_report['files']) == len(prep['files']) == 554 and prep_report['proposed_file_count'] == len(index['canonical_files']) == 34, 'Full immutable preparation and canonical34')
    for relative, row in prep_report['files'].items():
        value = raw(prep['files'][relative])
        require(sha(value) == row['sha256'] and len(value) == row['bytes'], 'Source-only prep raw entry identity')
    for relative, row in index['canonical_files'].items():
        require(raw(row['current_id']) == raw(row['preparation_id']) == raw(prep['files']['repository/' + relative]) and sha(raw(row['current_id'])) == row['raw_sha256'], 'Canonical raw source equality with exact final prep')
    status = index['status']
    require(all(status[k] is True for k in ['canonical_host_unit_passed', 'canonical_source_only_configure_passed', 'canonical_host_service_passed', 'production_files_applied']), 'Honest completed host scope')
    require(all(v is False for k, v in status.items() if k not in ['canonical_host_unit_passed', 'canonical_source_only_configure_passed', 'canonical_host_service_passed', 'production_files_applied']), 'Target/protocol/physical/Git-at-test-execution claims remain false')
    require(json.loads(raw(index['root_readback_id']))['passed'] is True, 'Separate original root readback retained')
    current = json_file('current-verification.json')
    require(current['selected_inputs_unchanged_after'] is True, 'Packaging after-readback flag')
    known = {(row['observed_from'], row['sha256'], row['bytes']) for row in mapping if row['observed_bytes']}
    require(all((name, row['sha256'], row['bytes']) in known for name, row in current['selected_inputs'].items()), 'Selected-input packaging readback metadata closure')
    print(json.dumps({'passed': True, 'scope': 'Archive integrity and original canonical host/config/service oracles only; no new execution/target/physical claims',
                      'manifest_sha256': sha(local('manifest.json').read_bytes()), 'mapped_versions': len(mapping),
                      'json_hash_bindings': len(json_file('bindings.json')['bindings']),
                      'explicit_omissions': sum(r['disposition'] == 'omitted' for r in mapping), 'summaries': summaries}, indent=2))


if __name__ == '__main__':
    main()
