# Public Opus packet-mode playback diagnostic

New, separate classic ESP32/LX6 target for the 49 complete creator streams from
`tests/run-opus-packet-modes-reference.py`. The controller freezes their exact
bytes and independent references. Stock public Ogg decoding precedes the actual
current wrapper for every fixture; whole/257-byte feeds produce 196 cases.

Observers forward identical public open/process/close arguments and results.
All decoded and emitted PCM bytes are transported locally with offsets and
SHA-256 identities. Errors remain authentic observations. Successful cases must
consume complete input and genuinely drain data-bearing EOS through an empty
terminal public call; cleanup closes each real handle exactly once.

The coordinator runs on core0; the diagnostic worker runs on core1 at priority3
with a 16384-byte stack. Assertions, heap poisoning, stack canaries and both idle
watchdogs are enabled. This profile is a diagnostic, not an alteration of the
production stream/decoder/output task bindings. No physical output or network
is used. Firmware, merged diagnostic flash, raw UART/PCM and executables remain
local. The result is not complete production audio_service pipeline acceptance.
