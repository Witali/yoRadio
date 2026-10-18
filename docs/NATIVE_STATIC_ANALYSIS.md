# Native firmware static analysis

Use Espressif clang-tidy and Clang Static Analyzer for both native targets.
Run a complete baseline initially and repeat it after substantial changes,
as requested. ASan/UBSan host tests and physical playback acceptance remain
separate checks.

[.clang-tidy](../.clang-tidy) selects correctness, ownership, portability and
performance checks. It leaves formatting alone. The supported GCC production
toolchain remains the firmware compiler. Configure Clang in a separate build
directory and use a separate sdkconfig; its SDK libc/compiler choices can differ.
Do not use a Clang configure with the production sdkconfig.

The [runner](../tools/run_native_lint.py) analyzes every project-owned C/C++
translation unit in that profile's compilation database, including shared
modules and transitive project headers. External SDK/vendor source and generated
build files are excluded as translation units. Disabled optional features and
QEMU-only source require their own configured profiles; a full production
profile scan does not claim every possible configuration was analyzed.

## Configure the two targets

Run these commands from the task worktree using PowerShell 7. The shared
dependency cache is shown explicitly because it lives in the main checkout.

```powershell
$env:IDF_TOOLCHAIN = 'clang'
try {
    ./idf/esp32-cyd2usb-native/build.ps1 `
        -DependencyRoot C:/Work/yoRadio/.idf `
        -BuildDirectory build-lint -Sdkconfig build-lint/sdkconfig `
        -IdfArguments @('reconfigure')
    ./idf/esp32c3-oled-native/build-production.ps1 -TestedRadioProfile `
        -DependencyRoot C:/Work/yoRadio/.idf `
        -BuildDirectory build-lint -Sdkconfig build-lint/sdkconfig `
        -IdfArguments @('reconfigure')
} finally {
    Remove-Item Env:IDF_TOOLCHAIN -ErrorAction SilentlyContinue
}
```

Install the SDK-pinned `esp-clang` with that SDK's `tools/idf_tools.py` if it
is missing. CYD IDF 6.0.2 uses `esp-20.1.1_20250829`; the pinned C3 IDF 6.1
revision uses `esp-21.1.3_20260408`. Native application compilation databases
contain the correct target architecture, definitions and include paths.
Clang support in ESP-IDF is experimental; a successful configure/analysis
does not qualify Clang-built production firmware.

## Run a complete analysis

Choose a new output directory for every campaign. Existing complete or failed
reports are never overwritten. The runner saves a log and exported YAML
diagnostics per source, plus JSON with source hashes, compiler version, commit,
dirty state, warning counts and analysis completeness.

```powershell
$analysisPython = 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe'
& $analysisPython -B -X utf8 tools/run_native_lint.py `
    --build-dir idf/esp32-cyd2usb-native/build-lint `
    --clang-tidy C:/Work/yoRadio/.idf/tools-v6.0.2/tools/esp-clang/esp-20.1.1_20250829/esp-clang/bin/clang-tidy.exe `
    --output .build/lint-cyd-next --jobs 2
& $analysisPython -B -X utf8 tools/run_native_lint.py `
    --build-dir idf/esp32c3-oled-native/build-lint `
    --clang-tidy C:/Work/yoRadio/.idf/tools-v6.1/tools/esp-clang/esp-21.1.3_20260408/esp-clang/bin/clang-tidy.exe `
    --output .build/lint-c3-next --jobs 2
```

A nonzero tool exit, timeout or compilation error makes the campaign incomplete.
Warnings remain visible for review; `complete: true` means the tools finished,
not that every warning was fixed. Reconfigure after source/configuration changes
that affect the compilation database. Retain significant reports under
`tests/results/` with the corresponding source change.

## Initial baseline on 18 October 2026

| Target | Own translation units | Warning instances | Parse/tool errors | Report |
| --- | ---: | ---: | ---: | --- |
| CYD PDM, IDF 6.0.2 | 11 | 29 | 0 | [CYD initial](../tests/results/native-lint-20261018/cyd-initial/report.json) |
| C3 tested radio, pinned IDF 6.1 | 49 | 504 | 0 | [C3 initial](../tests/results/native-lint-20261018/c3-initial/report.json) |

