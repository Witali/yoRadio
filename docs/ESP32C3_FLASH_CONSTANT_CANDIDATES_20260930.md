# ESP32-C3 Flash constant candidates

Audit date: 2026-09-30. Firmware source baseline: `701591bb`.

Most large immutable objects in the ESP32-C3 radio are **already in Flash**:
WebUI pages, fonts, audio lookup tables and ordinary string literals. There is
no large overlooked application string table in DRAM that would solve the
remaining HE-AAC memory deficit. The useful candidates below include small
pointer objects, redundant runtime copies of constant strings, and conditional
SDK changes. These are candidates only; firmware behavior and the board were
not changed during this audit.

## Scope and evidence

The repository scan covered **1,251 tracked C/C++/Arduino, assembly, included
table and linker files**, including inactive targets, vendored sources, tests
and saved source snapshots. The scan records every file, its hash, line count,
string-token count and placement-attribute hits in the
[source inventory](audits/esp32c3-flash-constants-20260930/source-inventory.csv).
String-token counts include header names and inactive preprocessor branches;
they are not counts of resident strings or an estimate of RAM savings.

| Repository area | Files scanned | Relevance to this C3 build |
| --- | ---: | --- |
| `idf` | 86 | C3 native application, shared components and other IDF boards |
| `yoRadio` | 407 | Shared pages, normalizer and FLAC are used; most Arduino drivers and optional decoders are not |
| `esp8266` | 512 | Other target and vendored codecs; findings are listed separately |
| `tests` | 111 | Test code and stubs, not production RAM |
| `tools` | 80 | Benchmark/reference sources, not automatically production code |
| `firmware` | 42 | Saved source snapshots, not current compilation inputs |
| `examples` and `broken204` | 13 | Examples and historical code |

A fresh **analysis-only build** used the exact saved
[`esp32c3-aac-buffers-quiet/sdkconfig`](../firmware/development/esp32c3-aac-buffers-quiet/sdkconfig):
ESP-IDF 6.0.2, Espressif codec 2.6.2, C3 at 160 MHz, DIO 80 MHz,
no PSRAM, no deep sleep, heap-in-Flash off, diagnostics off. No image was
installed. The build succeeded. Its 916 translation units were also scanned;
29 are tracked project sources, and the rest are dependencies or generated
build inputs. A translation unit being compiled does not mean all its data
survives conditional compilation and linker garbage collection.

The source scan is a broad lexical inventory. Candidate declarations and their
users were inspected manually, and the **complete linked RAM data sections**
were checked against the ELF/map, including anonymous string pools. This is not
a claim that every SDK call path or inactive board variant was runtime-tested.
Publicly unavailable AAC/SBR and Wi-Fi implementation sources were assessed
through their linked sections and public interfaces, not source-level proof.
Web assets embedded by the C3 build were checked in the map; other browser and
host scripts are not MCU static data.

The [build identity and section sizes](audits/esp32c3-flash-constants-20260930/summary.json)
record ELF SHA-256
`6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d`.
Configuration SHA-256 matches the saved quiet image. The new embedded Git
version differs from the currently installed image; this is not a remeasurement
of physical free heap.

| Linked output section | Bytes | Interpretation |
| --- | ---: | --- |
| `.dram0.data` | 12,160 | Initialized writable data plus constants explicitly retained in RAM |
| `.dram0.bss` | 30,704 | Zero-initialized mutable state and buffers |
| `.iram0.text` | 53,656 | RAM code; separate from the constant-data candidates |
| `.flash.rodata` | 305,204 | Read-only data already stored in Flash |

The SRAM alias reservation `.dram0.dummy` must not be counted again as data.
Object payloads exclude alignment and heap metadata; stack payloads are not
automatically recoverable heap. See the complete
[ELF objects](audits/esp32c3-flash-constants-20260930/elf-objects.csv),
[RAM input sections](audits/esp32c3-flash-constants-20260930/ram-input-sections.csv)
and [raw RAM string runs](audits/esp32c3-flash-constants-20260930/ram-string-runs.csv).

