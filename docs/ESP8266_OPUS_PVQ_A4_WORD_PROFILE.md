# Opus PVQ: frequency of the two remaining a4 byte reads

2026-09-15. Host census over accepted pvq-byte-word, not target timing.
The observer returns the original byte and retains short-circuit ordering.
It checks each source byte and its complete aligned word against the
392-byte static table. PCM and scratch/state/guard results are unchanged.

| kbps / frame | First search probe | Pre-split upper cost | Seconds | Total reads/s audio |
|---|---:|---:|---:|---:|
|12|0|0|0.24|0|
|24|102|140|0.24|1008.33|
|64|675|824|0.24|6245.83|
|128|1204|1794|0.24|12491.67|
|192|1765|2596|0.24|18170.83|
|320 /2.5ms|2784|2134|0.2425|20280.41|
|320 /5ms|2942|2646|0.245|22808.16|
|320 /10ms|2784|2888|0.25|22688.00|
|320 /20ms|2665|3052|0.26|21988.46|
|510|19751|25372|1.22|36986.07|

At192:4361 selected reads per0.24s, in all four byte phases. The first
probe count independently agrees with the earlier search census. The
upper-cost count includes recursive split decisions; it cannot be inferred
from only the final no-split search count.

All10 files have bit-exact PCM, max PCM error0, identical sample/packet
counts, scratch peaks, state sizes and arena guards under ASan/UBSan.
Three regressions pass, including malformed census and ambiguous model
insertion guards. No target firmware, CPU/flash configuration or default
changed. Frequency does not establish a performance gain.

Reproduce: `node tools/esp8266_opus_asm/profile_pvq_a4_word.cjs`.
Evidence: [summary.json](benchmarks/esp8266-opus-pvq-a4-word-profile-2026-09-15/summary.json)
and profile.log beside it. Proposed sites0x4024db52 /0x4024e1ad and required
proofs are in [the byte-load plan](ESP8266_OPUS_ASM_BYTE_LOAD_PLAN.md).
