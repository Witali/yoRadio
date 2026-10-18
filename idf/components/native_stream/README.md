# Portable native stream core

Shared C implementations for native ESP32 and ESP32-C3 firmware. No display,
pin, USB, sleep, target assembly or private decoder ABI belongs in this component.

- `stream_probe.h` and `stream_tags.h`: bounded fragmented signature and ID3 envelopes.
- `stream_frames.h` and `stream_confirm.h`: elementary MP3/ADTS boundaries and bounded candidate confirmation.
- `adaptive_input.c`: one-producer/one-consumer FIFO with explicit WRITING/READY/READING leases, bounded allocation, idle-only reclaim and independent caller-owned control storage.
- `stream_staging.h`: unpublished startup leases and bounded lookahead.
- `stream_encoded_router.h` and `stream_start.h`: producer adapters included after the service's packet types and queue helpers. The service owns generation/state policy and decoder drain behavior.
- `stream_body.h` and `icy_title.c`: fragmented ICY framing and bounded title parsing.
- `json_buffer.h` and `tls_stream_result.h`: bounded valid JSON and TLS EOF result preservation.

Queue transitions use a FreeRTOS `portMUX_TYPE`, including its ESP32 cross-core
lock. Heap allocation/free and payload copying stay outside the critical
section. Only the producer reopens a READY tail; READING/control/sole queued
nodes are ordering barriers. Buffer sizes and TLS reclamation policy belong to
each target and must be measured separately.

The C3 include-only compatibility files preserve existing build/harness paths.
Tests that extract function bodies follow those files to the canonical source
and record both source hashes. C3 compiles its compatibility translation units;
CYD registers this component. Each build has one definition per implementation.
