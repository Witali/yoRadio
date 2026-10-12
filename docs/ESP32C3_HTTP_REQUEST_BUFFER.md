# Releasing the completed HTTP request buffer

## Design and ownership audit

Experimental build key: `CONFIG_YORADIO_HTTP_RELEASE_REQUEST_BUFFER=y`.
It is **off by default**. This saves the configured HTTP request/header buffer
(4,096 bytes), not a TLS record buffer or an audio packet. Full AAC/SBR/PS,
decoded precision and the original request capacity are unchanged.

Audited SDK: ESP-IDF revision `9a97f6c54ec638111ce55cd36581b3c192f15207`.
Normalized UTF-8/LF SHA-256 of `components/esp_http_client/esp_http_client.c`:
`152d658025205b1d0d090127a6d56d24726118c488d7d5bf5f85a98a15e87740`.
The generator rejects other source content. CMake replaces exactly one source
in the experimental build; the shared SDK and other projects are not modified.

All uses of `request->buffer` in that source were reviewed before adding release:

| Owner / function | Existing use | Rule after this change |
|---|---|---|
| `esp_http_client_init` | Allocates descriptor and full TX data | Unchanged; setup capacity stays available |
| `http_client_prepare_first_line` | Writes method, URL/query and HTTP version | Called only after full-capacity storage is present |
| `esp_http_client_request_send` | Header pagination and partial-send retries | Reallocates missing storage before a fresh request; retains in-progress storage |
| `esp_http_client_prepare` / perform reuse path | Resets first-line bookkeeping | Compatible with a fresh full-capacity allocation |
| `esp_http_client_send_post_data` / `esp_http_client_write` | Sends caller-owned body, separate from request header storage | Release rejects non-GET/body/async cases; these paths are unchanged |
| `esp_http_client_fetch_headers` / `esp_http_client_read` / parser callbacks | Uses response buffer and cached response data | No ownership change; no alias to freed request data |
| `esp_http_client_cleanup` | Frees request data and descriptor | The cleared pointer makes cleanup safe after release |

The added release API accepts only a synchronous GET with no body or pending
write, in `HTTP_STATE_RES_ON_DATA_START`. The stream task calls it only after
`open_stream` has accepted final 2xx headers; redirects have already completed.
Rejected states retain the buffer. Release is idempotent and clears the data
pointer and first-line flag. No numeric struct offsets or private layout copies
are used: the extension compiles inside the pinned SDK source.

Future requests allocate the original `buffer_size_tx`, preserving long request
lines and header pagination. Allocation failure returns `ESP_ERR_NO_MEM` without
writing or dereferencing NULL; stale `errno=EAGAIN` is cleared. An inconsistent
missing buffer with a prepared first line fails instead of discarding pending
request state. The application does not share the HTTP handle between tasks.

## Host verification

`tests/test-http-request-buffer.py --idf <SDK> --output <new-directory>` compiles
the actual patched SDK first-line/request sender and real SDK header/utilities
with ASan/UBSan. The transport and response-state transitions are scripted;
this is not a TLS integration test or a physical heap measurement.

36 cases passed, covering a 3,001-byte path, more than 8 KiB of paginated request
headers, partial writes, 20 identical repeated requests, double release,
reallocation failure and recovery, early release rejection, body/POST/async
rejection, transport failure and async leftover ownership. The allocator
records a 4,096-byte release and equal allocation/free counts. Unknown SDK
content is rejected; LF/CRLF normalization yields the same patch.

## Qualification

The quiet ESP-IDF 6.1 candidate builds successfully. Its only active configuration
change from `idf61-production-prefill1000` is this experimental key. Build/link
checks confirm unchanged contents for 18 codec objects (119 text/rodata sections),
the same public certificate bundle, and an application that fits the OTA slot.
These checks do not establish physical playback or HTTP lifecycle correctness.

This feature remains experimental until physical comparison, all-codec and
HTTP lifecycle regression, and OTA checks pass. A 4,096-byte freed allocation
does not promise a 4,096-byte increase in the largest free block: allocator
coalescing and subsequent network/decoder allocations determine that result.
No production default is changed by this experiment.

## Physical comparison, 2026-10-12

