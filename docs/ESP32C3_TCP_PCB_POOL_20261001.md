# ESP32-C3 RTC TCP PCB pool — 2026-10-01

## Purpose and scope

The optional `CONFIG_YORADIO_TCP_PCB_POOL` keeps TCP control blocks out of the
large SRAM heap region used by AAC. The [heap investigation](ESP32C3_HEAP_LAYOUT_20261001.md)
identified a 168-byte TIME_WAIT PCB dividing that region and preventing a
55128-byte SBR allocation. This change addresses fragmentation without changing
the decoder, its numerical precision, rates, channels or AAC feature set.

The candidate is **not qualified and remains off by default**: two TCP ownership
assertions occur during the OTA campaign. The first hardware playback run
passes all 21 mixed-codec switches, including full HE-AAC/v2 in the first cycle.
Additional qualification is recorded below; a passing subset is not a claim
that every codec, TLS stream or deep-sleep interaction works.

## Memory placement and protocol contract

| Property | Conservative control | Pool candidate |
|---|---:|---:|
| Reserved IRAM | 43520 B | 43520 B |
| DRAM data | 12620 B | 12620 B |
| DRAM BSS | 31368 B | 31384 B |
| Fixed RTC PCB reservation | 0 B | 2688 B |
| Maximum active/TIME_WAIT PCBs combined | 16 | 16 |
| Native SBR owner request | 55128 B | 55128 B |

Sixteen unchanged 168-byte PCBs occupy `s_pcbs` in `.rtc.data` at `0x50000000`.
Sixteen ownership bytes occupy ordinary BSS and reset on every full boot.
`tcp_alloc` retains its normal complete initialization of a reused PCB. The
half-second RTC wake stub does not use the networking pool.

This reserves existing RAM; it does **not** create 2688 bytes of new memory or
reduce the PCB payload size. The reservation reduces the last-priority RTC heap,
while preventing these long-lived small allocations from splitting ordinary
DRAM. Unused slots remain reserved. Ordinary static heap capacity decreases by
16 bytes for ownership flags. Do not add the IRAM and DRAM aliases together.

The IDF 6.0.2 allocator already limits heap-backed TCP PCBs to
`MEMP_NUM_TCP_PCB` (`CONFIG_LWIP_MAX_ACTIVE_TCP`). The wrapper preserves that limit,
returns NULL when full, and leaves TCP's existing TIME_WAIT/closing recovery
logic in place. TCP timers, packet buffers, listen PCBs and all other memp types
remain unchanged. Statistics account for pool use, peaks and exhaustion. The
implementation requires heap-backed memp without overflow instrumentation and
rejects incompatible configurations at compile time.

All measurements use DIO 80 MHz, CPU 160 MHz, static Wi-Fi RX=6 and dynamic
RX/TX=16. Auto Suspend and deep sleep are off on the tested board. The AAC
relocation, packed history and early-reservation experiments are off. No
diagnostic heap walk or TCP lifetime logging runs in this candidate.

## Hardware and host evidence

The physical sequence is MP3 → FLAC → Vorbis → Opus → AAC-LC 48 kHz stereo →
HE-AAC 48 kHz stereo → HE-AAC v2 44.1 kHz stereo, repeated three times.

| Check | Result |
|---|---|
| Same sequence, conservative control | 19/21; first-cycle HE/v2 failures retained |
| Pool candidate | **21/21 PASS**, including first-cycle full SBR/PS output |
| WebSocket format/reconnect | PASS |
| Heap recovery after three cycles | PASS; largest block 114688 B at all checkpoints |
| Final settled free heap per cycle | 146220 / 146220 / 146220 B; 17 tasks |
| Filtered switching diagnostics | No allocation failure, panic, heap-corruption or capture-interruption marker |
| Host ASan/UBSan pool checks | PASS for capacities 1/16/32, statistics off/on |
| Same-image OTA HTTP/hash/settings checks | 15/15 PASS, **insufficient for acceptance** |
| Serial health during that OTA run | **FAIL: two ownership assertions and automatic reboots** |

Host checks cover exhaustion, reuse, forwarding, alignment, unique ownership
and 40000 concurrent allocation lifetimes in each of the six variants. Hardware
checks observe reported PCM rate/channels and runtime heap; they do not capture
the analogue output or establish acoustic continuity.

Installing the candidate from the earlier diagnostic image passed app-only OTA,
image hash/slot verification and Wi-Fi/playlist/settings preservation. Tests
initiated by the new candidate are separate from that installation check.

### OTA rejection despite HTTP success

The filtered capture contains two instances of
`assert failed: __wrap_memp_free ... (TCP PCB is allocated)` from ELF
`c54563bee69ec0c2435c8c81d6dd30c98c5d77692227806563c8a7ae837053f6`.
After each panic the board automatically starts the same application. Therefore
an unchanged image hash and successful later HTTP response cannot prove that
the negative OTA case avoided a crash. The raw 15 HTTP results remain preserved;
the separate `ota-repeat/serial-health.json` rejects this run.

The cause of the invalid ownership state remains under investigation. It is not
proven by the first assertion alone: overwritten ownership metadata could produce
the same assertion. The bounded history below supplies stronger evidence.
Do not remove or bypass the assertion to obtain a pass.
The filtered stack entries are possible code addresses, not a verified unwind.

A second image with verbose per-event logging passes all 11 negative-OTA and
restoration checks and has a clean serial capture. It changes timing and is not
a fix for the uninstrumented failure. A third diagnostic image retains the last
128 ownership/state/caller events in 1028 bytes of DRAM and dumps them only at an
ownership assertion, reducing serial timing interference. Both remain separate
artifacts; the original failed capture is retained.

