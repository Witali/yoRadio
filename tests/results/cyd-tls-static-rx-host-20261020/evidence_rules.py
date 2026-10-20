"""Pure byte/oracle checks for existing host evidence; never execute archived code."""
import ast
import hashlib
import json
import re


MODULE = '17e98a29cadd0387d9db725d50c12514847426cd9cfa607abf5224884fe17555'
GUARDS = '81fc22bbd240f71cb664ab08490f4e79ae805b066f0d61dbe24299af47ab49bb'
SDK_SOURCE = '1beac5da2dd0f99f626c81651e9cecb921eb9725a9f17624851802b8c6259ddc'
UNIT_SHA = '9137bdd08bceaf8bb7efcccbc9efa26e7a54457e0f654a9e68c9d96f44c51205'
CONFIG_SHA = 'f0a5ea8dc76a50e249b02c2815db4a963fa2c7577e6376ff4b6f94fe74d46316'
SERVICE_SHA = 'c53e24335b40df3c93122da1f20b949373fe71cf1fbf78aeb8e954c7c7101897'
PREP_SHA = '8690b77ea44e23ab71ad30190ef9cc5764080f5609009adac4519582f5c70606'
MAIN = 'idf/esp32-cyd2usb-native/main/'
FIXTURE = 'tests/native/cyd_tls_static_rx/'
SSL_TLS = 'components/mbedtls/mbedtls/library/ssl_tls.c'
SSL_H = 'components/mbedtls/mbedtls/include/mbedtls/ssl.h'
MISC = 'components/mbedtls/mbedtls/library/ssl_misc.h'
ZEROIZE = 'components/mbedtls/mbedtls/tf-psa-crypto/platform/platform_util.c'
ANCHORS = [b'static int ssl_handshake_init(', b'void mbedtls_ssl_init(', b'int mbedtls_ssl_setup(',
           b'void mbedtls_ssl_session_reset_msg_layer(', b'void mbedtls_ssl_free(',
           b'void mbedtls_ssl_config_init(', b'void mbedtls_ssl_config_free(']
USERDATA = [b'static inline void mbedtls_ssl_conf_set_user_data_p(',
            b'static inline void *mbedtls_ssl_conf_get_user_data_p(',
            b'static inline void mbedtls_ssl_conf_set_user_data_n(',
            b'static inline uintptr_t mbedtls_ssl_conf_get_user_data_n(']
MACROS = ['MBEDTLS_SSL_PAYLOAD_OVERHEAD', 'MBEDTLS_SSL_IN_PAYLOAD_LEN', 'MBEDTLS_SSL_OUT_PAYLOAD_LEN',
          'MBEDTLS_SSL_HEADER_LEN', 'MBEDTLS_SSL_IN_BUFFER_LEN', 'MBEDTLS_SSL_OUT_BUFFER_LEN']
POSITIVES = ('userdata', 'lifetime', 'registry_full', 'attach_failure', 'rollback', 'fallback', 'concurrent', 'stale_storage')
UNIT_CONTROLS = {
    'skip-init': ('lifetime', 'init_revokes_stale_identity'),
    'skip-free': ('lifetime', 'free_revokes_stale_identity'),
    'evict-full': ('registry_full', 'full_registry_does_not_evict'),
    'forget-resets-loan': ('lifetime', 'config_free_keeps_exclusive_loan'),
    'task-only-init': ('lifetime', 'task_critical_not_isr'),
    'skip-exclusive': ('concurrent', 'parallel_shared_or_distinct_exactly_one_loan'),
    'early-publish-phase': ('concurrent', 'no_reloan_during_erase_after_config_reuse'),
    'ordinary-free-static': ('userdata', 'reserved_pointer_never_sdk_heap_free'),
    'bypass-reclaim': ('fallback', 'busy_slot_reclaim_retry_preserved')}
