"""Superseded partial/nonpassing pointer-userdata prototype archive.

Default PLAN ONLY; no SDK/Git process. The exact nonpass report and terminal
observation are required. Archive integrity can pass while target qualification
remains false. Writing requires later root approval; prior evidence is immutable.
"""
import argparse
from pathlib import Path
import re
import struct
import subprocess
import sys

from archive_core import Collector, encode, hashfile, load, require, sha

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / 'tests/results/cyd-tls-rx-pointer-prototype-20261020'
HOST = ROOT / '.build/cyd-tls-reserve-host-draft-01'
CONFIG = ROOT / '.build/cyd-tls-reserve-config-draft-01'
PREP = ROOT / '.build/cyd-tls-reserve-target-prep-02'
TARGET = ROOT / '.build/trx01'
OBSERVATION = ROOT / '.build/trx01-observed-terminal-20261020.json'
OBSERVATION_SHA = '4411a96a7ac1318ce465a1e212cbbf4c216d50b9d1c42344991925f6cfce32a8'
REPORT_SHA = 'd4b6e019c0dcf1eaa59ca6f10f32be7d995fa82be2402fdb92ef8d9833561efc'
REJECTED_BUNDLE = 'f58e350a1fc70ed7be938261732177f2f1f04fd9a636b867322dfa3779583e61'
CANDIDATE = '77db50af0ff65dfa333b28584b48632c625d999984e7ff8fffd48cb0e52cdb0f'
PINS = {'host-qualification': (HOST / 'qualification-report.json', '9714a0869bf5d349dcb8fba0eac10f7fb7518182c62275e1340d9aca825da386'),
        'host': (HOST / 'attempt05/report.json', '5e144dbc846e972d14093c16f14be40539c95bd2fe5d8ec36a32662c25d713dc'),
        'configure': (CONFIG / 'report.json', '9c20612cc76f3b9b8542631c467710739cf3a759de442ebbd4568ab2b8675d72'),
        'readiness': (PREP / 'readiness.json', 'bce3679dcd0bbb743e735d613ceac49ef392abd8a75e76ef29989d92a527f8e0'),
        'terminal-observation': (OBSERVATION, OBSERVATION_SHA)}
VARIANTS = ('canonical', 'skip-marker', 'skip-exclusive', 'skip-rollback', 'early-publish-phase',
            'ordinary-free-static', 'bypass-reclaim', 'canonical-reclaim-off', 'reserve-off-reclaim-on', 'reserve-off-reclaim-off')
ACCEPTED = VARIANTS[:6]
EXECUTED = VARIANTS[:7]
UNRUN = VARIANTS[7:]
FAILURES = {'skip-marker': 'unlabelled_client_ordinary_rx', 'skip-exclusive': 'independent_context_rx_no_alias',
            'skip-rollback': 'rollback_returns_slot', 'early-publish-phase': 'no_reloan_during_erase',
            'ordinary-free-static': 'reserved_pointer_never_sdk_heap_free', 'bypass-reclaim': 'busy_slot_reclaim_retry_preserved'}
SDK = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
PREP_MANIFEST = '99d311538ee439357ffed8bd5d53ddce320339bfc0892a9aae1fcf24b0816a4c'


