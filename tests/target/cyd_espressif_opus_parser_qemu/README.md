# Public Espressif Ogg parser observation

This isolated LX6 diagnostic registers an additional public simple-decoder
type with unchanged `ESP_OGG_DEC_DEFAULT_OPS()`. Its parser callback calls
`esp_ogg_parse_frame()` exactly once with identical arguments and returns the
same result. Its free callback delegates to `esp_ogg_parse_free_extra()`.
The stock Ogg registration stays available and no opaque handle is inspected.

Fresh stock/observed pairs decode the complete existing 20 ms and generated
120 ms fixtures. Both use a 24,576-byte output buffer, separately from testing
production resize retries. Every public output is hashed without modification;
the pairs must match complete PCM, metadata and encoded input consumption.

Only successful parser returns expose output fields in the transcript:
`sample_num`, `duration`, `padding_start_size`, `padding_end_pos`, `frame_size`,
`skipped_size` and `total_size`. The documented public extra-data fields expose
the codec type and, only for Opus, its public sample rate, channels, frame
duration and self-delimited configuration. No cached-frame payload is read.
Field names alone do not establish their units, timeline scope or persistence.

A separate diagnostic hash covers vendor emission positions corresponding to
the fixture-derived raw frame interval `[312, 528312)`. Reviewed canonical
auditors independently check the unchanged encoded headers, page CRCs, packet
durations and granules before generating these range constants. This hash
neither alters output nor implements production trimming, and does not prove
numeric agreement with an independent decoder.

The sole worker runs on core 1 with priority 3 and a 16,384-byte stack; the
coordinator runs on core 0. Heap integrity, light poisoning, assertions, stack
canaries and both idle watchdogs remain enabled. The application-owned active
case labels are confined to this serialized worker, rather than stored inside
vendor parser state. No board or external network is used.

```text
python -B tests/run-cyd-espressif-opus-parser-qemu.py --output .build/<fresh-campaign>
```

Original source/tool/artifact identities and native child statuses are retained
locally. A buffer error, decoder error, panic or incomplete pair remains an
explicit nonpass. The diagnostic images must not be flashed as production
firmware. Initial granule offsets, single-page streams, chaining and general
production ownership require separate qualification before a trim fix.
