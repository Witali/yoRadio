# Portable custom FLAC transfer to native CYD

Status: **CYD runtime integration is implemented behind an explicit Kconfig
choice; Espressif remains the default**. Actual CYD decoder-task host tests and
the pinned Xtensa integration/component compilation pass. Custom-path target
execution, complete application exports and physical CYD A/B remain open gates.
This is stage CYD-C3-12 of the [transfer plan](ESP32_CYD_C3_TRANSFER_PLAN.md).
Default CYD configurations continue using the Espressif FLAC backend. This port
preserves display/board pins, audio backend, decoder/output task cores, priorities
and stack budgets.

## Source entry points

| Purpose | Current implementation |
| --- | --- |
| Shared decoder, workspace allocation and cleanup | [flac_decoder.cpp](../yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp), `FLACDecoder_AllocateBuffers`, `FLACDecoder_FreeBuffers` |
| Bounded bit reader, Rice, signed sample validation and PCM conversion | [flac_decoder.cpp](../yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp), `readUint`, `readRiceSignedInt`, `FLACDecode`, `decodeSubframe` |
| Stereo decorrelation, wide LPC and segmented history | [flac_decoder.cpp](../yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp), `decodeSubframes`, `restoreLinearPrediction` |
| Shared streaming adapter and API | [custom_flac_adapter.cpp](../idf/components/custom_flac/custom_flac_adapter.cpp), [custom_flac_adapter.h](../idf/components/custom_flac/custom_flac_adapter.h); historical C3 paths remain thin compatibility includes. |
| Adapter build definitions | [custom_flac/CMakeLists.txt](../idf/components/custom_flac/CMakeLists.txt): segmented workspace, 512 output frames, optional bytewise Rice |
| Platform compatibility headers | [custom_codec_support/Arduino.h](../idf/components/custom_codec_support/Arduino.h); native builds use internal heap, `psramFound()` is false |
| C3 PCM16 versus source metadata example | [audio_service.c](../idf/esp32c3-oled-native/main/audio_service.c), `custom_flac_output` and the FLAC branch of `decoder_task` |
| CYD decoder lifecycle, generation and maintenance | [audio_service.c](../idf/esp32-cyd2usb-native/main/audio_service.c), `decoder_task`, `packet_done`, `maintenance_ack` |
| CYD format publication and PCM queue | [audio_service.c](../idf/esp32-cyd2usb-native/main/audio_service.c), `publish_stream_info`, `send_pcm` |
| CYD output representation | [native_audio_output.c](../idf/esp32-cyd2usb-native/main/native_audio_output.c), `native_audio_output_supports_pcm`, `pcm_sample_to_s16` |
| CYD task stack and board profile | [board_config.h](../idf/esp32-cyd2usb-native/main/board_config.h), pipeline task table in `audio_service.c` |

The shared decoder is portable C++ integer code; it contains no RISC-V assembly.
Its state and sample workspace are global, despite the adapter's opaque instance
handle. Exactly one decoder owner may use it at a time. The existing serialized
decoder task can provide this ownership; destroy the previous decoder before
creating/feeding its successor. Do not introduce concurrent adapter instances.
`custom_legacy_codecs` is a separate AAC/MP3 component and does not implement FLAC.

## Supported profile and compatibility boundary

Custom FLAC accepts source depths 4 through 24 bits, mono/stereo, and blocks up
to 8192 samples. It reconstructs samples and stereo side channels at their source
precision, uses wide LPC accumulation, and converts the final output to signed
16-bit PCM. This output conversion discards lower source bits above 16; it does
not deliver lossless 24-bit PCM to the output device.

The pinned Espressif codec package at
`.idf/esp-adf-libs/esp_audio_codec/README.md`, FLAC section, documents 16/24/32-bit
decoding, 1–8 channels and 8–192 kHz. These vendor capabilities are broader than
the custom profile; the CYD output path imposes additional device limits. Keep
an explicit vendor/custom choice and test the retained vendor path. A default
change requires CYD qualification. Automatic fallback after custom consumption
requires replayable encoded input and explicit ownership; silently switching
after partial decode is not a complete design.

The generic CYD `publish_stream_info` describes the vendor's PCM representation.
The custom `custom_flac_output` callback publishes the original 4–24-bit source
depth separately, validates `pcm_bits_per_sample == 16`, and passes PCM16 to
queue sizing, frame alignment, duration accounting and output. Thus 4/12/20-bit
source is accepted without describing a 24-bit source buffer as PCM24.

`YORADIO_FLAC_DECODER` selects `YORADIO_FLAC_DECODER_ESPRESSIF` by default;
`YORADIO_FLAC_DECODER_CUSTOM` is an explicit opt-in. The latter bypasses vendor
FLAC registry registration and feeds the shared adapter directly. The shared
component is an unconditional CMake dependency because ESP-IDF expands component
requirements before loading Kconfig; its runtime calls remain conditional. The
vendor path and custom AAC/MP3 combination retain their independent selection.

