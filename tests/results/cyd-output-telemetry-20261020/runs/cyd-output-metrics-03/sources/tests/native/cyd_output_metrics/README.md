# CYD output driver observations

The runner executes the complete production metrics translation unit in quiet
and diagnostic configurations. Public write/queue/snapshot APIs drive all normal
state changes. A pthread mutex models each SDK task/ISR portMUX boundary; TLS
context guards reject using a task critical macro from ISR or reading the clock
inside a critical section. The clock is an explicit scripted SDK seam.

Cases check exact requested/reported bytes, partial/timeout/error classification,
diagnostic wall-time aggregation, invalid clocks, quiet mode without clock
reads, queue availability, ISR-only queue events, saturation, and concurrent
write/ISR publishers with coherent snapshots. A separate count-boundary build
changes only the documented static initial counter seed; no test writes private
metrics or audio phases/ACKs at runtime. Every semantic mutant must fail its
named assertion, rather than compile, time out or trigger a sanitizer failure.

This qualifies the counter service. Backend callback registration and actual
driver API integration require their own production-source tests. It does not
establish real interrupts, cache/IRAM safety, DMA behavior, driver timing,
physical audio, CPU overhead or full-radio resource margins. The diagnostic
duration covers an entire synchronous driver call, including preemption.
