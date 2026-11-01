# Actual CYD logical Ogg playback task diagnostic

This new sibling builds the complete current production audio service, state,
health and decoder registration. It uses real SDK tasks, queues, allocation,
client initialization/cleanup and unchanged public Espressif synthesis. HTTP
transport and output/LED hardware are the only synthetic boundaries.

One build embeds all three complete original fixtures. Opus 20 ms and 120 ms
must each emit 2112000 logical bytes with the independently positioned, exact
stock-vendor trimmed-window hashes. Vorbis must preserve its original complete
2112000-byte reference. Each fixture runs ordered EOF, partial Stop/discard/
reopen and partial three-owner maintenance/token/stale-token rejection/resume.
All task profiles remain stream core0/priority3/6144, decode core1/priority5/
16384 and output core1/priority6/4096. Assertions, stack canaries, heap poisoning,
heap integrity and both idle watchdogs stay enabled.

A fourth playback concatenates the original encoded bytes as Opus20 -> Vorbis
-> Opus120 in one synthetic HTTP session and generation. Reads can cross logical
boundaries in the same returned input block. Each complete output link is
independently hashed; the single final PCM EOF must follow all 6336000 bytes.
The application must really close/reopen its public decoder at link boundaries;
the harness does not inject ACKs, generation changes or terminal markers.

Actual public process observations recount initial capacities, genuine buffer
errors, next-call retries and every close. The parser derives capacities/calls
from observations, allowing once-only consumed input advancement. All five
120 ms lifecycle handles must exhibit their real 12288-to-23040 transition.
Source preparation explicitly includes `aac_public_config.h` while retaining
the exclusions for unrelated private AAC work. GCC/Ninja closure must show the
new production playback, page, timeline, trim and public AAC headers in use.

EOF, Stop, maintenance HELD and chaining record free/minimum heap and largest
internal free block; final records include original-owner stack watermarks.
The fixture census records the largest actual encoded page, separately from
global heap observations. These are diagnostic margins, not HTTP/TLS/TFT or
physical production resource measurements.

```text
python -B tests/run-cyd-ogg-playback-task-qemu.py --preflight-only --output .build/<fresh-campaign>
python -B tests/run-cyd-ogg-playback-task-qemu.py --output .build/<fresh-campaign>
```

Source/SDK/tool/image bindings must remain unchanged throughout execution.
Failed campaigns stay unchanged and cannot be relabelled as passing. Diagnostic
images remain local and must not be flashed as radio firmware. This gate does
not establish universal codec conformance or physical audio quality.
