# ESP32-C3: output task priority comparison (6–7 October 2026)

## Scheduling change

`CONFIG_YORADIO_OUTPUT_TASK_FIRST=y` raises the direct-DMA output task from
priority **6 to 8**, above the decoder (**7**). The stream task stays at **5**.
The option currently defaults to off and requires `YORADIO_DIRECT_DMA_PCM`.

The [preceding investigation](ESP32C3_PIPELINE_FLOW_20261006.md) found that
long FLAC LPC32 decode calls could delay refilling completed DMA blocks even
when decoded PCM was available. Returning a PCM lease can wake the decoder.
With priority 8, a ready output task runs first and then blocks when it needs
more PCM or a completed DMA block. It does not busy-wait.

The experiment keeps four DMA descriptors, 512 stereo frames per descriptor,
three-block startup prefill, queue capacities and all existing deadlines:
compressed input **20 ms**, PCM reservation **250 ms**, output PCM **5 ms**,
DMA descriptor **1000 ms**. Codec arithmetic, compressed storage, format
selection, sample rates and Wi-Fi task priorities are unchanged.

## Instrumented comparison

Same physical C3, 160 MHz, DIO 80 MHz flash, awake direct-DMA firmware.
Both variants use `YORADIO_PIPELINE_PROFILE=y`. The four identical 24-bit,
44.1 kHz stereo FLAC captures run for 60 seconds each, with 0.1-second WebUI
polling delays. The first ten seconds and partial windows are excluded:
each entry has nine complete windows, approximately 45 measured seconds.
The file's maximum allowed LPC order is shown; it does not force every
subframe to use that order.

| File / max LPC order | Mean CPU, priority 6 → 8 | Audio/wall, 6 → 8 | DMA completion queue overruns, 6 → 8 | Longest timed DMA acquisition, 6 → 8 |
|---|---:|---:|---:|---:|
| Groove / 12 | 73.43% → 73.44% | 1.0013 → 1.0015 | 1 → 0 | 42.448 → 19.391 ms |
| Groove / 32 | 77.51% → 79.92% | 0.9519 → 0.9918 | 208 → 42 | 53.322 → 17.820 ms |
| Indie / 32 | 80.40% → 84.83% | 0.9307 → 1.0014 | 300 → 1 | 56.647 → 19.605 ms |
| Indie / 12 | 77.91% → 78.15% | 0.9964 → 1.0015 | 22 → 0 | 45.694 → 18.710 ms |

An audio/wall ratio of 1 means the decoder supplies approximately one second
of audio per wall-clock second. It is not an acoustic continuity measurement.
DMA queue overruns count discarded completion notifications, not exact missing
PCM samples. Timed acquisition includes normal blocking and task preemption;
it is not a direct IRQ-to-task latency trace.

Estimated decoder task CPU per second of produced audio barely changes:
Groove32 **364.75 → 364.44 ms/s**, Indie32 **360.30 → 358.87 ms/s**.
The higher total CPU reflects more audio processed in a wall-clock second;
the results do not indicate a corresponding increase in computation per
decoded sample. Conversely, maximum elapsed FLAC calls increase from
47.440 to 50.395 ms and 49.020 to 51.868 ms because the output task can now
preempt them. These are separate CPU and elapsed-time measurements.

Groove32 still has 42 overruns and 22 compressed-input timeouts with priority
8. Input waits reach 27.627 ms including scheduling time. The observations do
not prove that every remaining overrun is caused by input starvation.
Output PCM-empty waits also rise: an early-running consumer naturally waits
for the producer more often, while already-filled DMA buffers can still play.

### Original failures remain failures

- The earlier priority-6 Groove12 case failed the progressive-free-heap gate.
- Priority-8 Indie32 failed the unchanged **85%** CPU budget: a complete CPU
  window reached **85.8%**, with an 84.83% weighted average.
- Other priority-8 load cases, the deliberate input-starvation control,
  runtime checks and settings restoration passed.
- OTA into the diagnostic image and back to the original nonprofiled image
  passed while AAC played; identity/partition, Wi-Fi, settings and playlist
  checks passed.

The minimum observed RSSI with priority 8 was −70 dBm. Observed stack headroom
was at least 13,256 bytes for the decoder and 1,092 bytes for output. These
short recordings do not establish an all-input stack worst case.

## Regression matrix with flow profiling disabled

