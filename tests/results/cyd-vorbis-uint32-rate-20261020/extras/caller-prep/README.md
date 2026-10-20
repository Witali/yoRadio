# Public uint32-rate caller proposal

Source preparation and synthetic host checks only. No C compilation, SDK,
decoder, reference, QEMU, device or Git operation was performed. Root owns
source integration, actual build/process receipts and runtime qualification.

`main.c` uses only public opaque original/checked Vorbis APIs. Root must copy
canonical `tests/target/cyd_vorbis_format_qemu/main/fixture.h` unchanged
(SHA256839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378).
No fixture copy is supplied here. Both identification buffers set original
S256/L2048; only rate bytes5–8 differ between golden and checked. The unchanged
setup/audio contain68 packets. Vendor golden rate is always192000Hz and is
independent of candidate policy. No separate8192 probe is included.

All16 rates, in order:48000,44100,32000,24000,22050,16000,12000,11025,8000,
1,63999,64000,192000,2147483647,2147483648,4294967295. Zero-header rejection
precedes them. Both macros must be explicitly0/1:

| Mode | RATE_EXPECT_UNSIGNED_REJECTION | RATE_LIMITED_POLICY | LIMIT_TO_64kHz |
|---|---:|---:|---|
| baseline | 1 | 0 | absent |
| acceptance | 0 | 0 | absent |
| limited | 0 | 1 | defined |

Both policy macros1 is rejected at preprocessing. The original prebuilt vendor
remains untouched. Candidate setup/output and ABI integration belong to root.

Every accepted case requires all68 packets, full consumption, exact PCM,
canaries and public rate/channel/16-bit metadata including zero-output priming.
Metadata objects persist separately per handle. The two guarded16384-byte PCM
buffers exceed the4096-byte maximum packet output. CASE_COMPLETE requires
nonzero accumulated PCM and successful public close of both handles. Rejected
cases also close the vendor handle. CASE_OPEN attests `header_error=1` only
for exact `ESP_AUDIO_ERR_FAIL` with null checked handle, preventing an unrelated
allocation error from satisfying the signed-validity control witness.

Coordinator and worker report actual core IDs0/1; the worker is pinned to core1,
priority3, stack16384 and yields every16 packets. Completion/failure flushes
stdout and restarts the isolated application for a bounded no-reboot QEMU run.

`rate_protocol.validate_log(log, mode, control=None, *, returncode, timed_out,
interrupted)` consumes native `CYD_VORBIS_RATE_` lines. It requires explicit
actual terminal0/not-timeout/not-interrupted facts and returns observations,
never firmware qualification. Unknown modes, controls, malformed/foreign
prefixes, missing/duplicate/extra lines and unexpected failures are rejected.

| Expected complete mode | Accepted | Rejected | Packet pairs | PCM bytes | Native lines |
|---|---:|---:|---:|---:|---:|
| acceptance | 16 | 0 | 1088 | 4362240 | 1124 |
| baseline | 14 | 2 | 952 | 3816960 | 988 |
| limited | 11 | 5 | 748 | 2999040 | 784 |

Only the matching named controls may stop early. `signed-validity` with
acceptance requires exact `legal_unsigned_rate_open_required` at0x80000000,
after14 fully decoded cases (985 lines). `signed-policy` with limited requires
exact `limited_rate_rejection_required` at0x80000000 after11 decoded and3 rejected
cases (781 lines). Controls cannot qualify a complete acceptance/policy matrix.

Current synthetic host gate:19 methods, terminal0 in `host-tests-02.json`, with
both streams retained and source hashes checked before/after. It exercises all
three modes/two controls and negative process, metadata/priming, unsigned print,
consumption, PCM, canary, close/count, cap-boundary and control-witness cases.
Historical attempt01 has18 methods and is retained with original sources under
`history/attempt01`; its original receipt/logs remain untouched.

This proposal does not change the pinned signed-long ABI. Actual metadata/PCM
behavior for the unsigned high half and enabled-cap behavior remain untested
until root's SDK/runtime campaign. No mono/multichannel or full G6 claim follows.
