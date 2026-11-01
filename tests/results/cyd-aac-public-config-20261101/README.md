# CYD public AAC-Plus configuration checkpoint

The unchanged pinned LX6 Espressif library confirms a real configuration gap:
the former NULL configuration decodes the lower-rate AAC core of HE streams.
The explicit public `esp_aac_dec_cfg_t.aac_plus_enable` preference restores
full-rate SBR and HE-AACv2 stereo. LC output is unchanged. No private AAC layout,
compact owner, reset repair, FIL hook or archive patch is used.

The new CYD `YORADIO_AAC_PLUS` preference defaults on for the Espressif AAC
backend, matching C3's public preference. It is hidden when that vendor backend
is disabled. Status continues to report confirmed PCM parameters; the public
API does not prove nominal HE/PS source labels.

This checkpoint records the AAC integration revision in commit `aa6857b0c`.
Later Ogg options legitimately extend the same Kconfig file. Its original
tested Kconfig bytes remain frozen here; the verifier explicitly reports
whether today's configuration still matches and offers `--require-current`
to enforce that additional check. Executed canonical readers remain pinned.
This historical gate does not qualify a later edited configuration or audio TU.

## Actual public decoder execution

SDK 6.0.2 / classic dual-core ESP32 QEMU campaign **02** completes all **36**
native cases with terminal compiler-driver, SDK and emulator status zero.
Each of six complete original FDK-generated fixtures is decoded with NULL,
explicit off, production-header on, then on with 4096/257/one-byte input.

| Complete fixture | NULL / explicit off | Production public preference |
| --- | --- | --- |
| LC 44100 stereo | 98304 PCM bytes, 44100 Hz, 2 channels | Identical whole PCM |
| LC 22050 mono | 26624 PCM bytes, 22050 Hz, 1 channel | Identical whole PCM |
| LC 48000 stereo | 106496 PCM bytes, 48000 Hz, 2 channels | Identical whole PCM |
| HE 44100 stereo | 57344 PCM bytes, 22050 Hz, 2 channels | 114688 bytes, 44100 Hz, 2 channels |
| HE 48000 stereo | 61440 PCM bytes, 24000 Hz, 2 channels | 122880 bytes, 48000 Hz, 2 channels |
| HEv2 44100 stereo | 30720 PCM bytes, 22050 Hz, 1 channel | 122880 bytes, 44100 Hz, 2 channels |

Every original encoded byte is consumed. Independent ADTS header/frame
accounting derives expected complete output lengths from each original fixture.
NULL and explicit-off hashes agree. All four on-mode schedules produce the
same complete PCM digest for each fixture. HEv2 produces 24123 nonidentical
left/right sample pairs, rather than duplicating its mono core.

Each actual open is called through a non-inlined helper owning its local AAC
and outer simple-decoder configuration. After synchronous open, that helper
overwrites valid AAC fields to the opposite preference and clears the outer
configuration, then returns before processing. All 36 complete decodes still
use the original settings. This qualifies the local configuration lifetime for
the pinned public implementation without inspecting decoder-private storage.

The diagnostic worker is core 1 / priority 3 / stack 16384. It is not the
production decoder task. Both idle watchdogs, heap poisoning, heap integrity
and stack canaries stay enabled. Initial/final PCM capacity is 12288; no resize
is requested. Stable repeat-stream free heap is 270140 bytes, minimum observed
heap 159424, unused worker stack 13364. Final unregister retains 100 bytes
relative to the pre-registration observation. These are diagnostic observations,
not production radio/TLS/TFT resource margins or a zero-retention claim.

The genuine GCC closure contains five selected whole translation units and
203 dependencies, including the actual production public configuration header.
Original commands, source snapshots, selected objects' identities, build metadata,
configuration, stdout/stderr, SDK child status and pre/post bindings are retained.
All bindings were unchanged at completion.

## Production integration compilation and Kconfig

The actual current `audio_service.c` with the conditional public configuration
is compiled on SDK 6.0.2 using the saved production PDM, continuous DAC and
legacy DAC GCC commands, each with AAC-Plus off/on: **six successful profiles**.
The twelve actual preprocess/compile processes finish zero. Compiler, generated
backend configuration, response files and every consumed source/header are
bound before/after. New Xtensa object and stack-usage identities are preserved;
old build outputs/configurations are not modified. This is whole-TU compilation,
not a new linked production firmware export or pipeline runtime test.

Installed Espressif Kconfiglib checks the actual production Kconfig: **eight**
default, explicit-off, dependency, Helix-hidden and restoration cases pass.
Unprovided unrelated SDK symbols and their original warnings are recorded,
without claiming a full production menu configuration from this host wrapper.

The original native campaign **01** remains a pre-QEMU compile failure: its
diagnostic printf used `%u` with an Xtensa `uint32_t` argument. The fresh passing
campaign uses an explicit unsigned cast and includes the lifetime witness.
The initial Kconfig compatibility-import failure and initial production-smoke
dependency-reader failure also remain nonpassing. Neither old report, frozen
source nor log was rewritten; separate fresh successors pass.

## Verify or reproduce

```text
python -B tests/results/cyd-aac-public-config-20261101/verify.py
python -B tests/run-cyd-aac-public-config-qemu.py --output .build/cyd-aac-public-config-new
python -B tests/check-cyd-aac-integration.py --output .build/cyd-aac-integration-new
```

The Kconfig test needs the installed SDK Python with Kconfiglib:

```text
python -B tests/test-cyd-aac-public-config.py --output .build/cyd-aac-config-new
```

The data-only verifier runs reviewed canonical readers, never archived programs,
the compiler, decoder or emulator. It checks every published byte and rejects
six contradictory transcript controls. `captures.zip` deduplicates exact
original bytes under `blobs/<sha256>`; `manifest.json` retains logical identities.
Executable/firmware/object/static-library payloads and installed SDK/toolchain/
vendor source bytes remain local with their exact hashes/sizes and provenance.
Three historical production manifests containing personal home paths are also
excluded in their entirety; their original metadata identities remain bound.
No encoded copy or semantic publication-scanner override is used. Omitted bytes
cannot be re-read by the published data-only verifier.

This is a real public configuration transfer subset. Compact Xtensa owners,
private ABI adaptations, actual production AAC task lifecycle, independent
numeric conformance, implicit late SBR with unchanged ADTS headers, OOM and
backpressure, full radio resources and physical audio remain open. Previously
deferred owner/reset and FLAC target scopes were not resumed.
