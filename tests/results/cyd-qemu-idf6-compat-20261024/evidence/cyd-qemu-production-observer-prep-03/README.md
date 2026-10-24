# Production PDM observer03: source preparation only

This standalone successor starts from byte-exact observer02 capture.py SHA256
`dea7385425b2a05a0d57f769bafb84a00b8dc528ea45681ba190de0391722d7b`.
It has not been imported, executed or used to launch a guest. Original observer02,
all earlier observations, firmware, SDK/config and external QEMU sources are
untouched. The full successor diff is capture-vs-02.diff; raw record-only origin
copies and their exact paths/hashes are indexed in provenance.json.

The only source changes select the future fixed executable at
`.build/cyd-qemu-idf6-build-01/qemu-system-xtensa.exe`, add observer02 and the
independent QEMU-model review to before/after runtime identities, and correct
metadata. Reports explicitly state emulator_model_patched=true and
firmware_patched=false. The legacy combined firmware_or_model_patched field is
true because the emulator model is changed. It is not a firmware patch claim.
The independent source review is
`.build/cyd-qemu-idf6-compat-review-20261024-01/review.json`, SHA256
`2de220f1c540ea4db351b318feee0a256b502f7164ef50badfb2bf583b26480d`.
That review is source-only evidence, not build or MMIO execution evidence.

The original production inventory remains exactly
`f9cf237bbbefe7967abbb558b06beb1ed4617035769669bb770223ad01bf5b12`:
source3a563324abdca56144a40d5759def0ccfe708b3c and original PDM app
66e99cfb4773bad31cd646ec22e0cdda5d1231bf9b3ea74a6940401aea98ecf3.
Original application, bootloader, partition/OTA/SPIFFS components, offsets, ROMs,
QIO80 / CPU240 / two-core configuration and task affinity remain authoritative.
No DIO downgrade, SDK CONFIG_FREERTOS_SMP change, flash-header edit, filesystem
formatting or production rebuild is introduced. Original tools and all selected
profile/source rows, the original executable, new executable and actual observer
are checked before and after, together with all four runtime source origins.
The four-MiB scratch flash contains only original components plus erased NVS;
-snapshot and final byte identity protect that scratch backing file.

Lifecycle, observations and bounds are byte-exact to observer02: owned hidden
QMP stdin/stdout child, UUID query-name verification before trace/cont, six
existing trace events verified enabled and others disabled, UART/stderr/trace
saved separately, no NIC/backend audio/listener/physical device. There is one
bounded guest execution, at most 20 seconds after cont, with a three-second
panic grace within that window and acknowledged QMP quit if needed. Complete
observation requires actual QMP EOF, reader join, no read/parse error or forced
stdout closure, actual exit0, the exact single guest-reset or host-qmp-quit
SHUTDOWN, every selected input unchanged, and unchanged scratch media. The
32MiB per-artifact bound is monitored by polling with terminal overshoot
rejection; cleanup and input hashing follow the bounded observation phase.

OBSERVATION_COMPLETED means controller/input/artifact/lifecycle completion.
It does not qualify successful boot, full radio, RF/network association or
traffic, physical audio, performance, static-RX loans or real hardware. All
qualification flags remain false and existing startup marker predicates are
unchanged. Earlier NONPASS results are retained and never reclassified here.

Root must first review this source, independently finish/save the fixed QEMU
build and its actual digest, and complete meaningful model regressions before
considering an observation. Example only, not executed:

    python -B -X utf8 .build/cyd-qemu-production-observer-prep-03/capture.py \
      --pins tests/results/cyd-production-radio-boot-20261020/preparation/inputs.json \
      --pins-sha256 f9cf237bbbefe7967abbb558b06beb1ed4617035769669bb770223ad01bf5b12 \
      --qemu .build/cyd-qemu-idf6-build-01/qemu-system-xtensa.exe \
      --qemu-sha256 ACTUAL_FIXED_BUILD_SHA256 \
      --output .build/cyd-qemu-production-observation-20261024-03

Root records the actual outer argv/terminal/logs separately. No deferred codec
scope, codec campaign, physical device, COM, network or flashing is part of this
source preparation or observer.
