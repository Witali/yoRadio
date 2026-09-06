# Exact AAC speed experiments — 2026-09-06

Wemos D1 mini / ESP8266, COM8, CPU160, QIO40, GCC8.4 O3. One retained
48-kHz/320-kbit/s AAC-LC frame in RAM; 8 warmups + 200 measured frames.
MP3 is an unchanged image-layout control. No Wi-Fi or normalization.

| Decoder variant | AAC avg / max, us | MP3 avg, us | Free task stack | Decision |
| --- | ---: | ---: | ---: | --- |
| Original bounded output | 18945 / 18970 | 4632 | 1712 B | Reference |
| Specialized window blocks | 17951 / 17960 | 4754 | 1792 B | Keep |
| Windows + 8-bit Huffman prefix | 16015 / 16033 | 4756 | 1792 B | Reject table size: output underruns |
| Above + cache top-up | 15870 / 15892 | 6148 | 1712 B | Reject |
| Above + sufficient-cache shortcut | 15867 / 15891 | 5429 | 1712 B | Reject |
| **Windows + 6-bit Huffman prefix** | **15140 / 15161** | **4756** | **1792 B** | **Final** |

Every case uses AAC codec DRAM 6804 B / IRAM 16384 B, heap 88640 B;
50 create/switch cycles return heap with delta=0. The final table uses
3072 bytes of flash only. Original and final `.dram0`/`.iram0` sizes match.

Physical output: original AAC wall 4254014 us, final 4253941 us for
4266666 us queued audio. Both report zero underruns, partial handoffs and
FIFO-empty flags, including repeated alternating images. The 8-bit table
instead produced 114 neutral underruns / 4405387 us wall. Wall time with DMA
backpressure is NOT CPU usage; the queue crosses measurement boundaries.

Final verification: 344 host tests passed; 1305600 exhaustive Huffman inputs,
3874304 independent bit-reader comparisons, all window sequences/shapes,
block sizes, cancellation, mono/stereo and PCM/PDM ownership tests.
All 154624 retained AAC PCM samples match the exact canonical/64-bit reference:
max error=0, SNR=Infinity dB. This measures **additional digital error**, not
the analog RC-filter/amplifier noise floor or AAC encoding loss.

`measurements.json` records image hashes/sizes/ELF sections and filtered UART
metrics. `*-ab-*` logs identify alternating image0/reference and image1/candidate.
`final-tests.log` is the complete final host test run. Earlier experiment logs
are retained and must not be mistaken for final acceptance.

Scripts: `run_aac_block_matrix.ps1`, `run_saved_images.ps1`,
`generate_aac_prefix.js --check`, `archive_aac_speed.js` in
`tools/esp8266_audio_profile/`. The ordinary image is under
`firmware/development/esp8266-native-aac-speed/`.

These short isolated tests do not validate sustained Wi-Fi streaming. The
diagnostic binaries have different flash layouts from ordinary radio; the
speed percentage is not a direct measurement of the complete network player.
