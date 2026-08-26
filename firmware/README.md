# YoRadio firmware archive

This directory contains immutable, versioned firmware builds for supported
YoRadio boards. Never replace or remove an existing release; create a new
`firmware/<version>/<variant>/` directory instead.

Successful production builds intended for testing or hand-off must also be
copied out of the ignored build directory. Unreleased, replaceable application
images are stored as `firmware/development/<variant>/app.bin`; the production
build scripts do this automatically. Promote a validated image into a new
immutable version directory when preparing a release.

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
