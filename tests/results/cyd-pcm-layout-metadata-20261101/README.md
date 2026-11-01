# Ordered CYD PCM speaker layout and header gain

PCM packets now carry their speaker layout together with the existing signed
header gain. The output owner applies each packet's layout and then gain after
configuration and generation checks, before writing its PCM. Ordinary codec
callbacks explicitly stamp legacy layout and zero gain. The new field uses
existing padding: the tested packet header remains 20 bytes with four-byte
aligned PCM, and split chunks retain complete frame boundaries.

The final six-profile ASan/UBSan lifecycle campaign passes with vendor,
Helix/minimp3 and their adaptive-input variants. New cases send two three-channel
chunks, eight-channel PCM and a legacy successor while public state already
describes the later link. They check every queued layout/gain and actual
layout-to-gain-to-write call order, both signed gain limits, invalid layout/
channel/frame refusal, stale-generation rejection, a driver refusal before any
PCM write, and generation cancellation during acquisition. Original lifecycle,
concurrency, alignment and PDM-tail assertions remain enabled.

Only the extracted output task enables its production Ogg metadata branch in
this HOST suite. Decoder calls keep the suite's explicit platform model; this
is not a new full Ogg decoder or native-target qualification. Real arithmetic,
all-channel normalization and all three producers have their separate
[mapped-output checkpoint](../cyd-surround-output-20261101/README.md).

`lifecycle-report.json`, the generated units and all twelve build/test logs are
unaltered copies of final attempt03. Its earlier attempt02 failed because the
new direct-queue setup omitted the existing running-state precondition. The
original assertion log and harness are retained here; it remains NONPASS.
The sole subsequent harness correction establishes running state in those two
direct-queue cases; no production bytes or assertions were weakened.

The ordinary FLAC regression also passes on these production bytes: 520 exact
PCM comparisons, sixteen lifecycle schedules and three existing semantic
controls. Its original `flac-report.json` is retained. That suite uses a HOST
RTOS/driver model and does not reopen the explicitly deferred FLAC target
OOM/backpressure/control scope. Full generated PCM, executables and the complete
ignored captures remain local; these copied reports do not reproduce omitted
execution or qualify physical hardware, target timing, or full-radio resources.

Both reports bind their original production/test sources by SHA-256. They are
historical results for those exact bytes, rather than evidence for future
source revisions. The mapping-family-1 decoder still requires application
dispatch and actual-task qualification before surround playback is complete.
