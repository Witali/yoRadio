Finite floor1 renderer evidence, 2026-10-24

Run `python verifier.py` offline in this directory. It reads only saved bytes;
it never invokes FFmpeg, the SDK, QEMU or a physical device.

The two current independent checks compare every signed PCM16 sample in eight
valid cases on each architecture for each corpus at the predeclared project
bound of two LSB. Six malformed setup cases per corpus are retained. The
old-tail control must reproduce all eight frozen baseline files, including
the first three numerical failures; the five ordinary position cases remain
byte-exact to that baseline and differ from Xiph by at most one LSB.

Original native/dual-reference NONPASS, failed checker01 attempts and host01
normal-only history are preserved. Host02 separately records actual timeout
and interruption cleanup controls with nonce-bound descendant-ready witnesses.
The raw gate retains its same-loader parity scope; it is not an independent
vendor renderer oracle. The host and finite raw results do not qualify full
G6, dependency closure, production radio, RF or physical hardware.

All selected bytes are gzip objects named by uncompressed SHA256. Omitted
executables, libraries, merged flash and replaceable build outputs have byte
identity records only. Tool pins inside saved reports are recorded historical
facts; their current binaries are not independently verified by this archive.