## Candidates in the C3 application

| Priority | Location and object | Present storage and potential benefit | Proposed change and conditions |
| --- | --- | --- | --- |
| Small straightforward change | [`flac_decoder.cpp:49–50`](../yoRadio/src/audioI2S/flac_decoder/flac_decoder.cpp#L49), `FLACFrameHeader`, `FLACMetadataBlock` | Two pointer objects, **4 + 4 bytes** in `.dram0.data` | Declare the pointers themselves `T *const`, or use the backing objects directly. Both pointers are initialized once and no reassignment was found across the repository. The pointed-to frame/metadata structs remain writable. Confirm the 8-byte payload leaves DRAM and run FLAC/codec-switch tests. |
| Small stack improvement | [`oled_display.c:96`](../idf/esp32c3-oled-native/main/oled_display.c#L96), `init[28]` | Flash initializer is copied into **28 bytes of stack**, then copied again to the transfer buffer | Use `static const uint8_t init[]`. [Actual disassembly](audits/esp32c3-flash-constants-20260930/oled-init-disassembly.txt) shows seven loads from DROM and stores at `sp+84` through `sp+108`. `send_commands()` already copies into a RAM transfer buffer before I2C. This saves a temporary copy; no steady heap saving unless separately justified stack sizing changes follow. |
| Small stack improvement | [`web_service.c:823`](../idf/esp32c3-oled-native/main/web_service.c#L823) and [`websocket_service.c:692`](../idf/esp32c3-oled-native/main/websocket_service.c#L692), route descriptors | 12 HTTP descriptors plus one WebSocket descriptor, each **24 bytes** in this ABI | Use `static const httpd_uri_t` objects, or a const route table. Initializers are fixed and callers do not modify them. Up to 288 bytes of source-level descriptor storage in `web_service_start`, plus 24 in the nested registration function; actual stack reduction requires compiler verification. **This does not remove the server's heap copies.** |
| Larger change for a small persistent gain | Same routes plus SDK `components/esp_http_server/src/httpd_uri.c:150–179` | SDK allocates **312 bytes of descriptors + 148 bytes of URI strings**, before allocator overhead | Consider an explicit borrowed-static-route API: retain Flash pointers for lifetime-stable descriptions/strings instead of `malloc`/`strdup`. The stock registration API always copies them, even if the originals are const. Preserve the existing owning API and track ownership so unregister/stop/error cleanup never frees Flash. Test wildcard routes, both `/webboard` methods, WebSocket, OTA and server restart. [Exact route inventory](audits/esp32c3-flash-constants-20260930/http-route-copies.json). |

Do not add the stack and server-copy rows as if both were existing static RAM
allocations. The latter is a server ownership redesign. Its **460-byte payload**
is an estimate from the registered routes and the DWARF type size, not a measured
free-heap delta after an implemented optimization.

## SDK candidates requiring separate qualification

`<IDF>` in the evidence files denotes the pinned local ESP-IDF 6.0.2 checkout.

| Candidate | Evidence and size | Required work and risk |
| --- | --- | --- |
| Make eFuse descriptor pointer arrays const | `components/efuse/esp32c3/esp_efuse_table.c`, generated `ESP_EFUSE_*[]` arrays; **37 linked arrays / 316 bytes** in DRAM. The descriptors they point to are already const. | Change the table generator, generated declarations and consuming API types to `const esp_efuse_desc_t *const ...`. Public APIs currently accept mutable pointer arrays, including `esp_efuse_get_purpose_field()`. Audit callers and early/cache-disabled access before accepting. Keep descriptor contents and eFuse operations unchanged; no eFuse burning is needed for this audit. |
| Move heap diagnostics together with heap code | `components/heap/linker.lf`, `tlsf.c`, `multi_heap.c`; RAM string inputs include `assert_valid_block`, `multi_heap_get_first_block`, `tlsf_free`, `tlsf_malloc`, `tlsf_memalign_offs` | Use the supported `CONFIG_HEAP_PLACE_FUNCTION_INTO_FLASH` route only after cache-disabled allocation paths are excluded. These five inputs have **865 bytes before string pooling**, not 865 independently reclaimable RAM bytes. Their strings are merged with other components. The previous experiment freed **9,072 bytes overall, code and data combined**; that is not a string-only gain and its HTTP-load qualification remains unresolved. See [the prior experiment](ESP32C3_AAC_MEMORY_20260930.md#heap-placement-experiment--not-a-default). |
| Reduce retained SDK assertion text | HAL/cache/MMU/Flash function names and assertion expressions remain in DRAM with assertion level 2 | A smaller assertion policy can remove text, but is a diagnostics tradeoff rather than a safe Flash relocation. Investigate only as a separate configuration experiment; preserve error handling and rerun OTA/Flash/heap-corruption diagnostics. Do not relocate cache-disabled panic text by adding ordinary `const`. |

The final map contains a **3,212-byte merged RAM literal pool** under
`.rodata.spi_flash_os_check_yield.str1.4`. It also contains heap, HAL, panic and
PHY strings: the map container name does **not** identify the original owner of
every string. Zero-size input rows and `bytes_before_relaxing` in the saved CSV
show this merging. Counting both this pool and its contributors would double
count the same bytes. The raw ASCII scan also includes numerical/pointer bytes
that happen to look printable; its 3,140-byte total is not a savings estimate.

## Objects already in Flash

These are verified in the analysis ELF and provide **zero additional RAM saving**
from another `const` or `PROGMEM` annotation.

| Object or group | Bytes in Flash | Source or ELF evidence |
| --- | ---: | --- |
| `index_html`, `emptyfs_html`, `emergency_form` | 2,344 + 4,496 + 299 | `yoRadio/src/core/netserver.h`, included through `web_pages_bridge.cpp` |
| Embedded `native-script.js.gz` | 10,960 | `_binary_native_script_js_gz_start/end`, DROM addresses `0x3c110bb4` to `0x3c113684` |
| `font`, `font8x15`, Unicode lookup, boot logo | 1,280 + 3,840 + 256 + 360 | `font5x7.h`, `font8x15.h`, `boot_logo_72x40.h` |
| Clock segment masks | 10 | `oled_display.c`, `segments.0` |
| AAC sample-rate lookup | 52 | `native_aac_decoder.c`, `rates.0` |
| WebUI required/allowed filenames, pointer arrays | 28 + 44 | `web_service.c`, `required.0` and `names.1` are already `const char *const[]` |
| Normalizer soft-limit lookup | 1,170 | `AudioNormalizer.cpp`, `kSoftLimitLut` |
| AAC/SBR examples | 4,100; 2,048 + 2,048; 620 + 620 + 640 + 620 | SDK `inverseQuantTable`, long windows, four `sbrDecoderFilterbankCoefficients*` arrays |
| Other codec examples | 5,088; 16,384 | SDK Opus `CELT_PVQ_U_DATA`; Vorbis `vwin8192` |

Ordinary status/error text, HTTP/JSON format strings, log tags and NVS key names
in the C3 sources use the default read-only placement, or are optimized away in
the quiet build. A pointer parameter/local variable does not copy the literal
into RAM. Conversely, `const char *p` makes the characters const, **not the
pointer**; immutable pointer tables need the second const:

```c
static const char text[] = "fixed text";
static const char *const names[] = {"one", "two"};
```

The native C3 compatibility shim deliberately defines `PROGMEM` as empty:
the C/C++ const qualification and linker placement do the work. This observation
does not authorize applying C3 byte-access assumptions to the ESP8266.

## Keep these in writable or retained memory

| Location | Reason to exclude from a direct constant move |
| --- | --- |
| `radio_control.c`, `s_current_name[144]`, current/candidate URLs and playlist line | Updated when the user changes station or imports a playlist. The default text in the initializer does not make the object constant. |
| `runtime_settings.c`, mDNS/SNTP buffers: 24 + 35 + 35 bytes | User-editable strings loaded from NVS and changed through WebUI. |
| `time_service.c`, two 35-byte SNTP buffers | lwIP retains their addresses; `time_service_apply()` updates them after stopping SNTP. Removing duplicate ownership may save RAM later, but substituting defaults would break saved settings. |
| `native_state.c/.h`, station/title/codec/stream-format fields | Mutable snapshots. `stream_format` holds formatted live parameters as well as literal statuses. An enum or borrowed codec-name design would be a separate API/lifetime change. |
| Audio input, ADTS, PCM, DMA, FLAC coefficients, normalizer state, WebSocket JSON and HTTP request buffers | Written during streaming or requests; neither const nor ROM lookup tables. |
| `rtc_wake_stub_clock.c`, `left[4]` and `g_rtc_clock` glyph/frame storage | Deep-sleep wake code accesses these before ordinary Flash access is available. This file's constants/data are deliberately retained in RTC memory. It is inactive in the quiet build; moving its constants to Flash would break the deep-sleep variant. |
| `encoder_input.c`, `s_transition_table[16]` | Already const in the optional C3 encoder path. Current ISR service uses flags 0; an IRAM-safe registration change would require a new data/call-path audit. `IRAM_ATTR` alone does not make all referenced constants safe. |
| SDK Flash-chip descriptors, chip-name strings, host dispatch tables, panic strings and libc syscall stub table | Used on early, ROM or cache-disabled paths. In particular, the seven 124-byte chip descriptors cannot simply be read from the Flash they control. Removing unused chip drivers would be a separate hardware-support change. |
| SDK PHY/Wi-Fi data and rate-control tables | Some are mutable; binary-only consumers prevent a source-level immutability and cache-safety proof. A table-like name is insufficient evidence. |

The traced **55,128-byte SBR object** is mutable decoder history/workspace. Its
constant coefficient tables already live in Flash. This audit does not turn
that allocation into read-only storage or resolve the full-radio SBR budget.

## Additional candidates in other source trees

These are source-level candidates only: **zero saving for the current native
C3 image**. Sizes below are nominal payloads on a 32-bit target, before compiler
elimination, object padding and any platform-specific Flash access mechanism.
Do not sum them into the C3 budget or claim verified placement on other boards.

| Source and object | Nominal size | Candidate and qualification |
| --- | ---: | --- |
| `yoRadio/src/core/netserver.cpp:82`, `files[11]` | 44 B static pointer table | Add top-level pointer const; the loop only reads it. |
| `yoRadio/src/core/config.cpp:32`, `reqiredFiles[11]` | 44 B temporary pointer table | Use `static const char *const[]`; verify actual stack code. |
| `yoRadio/src/displays/tools/utf8Rus.cpp:201`, `russianTransliteration[32]` | 128 B static pointer table | Add pointer const for the LCD transliteration variant; keep output buffer writable. |
| `yoRadio/src/audioI2S/AudioEx.h:466`, `codecname[9]` | 36 B per `Audio` object | Use a shared static const table instead of per-instance pointers; preserve getters and all nine names. |
| `yoRadio/src/core/timekeeper.cpp:283`, weather `host` | At most 4 B pointer | Add top-level const or use a const char array; the compiler may already eliminate this pointer. |
| `yoRadio/src/audioI2S/Audio.cpp:1095,1181` and `yoRadio/src/audioVS1053/audioVS1053Ex.cpp:2071`, speech `host`/`path` | 39 B for Google pair; 22 B for Mary pair | These local arrays are read-only inputs to request assembly. Use static const arrays; check client overloads and stack output. The generated request and speech buffers remain mutable. |
| `yoRadio/src/LiquidCrystalI2C/LiquidCrystalI2CEx.cpp:145`, `row_offsets[4]` | 16 B temporary | Static const table; actual benefit depends on optimization. |
| `yoRadio/src/audioI2S/aac_decoder/aac_decoder.cpp:7348`, `limBandsPerOctave[3]` | 12 B temporary | Static const lookup in the optional Helix SBR path; not the production Espressif AAC backend. Existing large Helix tables are already const/PROGMEM. |
| `esp8266/rtos-sdk-native/main/storage_service.c:24`, `paths[13]` | 52 B pointer table | Add pointer const and verify ESP8266 linker placement/access. |
| `esp8266/rtos-sdk-native/main/web_service.c:795,1538,1541,1557`, `required`, `pages`, `assets`, `posts` | 28 + 16 + 28 + 12 B pointer tables | Same top-level-const correction; URI strings and their server copies need separate accounting. |
| `esp8266/rtos-sdk-native/main/web_upload.c:116`, `allowed[11]` | 44 B pointer table | Same correction; test uploads and filename rejection. |
| `esp8266/rtos-sdk-native/components/esp_http_server/src/httpd_trace.c:40`, `trace_format` | Diagnostic-only | Deliberately writable placement avoids LX106 Flash byte-load emulation. Technically immutable text, but a performance-sensitive conditional candidate; benchmark before changing. |
| `yoRadio/src/yoEncoder/yoEncoder.h:44`, `enc_states[16]` | 16 B per encoder | Immutable values, but used by `IRAM_ATTR readEncoder_ISR()`. Consider sharing a DRAM const table first; moving it to Flash requires proving ISR cache availability. |
| Vendored Opus `silk/dec_API.c:451`, `mult_tab[3]` | 12 B temporary | Static const candidate in the ESP8266 source decoder; compare generated code first. The nonconst array in `celt/laplace.c` is test-only and has no production gain. |

The CYD native sources contained no additional large immutable RAM arrays in
this source scan. Shared FLAC candidates and existing normalizer placement are covered above;
their mutable sample buffers are not candidates. Tests, diagnostic fixtures and
historical snapshots were inventoried but are not production optimization targets.

## Suggested order and acceptance checks

1. Start with the **8-byte FLAC pointer cleanup** and **OLED init stack copy**.
   Compare before/after ELF sections and disassembly; do not infer heap gains
   from source array lengths alone.
2. Consider const HTTP route declarations for clarity and startup stack use.
   Treat the borrowed-route API as a separate change with explicit ownership
   tests; stock `httpd_register_uri_handler()` still allocates its copies.
3. Keep the eFuse const correction as an SDK maintenance candidate. Evaluate
   benefit against the public API/generator changes it requires.
4. Resume heap-in-Flash qualification separately if needed. Do not count its
   previous code/data saving again as newly discovered string savings.
5. For any accepted change, run [the relevant tests](ESP32C3_TESTING.md): codec
   transitions including HE/v2/PS, WebUI, OTA rejection/success/recovery, network
   reconnect and heap/CPU load. Retain the deep-sleep wake-stub constraints.

No target frequency, AAC profile, channel count, TLS buffer, stack allocation
or production placement default was reduced in this audit.

## Reproduce the inventory

Use the ESP-IDF Python environment, which includes `pyelftools`, from the
repository checkout. Run against a completed build with its ELF, map,
`project_description.json`, `compile_commands.json` and SDK dependencies present:

```powershell
python tools/esp32c3_tests/flash_constants.py `
  --build idf/esp32c3-oled-native/build-constants-audit `
  --output .build/flash-constants-audit
```

For the recorded build, copy the retained quiet sdkconfig into a separate build
directory and invoke `idf/esp32c3-oled-native/build.ps1` with that directory and
config. Do not run the generated flashing commands. The collector does not
modify sources, configuration or the board. Its outputs are evidence for manual
review, not an automatic const-conversion list. The route-copy JSON and OLED
disassembly additionally retain the manual size/copy checks used here.

Placement rules were cross-checked against the pinned SDK linker fragments and
Espressif's [ESP32-C3 memory types](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/memory-types.html)
and [RAM usage guide](https://docs.espressif.com/projects/esp-idf/en/stable/esp32c3/api-guides/performance/ram-usage.html).
The web links track the current documentation; the saved ELF/config and local
6.0.2 source determine the sizes and candidate decisions in this report.