FLAGS = ('YORADIO_TLS_STATIC_RX_RESERVE', 'IDF_TARGET_ESP32', 'ESP_TLS_USING_MBEDTLS', 'MBEDTLS_INTERNAL_MEM_ALLOC', 'MBEDTLS_CERTIFICATE_BUNDLE')
INVALIDS = [v + '-zero' for v in FLAGS] + [v + '-absent' for v in FLAGS] + ['dynamic', 'custom', 'variable', 'version']
NEW_CASES = ['tls_binding', 'tls_plain', 'tls_occupied', 'tls_numeric', 'tls_attach_error', 'tls_nested', 'tls_init_error',
             'tls_open_before_error', 'tls_open_after_error', 'tls_setup_error', 'tls_headers_error', 'tls_redirect_error',
             'tls_redirect_https', 'tls_redirect_plain', 'tls_redirect_to_https', 'tls_reopen', 'tls_cancel_open']
OLD_CASES = ['idle', 'pause_publish', 'resume', 'stop_cancels', 'end_no_resume', 'end_busy', 'state_lock', 'control_lock',
             'queue_failure', 'wide_epoch', 'timeout_read', 'timeout_open', 'timeout_headers', 'timeout_close', 'timeout_cleanup',
             'late_encoded', 'late_pcm', 'output_write', 'output_disable', 'control_reading', 'staging', 'back_to_back',
             'pause_failure', 'resume_queue_failure', 'empty_receive_epoch', 'stopped_no_resume', 'pending_resume']
SERVICE_CONTROLS = {'wrong-radio-callback': 'actual_radio_callback_selection', 'omitted-radio-registration': 'live_radio_loan_matches_transport'}
CONFIG_CASES = ['canonical', 'off', 'forced-zero', 'early', 'target', 'target-symbol-zero', 'major', 'minor', 'patch',
                'malformed-major', 'external', 'custom', 'dynamic', 'variable', 'tls-zero', 'bundle-zero', 'short-content',
                'serialize', 'gmt', 'missing-target', 'source-absent', 'source-duplicate', 'missing-module', 'missing-header',
                'missing-patcher', 'missing-guards'] + ['guard-' + str(i) for i in range(19)]


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def normalized(raw):
    value = raw.replace(b'\r\n', b'\n')
    require(raw == value or raw == value.replace(b'\n', b'\r\n'), 'Only uniform LF/CRLF is accepted')
    return value


def function(source, anchor):
    start = source.index(anchor)
    opening = source.index(b'{', start)
    lexical = re.sub(rb'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'',
                     lambda m: b' ' * len(m[0]), source, flags=re.S)
    depth = 0
    for i in range(opening, len(source)):
        if lexical[i] == 123:
            depth += 1
        elif lexical[i] == 125:
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
    raise ValueError('Unterminated SDK function')


def macro(source, name):
    lines = source.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if re.match(rb'#define\s+' + name.encode() + rb'(?:\s|$)', line):
            result = line
            while lines[i].rstrip().endswith(b'\\'):
                i += 1
                result += lines[i]
            return result
    raise ValueError('SDK capacity macro absent: ' + name)


def patch(raw, patcher):
    """Decode literals, then independently apply all six exact replacements."""
    values = {}
    for node in ast.parse(patcher.decode()).body:
        if isinstance(node, ast.Assign):
            for name in node.targets:
                if isinstance(name, ast.Name) and name.id in ('SOURCE_SHA256', 'GUARDS_SHA256', 'REPLACEMENTS'):
                    values[name.id] = ast.literal_eval(node.value)
    require(values['SOURCE_SHA256'] == SDK_SOURCE and values['GUARDS_SHA256'] == GUARDS, 'Pinned patch source/guard identities')
    replacements = values['REPLACEMENTS']
    require(len(replacements) == 6 and all(isinstance(a, bytes) and isinstance(b, bytes) for a, b in replacements), 'Six exact byte replacements')
    source = normalized(raw)
    require(sha(source) == SDK_SOURCE, 'Pinned complete SDK ssl_tls.c')
    for original, replacement in replacements:
        require(source.count(original) == 1, 'Exactly one SDK lifetime anchor')
        source = source.replace(original, replacement, 1)
    require(b'yoradio_tls_static_rx_calloc(conf, 1, in_buf_len);' in source and
            source.count(b'yoradio_tls_static_rx_forget_configuration(conf);') == 2 and
            b'yoradio_tls_static_rx_free(ssl->in_buf);' in source and
            b'yoradio_tls_static_rx_zeroize_free(ssl->in_buf, in_buf_len);' in source, 'Paired allocator and config lifetime hooks')
    return source if raw == normalized(raw) else source.replace(b'\n', b'\r\n')


