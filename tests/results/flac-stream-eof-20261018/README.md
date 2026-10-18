# Streaming FLAC metadata EOF qualification

Production fix: `ea239ddf` (`Reject truncated FLAC metadata at declared EOF`).
This is a separate donor FLAC campaign; it does not qualify OTA or implement
custom FLAC on CYD. No device was accessed and no production image was built.

`before/report.json` retains the executable pre-edit reproduction: 5387 groups,
4308 failures. `qualified/report.json` records the final frozen actual
adapter/core test: 5387 groups, zero failures, ASan/UBSan, no sanitizer diagnostics.
Raw compiler/test logs and all hashed harness/production source inputs are kept.

The 1077-byte metadata chain contains STREAMINFO, 1027 bytes of padding and a
last zero-length padding block. FFmpeg independently decodes the full fixture
to the known generator PCM. Every cut before complete metadata is tested with
inline EOF and a separate zero-byte EOF, each with whole and fragmented input:
4308 negative groups. Another 1077 groups resume the same incomplete prefix and
compare all PCM with the full decode; two groups preserve complete-metadata-only
behavior. A final call spanning multiple 512-byte internal chunks is covered.

The exact old adapter from Git revision
`fc89b4a965e8125149bdc0ca58ca1f9f9cd94dbc` is compiled as an executable negative
control. It reports all 4308 EOF failures while the continuation controls pass.
Both old/current variants use the same frozen current shared core and header.
Git source bytes and a Windows working copy may have different line endings;
each raw input hash records the bytes actually compiled.

All 120 deterministic 4/8/12/16/20/24-bit, mono/stereo/decorrelation and
constant/verbatim/fixed/LPC fixtures are decoded in three input schedules:
whole inline EOF, fragmented inline EOF, and fragmented input plus empty EOF.
Both current and old adapters match every byte of independently decoded FFmpeg
and known generator PCM: **720 complete comparisons**, no PCM change. A repeated
empty EOF produces no duplicate PCM. Fixture manifests and the deterministic
generator are retained; generated fixture bodies, PCM and binaries are omitted.

The host seams are the retained existing Arduino/log/timer/FreeRTOS headers.
The actual adapter and core compile with their includes and implementations
unchanged. This evidence does not establish target ABI, physical heap capacity,
task scheduling, DMA continuity, checksum conformance or full audio completion.
The fix intentionally leaves complete metadata-only acceptance unchanged.

Fresh reproduction from the worktree root, with WSL g++, Windows FFmpeg and the
usual Python environment (or native Linux tools):

```text
python tests/run-flac-stream-eof.py --output .build/NEW_FLAC_EOF --baseline-revision fc89b4a9
```

Final raw output: `.build/flac-stream-eof-qualified-final`.
Initial reproduction: `.build/flac-stream-eof-before-01`.
An intermediate runner attempt had a CRLF filename-list bug; its raw failure is
retained in `.build/flac-stream-eof-qualified-01`. It was corrected in the test
runner and is not counted as a successful qualification. The final campaign
was rerun after freezing the runner, including compiler/FFmpeg versions and
independent metadata-fixture validation.

`index.json` records exact archived bytes/hashes, excluding itself.
