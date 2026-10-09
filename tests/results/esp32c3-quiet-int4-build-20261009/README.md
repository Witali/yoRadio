# Quiet integer-clock production candidate: build evidence

See [the report](../../../docs/ESP32C3_QUIET_INT4_BUILD_20261009.md).
This archive proves configuration, linked allocator/codec paths, unchanged
AAC/FLAC arithmetic and saved image identity. It contains no hardware or
acoustic acceptance claim. The matching manifest remains explicitly
`production_qualified=false` and `hardware_tested=false`.

`build.ps1` records the build arguments; `audit_build.py` verifies the linked
image and normal certificate roots. `codec_objects.py` compares all nonempty
text/rodata sections in 18 codec objects against the previous quiet build.
The build log contains the captured environment setup; it is not a complete
compiler-output transcript. The completed ELF, link audits and image hashes
are the retained build evidence. Local scripts are provenance, not permission
to overwrite existing firmware artifacts or evidence.

`index.json` fixes the exact bytes of this archive. `sources/` preserves the
manifest's firmware overlays, including the unrelated, inactive CLZ CMake
block as provenance. Compile-command checks prove CLZ and the flash probe
are absent from this image. The actual firmware is saved separately under
`firmware/development/esp32c3-idf-6.1-r9a97-quiet-int4/`.
