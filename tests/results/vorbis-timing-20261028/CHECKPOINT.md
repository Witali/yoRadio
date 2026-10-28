# Vorbis granule/EOS metadata qualification

The [API](../../../idf/components/native_vorbis_timing/include/native_vorbis_timing.h)
and [design](../../../docs/CYD_VORBIS_TIMING_DESIGN.md) implement current-ready-span
trimming and position bookkeeping. No decoder, overlap, PCM, SDK/QEMU or radio
executes in this campaign. Counters are capped only where all bounded trims
are provably unchanged; out-of-wire-domain predictions are explicitly tagged.
Sequence gaps retain ready overlap while hard reset primes again.

Final host03, GCC13.3 ASan/UBSan with assertions enabled:

- 20,019 metadata actions,18,818 audio events; all36 short/long configurations
  and64 actual ordered size pairs,1,201 primes,588 hard resets and1,576 gaps.
- 720 arithmetic seeds include exact unbounded model values above the cap,
  up to1,208,935,042,986,666,029,486,079. Their C representation is projected
  to the proven cap;1,828 capped states and2,002 out-of-wire predictions occur.
- First-known front trim, first-known EOS tail trim, later EOS/current-span
  clamping, positive offsets, unknown anchors, mismatches, gaps and restart.
  322 leading-trim and3,988 trailing-trim rows retain exactly the modeled spans.
- All31 original streams/434 saved packet metadata events retain184,640
  original-rate frames per channel. EOS-on-final-packet policy is checked
  against the pinned original fixture. This is not new PCM qualification.
- 12,467 observations agree exactly with the unchanged granule-only Xiph slice.
  The reference executes only where LP64 long and signed64 intermediates are
  safe; boundary/capped cases use the independent unlimited Python model.
  Original block.c SHA256:7f65c7031c2b94405d2c1b5f0a73cc19efe9506e95736ba0b38d86bd42170a7e.
  Extracted fragment SHA256:0fa2f80ff036e27904dbc51ba8b86f9cd67db160334ea986970d40ac9f61bf8b.
- 26,359 invalid-call controls/1,521,715 assertions. Actual state/event/result
  bytes and guards are unchanged on failures; reset/init and sticky EOS are
  covered. Ten damaged captures must be rejected.
- Three supervised commands terminal0, outer CLI0, all children reaped/groups
  gone, sanitizer stderr empty. Source/model/input/capture identities retained.

Source-only GCC15.2 C/C++17 yields four ELF32 objects for LX6/RV32IMC; seven
commands terminal0. Production clang-tidy0warnings/0errors; own push frame160/144B
excludes callees/task high-water. Fixture lint uses an explicit LP64 source
context because its exact reference slice deliberately requires64-bit long.
Its six diagnostics compare its own pre-call object bytes, including padding;
no warning suppression or assertion weakening is introduced. No firmware image,
production selection, task/core/stack/configuration change or timing claim.

Host01 stopped before GCC at sandbox WSL E_ACCESSDENIED. Host02 completed C
execution and the full model comparison, then a corruption probe overwrote an
already-zero field with zero and was accepted. The probe was repaired to write1.
Host03's input.bin,model.json,capture.bin are byte-identical to host02; no corpus,
comparison, C code, safe reference bound or tolerance was changed by that repair.
All attempts are retained separately from the final successful CLI outcome.

`captures.zip`:172 members,17,553,396 uncompressed bytes;1,157,856 compressed.
SHA256:`9cb5c3974079a9da76bb88a532734cc8023a60d49f36f531813a7155264e1fd6`.
`manifest.json` SHA256:
`5b94f5f7a4382ca75345c1c6739f092d6d11789723a99be401dd391b8036f4c9`.
Frozen source/inputs, raw captures, process receipts, diagnostics and source
objects are retained. Rebuildable host executables/objects are omitted with
identities recorded. `replay.json` is packaging replay; `verification.json` is
independent root replay. The [pure verifier](../../verify-vorbis-timing-checkpoint.py)
checks all members, full unlimited model, original434 metadata events, source
extraction, process outcomes and corruption controls without archived execution,
extraction or child commands. Transport placement, full synthesis/PCM and all
previous raw/native/resource/physical/deferred gates remain open.
