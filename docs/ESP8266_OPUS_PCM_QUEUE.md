# ESP8266: PCM buffering before PDM

2026-09-11. Goal: continuous real Opus radio, not only fast raw decoding.
No production buffer/default change in this first step.
The new API is compiled only with `YORADIO_OPUS_PCM_LEASES=1`; the build helper
exposes `-OpusPcmLeases`, requiring diagnostic Opus. Default OFF removes the
new acquire branch and wrappers from production. It does not start a consumer.

At mono 48 kHz, PCM16 costs 96 kB/s; PDM32 costs 192 kB/s. Two768-word
DMA buffers cost6144B and hold at most32ms. The existing decoder's separate
960-sample PCM workspace costs another1920B:8064B in total, excluding decoder
history/input/scratch, task stacks and queue/driver control structures.

Candidate: replace the decoder workspace with TWO960-sample PCM frame slots
(3840B total, not an additional ring), plus two256-word DMA buffers (2048B).
Total5888B saves2176B before adding the consumer stack/TCB and synchronization.
PCM capacity40ms plus DMA10.67ms is only a maximum. A slot currently being
decoded is NOT ready audio; an active DMA buffer is already partly consumed.
This must be measured, not advertised as an assured50.67ms underrun margin.

The old synchronous callback cannot transfer a pointer to an asynchronous
consumer: the next coded frame overwrites the same PCM. Packed Opus packets
can contain multiple coded frames. Changing the adapter's config pointer
between callbacks does not change libopus's local output pointer.

## Implemented: explicit PCM ownership at each coded frame

- [x] Add a separate `yoradio_opus_decode_leased_bounded` API. It acquires a
  writable slot before each complete coded frame. Successful output transfers
  ownership; no later Opus access to that PCM, including diagnostic checks.
- [x] On decode error, output cancellation or scratch OOM, return the current
  uncommitted slot with `abort`. Already transferred slots remain caller-owned.
  The lease record lives outside the setjmp frame, including the OOM path.
- [x] Keep ordinary full-packet and synchronous block APIs compatible.
- [x] Host test holds the previous slot THROUGH the next frame decode, checks
  it has not changed, consumes/mutates it, then permits reuse. Test cancellation
  before acquire and after output, invalid alignment, OOM, re-entry and recovery.
- [x] Compare actual PCM against pristine generic32 libopus across SILK,
  hybrid, CELT, CBR/VBR, padding, 2.5..20ms frames and packets up to120ms.

Reproduce both modes (append the same `--capture FILE.opuspkt` to include a
locally retained radio capture):

```
node tools/esp8266_opus_profile/run_block_regressions.cjs
node tools/esp8266_opus_profile/run_block_regressions.cjs --leased
```

Reports: `tools/esp8266_opus_profile/{block,leased}-results.json` include exact
PCM hashes, source hashes and peak scratch. These are host correctness tests,
NOT evidence of hardware speed, scheduler latency or a working PCM consumer.

Saved result:12/12 cases exact for BOTH modes, including the retained private
DLF capture (576 hybrid packets /1728 coded frames, input SHA256
`8f550f4cda894c8c2303bcd37b293d708ece1c8bfe32c74ae7de6156a912c200`).
The capture itself remains local; only hashes/results are committed. The
consumer simulation needs3840B PCM versus1920B for the synchronous baseline;
peak codec scratch is unchanged (worst mixed-mode5968B DRAM /15600B IRAM).
No allocations occur during decoding. This does not yet include an RTOS task.

Target compile check, source136a6a1: saved `esp8266-opus-pcm-lease-off` and
`esp8266-opus-pcm-lease-api`, neither flashed. API ON costs208B flash, zero
additional STATIC RAM; the future3840B PCM pool and consumer stack are not
allocated yet. DMA ISR section identical (387B), and OFF retains the older
DMA512 section sizes. Hardware scheduling/codec-speed qualification remains
open; do not confuse this compile check with a running asynchronous queue.

## Remaining integration and qualification

- [x] Opt-in diagnostic build with two256-word DMA buffers; keep512 default.
- [x] Extend native adapter/bridge to use the two PCM slots, including pre-skip,
  EOS trimming and packets with no output; do not copy into another full ring.
- [x] One consumer owns all gain/normalizer/PDM state. Stop/switch waits for
  acknowledgement before resetting output or freeing queued PCM. No conversion
  in ISR and no blocking wait with interrupts disabled.
