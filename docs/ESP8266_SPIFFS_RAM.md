# ESP8266 SPIFFS RAM bound

The native mount uses `max_files = 5`: four audited simultaneous handles and
one spare. This does not change filesystem capacity, file size, cache policy,
audio formats, task stacks, or the codec's 4096-byte free-heap reserve.

The ESP8266 RTOS SDK allocates both its descriptor table and its cache at mount
time. In the current target objects, `sizeof(spiffs_fd) = 48`,
`sizeof(spiffs_cache_page) = 20`, `sizeof(spiffs_cache) = 20`, and the configured
page size is 256. These allocations therefore total `20 + 324 * max_files`:
3260 bytes for ten slots, 1640 bytes for five, saving **1620 DRAM bytes**.
The two allocation headers, 512-byte work buffer, and filesystem object remain
unchanged. Evidence: `esp_spiffs_init` in the board-bench `esp_spiffs.c.obj`,
offsets `+0x150..0x15d` (48-byte multiplier) and `+0x182..0x18f` (cache size).

## Simultaneous handles

- App task: playlist lookup holds index + CSV (2); its log writer instead holds
  one file. These operations are sequential on that task.
- Single HTTP task: static asset, CSV, log download, or active upload holds one
  file. Playlist installation/index rebuilding/cache creation can hold two,
  but the playlist mutex excludes the app's two-handle lookup. Upload closes
  the received file before validation/publication; cache checksum closes its
  input before checking/building the cache.
- Wi-Fi event task: credential lookup can independently hold one file.
- SDK `SPIFFS_rename` and `SPIFFS_remove` temporarily acquire an internal
  descriptor. Replacement/rebuild/cache paths close their input/output files
  first; these transient handles do not raise the four-handle bound. `stat`
  and `SPIFFS_info` do not allocate descriptors.

Thus app playlist (2) + HTTP file (1) + Wi-Fi (1), or HTTP playlist/cache (2)
+ app logger (1) + Wi-Fi (1), reaches four, including optional diagnostic
logging. Atomic replacement uses stat/rename/remove, not another persistent
FILE. Settings use NVS, OTA writes raw partitions, and normal audio uses TCP:
none consumes a SPIFFS handle. Startup playlist work precedes Wi-Fi/HTTP.

This is a bound for successful close/normal error cleanup, not a claim that a
corrupt filesystem leaking SDK handles remains usable. Keep the spare slot;
re-audit before adding independent file workers or nested file operations.
