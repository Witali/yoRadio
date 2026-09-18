# ESP8266 Opus ASM: arena ownership and reconnect fragmentation

Date: 2026-09-18. Scope: full native radio, CPU160/QIO40, accepted
eBands-final ASM chain, I2S PDM32 GPIO3, WebUI. No serial access or partition,
SPIFFS, playlist, Wi-Fi adapter or production-default changes.

## What failed

The preceding [local-station test](ESP8266_LOCAL_RADIO_2026-09-18.md) captured
three failures allocating the 6144-byte Opus scratch area:

| Attempt | Free DRAM | Largest free block | Required scratch |
| --- | ---: | ---: | ---: |
| Buffered hybrid24 reconnect | 8216 B | 4400 B | 6144 B |
| Paced hybrid24 warm restart | 10212 B | 5600 B | 6144 B |
| SILK12 reconnect | 8484 B | 4920 B | 6144 B |

These are direct evidence of insufficient contiguous memory, not evidence
that the decoder needs a new allocation on each audio frame. Also, each
total is less than scratch6144 + required free-DRAM reserve4096 = 10240 B,
even before allocator overhead. Both fragmentation and scarce total DRAM
matter; rearranging blocks alone would not restore the intended reserve.

The SDK allocator coalesces adjacent freed blocks, but cannot move live
network/HTTP allocations out of holes. Freeing large decoder blocks and
then allocating network objects before reinitializing Opus can prevent a
later large allocation. That is a concrete avoidable lifetime pattern;
we do not have an allocation trace identifying every intervening object.

## Does the ASM decoder use the common codec arena?

Yes. The normal radio uses the same ownership/allocation wrapper for C and
ASM. It does not instantiate a separate private heap for assembler code.

| Storage | Allocation and lifetime |
| --- | --- |
| Shared 16-KiB IRAM word arena | Reserved once by `CodecArenaPreallocateMp3` (historical name); reused by MP3/AAC/Opus, only one owner |
| Opus workspace, persistent state and 6144-B scratch | `CodecArenaCalloc(CODEC_ARENA_OPUS, ...)`; retained for the decoder lifetime |
| Temporary internal Opus arrays | Bump allocation and mark/restore inside the bound IRAM/DRAM areas, not heap malloc/free per packet |
| Compressed input and output PCM | Separate long-lived bridge allocations; not part of `CodecArenaCalloc` |
| Function stack frames | Task stack, separate from codec arenas |

Important: the DRAM "arena" is a **shared accounting/ownership manager**,
not one preallocated contiguous DRAM slab. `CodecArenaBind(nullptr, limit)`
selects separate tracked heap allocations. Its capacity limit is not an
extra reserved buffer. The common IRAM allocation really is contiguous.
Thus using a common arena does not, by itself, eliminate DRAM fragmentation.

`opus_allocate` binds state/scratch/IRAM through `native_opus_init_ex` and
`yoradio_opus_memory_bind`. The linked normal firmware's
`quant_all_bands` and `celt_decode_with_ec_dred` call the same scratch
mark/alloc/restore helpers. Persistent history is kept below the reusable
scratch cursor. Reset of a same-kind codec reuses storage. Switching codec
kind frees the previous codec first. The retained 16-KiB IRAM allocation is
intentional shared storage, not a leak.

The raw CPU benchmark also uses the shared word arena, but allocates its
state/scratch/PCM under a simpler benchmark lifetime. Its memory results
cannot substitute for full-radio reconnect/WebUI testing.

Relevant code:

- [Native common arena](../esp8266/rtos-sdk-native/components/helix_codecs/CodecMemoryArena.cpp)
- [Codec bridge and reserve check](../esp8266/rtos-sdk-native/components/helix_codecs/codec_bridge.cpp)
- [Opus arena binding](../esp8266/rtos-sdk-native/components/opus_decoder/native_opus.c)
- [Scratch allocator](../esp8266/rtos-sdk-native/components/opus_decoder/opus_memory.c)
- [Radio reconnect lifecycle](../esp8266/rtos-sdk-native/main/audio_service.c)

## Two corrections

1. **Retain Opus storage through a non-memory open failure.** Previously a
   cached decoder was destroyed after *any* failed `open_http_stream`, even
   a timeout/refusal/HTTP-status failure. Now it survives the existing
   second bounded attempt. ENOMEM, ENOBUFS or actual free DRAM below4096 B
   still request a cold retry. Stop, final failure, codec replacement,
   decode failure and unsuccessful close still perform cleanup. There is
   no unbounded retry, new task, buffer or static RAM. Clear errno before
   opening so a prior operation's ENOMEM cannot trigger unnecessary release.
   Commit `5a486857`.
2. **Check actual byte-addressable DRAM, not combined free heap.**
   `update_codec_memory` used `esp_get_free_heap_size`, which this SDK
   implements using MALLOC_CAP_32BIT and can count spare IRAM too. Opus
   now checks MALLOC_CAP_8BIT for its minimum4096-B reserve. Other codecs'
   policy is unchanged. This does not create more RAM; it prevents a
   misleading successful initialization with inadequate network headroom.
   Commit `156f5c0a`.

Successful-close Opus retention was already present in the preceding
firmware; correction1 extends it to the failed-open branch. It is not a
claim that reconnect reuse was absent everywhere.