def terminal_contract(report, observation):
    require(report['passed'] is False and not report.get('full_target_matrix_complete', False) and report['error'] == 'AssertionError: ', 'Exact final nonpass report required')
    require(report['compile_only'] is False and report['production_integration'] is False and report['physical_benefit_claimed'] is False and report['network_or_device'] is False, 'Exact candidate qualification limits')
    require(set(report['variants']) == set(ACCEPTED) and len(report['variants']) == 6 and all(row['passed'] is True for row in report['variants'].values()), 'Only six accepted historical outcomes required')
    require(report['candidate_sha256'] == CANDIDATE, 'Canonical host-fixed candidate changed')
    require(all(row['terminal_exit'] == 0 and row['timed_out'] is False for row in report['commands']), 'Every target child must terminate zero without timeout')
    labels = [row['label'] for row in report['commands']]
    runtime_labels = {name + '-qemu' for name in VARIANTS}
    require([label for label in labels if label in runtime_labels] == [name + '-qemu' for name in EXECUTED] and [row['label'] for row in report['commands'] if '-smp' in row['argv']] == [name + '-qemu' for name in EXECUTED], 'Exactly seven actual QEMU executions, no final three; SDK after-qemu state logs are separate')
    for name in EXECUTED:
        require(labels.count(name + '-build') == labels.count(name + '-qemu') == 1, 'Independent real build/runtime command required: ' + name)
        build = next(row for row in report['commands'] if row['label'] == name + '-build')['argv']
        runtime = next(row for row in report['commands'] if row['label'] == name + '-qemu')['argv']
        require(('-DisableReserve' in build) is name.startswith('reserve-off-') and ('-DisableReclaim' in build) is (name in ('canonical-reclaim-off', 'reserve-off-reclaim-off')), 'Exact real build option flags')
        require(runtime[runtime.index('-smp') + 1] == '2' and runtime[runtime.index('-nic') + 1] == 'none' and '-snapshot' in runtime and '-no-reboot' in runtime, 'Actual dual-core isolated no-NIC runtime command')
    for name in UNRUN:
        require(name + '-build' not in labels and name + '-qemu' not in labels and labels.count('freeze-' + name) == 1, 'Pending source recipe must remain unbuilt/unrun')
    for name, expected in FAILURES.items():
        if name == 'bypass-reclaim':
            continue
        require(report['variants'][name]['exact_semantic_failure'] == expected, 'Exact named semantic control: ' + name)
    require(observation['runner_session'] == 14586 and observation['runner_terminal_exit'] == 1 and observation['report_sha256'] == REPORT_SHA, 'Authoritative terminal1 observation')
    require(observation['accepted_variants'] == list(ACCEPTED) and observation['executed_qemu_variants'] == [name + '-qemu' for name in EXECUTED] and observation['not_executed'] == list(UNRUN), 'Exact observed partial cohort')
    rejected = observation['last_control']
    require(rejected['name'] == 'bypass-reclaim' and rejected['expected_semantic_marker_observed'] is True and rejected['controlled_stop_observed'] is True and rejected['generic_panic_after_marker'] is True and rejected['accepted_as_pass'] is False, 'Named marker followed by rejected panic is not a PASS')


def bind_inputs(c, container, report, base, current=False):
    for original, row in report.get('inputs', {}).items():
        if isinstance(row, dict) and 'snapshot' in row:
            target = c.add(base / row['snapshot'], 'frozen original input', row['sha256'], original=original)
            c.bind(container, ['inputs', original, 'sha256'], target)
            if current:
                c.add(original, 'current final target input equals pre-runtime snapshot', row['sha256'])
        elif isinstance(row, dict) and 'sha256' in row:
            c.bind(container, ['inputs', original, 'sha256'], c.add(original, 'reported native tool/source identity', row['sha256']))
    for index, command in enumerate(report.get('commands', [])):
        c.bind(container, ['commands', index, 'log_sha256'], c.add(base / (command['label'] + '.log'), 'exact raw command log', command['log_sha256']))
    for relative, digest in report.get('generated_inputs', {}).items():
        c.bind(container, ['generated_inputs', relative], c.add(base / relative, 'generated host seam/control', digest))
    for key in ('tools', 'native_tools'):
        for original, digest in report.get(key, {}).items():
            c.bind(container, [key, original], c.add(original, 'actual native tool identity', digest))
    for key in ('host_tool_identities', 'host_tool_identities_before'):
        for original, digest in report.get(key, {}).items():
            c.bind(container, [key, original], c.reported_tool(original, digest))


