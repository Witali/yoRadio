"""Verify frozen quiet-build evidence and saved binary; no build or hardware run."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
REPO=next(p for p in ROOT.parents if (p/'tools/esp32c3_tests/common.py').is_file())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
index=json.loads((ROOT/'index.json').read_text())
for name,expected in index['files'].items():
    path=(ROOT/name).resolve()
    assert path.is_relative_to(ROOT) and path.stat().st_size==expected['bytes'] and sha(path)==expected['sha256'],name
manifest=json.loads((ROOT/'artifact/manifest.json').read_text())
art=REPO/'firmware/development/esp32c3-idf-6.1-r9a97-quiet-min250'
blob=(art/'app.bin').read_bytes()
assert len(blob)==manifest['image']['bytes'] and hashlib.sha256(blob).hexdigest()==manifest['image']['sha256']
assert blob[176:208].hex()==manifest['image']['app_elf_sha256']
assert sha(art/'bootloader.bin')==manifest['bootloader_sha256']
assert sha(ROOT/'artifact/sdkconfig')==manifest['sdkconfig_sha256']
assert manifest['production_qualified'] is False and manifest['hardware_tested'] is False
audit=json.loads((ROOT/'build-audit.json').read_text())
assert audit['result']=='PASS' and audit['image']==manifest['image']
for name,digest in manifest['source_overlay_sha256'].items():assert sha(ROOT/'sources'/name)==digest,name
config=lambda p:dict(re.findall(r'^(CONFIG_\w+)=(.+)$',p.read_text(),re.M))
old,new=map(config,(ROOT/'prior-quiet/sdkconfig',ROOT/'artifact/sdkconfig'))
diff={k:dict(before=old.get(k),after=new.get(k)) for k in old.keys()|new.keys() if old.get(k)!=new.get(k)}
assert diff==audit['configuration_changes']
assert {k:new.get(k) for k in diff}==json.loads((ROOT/'configuration-intent.json').read_text())
results={name:json.loads((ROOT/(name+'.json')).read_text()) for name in ('verify-aac','verify-http','verify-allocator')}
for name,result in results.items():
    assert result['elf_sha256']==manifest['image']['app_elf_sha256'],name
    assert result['sdkconfig_sha256']==manifest['sdkconfig_sha256'],name
assert results['verify-http']['result']=='PASS'
assert results['verify-allocator']['passed'] is True
assert results['verify-allocator']['rx_only'] is True
assert results['verify-allocator']['reserved_storage']['bytes']==17058
assert results['verify-aac']['app_sha256']==manifest['image']['sha256']
assert results['verify-aac']['types']==dict(native_aac_decoder=204,aac_high_owner_t=32744,aac_high_runtime_t=160)
assert set(results['verify-aac']['linked_calls'])=={'compact5_PVMP4AudioDecodeFrame','__wrap_get_sbr_bitstream','aac_late_sbr_select'}
assert b'native_audio_output_flush_pcm' in (ROOT/'output-task-disassembly.txt').read_bytes()
assert b'native_audio_output_discard_pcm' in (ROOT/'output-task-disassembly.txt').read_bytes()
print('PASS:',len(index['files']),'byte-exact evidence files; saved image and build checks agree. Hardware acceptance remains pending.')