The capability distinction follows the
[official Espressif heap API](https://docs.espressif.com/projects/esp8266-rtos-sdk/en/latest/api-reference/system/mem_alloc.html).
The checked SDK source is ESP8266_RTOS_SDK `system_api.c` and
`heap/src/esp_heap_caps.c`; free-size totals sum regions matching the
requested capabilities. SDK HTTP asynchronous-request cloning also makes
short-lived allocations, while server startup buffers have a different,
long-lived lifetime. No SDK HTTP allocator leak was established here.

## Regression coverage

- 19/19 lifecycle/reconnect tests, no skips: eight bridge configurations,
  100 mixed-codec cycles per lifecycle configuration, injected allocation
  failures and ASan/UBSan cleanup checks.
- Regression first reproduced the reserve defect: abundant combined heap
  but actual DRAM one byte below the required reserve was incorrectly
  accepted. Corrected code rejects it; the exact boundary still succeeds.
- Ten independent sanitizer reconnect repetitions passed. Cover timeout,
  refusal, reset, unreachable host, protocol error, unset/stale errno,
  ENOMEM/ENOBUFS, DRAM4095/4096, final failure, Stop, cancellation and
  codec changes. Allocations/frees pair, except the intentional shared IRAM.
- 5/5 local-station tests: CRC-valid encoded prefix with unchanged packets,
  paced/buffered framing, ten valid streams alternating with ten HTTP503
  responses, then the original full stream. HEAD/invalid requests do not
  consume the fault schedule.

New replay tool: `tools/esp8266_opus_profile/reconnect_radio.cjs`.
It serves one explicit own-signal file on a bounded LAN listener, never a
directory. Full physical results are recorded below; host mocks do not
prove absence of leaks in the entire Wi-Fi SDK.

## Full firmware and physical validation

Artifact: `firmware/development/esp8266-opus-live-asm-heapreserve-20260918/`.
Application890352 B (+80 B from the previous accepted ordinary image),
SHA256 `dfa1c0a298dde56f33d5bb88627b4c9aa643deca12d5329ce4a0398e6f60b273`.
All18 accepted ASM transformations relocated with exact graph/semantic
checks; zero static-RAM delta. The new branchless eBands-SRC experiment is
**not** included. PCM2x960, DMA2x128 words, input2048 B, scratch6144 B,
LEDoff and the prior network/clock-compensation settings are unchanged.

OTA returned HTTP200/OK and the running slot changed from0x110000 to0x10000.
This is the normal player plus diagnostics, not the raw decoder benchmark.

Physical test: own 300-s SILK12/20-ms fixture, paced LAN source on the PC's
wired address. Ten 3013.5-ms valid prefixes alternated with ten HTTP503s;
the board requested every subsequent stream, including full stream21.
No Opus allocation/init failure was latched (`stage=0` throughout final
inspection). This verifies recovery across those ten injected failures,
not the exact address of each target allocation; the latter reuse is
covered by production-branch host tests.

The full-radio qualification **still failed**:

| Measurement | Result |
| --- | --- |
| First closed window | 25002 ms, 20034 ms PCM, 2765 underruns; includes the deliberate reconnect interval, not an ordinary continuity baseline |
| Later closed-window snapshot | 36848 ms, 18073.5 ms PCM, 8815 underruns, age58888 ms; stale/stalled and rejected |
| First health response after window | Combined free heap6496 B, free IRAM36 B, response1065 ms |
| Following status request | 15-s timeout, retained as failure |
| Final status | Stopped, CONNECTION ERROR, RSSI-48 dBm, combined heap26060 B, boot minimum4168 B |
| Last init-failure/current-DRAM endpoint | stage0, free DRAM25936 B, largest19084 B |
| Seven post-Stop snapshots over60 s | DRAM26288..26464 B, largest19856..20032 B; all HTTP200, 14.5..24.6 ms |

After the ten scheduled faults the full stream also reconnected twice
without any injected HTTP failure, then stopped with CONNECTION ERROR.
No DECODER INIT ERROR appeared in this run. This distinguishes the tested
memory correction from remaining network/output latency; it does not prove
the whole firmware leak-free or audio reliable. No acoustic recording was
made. DMA counters in a stopped snapshot include silence/recovery activity
and are not reported as an active-audio underrun rate.

Post-Stop memory was stable in this short observation but did **not** return
to the pre-test approximately30-KiB level. The codec lifecycle harness
returns its DRAM allocations, but target allocation tracing is still needed
to identify this remaining roughly4-KiB difference. SDK TCP state may
outlive socket close (its TIME-WAIT expiry is2xTCP_MSL), yet that mechanism
alone is not proof that it explains these particular retained bytes.

Raw evidence: [results directory](results/esp8266-opus-memory-reconnect-20260918/).
It includes the failing reserve test before the fix, all ten sanitizer
repeats, build/relocation and OTA reports, every physical window, server
fault log and post-Stop DRAM snapshots. The source remains unchanged during
the build; manifest source revision is156f5c0a.

At completion the board was explicitly stopped through WebSocket, clearing
the error. The finite test server was stopped; no listener remains on8765.
The corrected full firmware remains in slot0x10000. No serial reset or
computer shutdown was performed.

## Remaining work

- [ ] Determine all allocations responsible for persistent holes using a
  bounded low-overhead trace, if failures recur; distinguish network
  retention from decoder lifetime and total-headroom limits.
- [ ] Qualify repeated full-radio codec switches and long playback with
  concurrent WebUI without unbounded memory growth.
- [ ] Consider a reusable DRAM pool only after measuring total capacity and
  the largest boot-time block. Do not blindly reserve the whole arena limit.
- [ ] If considering segmented scratch/PCM loans, prove contiguous-array
  requirements and regenerate/test the frozen ASM ABI. The existing low-RAM
  profile changes the scratch-mark layout and is not a safe flag-only switch.
- [ ] Complete the separate CPU target and continuous-audio qualification.
  These memory corrections do not establish a decoder speed improvement.
