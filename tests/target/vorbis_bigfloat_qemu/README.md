# Public bigfloat arithmetic on native QEMU

The controller freezes the complete701-row corpus, unchanged shared C fixture
and owned arithmetic component before a fresh SDK build. ESP32 uses SDK6.0.2,
worker core1; C3 uses SDK6.1, worker core0. Coordinator core0, priority3,
worker stack16384, task/idle watchdogs and overflow checks remain enabled.

Only the fixture's existing completed-record `fflush` calls are redirected to
real `fflush` followed by `vTaskDelay(1)`. No arithmetic operation, allocation
ordinal or assertion changes; no intra-operation yield or watchdog reset hides
long operations. Inputs remain in flash, and all allocator guards use real
native `malloc`. Full BF records are retained and independently checked against
Fraction/isqrt and actual saved host32 dyadic/floor outputs.

The isolated test project makes only creator sign-compare/unused-parameter
diagnostics nonfatal and re-enables them where SDK defaults suppress them.
Only portable/libbf.c also downgrades format diagnostics; they remain visible.
Adapter/main retain SDK -Werror. Symbol and discarded-section checks require
excluded debug/decimal/string/transcendental helpers to stay outside the image.
The foundation and frozen fixture bytes are unchanged.

BFQ metadata adds source/corpus identity, actual task/core/priority, stack free
watermark, heap/free/minimum/largest block, registered idle watchdogs and heap
integrity. Compiler/database/linkmap/ELF/object/stack/image identities are saved.
This isolated diagnostic never flashes a board or changes production bindings.
It qualifies only the retained basic-arithmetic corpus, not transcendental gain,
Bark selection, the wider decoder or universal MCU resource fit.
