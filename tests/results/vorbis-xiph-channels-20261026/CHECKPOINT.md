# Xiph channel scratch checkpoint

Source commit: `ddd049bc2` (`fix: bound Xiph channel scratch stack use`).
This is an independent stack-storage change in the separate Xiph candidate.
The production CYD/C3 radio selection, task cores, priorities and stack sizes
are unchanged. No production firmware image is built or handed off here.

## Change and tradeoff

The four channel-sized arrays in `mapping0_inverse` and the outer pointer array
in residue0/1 `_01inverse` no longer use `alloca`. Each has a fixed two-channel
local buffer. Mono/stereo introduces no arena calls at these five sites. More
channels use the existing transactional block arena, with every required
allocation checked and `OV_EFAULT` propagated to synthesis. No-work residue
returns before allocating its wider outer pointer array.

All decoding loops, VQ additions, coupling, floor application, transform order,
public ABI and original registry signatures remain unchanged. There is no new
format cap. Partial wider allocations remain reachable through block ownership
and are released by the existing close/reopen contract.

For valid ESP32 headers, each mapping array is at most 1,020 source-level bytes
(channels 1–255); all four total 4,080 bytes. The residue outer array is at most
1,020 bytes. Wider streams now consume arena heap for this storage instead of
channel-dependent task stack. Fixed local arrays occupy 40 source-level bytes
combined. Alignment, compiler frames and callees are separate. Mono may use
slightly more fixed local storage. This is not a measured total RAM or speed
saving, and maximum 255-channel runtime/heap is not qualified.

## Host result

The unchanged [packet fixture](../../native/vorbis_xiph_packets.c) and
[owned runner](../../test-vorbis-xiph-packets.py) pass **47,166 scenarios** under
ASan/UBSan, with assertions, leak detection and unchanged floating-point options:

| Layer | Scenarios | Required refusals | Optional refusals |
| --- | ---: | ---: | ---: |
| Transactional arena | 23 | Individual checks | Previous focused suite |
| Original31 packet sweeps | 27,875 | 12,930 | 124 |
| Synthetic and direct no-work controls | 19,268 | 9,232 | 72 |

The original31 allocation counts are identical to the preceding packet port,
confirming the stereo fast path. The larger synthetic count reflects additional
allocation/refusal points in the same 36 four-channel streams, not new formats.
Both floors, all three residues, arena-cold/warm storage, both zero-size policies,
nominal EOP, every observed ordinal and full close/three-header replay are
covered. The 48 direct no-work controls still assert zero allocation attempts
and leave the first refusal armed. Same-process float comparisons check recovery
identity; they are not an independent numerical reference for all synthetic
formats or for maximum 255-channel playback.

All original **31 streams / 434 packets / 738,560 S16LE bytes** remain byte-exact
against the independent reference: maximum error **0**, original allowed bound
**2**, all **14** exact relations pass. No numerical tolerance or reference is
changed, and no normalization, alignment fit, trim or resampling is applied.

## Xtensa compiler observation

Seven retained commands use the actual Xtensa GCC 15.2.0 tool to capture version,
machine, ILP32 macros and four source-only objects. The old/new sources differ
only by the corresponding two scratch-storage fragments. Both versions use the
same `-O2 -fno-inline -fstack-usage -fno-fast-math -ffp-contract=off` flags.

| Function | Before own frame | After own frame |
| --- | --- | --- |
| `mapping0_inverse` | 96 B plus dynamic arrays | 128 B static |
| `_01inverse` | 112 B plus dynamic array | 112 B static |

The raw `.su` files, source and relocatable ELF32/Xtensa objects are retained.
The observation establishes removal of these dynamic local arrays under the
stated compiler options. It is **not** a complete decoder call-chain bound,
production compiler/inlining measurement, task high-water mark, SDK application
build, emulator run or physical result.

Clang-Tidy analyzes all 22 library and three fixture units with explicit Xtensa
flags and Picolibc/builtin headers: **316 warnings, zero errors**. Eight new
warnings concern valid C multilevel-pointer conversions and size_t-to-long
products. Parsed channels 1–255 bound every new product to 1,020 bytes on ILP32,
so the narrowing is representable; pointer conversions are normal C arena
assignments. Existing diagnostics remain visible. Nothing is suppressed, and
encoder paths/general stack use are not upgraded by this result. Pure exact
generation validation passes all 16 tests with the unchanged 33-edit inventory.

## Deferred work and evidence

The independent [wide floor0 amplitude audit](../../../docs/CYD_XIPH_FLOOR0_AMPLITUDE_DEFERRED_20261026.md)
identified width 31–63 gaps and a separate signed-long rate API issue on ILP32.
Automatic review stopped amplitude-test preparation with a possible
cybersecurity-risk response. No proposed fixture files were created and no
amplitude change followed. The unchanged floor0 inverse fragment is hash-pinned
in this checkpoint; ordinary corpus results do not qualify those wide fields.

The [packet target preparation](../../../docs/CYD_XIPH_PACKET_TARGET_DEFERRED_20261026.md)
and [older DSP watchdog gate](../../../docs/CYD_XIPH_DSP_TARGET_DEFERRED_20261026.md)
remain deferred. This source-only compiler observation does not prepare or run
either target. General OOM/stack/resource coverage, maximum channels, numerical
ranges, radio integration and physical acceptance remain open.

- Base manifest: `897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14`.
- Current port manifest: `400e4c3f3b01fec11d7d051d3a0cef62cc7e0528eb71962bd6e015ab8bf95355`.
- Generator: `873472c0a30c955fa5d81528195ef71e4f476915b1ac8b64dd1d04dbae7f0251`.
- Unchanged packet fixture: `1f0d8a34f1afac3d75ecf71f0e4d21fe5c018a1ec587d9da6a1b3eae6d1247fb`.
- Archive: [captures.zip](captures.zip), **4,432,437 bytes / 768 members**.
  SHA256: `cc73cdc5798c8471b05194e2ab902ded5c0464da35386bb49bb7dc650a7f2521`.
- Archive manifest: `51f85de954e54d9b08506632f4f678e3334f702f308479e960b72c04310db97d`.

The [offline verifier](../../verify-vorbis-xiph-channels-checkpoint.py) imports
only the hash-pinned trusted local preceding packet verifier, never archived
code. It rechecks every member, exact source transforms, 62 owned host commands,
all original PCM/relations, the four compiler objects/raw `.su` observations,
Clang streams and retained deferral fields. It performs no extraction, subprocess
or decoder execution. Native/DSP/amplitude/max255 qualification remains false.

```text
python -B tests/verify-vorbis-xiph-channels-checkpoint.py tests/results/vorbis-xiph-channels-20261026/captures.zip
```

Actual collection and successful offline-verification receipts are saved in
[publication/](publication/) outside the ZIP to avoid a self-reference.
