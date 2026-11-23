# Full-application HE-AAC memory and decoder scheduling

The unchanged public Espressif decoder now completes the original HE-AAC
fixture through TLS, TFT and WebUI on all three CYD outputs in the tested
optional network profiles. Each emits all 614,400 stereo PCM16 frames at
48 kHz, with complete SHA-256
`44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362`.
The peer sends all 102,420 original encoded bytes with full-sized TLS 1.2
records. The exact WebUI asset is served while audio progresses and again
after ordered EOF. These are finite SDK/QEMU integration results, not a
production Wi-Fi, acoustic or independent numerical codec qualification.

## Current successful profiles

| Output | TCP receive window | Receive mailbox | TCP send buffer | Minimum free heap | Allocation failures / OpenETH RX waits |
| --- | ---: | ---: | ---: | ---: | --- |
| PDM | 5,760 | 6 | 2,880 | 2,216 | 0 / 0 |
| Continuous DAC | 5,760 | 6 | 2,880 | 2,928 | 0 / 0 |
| Legacy DAC | 2,880 | 6 | 2,880 | 1,588 | 0 / 0 |

All retain a five-second task watchdog, 300 ms interrupt watchdog, two
cores, the existing task priorities/stacks and hardware-specific DAC/PDM
settings. TLS input/output capacities remain 16,384/4,096 bytes; dynamic
TLS buffers and the separate static-RX-reserve feature are disabled.
Here "static TLS buffers" does not mean the optional static-RX loan.
The normal quiet instrumentation policy is retained. The allocation-failure
callback remains active even though the CPU/stack sampler is disabled.

These small observed heap minima are not margins for extra clients or
all traffic patterns. The profiles remain optional. The ordinary 11,520/10
receive window/mailbox and 5,760-byte send buffer are unchanged, and their
full HE-AAC/WebUI test remains NONPASS. Reduced TCP windows also reduce the
bandwidth-delay budget, so remote high-bitrate and realistic-RTT throughput
need separate qualification. No new production firmware exports are claimed.

## Decoder fairness fix

The original continuous-DAC run triggered IDLE1's watchdog while CPU1 ran
`audio_decode`. Its saved ELF resolves the stack through the public AAC
Huffman/decoder process path. The generic loop previously waited one tick
only after every 32 public process calls. That count did not bound a busy
series of expensive AAC frames when PCM output did not block.

Commit `9029d4140` uses the existing 20 ms elapsed-work budget after each
public process call. When due, it waits two RTOS ticks and rebases after
the wait, then retains the original cancellation check. This leaves a whole
tick opportunity even at a tick boundary; it cannot preempt an individual
codec call. Ogg uses the same extracted helper with its previous behavior.
No decoder arithmetic, private ABI, watchdog feeding or core affinity changes.

The fixed continuous-DAC run completes the entire PCM without a watchdog,
but RX-four with the original send buffer still records one recovered
1,522-byte allocation failure. It remains NONPASS. The smaller send buffer
passes the original zero-allocation-failure gate. Legacy DAC similarly needs
the smaller receive window in the current finite workload. Every failed or
partially successful control retains its original result; full PCM alone
does not turn a resource failure into PASS.

## Matched controls and qualification

The [observations](observed.json) preserve all 14 original terminal runs,
their original reports and raw UART, effective SDK policy, frozen project
translation units, ELF/map/command identities and pinned SDK/vendor revisions.
Project-TU bindings are not presented as a complete compiler dependency closure.
Their `head` field records workspace HEAD at snapshot time; the compiled
project version and exact byte identities are recorded separately.

- Both original and fixed default-window HE runs remain NONPASS on WebUI
  resource pressure. Disabling the sampler alone is insufficient.
- RX-four originally passed on PDM and legacy but failed the continuous-DAC
  idle watchdog. With the scheduling fix, PDM passes, while both DACs complete
  PCM but retain a recovered allocation failure in that profile.
- RX-four/TX-two passes PDM and continuous; legacy's first result still has
  one real allocation failure and is not relabeled. RX-two/TX-two passes
  legacy with the SDK's six-entry minimum mailbox.
- The retained PDM AAC-LC 320 kbit/s control emits all 529,408 frames and its
  exact full reference hash. Current-code TLS/Opus with the original network
  defaults also passes EOF/WebUI with zero allocation failures.
- All 48 current actual AAC-task cases pass, including complete PCM, split
  input, Stop/reopen, maintenance/resume and truthful format observations.
  All 60 decoder handles and 60 HTTP clients close. The witness binds 17 real
  translation units and 459 dependencies, all unchanged at completion.
  Its synthetic transport/output and 20-second diagnostic watchdog are a
  separate scope from these full-application runs.
- The data-only reader rejects 41 contradictory transcripts without
  repeating the native campaign. The real fairness helper passes host
  ASan/UBSan boundary, slow-call and post-wait rebase controls.
- Full PDM Clang-Tidy completes 53 units with zero errors and 100 warnings.
  File/check/message/multiplicity exactly match the previous reviewed catalog.
  Static decoder/Ogg staging frames remain 1,760/2,144 bytes.

The first private RX-two preparation requested a four-entry mailbox. The
pinned SDK's minimum is six, so it normalized that request. Effective six
was verified before the only RX-two target execution. The corrected
reproduction and public overlay explicitly retain six; no four-entry run
is claimed. Original preparation/build evidence remains local and is pinned.

## Reproduction and hardware limits

Start with a fresh normal quiet CYD build and select the backend's own
defaults. For PDM/continuous, combine
`sdkconfig.tcp-rx-four-segments.defaults` and
`sdkconfig.tcp-tx-two-segments.defaults`. For legacy use the RX-two overlay
instead. See the [native build instructions](../../../idf/esp32-cyd2usb-native/README.md).

Fresh configuration-only checks of these published overlay combinations
pass for all three backends. Their exact results and configuration/log
identities are retained in `observed.json` and `qualification/overlay-*.json`.
They verify the effective TCP policy, selected output, two cores and original
watchdogs; they do not add three firmware builds or target executions.

Use [`prepare-profile.py --tls-production-policy`](../../target/cyd_full_app_openeth_qemu/README.md)
to add only the QEMU Ethernet setup and a disposable CA. Enable the PCM,
SHA-256, allocation and RX-backoff diagnostic hooks. Then use
`--codec aac --aac-profile he --through-eof --full-tls-records` with a fresh
result directory. Original keys, complete flash images and diagnostic build
products stay under ignored `.build`.

The byte-accessible IRAM option requires single-core mode in the
[pinned ESP32 SDK configuration](https://github.com/espressif/esp-idf/blob/7101770dc6db2667b3c477cc31365dd1acd6db4e/components/esp_system/port/soc/esp32/Kconfig.memory).
It is excluded because CYD retains both cores and its task bindings. The
normal word-only Ogg storage remains separate. Compact/private AAC and the
extended custom Vorbis branch stay deferred. Physical Wi-Fi/audio and
realistic network throughput await separate tests.
