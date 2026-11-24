# ESP32 I2S DMA START command regression

This test drives the real QEMU ESP32 MMIO model through QTest. It checks hardware self-clearing of OUTLINK_START and repeated ESP-IDF address-then-START read-modify-write sequences. The bundled unchanged `legacy_start_order_test.py` also retains all six earlier link/TX ordering and cancellation checks. No `.build` helper is required.

From the repository root, use an existing QEMU executable and ROM directory, with a fresh ignored output directory:

```powershell
python tests/target/cyd_full_app_openeth_qemu/i2s_dma/qtest_start.py --qemu PATH/TO/qemu-system-xtensa.exe --bios C:/Work/QEMU-ESP32/pc-bios --output .build/i2s-dma-start-check
```

The default helper is next to the script; `--legacy` can override it. The qtest accelerator executes no guest instructions. The VM remains running so virtual timers can be serviced; do not add `-S`. The four new cases check START readback with TX enabled/disabled and repeated SDK-style address-only/explicit-START writes with owner checking disabled/enabled. The owner-disabled case matches the production driver's setting. The owner-enabled case is a negative control that makes a second consumption fail with OUT_DSCR_ERR. Every MMIO/clock operation and assertion is preserved in the output.

The exact selected baseline (`eb88d36f5bea48f547615ee147cf01985f9adf301112e2954ad90b8ca461ed02`) passes the old six but fails all four new cases; exit code 1 is expected for that negative control. A START-only fixed private executable (`28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4`) passes all ten. These are register-semantics results, not a full-app timeout diagnosis, audio-quality assessment, or timing qualification.

## Hardware and SDK basis

[Espressif ESP32 TRM v5.9, section 2.6, printed page 60](https://documentation.espressif.com/ESP32_Technical_Reference_Manual_en.pdf#page=60) specifies that I2S OUTLINK_START and INLINK_START clear themselves in hardware. The pinned ESP-IDF 6.0.2 `components/esp_hal_i2s/esp32/include/hal/i2s_ll.h:553-588` sets the OUT_LINK address and START in two separate bitfield writes. Retaining START in the model makes a later address-only write issue an unintended new start.

`start-self-clear.patch` changes only the stored register value, clearing START alongside the existing PARK mask. Its command handler still uses the original write value. It changes no timer deadlines, EOF/TEOF handling, ownership handling, driver code, or production firmware.

## Retained source and provenance

`retained_model.c` is the exact 11,912-byte retained baseline, SHA256 `a05e52b1cfa0f4c5a1d74bed70efb8761d8a54cf18a120b10c45f1887cd3c286`. It originates from `hw/audio/esp32_i2s_dac.c` in [Witali/QEMU-ESP32](https://github.com/Witali/QEMU-ESP32), with the already-existing private 2026-11-13 link-before-TX gate overlay. This retained overlay is not claimed to be an unmodified tracked QEMU revision. Its original source header is preserved verbatim; the QEMU project's `COPYING` is included. The copied six-case helper preserves its original SPDX notice.

Apply the patch to this retained source in a fresh ignored scratch directory to reproduce the fixed model. The fixed source SHA256 is `b8ca03a6534fb4880fcdf87374ef7273fcb60c6b192261d1c13e1b27419e432d`; retained object SHA256 is `30be297358d6fef894223208a70d3e7d5ee0a35c99d3d4c5521b60fa28f9eb86`.

The private build used the matching entry from the existing QEMU build's compile database and replaced exactly the retained model object in the selected relay's flat link response. The unchanged recompile reproduced the retained object byte-for-byte. Relinking with the original executable basename reproduced the selected image after explicitly normalizing COFF timestamp, export-directory timestamp, and PE checksum. All section bytes outside the export timestamp matched. A differently named relink is also retained as a provenance negative control.

The compact [evidence package](../../../results/cyd-i2s-dma-start-20261124/README.md) contains source/input hashes, actual dependency hashes, compiler/link argv, PE comparisons, baseline failures, and fixed passes. QEMU executables, libraries, toolchain binaries, build caches, firmware, and TLS fixtures are deliberately absent; the recorded hashes identify the external inputs required to recreate the private relays. These tests do not prove that the START mismatch caused an intermittent native continuous-DAC timeout.
