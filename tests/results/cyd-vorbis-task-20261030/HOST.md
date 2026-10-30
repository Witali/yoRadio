# CYD Ogg final-byte EOS: host and compile checkpoint

All six lifecycle variants pass with the current production CYD decoder/output
task bodies: Espressif, Helix and minimp3, each with fixed or adaptive input.
The host runner uses GCC 13.3, `-Wall -Wextra -Werror`, ASan, UBSan and leak
detection. Its codec/platform functions are explicit seams; it does not execute
Espressif's binary decoder or establish complete q10 playback on the target.

The Ogg caller now retains one final encoded byte until the following packet
or EOF control arrives. It supplies that genuine final byte with EOS, then
drains empty EOS calls until neither input consumption nor PCM remains. The
lookahead itself allocates no heap storage. A packet is represented by at most
two borrowed segments; the normal payload is not concatenated or copied. A
previous held byte is copied to a local byte before replacing the task's tail.
The existing pending-input owner still handles a public decoder declining to
consume a short prefix.

New regression cases check:

- Nine distinct encoded bytes in one whole packet, one-byte packets and uneven
  packets. The Ogg mock credits three encoded bytes per PCM frame independently
  of process-call boundaries. Every encoded byte and all 64 output bytes are
  checked, including both cached PCM tail frames.
- A first EOS call containing genuine nonempty final data, followed by exactly
  two cached tail frames and a final empty drain. Terminal data packets work
  both with and without a previously held byte.
- A single held byte interrupted by public Stop and Play in the same decoder
  task. The new stream must contain its own exact bytes with no stale tail.
- Borrowed segment pointers and lengths, distinct previous-byte storage,
  empty nonterminal input, idempotent empty EOF and bypass for other codecs.
- Clearing retained input and EOF lookahead when no decoder handle has been
  published. The actual release helper also clears both owners on generation,
  codec, failure and maintenance cleanup paths.

Earlier byte-prefix/OOM/recovery, codec-switch, header-only fairness,
cancellation-during-yield, typed-open-error, output and queue ownership cases
remain enabled. The 96-byte header-only case still makes 97 calls and three
one-tick yields across packet boundaries. Tracked allocations must be released
between cases, in addition to the sanitizer and leak checks. Maintenance cleanup
is inspected in the shared release path; a public maintenance lifecycle is not
executed by this host seam.

Final host run: `.build/cyd-vendor-public-lifecycle-20261030-06/`, terminal exit
0 for all six variants. Report SHA-256:
`f5547369455894226a1ae046afaf793e1c62a5e402a3b44202c1da9311c5a545`.

The completed actual Xtensa GCC03 compile also passes all three existing
production profiles: `build-c3-transfer`,
`build-custom-flac-network-settings-continuous` and
`build-custom-flac-network-settings-legacy`. These compile the complete
production `audio_service.c` with existing SDK configurations and flags. This
is translation-unit evidence, not a linked firmware build or runtime result.
The three object files, logs, controller, report-pinned configuration headers
and compilation databases, and referenced response files are preserved.

Focused EOF clang-tidy01 finishes with exit 0. Its only displayed warning is
the existing `stream_frames.h:47` enum zero initialization; 18 non-user warnings
are suppressed. No new displayed warning or error is introduced. The complete
log, fixes YAML and `.clang-tidy` policy are included. This is a focused check,
not a new full repository lint pass.

[`host-captures.zip`](host-captures.zip) preserves all six real host executables,
logs, generated production bodies/platform stubs, all 16 exact report-pinned
repository sources, the required public headers and compiler launcher helper,
plus the completed GCC03 and focused lint evidence. Preservation checks source,
object/log/configuration/database bindings and every decoded archive member.
Installed compiler binaries are not archived; compiler identity and the target
compiler file hash are metadata. [`host-manifest.json`](host-manifest.json)
records sorted relative member paths, byte counts, hashes and the archive hash.

Native full-task attempts, public trace evidence and target PCM qualification
are recorded separately. These host artifacts do not claim physical hardware,
DMA timing, production resource margins or full-format conformance. Preservation
does not execute a decoder, emulator or test and leaves canonical source bytes
unchanged.
