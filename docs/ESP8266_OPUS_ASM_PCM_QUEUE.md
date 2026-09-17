# Accepted ASM kernels with asynchronous PCM output

2026-09-17. Diagnostic experiment for real low-bitrate Opus playback.

`-OpusPcmQueue -DmaBufferWords 256 -PcmStackBytes 1536` can now be combined
with the authenticated ASM backend. The frozen corpus is still verified
against every protected C/header hash. Only `upstream/src/opus_decoder.c`,
the packet/frame dispatcher, is compiled from C with the existing lease API.
All hot SILK/CELT units remain ASM; the ordinary live rebase tool still applies
and authenticates all18 accepted optimizations. This is a mixed dispatcher/ASM
build, not a newly handwritten or wholly frozen ASM library.

The change does not alter Opus state layout, arithmetic or PCM. An acquired
960-sample slot becomes consumer-owned on submit; the next frame acquires a
different free slot. The output task performs normal gain/PDM/I2S processing
while the decoder can produce the next frame. Stop must acknowledge the output
owner before releasing the pool. The existing host ownership tests exercise
backpressure,25 in-flight stops, output failure and reuse under ASan/UBSan.

This option remains OFF by default. The main audio stack stays5120B; the codec
heap reserve remains4096B. RAM and timing qualification must include the added
consumer stack/TCB and pool, not just the smaller DMA buffers.

Host comparison on the current source:12/12 cases exact against pristine
generic32 libopus, including2619 coded frames from the real Deutschlandfunk
24kbps Hybrid mono capture. There are no allocations during frame decoding.
Source and PCM hashes are retained in the synchronous/leased regression reports.
Host correctness does not establish board throughput or continuous playback.

- [x] Explicit mixed-dispatcher manifest and single-unit replacement guard.
- [x] Exact host PCM and concurrent ownership/failure tests.
- [ ] OTA and10 matched low-bitrate station attempts.
- [ ] At least20s continuous DMA without underruns, with responsive WebUI.
- [ ] Stop/Play and codec-switch verification, heap/stack watermark checks.

No production promotion is implied by a successful build or by `playing=true`.
