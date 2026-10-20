"""Synthetic archive guards only; no live target campaign reads or test reruns."""
import argparse
import ast
import copy
import json
from pathlib import Path
import re

from archive_core import encode, hashfile, require
import evidence_rules as rules
from verify import path_key, exact_header_paths

HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--attempt', default='prep-check-01')
    args = p.parse_args()
    require(re.fullmatch('prep-check-[0-9]{2}', args.attempt), 'Fresh exact preparation check name')
    out = HERE / args.attempt
    require(not out.exists(), 'Fresh preparation check output')
    out.mkdir()
    checked = []
    def accept(name, fn):
        fn()
        checked.append({'name': name, 'passed': True})
    def reject(name, diagnostic, fn):
        try:
            fn()
        except ValueError as error:
            require(diagnostic in str(error), 'Wrong diagnostic for synthetic guard ' + name + ': ' + str(error))
            checked.append({'name': name, 'passed': True, 'expected_rejection': True, 'required_diagnostic': diagnostic, 'actual_diagnostic': str(error)})
            return
        raise ValueError('Synthetic archival guard accepted invalid input: ' + name)
    report = {'passed': False, 'scope': 'Synthetic archival checks, no live campaign/SDK input reads or external commands', 'checks': checked}
    try:
        files = {p.name: {'sha256': hashfile(p), 'bytes': p.stat().st_size} for p in HERE.iterdir() if p.is_file()}
        for path in HERE.glob('*.py'):
            ast.parse(path.read_bytes())
        accept('python_syntax_all_tools', lambda: require(len(list(HERE.glob('*.py'))) == 5, 'Self-contained5 Python tools'))
        receipt = {'kind': 'root_authoritative_runner_terminal', 'runner_session': 17556, 'runner_terminal_exit': 0, 'report_sha256': 'a' * 64}
        final = {'passed': True, 'full_target_matrix_complete': True, 'compile_only': False, 'all_current_inputs_match': True,
                 'status': 'runtime_qualified_selected_variants', 'variants': {n: {'passed': True} for n in rules.VARIANTS},
                 'production_integration': False, 'physical_benefit_claimed': False, 'network_or_device': False, 'candidate_normalized_lf_sha256': rules.MODULE}
        accept('synthetic_complete_terminal_shape', lambda: rules.terminal(final, receipt, 'a' * 64))
        changed = dict(receipt, runner_terminal_exit=1)
        reject('terminal_nonzero_even_when_report_passes', 'Explicit root-authoritative terminal0', lambda: rules.terminal(final, changed, 'a' * 64))
        reject('wrong_terminal_report_sha', 'Explicit root-authoritative terminal0', lambda: rules.terminal(final, receipt, 'b' * 64))
        changed = copy.deepcopy(final)
        changed['variants'].pop('skip-free')
        reject('partial_matrix_never_collectable', 'Exact12 final outcomes', lambda: rules.terminal(changed, receipt, 'a' * 64))
        changed2 = dict(final, compile_only=True)
        reject('compile_only_never_runtime', 'Final fully completed runtime report required', lambda: rules.terminal(changed2, receipt, 'a' * 64))
        negative = b'TLS_RX_TARGET_ENTRY registry_fixture=1\nTLS_RX_TARGET_FAILURE init_revokes_stale_identity\nTLS_RX_TARGET_CONTROLLED_STOP\n'
        outcome = {'exact_semantic_failure': 'init_revokes_stale_identity', 'phase_scoped_mutation': False}
        accept('synthetic_named_control_shape', lambda: rules.oracle('skip-init', negative, outcome))
        reject('named_control_followed_by_panic', 'Panic never passes', lambda: rules.oracle('skip-init', negative + b'abort() was called at PC 0x40000000\n', outcome))
        reject('named_control_followed_by_backtrace', 'Panic never passes', lambda: rules.oracle('skip-init', negative + b'Backtrace: synthetic\n', outcome))
        reject('duplicate_named_control', 'Exact negative-control marker/stop/uniqueness', lambda: rules.oracle('skip-init', negative + b'TLS_RX_TARGET_FAILURE init_revokes_stale_identity\n', outcome))
        reject('wrong_named_control', 'Exact negative-control marker/stop/uniqueness', lambda: rules.oracle('skip-init', negative.replace(b'init_revokes_stale_identity', b'wrong_predicate'), outcome))
        reject('control_accidentally_completes', 'Exact negative-control marker/stop/uniqueness', lambda: rules.oracle('skip-init', negative + b'TLS_RX_TARGET_COMPLETE unexpected\n', outcome))
        disabled_result = {'reserve_enabled': False, 'reclaim_enabled': True, 'public_setup_reset_free_cycles': 16,
                           'original_sdk_ssl_source_compiled': True, 'reserve_module_static_slot_and_rx_wraps_absent': True, 'ordinary_callback_and_dispatcher': True}
        cfg = {'MBEDTLS_SSL_IN_CONTENT_LEN': 16384, 'MBEDTLS_SSL_OUT_CONTENT_LEN': 4096, 'MBEDTLS_SSL_MAX_FRAGMENT_LENGTH': True}
        # Arbitrary synthetic storage/heap numbers, never target measurements.
        capacity_line = b'TLS_RX_DISABLED_CAPACITY content=16384 storage=17000 allocated_min=17004 pre_handshake_payload=4096 setups=32\n'
        disabled_log = b'TLS_RX_DISABLED_ENTRY ordinary_sdk=1\n' + capacity_line + b'TLS_RX_DISABLED_COMPLETE reserve=0 reclaim=1 cycles=16 ordinary_sdk=1\n'
        accept('disabled_full_heap_separate_from_MFL_getter', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log, disabled_result, cfg))
        accept('disabled_storage_not_hardcoded', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log.replace(b'storage=17000 allocated_min=17004', b'storage=20000 allocated_min=20008'), disabled_result, cfg))
        no_mfl = dict(cfg, MBEDTLS_SSL_MAX_FRAGMENT_LENGTH=False)
        accept('disabled_without_MFL_getter_uses_full_content', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log.replace(b'pre_handshake_payload=4096', b'pre_handshake_payload=16384'), disabled_result, no_mfl))
        reject('disabled_capacity_marker_missing', 'Exactly one disabled capacity marker required', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log.replace(capacity_line, b''), disabled_result, cfg))
        reject('disabled_capacity_marker_duplicate', 'Exactly one disabled capacity marker required', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log + capacity_line, disabled_result, cfg))
        reject('disabled_short_content_rejected', 'Disabled full RX storage/all32 allocations must be retained', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log.replace(b'content=16384', b'content=4096'), disabled_result, cfg))
        reject('disabled_short_storage_rejected', 'Disabled full RX storage/all32 allocations must be retained', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log.replace(b'storage=17000', b'storage=16383'), disabled_result, cfg))
        reject('disabled_insufficient_actual_heap_rejected', 'Disabled full RX storage/all32 allocations must be retained', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log.replace(b'allocated_min=17004', b'allocated_min=16999'), disabled_result, cfg))
        reject('disabled_not_all32_setups_rejected', 'Disabled full RX storage/all32 allocations must be retained', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log.replace(b'setups=32', b'setups=31'), disabled_result, cfg))
        reject('disabled_full_content_is_wrong_MFL_getter', 'Disabled pre-handshake getter must match actual pinned MFL profile', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log.replace(b'pre_handshake_payload=4096', b'pre_handshake_payload=16384'), disabled_result, cfg))
        reject('disabled_small_getter_without_MFL_rejected', 'Disabled pre-handshake getter must match actual pinned MFL profile', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log, disabled_result, no_mfl))
        reject('disabled_actual_config_required', 'Actual disabled configuration required', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log, disabled_result))
        reject('disabled_valid_capacity_plus_panic_rejected', 'Panic never passes', lambda: rules.oracle('reserve-off-reclaim-on', disabled_log + b'abort()\n', disabled_result, cfg))
        old_report = {'passed': False, 'variants': {n: {'passed': True} for n in rules.VARIANTS[:10]},
                      'commands': [{'label': n + '-qemu', 'terminal_exit': 0, 'timed_out': False} for n in rules.VARIANTS[:11]]}
        old_log = b'TLS_RX_DISABLED_ENTRY ordinary_sdk=1\nTLS_RX_TARGET_FAILURE disabled_original_full_record_payload\nTLS_RX_TARGET_CONTROLLED_STOP\n'
        accept('bounded_old_nonpass_shape_only', lambda: require(rules.historical_nonpass(old_report, old_log)['full_gate_passed'] is False, 'Historical nonpass must remain false'))
        reject('old_nonpass_cannot_be_relabelled_pass', 'Historical rxt01 remains10 reported accepted outcomes and overall nonpass', lambda: rules.historical_nonpass(dict(old_report, passed=True), old_log))
        accept('uniform_line_ending_relation', lambda: require(rules.normalized(b'a\nb\n') == rules.normalized(b'a\r\nb\r\n'), 'LF/CRLF relationship'))
        accept('windows_parent_components_same_source', lambda: require(path_key('C:/Work/fixture/compat/tls/../../module.c') == path_key('c:\\work\\fixture\\module.c'), 'Lexical parent-component identity'))
        accept('windows_mixed_slashes_case_dot_same_source', lambda: require(path_key('C:\\WORK/mixed\\./tree/../source.C') == path_key('c:/work/mixed/source.c'), 'Mixed Windows slash/case identity'))
        accept('windows_same_basename_wrong_directory_unequal', lambda: require(path_key('C:/Work/a/module.c') != path_key('c:\\work\\b\\module.c'), 'Different directories remain different'))
        accept('windows_parent_escape_wrong_directory_unequal', lambda: require(path_key('C:/Work/fixture/../../module.c') != path_key('C:/Work/fixture/module.c'), 'Parent traversal cannot alias different directory'))
        accept('windows_distinct_drives_unequal', lambda: require(path_key('C:/Work/module.c') != path_key('D:/Work/module.c'), 'Drive identity retained'))
        reject('mixed_raw_source_line_endings', 'Uniform LF/CRLF required', lambda: rules.normalized(b'a\nb\r\n'))
        accept('exact200_command_labels', lambda: require(len(rules.command_labels()) == 200, '12freeze+2SDKbefore+10enabled16+2disabled13'))
        # First accept a COMPLETE command cohort. Each negative changes only one
        # condition, so removing its guard cannot pass via missing argv/log data.
        logs, command_rows = {}, []
        for label in sorted(rules.command_labels()):
            raw = (rules.SDK + '\n').encode() if label.startswith('sdk-head-') else (b'' if label.startswith('sdk-state-') else b'ARCHIVE_SYNTHETIC_COMMAND\n')
            argv = ['synthetic-tool']
            for name in rules.VARIANTS:
                reserve, reclaim = rules.options(name)
                if label == name + '-build':
                    argv = ['synthetic-pwsh', '-File', 'sdk-build.ps1'] + ([] if reclaim else ['-DisableReclaim']) + ([] if reserve else ['-DisableReserve'])
                if label == name + '-qemu':
                    argv = ['synthetic-qemu', '-M', 'esp32', '-smp', '2', '-nic', 'none', '-snapshot', '-no-reboot']
            logs[label + '.log'] = raw
            command_rows.append({'label': label, 'argv': argv, 'terminal_exit': 0, 'timed_out': False, 'log_sha256': rules.sha(raw)})
        complete = {'commands': command_rows}
        accept('complete_valid200_synthetic_commands', lambda: require(len(rules.commands(complete, logs.__getitem__)) == 200, 'All synthetic commands accepted'))
        timed = copy.deepcopy(complete)
        timed['commands'][0]['timed_out'] = True
        reject('timeout_never_control_pass', 'Original command terminal/log identity; timeout/failure rejected', lambda: rules.commands(timed, logs.__getitem__))
        nonzero = copy.deepcopy(complete)
        nonzero['commands'][0]['terminal_exit'] = 1
        reject('nonzero_command_never_control_pass', 'Original command terminal/log identity; timeout/failure rejected', lambda: rules.commands(nonzero, logs.__getitem__))
        corrupt_logs = dict(logs)
        corrupt_logs[command_rows[0]['label'] + '.log'] += b'changed\n'
        reject('command_raw_log_hash_mismatch', 'Original command terminal/log identity; timeout/failure rejected', lambda: rules.commands(complete, corrupt_logs.__getitem__))
        wrong_flags = copy.deepcopy(complete)
        next(r for r in wrong_flags['commands'] if r['label'] == 'canonical-build')['argv'].append('-DisableReserve')
        reject('wrong_actual_build_option', 'Actual independent build option flags', lambda: rules.commands(wrong_flags, logs.__getitem__))
        wrong_core = copy.deepcopy(complete)
        argv = next(r for r in wrong_core['commands'] if r['label'] == 'canonical-qemu')['argv']
        argv[argv.index('-smp') + 1] = '1'
        reject('wrong_actual_qemu_core_count', 'Actual isolated two-core no-NIC QEMU invocation', lambda: rules.commands(wrong_core, logs.__getitem__))
        sdk = 'C:/SDK'
        campaign = 'C:/Repo/.build/rxt02/campaigns/canonical'
        sdk_headers = ['components/mbedtls/mbedtls/library/ssl_misc.h', 'components/mbedtls/mbedtls/tf-psa-crypto/core/tf_psa_crypto_common.h',
                       'components/mbedtls/mbedtls/include/mbedtls/ssl.h', 'components/mbedtls/mbedtls/tf-psa-crypto/include/mbedtls/platform.h',
                       'components/freertos/FreeRTOS-Kernel/portable/xtensa/include/freertos/portmacro.h']
        parent = {sdk + '/' + rules.SSL_TLS: {'sha256': '0' * 64}, **{sdk + '/' + p: {'sha256': '1' * 64} for p in sdk_headers}}
        native = 'sources/repository/' + rules.MAIN + 'native_tls_rx_reserve.h'
        frozen = {native: '2' * 64}
        closure = {sdk + '/' + p: '1' * 64 for p in sdk_headers}
        closure.update({campaign + '/' + native: '2' * 64, campaign + '/working-build/config/sdkconfig.h': '3' * 64,
                        sdk + '/components/esp_timer/include/esp_timer.h': '4' * 64})
        accept('exact_guarded_variant_build_headers_valid', lambda: require(len(exact_header_paths(parent, frozen, campaign, closure, '3' * 64, True)) == 8, 'Eight exact intended headers'))
        wrongdir = dict(closure)
        wrongdir['C:/Shadow/ssl_misc.h'] = wrongdir.pop(sdk + '/' + sdk_headers[0])
        reject('wrongdir_samebasename_cannot_satisfy_header', 'Expected one exact compiled header path:', lambda: exact_header_paths(parent, frozen, campaign, wrongdir, '3' * 64, True))
        shadow = dict(closure)
        shadow[sdk + '/' + sdk_headers[0]] = 'f' * 64
        shadow['C:/Shadow/ssl_misc.h'] = '1' * 64
        reject('shadow_good_hash_cannot_replace_wrong_intended_header', 'Compiled guarded/frozen header hash mismatch:', lambda: exact_header_paths(parent, frozen, campaign, shadow, '3' * 64, True))
        wrong_native = dict(closure)
        wrong_native['C:/Repo/' + rules.MAIN + 'native_tls_rx_reserve.h'] = wrong_native.pop(campaign + '/' + native)
        reject('canonical_header_cannot_replace_variant_header', 'Expected one exact compiled header path:', lambda: exact_header_paths(parent, frozen, campaign, wrong_native, '3' * 64, True))
        wrong_config = dict(closure)
        wrong_config[campaign + '/other-build/config/sdkconfig.h'] = wrong_config.pop(campaign + '/working-build/config/sdkconfig.h')
        reject('other_build_sdkconfig_cannot_satisfy_current_build', 'Expected one exact compiled header path:', lambda: exact_header_paths(parent, frozen, campaign, wrong_config, '3' * 64, True))
        wrong_timer = dict(closure)
        wrong_timer['C:/Shadow/esp_timer.h'] = wrong_timer.pop(sdk + '/components/esp_timer/include/esp_timer.h')
        reject('shadow_timer_cannot_replace_intended_sdk_timer', 'Expected one exact compiled header path: components/esp_timer/include/esp_timer.h', lambda: exact_header_paths(parent, frozen, campaign, wrong_timer, '3' * 64, True))
        require(all(hashfile(HERE / p) == row['sha256'] for p, row in files.items()), 'Preparation tooling unchanged')
        report.update(passed=True, source_files=files, check_count=len(checked), target_campaign_read=False, archive_written=False)
    except BaseException as error:
        report['error'] = type(error).__name__ + ': ' + str(error)
        (out / 'report.json').write_bytes(encode(report))
        raise
    (out / 'report.json').write_bytes(encode(report))
    print(encode(report).decode())


if __name__ == '__main__':
    main()
