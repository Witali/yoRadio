# AAC core and remaining field-offset audit — 2026-10-01

The current readable export is [pseudocode/](pseudocode/). It replaces verified
numeric structure accesses with named fields throughout the native AAC core,
bit readers, SDK wrapper and their callers. All **186 functions** from the
pinned analysis ELF are retained at their original addresses and body sizes.
The vendor archive and executable instructions are unchanged.

This extends the [previous SBR/PS export](../esp32c3-aac-symbolic-20261001/README.md).
The RV32 compiler now checks **63 layouts**, the importer assigns pointer roles
to **94 functions**, and type propagation changes **98 function exports** versus
the original untyped export. Two data tables are resolved by their ELF symbols,
`hcbbook_binary` and `samp_rate_info`, without hardcoded absolute addresses.

## Replaced accesses and evidence

| Storage / former access | Named view | Native functions checked |
| --- | --- | --- |
| Core + `0x18`, bit-reader words 0–4 | `core->input`, `buffer`, `used_bits`, `available_bits`, `input_length`, `alignment_offset` | DecodeFrame, ADTS/ADIF/PCE readers, byte_align, all eleven Huffman codeword readers |
| Core + `0x2c`, `0x70`, `0x74`, `0x78` | `program`, `long_window`, `short_window`, `window_map` | InitLibrary, DeInit, get_prog_config, set_mc_info, infoinit |
| Core + `0x8c` … `0xec` | `mc`, channel descriptions, `ltp_buffer_state` | set_mc_info, huffdecode, get_tns, DecodeFrame, sbr_applied |
| Core + `0xc0` | `mc.ps_present` | sbr_applied copies `ps->detected` here; DecodeFrame doubles the output channel count when set |
| Channel + `0x2480` / `0x2484` / `0x24a8` | Spectrum pointer, shared parsing state, window sequence | InitLibrary, huffdecode, getics, DecodeFrame |
| Shared parsing + `0x1f4`, `0x4ac`, `0x6ac`, `0x8ac`, `0x8cc`, `0xacc`, `0xad0` | Window, factors, codebooks, groups, Q formats, maximum band, LTP | getics, huffdecode, get_ics_info, lt_decode |
| Coefficient block + `0x1000` / `0x1d18` | `spectral[n].shared` / `spectral[n].mask` | InitLibrary and Huffman callers |
| Core + `0x8a60`, `0x8a74`, `0x8a78`, `0x8a7c` | SBR bitstream, scratch, shared samples, owning workspace pointer | InitLibrary, DeInit, getics, SBR processing |
| SBR cached reader words 0–4 | `cursor`, `cached_bits`, `cache`, `read_bits`, `total_bits` | buf_getbits, buf_get_1bit, GetNrBitsAvailable, sbr_crc_check, sbr_read_data |
| Wrapper words and byte + `0x50` | Core, extra PCM buffer, pending bytes, external API, `saved_plus_enabled` | esp_aac_dec_open/decode/reset/close |
| TNS filter / pulse / section offsets | Typed filter, pulse and section members | get_tns/apply_tns, get_pulse_data/pulse_nc, huffcb/hufffac |
| Autocorrelation words 0–8 | Real/imaginary correlation coefficients and determinant | calc_auto_corr, calc_auto_corr_LC, high_freq_coeff variants |
| Envelope scratch + `0x100` … `0xa00` | Estimated/reference/gain/noise/tone arrays and harmonics | calc_sbr_envelope and its energy/filter callers |
| Fraction results, square-root cache, patch descriptor | `mantissa`, `exponent`, `input`, `output`, `count`, `start_band` | pv_div, pv_sqrt, calc_sbr_envelope, sbr_create_limiter_bands |
| Table base + index × stride + field offset | `hcbbook_binary.entry[i].signed_codebook`, `samp_rate_info.entry[i].long_bands` | getics, huffspec_fxp, infoinit |

The native core's `0xc0` field is a **PS-present flag**, not a channel count.
The older minimal runtime view called it `channels`; the extended analysis gives
it its verified meaning. Likewise, external API offset `0x34` is **bitrate** in
this binary, and wrapper byte `0x50` saves the AAC-Plus setting for reset.
These meanings were checked against computations and writers, not copied from
an upstream structure with a different layout.

The analysis header is
[`aac_analysis_core.h`](../../../tools/codec_benchmark/aac_analysis_core.h),
with explicit native argument roles in
[`aac_analysis_core.py`](../../../tools/codec_benchmark/aac_analysis_core.py).
Numeric ABI assertions remain at this boundary. They reject accidental changes
in sizes or member positions; live field references use names.

