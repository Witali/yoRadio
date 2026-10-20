"""Canonical registry module identity; earlier pointer-marker evidence is superseded."""
import hashlib
import importlib.util
from pathlib import Path
MODULE_SHA256="17e98a29cadd0387d9db725d50c12514847426cd9cfa607abf5224884fe17555"
PRIOR_REGISTRY_SHA256="58cb83830fa825b912068087007440fba9f4205fb0c64abbe684696b3e53485a"
def validate_module(path):
    raw=Path(path).read_bytes();normalized=raw.replace(b"\r\n",b"\n")
    uniform=raw==normalized or raw==normalized.replace(b"\n",b"\r\n")
    assert uniform,"Mixed module line endings are not qualified"
    assert hashlib.sha256(normalized).hexdigest()==MODULE_SHA256,"Canonical registry source identity changed"
    assert b"mbedtls_ssl_conf_" not in normalized and b"user_data" not in normalized
    assert b"static uintptr_t s_radio_configurations[RX_CONFIGURATION_CAPACITY];" in normalized
    return {"sha256":hashlib.sha256(raw).hexdigest(),"normalized_lf_sha256":MODULE_SHA256,"bytes":len(raw),"line_endings":"LF" if raw==normalized else "CRLF","userdata_api_used":False,"integer_identity_keys":True,"semantic_change_from_prior_registry":True}
def preflight(root,sdk):
    root=Path(root);main=root/'idf/esp32-cyd2usb-native/main'
    required=[main/name for name in ('native_tls_rx_reserve.c','native_tls_rx_reserve.h','compat/tls_static_rx/enable.cmake','compat/tls_static_rx/sdk-source-guards.json','Kconfig.projbuild','native_input_reclaim.c','native_input_reclaim.h','compat/input_reclaim/enable.cmake')]+[root/'tools/patch_cyd_tls_static_rx.py',root/'idf/components/native_stream/adaptive_input.c',root/'idf/components/native_stream/include/adaptive_input.h']
    assert all(path.is_file() for path in required),'Canonical source input missing'
    result=validate_module(main/'native_tls_rx_reserve.c')
    spec=importlib.util.spec_from_file_location('canonical_registry_patcher',root/'tools/patch_cyd_tls_static_rx.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    checked=m.validate_sdk_guards(sdk,main/'compat/tls_static_rx/sdk-source-guards.json');assert len(checked)==19
    return {'module':result,'supporting_sdk_sources':checked,'runtime_or_build':False}
