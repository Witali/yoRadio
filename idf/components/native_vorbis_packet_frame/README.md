# Exact audio packet front end

This optional allocation-free component composes the existing exact setup,
floor, residue and inverse-coupling APIs. It borrows a live immutable setup,
including the view provided by `native_vorbis_setup_owner`, and writes one
packet's floor data and residue after inverse coupling into caller-owned scratch buffers.
No packed VQ term is converted to floating tables.

Measurement returns explicit conservative capacities for the selected mode.
Decode uses actual original floor-presence flags for residue measurement;
coupling propagation does not alter the saved floor flags. A floor EOP returns
the specification's whole-frame zero result, while residue EOP preserves every
earlier complete contribution. All-unused floors need no sample storage, and
zero numeric grids still perform mandatory entropy reads.

Workspace is scratch; previous result borrows expire on every attempted reuse.
The result descriptor/cursor publish only on success, with sticky prefix EOP
reported separately. Neither radio selects this component. Floor curve
synthesis/multiplication, inverse transform, overlap, PCM, raw lifetime wiring,
target resources and physical qualification remain separate.
