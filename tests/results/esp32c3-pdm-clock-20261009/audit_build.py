"""Compare experiment configurations and retain linked PDM/AAC provenance."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

sys.path.insert(0,'tools/esp32c3_tests')
from ota import image_info

ROOT=Path('.build/c3-pdm-clock-20261009')
PROJECT=Path('idf/esp32c3-oled-native')
ORIGINAL=Path('firmware/development/esp32c3-idf-6.1-r9a97-flash-qio80')
OBJDUMP=Path('C:/Work/yoRadio/.idf/tools-v6.1/tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-objdump.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def config(path):
    return dict(re.findall(r'^(CONFIG_\w+)=(.+)$',path.read_text(),re.M))

original=config(ORIGINAL/'sdkconfig')
allowed={'CONFIG_YORADIO_PDM_CLOCK_DIAGNOSTICS','CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK'}
audit=dict(result='PASS',images={},sdk_revision='9a97f6c54ec638111ce55cd36581b3c192f15207',
    source_overlay_sha256={p:sha(Path(p)) for p in (
        'tools/patch_i2s_pdm_clock.py','tools/esp32c3_tests/pdm_clock.py','tests/test-pdm-clock.py',
        'idf/esp32c3-oled-native/CMakeLists.txt','idf/esp32c3-oled-native/main/Kconfig.projbuild',
        'idf/esp32c3-oled-native/main/CMakeLists.txt')})
for mode in ('integer','fractional'):
    variant='r9a97-pdm-'+mode
    build=PROJECT/('build-idf-6.1-'+variant)
    artifact=Path('firmware/development/esp32c3-idf-6.1-'+variant)
    current=config(build/'sdkconfig')
    changes={k:dict(before=original.get(k),after=current.get(k)) for k in original.keys()|current.keys()
             if original.get(k)!=current.get(k)}
    assert set(changes)<=allowed, changes
    assert current.get('CONFIG_YORADIO_PDM_CLOCK_DIAGNOSTICS')=='y'
    assert (current.get('CONFIG_YORADIO_PDM_FRACTIONAL_CLOCK')=='y')==(mode=='fractional')
    commands=json.loads((build/'compile_commands.json').read_text())
    pdm=[c for c in commands if Path(c['file']).name=='i2s_pdm.c']
    assert len(pdm)==1 and 'yoradio_i2s' in pdm[0]['file']
    assert not any('flac_clz' in c['file'] for c in commands)
    elf=build/'yoradio_esp32c3_oled_native.elf'
    image=image_info((artifact/'app.bin').read_bytes())
    assert sha(elf)==image['app_elf_sha256']
    assembly=subprocess.check_output([str(OBJDUMP),'-d','-S','--disassemble=i2s_pdm_tx_set_clock',str(elf)])
    (ROOT/mode/'pdm-clock-disassembly.txt').write_bytes(assembly)
    code=subprocess.check_output([str(OBJDUMP),'-d','--disassemble=i2s_pdm_tx_set_clock',str(elf)]).decode()
    assert 'i2s_hal_set_tx_clock' in code
    metadata=json.loads((artifact/'manifest.json').read_text())
    metadata.update(laboratory_only=True,production_qualified=False,clock_mode=mode,
        clock_diagnostics=True,expected_flash_mode='qio',flash_mhz=80,
        extra_trust_ca_sha256='5d07cd4783170ceeb5933e41a9618d7c0775567f7e9307d8478390cf3f526de8',
        restoration_image='esp32c3-idf-6.1-r9a97-production-qio80',
        restoration_app_sha256='21311e2f87a97cbbf03fe3036111334df8fac75ffe63b9b3207ff2d02e82de0a',
        source_overlay_sha256=audit['source_overlay_sha256'],
        source_note='The pre-existing main CMake CLZ block is inactive; no CLZ benchmark source compiled.',
        bootloader_sha256=sha(artifact/'bootloader.bin'),
        qualification='Build and linked audits only; clock/noise and sustained physical checks not yet qualified')
    (artifact/'manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    audit['images'][mode]=dict(image=image,configuration_changes=changes,
        generated_driver_sha256=sha(Path(pdm[0]['file'])),compiled_source=pdm[0]['file'],
        sdkconfig_sha256=sha(artifact/'sdkconfig'),disassembly_sha256=sha(ROOT/mode/'pdm-clock-disassembly.txt'))
    for tool,extra,name in [
        ('tools/codec_benchmark/verify_aac_network_build.py',['--build',str(build)],'verify-aac.json'),
        ('tools/esp32c3_tests/verify_http_link.py',['--sdkconfig',str(build/'sdkconfig'),'--elf',str(elf)],'verify-http.json')]:
        with (ROOT/mode/(name+'.log')).open('xb') as log:
            subprocess.run([sys.executable,'-X','utf8',tool,*extra,'--objdump',str(OBJDUMP),
                            '--output',str(ROOT/mode/name)],stdout=log,stderr=subprocess.STDOUT,check=True)
    print(mode,'config and link audits PASS',image['bytes'],flush=True)
(ROOT/'build-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
