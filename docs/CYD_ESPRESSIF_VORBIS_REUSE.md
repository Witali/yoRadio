# Reuse of Espressif Vorbis on CYD

The custom extended-standard decoder is
[deferred](CYD_VORBIS_EXTENDED_DEFERRED_20261028.md). Its sources and results
remain on `codex/esp32-cyd-c3-review` at `fffe2bed5`. Further vendor integration
uses `codex/cyd-espressif-vorbis` in the existing isolated task worktree.

## Existing implementation

CYD already registers Espressif Vorbis and Opus in
[decoder_registration.c](../idf/esp32-cyd2usb-native/main/decoder_registration.c).
[audio_service.c](../idf/esp32-cyd2usb-native/main/audio_service.c) selects
`ESP_AUDIO_SIMPLE_DEC_TYPE_OGG`, opens the public simple decoder, passes stream
chunks to `esp_audio_simple_dec_process`, queries each PCM frame's format and
copies the PCM into the output queue. The Ogg parser provides complete encoded
packets to the vendor frame decoder. No new raw-packet decoder is required for
this existing path.

Both setup scripts pin `esp-adf-libs` revision
`67b8d0e98f58c774b8652480893037273190e8dc` (component version 2.6.2).
The public interface and creator's example at that revision are the contract:

- [Simple decoder header](https://github.com/espressif/esp-adf-libs/blob/67b8d0e98f58c774b8652480893037273190e8dc/esp_audio_codec/include/simple_dec/esp_audio_simple_dec.h).
- [Creator's streaming example](https://github.com/espressif/esp-adf-libs/blob/67b8d0e98f58c774b8652480893037273190e8dc/esp_audio_codec/test_apps/audio_codec_test/main/simple_decoder_test.c).
- [Vorbis frame decoder header](https://github.com/espressif/esp-adf-libs/blob/67b8d0e98f58c774b8652480893037273190e8dc/esp_audio_codec/include/decoder/impl/esp_vorbis_dec.h).

On `ESP_AUDIO_ERR_BUFF_NOT_ENOUGH`, the creator's simple-decoder example
grows the output buffer and retries before advancing the input pointer. CYD
already follows that contract. C3 advances consumed input in this situation
only for its separate native AAC adapter; copying that special case into the
vendor Ogg path would change the retry contract.

## Hardware and build selection

| Property | CYD | C3 donor |
| --- | --- | --- |
| Processor | Dual-core Xtensa LX6 | Single-core RV32IMC |
| Vendor library directory | `lib/esp32/` | `lib/esp32c3/` |
| Current SDK | ESP-IDF 6.0.2 | ESP-IDF 6.1, pinned revision |
| Production stream task | Core 0, priority 3, stack 6144 | Core 0 |
| Production decoder task | Core 1, priority 5, stack 16384 | Core 0 |
| Production output task | Core 1, priority 6, stack 4096 | Core 0 |

Both builds enable `AUDIO_DECODER_VORBIS_SUPPORT` and
`AUDIO_SIMPLE_DEC_OGG_SUPPORT`. Each target links its own archive; the RV32
archive is not a binary-compatible replacement for the Xtensa archive.
Public headers are shared, while private owner layouts and linker wrappers
are outside this reuse step.

Audited archive SHA-256 values:

| Target | Archive | SHA-256 |
| --- | --- | --- |
| ESP32 | `libesp_audio_codec.a` | `92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58` |
| ESP32 | `libesp_audio_simple_dec.a` | `ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6` |
| C3 | `libesp_audio_codec.a` | `311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909` |
| C3 | `libesp_audio_simple_dec.a` | `232650ec81ae5e10ecbe1b2c86de2d1adf8f1b793f5ef343241c6e510db3e71f` |

## Applicable C3 improvements

CYD now yields one scheduler tick after every 32 simple-decoder process calls,
including calls that only consume headers and produce no PCM. The counter
survives input-packet boundaries, so small network chunks cannot prevent the
yield. A generation check after processing/yielding prevents a concurrent Stop
from publishing that result. Normal PCM queue backpressure continues to block
the decoder as before. This bounds the number of calls between scheduling
opportunities; it does not bound the duration of an individual vendor call.

Opening the simple decoder now preserves the distinction between
`ESP_AUDIO_ERR_MEM_LACK` and other errors. Only the former reports an allocation
failure; unsupported or invalid decoder setup reports a decode failure and
retains the original numeric error in health diagnostics. Opaque custom
factories still report allocation failure when returning `NULL`.

The direct public decoder experiment also found that a successful call can
leave a short input prefix unconsumed and produce no PCM. CYD now retains that
exact suffix and appends the next packet before retrying. The shared
[pending-input owner](../idf/components/native_stream/include/decoder_pending_input.h)
borrows normal packets directly and allocates only for such a retained suffix.
An explicit ownership flag selects copy versus in-place move; no comparison
between unrelated pointers is needed. Checked allocation and the public API's
32-bit input length remain resource/representation limits rather than format
clipping. Stop, codec changes, terminal completion and maintenance clear the
owner. A remaining suffix at EOF without progress fails explicitly instead
of looping forever.

C3 uses the same owner through a local forwarding header, only in its vendor
decoder branch. Its native AAC consumed-on-resize and zero-input PCM retry
remain separate. Pending storage participates in generation/codec/error/EOF
cleanup and the maintenance release predicate.

The whole CYD task test found another public-boundary difference: with all
703,584 encoded bytes consumed, supplying EOS only in a later empty control
packet returned 2,110,464 PCM bytes instead of 2,112,000. A read-only trace
confirmed that the deficit already existed at the vendor output, before the
PCM queue. No input bytes were lost and no decoder/allocator error occurred.

CYD now keeps one encoded Ogg byte until it knows whether more data or EOF
follows. At EOF that actual final byte carries `eos=true`. At most two borrowed
segments are processed; the lookahead itself allocates no heap and does not
concatenate ordinary packet bodies. Empty draining continues until both input
consumption and decoded PCM are zero. Generation/codec changes, errors, Stop
and maintenance clear the held byte. The vendor archives, other codec paths,
12,288-byte output buffer and task profiles are unchanged. This new adapter is
selected in the CYD Ogg caller; C3's existing private repair stays unchanged.

These changes preserve the production task affinities, priorities, stacks,
display configuration and audio backend selection. They do not enable the C3
private Vorbis repair, custom numerical components or old deferred experiments.

## Qualification boundaries and next steps

The lifecycle host suite executes the production decoder/output task bodies
against explicit platform/codec seams under ASan/UBSan. It checks scheduling,
cancellation, error propagation and ownership; it does not execute Espressif's
binary decoder. A separate valid-stream SDK/QEMU diagnostic exercises the
unchanged target-specific vendor libraries through their public Ogg API.

The historical C3 lifecycle test made only one empty-EOF process call. Its
2,107,648-byte PCM result omits 1,088 stereo frames from this fixture's final
granule of 528,000. The new diagnostic keeps that exact historical output as a
mandatory prefix and separately requires the full 2,112,000-byte result. A
matching full digest across schedules/architectures is an integration regression
identity; it is not an independent numeric oracle for the newly drained tail.
First-use retained heap is reported separately from stable repeat-stream heap.

[Host evidence](../tests/results/cyd-espressif-reuse-20261030/HOST.md) records
all six passing lifecycle variants and the control that resets the counter at
each input packet and fails the intended scheduling assertion. Focused
esp-clang-tidy analysis of the current production audio service completes with
zero errors and one existing shared-header enum-initialization warning.

The [retained-prefix host checkpoint](../tests/results/cyd-espressif-reuse-20261030/PENDING_HOST.md)
adds exact fragmented-byte/PCM tests, allocation refusal/recovery and ownership
checks, plus current Xtensa compilation in all three selected configurations.
The [C3 checkpoint](../tests/results/cyd-espressif-reuse-20261030/C3_PENDING.md)
adds 39 decode-loop cases, 152 maintenance cases, 13 semantic controls and
actual RV32 compilation, while preserving native AAC behavior.
The [native checkpoint](../tests/results/cyd-espressif-reuse-20261030/NATIVE.md)
executes unchanged vendor decoding on both MCUs, including all 703,584 one-byte
feeds. Complete PCM is identical across both architectures and all schedules;
the historical prefix remains exact. Original failed attempts and a precisely
documented post-run data-reader correction are retained.

The [actual CYD task checkpoint](../tests/results/cyd-vorbis-task-20261030/NATIVE.md)
now passes ordered EOF, Stop/reopen and maintenance/resume through the complete
production audio service and real SDK queues/tasks. Each complete run matches
the full direct-vendor PCM reference; five real HTTP clients and public decoder
handles close. [Host regressions](../tests/results/cyd-vorbis-task-20261030/HOST.md)
cover final-byte EOS, packet splits and cleanup, with current target compilation.

The task checkpoint uses explicit transport/output-hardware seams. Real
HTTP/TLS/TFT traffic, deliberate backpressure, production resource margins,
physical audio/throughput and all three output backends remain to qualify.
Vendor reuse does not prove universal Vorbis conformance or close requirements
of the deferred custom decoder.

The [Opus sibling regression](CYD_OGG_OPUS_EOF.md), through the same
`NATIVE_CODEC_OGG` caller, now passes a complete unchanged-vendor baseline,
4096/257/1-byte feeds and all three actual CYD task cases. It exposed a separate
playback correctness gap: the vendor returns 2115840 raw bytes for this fixture,
while its Opus pre-skip and terminal granule require 2112000 playback bytes.
Independent libopus playback confirms that length. Sample-accurate trimming
remains required; raw integration equality does not close it. Legal long-packet
resize behavior also remains to qualify. The old C3 interior calibration and
Vorbis byte/hash reference cannot substitute for these Opus gates.
