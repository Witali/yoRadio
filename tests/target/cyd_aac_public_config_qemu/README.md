# Public AAC-Plus configuration on classic ESP32

This diagnostic uses unchanged Espressif LX6 codec libraries on SDK 6.0.2.
It compares genuine NULL/default, explicit AAC-Plus-off and the CYD production
configuration header on six complete original LC/HE/HEv2 fixtures. Whole,
4096-, 257- and one-byte input schedules compare every emitted PCM digest.
Both nonidentical stereo samples and full-rate SBR output are observed.

The worker is a diagnostic task on core 1 / priority 3 / stack 16384, not the
production pipeline. Both idle watchdogs, heap poisoning and stack canaries
remain enabled. Images use test partitions and must not be flashed as radio
firmware. No board, external network, private ABI, compressed owner, binary
patch or codec linker wrapper is used.

```text
python -B tests/run-cyd-aac-public-config-qemu.py --output .build/cyd-aac-public-config-new
```

This isolates public configuration and decoding behavior. It does not qualify
production task integration, implicit late-SBR changes with identical headers,
allocation failures, complete malformed AAC handling, compact owners, radio
resources, numeric conformance against an independent decoder or physical audio.