## Memory and ownership

No region is shortened or moved. In particular:

- Core: **35,460 bytes**; channel: **9,396 bytes**; wrapper: **84 bytes**.
- The full **8,192-byte coefficient block** remains available to later DSP
  phases. Its parsing view names shared state and the mask; it does not prove
  those regions are free during another phase.
- The separately allocated workspace remains **12,288 bytes**. The envelope
  view covers its 4,096-byte scratch part and retains all sixteen rows, including
  the five rows not named by that phase.
- The SBR cached reader is **20 bytes**, including the total-bit limit used by
  CRC and GetNrBitsAvailable. It is distinct from the core's 20-byte reader.
- Native allocation/free sites were checked for the program (860), windows
  (696 each), SBR bitstream (1,044), SBR owner (55,128), controller (1,180),
  workspace and wrapper. These labels are not permission to reduce them.

Field-order references are the pinned
[PacketVideo tree](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/),
including [autocorrelation](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/calc_auto_corr.h)
and [envelope scratch uses](https://android.googlesource.com/platform/frameworks/av/+/437ced8a14944bf5450df50c5e7e7a6dfe20ea40/media/libstagefright/codecs/aacdec/calc_sbr_envelope.cpp).
Native layouts take precedence. Exact compiler inputs and relevant SDK headers
are retained under [implementation-snapshots/](implementation-snapshots/).

## Remaining numeric expressions

The reproducible [inventory](access-review.json) scans every function. Its
lexical candidates fall from **1,733 in the previous named export to 888**
(2,256 in the raw export). This is a count of candidate lines, not a count of
incorrect addresses or a proof that every remaining expression is safe.

Remaining expressions include sample indices, FFT butterflies, filter strides,
coefficient lookup arithmetic and optimized aliases. Examples requiring care
before a source rewrite are the envelope scratch cursor's `+0x400` … `+0x700`
accesses, PS pointers advanced across adjacent arrays and the negative alias in
`sbr_decode_envelope`. Their enclosing regions are named, but Ghidra still loses
some types while following optimized cursors. Do not replace these mechanically
or claim the residual list is empty. The native program word at offset 8 remains
explicitly unidentified instead of receiving an invented meaning.

Three functions retain Ghidra type-propagation warnings: `ps_bstr_decoding`,
`sbr_reset_dec` and, after the additional scratch views, `sbr_dec`. The known
invalid vendor reset location remains visible as `core[2]`; labeling it does not
repair the vendor binary. The existing guarded runtime repair is a separate
change. This export remains **inferred pseudocode, not compilable recovered C**.

## Verification and reproduction

All 21 checks passed: seven new core-symbolic tests, five previous symbolic
tests, five RV32 ABI tests, and four full-decompilation inventory tests. Checks
cover exact export/source hashes, all 186 function identities, pointer depth,
native argument positions, named lifecycle accesses and compiler rejection of
deliberately shifted fields. Table annotations verify the table bytes are unchanged.
No decoder arithmetic or executable firmware was changed by this audit.

Generate types with the existing RV32 compiler, then import a fresh analysis
project using the same pinned ELF and function inventory as the raw audit:

```powershell
python tools/codec_benchmark/prepare_aac_symbolic.py `
  --compiler PATH/TO/riscv32-esp-elf-gcc.exe --include-core `
  --output .build/aac-core-repeat
# Use the analyzeHeadless command from the preceding symbolic audit, replacing
# its output/project directory with .build/aac-core-repeat.
python tools/codec_benchmark/audit_aac_symbolic.py `
  --raw docs/audits/esp32c3-aac-full-20261001/pseudocode `
  --symbolic .build/aac-core-repeat/pseudocode `
  --output .build/aac-core-repeat/access-review.json
python tests/test-aac-core-symbolic.py --compiler PATH/TO/riscv32-esp-elf-gcc.exe
python tests/test-aac-symbolic.py --compiler PATH/TO/riscv32-esp-elf-gcc.exe
python tests/test-aac-abi.py --compiler PATH/TO/riscv32-esp-elf-gcc.exe
python tests/test-aac-full-decompile.py
```

Require both the successful import/export log markers and the complete manifest;
Ghidra may exit with code zero after a script error. Omitting `--include-core`
preserves reproduction of the older SBR/PS export. `provenance.json` protects
the exact evidence bytes; this explanatory README is maintained separately.
