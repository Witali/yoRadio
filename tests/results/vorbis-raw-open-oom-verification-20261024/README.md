# Raw-open evidence publication verification

The collection and offline verification commands both terminated with exit 0.
Their actual owned-process receipts and unmodified stdout/stderr are retained
here, outside the immutable evidence archive and its collected input groups.

Verified archive: [raw-open evidence](../vorbis-raw-open-oom-20261024/README.md).
Manifest SHA256:
`e0106428f6037b6ee32a2dc7210fa3e6b0ff02b03111fbb74d319454912a602a`.
The archive contains 1891 logical files in 383 content-addressed objects;
5306 replaceable or executable outputs have explicit identity-only omissions.

The verifier ran from the parent repository directory using only saved bytes
and the explicitly hash-bound reviewed pure protocol parsers. It recomputed
every captured baseline signed16 comparison independently: maximum error 1,
fixed bound 2. Recovery equality remains target guarded memcmp evidence;
recovery PCM is not separately captured. No decoder, SDK, compiler or QEMU
was executed by the offline verifier. Full G1/G4/G5/G6, Ogg, radio integration
and physical acceptance remain open.