Application-only OTA compared the installed `idf61-production-prefill1000`
with `idf61-quiet-http-txrelease`. Each case ran for 60 seconds; steady-state
checks exclude the first 15 seconds. The local HE-AAC fixture is identical in
both cases, paced at 1x. The public HTTPS source is a live 64-kbit/s HE-AAC
station; FFprobe and FAAD independently check its format. All cases below
reported 44.1 kHz stereo without reducing AAC profile support or precision.

| Firmware / transport | Minimum free heap | Minimum largest block | Memory gate | Completion queue drops / write errors |
|---|---:|---:|---|---:|
| Installed baseline / local HTTP | 33,064 B | 19,456 B | PASS | 0 / 0 |
| Installed baseline / public HTTPS | 20,412 B | 7,424 B | FAIL: largest block below 8,192 B | 0 / 0 |
| Request-buffer release / local HTTP | 38,052 B | 24,576 B | PASS | 0 / 0 |
| Request-buffer release / public HTTPS | 24,848 B | 10,752 B | PASS | 0 / 0 |
| Rebooted baseline control / local HTTP | 33,808 B | 20,480 B | PASS | 0 / 0 |
| Rebooted baseline control / public HTTPS | 20,676 B | 6,656 B | FAIL: largest block below 8,192 B | 0 / 0 |

All six cases passed format and steady observation-transport checks, with
zero recorded allocation failures, watchdog events or unexpected reboots.
The failed baseline memory gate is a reserve threshold, not an observed OOM.
These output counters do not establish analog continuity or audible quality.

The observed minimum-free-heap increases are 4,988 B locally and 4,436 B over
public HTTPS. They are not exact causal measurements of the freed allocation:
the initial baseline had a longer session history, the candidate rebooted
during OTA, and live program/network traffic differs between sequential cases.
The host allocator test establishes the specific 4,096-byte release.

After restoring/rebooting production, the same two cases were repeated to
control for the candidate's fresh boot. Compared with this baseline, candidate
minimum free heap increased by 4,244 B locally and 4,172 B over HTTPS; local
median free heap increased by exactly 4,244 B (36,060 to 40,304 B). HTTPS largest
block increased from 6,656 to 10,752 B. This supports a useful approximately
4-KiB gain after accounting for reboot, while remaining a short sequential
comparison with different live audio and allocation histories. The baseline
still failed the HTTPS reserve threshold after reboot; the candidate passed.

Two earlier attempts were incomplete due to 5-second WebUI TCP-connect timeouts
on the baseline: one during local playback, one before playback while stopped.
Neither installed the candidate; original firmware/settings/station restoration
was verified for both. The subsequent observation controller retains transport
errors as failed checks while continuing bounded collection; acceptance limits
and request timeouts are unchanged. The completed four-case campaign had no
such errors inside its playback windows. These repeats do not resolve the
earlier intermittent WebUI connection failure.

The candidate application is 1,456,160 bytes, 224 bytes larger than baseline.
Application SHA-256:
`ee0278e97d9b0d4abd1e217ec2e657896e6e562ba51f5638aeb431e1acfdbebc`.
Production application, selected station and settings were restored and verified
after the comparison. Source snapshots, build/link audits, host tests, raw
observations and independent replay are retained in the
[evidence archive](../tests/results/esp32c3-http-request-buffer/).

At this stage, codec/HTTP lifecycle regression, OTA rejection/recovery and
longer HTTPS playback were pending. The following sections record those
follow-ups. This initial comparison alone did not qualify production as a whole.

## Codec and HTTP regression, 2026-10-12

The same candidate binary was installed temporarily for 33 checks. Eleven
finite fixtures cover MP3 320 kbit/s, FLAC level 8, Vorbis q10, Opus 510 kbit/s,
AAC-LC 320 kbit/s, LC at 22.05/44.1/48 kHz, HE-AAC at 44.1/48 kHz, and
HE-AACv2 at 44.1 kHz. Each runs with automatic and explicit codec selection.
Positive file cases check native PCM rate/channels/profile, sampled output
counters and memory, stable EOF with cleared PCM fields, and the WebSocket
terminal state. These are transport/runtime tests, not fresh PCM precision tests.

| Group | Result |
|---|---:|
| File format / output / memory / EOF / WebSocket terminal state | 21/22 PASS |
| In-stream AAC profile/rate transitions | 1/2 PASS |
| Rapid Stop/Play generation | 1/1 PASS |
| Dropped/stalled/error source recovery, redirect, jitter | 5/5 PASS |
| WebSocket format and reconnect | 1/1 PASS |
| Settled heap recovery and lifetime health | 2/2 PASS |
| **Total** | **31/33 PASS** |

