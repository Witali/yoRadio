# ESP32-C3: actual PC16 PS delay writes

**Current policy (2026-10-02): production permits +/-3 PCM LSB; development permits +/-5.**
The older acceptance statements below describe the limits at measurement time.
Measured errors and archived evidence are unchanged. See [current precision policy](ESP32C3_AAC_PRECISION_POLICY.md).

## Result

The current Espressif decoder now has an experimental source implementation of
PS delay storage using **16-bit real + 16-bit imaginary mantissas**, with eight
independent four-bit exponents in a separate 32-bit word. Both components share
their pair's exponent. Eight pairs occupy 36 bytes instead of 64, without a
padded structure per pair. This modifies actual within-frame feedback writes,
not just a frame-boundary quantization probe.

All **81 paired comparisons on eleven inputs** pass the temporary ±5 PCM LSB
gate. The maximum is **3 LSB on ABBA**, so the final ±2 gate remains open.
The synthetic HEv2 maximum is 2 LSB. Binary bypass and the uncompressed source
control are bit-exact. No sample-rate or channel limit is introduced.

The experiment is **off by default**: it has no additional heap saving in the
current fixed owner layout, and decoding requires more guest instructions.

## Representation and memory

- Shift = exponent + 1, range 1..16; nearest rounding, ties away from zero.
  Positive rounding carry at the highest shift is clamped and counted.
  No saturation occurred on the retained corpus.
- The four PS delay families contain 617 complex pairs: native payload
  **4936 B → 2780 B**, comprising 2468 B mantissas and 312 B exponent words.
  Payload saving is **2156 B (43.68%, including the partial final group)**.
- Hybrid analysis, energy estimates, mixing coefficients and native DSP
  arithmetic remain unchanged. Real and imaginary pointer tables alias the
  packed spans; the replacement decorrelator is their only delay consumer.
- `CONFIG_YORADIO_AAC_PS_PC16` also requires the experimental per-decoder
  lossless PS relocation. That reduces the enclosing request from 55128 to
  **51596 B**; PC16 adds **zero further heap saving** because full-stereo SBR
  still needs the original channel region. Do not add payload saving to the
  lossless relocation's allocator saving.
- Per-decoder state is kept in the adapter and scoped by FreeRTOS TLS slot 1
  across open/process/close. The physical option has no global owner registry.
  Direct vendor reset remains unsupported; normal close/reopen is used.

## Quality and work

Counts are scalar signed-16 PCM samples per run. Each comparison repeats three
times with identical error counts. Radio captures are not transcoded, normalized
or realigned. Full histograms, error moments, clipping counts and source/input/
binary/configuration hashes are in the
[raw evidence](../tests/results/esp32c3-aac-pc16-write-20261001/).

| Input | PS packed | Maximum error, LSB | Samples beyond ±2 / compared | RMS L / R, LSB | Extra guest instructions |
| --- | --- | ---: | ---: | --- | ---: |
| LC 44.1 kHz stereo | No | 0 | 0 / 98304 | Not collected | +0.000% |
| LC 22.05 kHz mono | No | 0 | 0 / 26624 | Not collected | +0.007% |
| LC 48 kHz stereo | No | 0 | 0 / 106496 | Not collected | +0.000% |
| HE 44.1 kHz stereo | No | 0 | 0 / 114688 | Not collected | +0.000% |
| HE 48 kHz stereo | No | 0 | 0 / 122880 | Not collected | +0.001% |
| HEv2 44.1 kHz stereo | Yes | 2 | 0 / 122880 | Not collected | +32.387% |
| ABBA 64 kbps | Yes | 3 | 178 / 2646016 | 0.276439 / 0.273998 | +42.733% |
| Groove Salad 16 kbps | No | 0 | 0 / 1921024 | 0 / 0 | +0.000% |
| Groove Salad 32 kbps | No | 0 | 0 / 2646016 | 0 / 0 | +0.000% |
| Groove Salad 64 kbps | No | 0 | 0 / 2646016 | 0 / 0 | ~0.000% |
| Groove Salad 128 kbps | No | 0 | 0 / 2646016 | 0 / 0 | +0.004% |

Compared with the earlier 14+14+4 write port, ABBA's samples beyond ±2 fall
from 2542 to 178. More mantissa precision helps but does not prove the final
bound. Groove Salad 16 has no active PS in this decoder despite FFprobe's HEv2
label; it is a control, not additional coverage of compressed PS.

