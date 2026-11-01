# Application PCM header gain: host qualification

The new standalone `pcm_header_gain.h` computes the signed Q7.8 dB factor once
per logical link using RFC7845's formula `10^(gain/(20*256))`. Zero gain skips
the power calculation and leaves every PCM byte exact. It is not connected to
`ogg_playback.h`, `audio_service.c` or any production output in this checkpoint.

Formats are explicit: U8 offset-binary (silence 128), S8 two's-complement
(silence 0), and packed signed little-endian 16/24/32. Existing native output uses
signed 8-bit PCM, so selecting U8 never silently reinterprets that backend convention.
The gain is channel-independent. Frame-aligned spans can borrow unaligned byte
storage; bytes outside the span remain unchanged. No memory or pointer is
retained. A generation mismatch, invalid format/state/range/alignment, or failed
factor calculation leaves all PCM bytes and state unchanged.

Rounding is nearest with halfway cases away from zero, matching current Q15
output gain. Integer saturation precedes every potentially unsafe cast. PCM
reads/writes use byte assembly and defined unsigned conversion, without signed
right shifts, unaligned integer loads or out-of-range signed casts.

| Actual host qualification | Result |
| --- | --- |
| Entire signed gain range | All 65536 gain factors are finite, positive and monotone; 327680 silent-span applications preserve silence; 65535 power calls, with no call for zero |
| Independent integer-PCM oracle | Python Decimal at 80/120 digits produces 1125 identical selected vectors; all 4500 applications across 1/2/3/255-channel layouts agree exactly |
| Identity | 20 packed-format/channel layouts preserve every byte, including untouched span canaries and valid zero-byte spans |
| Transactional refusals | 81 invalid-state/generation/format/bounds/alignment cases leave bytes/state unchanged |
| Reset/reuse | 64 cycles reject stale generations and apply the new gain |
| Explicit overflow guard | Five owned-state corruption controls use finite `DBL_MAX`; zero/positive/negative peak samples safely remain silent/saturated even when multiplication reaches infinity |
| Tool checks | GCC `-Werror`, ASan, UBSan, float-cast-overflow and leak detection; original test stderr is empty |

Two original successful runs are preserved. Host01 qualifies the same primitive;
host02 adds the explicit finite-overflow guard cases. No earlier source, report
or log was rewritten. The data-only verifier independently recalculates all
selected vectors at 100 Decimal digits and checks the exact compiled arrays.

## Creator comparison and precision boundary

The public libopus 1.4 encoder/float decoder and `OPUS_SET_GAIN`/`OPUS_GET_GAIN`
produce nine actual gain observations, including both signed extremes. Raw
differences against multiplication by the helper's factor are retained without
an invented numerical acceptance bound. For example, +6 dB measures maximum
absolute difference 2.7433871507831498e-8; gain 32767 measures 0.10364988731453195
at reference magnitude 475705.22314429237. These are observations, not failed
values hidden behind a newly chosen tolerance or a claim of numeric equivalence.

The helper operates on **already quantized integer PCM**. Applying gain within
a float decoder before quantization is a distinct operation. The selected
integer-vector gate is exact; it is not an exhaustive correctly-rounded
real-arithmetic proof for every possible 32-bit sample/gain pair. Production
uses the platform's double/libm implementation. Native-MCU execution, actual
header parsing, generation/link integration, gain composition with the output
controls, production resources and physical playback still require qualification.
The deferred custom Vorbis arithmetic direction is untouched.

`captures.zip` stores original source/reference/log bytes under deduplicated
hash names. Both executable payloads remain local, with exact hash/size/role
and explicit omission records. No PCM audio payload is saved. Public Opus
headers retain their complete original licenses; system libraries remain local
and are not claimed to be sanitizer-built. Runtime identities are checked again
after each host run. The verifier executes no archived program or native tool.

```text
python -B tests/results/pcm-header-gain-20261101/verify.py
python -B tests/results/pcm-header-gain-20261101/verify.py --require-current
python -B tests/run-pcm-header-gain-host.py --output .build/pcm-header-gain-host-new
```

Primary references: [RFC7845 output gain](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.1),
[creator gain CTL](https://opus-codec.org/docs/opus_api-1.5/group__opus__decoderctls.html),
and [public Opus definitions](https://github.com/xiph/opus/blob/master/include/opus_defines.h).
