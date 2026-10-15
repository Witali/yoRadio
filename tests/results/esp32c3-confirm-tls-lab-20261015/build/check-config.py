import json,re
from pathlib import Path
def config(path):
    out={}
    for line in path.read_text().splitlines():
        m=re.fullmatch(r'(CONFIG_\w+)=(.*)',line)
        n=re.fullmatch(r'# (CONFIG_\w+) is not set',line)
        if m:out[m[1]]=m[2]
        elif n:out[n[1]]='n'
    return out
base=Path('.build/c3-confirm-tls-lab-20261015')
old=config(Path('firmware/development/esp32c3-idf61-confirm-probe/sdkconfig'))
new=config(Path('firmware/development/esp32c3-idf61-confirm-tls-lab/sdkconfig'))
diff={key:[old.get(key),new.get(key)] for key in old.keys()|new.keys() if old.get(key)!=new.get(key)}
assert set(diff)=={'CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE','CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH'},diff
assert new['CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE']=='y'
assert new['CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH']=='"'+(base/'trust/ca.pem').resolve().as_posix()+'"'
(base/'config-comparison.json').write_text(json.dumps(diff,indent=2)+'\n')
print('PASS: only added laboratory CA configuration differs')
