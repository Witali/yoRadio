# YoRadio firmware archive

This directory contains immutable, versioned firmware builds for supported
YoRadio boards. Never replace or remove an existing release; create a new
`firmware/<version>/<variant>/` directory instead.

Successful production builds intended for testing or hand-off must also be
copied out of the ignored build directory. Unreleased, replaceable application
images are stored as `firmware/development/<variant>/app.bin`; the production
build scripts do this automatically. Promote a validated image into a new
immutable version directory when preparing a release.

Whenever a development `app.bin` is replaced, update its `manifest.md` and add
or update the dated Development section in `CHANGELOG.md` in the same commit.
The changelog entry must describe the functional changes and validation; the
manifest must identify the source, build profile, flash offset, size and
SHA-256 of the exact binary.

Binary `*.bin` files in this directory are stored with Git LFS. Install Git
LFS before cloning or pulling release artifacts:

```powershell
git lfs install
git lfs pull
```

## Test-image cleanup (2026-09-09)

Obsolete benchmark, tone-generator, profiling and experimental A/B image
directories were removed from `development/`. Their previously tracked
images, manifests and configurations remain in Git history at `904394b`
(binary recovery requires the corresponding Git LFS objects). Historical
changelog paths may therefore refer to files no longer in the current tree.
Test sources, build profiles and measurement reports under `docs/` were not
removed.

The local safety archive is `.build/firmware-test-archive-2026-09-09/` at the
repository root. It also contains eight previously untracked files which
cannot be recovered from Git. This archive is ignored and is not uploaded.

Versioned releases, ordinary radio images and the current ESP8266
`esp8266-spiffs-log` / `esp8266-spiffs-log-off` profiles remain available.
Retained historical radio images are not necessarily the latest firmware;
check their manifests and changelogs before flashing.

## Artifact contents

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
