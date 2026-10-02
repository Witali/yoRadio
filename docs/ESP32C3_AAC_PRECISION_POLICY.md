# AAC production precision policy

Updated by the user on 2026-10-02: lossy AAC memory optimizations may differ from
the pinned reference decoder by at most **3 signed-16 PCM units per sample,
independently in each output channel**. This is an absolute maximum of +/-3 LSB,
not an RMS limit, not three discarded bits (+/-7), and not a limit after volume
reduction or resampling. The temporary development limit stays at +/-5 LSB.

Lossless memory-layout changes still require **bit-exact PCM**. Full AAC format,
sample-rate and channel support, clean resets/EOF, memory safety, playback speed,
network and OTA qualification remain required. Passing the precision gate alone
does not authorize a production default.

The source of truth is
[`aac_pcm_quality.h`](../idf/esp32c3-oled-native/main/aac_pcm_quality.h).
QEMU logs record its production limit. Python runners read the same definition.
Older logs with a recorded 2-LSB limit retain their original interpretation;
early QMF logs without a limit header also retain their historical 2-LSB gate.
Counts named `over_two` remain measurements above two and are never renamed to
pretend they measure three. Current decisions compare measured maxima with three.

## Reassessment of retained measurements

All five QMF storage formats and all five actual PS-write formats, including
18+18 with a shared exponent, meet the new **precision-only** gate on the retained
corpus: their maxima are 3 LSB. Historical input hashes and measured errors are
unchanged.

Of the eight additional area probes, seven meet the new precision-only gate.
IMDCT overlap still fails: up to 2838 LSB on synthetic HE-AAC. The zero PCM error
in frame-boundary smoothing probes retains its coverage limitation; it does not
qualify every within-frame FIR access. Payload savings remain separate from
actual allocated heap savings.

The [reassessment JSON](../tests/results/esp32c3-aac-precision-20261002/summary.json)
contains all 18 rows, measured maxima, decisions and hashes of the original
evidence. It adds a current-policy assessment without rewriting old logs/results.

```powershell
python tools/codec_benchmark/assess_aac_precision.py --output .build/aac-precision.json
python tests/test-aac-precision-policy.py
```

Tests check that 3 passes while 4, 5 and 7 fail production, preserve historical
parsing, retain the IMDCT failure and prevent a numerical pass being reported as
full production qualification.

A fresh QEMU build also records `AREASTORAGE_LIMIT development=5 production=3`.
Its 180 paired synthetic comparisons reproduce the previous PCM maxima and
above-limit counts. The runner correctly exits with failure because the IMDCT
experiment remains outside both limits. The build log, configuration, source
snapshots and [raw result](../tests/results/esp32c3-aac-precision-20261002/synthetic/result.json)
are retained with this assessment.
