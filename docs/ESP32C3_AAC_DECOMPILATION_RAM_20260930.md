# ESP32-C3 AAC decompilation and RAM candidates — 2026-09-30

## Conclusion and acceptance criteria

The shipped Espressif AAC decoder has real opportunities for smaller SBR state.
The best first candidate is its oversized smoothing pointer tables: **1,888
bytes** of potential saving, confirmed by compiling the reference structure for
RV32. Sharing the temporary low-band QMF workspace between stereo channels is
another **6,144-byte design candidate**. Neither is implemented in the decoder.

The main requirement is **complete preservation of the current decoder's
supported formats and features**, including AAC-LC, HE-AAC v1, HE-AAC v2, SBR,
PS, existing sample rates and both output channels. Preserve additional accepted
tools/containers/configurations too; the list above is not permission to remove
less common paths such as the binary's long-term prediction code.

The user permits at most **one least significant bit of output error**. For our
16-bit PCM interface, interpret this as `abs(new_sample - baseline_sample) <= 1`
for **every** sample in **each** channel. Compare in a wider signed integer type
to avoid overflow. This is a maximum error bound, not an RMS/average allowance.
Pure allocation/layout changes should remain byte-identical. Any arithmetic
change needs an output error bound as well as regression measurements.

**Decoding speed must ultimately be preserved.** The user permits a temporary
slowdown while reducing RAM, provided that subsequent speed optimization remains
an explicit task. For each candidate, record the RAM gain and measured timing
change against the unmodified decoder. A slower prototype can advance the RAM
work, but its performance follow-up stays open until remeasurement confirms
that the slowdown has been recovered within measurement variability. Do not
recover speed by removing format support or exceeding the one-LSB PCM limit.

**This audit does not enable a new optimization or establish that full HE/v2 now
fits the complete radio.** No firmware was flashed. The allocation failures and
operating-heap requirements in the [memory report](ESP32C3_AAC_MEMORY_20260930.md)
remain applicable.

## What was actually decompiled

- `esp_audio_codec` **2.6.2**, esp-adf-libs revision
  `67b8d0e98f58c774b8652480893037273190e8dc`.
- ESP32-C3 `libesp_audio_codec.a`, SHA-256
  `311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909`.
- Linked production-config ELF from source `701591bb`, SHA-256
  `6a4028f1d5ac44207d5978d7be15f43978f1ee057210b6ad18e24a6861ea4b8d`.
  Using the linked ELF resolves relocations and retains symbol names.
- Ghidra **12.0.4**, explicitly `RISCV:LE:32:default`, GCC convention.
  **176 functions** in the direct-call closure of AAC open/decode/close/reset,
  registration and frame parsing, restricted to symbols defined in the codec
  archive; all 176 decompilations completed. This includes shared codec helpers,
  excludes the AAC encoder and does not recover unlinked code or resolve every
  possible indirect call.
- Critical allocation, offset and lifetime claims were checked against GNU
  RISC-V disassembly. `ps_allocate_decoder` has a Ghidra type-propagation warning;
  its inferred C types must not be treated as authoritative.

The [saved evidence](audits/esp32c3-aac-decompile-20260930/README.md) includes the
176 pseudocode files, call manifest, 14 disassemblies, hashes and RV32 layout
experiment. **Pseudocode is not original source, a compilable replacement, or a
verified ABI header.** For example, Ghidra sometimes omits an argument to a
callee; register-level disassembly supplies the evidence in such cases.

## Allocation ownership recovered from the binary

The following requested sizes agree with the earlier allocation traces. They
exclude allocator metadata, caller ADTS/PCM storage, task stacks and global
registration lifetime. Some field names are inferred from the reference.

| Owner / purpose | Requested bytes | Allocation / lifetime |
| --- | ---: | --- |
| AAC wrapper | 84 | `esp_aac_dec_open` → close |
| Main core object | 35,460 | `PVMP4AudioDecoderGetMemRequirements`; open → close |
| Program configuration | 860 | Init; core pointer at `+0x2c` |
| Two frame-information objects | 696 × 2 | Init; pointers at `+0x70`, `+0x74` |
| SBR bitstream state when AAC Plus is enabled | 1,044 | Init; pointer at `+0x8a60` |
| Internal transform/SBR workspace | 12,288 | Init; owner at `+0x8a7c` |
| Simple/codec wrappers, from allocation trace | 48 + 24 | Decoder open → close |
| **Subtotal before SBR processing state** | **51,200** | Simultaneously live |
| SBR/PS object | 55,128 | First extended frame → close; pointer at `+0x8a58` |
| SBR control | 1,180 | Same phase; pointer at `+0x8a5c` |
| **With SBR/PS state** | **107,508** | Requested payload, not an arena capacity guarantee |

