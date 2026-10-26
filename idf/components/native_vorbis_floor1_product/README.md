# Exact floor1 spectrum product

Allocation-free dyadic multiplication of coupled residue by the unchanged Xiph
floor1 inverse-dB table. Frame wrappers reuse the existing raw-Y reconstruction
and curve renderer. See the [design](../../../docs/CYD_VORBIS_FLOOR1_PRODUCT_DESIGN.md)
for numeric bounds, ownership and failure guarantees.

This component is not selected by the CYD or C3 production applications. It
stops before floor0 multiplication, IMDCT, window/overlap and PCM synthesis.
The copied table retains the Xiph license in [COPYING](COPYING).
