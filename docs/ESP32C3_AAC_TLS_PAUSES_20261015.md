# AAC TLS delivery-pause diagnosis

## Result

The unchanged local-CA diagnostic image reproduces output starvation under a
controlled 1.51-second host delivery pause: **48 new DMA completion-queue drops**.
The 0.51- and 1.00-second pauses produce no new drops. There are zero write,
allocation, decoder or watchdog faults, and stopped-state recovery passes.
Overall result: **10/11 gates pass**, with the output failure retained.

| Requested pause | Actual host pause | Encoded-byte offset | New completion drops |
| --- | ---: | ---: | ---: |
| 0.5 s | 0.512070 s | 414,279 | 0 |
| 1.0 s | 1.003191 s | 745,703 | 0 |
| 1.5 s | 1.510316 s | 1,077,126 | 48 |

The source is the independently validated, owned 100.032-second AAC-LC
44.1-kHz stereo fixture from the earlier HTTP A/B/A experiment, SHA-256
`65feca3e7d6f0a87fb411488aa146a736da097b685772b00438d300268e0f9e7`.
Observation lasts 90 seconds (last sample 89.531 s). Host send-buffer request
and actual size are both 4,096 bytes. Pacing is 1.0, with catch-up after pauses;
all byte offsets and actual pause durations pass the unchanged schedule gate.
Negotiated TLS is 1.2, ECDHE-RSA-AES256-GCM-SHA384. Host completed writes do not
establish exact board receive times.

## Evidence at the failure

All 48 increments occur in the sampled interval 66.234–67.350 seconds, overlapping
the final host pause at 65.531–67.042 seconds. The phase histogram records 47
events with OUTPUT_WAIT + DECODER_WAIT + STREAM_READ, and one OUTPUT_WAIT event.
The finite recorder retains details for 16 events; **32 older details were
overwritten**, while their phase counts remain available.

For the 15 retained all-wait events:

| Checkpoint age at ISR | Range |
| --- | ---: |
| Output task checkpoint | 0.029–4.697 ms |
| Accepted PCM packet | 383.677–533.017 ms |
| Accepted encoded packet | 498.560–647.900 ms |
| Successful HTTP read | 498.958–648.298 ms |

The last event sees newly received encoded/network data (2.533 / 3.016 ms old),
but PCM is still 543.682 ms old and the output checkpoint is 4.010 ms old.
Together with the imposed pause, this supports exhaustion of buffered input
and PCM in this experiment. The output task was recently serviced; raising
its priority would not supply missing audio. Call phases alone are not
scheduler-state measurements, and the result does not establish the cause of
the earlier intermittent public-source failures or analog waveform details.

Numeric queue telemetry confirms four resident 2,060-byte slots (four-slot
minimum/limit). Occupancy counts WRITING, READY and READING leases, not just
decodable bytes. During the one-second pause one observation falls to two
occupied slots; sparse polling does not capture an empty queue at the longer
pause. The ISR ages provide the more direct starvation evidence.

## Health, image and restoration

All 106 retained health samples stay on one boot. Minimum sampled free heap /
largest block are 59,152 / 32,768 B. Settled free-heap medians before / after
Stop are 138,928 / 138,932 B, with the largest block unchanged at 114,688 B
and 16 tasks. No recorded allocation, decoder or watchdog faults occur.

The binary is the same `idf61-ctls-20261015` laboratory image used in the
[record-size control](ESP32C3_AAC_TLS_RECORD_CONTROL_20261015.md):
app SHA-256 `cd9d9461cedafcab26ddcf05ec4ce8780b8a570f6d49b21f1e6e4d00dba39e85`.
No firmware/DSP changes were made. The runner adds TLS support and retains
the firmware's existing numeric queue snapshot; 22 host tests pass.

The OTA controller restores `idf61-prod-20261013` on app1, stopped, with
matching image identity and unchanged Wi-Fi/playlist/settings. Private keys
and user settings are not archived.
[Raw evidence, phase analysis, exact sources and restoration](../tests/results/esp32c3-confirm-tls-pauses-20261015/)
are retained. This remains diagnostic evidence, not quiet production acceptance.

## Targeted next experiment

1. Add an opt-in, bounded post-initialization AAC input-capacity experiment,
   reusing the existing adaptive-slot/FLAC expansion mechanism. Preserve queued
   data and every producer/decoder lease; reclaim only idle extra slots.
2. Retain the TLS RX reserve and headroom for late SBR/PS allocations. Keep
   production defaults unchanged until same-connection AAC-LC → HE-AAC/HE-AACv2,
   full-rate formats, Stop/EOF/replacement and settled recovery pass.
3. Compare the **same image configuration except input capacity**, same fixture,
   TLS cipher, 4-KiB host buffer and exact pause schedule. Quantify additional
   resident bytes and output-counter changes. Repeat on a quiet production
   candidate before accepting a timing improvement.

This is a bounded network-jitter experiment; no finite buffer can guarantee
uninterrupted output through an arbitrarily long loss of incoming data.
