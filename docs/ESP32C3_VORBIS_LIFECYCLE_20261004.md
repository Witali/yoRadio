# ESP32-C3 Vorbis: original-library lifecycle and allocation failures

Date: 2026-10-04. Step 1 of the
[Vorbis repair plan](ESP32C3_VORBIS_REPAIR_PLAN.md) is complete.
**The original decoder still fails the error-handling gate. No decoder repair
or production firmware change is included in this step.**

## Results

The actual pinned Espressif RV32 Ogg/Vorbis objects were linked into a separate
ESP32-C3 QEMU application. The existing `vorbis-q10.ogg` fixture decodes at
48 kHz, stereo, signed 16-bit. Every fault case starts a fresh virtual machine;
an original crash cannot prevent the remaining cases from running.

| Test | Cases / cycles | Result |
| --- | ---: | --- |
| Valid stream: open, decode, close | 100 cycles in one VM | Identical PCM every time; all stream allocations freed; free heap and largest block restored |
| One failed allocation/reallocation at a time | 198 fresh VMs | **189 crashes, 6 handled errors, 3 unsafe success returns** |
| Invalid/truncated identification or setup header | 4 fresh VMs | **4 crashes** |
| Host classifier and retained-evidence checks | 16 tests | Passed |

This is 203 QEMU cases: one repeated baseline, 198 allocation failures and four
malformed headers. Completing the sweep is not a decoder pass. The runner
returns exit code **2** for these observed decoder failures; incomplete evidence
is an error, not a pass.

### Errors that returned

Allocation ordinals refer to the first valid decode after codec registration.

| Failed allocation ordinal | Observed result | Subsequent valid decode |
| --- | --- | --- |
| 2, 8, 9, 10, 11, 12 | Error `-2`, no remaining stream allocations, valid heap | Exact baseline PCM and restored heap |
| 3 | Reports success but produces zero PCM | Recovers |
| 4 | Reports success but produces zero PCM | Recovers |
| 198 | Reports success with 3,584 fewer PCM bytes and a different hash | Recovers |

The final case fails a 1,531-byte packet-cache reallocation during decoding.
It loses 1,792 interleaved 16-bit samples, or 896 stereo frames (about 18.67 ms
at 48 kHz), relative to the same decoder without injection. Later recovery
does not make that first decode successful. Failed nonzero `realloc` preserves
the original pointer in the harness, as required by the allocation contract.

### Reproduced failure paths

- **V1, invalid-header cleanup:** `invalid-info-version` reaches a load access
  fault in `vorbis_dsp_destroy` (`MEPC 0x4200b1fc`, fault address `0x4`). The
  previously inspected failed-open cleanup path is now exercised dynamically.
  The three other malformed-header cases also crash. The exact use-after-free
  instruction sequence is documented in the original static audit.
- **V2, unchecked DSP allocation:** `oom-0191` fails the 80-byte allocation in
  `vorbis_dsp_create`; the original code then stores through address zero
  (`MEPC 0x4200b0ec`).
- The sweep also exposes unchecked allocations in the surrounding simple
  decoder and parsing/DSP initialization paths. For example, `oom-0001` crashes
  in `esp_audio_simple_dec_open` after its initial 48-byte allocation fails.
  Step 2 must cover these callees and propagate parser errors; fixing only the
  two initially identified sites will not satisfy the failure gate.

These addresses describe this test ELF only. They are diagnostic evidence,
not patch locations. A panic's top function does not establish its root cause;
many failures surface later during partial-initialization cleanup.

## Memory and PCM baseline

| Measurement | Every valid cycle |
| --- | ---: |
| Allocation/reallocation requests | 198 |
| Peak simultaneously requested stream bytes | 42,118 B |
| Peak simultaneously allocated usable stream bytes | 42,672 B (41.67 KiB) |
| Remaining stream allocations after close | 0 |
| Free 8-bit heap before / after | 286,344 / 286,344 B |
| Largest free block before / after | 147,456 / 147,456 B |
| Minimum free heap sampled during allocation/decode | 243,304 B |
| Minimum largest free block sampled | 114,688 B |
| Test-task minimum unused stack | 14,604 B of 16,384 B |
| PCM output | 2,107,648 B; 1,053,824 interleaved samples; 526,912 stereo frames |

All 100 cycles have PCM SHA-256:

```text
eb2037928cd89a1922fd9ae9d055c03b587484b7378c55b0f319d79980976144
```

Registration happens once: four allocations retain 72 usable bytes for the
process lifetime. They are logged separately and excluded from stream peaks.
The owner ledger uses 20,480 static bytes; input and output workspaces use
2,048 and 16,384 static bytes. These, the test stack, system allocations and
allocator metadata are not part of the stream allocation peak. Stack results
include the harness and cannot be substituted for production task sizing.

The table below groups allocations that coexist at the measured usable-byte
peak by their allocating function. It is not a sum of allocation traffic.
The chronological ledger is replayed independently to verify both peak counters
and that every stream owner is released at close.

