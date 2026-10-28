# Shared frame timing and multi-channel exact synthesis

The owner caches each channel's unwindowed right half with its independent
signed64 base exponent. Actual neighboring sizes select the window slopes;
complete 106-bit products are added before final S16 rounding. One timing
state selects the same granule/EOS trim for every channel. Output is interleaved
in source channel order, without resampling or a fabricated terminal block.

Push validates every channel and all active history before any write. It
finishes all channel outputs before replacing any history/base, then publishes
timing/result last. Failure leaves actual state, history, bases, output and
result bytes unchanged so the caller can retry. Init/reset do not read or
write history/base elements; a following priming block replaces their active
regions. A discontinuity reanchors timing while retaining numeric overlap,
matching the existing timing policy; hard reset is separate.

All storage is caller-owned. History needs `channels*long_size/2` doubles;
output needs at most the same number of interleaved S16 samples. These are
storage costs, not proof of available MCU heap. Prepared windows remain
immutable and all use is serialized. No heap, VLA, internal lock or task is
introduced; production selection and core/audio bindings remain unchanged.
See [the design](../../../docs/CYD_VORBIS_SYNTHESIS_DESIGN.md).

The [checkpoint](../../../tests/results/vorbis-synthesis-20261028/CHECKPOINT.md)
qualifies the complete public packet-to-PCM pipeline on all31 original streams,
434 packets and738560 PCM bytes: host compares both references at the original
bound2/all14 relations; actual ESP32/C3 SDK/QEMU outputs match host byte-for-byte.
Host ownership tests cover all20019 timing actions and channels1..255 with
ASan/UBSan. This isolated candidate remains unselected by the production radio.
General floor0/wider precision, raw/Ogg integration and full radio resources
still require separate work.
