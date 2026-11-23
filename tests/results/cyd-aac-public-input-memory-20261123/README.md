# Public AAC input and output-buffer memory comparison

All 14 isolated ESP32 SDK 6.0.2/QEMU cases pass with the unchanged public
Espressif archives. Complete PCM matches the previous direct-public baseline:
529,408 stereo frames for LC and 614,400 full-rate stereo frames for HE.
The four original AAC-Plus on/off controls retain their original identities.
All 14 handles close, input bytes remain unchanged and repeated cases
restore heap. No production decoder or firmware image changes in this check.
The full HE-AAC/TLS/TFT/WebUI resource gate remains **NONPASS**.

## Matched fragmented-input observations

Each pair uses 8,192 PCM bytes and reveals the original encoded input in
257-byte increments. Parsed mode sends the available bytes to the ordinary
public simple decoder. Frame mode waits until a complete ADTS frame is
visible and uses the documented `use_frame_dec` mode. Both modes must emit
the entire original PCM, including the final tail.

| Source | Public input mode | Process calls | Free heap before close | Minimum sampled after process |
| --- | --- | ---: | ---: | ---: |
| LC | Parsed | 2,244 | 219,936 | 219,788 |
| LC | Complete frame | 517 | 221,012 | 220,864 |
| HE | Parsed | 699 | 163,856 | 163,708 |
| HE | Complete frame | 300 | 164,492 | 164,344 |

At this input split, complete-frame input saves 1,076 live bytes for LC
and 636 for HE. With the complete input already visible and equal 12,288-byte
PCM buffers, the saving is only 152 bytes for each codec profile. These
figures do not justify introducing another production frame assembly owner
to solve the full-application shortage. Call counts include parser input
collection and are not a CPU benchmark.

Availability grows a contiguous flash view. No separate transport or frame
assembly storage is allocated by this reference. `live_free` is a snapshot
after hashing and before closing the decoder; the minimum is sampled after
public process calls, not the global/transient heap peak. This is neither
TLS nor a measurement of the production pending-input owner.

## Output growth controls

Four complete-frame cases start with 12,288 or 1,024 PCM bytes. Two ordinary
parser cases also start with 1,024 bytes. Every small-buffer case genuinely
grows once to the public `needed_size` of 4,096 bytes; the decoder consumes
zero encoded bytes on that growth call. All complete PCM identities match.
HE at 4,096 output bytes needs two successful output chunks per ADTS frame.
The empty-input resize-retry path is supported by the fixture but was not
exercised by these actual library responses.

For whole-input HE in parsed mode, reducing the final PCM capacity from
12,288 to 4,096 increases live free heap from 160,244 to 164,580: 4,336 bytes,
rather than the nominal 8,192-byte buffer difference. An internal staging
allocation is a possible explanation; it has not been independently
attributed. This is not evidence that a smaller production PCM buffer will
recover its nominal size.

Parsed cases reach a genuine empty EOS drain. Frame cases mark only the
actual last ADTS frame EOS and report `drained=0`; no empty EOS drain is
claimed for frame mode. Five-second task watchdog, both idle watchdogs,
assertions, stack canaries and light heap poisoning remain enabled. The
reference worker uses core 1, priority 3 and a 16,384-byte stack. It does
not replace production task scheduling or establish physical audio behavior.

The 12 host test groups reject incomplete PCM, incorrect input/geometry,
wrong EOF, missing/reordered/duplicate cases, invalid buffer/chunk settings,
retained heap and misbound memory observations. The reader retains support
for previous memory records without a sampled minimum.

## Evidence and limits

The original intermediate build with three incorrect `uint32_t` printf
argument types failed compilation and never ran. The subsequent eight-case
frame run and ten-case parsed-buffer run passed. Their original sources,
logs and reports remain local; [provenance](provenance.json) records their
identities and outcomes. The fresh 14-case campaign built without compiler
warnings or errors. Its frozen preparation, actual main TU, linked vendor
paths/archives, compiler, ELF and original UART are bound in the evidence.

[Complete observations](observed.json) · [Original UART](qemu.log) ·
[Frozen preparation](prepared.json) ·
[Reproduction and flag meanings](../../target/cyd_full_app_openeth_qemu/README.md#other-playback-fixtures)

These are same-vendor integration identities. They do not establish
independent numerical AAC conformance, full-application HE-AAC success,
late SBR/PS transitions or physical board behavior. Compact/private AAC
remains deferred.
