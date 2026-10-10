# Preserve contiguous heap by initializing the MPI mutex early

The optional `CONFIG_YORADIO_TLS_EARLY_MPI_LOCK` prevents the observed
first-use TLS fragmentation in two ESP32-C3 diagnostic configurations.
After HE-AACv2/HTTPS stops, the largest allocatable block remains
**114,688 bytes**, instead of falling to **102,400 bytes**. This preserves
12,288 bytes of contiguous allocation capacity; it is not a 12 KiB reduction
in allocated data or decoder storage.

## Implementation and lifetime

`app_main()` acquires and immediately releases the SDK's existing hardware
MPI mutex before application, network and decoder allocations. The normal
SDK API retains ownership and the mutex lives for the application lifetime.
No private lock pointer, replacement mutex, manual free or cryptographic
operation is introduced. FreeRTOS is already running at this point.

The deep-sleep clock boot handler runs first, so its timer-wake fast path
remains ahead of this initialization. The codec-only benchmark branch
skips it. The option is restricted to ESP32-C3 with mbedTLS hardware MPI and
**remains disabled by default** pending final quiet-production qualification.
The board tests below use awake firmware; they do not qualify deep sleep.

The [previous owner trace](ESP32C3_TLS_HEAP_OWNER_20261010.md) found one
persistent 92-byte `radio_stream` allocation splitting the watched region.
Espressif's pinned TLS tests explicitly warm up the lazy MPI mutex before
memory checks. This experiment changes only that initialization order.
The observed split disappears, supporting the proposed repair. The probe
does not record a call stack, so this is not a direct identification of
the former allocation's constructor.

## Build controls

| Candidate | Control | Application bytes |
| --- | --- | ---: |
| `idf61-mpi-probe` | `idf61-web-tcp-v2` | 1,631,904; unchanged |
| `idf61-mpi-frac4` | `idf61-frac4` | 1,623,248; +16 |

Both keep ESP-IDF `9a97f6c54ec6`, QIO 80 MHz, nominal fractional 48 kHz,
full compact AAC/SBR/PS, the 17,058-byte TLS RX reserve, adaptive input,
250/500 ms prefill and four optional extra FLAC slots. FIR, software clock
compensation and direct-DMA PCM remain disabled. The first candidate keeps
owner/TCP probes; the second omits those probes but retains performance logs.
Both extend normal public certificate roots with the existing laboratory CA.

The active configuration delta versus each control is only the new option.
All **128 code/constant sections in 18 AAC/FLAC objects are byte-identical**.
AAC feature, HTTP and TLS/input allocation link audits pass. Linked startup
disassembly verifies acquire/release before state/profiler initialization.
IRAM, DRAM and RTC sections remain unchanged. The probes' Flash text/rodata
changes are +4/-8 B; the lighter candidate's are +8/+8 B. Inactive unrelated
CLZ work is excluded.

Builds, sdkconfigs and manifests are saved under
`firmware/development/esp32c3-idf-6.1-r9a97-mpi-probe/` and
`firmware/development/esp32c3-idf-6.1-r9a97-mpi-frac4/`.

## Fresh-boot AAC/TLS recovery

Each candidate passes **5/5 original checks** for 75 seconds of full
44.1 kHz stereo HE-AACv2 with 1.0x source pacing. One TLS connection grows
plaintext records from 1 KiB to the full 16 KiB. The original 2,048-byte
total-free and 4,096-byte largest-block recovery tolerances are unchanged.

| Measurement | Probe control | Early MPI, probes | Early MPI, no owner/TCP probes |
| --- | ---: | ---: | ---: |
| Initial largest allocation | 114,688 B | 114,688 B | 114,688 B |
| Largest allocation after Stop | 102,400 B | 114,688 B | 114,688 B |
| Recovery gate | FAIL | PASS | PASS |
| Remaining owners in watched region | 1, requesting 92 B | 0 | Not instrumented |
| Total free heap after Stop | 129,000 B | 128,972 B | 133,072 B |
| DMA notification increments / write errors | 1 / 0 | 0 / 0 | 0 / 0 |

The watched range retains the exact same addresses and initial raw size:
`0x3fcc036c..0x3fcdc70c`, 115,616 B. All five new snapshots are complete,
without unknown owners, dropped rows or overflow. After Stop it is again
one free block of 115,616 B. In the control its largest raw span was
105,532 B. The smaller rounded allocation capacities in the table are the
allocator's size-class result, not the raw walk size.

In the probe pair, minimum in-playback largest capacity increases from
15,360 to 19,456 B; minimum total free heap is essentially unchanged at
22,208 versus 22,212 B. Reported mean CPU is 56.57% versus 56.68%.
These single runs do not establish a speed difference. The early-init
calls execute only at startup, and decoder arithmetic is unchanged.

DMA observations span 70.150 and 70.149 seconds on the new candidates,
with 6,580 successful writes each and zero increments/errors. These are
digital counter intervals, not analog continuity measurements. The previous
control's early increment remains recorded. Fresh-boot host connection
attempts are 473 and 468, with no failures. The probe's TCP interval also
passes its CRC, sequence and watermark checks.

## Format matrix and remaining qualification

On `idf61-mpi-frac4`, all **22 HTTPS playback/EOF cases** pass: 11 fixtures
with automatic detection and explicit codec hints. These cover MP3, FLAC,
Vorbis, Opus, AAC-LC mono/stereo at 22.05/44.1/48 kHz, HE-AAC at 44.1/48 kHz
and HE-AACv2 at 44.1 kHz. Full AAC rates and features are preserved.
After the matrix, median free heap is 133,100 B versus 133,070 B initially;
largest capacity stays 114,688 B with 17 tasks. Recovery passes.

Nine HTTPS station changes (three cycles of FLAC level 8, HE-AAC 48 kHz
and HE-AACv2 44.1 kHz) and both AAC transition sequences also pass. The
sequences exercise changing sample rates/profiles and late implicit SBR/PS.
After switches and after transitions, settled median free heap is 133,088 B,
largest capacity is 114,688 B and task count is 17. Both recovery checks pass.
The complete matrix runner records **34/34 checks passed**, including Stop,
settings preservation and runtime-fault inspection after capture closes.
Its 1,357 host connection attempts have no failures. This finite run does
not resolve the earlier intermittent connection failure.

The final quiet image, complete release regression and the earlier
intermittent TCP connect timeout remain separate qualification work.
This change does not establish that the timeout is repaired, and does not
enable the other experimental memory/clock options by default.

After testing, app-only OTA restores the listened fractional-clock image
`idf61-listen48-8c1f2d` (ELF SHA-256
`76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`)
in `app0`. Wi-Fi, playlist and settings match the initial snapshot; all
three post-restore observations retain the original stopped state.

[Frozen sources, builds, physical results and replay](../tests/results/esp32c3-mpi-startup-20261010/README.md)
preserve the failed control and both successful first-use comparisons.
Replay validates evidence integrity; it is not production acceptance.
