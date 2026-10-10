import hashlib,json,subprocess
from pathlib import Path

root=Path('.build/c3-flac-rice-20261008')
template=Path('.build/c3-staged-dma-profile-20261008/build.ps1').read_text()
baseline=Path('firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof')
saved=json.loads((baseline/'manifest.json').read_text())
source_files=list(saved['source_overlay_sha256'])+[
    'yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp',
    'yoRadio/src/audioI2S/flac_decoder/flac_decoder.h',
    'idf/esp32c3-oled-native/components/custom_flac/CMakeLists.txt',
    'idf/esp32c3-oled-native/sdkconfig.flac-bytewise-rice.defaults']
source_hash={name:hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in source_files}
for mode in ('control','bytewise'):
    work=root/mode;work.mkdir(parents=True,exist_ok=False)
    variant='r9a97-flac-rice-'+mode
    recipe=template.replace('r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof',variant)
    recipe=recipe.replace('idf61-9a97-dmaprof','idf61-rice-'+mode)
    recipe=recipe.replace('.build/c3-staged-dma-profile-20261008/',work.as_posix()+'/')
    if mode=='bytewise':
        recipe=recipe.replace("'sdkconfig.staged-dma-profile.defaults')",
            "'sdkconfig.staged-dma-profile.defaults','sdkconfig.flac-bytewise-rice.defaults')")
    (work/'build.ps1').write_text(recipe)
    print('BUILD_START',mode,flush=True)
    with (work/'build.log').open('xb') as log:
        result=subprocess.run(['pwsh.exe','-NoProfile','-File',str(work/'build.ps1')],stdout=log,stderr=subprocess.STDOUT)
    if result.returncode:raise SystemExit(result.returncode)
    image=Path('firmware/development')/('esp32c3-idf-6.1-'+variant)
    manifest=json.loads((image/'manifest.json').read_text())
    for key in ('laboratory_only','extra_trust_ca_sha256','restoration_image','restoration_elf_sha256'):
        manifest[key]=saved[key]
    assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in source_hash.items())
    manifest['source_overlay_sha256']=source_hash
    manifest['qualification']='Fresh matched FLAC Rice experiment; physical comparison pending. NOT_QUALIFIED.'
    (image/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    (image/'qualification.json').write_bytes((json.dumps(dict(result='NOT_QUALIFIED',physical_tests=False,laboratory_only=True),indent=2)+'\n').encode())
    print('BUILD_END',mode,manifest['image'],flush=True)

def values(path):
    return dict(l.split('=',1) for l in path.read_text().splitlines() if l.startswith('CONFIG_') and '=' in l)
a=values(Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-rice-control/sdkconfig'))
b=values(Path('firmware/development/esp32c3-idf-6.1-r9a97-flac-rice-bytewise/sdkconfig'))
changed={k:dict(control=a.get(k),candidate=b.get(k)) for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
assert set(changed)=={'CONFIG_YORADIO_FLAC_BYTEWISE_RICE'},changed
(root/'config-difference.json').write_text(json.dumps(changed,indent=2)+'\n')
