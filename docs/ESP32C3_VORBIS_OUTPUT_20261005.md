# ESP32-C3 Vorbis output retry and EOF repair

Date: 2026-10-05. Step 3 of the [repair plan](ESP32C3_VORBIS_REPAIR_PLAN.md).
Pinned Espressif codec 2.6.2 RV32 DSP arithmetic is unchanged.

## What was wrong

An undersized PCM buffer reached synthesis before capacity was checked. A
second undersized retry also released the simple decoder's pending packet.
Both paths changed PCM. Separately, an empty EOS call did not drain the vendor
Ogg parser cache: the ample-buffer streaming reference itself omitted the last
five packets (1088 frames/channel). Accepting that old PCM hash would preserve
the truncation.

The repair checks output capacity from the current/previous block lengths
before synthesis, preserves pending compressed input on repeated retries, and
withholds one real input byte so a subsequent empty HTTP EOF can drain the
parser with nonempty EOS input. No fake packet or PCM padding is inserted.
The application continues EOS calls until the parser produces no more PCM.
Reset clears the retained-byte flag; original close frees its enclosing state.
All private ABI accesses use named fields and compile-time size/offset checks.

Block overlap follows [Vorbis I sections 4.3.1 and 4.3.8](https://xiph.org/vorbis/doc/Vorbis_I_spec.html).
The independently CRC-checked Ogg extractor accounts for packet continuation,
serial/sequence and final granule. A one-byte first audio packet is valid.

## Results

| Check | Result |
| --- | --- |
| Ample output; repeated EOS | PASS, 528000 stereo frames, 2112000 PCM bytes |
| One growth; repeated undersized retries; retry every packet | PASS, exact same PCM, 535 synthesis calls |
| Input split into 53-byte chunks | PASS, exact same PCM |
| Injected PCM resize failure then fresh replay | PASS, defined failure and recovered PCM/heap |
| Independent packet-by-packet original DSP | Exact match, maximum difference 0 LSB |
| FFmpeg 8.1.1 default Vorbis decoder | Same first sample/count, max 2 LSB, RMSE 0.709560 LSB, no samples above 3 LSB |
| 100 decode/close cycles | PASS, full stream heap recovery |
| 199 allocation failures, 4 malformed cases, 4 registration failures, 2 service failures | All 209 handled; clean heap and successful replay |
| Peak requested / allocator-usable bytes | 42121 / 42672 B; +3 / 0 B relative to step 2 |

PCM SHA-256: `e2c316f3e6b7a4a919027ab918cef54fc60a741a944aac26fc215ce33d396910`.
No time shifting, padding or sample deletion was used for comparisons.

[Output evidence](../tests/results/esp32c3-vorbis-output-20261005/README.md)
retains failing original/intermediate runs, raw logs, PCM, images and snapshots.
[Fault sweep](../tests/results/esp32c3-vorbis-output-faults-20261005/summary.json)
retains every allocation failure and replayed ownership ledger. Two headers
omitted from the lifecycle runner inventory are explicitly recorded separately
from the matching final output snapshot; the original report is unchanged.

## Reproduce

Use the QEMU build with `CONFIG_YORADIO_QEMU_VORBIS_LIFECYCLE=y` and
`CONFIG_YORADIO_VORBIS_REPAIR=y`. The exact sdkconfig/images are retained.

```text
python tools/codec_benchmark/run_vorbis_output.py --build <build> --fixture tests/fixtures/esp32c3_calibration/vorbis-q10.ogg --qemu <qemu-system-riscv32> --bios <qemu-share> --raw-reference --output <raw-run>
python tools/codec_benchmark/run_vorbis_output.py --build <build> --fixture tests/fixtures/esp32c3_calibration/vorbis-q10.ogg --qemu <qemu-system-riscv32> --bios <qemu-share> --reference <raw-run> --output <matrix-run>
python tests/test-vorbis-output.py
python tests/test-vorbis-repair-evidence.py
```

The fault runner accepts `--pcm-reference <raw-run>` so the intentional EOF
correction is checked against complete independent packet output. It retains
`original_pcm_match=false`; the previous truncated reference is not rewritten.

This is one fixture and its failure paths, not the entire Vorbis format corpus.
Arbitrary final granule trimming, chained logical streams, all large-block
modes, reset/replay without close, and physical sample-level tail capture still
need dedicated coverage. Hardware load/OTA results for images containing this
repair are in [the DMA experiment report](ESP32C3_OUTPUT_DMA_20261005.md).
