# Exact production CYD boot smoke proposal

Status: prepared, not executed. No QEMU, SDK, compiler, rebuild, device, COM port or physical flash operation was started. Production source and firmware remain unchanged.

The seven already exported production images have all required local components. A bounded local boot attempt is feasible with the installed emulator's historical CYD ST7789/SPI-DMA model. Source inspection cannot promise that its incomplete ESP32 Wi-Fi/PHY model will let the actual production app reach every service. The proposed attempt records that boundary instead of bypassing Wi-Fi or replacing app_main.

## Inputs and exact image layout

inputs.json pins every file below with its observed SHA256 and size. It independently confirms each archived app, sdkconfig, partition table and flasher recipe against its production manifest, plus the original build app and ELF against the manifest hashes. All seven exports identify source 3a563324abdca56144a40d5759def0ccfe708b3c.

| Profile | Original build directory under this worktree | Archived app SHA256 |
| --- | --- | --- |
| pdm | .build/srx01/gvp | 66e99cfb4773bad31cd646ec22e0cdda5d1231bf9b3ea74a6940401aea98ecf3 |
| continuous | .build/srx01/gvc | b2eee657dcb20c8cd23e2f1053ae9894365a99560f5e3ab2b6f15a02b9801add |
| legacy | .build/srx01/gvl | f6e33080c070e1b61947e5b0a3767bbae6a5595f8f4247cbba6f43dab621ad21 |
| custom-flac-pdm | .build/srx01/gcp | c618a6561aff0eb4f48b07ddf686b631dfc1f029fffea600969d1b40529fc855 |
| custom-flac-continuous | .build/srx01/gcc | 12abbc93201f0b2361273593537d6b56a046feffaaca83b94dcc83e06d80b56c |
| custom-flac-legacy | .build/srx01/gcl | 4d88e1903766204499b15917a2bee4689d74e06bd46b23a75ec1935a4fb9edd1 |
| disabled-pdm | .build/srx01/goff | 7a2be3d41a28a09951d688b61ebfd6ae33ad7edd17a4296585f73df3de32cb4e |

Archived directories are firmware/development/esp32-cyd2usb-native-static-rx-PROFILE/. The disabled-pdm image disables static RX while preserving the early-MPI option; it is not an early-MPI-disabled control.

Build a disposable four-MiB local file filled with FF bytes, then copy these exact existing bytes to the recipe offsets. The helper does this directly, without esptool rewriting boot headers or any source/image patch:

| Offset | Component |
| --- | --- |
| 0x1000 | Original build bootloader/bootloader.bin |
| 0x8000 | Original build partition_table/partition-table.bin; matches archived partition-table.bin |
| 0xe000 | Original build ota_data_initial.bin |
| 0x10000 | Archived production app.bin; matches original build yoradio_cyd2usb_native.bin |
| 0x370000 | Original build spiffs.bin |

NVS 0x9000..0xdfff and the spare app1 slot remain FF in this new emulated medium. This is not a board-state clone. Normal radio defaults keep Smart Start disabled (state 2). The app0/app1 sizes are both 0x1b0000, app1 starts at 0x1c0000, and SPIFFS size is 0x90000. Original flash mode/frequency header bytes are retained, including the actual exported dio/80m settings.

## Installed emulator and peripherals

Exact executable: C:/Work/QEMU-ESP32/bin/qemu-system-xtensa.exe, SHA256 f6a5f29315d1bea5c99b74890a99c86c70886fdc0d50f24f62c24cdda43abc35. ROMs under C:/Work/QEMU-ESP32/pc-bios/ are esp32-v3-rom.bin (9115bbcd03da9f54d3baca5ad94d588a43da54ed332347137ba3dc9010df258b) and esp32-v3-rom-app.bin (6d3240e7cdb1ec9c1d683515e0a8578e9fb8ece3e7736cb9a996512c656e8442). These hashes match the prior local static-RX QEMU fixture's recorded tool identities.

Observed local emulator source and README are separately pinned; their relationship to the installed executable has not been requalified here. They describe ESP32 dual Xtensa cores, SPI flash/cache, SRAM, timers/interrupt matrix, GPIO, crypto/MPI locking, SPI2 DMA and ST7789, and I2S0. Historical st7789=on wiring matches CYD SPI2 CS15/DC2/backlight21 and firmware SCK14/MOSI13. No SD/touch or external audio source is needed for idle startup.

