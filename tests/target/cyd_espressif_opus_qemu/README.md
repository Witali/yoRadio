# CYD public Espressif Opus regression

This isolated SDK 6.0.2 / LX6 QEMU diagnostic first passes the complete borrowed
Opus fixture to the unchanged public Ogg decoder with data-bearing EOS. It
records the actual full PCM identity before using either shared input adapter.
It then compares 4096, 257 and one-byte feeds with a separate caller EOF through
the production pending-prefix and final-byte EOS helpers. Output capacity stays
at the production 12288 bytes. No private decoder state or custom repair is used.

The full vendor identity is an integration regression, not an independent
conformance or audio-quality oracle. Public metadata, complete encoded-byte
consumption, empty EOF drain, cleanup, heap integrity and both idle watchdogs
are checked. First-use SDK/vendor retention is measured separately from later
stream ownership. Diagnostic images must not be flashed as radio firmware.

Run `tests/run-cyd-espressif-opus-qemu.py --output .build/<fresh-campaign>` with
the installed pinned Windows SDK and QEMU. All original source, command, native
child and build evidence stays under that campaign. No physical board is used.
