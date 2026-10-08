# ESP32-C3 latest ESP-IDF 6.1 revision qualification

The active SDK target is official `release/v6.1` commit
[`9a97f6c54ec638111ce55cd36581b3c192f15207`](https://github.com/espressif/esp-idf/commit/9a97f6c54ec638111ce55cd36581b3c192f15207),
checked on 2026-10-08. It is newer than the published `v6.1` tag. Work remains
on `codex/esp32c3-idf-upgrade`; the earlier 6.0.3 and release-tag results remain
controls. Full playback acceptance remains open until the physical matrix,
public streams and sustained memory/load checks pass.

## Reproducible SDK selection

`idf-version.txt` retains `v6.1` as the toolchain series. `idf-revision.txt`
contains the complete commit hash. Setup installs the SDK in
`.idf/v6.1-9a97f6c54ec6`, preserving the earlier checkout. Build refuses a
checkout at another commit. The source tree is clean and all 28 recursive
submodules match the pinned revisions.

Tools share `.idf/tools-v6.1`. Setup installs the versions required by this
SDK, including esptool 5.5.0; the RISC-V compiler remains
`esp-15.2.0_20251204`. The shallow SDK checkout embeds `9a97f6c5` as its IDF
version string. Firmware manifests separately record the full SDK commit.

The HTTP server now contains the reviewed upstream Content-Length overflow
guard. The project adapter preserves this source unchanged while retaining its
backport for audited older SDKs. Unknown source revisions still require review.
The lwIP TCP and netconn sources match the existing ownership-fix audit.

## Host and linked checks

| Check | Result and scope |
| --- | --- |
| Actual SDK HTTP reader, parser and TLS adapter | 85 ASan/UBSan cases pass with scripted transport |
| lwIP half-close ownership | Six cases pass with each of the heap and pool allocators |
| Native firmware Node regressions | 46 pass; stale ICY assertion updated for the guarded reader |
| Acceptance server and criteria | 19 tests pass |
| Public stream criteria | Eight tests pass |
| File runtime gate | Three tests pass, including 14 injected runtime faults |
| Linked AAC audit | Full PC19/SBR/PS configuration; SBR owner 32,744 B, decoder adapter 204 B |
| Linked HTTP/TLS audit | Radio guard, distinct EOF adapter and SDK dynamic RX wrapper present |

These checks distinguish actual SDK code under host sanitizers, firmware
linkage and physical execution. Scripted transport does not emulate TLS
cryptography. Initial Windows sandbox restrictions prevented temporary-directory
cleanup and a Git submodule inventory; reruns with normal process access passed.

## AAC PCM on the new SDK

QEMU executes a new build using the pinned SDK and its bootloader. Across
865,280 channel samples, the late-SBR and absent/resumed-SBR captures match
the retained PC19 output byte for byte. Against the retained uncompressed
reference, both stay below the permitted three-LSB error.

| Synthetic capture | Channel samples | Maximum PCM error | Changed samples | RMS error in LSB |
| --- | ---: | ---: | ---: | ---: |
| Late SBR activation | 189,440 | 2 LSB | 74 | 0.023090 |
| Absent and resumed SBR | 675,840 | 2 LSB | 834 | 0.042085 |

The same run checks six ordinary LC/HE/HEv2 formats, PC19 metadata and reopen
lifetime, output-buffer independence, malformed fill elements and allocation
failure recovery. It records 1,186,037 pointer checks and 696 allocations matched
by 696 frees; minimum observed decoder stack margin is 2,824 B. This corpus
does not establish an all-input precision bound or physical sound continuity.

## Physical profiling image

The saved image is
[`esp32c3-idf-6.1-r9a97f6c54ec6-rx6-dynamic`](../firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-rx6-dynamic/manifest.json),
1,613,728 bytes, ELF
`e51ff9fd08123d5aa5da09441818777eb6c04eca99c0279dfd396d1e88247e75`.
It is awake and retains all compact AAC features, dynamic TLS, copied RX
buffers and the six-segment TCP window. Its laboratory CA extends the normal
roots; verification and full 16 KiB TLS input capacity remain enabled.

The comparable release-tag control is `rx6-eof-fixed`, rather than the separate
rejected retained-RX experiment. The new SDK enables cross-signed certificate
verification and its trusted-certificate callback by default. The saved config
diff records these changes; receive-window and codec settings remain the same.

The corresponding link maps show only **254 B more static shared RAM** than
the release-tag control (89,000 versus 88,746 B, including RAM-resident code).
The application image grows by 8,848 B. These link-time totals do not include
runtime decoder/TLS allocations; the SDK update alone is not a RAM solution.

Installation by native app-only OTA passes and preserves Wi-Fi, playlist and
settings. Five malformed/oversized Content-Length checks plus restoration pass.
All eight real-TLS framing cases pass, including truncated fixed/chunked bodies,
clean close and bare TCP EOF. Each first reaches full 44.1 kHz stereo HEv2 PCM;
the runtime and settings gates pass. This covers incoming closure, not the
remaining outbound-alert and certificate-identity-negative RFC checks.

## Physical format and station results

All **44 file-playback cases pass**: eleven inputs over HTTP and HTTPS, each
with automatic detection and explicit codec selection. Inputs cover MP3 320,
FLAC level 8, Vorbis q10, Opus 510, AAC-LC 320, LC mono/stereo at 22.05/44.1/48
kHz, HE stereo at 44.1/48 kHz and HEv2 stereo at 44.1 kHz. Full output format,
natural EOF and the strengthened serial runtime gate pass. There are no
recorded allocation failures. The additional 45th check confirms Stop.

Changing-format and implicit-SBR streams, Stop/Play generation changes and
WebSocket format/reconnect checks all pass. These runs preserve full SBR/PS
and output rates; they do not impose a 22 kHz output limit.

Four public AAC HTTPS streams pass 60 seconds each, including full-rate mono
HE. FFprobe and the uncompressed FAAD reference inspect the live AAC sources
before each case. The source advertised as 32 kbit/s is HE-AAC in this capture;
the synthetic HEv2 fixture supplies the separate active-PS coverage.

| Public stream | Result | Mean / peak active CPU | Minimum free / largest block |
| --- | --- | ---: | ---: |
| AAC-LC 128 kbit/s, 44.1 kHz stereo | PASS | 54.03 / 54.9% | 58,804 / 43,008 B |
| HE-AAC 64 kbit/s, 44.1 kHz stereo | PASS | 65.79 / 66.5% | 23,448 / 7,936 B |
| HE-AAC 32 kbit/s, 44.1 kHz stereo | PASS | 61.76 / 62.1% | 21,872 / 9,216 B |
| HE-AAC 16 kbit/s, 32 kHz mono | PASS | 45.49 / 46.1% | 23,940 / 10,240 B |
| MP3 256 kbit/s, 44.1 kHz stereo | FAIL: WebUI timeout | Incomplete observation | Incomplete observation |

The successful rows use the unchanged public-stream gate's stable window,
beginning 15 seconds after start. CPU remains informational. These are
profiling-image measurements, with normal transport variation; a host build
overlapped part of the short matrix, so this is not a controlled SDK speed
comparison.

The MP3 run retains 135 successful status samples through 24.312 seconds,
followed by a five-second request timeout (`URLError` caused by `TimeoutError`).
Its serial decoder windows continue at approximately real-time speed, with
no recorded allocation/decoder/TLS fault. This does not prove uninterrupted
physical output or establish the timeout's cause. Idle recovery and settings
checks pass. The test restores the ordinary image and confirms its initial
playback state over three observations spanning 15 seconds.

A separate requested 600-second MP3 run ends after 468.437 seconds at the
case level. Request-phase instrumentation identifies a different failure:
Windows `OSError` / `WinError 10048` during TCP `connect`, before the HTTP
request is sent. No allocation or decoder failure is recorded. The original
FAIL is retained; it is an incomplete long run, not a ten-minute PASS.
The timing wrapper preserves urllib requests, timeouts and no-retry behavior;
two loopback checks verify successful transfer and header-timeout attribution.

Microsoft defines 10048 as an address already in use, including sockets still
closing; see [Winsock error codes](https://learn.microsoft.com/en-us/windows/win32/winsock/windows-sockets-error-codes-2).
The later host snapshot has 137 TCP entries, including 63 TIME_WAIT entries
and 17 TIME_WAIT entries to the board, against a 16,384-port dynamic range.
It does not establish general port exhaustion or explain the earlier five-second
timeout. Future load checks need to separate connection churn on the test host
from a board response failure. No OS networking settings were changed.

## Saved ordinary builds

All three ordinary variants compile with the pinned SDK and pass the linked
HTTP/TLS audit. Binaries and exact configurations are retained under
`firmware/development/esp32c3-idf-6.1-r9a97f6c54ec6-<variant>/`.

| Variant | Application size | Qualification |
| --- | ---: | --- |
| `quiet` | 1,446,672 B | Build and linked AAC/HTTP checks |
| `deep-sleep` | 1,459,472 B | Build and linked HTTP checks |
| `rtc32k` | 1,459,472 B | Build and linked HTTP checks; board has no crystal |

These images retain the ordinary network defaults. They do not inherit the
profiling image's experimental RX6/copy/dynamic-TLS overlays or laboratory CA.
The original build driver mistakenly invoked an awake-only AAC audit on the
successful deep-sleep build; its expected configuration rejection is retained.
The corrected driver builds the remaining crystal variant and applies the
appropriate linked checks without relaxing the awake-image audit.

## Full sized TLS record failure

The 600-second alternating-record HEv2 run **fails**. Full 44.1 kHz stereo
HEv2 appears initially, but a later 16,749-byte TLS allocation fails with
27,040 B free and only 15,360 B in the largest block. Playback terminates with
`stream read failed`. Full PCM first appears at 0.813 s, allocation fails at
4.922 s, and the first terminal status is at 5.344 s. The runner continues
observing that terminal state for
the rest of its 600-second window; this is not ten minutes of successful audio.
Both the playback and runtime gates fail. Idle memory recovers to 142,912 B
free / 114,688 B largest, with settings and the final ordinary image restored.

The new SDK therefore preserves the previously identified fragmentation
problem even with the six-segment TCP receive window. Full 16 KiB TLS records
and certificate verification remain required; shortening the accepted record
size would hide the problem and reduce HTTPS compatibility.

## Remaining acceptance

MP3 WebUI timeout diagnosis, the TLS allocation fix, sustained load, and final
production-image qualification remain open.
The final candidate also needs the broader high-depth/LPC32 FLAC corpus,
mixed-codec cycles, network fault/timeout cases and interrupted/invalid OTA
checks; their earlier SDK evidence is not a new run on this revision.
The new SDK is the active development target, but these short results do not
justify promoting the experimental network settings or merging the upgrade.

The next isolated memory experiment reduces only static Wi-Fi RX buffers and
their block-ack window; see the [candidate and acceptance plan](ESP32C3_WIFI_STATIC_RX_20261008.md).

## Evidence

The [exact evidence archive](../tests/results/esp32c3-idf61-revision-20261008/index.json)
contains 222 indexed files, including original failures, build/link reports,
host checks, synthetic QEMU PCM, physical telemetry, HTTP phase traces, SDK
identity and measured-source snapshots. It retains public test certificates
without private keys or captured broadcasts. Configuration and source files
keep their recorded byte hashes.

The two initial quiet/sleep console captures are partially truncated by the
tool's output limit. Their successful binaries/configurations and audits are
retained; the separate RTC build captures its complete process output.