### The 12 KiB workspace cannot simply be halved

`PVMP4AudioDecoderInitLibrary` allocates `0x3000` bytes and sets working pointers
to its base and `base + 0x1000`. This is shared internal scratch for transforms,
parsing/prediction and SBR, **not a redundant PCM output allocation**.

`sbr_dec` uses the scratch region for a linear sliding synthesis history. In the
PS path it copies `0x900` bytes to `scratch + 0x2700`, ending exactly at `0x3000`.
Even the ordinary full-rate SBR path copies `0x900` bytes to `scratch + 0x2200`,
ending at `0x2b00`. The PS path also uses `base + 0x1000` for a high-band QMF
workspace at an earlier phase. Merely reducing the allocator request corrupts
memory; mode-independent 4/8 KiB replacements are not supported by these accesses.

### Halving caller PCM does not save 4 KiB for HE stereo

`esp_aac_dec_decode` can split output, but when the caller supplies only 4,096
bytes it lazily allocates another 4,096-byte AAC-Plus output buffer and retains
the second half for a following call. Our current 8,192-byte caller buffer takes
the direct two-half path. Trading 4 KiB of caller RAM for 4 KiB inside the SDK
does not reduce this peak and adds an allocation/copy. The already implemented
12,288 → 8,192 caller reduction remains valid.

## Important difference from the open PacketVideo reference

The pinned [PacketVideo reference tree](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/)
explains the algorithm, but its structures cannot be substituted into our
library. Matching total sizes and some offsets did **not** mean all SBR fields
matched. Decompilation exposes a reordered area in `SBR_FRAME_DATA`:

| Field / range | Espressif offset | Reference offset | Bytes |
| --- | ---: | ---: | ---: |
| Low-band QMF real | `0x11b0` | `0x11b0` | 5,120 |
| Low-band QMF imaginary | `0x25b0` | `0x2a34` | 5,120 |
| High-band imaginary pointer / history | `0x39b0` / `0x39b4` | `0x3e34` / `0x3e38` | 4 / 1,152 |
| High-band real pointer / history | `0x3e34` / `0x3e38` | `0x25b0` / `0x25b4` | 4 / 1,152 |
| Synthesis history `V` | `0x42b8` | `0x42b8` | 2,304 |
| Four smoothing matrices | `0x4cb8`…`0x60b8` | Same | 5,120 |
| Four smoothing pointer tables | `0x60b8`…`0x64b8` | Same | 1,024 |

Offsets are relative to a frame-data object, **eight bytes after its channel
base**. A channel is `0x64c0` = 25,792 bytes. Real/imaginary names above follow
the analysis/generation call arguments, cross-checked with reference signatures.

The core also differs: Espressif uses a 35,460-byte core plus separate objects;
the upstream monolithic core is 108,344 bytes. Its `pShareWfxpCoef`, FFT and PS
overlays already reuse storage. Do not count them as new opportunities.

## Ranked proposals

All figures below are payload estimates **before** pointer/alignment/allocator
overhead. They are **not additive across modes**, and none is a measured saving
from a modified decoder.

| Priority | Change | Potential saving | Scope / evidence |
| --- | --- | ---: | --- |
| 1 | Smoothing pointer tables: 64 → 5 entries | **1,888 B** | Two SBR channels; initialization and use limits match binary and reference; RV32 size experiment confirms arithmetic |
| 2 | One low-band QMF work area, separate histories per channel | **6,144 B** conservatively | Ordinary stereo SBR; sequential channel calls and eight retained rows confirmed; PS requires its own layout |
| 3 | Keep four smoothing history rows; use the existing current gain/noise vectors as the fifth FIR input | **2,048 B** | Two-channel design estimate; retains all five filter taps; needs algorithm/lifetime verification |
| 4 | Allocate embedded PS control only when PS appears | Up to **3,536 B** while PS is absent | Helps HE v1; no saving for active PS; must allocate before parsing PS and preserve in-stream transitions |
| 5 | Replace unused right SBR channel with compact PS-specific storage | **16,004 B upper bound**, before retained control and alignment | HE v2 only; substantially more invasive, not a proven reachable saving |
| 6 | Genuine ring storage for synthesis history and a phase-based scratch plan | Not yet established | Remove expanded linear history only after bounding all scratch users, including PS and prediction |