def elf_details(path, nm, assemblies):
    raw = path.read_bytes()
    require(raw[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', raw, 18)[0] == 94, 'Actual Xtensa ELF94 required')
    syms = {}
    for line in nm.read_text(errors='replace').splitlines():
        match = re.fullmatch(r'([0-9a-f]+)\s+([0-9a-f]+)\s+([A-Za-z])\s+(.+)', line)
        if match:
            syms[match[4]] = {'address': int(match[1], 16), 'bytes': int(match[2], 16), 'type': match[3]}
    shoff = struct.unpack_from('<I', raw, 32)[0]
    shsize, shcount = struct.unpack_from('<HH', raw, 46)
    sections = [struct.unpack_from('<10I', raw, shoff + index * shsize) for index in range(shcount)]
    addresses = {syms[name]['address'] for name in ('mbedtls_calloc_func', 'mbedtls_free_func')}
    for path in assemblies:
        addresses.update(int(value, 16) for value in re.findall(r'\bl32r\s+a\d+,\s*([0-9a-f]+)', path.read_text(errors='replace')))
    words = {}
    for address in sorted(addresses):
        section = next((row for row in sections if row[1] != 8 and row[3] <= address <= row[3] + row[5] - 4), None)
        require(section is not None, 'Initialized ELF word absent')
        offset = section[4] + address - section[3]
        words[str(address)] = {'offset': offset, 'raw_hex': raw[offset:offset + 4].hex(), 'value': struct.unpack_from('<I', raw, offset)[0]}
    return {'elf_sha256': sha(raw), 'elf_bytes': len(raw), 'machine': 94, 'entry': struct.unpack_from('<I', raw, 24)[0],
            'symbols': {name: row for name, row in syms.items() if name in ('mbedtls_calloc_func', 'mbedtls_free_func', 'esp_mbedtls_mem_calloc', '__wrap_esp_mbedtls_mem_calloc', 'esp_mbedtls_mem_free')},
            'words': words, 'scope': 'Derived header/data-word metadata; original full ELF explicitly omitted'}


def failure_details(log_path, nm_path):
    log = log_path.read_text().replace('\r\n', '\n')
    require(re.findall(r'^TLS_RX_TARGET_FAILURE (.+)$', log, re.M) == ['busy_slot_reclaim_retry_preserved'] and log.count('TLS_RX_TARGET_CONTROLLED_STOP') == 1, 'Exact bypass marker/stop retained')
    abort = re.findall(r'abort\(\) was called at PC 0x([0-9a-f]+) on core (\d+)', log)
    require(len(abort) == 1 and abort[0][1] == '0' and log.index('TLS_RX_TARGET_CONTROLLED_STOP') < log.index('abort() was called'), 'Panic after named stop must remain rejected')
    syms = []
    for line in nm_path.read_text().splitlines():
        match = re.fullmatch(r'([0-9a-f]+)\s+([0-9a-f]+)\s+([A-Za-z])\s+(.+)', line)
        if match:
            syms.append({'name': match[4], 'address': int(match[1], 16), 'bytes': int(match[2], 16)})
    frames = []
    for token in re.findall(r'0x([0-9a-f]+):0x[0-9a-f]+', log):
        pc = int(token, 16)
        matches = [row for row in syms if row['address'] <= pc < row['address'] + row['bytes']]
        require(len(matches) == 1, 'Exact raw backtrace-to-nm resolution')
        frames.append({'pc': pc, **matches[0], 'offset': pc - matches[0]['address']})
    names = [row['name'] for row in frames]
    expected = ['lock_init_generic', 'lock_acquire_generic', '_lock_acquire', 'get_adjusted_boot_time', '_gettimeofday_r', 'gettimeofday', 'esp_sync_timekeeping_timers', 'esp_restart', 'require']
    require(names[3:12] == expected and frames[3]['offset'] == 0x17 and frames[3]['pc'] == int(abort[0][0], 16), 'Observed SDK lock/timekeeping/restart chain')
    return {'accepted_as_runtime_pass': False, 'named_marker_observed': True, 'controlled_stop_observed': True,
            'abort_after_marker': True, 'abort_pc': int(abort[0][0], 16), 'abort_core': 0,
            'log_sha256': hashfile(log_path), 'nm_sha256': hashfile(nm_path), 'resolved_frames': frames,
            'scope': 'Derived from original raw panic and same-ELF nm; named marker does not override runner rejection. No new target execution.'}


def collect(args):
    require(not OUT.exists(), 'New additive archive must not exist')
    report_path = TARGET / 'report.json'
    require(args.target_report_sha256 == REPORT_SHA and hashfile(report_path) == REPORT_SHA and hashfile(OBSERVATION) == OBSERVATION_SHA, 'Exact root-authorized final nonpass report/observation required')
    report = load(report_path)
    terminal_contract(report, load(OBSERVATION))
    c = Collector()
    primary = {}
    reports = {}
    for name, (path, digest) in {**PINS, 'target': (report_path, args.target_report_sha256)}.items():
        entry = c.add(path, 'authoritative ' + name + ' report', digest, preferred='reports/' + name + '.json')
        primary[name], reports[name] = entry['id'], load(path)
    host, configure = reports['host'], reports['configure']
    require(host['passed'] is True and host['inputs_unchanged'] is True and host['candidate_fix']['fixed_sha256'] == CANDIDATE, 'Exact passing host-fixed source proof')
    require(configure['passed'] is True and configure['configure_case_count'] == 24 and configure['original_inputs_unchanged'] is True and configure['all_input_snapshots_match'] is True, '24 real configure-only cases')
    bind_inputs(c, c.entries[primary['host']], host, HOST / 'attempt05')
    bind_inputs(c, c.entries[primary['configure']], configure, CONFIG)
    bind_inputs(c, c.entries[primary['target']], report, TARGET, current=False)
    c.bind(c.entries[primary['terminal-observation']], ['report_sha256'], c.entries[primary['target']])
    for name, row in configure['cases'].items():
        if name.endswith('-capture'):
            continue
        c.bind(c.entries[primary['configure']], ['cases', name, 'log_sha256'], c.add(CONFIG / name / 'configure.log', 'actual configure-only case log', row['log_sha256']))
        for relative, digest in row['generated_inputs_before'].items():
            c.bind(c.entries[primary['configure']], ['cases', name, 'generated_inputs_before', relative], c.add(CONFIG / name / relative, 'exact configure-only proposal/source input', digest))
    c.bind(c.entries[primary['configure']], ['canonical_overlay', 'sha256'], c.add(configure['canonical_overlay']['actual'], 'exact configured original proposal overlay', configure['canonical_overlay']['sha256']))
    qualification = reports['host-qualification']
    c.bind(c.entries[primary['host-qualification']], ['host_report_sha256'], c.entries[primary['host']])
    c.bind(c.entries[primary['host-qualification']], ['configure_report_sha256'], c.entries[primary['configure']])
    c.bind(c.entries[primary['host-qualification']], ['candidate_sha256'], c.add(HOST / 'attempt05/candidate-fixed.c', 'canonical host-fixed unapplied source', CANDIDATE))
    for name, row in qualification['attempts'].items():
        c.bind(c.entries[primary['host-qualification']], ['attempts', name, 'report_sha256'], c.add(HOST / name / 'report.json', 'host attempt historical/current raw report', row['report_sha256']))
    prep_manifest = load(PREP / 'manifest.json')
    prep_digest = hashfile(PREP / 'manifest.json')
    require(prep_digest == PREP_MANIFEST, 'Wrong exact reviewed prep02 manifest')
    pment = c.add(PREP / 'manifest.json', 'frozen unapplied target preparation manifest')
    for relative, row in prep_manifest['files'].items():
        c.bind(pment, ['files', relative, 'sha256'], c.add(PREP / relative, 'exact prep02 payload', row['sha256']))
    guard_entry = c.add(PREP / 'guard-checks-01/report.json', 'supporting SDK guard proof')
    guards = load(PREP / 'candidate/supporting-source-guards.json')
    require(len(guards) == 17 and len(load(PREP / 'guard-checks-01/report.json')['guard_cases']) == 22, '17 SDK guard closure and22 offline checks')
    c.bind(c.entries[primary['readiness']], ['guard_report_sha256'], guard_entry)
    guard_manifest = c.add(PREP / 'candidate/supporting-source-guards.json', 'exact 17-source supporting guard map')
    for relative, digest in load(PREP / 'guard-checks-01/report.json')['actual_sdk_guards'].items():
        target = c.add(PREP / 'guard-checks-01/sdk-copy' / relative, 'exact raw guarded SDK source/header', digest)
        c.bind(guard_entry, ['actual_sdk_guards', relative], target)
        c.bind(guard_manifest, [relative, 'sha256'], target)
    for folder in (HOST, CONFIG, PREP, ROOT / '.build/cyd-tls-reserve-port-prep-01', ROOT / '.build/cyd-tls-reserve-target-prep-01', ROOT / '.build/cyd-tls-reserve-target-matrix-freeze-check-01'):
        c.tree(folder, 'selected raw host/config/preparation/history; historical scope retained')
    c.tree(ROOT / '.build/cyd-tls-reserve-archive-prep-01', 'superseded never-sealed full-matrix archive preparation; not qualification')
    for path in sorted(TARGET.glob('*')):
        if path.is_file():
            c.add(path, 'raw actual target command/SDK state/runtime log')
    variants, metadata = {}, {}
    for name in VARIANTS:
        campaign = TARGET / 'campaigns' / name
        manifest_path = campaign / 'source-manifest.json'
        manifest = load(manifest_path)
        ment = c.add(manifest_path, 'frozen independent variant source manifest', report['frozen_campaign_manifests'][str(manifest_path)])
        c.bind(c.entries[primary['target']], ['frozen_campaign_manifests', str(manifest_path)], ment)
        for relative, digest in manifest['frozen_sources'].items():
            c.bind(ment, ['frozen_sources', relative], c.add(campaign / relative, 'exact compiled variant source', digest))
        if name in UNRUN:
            require(not (campaign / 'execution').exists() and not (campaign / 'working-build').exists(), 'Final three recipes must have no actual build/runtime artifacts')
            variants[name] = {'status': 'frozen_unbuilt_unrun', 'manifest_id': ment['id']}
            continue
        execution = campaign / 'execution'
        bundle_path = execution / 'execution-bundle.json'
        bundle = load(bundle_path)
        bent = c.add(bundle_path, 'actual independent target execution bundle', report['variants'][name]['execution_bundle_sha256'] if name in ACCEPTED else REJECTED_BUNDLE)
        if name in ACCEPTED:
            c.bind(c.entries[primary['target']], ['variants', name, 'execution_bundle_sha256'], bent)
        require(bundle['candidate_only'] is True and bundle['elf_machine'] == 94 and bundle['sdk_commit'] == SDK, 'Exact isolated target ABI scope')
        require(bundle['frozen_sources'] == manifest['frozen_sources'], 'Compiled/runtime bundle must use the exact frozen variant recipe')
        for relative, digest in bundle['frozen_sources'].items():
            c.bind(bent, ['frozen_sources', relative], c.add(campaign / relative, 'runtime-bundle frozen source identity', digest))
        for relative, digest in bundle['artifacts_before_qemu'].items():
            c.bind(bent, ['artifacts_before_qemu', relative], c.add(execution / relative, 'actual pre-runtime artifact/identity', digest))
        for original, digest in bundle['compiled_header_closure'].items():
            c.bind(bent, ['compiled_header_closure', original], c.add(original, 'actual compiled header closure', digest))
        for original, digest in bundle['tools'].items():
            c.bind(bent, ['tools', original], c.add(original, 'actual target tool/ROM identity', digest))
        build = campaign / 'working-build'
        description = load(build / 'project_description.json')
        elf = execution / 'artifacts' / description['app_elf']
        eent = c.add(elf, 'actual target ELF identity only', bundle['elf_sha256'])
        c.bind(bent, ['elf_sha256'], eent)
        assemblies = sorted(TARGET.glob(name + '-asm-*.log'))
        metadata[name] = elf_details(elf, TARGET / (name + '-nm.log'), assemblies)
        extra_ids = {}
        for path in (build / 'build.ninja', *sorted((build / 'toolchain').glob('*'))):
            if path.is_file():
                extra_ids[path.name] = c.add(path, 'actual compiler/link flags metadata')['id']
        overlay = build / 'native-tls-static-rx/ssl_tls.c'
        if overlay.is_file():
            extra_ids['actual-overlay'] = c.add(overlay, 'actual compiled SDK overlay')['id']
        variants[name] = {'status': 'accepted_historical_outcome' if name in ACCEPTED else 'rejected_panic_after_marker', 'manifest_id': ment['id'], 'bundle_id': bent['id'], 'elf_id': eent['id'], 'extra_ids': extra_ids,
                          'nm_id': c.add(TARGET / (name + '-nm.log'), 'actual symbols')['id'],
                          'asm_ids': {path.name.removeprefix(name + '-asm-').removesuffix('.log'): c.add(path, 'actual ownership call disassembly')['id'] for path in assemblies},
                          'qemu_log_id': c.add(TARGET / (name + '-qemu.log'), 'actual runtime oracle')['id']}
    observation = load(OBSERVATION)
    c.bind(c.entries[primary['terminal-observation']], ['last_control', 'log_sha256'], c.entries[variants['bypass-reclaim']['qemu_log_id']])
    c.bind(c.entries[primary['terminal-observation']], ['last_control', 'nm_sha256'], c.entries[variants['bypass-reclaim']['nm_id']])
    failure = failure_details(TARGET / 'bypass-reclaim-qemu.log', TARGET / 'bypass-reclaim-nm.log')
    header_path = PREP / 'guard-checks-01/sdk-copy/components/mbedtls/mbedtls/include/mbedtls/ssl.h'
    header = c.add(header_path, 'public getter documentation establishes missing numeric-userdata contract')
    declaration = {'header_id': header['id'], 'line_start': 2705, 'line_end': 2719,
                   'raw_excerpt': '\n'.join(header_path.read_text().splitlines()[2704:2719]),
                   'numeric_userdata_isolation_proven': False, 'old_candidate_superseded': True,
                   'scope': 'Public pointer getter is undefined after numeric setter; tests covered pointer userdata only; corrected registry is separate and not archived'}
    for name in ('archive_core.py', 'build_archive.py', 'verify.py', 'SPEC.md', 'README.template.md', 'HOST.template.md', 'check-prep.py'):
        c.add(HERE / name, 'archive construction/verification provenance', preferred='provenance/' + name)
    for folder in sorted(HERE.glob('prep-check-*')):
        c.tree(folder, 'archive packager preparation/check history; not target qualification')
    c.stable()
    index = {'candidate_sha256': CANDIDATE, 'target_report_sha256': args.target_report_sha256, 'terminal_observation_sha256': OBSERVATION_SHA, 'prep02_manifest_sha256': prep_digest,
             'primary_report_ids': primary, 'prep_manifest_id': pment['id'], 'guard_report_id': guard_entry['id'], 'guard_manifest_id': guard_manifest['id'], 'variants': variants,
             'status': {'superseded': True, 'unapplied_candidate': True, 'historical_partial': True, 'target_campaign_passed': False,
                        'runner_terminal_exit': 1, 'accepted_variants': 6, 'executed_variants': 7, 'unrun_variants': 3,
                        'numeric_userdata_isolation_proven': False, 'option_matrix_complete': False, 'production_integrated': False,
                        'corrected_registry_covered': False, 'physical_benefit_claimed': False, 'protocol_conformance_claimed': False},
             'closure_scope': 'Every selected raw report/source/log and explicit input/header/tool/execution artifact reference. Unreferenced replaceable SDK working binaries are outside this archive scope.'}
    c.files.update({'index.json': encode(index), 'path-map.json': encode({'entries': c.entries}),
                    'bindings.json': encode({'bindings': c.bindings}), 'elf-metadata.json': encode(metadata),
                    'rejected-runtime-failure.json': encode(failure), 'SDK-declaration-gap.json': encode(declaration),
                    'current-verification.json': encode({'all_selected_inputs_stable_after': True, 'selected_inputs': c.observed}),
                    'verify.py': (HERE / 'verify.py').read_bytes(), '.gitattributes': b'* -text\n** -text\n'})
    for source, target in (('README.template.md', 'README.md'), ('HOST.template.md', 'HOST.md')):
        raw = (HERE / source).read_bytes().replace(b'@@TARGET_SHA@@', args.target_report_sha256.encode())
        require(b'@@' not in raw, 'Unresolved template token')
        c.files[target] = raw
    return c


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target-report-sha256', required=True)
    p.add_argument('--attempt', default='attempt-01')
    p.add_argument('--write-reviewed-archive', action='store_true')
    args = p.parse_args()
    require(re.fullmatch('[0-9a-f]{64}', args.target_report_sha256) and re.fullmatch('attempt-[0-9]{2}', args.attempt), 'Explicit final SHA/fresh attempt required')
    attempt = HERE / args.attempt
    require(not attempt.exists(), 'Preserve existing attempt evidence')
    attempt.mkdir()
    terminal = {'passed': False, 'archive_written': False, 'historical_target_qualification_passed': False, 'archive_kind': 'superseded_partial_nonpass_pointer_prototype', 'sdk_qemu_git_network_device_commands': False}
    try:
        c = collect(args)
        terminal.update(mapped_versions=len(c.entries), json_hash_bindings=len(c.bindings), selected_input_count=len(c.observed))
        if args.write_reviewed_archive:
            require(not OUT.exists() and OUT.resolve() == OUT, 'Fresh exact archive output required')
            OUT.mkdir(parents=True, exist_ok=False)
            for name, raw in sorted(c.files.items()):
                path = OUT / name
                require(path.resolve().is_relative_to(OUT), 'Archive path escapes')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            (OUT / 'manifest.json').write_bytes(encode({'files': [{'path': name, 'bytes': len(raw), 'sha256': sha(raw)} for name, raw in sorted(c.files.items())]}))
            done = subprocess.run([sys.executable, '-B', str(OUT / 'verify.py')], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=60)
            (attempt / 'offline-verifier.log').write_bytes(done.stdout)
            require(done.returncode == 0, 'Offline archive verifier failed; preserve nonpass archive')
            c.stable()
            terminal.update(archive_written=True, archive=str(OUT), manifest_sha256=hashfile(OUT / 'manifest.json'), readme_sha256=hashfile(OUT / 'README.md'))
        else:
            (attempt / 'planned-files.json').write_bytes(encode({'files': [{'path': name, 'sha256': sha(raw), 'bytes': len(raw)} for name, raw in sorted(c.files.items())]}))
        terminal['passed'] = True
    except BaseException as error:
        terminal['error'] = type(error).__name__ + ': ' + str(error)
        if isinstance(error, subprocess.TimeoutExpired):
            (attempt / 'timeout.log').write_bytes(error.output or b'')
        (attempt / 'report.json').write_bytes(encode(terminal))
        raise
    (attempt / 'report.json').write_bytes(encode(terminal))
    print(encode(terminal).decode())


if __name__ == '__main__':
    main()
