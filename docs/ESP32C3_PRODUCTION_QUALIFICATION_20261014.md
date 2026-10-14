# Installed production image: sustained FLAC and Vorbis — 2026-10-14

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

Next: sustained Opus, exact-image format/EOF/network/OTA regressions,
HTTPS coverage and attribution of intermittent transport failures. New
610-second Vorbis/Opus fixtures have been generated in
`.worktree/merge-c3-idf-20261013/.build/c3-production-qualification-20261014/ogg-fixtures/`
for the next runs; the Vorbis result follows below, while Opus remains untested
in this ten-minute campaign.

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
