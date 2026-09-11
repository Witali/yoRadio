# Opus: publish completed PCM batches before the next decode

2026-09-11. Experimental, default OFF; not qualified as a general radio fix.

## Evidence and hypothesis

On source5147be3, input1KiB, FIR/ICDF/word helpers, local own SILK12 HTTP:
a steady 26991ms interval delivered27060ms PCM (ratio1.00256), with no
input-wait calls, but26 DMA misses. Read had0 attributed misses, decode0,
output15; health and profile are separate requests, so this is not a
precise causal accounting. Output wall time includes DMA waits, not CPU.

The bridge delivers a960-sample frame as512+448. Commit previously kept a
partially filled buffer available for the next callback until an EOF took
its prefix. Whether the next callback appends therefore depends on timing;
shorter prefixes leave less queued audio while the next frame is decoded.
This is a hypothesis for some short misses, not an explanation of TCP stalls.

## Isolated candidate

`-OpusPcmPublish`, CMake `YORADIO_ESP8266_OPUS_PCM_PUBLISH`, requires diagnostic
Opus and standard I2S PDM32. At the end of each successful Opus PCM callback,
publish its exact committed tail. MP3/AAC, the PCM callback sizes, normalization,
gain, PDM bit algorithm, network waits and the ISR are unchanged.

The single producer changes FILLING to READY in a short critical section:
no writable loan may remain, the descriptor length was set by commit,
and no active DMA memory is touched. Empty/already published calls succeed.
No padding, replay, extra buffer, persistent counter, busy wait or malloc.
Both physical buffers remain512words. Coded durations/pre-skip/EOS may yield
other tail lengths and must remain valid; no assumption that every call is448.

## Acceptance

- [x] Actual producer host tests: exact lengths1/64/120/136/448/480/512,
  publication during live loan rejected, idempotence,100 frames of512+448,
  ordered payload with no inserted/dropped words, stop and IRQ interleavings.
- [x] Full PCM/PDM publication ON/OFF matrix and build-flag regression:
  PDM32/128, RCPDM, Simple and Feedback, six sample rates, mono/stereo,
  normalization on/off and six batch sizes; every resulting PCM/PDM value
  matches. Ten initial tests and seven expanded tests pass, no skips.
- [x] Compile matching ON/OFF images from c9728ad:885520/885648B. Static
  DRAM data1652B/BSS18520B and IRAM text22848B/BSS4040B unchanged. ISR387B
  section is byte-identical. Only flash text grew128B. These are static
  sizes, not heap/stack safety guarantees during network use.
- [x] At least10 attempted physical windows per variant on the same fixture;
  retain start failures, transport errors, missing samples and DMA misses.
- [x] Matched flash-output A/B,10+10 attempts; all reports retained. Only
  SILK12 passed individual continuity windows; overall qualification failed.
- [ ] Qualify real Opus radio >=20s and WebUI; faster raw decoder alone is not
  completion. Reject candidate if no repeatable benefit or if RAM regresses.

No production default has been changed. Raw Opus CPU figures remain in
[the invariant audit](ESP8266_OPUS_LOOP_INVARIANTS.md); they do not measure PDM.

In the c9728ad radio A/B images the flag applies only to audio_service.c.
The old separate flash-output benchmark bypassed that callback: old
measurements must not be presented as evidence for this publication change.
The next benchmark implementation applies the same publication after every
successful <=512-sample output batch, including its final partial batch.
Write/publication errors stop the benchmark and release allocations; the raw
decoder-only path is unchanged. Its source SHA256 is recorded in new build
manifests. The completed physical flash-output A/B below uses matching
new OFF/ON builds, not these radio images or old benchmark images.
This isolates audio transport, but retains Wi-Fi/WebUI interruptions,
as before; CPU and wall time must still be reported separately.

Comparison after both series finish:

```powershell
node tools/esp8266_opus_profile/compare_publication.cjs firmware/development/esp8266-opus-publish-off firmware/development/esp8266-opus-publish-on firmware/development/esp8266-opus-publish-on/comparison.json
```

