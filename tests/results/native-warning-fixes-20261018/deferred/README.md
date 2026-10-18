# Deferred AAC reset view experiment

An assistant task was stopped by an automatic content check before completing
its regression qualification. The exact unverified diff is retained in
`aac-reset-unverified.patch`; it is not applied to the firmware source.

The baseline warning comes from recovering a channel owner by subtracting a
prefix from its frame subobject. No escaping allocated owner was reproduced.
The experiment passes an explicit typed right-PS synthesis pointer instead;
it still needs 32-bit layout/reset guard tests and vendor/QEMU PCM regression.
No private ABI offsets should be copied to CYD or changed without validation.

The confirmed Vorbis parser failures are a separate change with their own
executable regressions. No alternate agent prompts were used to bypass the
content check.
