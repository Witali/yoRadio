# Public owned-book consumer baseline source preparation

This is a source-only diagnostic preparation, not a production repair. It closes the previous owned-book seam's restriction to q_bits2, decode types1/3 and point0. It uses only public Tremor consumer functions, owned table/scalar arrays, exact unchanged setup-parser source, and already retained raw setup fixtures. There is no vendor decoder/backend, external handle, binary inspection, Ogg stream run, synthesis, PCM, physical board or production task change.

The finite selection is fixed: 16 old books, eight additional singleton books, eight q_bits9/16 wide additions, one existing floor0 zero-minimum book and its nonzero-minimum equivalent, plus two separately labelled unit-only zero-delta book variants. All 34 original raw setup selections remain exact. Only the two additive unit variants replace the declared 32-bit minimum/delta float fields with zero; they retain Huffman and multiplicand fields and claim valid book construction only, not independent full-stream qualification. There are exactly 36 cases, 123 codeword probes and 365 vector calls. Integer-valued books use point0, residue point−8 and floor0 point−24. The two fractional floor0 books use representable points−8/−24, giving 439 expected SDK protocol records.

Singletons have distinct preferred-zero and nonpreferred-one tolerance-control probes. The latter are not a full-standard or full-decoder qualification. Existing native original-bit1 packet failures, preferred-zero acceptance, the mixed reference classification and all prior numerical NONPASS results remain unchanged records. This unit never reruns or requalifies their target PCM.

The raw public source is pinned revision `0ad0141e864cfbb130db4f22e279d421832e7336`: `codebook.c` SHA256 `0cfcbdadd7a491bc6bb7c24a2e7d3ed6ce9fb9360122b93631d205fcdf5ac749`, `codebook.h` `88c0cffdfaf4ad0e9143f6c9e99ee9e6d69703ac544655c91e01ae12afcb4172`, BSD `COPYING` `d2ab5758336489da61c12cc5bb757da5339c4ae9001f9bb0562b4370249af814`. Complete original files, download metadata and exact extracted function fragment are retained. `consumer_port.inc` changes only decode_map linkage/name and makes GNU void-pointer byte arithmetic explicit with an unsigned-char pointer. All public multiply, shifts, masking and sequence accumulation remain unchanged. `PORT.diff` records the exact difference.

`oracle.py` independently reads complete raw setup book fields with an LSB reader, assigns prefix intervals, and computes exact rational vectors. It reconstructs canonical q_min/q_del fields, applies the actual `q_del >>= q_bits; q_delp += q_bits` scaling, requires that selected fixtures preserve that rational value exactly, checks every scaled product fits signed32, and evaluates integer output as `Fraction(value) * 2**(-point)`. It applies the sequence flag before scaling and requires complete exact signed32 vectors without fitting. A test that compares unscaled floating vectors to a fixed-point output would be wrong.

The D16 map1 singleton cases explicitly require dec_type2/q_pack0, both sequence flags and every declared fixed-point position. q_pack0 has a zero entry shift, which is valid; it is not diagnosed as an invalid shift. Valid packed zero min/delta fields have zero magnitude and the published point sentinel−9999 (delta point subsequently increases by q_bits). The unchanged public consumer uses point differences without a zero guard. Baseline sanitizers can diagnose an oversized shift even for zero operands. No preemptive guard or arithmetic repair is included, and no claim is made about any opaque implementation using this code.

Three results remain separate:

- Host ASan/UBSan consumer diagnostics use the retained public struct with fixed 32-bit scalar types and explicit owned bitreader callbacks. Host prefix tables are independently constructed valid owned arrays and explicitly do not claim actual target publication. No canonical target parser/ABI is run on an LP64 host.
- SDK publication uses the exact canonical setup `6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c` and unchanged ILP32 ABI `e60e572a2cfc21ea7d9abdeb4994b1c1320c626d75ad64f980eb5ca375255f60`, own bounded allocation/bitreader callbacks, every actual returned q field, complete quantized arrays, array sizes, canaries and normal free. This is the actual target publication test.
- Complete Fraction comparison records every actual vector at the declared point. An honestly recorded mismatch can be a complete diagnostic NONPASS. A sanitizer abort is preserved and cannot count as an available vector or an expected passing control. There is no single catch-all finalpassed flag.

