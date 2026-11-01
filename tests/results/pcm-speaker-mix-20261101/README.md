# Wide family1 speaker matrix checkpoint

The new `pcm_speaker_mix.h` supplies the RFC7845 family1 speaker matrices for
one through eight logical channels. It prepares combined left/right linear
coefficients for a final mono sum without an intermediate signed16 limiter.
Every assigned speaker contributes, including center, surrounds and LFE.
It allocates no memory, changes no input PCM, and preserves old state on an
invalid channel count, coefficient or non-finite/full-scale-overflowing factor.

This helper is not yet selected by production. Packet reconstruction, public
decoder ownership, speaker-layout queue metadata, all-channel normalization
and the final output-owner rounding/clipping still require their integration
gates. Existing mono/stereo output arithmetic remains unchanged.

Integration must keep the C1/C2 legacy bypass. The generic mono matrix expects
equal left/right factors for C1; the existing mono gain cache has right0 and
must not be passed to it. `psm_value` reads aligned host-endian `int16_t`
samples. Packed/unaligned little-endian queue data must first be loaded through
the PCM reader into an aligned sample array, rather than cast to that pointer.

Fresh host campaign02 passes GCC strict warnings, ASan, UBSan and leak checks:
72 matrix coefficients equal the nearest binary64 values independently
evaluated from the exact formulas at both100 and160 Decimal digits; all36
speaker impulses,104 control groups, left/right balance, opposite-sign
cancellation and both positive/negative headroom assertions pass. No codec,
SDK, emulator or physical audio hardware executes in this qualification.
The earlier campaign01 passes its original73 control groups and is retained
locally; campaign02 adds the balance/negative/cancellation assertions.

`report.json`, `native.stdout.log` and `native.stderr.log` are unchanged copies
from `.build/pcm-speaker-mix-host-20261101-02`. The report preserves actual
process IDs, terminal statuses, compiler identity, stream hashes and frozen
source identities. The diagnostic executable and complete local source capture
remain in the ignored build directory. A report is evidence of this bounded
host run, not independent replay of omitted files or universal numerical
conformance of a codec. No final S16 rounding tolerance is introduced.

```powershell
python -B tests/run-pcm-speaker-mix-host.py --output .build/<fresh-capture>
```

Formula source: [RFC7845 section5.1.1.5, figures4–9](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.1.1.5).
