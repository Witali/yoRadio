# Exact production CYD boot: NONPASS before app_main

Two local QEMU attempts used the unchanged saved vendor PDM production images
from source 3a563324abdca56144a40d5759def0ccfe708b3c: static RX reserve ON and OFF.
The complete original flash components were copied byte-for-byte into a fresh
four-MiB disposable image. No application, configuration, SDK or emulator bytes
were patched; no rebuild, physical board, serial port, network or host audio
backend was used.

Both controllers returned 1. Both guests reached the expected application
identity, multicore SDK startup and heap initialization, then asserted during
SDK flash initialization at esp_flash_spi_init.c:654 before app_main. The
bootloader's QIE readback had already failed. The emulator exits 0 after the
guest requests reboot under -no-reboot; this does not represent startup success.
All application markers are false. All selected input bytes and scratch images
remained unchanged.

DIAGNOSIS.md distinguishes observations from the inferred flash-model/profile
limitation. The exact failing flash_ret/transaction and correspondence between
inspected emulator source and installed executable are unproven. Neither early
MPI return, display completion, pipeline startup nor static-RX use is qualified.
Earlier isolated TLS qualification and production build/lint evidence remain
separate; physical acceptance is still open.

Each profile directory contains its original report/log and a root-observed
controller terminal receipt. preparation/ preserves the exact executed helper,
observed input pins and the proposal as written before execution. Its prepared
status describes that historical preparation, not a later runtime pass.
manifest.json lists raw size/SHA256 for every retained member. Firmware, ELF,
ROM/tool and scratch-image binary payloads are omitted; their observed hashes
remain in the reports/input inventory. No omitted binary reconstruction is
claimed.
