# HE-AAC default-network HTTP timeout control

The original default-network HE-AAC/WebUI failure remains NONPASS.
An exact one-setting comparison increases `YORADIO_WEB_SEND_TIMEOUT_SECONDS`
from 1 to 10 seconds, the existing CYD Kconfig maximum, without changing TCP,
TLS capacities, watchdogs, instrumentation, source code or codec binaries.
The effective typed configuration difference was checked before execution.
The disposable local TLS material is identical to the original control.

The new original controller result is **TERMINAL_NONPASS**:
`IncompleteRead(5120 bytes read)`. PCM continues, but the complete 614,400-frame
flush and EOF are not reached. The original UART records RX memory pressure,
subsequent recovery and a dropped receive frame. Neither a longer timeout nor
the partial PCM output is presented as a memory fix or a successful full run.

The C3 donor uses a 20-second WebUI send timeout. CYD's current 1-second setting
also bounds ordinary HTTP sends; WebSocket frame deadlines are separately
enforced. Any future transfer of the longer static-download timeout needs its
own bounded-client qualification. This experiment does not justify changing
global production timeouts to conceal resource exhaustion.

[Original report](report.json), [raw UART](qemu.log),
[observations](observed.json) and [compiled project-unit identities](fixture-identity.json)
are retained byte-for-byte. Project-unit bindings are not a full compiler
dependency closure. Exact ELF/map/command/config identities are recorded;
keys, complete flash images and build products stay local under `.build`.
The build terminal summary is not a complete native compiler transcript.
Physical Wi-Fi/audio is untested. The previous six normal production exports
remain unchanged; successful optional TCP profiles retain their separate
[HE-AAC qualification](../cyd-aac-resource-profile-20261123/README.md).
