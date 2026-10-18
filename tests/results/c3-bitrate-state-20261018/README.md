# C3 bitrate publication audit

The donor C3 source now checks stream generation and bitrate-source priority in
one state-mutex transaction. ICY hints rank below decoder data, which ranks
below measured audio throughput. A delayed decoder cannot overwrite a measured
result, and an old transport cannot mark a new stream as already measured.
The separate global readiness boolean has been removed.

Both targets use the portable five-second audio-byte meter. Explicit window and
decoder-publication flags handle time zero, and wide arithmetic handles kbps
rounding without wrapping the uint32 bps input. No CPU/ABI or board settings
are copied between targets.

[Eight test groups](fixed/report.json) execute actual C3 functions and native
state with controlled preemption and real pthread contention under ASan/UBSan.
The [frozen old-source controls](negative/report.json) fail all six focused
assertions as expected: cross-generation meter readiness, decoder overwriting
measured state, both rounding paths, and both zero-epoch timing paths. These
are deterministic host observations, not live-board timing measurements.

Existing [Play/Stop/Resume](commands/report.json) and
[state/title](state/report.json) regressions also pass, including 2,000
concurrent commands and 20,000 contended title updates. The full format runner's
packet/stats extraction boundary follows the current source after the local
meter type was replaced by the shared header. SDK and full lint qualification
are performed after integration with the other completed changes. The complete
[seven-group format suite](format-suite.json) also passes ([output](format-suite.log));
its C host commands use ASan/UBSan, while the real Helix C++ command remains an
ordinary codec test.