Native Ogg FLAC mapping, complete malformed-stream conformance, frame CRC/MD5
validation, source depths above 24 and mid-stream format changes are not qualified
features of this custom adapter. The core checks that the frame footer exists;
that is not CRC value verification. STREAMINFO total samples are not an exact
end-of-audio validator here. These are existing boundaries, not completed work
or new regressions attributed to the CYD transfer.

## Memory and scheduling

The segmented workspace uses up to two channels × 8192 samples × 4 bytes =
65536 bytes, in allocations no larger than 4096 bytes. This reduces the largest
individual allocation; it does not reduce total sample precision or workspace.
The adapter separately permits a known frame window up to 65536 bytes plus
512 input bytes; an unknown maximum frame size uses a 32768-byte window. Metadata
is also bounded. Streams exceeding these policies are not universally supported.
The 512-frame stereo callback buffer consumes 2048 bytes of decoder task stack.
Object/allocator overhead and nested call stack are additional costs.

Do not copy C3 input growth, TLS reserve, DMA geometry, cache settings or IRAM
choices as part of the decoder port. CYD has TFT/DMA/TLS allocations and two CPU
cores. Preserve the current task table: network/stream on core 0, audio decoder
and output on core 1. Measure free heap, largest free block, minimum stack margin,
decode time, queue progress, DMA reuse and watchdog behavior on both CYD audio
profiles. Host heap totals and QEMU instruction counts are not physical capacity
or timing evidence.

## Donor metadata EOF prerequisite

The original adapter returned `1` (needs more input) for a partial signature,
metadata block header or metadata payload even when the caller declared EOF.
C3's terminal packet path then destroyed the decoder without treating that
positive result as decode failure. An actual adapter/core executable reproduced
this with `feed("fLaC", 4, true, ...)` and with every cut of a 1077-byte metadata
chain, including a separate zero-byte EOF.

