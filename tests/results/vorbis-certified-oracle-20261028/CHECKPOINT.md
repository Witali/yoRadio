# Independent host floor0 oracle checkpoint

This checkpoint qualifies the MPFR4.2.2/GMP6.3.0 host reference at the retained
exact inputs. It does not select a production implementation or certify every
legal numerical domain.

The reference imports each affine LSP exactly, evaluates independent direct
cosines with directed MPFR arithmetic, and encloses the denominator and log2
gain. It exports exact dyadic bounds and both arbitrary-size integer floors;
it never constructs the enormous linear gain. Exact absence, unity, pole and
indeterminate outcomes remain distinct from precision/resource refusal.

The retained successful campaign covers all447 front-end packet identities
(434 original packets plus13 supplemental cases), deduplicated into8202 exact
numerical requests including10 analytical examples. Every possible supplied
Bark index of each active floor0 channel is represented. Floor1, absent floor0
and undefined mapping entries remain explicitly accounted for in identities.
There are8194 nested256/512-bit log enclosures; two requests initially require
more precision. Requests8000 and8198 retain actual1024/2048/4096-bit refinements
and resolve their integer floors at4096bits. The tiny finite LSP example proves
an integer exponent of at least1572bits. This is a retained-case result, not a
universal precision bound.

All13 actual commands have nonce-bound terminal/reaped process-group receipts.
The protocol campaign exits2 as expected, rejecting16 malformed records while
retaining its valid middle record. An above-budget8193-bit request returns a
typed resource refusal under the explicit8192-bit caller budget. Campaign01
retains a WSL access refusal before the Linux child; the earlier dependency
source-preparation assertion is also retained. Neither is presented as an
arithmetic execution.

`captures.zip` contains97 regular members,30,794,467 decoded bytes:

- ZIP:3,817,347bytes; SHA256 `f0040b4512daeea2f4e690e6d8f3f6378e645ef616065622de39b80f683264db`.
- Manifest SHA256 `910574cdb63aca2cac52db07952df810ae7e6feda6477643c90a17fea0cd5c1d`.
- Three explicitly hashed derived omissions: the rebuildable host executable
  and two copies of the locally built static MPFR library.
- Executed/live runner SHA256 `f34cf3eacdaf02d0e1fcd5a8a08063e69aa302ad1f8b3f4f8704b40bed20fdbb`.
- Executed/live C oracle SHA256 `a5b20411d709d8b255f23909d6f618ec56cd85219aa7b7e08b69dd0e4fa56408`.

The C oracle was compiled with AddressSanitizer/UndefinedBehaviorSanitizer and
strict warnings; all retained oracle stderr logs are empty. The linked MPFR
static dependency and installed GMP library **were not sanitizer-instrumented**.
Their source/build/header/library identities are retained; this checkpoint does
not claim sanitizer coverage inside those dependencies or recoverable host OOM.

The pure verifier checks every ZIP member and omission, all trusted live code
pins before imports, complete request/identity lineage, every saved enclosure
and floor, analytical examples, refinements, protocol controls and process
receipts. It reads archived code only as data, never extracts archives or starts
the compiler, C oracle, MPFR, SDK or QEMU. `replay.json` records its result.
The successful pure replay also verifies8201 nested denominator intervals and
ten malformed-name/response controls. Its finite tiny-LSP floor has1573bits.
The first pure replay rejected the budget-control file's actual Windows CRLF
encoding because the reader expected LF. That failed reader/result is preserved
locally; the correction checks the exact executed CRLF bytes without changing
mathematical comparisons or repeating the C campaign.
Repeat into a fresh path from the repository worktree:

```sh
python -B -X utf8 tests/verify-vorbis-certified-oracle-checkpoint.py --output .build/vorbis-certified-oracle-replay-new.json
```

The verifier also needs the pinned live readers and retained
`tests/results/vorbis-floor0-spectrum-20261028/captures.zip` to reconstruct all447
inputs independently. A changed executable source fails the identity check;
archived scripts are never substituted for trusted live code.

`COPYING` and `COPYING.LESSER` are the unchanged MPFR license texts from the
actual local dependency installation; their hashes match its retained build
receipt. They accompany the archived MPFR header.

No MCU gain implementation, discrete Bark-index certificate, wider transform,
history/PCM continuation, native execution or production selection is qualified
by this host oracle checkpoint. It does not change task cores or priorities.
