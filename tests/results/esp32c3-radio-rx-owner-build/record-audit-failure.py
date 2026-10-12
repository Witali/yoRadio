"""Preserve the unusable diagnostic build; never label a missing hook as success."""
import hashlib,json,re,shutil
from pathlib import Path
from elftools.elf.elffile import ELFFile
root=Path(__file__).resolve().parent
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-radio-rx-owner')
art=Path('firmware/development/esp32c3-idf-6.1-r9a97-radio-rx-owner')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((art/'manifest.json').read_text())
assert manifest['image']['sha256']==sha(art/'app.bin') and manifest['image']['bytes']<=1900544
for name,digest in json.loads((root/'source-hashes.json').read_text()).items():assert sha(Path(name))==digest,name
config=dict(re.findall(r'^(CONFIG_\w+)=(.+)$',(build/'sdkconfig').read_text(),re.M))
assert config['CONFIG_LWIP_L2_TO_L3_COPY']=='y' and config['CONFIG_YORADIO_RX_BUFFER_DIAGNOSTICS']=='y'
with (build/'yoradio_esp32c3_oled_native.elf').open('rb') as f:
    elf=ELFFile(f);syms={s.name:s['st_size'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
assert '__wrap_esp_pbuf_allocate' not in syms and 'pbuf_alloc' in syms
names=['owners','pbuf_alloc','esp_pbuf_allocate','__wrap_esp_pbuf_allocate',
       'esp_netif_free_rx_buffer','__wrap_esp_netif_free_rx_buffer','rx_buffer_diagnostic_poll']
report=dict(result='FAIL',build_succeeded=True,flashed=False,
    reason='Production uses L2-to-L3 copy; the diagnostic allocation hook esp_pbuf_allocate is absent from the linked image',
    image=manifest['image'],symbols={n:syms.get(n) for n in names},
    next_action='Observe the actual wlanif_input PBUF_RAW/PBUF_RAM allocation and final release paths; preserve copy mode and reference counts',
    source_sha256={})
sdk=Path('C:/Work/yoRadio/.idf/v6.1-9a97f6c54ec6')
for relative in ('components/esp_netif/lwip/netif/wlanif.c','components/lwip/lwip/src/core/pbuf.c',
                 'components/lwip/lwip/src/core/mem.c'):
    p=sdk/relative;report['source_sha256'][relative]=sha(p)
    target=root/'sdk-sources'/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
(root/'build-audit-failure.json').write_text(json.dumps(report,indent=2)+'\n')
manifest.update(laboratory_only=True,hardware_tested=False,production_qualified=False,
    qualification='Build succeeded but diagnostic link audit FAILED: allocation hook is inactive with production L2-to-L3 copy. Not flashed; do not use for RX ownership conclusions.',
    diagnostic_effective=False,build_report='tests/results/esp32c3-radio-rx-owner-build/build-audit-failure.json')
(art/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(art/'.gitattributes').write_text('*.json -text -filter -whitespace\nsdkconfig -text -filter -whitespace\n')
for name in ('sdkconfig','manifest.json'):shutil.copyfile(art/name,root/('artifact-'+name))
for p in (build/'log').glob('*'):
    if p.is_file():
        target=root/'idf-logs'/p.name;target.parent.mkdir(exist_ok=True);shutil.copyfile(p,target)
print(json.dumps({k:v for k,v in report.items() if k!='source_sha256'},indent=2))
