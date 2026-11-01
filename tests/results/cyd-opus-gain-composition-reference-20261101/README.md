# Independent complete-stream gain composition reference data

This prepares data for the next production correction; **no gain implementation
or native target is qualified** by this checkpoint. The decoder's captured
stock integer PCM comes from the earlier independently positioned full-stream
campaign. Mono mixing, normalization, output ownership and hardware still need
their actual implementation gates.

Two complete unchanged source fixtures produce 14 CRC-valid header views:
zero, +6, -6, +20, +48 dB and both signed Q7.8 extremes. Only the gain field,
logical-stream serials and affected page CRCs change; all audio/comments/lacing/
granules stay exact. Zero is exactly the original. New serials make future
multi-link streams legal, without re-encoding or shortening audio.

Independent Python Decimal at **100 and 160 digits** agrees for all **65536
signed16 input values** in each of 28 header/player combinations: **1835008
table entries**. Header gain is combined with the existing player Q15 gain
before one nearest-away rounding and final signed16 saturation. Full zero/
mute/extreme controls pass, as do 420 selected vectors. The 56 complete stereo
reference rows each cover all **1056000 retained samples / 2112000 bytes**.
No production gain helper is imported or used to calculate expected results.

The full-fixture counterexample is substantial: +48 dB combined with player
volume1 (Q15=129) has factor about0.98887, zero final saturation and peaks
15123/15129. Clipping the header stage before player attenuation changes
**1016024/1016019 samples**, respectively. The next pipeline must preserve that
combined result rather than accept early clipping as its final playback policy.

This reference is for stereo integer-PCM composition, not libopus floating
synthesis equivalence or an agreed final mono/normalizer acceptance policy.
The held in-place production hook is not approved by these data. Actual per-link
gain metadata ordering/reset, final DSP mixing/limiting and production tests
remain required. Source/header gain0 still has exact earlier logical hashes.

```text
python -B tests/prepare-cyd-opus-gain-playback.py --output .build/<fresh-reference>
python -B tests/results/cyd-opus-gain-composition-reference-20261101/verify.py
```

The verifier executes reviewed canonical data-only parsing/mutation routines,
reconstructs all complete encoded views from public source fixtures and checks
selected vectors independently at 120 Decimal digits. It executes no archived
program, decoder, compiler, emulator or production helper. Original full PCM
and derived encoded payloads remain local, with exact identities; the public
reader cannot recompute omitted complete PCM hashes. Small header patch records
contain metadata only, without any audio-packet body or executable image.
