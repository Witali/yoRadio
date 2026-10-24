# Classic ESP32 / IDF6 emulator model source preparation

This package is unexecuted source preparation for root review. The original QEMU
checkout, SDK, firmware, images, configuration, prior capture results and external
worktrees have not been edited. No compiler, QEMU guest, test, Python import,
binary disassembler or Git operation was run by this preparer.

The baseline is the root-verified clean QEMU HEAD
`2a593f8d00c9be312ddc6e600dbb778f0e6459eb` at `C:/Work/QEMU-ESP32`.
`source-pins.json` records raw original file hashes. `originals/` contains exact
copies of the five affected original files. `overlay/` contains proposed versions
of those five files and one new regression driver. `compat.patch` is a unified
diff using normal QEMU-relative paths, independently reconstructed in memory
against the copied text. Applying or building it has not been attempted.

## Why the changes are needed

The frozen observation02 analysis is at
`../cyd-qemu-production-analysis-20261024-02/` (readiness SHA-256
`42da263762cf0aca97ee43c00fcfe777b30d901eeaa7b2095b9e1b047c15d08b`).
The root-owned diagnostic observed startup through `app_main` and display entry,
but no audio pipeline, radio-control or Web startup. SPIFFS returned `-10025`
and the asynchronous Wi-Fi task later asserted on missing PHY clock bits.
`OBSERVATION_COMPLETED` remains a controller result, not a startup qualification.

Actual partition placement and the full SPIFFS region match the original image.
All 144 stored SPIFFS magic words match the exact SDK generator geometry. These
checks establish placement and those magic values, not full filesystem integrity.
The three short `EB` reads of magic/erase-count addresses never reached the NOR
read state before CS rose: the current classic controller omits its dummy phase,
while the NOR model expected the legacy clock-token representation. The newly
rebuilt baseline already fixes GD status-register command decoding; that result
and both old captures are preserved.

## Proposed model changes

1. `hw/ssi/esp32_spi.c` forwards enabled dummy phases before data, without copying
   their received bytes into the caller's FIFO or DMA data. QIO uses four lanes,
   DIO two, and fast/DOUT/QOUT one for this phase. Builtin READ selects the matching
   opcode from the existing CTRL read-mode flags; USR still uses its configured
   opcode. `include/hw/ssi/esp32_spi.h` adds only those documented CTRL fields.
2. Classic ESP32's machine enables the existing public NOR property
   `byte-dummy-cycles`, as the C3 machine already does. The shared NOR source and
   its legacy representation for other controllers are not changed.
3. DPORT stores and returns `WIFI_CLK_EN` at `0x3ff000cc`, including normal full
   32-bit writes and reset value `0xfffce030`. The SDK's actual RMW writes can then
   be observed by its own mask check. No clock bits are fabricated when read.
   This implements register state, not RF, calibration, or working network access.

The address/dummy boundary matters. Exact SDK6 source
`components/esp_hal_mspi/spi_flash_hal_common.inc:119-132` uses 28 address bits plus
five quad dummy clocks for classic ESP32 QIO. `:239-242` supplies the real 24-bit
address left-aligned with trailing ones. The byte-oriented SSI interface already
emits a complete final address byte, containing part of that dummy phase.
Therefore the additional bytes are
`ceil((address_bits + dummy_clocks * lanes) / 8) - ceil(address_bits / 8)`.
Rounding both phases independently would add an extra byte and shift every read.

| Mode / SDK configuration | Address bits | Dummy clocks | Lanes | Additional dummy bytes |
| --- | ---: | ---: | ---: | ---: |
| slow READ | 24 | disabled | 1 | 0 |
| fast / DOUT / QOUT | 24 | 8 | 1 | 1 |
| DIO | 24 | 4 | 2 | 1 |
| QIO | 24 | 6 | 4 | 3 |
| classic SDK DIO | 28 | 2 | 2 | 0 |
| classic SDK QIO | 28 | 5 | 4 | 2 |

This preserves the existing byte-oriented abstraction. It does not claim arbitrary
bit-stream or analog sampling-delay accuracy. Actual configured production clock
counts and subsequent boot behavior still require the root-owned diagnostic.

## Primary evidence

