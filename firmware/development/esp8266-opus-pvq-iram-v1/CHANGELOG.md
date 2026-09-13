# PVQ IRAM experiment, 2026-09-13 — not qualified, not flashed

Source1da33ad4, diagnostic-only `-OpusPvqIram`, default OFF. Matched control:
`../esp8266-opus-pvq-flash-v1/`. Only placement of decode_pulses and
alg_unquant changes; entire Opus archive instruction/relocation dump matches.

IRAM text22900 ->24734B (+1834B), IRAM BSS4044B unchanged.
DRAM data1652B/BSS18752B unchanged,16KiB codec word arena unchanged.
Some linked CALL0 relaxations become long calls: alg_unquant778 ->802B,
decode_pulses985 ->989B. Same input objects do not imply identical linked
instruction count or any speed improvement. App902992 ->902912B.

The link map leaves3860B nominally beyond the16KiB arena, but a read-only
physical preflight measured only112B free IRAM on the current stage8 image.
SDK runtime allocations also use IRAM; map capacity is not dynamic heap.
The runner refused BEFORE ANY OTA or raw test, requiring growth1834B plus
2048B runtime headroom. `board-preflight.json` retains this refusal and has
no mutation events. No physical speed claim and no RAM saving are made.

This experiment remains off until a separately proven memory arrangement
makes it safe. Never shrink the codec arena, lower the heap reserve, silently
spill into DRAM or bypass the preflight to obtain a benchmark number.
`link-proof.json` includes exact app/ELF hashes and object-code proof.
`link-proof-v2.json` is the same proof with image provenance retained.

Build integration: replace the generated .s suffix so SDK ldgen sees
cwrs.c.obj/vq.c.obj. Original .c.s.obj symbol mapping failed locally; direct
section selectors with underscores also fail this SDK's grammar. Neither
failed build was flashed. No SDK parser or decoder arithmetic was changed.
