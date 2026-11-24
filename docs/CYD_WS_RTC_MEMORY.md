# Optional CYD WebSocket workspace in RTC SLOW

`CONFIG_YORADIO_WS_STATUS_RTC_SLOW` moves the existing WebSocket JSON buffer,
two status snapshots, fixed client state and socket list out of ordinary DRAM.
It is experimental and disabled by default. Message capacity remains 5,120
bytes, the client limit remains two, and audio tasks keep their original
cores, priorities and stacks. No audio, DMA or codec buffer is moved.

The measured classic ESP32 workspace occupies 6,560 bytes. In the matched
PDM diagnostic ELF, both BSS and heap-start placement improve by exactly
6,560 bytes. The linked RTC region uses 6,664 bytes, including the diagnostic
64-byte access probe and other SDK RTC data; 1,504 bytes remain below the
SDK's separate 24-byte reservation. These are this fixture's linker values,
not a general promise of available heap or RTC space in other builds.

## Hardware and ownership

Classic ESP32 provides an 8 KiB RTC SLOW region at `0x50000000`. Both CPUs
can access it through the data bus, which supports byte, halfword and word
operations. RTC FAST has different CPU access restrictions and is not used.
See the [Espressif technical reference manual](https://documentation.espressif.com/esp32_technical_reference_manual_en.pdf),
system and memory chapter, and the [pinned SDK memory guide](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-guides/memory-types.html).

The option is restricted to classic ESP32 with the ULP coprocessor disabled.
The normal linker enforces RTC capacity. RTC access is slower, and this
storage is not DMA memory. The HTTPD task retains exclusive ownership of the
workspace; atomics and task-control state remain in ordinary DRAM.

A successful new server registration clears the client slots. RTC state
can survive deep sleep while ordinary service flags restart; inheriting
old occupied slots would otherwise prevent fresh clients from connecting.
The host regression first reproduced this failure, then passed with the
clear in place. This simulates retained client state; it is not physical
deep-sleep qualification.

## Enable in an isolated build

From `idf/esp32-cyd2usb-native`, start with fresh configuration/build paths:

```powershell
.\build.ps1 -BuildDirectory build-wsrtc -Sdkconfig sdkconfig.wsrtc -IdfArguments @('-D','SDKCONFIG_DEFAULTS=sdkconfig.defaults;sdkconfig.ws-status-rtc-slow.defaults','build')
```

For either DAC, retain its own `-AudioBackend` selection and corresponding
`sdkconfig.dac.defaults` or `sdkconfig.legacy-dac.defaults` before the RTC
overlay in the defaults list. Do not substitute C3 hardware defaults.

## Qualification

The [saved observations](../tests/results/cyd-ws-rtc-memory-20261124/README.md)
include original failed controls, full-application TLS/HE-AAC runs, live
WebSocket peers and linker geometry. Normal TCP settings remain 11,520-byte
RX, ten receive-mailbox entries and 5,760-byte TX. TLS capacities remain
16,384/4,096, with dynamic buffers and the separate static-RX-reserve option
disabled. Watchdogs remain five seconds / 300 ms and both CPUs stay enabled.

With two live clients, the latest PDM and continuous-DAC runs pass. Legacy
DAC delivers all PCM and WebUI responses but retains one recovered
allocation failure; its resource gate remains NONPASS.

The diagnostic RTC probe performs byte and string operations on both CPU
cores before the application test. Host tests pass 60 groups under ASan and
UBSan with the option both off and on. Normal-PDM Clang-Tidy completes all
53 units with zero errors and the same 100 previously reviewed warnings.
The host section attribute alone does not qualify target memory access.

OpenETH status capture now reads the actual Ethernet interface rather than
the absent Wi-Fi runtime. It reports no Wi-Fi profile or valid RSSI. This
replacement is confined to the diagnostic backend. The optional real
WebSocket peers continuously drain status, require newer receipts for each
idle/playing/EOF phase, send application `ping` commands in each phase, and
require a normal close. Existing PCM, TLS, asset and allocation gates remain.

The successful PDM repeat reached only 324 bytes of minimum free heap.
Passing this finite workload does not establish a robust margin for more
clients or different traffic. The option therefore remains experimental.

At this original runtime checkpoint, normal production exports were still
pending. Physical Wi-Fi/audio, RTC timing and sleep/wake testing remain open.
Extended custom Vorbis and private AAC work remain deferred.

The [shared-scheduler follow-up](CYD_WS_SCHEDULER.md) frees additional task
memory and completes the legacy two-client workload without an allocation
failure. It preserves an intermittent continuous-DAC output timeout as a
separate open issue. The original RTC-placement outcomes above remain the
results of their own source revision and are not relabeled.

The [production RTC matrix](../tests/results/cyd-ws-rtc-production-20261124/README.md)
now supplies six real Wi-Fi applications from clean source `b65437a1b`:
vendor/custom FLAC on PDM, continuous DAC and legacy DAC. Each differs from
its [ordinary RTC-off counterpart](../tests/results/cyd-ws-production-20261124/README.md)
only by the RTC option, and recovers exactly 6,560 bytes of DRAM. In these
normal images RTC usage is 6,600 bytes plus the separate 24-byte reservation,
leaving 1,568 bytes; the diagnostic figures above include a 64-byte probe.
All six image/ELF/OTA/frame checks and focused WebSocket Clang checks pass.
The normal matrix separately completed full Clang. These builds establish
configuration and linkage, not a new runtime memory margin or physical
qualification. The option remains experimental and off by default.