- [Espressif ESP32 TRM](https://documentation.espressif.com/esp32_technical_reference_manual_en.pdf),
  version 5.7 returned by the documentation service: SPI_USER and SPI_USER1 register
  descriptions independently enable address/dummy phases and specify clock-count
  encoding. The older vendor URL returned version 5.2. No claim relies on the
  website's newer version listing. The retrieved TRM text did not expose the
  WIFI_CLK_EN register; its exact address/reset/RW evidence is the SDK header below.
- [GigaDevice GD25Q32C Rev4.1 datasheet](https://download.gigadevice.com/Datasheet/DS-00088-GD25Q32C-Rev4.1.pdf),
  section 7.11 and figure 13: the EB read uses an address, mode bits and quad dummy
  clocks before response data. The primary search extraction was available; a
  later direct fetch timed out.
- Exact local SDK6.0.2 `components/esp_hal_mspi/spi_flash_hal_common.inc:117-132`
  and `:239-242`, and `esp32/include/hal/spi_flash_ll.h:247-275,364-398`, supply the
  actual classic address/mode/dummy setup. [Upstream tag reference](https://github.com/espressif/esp-idf/blob/v6.0.2/components/esp_hal_mspi/spi_flash_hal_common.inc).
- Exact local SDK6.0.2
  `components/soc/esp32/register/soc/dport_reg.h:1031-1050` defines the full 32-bit
  R/W register, offset, reset value, common/Wi-Fi/BT masks. The companion
  `components/esp_hal_clock/esp32/include/hal/clk_gate_ll.h` performs real register
  RMW operations. [Upstream tag reference](https://github.com/espressif/esp-idf/blob/v6.0.2/components/soc/esp32/register/soc/dport_reg.h).
  The web cache could not fetch these tag pages; evidence is the pinned local
  primary SDK distribution, not an inferred remote match.
- Pinned QEMU `hw/block/m25p80.c:1008-1143,1216-1226,1790` contains the existing
  byte-dummy-cycles contract. `hw/ssi/esp32c3_spi.c:188-219` and
  `hw/riscv/esp32c3.c:265` are implementation references. Classic ESP32 requires
  the additional partial-address handling above; its code is not copied blindly.

## Proposed regression execution, not yet performed

`overlay/tools/test_esp32_idf6_compat.py` uses actual QTest MMIO with both CPUs
stopped (`-accel qtest -S`) and a fresh synthetic 4 MiB NOR image. It uses stdio
pipes, disables NIC/audio/display/serial, and opens no listener. This synthetic
image is a peripheral fixture, not a substitute production boot image or a newly
formatted user filesystem. `-snapshot` and before/after hashes cover its backing
file, selected executable, two ROMs, model sources, and the driver itself.

The 187 proposed recorded assertions cover full DPORT write/read/reset/RMW/clear
semantics, GD QE status write/read and QE-off output, all six read modes via USR
and builtin READ, exact bytes at three distinct addresses, lengths 2/3/16/64,
the SDK 28/5 and 28/2 combinations, disabled stale dummy counts, and omitted-dummy
negative controls. Distinct backing data and the two SPIFFS magic-sized sentinels
expose leading zero bytes, skipped data, wrong addresses and mode/lane errors.
Assertions are explicit comparisons and remain active under Python optimization.
Failures are collected across the cases, so the untouched baseline can show both
independent model defects. Protocol/controller failures abort the fixture.

The future invocation needs the newly built executable's actual digest and the
source worktree used to build it. Example only, with intentionally unresolved
placeholders:

```text
python tools/test_esp32_idf6_compat.py --qemu <new-exe> --qemu-sha256 <actual-sha256> --source-root <new-QEMU-worktree> --rom-dir C:/Work/QEMU-ESP32/pc-bios --out <existing-parent>/.build/cyd-idf6-qtest-01
```

The driver bounds the fixture to 60 seconds and each output log to 32 MiB. It
terminates and reaps only its own paused child process, requires actual pipe EOF
and reader join, and records termination/exit details. This intentional teardown
does not claim guest SHUTDOWN behavior or natural boot exit. The possible success
label `MMIO_REGRESSIONS_COMPLETED` has no production boot or hardware meaning.
`MMIO_REGRESSIONS_FAILED` means comparisons ran with a complete controller and
failed; `INCOMPLETE` means the controller or preservation checks did not complete.

Root should first source-review and apply-check the patch on a fresh branch at
the pinned baseline, build there, then run this new paused fixture. An untouched
baseline negative run and existing classic SPI2/SPI3 peripheral regressions provide
useful controls. None has been executed here. Only after meaningful regression
results should root consider a separate bounded production observation with the
original QIO80 / 240 MHz / two-core firmware and its original complete flash image.
No DIO downgrade, firmware modification, assert removal, arbitrary formatting,
unrelated branch merge or codec change is proposed.
