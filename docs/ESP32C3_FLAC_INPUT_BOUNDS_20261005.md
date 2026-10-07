# FLAC input bounds and truncated-frame recovery

Date: 2026-10-05. Applies to the shared yoRadio FLAC core used by the native
ESP32-C3 custom FLAC adapter. AAC arithmetic, precision and format support are
unchanged.

## Reproduced fault

The bit reader fetched the next byte before checking whether input remained.
Its diagnostic logged a negative remaining byte count but continued reading.
The frame detector also inspected four magic bytes without requiring four
input bytes. ASan reproduces a heap-buffer-overflow for all twelve tested
prefix lengths: 0, 1, 2, 3, 4, 7, 8, 16, 64, 512, 2048 and 8192 bytes of the
existing `flac-level8` audio data. Input allocations have exactly the tested
length, without spare bytes hiding the overread.

This is an input-bounds defect, distinct from post-Stop heap fragmentation or
the incomplete USB telemetry discussed in the previous reports.

## Repair

- Check the input boundary before each byte fetch. A sticky error prevents
  further reads, including unterminated unary Rice/wasted-bit runs, until reset.
- Return `ERR_FLAC_TRUNCATED_INPUT` without exposing PCM from an incomplete
  frame. Check that the two-byte footer exists before exposing that frame.
  Existing CRC value validation is not added by this change.
- Bound the Ogg capture/header skip, channel workspace selection, predictor
  warm-up count and residual partitions. Remove unused Ogg field reads.
- Handle a zero-bit residual escape explicitly and avoid signed shift overflow
  in bit masks and wasted-bit restoration. Keep Rice arithmetic explicitly
  32-bit on both host and target; reject values outside its specified range.
- Preserve the seventeenth bit in a constant stereo side subframe. The previous
  temporary `int16_t` truncated that valid value before channel reconstruction.

Checks follow [RFC 9639 sections 9.2.2–9.3](https://www.rfc-editor.org/rfc/rfc9639.html#section-9.2.2):
wasted bits leave positive sample depth, LPC precision 16 and negative prediction
shifts are forbidden, the first residual partition exceeds the warm-up count,
and a zero-width escaped partition contains zero residuals. No new rate or
precision restriction is introduced for valid inputs.

The core still has its previous maximum block size, channel and source bit-depth
limits. Full 24-bit FLAC support, a complete malformed-stream audit, complete Ogg
mapping support and other outstanding format cases remain separate work.

## Host validation

`python tools/codec_benchmark/run_flac_bounds.py --output .build/flac-bounds-check`
uses WSL GCC on Windows, ASan/UBSan, and the installed FFmpeg for the independent
PCM reference. It compiles the actual shared core with only Arduino platform
stubs, using the C3's segmented workspace and 512-frame output size.

- The complete file produces **528,000 stereo frames / 2,112,000 PCM bytes**,
  identical to both the original decoder and FFmpeg 8.1.1.
- All twelve truncated prefixes return a defined error without sanitizer
  findings. Three further cases remove the last 1, 2 or 3 bytes: the last
  incomplete frame is withheld, leaving 525,312 complete stereo frames.
- Edge checks cover 31/32-bit reads, zero-width residuals, the extreme legal
  positive/negative Rice residuals, forbidden Rice minimum, 17-bit constant side
  data, unterminated unary input, invalid wasted bits/order/partition size,
  short Ogg prefixes/header tables and resetting a prior error.
- The same complete set passes with `--contiguous`, which uses the ordinary
  Arduino workspace and its default 2,048-frame output size.

These are input and PCM checks, not an assertion that every possible FLAC file
or a network outage has been qualified. Physical CPU, memory and playback
measurements are recorded separately below.

## Physical validation

Before installing the repair, the existing control image completed **105
switches**: fifteen cycles through LC 48 kHz, HE 48 kHz, HEv2 44.1 kHz, MP3,
FLAC, Vorbis and Opus. All 105 seven-second playback windows and all fifteen
settled checkpoints pass. The largest block stays at 114,688 B; the final
median free heap is 80 B below the first settled checkpoint. No panic/capture
error or boot banner appears in the retained run. This is a switching test of
these fixtures, not broad format or thirty-minute continuous qualification.
It does not identify the prior rare fragmentation owner.

WebUI OTA installs the candidate in 21.47 s while controlled AAC plays. Image,
settings, Wi-Fi and playlist checks pass, as does serial health. The candidate
is saved at `firmware/development/esp32c3-flac-bounds/`, without deep sleep or
the heap-owner probe. ELF sizes match the control: IRAM **43,354 B**, DRAM data
**12,620 B**, BSS **29,464 B**. No additional audio buffer is introduced.

`flac_truncation.py` then cuts the stream after 32 or 4,096 audio bytes, or
removes its final byte. All **15 physical gates pass**, including explicit
`FLAC decode error -12`, terminal status, natural memory recovery without Stop,
subsequent AAC/FLAC playback, serial health and saved-settings restoration.
After each damaged stream, largest free block is 114,688 B and task count is 17.

Both images then play the same generated 120-second 48 kHz / stereo / 16-bit
FLAC fixture for a 60-second window with frequent WebUI requests. All original
load and idle-recovery gates pass for both; no acceptance threshold is changed.

| Metric | Before | Repaired |
| --- | ---: | ---: |
| CPU mean / peak | 68.89 / 70.0% | 67.00 / 67.7% |
| Decoder time / decoded audio duration | 26.02% | 24.00% |
| Decoded audio / elapsed time | 1.00158 | 1.00156 |
| Minimum free heap / largest block | 69172 / 53248 B | 70732 / 55296 B |
| Maximum HTTP response | 125 ms | 125 ms |
| Minimum RSSI | -75 dBm | -75 dBm |

No slowdown appears in this pair. It is not a universal speedup claim: receive
buffers and scheduling vary, and only this fixture/load has been compared.
The final image is `3a30ce4278babd7b1a9de879aa6bc2b912b0cf69f3a263801360060d09da6ee4`;
the restored AAC 44.1 kHz stereo station is playing. Broader format, long-soak,
USB telemetry-loss and the earlier fragmentation investigation remain open.

Retained reports, filtered logs, exact sources, sanitizer diagnostics and the
build identity are covered by the
[evidence manifest](../tests/results/esp32c3-flac-bounds-20261005/manifest.json).
Run `python tests/test-flac-bounds-evidence.py` to verify and replay that evidence.
