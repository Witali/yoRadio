"""Freeze a fresh isolated target campaign; does not configure/build or run it.

Root must review this new candidate/fixture before invoking sdk-build.ps1.
The earlier passing host/config campaigns and original prep remain immutable.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
VARIANTS = ('canonical','skip-init','skip-free','evict-full','forget-resets-loan','skip-exclusive','early-publish-phase','ordinary-free-static','bypass-reclaim')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--variant', choices=VARIANTS, default='canonical')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists() or not out.is_relative_to(ROOT / '.build') or out.is_relative_to(HERE):
        parser.error('Choose a fresh sibling ignored campaign directory')
    if any((parent / 'report.json').exists() for parent in out.parents):
        parser.error('Do not nest a campaign in another evidence directory')
    out.mkdir(parents=True)
    identities = {}
    main=ROOT/'idf/esp32-cyd2usb-native/main'
    sources=[*sorted((HERE/'project').rglob('*')),HERE/'sdk-build.ps1',HERE/'freeze-run.py']
    sources += [main/name for name in ('native_tls_rx_reserve.c','native_tls_rx_reserve.h','compat/tls_static_rx/enable.cmake','compat/tls_static_rx/sdk-source-guards.json','native_input_reclaim.c','native_input_reclaim.h','compat/input_reclaim/enable.cmake','Kconfig.projbuild')]
    sources += [ROOT/'tools/patch_cyd_tls_static_rx.py',HERE.parent/'source_contract.py']
    sources += [ROOT/'idf/components/native_stream'/name for name in ('adaptive_input.c','include/adaptive_input.h')]
    for source in sources:
        if not source.is_file():continue
        relative=source.relative_to(HERE) if source.is_relative_to(HERE) else Path('repository')/source.relative_to(ROOT)
        destination=out/'sources'/relative;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(source.read_bytes())
        identities[str(source)]={'sha256':sha(source),'snapshot':destination.relative_to(out).as_posix()}
    module=out/'sources/repository/idf/esp32-cyd2usb-native/main/native_tls_rx_reserve.c'
    patcher=out/'sources/repository/tools/patch_cyd_tls_static_rx.py'
    import importlib.util
    spec=importlib.util.spec_from_file_location('freeze_contract',HERE.parent/'source_contract.py');contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
    module_contract=contract.validate_module(module)
    edits = []
    def replace(path, original, replacement):
        data = path.read_bytes()
        newline = b'\r\n' if b'\r\n' in data else b'\n'
        old = original.encode().replace(b'\n', newline)
        new = replacement.encode().replace(b'\n', newline)
        assert data.count(old) == 1
        path.write_bytes(data.replace(old, new))
        edits.append({'file': path.relative_to(out).as_posix(), 'before': original, 'after': replacement})
    expected = None
    if args.variant in ('skip-init','skip-free'):
        name='init' if args.variant=='skip-init' else 'free'
        # Mutate only the exact selected hook replacement, retaining its SDK source guard.
        old="    yoradio_tls_static_rx_forget_configuration(conf);\\n"
        data=patcher.read_bytes().decode();anchor="b'void mbedtls_ssl_config_"+name+"("
        first=data.index(anchor);second=data.index(anchor,first+len(anchor))
        location=data.index(old,second);data=data[:location]+data[location:].replace(old,"    /* negative: omitted lifecycle forget */\\n",1)
        patcher.write_bytes(data.encode());edits.append({'file':patcher.relative_to(out).as_posix(),'hook':name,'kind':'exact replacement-span lifecycle omission'})
        expected='init_revokes_stale_identity' if name=='init' else 'free_revokes_stale_identity'
    elif args.variant=='evict-full':
        replace(module,'if (empty != RX_CONFIGURATION_CAPACITY)\n        s_radio_configurations[empty] = identity;','if (empty != RX_CONFIGURATION_CAPACITY)\n        s_radio_configurations[empty] = identity;\n    else s_radio_configurations[0] = identity;')
        expected='full_registry_does_not_evict'
    elif args.variant=='forget-resets-loan':
        replace(module,'#include "tf_psa_crypto_common.h"','#include "tf_psa_crypto_common.h"\nextern int tls_reserve_test_forget_phase(void);')
        replace(module,'    if (!configuration) return;\n    const uintptr_t identity = (uintptr_t)configuration;\n    portENTER_CRITICAL_SAFE(&s_lock);','    if (!configuration) return;\n    const uintptr_t identity = (uintptr_t)configuration;\n    portENTER_CRITICAL_SAFE(&s_lock);\n    if (tls_reserve_test_forget_phase() && s_state == RX_LOANED) s_state = RX_FREE;')
        expected='config_free_keeps_exclusive_loan'
    elif args.variant=='skip-exclusive':
        replace(module,'== identity && s_state == RX_FREE)','== identity)')
        expected='independent_context_rx_no_alias'
    elif args.variant=='early-publish-phase':
        replace(module,'#include "tf_psa_crypto_common.h"','#include "tf_psa_crypto_common.h"\nextern int tls_reserve_test_erase_phase(void);')
        replace(module,'s_state = RX_RETURNING;','s_state = tls_reserve_test_erase_phase() ? RX_FREE : RX_RETURNING;')
        expected='no_reloan_during_erase'
    elif args.variant=='ordinary-free-static':
        replace(module,'if (pointer != s_rx) return false;','if (pointer != s_rx) return false;\n    mbedtls_free(pointer);\n    return true;')
        expected='reserved_pointer_never_sdk_heap_free'
    elif args.variant=='bypass-reclaim':
        replace(module,'#include "tf_psa_crypto_common.h"','#include "tf_psa_crypto_common.h"\nextern void *__real_esp_mbedtls_mem_calloc(size_t,size_t);')
        replace(module,'return mbedtls_calloc(count, bytes);','return __real_esp_mbedtls_mem_calloc(count, bytes);')
        expected='busy_slot_reclaim_retry_preserved'
    generated = {path.relative_to(out).as_posix(): sha(path) for path in (out / 'sources').rglob('*') if path.is_file()}
    result = {'status': 'frozen_unbuilt_unrun_target_candidate', 'variant': args.variant,
              'expected_failure': expected, 'exact_changes': edits, 'original_inputs': identities,
              'frozen_sources': generated, 'SDK_commit': '7101770dc6db2667b3c477cc31365dd1acd6db4e',
              'scoped_injection_is_not_real_oom_proof': True, 'canonical_module_contract':module_contract,
              'early_publish_mutation_phase_scoped': args.variant == 'early-publish-phase',
              'forget_loan_mutation_phase_scoped': args.variant == 'forget-resets-loan',
              'phase_scoped_mutation': args.variant in ('early-publish-phase','forget-resets-loan')}
    (out / 'source-manifest.json').write_bytes((json.dumps(result, indent=2) + '\n').encode())
    assert all(sha(source) == record['sha256'] for source, record in identities.items())
    print(json.dumps({'frozen': True, 'unbuilt': True, 'variant': args.variant, 'output': str(out),
                      'manifest_sha256': sha(out / 'source-manifest.json')}))


if __name__ == '__main__':
    main()