The two failures are preserved in the
[regression evidence](../tests/results/esp32c3-http-buffer-regression/):

- `vorbis-q10:auto`: the short steady window failed the existing 2,048-byte
  first/last heap-median criterion. Free heap oscillated between 70,400 and
  73,288 B; the largest block stayed at 57,344..59,392 B, with no allocation
  failure. The test exited before its EOF checks. Explicit Vorbis selection
  subsequently passed the complete file test. A short-window decline alone
  does not establish a leak.
- `transition:changing`: WebUI TCP connection timed out before the full AAC
  transition sequence could be observed. The other `implicit-sbr` sequence
  passed. The timeout does not establish an AAC decoding failure, and the
  interrupted sequence is not counted as passed.

The final idle heap median was 139,704 B versus 139,844 B initially (140 B
lower); largest free block stayed at 114,688 B and task count at 16. No allocation
failure, watchdog event or unexpected reboot was recorded across the campaign.
Thus the series passes the existing settled recovery limits, while retaining
the short-window Vorbis failure and incomplete transition observation.

Raw status/health/server records, numerical HTTP phase tracing, source snapshots
and an offline replay are retained. The replay verifies recorded evidence; its
own success does not turn the two failed cases into passes. Original production,
station and settings were restored after the matrix.

### Targeted follow-ups

A deterministic 90-second Vorbis q10 fixture (48 kHz stereo, approximately
507 kbit/s) was generated with the shared stress generator. Each firmware
played its first 60 seconds at 1x, with the existing 15-second warmup and
unchanged sustained memory/output gates. This is one continuous Ogg stream,
not concatenated short files. Generator settings, encoded hash and manifest
are archived; the replaceable large audio and source WAV stay under `.build/`.

| Vorbis firmware | Minimum free heap / largest block | First → last steady heap median | Format / output / memory / observation transport |
|---|---:|---:|---|
| Baseline | 66,276 / 51,200 B | 66,984 → 68,524 B | PASS / PASS / PASS / PASS |
| Request-buffer release | 70,336 / 53,248 B | 71,032 → 70,404 B | PASS / PASS / PASS / PASS |

The minimum and overall median free heap both improved by 4,060 B in this
comparison. Neither run recorded allocation failures, watchdog events, queue
drops or write errors in the steady window. The short-fixture heap failure
did not reproduce as a sustained-budget failure. Together with the matrix's
settled recovery, this provides no evidence of a persistent memory loss in
these runs; it is not an unbounded leak-proof claim.

The interrupted `changing` sequence was also repeated on the candidate:
AAC-LC 44.1 kHz → AAC-LC 48 kHz → HE-AAC 48 kHz → HE-AACv2 44.1 kHz.
All four formats were confirmed in order; 87 status/health observations
recorded no transport error, allocation failure, watchdog or reboot. Minimum
free heap was 39,072 B, largest block 24,576 B. This confirms the sequence in
the repeat, while leaving the earlier intermittent WebUI timeout unresolved.

Both follow-ups were independently replayed from saved evidence, and original
production/settings/station restoration was checked again. The original
matrix remains **31/33**, with these additional successful controls reported
separately. No firmware source or default was changed during this campaign.

## OTA and ten-minute HTTPS qualification, 2026-10-12

The same application SHA-256 was temporarily installed again. All **15/15 OTA
checks passed**: wrong chip/project, corrupt/truncated/extra-byte images, missing
multipart boundary, SPIFFS target, oversized request, disconnect, stalled upload,
two ordinary updates, update during confirmed HE-AAC 44.1 kHz stereo playback,
slow upload, and saved-settings verification after reboot. Updates targeted
application slots only; NVS/SPIFFS and bootloader were not rewritten. Physical
power-cut recovery was not part of this software-controlled suite.

The candidate then played the public HE-AAC HTTPS source for **600 seconds**.
FFprobe/FAAD confirmed its format before the run. Sampling used one-second
intervals plus request time; steady gates excluded the first 15 seconds.

