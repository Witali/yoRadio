# Small TV JPEG dependency

This software is based in part on the work of the Independent JPEG Group.
The original license files are in `licenses/` and in the upstream source archive.

`upstream.tar.gz` is a deterministic gzip of the unmodified `git archive` for
libjpeg-turbo 3.2.0, commit `c85e6b905bf237038faa936dab160ebfc5da0344`.
`BUNDLE.json` pins both its compressed bytes and the original tar size;
`UPSTREAM.json` pins the original tar, licenses and three adaptation patches.
No network connection or additional upstream checkout is needed during a build.

`tools/build_jpeg_library.py` verifies and exports these inputs into the selected
build directory, applies the patches there and builds a static RV32IMC/ILP32
library with the pinned ESP-IDF tools. Release optimization is explicitly `-Os`.
SIMD, TurboJPEG, tools and tests are disabled; ordinary JPEG decoding precisions
and entropy modes remain enabled. The build report binds the actual archive,
exported source, configured headers, compiler, tools and flags. A changed or
incomplete cached build is rejected, rather than silently reused.

The three patches are the same bytes qualified in `tests/jpeg_library_probe/`.
Those copies remain historical test inputs; this directory is the production
dependency. Modifications are marked in patched source: bounded image pools and
progressive windows, exact flash-resident 12-bit tables, and compact pool reserves.

The app build now compiles the bounded codec and storage adapters. This build
integration alone does not switch the UI/upload path from TJpgd, validate the
complete application's memory use, or establish target runtime acceptance.
