# Full unsigned Vorbis identification rate

Source commit: `3600c1ee5`. Qualification:
[rate checkpoint](../tests/results/vorbis-xiph-rate-20261026/CHECKPOINT.md).
This applies to the separate source-built Xiph candidate. CYD and C3 radio
projects still register their existing codec components; this candidate is
not added to either application's component list or audio task.

## Representation and API

[Vorbis I section 4.2.2](https://xiph.org/vorbis/doc/Vorbis_I_spec.html)
defines a nonzero unsigned 32-bit identification sample rate. Upstream
[`vorbis_info.rate`](https://xiph.org/vorbis/doc/libvorbis/vorbis_info.html)
is signed `long`. On ILP32/LLP64 that type cannot expose the upper half of the
format range positively. LP64 tests alone cannot detect this limitation.

The owned [public-header fragment](../idf/components/native_vorbis_xiph_port/edits/codec-rate-field.after.h)
declares capability `NATIVE_VORBIS_XIPH_RATE_API=1` and type
`native_xiph_sample_rate_t`. It uses `unsigned long` when
`ULONG_MAX == 0xffffffffUL`, otherwise the original `long`. Consequently the
public member represents every rate from 1 through 4,294,967,295 positively.
No value is clamped, stored as a negative sentinel or rejected merely because
its top bit is set. Zero remains invalid.

This is an explicit **public source-type extension on 32-bit long**. Signed and
unsigned long have the same storage/alignment; C and C++ probes also verify the
entire original struct size, alignment and all field offsets. Layout preservation
does not make old consumers understand newly accepted high values. Rebuild
consumers against the matching generated headers; old signed-long binaries and
`%ld` rate formatters are unsuitable for those values. Use an unsigned format
such as `PRIu32` with an explicit `uint32_t` cast for parsed rates.

The base component retains all 116 original files byte-for-byte. The overlay
changes only the declared codec header and copies upstream `vorbisenc.h` and
`vorbisfile.h` unchanged beside it. Those siblings use quoted `"codec.h"`
includes; leaving them in the base public directory could silently select the
original signed declaration and then block the overlay through its include guard.
The [component CMake](../idf/components/native_vorbis_xiph_port/CMakeLists.txt)
therefore exports only `ported/include` for Vorbis public headers. Library,
metadata, current packet and comment host builds use that same public directory.
The generator records all three public header identities explicitly.

## Parser and consumers

The [identification fragment](../idf/components/native_vorbis_xiph_port/edits/info-rate.after.c)
reads two 16-bit pieces, checks both for EOP and combines them after conversion
to unsigned long. This distinguishes valid `0xffffffff` from the 32-bit reader's
`-1` EOP result on ILP32. The existing positive-rate check continues to reject
zero. Channel, block, framing, version and signed bitrate hint behavior stays
unchanged; all identification prefix errors retain their exact public classes.

Within the compiled decoder, remaining rate consumers are header sequencing
(zero/nonzero) and `vorbis_granule_time` (double division). Both work with the
positive member without a separate arithmetic change. The time tests cover
ordinary granules, the `-1` sentinel and two unsigned-granule branch cases.
Floor0's rate is a different 16-bit setup field and remains untouched.

Encoder-only psychoacoustic/bitrate paths and the retained, uncompiled
`vorbisenc.c`/`vorbisfile.c` convenience implementations contain signed-rate
parameters or intermediate values. Their full-range operation is not qualified.
The metadata ELF may retain decoder symbols through header registry references;
symbol presence does not mean the metadata fixture executes those functions.

## Evidence and limits

- Host ASan/UBSan: 13,492 metadata scenarios over 105 rate values, four channel/
  block/hint profiles, both allocator zero policies, every identification byte
  prefix, exact error classification, duplicate/order checks and fresh recovery.
- Header ABI: all 12 C/C++ public-entry permutations pass on host and in the
  actual ESP32 SDK build. Two host probes intentionally selecting original
  headers first fail the owned-header capability check.
- Actual SDK 6.0.2/Xtensa/QEMU: all 13,492 metadata scenarios pass on ILP32 with
  positive unsigned rate, original 32-byte struct/alignment 4/rate offset 8.
  All 37 library/fixture/probe rows compile. Watchdog and both IDLE checks remain
  enabled. The new metadata worker runs on core 1 with normal priority 0 time
  slicing; production tasks are unchanged.
- Host packet regression: 47,166 scenarios and all original 31/434/738,560 PCM
  bytes pass with max 0 and all 14 relations at the unchanged bound 2. This is a
  host result, not new native audio execution or high-rate hardware playback.

Time tests use a manually constructed read-only `vi` context for the public
granule-time function; they do not initialize DSP state. The SDK/QEMU program
executes H0/H1 metadata and time APIs only. It does not
execute setup parsing, DSP initialization or audio decoding, and does not close
the deferred packet/DSP/amplitude gates. No production image is emitted for
hand-off. No physical audio output is claimed to support arbitrary metadata
rates. Runtime adapter selection, hardware rate validation, general resources,
remaining format ranges and physical acceptance stay in the
[transfer plan](ESP32_CYD_C3_TRANSFER_PLAN.md).
