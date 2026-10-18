# CYD continuous frame routing and leased queue

Software evidence for CYD-C3-03 and the queue portion of CYD-C3-04. Physical
playback, analog output and SMP/DMA timing remain unqualified. Host queue
tests use actual pthread mutexes and conditions in place of FreeRTOS; codec
APIs in lifecycle tests are scripted.

| Coverage | Evidence |
| --- | --- |
| Actual CYD send/finish functions, shared confirmation/staging/router, actual leased queue and concurrent consumer; 34 corpus cases including long false candidates and two midstream codec changes | [CYD integration](cyd-confirm-integration-pass/report.json), [log](cyd-confirm-integration-pass/run.log) |
| Same extended corpus against C3 production functions after policy hooks | [C3 integration](c3-confirm-shared-final/report.json) |
| 60,000 concurrent queue packets, FIFO, lease retention, allocation failures/races, limits, independent control storage and TLS pressure wrapper | [Shared queue](shared-queue/report.json) |
| Tail barriers, original-prefix restoration, consumer ownership, 600,000 exact bytes and opaque FLAC/Ogg coalescing | [Tail](shared-input-tail/report.json) |
| Actual queue staging, 20,000 randomized operations, compaction, cancellation and corpus candidates | [Staging](shared-staging-corpus/report.json) |
| Common frame walker compared with ffprobe across all MPEG version/rate groups and ADTS fixtures; 1,457 mixed-stream frame boundaries | [Frame corpus](frame-results.json) |
| Actual decoder/output/state functions in Espressif/Helix/minimp3 branches, both ring and leased queue API seams; ordered drain, cached PCM, final-only flush, cancellation/OOM and 2,000 concurrent Play/Stop per variant | [Six lifecycle variants](cyd-lifecycle/report.json) |
| Actual HTTP/TLS/ICY task and status with frame features disabled, preserving the original ring fallback | [HTTP fallback](cyd-stream/report.json) |

The initial canonical extraction was compared byte-for-byte after newline
normalization with the original seven C3 modules. Later policy hooks preserve
C3 behavior while CYD also cancels on a failed generation and waits for PCM
before publishing audio_running. The extended test initially used an old-ID
terminal packet to stop its capture worker after cancellation; CYD correctly
rejects it. The updated test asserts that rejection and uses the current ID
to end only the harness worker.

Default CYD storage has an eight-slot budget and a four-slot startup floor.
The 128-byte control payload handles replay while all four candidate slots
are retained. Terminal markers use the same independent FIFO node. The C3
TLS reclamation policy and its prefill duration are not copied as CYD defaults.
Full analysis reports are retained in the [lint campaign](../native-lint-20261018/).

All production GCC builds below pass from source `8bf1d73a`, with clean
application descriptors and verified embedded ELF hashes. Saved config
snapshots accompany every image. No physical flashing was performed.

| Variant | Bytes | Application and manifest |
| --- | ---: | --- |
| CYD PDM | 1364800 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-frames-pdm/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-frames-pdm/manifest.json) |
| CYD continuous DAC | 1358752 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-frames-dac/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-frames-dac/manifest.json) |
| CYD legacy DAC | 1364816 | [app.bin](../../../firmware/development/esp32-cyd2usb-native-frames-legacy-dac/app.bin), [manifest](../../../firmware/development/esp32-cyd2usb-native-frames-legacy-dac/manifest.json) |
| C3 tested-radio profile | 1474336 | [app.bin](../../../firmware/development/esp32c3-oled-native-shared-frames/app.bin), [manifest](../../../firmware/development/esp32c3-oled-native-shared-frames/manifest.json) |

CYD images fit the unchanged 0x1b0000 application slots. PDM preserves every
pre-existing SDK configuration value; the four added settings enable the
portable queue/router/confirmation/tail features. Size grew by 8,720 bytes
relative to stage 02, or 14,080 bytes relative to the original baseline.
