# Actual original floor0 data: the next spectrum handoff

All12 original/equivalent floor0 streams are ordinary-range inputs. They account
for168 of the original434 audio packets and336 decoded channels. Their observed
log2 gains are approximately-6.614935695207814 to4.019377466143503. The next concrete
step should apply floor0 to these actual packet-frame results and feed the reused
IMDCT, retaining every original434 packet rather than adding more extreme-only
numeric scaffolding. These observations do not authorize a format limit.

The [pure audit recipe](../tests/audit-vorbis-floor0-route.py) reads existing
saved models/captures and pins all eight local pure readers/oracles. It compiles
and launches no decoder, SDK, emulator or child command. It executes no archived
code and duplicates no prior evidence archive. Reproduce with a fresh directory:

```
python -B tests/audit-vorbis-floor0-route.py --output .build/floor0-route-replay
```

The [161096-byte report](../tests/results/vorbis-floor0-route-audit-20261028/audit.json)
records ordered identities and hashes for all434 original identification/setup/
audio packets, all14 relation identities, per-stream ranges and provenance.
Report SHA256:`1cd0e99e7927f4359ff5e0023b3e5a492b05b59cfb759de4b265f7c661983a89`.
Recipe SHA256:`1d1abc9ad3343290d5ea23aa33c1b5f10487963e7ff55d8f0fe1688077858def`.
Input archive SHA256:
`3b74cc7425b315997011040b6b6a8924b908cdff0404e0d0601cbb81a68a93ea`.

The saved1313-row host C capture is compared completely with its retained
expected model. Each of the original434 frames is additionally reconstructed
with the exact independent packet model and compared with that capture. There
are no new native execution or floor0 linear-spectrum/PCM measurements here.

| Observed floor0 input | Values |
| --- | --- |
| Order / declared floor rate | 5 or6 /48000 |
| Bark-map size / amplitude width / offset | 64 or128 /6 or8 /60 |
| Raw amplitudes | 44..55 or176..206, with exact observed sets in JSON |
| Presence / undefined metadata | All336 present; no zero order/rate/map/offset/amplitude |
| LSPs | 1848 exact rational values,27 distinct,7/16..11/4; all strictly increasing and exactly binary64-representable |
| Residue | Exactly-1,0,1; common exponent0, measured magnitude width6, one limb |
| Complete mapped bins / nonzero residue bins | 116736 /5376 |

All LSPs are nonzero rational numbers in(0,3). A mapped angle is a rational
multiple of irrational pi in[0,pi); equality of their cosines would require a
nonzero rational LSP to be a rational multiple of pi. Thus no such factor is
zero in this corpus, and the weighted squared products give positive D. This
is a domain argument for these actual inputs, not a general pole policy.

The independent800-digit Chudnovsky/direct-cosine model observes
D approximately0.3313920205860603 to4.213649429758758. Across all2846 distinct gain
evaluations, a separate150-digit Machin/direct-cosine calculation agrees to
better than1e-100; observed maximum relative D difference is6.35e-149 and maximum
absolute log2-gain difference4.48e-148. These are convergence checks for this
well-conditioned corpus, not universal certified error bounds. Six Bark maps
have identical integer results at120/240 context digits; nonzero positions stay
at least0.000256549591077 from an integer boundary. Bark uses160-digit pi.

On nonzero residue bins the gain range is approximately-6.226094031692908 to4.019377466143503.
Maximum per-channel log2 span is approximately10.06314585675448 across all bins and9.14161541451138
on nonzero residue bins. All six original/equivalent pairs retain identical
exact decoded numerical floor/residue inputs; their distinct encoded bytes and
reference PCM identities are preserved.

The original subset does not cover absent floors, order0/1/255, zero rate/map/
offset, amplitude widths beyond6/8, odd floor rates, map65535, poles/indeterminate
domains, extreme affine/gain spans, wide nontrivial residue or mixed floor0/1
channel mappings. Existing separate tests are not promoted into this corpus.
The finite extreme witness in the transform design, gain-precision refinement,
window underflow, full31 PCM/bound2/all14 relations, stopped composition check,
raw/radio integration and native/resource/physical gates remain open. Int64 fit
has not been used as evidence of gain precision.
