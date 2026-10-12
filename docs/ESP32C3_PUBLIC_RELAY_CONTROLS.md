# Direct and relayed public MP3 controls

## Question

Can a host relay reproduce or avoid the previously observed public MP3
interruption, while retaining encoded audio and ICY metadata? The
[earlier comparison](ESP32C3_MP3_TRANSPORT_CONTROLS_20261010.md) stopped around
26 seconds. [Local ICY controls](ESP32C3_ICY_TRANSPORT_CONTROLS.md) did not
reproduce that failure.

## Method

Same installed production image throughout: `idf61-production-prefill1000`,
ELF SHA-256 `73da8e2146c5b3691bcfc7a8fb46b34109e74099eac221df2b66e05a62b95245`.
No firmware update or reset. Both observations last 90 seconds, with 15 seconds
excluded from steady output/memory gates. Existing gates are unchanged.

Source: `http://ice5.somafm.com/groovesalad-256-mp3`. FFprobe independently checks
the corresponding HTTPS endpoint before playback. Cases run sequentially:
direct board HTTP, then board HTTP to a host relay fetching that same HTTP URL.
The relay preserves ICY request/response framing and encoded audio, with no
decoding, reconnection or deliberate pacing. It uses bounded 2,048-byte reads,
5-second socket timeouts and a 120-second observation limit. The controller
stops playback after its 90-second observation.

The source is live: sequential cases do not contain identical music, and
different clients may resolve different origin addresses. Relaying changes
TCP endpoints, queues, timing and the network path; it is a diagnostic control,
not proof of the cause of any direct failure. Downstream send counts record
completed host writes, not board receipt. A final write can fail when the board
is deliberately stopped; upstream reads may then exceed downstream sends.

## Verification and evidence

All **24 host tests** passed with no skips. Relay-specific tests compare every
body byte with a local upstream fixture, with and without ICY, and verify
headers, close-delimited EOF, counters and SHA-256 digests. Existing audio
server, pacing, pause, recovery and standalone ICY tests remain passing.

[Evidence archive](../tests/results/esp32c3-public-relay-controls/) retains
source snapshots, controller, FFprobe result, status/health, relay timings and
counts, independent gate replay and playback/settings restoration evidence.
Broadcast audio, raw station metadata, playlist and credentials are not saved.
Settings are compared only in memory. The original selected station and
playing state are restored through WebUI, without flashing or rebooting.

## Interpretation

Both 90-second cases passed format, output and memory gates; neither reproduced
the earlier interruption. The original station/playback/settings and unchanged
firmware identity were verified after restoration.

| Case | Completion queue drops / write errors | Minimum sampled free / largest block (bytes) |
|---|---:|---:|
| Direct HTTP | 0 / 0 | 82,536 / 65,536 |
| Relayed HTTP | 0 / 0 | 80,116 / 63,488 |

Allocation-failure and watchdog counters stayed zero. The relay received HTTP
200 and `icy-metaint: 45000`, forwarded 2,919,104 bytes and read 2,921,152 bytes.
Its maximum observed upstream read duration was 178.9 ms. At the end of the
observation/Stop sequence it recorded `ConnectionResetError`, with one 2,048-byte
block read but not recorded as successfully written. This does not represent a
playback failure in the completed observation. The relay's first version does
not record whether an exception arose on read or write; do not attribute this
terminal exception to a particular peer or claim byte-identical complete hashes.

This short control cannot qualify long playback or resolve the HE-AAC HTTPS
memory-headroom concern. Earlier failures remain evidence even when a later
run succeeds. A failure that no longer reproduces must not be attributed to a
firmware fix: this campaign changes no firmware code.
