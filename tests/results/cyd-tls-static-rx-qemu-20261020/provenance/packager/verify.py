"""Standalone stdlib-only integrity/oracle replay. Never execute archived code/tools."""
import gzip
import hashlib
import json
import ntpath
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import evidence_rules as rules


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def path_key(value):
    # Match Windows lexical comparison on any offline host. Raw evidence stays
    # byte-exact; no filesystem access or symlink-resolution claim is made.
    return ntpath.normcase(ntpath.normpath(value)).replace('\\', '/')


def exact_header_paths(parent_inputs, frozen_sources, campaign, closure, sdkconfig_sha, reserve):
    """Exact paths/identities, never satisfy a requirement by basename alone.

    Other SDK headers may legitimately share a basename. They cannot substitute
    for a missing or hash-mismatched intended header below.
    """
    parents = {path_key(p): row['sha256'] for p, row in parent_inputs.items()}
    closed = {path_key(p): digest for p, digest in closure.items()}
    require(len(parents) == len(parent_inputs) and len(closed) == len(closure), 'Unique lexical source/dependency paths')
    ssl_sources = [p for p in parents if p.endswith('/' + rules.SSL_TLS)]
    require(len(ssl_sources) == 1, 'One exact parent SDK source root')
    sdk = ssl_sources[0][:-len('/' + rules.SSL_TLS)]
    relative_headers = [
        'components/mbedtls/mbedtls/library/ssl_misc.h',
        'components/mbedtls/mbedtls/tf-psa-crypto/core/tf_psa_crypto_common.h',
        'components/mbedtls/mbedtls/include/mbedtls/ssl.h',
        'components/mbedtls/mbedtls/tf-psa-crypto/include/mbedtls/platform.h']
    if reserve:
        relative_headers.append('components/freertos/FreeRTOS-Kernel/portable/xtensa/include/freertos/portmacro.h')
    expected = {}
    for relative in relative_headers:
        intended = path_key(sdk + '/' + relative)
        require(intended in parents, 'Exact guarded header absent from parent inputs: ' + relative)
        expected[intended] = parents[intended]
    if reserve:
        native = 'sources/repository/' + rules.MAIN + 'native_tls_rx_reserve.h'
        expected[path_key(campaign + '/' + native)] = frozen_sources[native]
        # esp_timer is not in the19 guards; bind its exact intended installed SDK
        # path to the retained actual compiled/current closure bytes instead.
        timer = path_key(sdk + '/components/esp_timer/include/esp_timer.h')
        require(timer in closed, 'Expected one exact compiled header path: components/esp_timer/include/esp_timer.h')
        expected[timer] = closed[timer]
    expected[path_key(campaign + '/working-build/config/sdkconfig.h')] = sdkconfig_sha
    for intended, digest in expected.items():
        require(intended in closed, 'Expected one exact compiled header path: ' + intended)
        require(closed[intended] == digest, 'Compiled guarded/frozen header hash mismatch: ' + intended)
    return expected


