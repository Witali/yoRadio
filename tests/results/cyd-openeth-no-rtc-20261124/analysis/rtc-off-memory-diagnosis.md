# RTC-off HE-AAC memory diagnosis

All three preselected RTC-off runs are now terminal **NONPASS** for `Unexpected allocation failure count`. Their original reports/UART remain unchanged. The companion JSON binds reports, UART, fixture/config/controller inputs and the exact inspected source bytes. No compiler, new guest, or production change was used for this analysis.

| Output | Allocation failures at EOF | Last size / caps | Minimum heap | OpenETH RX waits | Audio driver errors/timeouts/short writes |
|---|---:|---|---:|---:|---|
| Legacy | 171 | 1,512 / 6,144 | 964 | 0 | 0 / 0 / 0 |
| PDM | 25 | 1,512 / 6,144 | 972 | 0 | 0 / 0 / 0 |
| Continuous | 35 | 1,512 / 6,144 | 2,312 | 0 | 0 / 0 / 0 |

Every run delivers 614,400 PCM frames with SHA256 `44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362`, the complete TLS response/full-record geometry, all three identical WebUI assets, two WS clients' idle/playing/EOF observations, three application pongs each, and close code 1000. PDM completion-queue drops are 0; the DAC metrics report null. None has a successful `post_eof_health` sample; the allocator gate already failed. Preserve that distinction and do not substitute `last_reachable_health` for the missing final-window proof.

## Phase bounds actually observed

- **Legacy:** allocation count 0 at first active 22.161 s and after the playing asset at 29.053 s (heap 7,528, largest 5,376, minimum 3,048). At sampled EOF 324.106 s it is 171; unchanged at last reachable 333.055 s. The first failing allocation is somewhere in that interval, not timestamped by the existing hook.
- **PDM:** count 0 at first active 25.642 s; count 1 at the playing/WebUI sample 34.910 s (heap 6,188, largest 3,840, minimum 972); count 25 at EOF 102.325 s, unchanged at 110.003 s.
- **Continuous:** count 0 at first active 24.383 s; count 1 at playing/WebUI 36.409 s (heap 6,716, largest 4,352, minimum 2,312); count 35 at EOF 56.661 s, unchanged at 64.561 s.

These are guest uptime observations, not physical timing measurements. Each last allocation record is 1,512/6,144. The snapshots do not preserve earlier failed sizes or the failing task/caller. A failure count counts attempts/retries, not simultaneously missing buffers; multiplying it by 1,512 or subtracting 6,560 from a heap number would not give the required reserve. Continuous fails despite total historical minimum exceeding 1,512: contiguous capability-qualified availability and allocator timing matter. Heap has recovered to about 165–167 KiB by EOF, which is compatible with transient pressure; these observations alone neither identify a leak nor exclude one generally.

## Attribution: strong source-sized TX-pbuf inference, no captured stack

`native_health.c:16–24` records only count, last size and capabilities, discarding the allocator function argument. Caps 6,144 are `MALLOC_CAP_DEFAULT | MALLOC_CAP_INTERNAL` (`heap_caps.c:107–110`, `esp_heap_caps.h:42–43`), not a DMA request. All three UARTs contain zero `CYD_OPENETH_RX_WAIT` episodes, so the previously identified OpenETH RX-copy allocation failure is not observed here.

The lwIP TX allocation fits **exactly**:

1. Actual compiled legacy ELF DWARF reports `sizeof(struct pbuf) = 16`; `LWIP_PBUF_REF_T` is `u8_t` (`lwip/src/include/lwip/opt.h:1633–1634`).
2. IPv6 is off, MSS is 1,440, alignment is 4. `PBUF_TRANSPORT` reserves 14 + 20 + 20 = 54 bytes, aligned to 56 (`pbuf.h:78–93`, `lwipopts.h:112`).
3. With current `TCP_OVERSIZE_MSS`, `tcp_pbuf_prealloc` is compiled; ESP-IDF forces `LWIP_NETIF_TX_SINGLE_PBUF=1`, which makes it allocate `max_length` even for short writes (`lwipopts.h:765`, `tcp_out.c:238–243,613`). `pbuf_alloc(PBUF_RAM)` allocates 16 + 56 + 1,440 = **1,512 bytes** (`pbuf.c:273–284`).
4. `mem_malloc` reaches libc malloc and therefore the same caps (`mem.c:207–209`, `lwipopts.h:1730–1735`). The netconn write path treats `ERR_MEM` as temporary and retries after sent/poll callbacks (`api_msg.c:1840–1857`), explaining successful responses alongside failure counts.