Use -audiodev none,id=quiet and the machine audiodev=quiet property. Local qemu-options.hx documents the none backend, hw/core/machine.c registers the property, and hw/xtensa/esp32.c passes it to embedded I2S0. Thus the proposal uses no host sound backend or sound output. The display model remains active with -display none, so LCD initialization still executes headlessly.

The ESP32 machine source has no Wi-Fi device. It can create open_eth, which -nic none disables. C3 Wi-Fi models are unrelated to this machine. Do not claim association, RF, sockets, WebUI requests, TLS negotiation or radio reception from a successful idle boot.

## Concrete proposed execution, after root review

The source-only capture.py helper has not been run. It validates selected pins, constructs the disposable medium, starts exactly one hidden emulator process, captures its emulated UART0 stdout to a local file, and stops/reaps only that owned process. No physical UART/COM port or host network endpoint is opened. Its QEMU command is:

    C:/Work/QEMU-ESP32/bin/qemu-system-xtensa.exe -audiodev none,id=quiet -M esp32,st7789=on,audiodev=quiet -smp 2 -L C:/Work/QEMU-ESP32/pc-bios -display none -monitor none -serial stdio -no-reboot -snapshot -nic none -drive file=NEW_OUTPUT/qemu-flash.bin,if=mtd,format=raw

Start with the vendor PDM image only:

    & 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe' -B -X utf8 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/cyd-production-radio-boot-prep-01/capture.py' --profile pdm --output 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/cyd-production-radio-boot-pdm-01'

Keep the executor yielding at most every 30 seconds while the helper runs. The helper has a 120-second wall deadline and requires five further seconds after all required markers, then performs an explicit owned-process stop. A deadline, process exit, panic, missing marker, service-start error or changed pinned input is nonpass. Timeout alone never passes. Raw exit code after our termination is recorded and does not masquerade as guest success. report.json records markers independently, including partial MPI/display evidence when later startup is blocked. Recheck source/image/tool and scratch-medium hashes after termination.

The useful first comparison is the already saved PDM reserve-ON/reserve-OFF pair. Repeat the same command with --profile disabled-pdm and --output C:/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/cyd-production-radio-boot-disabled-pdm-01. Both preserve early MPI. Consider other backends only after reviewing this pair. If either stalls or panics at an unmodeled peripheral, preserve that actual failure boundary. Do not patch the application/SDK/emulator or switch to an alternate board model in this gate.

## What each observation establishes

| Observation | Supported interpretation |
| --- | --- |
| Starting pure ESP-IDF yoRadio (Arduino-free), exactly once | app_main progressed beyond native_tls_early_mpi_prepare. Existing pinned PDM disassembly shows its acquire/release call before the first log. This proves observed return, not absence of all future lock allocation or target hardware timing. |
| ST7789: SPI2 DMA | Driver setup reached its log. This log precedes the initial screen clear and alone does not establish that clear completed. |
| Pipeline ready: selected backend | Display init and initial clear returned, network_task was created, audio queues and three pipeline owners were created, native output init completed, and startup reached ready publication. It does not exercise decoded PCM or active I2S/DAC output configuration. |
| Smart Start state: 2, followed by Native HTTP/HTTPS server started without component failure | Radio initialization returned and WebSocket/HTTP service startup reached ready publication. No HTTP request was sent, and no connection or playback is qualified. |
| Network failed:... | Retain as an explicit network infrastructure failure. app_main deliberately continues to audio/Web startup, so subsequent markers do not erase this failure. |
| No panic plus five-second settling after every required marker | The selected startup subset stayed observable during the bounded capture. It is not a soak or physical stability result. |

Static RX has no startup allocation or positive boot marker: its buffer, state and registry are BSS, with runtime eligibility registered only by the radio TLS certificate-attach callback. The saved PDM map places s_rx at 0x3ffbaa28 with size 0x414d. A network-free idle boot cannot exercise a static-RX loan, ownership handover, TLS handshake, reclaim recovery or consumption by playback. The helper always leaves static_rx_loan_exercised=false and full_radio_startup_qualified=false. Earlier focused host/QEMU evidence remains separate.

No private AAC/Vorbis work, deferred FLAC target tests, production rebuild, restore upload, serial reset or external network is part of this proposal.
