# Public Ogg parser observation: paired stock and pass-through instances

The pinned Espressif Ogg/Opus decoder executes on ESP32 LX6 QEMU with
ESP-IDF 6.0.2. An additional supported public simple-decoder registration uses
unchanged `ESP_OGG_DEC_DEFAULT_OPS()`. Its application parser callback calls
`esp_ogg_parse_frame()` once with the identical arguments and returns the same
result. Its free callback delegates to `esp_ogg_parse_free_extra()`. The stock
Ogg registration remains available. No opaque decoder handle or private parser
layout is inspected or changed.

Fresh stock/pass-through pairs decode both complete existing fixtures with
data-bearing EOS and full empty draining. A 24576-byte output buffer avoids
testing resize policy in this diagnostic. Every returned PCM byte is hashed
without modifying playback. Source metadata, input consumption and complete
raw output must match within each pair.

| Pair | Encoded bytes consumed | Public decoder calls | PCM frames returned | Raw PCM bytes | Successful observed parser calls | Delegated frees |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 20 ms fixture, stock/pass-through | 706319 each | 552 each | 551 each | 2115840 each | 574 | 1 |
| 120 ms fixture, stock/pass-through | 707097 each | 93 each | 92 each | 2119680 each | 108 | 1 |

The raw identities remain the prior direct-vendor references:

- 20 ms: `a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b`.
- 120 ms: `670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684`.

All four cases check 48 kHz stereo PCM16 metadata. Stock instances have zero
application observation/free callback counts. The two observed instances have
574 and 108 successful callbacks respectively, in consecutive native call order,
and exactly one delegated free each. The callback does not change either full
raw output, encoded consumption or the diagnostic window identity.

## Public fields observed without unit assumptions

Every one of the 682 successful public parser records reports:

```text
sample_num=0 duration=0 padding_start_size=0 padding_end_pos=0 total_size=0
```

The complete records also retain input length/BOS/EOS, frame/skipped sizes and
typed public extra-data fields. Those fields are read only after the vendor
returns success. For extra data explicitly identifying Opus, the observed
configuration is rate 48000, channels 2, `frame_duration=0` and
`self_delimited=0`. The same duration configuration value appears for both
fixtures and must **not** be treated as their actual packet duration.

These observations do not supply a usable trim interval through those output
fields for these two pinned runs. Field names or zero values do not establish
their units, timeline scope, persistence or behavior on other streams. No
production trimming fix follows from assuming additional undocumented meaning.

## Same-vendor emission-position references

Reviewed fixture auditors independently verify the encoded page CRCs,
continuations, packet durations, pre-skip and granules before generating the
range constants. A separate read-only hash covers vendor PCM emission positions
`[312, 528312)` in both fixtures, containing 2112000 PCM16 stereo bytes:

| Fixture | Emission-position window SHA-256 |
| --- | --- |
| 20 ms | `b63b58b563d2a20d90a7bef235e5c1099dc52433db19083492d9c7098345469f` |
| 120 ms | `4110db997c16a05c329284bb6105468752c25d67818e3a99b8c9d47c5f481fd0` |

The window computation does not remove, replace or reorder output. These are
fixture-derived references within the same vendor's raw emission positions,
not independent numeric conformance or proof of sample alignment. They do not
implement Opus pre-skip/end trimming. Required playback semantics remain open in
[the Ogg/Opus plan](../../../docs/CYD_OGG_OPUS_EOF.md).

## Original compile failure and fresh passing run

Attempt 01 fails actual GCC compilation because the public Ogg headers were
included without their exported `impl/` path. The outer build child exits 1;
the SDK driver exits 2. QEMU is never started. Its original report, error logs,
source snapshots and generated range header remain unchanged and nonpassing.

The only source correction changes two includes to `impl/esp_ogg_dec.h` and
`impl/esp_ogg_parse.h`. The controller and all other frozen inputs remain
identical. Fresh attempt 02 completes all eight native commands and its SDK
driver with exit 0. Its original report is passing with every source/build
binding current. A later data-only audit rechecks 72 source, 11 build-artifact
and five tool bindings without launching another native process.

The coordinator runs on core0; the diagnostic worker runs on core1 with
priority3 and a 16384-byte stack. Assertions, both idle watchdogs, stack
canaries, light heap poisoning and heap integrity stay enabled. Final free heap
is 258908 bytes, minimum observed heap is 229088 bytes, and unused worker stack
is 3980 bytes. These are diagnostic observations rather than production
radio/TLS/TFT or physical-output resource margins.

## Saved evidence and replay

`parser-captures.zip` deduplicates exact published payloads under
`blobs/<sha256>`. `parser-manifest.json` maps logical paths to byte counts,
hashes and blob names. It retains both original reports, command logs/statuses,
actual SDK child statuses, frozen sources/public vendor archives, configuration,
compiler/link records, generated range headers and linked fixture audits.
All 682 individual successful parser records are separately inventoried and
recounted from the unchanged native transcript. Replaceable unselected SDK
scratch is inventoried by hash.

All 17 compiled image payloads are excluded entirely, including application,
boot, merged flash, partition and SDK compiler probes. Their exact original
hashes, sizes and explicit local-only provenance remain. Original images stay
unchanged in ignored local campaigns. No encoded copy or semantic scanner
override publishes excluded image bytes; their recorded hashes are checked
without claiming to verify omitted bytes.

```text
python -B tests/verify-cyd-opus-parser-checkpoint.py
```

The standalone verifier checks every published byte, both original histories,
the exact two-include source correction, paired PCM/metadata/consumption,
successful callback sequences, delegated free counts and fixture audits. It
imports only pinned reviewed canonical data-only readers. No archived program,
compiler, decoder or emulator is started. The retained images are diagnostics
and must not be flashed as production firmware. Production trim ownership,
initial offsets, chaining, malformed streams and physical playback remain
separate required work.
