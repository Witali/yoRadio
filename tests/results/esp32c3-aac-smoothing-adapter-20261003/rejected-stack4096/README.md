# Rejected integration run: undersized emulator task stack

This run used the four-row SBR smoothing adapter with the old QEMU task
selection. `YORADIO_QEMU_AAC_TEST` by itself selected only 4096 stack bytes;
the profiling and numerical-experiment options selected the production
decoder stack plus 4096 bytes for the test harness. The real radio decoder
already has a 16384-byte stack.

The original log ends in an OLED I2C driver load-access fault. A GDB hardware
watchpoint on the first word of the OLED device object establishes the cause:

- Task stack starts at `0x3fc92cc8`; the OLED object is at `0x3fc92c80`.
- In `calc_sbr_envelope`, SP is `0x3fc92b40`, below the task stack boundary.
- The store at `0x42021002` writes `320(sp)`, exactly `0x3fc92c80`, replacing
  the OLED bus pointer with zero. The watchpoint stops at the next instruction.
- The call chain includes the new `complex_envelope` temporary-row wrapper.

The fault therefore demonstrates stack overflow in this test task. It does
not establish an incorrect SBR owner offset or an OLED-driver defect. The
failed run provides no PCM, concurrency, or production qualification.

`app_main.c`, `sdkconfig`, `qemu.log`, and `gdb.log` preserve the failed input
and observation. Addresses apply only to the ELF hash in `manifest.json`.
The fix selects the decoder-sized stack for every `YORADIO_QEMU_AAC_TEST`
configuration. The separate 8192-byte concurrent decoder tasks still measure
their own remaining stack and must pass without being enlarged.