- [x] Budget its stack and TCB explicitly; retain4KiB decoder heap reserve and
  the documented audio-stack minimum. Existing app task runs potentially slow
  network/WebUI/storage maintenance and cannot just become this consumer.
- [ ] Measure stack watermark, min DRAM, ready PCM and DMA occupancy, task CPU,
  underruns and stop/switch latency. DMA256 needs service roughly every5.33ms.
- [x] Exact PCM/PDM sequence and ownership tests with cancellation and faults.
- [ ] At least10 matched board attempts, at least20s uninterrupted Opus audio
  per qualifying interval, plus WebUI and codec-switch tests. Keep all failures.

Do not lower memory guards or accept lossy u-law/A-law to make a test pass.
Buffering cannot cure average CPU demand above100%, and it does not fix TCP
receive/reconnect failures. Those remain independent qualification blockers.

## Diagnostic consumer implementation (2026-09-11)

`-OpusPcmQueue -DmaBufferWords 256` enables the actual native adapter/bridge
and `audio_pcm_queue.c`, not merely the lease API. Both remain OFF by default.
The queue replaces the decoder PCM workspace with3840B, without another copy.
It adds a2048B consumer stack plus the SDK TCB and small static slot/health state.
The main audio stack stays5120B. Net RAM must be measured on the board; the
2176B buffer saving relative to DMA768 is mostly consumed by the new task.

The consumer has priority6 (decoder5), blocks on DMA or missing PCM, and keeps
the previous512+remainder normalization boundaries. The ISR only services DMA.
Stop discards ready frames, waits for an in-flight write, then detaches PCM;
only afterwards may the audio owner reset/free the decoder. Startup failures
delete the new task. Volume/normalizer controls are snapshotted atomically;
normalizer reset is performed by the output owner, never concurrently.

Host evidence: direct DMA256/512/768 output is bit-exact at6 sample rates with
mono/stereo and normalization; the actual queue C source passes ASan/UBSan
with two host threads, backpressure,25 in-flight Stops and output failure/reuse.
Native adapter leases pass111 acquisitions:86 transferred,25 trimmed/aborted,
zero stranded slots. The actual codec bridge passes100 mixed-codec allocation
cycles and67 fault sites with the enlarged pool. Both PCM comparison reports
remain12/12 exact including the retained DLF capture. Mock RTOS stack values
are NOT ESP8266 stack measurements.

`/api/native/audio` adds `pcm_ready`, `pcm_stack_free`, `pcm_submitted`,
`pcm_output`, `pcm_output_calls`, `pcm_output_us`, `pcm_error`. PCM progress is
counted after output writes, not enqueue. `pcm_output_us` is consumer WALL
time including DMA waits/preemption, NOT CPU time. The older OUTPUT stage
measures enqueue on this profile and must not be compared as physical output
CPU work. Worst-case diagnostic JSON fits the existing1088B shared scratch;
overflow is rejected, not sent as truncated JSON. Board qualification pending.

## Board result: NOT qualified (2026-09-11)

Source27f0818, app889408B; OTA confirmed slot0x110000. Exact artifact,
manifest, OTA reports and every failed run are in
`firmware/development/esp8266-opus-pcm-queue256/`.

| Series | Attempts | Accepted starts | Valid20s intervals | Observations |
| --- | ---: | ---: | ---: | --- |
| Nightwave Plaza, actual~64kbps | 10 | 10 | 0 | Receive timeout116;6 missing profile windows; no successful start-status replies |
| Own CELT64 file, LAN HTTP | 10 | 10 | 0 | First short decode, then9 observed decoder-init failures |

Both input sources can deliver a short PCM segment: the first remote attempt
submitted/output23688 samples; the first local attempt22728. No queue error
was reported in captured health samples, and submitted/output totals matched
after drain. This does NOT establish continuous playback or rule out unseen
failures. Silent/idle DMA EOFs after playback stops are not useful underrun
measurements, and no CPU utilization is inferred from these wall-time traces.

Lowest observed free consumer stack1672/2048B; main audio stack1496/5120B.
These came from short successful output paths, not all gain/error scenarios.
Local-series boot-lifetime heap minimum4004B. Most health samples were taken
AFTER Stop/init failure, so their24..27KiB free heap is not playback headroom.

