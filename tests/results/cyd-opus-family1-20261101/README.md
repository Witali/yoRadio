# Public family 1 playback observation

The pinned Espressif Ogg path returned `ESP_AUDIO_ERR_NOT_SUPPORT` (`-7`) for
all twelve real cases: complete creator-valid family 1 layouts with 3, 6 and
8 channels, measured through stock public Ogg decoding first and then the
current playback wrapper, each with whole-input and 257-byte schedules.
Every handle opened and closed; no PCM, output layout or resize was reported.
The vendor logged failure to create its Opus decoder. No public allocation
failure was returned. This is an observed playback gap, not a permitted
resource simplification or a claim that every multichannel layout fails.

| Encoded channels | Streams / coupled | Full fixture bytes | Whole stock/wrapper consumed | Split stock consumed | Split wrapper consumed |
|---|---|---:|---:|---:|---:|
| 3 | 2 / 1 | 6254 | 1061 | 1285 | 1061 |
| 6 | 4 / 2 | 12063 | 1832 | 2056 | 1832 |
| 8 | 5 / 3 | 15928 | 2205 | 2313 | 2205 |

Error cases stop at the genuine refusal. They do not claim complete input
consumption, successful EOS/drain or PCM that was never produced. The full
original fixtures remain available and independently validated.

Creator libopus 1.4's public surround encoder generated eleven 20 ms packets
per fixture, using its default family 1 mappings. Every channel carries a
distinct active signal; LFE is 73 Hz. A separate public multistream float
decoder read every packet and all channels: 10560 raw frames and 9600 logical
frames. The declared stereo reference matrix includes every speaker, including
LFE; no new numeric acceptance tolerance is used. Creator libogg 1.3.5 separately
walked each complete Ogg file with whole/257 feeds, reconstructed all original
audio packets byte-for-byte, and reported zero synchronization errors or holes.
Eighteen data-only framing/malformed-input controls also passed.

The native SDK6.0.2/LX6 build and QEMU completed with terminal zero. Actual
GCC/Ninja records bind 5 selected translation units and 206 dependencies. Only
the current public wrapper, shared input/timeline/trim owners and production
registration were consumed; the diagnostic does not compile audio_service or
physical output. The worker runs on core1, priority3, stack16384. Production
task profiles were not changed. Final free heap was 283228 bytes, minimum
266652, stack-free13628, with heap integrity intact.

Repeated heap was not stable: after-case free heap fell by 24 bytes per case;
388 bytes remained after unregister. These cases also finish two empty PSA
hashes each. No empty-hash control was run, so attribution to the codec versus
the diagnostic/crypto layer remains open. Open/close accounting alone does not
qualify leak-free recovery.

The original host sandbox refusal, SDK sandbox activation failure, printf
format compile failure, earlier successful host checkpoint and final corrected
captures are preserved. The WSL child status is the original DWORD4294967295,
not a shell-normalized status1. Installed SDK/vendor trees were unchanged.

Run the data-only verifier:

```powershell
python -B tests/results/cyd-opus-family1-20261101/verify.py
```

It checks exact source/process/build bindings, actual public events and six
contradictory controls. It starts no SDK, emulator or decoder and reads no omitted
binary/audio/PCM payload. Those payloads remain local with explicit byte/hash
identities. The archive is an observation record, not decoder conformance or
physical-output qualification. No production source was changed by this work.

Mandatory family0/1 playback is specified by
[RFC7845 section5.1.1.5](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.1.1.5).
The public composition alternative is a separate next experiment; this record
does not claim that alternative works.
