"""Narrow generated-header compatibility-alias correction; original helpers stay frozen."""
import hashlib
from common import BASE, PROFILE, load, pin

def config_proof(build):
    before = load(PROFILE / 'baseline/sdkconfig.json')
    after = load(build / 'config/sdkconfig.json')
    delta = {k: dict(before=before.get(k), after=after.get(k))
             for k in before.keys() | after.keys()
             if k not in before or k not in after or type(before[k]) is not type(after[k]) or before[k] != after[k]}
    assert delta == load(BASE / 'preflight.json')['expected_effective_config_delta']
    old = (PROFILE / 'baseline/sdkconfig.h').read_bytes()
    new = (build / 'config/sdkconfig.h').read_bytes()
    old_lf, new_lf = old.replace(b'\r\n', b'\n'), new.replace(b'\r\n', b'\n')
    replacements = (
        (b'#define CONFIG_LWIP_TCP_OVERSIZE_MSS 1\n', b'#define CONFIG_LWIP_TCP_OVERSIZE_DISABLE 1\n'),
        (b'#define CONFIG_TCP_OVERSIZE_MSS CONFIG_LWIP_TCP_OVERSIZE_MSS\n',
         b'#define CONFIG_TCP_OVERSIZE_DISABLE CONFIG_LWIP_TCP_OVERSIZE_DISABLE\n'),
    )
    expected = old_lf
    for previous, replacement in replacements:
        assert old_lf.count(previous) == new_lf.count(replacement) == 1
        expected = expected.replace(previous, replacement)
    assert expected == new_lf, 'Header difference exceeds the selected choice and its generated compatibility alias'
    return dict(effective_delta=delta, before=pin(PROFILE / 'baseline/sdkconfig.json'),
                after=pin(build / 'config/sdkconfig.json'), header_before=pin(PROFILE / 'baseline/sdkconfig.h'),
                header_after=pin(build / 'config/sdkconfig.h'),
                header_comparison='Exactly the modern selected-choice define and its sdkconfig.rename compatibility alias, after explicit CRLF normalization; raw hashes retained.')
