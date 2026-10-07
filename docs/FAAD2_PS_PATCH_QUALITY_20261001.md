# Supplied FAAD2 packed PS-history patch: measured quality

## Result

Built and tested the user's exact `faad2_esp32c3_packed_ps_history_final.patch`
against its declared upstream commit. On the tested corpus it reaches **2 signed-16
PCM LSB maximum**, with no >2 or >5 samples. `sizeof(ps_info)` decreases by
**9600 bytes** in the host build. The patch-disabled build remains PCM-identical
to unmodified upstream FAAD2 on every input.

This is a **14+14+4 midpoint PS-only** implementation, not the new PC16 format.
It leaves `sbr_info::Xsbr`, hybrid-filter histories, mixing/phase coefficients,
energy state and native DSP arithmetic unchanged. It packs the four PS delay
arrays at **each history write inside decorrelation**, including within a frame.

The [C3 PC16 experiment](ESP32C3_AAC_PC16_QUALITY_20261001.md) instead roundtrips
both SBR and PS retained state after each frame, with a different decoder and
history layout. Its three-LSB maximum is not evidence that 16-bit mantissas are
inherently worse than 14-bit mantissas.

## Provenance and configuration

- Upstream FAAD2 commit: `e8e76f0a44db45aed773a3f62fe35a63c867a738`.
- Source archive SHA-256: `36f5aa8cbfcc442cdaced7f29dbe66276c62a1432d3c639405c07bcdf47614ab`.
- [Unchanged supplied patch](../tools/codec_benchmark/patches/faad2-packed-ps-history-supplied.patch),
  SHA-256 `44bc82a60793946a9477da17d841abf8444da80a279aa7ae48e4005cb49cdbd1`.
  It was applied with `git apply --recount`; the apply log is retained.
- All three builds use `FIXED_POINT`, full complex SBR/PS, `APPLY_DRC` and GCC
  `-O2 -fno-strict-aliasing -ffloat-store`, matching the earlier host baseline.
  Only the packed build defines `FAAD_PACKED_PS_HISTORY`. No LTP/LD features
  are removed and no core-only or low-rate fallback is requested.
- A **100000-pair quantizer comparison** per packed run verifies the supplied
  implementation against our portable `PC14_MIDPOINT`, including int32 extrema.
  The packed words and reconstructed integers agree. This does not imply that
  applying the same quantizer at different points produces identical PCM.

Source builds live in an ignored experiment directory, separate from both the
pristine downloaded source and the firmware. The patch is not installed as the
production AAC backend.

## Quality measurements

Six synthetic AAC-LC/HE/v2 fixtures and five previously captured 30-second radio
files were decoded by three binaries: unmodified upstream, patched source with
the option disabled, and patched source with the option enabled. This gives
**33 decoding runs**. Synthetic inputs repeat twice continuously; recordings
run once. Compared signed-16 PCM has no gain normalization or resampling.

| Input with active PS | Maximum L / R, LSB | RMS L / R, LSB | Samples beyond ±2 | PS-active frames |
| --- | --- | --- | ---: | ---: |
| Synthetic HE-AAC v2, two passes | 1 / 2 | 0.131178 / 0.446792 | 0 | 30 |
| ABBA 64 kbps | 1 / 2 | 0.343651 / 0.421758 | 0 | 635 |

The synthetic output has four samples with absolute difference 2, all in the
right channel. ABBA has 131, also in the right channel. These pass the inclusive
±2 limit. None exceeds the temporary ±5 limit.

The other nine inputs are bit-identical controls with **no active PS**, not
additional tests of packed PS accuracy. They include AAC-LC, HE-AAC v1 and the
Groove Salad 16 kbps capture, which FAAD decodes as 32 kHz mono without PS.
Full output rates/channel layouts and matching per-frame shapes are verified.

FAAD's unchanged default `dontUpSampleImplicitSBR=0` policy upsamples the
22.05 kHz AAC-LC mono fixture to 44.1 kHz mono in all three builds. This is
decoder-internal upsampling, not post-comparison resampling or active SBR/PS.
The probe counts `NO_SBR_UPSAMPLED` separately from actual SBR and retains the
raw status for every frame. Preserving a native 22.05 kHz output policy would
need explicit consideration in a future firmware adapter.

ABBA begins with one zero-output initialization frame and ten mono PCM frames,
then activates PS and produces stereo for 635 frames. The comparison follows
each frame's actual channel count rather than assigning stereo alternation to
the initial mono samples. Channel sample counts are 1320960 and 1300480.
The patch preserves this transition and the baseline's consumed-byte counts.

## What memory saving is established

The four arrays contain 2400 complex entries: native payload 19200 bytes,
packed payload 9600 bytes. On the tested x86-64 host, `sizeof(ps_info)` changes
from **22744 to 13144 bytes**, confirming the 9600-byte structure reduction.
This is a real layout change in this source decoder, unlike the C3 pack/restore
probe. It is not a measurement of the complete radio's peak heap or C3 RAM use.

FAAD backend porting to C3, stack/heap peaks, cache effects, decoding speed, longer/adversarial
streams and wider PS-tool coverage remain untested. Passing these eleven inputs
does not prove the ±2 bound for every legal AAC stream. The original supplied
study's exact input and one-LSB result have not been reproduced.

A subsequent [Espressif PS write-port experiment](ESP32C3_AAC_PS_WRITE_PORT_20261001.md)
adapts this packing strategy to the current C3 decoder and tests it in QEMU.
It reaches 3 LSB, with 2468 bytes less delay payload but no heap saving yet.
That is a different backend/layout from this FAAD host result.

## Reproduce and validate

With the already-downloaded pinned FAAD archive, pristine extraction and retained
ADTS captures available locally:

```powershell
$python = 'C:/Work/yoRadio/.idf/tools-v6.0.2/python_env/idf6.0_py3.12_env/Scripts/python.exe'
& $python tools/codec_benchmark/run_faad_ps_patch.py
& $python tests/test-faad-ps-patch.py
```

The runner uses native Linux GCC or WSL GCC on Windows. `--archive`, `--recordings`
and `--output` select paths; the output must be inside the repository for patch
application. It validates the archive, pristine source and supplied patch hashes,
then builds a separate patched copy. It never accesses a board or the network.

Raw PCM stays in `.build/faad-ps-patch-20261001/`. Tracked evidence contains input
and PCM hashes, per-frame shapes, compiler commands, raw decoder summaries and
per-channel integer error histograms in
[`tests/results/faad2-ps-patch-20261001`](../tests/results/faad2-ps-patch-20261001/).