def input_bytes(report, read, suffix):
    matches = [row for key, row in report['inputs'].items() if key.replace('\\', '/').endswith('/' + suffix)]
    require(len(matches) == 1, 'Unique frozen input: ' + suffix)
    row = matches[0]
    raw = read(row['snapshot'])
    require(sha(raw) == row['sha256'], 'Frozen input identity: ' + suffix)
    return raw


def common(report, read):
    require(report['passed'] is True and not report.get('error'), 'Final successful report required')
    for key in ('target_build', 'sdk_build', 'qemu', 'hardware', 'physical_benefit'):
        require(report.get(key, False) is False, 'Host evidence cannot assert target/physical gate')
    module = input_bytes(report, read, MAIN + 'native_tls_rx_reserve.c')
    value = normalized(module)
    require(sha(value) == MODULE and b'user_data' not in value and b'mbedtls_ssl_conf_' not in value and
            b'static uintptr_t s_radio_configurations[RX_CONFIGURATION_CAPACITY];' in value, 'Canonical integer registry, no application userdata')
    require(report['module_contract']['sha256'] == sha(module) and report['module_contract']['normalized_lf_sha256'] == MODULE and
            report['module_contract']['userdata_api_used'] is False and report['module_contract']['integer_identity_keys'] is True, 'Raw and normalized module contract')
    guards_raw = input_bytes(report, read, MAIN + 'compat/tls_static_rx/sdk-source-guards.json')
    require(sha(guards_raw) == GUARDS, 'Current supporting guard JSON identity')
    guards = json.loads(guards_raw)
    require(len(guards) == 19, 'Nineteen complete supporting sources')
    for relative, expected in guards.items():
        raw = input_bytes(report, read, relative)
        require(sha(normalized(raw)) == expected['normalized_lf_sha256'], 'Complete SDK guard: ' + relative)
    for original, row in report['inputs'].items():
        raw = read(row['snapshot'])
        require(sha(raw) == row['sha256'] and ('bytes' not in row or len(raw) == row['bytes']), 'Every original source snapshot hash')
    return guards


def sdk_evidence(report, read, service=False):
    raw = input_bytes(report, read, SSL_TLS)
    overlay = patch(raw, input_bytes(report, read, 'tools/patch_cyd_tls_static_rx.py'))
    zero = function(input_bytes(report, read, ZEROIZE), b'void mbedtls_zeroize_and_free(')
    prefix = b'#include "platform.h"\n#include "native_tls_rx_reserve.h"\n'
    def spans(source):
        return prefix + b'\n\n'.join(function(source, a) for a in ANCHORS) + b'\n\n' + zero + b'\n'
    if service:
        require(read('sdk-on.c') == spans(overlay) and read('sdk-off.c') == spans(raw), 'Exact on/off SDK source spans')
        require(report['sdk_span_hashes'] == {n: {a.decode(): sha(function(s, a)) for a in ANCHORS}
                                             for n, s in [('on', overlay), ('off', raw)]}, 'Reported on/off span hashes')
    else:
        require(read('sdk-overlay.c') == overlay and read('sdk-spans.c') == spans(overlay), 'Whole generated overlay and extracted exact SDK spans')
        require(report['exact_sdk_spans'] == {a.decode(): sha(function(overlay, a)) for a in ANCHORS}, 'Reported seven exact span hashes')
    public = input_bytes(report, read, SSL_H)
    getters = b'\n'.join(function(public, a) for a in USERDATA) + b'\n'
    capacity = b'\n'.join(macro(input_bytes(report, read, MISC), name) for name in MACROS) + b'\n'
    require(read('stubs/public_user_data.h') == getters and read('stubs/capacity.h') == capacity, 'Exact pointer/numeric public accessors and capacity macros')
    return overlay


def clean_runtime(raw):
    text = raw.decode(errors='replace')
    require(not any(x in text for x in ['AddressSanitizer', 'LeakSanitizer', 'runtime error:', 'Assertion ', 'PANIC', 'abort()']), 'Runtime diagnostic is not an accepted oracle')
    return text


