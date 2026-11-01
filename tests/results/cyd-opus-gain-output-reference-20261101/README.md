# Independent final mono gain reference data

The reference preparer uses the complete independently positioned stock
Espressif integer PCM for the original 20 ms and 120 ms Opus fixtures. It
executes no decoder, production gain helper or native output renderer.

There are 56 complete mono references (528000 frames/1056000 bytes each): seven
signed Q7.8 header gains at four player volumes for both source fixtures.
For nonzero gain, header and player coefficients combine before wide stereo
mixing, one nearest-away rounding and final signed16 saturation. Zero gain
retains the exact legacy per-channel Q15 rounding and truncating mono average.
Normalization is disabled. Gains include +/-6 dB, +20/+48 dB and both signed
extrema; volumes include mute and the +48 dB/volume1 anti-early-clipping case.

All 3145704 possible stereo-sum entries across the 24 nonzero gain/volume
combinations agree at 100 and 160 Decimal digits. Another 7200 selected
mono/stereo/balance vectors include +/-1 Q7.8, signed endpoints, opposite signs,
halfway rounding and saturation. The data-only public verifier recomputes those
7200 vectors independently at 120 digits and checks all published byte bindings.

The two original whole stock PCM payloads stay local. Their exact size/hash
identities are explicit; public verification does not claim to recompute full
PCM hashes from omitted bytes. This is reference preparation, not production
rendering or enabled-normalizer qualification. The separate actual-task gate
must compare its real public PDM driver output against these full goldens.

```text
python -B tests/results/cyd-opus-gain-output-reference-20261101/verify.py
```
