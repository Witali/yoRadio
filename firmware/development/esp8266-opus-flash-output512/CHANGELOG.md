# Flash-source Opus physical-output diagnostic, 2026-09-10

Source `391a85b`, app 912512 bytes. CPU160/QIO40, GPIO3, standard I2S
PDM32, two512-word DMA buffers, publication512. WordASM/ICDF-word/PDM
IRAM/batch enabled. Diagnostic benchmark only, not a production release.

`board-results.json` retains every case and observation error. All five PCM
fingerprints matched. SILK12 passed one24-second digital continuity run;
the other four cases failed. Worst sampled free DRAM380 bytes and global
minimum208 bytes are unsafe. No claim of general gap-free playback.

[Method, comparison and limitations](../../../../docs/ESP8266_OPUS_FLASH_OUTPUT_BENCHMARK.md).