The follow-up compares the normal performance counters with detailed flow
profiling disabled in both images. Its configuration differs only in
`CONFIG_YORADIO_OUTPUT_TASK_FIRST`. Both app binaries are **1,579,120 bytes**;
IRAM text **43,354**, DRAM data **12,620** and BSS **29,464 bytes** are unchanged.
The candidate ELF contains no detailed DMA-wait/overrun diagnostic symbols.

For each image, `output_priority_matrix.py` runs:

1. Nine 40-second playback tests under WebUI load: MP3, AAC-LC, HE-AAC,
   HE-AACv2, Vorbis, Opus, ordinary FLAC and two radio LPC32 recordings.
2. Twelve-second settled idle samples before playback and after each load;
   adjacent free-heap, largest-block and task-count recovery checks.
3. Seven finite-file format/EOF tests, one per codec/profile above excluding
   the additional radio recordings.
4. Stop/new-play generation cancellation and three cycles through all seven
   short fixtures, with settled memory checks.
5. Filtered runtime fault checks and a reboot preserving settings.

Original CPU, playback-progress and heap thresholds are retained. A load PASS
allows an audio/wall ratio between 0.9 and 1.1; passing it alone does not
establish uninterrupted sound. Complete CPU/audio windows after ten seconds
are analyzed separately for the comparison.

The 6 October control process disappeared after seven successful load/recovery
cases. No Python test process remained on 7 October; the cause is unknown.
Its partial report is retained as **incomplete**, and the complete control
and candidate series are run again. It is not counted as a firmware crash
or a completed matrix.

### Profile-off load comparison

Five complete approximately five-second CPU and decoder windows per file,
after ten seconds of warm-up. These weighted means differ slightly from the
original acceptance runner's arithmetic mean, whose first sample can straddle
the warm-up boundary. Original acceptance results are preserved separately.

| Source | Mean CPU, priority 6 → 8 | Audio/wall, 6 → 8 | Original load gate, 6 → 8 |
|---|---:|---:|---|
| MP3 48 kHz stereo | 60.15% → 60.12% | 1.0016 → 1.0019 | FAIL heap → FAIL heap |
| AAC-LC 48 kHz stereo | 48.16% → 47.78% | 1.0016 → 1.0016 | PASS → PASS |
| HE-AAC 48 kHz stereo | 63.53% → 64.37% | 1.0016 → 1.0016 | PASS → PASS |
| HE-AACv2 44.1 kHz stereo | 72.70% → 74.46% | 1.0016 → 1.0008 | PASS → PASS |
| Vorbis 48 kHz stereo | 73.86% → 73.30% | 1.0018 → 1.0019 | PASS → PASS |
| Opus 48 kHz stereo | 80.16% → 80.20% | 1.0017 → 1.0017 | PASS → PASS |
| FLAC 48 kHz / 16-bit stereo | 67.17% → 67.06% | 1.0015 → 1.0015 | PASS → PASS |
| Groove LPC32 44.1 kHz / 24-bit | 77.26% → 79.94% | 0.9601 → 1.0014 | PASS → PASS |
| Indie LPC32 44.1 kHz / 24-bit | 80.44% → 85.88% | 0.9227 → 1.0017 | PASS → FAIL CPU |

Both LPC32 recordings reach full decoder audio progress with priority 8.
Estimated decoder task CPU per produced audio second is **362.28 → 362.72
ms/s** for Groove and **361.32 → 360.25 ms/s** for Indie. The higher total CPU
therefore accompanies doing more audio work, rather than a similar increase
in predictor cost per sample. Nevertheless, Indie's **87.4%** peak CPU window
and **85.88%** average exceed the existing 85% budget; the margin failure is
real and is not waived because audio timing improved.

HE-AACv2 rises by **1.76 percentage points** of total CPU, with an estimated
decoder cost of **492.61 → 501.59 ms per audio second** (about +1.8%). This
single pair does not prove an exact scheduling overhead. Other non-LPC32
mean CPU changes are between −0.56 and +0.84 percentage points. No codec
arithmetic changes were made to obtain the scheduling improvement.

The two MP3 failures are the same progressive-free-heap gate. The median of
the first/last three accepted CPU samples changes **83,188 → 79,656 bytes**
with priority 6 and **83,672 → 80,092 bytes** with priority 8. Every post-load
Stop recovery passes, including MP3. Heap varies during playback and recovers
after Stop; this does not establish its allocation owner or rule out growing
allocations during longer playback. Preserve both failures and investigate
that owner separately.