Each attempt explicitly POSTs the unchanged local `/test.opus` URL to
`/api/native/opus-stream`, preserves its response in startN.log, waits3s,
then runs `run_stage_wall.cjs --seconds 25 --output runN.json`. A POST
timeout remains an unconfirmed start, even if the earlier stream continues.
Ten attempts per variant; no discarded observation failures or retries
substituted for failed windows. The source fixture SHA256 is
807878b973cbe75f518338d5afacb3fcf5c168999bee6420c7813df42b3002aa.

## Physical radio-path result, 2026-09-11

Both application-only OTA operations passed. Ten attempts per variant on
the same own SILK12 file, CPU160/QIO40, source c9728ad. These are sequential
Wi-Fi runs, not simultaneous or isolated CPU timings. The source server was
restarted between series after a PC restart; its payload/hash and options
were unchanged. OFF has two unconfirmed POST starts (4,8), and all ten ON
POSTs were confirmed. Missing responses remain failed attempts.

| Attempt | OFF DMA misses | ON DMA misses |
|---|---:|---:|
| 1 | 956 | 2 |
| 2 | 2289 | 566 |
| 3 | 11 | missing health |
| 4 | 9; start unconfirmed | 0 |
| 5 | missing health | missing health |
| 6 | missing health | 0 |
| 7 | missing health | missing health |
| 8 | missing health; start unconfirmed | 848 |
| 9 | missing health | 0 |
| 10 | missing health | missing health |

Health continuity qualified0/10 OFF and3/10 ON. ON windows4/6/9 lasted
28211/29031/28024ms, with PCM/elapsed ratios1.00419/1.00408/1.00414.
The separately requested profile for ON6 includes one output miss beyond
the health interval. Thus these are precisely bounded **health windows**,
not a claim that the full attempted playback or every surrounding second
was gap-free. The fixture output is physically submitted to GPIO3 DMA;
there was no analog recording or listening-quality verification here.

ON1 has2 misses attributed to output without input waits. OFF3/4 have11/9
output misses without input waits. This supports another controlled output
experiment, but does not establish an overall speedup: many other windows
had transport timeouts or unavailable observations. Never compare the
median of only visible windows as a successful ten-run speed result.

Lowest heap in complete health pairs:6528B OFF,6336B ON; these include
network allocations and are not decoder-owned RAM. Static RAM and ISR
remain identical, as verified in comparison.json. No RAM saving is claimed.

The real56-kbit Opus follow-up failed: first health timed out; the second
showed stale PCM and transport timeout116. Subsequent status reported
DECODER INIT ERROR. Its allocation diagnostic is stage10, free_dram3284,
requested_bytes4096, reserve_bytes4096, detail3344: the post-allocation
reserve gate rejected the decoder, **not** a failed4096-byte allocation.
After cleanup free heap was27064B; RSSI at that later snapshot was-50dBm.
Neither this single RSSI nor the recovered heap proves the absence of
network loss or a leak. Playback was explicitly stopped after the test.

Decision: keep publication experimental/default OFF. It has promising
output-only windows but is not a fix for all radio pauses. Next compare
matching flash-output builds using the same12/24/64/128/192-kbit corpus,
then resolve transport/reconnect RAM pressure and recheck real stations.
No runtime bitrate limit is introduced.

[All raw attempts, matched manifests, ISR evidence and summary](../firmware/development/esp8266-opus-publish-on/comparison.json).
Both artifact directories also retain start logs and local TCP telemetry;
accepted_wire_bytes is the PC write-queue count, not proof of delivery.

## Follow-up source audit (no behavior change)

Before adding another transport workaround, the actual SDK89a3f254b63819035f65d9c5dcdae8864f1a6a8a
was inspected. lwIP api_msg.c netconn_drain already frees queued receive
pbufs; its full close calls tcp_close. tcp.c tcp_close_shutdown sends RST
and purges unread/refused data, and tcp_in.c aborts data arriving after
TF_RXCLOSED. Adding shutdown(RDWR) before every close is therefore not a
demonstrated fix. The successful-close cached Opus decoder is already reused;
an open failure explicitly releases it before retrying. No new leak was
established by this audit, and no close/reconnect code was changed.

