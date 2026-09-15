# PVQ endpoint word-load control

Experimental raw Opus ASM benchmark; not ordinary radio or a default profile.
CPU160MHz/runtime QIO40, RAM-preloaded packets; physical audio output OFF.
Application-only native WebUI OTA. Never send UART commands or reset GPIO3.

Unchanged accepted row-word app,903216 B; no endpoint-word patches.
All20 control attempts completed, exact PCM; median CPU19281.98187% before
and82.01310% after the candidate. Candidate80.99456% passes both comparisons.
No decoder/HTTP observation errors. Minimum DRAM8344 B and stack1660 B
in both controls; A/run8 mono12 timing excess267us retained.
Ordinary radio restored through OTA after all30 A/B/A attempts.
See the candidate artifact directory for full comparisons, logs and restoration.
