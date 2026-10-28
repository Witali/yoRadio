# Exact window products and immutable borrowed views

The [component](../../../idf/components/native_vorbis_window_exact/README.md)
and [design](../../../docs/CYD_VORBIS_EXACT_WINDOW_DESIGN.md) retain a complete
odd product of two binary64 significands in at most 106 bits, with an unchanged
signed64 base exponent and a separate shift in [-2148,1023]. Their exponent
sum is symbolic. No floating product, narrowing, overflow or underflow occurs.
A copied-descriptor view applies the existing window geometry on demand and
needs no full window-output array. Existing APIs and production remain unchanged.

Final host04, GCC 13.3 ASan/UBSan with assertions enabled:

- 64,940 scalar rows, 70 invalid-domain rows, all 2,047 finite sample exponent
  fields, all 1,024 factor exponent fields and all 53 significand widths for
  both operands. Products reach 106 bits and both shift endpoints. Full
  signed64 base endpoints are retained without arithmetic on them.
- All 17,962 prior nonzero products rounded to zero remain exactly nonzero,
  including all 13,767 with base exponent >=1074. No witness is deduplicated.
  The pinned saved overlap capture is read solely as data; its 864 records,
  1,197,984 terms, raw source/history bits and actual binary64 coefficients
  reconstruct the complete witness set. Identity SHA256:
  `844e6d38700b6e8c6d8683d7afcc49d7a46289a1a4d1735d3cc1a554826af472`.
- Every one of 587,520 view results across all 36 size configurations and
  288 shapes agrees with the independent unbounded integer-ratio product
  oracle. All 8,160 actual coefficients retain the existing 70-digit sine
  reference bound 2e-15; maximum error is 3.3306690738754696e-16. Geometry,
  zero support, unity plateau and descending indices match the existing
  owned window and pinned Xiph reference, including trailing-zero placement.
- Positive/negative zero, subnormals, maximum finite magnitudes, sign,
  invalid sample/factor values, both extreme base scales, and alternate
  floating rounding modes are covered. The integer product is rounding-mode
  independent. Every refusal preserves actual result/view/input bytes and
  guards, including injected late NaN/Inf/factor values before restoration.
  Descriptor copies are used after the original descriptors are overwritten.
- 10,360 expected refusals / 14,889,244 guard checks; 13 corrupted captures
  are rejected. All three supervised commands and the outer controller exit0,
  every child is reaped/group gone, and sanitizer stderr is empty.

Source-only GCC 15.2 C/C++17 profiles pass ten commands and produce six ELF32
relocatables for LX6/RV32IMC. Both production units have zero Clang warnings
and errors. Own frames at -O2/-fno-inline: scalar product 112/112 B,
view preparation 144/160 B, indexed read 48/32 B; these exclude callees and
task high-water. Fixture lint04 has 23 displayed / 44 generated warnings and
zero errors. Raw stderr records five system-header warnings hidden by the
tool's defaults. Displayed diagnostics are the reused C-fixture include and
pre-call byte-snapshot comparisons; no custom suppression or configuration
weakening was added.

Every attempt is retained. Host01 stops at sandbox WSL E_ACCESSDENIED before
GCC; host02 passes all numerical comparisons; host03 adds 13 corruption
controls and explicit factor-width accounting. Lint01/02 need the actual
ESP32 fenv core-header directory. Lint03 then passes but shows a possible
malloc(0) in the fixture because analysis cannot infer the successful shape
API's postcondition. An explicit legal-size CHECK documents that postcondition
in host04/lint04. Inputs and numerical captures are byte-identical across
host02/03/04; the last run adds 288 contract assertions. Production sources,
comparison bounds and corpus membership do not change.

Source profile01 encounters Windows DLL error623 before the compiler starts;
profile02 passes in the normal approved tool runtime with identical sources.
A root driver probe insertion accidentally appended a C++ declaration after
its JSON receipt. Both raw reports are preserved, alongside corrected JSON
and exact transformation/hash receipts; no compiler rerun or input change is
used for that metadata repair. The pure verifier checks both representations.

`captures.zip`: 394 members, 247,543,897 decoded bytes; 43,574,016 ZIP bytes.
SHA256: `ba372710a086d31849ad2aab28075549480490a499855c131882c4dc0ab50989`.
`manifest.json` SHA256:
`7610b9255c57b670922696d9625dc5b7c39754e9a2db7931bfd636620624c6b2`.
All raw inputs, captures, models, sources, diagnostics, command receipts,
source-profile objects and final seal are retained. Three rebuildable host
executables are omitted with byte counts/hashes recorded. The
[pure verifier](../../verify-vorbis-window-exact-checkpoint.py) checks every
member, all operand identities/products/views and corruption controls using
pinned live readers, with no archived execution, extraction or child command.
`replay.json` records the complete replay; `verification.json` independently
seals exact artifacts and that completed replay without repeating the numerics.
Two pre-Python launch errors (PowerShell redirection and the disabled PATH
application alias) are retained in `replay-launches.json`; neither ran the
reader. The third launch performs the one complete successful pure replay.

This removes window-product representation loss in the new API only. Exact
products must still reach adjacent-block addition and final PCM without a
binary64 narrowing step. Approximate coefficient/IMDCT/gain errors, wider
fallback, full31 PCM/bound2/all14 relations, granule/output/raw/radio integration,
native/resource/performance and physical qualification remain open. No overlap,
PCM, SDK/QEMU or production radio code is executed by this campaign; previous
deferred scopes and the old underflow captures remain unchanged.
