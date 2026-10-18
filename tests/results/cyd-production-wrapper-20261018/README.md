# CYD production build wrapper tests

The new [PowerShell wrapper](../../../idf/esp32-cyd2usb-native/build-production.ps1)
and [exporter](../../../tools/export_cyd_production.py) run the existing pinned
CYD build in a separate process, then validate image, ELF digest, backend, SDK
config, partition bounds and source identity before publishing a development
handoff. See [usage and scope](../../../idf/esp32-cyd2usb-native/PRODUCTION_BUILD.md).

Missing isolated configs use the corresponding full CYD profile when available,
with path/hash provenance; existing isolated configs are preserved. A clone
without that local full config uses CYD defaults and its backend overlay.
Generated firmware/evidence outputs are excluded from source fingerprints;
source/assets/config changes still invalidate a build. Actual Git dirty state
is recorded separately from source changes and checked against the descriptor.

[39 deterministic tests](report.json) have 38 passes, zero failures/errors and
one skipped directory-symlink case because this Windows host cannot create it.
They cover all backend fixtures, validation failures, seed preservation,
sequential output exports, source mutation, prior handoff preservation and an
actual child process/PowerShell frontend. They do not substitute for real SDK
build/export qualification, which follows in the integrated source snapshot.
