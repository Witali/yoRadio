# CYD legacy DAC startup under TLS load

The baseline UART identifies the failed allocation in
`i2s_alloc_dma_buffer` during the first `i2s_driver_install`. The SDK asks
for eight separate 2,048-byte payload buffers in internal DMA-capable
memory while the stream and decoder are active. It allocates the DMA
descriptors separately. The health counter recorded a failed 2,048-byte
request with those capabilities, followed by `ESP_ERR_NO_MEM` and no PCM
writes. The SDK frees the partial allocation before returning the error.
[ESP-IDF 5.5.4 legacy driver](https://github.com/espressif/esp-idf/blob/v5.5.4/components/driver/deprecated/i2s_legacy.c#L577).

The native legacy backend uses four 512-frame descriptors and one
2,048-byte conversion buffer. This saves 12 KiB of payload and conversion
storage. It still generates x16 two-slot DAC data with the same fractional
error diffusion and DMA interrupt interval. Four buffers cover 2.67 ms at
the maximum output rate of 768 kHz. The output task waits two milliseconds
for PCM before submitting two milliseconds of midpoint samples for legacy
DAC. Its core and priority follow the existing dual-core task configuration.
[I2S DMA sizing and timing](https://docs.espressif.com/projects/esp-idf/en/v6.0.2/esp32/api-reference/peripherals/i2s.html).

All three [QEMU runs](observed.json) used the same typed SDK configuration,
bootloader, partitions, SPIFFS, and QEMU executable. The [OpenETH fixture](../../target/cyd_full_app_openeth_qemu/README.md)
uses dynamic TLS buffers, a TCP window of 8,640 bytes and an eight-entry
receive mailbox, plus the 96 kHz ceiling of the emulated DAC. The guest
requests 768 kHz for the 48 kHz Opus source.

| Variant | Result |
| --- | --- |
| Eight descriptors, 6 KiB conversion buffer | The 2,048-byte allocation failed before the first PCM write. |
| Four descriptors, 2 KiB conversion buffer | All 43 full TLS records and the tail arrived. The driver flushed 528,000 PCM frames with zero allocation or output failures. The WebUI request after EOF timed out. |
| Four descriptors and two-millisecond idle refill | The entire scenario passed. The driver flushed 528,000 PCM frames. The exact 13,588-byte WebUI asset was served during playback and after EOF. The guest recorded zero allocation failures, output errors, OpenETH allocation waits, or watchdog events. Minimum free heap was 2,056 bytes. |

Host ASan/UBSan checks passed for output pause, PCM gain, normalization,
header gain, and output telemetry. The legacy checks cover the DMA payload
budget, re-priming on rate change, and the two-millisecond idle writes.
The maintenance runner passed 83 lifecycle cases and rejected nine
intentional regressions after its PCM and decoder dependencies were updated.
The emulator result covers accepted PCM and network activity. Physical DAC
timing and Wi-Fi remain open.