### 1. Oversized pointer tables: strongest first experiment

`init_sbr_dec` initializes **five** pointers at each of four table bases:
`0x60b8`, `0x61b8`, `0x62b8`, `0x63b8`. Each currently reserves 256 bytes.
The binary's Flash constant `smoothLengths` is `{4, 0}`; `calc_sbr_envelope`
passes the maximum history length 4 to `envelope_application`. That function
uses and rotates entries 0 through 4. The [reference initialization](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/init_sbr_dec.cpp)
and [envelope implementation](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/calc_sbr_envelope.cpp)
explain the same five-tap operation. The 64 spectral bins belong in each pointed-to
row, not in the row-pointer count.

`2 channels × 4 tables × (64 − 5) pointers × 4 bytes = 1,888 bytes`.

The RV32 probe changes only those four **reference header** declarations and
measures `sizeof(SBRDECODER_DATA)`: **55,128 → 53,240 bytes**. It does not execute
a decoder. Our binary has fixed channel strides and offsets, so every affected
consumer, reset, allocation and free path must be rebuilt consistently. Reducing
only `calloc` or replacing one initializer is invalid.

### 2. Share low-band work without discarding inter-frame history

`sbr_applied` calls `sbr_dec` for the left channel and then the right. Each has
two `40 × 32 × int32` low-band matrices: 10,240 bytes per channel. `init_sbr_dec`
sets 32 new columns and a write offset of 8; `sbr_dec` retains those eight rows.

A straightforward layout uses one 10,240-byte current work area and two
2,048-byte retained real/imaginary histories: `20,480 − 10,240 − 4,096 = 6,144`.
Copy/rebind the appropriate history before and after each channel. Preserve
the arithmetic, row order, overlap and reset behavior. Measure the extra copy
cost on the board. PS already uses right-channel storage differently; this
number cannot be applied to HE v2 unchanged.

### 3. Remove a redundant current smoothing row, not a filter tap

The existing filter reads four prior rows plus a current gain/noise row. That
current row was just copied from gain/noise vectors which already exist in
scratch. A candidate implementation reads those vectors directly, keeps a ring
of four prior rows and updates it after the last reader. Four matrices lose one
64-element row per channel: `2 × 4 × 64 × 4 = 2,048` bytes.

Preserve reset prefill, envelope boundaries, zero/four smoothing modes and the
optimization that stops copying identical history. This requires a reconstructed
or source-built `envelope_application`, not a size-constant edit. Combined with
proposal 1, recalculate the pointer count as four plus the chosen current-row
representation; do not assume the two final implementations are independent.

### 4–5. Preserve PS while giving it a smaller state layout

The binary sets the PS pointer at `SBR + 0xc984` to the embedded state at
`SBR + 0xc988`, even before PS is active. This accounts for 3,536 bytes that could
be allocated lazily. `sbr_extract_extended_data` invokes `ps_read_data` when it
encounters a PS extension: allocation must happen **before** that call, including
PS appearing later in a stream. A first-frame-only decision would lose support.

For active PS, `ps_allocate_decoder` reuses right-channel SBR memory. Its buffer
and pointer-table window is `SBR + [0x7678, 0x93b4)`, **7,484 bytes**; right
synthesis `V` uses `SBR + [0xa780, 0xb080)`, **2,304 bytes**. Against an entire
25,792-byte right channel this suggests `25,792 − 7,484 − 2,304 = 16,004` bytes
as an **upper bound** before keeping needed control data/alignment. This is not
proof that all other bytes can immediately be freed.

Create explicit stereo-SBR and PS state variants with small independently
allocated blocks. Audit all bitstream, reset, concealment and transition users;
support changes in either direction. Keep the 3,536-byte PS object and both
output histories in PS mode. The core's two `38 × 64 × int32` PS work matrices
already reuse the right AAC channel/coefficient area; their **19,456 bytes are
not an additional saving**. Right-channel savings overlap proposals 1–3.