| Allocating function | Live blocks | Requested bytes | Usable bytes |
| --- | ---: | ---: | ---: |
| `_make_decode_table` | 44 | 16,138 | 16,412 |
| `vorbis_dsp_create` | 7 | 12,384 | 12,392 |
| `parse_vorbis_header` | 2 | 3,924 | 3,992 |
| `esp_es_parse_frame` | 1 | 3,930 | 3,968 |
| `_vorbis_unpack_books` | 6 | 2,926 | 2,956 |
| `append_packet` | 1 | 1,531 | 1,536 |
| `floor1_info_unpack` | 14 | 417 | 480 |
| `esp_ogg_parse_frame` | 1 | 332 | 336 |
| `res_unpack` | 4 | 180 | 188 |
| `esp_es_parse_open` | 1 | 112 | 112 |
| `esp_vorbis_dec_open` | 2 | 80 | 80 |
| `mapping_info_unpack` | 4 | 8 | 60 |
| `vorbis_info_init` | 1 | 52 | 52 |
| `esp_audio_simple_dec_open` | 1 | 48 | 48 |
| `esp_audio_dec_open` | 2 | 48 | 48 |
| `esp_ogg_dec_open` | 1 | 8 | 12 |
| **Total** | **92** | **42,118** | **42,672** |

## Implementation and evidence

- [Test firmware](../idf/esp32c3-oled-native/main/qemu_vorbis_lifecycle.c)
  replaces only the library's weak allocation shims with tracked libc calls.
  It does not patch the decoder's DSP, ownership or error paths.
- [Runner](../tools/codec_benchmark/run_vorbis_lifecycle.py) checks the pinned
  archive/fixture identities, builds a disposable flash image, runs each VM
  separately and records the original result before moving to the next case.
- [Evidence saver](../tools/codec_benchmark/save_vorbis_lifecycle.py) verifies
  complete coverage and matches every injected request's size, kind, phase and
  caller against the successful decode. It derives the peak owner table.
- [Retained evidence](../tests/results/esp32c3-vorbis-lifecycle-20261004/manifest.json)
  contains 203 compressed raw logs and 203 ordered owner ledgers, the complete
  [report](../tests/results/esp32c3-vorbis-lifecycle-20261004/report.json),
  [summary](../tests/results/esp32c3-vorbis-lifecycle-20261004/summary.json),
  symbols, source snapshots, exact configuration and QEMU-only boot/app images.

The executed runner initially grouped ledger events by type. Retained ordered
ledgers were derived afterwards from unchanged raw logs. The frozen executed
source and its original ledger hashes remain in `report.json`; evidence tests
reproduce both formats. The retained validator also rejects harness no-progress
codes as handled SDK errors and requires full heap restoration after recovery.
These stricter checks leave all 203 classifications unchanged.
The reusable runner now snapshots sources automatically before execution, and
the saver rejects source or build identities changed after a run. The original
run's source snapshots were retained separately before those improvements.

App SHA-256:
`23488fc08110aef4ebeff32482f9450a889299c431a5607803d2edc57639cf56`.
ELF SHA-256:
`c899bdc845cce2cbb270eb955a8e3bfe196810f2ef6196de7334b656818bcce5`.
The fixture and two archive hashes are retained in `report.json` and checked
before a run. The new Kconfig option defaults off and selects a separate test
entry point. **These images are for QEMU only; do not flash them to a board.**

## Reproduce

From the repository/worktree root, with the existing ESP-IDF dependencies and
ESP32-C3 QEMU installed, build in a separate directory:

```powershell
./idf/esp32c3-oled-native/build.ps1 -BuildDirectory build-qemu-vorbis-lifecycle -Sdkconfig build-qemu-vorbis-lifecycle/sdkconfig -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.qemu-vorbis-lifecycle.defaults') -DependencyRoot C:/Work/yoRadio/.idf build
```

Run using the ESP-IDF Python environment. The QEMU and BIOS paths below are the
WSL paths used for this run; change them to match another installation. Choose
new output directories to preserve earlier evidence.

```powershell
$python = 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
$qemu = '/mnt/c/Work/yoRadio/.worktree/esp32c3-stream-format/.build/qemu-cache-host/qemu-system-riscv32'
$bios = '/mnt/c/Work/QEMU-ESP32/share/qemu'
& $python tools/codec_benchmark/run_vorbis_lifecycle.py --deps C:/Work/yoRadio/.idf --qemu $qemu --bios $bios --wsl --cycles 100 --output .build/vorbis-lifecycle/recheck
# Exit 2 is expected while the original decoder still has the recorded failures.
& $python tools/codec_benchmark/save_vorbis_lifecycle.py --run .build/vorbis-lifecycle/recheck --build idf/esp32c3-oled-native/build-qemu-vorbis-lifecycle --output tests/results/vorbis-lifecycle-recheck
& $python tests/test-vorbis-lifecycle.py
& $python tests/test-vorbis-lifecycle-evidence.py
```

`--baseline-only` is a quick decode check, not completion of step 1. The full
sweep takes the allocation count from the valid baseline rather than assuming
a fixed number in the runner.

## Limits and next step

The sweep covers every allocation request on the successful path for **one**
fixture, with one injected failure per VM. It does not exhaust multiple
simultaneous failures, allocations unique to alternate paths, all legal Vorbis
setups or all malformed inputs. Registration failure remains a separate case
for step 2. The four malformed tests call the raw Vorbis open API after removing
the Ogg packet type/signature, to exercise decoder header cleanup directly.

Identical hashes establish repeatability against this decoder's own baseline;
they do not establish agreement with libvorbis or correct EOF trimming. PCM
retry/EOF qualification remains step 3. A 16 KiB output buffer avoids intentional
output-resize retries in this experiment.

This isolated image starts no networking, player, WebUI or physical audio output.
It does not reproduce or explain the physical radio's post-Vorbis fragmentation,
measure production CPU load, or qualify OTA. No board was flashed. No memory
saving is claimed. Step 2 can now repair initialization, error propagation and
teardown against preserved failing cases while keeping valid-stream PCM intact.
