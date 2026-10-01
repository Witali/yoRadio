# AAC scratch placement experiment — 2026-10-01

`CONFIG_YORADIO_AAC_EARLY_SCRATCH_RESERVE` changes allocation order, not sizes
or decoding arithmetic. It is disabled by default. The full decompilation
shows a 12288-byte scratch workspace allocated after the 35460-byte core and
several smaller objects. In the retained physical baseline, both large objects
land in retention RAM, leaving too small a contiguous region for 55128-byte SBR.

The experiment requests scratch when creating the native ADTS adapter, before
caller PCM and SDK core allocations. TLS slot 1 restricts transfer to that
decoder's synchronous open call; normal SDK close frees the transferred block.
Unused reservations are discarded, early allocation failure falls through to
normal allocation, and failed opening may retry without an unclaimed reserve.
Actual SBR/control OOM becomes an error instead of successful core-only PCM.

**Decoder payload saving: zero.** The adapter gains eight bytes of state on
RV32. The hypothesis is improved placement among existing heap regions. Do not
count the 12 KiB workspace as freed RAM or reduce its size: AAC and SBR both
use it. This option is mutually exclusive with the earlier SBR-reservation and
QEMU layout experiments, and pins the audited Espressif archive SHA-256.

## Quality and ownership checks

Host ASan/UBSan checks execute the real adapter and allocation hooks: zeroed
transfer, task isolation, shaped-allocation mismatch, early failure recovery,
generic/allocation open errors, SBR/control OOM, header reconfiguration, and
cleanup before and after decoding. The shared stream/PCM and real Helix tests
also pass with the default path unchanged.

The RV32 QEMU format sequence emits **328770 stereo frames at 48 kHz after
the existing output conversion, byte-identical** to the retained reference;
maximum error is **0 LSB**. The reference is the earlier reservation run that
was itself checked byte-for-byte against the original control. Its PCM SHA-256
is `4d3ac0894a84dee73509e8a9e726ee2a7a6dc71eee1a46db1f3290b5580caee8`.
This is tested-corpus equivalence, not exhaustive AAC conformance. The existing
implicit LC-to-SBR limitation is still explicitly recorded, not accepted as
full-format playback success.

[Raw QEMU evidence and source fingerprints](../tests/results/esp32c3-aac-scratch-20261001/).

## Reproduce

Build with `sdkconfig.defaults`, `sdkconfig.aac-ram.defaults`,
`sdkconfig.aac-scratch.defaults`, `sdkconfig.cpu-profile.defaults`, and
`sdkconfig.cpu-profile-http.defaults` in that order, in a fresh build directory.
This keeps dynamic Wi-Fi RX/TX at 16 to isolate placement from the six-buffer
experiment. For QEMU, use defaults, `sdkconfig.qemu.defaults`,
`sdkconfig.qemu-aac-reserve.defaults` (format fixtures only), and scratch defaults.

Run `tools/codec_benchmark/run_aac_scratch.py` with `--build`,
`--dependency-root`, `--qemu`, `--bios`, `--wsl`, `--output`, and the retained
`--reference-wav`. Never flash the QEMU image. The saved physical application
is in `firmware/development/esp32c3-aac-scratch-radio/`.

## Physical switching result: rejected as a standalone fix

Three cycles of Opus → LC48 → HE48 → HEv2 complete without reset, with all
six HE/v2 starts failing allocation. Each 55128-byte SBR request sees a largest
block of **53248 B**, with 75128–76164 B free. The adapter correctly reports a
decode failure instead of pretending that reduced-rate core PCM is full HE.
Opus and LC play; settled heap recovers to 144336–144908 B, largest 90112 B.
There is no growing leak in these three checkpoints.

This placement alone is **not a usable HE fix and remains off**. A promising
follow-up is the separately verified lossless PS relocation: its 51596-byte
owner might fit this 53248-byte block. That combination must be implemented
with per-decoder ownership and tested; arithmetic equivalence of each isolated
experiment is not hardware qualification of their combination.

[Physical switching/OTA records](../tests/results/esp32c3-aac-scratch-20261001/hardware/).
The rejected image was replaced after the test. Wi-Fi, playlist and settings
matched before/after OTA; no credential contents are included in evidence.
