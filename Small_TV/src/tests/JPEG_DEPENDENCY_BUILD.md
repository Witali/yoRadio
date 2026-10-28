# Offline JPEG dependency and application build

The production source bundle is in `third_party/libjpeg-turbo/`. It contains the
unmodified 3.2.0/c85e6b90 Git archive, compressed to 2520264 bytes, plus the three
previously qualified patches and licenses. The original tar is 9932800 bytes;
its SHA-256 remains `a778d84d…f90b07`. Test and production patch copies match.

`build.ps1` now prepares this dependency with `tools/build_jpeg_library.py` using
the selected pinned ESP-IDF compiler, CMake and Ninja. No source download or
separate libjpeg checkout is needed. A content fingerprint selects the output
directory. Reuse checks the saved library, all exported source and configured
headers; interrupted or altered builds fail with a request for a fresh directory.
The app source manifest and bidirectional audit include codec/storage modules,
the bundle and build inputs. The archive also retains the dependency build report
and its hash. Source and dependency pins are rechecked after application linking.
Python bytecode generation is disabled while running the shared SDK tools.

Release flags are explicitly `-Os -DNDEBUG`. Inspection of actual Ninja commands
confirmed that the old qualified library also used `-Os`, despite the `-O3`
entry in its CMakeCache. The new archive is byte-identical to that qualified RV32
archive: `d690bdf330d3c406b92686100a9478432724f13dec8b7faff63fde882dc17d8a`.
This is not a new optimization result or a new target runtime measurement.

The application component now compiles the bounded decoder, backing adapter,
NOR, ownership guard, transport, ESP-IDF binding, scratch, journal and cache.
The UI/upload path still calls TJpgd; the unused extension is removed by linker
section GC. Compiling these modules does not establish full application RAM,
task stack, latency, privacy, asynchronous HTTP or cache deployment correctness.
Those remain the next integration work, followed by separate LCD/network gates
and acceptance of the exact final app/ELF.

Checks:

```powershell
python -B Small_TV/src/tests/jpeg_dependency_test.py --selection BUILD/jpeg-library/selection.json -v
pwsh -File Small_TV/src/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory BUILD
pwsh -File Small_TV/src/tests/run.ps1 -PythonPath C:/Work/yoRadio/.idf/tools-v6.1/python_env/idf6.1_py3.12_env/Scripts/python.exe
```

The dependency contract uses temporary copies for corruption tests. It checks
gzip/tar bytes and length, provenance agreement, each patch and license, actual
incremental reuse, altered private/configured headers, altered archive, a false
reported archive digest and an interrupted build. These checks do not simulate
flash faults, LCD output, Wi-Fi or physical board behavior.

2026-10-20: 13 dependency tests, 12 inventory controls, 10 cache-generator
rejections, 5806 existing native checks and 6 artifact checks passed. Main
app `676c5edf…dc086d`, ELF `cb84e536…fdc803`, source `2d1fb659…64a94`;
1170432 app bytes and 365568 free partition bytes. Assets remain `bb4469e3…084edc1`.
No new VM or hardware flash was used in this checkpoint. Evidence:
[`jpeg-dependency-build-validation-20261020.json`](../../qemu/parity/jpeg-dependency-build-validation-20261020.json).
