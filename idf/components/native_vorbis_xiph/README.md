# Pinned Xiph evaluation component

This isolated candidate builds the complete upstream libvorbis 1.3.7 base
library and libogg 1.3.5. It is not selected by either production radio
application. Basic Ogg/Vorbis playback already exists through Espressif's
package; see the [branch audit](../../../docs/CYD_OGG_VORBIS_BRANCH_AUDIT_20261025.md).

All files under `upstream/` are byte-identical members of the official release
archives. `SOURCE.json` records URLs, archive/checksum-list hashes and each
imported file. Both upstream `COPYING` files are retained. The scoped Git
attributes preserve the original bytes. No upstream build script is executed.

The IDF adapter compiles exactly the 20 C files in the official libvorbis base
target, plus libogg's `bitwise.c` and `framing.c`. `vorbisfile.c` and
`vorbisenc.c` are retained but are not compiled. Encoder-side callbacks share
the base registry; removing them is a separate optimization, after evaluation.
The platform header substitutes only the documented placeholders in
libogg's `config_types.h.in`, using stdint fixed-width types. Newlib provides
`alloca.h` and libm. `HAVE_CONFIG_H` remains unset. Fast math and floating
contraction are disabled. Allocation uses the unchanged upstream libc macros.
The first actual SDK build rejected upstream `block.c:395..397` solely because
GCC 15 promotes misleading indentation to an error. The component adapter uses
`-Wno-error=misleading-indentation` to retain those warnings while compiling the
unchanged release. The fixture's warning policy is unchanged.
The next build and a complete 23-unit GCC probe also identified
`-Wmaybe-uninitialized` in encoder-only `lpc.c:78` and `psy.c:714`. For the
positive orders/sizes supplied by their upstream callers, the preceding loops
initialize the read arrays. Only those two GCC translation units use
`-Wno-error=maybe-uninitialized`; the warnings remain visible. No upstream C
or header is patched, and no decoder result is accepted by changing diagnostics.

`component-manifest.json` binds every component file except itself and lists
the exact compiled C units. The target controller must check both the supplied
manifest SHA-256 and the complete file inventory before building.

Use the raw public header/synthesis API for the first experiment, preserving
all three complete header packets, audio packet numbering, granules and EOS.
PCM conversion and capture belong to the fixture, not the upstream library.
The original 31-case corpus and its existing S16 error bound remain unchanged.
Success on that finite corpus is not proof of full standard coverage,
production memory margin or physical real-time throughput. In particular,
upstream still uses float intermediates, clamps VQ exponents, and has signed
floor0 amplitude expressions requiring further boundary evaluation.

Official provenance:

- [libvorbis release checksums](https://ftp.osuosl.org/pub/xiph/releases/vorbis/SHA256SUMS)
- [libogg release checksums](https://ftp.osuosl.org/pub/xiph/releases/ogg/SHA256SUMS)
- [libvorbis base target](https://github.com/xiph/vorbis/blob/v1.3.7/lib/CMakeLists.txt)
- [libogg type template](https://github.com/xiph/ogg/blob/v1.3.5/include/ogg/config_types.h.in)
