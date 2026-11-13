# Wi-Fi station and peer lifetime

The ESP32-C2 driver keeps the station and its owned peer across an ordinary
association cancellation or link loss. It clears the active peer reference.
Stopping the station role clears its global pointer, then frees the owned
peer and station. These paths use the SDK in both firmware images.

## Object layout and call sites

Addresses in the native column are for app `88927726d740…` and ELF
`3bf88f53f318…`. Factory ELF is `8c9fd166a653…`.

| Role or boundary | Factory | Native |
| --- | --- | --- |
| `g_ic + 16`, published station pointer | `0x3fcc291c` | `0x3fcb5534` |
| `wifi_create_sta`, allocates 536 bytes and publishes the station | `0x42070a14` / store `0x42070a5e` | `0x42075664` / store `0x420756ac` |
| Owned peer at `station + 232`, with `peer + 0` pointing back to the station | 952 bytes / stores `0x42070a7e`, `0x42070ace` | 976 bytes / stores `0x420756cc`, `0x42075716` |
| `cnx_bss_alloc`, selects one of four slots starting at `g_cnxMgr + 8` | `0x4206b542`, stride 952 | `0x4206fb74`, stride 976 |
| `ieee80211_mlme_connect_bss`, publishes active peer at `station + 228` | `0x4206fdea` / store `0x4206fe00` | `0x42074a42` / store `0x42074a58` |
| `cnx_sta_leave`, clears the active reference inside the Wi-Fi global mutex | `0x4206c1ae` / store `0x4206c3fa` | `0x42070de8` / store `0x42071012` |
| `wifi_destroy_sta`, clears the global station pointer inside the mutex | `0x4207078c` / store `0x420707d4` | `0x420753f2` / store `0x4207543a` |
| `wifi_destroy_sta`, frees owned peer then station after unlocking | `0x420707e8`, `0x420707f4` | `0x4207544e`, `0x4207545a` |

The matching script checks the full RV32 bodies in each linked image against
the corresponding `libnet80211.a`, including the changed branch targets and
relocations. The checked call chains include
`wifi_start_process → wifi_mode_set → wifi_create_sta`,
`wifi_stop_process → wifi_destroy_sta`,
`wifi_disconnect_process → ieee80211_sta_disconnect → ieee80211_sta_new_state → cnx_sta_leave`
and `cnx_connect_to_bss → cnx_connect_op → ieee80211_mlme_connect_bss`.
The audit decodes the callback passed in `a1` to `chm_acquire_lock` and
in `a3` to `chm_start_op`. Both resolve to `cnx_connect_op` at
`0x420699cc` in factory and `0x4206e554` in native.
The four cached BSS slots are embedded in the connection manager.
`cnx_bss_alloc` can call `cnx_remove_rc` to recycle one.

The create body registers driver receive and MIC failure callbacks. The
matched relocation bindings give the factory targets `0x4038e1c0` and
`0x4206d5f4`, and the native targets `0x420d0b42` and `0x420722dc`.
The destroy body clears the receive callback for the station role.

The native disconnect path also cancels a pending channel-switch connection
through `cnx_csa_cancel_pending_connect` at `0x4206edae`. Its zero-state
branch calls `cnx_remove_all_rc` at `0x4206f796` to reset the BSS cache.
These calls are visible in the matched native body. The QEMU scenarios
exercise the active-peer clear and do not establish execution of every
disconnect branch.

The initialized OSI tables resolve offsets 84/88 to mutex lock/unlock,
176 to free and 372 to zero-initialized allocation. The factory entries are
`0x40383d7e`, `0x40383d70`, `0x4038e4da`, `0x40383d00`. The native
entries are `0x4038399a`, `0x40383992`, `0x40387170`, `0x4038395e`.
The QEMU observer also checks the actual allocation and free targets in
`a5` at the indirect calls.

## Observed paths

The native guest booted from a disposable flash copy with synthetic settings.
The observer read only bounded pointer fields and registers and used hardware
breakpoints at checked instruction addresses.

- At the first active-peer publication, the test disabled the virtual AP.
  The clear breakpoint fired before `cnx_sta_associated`. The attempted
  peer was a scan-cache slot. Its active reference became null, while the
  station, owned peer and backpointer retained their values. Bringing the AP
  back allowed a new publication and HTTP 200.
- After an established connection, a second AP outage cleared the active
  reference again. The station and owned peer survived. The retry published a
  scan-cache slot and HTTP resumed.
- A real `POST /restart` returned HTTP 200. The SDK entered
  `wifi_destroy_sta` with the active reference already null. The test
  observed both free calls and their returns after the global station pointer
  became null. The next boot reached a new station allocation, then served
  HTTP again.

The earlier native image `564ea463fc98…` also passed the connected
disconnect/reconnect scenario. The factory column is a static SDK match.
The live tests cover the named paths in QEMU. Concurrent consumers and
physical RF are outside those observations.

## Allocation failure

Both linked bodies return `0x101` if the first allocation fails, without
publishing a station. If the second allocation fails, both have already
published `g_ic + 16`. They store the null owned-peer pointer, free the
station, clear `g_ic + 16` and return `0x101`.

The second failure branch is `0x42070aa8 → 0x42070b1c` in factory and
`0x420756f0 → 0x42075754` in native. The free and clear sites are
`0x42070b26/0x42070b2c` and `0x4207575e/0x42075764`, respectively.
There is an interval between free and clear. Establishing whether any
concurrent consumer can reach the stale pointer requires a separate test.

Eight isolated RV32 cases execute the matched SDK bodies with synthetic
allocation and mutex backends. They cover both allocation failures, reuse of
an existing station and creation followed by destruction in each image.

## Reproduction

Run [audit_station_lifetime.py](../tools/audit_station_lifetime.py) with the
same `--factory-elf`, `--native-elf`, `--app`, `--factory-net` and
`--native-net` inputs as the [entrypoint audit](../reference/BEHAVIOR_GAPS.md),
plus a new `--output` JSON path. It requires `pyelftools`.

[replay_station_lifetime.py](../tools/replay_station_lifetime.py) takes the
same ELF/app files, the resulting `--station-audit` JSON and a new
`--output` path. It also requires `unicorn`.

Run [station_lifetime_qemu.py](station_lifetime_qemu.py) with `--repo`,
`--dependency-root`, `--qemu-tools`, `--qemu`, `--elf`, `--artifact-root`
and a new `--output` directory. Use `--cancel-association --observe-restart`
for all three scenarios. The artifact root must expose the candidate
archive under `firmware/development/small-tv-esp32c2-reconstructed`, the
directory name expected by the frozen QEMU launcher. For the advancedset build,
copy its archived files to that relative path in a disposable fixture root.
