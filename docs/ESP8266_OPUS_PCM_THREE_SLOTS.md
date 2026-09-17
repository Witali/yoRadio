# Third decoder-owned PCM slot experiment

`-Diagnostic -OpusPcmQueue -OpusPcmAppTask -OpusPcmSlots 3` selects three
960-sample mono slots instead of two. Default remains two. The producer
decodes directly into the leased slot; no second PCM copy or task is added.
Three slots provide60ms total PCM capacity; a slot being filled or read
is not available for reuse. Stop still waits for ownership acknowledgement.

Extra PCM allocation1920B and small queue metadata; input2048 to1024 saves
1024B, giving approximately896B extra DRAM. Keep the4096B initialization
reserve and all stack sizes. Do not lower that guard to force this test.
ASan/UBSan ownership tests exercise both counts, both consumer modes, both
stack settings, backpressure, ordered samples, errors and in-flight stop.
Not a production default; physical continuity and heap qualification needed.

Checkpoint2026-09-17: all8 ASan/UBSan combinations PASS. This option has
not yet been compiled into a target image or tested on the board. Work was
stopped at the user's request before that step. Next experiment: three slots,
input1024, unchanged4096B reserve; compare against the two-slot baseline.
