# FAAD2 Q14 arithmetic and applicability to the ESP32-C3 decoder

## Conclusion

FAAD2's `FIXED_POINT` build uses `REAL_BITS=14` for one fixed-point domain.
This means **14 fractional bits in a signed 32-bit integer**, not a 14-bit
mantissa or 14-bit PCM. Changing that binary point alone saves **zero storage
bytes**. Our Espressif/PacketVideo decoder already uses integer fixed-point
arithmetic, with different scales in different processing stages.

Selective compact history storage remains useful, but it is a separate change
from FAAD's Q14 arithmetic. Preserve native DSP arithmetic while qualifying
each packed area and the combined output against the current
[maximum +/-3 signed-16 PCM LSB requirement](ESP32C3_AAC_PRECISION_POLICY.md).

## What FAAD actually implements

Audited upstream revision `e8e76f0a44db45aed773a3f62fe35a63c867a738`.
All 129 files in the retained source archive matched its local extraction.
The [audit manifest](../tests/results/faad2-q14-audit-20261003/audit.json)
records the archive, source and compiler-output hashes.

| Definition | Meaning |
| --- | --- |
| `FIXED_POINT` | Selects fixed-point code in `common.h`; the default alternative uses float32 |
| `real_t = int32_t`, `REAL_BITS=14` | Four-byte signal values with 14 fractional bits |
| `COEF_BITS=28`, `FRAC_BITS=31`, `Q2_BITS=22` | Other coefficient/value domains retain different binary points |
| `complex_t = real_t[2]` | Eight bytes per complex value in either fixed int32 or float32 mode |

