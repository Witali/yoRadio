# ESP32-C3 QEMU Flash models, capacities and read modes

## Result

QEMU branch `codex/esp32c3-qio`, commit `b918b5889d`, adds selectable
GigaDevice GD25Q / Winbond W25Q families and 2/4/8/16 MiB capacities.
It fixes the GigaDevice Quad Enable path that prevented the QIO application
from starting. The previously failing image now decodes the MP3 fixture on
both families, with every PCM byte equal to the previous successful DIO run.

The physical board was not changed. These are emulator functionality tests;
they do not establish hardware timing or replace calibrated CPU benchmarks.

## Selection

```sh
qemu-system-riscv32 -M esp32c3,flash-model=w25q,flash-size=8M \
  -L /path/to/qemu/share/qemu -nographic \
  -drive file=flash-8m.bin,if=mtd,format=raw
```

| Capacity | GigaDevice (`flash-model=gd25q`) | Winbond (`flash-model=w25q`) |
|---|---|---|
| 2 MiB | GD25Q16, `C8 40 15` | W25Q16, `EF 40 15` |
| 4 MiB | GD25Q32, `C8 40 16` | W25Q32, `EF 40 16` |
| 8 MiB | GD25Q64, `C8 40 17` | W25Q64, `EF 40 17` |
| 16 MiB | GD25Q128, `C8 40 18` | W25Q128, `EF 40 18` |

Default `flash-model=auto` preserves the previous capacity-dependent choice:
W25X16 / GD25Q32 / GD25Q64 / IS25LP128. Default `flash-size=auto` infers
capacity from the image. Explicit capacity must match the image exactly.
Invalid configurations fail at startup; images are never silently resized.
The suffix in chip names is in **megabits**, the selector is in **MiB**.
Select these properties before starting the emulator, not while it runs.

Pad a copy of a smaller image with `FF` to increase capacity, and adjust the
firmware Flash-size configuration and partition table to use the extra space.
Changing the emulator capacity alone does not enlarge partitions. The detailed
instructions are in QEMU's `docs/system/esp32c3-flash.rst` (also in the patch below).

## Changes checked against documentation

- SR2 bit 1 (S9) supplies QE for these families; reads via `35`, writes via
  `31` or two-byte `01`, with WREN and WEL clearing.
- Quad reads/programming require QE in the C3 attachment.
- Slow/Fast/DOUT/DIO/QOUT/QIO read commands: `03/0B/3B/BB/6B/EB`.
- SPI1 dummy register counts are encoded as N-1. Fast/output reads use one
  single-wire dummy byte; DIO one mode byte; QIO one mode byte plus four
  quad-wire clocks, totaling three wire bytes.
- The special read command honors the mode flags; special status writes
  honor the two-byte flag. Transfer bounds and an index-versus-byte-value
  mistake in asymmetric transmit/receive were also corrected.
- A per-device `byte-dummy-cycles` property avoids changing other boards'
  existing dummy-token convention.

Manufacturer references:
[GD25Q16C Rev3.2](https://download.gigadevice.com/Datasheet/DS-00086-GD25Q16C-Rev3.2.pdf),
[GD25Q32C Rev4.1](https://download.gigadevice.com/Datasheet/DS-00088-GD25Q32C-Rev4.1.pdf),
[GD25Q128E Rev1.4](https://download.gigadevice.com/Datasheet/DS-00480-GD25Q128E-Rev1.4.pdf),
[W25Q128JV RevF](https://www.winbond.com/resource-files/w25q128jv%20revf%2003272018%20plus.pdf).

[ESP-IDF 6.1 for ESP32-C3](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/api-reference/peripherals/spi_flash/index.html#support-for-features-of-flash-chips)
lists ISSI, GD, MXIC, FM, Winbond, XMC and BOYA for QIO/QOUT, and supports
slow/fast/DIO/DOUT on most 24-bit-address parts. This is a family support list,
not certification of every optional feature or ordering suffix.

## Validation

| Test | Result |
|---|---|
| Two explicit families × four capacities | 8/8 passed, 53 checks each |
| Legacy defaults at four capacities | 4/4 passed, 13 checks each |
| Invalid family/size, image mismatch, missing drive | 5/5 correctly rejected |
| Total register/configuration assertions | **481 passed** |
| Preserved QIO application, GD25Q32 | **294,912 PCM bytes, exact DIO match** |
| Preserved QIO application, W25Q32 | **294,912 PCM bytes, exact DIO match** |
| Full existing DIO PCM regression, rebuilt QEMU | **8/8 passed** |

The register matrix exercises six read modes using both user transactions
and special commands. Distinct data at address 0, 0x12340 and the last 64
bytes detects address aliasing; tests also cover capacity wrap, program,
sector erase, adjacent data, QE/WEL and unequal duplex lengths.

The PCM matrix covers MP3, AAC-LC, HE-AAC and HE-AACv2 independently, then
MP3 → HE-AAC → MP3 and AAC-LC → MP3 → HE-AACv2, with/without intervening
ID3 tags. Mixed output is byte-exact against independently decoded segments.
This is decoded PCM before resampling, volume and physical DMA output.

The preserved QIO fixture uses a DIO boot image header; its ESP-IDF application
explicitly configures QIO and logs `spi_flash: flash io: qio`. Therefore it
proves the repaired application QIO path, not every ROM boot-header variant.
Other boot-header variants are not certified by this report.

Scope excludes electrical timing, full SFDP/OTP, status persistence across
emulator runs, continuous-read/QPI, DDR/Octal and vendor optional features.
The selector is a functional family model, not an exact model of every
revision, factory QE preset or voltage suffix.

## Reproduction and evidence

[Archived results and hashes](../tests/results/esp32c3-qemu-flash-20261013/sha256.json)
include register results, complete compressed logs, PCM files, the synthetic
QIO fixture image, build logs, test controllers and
[the QEMU patch](../tests/results/esp32c3-qemu-flash-20261013/qemu.patch).
The old QE failure is recorded as a baseline observation; its initial probe
predates the added asymmetric-duplex and QE-disabled read assertions.

Run the register test from the patched QEMU repository:

```sh
python3 tests/esp32c3_flash_test.py --qemu /path/to/qemu-system-riscv32 \
  --bios /path/to/qemu/share/qemu --output flash-results.json
```

For the preserved QIO application, decompress `qio/fixture-flash.bin.gz`
from the archive into a temporary file. Then, from YoRadio under Linux/WSL:

```sh
python3 tools/codec_benchmark/check_flash_boot_pcm.py \
  --qemu /path/to/qemu-system-riscv32 --bios /path/to/qemu/share/qemu \
  --flash /tmp/fixture-flash.bin \
  --reference-log tests/results/esp32c3-qemu-flash-20261013/dio/mp3-320.log.gz \
  --output /tmp/qio-pcm-new
```

Use `tools/codec_benchmark/run_pipeline_pcm.py` and the existing test-only
PCM capture build to repeat the eight-case matrix. See the archived report
for exact commands and source/configuration hashes.
