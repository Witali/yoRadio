import hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OLD=Path('.build/c3-quiet-health-20261010')
target='quiet-output-health'
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-'+target)
artifact=Path('firmware/development/esp32c3-idf-6.1-r9a97-'+target)
assert not build.exists() and not artifact.exists()
build.mkdir()
shutil.copyfile('firmware/development/esp32c3-idf-6.1-r9a97-quiet-mpi-health/sdkconfig',build/'sdkconfig')
sources={}
for path in [*Path('idf/esp32c3-oled-native/main').glob('*'),Path('idf/esp32c3-oled-native/CMakeLists.txt'),Path('tools/patch_i2s_pdm_clock.py'),Path('tests/native/flash_mode/boot_probe.c')]:
    if not path.is_file():continue
    data=path.read_bytes();sources[path.as_posix()]=hashlib.sha256(data).hexdigest()
    dest=ROOT/'build-sources'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
(ROOT/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
audit=(OLD/'audit.py').read_text().replace('quiet-mpi-health','quiet-output-health').replace('c3-quiet-health-20261010','c3-output-health-20261010').replace("baseline='quiet-frac4'","baseline='quiet-mpi-health'")
audit=audit.replace("assert changes=={'CONFIG_YORADIO_TLS_EARLY_MPI_LOCK':[None,'y']},changes",'assert changes=={},changes')
audit=audit.replace("production_health=True,source_note=", "production_health=True,output_health=True,source_note=")
audit=audit.replace('lifetime OOM/WDT counters; inactive CLZ excluded.','lifetime OOM/WDT and staged output counters; inactive CLZ excluded.')
(ROOT/'audit.py').write_text(audit)
shutil.copyfile(OLD/'export-used.py',ROOT/'export-used.py')
(ROOT/'build.ps1').write_text((OLD/'build.ps1').read_text().replace('quiet-mpi-health','quiet-output-health').replace('c3-quiet-health-20261010','c3-output-health-20261010'))
shutil.copytree('.build/production-health-native',ROOT/'native-health')
print('Prepared',target,'with',len(sources),'frozen sources')