The minimum RSSI varies between runs: per-file minima range from −79 to −71
dBm for the control and −70 to −65 dBm for the candidate. These are sequential
physical Wi-Fi measurements, not RF-controlled paired trials. Small CPU or
HTTP differences cannot be attributed solely to scheduling. The worst HTTP
request was 406 ms in the candidate Indie test, below the unchanged 2 s gate.

### Completed regression and decision

The full control finishes **38/39 PASS** and the candidate **37/39 PASS**.
The failures are exactly those listed above; no failed threshold is relaxed.
For **both** images, all seven finite-file/EOF cases, Stop recovery after all
nine loads, Stop/new-play cancellation, three seven-codec switching cycles,
runtime fault checks and settings-preserving reboot pass. No switching
failure is recorded. The candidate OTA transition while AAC plays also passes.
Both full matrix runs complete on 7 October; the instrumented comparison was
completed on 6 October.

**Keep priority 8 in the development image, but leave the fresh-build Kconfig
default off until the remaining qualification issues are resolved.** The
scheduling change improves both difficult FLAC recordings without adding RAM
or changing codec output arithmetic. The MP3 heap gate and insufficient CPU
headroom on Indie LPC32 still prevent a clean acceptance result. A short
matrix cannot establish an hour of AAC stability, all supported input modes,
public HTTPS reliability or acoustic continuity.

The board is left awake on
`firmware/development/esp32c3-output-first/app.bin`, application partition
`app1`, ELF SHA-256
`7f7c1cd4a59c7b215c3fe55c25b1b41f083905d9d8e84137f000c0273a10ec78`.
Detailed flow profiling is disabled. Priority 8 is enabled in this image's
saved configuration. Wi-Fi, playlist and settings equality checks passed.

Next qualification work is to identify the live MP3 heap allocations, improve
LPC32 CPU headroom while retaining timely DMA service, and repeat longer
AAC/HE-AACv2 and public-stream runs. The broader outstanding gates remain in
the [testing document](ESP32C3_TESTING.md); this experiment does not close them.

## Reproduce and evidence

Use the exact saved images and fixture manifest. The firmware build and saved
configuration must be adjacent. The matrix runner verifies installed image
identity and refuses deep sleep, QEMU and detailed flow-profiling builds.
It does not flash the board. Use `diagnostic.py ota_transition` between images.

```powershell
python tools/esp32c3_tests/output_priority_matrix.py `
  --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 `
  --firmware firmware/development/esp32c3-pipeline-profile-off/app.bin `
  --fixtures .build/output-priority-20261006/fixtures/manifest.json `
  --seconds 40 --output .build/priority/control

# Install the priority-8 image through the normal OTA transition runner.
python tools/esp32c3_tests/output_priority_matrix.py `
  --board http://BOARD_IP --host PC_LAN_IP --serial-port COM9 `
  --firmware firmware/development/esp32c3-output-first/app.bin `
  --fixtures .build/output-priority-20261006/fixtures/manifest.json `
  --seconds 40 --output .build/priority/candidate

python tools/esp32c3_tests/compare_output_priority_matrix.py `
  --control .build/priority/control --candidate .build/priority/candidate `
  --output .build/priority/comparison.json
python tests/test-output-priority-matrix.py
python tests/test-output-priority-evidence.py
```

The composite manifest combines the existing generated stress fixtures with
the Groove32 and Indie32 recordings from the [radio study](ESP32C3_FLAC_RADIO_20261006.md).
Exact hashes are retained; copyrighted station audio remains in ignored local
capture directories. The fixture server is shared by all boards.

Retained evidence: [priority comparison](../tests/results/esp32c3-output-priority-20261006/).
It includes original failed gates, filtered logs, status samples, firmware
identities, build checks, exact source snapshots and an integrity manifest.
No Wi-Fi credentials or raw UART logs are retained.

Saved images: [priority 8, normal counters](../firmware/development/esp32c3-output-first/)
and [priority 8, detailed flow profiling](../firmware/development/esp32c3-output-first-profile/).
These remain development firmware; the short scheduling comparison does not
complete long-duration AAC/network/format qualification.
