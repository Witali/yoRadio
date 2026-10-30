# Fragmented public Ogg/Opus resize with production input helpers

The pinned Espressif Ogg/Opus decoder executes on ESP32 LX6 QEMU with
ESP-IDF 6.0.2. The complete 707,097-byte
[`stereo-510-120ms.ogg`](../../fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg)
contains 92 legal 120 ms stereo CELT packets. Its unchanged-vendor reference
matches the [separate whole-input resize checkpoint](RESIZE.md).

The diagnostic first decodes one complete borrowed input with data-bearing
EOS and a 24,576-byte output buffer. Fresh decoder instances then receive
4096-, 257- and one-byte input fragments, followed by separate caller EOF.
They compile and use the exact production pending-prefix and final-byte EOS
headers. Each starts with the original 12,288-byte PCM capacity and follows
the current production policy: grow the output buffer and retry unchanged
input when the public API requests more space.

No private decoder layout, custom synthesis, physical board, external network
or production source change is used. This is a direct diagnostic worker, not
the complete production audio task and its queues.

| Stream | Input feeds | Public calls | Resize requests | Final capacity |
| --- | ---: | ---: | ---: | ---: |
| Complete-input reference | 1 | 93 | 0 | 24,576 |
| 4096-byte fragments | 173 | 348 | 1 | 23,040 |
| 257-byte fragments | 2,752 | 5,506 | 1 | 23,040 |
| One-byte fragments | 707,097 | 707,099 | 1 | 23,040 |

All four streams consume every encoded byte, return 92 PCM frames, drain to
completion, and emit **2,119,680 PCM16 stereo bytes at 48 kHz**, SHA-256
`670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684`.
Every public PCM frame has the checked metadata. No decoder error follows
resizing.

Each fragmented stream encounters one actual nonterminal sizing error:

| Fragment size | Public call | Input length | EOS | Result | Consumed | Decoded | Needed | Capacity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4096 | 3 | 4095 | 0 | -8 | 0 | 0 | 23,040 | 12,288 |
| 257 | 63 | 256 | 0 | -8 | 0 | 0 | 23,040 | 12,288 |
| 1 | 8046 | 1 | 0 | -8 | 0 | 0 | 23,040 | 12,288 |

The vendor consumes zero bytes on these errors. Retrying the unchanged input
therefore preserves complete output for every observed schedule. A conditional
fresh strategy that would honor nonzero error consumption exists in the
diagnostic, but **no such instance runs**: the current policy succeeds and
every observed error has zero consumption. No empty-input retry runs either.
These facts do not establish behavior when a different decoder consumes input
on an error and do not justify changing production on that assumption.

All schedules report zero pending-prefix coalesces. The real shared pending
owner is called, but its allocation/recovery path is not exercised here.
Existing host tests remain separate evidence for those branches.

The coordinator runs on core 0; the worker runs on core 1 with priority 3
and a 16,384-byte stack. Assertions, stack canaries, light heap poisoning,
heap integrity and both idle watchdogs remain enabled. Each fragmented stream
restores free heap to 282,920 bytes. Final unregister retains 100 bytes relative
to the pre-registration measurement. Minimum free heap is 220,180 bytes and
unused worker stack is 4,172 bytes. These are diagnostic observations rather
than production radio/TLS/TFT memory or timing margins or zero-retention claims.

## Remaining qualification

Fragmented input, the exact production input helpers and the current public
resize policy are qualified for this pinned decoder and fixture. The following
remain unexercised:

- Nonzero input consumption on a sizing error and empty-input retry semantics.
- Resize inside the actual production CYD audio tasks and queues.
- Output allocation failure, deliberate backpressure and physical output.

Required Opus playback trimming remains unresolved. The raw stream contains
529,920 frames; pre-skip 312 and EOS granule 528,312 require discarding a
312-frame prefix and 1,608-frame tail. Correct logical playback contains
528,000 frames, or 2,112,000 PCM16 stereo bytes. The raw agreement above is an
integration reference, not standard-complete playback or an independent
numerical conformance oracle. See the
[required Ogg/Opus plan](../../../docs/CYD_OGG_OPUS_EOF.md) and
[independent fixture audit](../../fixtures/opus_ogg_long_packets/README.md).

## Preserved evidence

Campaign 01 and all native commands, including the real SDK child, terminate
with exit 0. Its original report, baseline and interpretation remain unchanged.
`resize-stream-captures.zip` deduplicates exact published payloads under
`blobs/<sha256>`; `resize-stream-manifest.json` maps each logical file to its
size, hash and blob. It preserves frozen harness/controller/registration,
production input headers, public vendor headers/source/archives, actual command
logs/statuses, configurations, compiler commands, selected compiled objects
and stack reports, link map and fixture provenance. Replaceable unselected SDK
scratch is inventoried by hash.

The separate whole-input RESIZE manifest/archive is linked by exact hashes
without duplicating that archive. The standalone verifier checks the original
whole-input report identity and complete raw reference agreement, and verifies
that checkpoint as data.

All compiled ELF/bin image payloads remain unchanged in the ignored local
campaign and are omitted entirely from publication. Exact hashes, byte counts,
roles and local-only provenance remain. No semantic scanner override or
encoded image copy is used. The verifier checks recorded image-hash bindings
without claiming to read omitted binary bytes.

Run the standalone data-only verifier:

```text
python -B tests/verify-cyd-opus-resize-stream-checkpoint.py
```

It checks every published byte, actual source/build/command/SDK-child binding,
the three real nonterminal sizing errors, exact shared input headers, cleanup
and independent encoded fixture CRC/framing/timeline. It imports only pinned
reviewed canonical readers and starts no archived program, compiler, decoder
or emulator. The diagnostic images must not be flashed as production firmware.
