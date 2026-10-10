import hashlib,json,re,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OLD=Path('.build/c3-output-health-20261010')
target='quiet-growth-tls'
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-'+target)
artifact=Path('firmware/development/esp32c3-idf-6.1-r9a97-'+target)
assert not build.exists() and not artifact.exists()
ca=ROOT/'ca.pem'
shutil.copyfile('.build/c3-tls-records-20261007/trust/ca.pem',ca)
shutil.copyfile('.build/c3-tls-records-20261007/trust/server.pem',ROOT/'server.pem')
config=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-output-health/sdkconfig').read_text()
config,count=re.subn(r'^# CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE is not set$',
    'CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE=y\nCONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH="'+ca.as_posix()+'"',config,flags=re.M)
assert count==1
build.mkdir();(build/'sdkconfig').write_text(config)
sources={}
for path in [*Path('idf/esp32c3-oled-native/main').glob('*'),Path('idf/esp32c3-oled-native/CMakeLists.txt'),Path('tools/patch_i2s_pdm_clock.py'),Path('tests/native/flash_mode/boot_probe.c')]:
    if not path.is_file():continue
    data=path.read_bytes();sources[path.as_posix()]=hashlib.sha256(data).hexdigest()
    dest=ROOT/'build-sources'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
(ROOT/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
audit=(OLD/'audit.py').read_text().replace('quiet-output-health','quiet-growth-tls').replace('c3-output-health-20261010','c3-aac-growth-tls-20261010').replace("baseline='quiet-mpi-health'","baseline='quiet-output-health'")
expected={'CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE':[None,'y'],
          'CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH':[None,'"'+ca.as_posix()+'"']}
audit=audit.replace('lab=False','lab=True').replace('assert changes=={},changes','assert changes=='+repr(expected)+',changes')
audit=audit.replace("assert bundle.read_bytes()==(BASE/'esp-idf/mbedtls/x509_crt_bundle').read_bytes()", "from bundle_audit import verify_bundle\nverify_bundle(BASE/'esp-idf/mbedtls/x509_crt_bundle',bundle,ROOT/'ca.pem',ROOT/'bundle-audit.json')")
audit=audit.replace('if not lab:', 'if True:').replace("assert after.get('CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE')!='y'","assert after.get('CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE')=='y'")
audit=audit.replace('console_and_logs=lab','console_and_logs=False')
audit=audit.replace("if lab:manifest['extra_trust_ca_sha256']=previous['extra_trust_ca_sha256']","if lab:manifest['extra_trust_ca_sha256']=sha(ROOT/'ca.pem')")
audit=audit.replace("source_note='Quiet candidate", "source_note='LAB CA ONLY; quiet candidate")
(ROOT/'audit.py').write_text(audit)
shutil.copyfile(OLD/'export-used.py',ROOT/'export-used.py')
(ROOT/'build.ps1').write_text((OLD/'build.ps1').read_text().replace('quiet-output-health','quiet-growth-tls').replace('c3-output-health-20261010','c3-aac-growth-tls-20261010'))
# Firmware has no source changes: only a test root and project version differ.
print('Prepared quiet laboratory CA image with',len(sources),'frozen sources')
