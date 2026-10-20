# Scope, seams and stored evidence

The raw audit, host, target and integration reports are byte-identical to their
original ignored outputs. Input hashes and snapshot maps in those reports are
historical run provenance. The archive verifier checks stored bytes and does
not assert that historical repository/SDK input hashes equal the live checkout.

## SDK-source host proof

The actual request generator, body sender, cached response reader and request
cleanup spans run with actual SDK header/utilities. Private client layout,
transport, allocation accounting and scripted auth/redirect/response-state
preparation are host seams. Tests cover reuse capacities4096/8192, OOM retry,
state/body/async admission, retained borrowed pointers and cached reads. They
are not the full SDK auth/redirect/parser/TLS state machine. Semantic controls
must exit80 at their expected named assertion; sanitizer crashes are not a pass.

## Whole target translation unit

The complete patched SDK6.0.2 `esp_http_client.c` was compiled to an Xtensa object
using the existing `build-c3-transfer` row. Only source/output paths were
replaced; compiler flags, headers and generated configuration were preserved.
The target report stores the original row/raw command, response-file/specs,
before/after hashes, all248 dependency paths/snapshots, GCC/cc1/as/nm identities,
SDK commit/clean-status logs and object/symbol checks. Its264 recorded inputs
include report/validator context as well as compiler inputs. The finalizer was
captured after compile and is identified as such; it corrected the CRLF report
check without rebuilding. PE tool payloads are omitted by policy, with hashes
retained. Their DLL closure was not certified. This object proves compilation
against real target private structs/headers; it proves neither linked firmware
placement nor runtime memory ownership under actual TLS traffic.

## Radio and configure integration

The unchanged extracted production `open_stream` runs with explicit HTTP,
clock and release-result seams. The SDK release implementation is tested in
the separate host proof, not substituted as real in the radio fixture.
Enabled/disabled traces agree for response status, redirect, timeout and ICY
metadata behavior. Rejected release retains the request buffer and playback;
redirect/error/deadline/invalid-header paths do not request release.

The actual CMake helper is exercised against a copied SDK input and a mock
component target with source/include/options properties. No CMake SDK library
is built by these tests. Enabled absolute/relative source replacement, disabled
and early expansion, exact1 source, version/source drift/already-patched
rejections and configure dependencies are checked. Installed Windows
CMake/Ninja/Python tool hashes are recorded, not their executable payloads.

## Layout and reproduction

`catalog.json` covers every original artifact file, including failed integration
attempt01. For each entry, `payload` is a direct archive path or a short
content-addressed object; null means the explicit executable omission policy.
The retained runner/fixture/source snapshots and commands are accessible through
this mapping. Original absolute paths in commands and raw reports are retained
as provenance, so replay elsewhere requires restoring a fresh local layout and
reviewing tool/SDK paths; no one-command portable runtime replay is claimed.

The archive contains raw compiler/configure/test logs, generated function spans,
stubs, dependency files, source/config snapshots, audit SDK comparisons/map
observations and the actual Xtensa object. It contains no board measurement or
successful production application build. Keep those qualification gates separate
when updating the parent transfer plan.
