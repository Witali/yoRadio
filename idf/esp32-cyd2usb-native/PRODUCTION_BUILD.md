# Reproducible CYD production builds

Use the CYD ESP32 Xtensa project and its pinned ESP-IDF **v6.0.2** dependencies.
The C3 SDK, sdkconfig, RISC-V ABI, peripheral setup, and GPIO choices are not
production inputs for this board.

From the repository root, with dependencies already installed:

```powershell
& ./idf/esp32-cyd2usb-native/build-production.ps1 `
    -DependencyRoot C:/Work/yoRadio/.idf -AudioBackend pdm
```

Use `continuous` for the native DAC continuous driver, or `legacy` for the
ESP-IDF 5.5 legacy I2S/DAC driver embedded in the pinned CYD project. Each
backend defaults to its own `build-production-<backend>/sdkconfig` and preserves
the corresponding CYD defaults selected by the existing `build.ps1`.
An existing isolated config is never overwritten. When it is missing, the
wrapper seeds it from the corresponding CYD `sdkconfig`, `sdkconfig.dac`, or
`sdkconfig.legacy-dac` full profile if available. A clean clone without those
generated full configs uses CYD defaults and the backend overlay. The seed path,
SHA256 and default files are recorded; even ignored seed inputs are checked for
changes before publication. The wrapper never imports a C3 configuration or
modifies the original full-profile files.

The default archive is
`firmware/development/esp32-cyd2usb-native-production-<backend>/`. Override the
variant with `-Variant name`, or select a different directory **inside**
`firmware/development` with `-FirmwareOutputDirectory`. Versioned release
directories are rejected. To select an existing isolated build/configuration:

```powershell
& ./idf/esp32-cyd2usb-native/build-production.ps1 `
    -DependencyRoot C:/Work/yoRadio/.idf -AudioBackend continuous `
    -BuildDirectory build-production-continuous `
    -Sdkconfig build-production-continuous/sdkconfig `
    -Variant esp32-cyd2usb-native-production-continuous `
    -Evidence tests/results/your-validation/README.md
```

This is an offline build wrapper: dependencies must exist before invocation.
It does not invoke setup, download packages, flash, reset, or deploy OTA.
PowerShell 7 is required. The Python orchestrator runs the existing build script
in a child PowerShell process so an `exit` in SDK environment setup cannot skip
the archive step in the parent process. Arguments are passed as an argument
vector without constructing shell command text. Existing IDF build-script
limitations still apply to its own invocation of `idf.py`.

Production builds use GCC, with separate build directories from Clang analysis.
The wrapper requires clean source by default, including non-ignored untracked
source/assets/configuration. Generated `firmware/development/` and
`tests/results/` paths are excluded from the source fingerprint and source-dirty
check, so archiving one backend does not require committing its outputs before
building another. The exclusions are recorded in the manifest. Clean tracked
files use Git's indexed blob identities, avoiding repeated reads of large
immutable release/history artifacts. Modified and untracked source uses actual
working-file hashes.

`-AllowDirty` explicitly permits an experiment; its manifest records source
dirty state, actual Git dirty state, untracked source paths, and the content
SHA256. The image's `-dirty` marker must match Git's actual tracked dirty state,
which can include previously exported tracked development images. The source
commit and working-content snapshot must remain unchanged during the build.
Concurrent source edits are therefore incompatible with a production export.

The exporter checks all of the following before replacing a development
hand-off:

- ESP32 target in CMake, sdkconfig, flash recipe, and image chip ID; Xtensa ELF
  machine and the pinned CYD GCC/IDF dependency roots.
- Exactly the requested PDM/continuous/legacy backend; generated current
  sdkconfig values match the actual text configuration. Deprecated aliases in
  IDF's text file do not falsely fail this comparison.
- Image segment bounds/checksum and appended SHA256; application descriptor
  project, source version, IDF version, and embedded SHA256 of the actual ELF.
- Generated partition-table MD5, partition overlap and 4 MiB flash bounds, both
  OTA application slots, image size against the smaller slot, and application
  address in the generated flash recipe.

The archive contains `app.bin`, text and JSON sdkconfig, the generated partition
table, CMake project description, flash recipe, builder logs, and `manifest.json`.
The manifest records image/ELF/config/partition/compiler SHA256, source identity,
backend, build command, logs, and optional evidence references. The manifest is
published last as the completed export marker. `physical_tested` remains false:
software qualification cannot prove board playback or audio quality.

If a successful builder produces an unqualified candidate, the previous hand-off
is preserved and the candidate is saved under
`failed-validation/<timestamp>/unverified-app.bin` with a failure report. Such a
file must not be treated as a verified production image.

An existing build can be qualified without running IDF again:

```powershell
& C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe `
    tools/export_cyd_production.py export `
    --dependency-root C:/Work/yoRadio/.idf --backend pdm `
    --build-dir build-production-pdm --variant esp32-cyd2usb-native-production-pdm
```

Run executable host qualification with:

```powershell
& C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe `
    tests/run-cyd-production-wrapper.py
```

These tests use deterministic fixture images, Xtensa ELF headers, configurations,
and a real child process with a mocked external builder command. They verify
acceptance and rejection, source changes, preservation of an older hand-off,
offline preflight, and export after child-process termination. They do not
replace a real IDF build or physical acceptance for each audio backend.
