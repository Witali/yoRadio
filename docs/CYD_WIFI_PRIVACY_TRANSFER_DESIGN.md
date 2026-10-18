# Native Wi-Fi credential privacy transfer design

Status: source audit and implementation proposal for transfer stage 09. Runtime
and WebUI changes wait until the stage 08 OTA firmware exports are complete.
This document does not report an implemented privacy boundary.

The audit read firmware, tool and test source, and decompressed tracked WebUI
assets in memory. It did not read device files, real `wifi.csv` files, private
backups or NVS, and did not copy credential material into evidence.

## Current entry points and consumers

| Entry point | Current behavior and implication |
| --- | --- |
| [C3 static routing](../idf/esp32c3-oled-native/main/web_service.c#L429) | Maps every `/data/*` URI into `/spiffs`, including credential live, backup and temporary names. Query strings are stripped before opening. `Cache-Control: no-cache` still permits caching. |
| [C3 file opener](../idf/esp32c3-oled-native/main/web_upload.c#L37) | Runs storage recovery before reading. Denied paths must be rejected before this helper, including from asynchronous static workers. |
| [C3 credential loading](../idf/esp32c3-oled-native/main/network_service.c#L66) | Loads up to five profiles. [Saving](../idf/esp32c3-oled-native/main/network_service.c#L389) validates the whole file, publishes atomically, then updates RAM. Preserve that transaction boundary. |
| [C3 form writes](../idf/esp32c3-oled-native/main/web_upload.c#L207) | Accepts explicit single credentials or a plaintext CSV upload, then requests reboot after a successful save. |
| [Shared multipart form](../idf/components/native_storage/include/web_file_form.h#L65) | Implements `ssid`/`pass`, `wifile`, and board-upload `data=wifi.csv`. These are write paths, not a reason to expose raw files for reading. |
| [Shared gzip script](../yoRadio/data/www/script.js.gz) | Decompressed `handleWiFiData` at line 583 copies downloaded passwords into DOM `data-pass`. `submitWiFi` at line 637 substitutes that value for a blank password input, then uploads an entire CSV. `getWiFi` is used during settings/AP initialization. `wifiexport` opens the public CSV URL. |
| [Shared gzip settings page](../yoRadio/data/www/options.html.gz) | Decompressed lines 212–252 contain five credential rows; lines 264–265 provide export and save controls. |
| [C3 embedded script input](../idf/esp32c3-oled-native/main/CMakeLists.txt#L621) | Copies the same shared gzip asset into firmware. Update the tracked asset, its UI fixtures and the embedded firmware together. |
| [CYD static regression](../tests/native/cyd_web_static_test.c#L146) | Already expects `/data/wifi.csv` to be unavailable. Keep that boundary while adding the native API. |
| [OTA preservation tool](../tools/esp32c3_tests/ota.py#L95) | Reads Wi-Fi CSV into memory to compare before/after OTA. It deliberately avoids raw files and credential hashes in reports, but still depends on the public download. |
| [Web-memory tool](../tools/esp32c3_tests/web_memory.py#L172) | Uses that private snapshot and later restores Wi-Fi through CSV import. Its default behavior must migrate with the endpoint. |
| [Wi-Fi asset patch tool](../tools/update_wifi_ssid_warning_web_assets.ps1#L60) | Contains the old `dataset.pass` preservation logic in replacement templates. Update or retire the relevant template so a later asset rebuild cannot restore the leak. |

Blocking only the raw file route is insufficient: the existing UI depends on
the downloaded password to preserve it. A native replacement must change the
read API, edit protocol and UI in the same implementation batch.

## Public metadata and private updates

Provide a bounded `GET /api/native/wifi` response containing a non-secret
revision and ordered profiles with opaque IDs and SSIDs. Do not include a
password, password length, masked suffix, password hash or secret-derived ID.
Responses use `Cache-Control: no-store`. The UI never stores a saved password
in attributes, hidden inputs, application state or local storage.

Use a structured update with an explicit password action:

```json
{
  "revision": "opaque-edit-revision",
  "profiles": [
    {"id": "existing-row-id", "ssid": "Existing network", "password_action": "keep"},
    {"ssid": "New network", "password_action": "set", "password": "newly-entered-value"},
    {"ssid": "Open network", "password_action": "set", "password": ""}
  ]
}
```

`keep` requires an existing ID from the matching revision and an omitted
password field. `set` requires an explicit value; an empty value deliberately
selects an open network. New profiles cannot keep a secret. Reject duplicate
or conflicting action fields, unknown IDs and stale revisions; stale edits
return HTTP 409 without publishing or rebooting. A literal string such as
`********` cannot be the unchanged marker because it can be a real password.

IDs identify rows, not SSIDs, so duplicate SSIDs and reordering cannot cause
the wrong secret to be copied. Resolve kept values only inside the credential
owner, validate the complete resulting configuration, and perform one existing
atomic CSV publication. Publish the new RAM snapshot and edit revision only
after successful durable publication. Serialize metadata snapshots and updates
with the credential owner; a new asynchronous reader must not observe the
intermediate `s_credentials` rebuild.

The decoder needs explicit body, record, field and decoded-string bounds;
accepting an unrestricted JSON tree is unnecessary. Retain existing byte
limits, significant leading/trailing SSID spaces and the edge-space warning.
Specify how legacy non-UTF-8 SSIDs are displayed and preserved before enabling
their edit path; a lossy JSON display must not silently rewrite saved bytes.

## Platform boundaries

The privacy protocol is independent of CPU cores, display controllers, audio
backends and task affinity. It does not require an SDK upgrade or filesystem
format conversion. Existing private CSV storage and recovery can remain.

C3 currently has five-profile selection/fallback and uses 31/63-byte writable
SSID/password limits. Preserve those established limits during this change.
CYD currently advertises `wifi_profiles:false`; reuse suitable storage and API
helpers without claiming C3 profile fallback or enabling a five-row editor on
CYD. Advertise actual runtime capabilities and keep existing explicit
write-only/import behavior where the profile editor is unsupported.

## Static route allowlist

Replace blanket `/data/*` serving with an explicit public file allowlist. The
existing playlist download is a legitimate consumer. Inventory any additional
public data consumer before admitting its path; an internal index, temporary
file or recovery backup does not automatically belong in the allowlist.

Reject credential live/backup/temporary names and all unlisted aliases before
file open, recovery, asynchronous dispatch or response preparation. Test query
strings, method variants, percent encodings, double separators, dot segments,
case variants and suffixes. Exact approved public paths are simpler than a
denylist of known private filenames. The underlying filesystem must not become
a public download API again through gzip or fallback handling.

## UI and import migration

Capability-gate the new native Wi-Fi metadata/update protocol in the shared
gzip UI. Legacy Arduino/ESP8266 consumers of that asset need an explicit
compatibility path; this stage does not silently migrate their firmware.
Native metadata failure disables saving and reports the error. It must never
fall back to downloading the old public credential file.

Replace `dataset.pass` preservation with the typed `keep` action. Make setting
an empty password an explicit open-network action, distinct from leaving a
saved password unchanged. Use relative, same-origin URLs: the current Wi-Fi
download, upload and export strings hardcode `http://`, which is unsuitable
when the native UI is served over HTTPS.

Retain explicit CSV import as replacement of user-supplied credentials. An
imported password is data, not an unchanged marker. Validate the full imported
configuration before publishing, preserve existing transactional recovery, and
clear request-owned secret buffers afterward. A public metadata export may
contain SSIDs only and must not resemble a complete credential backup.

## Explicit private-backup contract

Set a private-export capability to false until a real authorization mechanism
exists. HTTPS authenticating the device to its client does not authorize an
arbitrary LAN client to download saved passwords. Renaming the public CSV URL
or adding a confirmation button does not establish that authorization.

If private export is implemented later, define an authorized maintenance flow
first. Require that authorization on the server, protect against cross-origin
requests, use a bounded coherent credential snapshot, and return an explicit
private attachment with `no-store`. Avoid secrets or bearer tokens in URLs,
browser history, routine logs and reports. Never expose `.tmp` or `.bak` as a
backup mechanism. Default UI and test tooling must not invoke private export
automatically or fall back to it when metadata fails.

## Tool claims and verification

Migrate the default physical OTA/web-memory tools to public profile metadata
and reconnection checks. Rename result fields accordingly: identical SSIDs and
successful reconnection do not prove byte-for-byte password preservation.
Host tests with synthetic credentials can prove exact transaction preservation.
An optional explicitly authorized private snapshot, if later supported, stays
in memory and never produces raw credentials or credential hashes in reports.

Before enabling the new API, qualify:

- Actual C3/CYD route handling rejects private names before any opener or
  recovery side effect; public assets and playlist export still work.
- Actual store/update functions preserve kept secrets across edits, reordering
  and duplicate SSIDs; set/open/delete/new-row/stale-revision cases behave as
  specified. Test UTF-8, byte boundaries, spaces and legacy encoding policy.
- Inject write, flush, close, publication and rollback failures. Unsuccessful
  updates leave the live file and RAM snapshot unchanged and request no reboot.
- Decompress and execute the tracked gzip UI in DOM fixtures. A synthetic old
  secret must be absent from requests, responses, attributes, logs and exports;
  blank unchanged inputs produce `keep`, and API errors do not enable fallback.
- Exercise actual HTTPD/parser/session code over HTTP and verified TLS for
  metadata, allowlist rejection and bounded updates. Check cache headers,
  malformed/duplicate fields, request limits and cleanup.
- Include semantic negative controls for the former public CSV route and the
  old `dataset.pass` protocol. Do not use real credentials as test canaries.

These are implementation gates, not claims of completed runtime privacy or
authentication support.