[RFC 9639 section 6](https://www.rfc-editor.org/rfc/rfc9639.html#section-6)
defines the signature/metadata/audio sequence;
[sections 8 and 8.1](https://www.rfc-editor.org/rfc/rfc9639.html#section-8)
define required STREAMINFO, metadata lengths and the last-block flag. The RFC
does not specify this C API's error result. The adapter policy is explicit:
incomplete metadata may request more data while the stream is open, but must
return `ERR_FLAC_TRUNCATED_INPUT` after its final internal chunk when EOF is set.

The narrow fix changes only that decision in `custom_flac_decoder_feed`. It
handles inline and separate empty EOF, waits through earlier 512-byte internal
chunks of the same final call, and preserves complete metadata-only behavior.
It does not add frame checksum, sample-count or full-stream completion checks.

The new actual regression is
[main.cpp](../tests/native/flac_stream_eof/main.cpp), run by
[run-flac-stream-eof.py](../tests/run-flac-stream-eof.py). It compiles the real
production adapter/core with existing timer/log/FreeRTOS/Arduino host seams.
The old adapter is compiled from an exact Git revision as an executable negative
control; it is not represented by a fake decoder or a changed test assertion.

The [separate EOF campaign](../tests/results/flac-stream-eof-20261018/README.md)
records 5387 passing current groups: every one of 1077 metadata cuts with
inline/empty EOF and whole/fragmented prefixes, 1077 exact-PCM continuation
cases, and two complete-metadata controls. The executable old adapter records
4308 failures on the same EOF checks. Another 120 valid files × three schedules
× current/old adapters give 720 complete PCM comparisons against known encoder
PCM and fresh FFmpeg, with no PCM changes. Both variants use the frozen current
shared core; this is an adapter regression control, not a whole historic
firmware reconstruction. ASan/UBSan are enabled throughout.

## Existing evidence and missing gates

The new [CYD runtime campaign](../tests/results/cyd-flac-runtime-20261019/README.md)
executes the actual production `decoder_task`, callback, `send_pcm`, native state,
shared streaming adapter and segmented core under ASan/UBSan. Its 130 valid
fixtures × four schedules give 520 exact PCM comparisons against deterministic
encoder PCM and fresh FFmpeg. Source depths 4/8/12/16/20/24, mono/stereo and stereo
decorrelation, four subframe forms, 8192 blocks and short tails are represented.
It also checks 4304 truncated metadata schedules, an empty-stream control,
24 persistent allocation failures followed by 24 exact-PCM reopens, unknown and
maximum frame windows, rejected oversized frame windows, codec replacement,
nonterminal codec drain, generation cancellation and maintenance during three
blocked queue attempts. A same-generation maintenance control explicitly checks
workspace cleanup before ACK. Three executable semantic mutants demonstrate
the source/PCM distinction and terminal/ACK cleanup assertions. Actual registry
functions exercise both selections and every registration failure rollback.

The FIFO, blocking scheduler, vendor/legacy codec calls and heap-failure injector
are explicit host seams. The custom FLAC decode is real; the vendor binaries and
RTOS scheduler do not execute in this host test. Six retained vendor/legacy task
variants pass the existing lifecycle regression separately. The SDK evidence
compiles the actual integration in both explicit custom and untouched-default
vendor configurations, compiles the real custom adapter/core, and checks object
symbols for selected ownership. These are software/compilation results, not an
application link, Xtensa PCM execution or physical performance qualification.

The latest warning-fix campaign's
[depth report](../tests/results/native-warning-fixes-20261018/flac-depths/report.json)
contains 120 deterministic fixtures × segmented core / contiguous core / streaming
adapter = 360 exact PCM comparisons against known PCM and fresh FFmpeg output,
with ASan/UBSan. It also contains 456 persistent C allocation failures followed
by successful reopen/PCM checks. Current core/adapter implementation hashes match
that campaign; the current header additionally guards the GCC optimization pragma
from Clang. The old report is not an exact snapshot of that changed header.

Earlier [depth qualification](ESP32C3_FLAC_DEPTHS_20261005.md) covers large 8192
blocks, 24-bit stress files and short tails;
[bounds](ESP32C3_FLAC_INPUT_BOUNDS_20261005.md),
[predictor](ESP32C3_FLAC_PREDICTOR_20261006.md) and
[hot-loop](ESP32C3_FLAC_HOTLOOPS_20261008.md) suites cover truncated core inputs,
wide side samples, LPC coefficients/shifts, segment boundaries and Rice state.
Evidence replay scripts validate archived results; they must not be reported as
a new decode of current firmware. The positive streaming matrix did not cover
EOF inside metadata; the new prerequisite suite fills that gap.

The existing C3 `qemu_codec_calibration.c` FLAC entry registers
`esp_flac_dec_register` and exercises vendor calls/counts/layout. It does not run
the custom streaming adapter or prove its exact PCM on Xtensa. Existing C3
physical HTTP/HTTPS, truncation and recovery evidence also does not qualify CYD.

Keep bytewise Rice and restricted LPC auto-unrolling experiments disabled by
default. The [physical C3 Rice study](ESP32C3_FLAC_RICE_PHYSICAL_20261008.md)
found worse decode progress/DMA behavior despite favorable host/RV32 object
measurements. LX6 requires its own paired measurements before any optimization
claim or default change.

## Remaining implementation plan

1. **Shared component complete:** one canonical adapter/API/build recipe is
   exposed to both projects; the core and adapter algorithms retain their bytes.
   [Fresh qualification](../tests/results/custom-flac-transfer-20261018/README.md)
   repeats5387 EOF groups/720 PCM comparisons and compiles the actual component
   on pinned RISC-V/Xtensa SDKs. CYD vendor/custom selection is now implemented.
2. **Software complete:** the CYD callback separates source depth and PCM16;
   create/feed/destroy cover generation changes, codec replacement/drain, errors,
   EOF and maintenance. The single decoder-task owner frees workspace before
   publishing a released generation or maintenance ACK; task affinity is retained.
3. **Host complete for the stated profile:** actual CYD task/real-adapter tests
   cover metadata EOF, terminal errors, blocked send cancellation, generation
   changes, reopen, allocation failures and frame-window policy. The retained
   vendor path has regression coverage; its host codec calls remain doubles.
4. **Application matrix complete:** [six full GCC exports](../tests/results/cyd-network-settings-20261020/SDK.md)
   cover vendor/custom FLAC with PDM, continuous DAC and legacy DAC from clean
   source `195cd3b0e`. ELF symbols verify the selected decoder; custom changes
   exactly the two FLAC configuration selectors.
5. **SDK/QEMU adapter and core complete for the stated profile:** the
   [standalone Xtensa harness](../tests/target/cyd_flac_qemu/README.md) runs
   unchanged production components with real SDK tasks on cores 0/1. Its
   [frozen qualification](../tests/results/cyd-flac-qemu-20261020/README.md)
   preserves 520 unique byte-exact PCM16 comparisons and 48 guard/recovery
   checks, final image/configuration/source hashes and terminal emulator exit 0.
   Six source depths and four input schedules are covered. This is a synthetic
   decoder owner with an isolated debug profile, not full-radio resource data.
6. **Actual CYD task target gate open:** run unchanged `audio_service.c` via
   public startup/play/stop/maintenance APIs with all three real SDK task owners.
   First cover ordered EOF/PCM identity, Stop/reopen and maintenance/resume;
   then backpressure/errors, scoped OOM and deliberate target semantic controls.
   HTTP transport and output hardware need explicitly bounded seams. No test
   may assign the private phase or ACK instead of executing its actual owner.
7. **Physical qualification open:** CYD A/B with matched
   configuration, all three audio output backends, ordinary/demanding FLAC, HTTP/HTTPS,
   UI traffic, EOF/Stop recovery, repeated codec changes, DMA and watchdog metrics.
   No custom default switch or speedup claim before this gate passes.

The portable donor EOF fix and its evidence are a prerequisite to these steps;
they do not close stage CYD-C3-12.
