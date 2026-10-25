# Existing Ogg/Vorbis support across ESP32 branches

The user's recollection is correct: Ogg/Vorbis playback was already added,
including to native CYD. The unconnected later repair must not be described
as missing basic codec support.

Both configured remotes were fetched successfully without pruning, checking
out, merging or deleting branches. The source inventory covers all 136 local
and 60 nonsymbolic remote branch refs, representing 139 distinct commit tips.
It includes branches with unrelated names rather than selecting only names
containing ESP32 or CYD. The
[complete matrix](../tests/results/cyd-vorbis-branch-audit-20261025/branches.csv)
and [Git object inventory](../tests/results/cyd-vorbis-branch-audit-20261025/inventory.json)
bind each result to its inspected commit and source blobs. This is a static
source/configuration/history audit; it runs no decoder, firmware or board test.

## Introduction and active paths

- `82fe17e18af7704962a66276f42f0053df004782`, 2026-08-17,
  **Add OGG Vorbis and Opus decoding**: adds
  [OggDecoder.cpp](../yoRadio/src/audioI2S/OggDecoder.cpp), actual URL/MIME and
  PCM routing in [Audio.cpp](../yoRadio/src/audioI2S/Audio.cpp), codec dependency
  setup, minimal-IDF linkage and enabled configuration.
- `7b13afacf7713521a3fbb25c731fc96094238c26`, authored 2026-08-18 and committed
  2026-08-19: adds the native CYD multicore radio pipeline. The old
  `codex/esp-idf-native` history contains the equivalent introduction as
  `6cd92fab07021adc256b4c08149ef002c5a99224`.
- `b4946459850fbf8518fba3b87948c4f987cd1267`, 2026-08-19: adds native C3
  firmware with the existing Ogg dispatch.

On the current CYD source, [decoder_registration.c](../idf/esp32-cyd2usb-native/main/decoder_registration.c)
registers `esp_vorbis_dec_register`; [audio_service.c](../idf/esp32-cyd2usb-native/main/audio_service.c)
maps `NATIVE_CODEC_OGG` to `ESP_AUDIO_SIMPLE_DEC_TYPE_OGG` and uses the public
open/process/get-info APIs before passing PCM to the audio output.
[sdkconfig.defaults](../idf/esp32-cyd2usb-native/sdkconfig.defaults) enables
`CONFIG_AUDIO_DECODER_VORBIS_SUPPORT=y` and
`CONFIG_AUDIO_SIMPLE_DEC_OGG_SUPPORT=y`. The corresponding C3 paths and flags
are also present.

The minimal-IDF frontend compiles `OggDecoder.cpp` with
`YORADIO_ESP_IDF_MINIMAL`. Other Arduino build configurations get unsupported
stubs; merely finding that file does not prove support in every Arduino build.

## Branch families

Counts below include local and remote refs separately. Branches sharing a
commit or identical integration sources do not provide separate runtime tests.

| Source/configuration family | Refs | Representative branches |
| --- | ---: | --- |
| Native CYD and C3 plus minimal-IDF Ogg/Vorbis paths | 146 | `main`, `codex/cyd-sd-playback`, `codex/cyd-native-port-todo`, `codex/esp32-cyd-c3-review`, `codex/esp32c3-idf-upgrade`, `codex/esp32c3-stream-format` |
| Native CYD plus minimal-IDF; predates native C3 | 2 | `codex/esp-idf-native`, its origin ref |
| Minimal-IDF frontend Ogg/Vorbis; no native application path | 14 | `codex/improve-aac-quality`, `codex/integrate-recommended-worktrees` |
| Predates this Vorbis integration | 34 | `upstream/main`, `upstream/new`, `codex/esp-idf-minimal`, `codex/core-task-isolation` |

The last family can contain the older Ogg/FLAC path; that is not Vorbis support.
The all-ref history query finds no Ogg/Vorbis-topic commits absent from inspected
HEAD `90e26f82865ed8249ad9938beb20e501a225f448`. A second query finds no absent
commits for `OggDecoder.{cpp,h}` or either native `vorbis_repair` directory.
These are explicit topic/path ancestry checks, not a claim that every unrelated
commit from every branch has been merged.

The seven inspected C3 development branches contain no missing Ogg runtime
implementation relative to that HEAD. The codec-optimization review branch adds
an optimization document; it describes existing Vorbis repairs rather than
introducing another decoder.

## Existing library versus additional repair

Playback uses Espressif `esp_audio_codec` 2.6.2, pinned by setup scripts to
`esp-adf-libs` commit `67b8d0e98f58c774b8652480893037273190e8dc`.
The package links target-specific `libesp_audio_codec.a` and
`libesp_audio_simple_dec.a`; the in-repository Ogg frontend is a wrapper,
not the complete Xiph synthesis source. No complete source-buildable Xiph
integration was found in the scanned production source families.

The later CYD bridge starts at `cbb69fdad` and is explicitly
[isolated from production registration](../idf/esp32-cyd2usb-native/main/vorbis_repair/README.md).
Its lack of activation does not disable the existing original radio decoder.
Likewise, the exact numeric/setup/floor/residue components are separate work
on conformance and precision. The retained complete31 numerical checkpoint
still has 15 passing and 16 failing cases; this does not mean all ordinary
Vorbis streams fail or that Vorbis support is absent.

No current CYD hardware qualification is inferred from this audit. Historical
C3 physical playback evidence cannot establish CYD throughput or memory margin.

## Consequence for the remaining work

Keep the existing Ogg/Vorbis radio path. Do not list basic support as a feature
still to be added or require a new codec implementation merely to provide it.
The user-approved next investigation is to build a pinned complete upstream
decoder with minimal adaptation, compare the existing failing corpus and
measure target resources before deciding on a replacement or targeted fixes.
This audit adds no custom IMDCT/synthesis work; evaluate the ready implementation first.
Existing conformance requirements, tests and deferred work remain recorded.