The bounded-history image reproduces the fault during the negative OTA run.
All 62 events from sequence 0 through 61 are present (no ring wrap). Slot 3 is
allocated at event 58, freed at event 60 with ownership set, then freed again
at event 61 with ownership clear. No allocation intervenes. For this exact ELF,
the captured caller return addresses, resolved at the preceding instruction,
identify `tcp_input_delayed_close` at `tcp_in.c:627` for event 60 and `tcp_free`
in the `tcp_close_shutdown` path for event 61. This confirms a repeated release
in the recorded sequence; the reason the caller retains that PCB is still open.

Only the first three HTTP cases pass in this run. The truncated-image case and
the following seven checks fail, including restoration, when WebUI does not
return at its old address after the panic. The serial-health gate fails too.
The assertion remains enabled. The native USB watchdog reset subsequently
returns WebUI HTTP 200. The shell wrapper reports the esptool disconnect exit
code even though the supplied reset script explicitly verifies recovery; the
retained log distinguishes those facts.

Audit netconn ownership, close-pending callbacks and immediate PCB address reuse.
An upstream [LAST_ACK close-completion proposal](https://github.com/espressif/esp-lwip/pull/91)
describes a related missed callback, but this build has `LWIP_SO_LINGER` disabled,
so its guarded one-line change is not an established fix here. The pinned lwIP
revision is `fd432e4ee2cfb7f7f1c7eb7227e0173412e7b84e`. No SDK patch was applied.

After recovery, app-only OTA restores `esp32c3-iram-safe-wifi16`, the conservative
control with the PCB pool, Auto Suspend and deep sleep disabled. The transition
checks its exact image hash and preserves Wi-Fi/playlist/settings. Its own
first-cycle HE/v2 limitation remains documented; restoration is not a claim that
the original overall codec goal is complete. `final-board.json` records the
subsequent read-only board identity and technical playback status.

`tools/esp32c3_tests/ota_diagnostic.py` now combines the existing OTA gates with
filtered serial capture and exits nonzero on panic, heap corruption or capture
failure. It permits expected reboot banners. Regression tests specifically
cover a panic followed by a successful boot into the same image.

### Clean-start AAC survey

Three 35-second observations with the saved ten-block input ring all retain the
expected PCM rate/channels. Full Wi-Fi/playlist/settings comparisons pass on
restoration, and no panic marker occurs in this survey.

| Stream | CPU busy mean | Decoder mean | Minimum sampled free heap | Minimum largest block |
|---|---:|---:|---:|---:|
| AAC-LC 48 kHz stereo | 37.067% | 18.767% | 76948 B | 65536 B |
| HE-AAC 48 kHz stereo | 51.217% | 36.167% | 20548 B | 10752 B |
| HE-AAC v2 44.1 kHz stereo | 56.000% | 40.750% | 20680 B | 10752 B |

These short FreeRTOS runtime-counter observations are close to the conservative
control (36.950/51.167/56.033% total; 18.800/36.217/40.967% decoder). They do not
establish a speedup or long-term stability. The numerical AAC path is unchanged.

### Deep-sleep build footprint only

Adding `-DeepSleepClock` to the same defaults links successfully. RTC text uses
2580 bytes, PCBs 2688 bytes, clock state 1064 bytes, timer data 36 bytes, alignment
4 bytes and the SDK's reserved tail 24 bytes. **1796 bytes** remain between the
static sections and reserved tail, before heap allocator overhead. This is not
a measured sleep stack margin or physical wake test. The artifact is saved as
`esp32c3-tcp-pcb-pool-sleep`; the board continues using an awake image.

## Reproduction

Build the awake candidate from these defaults:

```powershell
./idf/esp32c3-oled-native/build.ps1 -DependencyRoot C:/Work/yoRadio/.idf `
  -BuildDirectory build-tcp-pcb-pool -Sdkconfig build-tcp-pcb-pool/sdkconfig `
  -SdkconfigDefaults @('sdkconfig.defaults','sdkconfig.aac-ram.defaults',`
    'sdkconfig.cpu-profile.defaults','sdkconfig.cpu-profile-http.defaults',`
    'sdkconfig.iram-safe.defaults','sdkconfig.tcp-pcb-pool.defaults')
```

Use the [heap investigation's switch command](ESP32C3_HEAP_LAYOUT_20261001.md#reproduction-and-artifacts)
with `firmware/development/esp32c3-tcp-pcb-pool/sdkconfig`. Host tests:
`python tests/run-tcp-pcb-pool.py` in an environment with `cc`, pthreads and
ASan/UBSan. Use `tools/esp32c3_tests/ota_diagnostic.py` for new OTA runs; pass the
pool `app.bin`, board/host/serial arguments and a new output directory. The older
driver is retained at `tests/results/esp32c3-conservative-20261001/ota-repeat/run.py`
to reproduce the original HTTP-only result, but that result cannot qualify OTA
without checking the serial capture.

- [Exact candidate image/config/source manifest](../firmware/development/esp32c3-tcp-pcb-pool/manifest.json).
- [Retained results](../tests/results/esp32c3-tcp-pcb-pool-20261001/).

Before default promotion, resolve the ownership assertion and repeat OTA from
the candidate with the serial-health gate. Also complete longer mixed-codec/load
tests, trusted TLS, maximum configured audio buffer and physical sleep/wake checks.
The existing 24-bit FLAC and implicit same-header LC→SBR gaps are independent
of PCB placement and remain open.