def commands(report, read):
    rows = report['commands']
    require(len({r['label'] for r in rows}) == len(rows), 'Command labels must be unique')
    for row in rows:
        require(isinstance(row['exit_status'], int) and row['exit_status'] >= 0, 'Timeout/signal is not an accepted command')
        require(sha(read(row['label'] + '.log')) == row['log_sha256'], 'Original raw command log')
    require(report['tools_before'] == report['tools_after'] and len(report['tools_before']) > 0, 'Original tools before/after identity')
    for label in ('tools-before', 'tools-after'):
        require(json.loads(read(label + '.log').decode().splitlines()[0]) == report['tools_before'], 'Raw original tool identity log')
    return {r['label']: r for r in rows}


def strict_build(command):
    flags = command['argv']
    require(all(x in flags for x in ['-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined', '-fno-sanitize-recover=all']), 'Strict ASan/UBSan build flags')


def replace_once(data, old, new):
    newline = b'\r\n' if b'\r\n' in data else b'\n'
    old = old.replace(b'\r\n', b'\n').replace(b'\n', newline)
    new = new.replace(b'\r\n', b'\n').replace(b'\n', newline)
    require(data.count(old) == 1, 'Exactly one declared host mutation anchor')
    return data.replace(old, new, 1)


def unit_compiled_copies(report, read):
    module = input_bytes(report, read, MAIN + 'native_tls_rx_reserve.c')
    sdk = read('sdk-spans.c')
    runner = input_bytes(report, read, 'tests/run-cyd-tls-static-rx-unit.py')
    found = [node.value for node in ast.walk(ast.parse(runner.decode())) if isinstance(node, ast.Assign) and
             any(isinstance(name, ast.Name) and name.id == 'controls' for name in node.targets)]
    require(len(found) == 1, 'Unique literal unit control recipe list')
    controls = ast.literal_eval(found[0])
    require(len(controls) == 9 and {row[0] for row in controls} == set(UNIT_CONTROLS), 'Nine exact literal generated unit controls')
    for name, edit, sdk_edit, case, predicate in [('canonical', None, None, None, None)] + controls:
        expected_module, expected_sdk = module, sdk
        if name != 'canonical':
            require((case, predicate) == UNIT_CONTROLS[name], 'Literal mutation predicate agrees reviewed oracle')
        if edit:
            expected_module = replace_once(module, *edit)
        if sdk_edit:
            require(sdk_edit in ('init', 'free'), 'Only reviewed SDK config hooks may be omitted')
            anchor = b'void mbedtls_ssl_config_' + sdk_edit.encode() + b'('
            body = function(sdk, anchor)
            changed = replace_once(body, b'    yoradio_tls_static_rx_forget_configuration(conf);', b'    /* negative: omitted lifecycle forget */')
            expected_sdk = replace_once(sdk, body, changed)
        require(read(name + '/module.c') == expected_module and read(name + '/sdk.c') == expected_sdk, 'Actual compiled unit module/SDK copies equal exact canonical or declared mutation: ' + name)
    for name in INVALIDS:
        require(read('reject-' + name + '/module.c') == module, 'Invalid compile uses exact canonical module')


