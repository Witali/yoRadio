# Bounded WebUI transfers and deferred reboot

Step 1 of the [memory reservation plan](ESP32C3_MEMORY_RESERVATION_PLAN_20261013.md).
This experiment changes WebUI memory lifetimes, not decoder formats or PCM.

## Final buffer policy

| Operation | Storage | Lifetime |
|---|---|---|
| Download files to browser | 2,048 bytes per static worker; two workers | Worker stacks allocated at startup; unchanged 4,096-byte stacks |
| Upload files into SPIFFS | One 2,048-byte write buffer, reused across form files | Allocate before opening the first temporary file; free after reception, before publication |
| Receive multipart bytes | 256-byte receive chunk and bounded parser/form | Existing 8,192-byte HTTP task stack |
| OTA application update | Existing 4,096-byte staging buffer in OTA context | Existing per-request allocation; direct OTA partition writes, no SPIFFS |
| Delayed reboot | Existing WebSocket status task | No new reboot task/stack allocated at request completion |

The final choice follows the user's refinement: rare SPIFFS uploads do not need
a permanent payload reserve. Downloads stay at 2 KiB per worker. Earlier 4 KiB
upload/download variants are retained as experiments, not recommended defaults.

Whole HTTP upload bodies are no longer allocated. At the 98,304-byte request
limit, the former allocation was 98,305 bytes; the new staging allocation is
2,048 bytes: **96,257 fewer transient heap bytes (about 94 KiB)**. This is a
calculation for that allocation only, not a measurement of all network or file
system allocations. Parser/form state uses the already-reserved HTTP stack.

