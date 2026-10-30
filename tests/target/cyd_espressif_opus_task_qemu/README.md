# Actual CYD tasks with public Espressif Ogg/Opus

This sibling of the frozen Vorbis task harness runs complete production
`audio_service.c`, state, health and decoder registration with the real SDK
tasks, queues, allocators and public vendor decoder. HTTP transport and physical
output/LED calls are explicit seams. No board or external network is used.

The original CYD task profiles remain stream core 0 / priority 3 / stack 6144,
decode core 1 / priority 5 / stack 16384, output core 1 / priority 6 / stack 4096.
Assertions, heap poisoning, stack canaries and both idle watchdogs stay enabled.

First run `tests/run-cyd-espressif-opus-qemu.py` to establish the full unchanged
vendor result. Then run:

```text
python -B tests/run-cyd-espressif-opus-task-qemu.py --reference .build/<passing-direct-campaign> --output .build/<fresh-task-campaign>
```

The controller re-reads the original direct transcript, verifies its source,
image and child-status bindings, and generates `reference.h` from the observed
PCM byte count and SHA. The reference is not inferred from Vorbis or from an
assumption that the vendor performs Opus pre-skip/end trimming. The full
706319-byte `opus-510.ogg` is embedded without shortening or replacing it.

Cases are ordered EOF with complete PCM, partial Stop/discard then full reopen,
and partial three-owner maintenance followed by token-checked automatic resume.
Each complete run must match the measured direct-vendor output. Metadata,
client/decoder cleanup, original task bindings and heap integrity are checked.

The campaign reuses the pinned reviewed Vorbis controller's SDK process,
dependency-closure and build checks. The historical Vorbis sources and saved
evidence remain unchanged. This is an integration regression; independent Opus
conformance, other packet modes/durations, deliberate backpressure, real
HTTP/TLS/TFT traffic and physical audio remain separate qualifications. The
diagnostic image is not production firmware and must not be flashed.
