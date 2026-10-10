"""Build-only experiment: minimum startup prefill 500 ms, existing maximum unchanged."""
import hashlib,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path('.build/c3-prefill500-reneg-20261010')
ROOT.mkdir(exist_ok=False)
OLD=Path('.build/c3-aac-growth-tls-20261010')
target='quiet-prefill500-reneg'
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-'+target)
assert not build.exists()
config=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-growth-tls/sdkconfig').read_text()
config,count=re.subn(r'^CONFIG_YORADIO_INPUT_PREFILL_MIN_MS=250$',
                    'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS=500',config,flags=re.M)
assert count==1
build.mkdir();(build/'sdkconfig').write_text(config)
sources={}
for path in [*Path('idf/esp32c3-oled-native/main').glob('*'),Path('idf/esp32c3-oled-native/CMakeLists.txt'),Path('tools/patch_i2s_pdm_clock.py'),Path('tests/native/flash_mode/boot_probe.c')]:
    if not path.is_file():continue
    data=path.read_bytes();sources[path.as_posix()]=hashlib.sha256(data).hexdigest()
    dest=ROOT/'build-sources'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
(ROOT/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
for name in ('ca.pem','server.pem','export-used.py'):
    shutil.copyfile(OLD/name,ROOT/name)
audit=(OLD/'audit.py').read_text().replace('quiet-growth-tls',target).replace('c3-aac-growth-tls-20261010','c3-prefill500-reneg-20261010')
audit=audit.replace("baseline='quiet-output-health'","baseline='quiet-growth-tls'")
audit=re.sub(r'^assert changes==.*?,changes$',"assert changes=={'CONFIG_YORADIO_INPUT_PREFILL_MIN_MS':['250','500']},changes",audit,flags=re.M)
audit=audit.replace("from bundle_audit import verify_bundle\nverify_bundle(BASE/'esp-idf/mbedtls/x509_crt_bundle',bundle,ROOT/'ca.pem',ROOT/'bundle-audit.json')",
                    "assert bundle.read_bytes()==(BASE/'esp-idf/mbedtls/x509_crt_bundle').read_bytes()")
audit=audit.replace('input_prefill_min_ms=250','input_prefill_min_ms=500')
(ROOT/'audit.py').write_text(audit)
(ROOT/'build.ps1').write_text((OLD/'build.ps1').read_text().replace('quiet-growth-tls',target).replace('c3-aac-growth-tls-20261010','c3-prefill500-reneg-20261010'))
compare=Path('.build/c3-output-health-20261010/compare_objects.py').read_text()
compare=compare.replace("collect('quiet-mpi-health'),collect('quiet-output-health')", "collect('quiet-growth-tls'),collect('"+target+"')")
compare=compare.replace("{'native_audio_output.c.obj','web_service.c.obj'}","{'audio_service.c.obj'}")
(ROOT/'compare_objects.py').write_text(compare)
print('Prepared',len(sources),'source identities; only minimum prefill config differs')