This establishes a matching source allocation and recovery mechanism, not proof that every one of the 171/25/35 failures came from that call. The probable stack is socket/netconn write → `tcp_write` → `tcp_pbuf_prealloc` → `pbuf_alloc` → `mem_malloc`; current telemetry supplies no actual call stack, task, PCB, or TX-versus-clone attribution. The companion JSON keeps this explicitly classified as inference.

## Next bounded diagnostic gate

Before choosing a serializer redesign or changing global TCP oversizing, first try a **diagnostic-only link wrapper** through the existing `attach.cmake` seam: `--wrap=pbuf_alloc`, with the exact public signature `struct pbuf *pbuf_alloc(pbuf_layer, u16_t, pbuf_type)`. Call `__real_pbuf_alloc` once and preserve its return. Only on NULL, record layer/type/requested length, source-derived allocation size where applicable, and the immediate caller PC in a small fixed atomic counter table with an overflow bucket. The caller can identify the cross-object `tcp_out` site more directly than a malloc wrapper, whose caller would be `mem_malloc`.

Link wrapping does **not** guarantee coverage of calls resolved locally inside `pbuf.c`; it also cannot distinguish every internal allocation-failure branch from its return alone. Before making a runtime call-site claim, verify actual linked `tcp_out` call references and wrapper binding by map/disassembly, symbolize captured PCs against that exact ELF, and compare probe failure deltas with the original global allocation count. Keep unexplained failures visible. RAM allocation size is explicitly derived from the pinned layer/alignment/type formula; do not label it a directly observed malloc argument. If wrapper coverage is inadequate, only then consider a source-pinned build-local SDK overlay at the real failure branches.

No printf/logging, heap queries, unwinding, allocation, socket operations or blocking locks from the failed-allocator callback. The proposed wrapper records after the real call returns; it needs no changes to that callback. If safe, attach an already-cached phase enum and a pre-registered numeric task tag using proven nonallocating 32-bit operations. Register tags outside the failure path; record unknown when context is unavailable. Drain/snapshot/print later after PCM EOF through an existing diagnostic owner, preserving any additional counts through the final observation. Avoid 64-bit atomics or task-name discovery in the failure path. Preserve its exact DRAM overhead and acknowledge that even a small diagnostic owner can change a marginal run's count.

Gate requirements: exact real-call forwarding and NULL-only counters under controlled failure, layer/type/size/caller-PC classification, no allocation or extra logging by the hot-path probe, unchanged retry/return behavior, bounded overflow/concurrent snapshot tests, and target code/config/image/wrapper-reference binding. Then repeat the same RTC-off controller on all outputs. Proceed only when the pbuf counters explain the relevant allocator failures, or report the unexplained remainder. This diagnostic is not implemented here.

## Practical options after attribution

The earlier [WS options](ws-memory-options.md) remain bounded alternatives. A real sink-based status serializer can remove the persistent 5,120-byte rendered owner while retaining a 256/512-byte staging buffer: predicted DRAM release 4,864/4,608 bytes, with full escaped-message capacity and both clients intact. That reserve could help full-MSS pbufs, but must be measured by ELF/heap and the original zero-failure runtime gate; no success is inferred by arithmetic. Keep one absolute one-second logical-message send budget per peer, SMP stop/reuse rules, receive/control budgets and all audio core/stack bindings.

Splitting the **existing** payload into smaller transport writes retains its 5,120-byte owner and, with the current single-pbuf/oversize path, can still allocate full-MSS pbufs. Disabling `TCP_OVERSIZE` may change short-write allocation behavior because it selects a different preallocator branch, but also changes global TCP coalescing/packet behavior, does not remove full-size segment needs, and is not a demonstrated fixed 4–7-KiB saving. Do not select it before the failure-class gate.

Stack shrinking is also unproven: HTTPD is 6,144 bytes, static worker is 3,072 + 1,024 = 4,096, lwIP TCPIP is 3,072, and stream/decode/output remain 6,144/16,384/4,096. These are live owners with nested parser/TLS/copy paths; no peak call-stack or high-water evidence here authorizes reducing them. The boot log's 67-KiB word-only IRAM pool makes the earlier IRAM option physically plausible, but byte-safe access, actual allocation region and net DRAM benefit still need proof. No new private codec owner, reduced client/payload limit, audio-buffer reduction, or production change is recommended.
