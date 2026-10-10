"""Prepare an isolated one-second prefill experiment with all probes disabled."""
import hashlib,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path('.build/c3-prefill1000-reneg-20261010');ROOT.mkdir(exist_ok=False)
OLD=Path('.build/c3-prefill500-reneg-20261010')
target='quiet-prefill1000-reneg'
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-'+target)
assert not build.exists()
config=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-growth-tls/sdkconfig').read_text()
for key,old in [('YORADIO_INPUT_PREFILL_MIN_MS',250),('YORADIO_INPUT_PREFILL_MS',500)]:
    config,count=re.subn(r'^CONFIG_'+key+'='+str(old)+'$', 'CONFIG_'+key+'=1000',config,flags=re.M)
    assert count==1,key
build.mkdir();(build/'sdkconfig').write_text(config)
sources={}
for path in [*Path('idf/esp32c3-oled-native/main').glob('*'),Path('idf/esp32c3-oled-native/CMakeLists.txt'),Path('tools/patch_i2s_pdm_clock.py'),Path('tests/native/flash_mode/boot_probe.c')]:
    if not path.is_file():continue
    data=path.read_bytes();sources[path.as_posix()]=hashlib.sha256(data).hexdigest()
    dest=ROOT/'build-sources'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
(ROOT/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
for name in ('ca.pem','server.pem','export-used.py','fixture-inputs.json','dependencies.json','requirements-tls-renegotiation.txt','review.py'):
    shutil.copyfile(OLD/name,ROOT/name)
audit=(OLD/'audit.py').read_text().replace('quiet-prefill500-reneg',target).replace('c3-prefill500-reneg-20261010','c3-prefill1000-reneg-20261010')
audit=audit.replace("{'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS':['250','500']}",
                    "{'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS':['250','1000'],'CONFIG_YORADIO_INPUT_PREFILL_MS':['500','1000']}")
audit=audit.replace('input_prefill_min_ms=500,input_prefill_ms=500','input_prefill_min_ms=1000,input_prefill_ms=1000')
audit=audit.replace("'s_pcm_fir','pcm_fir_coefficients'", "'s_audio_pipeline_probe','s_pcm_fir','pcm_fir_coefficients'")
(ROOT/'audit.py').write_text(audit)
(ROOT/'build.ps1').write_text((OLD/'build.ps1').read_text().replace('quiet-prefill500-reneg',target).replace('c3-prefill500-reneg-20261010','c3-prefill1000-reneg-20261010'))
compare=(OLD/'compare_objects.py').read_text().replace('quiet-prefill500-reneg',target)
compare=compare.replace("{'audio_service.c.obj'}","{'audio_service.c.obj','native_audio_output.c.obj'}")
(ROOT/'compare_objects.py').write_text(compare)
shutil.copyfile(__file__,ROOT/'prepare.py')
print('Prepared',len(sources),'sources; both prefill limits 1000 ms; diagnostic disabled')