def unit(report, read):
    common(report, read)
    sdk_evidence(report, read)
    unit_compiled_copies(report, read)
    require(set(report['positive_cases']) == set(POSITIVES) and set(report['controls']) == set(UNIT_CONTROLS) and set(report['compile_rejections']) == set(INVALIDS), 'Exact unit8/9/14 cohort')
    rows = commands(report, read)
    expected_labels = {'tools-before', 'tools-after', 'cpp-lifetime-build', 'canonical-build'}
    strict_build(rows['canonical-build'])
    require(rows['cpp-lifetime-build']['exit_status'] == 0, 'Actual separate C++ lifetime fixture build')
    for case in POSITIVES:
        for prefix in ('canonical-', 'restored-'):
            label = prefix + case
            expected_labels.add(label)
            text = clean_runtime(read(label + '.log'))
            require(rows[label]['exit_status'] == 0 and text.count('TLS_RX_HOST_COMPLETE case=' + case + ' ') == 1 and 'TLS_RX_HOST_FAILURE' not in text, 'Positive/restored unit oracle: ' + label)
            match = re.search(r'allocations=(\d+) releases=(\d+)\s*$', text)
            require(match and match[1] == match[2], 'Host ownership allocation/free balance')
            if prefix == 'canonical-':
                require(report['positive_cases'][case] == {'exit_status': 0, 'result': text.strip()}, 'Positive report matches raw log')
    for name, (case, predicate) in UNIT_CONTROLS.items():
        build, run = name + '-build', name + '-' + case
        expected_labels.update((build, run))
        strict_build(rows[build])
        text = clean_runtime(read(run + '.log'))
        require(rows[build]['exit_status'] == 0 and rows[run]['exit_status'] == 2 and text.splitlines()[-1] == 'TLS_RX_HOST_FAILURE ' + predicate and text.count('TLS_RX_HOST_FAILURE') == 1, 'Exact named unit control, no crash: ' + name)
        require(report['controls'][name] == {'case': case, 'exit_status': 2, 'expected_named_failure': predicate, 'phase_scoped': name == 'early-publish-phase'}, 'Exact unit control metadata')
    for name in INVALIDS:
        label = 'reject-' + name
        expected_labels.add(label)
        diagnostic = 'CYD RX reserve requires the audited ' + ('ESP-IDF6.0.2 declaration/layout profile' if name == 'version' else 'classic ESP32 static/internal profile')
        require(rows[label]['exit_status'] > 0 and diagnostic in read(label + '.log').decode() and report['compile_rejections'][name] == {'exit_status': rows[label]['exit_status'], 'exact_diagnostic': diagnostic}, 'Exact invalid compile diagnostic')
    require(set(rows) == expected_labels and len(rows) == 52, 'No missing/extra unit command')
    require(report['userdata_getter_setter_absent'] is True and report['host_pthreads_are_not_actual_core_proof'] is True, 'Unit host qualification boundaries')
    return {'positive_groups': 8, 'exact_controls': 9, 'invalid_compile_profiles': 14, 'restored_groups': 8, 'commands': 52}


