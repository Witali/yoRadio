# Independent full-stream Ogg/Opus sample-position checkpoint

The complete unchanged 20 ms and 120 ms fixtures have now been decoded through
both the stock Espressif public Ogg decoder on dual-core LX6/SDK 6.0.2/QEMU and
the installed creator reference, **libopus 1.4**, through its public packet API.
The independent comparison observes a unique **312-frame** start for complete
528000-frame logical playback in both vendor raw outputs. No production trim
filter is installed by this checkpoint.

Every original Ogg page is independently CRC/sequence/continuation checked and
all 551/92 complete audio packets are decoded in original order. No shortened
stream, selected interior segment, fitted gain, channel remap or resampling is
used. The public reference decoder returns the original full raw frame counts;
actual OpusHead pre-skip and terminal granule produce 2112000 logical PCM bytes.

| Fixture | Complete candidate windows | Unique best start | Max absolute error | RMSE | Best squared error | Second-best squared error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| F20 | 961 | 312 | 9 | 1.17055898328 | 1446940 | 17407331889317 |
| F120 | 1921 | 312 | 9 | 1.17211121357 | 1450780 | 17407329428100 |

For every candidate, **all 1056000 interleaved samples** in the complete
528000-frame playback span are compared. The candidate census covers every
possible full-length window in that fixture's vendor raw output: 961 starts
for 20 ms and 1921 for 120 ms. The actual pre-skip, 312, is the unique minimum;
one-sample shifts and every other complete-window displacement are included.
The terminal position is raw frame 528312, retaining exactly 528000 frames and
discarding 648/1608 raw tail frames, respectively. These are observed sample
positions and measured numeric differences, not universal Opus conformance.
No new numeric tolerance was introduced or substituted for an existing bound.

## Actual native and host witnesses

The new native diagnostic uses fresh stock public Ogg instances, a sufficient
24576-byte output buffer, genuine data-bearing EOS and complete draining. Every
captured raw/full-window digest must reproduce the earlier preserved campaigns
before host comparison is allowed. Complete sequential PCM observations are
reassembled and independently hashed by the controller. Public arguments,
decoder libraries, encoded fixtures and original firmware source are unchanged.

Native campaign **01** remains NONPASS. Its 20 ms case completed with both
original digests, but heavy UART PCM observation during 120 ms playback starved
IDLE1 and the real enabled watchdog fired. Campaign **02** changes only the new
diagnostic's scheduling: one `vTaskDelay(1)` after each printed PCM frame. It
rebuilds and passes both complete cases with unchanged digests. The original
failed report, build/source snapshots and local raw transcript stay unchanged.
Neither watchdog configuration nor task core/priority/stack is weakened.

The authoritative independent host run preserves the installed GCC/libopus
identities, actual compiler command, both full reference executions, stdout,
stderr and terminal statuses. The library identity is checked before and after
execution. The public decoder's full output is written before the separate
sample-position search. The comparison harness passes ASan, UBSan and leak
detection with halt-on-error enabled and empty test stderr. The installed
libopus library itself is not claimed sanitizer-built. This execution is
separate from the metadata observer's earlier sanitizer gate.

## Publication and verification limits

Exact original reports/logs/source snapshots are retained here. Full PCM,
packet transport, raw hex console transcripts, ELF/application/boot/merged
images and the host executable remain local under ignored `.build`. Their exact
identities, byte counts and roles are recorded; no payload is copied or encoded
in this checkpoint. Installed SDK/toolchain payloads are not redistributed.

```text
python -B tests/results/cyd-opus-position-20261101/verify.py
```

The initial data-only reader rejected raw CRLF SDK configuration lines because
it matched them before newline normalization. Its original reader/failure
record is preserved under `evidence/reader-first`. The correction normalizes
CRLF only in the reader view; no original config, log, native source, status or
comparison result was rewritten, and no native campaign was repeated.

The data-only verifier checks published bytes, exact command/status/source and
omission bindings, complete metrics and 14 contradictory witness controls. It
executes no archived code or native tool. It **cannot recompute sample errors
without the omitted local PCM**, and does not claim to do so. Local reproduction:

```text
python -B tests/run-cyd-opus-position-qemu.py --output .build/<fresh-native>
python -B tests/run-cyd-opus-position-oracle.py --native-capture .build/<fresh-native> --output .build/<fresh-reference>
```

The original source snapshots remain separately pinned; reproduce only with
the installed matching SDK/vendor/QEMU/libopus tool identities. Diagnostic
images must not be flashed as production firmware. Production integration,
chained stream ownership, other Opus modes/mappings, rate/gain semantics,
OOM/backpressure, network/TLS/TFT resources and physical audio remain separate
requirements. This checkpoint closes the independent position uncertainty for
the two complete fixtures, not those remaining requirements.

The reference follows the creator's [public decoder API](https://opus-codec.org/docs/opus_api-1.5/group__opus__decoder.html)
and [RFC 7845 pre-skip/granule/end-trimming rules](https://www.rfc-editor.org/rfc/rfc7845.html#section-4.2).
