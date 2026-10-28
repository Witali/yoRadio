# Exact products from a borrowed Vorbis window

This component retains every bit of a finite binary64 sample multiplied by a
binary64 window factor. It decodes the operands and multiplies their integer
significands, returning an odd magnitude of at most 106 bits. A bounded shift
and the original signed64 base exponent remain separate. Their symbolic sum
can extend beyond either int64 endpoint without signed arithmetic or overflow.
Zero has canonical zero fields; no floating product can underflow here.

`native_vorbis_window_exact_prepare` validates a full block and prepared window
lookups, then copies descriptors into a view borrowing their immutable arrays.
`native_vorbis_window_exact_at` returns one exact product using the existing
support, plateau and short/long slope geometry. It needs no full output array,
allocation, trigonometry or task. Original descriptors can expire after prepare;
borrowed arrays must remain alive and immutable until every read ends.

The product is exact for the supplied binary64 inputs. Window coefficients
and the reused IMDCT are still approximations; this does not certify the full
decoder or repair information already lost before the window. Existing APIs,
production selection, overlap/PCM, audio backends and core bindings are unchanged.
See [the design](../../../docs/CYD_VORBIS_EXACT_WINDOW_DESIGN.md).

The [host qualification](../../../tests/results/vorbis-window-exact-20261028/CHECKPOINT.md)
retains all 17,962 recorded underflow witnesses as data-only operands and
checks every original window shape against an independent integer-ratio
product oracle. The old window/overlap captures and their limitations remain
unchanged. The following [exact PCM component](../native_vorbis_pcm_exact/README.md)
now adds complete products from adjacent-window slices through S16 rounding;
stream history/ownership and full decoder integration remain.
