# ESP32-C3 OLED native: shared installation files

Prepared 2026-09-30 for the prebuilt-firmware route in the
[beginner's guide](../../../docs/ESP32C3_BEGINNERS_GUIDE.md#prebuilt-firmware-no-compilation).

This package supplies the bootloader, native 4 MiB partition table, initial OTA
selector and 256 KiB SPIFFS image. Choose `app.bin` separately from one of the
five native ESP32-C3 OLED variants listed in the guide and write it at `0x10000`.
These files are not an application and cannot run by themselves.

- ESP-IDF: v6.0.2; flash: DIO, 80 MHz, 4 MiB.
- Bootloader: quiet production profile from `eef49d1a9421222e0359f84a540d29b96fb765b3`, copied unchanged
  from `esp32c3-oled-native-production` with its partition table and OTA selector.
  A development application can still print its own logs with this bootloader.
- SPIFFS: copied from the successful `build-production-rtc32k` build at source
  `63572edf79803f6939a64c466f24ec1c3d79602a`. It contains the repository's compressed WebUI and playlist,
  and no Wi-Fi credentials. It is independent of deep-sleep/crystal build options.
- First installation writes SPIFFS and initial OTA state. Existing filesystem
  contents (including Wi-Fi and playlist) are replaced. NVS is not part of this
  package. For ordinary updates use only the application and initial OTA selector
  as documented in the guide; keep the existing bootloader, partition table and SPIFFS.
- Not compatible with the Arduino/I2S release's different partition layout.

| File | Bytes | Flash offset | SHA-256 |
| --- | ---: | --- | --- |
| `bootloader.bin` | 13200 | `0x0` | `b443314aaac9c274348009799c0ec715994dd8e136215d70982f6683fd6f6a50` |
| `partitions.bin` | 3072 | `0x8000` | `f26d55c34a06f24ed917555cc4608a87f7c2300a6a71e20153d6dd43816e2f18` |
| `boot_app0.bin` | 8192 | `0xe000` | `7d2c7ac4888bfd75cd5f56e8d61f69595121183afc81556c876732fd3782c62f` |
| `spiffs.bin` | 262144 | `0x3b0000` | `267ed480f7f9d74f86efdec0ea05163d3012e3bb9520c1f67efafb39719842fb` |

## Validation

All staged SPIFFS files match the tracked sources at `63572edf`, allowing Windows
CRLF line endings in `.gitignore` and `playlist.csv`. Regenerating SPIFFS with the
build's ESP-IDF settings produced exactly the archived image. The partition table
and OTA selector match the production RTC-crystal build; the selector is 8192 bytes
of `0xff`. Manifest hashes identify all files. All five native application
variants pass esptool 5.3.1 `image-info`, fit the application partition, and were
merged offline with this package to verify the documented offsets and contents.
On 30 September 2026 these shared files were flashed with the ordinary
production application. Write verification, AP setup, HTTP assets and Wi-Fi
configuration passed. This does not validate the sleeping-clock or crystal
features of other applications. See the [hardware report](../../../docs/ESP32C3_HARDWARE_VALIDATION_20260930.md).

SPIFFS was also decoded and its gzip files decompressed. Its 13 files contain only
the tracked WebUI assets, playlist and `.gitignore`; no `wifi.csv`, deleted file
pages or known local Wi-Fi credentials were found. This checks the distributed
image, not the contents of an already configured board.

The older `full.bin` files in the production/development variant folders remain
unchanged. They are 4 MiB recovery images with an empty SPIFFS region. The guide
uses these separate files to install the WebUI as well.
