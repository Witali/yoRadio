# Isolated Vorbis lookup1 integer-root test

The fixture includes the entire unchanged, frozen canonical setup.c and its
native ABI assertions in the main translation unit. It calls only the existing
static _book_maptype1_quantvals helper through a volatile function pointer.
Function-section GC removes unused parser and decoder code; only public codec
headers are included, and no codec archive is linked.

The independent host generator supplies cases.json and cases.h. The target
controller validates each expected integer root with Python arbitrary-precision
integer inequalities and reads back every emitted C row before SDK execution.
Entries up to signed32 maximum are arithmetic unit inputs; values above24 bits
are not presented as encoded Vorbis stream cases.

The ESP32 coordinator runs on core0 and its worker on core1; the C3 uses core0.
Both workers have priority3 and configured stack16384. This isolated fixture
does not alter production task bindings, board pins, display or audio settings.

The controller retains source snapshots, actual owned command terminals,
compiler/dependency/symbol/build evidence, all ordered target rows and source
hashes before/after execution. QEMU uses explicit ROM paths, no network/display,
snapshot flash and no-reboot. The guest prints a terminal marker and restarts;
success also requires the owned QEMU process to exit normally with code0.

This is finite arithmetic and target compilation evidence, not a decoder,
PCM comparison, full ABI/conformance gate, production firmware export,
real-time/resource measurement or physical board acceptance. It does not test
deferred public-consumer zero guards, Ogg, FLAC errors or AAC.
