"""Freeze a quiet production candidate with early MPI initialization and health."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
target='quiet-mpi-health'
build=Path('idf/esp32c3-oled-native/build-idf-6.1-r9a97-'+target)
artifact=Path('firmware/development/esp32c3-idf-6.1-r9a97-'+target)
assert not build.exists() and not artifact.exists()
config=Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-frac4/sdkconfig').read_text()
assert 'CONFIG_YORADIO_TLS_EARLY_MPI_LOCK=' not in config
build.mkdir();(build/'sdkconfig').write_text(config+'\nCONFIG_YORADIO_TLS_EARLY_MPI_LOCK=y\n')
sources={}
for path in [*Path('idf/esp32c3-oled-native/main').glob('*'),Path('idf/esp32c3-oled-native/CMakeLists.txt'),Path('tools/patch_i2s_pdm_clock.py'),Path('tests/native/flash_mode/boot_probe.c')]:
    if not path.is_file():continue
    data=path.read_bytes();sources[path.as_posix()]=hashlib.sha256(data).hexdigest()
    dest=ROOT/'build-sources'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
(ROOT/'source-hashes.json').write_text(json.dumps(sources,indent=2)+'\n')
(ROOT/'source-head.txt').write_bytes(subprocess.check_output(['git','rev-parse','HEAD']))
audit=Path('tests/results/esp32c3-mpi-startup-20261010/audit.py').read_text()
audit=audit.replace("choices=['mpi-probe','mpi-frac4']", "choices=['quiet-mpi-health']")
audit=audit.replace("Path('.build/c3-mpi-startup-20261010')", "Path('.build/c3-quiet-health-20261010')")
audit=audit.replace('lab=True', 'lab=False')
audit=audit.replace("baseline='web-tcp-v2' if a.target=='mpi-probe' else 'frac4'", "baseline='quiet-frac4'")
audit=audit.replace("source_note='Early initialization of the existing SDK MPI mutex; inactive CLZ excluded; decoder and TLS allocation routes unchanged.'", "production_health=True,source_note='Quiet candidate with early MPI initialization and on-demand health; lifetime OOM/WDT counters; inactive CLZ excluded.'")
(ROOT/'audit.py').write_text(audit)
(ROOT/'export-used.py').write_bytes(Path('tests/results/esp32c3-mpi-startup-20261010/export-used.py').read_bytes())
print('Prepared quiet candidate and',len(sources),'frozen source files')