def service(report, read, identity):
    common(report, read)
    sdk_evidence(report, read, service=True)
    require(report['quick'] is False and report['variant_count'] == 12 and report['positive_case_count'] == 536 and report['named_control_count'] == 2, 'Full host service12/536/2 terminal cohort')
    rows = commands(report, read)
    require(set(report['controls']) == set(SERVICE_CONTROLS), 'Exactly two real radio binding controls')
    labels = {'tools-before', 'tools-after'}
    tags = set()
    for reserve, reclaim in [(1, 1), (1, 0), (0, 1), (0, 0)]:
        config = normalized(read(f'config-r{reserve}-q{reclaim}/sdkconfig.h')).decode()
        require(re.search(r'^#define CONFIG_YORADIO_TLS_STATIC_RX_RESERVE ' + str(reserve) + '$', config, re.M) and ('#define CONFIG_YORADIO_TLS_INPUT_RECLAIM 1' in config) == bool(reclaim), 'Actual generated reserve/reclaim option pair')
        for backend in ['pdm', 'dac', 'legacy_dac']:
            tag = f'r{reserve}-q{reclaim}-{backend}'
            tags.add(tag)
            build = 'build-' + tag
            labels.add(build)
            strict_build(rows[build])
            require(rows[build]['exit_status'] == 0 and '-DCONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_' + backend.upper() + '=1' in rows[build]['argv'], 'Actual backend compile command')
            argv = rows[build]['argv']
            require(any(v.endswith('/native_tls_rx_reserve.c') for v in argv) == bool(reserve) and any(v.endswith('/native_input_reclaim.c') for v in argv) == bool(reclaim), 'Real per-option module inclusion')
            cases = NEW_CASES + OLD_CASES + ([] if backend == 'legacy_dac' else ['delete_failure'])
            require(set(report['variants'][tag]) == set(cases), 'Exact backend scenario set: ' + tag)
            for case in cases:
                label = tag + '-' + case
                labels.add(label)
                text = clean_runtime(read(label + '.log'))
                require(rows[label]['exit_status'] == 0 and text.count('PASS ' + case + ';') == 1 and 'TLS_SERVICE_FAILURE' not in text and report['variants'][tag][case] == {'exit_status': 0, 'result': text.strip()}, 'Exact service scenario oracle: ' + label)
    require(set(report['variants']) == tags, 'Exactly reserve/reclaim2x2 by three actual host backends')
    for name, predicate in SERVICE_CONTROLS.items():
        build, label = 'build-control-' + name, 'control-' + name
        labels.update((build, label))
        strict_build(rows[build])
        text = clean_runtime(read(label + '.log'))
        require(rows[build]['exit_status'] == 0 and rows[label]['exit_status'] == 2 and re.findall(r'^TLS_SERVICE_FAILURE (.+)$', text, re.M) == [predicate], 'Named service control without crash')
        control = report['controls'][name]
        require(control['exit_status'] == 2 and control['expected_named_failure'] == predicate, 'Service control metadata')
        mutation = control['mutation']
        raw = read(mutation['path'])
        require(sha(raw) == mutation['original_sha256'] and raw.decode().count(mutation['old']) == 1 and sha(raw.decode().replace(mutation['old'], mutation['new'], 1).encode()) == mutation['mutated_sha256'], 'Exact semantic mutation and restored source bytes')
    require(set(rows) == labels and len(rows) == 554, 'Exact service commands')
    for relative, digest in report['generated'].items():
        require(identity(relative) == digest, 'Every generated service artifact identity (omitted binaries remain hash-only): ' + relative)
    source = input_bytes(report, read, MAIN + 'board_config.h').decode()
    names = ('BOARD_TASK_STACK_RADIO_STREAM', 'BOARD_TASK_STACK_AUDIO_DECODER', 'BOARD_TASK_STACK_AUDIO_OUTPUT')
    lines = [re.search(r'^#define ' + n + r'\s+\d+', source, re.M)[0] for n in names]
    profile = ('#pragma once\n' + '\n'.join(lines) + '\n').encode()
    require(normalized(read('board_task_profile.h')) == profile and report['board_stack_extraction']['exact_macro_lines'] == lines and report['board_stack_extraction']['header_sha256'] == sha(profile), 'Actual canonical board task macro extraction (reported text hash is LF, raw bytes remain independently bound)')
    for source_name, output, keep in [('audio_service.c', 'audio.inc', ('stream_encoded_router.h', 'stream_start.h', 'input_prefill.h', 'native_tls_rx_reserve.h', 'native_input_reclaim.h')), ('native_audio_output.c', 'production.inc', ()), ('native_state.c', 'state.inc', ())]:
        raw = input_bytes(report, read, MAIN + source_name).decode().replace('\r\n', '\n')
        stripped = re.sub(r'^#include[^\n]*\n', lambda m: m[0] if any('"' + n + '"' in m[0] for n in keep) else '', raw, flags=re.M)
        require(normalized(read(output)) == stripped.encode(), 'Whole source with only platform includes replaced: ' + source_name)
    return {'variants': 12, 'positive_scenarios': 536, 'exact_controls': 2, 'commands': 554}


