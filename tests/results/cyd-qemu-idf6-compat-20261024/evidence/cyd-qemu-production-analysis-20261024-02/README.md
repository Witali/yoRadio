# Production observer02: independent read-only diagnosis

The root-owned controller completed its observation, not startup acceptance.
The original report remains unchanged: OBSERVATION_COMPLETED, QEMU exit0, real
QMP stdout EOF, reader joined without error, one guest-reset SHUTDOWN, unchanged
selected inputs and unchanged scratch medium. MPI's first return and display
driver entry are observed; pipeline/radio/Web readiness are not. The UART has
both a SPIFFS mount failure and a later asynchronous Wi-Fi PHY assertion.

The reviewer ran no guest, SDK/build/test tool, runner import, Git command,
binary disassembly or physical operation and changed no external/model/firmware
source. Only this ignored diagnostic directory was written. The read-only data
projections describe the captured bytes and source, not a new runtime PASS.

## The rebuilt GD model fixed the observed SR2 boundary

Independent parsing finds 1091 trace lines and 122 closed CS segments:121 have
both select and deselect, and the initial partial segment is excluded from
complete transaction claims. `flash-transactions.json` retains fourteen complete
SR2/QIOR transactions with raw text and original line numbers.

Five complete0x35 reads now have transfer states0 then5 and return actual SR2
data; one0x31 write now has states0 then3, consumes data0x02 as status data,
and its later0x35 readback is0x02. QE is bit index1, mask0x02. No assertion is
made that every flash function is now correct. The original QIE failure and
`init_flash:654` assertion disappear, consistent with that specific repair.

## The SPIFFS placement and magic geometry match the actual image

The actual partition table was parsed from the scratch image's0x8000 region,
not inferred from a proposed offset. It matches the saved original partition
table byte-for-byte. The five entries are nvs0x9000/0x5000,
otadata0xe000/0x2000, app0 0x10000/0x1b0000, app1 0x1c0000/0x1b0000,
and spiffs type1/subtype130 at0x370000 with size0x90000.

The complete SPIFFS region equals the saved589824-byte spiffs.bin, SHA256
e92e0bab990144ad683306fc59b60cb510656f96dff6f13952332cc7ca8ed027.
The saved SDK configuration and actual build.ninja generator command agree on
page256, object name32, metadata0, magic and magic-length enabled. The generator
uses its default logical block4096; SDK esp_spiffs.c uses the physical erase
sector size4096 as its logical block. The SDK's object ID is uint16.

All144 scratch-image block magic words at block*4096+252 match the SDK macro:
uint16(0x20140529 xor256 xor(144-block)). The first two are0x04b9/0x04a6;
the last is0x0428. `partition-spiffs-geometry.json` records every actual and
expected word. This is evidence for the selected geometry/magic compatibility,
not a full integrity check of all files or object metadata.

## A concrete QIOR transport defect explains the mount failure

`SPIFFS_ERR_NOT_A_FS` is-10025 (`spiffs/src/spiffs.h:43`). With magic enabled,
`spiffs_obj_lu_scan` reads each block magic and rejects after a second mismatch
(`spiffs_nucleus.c:347-378`). It reads magic and erase count through
spiffs_api_read → esp_partition_read, without formatting. The firmware
explicitly preserves `format_if_mount_failed=false`.

Three full captured transactions are decisive:

| Trace lines | Wire command/address | Following three wire bytes | Outcome |
| --- | --- | --- | --- |
|558-567|eb 37 00 fc|ff ff ff, states3 with len3/4/5 and needed8|Deselect while still collecting; never enters storage READ.|
|568-577|eb 37 00 fe|same|Same; this is the block0 erase-count address.|
|578-587|eb 37 10 fc|same|Same; this is the block1 magic address.|

The source's trace state3 is STATE_COLLECTING_DATA. GD QIOR parsing expects
three address bytes plus a mode byte and four legacy dummy-clock tokens, so
needed8. The current classic ESP32 SPI transaction sends command, address,
then directly the caller's data clocks; it ignores its exposed USER.DUMMY and
USER1.DUMMY_CYCLELEN fields. Consequently the response clocks are consumed as
unfinished command setup. `m25p80_transfer8` initializes its returned byte to0
and returns that value while collecting, so the caller receives zero setup
bytes rather than the backing image's correct magic. There is no early CS
deassertion inside the command/address/data sequence: both boundaries are
captured.

