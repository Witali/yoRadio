# First-use TLS fragmentation and ten-minute FLAC, 2026-10-10

The follow-up to the [integrated 48 kHz trial](ESP32C3_FRACTIONAL_INTEGRATION_20261010.md)
identifies one persistent **92-byte allocation** inside the initially largest
free region. It explains the observed split of that region after first
HE-AACv2/HTTPS use. The allocating task is `radio_stream` (recorded as
`radio_strea`); its exact calling function is still unconfirmed.

Heavy FLAC completes ten minutes with no observed DMA counter increments or
write errors. The previous WebUI connection timeout does not recur. Four
missing TCP event records prevent qualification of the complete FLAC TCP
trace. Neither absence of a timeout nor this diagnostic image qualifies the
final quiet production image.

## Controlled diagnostic repeat

The existing `idf61-web-tcp-v2` image is reused, with app SHA-256
`991f29dd04a1458fea7adaaa377b5ee2165a6e900c601bd8ffb5e5e165674cbc`.
Its active configuration differs from `idf61-frac4` only by heap hooks,
the heap-owner probe and the TCP probe. These change memory layout and timing,
so this is an attribution experiment, not a matched speed comparison.

Both use full compact AAC/SBR/PS and native rates, QIO 80 MHz, the 17,058-byte
TLS RX reserve, adaptive input, 250/500 ms prefill, four optional extra FLAC
slots and fractional nominal 48 kHz output. Software rate compensation,
FIR and direct-DMA PCM are disabled. Boot readback again verifies the clock
registers, actual QIO/80 MHz and mapped-image CRCs. No firmware code or default
changes are made by this experiment.

| Measurement | HE-AACv2 TLS record growth | Heavy FLAC HTTPS |
| --- | ---: | ---: |
| Observed playback | 75.114 s | 600.002 s |
| Format | 44.1 kHz stereo | 48 kHz stereo, 16-bit |
| Retained status samples | 416 | 3,286 |
| Original test cases | 4/5; idle recovery fails | 6/6 |
| Reported mean CPU | 56.57% | 82.70% |
| Minimum free heap / largest block | 22,208 / 15,360 B | 44,624 / 36,864 B |
| Recorded TCP connect attempts / failures | 475 / 0 | 3,340 / 0 |
| DMA notification increments / write errors | 1 / 0 | 0 / 0 |
| Complete owner snapshots | PASS | PASS |
| Playback TCP trace integrity | PASS within anchors | FAIL: four missing events |

Both fixtures use 1.0x pacing. AAC keeps one TLS connection while plaintext
record sizes grow from 1 KiB to 16 KiB: 118 captured wire records of 1,048 B
and 11 of 16,408 B. No decoder, allocation, TLS, watchdog or reset fault is
recorded. CPU has no acceptance ceiling.

AAC's whole DMA observation spans 70.114 s. The single counter increment lies
between samples at 1.309 and 6.315 s after observation start. A separately
reported interval after the first ten seconds covers 60.096 s with zero
increments. The initial increment remains recorded; it is not erased by
the later window. FLAC's whole counter bracket spans 595.329 s, with 55,817
successful writes and zero increments/errors. These are digital counters,
not acoustic measurements, and do not extrapolate to unobserved edges.

## The retained allocation

Complete snapshots track the initially free range `0x3fcc036c..0x3fcdc70c`.
There are no unknown owners, capture overflows or dropped snapshot rows.
After AAC Stop it contains:

| Address | Raw bytes | Owner |
| --- | ---: | --- |
| `0x3fcc036c` | 9,984 | Free |
| `0x3fcc2a70` | 92 | Allocation ID 32, task `radio_strea` |
| `0x3fcc2ad0` | 105,532 | Free |

The original raw free span was 115,616 B. The largest remaining raw span is
105,532 B. The allocator's rounded maximum-allocation result changes from
114,688 to 102,400 B, failing the unchanged 4,096-byte recovery tolerance.
This is not a 12 KiB payload leak: one small live object splits the region.
It retains the same address and allocation ID after the subsequent FLAC run.
FLAC recovers to its own baseline, which already includes this object.

### Likely cause and next controlled test

The exact candidate ELF's debug information gives `sizeof(Queue_t) == 92`.
Disassembly confirms `xQueueCreateMutex()` requests 92 bytes. In the pinned
SDK, `esp_crypto_mpi_lock_acquire()` delegates to `_lock_acquire()`; libc
creates its mutex lazily. Espressif's own TLS test setup explicitly acquires
and releases this MPI lock before checking memory, explaining that mbedTLS
4.x RSA key validation creates it on first use.

This makes the hardware MPI mutex a concrete hypothesis, **not yet a runtime
identification of allocation ID 32**. The owner probe records task and
lifetime, not the call stack. The matching size alone is insufficient proof.
Pinned SDK sources and exact ELF inspection are included in the archive.

Next, test early acquire/release of this lock before temporary network/audio
allocations. Compare fresh-boot AAC/TLS and settled Stop snapshots, keeping
the original recovery thresholds. Check that the 92-byte retained owner no
longer splits the watched region, repeat handshakes and codec switches, then
verify on the quiet configuration. Do not free a live global SDK mutex or
disable cryptographic locking.

## TCP trace and restoration

AAC's TCP window qualifies 73.685 s between anchors: 1,226 events, 70 listener
samples and 71 watermarks; its 0.511/0.917 s edges remain unqualified.
FLAC is missing event sequences **1836, 2267, 3603 and 10224**. All retained
frames pass CRC, with zero reported ring drops and no observed IP-output
error. Missing complete records still invalidate the full trace; absence
of a failed connection here does not explain the earlier connect timeouts.

The controller restores `idf61-listen48-8c1f2d` in app1 by application-only
OTA. Wi-Fi, playlist and settings compare unchanged in memory; three later
observations confirm the original stopped state. No NVS/filesystem write,
bootloader flash or serial reset is performed.

[Frozen evidence and replay](../tests/results/esp32c3-frac4-attribution-20261010/README.md)
retain original failures, both DMA windows, owner snapshots, transport
metadata and restoration. Replay success verifies evidence, not production
acceptance.
