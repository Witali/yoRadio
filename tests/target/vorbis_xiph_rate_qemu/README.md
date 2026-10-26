# Independent unsigned-rate ESP32 metadata fixture

This project qualifies the owned public rate type and identification/comment
metadata APIs on actual ESP32 ILP32. It does not execute setup headers, DSP
initialization, audio packet decoding or any deferred fixture.

Run only through the owned Python controller after host validation and final
manifest/fixture pins have been agreed. No physical board is used.

The newly designed worker is pinned to core1 at priority0 with normal FreeRTOS
time slicing. The coordinator starts on core0. Watchdog initialization and both
idle checks remain enabled. Runtime diagnostics are rejected without filtering.
This scheduling belongs only to this independent metadata fixture.

Twelve compile-only translation units cover all six public-header inclusion
orders in C and C++. They exclude optional static convenience callback examples;
the original public header bodies remain available, and encoder/convenience
library execution is not qualified. The owned codec type is checked along with
every original vorbis_info offset, size and alignment.

Header dispatch can retain unexecuted decoder symbols through registry tables.
The controller does not claim those symbols are absent. Its pinned caller and
five runtime events restrict qualification to the declared metadata execution.
The original packet/DSP/amplitude gates retain their independent status.
