# CYD WebSocket DRAM options — read-only audit

Audited source: `7595a79958b8a2ef56babb24c43259fcf536b6dd`. No build, new runtime test, or source change was performed. RTC-on final-window results are a separate qualification; RTC-off HE-AAC/two-client results must decide whether further work is needed. No production implementation is selected here.

## Actual ownership and donor comparison

The measured classic-ESP32 ELF assigns these five HTTPD-owned objects 6,560 bytes in total (the same objects return to DRAM with RTC storage disabled):

| Owner | Bytes | Purpose |
|---|---:|---|
| `s_status` | 5,120 | Complete escaped status JSON, cached between revisions/heartbeats |
| `s_previous`, `s_current` | 508 each | Logical change detection and captured immutable status |
| `s_clients[2]` | 384 | Sessions, receive reassembly, individual deadlines/revisions |
| `s_sockets[10]` | 40 | HTTPD socket enumeration |

Evidence: `.build/cws24r/rtc-pdm-workspace/fixture-identity.json` symbol bindings; CYD `websocket_service.c:42–95,264–433`. These are storage sizes, not a newly measured free-heap margin. The roughly 4,899-byte worst-case escaped JSON regression and 5,120-byte capacity remain requirements.

The current donor has `s_broadcast_status[1280]`, a 48-byte current-message buffer, two status keys, and session slots for `CONFIG_LWIP_MAX_SOCKETS` (`esp32c3-oled-native/main/websocket_service.c:51–93`). Its legacy payload differs from CYD's combined `status`/`payload` JSON. Its field escaper explicitly preserves a bounded prefix when a field does not fit (`:290–301`); that smaller buffer cannot preserve CYD's complete worst-case fields. The donor still renders a complete contiguous string before sending (`:304–410`). It has no streaming or word-backed WS owner to transplant.

CYD already has the transferable ownership improvements: HTTPD-only workspace/session mutation, no queued payload/fd capture, logical status keys, partial-I/O completion, finite deadlines, shared RFC message parsing, and bounded command handling. CYD additionally admits exactly two sessions and uses an existing timer/event-loop path instead of a dedicated WS task. There is no overlooked donor WS stack or duplicate 5-KiB serializer to remove. Stream/decode/output bindings remain core0/priority3, core1/priority5, core1/priority6 (`audio_service.c:1615–1618`); their board-defined stacks and all lifecycle atomics stay outside these options.

## Bounded options if the RTC-off controls establish a deficit

| Option | Estimated DRAM benefit | Main seam / cost |
|---|---:|---|
| Smaller writes of the existing contiguous payload | **0 bytes** | `send_complete_frame_bytes` already handles partial writes. Retaining `s_status` retains its cost. |
| Stream one existing WS frame using a count pass and a 256/512-byte staging buffer | **4,864 / 4,608 bytes** | Replace the complete rendered owner with a sink-based serializer; one header, then ordered payload writes. |
| Stream one fragmented WS message through a 256/512-byte staging buffer | **4,864 / 4,608 bytes** | Reuse SDK fragment framing; new logical-message send state and total deadline. |
| Word-backed IRAM copy plus 256/512-byte DRAM staging | Up to **4,864 / 4,608 bytes**, conditional | About 5,120 bytes of genuinely spare instruction-only IRAM, custom word access and staging; no guaranteed gain from a generic 32-bit allocation. |
| Remove one redundant persistent status key | **508 bytes** | New capture/compare/update design; not an unported donor improvement. Insufficient alone. |
| Reuse another existing owner | No demonstrated 4–7-KiB saving | No compatible idle persistent byte buffer was found. HTTP response bodies are stack locals; static-file workers and audio/TLS owners can run concurrently. |

The streaming estimates assume a static staging buffer replacing `s_status`, unchanged snapshot/session/socket owners, and no HTTPD stack increase. They are predictions requiring ELF/heap verification. A full-size temporary heap allocation would only move the same peak demand and add failure/fragmentation paths.

### One frame, multiple transport writes

`format_status` is one bounded JSON walk (`websocket_service.c:321–364`); `send_status` and `status_work` already run synchronously under exclusive HTTPD ownership (`:378–433`). A count-only walk over the captured key can determine the exact payload length, followed by the same walk into a small flushing sink. Keep the existing 5,120-byte logical cap, escaping/replacement rules and identical final JSON; do not recapture live state between count and emission or between peers.

