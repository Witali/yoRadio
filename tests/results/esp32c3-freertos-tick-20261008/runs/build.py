import hashlib
import json
from pathlib import Path
import subprocess

root = Path('.build/c3-tick-20261008')
base = Path('firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof')
control = json.loads((base/'manifest.json').read_text())
template = Path('.build/c3-staged-dma-profile-20261008/build.ps1').read_text()

for tick in (2,5):
    variant = 'r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof-tick'+str(tick)
    recipe = template.replace('r9a97f6c54ec6-rx6-reserve-rxonly-dmaprof', variant)
    recipe = recipe.replace('idf61-9a97-dmaprof', 'idf61-9a97-tick'+str(tick))
    recipe = recipe.replace("'sdkconfig.staged-dma-profile.defaults')",
        "'sdkconfig.staged-dma-profile.defaults','sdkconfig.freertos-tick-"+str(tick)+"ms.defaults')")
    target = root/('tick'+str(tick))
    target.mkdir(exist_ok=False)
    recipe = recipe.replace('.build/c3-staged-dma-profile-20261008/', target.as_posix()+'/')
    (target/'build.ps1').write_text(recipe)
    print('BUILD_START',tick,flush=True)
    with (target/'build.log').open('xb') as log:
        status = subprocess.run(['pwsh.exe','-NoProfile','-File',str(target/'build.ps1')],
            stdout=log,stderr=subprocess.STDOUT).returncode
    if status:
        raise SystemExit(status)
    image = Path('firmware/development')/('esp32c3-idf-6.1-'+variant)
    config = (image/'sdkconfig').read_text()
    assert 'CONFIG_FREERTOS_HZ='+str(1000//tick)+'\n' in config
    def values(text):
        return dict(line.split('=',1) for line in text.splitlines() if line.startswith('CONFIG_') and '=' in line)
    previous, current = values((base/'sdkconfig').read_text()),values(config)
    changed = {key:dict(control=previous.get(key),candidate=current.get(key))
        for key in previous.keys()|current.keys() if previous.get(key)!=current.get(key)}
    assert set(changed)=={'CONFIG_FREERTOS_HZ'},changed
    manifest = json.loads((image/'manifest.json').read_text())
    for key in ('laboratory_only','extra_trust_ca_sha256','restoration_image','restoration_elf_sha256'):
        manifest[key]=control[key]
    sources = list(control['source_overlay_sha256'])+[
        'idf/esp32c3-oled-native/sdkconfig.freertos-tick-'+str(tick)+'ms.defaults']
    manifest['source_overlay_sha256']={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sources}
    manifest['qualification']='Build and linked audits only; experimental '+str(tick)+' ms tick; physical tests pending.'
    manifest['scheduler_tick_ms']=tick
    manifest['control_configuration_diff']=changed
    (image/'manifest.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
    qualification=dict(result='NOT_QUALIFIED',image=manifest['image'],physical_tests=False,
        laboratory_only=True,scheduler_tick_ms=tick,reference=base.as_posix())
    (image/'qualification.json').write_bytes((json.dumps(qualification,indent=2)+'\n').encode())
    print('BUILD_END',tick,manifest['image'],flush=True)
print('TICK_BUILDS_COMPLETE',flush=True)
