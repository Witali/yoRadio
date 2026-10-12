import hashlib,json,shutil
from pathlib import Path
root=Path(__file__).resolve().parent
dest=Path('tests/results/esp32c3-radio-rx-copy-build')
assert not dest.exists()
assert json.loads((root/'build-audit.json').read_text())['result']=='PASS'
host=Path('.build/c3-rx-copy-host-3')
assert json.loads((host/'report.json').read_text())['pass']
def copy(source,target):
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
for name in ('build.ps1','prepare.py','export-used.py','audit.py','build.log',
             'source-hashes.json','source-head.txt','build-audit.json','freeze-build.py'):
    copy(root/name,dest/name)
for folder in ('sources','link-final'):
    for p in (root/folder).rglob('*'):
        if p.is_file():copy(p,dest/p.relative_to(root))
for p in host.rglob('*'):
    if p.is_file() and p.name!='test':copy(p,dest/'host'/p.relative_to(host))
for name in ('tests/check-rx-copy-link.py','tools/esp32c3_tests/rx_ownership.py'):
    copy(Path(name),dest/'test-sources'/name)
for name in ('build.log','run.log','report.json'):
    copy(Path('.build/codec-owner/host')/name,dest/'legacy-host'/name)
sdk=Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6')
for rel in ('components/esp_netif/lwip/netif/wlanif.c',
            'components/lwip/lwip/src/core/pbuf.c','components/lwip/lwip/src/core/mem.c'):
    assert (sdk/rel).read_bytes()==(host/'sdk-sources'/rel).read_bytes(),rel
for rel in ('components/esp_netif/include/lwip/esp_netif_net_stack.h',
            'components/esp_netif/lwip/esp_netif_lwip_defaults.c',
            'components/lwip/port/include/lwipopts.h'):
    copy(sdk/rel,dest/'sdk-sources'/rel)
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-radio-rx-copy')
for p in (build/'log').glob('*'):
    if p.is_file():copy(p,dest/'idf-logs'/p.name)
verify=Path('.build/c3-radio-rx-owner/verify_commit.py').read_text().replace(
    'esp32c3-radio-rx-owner-build','esp32c3-radio-rx-copy-build')
(dest/'verify_commit.py').write_text(verify)
(dest/'.gitattributes').write_text('* -text -filter -whitespace\n')
index={p.relative_to(dest).as_posix():dict(bytes=p.stat().st_size,
    sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'index.json').write_text(json.dumps(index,indent=2)+'\n')
print('Archived',len(index),'build/host/link evidence files; no physical qualification claim')
