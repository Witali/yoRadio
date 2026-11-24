# RTC-off full TLS/HE-AAC controls

The ordinary RTC-off profile does **not** meet the zero-allocation-failure
resource gate on any of the three audio outputs. All three controls deliver
the complete verified TLS input, exact decoded PCM and WebUI after EOF.
Audio decoder, stream, output, write, timeout and short-write fault counters
remain zero. Recovered allocator failures still make these runs **NONPASS**.

| Backend | Allocation failures at EOF | Minimum free heap, bytes | Last failed request, bytes / caps |
| --- | ---: | ---: | ---: |
| Legacy DAC | 171 | 964 | 1,512 / 6,144 |
| PDM | 25 | 972 | 1,512 / 6,144 |
| Continuous DAC | 35 | 2,312 | 1,512 / 6,144 |

See [raw runtime evidence and independent gates](native/matrix-summary.json)
and [SDK qualification](sdk/README.md). The three-case wrapper exits zero
after collecting all terminal reports; that exit is **not** a passing
resource verdict. Every individual controller report remains NONPASS.
The [frozen review recipes](recipes/README.md) and manifests identify the
selected inputs and transformations; firmware and private TLS keys stay local.

## Matched inputs

Source is frozen at `7595a79958b8a2ef56babb24c43259fcf536b6dd`.
Relative to the [RTC-on controls](../cyd-openeth-rx-exact-20261124/README.md#final-resource-check-after-webui-and-peer-closure),
the sole effective configuration change is
`CONFIG_YORADIO_WS_STATUS_RTC_SLOW=y` to disabled. The five HTTPD-owned
workspace objects return to DRAM, increasing BSS and heap-start placement
by exactly 6,560 bytes. No channel, JSON field/capacity, client, socket,
audio/DMA/input/TLS buffer, task binding or timeout is reduced.

The independent 64-byte RTC access probe remains enabled. RTC usage is
104 bytes plus the SDK's separate 24-byte reservation, leaving 8,064 bytes;
RTC-off here describes the WebSocket workspace, not removal of that probe.
The diagnostic applications are not production Wi-Fi or board releases.
Their original descriptor version/date are deliberately retained for A/B
comparison rather than presented as clean new release metadata.

The exact-length diagnostic OpenETH driver remains SHA-256
`e4808727b9a3a5a0e1617d57f0d39a11bdf85443b9e3556990ea4822cef60882`.
The fixed QEMU executable remains
`28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4`,
and the strengthened controller remains
`ca236ed51cbb54e06391e7cfb5b88ef465594ccfbd122e52ddcade64f479cc4f`.
All three GCC/image/ELF/OTA/frame and focused WebSocket/SDK-driver Clang
checks pass with no new warnings. Original check-helper failures and the
precisely reviewed unlinked bootloader-description timestamp difference
are preserved in the SDK evidence, rather than replaced by passing retries.

## Runtime observations and limits

Each TLS 1.2 response contains all 102,420 encoded HE-AAC bytes. The six
full-sized body records have 16,408-byte encrypted payloads, followed by a
4,140-byte tail. Every output produces 614,400 stereo PCM16 frames at
48 kHz, with SHA-256
`44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362`.
WebUI content is identical before playback, during playback and after EOF.
Two continuously drained WebSocket clients receive fresh idle/playing/EOF
status, three application pongs each and normal close code 1000.

The existing zero-allocation assertion fails at the EOF boundary, before
the new final-status/health gate can run. Therefore `post_eof_health` and
its success marker are absent, not silently inferred from earlier health
or relabeled as passing. The later `last_reachable_health` snapshots remain
separate evidence and retain the same nonzero allocation counts. OpenETH
RX-wait episodes/recoveries are zero in all three reports. QEMU is stopped
intentionally after observations; controller-induced exit status 1 is not
a clean guest exit or an observed guest crash.

PDM's separate `completion_queue_drops` counter is zero at EOF and 116 in
`last_reachable_health`. These are dropped completion notifications, retained
independently from the zero write/timeout counters. They do not establish PCM
loss or physical DMA timing/analog quality. The RTC-on post-close count of 89
belongs to its own earlier control, not this RTC-off run.

The last failed size is consistent with the pinned lwIP TCP TX pbuf path:
16-byte target `struct pbuf` + 56-byte aligned transport reserve + 1,440-byte
MSS = 1,512 bytes. With `LWIP_NETIF_TX_SINGLE_PBUF` and TCP oversize enabled,
even a small transport write can request a full-MSS pbuf. This is a
source-supported attribution hypothesis; the current allocation callback
retains no runtime caller/task, and the last request does not establish
that all failures share a call site. Merely splitting writes while keeping
the complete 5,120-byte JSON owner would save no static DRAM.
The [source/DWARF-backed diagnosis](analysis/rtc-off-memory-diagnosis.md)
and [selected machine-readable bindings](analysis/rtc-off-memory-diagnosis.json)
retain the actual observations and the attribution limits.

The next offline gate is allocation-free, build-local attribution of the
failed pbuf allocations, followed by a measured reduction in peak DRAM.
The full JSON contract, two clients, normal TCP/TLS budgets, original core/
priority/stack bindings and all negative results remain requirements.
The separate RTC-on matrix passes zero-allocation checks through the final
WebUI/peer closure; it does not change these RTC-off outcomes. Production
Wi-Fi, physical audio/DMA and RTC timing/sleep remain untested here.
