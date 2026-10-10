"""Prepare a lab-only checkpoint image from the 250..500 ms baseline."""
import hashlib,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path('.build/c3-pipeline-probe-20261010');ROOT.mkdir(exist_ok=False)
OLD=Path('.build/c3-prefill500-reneg-20261010')
target='quiet-pipeline-probe'
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-'+target)
assert not build.exists()
config=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-growth-tls/sdkconfig').read_text()
assert 'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS=250' in config
config+='\nCONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC=y\n'
build.mkdir();(build/'sdkconfig').write_text(config)
sources={}
for path in [*Path('idf/esp32c3-oled-native/main').glob('*'),Path('idf/esp32c3-oled-native/CMakeLists.txt'),Path('tools/patch_i2s_pdm_clock.py'),Path('tests/native/flash_mode/boot_probe.c')]:
    if not path.is_file():continue
    data=path.read_bytes();sources[path.as_posix()]=hashlib.sha256(data).hexdigest()
    dest=ROOT/'build-sources'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
(ROOT/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
for name in ('ca.pem','server.pem','export-used.py','fixture-inputs.json','dependencies.json','requirements-tls-renegotiation.txt'):
    shutil.copyfile(OLD/name,ROOT/name)
audit=(OLD/'audit.py').read_text().replace('quiet-prefill500-reneg',target).replace('c3-prefill500-reneg-20261010','c3-pipeline-probe-20261010')
audit=audit.replace("{'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS':['250','500']}","{'CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC':[None,'y']}")
audit=audit.replace('input_prefill_min_ms=500','input_prefill_min_ms=250')
audit=audit.replace("assert symbols['s_tls_large_storage']['st_size']==17058", "assert symbols['s_tls_large_storage']['st_size']==17058\n    assert symbols['s_audio_pipeline_probe']['st_size']==516\n    assert after['CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ']=='160' and after.get('CONFIG_PM_ENABLE')!='y'")
audit=audit.replace("production_health=True,output_health=True", "production_health=True,output_health=True,pipeline_health_diagnostic=True")
(ROOT/'audit.py').write_text(audit)
(ROOT/'build.ps1').write_text((OLD/'build.ps1').read_text().replace('quiet-prefill500-reneg',target).replace('c3-prefill500-reneg-20261010','c3-pipeline-probe-20261010'))
compare=(OLD/'compare_objects.py').read_text().replace('quiet-prefill500-reneg',target)
compare=compare.replace("{'audio_service.c.obj'}","{'audio_service.c.obj','native_audio_output.c.obj','web_service.c.obj'}")
(ROOT/'compare_objects.py').write_text(compare)
shutil.copyfile(__file__,ROOT/'prepare.py')
print('Prepared',len(sources),'source identities; diagnostic only, baseline prefill retained')
