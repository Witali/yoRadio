# Public identification header: rates and channels

Read-only source/standards audit, 2026-10-20. No codec, SDK, compiler, QEMU,
reference, Git, canonical or campaign operation was executed. Existing completed
reports and macro logs were read as evidence; this audit adds no target result.

## Standard and advertised API

[Vorbis I](https://xiph.org/vorbis/doc/Vorbis_I_spec.html), §2.1.5 assigns
signedness by field context. §4.2.2 explicitly reads sample rate as unsigned32
and channels as unsigned8, requiring both positive: valid field ranges are
1..4294967295Hz and1..255 channels. Its signed bitrate hints are different
fields. The common8kHz–192kHz description is not an identification-field cap.
§4.3.9 defines encoded channel positions through eight channels; above eight,
locations are implementation-defined. It permits documented output reordering,
which does not make additional channels invalid. §1.1.6 allows specifically
labelled hardware omissions, not arbitrary simplification. No rate/channel
range omission is labelled in §4.2.2 or §4.3.9. Field validity alone does not
certify setup, packet validity, implementation support or available resources.

The actual local component identifies itself as2.6.2 in `idf_component.yml`.
Its README183–188 and the matching [Espressif2.6.2 public documentation](https://components.espressif.com/components/espressif/esp_audio_codec/versions/2.6.2/readme)
advertise Vorbis rates8000,11025,12000,16000,22050,24000,32000,44100,48000Hz,
mono/dual and16-bit decoded PCM. Other rates and multichannel are not advertised
there. Existing isolated192000Hz proof establishes a narrower observed extension,
not support for every unlisted value. This vendor contract is narrower than the
format's valid identification fields.

The consumed public [esp_vorbis_dec.h](C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec/include/decoder/impl/esp_vorbis_dec.h:46)
accepts raw information/setup byte buffers and uint32 sizes, rather than a
separate rate/channel enumeration. Public
[esp_audio_dec_info_t](C:/Work/yoRadio/.idf/esp-adf-libs/esp_audio_codec/include/decoder/esp_audio_dec.h:122)
reports `uint32_t sample_rate` and `uint8_t channel`. These types can represent
the identification ranges; their width is not a promise that every value is
implemented.

## Concrete source finding

Both [CYD setup.c943](C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c:943)
and [C3 setup.c943](C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/idf/esp32c3-oled-native/main/vorbis_repair/setup.c:943)
assign the32-bit rate read to `vorbis_info.rate`, then reject `rate<1` at958.
The reader returns signed `long`. That field is signed `long` in
[CYD ABI](C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/idf/esp32-cyd2usb-native/main/vorbis_repair_abi.h:43)
and [C3 ABI](C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/idf/esp32c3-oled-native/main/vorbis_repair_abi.h:37).
The CYD header explicitly asserts32-bit long at121/164; the executed CYD and
C3 setup macro logs also show `__SIZEOF_LONG__=4` and
`__LONG_MAX__=0x7fffffffL`. This path cannot hold0x80000000..0xffffffff as a
positive rate. It is a confirmed representational mismatch; exact public-call
failure/metadata behavior at those boundaries has not been run.

Keep the pinned ABI field type/layout. Interpreting its32-bit pattern as
unsigned for the validity check is the narrow candidate; it still needs actual
public metadata and PCM proof downstream. If the optional `LIMIT_TO_64kHz`
branch is enabled, its comparison at955 must also interpret that pattern as
unsigned, otherwise high-bit values evade the cap. End-of-packet status cannot
be inferred solely from a signed32 return of-1 for the rate: that pattern is
also the maximum unsigned value. Preserve the existing final framing/EOP check.
This audit neither inspects private binaries nor proposes an ABI type change.

Channels use signed `int` after an8-bit read, so1..255 is representable. Setup959
only rejects values below1; DSP allocation987–994 allocates per channel. This
does not prove the vendor conversion/mapping path supports more than two.
The public contract remains mono/dual until meaningful valid-input tests show
otherwise. The raw output guard computes PCM size from the actual channel count
at [output.c27](C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/idf/esp32-cyd2usb-native/main/vorbis_repair/output.c:27)
and delegates conversion/metadata to the real public decoder at38.

## Existing proof and next tests

The qualified raw8192 tests on CYD/C3 exercise stereo rates48000,63999,64000,
192000Hz; their caller explicitly requires channel2. The completed block matrix
uses target192000Hz/channel2 for all108 cases. Its minimal source bank is48000Hz
with a separately qualified192000Hz rebind. The canonical minimal generator
still has `CHANNELS=2` at22. These proofs do not cover mono, every advertised
rate, multichannel, or the signed32 boundary.

Use the existing public raw harness with fresh independently valid fixtures:

1. Root's next rate regression can use the already host-qualified floor1
   fixture, fixed long2048, vendor golden192000Hz, and a checked header differing
   only in rate bits. Use the nine advertised rates plus1,192000,0x7fffffff,
   0x80000000,0xffffffff (14 rates). This isolates rate signedness from the
   previously fixed8192 guard. Require public decoded metadata and PCM, not
   merely successful open. Preserve baseline, a signed-limit control, and the
   enabled optional-cap policy as separate results.
2. Close the advertised mono gap: all nine documented rates at mono and stereo
   (18 combinations), with a bounded setup and representative transition
   controls. Retain the existing block matrix. A reference wrapper's signed
   rate/timestamp limit is not an input-validity oracle; preserve raw headers
   and use an API able to represent the value, or report its limitation.
3. Channel-count progression at a documented rate:1/2 controls, then3,6,8,9,255
   with a correctly generated uncoupled setup, bounded block size, distinct
   nonzero per-channel payload and explicit expected channel ordering. Larger
   counts are not promised to fit or decode; this is valid-input coverage,
   not a new OOM campaign. Never relabel an unsupported valid stream invalid.

For each supported combination, require exact reported rate/channel/16-bit PCM,
packet consumption, frame/byte accounting `frames*channels*2`, canaries, handle
closure and independent PCM/channel-order comparison. Editing only the channel
byte in the existing coupled stereo donor is not a valid mono/multichannel
fixture: channel-dependent setup and packet content must match.

## Output hardware is a separate boundary

The [CYD PDM configure path](C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/idf/esp32-cyd2usb-native/main/native_audio_output.c:494)
and [C3 PDM path](C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/idf/esp32c3-oled-native/main/native_audio_output.c:403)
accept8kHz–48kHz input and resample to fixed48kHz. CYD's legacy branch has the
same explicit input limits; its continuous-DAC branch at577 delegates frequency
acceptance to the driver. These are output/backend decisions. They neither
invalidate other Vorbis headers nor bound isolated raw decode. Likewise,
mixing/selecting speaker channels is not raw multichannel decoder conformance.

G6 remains open for these header dimensions. No blanket mono/multichannel,
full unsigned-rate, fixed-point, radio, physical or full Vorbis conformance
claim follows from the current guard removal or absence of another guard.