| Measurement | Result |
|---|---:|
| Steady decoded-format observations | 505, all HE-AAC 44.1 kHz stereo |
| Steady output interval | 583.979 s |
| Completion queue drops / write errors | 0 / 0 |
| Allocation failures / watchdog events / unexpected reboots | 0 / 0 / 0 |
| Minimum **sampled** free heap / largest block | 24,712 / 11,264 B |
| Firmware heap low-water mark since boot | 15,168 B |
| First → last steady free-heap median | 27,584 → 29,500 B |
| First → last steady largest-block median | 15,360 → 16,384 B |
| Maximum status + health request duration | 254.86 ms |
| Failed observation requests | 0 |
| Settled memory recovery | PASS |

The firmware low-water mark includes transient allocations between polls and
is lower than the sampled minimum. The existing in-playback gate applies to
sampled values; passing it does not establish a 16-KiB absolute free-heap floor.
No allocation failure was reported. The output counters establish the measured
digital behavior, not an analog listening assessment.

Original production image, settings, station and decoded playback were restored
after both stages. An offline replay checks the reports against raw observations
and captured sources in the [OTA/soak archive](../tests/results/esp32c3-http-buffer-ota-soak/).
This run advances HE-AAC/OTA qualification; it does not resolve the earlier
intermittent public MP3 interruption or prove that the historical WebUI timeout
was fixed. The feature remains opt-in while the production profile is qualified.

## Reproducible measured profile

A fresh ordinary `build-production.ps1` configuration differed from the tested
image in 26 resolved values, including renamed aliases: QIO, TLS reserve,
adaptive input, prefill, fractional output and SRAM-placement policies were
not all selected by that command. Therefore its name alone did not identify
the configuration used for these measurements.

Use `build-production.ps1 -TestedRadioProfile` to select the 20 primary settings
in `sdkconfig.radio-tested.defaults`, in addition to the normal base/quiet
defaults. It uses a separate default build/output directory. Explicit selection
also applies those settings to an existing configuration, removing legacy
aliases; unrelated settings remain. See [production commands](../idf/esp32c3-oled-native/PRODUCTION.md).

Real ESP-IDF reconfiguration verified three cases:

- Fresh selected profile: byte-identical to the tested `sdkconfig`.
- Existing ordinary configuration updated with the switch: byte-identical too.
- Fresh ordinary command without the switch: unchanged from its previous hash.

The selected configuration SHA-256 is
`a62f4ea356ff0fed10a66aac688524a1da4a194bc426e222bbd42330a0ecb3ca`.
The configuration audit did not compile or flash another application and makes
no claim of byte-identical firmware images. Its configurations and source
snapshots are included in the OTA/soak archive. “Tested” names the measured
configuration and does not mark the complete production goal achieved.

### Fresh application build, 2026-10-12

A clean build using `build-production.ps1 -TestedRadioProfile` now completes
successfully. Its `sdkconfig` is byte-identical to the measured candidate,
with the same SHA-256 above. The saved image is
`firmware/development/esp32c3-idf-6.1-r9a97-production-radio/app.bin`:

- App SHA-256: `e526eb7dc072fe58c61d5424942f20933b9e8288d948574f6833eb38ab43e211`.
- Embedded ELF SHA-256: `d583ef1b8b51686498a7b2bc3445445d5f2779f14f0a65f5f644e68489407a52`.
- Size: 1,456,144 bytes, within the 1,900,544-byte OTA slot.

Build/link checks confirm the full compact AAC configuration, 17,058-byte TLS
reserve, HTTP request-buffer release, adaptive input ownership, normal CA trust,
quiet output and disabled deep sleep. AAC/FLAC object comparison matches all
18 objects and 119 nonempty text/constant sections against the earlier baseline.

A broader comparison covers 964 application object files: 11,389 text/constant
sections match byte-for-byte. Six sections differ: application/bootloader build
metadata, three generated assertion path strings, and the HTTP assertion's
string-address addend (57 to 53). SDK HTTP overlay source is identical; retained
disassembly confirms that instruction difference references the changed path.
This is object-level evidence, not a claim of identical linked images.

[Build evidence](../tests/results/esp32c3-production-radio-build/) retains source
snapshots, build logs, configuration, link audits and object comparison. This
exact new binary has **not yet been tested on hardware**. Prior OTA and playback
results apply to `quiet-http-txrelease`, not automatically to this rebuild.

## Ten-minute public MP3 controls, 2026-10-12

The same `quiet-http-txrelease` binary was observed for 600 seconds each on
`ice5.somafm.com/groovesalad-256-mp3`, first HTTP and then HTTPS. Steady gates
exclude the first 15 seconds; firmware fault counters cover the whole run.
The source reference was probed through HTTPS for both cases. That reference
does not independently establish HTTP route equivalence.

