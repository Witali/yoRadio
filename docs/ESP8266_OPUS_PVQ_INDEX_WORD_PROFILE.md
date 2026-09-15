# Opus ASM: signed PVQ index census

2026-09-15. Parent: accepted endpoint-word80.99456% raw CPU192.
Host-only observation; no new target image or performance claim.

At0x4024db22 quant_partition reads a signed16-bit index before adding the
bits-table base. Count the original read on every partition entry. The
observer returns the original int16 and never reads beyond the210-byte
C object. Target word access will need a separate proof for the final word.

|Corpus|Reads|Audio seconds|Reads/second|Last index reads|
|---|---:|---:|---:|---:|
|mono12|0|0.24|0|0|
|mono24|156|0.24|650|12|
|stereo64|846|0.24|3525|24|
|stereo128|1904|0.24|7933.33|24|
|stereo192|3026|0.24|12608.33|24|
|stereo320,2.5ms|3434|0.2425|14160.82|0|
|stereo320,5ms|4218|0.245|17216.33|0|
|stereo320,10ms|4518|0.25|18072|0|
|stereo320,20ms|4784|0.26|18400|26|
|stereo510|36940|1.22|30278.69|122|

At192 phases0/2 have1482/1544 reads. Negative values were not observed;
this does NOT justify unsigned extraction or restricting valid modes.
The last index is used24 times, so its aligned word is not a theoretical
corner case. Current ELF has two zero padding bytes after the index array
inside flash.rodata; a future recipe must independently authenticate them.

All10 files preserve exact PCM, sample/packet counts, mono/stereo state,
scratch peaks and arena guards under ASan/UBSan. Counts independently match
the earlier unconditional row-length census on identical fixture hashes.
They are semantic host frequencies, not a hardware instruction/timing trace.

Evidence: [summary](benchmarks/esp8266-opus-pvq-index-word-profile-2026-09-15/summary.json),
profile.log,profile_pvq_index_word.cjs,pvq_index_probe.inc.c and three
esp8266-opus-pvq-index-profile tests. No board or firmware default change.

Next: save the original a0 return atsp+108 earlier, defer the signed index
load to the old return-store site, and use a fixed-jump helper with a0 as
SAR scratch. Prove identical live registers, stack stores, signed values,
interrupt context, all table bounds and encoder-only helper storage before
host/linked tests and10 A/10 B/10 A board trials. No additional allocation.
