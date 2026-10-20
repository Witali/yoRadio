"""Pure source/metadata/oracle checks. No archived script or tool is executed."""
import ast
import hashlib
import json
import re

SDK = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
MODULE = '17e98a29cadd0387d9db725d50c12514847426cd9cfa607abf5224884fe17555'
GUARDS = '81fc22bbd240f71cb664ab08490f4e79ae805b066f0d61dbe24299af47ab49bb'
SDK_SOURCE = '1beac5da2dd0f99f626c81651e9cecb921eb9725a9f17624851802b8c6259ddc'
RUNNER_SESSION = 17556
OLD_REPORT_SHA = '344bdd390454d08a50822bb9283b1efefe2075d274cca728609e69d66b9d4180'
OLD_LOG_SHA = '7e73ae96d311b14ae6652d37c4e62d0de36e6d1da7aea1ac224188cd368e057e'
OLD_RECEIPT_SHA = 'e36a0a15ce2529677451ea448f7f10566c102c075501a1584f04914606797aea'
MAIN = 'idf/esp32-cyd2usb-native/main/'
SSL_TLS = 'components/mbedtls/mbedtls/library/ssl_tls.c'
VARIANTS = ('canonical', 'skip-init', 'skip-free', 'evict-full', 'forget-resets-loan', 'skip-exclusive', 'early-publish-phase',
            'ordinary-free-static', 'bypass-reclaim', 'canonical-reclaim-off', 'reserve-off-reclaim-on', 'reserve-off-reclaim-off')
FAILURES = {'skip-init': 'init_revokes_stale_identity', 'skip-free': 'free_revokes_stale_identity', 'evict-full': 'full_registry_does_not_evict',
            'forget-resets-loan': 'config_free_keeps_exclusive_loan', 'skip-exclusive': 'independent_context_rx_no_alias',
            'early-publish-phase': 'no_reloan_during_erase', 'ordinary-free-static': 'reserved_pointer_never_sdk_heap_free',
            'bypass-reclaim': 'busy_slot_reclaim_retry_preserved'}
WRAPS = ('yoradio_tls_static_rx_calloc', 'mbedtls_platform_zeroize', 'heap_caps_calloc', 'heap_caps_free', 'esp_crt_bundle_attach')
ASM = ('mbedtls_ssl_setup', 'mbedtls_ssl_free', 'esp_mbedtls_mem_free')
ENABLED_ASM = ASM + ('yoradio_tls_static_rx_calloc', 'mbedtls_ssl_config_init', 'mbedtls_ssl_config_free')
ABSENT = ('native_tls_rx_reserve_crt_bundle_attach', 'yoradio_tls_static_rx_calloc', 'yoradio_tls_static_rx_free',
          'yoradio_tls_static_rx_zeroize_free', '__wrap_yoradio_tls_static_rx_calloc', '__wrap_mbedtls_platform_zeroize',
          '__wrap_heap_caps_calloc', '__wrap_heap_caps_free', 's_radio_configurations', 'yoradio_tls_static_rx_forget_configuration',
          '__wrap_esp_crt_bundle_attach', 's_rx')


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def normalized(raw):
    value = raw.replace(b'\r\n', b'\n')
    require(raw == value or raw == value.replace(b'\n', b'\r\n'), 'Uniform LF/CRLF required')
    return value


def text(raw):
    return raw.decode(errors='replace').replace('\r\n', '\n')


def options(name):
    return not name.startswith('reserve-off-'), name not in ('canonical-reclaim-off', 'reserve-off-reclaim-off')


def terminal(report, receipt, digest):
    require(receipt['kind'] == 'root_authoritative_runner_terminal' and receipt['runner_session'] == RUNNER_SESSION and receipt['runner_terminal_exit'] == 0 and receipt['report_sha256'] == digest,
            'Explicit root-authoritative terminal0 and exact final SHA receipt required')
    require(report['passed'] is True and report['full_target_matrix_complete'] is True and report['compile_only'] is False and report['all_current_inputs_match'] is True,
            'Final fully completed runtime report required')
    require(report['status'] == 'runtime_qualified_selected_variants' and not report.get('error') and set(report['variants']) == set(VARIANTS) and all(v['passed'] is True for v in report['variants'].values()), 'Exact12 final outcomes')
    require(report['production_integration'] is False and report['physical_benefit_claimed'] is False and report['network_or_device'] is False, 'Isolated qualification limits')
    require(report['candidate_normalized_lf_sha256'] == MODULE, 'Final integer-registry module')


