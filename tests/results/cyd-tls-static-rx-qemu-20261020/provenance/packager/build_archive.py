"""Bounded target archive. Default PLAN ONLY; authoritative terminal receipt required.

Filesystem-only collection and offline verification; never execute SDK/tool/test
recipes. No partial/live campaign can be collected. Root must separately approve
plan and write. Whole build trees, binaries, tool bytes and prior drafts excluded.
"""
import argparse
from pathlib import Path
import re
import struct
import subprocess
import sys

from archive_core import Collector, encode, hashfile, load, require, sha
import evidence_rules as rules

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TARGET = ROOT / '.build/rxt02'
DEST = ROOT / 'tests/results/cyd-tls-static-rx-qemu-20261020'
TOOLS = ('archive_core.py', 'build_archive.py', 'evidence_rules.py', 'verify.py', 'check-prep.py', 'SPEC.md', 'README.template.md', 'TARGET.template.md')


def safe(base, relative):
    path = (base / relative).resolve()
    require(path.is_relative_to(base.resolve()), 'Evidence path escape')
    return path


def derive_elf(path, symbols):
    image = path.read_bytes()
    require(image[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', image, 18)[0] == 94, 'Original Xtensa ELF32LE machine94')
    section_offset = struct.unpack_from('<I', image, 32)[0]
    section_size, count = struct.unpack_from('<HH', image, 46)
    sections = [struct.unpack_from('<10I', image, section_offset + n * section_size) for n in range(count)]
    words = {}
    for kind, name in [('calloc', 'mbedtls_calloc_func'), ('free', 'mbedtls_free_func')]:
        address = symbols[name]['address']
        found = [s for s in sections if s[1] != 8 and s[3] <= address and address + 4 <= s[3] + s[5]]
        require(len(found) == 1, 'One initialized ELF allocator word section')
        offset = found[0][4] + address - found[0][3]
        words[kind] = {'address': address, 'file_offset': offset, 'raw_hex': image[offset:offset + 4].hex(), 'value': struct.unpack_from('<I', image, offset)[0]}
    return {'elf_sha256': sha(image), 'elf_bytes': len(image), 'machine': 94, 'allocator_words': words,
            'scope': 'Metadata derived by reading original omitted ELF at packaging. Offline verifier checks bindings/internal consistency; it cannot reread/reconstruct omitted ELF bytes.'}


def receipt(args):
    require(re.fullmatch('[0-9a-f]{64}', args.report_sha256) and re.fullmatch('[0-9a-f]{64}', args.terminal_receipt_sha256), 'Explicit root final SHA pins')
    note = args.terminal_receipt.resolve()
    require(note.is_relative_to(ROOT / '.build') and not note.is_relative_to(TARGET) and hashfile(note) == args.terminal_receipt_sha256, 'Separate root-authored terminal receipt with exact raw SHA')
    row = load(note)
    require(Path(row['report_path']).resolve() == TARGET / 'report.json', 'Receipt must name exact canonical campaign report')
    require(hashfile(TARGET / 'report.json') == args.report_sha256, 'Exact final raw report')
    report = load(TARGET / 'report.json')
    rules.terminal(report, row, args.report_sha256)
    return note, row, report


def historical_section(c):
    """Called only AFTER new terminal/full gate and all new cases validate."""
    base = ROOT / '.build/rxt01'
    report_path = base / 'report.json'
    old = load(report_path)
    report_entry = c.add(report_path, 'Bounded historical raw rxt01 report, partial/nonpass; other references not requalified', rules.OLD_REPORT_SHA, preferred='history/rxt01-report.json')
    failed_path = base / 'reserve-off-reclaim-on-qemu.log'
    log_entry = c.add(failed_path, 'Historical rejected disabled getter predicate raw log', rules.OLD_LOG_SHA)
    receipt_entry = c.add(ROOT / '.build/cyd-static-rx-target-nonpass-02.json', 'Exact corrected root terminal1 receipt; historical only', rules.OLD_RECEIPT_SHA, preferred='history/rxt01-root-nonpass.json')
    summary = rules.historical_nonpass(old, failed_path.read_bytes())
    suffix = '/tests/native/cyd_tls_static_rx/target/project/main/disabled.c'
    original = [p for p in old['inputs'] if p.replace('\\', '/').endswith(suffix)]
    require(len(original) == 1, 'One original disabled source in pinned old report')
    source = old['inputs'][original[0]]
    require(source['sha256'].startswith('567c8da4'), 'Original old disabled source identity prefix; complete SHA bound by exact old report')
    source_entry = c.add(safe(base, source['snapshot']), 'Original failed disabled fixture raw snapshot, not current corrected source', source['sha256'])
    c.bind(report_entry, ['inputs', original[0], 'sha256'], source_entry)
    failed_index = next(i for i, r in enumerate(old['commands']) if r['label'] == 'reserve-off-reclaim-on-qemu')
    c.bind(report_entry, ['commands', failed_index, 'log_sha256'], log_entry)
    return {'report_id': report_entry['id'], 'rejected_log_id': log_entry['id'], 'root_receipt_id': receipt_entry['id'], 'original_disabled_id': source_entry['id'], 'original_disabled_input_key': original[0],
            'summary': summary, 'old_full_report_sha256': rules.OLD_REPORT_SHA,
            'other_old_references': {'retained_or_requalified': False, 'scope': 'Only four historical raw payloads retained. Other old source/tool/ELF/bundle/log references remain uninterpreted report metadata; no reconstruction or qualification.'}}


def collect(args):
    require(not DEST.exists(), 'Fresh additive archive destination')
    note, terminal, report = receipt(args)  # Before touching any campaign outputs.
    c = Collector()
    root_map = {}
    def top(path, role, expected=None):
        row = c.add(path, role, expected)
        if path.is_relative_to(TARGET):
            root_map[path.relative_to(TARGET).as_posix()] = row['id']
        return row
    primary = top(TARGET / 'report.json', 'Exact authoritative final canonical12 runtime report', args.report_sha256)
    note_entry = c.add(note, 'Root authoritative runner terminal receipt', args.terminal_receipt_sha256, preferred='reports/root-terminal.json')
    c.bind(note_entry, ['report_sha256'], primary)
    for original, row in report['inputs'].items():
        entry = top(safe(TARGET, row['snapshot']), 'Raw canonical/SDK pre-execution input snapshot', row['sha256'])
        c.bind(primary, ['inputs', original, 'sha256'], entry)
        c.add(original, 'Current byte-equal original input readback; not a Git cleanliness assertion', row['sha256'])
    for key, digest in report['tools'].items():
        c.bind(primary, ['tools', key], c.add(key, 'Original tool/ROM binary identity; bytes deliberately omitted', digest))
    for path in sorted(TARGET.glob('*')):
        if path.is_file():
            top(path, 'Raw top-level original freeze/build/nm/asm/dependency/ninja/merge/QEMU/SDK-state log or metadata')
    for dirname in ('input-snapshots', 'sdk-inputs', 'sources'):
        folder = TARGET / dirname
        if folder.exists():
            for path in sorted(folder.rglob('*')):
                if path.is_file():
                    top(path, 'Raw bounded canonical source/header input snapshot')
    for number, row in enumerate(report['commands']):
        c.bind(primary, ['commands', number, 'log_sha256'], c.entries[root_map[row['label'] + '.log']])
    rules.commands(report, lambda p: safe(TARGET, p).read_bytes())
    variants, elf_metadata, flash_metadata = {}, {}, {}
    for name in rules.VARIANTS:
        campaign = TARGET / 'campaigns' / name
        manifest_path = campaign / 'source-manifest.json'
        manifest = load(manifest_path)
        manifest_digest = report['frozen_campaign_manifests'][str(manifest_path)]
        manifest_entry = top(manifest_path, 'Frozen independent variant source manifest; actual execution bundle separately retained', manifest_digest)
        c.bind(primary, ['frozen_campaign_manifests', str(manifest_path)], manifest_entry)
        mapping = {'source-manifest.json': manifest_entry['id']}
        originals = {}
        for original, row in manifest['original_inputs'].items():
            require(original in report['inputs'] and report['inputs'][original]['sha256'] == row['sha256'], 'All original recipe inputs frozen by parent before execution')
            original_entry = c.entries[root_map[report['inputs'][original]['snapshot']]]
            c.bind(manifest_entry, ['original_inputs', original, 'sha256'], original_entry)
            originals[row['snapshot']] = safe(TARGET, report['inputs'][original]['snapshot']).read_bytes()
        expected = rules.source_variant(name, manifest, originals)
        for relative, digest in manifest['frozen_sources'].items():
            require(safe(campaign, relative).read_bytes() == expected[relative], 'Actual frozen recipe bytes')
            row = top(safe(campaign, relative), 'Exact executed source recipe, including only declared semantic mutation', digest)
            c.bind(manifest_entry, ['frozen_sources', relative], row)
            mapping[relative] = row['id']
        execution, build = campaign / 'execution', campaign / 'working-build'
        bundle_path = execution / 'execution-bundle.json'
        bundle = load(bundle_path)
        bundle_entry = top(bundle_path, 'Original actual target execution bundle', report['variants'][name]['execution_bundle_sha256'])
        c.bind(primary, ['variants', name, 'execution_bundle_sha256'], bundle_entry)
        require(bundle['candidate_only'] is True and bundle['sdk_commit'] == rules.SDK and bundle['frozen_sources'] == manifest['frozen_sources'], 'Independent compiled/runtime source identity')
        require(bundle['reserve_enabled'] is rules.options(name)[0] and bundle['reclaim_enabled'] is rules.options(name)[1], 'Execution option identity')
        for relative, digest in bundle['frozen_sources'].items():
            c.bind(bundle_entry, ['frozen_sources', relative], c.entries[mapping[relative]])
        for path in sorted(execution.rglob('*')):
            if path.is_file():
                mapping[path.relative_to(campaign).as_posix()] = top(path, 'Original bounded execution artifact or explicit omitted binary')['id']
        for relative, digest in bundle['artifacts_before_qemu'].items():
            row = c.entries[mapping['execution/' + relative]]
            require(row['sha256'] == digest, 'Actual pre-runtime artifact unchanged')
            c.bind(bundle_entry, ['artifacts_before_qemu', relative], row)
        closure_ids = {}
        for original, digest in bundle['compiled_header_closure'].items():
            row = c.add(original, 'Actual compiled dependency closure source/header/generated config; binary identity only if encountered', digest)
            c.bind(bundle_entry, ['compiled_header_closure', original], row)
            closure_ids[original] = row['id']
        for original, digest in bundle['tools'].items():
            require(report['tools'].get(original) == digest, 'Exact original tool identities across all12')
            c.bind(bundle_entry, ['tools', original], c.add(original, 'Original actual SDK/QEMU/tool/ROM identity only', digest))
        selected = ['config/sdkconfig.h', 'config/sdkconfig.json', 'flasher_args.json', 'build.ninja', 'compile_commands.json', 'project_description.json', 'CMakeCache.txt']
        if rules.options(name)[0]:
            selected.append('native-tls-static-rx/ssl_tls.c')
        else:
            require(not (build / 'native-tls-static-rx/ssl_tls.c').exists(), 'Disabled actual overlay absent')
        for relative in selected:
            mapping['working-build/' + relative] = top(build / relative, 'Selected actual configure/build/source/link metadata')['id']
        for path in sorted(build.glob('*.map')):
            mapping['working-build/' + path.name] = top(path, 'Optional original link map text')['id']
        for relative in ('working-sdkconfig', 'option-disabled.defaults'):
            path = campaign / relative
            if path.exists():
                mapping[relative] = top(path, 'Actual frozen option/config input')['id']
        description = load(build / 'project_description.json')
        elf = execution / 'artifacts' / description['app_elf']
        elf_entry = top(elf, 'Actual runtime ELF identity only', bundle['elf_sha256'])
        top(build / description['app_elf'], 'Original nm/disassembly build ELF identity, byte-equal runtime copy', bundle['elf_sha256'])
        top(build / description['app_bin'], 'Original merged application image identity, byte-equal execution copy', hashfile(execution / 'artifacts' / description['app_bin']))
        c.bind(bundle_entry, ['elf_sha256'], elf_entry)
        symbols = rules.nm((TARGET / (name + '-nm.log')).read_bytes())
        elf_metadata[name] = derive_elf(elf, symbols)
        elf_metadata[name].update(elf_id=elf_entry['id'], nm_id=root_map[name + '-nm.log'])
        assemblies = {s: (TARGET / (name + '-asm-' + s + '.log')).read_bytes() for s in (rules.ENABLED_ASM if rules.options(name)[0] else rules.ASM)}
        rules.elf_logs(name, symbols, assemblies, elf_metadata[name], bundle)
        rules.config(name, bundle['configuration'])
        rules.oracle(name, (TARGET / (name + '-qemu.log')).read_bytes(), report['variants'][name], bundle['configuration'])
        flash_path = execution / 'qemu-flash.bin'
        flash = flash_path.read_bytes()
        require(len(flash) == 0x400000 and sha(flash) == bundle['flash_sha256'], 'Original flash identity/size')
        flash_entry = c.entries[mapping['execution/qemu-flash.bin']]
        c.bind(bundle_entry, ['flash_sha256'], flash_entry)
        components = []
        for offset, relative in load(build / 'flasher_args.json')['flash_files'].items():
            path = safe(build, relative)
            row = top(path, 'Actual merged component binary identity; omitted')
            raw = path.read_bytes()
            start = int(offset, 0)
            require(flash[start:start + len(raw)] == raw, 'Original omitted merged flash component byte range')
            components.append({'offset': start, 'relative_build_path': relative, 'artifact_id': row['id'], 'sha256': row['sha256'], 'bytes': len(raw)})
        flash_metadata[name] = {'flash_id': flash_entry['id'], 'flash_sha256': sha(flash), 'bytes': len(flash), 'components': components,
                                'scope': 'Original omitted flash/component range comparison at packaging; offline verification cannot reconstruct omitted binary bytes.'}
        variants[name] = {'original_campaign': str(campaign), 'manifest_id': manifest_entry['id'], 'bundle_id': bundle_entry['id'], 'files': mapping, 'compiled_header_ids': closure_ids}
    history = historical_section(c)
    for n in TOOLS:
        c.add(HERE / n, 'Reviewed self-contained archive tooling/template', preferred='provenance/packager/' + n)
    for folder in sorted(HERE.glob('prep-check-*')):
        c.tree(folder, 'Pure archive preparation checks; never target execution')
    c.stable()
    index = {'format_version': 1, 'target_original_directory': str(TARGET), 'terminal_receipt_id': note_entry['id'], 'terminal_receipt_sha256': args.terminal_receipt_sha256,
             'final_report_id': primary['id'], 'final_report_sha256': args.report_sha256, 'files': root_map, 'variants': variants, 'historical_nonpass': history,
             'status': {'isolated_target_12_variant_gate': True, 'production_integration_qualified': False, 'physical_benefit_claimed': False,
                        'tls_network_protocol_qualified': False, 'production_radio_binding_qualified': False,
                        'omitted_elf_independently_reconstructed_offline': False, 'host_or_old_pointer_results_relabelled': False}}
    c.files.update({'index.json': encode(index), 'path-map.json': encode({'entries': c.entries}), 'bindings.json': encode({'bindings': c.bindings}),
                    'derived-elf-metadata.json': encode(elf_metadata), 'derived-flash-metadata.json': encode(flash_metadata),
                    'packaging-readback.json': encode({'all_selected_inputs_unchanged_after': True, 'selected_inputs': c.observed}),
                    'verify.py': (HERE / 'verify.py').read_bytes(), 'evidence_rules.py': (HERE / 'evidence_rules.py').read_bytes(), '.gitattributes': b'* -text\n** -text\n'})
    for source, name in [('README.template.md', 'README.md'), ('TARGET.template.md', 'TARGET.md')]:
        raw = (HERE / source).read_bytes().replace(b'@@REPORT_SHA@@', args.report_sha256.encode()).replace(b'@@RECEIPT_SHA@@', args.terminal_receipt_sha256.encode())
        require(b'@@' not in raw, 'Resolved templates')
        c.files[name] = raw
    # The reviewed verifier validates the complete virtual archive before any
    # archive write, including PLAN ONLY. This executes archival checks, never
    # source recipes, SDK code, tests or external tools.
    import verify
    virtual = dict(c.files)
    virtual['manifest.json'] = encode({'files': [{'path': n, 'bytes': len(raw), 'sha256': sha(raw)} for n, raw in sorted(c.files.items())]})
    verify.main(virtual)
    c.stable()
    return c


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--report-sha256', required=True)
    p.add_argument('--terminal-receipt', type=Path, required=True)
    p.add_argument('--terminal-receipt-sha256', required=True)
    p.add_argument('--attempt', default='attempt-01')
    p.add_argument('--write-reviewed-archive', action='store_true')
    args = p.parse_args()
    require(re.fullmatch('attempt-[0-9]{2}', args.attempt), 'Fresh exact attempt name')
    attempt = HERE / args.attempt
    require(not attempt.exists(), 'Preserve prior attempts')
    attempt.mkdir()
    result = {'passed': False, 'archive_written': False, 'mode': 'write_reviewed_archive' if args.write_reviewed_archive else 'plan_only', 'sdk_compiler_qemu_wsl_git_network_device_invoked': False}
    try:
        c = collect(args)
        manifest = encode({'files': [{'path': n, 'bytes': len(raw), 'sha256': sha(raw)} for n, raw in sorted(c.files.items())]})
        result.update(manifest_sha256=sha(manifest), payload_files=len(c.files) + 1, payload_bytes=sum(map(len, c.files.values())) + len(manifest), mapped_versions=len(c.entries), explicit_omissions=sum(r['disposition'] == 'omitted' for r in c.entries), json_hash_bindings=len(c.bindings))
        for name, raw in [('planned-files.json', manifest), ('planned-index.json', c.files['index.json']), ('planned-path-map.json', c.files['path-map.json'])]:
            (attempt / name).write_bytes(raw)
        if args.write_reviewed_archive:
            require(not DEST.exists() and DEST.resolve() == DEST, 'Exact fresh additive destination')
            DEST.mkdir(parents=True)
            for name, raw in c.files.items():
                path = safe(DEST, name)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            (DEST / 'manifest.json').write_bytes(manifest)
            done = subprocess.run([sys.executable, '-B', str(DEST / 'verify.py')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
            (attempt / 'offline-verifier.log').write_bytes(done.stdout)
            require(done.returncode == 0, 'Offline archive verifier rejected; preserve failure')
            c.stable()
            result.update(archive_written=True, archive=str(DEST), readme_sha256=hashfile(DEST / 'README.md'))
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
