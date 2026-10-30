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

These changes preserve the production task affinities, priorities, stacks,
display configuration and audio backend selection. They do not enable the C3
private Vorbis repair, custom numerical components or old deferred experiments.

## Qualification boundaries and next steps

The lifecycle host suite executes the production decoder/output task bodies
against explicit platform/codec seams under ASan/UBSan. It checks scheduling,
cancellation, error propagation and ownership; it does not execute Espressif's
binary decoder. A separate valid-stream SDK/QEMU diagnostic exercises the
unchanged target-specific vendor libraries through their public Ogg API.

[Host evidence](../tests/results/cyd-espressif-reuse-20261030/HOST.md) records
all six passing lifecycle variants and the control that resets the counter at
each input packet and fails the intended scheduling assertion. Focused
esp-clang-tidy analysis of the current production audio service completes with
zero errors and one existing shared-header enum-initialization warning.

After those gates, full production audio-task streaming, Stop/reopen,
maintenance, queue backpressure and radio/TLS/TFT resource qualification remain
necessary. The disconnected board also leaves physical audio/throughput and
the three output backends unqualified. Vendor reuse does not prove universal
Vorbis conformance or close requirements of the deferred custom decoder.
