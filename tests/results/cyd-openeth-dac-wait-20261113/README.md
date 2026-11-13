# Continuous DAC DMA start and stop under QEMU TLS load

The [previous DAC runs](../cyd-openeth-dac-20261113/README.md) localized the
watchdog to the synchronous SDK write path, waiting for the previous DMA
transfer. The pinned ESP-IDF 6.0.2 source publishes its running flag after
starting DMA. Its completion ISR clears that flag. An interrupt before the
task's store can therefore leave a stopped transfer marked running. The same
write path spins while waiting for that flag and ignores its write timeout
at that point. [ESP-IDF DAC write contract](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-reference/peripherals/dac.html#_CPPv420dac_continuous_write23dac_continuous_handle_tP7uint8_t6size_tP6size_ti).

The build-local overlay changes the two synchronous DMA starts to publish
the running flag first. Its optional bounded wait uses FreeRTOS timeouts and
yields one tick between checks. It returns `ESP_ERR_TIMEOUT` through the
SDK's existing mutex-release path. Five ASan/UBSan cases cover early
completion, zero timeout, finite timeout, recovery after a timeout and the
existing indefinite-wait argument. The old start order fails the early
completion control, even with the bounded wait enabled. LF and CRLF inputs
generate the same overlay and three source drift controls are rejected.

The baseline, start-order control and combined candidate have identical typed
SDK configurations, bootloader, partition table, OTA data and SPIFFS. They
use the C3 TCP window and mailbox, dynamic TLS buffers, the continuous DAC,
and the same verified local TLS Opus station. Xtensa disassembly confirms
that the flag stores precede both synchronous DMA starts. The combined ELF
also contains the FreeRTOS timeout and yield calls.

The start-order-only full-record run accepted at least 24,648 decoded frames
before an HTTP timeout. Its ordinary-record run timed out before Play. These
two trials do not determine whether start ordering alone resolves the DMA
stall observed in the baseline.

The combined diagnostic build completed the full Opus fixture with 528,000
accepted frames and a successful ordered flush under both TLS record modes.
Each successful run delivered the 706,319-byte TLS body and served the exact
13,588-byte WebUI asset during playback and after EOF. No allocation failures,
OpenETH RX waits, driver errors or watchdog events were observed. The first
ordinary run reported a minimum heap of 20,968 bytes. The two full-record
runs reported 5836 and 4800 bytes. Both confirmed 43 full 16-KiB records plus
the tail.

This change is selected by the [diagnostic build](../../target/cyd_full_app_openeth_qemu/README.md).
It leaves the installed SDK intact. The standard continuous DAC build,
legacy DAC EOF and physical timing still need their own verification.
[Artifact and receipt digests](observed.json).
