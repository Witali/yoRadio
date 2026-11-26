# CYD WS/WSS: defined-case coverage and slow-reader recovery

Source `95672e8f`, evidence checkout `162bdb72`, the qualified **continuous-DAC,
RTC-off** image, and the unchanged two-core QEMU model pass the six new trials
below. Audio is idle in this protocol campaign. The separate
[three-output TLS/HE-AAC resource campaign](../cyd-ws-close-20261126/README.md)
qualifies full audio, exact PCM and post-EOF WebUI on all three outputs.

The [WS](baseline/ws/report.json) and [WSS](baseline/wss/report.json) original
85-case matrices each retain **84 PASS + R06 INCOMPLETE**. Their original
outcomes and nonzero launcher exits are unchanged. The new independently
observed R06 campaign supplies the missing pressure/deadline evidence with
drained and read-resume controls. Together these reports cover the **85 defined
cases per transport**; this is not a rewritten all-green original matrix or an
exhaustive proof of every possible RFC execution.

| Transport | Mode | Completed commands | Unique server TCP bytes | Result |
| --- | --- | ---: | ---: | --- |
| WS | Drained | 524 | 354441 | PASS |
| WS | Withheld | 367 | 217246 | PASS |
| WS | Read-resume | 365 | 244602 | PASS |
| WSS | Drained | 524 | 469981 | PASS |
| WSS | Withheld | 310 | 226666 | PASS |
| WSS | Read-resume | 307 | 258667 | PASS |

All six runs retain a healthy second peer, final allocation failures **0**,
stable boot/fault counters and joined/stopped peer, debugger and guest owners.
Drained and read-resume controls receive Pong, exchange the exact Close 1000
payload and finish with both TCP FIN/ACKs. WSS controls additionally observe a
clean TLS close. WSS is terminated by the guest, with host verification of the
CA chain, `localhost`, certificate dates and the pinned leaf; no host TLS proxy
is used. TLS remains 1.2 with the declared AES-GCM cipher.

## Pressure and the unchanged frame deadline

The earlier exact-zero-window trigger missed valid pressure. This SDK can hold
an unsent whole segment when it does not fit a positive peer window. Its
`tcp_out.c:1266,1309` computes the effective window and checks the actual queued
sequence range. The new observer reads only scalar owner/header fields and
independently verifies the queue-head pointer, network byte order, bounded
sequence distance, positive length, exhausted send buffer and
`0 < snd_wnd <= cwnd`, with queued end **strictly greater** than `snd_wnd`.
This is instantaneous blockage; persist splitting or later window updates can
still make progress. TCP window/SWS rules permit this behavior.
[RFC 9293 §3.8.6](https://www.rfc-editor.org/rfc/rfc9293.html#section-3.8.6)

Both withheld runs then observe the same stored WS-frame deadline, the actual
pre-select target clock, the exact original remaining timeval, select result
zero, caller result `-3`, and the source failure/shutdown path. No new deadline
is substituted for a chunk. Reference start time is explicitly **derived** as
stored deadline minus one second; an entry clock or post-select microsecond
clock is not invented. The actual 1000-Hz tick delta and one-tick quantization
remain recorded. Debugger interference is measured separately, with unchanged
512-stop, 2-second single-stop and 30-second total-pause limits; it is not
physical latency qualification.

Withheld termination is **abnormal**: the guest capture contains a server RST.
SLIRP presents a plain receive EOF to the WS client and ragged TLS EOF to the
WSS client. In particular, the WS report's host-side `orderly-eof` label does
not mean the guest used TCP FIN, and the WSS result does not claim Close 1000
or TLS close_notify. Only the matching real timeout/abort, sender join, zero
withheld reads and final selected-flow server evidence qualify this outcome.
A reset, local close or elapsed host time alone never does. Failed WebSocket
connections may omit Close when the peer is unlikely to receive it; this is
distinct from clean closure.
[RFC 6455 §7.1.7](https://www.rfc-editor.org/rfc/rfc6455.html#section-7.1.7)

The unchanged envelope is at most 593 commands, less than 16 KiB client WS
input, 8 MiB unique server TCP payload including TLS ciphertext, and a 30-second
peer case with its original cleanup reservation. Guest boot/provisioning is
outside that peer timer, so the WSS drained outer duration exceeds 30 seconds.
No concurrent same-SSL-socket reader/writer is introduced. Final capture is
validated only after owner cleanup and stopped/error-free capture; record
alignment alone is insufficient. TCP/TLS buffers, command/status capacities,
two peers, audio task/core bindings and watchdog settings are unchanged.

## Evidence and fixture checks

The [summary](summary.json) cross-checks all source/image/ELF/configuration pins,
replays the retained actual GDB scalar samples through the state machine,
verifies raw MI prefix hashes, independently re-decodes final PCAP and evaluates
the peer verdict again. Raw MI, UART, PCAP, NVS, composed flash, private keys and
their private locations are excluded from this publication.

Pure/scripted checks pass: **69 observer groups, 29 peer groups and 11 integration
groups**. The tests cover positive-window arithmetic, stale/mismatched owners,
missing caller/timeval evidence, sender/local/early resets, wrong final flow,
unclean control closure, mutated nested proof and expired-fixture vetoes.
The [first failed peer check](unit/peer-first-nonpass.txt) is retained; its nested
snapshot mutability issue was corrected before the final run. Historical live
fixture attempts retain their original outcomes in [history](history/attempts.json).

[Exact source snapshots](SOURCE_ARCHIVE.json) include the driver, client,
observer, capture decoder and tests. They are qualification fixtures tied to
the recorded SDK, tools, image and original ignored layout, rather than a
portable installed CLI. Restore each `original_relative_path` to reproduce that
layout; archived scripts are not intended to run from this results directory.
The [implementation binding](SOURCE_BINDING.json) links the unchanged code to
the earlier SDK qualification; it does not replace full production dependency
closure.

Whole-service Stop/join is outside this matrix. Twelve fresh CYD production
exports and the C3 compiler/artifact refresh remain pending. No physical board,
Wi-Fi performance, analog output, complete worst-case stack or physical timing
acceptance is claimed. The explicitly deferred private Vorbis/AAC/FLAC scopes
remain deferred.
