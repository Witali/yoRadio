# Installed production image: playback and EOF qualification — 2026-10-14

The installed `idf61-prod-20261013` application was tested without flashing or
rebooting. App SHA-256:
`f31ffba883053cf33d7f2e928bf529e5cbcac8f14a8aafd172e835a027684631`;
ELF identity:
`dc06c1a61da089e10f4d22855f05b7e0e4168e35b1810c40751472ccdad9cbe8`.
This is the [production deployment](ESP32C3_PRODUCTION_DEPLOYMENT_20261013.md),
with the experimental frame router and early compact SBR reservation disabled.

## Test and results

A finite 610-second FLAC level-8 fixture, 48 kHz stereo, 16-bit PCM and
approximately 1,283 kbit/s, was served over local HTTP at real-time pacing.
The observation lasted 600 seconds; the file was not looped or concatenated.
The source fixture is synthetic fixed-seed noise mixed with tones. Its manifest,
encoder options, hashes, runner and source snapshots accompany the
[raw evidence](../tests/results/esp32c3-production-qualification-20261014/flac-600-01/summary.json).

| Check | Result |
| --- | --- |
| Independent acceptance gates | 9/9 PASS |
| Playback observations | 521; 508 after the 15-second warmup |
| Post-warmup output window | 584.196 seconds |
| New completion-queue drops / write errors | 0 / 0 |
| Decoder / allocation / watchdog faults | 0 / 0 / 0 |
| Unexpected reboot | None; boot identity and uptime remained consistent |
| Minimum sampled active free heap / largest block | 62,700 / 45,056 bytes |
| Firmware free-heap low-water after the run | 51,236 bytes |
| Median settled free heap before / after | 139,496 / 139,484 bytes |
| Settled largest block before / after | 114,688 / 114,688 bytes |
| Task count before / after | 16 / 16 |
| Maximum paired status/health request duration | 235.999 ms |
| Wi-Fi, playlist and settings | Unchanged; compared in memory only |

The board is left stopped on the same application. Historical completion-queue
counts were nonzero and continued to increase while idle; the output gate uses
only deltas inside the sustained playback window. It does not misclassify
idle/startup notifications as an observed interruption during FLAC playback.

Before this test the board was already stopped with `stream read failed`.
That state is retained in the report. Its preceding station/network history
was not captured, so this test does not explain or fix that earlier event.

## Reproduction and limits