def config(report, read):
    guards = common(report, read)
    require(report['compiler'] is False and report['configure_case_count'] == 45 and set(report['cases']) == set(CONFIG_CASES), 'Exactly45 source-only configure cases')
    overlay = patch(input_bytes(report, read, SSL_TLS), input_bytes(report, read, 'tools/patch_cyd_tls_static_rx.py'))
    copied_sources = {
        'helper': (MAIN + 'compat/tls_static_rx/enable.cmake', MAIN + 'compat/tls_static_rx/enable.cmake'),
        'module': (MAIN + 'native_tls_rx_reserve.c', MAIN + 'native_tls_rx_reserve.c'),
        'header': (MAIN + 'native_tls_rx_reserve.h', MAIN + 'native_tls_rx_reserve.h'),
        'patcher': ('tools/patch_cyd_tls_static_rx.py', 'tools/patch_cyd_tls_static_rx.py'),
        'guards': (MAIN + 'compat/tls_static_rx/sdk-source-guards.json', MAIN + 'compat/tls_static_rx/sdk-source-guards.json')}
    def present(relative):
        try:
            read(relative)
            return True
        except (FileNotFoundError, KeyError):
            return False
    for name, row in report['cases'].items():
        require(row['passed'] is True and sha(read(name + '/configure.log')) == row['log_sha256'], 'Raw configure log identity')
        text = read(name + '/configure.log').decode(errors='replace')
        argv = row['argv']
        require('-G' in argv and argv[argv.index('-G') + 1] == 'Ninja' and '-S' in argv and '-B' in argv, 'Configure-only actual CMake invocation')
        project = read(name + '/project/CMakeLists.txt').decode()
        require('project(CanonicalReserveGate NONE)' in project and 'native_enable_tls_static_rx_reserve()' in project, 'Real helper with no compiler language')
        inactive = name in ('off', 'forced-zero', 'early')
        for kind, (relative, suffix) in copied_sources.items():
            if inactive and kind != 'helper' or name == 'missing-' + kind:
                require(not present(name + '/repository/' + relative), 'Only declared missing case inputs may be absent/present')
                continue
            require(read(name + '/repository/' + relative) == input_bytes(report, read, suffix), 'Per-case helper/module/header/patcher/guard copy is canonical: ' + name + '/' + kind)
        if not inactive:
            mutated = list(guards)[int(name.split('-')[1])] if name.startswith('guard-') else None
            for relative in guards:
                expected_sdk = input_bytes(report, read, relative) + (b'\n/* mutation guard */\n' if relative == mutated else b'')
                require(read(name + '/sdk/' + relative) == expected_sdk, 'Every per-case SDK file is canonical except exact declared guard mutation: ' + name + '/' + relative)
        if name == 'canonical' or inactive:
            require(row['exit_status'] == 0, 'Positive configure terminal')
            capture = read(name + '/build/capture.txt').decode().splitlines()
            require(capture == row['exact_capture'], 'Actual target capture equals original report')
            base = argv[argv.index('-B') + 1].replace('\\', '/').rsplit('/', 1)[0]
            helper = base + '/repository/' + MAIN + 'compat/tls_static_rx/enable.cmake'
            source = base + '/sdk/' + SSL_TLS
            expected = ['main_sources-NOTFOUND' if inactive else helper.rsplit('/', 1)[0] + '/../../native_tls_rx_reserve.c', 'keep-main',
                        (source if inactive else base + '/build/native-tls-static-rx/ssl_tls.c') + ';' + base + '/project/keep.c', 'keep-sdk', '|']
            require(capture[:5] == expected, 'Exact source substitution and retained link options, no compiler')
            dependencies = capture[5].split(';') if len(capture) > 5 and capture[5] else []
            if inactive:
                require(not dependencies and 'inactive_access_forbidden' in project and 'nonexistent-python' in project, 'Off/early accesses no SDK or Python inputs')
                require(not present(name + '/build/native-tls-static-rx/ssl_tls.c') and all(not present(name + '/sdk/' + relative) for relative in guards), 'Inactive cases have no SDK copy/overlay')
            else:
                expected_dependencies = [source, base + '/repository/tools/patch_cyd_tls_static_rx.py', helper.rsplit('/', 1)[0] + '/sdk-source-guards.json'] + [base + '/sdk/' + relative for relative in sorted(guards)]
                require(dependencies == expected_dependencies and read(name + '/build/native-tls-static-rx/ssl_tls.c') == overlay and row['overlay_sha256'] == sha(overlay), 'Byte-exact generated SDK overlay and all19 configure dependencies')
        else:
            if name.startswith('guard-'):
                diagnostic = 'CYD static RX overlay rejected SDK'
            elif name.startswith('source-'):
                diagnostic = 'Expected exactly one audited static RX source'
            elif name == 'missing-header':
                diagnostic = 'Missing canonical static RX reserve header'
            elif name.startswith('missing-') and name != 'missing-target':
                diagnostic = 'Missing canonical static RX reserve inputs'
            elif name == 'missing-target':
                diagnostic = 'CYD static RX reserve requires registered canonical targets'
            elif name in ('target', 'target-symbol-zero', 'major', 'minor', 'patch', 'malformed-major'):
                diagnostic = 'CYD static RX reserve requires exact ESP32 IDF6.0.2'
            else:
                diagnostic = 'CYD static RX reserve rejects unsupported allocator/buffer/config lifetime'
            require(isinstance(row['exit_status'], int) and row['exit_status'] > 0 and row['exact_rejection'] == diagnostic and diagnostic in text, 'Exact configure rejection category, not timeout')
        if name.startswith('guard-'):
            relative = list(guards)[int(name.split('-')[1])]
            require(read(name + '/sdk/' + relative) == input_bytes(report, read, relative) + b'\n/* mutation guard */\n', 'One named supporting-source mutation')
    return {'configure_only_cases': 45, 'supporting_guard_mutations': 19, 'sdk_build': False}
