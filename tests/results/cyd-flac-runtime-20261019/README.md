# CYD custom FLAC runtime integration

The optional custom decoder is integrated into the actual CYD decoder task.
Espressif remains the Kconfig default. No board pin, output backend, decoder or
output core, task priority or task stack budget is changed by this integration.

| Gate | Evidence |
| --- | --- |
| Actual CYD task, custom callback, PCM queue sizing, native state, shared adapter and segmented core | [Host report](host/report.json), ASan/UBSan |
| Known encoder PCM and fresh FFmpeg, 130 valid fixtures × four receive schedules | 520 exact PCM comparisons, source depths 4/8/12/16/20/24, mono/stereo and decorrelation, constant/verbatim/fixed/LPC, 8192 blocks and short tails |
| Every incomplete prefix of a 1077-byte metadata chain | 4304 cases: whole/fragmented prefix and inline/separate empty EOF |
| Complete metadata without audio | [Four EOF controls](host/metadata-only-boundaries.json); the empty-stream control is in the main report |
| Direct production allocations, including adapter nothrow object, input and channel segments | 5 ordinary +19 maximum-block persistent failure points; each followed by successful reopen and exact PCM |
| Owner lifecycle | Generation change, codec replacement, nonterminal codec drain, terminal error/EOF, three blocked sends followed by Stop/maintenance, same-generation maintenance cleanup before ACK |
| Frame-window policy | Unknown (32768), maximum known (65536), oversized rejection (65537) |
| Custom AAC and FLAC coexistence | Actual FLAC task PCM plus codec replacement; legacy codec calls remain explicit doubles |
| Semantic negative controls | Source depth used as queue depth, retained terminal workspace, ACK before cleanup: each detected by an assertion; sanitizer failures/timeouts do not count |
| Registry and rollback | Actual registry function under vendor/custom selections, every enabled registration failure |
| Retained vendor/legacy task paths | [Six lifecycle variants](vendor-regression/report.json), ASan/UBSan; codec and RTOS calls remain host doubles |
| Pinned ESP-IDF v6.0.2, Xtensa GCC | [Custom](sdk/custom/integration-compile.json) audio/registry/adapter/core compilation and [untouched-default vendor](sdk/vendor/integration-compile.json) audio/registry compilation |
| Actual selected ownership | Undefined object symbols contain custom feed only in custom audio; vendor FLAC registration only in vendor registry |

Run the primary campaign with:

```powershell
C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe tests/run-cyd-flac-runtime.py --output .build/cyd-flac-runtime-fresh
```

The host runner freezes sources before compiling and executing. Exact snapshots,
generated production extracts, compiler/test logs, fixture manifests and commands
are preserved here. `check-cyd-flac-metadata-only.py` records the additional
complete-metadata controls against that same frozen binary/report. The existing
vendor regression runner records source hashes at campaign completion; those
matching source files and its generated task extract are archived separately.
SDK configuration, exact compiler commands, diagnostics and object-symbol output
are preserved; the SDK checks compile the current source and verify each main
unit's bytes before/after compilation. No compiled test executables or private
keys are included. The deterministic fixture generator and encoded/PCM hashes
allow the excluded bulk fixture and reference PCM files to be regenerated.

The FIFO, scheduler, SDK timer/log headers and allocation failures are host seams.
The custom FLAC adapter/core is real. These results do not execute vendor codec
archives, the FreeRTOS scheduler or Xtensa PCM decoding. SDK configuration emits
existing dependency/Kconfig notices, retained in its logs; the selected C/C++
integration and custom component compilations have no compiler diagnostics.

Complete application exports, custom-path QEMU execution and physical CYD A/B
with both output profiles remain open gates. Hardware heap fragmentation, minimum
stack margin, DMA progress, watchdog and decode timing have not been measured by
this campaign. No default switch, speedup, CRC/MD5 validation or complete malformed
FLAC conformance is claimed. See the [design and remaining gates](../../../docs/CYD_FLAC_TRANSFER_DESIGN.md).