Timing is median QEMU guest instructions from runs 2/3, including wrappers,
assertions and counters. It is not hardware CPU utilization or cache-corrected
time. The native source control adds 6.772% / 7.063% for synthetic HEv2 / ABBA.
No calibration factor is changed. Speed recovery remains required: reduce
packing/dispatch work and assess a small decoded-value cache separately.

## Integration checks

The same allocator/decorrelator also runs through the physical firmware's
per-decoder hooks in QEMU. Ten format segments produce 328770 converted stereo
frames with maximum 2 LSB against the retained lossless relocation output.
This test preserves the known unchanged-header implicit-SBR limitation as a
failure still needing a restart; it is not full-format acceptance.

The lossless relocation alone is bit-exact over those frames, but its physical
three-cycle switching test fails all six HE/v2 starts: the 51596-byte request
sees only a 43008-byte largest block. Total free heap is still 71936–76188 B.
Opus/LC pass, idle heap recovers, and there is no reset. The combined placement
hypothesis therefore did not fix full-radio playback.
[Owner-only evidence](../tests/results/esp32c3-aac-ps-owner-20261001/).

The fast packer produces identical mantissas, exponents and saturation counts
to the previously qualified scalar implementation on 8291457 host pairs under
UBSan, plus 100000 RV32 pairs. Host ASan/UBSan adapter, framing, retry, allocation
failure, task-isolation and cleanup checks also pass. Existing saved PS/reset/
scratch evidence retains its original source snapshots.

Broader streams, same-owner PS/stereo transitions, malformed inputs, long runs,
physical Wi-Fi/OTA stress and final speed/precision remain qualification gates.

## Reproduce

For the paired QEMU suite, build with `sdkconfig.defaults`,
`sdkconfig.qemu.defaults`, `sdkconfig.qemu-aac-packed-history.defaults`, and
`sdkconfig.qemu-aac-pc16-write.defaults`. Run
`tools/codec_benchmark/run_aac_pc16_write.py` with `--dependency-root`, `--qemu`,
`--bios`, `--wsl`, and `--output`; add `--input recording.aac` for unchanged ADTS.
Exit 0 is the development corpus gate, not production approval; inspect
`production_precision_pass` separately. Run `tests/test-aac-pc16-write.py` to
reparse evidence and reject incomplete/corrupted records.

For production-hook integration in QEMU, use defaults, QEMU defaults,
`sdkconfig.qemu-aac-reserve.defaults`, and `sdkconfig.aac-ps-pc16.defaults`.
Run `tools/codec_benchmark/run_aac_pc16_owner.py` with the same runner parameters
and `--reference-wav` pointing to the retained lossless owner output.

The physical development image uses defaults, AAC RAM profile, bounded Wi-Fi,
PC16, CPU profile, and HTTP profile defaults in that order. It is saved under
`firmware/development/esp32c3-aac-ps-pc16-radio/`; never flash a QEMU image.
The private ABI is pinned to the audited Espressif 2.6.2 archive. Licensing and
reference-source attribution follow the [PS write port](ESP32C3_AAC_PS_WRITE_PORT_20261001.md).

## Physical PC16 follow-up and cache

The PC16 image without a decoded-value cache passes 35-second LC48, HE48 and
HEv2 HTTP streams. Measured mean total/decode-task CPU is 36.433/18.617%,
50.517/35.933%, and 68.133/53.883%, respectively. Minimum sampled free/largest
heap is 75624/57344 B, 21316/7680 B, and 21608/7680 B. These are short runtime
counter measurements, not an exhaustive stress or acoustic test.

In the separate 12-switch, three-cycle test, four starts fail: HEv2 in all
three cycles and HE48 in the second. The 51596-byte allocation sees a largest
block of 45056 B, despite 75860–75988 B free. Opus, LC and the other two HE48
starts pass. Idle heap settles at 144728–144736 B, largest 94208 B; there is no
growing leak across these checkpoints. Compression has not fixed fragmentation.
[Physical CPU/heap/switching/OTA records](../tests/results/esp32c3-aac-pc16-write-20261001/hardware/).

After testing, the board was restored by application-only OTA to the previous
uninstrumented bounded-Wi-Fi image, with Wi-Fi, playlist and settings unchanged.
That image's earlier finite/continuous passes do not qualify all switching paths.

The subsequent [288-byte reconstructed-value cache](ESP32C3_AAC_PC16_CACHE_20261001.md)
preserves PCM but increases guest instruction work; it remains off by default.