| Transport | Observation / format / output / memory / WebUI | Min sampled free / largest, B | Concurrent FFmpeg |
|---|---|---:|---|
| HTTP | PASS / PASS / PASS / PASS / PASS | 86,768 / 73,728 | FAIL, 0.000 decoded s |
| HTTPS | PASS / PASS / PASS / PASS / PASS | 81,920 / 65,536 | PASS, 605.000 decoded s |

The HTTP host control failed before decoding: FFmpeg rejected `tls_verify`
on a plain HTTP input. This is a test-command failure, not a board decoding
failure or a completed independent comparison. The corrected controller adds
that option only for HTTPS; a separate three-second HTTP command check passed.
The original controller and failure remain retained. A complete simultaneous
HTTP host/board comparison is still required.

HTTPS FFmpeg uses certificate verification. Separate live clients can receive
different content/start points; their results do not prove bit-identical input.
Queue-drop totals include deliberate idle periods; only steady-window deltas
are used for output acceptance. These are digital counters, not an analog
listening measurement. Passing runs do not establish a fix for historical
intermittent MP3 stops or WebUI TCP-connect failures.

Original application, settings, selected station and decoded playback were
restored and verified. [Raw evidence and replay](../tests/results/esp32c3-public-mp3-long/)
retain each case outcome, host failure, corrected command check and restoration.
Public audio and private FFmpeg stderr are not archived.

## Production rebuild HTTP regression, 2026-10-12

The exact `production-radio` application above was installed by OTA and
verified by embedded ELF hash before running the same 33-case HTTP matrix.
Result: **31/33 PASS**. Failed cases remain:

- `file-eof:opus-510:auto`: Progressive heap loss.
- `file-eof:hev2-44100-stereo:aac`: URLError.

The matrix covers eleven finite fixtures in automatic/explicit codec modes,
two AAC transitions, Stop/Play, dropped/stalled/error sources, redirect/jitter,
WebSocket reconnect, settled memory recovery and lifetime health. A failure
inside a finite-file case can prevent its later EOF checks; it must not be
counted as full EOF coverage for that case.

Original production, settings and station were restored and verified.
[Raw observations and replay](../tests/results/esp32c3-production-radio-regression/)
retain outcomes and the controller. Hardware testing is now recorded for this
exact binary; complete production qualification remains false. This HTTP
matrix does not replace exact-image HTTPS/OTA or sustained-playback checks.

### Production Opus memory follow-up

The same production image ran three sequential AUTO Opus cycles on a
continuous 90-second synthetic 48 kHz stereo file (510 kbit/s CBR). FFmpeg
decoded the complete file without error before board testing. Each cycle
observed 60 seconds, using the unchanged 15-second warmup and memory gates.
After each Stop, idle recovery was measured against the initial idle window.
The final cycle additionally ran to EOF.

| Cycle | First → last steady free-heap median, B | Minimum free / largest, B | Memory gate | Stop recovery |
|---|---:|---:|---|---|
| 1 | 84,260 → 84,268 | 81,088 / 65,536 | PASS | PASS |
| 2 | 84,268 → 82,048 | 81,088 / 65,536 | FAIL | PASS |
| 3 | 84,220 → 84,160 | 81,136 / 63,488 | PASS | PASS |

All three cycles passed format, observation transport and steady output gates:
zero completion-queue increments and write errors. No allocation failures,
watchdog events or unexpected reboots were recorded. Final EOF passed.
Cycle 2 retains its **2,220-byte median decline**, exceeding the unchanged
2,048-byte threshold. This is not a fully passing memory qualification.

Initial → final idle heap medians: 139,844 → 139,920 B; largest blocks: 110,592 → 110,592 B.
The three cycles do not show accumulating post-stop memory loss. They do not
identify the owners responsible for active-playback fluctuations. Correlate
network receive queues and heap observations before attributing them to a
codec leak or changing the gate. The original short Opus failure also remains.

Original firmware, station and settings were restored. The
[archive](../tests/results/esp32c3-production-radio-opus/) preserves the failed
gate, successful controls, fixture generation manifest and restoration.
`offline_replay.py` uses frozen test sources and reproduces the original review
without downloading or regenerating audio. Large fixture audio stays in `.build/`.
