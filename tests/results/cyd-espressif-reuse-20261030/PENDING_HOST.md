# CYD retained decoder input: host and compile checkpoint

All six lifecycle variants pass with the production CYD decoder/output task
bodies: Espressif, Helix and minimp3, each with fixed or adaptive input. The
host runner uses GCC 13.3, `-Wall -Wextra -Werror`, ASan, UBSan and leak
detection. Codec and platform functions are explicit test seams; this host
checkpoint does not execute Espressif's binary decoder.

The public caller now keeps input which a successful decoder call has not
consumed. A short prefix is retained verbatim and joined to the next packet.
Ordinary packets remain borrowed without allocation. Retained storage uses
checked allocation and the public API's `uint32_t` length representation;
this is not an extra limit on the encoded format. A nonempty remaining prefix
which still cannot progress at EOF produces a typed decode failure. An empty
EOF continues to drain cached PCM normally.

The added regressions verify:

- Distinct encoded bytes through one-byte feeds and two uneven split patterns,
  including partially consumed borrowed and owned suffixes. Every emitted PCM
  byte is checked against the consumed byte sequence, detecting duplication,
  omission and reordering.
- Allocation failure during the initial prefix copy and a later append growth,
  the `MEM_LACK` health result, allocation-failure completion, cleanup and a
  successful new Play in the same task. Failed allocation preserves the old
  retained prefix until its owner releases it.
- Stop with a retained suffix, a codec switch within the same generation,
  nonempty stalled EOF and normal complete EOF. A tracked allocation table
  requires all PCM and retained-input owners to be released between cases.
- Helper zero-copy preparation, unchanged output parameters on failure,
  checked total length, overlapping owned-suffix movement, idempotent clear
  and cleanup when no decoder handle has been published.

The earlier scheduling, cancellation-during-yield and typed-open-error cases
also remain enabled. Canonical source inspection confirms maintenance uses
the same release helper before its decoder acknowledgement. This host seam
does not execute a public maintenance scenario, so that path is not claimed
as runtime-qualified here.

Final host run: `.build/cyd-vendor-public-lifecycle-20261030-05/`, terminal exit
0 for all six variants. Its report SHA-256 is
`20ff17a7ed788265becb2b470a90ee8e47b3f6fe1071618b6e6d867ac83e0d3d`.

The root's completed actual Xtensa GCC compile02 also passes all three existing
profiles: `build-c3-transfer`,
`build-custom-flac-network-settings-continuous` and
`build-custom-flac-network-settings-legacy`. These compile the complete
production `audio_service.c` with their existing SDK configurations and flags.
They are translation-unit checks, not linked firmware builds or runtime tests.
The report-pinned configuration headers and compilation databases, referenced
response files, three object files, logs and controller are preserved.

Focused clang-tidy02 finishes with exit 0. Its only displayed warning is the
existing `stream_frames.h:47` enum zero initialization; 18 non-user warnings
are suppressed. No new displayed warning or error is introduced by this
change. The complete log and fixes YAML are retained; this is not a new full
repository lint pass.

[`pending-host-captures.zip`](pending-host-captures.zip) contains the real six
host executables, logs, generated production bodies and platform stubs, exact
report-pinned repository sources, required public headers, compiler launcher
helper, compile02 evidence and focused lint02 evidence. Preservation validates
all 15 host source hashes, the three target object/log/configuration/database
bindings and every decoded ZIP member. Installed compiler binaries are not
archived; host compiler identity and the target compiler file hash are metadata.
[`pending-host-manifest.json`](pending-host-manifest.json) records relative
member paths, sizes, SHA-256 hashes and the complete archive identity.

The original `host-captures.zip`, `host-manifest.json` and `HOST.md` remain
unchanged. Native public-vendor decoding, actual audio-service task integration,
physical hardware, full-format conformance and production resource margins
are separate gates. No decoder, emulator or test was launched while preserving
this checkpoint.
