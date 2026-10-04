# Scoped low-QMF: physical adapter qualification (incomplete)

`CONFIG_YORADIO_AAC_LOW_WORKSPACE` enables the
[QEMU-checked low-QMF layout](ESP32C3_AAC_LOW_QMF_WORKSPACE_20261003.md) in a physical
radio build. Select `sdkconfig.aac-low-workspace.defaults`. It also selects the
compact SBR owner, PC18 high history and four-row smoothing. The option is
disabled by default while full-radio qualification continues.

The owner requests 35,900 instead of 45,932 bytes, saving **10,240 allocator
bytes** per active SBR decoder. A 10,240-byte temporary matrix uses the existing
16 KiB decoder stack. Native int32 SBR/PS arithmetic, all eight retained history
rows, full output rates and both channels remain available. No additional
quantization is introduced by this change.

## Build and QEMU verification

The physical build's configuration differs from the preceding installed
smoothing candidate only by `CONFIG_YORADIO_AAC_LOW_WORKSPACE=y`. Deep sleep and
Flash Auto Suspend remain disabled; Flash uses DIO/80 MHz. The image has no
pointer-audit registry, test interleaving, low-workspace reporting or QEMU test
symbols. The wrapper's compiled stack frame is 10,304 bytes, including the
matrix, canaries and its other local state.

The production path omits the emulator's transient-row poison fill. That path
passed the complete six-run QEMU pointer/lifetime/PCM suite: 657,540 synthetic
control samples remain identical to the prior adapter, and all five recordings
retain their full-output hash and 12,505,088 total channel samples. Concurrent
decoders, failed allocations, reset/reopen, exact stack-object bindings and
the six intentional low-pointer errors are still exercised by the QEMU harness.
The production-path runs total 2,583,444 address/range checks, 161,368 SBR
copies, 929 allocations matched by 929 frees, and 4,845 scoped low-QMF matrices.
This is a boundary/ownership audit, not instrumentation of every native
load/store. The unchanged-header implicit SBR/PS restart limitation remains.

The successful physical image is saved under
[`firmware/development/esp32c3-aac-low-workspace`](../firmware/development/esp32c3-aac-low-workspace/manifest.json).
Its application ELF SHA-256 is
`5ba3d98ec9a10e0f28be59e5799767e56e106fd85c8d036081c7472e2ac2b8c4`.
This is an awake development image, not a versioned release.

## Controlled physical A/B measurement

The same board played the same synthetic AAC streams for 40 seconds per case,
with repeated WebUI status requests, before and after OTA. Both three-case
suites and restoration passed. Values below use the existing summarizer's
5–35 second window after the first PCM checkpoint; they are distinct from
the acceptance runner's own warmup window. CPU percentages are FreeRTOS runtime
measurements on the board, without an emulator correction factor.

| Stream | Decoder CPU before / after | Whole-radio CPU before / after | Minimum free heap before / after | Largest free block before / after |
| --- | ---: | ---: | ---: | ---: |
| AAC-LC 48 kHz stereo | 19.283 / 19.250% | 47.167 / 47.467% | 76,280 / 76,564 B | 65,536 / 65,536 B |
| HE-AAC 48 kHz stereo | 38.050 / 38.183% | 61.183 / 62.150% | 28,096 / 36,764 B | 18,432 / 28,672 B |
| HE-AACv2 44.1 kHz stereo | 42.867 / 42.533% | 63.217 / 66.450% | 28,348 / 38,792 B | 18,432 / 27,648 B |

There is no material decoder CPU regression in this A/B run. Whole-radio CPU
also includes Wi-Fi, HTTP and output work and is higher in the HE cases; one
pair of runs does not isolate every cause or establish a universal speed bound.
The smallest sampled decoder stack headroom changes from **12,976 to 2,824
bytes**, both from the same 16,384-byte stack allocation. Network allocations
vary, so sampled total free-heap changes need not equal the exact owner saving.

## OTA and remaining qualification

The initial WebUI OTA transition while AAC-LC played passed in **21.390 s**.
The running target hash was verified and Wi-Fi, playlist and settings remained
unchanged. The three subsequent OTA updates also pass: app0 to app1 in
20.921 s, back to app0 in 21.625 s, and to app1 while playing in 21.032 s.
Each verifies the running hash and unchanged settings; serial health and the
final restore pass. The final board snapshot confirms the target image and
resumed saved-station playback. These four successful transfers are bounded
checks, not a long-duration OTA soak or every malformed-upload case.

All **18 local playback/EOF cases** pass: automatic and explicit codec selection
for MP3 320 kbit/s, FLAC level 8, Vorbis q10, Opus 510 kbit/s, AAC-LC 320 kbit/s,
AAC-LC 22.05 kHz mono, HE-AAC 44.1 and 48 kHz stereo, and HE-AACv2 44.1 kHz
stereo. The runner verifies the decoded profile/rate/channels and that finite
playback stops. It is not an acoustic measurement or a rerun of every malformed
input and EOF-metadata regression. The captured local run has no decoder,
allocation or panic error and leaves at least **2,828 B** of decoder stack.
Restoring the saved station also passes.

The smaller owner must still meet full-radio acceptance, including the public
HE-AAC cases that failed on the preceding image. A successful short local test
does not close those failures or qualify all supported formats. Do not promote
the build or treat failed playback windows as passing CPU benchmarks.