Use [local sustained playback](ESP32C3_TESTING.md#sustained-local-playback-on-a-quiet-production-image)
with the archived fixture manifest and `--seconds 600`. The original generated
fixture remains in `.worktree/esp32c3-idf-upgrade/.build/c3-reserve-soak-20261008/fixtures/`.
It can be regenerated with `tools/audio_test_server/generate_stress.py
--seconds 610 --codec flac --output NEW_DIRECTORY`; verify the recorded tool
version and encoded SHA-256 before comparing runs.

The evidence validates this long local FLAC case. It does not establish
acoustic continuity, all FLAC sample depths/LPC orders, HTTPS FLAC, or EOF:
playback was deliberately stopped before the finite file ended. The full goal
and `production_qualified=false` remain unchanged.

Next: exact-image network/HTTPS/OTA regressions and codec transitions,
HTTPS coverage and attribution of intermittent transport failures. New
610-second Vorbis/Opus fixtures have been generated in
`.worktree/merge-c3-idf-20261013/.build/c3-production-qualification-20261014/ogg-fixtures/`
for the runs documented below. Both Ogg fixtures have now completed their
ten-minute physical observations.

## Sustained Vorbis on the same boot

The unchanged production application subsequently played a single continuous
610-second Ogg Vorbis q10 fixture: 48 kHz stereo, approximately 507.1 kbit/s,
with a 600-second observation at real-time HTTP pacing. It uses the same
fixed-seed source PCM as the FLAC fixture. The board was initially stopped;
no flashing, reset or settings change was performed between the two tests.

[Vorbis evidence and summary](../tests/results/esp32c3-production-qualification-20261014/vorbis-600-01/summary.json)
retain the raw observations, request phases, fixture manifest and controller.
Unchanged test sources reference the checksum-verified FLAC source archive;
`test-source-reference.json` records that mapping instead of duplicating files.

| Check | Vorbis result |
| --- | --- |
| Acceptance gates | 9/9 PASS |
| Playback / post-warmup observations | 521 / 508 |
| Post-warmup output window | 584.310 seconds |
| New completion-queue drops / write errors | 0 / 0 |
| Decoder / allocation / watchdog faults | 0 / 0 / 0 |
| Unexpected reboot | None; same boot as the FLAC run |
| Minimum sampled active free heap / largest block | 69,716 / 55,296 bytes |
| Median settled free heap before / after | 139,492 / 139,492 bytes |
| Settled largest block before / after | 114,688 / 114,688 bytes |
| Task count before / after | 16 / 16 |
| Maximum paired status/health request duration | 258.369 ms |
| Settings and final state | Unchanged; playback stopped |

This run shows no sustained memory-loss failure or post-Stop resource loss.
It extends the previous shorter Vorbis observations on other binaries without
rewriting their historical failures or proving their allocation ownership.
The result applies to this local HTTP fixture; it does not establish Vorbis
over HTTPS, chained Ogg, other channel layouts, EOF or acoustic continuity.
Full production qualification remains open.

## Sustained Opus on the same boot

The same installed image then played the 610.0065-second continuous Ogg Opus
fixture: 48 kHz stereo, encoder target 510 kbit/s (512.7 kbit/s including
container overhead), 20 ms frames, fixed bitrate. The 600-second observation
uses real-time HTTP pacing and the same source PCM as the FLAC/Vorbis files.
No flashing or reset occurred between these three runs.

[Opus evidence](../tests/results/esp32c3-production-qualification-20261014/opus-600-01/summary.json)
records **9/9 PASS**. There were 518 playback observations, 505 after warmup,
and a 584.118-second sustained output window with zero new queue drops or
write errors. Every retained decoder-failure sequence, allocation-failure
counter and watchdog counter was zero. Maximum paired status/health duration
was 227.917 ms. Settings remained unchanged; the board is left stopped.

FFmpeg 8.1.1 also decoded the entire exact Opus fixture with `-xerror` and
exit code zero. The command, encoded hash and stderr are retained in
`fixture-reference.json`. This is independent fixture validation, not a
comparison with board PCM or a measurement of analog sound.

### Three sequential long-playback cases

All rows refer to this exact binary, the same boot, a 600-second local HTTP
observation and the existing 15-second warmup. Values are bytes and sampled
application-wide heap, including network buffers; they are not isolated
codec allocation sizes.

| Codec | Gates | Minimum active free / largest | Median settled free before → after | Settled largest before → after | New output / decoder / allocation / watchdog faults |
| --- | --- | --- | --- | --- | --- |
| FLAC level 8 | 9/9 | 62,700 / 45,056 | 139,496 → 139,484 | 114,688 → 114,688 | 0 / 0 / 0 / 0 |
| Vorbis q10 | 9/9 | 69,716 / 55,296 | 139,492 → 139,492 | 114,688 → 114,688 | 0 / 0 / 0 / 0 |
| Opus 510k | 9/9 | 80,644 / 65,536 | 139,492 → 139,492 | 114,688 → 114,688 | 0 / 0 / 0 / 0 |

Task count remains 16. These runs show no failure of the active memory trend
or settled recovery gates. They do not attribute historical short-window Opus
heap fluctuations to a specific owner or erase those original observations.
Radio signal varied during the campaign, so this is not a controlled RF or
CPU-performance comparison. The long runs do not cover EOF; the subsequent
finite-file evidence is below. HTTPS, fault recovery and the remaining
exact-image matrix still need evidence; `production_qualified` stays false.

## Strict finite-file and natural EOF matrix

After the three long runs, the same installed image and boot completed
**28/28 acceptance cases**, including **22 positive file cases**: each of
the following fixtures once with automatic codec detection and once with
the explicit codec hint.

| Fixture group | Layouts checked |
| --- | --- |
| MP3 | 320 kbit/s, 48 kHz stereo |
| FLAC | level 8, 48 kHz stereo |
| Vorbis | q10, 48 kHz stereo |
| Opus | 510 kbit/s, 48 kHz stereo |
| AAC-LC | 320-kbit calibration; 44.1/48 kHz stereo; 22.05 kHz mono |
| HE-AAC | 44.1/48 kHz stereo, full SBR output rate |
| HE-AACv2 | 44.1 kHz stereo, SBR/PS |

The strengthened test requires the final three observations to have both
`audio=false` and `format="stream ended"`. An error status, explicit Stop,
decoder failure or missing decoder diagnostics cannot satisfy the gate.
Failures retain a snapshot before cleanup. Five new host regression tests
cover these distinctions; all 21 EOF/health/sustained validator tests pass.
The first sandboxed host run failed in Windows temporary-directory cleanup;
the normal-environment rerun passed without changing the test assertions.

[Raw evidence and independent replay](../tests/results/esp32c3-production-qualification-20261014/http-eof-01/audit.json)
verify all 22 playback/EOF sequences again, check all server payloads were
completely delivered, and require zero decoder-failure sequences across all
683 health observations. Allocation and watchdog counters were also zero,
with no unexpected reboot. Minimum sampled free/largest heap was
**29,332 / 14,848 bytes**.

Natural-EOF resource recovery was checked from each case's last three health
observations **before cleanup Stop**, against the initial idle baseline.
All 22 pass: worst median free-heap loss was **12 bytes**, and the largest
block never decreased. Final idle free/largest medians equal their initial
values (**139,492 / 114,688 bytes**), with 16 tasks. Private settings were
compared in memory and remain unchanged; the board is stopped.

This closes the standard finite HTTP fixture matrix on this exact binary.
It does not cover every bit depth/channel layout, midstream codec changes,
HTTPS, network errors or repeated OTA. Finite-file status and health checks
do not establish analog continuity; the separate long-playback cases above
contain the sustained output-counter evidence. Full qualification remains
open, and previous weaker EOF reports are not retroactively upgraded.

## Network faults and WebSocket follow-up

The first network/WebSocket campaign on the same image and boot records
**12/14 PASS**. Drop, stall, HTTP 503, redirect, jitter and two WebSocket
reconnections pass their recorded gates. Independent inspection confirms
that drop/stall actually played before their final three stopped samples:
`stream read failed` after drop, `station unavailable` after stall. HTTP 503
ends with `connection failed`. Recovery is a new explicit Stop/Play command
to 22.05-kHz mono AAC; this does not prove automatic reconnect or an exact
watchdog deadline.

The subsequent idle observation fails on a TCP connect timeout: request 479,
local port 62760, 5,003.6 ms. Four idle status samples were already collected;
no HTTP response was received for the failing connection. The dependent
heap-recovery check then raises `KeyError` because the checkpoint was never
published. This second failure is a test dependency error, not evidence of
a firmware leak. Final Stop/settings verification succeeds. All 226 health
rows retain zero allocation, decoder and watchdog faults and the same boot.
Minimum sampled heap/largest: **63,152 / 49,152 bytes**.

The [original report and phase evidence](../tests/results/esp32c3-production-qualification-20261014/network-ws-01/audit.json)
remain unchanged. A later live read finds the board stopped, with settled
heap/largest **139,356 / 114,688 bytes**, 16 tasks and the same boot. This
does not attribute or fix the intermittent connect timeout.

The test now saves partial idle health plus one diagnostic snapshot, retains
the original FAIL, and reports dependent recovery as BLOCKED when a complete
checkpoint is missing. It requires fresh samples and a confirmed stopped
state; old/partial samples cannot satisfy recovery. Six host regression tests
pass. No firmware code, image or settings change was made.

A complete repeat with the repaired checkpoint diagnostics passes **14/14**:
[repeat evidence](../tests/results/esp32c3-production-qualification-20261014/network-ws-02/audit.json).
All 233 health observations retain zero decoder/allocation/watchdog faults
and the same boot. Minimum sampled heap/largest is **63,224 / 47,104 bytes**;
settled median free/largest before and after both groups is exactly
**139,356 / 114,688 bytes**, with 16 tasks. Settings remain unchanged and
playback ends stopped. The timeout did not recur; this is a successful
repeat, not a root-cause fix or grounds to remove the original failure.

## Ten-minute public HE-AAC HTTPS playback

The unchanged installed image next passes **7/7 checks** for 600 seconds of
Groove Salad's 32-kbit AAC HTTPS stream, with the normal public CA bundle.
FFprobe and the independent unquantized FAAD probe identify **HE-AAC,
44.1 kHz stereo**, with SBR and no PS in the five-second reference capture.
This is HE-AAC evidence, not HE-AACv2. Reference hashes and numeric decoder
results are retained; broadcast audio and private settings are not archived.

[Raw report and independent replay](../tests/results/esp32c3-production-qualification-20261014/https-he-600-01/audit.json)
confirm the full observation and the following measurements:

| Measurement | Result |
| --- | --- |
| First observed PCM | 2.288 s |
| Health observations / steady playback samples | 1,107 / 1,058 |
| Output observation after 15-second warmup | 584.318 s |
| New steady completion-queue drops / write errors | 0 / 0 |
| Decoder / allocation / watchdog faults | 0 / 0 / 0 |
| Minimum sampled free heap / largest block | 24,232 / 9,216 B |
| Firmware lifetime free-heap low-water after the run | 16,088 B |
| Settled median free heap before / after | 139,356 / 139,300 B |
| Settled largest block before / after | 114,688 / 114,688 B |
| Tasks before / after | 16 / 16 |
| Maximum paired status/health request duration | 221.382 ms |

The boot identity remains `abb31264b4eb2085`; no traced HTTP request fails.
Private settings remain equal and the board ends stopped. The 56-byte settled
free-heap difference passes the existing recovery gate; it is not evidence
of an accumulating leak. The firmware low-water is recorded separately from
sampled active heap and is not an arbitrary release floor.

This qualifies this source and observation on the exact image. Other HTTPS
formats, codec transitions, repeated OTA and attribution of the earlier TCP
timeout remain open. Output counters do not establish analog sound quality.

## In-connection format changes: production gap confirmed

The unchanged production image completes the transition campaign with
**9/11 PASS and two retained failures**. This is a functional failure even
though memory and lifetime-health gates pass:

| Encoded sequence in one HTTP connection | Result |
| --- | --- |
| AAC-LC 44.1 stereo → LC 48 stereo → HE 48 stereo → HEv2 44.1 stereo | PASS |
| AAC-LC 22.05 mono → HEv2 44.1 stereo → LC 48 stereo | PASS |
| MP3 48 stereo → HE-AAC 48 stereo → MP3 48 stereo | FAIL: HE-AAC phase missing |
| AAC-LC 48 stereo → MP3 48 stereo → HEv2 44.1 stereo | FAIL: MP3 phase missing |
| Stop during stalled input, then replacement AAC playback | PASS |

[Reports and independently replayed format assertions](../tests/results/esp32c3-production-qualification-20261014/transitions-01/audit.json)
retain all samples. In the MP3-first case one sample incorrectly reports
`MP3 11.025 kHz mono`; no HE-AAC format appears. In the AAC-first case the
later HE-AACv2 appears, but the intervening MP3 segment never does. Terminal
`stream ended` and zero decoder-failure counters therefore do not prove that
all segments were decoded. These observations are not a PCM comparison.

The source/configuration explanation is concrete: this binary has
`CONFIG_YORADIO_FRAME_ROUTER` disabled. `send_stream_audio()` selects the
codec at startup, then forwards subsequent bytes with that original family.
The AAC decoder can update its own profile/rate/channels, but the transport
does not change decoder families. The experimental route adapter has explicit
ordered codec-drain markers; it remains disabled pending its confirmation and
alignment-recovery requirements in the
[stream-confirmation plan](ESP32C3_STREAM_CONFIRMATION_PLAN.md).

All 306 retained health observations stay on the same boot, with zero recorded
allocation, decoder and watchdog faults. Sampled free/largest minima are
**28,764 / 13,312 B**; settled median free/largest return exactly to
**139,308 / 114,688 B**, with 16 tasks. Settings are unchanged and the board is
stopped. No firmware changes were made. The next implementation priority is
safe confirmed decoder-family switching and bounded recovery, followed by
re-running these exact failed sequences on the resulting candidate.