Wi-Fi CSV is separately bounded to 799 bytes and validated before publication.
All multipart file data is staged before the form is accepted. Up to 16 files
fit the bounded manifest (the recovery UI's standard assets and data files fit).
Truncation, invalid fields, duplicate destinations and allocation/write failure
do not publish incomplete files. A storage error during publication of an
otherwise valid multi-file form can still leave earlier files published; this
is not a power-loss-atomic multi-file transaction. Unlike the old recovery
handler, uploading one asset no longer deletes unrelated WebUI assets.

The sink uses POSIX `write()` to avoid another libc payload buffer splitting
the explicitly accumulated chunks. `fsync()`/`close()` run at file completion,
not after every network chunk. The final partial chunk is written as-is.
Underlying HTTP, filesystem and network metadata allocations still exist.

## How this SPIFFS writes Flash

Audited SDK: ESP-IDF `9a97f6c54ec638111ce55cd36581b3c192f15207`;
SPIFFS submodule `ad902cadceb39d0825a97e25ecb5867641f606ba`.
The production configuration has 256-byte logical pages, 32-byte object-name
storage, write caching enabled, and a 256 KiB SPIFFS partition.

- `SPIFFS_write()` can cache writes smaller than a logical page when direct
  mode is not set. Large calls flush any pending cache and enter the write path.
- `spiffs_hydro_write()` distinguishes replacing existing bytes from appending.
- `spiffs_object_append()` allocates a new data page at a page boundary, or
  programs the unused tail of an existing page. It does **not** erase and
  rewrite an entire 4 KiB sector for every sequential append.
- Appends also update the file's index and size. Existing-data modification
  uses page replacement; old pages become reclaimable. Neither behavior implies
  a sector-sized read/modify/erase/write on every application call.
- Garbage collection relocates live pages when needed and erases reclaimable
  blocks. It can be slow near capacity. The 4 KiB erase size does not mean a
  4 KiB application buffer maps to one sector: pages contain metadata and files
  need not occupy contiguous physical addresses.

Primary references: pinned
[write/cache dispatch](https://github.com/pellepl/spiffs/blob/ad902cadceb39d0825a97e25ecb5867641f606ba/src/spiffs_hydrogen.c#L435),
[append/modify logic](https://github.com/pellepl/spiffs/blob/ad902cadceb39d0825a97e25ecb5867641f606ba/src/spiffs_nucleus.c#L1224),
[garbage collection](https://github.com/pellepl/spiffs/blob/ad902cadceb39d0825a97e25ecb5867641f606ba/src/spiffs_gc.c#L109), and
[Espressif SPIFFS documentation](https://docs.espressif.com/projects/esp-idf/en/v6.1/esp32c3/api-reference/storage/spiffs.html).

Thus a 2 KiB staging buffer can reduce API calls and metadata work without
reserving a sector-sized buffer. This experiment does **not** count physical
program/erase operations or claim a measured endurance improvement.

## Validation and reproduction

Host tests compile the actual multipart parser and form callback under
AddressSanitizer/UndefinedBehaviorSanitizer. The POSIX sink is extracted verbatim
from `web_upload.c` and compiled with allocator/IO mocks. Tests cover arbitrary
TCP splits, a binary 90 KiB payload, incomplete forms, duplicate files, credential
bounds, the 16-file bound, exactly 2 KiB write calls plus the final tail, buffer
reuse, allocation failure, write failure and sync failure.

```powershell
python -B -X utf8 tests/run-esp32c3-web-memory.py
node --test tests/esp32c3-native-idf.test.js tests/esp32c3-web-static-workers.test.js tests/webui-firmware-ota.test.js
```

The physical runner is `tools/esp32c3_tests/web_memory.py`. It performs app-only
OTA, retains original files/settings only in RAM, compares exact downloaded
bytes, and restores the original app and files. It requires playback stopped
initially. Pass explicit `--board`, `--host`, `--baseline`, `--candidate`,
`--restore` firmware paths and a new `--output` directory. Credentials, station
names, URLs and original-file hashes must not be added to reports.

### Initial failure retained

The first 4 KiB download experiment added a diagnostic route without increasing
the HTTP handler-table capacity. The final wildcard route could not register;
downloads returned 404. It also exposed only 264 bytes of HTTP stack high-water
margin with the large stack staging buffer. This was not a passed firmware.
The route count was corrected, manifest names now match SPIFFS's configured
bound, and the final upload buffer is temporary heap storage. Original firmware
was restored via OTA after the failed runner could not verify files through the
missing wildcard route. Preserve this failed trial alongside the corrected run.

### Results

Implementation commit: `0abc0b64`; corrected physical controller: `50b5863`.
Final image: `idf61-web-upload2k`, 1,458,672 bytes, ELF SHA-256
`613d5d04ba8b3e48d87b61b59120a10a68839961f42daef2ec3f25c9fd9c4ef6`.
The image was built before the implementation commit, from the same source.
See its [manifest](../firmware/development/esp32c3-idf-6.1-r9a97-web-upload2k/manifest.json)
and [frozen evidence](../tests/results/esp32c3-web-memory-20261013/).

| Measurement | Baseline | Final candidate |
|---|---:|---:|
| Upload payload 57,904 bytes | HTTP 500 | HTTP 200, exact bytes |
| Upload payload 65,536 bytes | HTTP 500 | HTTP 200, exact bytes |
| Upload payload 96,000 bytes | HTTP 500 | HTTP 200, exact bytes |
| Boot/session minimum heap after those uploads | 22,256 bytes | 105,332 bytes |
| Minimum observed free HTTP stack during upload cases | Not instrumented | 3,296 bytes of 8,192 |
| Minimum observed free static-worker stack | Not instrumented | 424 bytes of 4,096 |
| Permanent upload payload reserve | None | None |

Heap minima include earlier operations in each boot/session; they are not
isolated allocation measurements. Baseline uploads recorded no allocation
failures, so their HTTP 500 responses must not be labelled proven heap OOM.
Filesystem failure attribution needs separate instrumentation.

Linker sections changed by +8 bytes in `.dram0.bss`, zero in `.dram0.data`,
and +70 bytes in `.iram0.text`. The IRAM text-end padding shrank by 70 bytes,
so this did not enlarge the combined IRAM allocation. The app image grew
by 2,528 bytes. HTTP and download-worker stack allocations stayed unchanged.
The compiler reports a 2,672-byte `handle_upload` frame. Reboot requests no
longer allocate the old 2,048-byte task stack plus its task/allocator overhead.

Validation completed:

- Three native C suites passed with ASan/UBSan; 55 JavaScript tests passed.
- Parallel downloads (three at a time, twelve requests) returned exact bytes.
- Truncated/disconnected uploads, duplicate assets and invalid Wi-Fi forms
  were rejected without publishing incomplete files.
- Recovery multipart upload, Wi-Fi upload/reboot and WebSocket reboot passed.
- Corrupt OTA was rejected; valid app-only OTA round trips passed.
- HE-AAC and FLAC 48 kHz stereo playback with concurrent downloads passed on
  both baseline and candidate. During each short active playback window there
  were no increments in completion-queue drops, output write errors,
  allocation failures or task-watchdog events. Idle cumulative queue-drop
  counters are not evidence of playback loss.

`physical-02` retains two test-harness problems: its FLAC URL used the server's
AAC-only `/stream/` route (HTTP 400 before audio delivery), and its empty-body
oversize request expected HTTP 400 although the HTTP server returned 408.
`physical-03` retested the same candidate image with the corrected controller:
FLAC uses `/file/flac-level8`; an oversize request with a body byte returns 400;
a header-only oversize request may return 408. All four targeted cases passed.
The original failures remain in the evidence, not rewritten as successes.

Both completed runs verified restoration of the original
`idf61-production-prefill1000` image, Wi-Fi, playlist, settings and assets.
Playback is stopped, matching the initial state. No private settings or their
hashes are retained in the evidence. The first failed run required manual OTA
restoration; its original RAM snapshot verification did not complete.

This is focused local-HTTP/WebUI/OTA validation. It is not full production
qualification, a long-duration audio test, a PCM quality comparison, or a new
shared-arena/HE-AAC-over-HTTPS memory qualification. Later plan steps remain.

### Stream identification is separate from the test URL

`audio_service.c` already recognizes `fLaC`, `OggS`, and AAC/MP3 sync patterns.
Currently explicit codec selection takes precedence, then HTTP Content-Type;
signature detection is only a fallback on the first received audio fragment.
Unknown data defaults to MP3, and `ID3` is treated as MP3 rather than skipped
before identifying the actual audio. These are limitations, not guarantees of
robust detection. Future work should accumulate split headers, validate frame
fields, skip bounded tags, identify the codec within Ogg, and reject unknown
data explicitly. No detector behavior was changed in this WebUI memory work.
Detection cannot repair an HTTP 400 response containing no audio bytes.
