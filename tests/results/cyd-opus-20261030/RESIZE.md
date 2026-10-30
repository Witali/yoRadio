# Public Ogg Opus output resize: whole-input LX6 observation

The unchanged pinned Espressif Ogg/Opus decoder executes on ESP32 LX6 QEMU
with ESP-IDF 6.0.2. The complete 707097-byte
[`stereo-510-120ms.ogg`](../../fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg)
is supplied as one borrowed encoded input with data-bearing EOS. The fixture
contains 92 legal 120 ms stereo CELT packets. Each may produce 23040 PCM16
bytes, exceeding the production caller's initial 12288-byte capacity.

Three independent public decoder instances compare an unresized 24576-byte
reference with two retry policies starting at 12288 bytes. The first policy
retries unchanged input after resizing; the second would apply public consumed
input before retrying. Their code is identical except for that explicit policy.
No private decoder layout, repair, custom codec, physical board or network is
used. This is a diagnostic worker, not the complete production audio task.

| Strategy | Public calls | Resize requests | Final capacity | Full raw PCM bytes |
| --- | ---: | ---: | ---: | ---: |
| Unresized reference | 93 | 0 | 24576 | 2119680 |
| Retry unchanged input | 94 | 1 | 23040 | 2119680 |
| Honor consumed input | 94 | 1 | 23040 | 2119680 |

Both actual resize events occur on call 1 and expose:

```text
result=-8 len_before=707097 raw_len=707097 consumed=0 decoded_size=0 needed_size=23040 capacity=12288
```

Both retry instances consume all 707097 encoded bytes, drain to completion,
and match the complete unresized reference, SHA-256
`670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684`.
Each returns 92 PCM frames. No public decoder error occurs after resizing.
Because consumption on both errors is **zero**, these observations do not
exercise or distinguish a nonzero-consumption error policy. They do not justify
a production change on the assumption that this decoder consumed input on error.

The coordinator runs on core0; the diagnostic worker runs on core1 with
priority3 and a 16384-byte stack. Assertions, both idle watchdogs, stack
canaries, light heap poisoning and heap integrity remain enabled. Each retry
returns free heap to 282920 bytes. Final unregister retains 100 bytes relative
to the pre-registration measurement. Minimum observed heap is 229864 bytes;
unused worker stack is 4396 bytes. These are diagnostic measurements rather
than production radio/TLS/TFT memory or timing margins.

## Qualification boundary

Whole-input public resize/retry is qualified for this exact pinned decoder and
fixture. The following remain unexercised:

- Nonzero input consumption on a sizing error.
- Fragmented-input resize through the production pending-input/EOF helpers.
- Resize inside the actual production CYD tasks and queues.
- Output allocation failure, backpressure and physical output hardware.

Required Opus pre-skip/end trimming also remains unresolved. The raw result
contains 529920 frames. This fixture declares pre-skip 312 and terminal granule
528312, leaving 1608 terminal padding frames. Correct playback is 528000 frames
or 2112000 PCM16 stereo bytes. The raw integration identity above is not a
standard-complete playback oracle or an independent numeric conformance proof.
See [the Ogg/Opus work plan](../../../docs/CYD_OGG_OPUS_EOF.md) and
[the independently generated fixture timeline](../../fixtures/opus_ogg_long_packets/README.md).

## Saved evidence

`resize-captures.zip` deduplicates exact published payloads under
`blobs/<sha256>`. `resize-manifest.json` maps logical paths to sizes, hashes and
blob names. It preserves the original successful report, baseline,
interpretation, every native command log/status, actual SDK child status,
frozen harness/controller/registration, public vendor headers/source/archives,
configuration, compiler commands, link map and independent fixture provenance.
Replaceable unselected SDK scratch is inventoried by hash.

All ten compiled image payloads, including application, merged flash, boot,
partition and SDK compiler probes, are omitted entirely from the public archive.
Exact original hashes, sizes, roles and local-only
provenance remain. Original images remain unchanged in the ignored local
campaign. No encoded copy or semantic scanner override is used to publish an
excluded payload. The verifier checks the recorded image-hash bindings without
claiming to verify bytes that are not published.

Run the standalone data-only verifier:

```text
python -B tests/verify-cyd-opus-resize-checkpoint.py
```

It checks every published byte, exact source/status/record binding and both real
sizing-error witnesses, then independently reconstructs the encoded fixture's
CRC/framing/timeline. It imports only pinned reviewed canonical readers. No
archived program, compiler, decoder or emulator is started. The retained images
are diagnostics and must not be flashed as production firmware.
