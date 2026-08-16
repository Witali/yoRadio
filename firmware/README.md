# YoRadio firmware archive

This directory contains immutable, versioned firmware builds for the
ESP32-2432S028 CYD2USB board. Never replace or remove an existing release;
create a new `firmware/<version>/<variant>/` directory instead.

Binary `*.bin` files in this directory are stored with Git LFS. Install Git
LFS before cloning or pulling release artifacts:

```powershell
git lfs install
git lfs pull
```

Each variant directory contains:

- `app.bin` — application image for OTA/WebUI updates;
- `full.bin` — merged 4 MiB image for initial programming and recovery;
- `bootloader.bin`, `partitions.bin` and `boot_app0.bin` — component images;
- `manifest.md` — build configuration, flash offsets, sizes and SHA-256 hashes.

The combined image deliberately does not contain user SPIFFS data. Flashing
`full.bin` at address `0x0` replaces the entire 4 MiB flash and therefore
erases NVS, SPIFFS, saved Wi-Fi networks, playlists and other settings. For a
normal update use `app.bin` through WebUI, or the component images at their
manifest offsets, to preserve settings.

See [CHANGELOG.md](CHANGELOG.md) for release notes.
