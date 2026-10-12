# Small_TV stock firmware security audit

Static review on 2026-10-12 of the owner's verified 4 MiB snapshot:

```text
SHA-256: 5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4
```

## Result and scope

No clear evidence of intentionally malicious behavior was found in the
reviewed application paths. The identified network behavior implements
weather retrieval, time synchronization, local configuration and the
setup captive portal. No reviewed path sends the configured Wi-Fi
password to an external server, receives executable commands from a
remote control server, or installs a downloaded application image.

The firmware does have security defects: unauthenticated local management,
an open setup access point, plaintext weather requests, and unsafe input
length handling. These are vulnerabilities, not evidence of deliberate
malware. Successful exploitation or arbitrary code execution has not
been demonstrated.

This is not a proof that the entire binary is harmless. The review used
Ghidra 12.0.4, RISC-V disassembly, address references and the matching
ESP-IDF v5.5.4 headers. It concentrated on application initialization,
outbound network configuration, all 34 registered HTTP handlers, and
flash writes. It did not exhaustively verify SDK/library code, ROM,
bootloader behavior, indirect calls, or image decoders. No live traffic
capture, firmware execution, fuzzing, network requests to the device,
reset or flashing was performed. Image checksums establish consistency
of our dump; they do not authenticate the firmware publisher.

## Identified network behavior

| Component | Behavior | Code evidence (runtime addresses) |
| --- | --- | --- |
| Weather client | HTTP GET to `api.openweathermap.org/data/2.5/weather`, query fields `q=<city>,<country>&appid=<key>` | `0x42010864`, URL reference at `0x4201094C`, client initialization at `0x42010982` |
| Time synchronization | SNTP servers `ntp1.aliyun.com`, configured NTP server (default `pool.ntp.org`; empty-field fallback `cn.pool.ntp.org`), and `pool.ntp.org` | `0x42010A06` |
| Local management | HTTP server on TCP port 80, 34 registered GET/POST routes | Server startup `0x4200FA88`, handlers in `registered-routes.tsv` |
| Setup DNS | UDP port 53, answers queries with `192.168.43.1`, TTL 60 seconds | `0x4200C74E`; socket creation `0x4200C77A`, response `0x4200C950` |
| Captive portal | HTTP 404 handler redirects nonmatching Host headers to `http://192.168.43.1/` | `0x4200D4BE` |

The DNS task is started by setup-mode initialization at `0x4200D06E`.
Its fixed local answer is consistent with a captive portal; it is not an
identified external command channel.

The embedded page's `https://ezgif.com/` link opens a browser-based image
converter. It is not a request issued by the ESP32 application. W3C URLs
are SVG namespaces. `user@example.com` is a literal `From` request header
in the weather client's redirect event callback (`0x4200FCCC`), not a
mail delivery destination. Generic authorization, TLS and OTA strings
from linked SDK code do not establish that those features are enabled.

Direct references to `esp_http_client_init` identify the weather client.
Direct references to `lwip_socket` identify the captive DNS server and
SDK HTTP server/control and socket transport code. This reference search
does not cover every indirect call or lwIP raw-UDP path.

## Confirmed security findings

### 1. Local management has no application authentication

The registered handlers do not check a session, password, authorization
header or anti-CSRF token before changing state. The HTTP configuration
has port 80 and null transport context, `open_fn` and URI matching
callbacks; it starts the ordinary HTTP server. For example,
`POST /restart` (`0x4200D34A`) immediately schedules a restart after sending
its response. `/configure` changes Wi-Fi credentials, `/advancedset`
changes the NTP server and weather API key, and the upload handlers erase
and write image storage. `/wifireset` updates connection settings and
schedules a restart. `/getsettings` returns display preferences, not the
Wi-Fi password.

The server is started in both station and setup modes. A client that can
reach its HTTP port can use these management functions. Network isolation
or access-point protection may limit reachability, but the handlers
themselves do not authenticate the client.

Setup AP configuration (`0x4200CE9E`) clears `wifi_config_t`, sets SSID
`Small_TV`, leaves the password empty, and sets `authmode` to 0
(`WIFI_AUTH_OPEN`). The setup network consequently adds no Wi-Fi password
barrier. This is distinct from the password used to join the owner's
normal Wi-Fi network.

### 2. Weather requests expose query data over plaintext HTTP

The URL is built with `http://`, including the configured city/country
and API key. Network parties on the request path can observe or modify
the exchange. There is no TLS certificate validation for this request.
The transmitted query contains weather configuration; no configured
Wi-Fi password or SSID is included in this reviewed request builder.

### 3. Captive DNS response crosses its stack buffer boundary

