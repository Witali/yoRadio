# Local emulator rebuild preparation

The installed QEMU and its existing build output have SHA256
`f6a5f29315d1bea5c99b74890a99c86c70886fdc0d50f24f62c24cdda43abc35`.
The captured production-image flash transactions disagree with the newer local
GigaDevice 0x31/0x35 source branches. First inspect Git provenance and Ninja's
dry run, then rebuild the existing target offline if the proposed work is bounded.

Do not install or replace the original runtime in `bin/`. Preserve its pinned
bytes and all previous evidence. Copy a successful new executable here and give
it a separate identity before using it. Do not modify firmware, SDK, original
configurations, flash images, or QEMU source. The original trace controller's
`DIAGNOSTIC_INCOMPLETE` result remains unchanged.

This preparation is not a build result or a boot qualification.