Both complete runs used the retained [initial configuration](../tests/results/native-lint-20261018/initial.clang-tidy).
The CYD run includes the first lifecycle transfer while it was in progress;
source hashes identify its exact inputs. These counts are warning instances,
including repeated diagnostics from headers, not confirmed defects.

The C3 run includes 245 `portability-avoid-pragma-once` instances and 161
`DeprecatedOrUnsafeBufferHandling` recommendations; CYD has 16 of the latter.
The working configuration excludes these two rules after review: all supported
toolchains implement `#pragma once`, and mandatory Annex K replacements for
every bounded `memcpy`/`snprintf` are unsuitable for the embedded APIs in use.
Other bounds, use-after-free, null, stream and arithmetic checks remain enabled.
The original broad reports remain intact, so future counts must be compared
with their recorded configuration hashes.

After the lifecycle change, complete runs with the working configuration cover
the same 11 CYD and 49 C3 units:
[CYD lifecycle](../tests/results/native-lint-20261018/cyd-lifecycle/report.json)
has 10 warning instances; [C3 reviewed profile](../tests/results/native-lint-20261018/c3-reviewed-profile/report.json)
has 98 instances at 79 unique diagnostic locations. Both have zero parse/tool
errors. CYD `audio_service.c` has no remaining diagnostics in this run.
Most of the numerical reduction comes from the two documented rule exclusions;
it must not be presented as hundreds of firmware bugs fixed.

## Review queue

| Finding | Review and next action |
| --- | --- |
| CYD stream-buffer null path | The analyzer assumes `vTaskDelete(NULL)` returns. The lifecycle change adds an explicit return after self-deletion; keep allocation failure visible. |
| CYD resampler signed/unsigned conversion | Use signed rounding constants explicitly and compare PCM, including negative samples and stream boundaries. |
| C3 FLAC shift bounds | Existing code checks input depth and wasted bits. Revalidate the reduced depth before shifting, then run malformed input and PCM fixtures. Do not infer an observed crash from the static report. |
| C3 AAC private overlay bounds | Inspect the right-channel overlay and reset call chain against the audited layout and allocation. Retain the warning until checked; do not suppress an ABI access solely because historical playback passed. |
| C3 Wi-Fi `strcspn` taint | `fgets` and the tab split bound the string; the checker loses the returned span. Review with long/fragmented lines before changing accepted credentials. |
| C3 embedded-script pointer subtraction | Linker start/end symbols refer to one binary asset; review linker-symbol representation separately from ordinary C arrays. |
| C3 snapshot `memcmp` | `capture_status_key` zeroes the entire key before assigning fields. Review padding/representation against an explicit field comparison before changing event behavior. |
| Enum sentinels, quiet-log dead stores and signed timezone/error codes | Review semantics individually. Casting timezone hours to unsigned would change valid negative offsets. |
| File read/EOF diagnostics | Inspect send failure, `ferror` and `feof` paths in both static workers; keep original failures and executable HTTP tests. |

Runtime fixes use separate focused commits and their own tests. Do not apply
bulk `--fix` to private codec layouts, arithmetic or user settings.

After the portable stream transfer, complete full reruns cover 13 CYD units
(the shared ICY source and TLS adapter were added) and all 49 C3 units:
[CYD stream final](../tests/results/native-lint-20261018/cyd-stream-final/report.json)
has 10 warnings and [C3 shared stream final](../tests/results/native-lint-20261018/c3-shared-stream-final/report.json)
has 98, both with zero parse/tool errors. CYD `audio_service.c`, the shared
parser and both TLS adapters have no diagnostics. Earlier intermediate runs
are retained: the CYD header-name comparison was made explicit; the C3 `.c`
include is an intentional compatibility translation unit, documented locally
with a single rule annotation after compiling it in both firmware and host
tests. No general analyzer or memory-safety check was disabled.

After continuous frame routing, full runs cover
[14 CYD units](../tests/results/native-lint-20261018/cyd-frames/report.json)
(11 warnings) and [all 49 C3 units](../tests/results/native-lint-20261018/c3-frames/report.json)
(98 warnings), with zero parse/tool errors. The shared queue has no diagnostics.
The additional CYD warning is the existing frame-info zero initialization with
an enum whose named values begin at one; keep it in the sentinel/type review
queue. It is not evidence of an observed invalid frame or memory failure.