The first new HTTPS matrix already identifies a remaining allocator problem:
the 64 kbit/s case reports three failed 1,700-byte allocations. At those events
free totals are 11,004, 9,168 and 7,568 B, but the largest block is only 1,664 B.
Its completed CPU windows do not turn that playback result into a pass. The
32 kbit/s HE-AAC case passes; the 16 kbit/s test ends early on a WebUI transport
error after about 22 seconds, with PCM still reported before the error and no
allocation failure captured in that window. The transport failure is not
silently attributed to the codec or counted as success.

The HTTP matrix also retains a WebUI transport failure for 64 kbit/s HE-AAC
after about 52.5 seconds of observation, without any captured allocation or
panic error. Its other four public streams pass. The same HTTP 16 kbit/s source
reports HE-AACv2, 32 kHz stereo and passes; it is not interchangeable with the
older retained 16 kbit/s mono capture. These short runs show improved coverage,
but do not establish the cause of the two transport failures.

| Public stream | HTTP, up to 60 s | HTTPS, up to 60 s |
| --- | --- | --- |
| Groove Salad AAC-LC 128 kbit/s | PASS | PASS |
| Groove Salad HE-AAC 64 kbit/s | FAIL: WebUI `URLError` | FAIL: three 1,700 B allocation failures |
| Groove Salad HE-AAC 32 kbit/s | PASS | PASS |
| Groove Salad HE-AACv2 16 kbit/s | PASS | FAIL: WebUI `URLError` |
| Groove Salad MP3 256 kbit/s | PASS | PASS |

Both public suites recover to idle and restore the previous board settings.
Neither serial log contains a captured panic. A failed or shortened window is
not a passing CPU benchmark, even if earlier PCM and CPU samples were valid.
The smallest recorded decoder stack margin across these public runs is
**2,728 B**; the same 16 KiB decoder stack is used for all codecs.

## Retained evidence and reproduction

[The evidence directory](../tests/results/esp32c3-aac-low-production-20261003/)
contains raw technical status/performance records, actual PASS/FAIL reports,
matched A/B summaries, build checks, six QEMU logs and exact implementation
snapshots. `implementation.json` hashes those files. The saved firmware
manifest identifies the application binary and complete hardware configuration.

Run `python tests/test-aac-low-production.py` to verify these records. It
recomputes A/B and public-window summaries, checks firmware/configuration
fingerprints and compares actual synthetic PCM with the preceding adapter.
The test also requires retention of the known public failures. A passing
evidence-validation test does not promote this image.

For QEMU, follow the preceding low-QMF report, but select
`sdkconfig.aac-low-workspace.defaults` and
`sdkconfig.qemu-aac-pointer-audit.defaults` instead of the QEMU low-workspace
default file. Ensure `CONFIG_YORADIO_QEMU_AAC_LOW_WORKSPACE` is disabled, then
pass `--production-path` to `run_aac_low_workspace.py`. This exercises the
production storage path without transient-row poisoning, with audit checks
still enabled in the emulator. The physical image excludes those audit checks.

The board runners are `diagnostic.py run --suite load` for the three matched
AAC load cases; `diagnostic.py run --suite http` for the finite local files;
`public_streams.py --transport http` and `--transport https` for public streams;
and `ota_diagnostic.py --suite roundtrip --suite while-playing` for repeat OTA.
Supply the board/host addresses, serial port, matching saved firmware or
sdkconfig, and separate output directories as documented in
[ESP32-C3 testing](ESP32C3_TESTING.md). Public windows use 60 seconds and a
0.1-second request interval. Run device-controlling suites sequentially.

## Next lossless allocation candidate

The [asymmetric-owner follow-up](ESP32C3_AAC_ASYMMETRIC_OWNER_20261003.md)
implements this candidate in QEMU. Moving each channel's smoothing tables into a common
prefix produces a 32,744 B owner and a measured further 4,096 B allocator saving.
All six pointer/PCM runs pass; the [physical follow-up](ESP32C3_AAC_ASYMMETRIC_PRODUCTION_20261004.md)
now records ordinary firmware integration and hardware qualification. The
original estimate and required consumer audit below explain the starting point.

A target-compiled size probe finds `aac_high_frame_t=14680`, channel prefix
16 B, smoothing pointer tables 80 B, and `aac_high_channel_t=17940`. The channel
union is sized for the 15,556-byte PS overlay plus its 2,304-byte synthesis
array, even for the left channel. The live PS overlay is on the right channel.
The left frame, prefix and smoothing tables need 14,776 B; the difference is
**3,164 B**. An asymmetric owner could request **32,736 B** instead of 35,900 B,
potentially crossing another 4 KiB allocator boundary. This is a candidate,
not an implemented or measured saving.

Before changing it, separate the following native and typed-code consumers:

1. `sbr_open` currently uses one channel size both as memset length and loop
   stride, terminating at the PS control fields. A smaller left view needs
   distinct initialization lengths and a verified loop termination rule.
2. `sbr_read_data` advances channel frames by that same fixed stride and uses
   the embedded-PS address as its loop end. The frame-loop sentinel must be
   distinguished from the actual PS detection-word address.
3. `sbr_applied`, `ps_allocate_decoder`, the top-level decoder and reset/reopen
   wrappers must use the new right-channel, PS, synthesis and control offsets.
4. `channel[2]` in typed views and every smoothing-table lookup must become
   explicit named left/right accessors. Preserve the identical frame prefix
   used by the scoped low bindings and the right PS reset exclusions.
5. Require the complete pointer/copy audit, exact PCM, concurrent instances,
   allocation failure/reset tests, measured block saving and physical network
   acceptance. Do not overlap live PS state merely to match a desired size.