The unmodified ABI deliberately hard-asserts ESP32 ILP32 and alignment. General LP64 host sanitizers cannot compile that exact target ABI as if it were portable. The host header changes only the public codebook header's include to an owned type/reader declaration; host code is consumer-only. Root must supply an existing compiler with actual ASan+UBSan runtime support and pin its real SHA256. If this toolchain lacks either runtime, preserve the build failure and report unavailable coverage. Nothing installs, fetches or silently falls back to a weaker sanitizer configuration.

Only source assembly, metadata/raw setup copies, SHA256 checks and AST/symtable inspection were performed by the preparing agent. No prepared Python import, oracle/test/materializer execution, compiler, unit, decoder, SDK, QEMU or Git command was run. Generated runtime/header hashes do not exist yet and are not invented.

Root-owned construction controls (26 methods: 16 oracle and ten protocol/scope controls), from this preparation directory:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 -m unittest -v test_oracle test_protocol
```

Root-owned materialization, from the worktree root after reviewing the frozen readiness SHA:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 .build/cyd-vorbis-public-book-consumer-prep-01/materialize.py --output .build/cyd-vorbis-public-book-consumer-runtime-01 --readiness-sha256 '<actual reviewed source readiness SHA256>'
```

Root then independently reviews generated contract, all36 raw C-array readbacks, 123/365 counts, field edits, complete vectors, q_bits-scaled fields and actual generated `readiness.json`. Host compiler location is explicitly supplied; no machine-specific unverified compiler path is assumed:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 .build/cyd-vorbis-public-book-consumer-prep-01/run_host.py --runtime .build/cyd-vorbis-public-book-consumer-runtime-01 --runtime-readiness-sha256 '<actual reviewed generated runtime readiness SHA256>' --compiler '<existing reviewed Clang/GCC absolute path>' --compiler-sha256 '<actual existing compiler SHA256>' --output .build/cyd-vorbis-public-book-consumer-host-01
```

Root's read-only WSL metadata query completed with terminal0/chunk a953ba: `/usr/bin/python3` is Python3.12.3 (Aug31 2026; GCC13.3.0); `/usr/bin/gcc` resolves to `/usr/bin/x86_64-linux-gnu-gcc-13`, SHA256 `1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26`, Ubuntu GCC13.3.0-6ubuntu2~24.04.1. No Windows Clang/GCC is assumed. This confirms compiler metadata only; sanitizer runtime availability is still an actual build gate. The explicit existing-tool WSL recipe is:

```powershell
wsl.exe --cd /mnt/c/Work/yoRadio/.worktree/esp32-cyd-c3-review -- python3 -B .build/cyd-vorbis-public-book-consumer-prep-01/run_host.py --runtime /mnt/c/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/cyd-vorbis-public-book-consumer-runtime-01 --runtime-readiness-sha256 '<actual reviewed generated runtime readiness SHA256>' --compiler /usr/bin/gcc --compiler-sha256 1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26 --output /mnt/c/Work/yoRadio/.worktree/esp32-cyd-c3-review/.build/cyd-vorbis-public-book-consumer-host-01
```

The baseline uses `-std=c11 -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer`, one fresh owned process for each of 365 calls, retained stdout/stderr, terminal/timeout facts and binary hash. It continues after individual numerical/sanitizer NONPASS and preserves all rows. It does not label baseline failures expected passes. SDK/QEMU execution requires the separate reviewed controller preparation described in `SDK-PLAN.md`; this source freeze does not pretend that controller or actual target execution already exists.
