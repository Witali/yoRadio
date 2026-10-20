# Public raw block-matrix target proposal

This fresh prep contains a 195-line shared public caller, 74-line strict offline
validator, eight synthetic host tests and an encoded-bank contract/template.
It contains no SDK launcher/controller or claimed target build. Only the host
protocol suite ran: exit0, eight methods,5.453s. Source/caller/data provenance and
that exact receipt are pinned. No live host report was read; root supplied status
updates while retaining ownership of the actual validation campaigns.

## Complete scope and protocol

The caller always visits all 36 legal short/long pairs in bank order identity,
transitions,minimal and exponent order short6..13,long=short..13. Bank counts are
68/70/14 packets:108 unique cases,5472 paired packets and360 present-transition
groups. All original realistic floor-clipping cases remain. Minimal supplements
them. Missing cases cannot become allowed skips.

Both public original and checked handles are newly opened per case and closed
before CASE_COMPLETE. Their public metadata objects are zeroed once per handle
pair, outside the packet loop, and checked on EVERY packet including priming.
Each original decode must first succeed with complete input consumption, expected
stereo16 overlap bytes, buffer bound,16-byte canaries and correct public metadata;
only then is the checked packet decoded and required byte-exact. Buffers receive
different poison values and canaries are reset/checked around each call. No
private decoder header/state, target Ogg/simple API, reset, OOM or radio hook is
used. Errors preserve bank/pair/packet coordinates and metadata mismatch values.

For each present mode transition, aggregate checked nonzero bytes must be
positive. Exact PCM means vendor nonzero is identical. Identity has SL1/LL66;
transitions has SS1/SL2/LS1/LL65; minimal SS4/SL3/LS3/LL3. Expected output bytes
are0 for packet0, then previous_block+current_block (stereo16). This handles all
sizes64..8192 and equal-size mode pairs without conflating their labels.

Native prefixes/core rules are selected by exactly one explicit profile define:
BLOCK_MATRIX_PROFILE_CYD -> CYD_VORBIS_BLOCK_, worker1, actual ESP32 guard;
BLOCK_MATRIX_PROFILE_C3 -> C3_VORBIS_BLOCK_, worker0, actual ESP32-C3 guard.
Coordinator must be0 in both. Every PACKET/CASE/TRANSITION/BANK/COMPLETE core
field comes from actual xPortGetCoreID(); the configured BEGIN worker and pinned
affinity remain explicit. Prefixes are never translated. The successful full
protocol has6056 lines; every ordered case/packet/transition/close/completion is
validated. Panic, foreign prefix/core, extra/failure line, missing data or an
unknown/interrupted/timed-out/nonzero process is nonpass. A COMPLETE print alone
cannot qualify a still-running or incomplete process.

## Root-frozen encoded input contract

Root supplies banks_data.h and three raw array headers through the template. It
intentionally contains an #error until replaced with actual reviewed input bytes.
Each bank needs raw info[23] and setup WITHOUT the seven-byte packet prefix,
concatenated audio bytes, uint32 offsets and uint8 mode flags. For minimal's
current setup.bin[76], stripping 05+'vorbis' gives69 payload bytes; strip the same
prefix from identification.bin[30] to23. Keep original packet bit lengths/bytes,
window flags and bank names. Recheck source offsets/modes and all hashes against
actual host-qualified generated artifacts. No bank bytes or host qualification
are fabricated by the synthetic host_model.json.

The descriptor records ORIGINAL header rate:192000,192000,48000. The caller
copies each bank's original info and edits only the public block exponents and
sample-rate field, using192000 on BOTH handles for every case. This avoids
assuming original-vendor low-rate8192 support. In particular, retain minimal's
original48000 info as source provenance and prove its exact rate-only192000
counterparts independently for ALL36 cases before launch. Setup/audio/offsets/
mode flags must match that independently qualified family. The required compile
define BLOCK_MATRIX_MINIMAL_RATE_REBIND_VERIFIED=1 is an attestation, not proof;
root must bind its actual completed host report/input hashes to the campaign.

Root's reported original dual-reference108 run is completed NONPASS:78 cases
passed both,30 native FFmpeg rejected an extra floor endpoint/longest-N/2 bound.
Root's primary-source audit says that bound is absent from the Vorbis spec;
these30 are not thereby invalid or omitted. The new required basis is actual
all 108 Xiph/libvorbis-reference acceptance plus retained78 native cross-checks,
and all 36 minimal192000 rate rebindings. Root now reports Xiph108 terminal0
(toolchunk1a7a31) and both-reference minimal192000 rebinding36 terminal0
(toolchunk64bc09). This prep did not independently read/run those campaigns. Root
binds their actual terminal reports/input hashes before populating bank data and
launching; the old dual-reference NONPASS remains unchanged.

## Small integration instructions (not executed)

Reuse the already reviewed isolated SDK project/defaults for the selected ABI.
Compile this main.c plus exactly candidate setup.c/output.c and that ABI's header;
link only --wrap=esp_vorbis_dec_open and --wrap=esp_vorbis_dec_decode against the
pinned original public vendor archives. Do not include application/simple/Ogg/AAC
patch hooks. Select one profile and the explicit rebind attestation; require the
real frozen data manifest SHA. All source/tool/archive/SDK/config/compile/link
identity, correct ELF machine and actual setup.c macro dump (LIMIT_TO_64kHz
absent) remain root-owned checks. Checking only the caller macro context is
insufficient. The adapted caller has not received any SDK/target qualification.

Root keeps the bounded owned build/probe/merge/QEMU commands, raw stdout/stderr,
terminal/interrupt/timeout facts, input hashes before/after and failure history.
Use the reviewed isolated flash recipe and matching emulator/core profile.
No automatic retry, partial pass, physical/radio/network inference or one-ABI
inference is introduced here.

Offline usage after obtaining actual facts:

```python
observed = validate_log(raw_stdout + raw_stderr, frozen_banks, "cyd",
    manifest_sha256=actual_frozen_manifest_sha,
    minimal_rate_rebind_qualified=actual_bound_host_rebind_result,
    returncode=actual_returncode, timed_out=actual_timeout,
    interrupted=actual_interruption)
```

The function returns counts/observations only. It never declares host or target
qualification and starts no process. All keyword facts are required. Hash/input
binding belongs to root's campaign. Run only the synthetic host suite with the
non-SDK Python: `python -B test_block_protocol.py`; its helper success defaults
apply solely to manufactured protocols, never the public validator API.