At `0x4200C838`, the receive limit is 127 bytes. The received query is
copied into a response region beginning at `sp + 48`; the input region
begins at `sp + 176`, giving the response region 128 bytes. The code then
appends a 16-byte DNS answer without checking that the query leaves room
for it, and sends `received_length + 16` bytes (`0x4200C948`). For lengths
above 112, writes cross into the adjacent input region; at the maximum,
the response length is 143 bytes.

The confirmed overwrite is into the adjacent receive buffer, not the
saved return address. This audit does not claim a demonstrated code
execution exploit or an inevitable crash. Very short packets are also
not checked against the full DNS header size before header fields are
read and written. This implementation needs proper packet validation
and a response-size check.

### 4. Image transfer lengths can overlap unrelated RAM state

`POST /start_upload` validates image numbers 1..5 and declared sizes up
to `0x19000` (100 KiB). The normal flash destination is one of the five
image slots. However, `/upload_chunk` checks only
`uploaded_bytes + request.content_len <= 0x19000` before passing the
untrusted content length to `httpd_req_recv` with destination
`0x3FCBD2EC` (`0x4200DCCE`..`0x4200DCDA`). There is no separate receive
buffer capacity check.

Other live globals occupy addresses shortly after that destination:
temporary Wi-Fi password data at `0x3FCBFEEC` (offset `0x2C00`) and the
timer handle at `0x3FCC39D0` (offset `0x66E4`), both far below the accepted
100 KiB limit. Thus an accepted sufficiently large read can overwrite
unrelated application state. The original buffer declaration is not
available; no exact source-level array size is asserted.

`GET /get_Photo_File` (`0x4200E11C`) also reads caller-sized image chunks
into the same destination without a distinct buffer capacity check.
Flash read/write return values are not checked in these application
helpers. Several simple settings handlers additionally dereference
`strstr` results without checking for a missing field; examples include
`/setclocktype` and `/setgifvalue`. Malformed or oversized requests may
disrupt operation or corrupt memory. No exploit was sent to the device.

## Flash changes and update functionality

The reviewed flash-write callers implement settings persistence,
multipart image uploads, JPEG output, and SDK storage. Settings persistence
at `0x42008A00` erases one sector at flash `0x3E7000` and writes a
`0x1BC`-byte settings structure. That structure includes Wi-Fi and weather
configuration without application encryption. In this captured snapshot,
the entire sector is erased (`0xFF`); no saved owner credentials were
extracted from it.

No `/update` route is among the 34 registered handlers. An update link in
embedded HTML is commented out. The partition table contains one factory
application and no OTA data/slot partitions. The identified reference to
`esp_ota_get_running_partition` from `0x4207BC60` implements an SDK flash
write/erase protection range check; it is not a discovered downloader.
These observations support the reviewed upload path being image storage,
but they do not prove every possible firmware-write path is absent.

## Practical use

Treat the stock firmware as a device for a trusted or isolated network.
Restrict access to its HTTP port, avoid forwarding that port to the
Internet, and disable Internet access if weather/NTP are unnecessary.
Replacing it with reviewed firmware would permit authentication,
encrypted requests and proper input bounds to be implemented. The dump
was preserved unchanged; no remediation was installed on the device.

## Evidence and reproduction

- [C-like decompilation](security-decompiled.c): 56 selected functions,
  including all registered handlers. This is analysis output, not the
  original source; unknown names/types and inferred array boundaries
  remain visible.
- [Machine instructions](security-disassembly.txt): DNS, transfer,
  restart and server registration paths, from the reconstructed ELF
  whose code bytes match the saved image.
- [Registered routes](registered-routes.tsv): descriptor, HTTP method,
  URI and handler. Method numbers are 1=GET and 3=POST in the linked
  HTTP parser enumeration.
- [Address references](security-references.tsv): selected network,
  settings and flash API references, plus direct callers.
- [Configuration values](security-configuration.json): decoded server
  configuration and erased-settings-sector check for this snapshot.
- [ExportSecurity.java](../ExportSecurity.java): Ghidra exporter. Prepare
  the input with [prepare_analysis.py](../prepare_analysis.py), complete
  headless analysis, run [ExportDisplay.java](../ExportDisplay.java), then
  run `ExportSecurity.java <output-directory>`.

The exports contain field names and addresses, not saved credential
values. Some references printed as `gp + offset` depend on Ghidra's
global-pointer analysis and should be checked against the instruction
listing before further conclusions are drawn.

The SDK interpretation was checked against local ESP-IDF v5.5.4 headers,
particularly `esp_http_server.h`, `esp_http_client.h` and `esp_wifi_types.h`.
Primary documentation: [Espressif HTTP Server](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32c2/api-reference/protocols/esp_http_server.html)
and [partition tables](https://docs.espressif.com/projects/esp-idf/en/v5.4.3/esp32c2/api-guides/partition-tables.html).
