# AAC reset: confirmed vendor offset defect and source repair

The complete decompilation revealed that `PVMP4AudioDecoderResetBuffer` still
uses an offset from the older monolithic core. In the pinned ESP32-C3 library,
the core is **35460 bytes**, but an active-SBR reset writes a PS pointer at
**core + 87004 (`0x153dc`)**. The PS branch reads the same stale location.

The QEMU reproduction confirms **six out-of-bounds writes**, safely contained
inside explicit test padding, across two resets each of HE44, HE48 and HEv2.
An unchanged binary supplies the reference; this is not just a decompiler guess.
LC reset does not enter the defective branch. The ordinary radio adapter uses
close/reopen and does not call this reset function today.

## Repair and validation

A source implementation uses the separately allocated SBR owner's PS pointer
and reproduces the remaining native reset operations. It also supports the
[smaller SBR allocation](ESP32C3_AAC_SBR_LAYOUT_20261001.md). Reopening channel
workspaces after reset must preserve the relocated PS control just as the
original keeps its tail control. A small source replacement of `sbr_open` does
this with disjoint zero ranges, without a 3536-byte temporary copy.

Six LC/HE/v2 inputs, three decode cycles each, two resets per instance:
**24 reset calls, 887808 scalar PCM samples, identical bytes and output formats**.
Consumed input, output size, rate and channels match on every call. Core/SBR
guards and cleanup pass. This fixes the measured path in a test build; it does
not qualify every malformed stream or enable production use of the private ABI.

The padded reference and candidate cannot coexist within the emulated C3 heap:
the initial simultaneous trial hit AAC's existing memory fallback and is retained
as a **failed test**, not successful HE decoding. The final test runs instances
sequentially, records original call metadata and PCM in the disposable QEMU app1
partition, then reads and compares every candidate byte. Only the emulator image
is written. No board, NVS or user firmware is touched. This diagnostic is not a
memory-saving or CPU benchmark; its reference padding deliberately costs RAM.

## Reproduce

Build with the same defaults as the SBR layout test, plus
`sdkconfig.qemu-aac-reset.defaults`, using build/config directory
`build-qemu-aac-reset`. Then:

```powershell
python tools/codec_benchmark/run_aac_reset.py `
  --dependency-root C:/Work/yoRadio/.idf `
  --qemu .build/qemu-cache-host/qemu-system-riscv32 `
  --bios /mnt/c/Work/QEMU-ESP32/share/qemu --wsl `
  --output .build/aac-reset
python tests/test-aac-reset.py
```

The runner checks `CONFIG_YORADIO_QEMU_AAC_RESET_TEST`; the test is disabled by
default and cannot be selected without QEMU and the pinned layout experiment.
Do not flash this diagnostic to hardware: it writes its disposable app1 region.
Raw successful/rejected logs, configuration and hashes are retained in
[`tests/results/esp32c3-aac-reset-20261001`](../tests/results/esp32c3-aac-reset-20261001/).
