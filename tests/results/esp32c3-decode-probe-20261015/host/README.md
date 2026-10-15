# Decoder work diagnostic host verification

Six health-handler configurations pass ASan/UBSan (watchdog, diagnostics,
adaptive input and optional shared arena). Maximal serialized event durations
and optional counters fit the bounded JSON buffer. Twenty custom-decoder
terminal cases, thirty generic drain cases, twenty output boundary cases and
89 HTTP/TLS reader cases pass. Python validation: seven pipeline and thirteen
health tests pass. No physical timing or audio-quality claim follows.

The initial sandboxed WSL launch was denied by the host environment; rerunning
with host access passed. An initial reader invocation omitted its required
--idf argument and was corrected before the recorded test run.