### Precision candidates, subject to the one-LSB output limit

- **16-bit stored exponents:** two `5 × 64` exponent histories per channel
  could save `2 × 2 × 5 × 64 × (4 − 2) = 2,560` bytes, retaining 32-bit
  mantissas and widening exponents for arithmetic. Prove every reachable
  exponent fits, including resets, extreme valid envelopes and corrupted input;
  otherwise it is not a lossless representation change. This overlaps proposal
  3 and saves less in a compact PS layout. No range proof has been completed.
- **Packed narrower QMF samples:** 24-bit storage for the two-channel low-band
  matrices alone would save 5,120 bytes, but discarding eight internal low bits
  does **not** imply one-LSB PCM accuracy. Gains, prediction, PS mixing and
  synthesis accumulate/amplify error. Keep this exploratory until scaling,
  overflow and worst-case output error are bounded and packing cost is measured.
- Do not narrow `time_quant`, mantissas or delay histories just because a
  particular music sample has small values. A corpus maximum is not a proof
  for every supported input.

## Can SBR state be compressed? What about mu-law / A-law?

The SBR allocation is mostly **mutable decoder state**, not the compressed AAC
bitstream. The major groups across both channels are:

| Data | Bytes | Meaning |
| --- | ---: | --- |
| Low-band complex QMF matrices | 20,480 | Real/imaginary subband samples: current frame plus retained rows |
| High-band QMF histories | 4,608 | Samples carried across frames for high-frequency reconstruction |
| Synthesis histories | 4,608 | Filter delay state, already stored as 16-bit values |
| Smoothing histories | 10,240 | Gain/noise mantissas and exponents, not ordinary PCM samples |
| Other channel fields | 11,648 | Envelopes, previous noise/bandwidth state, harmonic state, pointers and control |
| PS object and top-level fields | 3,544 | Stereo reconstruction control; more PS state aliases the right channel above |
| **Total** | **55,128** | Excludes the separately allocated 1,180-byte control object |

These buffers support reconstruction of higher frequencies and, with PS, stereo
from the transmitted core. Complex QMF values and gain/exponent pairs have
different numeric scales and meanings. Applying one audio compander indiscriminately
to them would change the algorithm, and pointers/control must remain exact.

