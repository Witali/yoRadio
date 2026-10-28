# ESP32-C2 JPEG/NOR test firmware

Standalone decoder/storage probe for the Small TV reconstruction. It runs
synthetic JPEG fixtures, compares RGB565 digests and exercises guarded temporary
flash, limits and recovery. The main clock UI and Wi-Fi are not part of this image.

Use `manifest.json` for exact addresses, image/source/ELF hashes and the pinned
ESP-IDF revision. `assets.bin` contains the matching ownership stamp. The build
and QEMU runner are in `Small_TV/src/tests/jpeg_backing/`; results are documented
in `Small_TV/src/tests/JPEG_BACKING.md`.

The binary statically links the adapted libjpeg-turbo 3.2.0 decoder at commit
`c85e6b905bf237038faa936dab160ebfc5da0344`, without SIMD or TurboJPEG. Adaptation
patches and provenance are in `Small_TV/src/tests/jpeg_library_probe/`.
See the accompanying unchanged [LICENSE.md](LICENSE.md) and [README.ijg](README.ijg).

This software is based in part on the work of the Independent JPEG Group.