web_service.c session_opened already enables TCP_NODELAY. The diagnostic
Opus status handler uses a384-byte stack row and chunked sends, not a
malloc'ed full JSON body. The effect of its many short writes and underlying
TCP queues on live heap/timing remains a hypothesis to measure; it must not
be described as an identified full-body allocation or missing NODELAY.
The current matched series retains the same30s polling protocol throughout.

The saved through192 raw baseline reports DRAM scratch peaks1808/2904/5488/
5488/5488B for12/24/64/128/192kbps; IRAM word peaks14112/15600B. Thus a4-KiB
DRAM scratch proposal is already contradicted by CELT measurements. Even
5488B is an observed corpus peak, not a universal bound for all supported
packets. Keep the6144B allocation until a separate lifetime/coverage proof
justifies changing it. FFT/MDCT word-access fixes are also already present;
do not repeat them as a newly discovered narrow-flash-load optimization.

## Completed matched flash-output A/B, 2026-09-11

Sourceeee18c2, apps903664/903808B, identical corpus header
cd3d55d30806bd143810cb6ec56e34db69956c7ccb011f46f85ae2aac5d65d7a.
Ten attempted runs per variant, all completed with exact PCM/counts.
Each window is24s PCM from repeated12-packet rounds, resetting the decoder
every240ms but not DMA. No audio TCP/Ogg/ICY; Wi-Fi/WebUI remain active,
status polling every30s. These are not24s of distinct decoder history.

| Corpus | Median pipeline CPU OFF / ON | Continuous windows OFF / ON | Median DMA misses OFF / ON |
|---|---:|---:|---:|
| SILK mono12 | 36.862% / 36.781% | 9/10 / 10/10 | 0 / 0 |
| Hybrid mono24 | 68.338% / 68.322% | 0/10 / 0/10 | 40 / 35 |
| CELT stereo64 → mono | 79.208% / 78.781% | 0/10 / 0/10 | 49 / 53 |
| CELT stereo128 → mono | 89.733% / 88.675% | 0/10 / 0/10 | 168.5 / 231.5 |
| CELT stereo192 → mono | 99.145% / 97.622% | 0/10 / 0/10 | 1023.5 / 829 |

CPU includes hashing, normalization/PDM, charged ISR and benchmark overhead,
not just the decoder. Saved maxima and outliers remain part of the result.
Both variants reached192B lifetime minimum heap; this persists after the
original event and is not proof of a new OOM on every later run. Lowest
per-case free DRAM OFF:7152/3244/1732/364/500B; ON:7140/1732/1572/500/500B.
Both fail even the diagnostic4096B reserve gate; no RAM safety is claimed.
Static RAM and ISR are identical, so this is dynamic pressure, not evidence
that publication statically allocated an extra buffer. No leak conclusion.

OFF had observation errors in attempts1/8; ON in1/2/3/4/10. They all remain
in the ten-run series. No analog recording; zero FIFO-empty alone is not a
pass because the neutral-word DMA fallback can keep the hardware clocked.
The A/B was sequential; local host regressions/compilation also ran during
parts of ON. This is not isolated instruction timing or a guarantee that
sub-percent differences reproduce under other network/cache conditions.

Decision: publication stays experimental/default OFF. The SILK12 result is
promising, but it does not remove Hybrid/CELT misses or real-radio transport
failures. Some maximum decode wall times grow sharply between HTTP snapshots;
preemption/cache effects are hypotheses, not attribution of those delays to
a specific decoder function. Repeated initialization is another benchmark
factor to isolate, not a proven cause. Adaptive WebUI CPU budgeting is saved
as an unimplemented experiment in ESP8266_WEBUI_REPAIR_TODO.md.

The actual compiled HTTP component is the local
esp8266/rtos-sdk-native/components/esp_http_server fork: it already coalesces
headers and small chunk framing using request scratch. The unmodified SDK
source's separate CRLF/header sends must not be mistaken for current behavior.
QIO80 is also not a free fix: the board README records unstable QIO80 boots;
the controlled profiles deliberately keep QIO40.

[Full comparison and input hashes](../firmware/development/esp8266-opus-flash-publish-on/comparison.json).
The next independent compute experiment measures the existing LX106 CELT
rotation assembly against C on the same raw corpus; no production change yet.
