# Complete public AAC references for TLS regression

The separate ESP32 SDK 6.0.2 diagnostic decodes each entire input through
the unchanged public Espressif simple-decoder API, on core 1 at priority 3.
It uses no production parser, pending owner, radio pipeline, private codec
ABI, reset hook or codec linker wrapper. Both original archives and the
actual linked vendor component paths are verified. The main C translation
unit, frozen fixtures, compiler, ELF and original UART are bound by hashes.

| Source | AAC-Plus | Encoded bytes | PCM rate | Complete PCM frames | PCM bytes | Complete PCM SHA-256 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| LC | 1 | 443,706 | 48,000 | 529,408 | 2,117,632 | `95c66ea66a1af8cfdd70a38441f83a2599b7e690ccdd336bb462b8c41ef45ff0` |
| LC | 0 | 443,706 | 48,000 | 529,408 | 2,117,632 | `95c66ea66a1af8cfdd70a38441f83a2599b7e690ccdd336bb462b8c41ef45ff0` |
| HE | 1 | 102,420 | 48,000 | 614,400 | 2,457,600 | `44d9a67ecc2e6a6d382951442fb7bdf687510c784e2e9137036cbe0a38b6f362` |
| HE | 0 | 102,420 | 24,000 | 307,200 | 1,228,800 | `025a8f45c5efeeb8e9424e9088c27c3a74cce92f61d8f9f66ab8d6d25530cf7d` |

All four handles close and all four inputs reach genuine public EOS drain.
Original encoded bytes remain unchanged. Repeated cases restore heap;
both idle watchdogs, the five-second task watchdog, assertions, canaries
and light heap poisoning are enabled. The first call can retain the public
hash subsystem's one-time initialization allocation.

LC is the complete calibration input: 517 ADTS frames. HE contains 20
consecutive copies of the original synthetic 48 kHz FDK segment: 300 ADTS
frames, with a 24 kHz core and full 48 kHz SBR output. The HE identity is
measured across one continuous public handle and the entire repeated
encoding, rather than by concatenating independently decoded PCM hashes.
The AAC-Plus-off control preserves LC and emits HE's core-rate output.

The public configuration agrees with the creator's
[simple-decoder example](https://github.com/espressif/esp-adf-libs/blob/master/esp_audio_codec/test_apps/audio_codec_test/main/simple_decoder_test.c)
and the pinned local AAC header. All full-rate hashes are now checked by
the [full-application TLS runner](../../run-cyd-full-app-openeth.py).
These are same-vendor integration identities, not independent AAC numerical
or standards conformance, production resource margins or physical audio tests.

The reference and EOF observer tests reject partial PCM, incorrect geometry,
wrong input binding, reordered/missing cases, duplicate checksums, changed
hashes, incomplete final tails, missing drain and retained repeated heap.
The complete application AAC-LC control also matches this full PCM identity
and serves WebUI after EOF. HE-AAC under simultaneous TLS/TFT/WebUI still
requires its separate resource qualification; a direct-reference pass does
not close that requirement. Compact/private AAC remains deferred.

[Measurements and input identities](observed.json) · [Original UART](qemu.log) ·
[Reproduction](../../target/cyd_full_app_openeth_qemu/README.md#other-playback-fixtures)
