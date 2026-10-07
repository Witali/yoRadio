# ESP32-C3 PC19: complete real-recording PCM comparison

**All five retained recordings pass the 3-LSB gate:** 12,505,088 signed-16
channel samples, a maximum error of 2 LSB and zero samples above the limit.
This extends [PC19 synthetic qualification](ESP32C3_AAC_PC19_20261004.md).
It does not yet qualify production networking, CPU load, OTA or malformed input.
The board firmware and production defaults have not changed.

## Results

The inputs are the same complete, untranscoded radio captures used in the
[earlier history experiments](ESP32C3_AAC_HIGH_HISTORY_20261003.md), approximately
30 seconds each. SHA-256 hashes are checked against their retained provenance.

| Recording | Profile | Decoded PCM | ADTS frames | Channel samples | Changed samples | Peak error, LSB | RMS error, LSB | Above 3 LSB |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| abba64 | HE-AACv2 | 44.1 kHz stereo | 646 | 2,646,016 | 345 | 2 | 0.013342 | 0 |
| groovesalad16 | HE-AAC mono | 32 kHz, two PCM channels | 469 | 1,921,024 | 384 | 2 | 0.017043 | 0 |
| groovesalad32 | HE-AAC | 44.1 kHz stereo | 646 | 2,646,016 | 0 | 0 | 0 | 0 |
| groovesalad64 | HE-AAC | 44.1 kHz stereo | 646 | 2,646,016 | 0 | 0 | 0 | 0 |
| groovesalad128 | AAC-LC | 44.1 kHz stereo | 1,292 | 2,646,016 | 0 | 0 | 0 | 0 |
| **Total** | | | **3,699** | **12,505,088** | **729** | **2 maximum** | | **0** |

AAC-LC is an unchanged-path control: it does not exercise SBR history storage.
The two HE-AAC stereo recordings decode identically in both images. The measured
differences occur in ABBA HE-AACv2 and Groove Salad 16 HE-AAC mono. All rates and channel
counts are checked on every returned frame; there is no forced 22/24 kHz output.

Profile correction: the original table copied FFprobe's HE-AACv2 classification
for Groove Salad 16. [Reading the native SBR/PS flags](ESP32C3_AAC_METADATA_20261004.md)
confirms HE-AAC mono; two PCM channels do not establish PS. PCM measurements and
the checksummed evidence from the earlier run remain unchanged.

## Method and failure detection

Each image decodes through `native_aac_decoder_process`, the real production
adapter. The candidate has PC19 extra metadata in its decoder context, four-row
smoothing, scoped low-QMF workspace and the asymmetric owner. The reference has
native full-precision sample histories and earlier lossless owner compaction.
Both use the same experimental late-SBR/retention controller.

The host requires complete ADTS framing and counts every frame. The QEMU input
is mapped from the existing disposable app1 recording envelope; no physical
board or network connection is used. Input chunks cycle through 1, 7, 193, 997
and 31 bytes, splitting headers and payloads. Each call feeds two independent
decoders whose PCM buffers have different poison patterns. Returned PCM must
match within the image, and buffer guards must remain intact.

The capture includes every returned sample, starting with the first frame.
The host checks output frame count against ADTS count, frame length against
core/output rates, complete PCM chunks, full input consumption, channel count
and non-silent output. It rejects partial, duplicated, reordered or missing
data. Separate images are compared without alignment, resampling, gain
adjustment, initial-frame exclusion or loop boundaries. Error statistics include
signed histograms, per-frame and per-channel peaks, RMS, bias and exceedances.

The five parser tests deliberately exercise missing/truncated input, absent or
duplicated PCM, incorrect rates and a one-sample 4-LSB failure. Successful
capture alone is not a precision pass: its result explicitly retains
`recording_precision_qualified: false`. The cross-image comparison command
enforces the unchanged limit and exits 2 if any sample exceeds it.

## Memory and regression evidence

Every candidate run also executes the complete existing synthetic gap,
late-activation, reset, concurrent-decoder and allocation-failure tests. The
pointer audit additionally decodes the external input and checks all tracked
allocations have corresponding frees. Total checks per image include both the
synthetic suite and recording, so they must not be reported as recording-only:

| Recording | Pointer checks | Tracked allocations / frees | Minimum free decoder stack |
| --- | ---: | ---: | ---: |
| abba64 | 3,314,243 | 501 / 501 | 2,844 B |
| groovesalad16 | 1,541,081 | 501 / 501 | 2,844 B |
| groovesalad32 | 1,784,111 | 501 / 501 | 2,844 B |
| groovesalad64 | 1,783,451 | 501 / 501 | 2,844 B |
| groovesalad128 | 1,351,217 | 495 / 495 | 2,844 B |

All ten image runs finish with valid heap and the QEMU smoke completion marker.
These isolated tests do not establish sufficient heap with Wi-Fi/TLS active or
physical CPU/cache performance. The earlier measured 144-byte PC19 increment
and audited instruction overhead are documented separately; this capture does
not claim a new speed result.

## Evidence and reproduction

[Saved evidence](../tests/results/esp32c3-aac-pc19-recordings-20261004/) includes
per-frame/per-channel error distributions, input and PCM hashes, build configs,
ELF/archive hashes, patch audits, source snapshots and diagnostic logs. The
real-recording PCM hex lines are removed from archived logs; their original log
hash, removed line count and PCM byte count are recorded. Source captures and
complete raw logs remain in ignored local test directories. They are necessary
to reproduce the sample comparison; the committed statistics alone do not
constitute an independent PCM re-decode.

Build the reference/candidate configs in separate directories as in the
[PC19 guide](ESP32C3_AAC_PC19_20261004.md), using the configs saved with this
recording experiment. With the existing ESP-IDF Python/QEMU environment:

```powershell
python tools/codec_benchmark/run_aac_recording_capture.py --build <candidate-build> --dependency-root C:/Work/yoRadio/.idf --input <capture.aac> --ffprobe <ffprobe.exe> --qemu <qemu-system-riscv32> --bios <qemu-share> --wsl --output <candidate-output>
python tools/codec_benchmark/run_aac_recording_capture.py --full-precision --build <reference-build> --dependency-root C:/Work/yoRadio/.idf --input <capture.aac> --ffprobe <ffprobe.exe> --qemu <qemu-system-riscv32> --bios <qemu-share> --wsl --output <reference-output>
python tools/codec_benchmark/compare_aac_recording_pcm.py --input <capture.aac> --reference-log <reference-output>/qemu.log --candidate-log <candidate-output>/qemu.log --output <comparison.json>
python tests/test-aac-recording-capture.py
python tests/test-aac-recording-evidence.py
```

Use shell-appropriate paths in place of the angle-bracket placeholders. The
capture runner writes only a disposable emulator image. Stored commands and
input hashes identify the actual runs. Evidence tests verify histograms,
provenance, frame totals, pointer results and omission of captured music PCM;
they do not replace the cross-image PCM gate.

Remaining work: correct HE-mono versus PS metadata using decoder state; exercise
malformed extensions and allocation failure at late activation; integrate and
qualify the changes on the physical board with CPU/heap, HTTP/HTTPS, repeated
station switching, OTA and all supported codecs. Broader AAC profile/rate and
framing coverage remains necessary; these five captures are not all-format
conformance evidence.
