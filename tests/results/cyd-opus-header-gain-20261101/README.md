# Public Ogg Opus header gain: observed missing playback adjustment

The unchanged pinned Espressif LX6 public Ogg path **ignores nonzero OpusHead
output gain for this complete fixture**. Zero, +6 dB and -6 dB headers produce
identical nonzero raw PCM through six independent decoder handles. This is a
successful observation campaign that exposes remaining playback work, not a
passing header-gain implementation. No production gain math is added here.

[RFC 7845 section 5.1, field 6](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.1)
defines a signed little-endian Q7.8 dB field and the factor
`10^(gain_q8/(20*256))`. Default playback application is SHOULD. When a player
chooses any volume/normalization adjustment, that adjustment MUST be added to
the header gain. This checkpoint preserves that distinction, rather than
claiming that every recommendation is an unconditional MUST.

## Exact paired input and complete vendor output

All inputs preserve the complete original **706319-byte** synthetic 20 ms
fixture. Its 15 page CRCs and all 551 audio packets are checked. Only OpusHead
bytes 16–17 and the containing page's CRC change. Comments, lacing, granules,
serial/sequence fields and every subsequent page remain byte-identical. The
zero variant is exactly the original. The generator refuses existing R128 gain
tags, avoiding inconsistent metadata when changing header gain.

Native SDK 6.0.2 / classic ESP32 QEMU campaign **01** uses three gain variants
with whole input and 257-byte feeds: **six fresh stock decoder handles**.
Every handle consumes all original bytes, emits all 551 raw frames, receives
real data-bearing EOS and drains completely. No public arguments are changed,
codec hooks installed or application gain applied.

Every output is **2115840 PCM16 stereo bytes at 48 kHz**, SHA-256
`a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b`.
The whole-stream measurements also agree exactly: squared-sample sum
**12668839949307**, absolute-sample sum **2783974037**, **1057006** nonzero
samples, peak **15293**, and zero saturation samples. Whole/split feeds match
for every gain. Equality cannot be explained by silence or clipping.

All original native commands, the actual SDK compiler-driver child and QEMU
terminate zero. The original outer report is complete, passing and has all
pre/post source/tool/image bindings current. The actual GCC closure contains
five selected whole translation units and 202 dependencies. Both idle
watchdogs, assertions, heap poisoning, heap integrity and stack canaries stay
enabled. The diagnostic worker is core 1 / priority 3 / stack 16384; production
task profiles are not changed. Stable repeat-stream free heap is 258376 bytes,
minimum heap 227772 and unused worker stack 3948. Registry unregister retains
100 bytes relative to its pre-registration observation. These are diagnostic
measurements, not full radio resource margins.

## Independent public reference

The installed creator implementation, **libopus 1.4**, decodes all 551 original
packets through its [public raw float API](https://opus-codec.org/docs/opus_api-1.5/group__opus__decoder.html).
Each gain has a fresh decoder. Packet bodies and complete raw float signal
energy/peak are identical before adjustment. A separate host stage applies
the explicit normative factor before PCM16 rounding and clipping; the library
does not receive a container header or a gain-control request.

| Header gain | Explicit factor | Reference PCM peak | Squared-sample sum | Saturation samples |
| --- | ---: | ---: | ---: | ---: |
| 0 dB | 1 | 15296 | 12669054620577 | 0 |
| +6 dB | 1.9952623149688795 | 30519 | 50436401681516 | 0 |
| -6 dB | 0.5011872336272722 | 7666 | 3182321936424 | 0 |

All three full reference PCM hashes differ. All preserve 528960 raw frames /
2115840 PCM bytes. Conversion uses nearest rounding with ties away from zero,
then saturation. No numerical tolerance is introduced and no universal or
bit-identical conformance between decoder implementations is claimed. The
observed ignored-gain conclusion follows the exact paired vendor identity,
independently corroborated by the distinct normative reference signals.

The host driver passes GCC with ASan, UBSan and leak detection, with empty
reference stderr and every native command terminal zero. Compiler/library
identities are checked before and after. The installed library itself is not
claimed sanitizer-built. Original 19-case data preparation and the fresh
20-case extension, including an existing R128-tag refusal, remain separate
unchanged captures.

## Verify and qualification limits

```text
python -B tests/results/cyd-opus-header-gain-20261101/verify.py
```

The data-only verifier checks all published bytes, actual compiler/process
bindings, complete paired measurements and six contradictory witness controls.
It reconstructs the encoded test transport from unchanged original packets.
It runs reviewed canonical data readers, never archived code, a compiler,
decoder or emulator. Published evidence preserves original reports, source
snapshots, logs, configuration and build/dependency metadata unchanged.

Executables, firmware/object/static-library images, PCM and packet transport,
derived gain-fixture payloads and installed source bytes remain local under
ignored `.build`, with exact hashes/sizes/provenance recorded. No encoded copy
or semantic publication-scanner override is used. The public verifier cannot
re-read omitted image/PCM bytes or independently recompute their sample sums.

Reproduce with fresh ignored directories:

```text
python -B tests/run-cyd-opus-header-gain-qemu.py --output .build/cyd-opus-header-gain-new
python -B tests/run-opus-header-gain-reference.py --output .build/opus-header-gain-reference-new
```

Application gain, per-link ownership/reset/chaining, signed-range handling,
rounding/clipping policy, other Opus modes/mappings, production task integration,
radio/TLS/TFT resources and physical audio remain open. This checkpoint gives
evidence for the next correction and avoids assuming gain behavior merely
because the public parser configuration exposes no gain field.