def main(payloads=None):
    root = Path(__file__).resolve().parent
    def local(relative):
        p = root / relative
        require(p.resolve().is_relative_to(root) and not p.is_symlink(), 'Archive path escape/symlink')
        return p
    def payload(relative):
        return payloads[relative] if payloads is not None else local(relative).read_bytes()
    def document(relative):
        return json.loads(payload(relative))
    manifest = document('manifest.json')
    names = [r['path'] for r in manifest['files']]
    actual = set(payloads) - {'manifest.json'} if payloads is not None else {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and p.relative_to(root).as_posix() != 'manifest.json'}
    require(len(names) == len(set(names)) and set(names) == actual, 'Exact unique manifest payload set')
    for row in manifest['files']:
        raw = payload(row['path'])
        require(len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'Manifest byte identity')
    require(payload('.gitattributes') == b'* -text\n** -text\n', 'Whole archive raw byte attributes')
    rows = document('path-map.json')['entries']
    cache = {}
    def raw(entry_id):
        row = rows[entry_id]
        require(row['id'] == entry_id and row['disposition'] == 'stored', 'Binary/tool bytes omitted; metadata cannot substitute for raw payload')
        if entry_id not in cache:
            encoded = payload(row['stored_path'])
            require(sha(encoded) == row['stored_sha256'] and len(encoded) == row['stored_bytes'] and row['encoding'] in ('raw', 'gzip'), 'Stored representation identity')
            value = gzip.decompress(encoded) if row['encoding'] == 'gzip' else encoded
            require(len(value) == row['bytes'] and sha(value) == row['sha256'] and not value.startswith((b'\x7fELF', b'MZ', b'!<arch>\n')), 'Original bytes, no stored binary executable/archive')
            if row['encoding'] == 'gzip':
                require(gzip.compress(value, compresslevel=9, mtime=0) == encoded, 'Deterministic gzip')
            cache[entry_id] = value
        return cache[entry_id]
    for i, row in enumerate(rows):
        require(row['id'] == i and row['roles'] and len(row['sha256']) == 64, 'Complete path map')
        if row['disposition'] == 'stored':
            raw(i)
        else:
            require(row['disposition'] == 'omitted' and row['reason'] and 'stored_path' not in row, 'Explicit omitted binary/tool identity')
    bindings = document('bindings.json')['bindings']
    for row in bindings:
        value = json.loads(raw(row['container_id']))
        for key in row['hash_tokens']:
            value = value[key]
        require(value == rows[row['target_id']]['sha256'], 'Original JSON hash-reference binding')
    index = document('index.json')
    report = json.loads(raw(index['final_report_id']))
    receipt = json.loads(raw(index['terminal_receipt_id']))
    require(sha(raw(index['final_report_id'])) == index['final_report_sha256'] and sha(raw(index['terminal_receipt_id'])) == index['terminal_receipt_sha256'], 'Final report and root terminal receipt raw pins')
    rules.terminal(report, receipt, index['final_report_sha256'])
    require(path_key(receipt['report_path']) == path_key(index['target_original_directory'] + '/report.json'), 'Authoritative receipt names exact campaign')
    files = index['files']
    read = lambda p: raw(files[p])
    commands = rules.commands(report, read)
    require(set(index['variants']) == set(rules.VARIANTS), 'All12 independent compiled/executed campaigns')
    def frozen_input(original):
        entry = report['inputs'][original]
        value = read(entry['snapshot'])
        require(sha(value) == entry['sha256'], 'Parent pre-execution frozen input')
        return value
    def input_suffix(suffix):
        matches = [p for p in report['inputs'] if path_key(p).endswith('/' + suffix.lower())]
        require(len(matches) == 1, 'Unique source/SDK input suffix')
        return frozen_input(matches[0])
    for original in report['inputs']:
        frozen_input(original)
    source = input_suffix(rules.MAIN + 'native_tls_rx_reserve.c')
    require(sha(source) == report['candidate_sha256'] and sha(rules.normalized(source)) == rules.MODULE and b'user_data' not in source, 'Exact raw and normalized final module')
    require(sha(input_suffix('tests/native/cyd_tls_static_rx/source_contract.py')) == report['executed_source_contract_sha256'], 'Actual executed source-contract identity')
    guarded_raw = input_suffix(rules.MAIN + 'compat/tls_static_rx/sdk-source-guards.json')
    require(sha(guarded_raw) == rules.GUARDS and len(json.loads(guarded_raw)) == 19, 'Complete exact nineteen-source SDK guards')
    for relative, expected in json.loads(guarded_raw).items():
        require(sha(rules.normalized(input_suffix(relative))) == expected['normalized_lf_sha256'], 'Actual raw SDK supporting-source closure')
    elf_metadata, flash_metadata = document('derived-elf-metadata.json'), document('derived-flash-metadata.json')
    for name in rules.VARIANTS:
        item = index['variants'][name]
        vm = item['files']
        get = lambda p: raw(vm[p])
        recipe = json.loads(raw(item['manifest_id']))
        bundle = json.loads(raw(item['bundle_id']))
        manifest_path = item['original_campaign'] + '/source-manifest.json'
        require(sha(raw(item['manifest_id'])) == next(v for p, v in report['frozen_campaign_manifests'].items() if path_key(p) == path_key(manifest_path)), 'Parent frozen manifest binding')
        originals = {r['snapshot']: frozen_input(p) for p, r in recipe['original_inputs'].items()}
        expected = rules.source_variant(name, recipe, originals)
        for p, value in expected.items():
            require(get(p) == value, 'Exact compiled source recipe; only declared mutation')
        require(bundle['candidate_only'] is True and bundle['sdk_commit'] == rules.SDK and bundle['frozen_sources'] == recipe['frozen_sources'] and bundle['tools'] == report['tools'], 'Actual execution source/tool/SDK identity')
        reserve, reclaim = rules.options(name)
        require(bundle['reserve_enabled'] is reserve and bundle['reclaim_enabled'] is reclaim, 'Actual execution matrix option identity')
        require(sha(raw(item['bundle_id'])) == report['variants'][name]['execution_bundle_sha256'], 'Original execution bundle hash')
        for relative, digest in bundle['artifacts_before_qemu'].items():
            require(rows[vm['execution/' + relative]]['sha256'] == digest, 'Pre-runtime artifact metadata closure (binary bytes may be omitted)')
        closure = bundle['compiled_header_closure']
        require(set(closure) == set(item['compiled_header_ids']), 'Complete actual compiled dependency closure')
        for original, digest in closure.items():
            require(rows[item['compiled_header_ids'][original]]['sha256'] == digest, 'Retained actual dependency input identity')
        captured = json.loads(get('execution/compiled-header-closure.json'))
        require(captured == {'captured_before_qemu': True, 'sha256': closure}, 'Actual pre-runtime closure receipt')
        intended_headers = exact_header_paths(report['inputs'], recipe['frozen_sources'], item['original_campaign'], closure,
                                              sha(get('working-build/config/sdkconfig.h')), reserve)
        for intended, digest in intended_headers.items():
            actual = next(p for p in closure if path_key(p) == intended)
            require(sha(raw(item['compiled_header_ids'][actual])) == digest, 'Raw exact intended header bytes match guarded/frozen/current identity')
        cfg = json.loads(get('working-build/config/sdkconfig.json'))
        require(cfg == bundle['configuration'] == json.loads(get('execution/artifacts/config/sdkconfig.json')), 'Actual compiled/executed complete config equality')
        rules.config(name, cfg)
        require(get('working-sdkconfig') == get('execution/artifacts/working-sdkconfig'), 'Actual SDK config source copy')
        header_keys = [p for p in closure if path_key(p) == path_key(item['original_campaign'] + '/working-build/config/sdkconfig.h')]
        require(len(header_keys) == 1 and raw(item['compiled_header_ids'][header_keys[0]]) == get('working-build/config/sdkconfig.h'), 'Compiled actual SDK configuration header')
        description = json.loads(get('working-build/project_description.json'))
        require(description == json.loads(get('execution/artifacts/project_description.json')) and description['target'] == 'esp32', 'Actual SDK project/target identity')
        require(path_key(description['c_compiler']) in {path_key(p) for p in report['tools']}, 'Actual compiler tool identity')
        compile_bytes = get('working-build/compile_commands.json')
        require(compile_bytes == get('execution/artifacts/compile_commands.json'), 'Original actual compilation command database')
        commands_all = json.loads(compile_bytes)
        selected = json.loads(get('execution/actual-module-sdk-commands.json'))
        candidate = path_key(item['original_campaign'] + '/sources/repository/' + rules.MAIN + 'native_tls_rx_reserve.c')
        overlay = path_key(item['original_campaign'] + '/working-build/native-tls-static-rx/ssl_tls.c')
        sdk_original = next(p for p in report['inputs'] if path_key(p).endswith('/' + rules.SSL_TLS))
        picked = [r for r in commands_all if path_key(r['file']) in (candidate, overlay, path_key(sdk_original))]
        require(picked == selected and len(selected) == (2 if reserve else 1) and {path_key(r['file']) for r in selected} == ({candidate, overlay} if reserve else {path_key(sdk_original)}), 'Exactly canonical module plus actual overlay, or original SDK only')
        require(sum(path_key(r['file']).endswith('/native_input_reclaim.c') for r in commands_all) == int(reclaim), 'Actual per-option reclaim source inclusion')
        ninja = rules.text(read(name + '-ninja-commands.log'))
        for symbol in rules.WRAPS:
            require(('--wrap=' + symbol in ninja) is reserve, 'Actual conditional reserve/diagnostic link wraps')
        require(('--wrap=esp_mbedtls_mem_calloc' in ninja) is reclaim and '--wrap=esp_mbedtls_mem_free' not in ninja, 'Actual calloc-only reclaim link pairing')
        if reserve:
            patched = rules.patch(input_suffix(rules.SSL_TLS), get('sources/repository/tools/patch_cyd_tls_static_rx.py'))
            require(get('working-build/native-tls-static-rx/ssl_tls.c') == patched, 'Actual compiled SDK overlay exact mutation recipe')
        else:
            require('working-build/native-tls-static-rx/ssl_tls.c' not in vm and all(not path_key(r['file']).endswith('/native_tls_rx_reserve.c') for r in commands_all), 'Disabled module/overlay source absence')
        defaults = (('CONFIG_YORADIO_TLS_INPUT_RECLAIM=n\n' if not reclaim else '') + ('CONFIG_YORADIO_TLS_STATIC_RX_RESERVE=n\n' if not reserve else '')).encode()
        require(rules.normalized(get('option-disabled.defaults')) == defaults if defaults else 'option-disabled.defaults' not in vm, 'Actual option-default overrides only')
        symbols = rules.nm(read(name + '-nm.log'))
        assemblies = {s: read(name + '-asm-' + s + '.log') for s in (rules.ENABLED_ASM if reserve else rules.ASM)}
        meta = elf_metadata[name]
        require(rows[meta['elf_id']]['disposition'] == 'omitted' and rows[meta['elf_id']]['sha256'] == bundle['elf_sha256'] and rows[meta['elf_id']]['bytes'] == meta['elf_bytes'] and meta['nm_id'] == files[name + '-nm.log'], 'Derived metadata bound to omitted ELF and retained nm')
        rules.elf_logs(name, symbols, assemblies, meta, bundle)
        flash = flash_metadata[name]
        require(flash['bytes'] == rows[flash['flash_id']]['bytes'] == 0x400000 and flash['flash_sha256'] == rows[flash['flash_id']]['sha256'] == bundle['flash_sha256'] and rows[flash['flash_id']]['disposition'] == 'omitted', 'Original omitted flash identity')
        recipe_flash = json.loads(get('working-build/flasher_args.json'))['flash_files']
        require({int(k, 0): v for k, v in recipe_flash.items()} == {r['offset']: r['relative_build_path'] for r in flash['components']}, 'Actual flasher component recipe')
        for component in flash['components']:
            row = rows[component['artifact_id']]
            require(row['disposition'] == 'omitted' and row['sha256'] == component['sha256'] and row['bytes'] == component['bytes'] and component['offset'] + component['bytes'] <= flash['bytes'], 'Derived original flash-component metadata; no offline binary reconstruction')
        rules.oracle(name, read(name + '-qemu.log'), report['variants'][name], cfg)
    status = index['status']
    require(status['isolated_target_12_variant_gate'] is True and all(v is False for k, v in status.items() if k != 'isolated_target_12_variant_gate'), 'Target-only scope, no production/physical/protocol/offline ELF claim')
    require(document('packaging-readback.json')['all_selected_inputs_unchanged_after'] is True, 'Original packaging after-readback assertion')
    history = index['historical_nonpass']
    old_report = json.loads(raw(history['report_id']))
    require(sha(raw(history['report_id'])) == rules.OLD_REPORT_SHA and sha(raw(history['rejected_log_id'])) == rules.OLD_LOG_SHA and sha(raw(history['root_receipt_id'])) == rules.OLD_RECEIPT_SHA, 'Exact bounded nonpass history raw pins')
    source_entry = old_report['inputs'][history['original_disabled_input_key']]
    require(sha(raw(history['original_disabled_id'])) == source_entry['sha256'] and source_entry['sha256'].startswith('567c8da4'), 'Complete original disabled snapshot hash from exact old report')
    require(history['summary'] == rules.historical_nonpass(old_report, raw(history['rejected_log_id'])) and history['other_old_references']['retained_or_requalified'] is False, 'Old parent remains nonpass; only bounded historical rejection is replayed')
    print(json.dumps({'passed': True, 'scope': 'Stored bytes and original12 isolated target outcomes; omitted ELF/binaries not independently reconstructed offline',
                      'manifest_sha256': sha(payload('manifest.json')), 'mapped_versions': len(rows), 'json_hash_bindings': len(bindings),
                      'explicit_omissions': sum(r['disposition'] == 'omitted' for r in rows), 'variants': list(rules.VARIANTS)}, indent=2))


if __name__ == '__main__':
    main()
