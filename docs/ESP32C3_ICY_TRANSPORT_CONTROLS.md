# Matched ICY transport controls on the installed production image

## Purpose and coverage

The previous [MP3 transport comparison](ESP32C3_MP3_TRANSPORT_CONTROLS_20261010.md)
found public HTTP and HTTPS interruptions at roughly 26 seconds, despite
successful local files and concurrent host playback. These controls add ICY
metadata to the same local MP3 fixture, without changing the audio or firmware.

The repository already had a standalone AAC `IcyServer` and title/parser tests.
They are retained. The new shared-server mode supports finite MP3 and repeating
AAC with configurable intervals and ordinary file delivery/pacing statistics.
The configured interval is 45,000 encoded audio bytes, matching the previous
public stream's advertised interval. Metadata cycles between two synthetic
titles and a zero-length update. Each observation lasts 90 seconds; output and
memory gates exclude the initial 15 seconds.

## Reference and host verification

Framing is checked against the [FFmpeg ICY reader](https://ffmpeg.org/doxygen/8.0/http_8c_source.html).
FFmpeg produced byte-identical signed-16 PCM for plain and ICY-wrapped MP3 at
intervals 1,023 and 45,000, with short, empty and maximum 4,080-byte metadata.
Independent framing tests cover arbitrary feed boundaries and exact EOF length.
All **22 host tests** passed, with no skipped tests, including the old standalone
ICY API, normal HTTP delivery, pacing, pauses and recovery. Direct-script and
module CLI entry points both work.

The tests compare encoded bytes and reference PCM; they do not measure analog
output from the board. Socket writes may be coalesced by TCP, so requested
write boundaries are not claimed as actual board read boundaries.

## Physical method

Installed version: `idf61-production-prefill1000`, ELF SHA-256
`73da8e2146c5b3691bcfc7a8fb46b34109e74099eac221df2b66e05a62b95245`.
No flashing or reset is performed. The test captures settings only in memory,
reads the selected playlist index through WebUI, and restores the previous
station and playback state afterward. Raw station names, playlist contents and
credentials are not stored in evidence.

Cases: local MP3 256 kbit/s, 44.1 kHz stereo without ICY; the identical file
with ICY; and native 44.1 kHz stereo HE-AACv2 with ICY. Delivery is paced at 1x.
The MP3 fixture is the existing 130-second synthetic control; the AAC fixture
repeats ADTS. Server events distinguish audio bytes from wire bytes and verify
that the board actually requested and received metadata.

## Findings

| 90-second case | Format | Steady completion drops / write errors | Minimum free / largest block (bytes) | Memory gate |
|---|---|---:|---:|---|
| MP3, plain | PASS | 0 / 0 | 79,580 / 61,440 | FAIL: progressive heap trend |
| Same MP3, ICY | PASS | 0 / 0 | 79,116 / 63,488 | PASS |
| HE-AACv2, ICY | PASS | 0 / 0 | 35,052 / 24,576 | PASS |

All three observations completed without an unexpected stop or reboot. Health
counters reported zero allocation failures and watchdog events. The original
production image, selected station, playing state and settings were restored
and verified. No analog listening or output capture was performed.

See `review.json` in the [evidence archive](../tests/results/esp32c3-icy-transport-controls/)
for independently replayed format, output and memory gates and restoration.
The plain MP3 case recorded zero completion queue drops/write errors, but
failed the existing progressive-heap gate: first/last three-sample median
free heap changed from 82,572 to 79,684 bytes (2,888 bytes). Minimum sampled
free heap was 79,580 bytes and largest block 61,440 bytes, with zero allocation
failures or watchdog events. This is a headroom trend observation, not proof
of a leak or an allocation failure. The failed gate is preserved.

The matched MP3-with-ICY case passed format, output and memory gates. Therefore
ICY insertion alone did not reproduce the public interruption in this run.
This does not exclude interactions with public delivery bursts, ICY contents,
network conditions or server connection behavior. It does not close the
original public-stream issue or the HE-AAC HTTPS headroom issue.

The archive retains the exact source snapshots loaded by the physical run.
The final ICY module also retains the original standalone AAC server; the
review checks that the new `IcyFramer` class matches the physically tested
version. The final combined module passed the complete host suite.

Next investigation: compare direct public delivery with a controlled relay of
the same live source, recording arrival/pacing and termination evidence, and
check whether the small plain-MP3 heap decline stabilizes or repeats across
sessions. Keep audio support, decoder precision and the existing gates intact.
