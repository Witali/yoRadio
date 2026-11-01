# Unchanged CYD production boot replay: partial checkpoint

The saved ON/OFF static-TLS-RX PDM production images from source
`3a563324abdca56144a40d5759def0ccfe708b3c` now pass the old QIO initialization
barrier in the selected IDF6-compatible dual-core ESP32 QEMU. **Complete radio
startup still does not pass.** These are actual saved native runs, preserved on
1 November 2026; this checkpoint runs no new firmware build or emulator campaign.

| Observation | Result |
| --- | --- |
| Ordinary receive profile, ON and OFF | Original firmware reaches `app_main`, including the project log after early MPI preparation, then fails SPIFFS mount with `-10025`. Original terminal reports remain NONPASS. |
| Complete stopped-CPU SPI readback | All 589824 original SPIFFS bytes match over 9216 QIO reads; 16 scalar/batched comparisons agree. Guest CPUs never execute production firmware in this diagnostic. This is a read-path observation, not a successful mount or radio boot. |
| Explicit GPIO-matrix receive profile, ON and OFF | With the emulator's `input-delay-ns=25` property, both unchanged images pass SPIFFS mount and reach ST7789 driver entry, then panic during Wi-Fi PHY initialization. Original terminal reports remain NONPASS. |
| Exact ELF symbolication | Both genuine `LoadStorePIFAddrError` exceptions, address `0x60033c00`, resolve through `register_chipv7_phy`, `esp_phy_load_cal_and_init`, and Wi-Fi startup. No instruction-pointer change, patched firmware, forced ACK, or fabricated ready marker is used. |

The 25 ns profile has a pinned classic ESP32 SDK GPIO-matrix basis; it is an
explicit emulator receive-path setting, not a physical-board calibration or
a universal choice for other boards. The ordinary runner remains unchanged at
[its canonical entry](../../run-cyd-production-boot-replay.py). The exact
historical GPIO-profile controller is retained under `evidence/` as source
provenance; archived programs are not run by the data verifier.

The selected QEMU executable has SHA-256
`4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d`.
Every original firmware component, configuration, partition, flash header and
filesystem remains unchanged. ON/OFF merged-flash SHA-256 values are respectively
`4eb701f7c78a1a7aa88c1f2cd72c355f626c9cb9db0d503012fc177a03125e2a` and
`e67e909b725118f4fae76b94545e11ab01e862140fc89f0a4637dd332ad50353`.
The original volume was already present in both images: its 144 magic words and
256-byte-page geometry match the SDK. No format operation or replacement empty
filesystem was used. Flash snapshots and all 48 ordinary / 51 GPIO-profile input
bindings remained unchanged after each observed run.

The full readback is SHA-256
`e92e0bab990144ad683306fc59b60cb510656f96dff6f13952332cc7ca8ed027`.
The earlier scalar readback campaign remains explicitly incomplete: all 1154
completed comparisons matched, but only 2447 of 9216 complete-volume chunks ran
before the host deadline. Its failed report is retained separately. Trace
campaigns and the non-mutating guest SPI observer also retain their original
reports, including the trace-log-limit nonpass; none is relabelled as a boot pass.

The GPIO-profile QEMU processes exit with status **0 after a guest panic**. The
controller correctly marks their startup gate failed. A zero emulator status
alone is insufficient evidence of successful firmware startup. Stopped-CPU
readback exits with status 1 because its owned process is deliberately terminated
after the observation; its report independently requires completed reads,
actual stdout EOF, a joined reader and no controller errors.

`manifest.json` pins exact original bytes of 46 text evidence files and records
the hashes/sizes of 50 local-only payloads. Original reports, selected controller
sources, ordinary/GPIO console logs, filesystem audit and symbolication summary
are published unchanged. Firmware, ELF, flash, filesystem, ROM, raw QTest/NOR
streams, contact-bearing source and raw symbolication output stay local; their
payloads are not copied or encoded here. The data-only verifier checks published
bytes and recorded omission bindings. It cannot independently re-read omitted
binary data and does not claim complete emulator source/dependency closure.

```text
python -B tests/results/cyd-production-boot-replay-20261101/verify.py
```

No physical board, serial port, host audio or external network was used. Static
TLS RX loans, actual TLS traffic, complete radio/UI startup, audio throughput,
production resource margins and physical acceptance remain unqualified. This
checkpoint preserves a reproducible next emulator boundary; it does not enable
the default-off memory optimizations or close transfer stages 13/15.
