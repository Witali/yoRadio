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
- `bootloader.bin` and `partitions.bin` — component images;
- `manifest.md` — build configuration, flash offsets, sizes and SHA-256 hashes.

The combined image deliberately does not contain user SPIFFS data. For normal
updates prefer `app.bin`, which leaves saved Wi-Fi networks, playlists and
other settings untouched.

See [CHANGELOG.md](CHANGELOG.md) for release notes.
