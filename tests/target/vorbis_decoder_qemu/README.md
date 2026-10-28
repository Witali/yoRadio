# Persistent raw decoder on native QEMU

This isolated diagnostic firmware calls the public persistent
`native_vorbis_decoder` owner directly. It does not use the older batch
synthesis helper and does not register a production decoder or audio task.

The controller preserves all 31 original streams, 434 raw packets and 738,560
PCM bytes. It checks every S16 value against both the original retained
libvorbis references and the saved Xiph packet capture, with the unchanged
maximum absolute error of 2 and all 14 original relations. Full PCM bytes are
saved, including the packet spans; there is no alignment, scale or channel fit.

`transport.json` records the original raw-fixture contract: complete octet bit
extents, preserved packet granules, a terminal EOS packet and no sequence gap.
The generated C header contains literal arrays for these fields. The target
passes them unchanged. This is fixture metadata with provenance to the pinned
previous native synthesis controller, not recovered Ogg/container validation or
an inference from HTTP EOF. No synthetic flush packet is added.

Each packet is measured without owner allocation or state advancement. A real
refusal precedes successful decoding: a capacity one S16 element too small, or
an unaddressable capacity for the zero-output priming packet. Output/result
bytes and committed metadata are checked after refusal. After terminal EOS,
both measure and process refuse; reset performs no allocation; the first two
packets are retried with semantic result equality and a full PCM `memcmp`.
Caller header/allocator/packet storage is overwritten after its authorized
borrow. Clear must null the handle before allocator callbacks, release every
owner allocation, and accept repeated/null clear calls. Tracked owner payload,
caller PCM payload and per-allocation guard overhead are reported separately.

Before the original corpus, an independently decoded legal 255-channel/8192
setup requests its 8,355,840-byte history through real native `malloc`. The
fixture expects `NO_MEMORY`, records the actual failed request, allocation
attempts and complete cleanup, then recovers through the full original corpus.
`resource.json` retains the vector and host-builder provenance. This control
uses no allocator budget and does not claim the large decoder fits native RAM.

The coordinator stays on core 0. The priority-3, 16 KiB worker runs on core 1
on ESP32 and core 0 on ESP32-C3. Watchdog and idle checks remain enabled. The
fixture yields at packet and bounded PCM chunk boundaries. The controller owns
each process through its terminal state and preserves source/configuration,
SDK/build/image hashes, compile flags, stack records, symbols and full logs.

Use the project Python explicitly from the review worktree, with a fresh
output directory for each attempt:

```powershell
C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -B -X utf8 tests/test-vorbis-decoder-qemu.py --target esp32 --output .build/vorbis-decoder-esp32-20261028-01
C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -B -X utf8 tests/test-vorbis-decoder-qemu.py --target esp32c3 --output .build/vorbis-decoder-c3-20261028-01
```

`--protocol-only` checks the pure log parser against the complete synthetic
transcript and 24 malformed transcript controls. It does not qualify native
execution. `--prepare-only` freezes sources and input data without launching
the SDK. A completed native campaign is required for target qualification.
