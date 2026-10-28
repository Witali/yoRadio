# Remaining certified floor0 gain and wider synthesis

The ordinary public pipeline now passes the complete original31/434-packet
corpus on host, ESP32 and C3. That closes its finite PCM contract; it does not
prove every encoded numerical domain. The persistent raw owner preserves
distinct incomplete numerical outcomes instead of relabelling them malformed.

## Two different representation failures

The current floor0 boundary first retains53 significant bits of the scaled
logarithm. A stored log exponent>=53 has no binary64 fractional precision and
returns `NEEDS_PRECISION`. Lesser exponents still have no universal upstream
denominator/transcendental error certificate. The later common binary64 grid
needs a maximum/minimum top-bit span<=1660 and otherwise returns `NEEDS_WIDER`.
Increasing an integer exponent from64 to128 bits solves neither general issue.

A concrete legal finite example shows why. At order1/Bark index0, choose exact
affine LSP phi=2^-788 (`minimum_bits=1`, minimum multiplier1, delta multiplier0).
With amplitude bits8, raw amplitude1 and offset60, scaled amplitude A=4/17.
The creator equations give sqrt(D)=1-cos(phi)>0 and sqrt(D)<=phi^2/2=2^-1577.
Thus log2(G)=(0.11512925/ln(2))*(A/sqrt(D)-60)>2^1571. The integer part of this
logarithm, which is the exponent of the linear gain, needs at least1572 bits.
It is finite, not an exact pole or a malformed packet. Per-bin int64 or int128
scales cannot represent it. The upstream float cosine rounds away this example;
upstream is a normalization/algorithm reference here, not its accuracy oracle.

## Next numerical implementation requirement

Implement a caller-workspace, precision-controlled enclosure of the mathematical
log gain at one supplied exact Bark index. Keep signed variable-length integer
mantissas and binary scales; use directed bounds rather than a single libm
approximation. Split the integer exponent without narrowing to a machine word.
An interval crossing an integer boundary must refine or retain both endpoints.
Resource/precision refusal must be retryable and retain original provenance.

The enclosure needs exact raw/(2^bits-1), the exact specification decimal
0.11512925, directed pi/phase/sine bounds, nonnegative P+Q products, square
root, division and log2 bounds. Exp2 refinement is a following conversion.
The existing phase-grid certificate proves separation and a phase-only error
budget; it does not bound every downstream sine/libm/gain error. A fixed2304-bit
precision promise is not justified across all encoded orders/ranges. Discrete
Bark indexing also uses libm before integer floor and needs its own certificate.

Existing exact affine VQ, residue/coupling and joint integer multiplication are
useful inputs. The exact106-bit window and final PCM modules preserve their
supplied operands; their fixed int64 bases do not cover this new exponent.
Independent high-precision/direct-cosine checks must differ from the production
half-angle algorithm and retain all447 frame cases and the original full corpus.

## Required downstream continuation

Independent wide exponents must survive transform sums, cancellation, windows
and history until final S16. A refined transform must retain previous-block
precision/provenance before frame scratch expires. Switching an exceptional
packet to a different history or merely feeding exponent buckets through the
old approximate transform does not complete this requirement. Directed output
intervals can prove saturation or rounding decisions; undecided exact ties need
explicit treatment rather than an unsupported universal correct-rounding claim.
The unchanged project PCM bound2 and exact identities remain the acceptance
contract; finite-corpus success must remain distinct from a domain certificate.

Creator references: [Vorbis I6.2.3 and4.3.6](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
and unchanged pinned Xiph1.3.7 `lib/lsp.c` in `native_vorbis_xiph/upstream`.
This is a read-only mathematical audit, not a new runtime qualification. No
private ABI, old deferred controller, production selection or task binding is
changed. The complete wider decoder remains required by the transfer plan.