The five longer QIOR reads of erased NVS also consume their first five response
clocks as setup before entering storage READ. They cannot qualify read-byte
alignment merely because erased0xff contents obscure later bytes. The three
short SPIFFS reads never enter storage READ at all.

The supported model-only correction is to implement the classic ESP32 SPI dummy
phase before actual RX/TX data and align its byte-oriented SSI convention with
the flash model. The existing C3 implementation already offers a reference:
`esp32c3_spi_get_dummy` calculates ceil(clocks*lanes/8), and its ESP32-C3 machine
selects the public `byte-dummy-cycles=true` flash property. Classic ESP32
currently never sets that property and has no dummy transmission. Both sides
must agree; changing only the flash property or arbitrarily padding the
filesystem data would leave the transport wrong. Fast, dual-output,
quad-output, dual-I/O and quad-I/O modes need their own semantic checks.

No filesystem regeneration, NVS modification, automatic format, alternate
partition offset, DIO downgrade or firmware/SDK guard suppression is indicated.

## The later PHY failure is a separate DPORT register omission

The UART independently reports `phy module clock bits0x0, required0x8f8f`, then
asserts at phy_init.c:336 after `app_main` returned. The failure occurs in the
asynchronous network task; it does not prove a call-stack dependency on SPIFFS.

SDK `esp_phy/src/phy_init.c:334-336` enables common and PHY clocks, then checks
the required mask. `esp32/include/phy_init_deps.h:9` defines0x8f8f. The actual
SDK LL chain is in `components/esp_hal_clock/esp32/include/hal/clk_gate_ll.h`:

- get_clk_en_reg(PERIPH_WIFI_BT_COMMON_MODULE) returns DPORT_WIFI_CLK_EN_REG.
- common enable RMW-sets0x3c9; Wi-Fi enable RMW-sets0x406; RNG and BT clock
  enables use the same clock register. The PHY-calibration-only LL call has
  no extra ESP32 clock bit.
- `phy_module_has_clock_bits` reads that actual register and checks the mask;
  it does not use an emulator-specific readiness shortcut.

The SDK register definition places WIFI_CLK_EN at DPORT+0xcc (full32-bit R/W,
documented reset0xfffce030). CORE_RST_EN is the neighboring DPORT+0xd0
(documented reset0), used by related reset helpers. Current QEMU DPORT state,
register definitions and read/write switches do not implement either. The read
function initializes its result to0 and returns that for the missing0xcc case;
the write switch drops such writes. This directly matches the reported zero
after clock enables and supports implementing normal clock-register storage
and readback, not returning a fabricated0x8f8f or disabling the SDK assertion.

This change would only restore register semantics required by the SDK. No RF,
Wi-Fi association, calibration completion or real network traffic is qualified
by clock readback, and further unimplemented Wi-Fi/PHY behavior can remain.

## Source identities and next work

`inputs.json` lists exact raw artifacts, original image/config/recipe, SDK
SPIFFS and clock sources, and current QEMU sources used here. The root-owned
rebuild's new task-local executable has separately supplied SHA256
fe0dc693a042096f0666b433d41ec7555b5cf44f85d852e7f7ac006145f44d73;
the old installed executable and both older capture results remain untouched.

Source-only preparation of the narrowly scoped SPI/DPORT model corrections is
authorized separately by root. It must preserve production bytes/config and
use meaningful future MMIO/backing-byte tests. No such correction, compiler
invocation or new observation is counted by this diagnostic report.

Primary hardware references checked: the [Espressif ESP32 technical reference
manual](https://espressif.com/sites/default/files/documentation/esp32_technical_reference_manual_en.pdf)
defines independently enabled command/address/dummy/read/write phases and the
dummy clock-length field. The [GigaDevice GD25Q32C datasheet, section7.11,
figure13](https://download.gigadevice.com/Datasheet/DS-00088-GD25Q32C-Rev4.1.pdf)
defines0xEB as a three-byte address, one mode byte and four further quad clocks
before data; QE is required. Local SDK register/header identities are retained
for the exact firmware's clock and SPI field definitions.
