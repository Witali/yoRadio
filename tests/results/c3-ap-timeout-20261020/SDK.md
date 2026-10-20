# C3 AP timeout production build

Clean source: `e78b154da304aa9859177ae7dd798ad2518e6ce5`.
Pinned ESP-IDF: `9a97f6c54ec638111ce55cd36581b3c192f15207`.
The production wrapper uses the existing tested radio profile. No board was
flashed or reset. Earlier firmware variants and versioned releases are intact.

| Variant | Application bytes | Each OTA slot | Spare bytes |
| --- | ---: | ---: | ---: |
| [C3 AP timeout](../../../firmware/development/esp32c3-oled-native-ap-timeout/manifest.json) | 1542256 | 1900544 | 358288 |

`SDK.json` records actual image XOR/SHA256, descriptor/ELF linkage, RISC-V32
ELF machine, ESP32-C3 chip ID 5, partition-table MD5/nonoverlap/both OTA slots,
compiler hash and defined symbols. The immediate reserved restart symbol is
present; the obsolete AP timer callback is absent. Configuration is identical
to the N4 C3 export. Audio/app/board/default-profile sources and all CYD
production sources are unchanged from the previous checkpoint.

The build logs contain no compiler warnings. Five existing SDK CMake include
dependency warnings remain; the complete raw diagnostics are saved with the
firmware. The local qualification script initially used the ESP32-only image
descriptor helper, rejected the C3 chip ID, and was corrected to validate ID 5
explicitly. The application bytes were not changed by that correction.

The firmware folder preserves app/configuration/partition/recipe/project and
stdout/stderr bytes with their manifest hashes. `SDK.json` and `sdk-symbols.log`
add qualification of the actual linked image. Git LFS pointers and actual local
objects are checked before the artifact commit. The emulator and host evidence
do not establish physical OTA, RF/DHCP, sleep timing or audio/resource margins.