Standard **mu-law and A-law use lossy 8-bit companding** of linear audio values;
see [ITU-T G.711](https://www.itu.int/rec/T-REC-G.711/en). They are not a suitable
drop-in representation for a one-LSB-accurate decoder. As a numerical illustration,
the saved Python 3.12 `audioop` experiment round-trips all 65,536 signed 16-bit
values:

| Representation | Restored value for input 30,000 | Error for that input | Maximum absolute error across all inputs |
| --- | ---: | ---: | ---: |
| mu-law | 30,076 | 76 | 644 |
| A-law | 30,208 | 208 | 512 |

This is an [illustration of companding error](audits/esp32c3-aac-decompile-20260930/g711-illustration.json),
**not a measured SBR output error**. Internal QMF values are mostly 32-bit, so
using G.711 would additionally need a scaling rule. Later gain/filter stages can
amplify error, and storing/reloading persistent histories repeats quantization.
The plain 8-bit schemes provide no basis for the required output bound.

More appropriate options to investigate:

1. **Exact bounded integers:** narrow exponents, flags, counters or relative
   offsets only after proving their ranges. This removes unused bits without
   introducing audio error; the exponent candidate above has an explicit size.
2. **Lossless compression of inactive history blocks:** predict/delta-code values
   and encode the exact residual, with an uncompressed fallback. Decode into the
   shared active-channel workspace. Compressible silence may save RAM, but noisy
   data need not; temporary compressed/uncompressed coexistence and metadata can
   increase peak RAM. Do not budget average compression as guaranteed capacity
   for every valid AAC stream. Frequent random access also raises CPU cost.
3. **Block floating point:** one shared exponent plus narrower signed mantissas
   per block can be more appropriate than a fixed 8-bit speech compander. Exact
   reconstruction is possible only when discarded bits are provably redundant;
   otherwise derive the total output error bound, including gains and feedback,
   and meet the one-LSB requirement. No acceptable mantissa width is established.
4. **Companding plus an exact residual:** mathematically lossless if the residual
   is retained, but its storage/metadata can erase the gain. The relevant question
   becomes residual compressibility, not whether G.711 itself is lossless.

Prefer eliminating redundant storage and sharing workspaces first: their saving
does not depend on the station's audio content and they can retain exact PCM.

## Implementation route and rejection cases

The supplied library is precompiled. Large layout changes require compatible
source or a maintained source-built replacement with the same tested feature
set. Use the pinned PacketVideo code as a reconstruction reference and compare
against the existing Espressif decoder; do not compile Ghidra output as if it
were original C. Rebuild all layout consumers together. Keep a baseline backend
for differential tests and an explicit configuration for the prototype.

Splitting the 55,128-byte allocation into smaller blocks helps fragmentation,
but **saves no payload by itself** and can add metadata. A shared codec arena
helps ownership/contiguity; the optional Helix arena is not resident RAM in this
production build and cannot be counted as free capacity. Do not change the
allocator to return a smaller block while leaving fixed-offset accesses intact.

The binary contains an out-of-memory branch which disables AAC Plus and
continues decoding. **That fallback is a failure of this task's full-format
requirement**, not a successful memory optimization. Likewise, a lower output
rate, forced mono, omitted PS/SBR, fewer smoothing taps, or accepting a format
while dropping its tools is not an acceptable result. Keep 64-bin bounds unless
all supported inputs prove a smaller bound; `calc_sbr_envelope` in this binary
allows a 64-bin extent, so a blanket 48-bin reduction is not justified.

Large constant/Huffman/window tables and strings are already in Flash. See the
[constant audit](ESP32C3_FLASH_CONSTANT_CANDIDATES_20260930.md); these mutable
signal histories cannot be placed in read-only Flash.

## Required validation before accepting a RAM optimization

1. Establish the existing backend's accepted format/tool matrix. Retain all
   current LC/HE/v2 fixtures; add vectors for any supported but untested tool,
   transport, framing or configuration path discovered in this analysis.
2. Compare output rate, channel count/order, sample count, EOF/error status and
   PCM against the **same unmodified library**. Allocation/layout changes must
   be byte-identical. Arithmetic/storage changes must have maximum absolute
   error at most 1 in signed 16-bit PCM, per channel, with zero timing offset.
3. Include long/short windows, attacks, silence, full-scale signals, stereo
   coupling, maximum envelopes/noise bands, both smoothing modes, SBR resets,
   PS appearing/disappearing, configuration changes and damaged/truncated input.
   Guard every new block; test allocation failure and repeated close/reopen.
4. Use reference decoders to cross-check profile/rate/channel/duration and signal
   behavior; different fixed-point implementations need not be byte-identical.
   Keep the shipped library as the one-LSB differential baseline. For lossy
   internal narrowing, supplement corpus tests with an error/range analysis.
5. Run the real library/prototype on QEMU, then the **complete radio on the C3**:
   Wi-Fi streaming, OLED, PDM, WebUI polling/OTA and codec transitions. Measure
   peak live bytes, largest free block, stack high-water and CPU/cache cost.
   Retain the existing operating-heap margin; isolated decoding is insufficient.
6. Compare decoding speed per profile/rate/channel configuration using identical
   inputs, CPU/Flash clocks, compiler options and instrumentation. Record cycles
   or time per decoded audio second, tail/maximum decode-call latency and total
   radio CPU/underruns; include copying and packing/unpacking overhead. Repeat
   measurements to distinguish a regression from normal variability. If the
   original full radio cannot allocate HE/PS, compare with the working isolated
   original decoder as well; core-only fallback is not an equivalent baseline.
   Keep QEMU estimates separate from physical C3 qualification. For any slowdown,
   save its percentage, affected cases and a concrete speed-optimization TODO,
   then repeat the same A/B after that optimization. Temporary slowdown does not
   relax real-time playback checks or close the performance task.

Use the existing [testing guide](ESP32C3_TESTING.md) and allocation/QEMU tools.
This audit ran decompilation, disassembly comparisons and a reference layout
probe only. It did **not** run PCM tests of any proposed altered algorithm.

Recommended order: pointer-table compaction → low-band work/history separation
→ current smoothing-row reuse → mode-specific PS state. Consider internal
precision changes only after those layout options and their error budgets are
understood. Recalculate the complete live budget at each step; do not add all
estimates in this document into a promised total saving.