def oracle(name, raw, result, cfg=None):
    log = text(raw)
    require(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered', log, re.I), 'Panic never passes, even after named marker')
    reserve, reclaim = options(name)
    if not reserve:
        require(log.count('TLS_RX_DISABLED_ENTRY ordinary_sdk=1') == 1 and log.count('TLS_RX_DISABLED_COMPLETE reserve=0 reclaim=' + str(int(reclaim)) + ' cycles=16 ordinary_sdk=1') == 1, 'Exact disabled ordinary SDK oracle')
        require(all(s not in log for s in ['TLS_RX_TARGET_ENTRY', 'TLS_RX_TARGET_FAILURE', 'TLS_RX_TARGET_CONTROLLED_STOP']), 'No enabled fixture substitution in disabled run')
        require(result['reserve_enabled'] is False and result['reclaim_enabled'] is reclaim and result['public_setup_reset_free_cycles'] == 16 and all(result[k] is True for k in ['original_sdk_ssl_source_compiled', 'reserve_module_static_slot_and_rx_wraps_absent', 'ordinary_callback_and_dispatcher']), 'Disabled result metadata')
        require(cfg is not None, 'Actual disabled configuration required for capacity/getter separation')
        capacity = re.findall(r'^TLS_RX_DISABLED_CAPACITY content=(\d+) storage=(\d+) allocated_min=(\d+) pre_handshake_payload=(-?\d+) setups=(\d+)$', log, re.M)
        require(len(capacity) == 1 and log.count('TLS_RX_DISABLED_CAPACITY') == 1, 'Exactly one disabled capacity marker required')
        content, storage, allocated, payload, setups = map(int, capacity[0])
        require(content == cfg['MBEDTLS_SSL_IN_CONTENT_LEN'] == 16384 and storage >= content and allocated >= storage and setups == 32, 'Disabled full RX storage/all32 allocations must be retained')
        expected_payload = min(cfg['MBEDTLS_SSL_IN_CONTENT_LEN'], cfg['MBEDTLS_SSL_OUT_CONTENT_LEN']) if cfg.get('MBEDTLS_SSL_MAX_FRAGMENT_LENGTH', False) else cfg['MBEDTLS_SSL_IN_CONTENT_LEN']
        require(payload == expected_payload, 'Disabled pre-handshake getter must match actual pinned MFL profile, independently of storage')
    elif name in FAILURES:
        require(log.count('TLS_RX_TARGET_ENTRY registry_fixture=1') == 1 and re.findall(r'^TLS_RX_TARGET_FAILURE (.+)$', log, re.M) == [FAILURES[name]] and log.count('TLS_RX_TARGET_CONTROLLED_STOP') == 1 and 'TLS_RX_TARGET_COMPLETE' not in log, 'Exact negative-control marker/stop/uniqueness')
        require(result['exact_semantic_failure'] == FAILURES[name] and result['phase_scoped_mutation'] is (name in ('early-publish-phase', 'forget-resets-loan')), 'Exact named/scoped control metadata')
    else:
        markers = ['TLS_RX_TARGET_ENTRY registry_fixture=1', 'TLS_RX_TARGET_COMPLETE registry_fixture=1 production_radio=0 physical_benefit=0',
                   'TLS_RX_TARGET_CASE ownership_rollback_reopen injected_nulls=4 real_oom_claim=0', 'TLS_RX_TARGET_CASE smp_ownership_handover_erase cores=0,1',
                   'TLS_RX_TARGET_CASE registry_userdata_init_free_live_reuse attach_return_injection=1 early_setup_actual=1',
                   'TLS_RX_TARGET_CASE registry_capacity entries=8 clients=9 soft_fallback=1', 'TLS_RX_TARGET_CASE actual_initializer_isr registry_revoked=1']
        require(all(log.count(s) == 1 for s in markers) and 'TLS_RX_TARGET_FAILURE' not in log and 'TLS_RX_TARGET_CONTROLLED_STOP' not in log, 'Exact canonical public lifecycle/ISR/SMP oracle')
        capacity = re.findall(r'^TLS_RX_TARGET_CAPACITY content=(\d+) storage=(\d+) pointer_alignment=(\d+)$', log, re.M)
        oom = re.findall(r'^TLS_RX_TARGET_CASE real_oom_reserved_rx blocks=(\d+) actual_backend_nulls=(\d+)$', log, re.M)
        recovery = re.findall(r'^TLS_RX_TARGET_CASE actual_reclaim_recovery real_nulls=(\d+) recoveries=(\d+) released=(\d+) min=4 target=8$', log, re.M)
        require(len(capacity) == len(oom) == 1 and int(capacity[0][0]) == 16384 and int(capacity[0][1]) >= 16384 and all(int(v) > 0 for v in oom[0]), 'Measured capacity and separate actual heap-NULL observation')
        require((len(recovery) == 1 and all(int(v) > 0 for v in recovery[0])) if reclaim else not recovery, 'Actual reclaim option observation')
        require(result['capacity_observed'] == list(capacity[0]) and result['real_heap_observation'] == list(oom[0]) and result['actual_reclaim_observation'] == [list(v) for v in recovery] and result['injected_rollback_cases'] == 4 and result['injected_failures_not_real_oom_proof'] is True, 'Original parsed observations match raw log')


def historical_nonpass(report, raw):
    """Only replay old report shape and rejected log; no old successes requalified."""
    require(report['passed'] is False and not report.get('full_target_matrix_complete', False) and set(report['variants']) == set(VARIANTS[:10]) and all(v['passed'] is True for v in report['variants'].values()), 'Historical rxt01 remains10 reported accepted outcomes and overall nonpass')
    runtime = [r for r in report['commands'] if r['label'] in {n + '-qemu' for n in VARIANTS}]
    require([r['label'] for r in runtime] == [n + '-qemu' for n in VARIANTS[:11]] and not any(r['label'] in ('reserve-off-reclaim-off-build', 'reserve-off-reclaim-off-qemu') for r in report['commands']), 'Historical eleventh executed/twelfth unrun')
    failed = runtime[-1]
    require(failed['terminal_exit'] == 0 and failed['timed_out'] is False, 'Old failing fixture QEMU child returned0, parent remained nonpass')
    log = text(raw)
    require(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered', log, re.I), 'Historical rejection had no panic')
    require(log.count('TLS_RX_DISABLED_ENTRY ordinary_sdk=1') == 1 and re.findall(r'^TLS_RX_TARGET_FAILURE (.+)$', log, re.M) == ['disabled_original_full_record_payload'] and log.count('TLS_RX_TARGET_CONTROLLED_STOP') == 1 and 'TLS_RX_DISABLED_COMPLETE' not in log, 'Historical exact failed getter expectation, never relabelled pass')
    return {'recorded_accepted_outcomes': 10, 'executed_qemu_children': 11, 'rejected_variant': 'reserve-off-reclaim-on', 'unrun_variant': 'reserve-off-reclaim-off', 'parent_terminal_exit_root_reported': 1, 'full_gate_passed': False}


def config(name, cfg):
    reserve, reclaim = options(name)
    for k in ('ESP_TLS_USING_MBEDTLS', 'MBEDTLS_INTERNAL_MEM_ALLOC', 'MBEDTLS_CERTIFICATE_BUNDLE', 'COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE'):
        require(cfg[k] is True, 'Required actual config: ' + k)
    require(bool(cfg.get('YORADIO_TLS_STATIC_RX_RESERVE', False)) is reserve and bool(cfg.get('YORADIO_TLS_INPUT_RECLAIM', False)) is reclaim, 'Actual option matrix')
    require(cfg['MBEDTLS_SSL_IN_CONTENT_LEN'] == 16384 and cfg['MBEDTLS_SSL_OUT_CONTENT_LEN'] == 4096, 'Unchanged record profile')
    for k in ('FREERTOS_UNICORE', 'MBEDTLS_DYNAMIC_BUFFER', 'MBEDTLS_SSL_VARIABLE_BUFFER_LENGTH', 'MBEDTLS_CUSTOM_MEM_ALLOC', 'HEAP_ABORT_WHEN_ALLOCATION_FAILS'):
        require(not cfg.get(k, False), 'Forbidden actual config: ' + k)


def command_labels():
    labels = {'sdk-head-before', 'sdk-state-before'} | {'freeze-' + n for n in VARIANTS}
    for name in VARIANTS:
        labels |= {name + s for s in ('-build', '-nm', '-dependencies', '-ninja-commands', '-merge', '-qemu')}
        labels |= {name + '-asm-' + s for s in (ENABLED_ASM if options(name)[0] else ASM)}
        for phase in ('after-build', 'after-qemu'):
            labels |= {'sdk-' + what + '-' + name + '-' + phase for what in ('head', 'state')}
    return labels


def commands(report, read):
    rows = report['commands']
    require(len(rows) == len(command_labels()) == len({r['label'] for r in rows}) and {r['label'] for r in rows} == command_labels(), 'Complete unique command set for12 builds/runtime executions')
    result = {}
    for row in rows:
        require(row['terminal_exit'] == 0 and row['timed_out'] is False and sha(read(row['label'] + '.log')) == row['log_sha256'], 'Original command terminal/log identity; timeout/failure rejected')
        result[row['label']] = row
        if row['label'].startswith('sdk-head-'):
            require(text(read(row['label'] + '.log')).strip() == SDK, 'Original exact SDK commit log')
        if row['label'].startswith('sdk-state-'):
            require(not text(read(row['label'] + '.log')).strip(), 'Original SDK tracked-clean log')
    for name in VARIANTS:
        reserve, reclaim = options(name)
        argv = result[name + '-build']['argv']
        require(('-DisableReserve' in argv) is (not reserve) and ('-DisableReclaim' in argv) is (not reclaim), 'Actual independent build option flags')
        argv = result[name + '-qemu']['argv']
        require(argv[argv.index('-M') + 1] == 'esp32' and argv[argv.index('-smp') + 1] == '2' and argv[argv.index('-nic') + 1] == 'none' and '-snapshot' in argv and '-no-reboot' in argv, 'Actual isolated two-core no-NIC QEMU invocation')
    return result


def nm(raw):
    return {m[4]: {'address': int(m[1], 16), 'bytes': int(m[2], 16), 'type': m[3]}
            for m in re.finditer(r'^([0-9a-f]+)\s+([0-9a-f]+)\s+([A-Za-z])\s+(.+)$', text(raw), re.M)}


def elf_logs(name, symbols, assemblies, metadata, bundle):
    reserve, reclaim = options(name)
    expected_calloc = '__wrap_esp_mbedtls_mem_calloc' if reclaim else 'esp_mbedtls_mem_calloc'
    require(bundle['elf_machine'] == metadata['machine'] == 94 and metadata['elf_sha256'] == bundle['elf_sha256'], 'Original omitted-ELF metadata identity/machine94')
    require(bundle['allocator_words'] == {'calloc': expected_calloc, 'free': 'esp_mbedtls_mem_free'} and '__wrap_esp_mbedtls_mem_free' not in symbols, 'Strict ordinary free and configured calloc pairing')
    for field, pointer, expected in [('calloc', 'mbedtls_calloc_func', expected_calloc), ('free', 'mbedtls_free_func', 'esp_mbedtls_mem_free')]:
        word = metadata['allocator_words'][field]
        require(word['address'] == symbols[pointer]['address'] and word['value'] == symbols[expected]['address'] and int.from_bytes(bytes.fromhex(word['raw_hex']), 'little') == word['value'] and 0 <= word['file_offset'] <= metadata['elf_bytes'] - 4, 'Derived ELF data word bound to original nm; not offline ELF reread')
    require(set(assemblies) == set(ENABLED_ASM if reserve else ASM), 'Exact original disassembly logs')
    for symbol, raw in assemblies.items():
        require('<' + symbol + '>:' in text(raw), 'Disassembly entry symbol')
    if reserve:
        require('__wrap_yoradio_tls_static_rx_calloc' in text(assemblies['mbedtls_ssl_setup']) and 'yoradio_tls_static_rx_free' in text(assemblies['mbedtls_ssl_setup']) and 'yoradio_tls_static_rx_zeroize_free' in text(assemblies['mbedtls_ssl_free']) and '__wrap_heap_caps_free' in text(assemblies['esp_mbedtls_mem_free']), 'Actual allocator/rollback/zeroize/free call logs')
        for hook in ('init', 'free'):
            present = 'yoradio_tls_static_rx_forget_configuration' in text(assemblies['mbedtls_ssl_config_' + hook])
            require(present is (name != 'skip-' + hook), 'Actual config hook presence/declared omission')
    else:
        require(all(s not in symbols for s in ABSENT) and 'yoradio_tls_static_rx' not in text(assemblies['mbedtls_ssl_setup']) + text(assemblies['mbedtls_ssl_free']), 'Reserve-off module/static slot/RX wrappers absent')
        require('mbedtls_calloc' in text(assemblies['mbedtls_ssl_setup']) and 'mbedtls_zeroize_and_free' in text(assemblies['mbedtls_ssl_free']) and 'heap_caps_free' in text(assemblies['esp_mbedtls_mem_free']), 'Disabled ordinary SDK call logs')


def patch(source, patcher):
    literals = {}
    for node in ast.parse(patcher.decode()).body:
        if isinstance(node, ast.Assign):
            for key in node.targets:
                if isinstance(key, ast.Name) and key.id in ('SOURCE_SHA256', 'GUARDS_SHA256', 'REPLACEMENTS'):
                    literals[key.id] = ast.literal_eval(node.value)
    raw = normalized(source)
    require(literals['SOURCE_SHA256'] == SDK_SOURCE == sha(raw) and literals['GUARDS_SHA256'] == GUARDS and len(literals['REPLACEMENTS']) == 6, 'Complete pinned SDK source and six exact overlay replacements')
    for old, new in literals['REPLACEMENTS']:
        require(raw.count(old) == 1, 'Unique exact SDK replacement anchor')
        raw = raw.replace(old, new, 1)
    return raw if source == normalized(source) else raw.replace(b'\n', b'\r\n')


def mutate_bytes(raw, before, after):
    newline = b'\r\n' if b'\r\n' in raw else b'\n'
    before, after = [s.encode().replace(b'\n', newline) for s in (before, after)]
    require(raw.count(before) == 1, 'One declared variant edit')
    return raw.replace(before, after, 1)


def source_variant(name, manifest, originals):
    expected_variant = name if name in FAILURES else 'canonical'
    require(manifest['status'] == 'frozen_unbuilt_unrun_target_candidate' and manifest['variant'] == expected_variant and manifest['expected_failure'] == FAILURES.get(name) and manifest['SDK_commit'] == SDK, 'Frozen recipe scope predates execution, exact variant')
    require(manifest['phase_scoped_mutation'] is (name in ('early-publish-phase', 'forget-resets-loan')) and manifest['canonical_module_contract']['normalized_lf_sha256'] == MODULE, 'Exact scoped source-mutation provenance')
    result = dict(originals)
    module = 'sources/repository/' + MAIN + 'native_tls_rx_reserve.c'
    patcher = 'sources/repository/tools/patch_cyd_tls_static_rx.py'
    require(sha(normalized(result[module])) == MODULE and b'user_data' not in result[module], 'Original final registry identity, no application userdata')
    edits = []
    def edit(path, before, after):
        result[path] = mutate_bytes(result[path], before, after)
        edits.append({'file': path, 'before': before, 'after': after})
    if name in ('skip-init', 'skip-free'):
        hook = name.removeprefix('skip-')
        old = '    yoradio_tls_static_rx_forget_configuration(conf);\\n'
        raw = result[patcher].decode()
        anchor = "b'void mbedtls_ssl_config_" + hook + '('
        first = raw.index(anchor)
        second = raw.index(anchor, first + len(anchor))
        location = raw.index(old, second)
        result[patcher] = (raw[:location] + raw[location:].replace(old, '    /* negative: omitted lifecycle forget */\\n', 1)).encode()
        edits.append({'file': patcher, 'hook': hook, 'kind': 'exact replacement-span lifecycle omission'})
    elif name == 'evict-full':
        old = 'if (empty != RX_CONFIGURATION_CAPACITY)\n        s_radio_configurations[empty] = identity;'
        edit(module, old, old + '\n    else s_radio_configurations[0] = identity;')
    elif name == 'forget-resets-loan':
        edit(module, '#include "tf_psa_crypto_common.h"', '#include "tf_psa_crypto_common.h"\nextern int tls_reserve_test_forget_phase(void);')
        old = '    if (!configuration) return;\n    const uintptr_t identity = (uintptr_t)configuration;\n    portENTER_CRITICAL_SAFE(&s_lock);'
        edit(module, old, old + '\n    if (tls_reserve_test_forget_phase() && s_state == RX_LOANED) s_state = RX_FREE;')
    elif name == 'skip-exclusive':
        edit(module, '== identity && s_state == RX_FREE)', '== identity)')
    elif name == 'early-publish-phase':
        edit(module, '#include "tf_psa_crypto_common.h"', '#include "tf_psa_crypto_common.h"\nextern int tls_reserve_test_erase_phase(void);')
        edit(module, 's_state = RX_RETURNING;', 's_state = tls_reserve_test_erase_phase() ? RX_FREE : RX_RETURNING;')
    elif name == 'ordinary-free-static':
        edit(module, 'if (pointer != s_rx) return false;', 'if (pointer != s_rx) return false;\n    mbedtls_free(pointer);\n    return true;')
    elif name == 'bypass-reclaim':
        edit(module, '#include "tf_psa_crypto_common.h"', '#include "tf_psa_crypto_common.h"\nextern void *__real_esp_mbedtls_mem_calloc(size_t,size_t);')
        edit(module, 'return mbedtls_calloc(count, bytes);', 'return __real_esp_mbedtls_mem_calloc(count, bytes);')
    require(manifest['exact_changes'] == edits, 'Only independently reconstructed exact declared mutations')
    require({p: sha(v) for p, v in result.items()} == manifest['frozen_sources'], 'Every actual compiled source equals original or declared mutation')
    return result
