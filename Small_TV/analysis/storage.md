# Small_TV flash storage layout

Static analysis of the saved 4 MiB dump on 2026-10-12 found no SPIFFS,
LittleFS, SimpleFS or FAT filesystem implementation in the reviewed
application paths. The device stores its images and settings directly
at fixed flash offsets. The complete backup already includes these
bytes; there is no identified separate filesystem/disk image to mount.

## Declared partitions

The partition table at flash `0x8000` has only three entries:

| Label | Type / subtype | Offset | Size |
| --- | --- | --- | --- |
| `nvs` | data / NVS (`0x01 / 0x02`) | `0x009000` | `0x6000`, 24 KiB |
| `phy_init` | data / PHY (`0x01 / 0x01`) | `0x00F000` | `0x1000`, 4 KiB |
| `factory` | app / factory (`0x00 / 0x00`) | `0x010000` | `0x177000`, 1500 KiB |

There is no filesystem partition (SPIFFS normally uses data subtype
`0x82`), nor an OTA slot or OTA data partition. The raw image and
application-settings regions below are **outside the declared
partitions**, but are included in `full-flash.bin` and used by direct
`esp_flash_read`, `esp_flash_write` and `esp_flash_erase_region` calls.
The NVS partition is a key/value store used by SDK initialization,
rather than a directory of image/web files.

## Raw image and settings areas

All range ends in this table are exclusive.

| Area | Start | End | Reserved capacity / format |
| --- | --- | --- | --- |
| Photo 1 | `0x200000` | `0x219000` | 100 KiB; starts with JPEG in this dump |
| Photo 2 | `0x219000` | `0x232000` | 100 KiB; JPEG |
| Photo 3 | `0x232000` | `0x24B000` | 100 KiB; JPEG |
| Photo 4 | `0x24B000` | `0x264000` | 100 KiB; JPEG |
| Photo 5 | `0x264000` | `0x27D000` | 100 KiB; JPEG |
| Built-in animation 0 | `0x27D000` | `0x2AF000` | 200 KiB; custom `GIF`-prefixed frame table and JPEG frames |
| Built-in animation 1 | `0x2AF000` | `0x2E1000` | 200 KiB; same format |
| Built-in animation 2 | `0x2E1000` | `0x313000` | 200 KiB; same format |
| Built-in animation 3 | `0x313000` | `0x345000` | 200 KiB; same format |
| Built-in animation 4 | `0x345000` | `0x377000` | 200 KiB; same format |
| Weather / display assets | `0x377000` onward | Complete boundary not established | Fixed-address assets, including references at `0x3BA800`, `0x3BE400`, `0x3C2000` and `0x3C5C00` |
| Application settings sector | `0x3E7000` | `0x3E8000` | 4 KiB sector; settings structure uses `0x1BC` bytes |

The five photo slots are confirmed by `/start_upload` at `0x4200DDA4`:
`base = 0x200000 + (file_number - 1) * 0x19000`, with accepted image
numbers 1..5. The handler erases 25 sectors for the selected slot. JPEG
signatures at all five starts confirm the snapshot contains images there.

Animation selection at `0x4200B5CC` chooses one of the five listed bases,
reads a 1024-byte header/table and tests only the first three bytes for
`GIF`. Eight-byte frame entries begin at header offset 11; the second
word is a relative JPEG frame offset. In all five blocks, the first
frame offset is `0x400` and JPEG signatures occur there. Their header
bytes are not `GIF87a` or `GIF89a`: these are custom animation containers,
not standard GIF files or a filesystem. A decoder can be reconstructed
from the table without a SPIFFS mount.

`0x42008552` loads application settings from `0x3E7000`, and `0x42008A00`
erases/re-writes that sector. Settings include connection configuration,
NTP/weather configuration and display preferences. The captured settings
sector is entirely erased (`0xFF`), so startup supplies defaults for the
fields it validates. The stored photo-size words are also erased; this
does not negate the JPEG data present in the fixed slots. Saved passwords
must not be printed when inspecting a future dump containing settings.

## Embedded web pages

The HTTP handlers serve HTML constants from the application's read-only
data segment rather than opening files. Identified page starts are:

| Page | Runtime address | Flash offset | Handler |
| --- | --- | --- | --- |
| Wi-Fi setup | `0x3C0D6EDC` | `0x026EDC` | `/`, `0x4200D404` |
| Clock/settings | `0x3C0D963B` | `0x02963B` | `/`, `0x4200D404`, connected-state branch |
| Photo upload | `0x3C0E2E6E` | `0x032E6E` | `/photo`, `0x4200D54C` |

Thus the editable content is exposed through the device's custom HTTP
API, not a general filesystem file manager. A string search also found
no `SPIFFS`, `spiffs`, `LittleFS`, `littlefs`, `SimpleFS` or `FATFS` names
in the snapshot. This search alone would not prove filesystem absence;
the partition table and direct storage code are the stronger evidence.

See [storage-map.json](storage-map.json) for checked signatures and offsets,
the [security decompilation](security/security-decompiled.c) for the
storage handlers, and the [hardware report](README.md) for the image map.
Partition type interpretation follows [Espressif's partition-table
documentation](https://docs.espressif.com/projects/esp-idf/en/v5.4.3/esp32c2/api-guides/partition-tables.html).