The pinned SDK `httpd_ws_send_frame_async` writes a header and then a contiguous payload synchronously (`.idf/v6.0.2/components/esp_http_server/src/httpd_ws.c:403–460`), so merely passing smaller transport limits saves no application buffer. A real streaming implementation needs a narrow status-frame writer with validated unmasked TEXT/FIN/length framing and existing `send_complete_frame_bytes` transport/deadline handling. Avoid relying on the SDK's incidental `payload=NULL,len>0` header-only behavior. Preserve both plain and TLS transport paths (`native_web_transport.c:165–175`). This keeps wire framing unchanged but adds framing/serializer code that needs differential tests.

### Fragmented message

This can avoid a count pass and reuse the public SDK frame API: initial TEXT/FIN=0, continuation frames, final continuation/FIN=1. All fragments must be one status message, never separate JSON messages. Control frames may occur between fragments; other data messages must not interleave. UTF-8 may cross fragment boundaries while the complete message stays valid. These are standard behaviors, not a relaxed protocol ([RFC 6455 sections 5.4–5.6](https://www.rfc-editor.org/rfc/rfc6455.html#section-5.4)).

Set one absolute **one-second send deadline for the entire logical status message**, independently for each client; do not call the current `send_text` once per fragment because it resets the deadline every call (`websocket_service.c:223–230`). Retain independent receive/control budgets and existing incoming-message timeout. A failed partial message closes that client; only successful final FIN advances its revision. HTTPD must own the entire synchronous send and reset staging state before the next peer. Exact-buffer multiples need a correct final fragment, potentially an empty final continuation. Fragmentation saves no more RAM than single-frame streaming and adds message-state/interop coverage.

### Word-only IRAM

The pinned SDK explicitly restricts `MALLOC_CAP_32BIT` storage to word accesses; byte/halfword operations can fault. Its byte-accessible IRAM exception option is single-core only, so it is unsuitable for this dual-core CYD (`.idf/v6.0.2/docs/en/api-reference/system/mem_alloc.rst:40–44,129–135`). A `uint32_t[]` cast to `char *` is not a fix: JSON helpers, `strlen`, UTF-8 checks and transport/TLS code use bytes. A viable variant needs word-pack/unpack accessors and DRAM staging, with no IRAM pointer escaping to those APIs.

Also distinguish instruction-only IRAM from D/IRAM aliases: generic `MALLOC_CAP_32BIT` can fall back to memory already usable as DRAM (`components/heap/port/esp32/memory_layout.c:16–52`). Demonstrate the actual address/capability/linker allocation and net 8-bit heap gain, and inspect target instructions for word-only access. Host ASan and permissive emulator RAM do not establish bus-width safety. This is a new hardware-specific maintenance cost, not donor reuse.

## Reuse boundaries and qualification effort

HTTP status/health bodies are already automatic 2,560/2,304-byte arrays (`web_service.c:38–96`), not a second persistent owner. Borrowing them requires a larger call frame or redesign; current HTTPD stack is 6,144 bytes (`:416–417`). Sharing a static-file chunk is unsafe because `web_static.c:108,137–145` serves asynchronous workers. Codec, DMA, decoder-input and TLS owners overlap the HTTPD task on the other CPU and must not become new shared/private-codec storage. The existing request-TX release is a client-handle owner contract, not a spare WS buffer.

If controls fail, first record the actual allocation/heap deficit and compare bounded streaming prototypes; do not adopt a redesign solely to erase the entire 6,560-byte RTC difference. Streaming addresses roughly 4.5–4.75 KiB. Reaching 6–7 KiB would need a separately justified saving, such as a fully qualified HTTPD-stack reduction after broader HTTP serializer work; no such reduction is established here.

Required evidence before selecting any implementation:

1. Differential full JSON against the existing formatter: every field, maximal six-byte escapes, invalid/truncated UTF-8, exact capacity and chunk boundaries. Share the escape implementation rather than maintain two subtly different walkers.
2. Existing `tests/run-cyd-websocket.py` ASan/UBSan lifecycle/SMP/slow-peer suite plus wire-level output tests. Exercise one-byte writes, TLS WANT_READ/WANT_WRITE, EAGAIN/EINTR, timeout between chunks, stale fd/session reuse, stop/restart, two peers, and failure during a partial payload. Verify one total one-second budget per peer.
3. For fragmentation, independently reassemble frames and verify FIN/opcodes, control interleaving, no data-message interleaving, empty final continuation and UTF-8 split points. Keep existing inbound RFC6455 tests unchanged.
4. Matched target ELF storage, static frames/stack headroom and full RTC-off HE-AAC/TLS/two-WS runs through final WebUI/peer closure on all three outputs, with unchanged buffers/core bindings and every original NONPASS retained. Queue-drop telemetry stays visible separately.

The low-benefit criterion from the refactoring skill favors no change if RTC-off controls already meet the required margin, and rejects a broad shared-buffer/codec-ownership redesign for a speculative few hundred bytes. This audit is a conditional options list, not a production recommendation.