The diagnostic snapshot identifies stage8 (scratch allocation), requested6144B,
free DRAM8304B before cleanup,24820B afterwards. This is an allocation failure,
not stage10 (reserve guard). Fragmentation/contiguous allocation availability is
the leading explanation; largest free block was not measured. No leak is
proven by this snapshot. The4KiB reserve was not lowered.

A reset boundary occurred between remote and local series: uptime/generation
restarted and SDK reset reason changed7 to2. In this SDK2 is `ESP_RST_EXT`;
the cause is unknown, and this task did not issue UART/reset commands. Do not
treat the two series as one uninterrupted run. LAN source socket bytes record
bytes handed to the host socket, NOT bytes received by ESP8266.

Static DRAM BSS:18520B (oldDMA512) ->16552B (queueDMA256), a1968B saving.
Dynamic PCM grows1920B, and the consumer adds2048B stack plus its TCB, so total
application RAM grows roughly2KiB rather than shrinking. IRAM sections stay
unchanged; ISR code changes387 ->389B due to configuration, not identical-code
timing. This profile also uses3000ms inactivity versus old512 profile1000ms;
it is not a single-variable performance A/B.

Decision: retain the implementation only as an OFF-by-default experiment.
The idea remains efficient per millisecond of buffered audio, but this
implementation has not solved the actual device failures. Restore the exact
pre-test DMA512 image by OTA; its confirmation is in `restore-dma512-ota.json`.
That rollback itself is not evidence that old Opus playback is qualified.

Next gates before another hardware promotion:

- [ ] Measure largest DRAM block and allocation lifetimes around HTTP setup,
  Opus state/scratch allocation and reconnect; avoid fixing it by lowering guards.
- [ ] Audit consumer call-chain stack and exercise normalization/error paths
  before trying a smaller consumer stack (main audio remains>=5120B).
- [ ] Trace TCP window updates and packet arrival on the LAN control. The local
  failure excludes the remote station as the only possible cause, not Wi-Fi,
  RAM or scheduling. No missing-window bug has yet been established in lwIP.
- [ ] Obtain10 qualified continuous windows, then test actual Stop/Play and
  cross-codec switching; host ownership tests alone are insufficient.

## Follow-up: separate input starvation from output scheduling

2026-09-11. A fresh DMA512 run of the own CELT64 LAN fixture receives data
for over87 seconds. The host TCP_INFO samples show a changing receive window,
no sampled zero window in the first87 seconds, and some retransmissions.
This does not rule out short unsampled stalls, but does not support a permanently
closed TCP window. Bytes accepted by the host socket are not delivered bytes.

In the saved steady window:27.998s board time,27.200s PCM,697 new DMA misses,
6668B minimum of the two free-heap samples. The decode-exclusive stage accounts
for73.54% wall time, output17.79%, read3.81%. These are wall-time intervals,
NOT task CPU utilization, and non-atomic stage miss counters must not be summed
to attribute every DMA miss. The old synchronous path is not continuous even
when input is arriving. This is a reason to test the consumer, not proof it works.

The diagnostic `/api/native/opus-stream` snapshot now includes the largest
CAP8 block at the first init failure, and current free/largest CAP8. It uses one
allocator lock, no allocations/logs and no periodic timer; corrupt links return
UINT32_MAX rather than being followed. It is coupled to the untraced v3.4 SDK
allocator and is absent from production. Bounds/CAP8/sentinel/fragmentation
tests run under ASan/UBSan; lifecycle tests preserve the pre-cleanup snapshot.
Do not poll the heap walk in a tight playback loop: the SDK lock masks interrupts.

`audit_pcm_stack.cjs` recompiles the exact target commands with `-fstack-usage`.
Maximum individual frames:queue64B, output144B, normalizer wrapper16B,
normalizer64B, DMA driver80B. Individual frames do not prove total call depth
or ISR margin. Together with the earlier1672/2048B observed free watermark,
this permits a conservative diagnostic trial with1536B, not a claim of safety
for every path. Main audio remains5120B; decoder heap reserve remains4096B.

The build helper now accepts `-PcmStackBytes 1536` only with `-OpusPcmQueue`.
Default stays2048B and the queue stays OFF. Host concurrent ownership/error
tests run for both sizes; physical gain/normalization/error-path stack and
continuous playback qualification remain necessary. The smaller task saves
512B, but the queue profile still uses about1.5KiB more total RAM than oldDMA512
after accounting for its extra PCM and task stack/TCB.
