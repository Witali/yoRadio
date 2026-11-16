# Six-channel Opus with PDM, TFT and WebUI

The matched CYD builds ran on dual-core classic ESP32 in QEMU with
ESP-IDF 6.0.2, the corrected I2S DMA model, OpenETH, a 5-second task watchdog,
and static TLS RX with 16,384-byte TLS 1.2 body records. The comparison
keeps the same codecs, 512 kbit/s six-channel Opus signal, TFT mode,
audio task affinity and PDM DMA geometry.

## TFT allocation

The network-status renderer keeps two DMA slots and transfers four
RGB565 rows per slot. The two slots now occupy 5,120 bytes of the primary
DMA buffer. The first matched health samples had 136,500 bytes of free
DMA heap in the baseline and 141,644 in the smaller TFT build. With the
smaller TFT buffer alone, both six-channel fixtures started PDM. The
WebUI connection still closed during playback under receive pressure.
The QMP framebuffer comparison matched all 76,800 pixels of the
network-client frame with the QEMU control strip disabled.
[Images and measurements](display-observed.json).
[ESP-IDF SPI DMA buffer requirements](https://docs.espressif.com/projects/esp-idf/en/v6.0/esp32/api-reference/peripherals/spi_master.html).

## Compressed input pool

After the verified Family 1 identification page and before decoder open,
the CYD playback task selects the existing four-slot minimum when the
channel mapping needs at least four decoder handles. The adaptive pool
returns idle excess buffers immediately and retires leased excess buffers
when their owners return them. The next connection restores the configured
target after the previous decoder releases its generation.

The [reference dispatcher test](../../run-ogg-family1-dispatch-host.py)
checks the new callback once per Family 1 link before any decoder handle
exists and zero times for Family 0. The ASan/UBSan run passed 43 schedules,
12 controls and comparisons of 12,983,296 exact PCM samples against
the creator decoder.

## Full application playback

| Channels | Packet | Ogg page target | Result | Minimum free byte heap |
| --- | ---: | ---: | --- | ---: |
| 6 | 20 ms | 200 ms | Full TLS, PDM and WebUI after EOF | 2,892 B |
| 6 | 20 ms | 1,000 ms | Full TLS, PDM and WebUI after EOF | 4,112 B |
| 6 | 120 ms | 200 ms | One 11,520-byte word allocation failed while reserving 69,120 bytes of PCM planes | 3,676 B |
| 8 | 20 ms | 200 ms | Espressif decoder open failed on a 17,784-byte allocation | 14,944 B |

Each successful run transferred 55 full 16 KiB TLS body records and its
final short record. The ordered flush reported exactly 672,000 PCM frames.
All six channel metrics agreed with the libopus decode and WebUI returned
the same 13,588-byte asset before playback, during playback and after EOF.
The two successful runs recorded zero allocation failures.

The 1,000 ms page run measured eight resident input slots before playback,
four after the decoder started, and four released slots. At EOF the pool
held no ready, reading or writing leases.
[Playback observations](input-pool-observed.json).