Definitions are in upstream
[`fixed.h`](https://github.com/knik0/faad2/blob/e8e76f0a44db45aed773a3f62fe35a63c867a738/libfaad/fixed.h)
and [`common.h`](https://github.com/knik0/faad2/blob/e8e76f0a44db45aed773a3f62fe35a63c867a738/libfaad/common.h).
`REAL_CONST` scales and rounds constants by `2^14`. For example, the real value
1.5 is stored as integer 24576. Its quantization step is 1/16384 in that domain;
this is not a bound on final PCM error after the complete decoder.

The portable `MUL_R` forms a signed 64-bit product, adds a half-unit rounding
constant, and shifts right by 14. In mathematical notation, with wide
intermediates, it is `(a*b + 8192) >> 14`. Other multiply helpers use their own
shifts. The fixed header marks 14 as the maximum fractional-bit setting for
fixed SBR, rather than a selectable 14-bit storage mode.

Reducing `REAL_BITS` trades fractional resolution for headroom within the same
32-bit container. Substituting `int16_t` is a different operation: int16 Q14
only represents approximately -2 to +2, instead of the int32 Q14 range of
-131072 to just below +131072. It cannot safely hold arbitrary existing values.

## New RV32 compiler check

Compiled a [small wrapper](../tests/results/faad2-q14-audit-20261003/precision_probe.c)
against the unchanged pinned `fixed.h`, using Espressif GCC 15.2.0, `-O3`,
`-march=rv32imc`, `-mabi=ilp32`. Static assertions check four-byte `real_t` and
float; the object's constant data confirms 8-byte fixed complex values.
The [disassembly](../tests/results/faad2-q14-audit-20261003/disassembly.txt)
contains:

| Isolated wrapper | Instructions including return | Code bytes | Product instructions |
| --- | ---: | ---: | --- |
| FAAD Q14 `MUL_R` | 10 | 28 | `mul` and `mulh` |
| Diagnostic Q12 expression | 10 | 30 | `mul` and `mulh` |

Q12 here changes only the macro expansion in one wrapper. It is **not a full
decoder build or a qualified FAAD configuration**. Both wrappers still compute
the full product. Different rounding-immediate encodings explain the code-size
difference; instruction counts do not establish equal cycles or a decoding
speedup. No new PCM decode, physical CPU benchmark or firmware build was
performed for this audit.

To reproduce, use the pinned source obtained by the existing
[FAAD comparison workflow](FAAD2_HISTORY_SCALING_20261001.md). With its `libfaad`
directory and the cross-toolchain on the search path, run from this worktree:

```powershell
riscv32-esp-elf-gcc -std=c11 -O3 -march=rv32imc -mabi=ilp32 -I"<FAAD-source>/libfaad" -c tests/results/faad2-q14-audit-20261003/precision_probe.c -o .build/faad-q14-probe.o
riscv32-esp-elf-objdump -d .build/faad-q14-probe.o
```

The retained manifest contains the exact original compiler command. The object
file is evidence for this check, not an application image.

## Why a single shift does not transfer to our decoder

FAAD's fixed QMF analysis shifts input right by four and omits a factor of two
used in the floating output path. Fixed PS energy calculations explicitly
account for the resulting signal and energy scales. The measured fixed-integer
to floating QMF RMS ratio is about **512**, not 16384. Its synthesis and final
PCM conversion also depend on those conventions. See the
[source and scaling comparison](FAAD2_HISTORY_SCALING_20261001.md).

Our retained
[`calc_sbr_anafilterbank` pseudocode](audits/esp32c3-aac-decompile-20260930/pseudocode/calc_sbr_anafilterbank.c)
instead starts with int16 core PCM, shifts by 16 before high-word products,
and invokes `analysis_sub_band`. This is evidence of a different pipeline, not
a universal Q-format for every native field. A Q14 rewrite would require
consistent changes to producers, consumers, coefficients, energy/gain/noise
calculations and output scaling, with overflow and PCM checks throughout.

Simply rescaling a stored value by a power of two and undoing it after a
shared-exponent quantizer does not generally improve precision: the exponent
changes with the value. The earlier test verified this for 98,304 interior
cases; exponent-floor and saturation boundaries are exceptions requiring
explicit checks.

## Existing measurements relevant to the decision

These are retained experiments, **not new audio measurements for this audit**.
Storage quantizers below are distinct from Q14 arithmetic.

| Experiment | Observed output difference | Storage / allocation result | Current interpretation |
| --- | --- | --- | --- |
| [Pristine FAAD float32 versus fixed](FAAD2_FLOAT_FIXED_COMPARISON_20261001.md) | LC at most 2 LSB; real captures 2-6 LSB outside ABBA; much larger HE/PS differences, including ABBA PS onset | Both scalar types occupy four bytes | Q14 does not establish equivalence within +/-3 LSB; causes of large differences remain unresolved |
| [14+14+4 current-decoder history probe](ESP32C3_AAC_PACKED_HISTORY_20261001.md) | At most 3 LSB on real captures, 7 on synthetic HEv2 | Allocation unchanged | Broad history scope fails the current +/-3 gate |
| [14+14+4 actual PS delay writes](ESP32C3_AAC_PS_WRITE_PORT_20261001.md) | Maximum 3 LSB across 81 paired comparisons | Delay payload 4936 -> 2468 B; actual heap saving zero | Meets this corpus's precision gate; owner integration and speed qualification remain open |

The PS-write prototype adds 26.681% / 40.658% QEMU guest instructions on the
active synthetic HEv2 / ABBA inputs. That includes prototype instrumentation
and is not measured physical CPU load. It is a reason to optimize and measure
the implementation before production, not to infer a faster decoder from a
smaller representation. Independent passing variants must also pass together;
their individual maximum errors cannot simply be treated as a combined bound.

## Implementation decision

1. Keep native fixed-point DSP arithmetic as the reference; do not add a
   misleading RAM-saving `REAL_BITS=14` firmware flag.
2. Continue the [per-area memory experiments](ESP32C3_AAC_MEMORY_EXPERIMENTS_20261002.md):
   compact persistent storage and reconstruct native operands at use sites.
   The selective PS 14+14+4 result is a candidate, not permission to replace all
   QMF arrays with that format.
3. Qualify changed owner layouts, every reader/writer/reset/free path, cumulative
   +/-3 PCM error, actual heap reclaimed and physical performance. Preserve full
   existing AAC/SBR/PS functionality and output rates.

Firmware arithmetic, build defaults and the connected board were unchanged by
this research. Existing physical HE-AAC memory failures remain unresolved.

## Validation of the retained evidence

All 19 existing checks passed: `tests/test-faad-history-comparison.py` (6),
`tests/test-faad-arithmetic-comparison.py` (7), and
`tests/test-faad-ps-patch.py` (6). These validate saved measurements and analysis
helpers; they do not rerun full decodes. The three new probe/output hashes and
all local links in this report were also checked.
